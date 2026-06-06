import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header, status_badge

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Access Denied. Please log in from the main portal.")
    st.stop()

apply_global_styles()
page_header("RFQ Management", "Create and manage procurement requests", "📄")

API_URL = "http://localhost:8000"

tab1, tab2 = st.tabs(["All RFQs", "Create New RFQ"])

# ── TAB 1: RFQ LIST WITH PUBLISH ACTION ──────────────────────────────────────────
with tab1:
    section_header("Procurement Requests")
    try:
        res = requests.get(f"{API_URL}/rfqs/")
        if res.status_code == 200:
            rfqs = res.json()
            if rfqs:
                for r in rfqs[::-1]:  # newest first
                    badge = status_badge(r.get("status", "Draft"))
                    with st.container():
                        col_info, col_meta, col_action = st.columns([4, 2, 2])

                        with col_info:
                            st.markdown(
                                f"""<div style="padding:0.1rem 0;">
                                    <span style="font-family:'Plus Jakarta Sans',sans-serif;
                                        font-size:0.95rem; font-weight:600; color:#EFF4FB;">
                                        #{r['id']} · {r['title']}
                                    </span><br/>
                                    <span style="font-family:'DM Mono',monospace;
                                        font-size:0.72rem; color:#4A5A72;">
                                        Qty: {r['quantity']} · Deadline: {str(r['deadline'])[:10]}
                                    </span>
                                </div>""",
                                unsafe_allow_html=True,
                            )

                        with col_meta:
                            st.markdown(f"<div style='padding-top:0.3rem'>{badge}</div>", unsafe_allow_html=True)

                        with col_action:
                            # Only show Publish button for Draft RFQs to Procurement Officers / Admins
                            if (r.get("status") == "Draft"
                                    and st.session_state.user_role in ["Admin", "Procurement Officer"]):
                                if st.button("Publish →", key=f"pub_{r['id']}", use_container_width=True):
                                    upd = requests.patch(
                                        f"{API_URL}/rfqs/{r['id']}/status?new_status=Open"
                                    )
                                    if upd.status_code == 200:
                                        st.success(f"RFQ #{r['id']} is now Open — vendors can bid.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to publish.")

                        st.markdown(
                            "<div style='border-bottom:1px solid rgba(255,255,255,0.05); margin:0.4rem 0'></div>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No RFQs yet. Create one using the tab above.")
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")

# ── TAB 2: CREATE RFQ ────────────────────────────────────────────────────────────
with tab2:
    section_header("Initiate Procurement Workflow")

    if st.session_state.user_role not in ["Admin", "Procurement Officer"]:
        st.error("Access Restricted — only Procurement Officers and Admins can create RFQs.")
        st.stop()

    with st.form("rfq_creation_form", clear_on_submit=True):
        title          = st.text_input("RFQ Title *", placeholder="e.g., Industrial UPS Units — Q3 2026")
        product_details = st.text_area("Specifications & Requirements *",
                                       placeholder="Describe product/service details, technical specs, quality standards…")

        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Required Quantity *", min_value=1, step=1)
        with col2:
            deadline = st.date_input("Submission Deadline *",
                                     value=datetime.today() + timedelta(days=7))

        submitted = st.form_submit_button("Create RFQ (Saved as Draft)", use_container_width=True)

        if submitted:
            if not title or not product_details:
                st.error("Title and Specifications are required.")
            else:
                dt_deadline = datetime.combine(deadline, datetime.min.time()).isoformat()
                payload = {
                    "title": title,
                    "product_details": product_details,
                    "quantity": int(quantity),
                    "deadline": dt_deadline
                }
                try:
                    post_res = requests.post(f"{API_URL}/rfqs/?creator_id=1", json=payload)
                    if post_res.status_code == 200:
                        st.success(f"RFQ '{title}' created as Draft. Go to All RFQs tab and click Publish when ready.")
                    else:
                        st.error(f"Failed: {post_res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

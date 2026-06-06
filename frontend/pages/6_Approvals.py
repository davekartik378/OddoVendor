import streamlit as st
import requests
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header, status_badge

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Access Denied. Please log in from the main portal.")
    st.stop()

apply_global_styles()
page_header("Approval Workflow", "Review and authorise procurement decisions", "✅")

API_URL = "http://localhost:8000"

if st.session_state.user_role not in ["Manager", "Admin"]:
    st.error(f"Access Restricted — '{st.session_state.user_role}' cannot authorise procurement.")
    st.stop()

# ── FETCH RFQs AWAITING APPROVAL ─────────────────────────────────────────────────
# Only RFQs in "Open" status with at least one submitted quotation qualify.
# "Draft" RFQs have not been published to vendors yet — managers should NOT approve them.
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    pending_rfqs = [r for r in rfqs_res.json() if r.get("status") == "Open"]
except Exception:
    pending_rfqs = []

if not pending_rfqs:
    st.success("No open RFQs awaiting approval right now.")
    st.stop()

section_header("Open Requests Awaiting Decision")

rfq_dict = {f"RFQ #{r['id']} · {r['title']}": r['id'] for r in pending_rfqs}
selected_label = st.selectbox("Select Request", list(rfq_dict.keys()))
rfq_id = rfq_dict[selected_label]

# ── QUOTATION TABLE ───────────────────────────────────────────────────────────────
section_header("Available Quotations")

quotes_res = requests.get(f"{API_URL}/rfqs/{rfq_id}/quotations/")

if quotes_res.status_code == 200 and quotes_res.json():
    quotes = quotes_res.json()
    df = pd.DataFrame(quotes)

    display_df = df[["id", "vendor_name", "unit_price", "delivery_days", "health_score"]].copy()
    display_df.columns = ["Quote ID", "Vendor", "Unit Price (₹)", "Delivery (Days)", "Health ★"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── APPROVAL FORM ─────────────────────────────────────────────────────────────
    section_header("Sign Off & Authorise")

    # Build a readable quote dropdown instead of raw IDs
    quote_labels = {
        f"Quote #{q['id']} · {q['vendor_name']} · ₹{q['unit_price']} · {q['delivery_days']} days": q['id']
        for q in quotes
    }

    with st.form("approval_form"):
        selected_quote_label = st.selectbox("Select Winning Bid *", list(quote_labels.keys()))
        remarks = st.text_input(
            "Approval Remarks *",
            placeholder="e.g., Selected for fastest delivery and competitive pricing."
        )

        st.markdown(
            """<div style="
                background:rgba(245,166,35,0.07); border:1px solid rgba(245,166,35,0.25);
                border-radius:8px; padding:0.75rem 1rem; margin:0.5rem 0;
                font-family:'DM Sans',sans-serif; font-size:0.82rem; color:#FCD34D;
            ">
                🔐 Submitting this form generates a SHA-256 cryptographic hash and permanently
                locks this decision into the audit ledger. This action cannot be undone.
            </div>""",
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button("Approve & Digitally Sign", use_container_width=True)

        if submitted:
            if not remarks:
                st.error("Approval remarks are required for the audit log.")
            else:
                winning_id = quote_labels[selected_quote_label]
                # Use the logged-in user's session — for hackathon demo, manager_id=1
                # In production this would come from a proper auth token
                manager_id = 1
                res = requests.post(
                    f"{API_URL}/rfqs/{rfq_id}/approve"
                    f"?winning_quote_id={winning_id}&manager_id={manager_id}&remarks={remarks}"
                )
                if res.status_code == 200:
                    st.success("Approved! RFQ locked. Losing vendors marked as rejected.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Approval failed: {res.text}")
else:
    st.warning("No quotations submitted for this RFQ yet. Vendors must bid before you can approve.")

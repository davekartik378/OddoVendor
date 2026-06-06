import streamlit as st
import requests
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Access Denied. Please log in from the main portal.")
    st.stop()

apply_global_styles()
page_header("Quotation Comparison", "Analyse vendor bids side-by-side and get AI recommendations", "⚖️")

API_URL = "http://localhost:8000"

if st.session_state.user_role == "Vendor":
    st.error("Vendors cannot view competitor pricing. Access restricted.")
    st.stop()

# Fetch RFQs
try:
    rfqs = requests.get(f"{API_URL}/rfqs/").json()
    rfq_dict = {f"RFQ #{r['id']} · {r['title']}": r['id'] for r in rfqs}
except Exception:
    rfq_dict = {}

if not rfq_dict:
    st.info("No RFQs in the system yet.")
    st.stop()

selected_label = st.selectbox("Select RFQ to Analyse", list(rfq_dict.keys()))
rfq_id = rfq_dict[selected_label]

section_header("Submitted Bids")

quotes_res = requests.get(f"{API_URL}/rfqs/{rfq_id}/quotations/")

if quotes_res.status_code == 200 and quotes_res.json():
    quotes = quotes_res.json()
    df = pd.DataFrame(quotes)

    display_df = df[["vendor_name", "unit_price", "delivery_days", "health_score", "remarks"]].copy()
    display_df.columns = ["Vendor", "Unit Price (₹)", "Delivery (Days)", "Health ★", "Remarks"]

    # Highlight lowest price and fastest delivery
    styled = (
        display_df.style
        .highlight_min(subset=["Unit Price (₹)"],   color="#0D2E1E")
        .highlight_min(subset=["Delivery (Days)"],  color="#0D1E2E")
        .set_properties(**{"font-family": "DM Sans, sans-serif", "font-size": "13px"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # ── SMART ADVISOR ────────────────────────────────────────────────────────────
    section_header("Smart Advisor Engine")
    st.markdown(
        "<p style='font-size:0.85rem; color:#8B9DB8; margin-bottom:0.75rem;'>"
        "Runs a local weighted scoring model: 60% price · 20% delivery speed · 20% vendor health."
        "</p>",
        unsafe_allow_html=True,
    )

    if st.button("Run Value Optimisation Analysis", type="primary"):
        with st.spinner("Analysing bids…"):
            adv_res = requests.get(f"{API_URL}/engine/advisor/{rfq_id}")
            if adv_res.status_code == 200:
                data = adv_res.json()
                # Render recommendation in a proper styled card, NOT st.success()
                rec = data["recommendation"]
                # Strip markdown asterisks for clean display
                rec_clean = rec.replace("**", "")
                st.markdown(
                    f"""<div style="
                        background: rgba(16,185,129,0.08);
                        border: 1px solid rgba(16,185,129,0.3);
                        border-radius: 10px;
                        padding: 1.1rem 1.3rem;
                        margin-top: 0.5rem;
                    ">
                        <div style="
                            font-family:'DM Sans',sans-serif;
                            font-size:0.7rem; font-weight:600;
                            letter-spacing:0.08em; text-transform:uppercase;
                            color:#10B981; margin-bottom:0.5rem;
                        ">System Recommendation</div>
                        <div style="
                            font-family:'Plus Jakarta Sans',sans-serif;
                            font-size:0.92rem; color:#EFF4FB;
                            line-height:1.6;
                        ">{rec_clean}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.error("Advisor engine failed. Ensure quotations exist for this RFQ.")
else:
    st.warning("No quotations submitted for this RFQ yet. Vendors need to bid first.")

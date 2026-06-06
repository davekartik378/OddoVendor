import streamlit as st
import requests
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header, status_badge

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Please log in to access this page.")
    st.stop()

apply_global_styles()
page_header("Quotation Comparison", "Analyse vendor bids side-by-side and get recommendations", "⚖️")

API_URL = "http://localhost:8000"

if st.session_state.user_role == "Vendor":
    st.error("Vendors cannot view competitor pricing. Access restricted.")
    st.stop()

# Fetch RFQs
try:
    rfqs = requests.get(f"{API_URL}/rfqs/").json()
    # Show all non-Draft RFQs
    relevant_rfqs = [r for r in rfqs if r.get("status") != "Draft"]
    rfq_dict = {f"RFQ #{r['id']} · {r['title']} [{r['status']}]": r['id'] for r in relevant_rfqs}
except Exception:
    rfq_dict = {}

if not rfq_dict:
    st.info("No published RFQs in the system yet.")
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

    styled = (
        display_df.style
        .highlight_min(subset=["Unit Price (₹)"],  color="#D1FAE5")
        .highlight_min(subset=["Delivery (Days)"], color="#DBEAFE")
        .set_properties(**{"font-family": "Geist, sans-serif", "font-size": "13px"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── SMART ADVISOR ─────────────────────────────────────────────────────────
    section_header("Smart Advisor Engine")
    st.markdown("""
    <p style="font-size:0.85rem; color:#64748B; margin-bottom:0.75rem;">
        Weighted scoring: 60% price · 20% delivery speed · 20% vendor health score.
    </p>
    """, unsafe_allow_html=True)

    if st.button("Run Value Optimisation Analysis", type="primary"):
        with st.spinner("Analysing bids…"):
            adv_res = requests.get(f"{API_URL}/engine/advisor/{rfq_id}")
            if adv_res.status_code == 200:
                data = adv_res.json()
                rec_clean = data["recommendation"].replace("**", "")
                st.markdown(f"""
                <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px;
                    padding:1.1rem 1.3rem; margin-top:0.5rem;">
                    <div style="font-family:'Geist',sans-serif; font-size:0.68rem; font-weight:700;
                        letter-spacing:0.09em; text-transform:uppercase; color:#059669; margin-bottom:0.5rem;">
                        System Recommendation
                    </div>
                    <div style="font-family:'Geist',sans-serif; font-size:0.92rem; color:#064E3B; line-height:1.6;">
                        {rec_clean}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.error("Advisor engine failed. Ensure quotations exist for this RFQ.")

    # ── SELECT WINNER (for Manager/Admin to approve) ─────────────────────────
    # Only show "Mark for Review" for Open RFQs with quotes
    rfq_info = next((r for r in rfqs if r['id'] == rfq_id), None)
    if rfq_info and rfq_info.get("status") == "Open":
        if st.session_state.user_role in ["Admin", "Procurement Officer"]:
            section_header("Move to Approval")
            st.markdown("""
            <p style="font-size:0.85rem; color:#64748B; margin-bottom:0.75rem;">
                Once you have analysed the bids, submit this RFQ for manager approval.
            </p>
            """, unsafe_allow_html=True)
            if st.button("Submit for Manager Approval →", type="primary"):
                upd = requests.patch(f"{API_URL}/rfqs/{rfq_id}/status?new_status=Under Review")
                if upd.status_code == 200:
                    st.success("RFQ submitted for approval. The Manager will be notified.")
                    st.rerun()
                else:
                    st.error("Failed to update status.")
else:
    st.markdown("""
    <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:10px;
        padding:1.5rem; text-align:center;">
        <div style="font-size:1.5rem; margin-bottom:0.4rem;">⏳</div>
        <p style="color:#92400E; font-size:0.88rem; margin:0;">
            No quotations submitted for this RFQ yet. Vendors need to bid first.
        </p>
    </div>
    """, unsafe_allow_html=True)

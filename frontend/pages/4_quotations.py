import streamlit as st
import requests
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Access Denied. Please log in from the main portal.")
    st.stop()

apply_global_styles()
page_header("Submit Quotation", "Respond to open procurement requests with your pricing", "💸")

API_URL = "http://localhost:8000"

# Hard stop for non-vendors
if st.session_state.user_role != "Vendor":
    st.error(f"This module is for Vendors only. You are logged in as '{st.session_state.user_role}'.")
    st.stop()

if not st.session_state.get("vendor_id"):
    st.error("No vendor profile linked to this session. Please log out and sign in as Vendor.")
    st.stop()

# Fetch open RFQs
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    open_rfqs = [r for r in rfqs_res.json() if r.get("status") == "Open"]
except Exception:
    open_rfqs = []
    st.error("Cannot connect to backend.")
    st.stop()

if not open_rfqs:
    st.info("No open RFQs available for bidding at this time. Check back later.")
    st.stop()

section_header("Open Procurement Requests")

rfq_options = {
    f"RFQ #{r['id']} · {r['title']} (Qty: {r['quantity']})": r['id']
    for r in open_rfqs
}

with st.form("quote_submission_form"):
    selected_label = st.selectbox("Select RFQ to Bid On *", list(rfq_options.keys()))

    col1, col2 = st.columns(2)
    with col1:
        unit_price    = st.number_input("Your Unit Price (₹) *", min_value=1.0, step=100.0)
    with col2:
        delivery_days = st.number_input("Estimated Delivery (Days) *", min_value=1, step=1)

    remarks = st.text_area("Additional Remarks / Warranty Terms",
                           placeholder="e.g., 1-year warranty included, GST applicable…")

    submitted = st.form_submit_button("Submit Quotation", use_container_width=True)

    if submitted:
        payload = {
            "rfq_id":       rfq_options[selected_label],
            "unit_price":   unit_price,
            "delivery_days": int(delivery_days),
            "remarks":      remarks
        }
        try:
            res = requests.post(
                f"{API_URL}/quotations/?vendor_id={st.session_state.vendor_id}",
                json=payload
            )
            if res.status_code == 200:
                st.success("Quotation submitted successfully! You will be notified if selected.")
                st.balloons()
            else:
                st.error(f"Submission failed: {res.json().get('detail', res.text)}")
        except Exception as e:
            st.error(f"Connection error: {e}")

import streamlit as st
import requests

st.set_page_config(page_title="Submit Quotation", page_icon="💸", layout="wide")

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in.")
    st.stop()

st.title("💸 Vendor Bidding Portal")
st.markdown("Submit your pricing and delivery timelines for open procurement requests.")
st.markdown("---")

API_URL = "http://localhost:8000"

if st.session_state.user_role != "Vendor":
    st.info(f"You are logged in as {st.session_state.user_role}. This screen is designed for Vendor workflows.")

# Fetch Open RFQs
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    open_rfqs = [r for r in rfqs_res.json() if r.get("status") in ["Draft", "Open"]]
except:
    open_rfqs = []

if not open_rfqs:
    st.success("No active RFQs require bidding at this time.")
else:
    # Build a dictionary for the dropdown: "RFQ #1 - Title" -> 1
    rfq_options = {f"RFQ #{r['id']} - {r['title']} (Qty: {r['quantity']})": r['id'] for r in open_rfqs}
    
    with st.form("quote_submission_form"):
        selected_rfq_label = st.selectbox("Select Target RFQ", list(rfq_options.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            unit_price = st.number_input("Unit Price (₹) *", min_value=1.0, step=100.0)
        with col2:
            delivery_days = st.number_input("Estimated Delivery (Days) *", min_value=1, step=1)
            
        remarks = st.text_area("Additional Remarks / Warranty Details")
        
        submitted = st.form_submit_button("Submit Binding Quotation")
        
        if submitted:
            # We now securely pull the REAL vendor ID from the session state
            active_vendor_id = st.session_state.get("vendor_id")
            
            if not active_vendor_id:
                st.error("Authentication Error: No Vendor Profile linked to this session. Please log out and log back in.")
            else:
                payload = {
                    "rfq_id": rfq_options[selected_rfq_label],
                    "unit_price": unit_price,
                    "delivery_days": delivery_days,
                    "remarks": remarks
                }
                
                try:
                    res = requests.post(f"{API_URL}/quotations/?vendor_id={active_vendor_id}", json=payload)
                    
                    if res.status_code == 200:
                        st.success("✅ Quotation submitted successfully! You will be notified if selected.")
                        st.balloons()
                    else:
                        # This exposes the exact error from the backend (e.g., if the RFQ is closed)
                        error_msg = res.json().get('detail', res.text)
                        st.error(f"Failed to submit quotation: {error_msg}")
                except Exception as e:
                    st.error(f"Critical Connection Error: {e}")
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Approvals Workflow", page_icon="✅", layout="wide")

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in.")
    st.stop()

st.title("✅ Executive Approval Workflow")
st.markdown("Review procurement recommendations and cryptographically sign approvals.")
st.markdown("---")

API_URL = "http://localhost:8000"

# Strict Role Check
if st.session_state.user_role not in ["Manager", "Admin"]:
    st.error(f"Action Restricted. The '{st.session_state.user_role}' role cannot authorize procurement spending.")
    st.stop()

# Fetch RFQs that are awaiting approval
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    pending_rfqs = [r for r in rfqs_res.json() if r.get("status") in ["Draft", "Open"]]
except:
    pending_rfqs = []

if not pending_rfqs:
    st.success("🎉 Inbox Zero! No procurement requests require your approval at this time.")
else:
    # Build dropdown dictionary
    rfq_dict = {f"RFQ #{r['id']} - {r['title']}": r['id'] for r in pending_rfqs}
    
    selected_rfq_label = st.selectbox("Select Pending Request", list(rfq_dict.keys()))
    rfq_id = rfq_dict[selected_rfq_label]
    
    st.markdown("### Available Quotations")
    
    quotes_res = requests.get(f"{API_URL}/rfqs/{rfq_id}/quotations/")
    
    if quotes_res.status_code == 200 and quotes_res.json():
        quotes = quotes_res.json()
        df = pd.DataFrame(quotes)
        
        display_df = df[['id', 'vendor_name', 'unit_price', 'delivery_days']]
        display_df.columns = ['Quote ID', 'Vendor', 'Unit Price (₹)', 'Delivery (Days)']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("Sign Off & Authorize")
        
        with st.form("approval_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Let the manager pick the winning Quote ID
                winning_quote_id = st.selectbox("Select Winning Bid (Quote ID) *", df['id'].tolist())
                
            with col2:
                remarks = st.text_input("Approval Remarks / Justification *", placeholder="e.g., Selected for fastest delivery time.")
                
            st.info("🔐 Submitting this form will generate a SHA-256 cryptographic hash to lock this decision into the system ledger permanently.")
            submitted = st.form_submit_button("Approve & Digitally Sign", type="primary")
            
            if submitted:
                if not remarks:
                    st.error("Approval remarks are legally required for the audit log.")
                else:
                    # Execute the approval endpoint. (Using manager_id = 2 for hackathon simulation)
                    res = requests.post(
                        f"{API_URL}/rfqs/{rfq_id}/approve?winning_quote_id={winning_quote_id}&manager_id=2&remarks={remarks}"
                    )
                    
                    if res.status_code == 200:
                        st.success("✅ Workflow Approved! The RFQ has been locked and losing vendors have been rejected.")
                        st.balloons()
                    else:
                        st.error("System failed to lock the approval.")
    else:
        st.warning("Waiting on vendors to submit bids for this request.")
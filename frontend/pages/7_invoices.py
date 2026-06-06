import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Purchase Orders", page_icon="🖨️", layout="wide")

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in.")
    st.stop()

st.title("🖨️ Purchase Orders & Invoices")
st.markdown("Convert approved workflows into official financial documents.")
st.markdown("---")

API_URL = "http://localhost:8000"

if st.session_state.user_role not in ["Procurement Officer", "Admin"]:
    st.error("Action Restricted. Only Procurement Officers can generate official POs.")
    st.stop()

# Fetch Approved RFQs ready for fulfillment
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    approved_rfqs = [r for r in rfqs_res.json() if r.get("status") == "Approved"]
except:
    approved_rfqs = []

if not approved_rfqs:
    st.success("No pending approvals waiting for Purchase Order generation.")
else:
    st.subheader("Pending Fulfillment")
    
    # Display the queue
    df = pd.DataFrame(approved_rfqs)
    display_df = df[['id', 'title', 'quantity']]
    display_df.columns = ['RFQ ID', 'Project Title', 'Quantity']
    st.dataframe(display_df, hide_index=True)
    
    st.markdown("---")
    
    with st.form("po_generator_form"):
        rfq_options = {f"RFQ #{r['id']} - {r['title']}": r['id'] for r in approved_rfqs}
        selected_rfq = st.selectbox("Select Project to Finalize", list(rfq_options.keys()))
        
        submitted = st.form_submit_button("Generate Official PO & Invoice", type="primary")
        
        if submitted:
            target_id = rfq_options[selected_rfq]
            
            with st.spinner("Compiling PDF document locally..."):
                res = requests.post(f"{API_URL}/generate-po/{target_id}")
                
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"✅ Success! Generated {data['po_number']}.")
                    
                    # Fetch the actual PDF file bytes from the backend to create a download button
                    pdf_res = requests.get(f"{API_URL}/download-invoice/{data['po_number']}")
                    
                    if pdf_res.status_code == 200:
                        st.download_button(
                            label="📥 Download Invoice (PDF)",
                            data=pdf_res.content,
                            file_name=f"{data['po_number']}.pdf",
                            mime="application/pdf",
                            type="primary"
                        )
                        st.info("The workflow loop is now complete. The RFQ has been marked as 'Closed'.")
                else:
                    st.error(f"Failed to generate PO: {res.text}")
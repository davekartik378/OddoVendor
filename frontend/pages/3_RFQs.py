import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RFQ Management", page_icon="📄", layout="wide")

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in.")
    st.stop()

st.title("📄 Request for Quotation (RFQ) Portal")
st.markdown("Initiate new procurement requests and track active bids.")
st.markdown("---")

API_URL = "http://localhost:8000"

tab1, tab2 = st.tabs(["📋 Active RFQs", "➕ Create New RFQ"])

# --- TAB 1: ACTIVE RFQs ---
with tab1:
    st.subheader("Open Procurement Requests")
    try:
        res = requests.get(f"{API_URL}/rfqs/")
        if res.status_code == 200:
            rfqs = res.json()
            if rfqs:
                df = pd.DataFrame(rfqs)
                display_df = df[['id', 'title', 'quantity', 'deadline', 'status']]
                display_df.columns = ['RFQ ID', 'Title', 'Quantity Required', 'Deadline', 'Status']
                
                # Highlight status using Streamlit's new dataframe styling
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No active RFQs found in the database.")
    except Exception as e:
        st.error("Failed to connect to the backend server.")


# --- TAB 2: CREATE RFQ ---
with tab2:
    st.subheader("Initiate Procurement Workflow")
    
    if st.session_state.user_role not in ["Admin", "Procurement Officer"]:
        st.error("Action Restricted. Only Procurement Officers and Admins can create RFQs.")
    else:
        with st.form("rfq_creation_form", clear_on_submit=True):
            title = st.text_input("RFQ Title (e.g., Heavy Machinery Parts) *")
            product_details = st.text_area("Detailed Specifications & Requirements *")
            
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input("Required Quantity *", min_value=1, step=1)
            with col2:
                # Default deadline to 7 days from today
                deadline = st.date_input("Submission Deadline *")
                
            submitted = st.form_submit_button("Broadcast RFQ")
            
            if submitted:
                if not title or not product_details:
                    st.error("Title and Specifications are required.")
                else:
                    # Convert Streamlit date to standard datetime for FastAPI
                    dt_deadline = datetime.combine(deadline, datetime.min.time()).isoformat()
                    
                    payload = {
                        "title": title,
                        "product_details": product_details,
                        "quantity": quantity,
                        "deadline": dt_deadline
                    }
                    
                    # Note: We pass creator_id=1 as a query param for the hackathon demo
                    try:
                        post_res = requests.post(f"{API_URL}/rfqs/?creator_id=1", json=payload)
                        if post_res.status_code == 200:
                            st.success(f"✅ RFQ '{title}' generated successfully! Status set to Draft.")
                        else:
                            st.error(f"Failed to create RFQ: {post_res.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
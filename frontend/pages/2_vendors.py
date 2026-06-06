import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Vendor Management", page_icon="🏢", layout="wide")

# Security Check: Kick out unauthenticated users
if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in from the main portal.")
    st.stop()

st.title("🏢 Vendor Management Portal")
st.markdown("Maintain organized vendor records, track health scores, and register new suppliers.")
st.markdown("---")

API_URL = "http://localhost:8000"

# Create two tabs for a clean UI
tab1, tab2 = st.tabs(["📋 Vendor Directory", "➕ Register New Vendor"])

# --- TAB 1: VENDOR DIRECTORY ---
with tab1:
    st.subheader("Approved Suppliers")
    
    try:
        response = requests.get(f"{API_URL}/vendors/")
        if response.status_code == 200:
            vendors = response.json()
            if vendors:
                df = pd.DataFrame(vendors)
                
                # Clean up the dataframe columns for a professional display
                display_df = df[['id', 'name', 'category', 'contact_email', 'gst_number', 'health_score']]
                display_df.columns = ['ID', 'Vendor Name', 'Category', 'Contact Email', 'GST Number', 'Health Score (out of 5.0)']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No vendors registered in the system yet. Head to the registration tab to add one.")
        else:
            st.error("Failed to fetch vendors from the database.")
    except requests.exceptions.ConnectionError:
        st.error("🚨 CRITICAL: Cannot connect to backend server. Is Uvicorn running?")

# --- TAB 2: REGISTRATION FORM ---
with tab2:
    st.subheader("New Vendor Onboarding")
    
    # Role-based Access Control
    if st.session_state.user_role not in ["Admin", "Procurement Officer"]:
        st.error(f"Action Restricted. The '{st.session_state.user_role}' role does not have permission to onboard new vendors.")
    else:
        with st.form("vendor_registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                vendor_name = st.text_input("Vendor Company Name *")
                contact_email = st.text_input("Official Contact Email *")
                
            with col2:
                # Max chars matches our backend Pydantic validation
                gst_number = st.text_input("GST Number (Exactly 15 Characters) *", max_chars=15)
                category = st.selectbox("Primary Supply Category *", [
                    "Heavy Machinery", 
                    "Electronics & Hardware", 
                    "Software & IT Services", 
                    "Raw Materials",
                    "Logistics & Transport",
                    "Other"
                ])
            
            submitted = st.form_submit_button("Register Vendor")
            
            if submitted:
                # 1. Frontend Validation
                if not vendor_name or not contact_email or not gst_number:
                    st.error("Please fill in all required fields.")
                elif len(gst_number) != 15:
                    st.error("GST Number must be exactly 15 characters long.")
                else:
                    # 2. Package data for the API
                    payload = {
                        "name": vendor_name,
                        "gst_number": gst_number.upper(),
                        "contact_email": contact_email,
                        "category": category
                    }
                    
                    # 3. Backend Execution
                    try:
                        res = requests.post(f"{API_URL}/vendors/", json=payload)
                        if res.status_code == 200:
                            st.success(f"✅ Vendor '{vendor_name}' registered successfully!")
                            st.balloons() # Little hackathon flair
                        else:
                            # This catches our FastAPI error if a GST number already exists
                            st.error(f"Registration Failed: {res.json().get('detail', 'Unknown Error')}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
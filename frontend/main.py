import streamlit as st
import requests

# Must be the first Streamlit command
st.set_page_config(page_title="VendorBridge ERP", page_icon="🌉", layout="wide")

API_URL = "http://localhost:8000"

# Initialize Session State Variables
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "vendor_id" not in st.session_state:
    st.session_state.vendor_id = None

st.title("🌉 VendorBridge Command Center")
st.markdown("Offline-First Procurement & Vendor Management")
st.markdown("---")

# --- THE UPGRADED AUTHENTICATION WALL ---
if st.session_state.user_role is None:
    st.subheader("System Authentication")
    
    with st.form("login_form"):
        st.info("Select your role. Vendors must authenticate against a registered profile.")
        role = st.selectbox("System Role", ["Admin", "Manager", "Procurement Officer", "Vendor"])
        user_email = st.text_input("Email ID", value="demo@vendorbridge.com")
        
        submitted = st.form_submit_button("Authenticate Securely")
        
        if submitted:
            st.session_state.user_role = role
            st.session_state.user_email = user_email
            
            # If they are an internal employee, log them in immediately
            if role != "Vendor":
                st.rerun()

    # Dynamic Vendor Profile Selection (Only shows if they clicked Authenticate as Vendor)
    if st.session_state.user_role == "Vendor":
        try:
            res = requests.get(f"{API_URL}/vendors/")
            if res.status_code == 200 and res.json():
                vendor_list = res.json()
                # Create a mapping of Company Name -> Database ID
                vendor_map = {v['name']: v['id'] for v in vendor_list}
                
                with st.form("vendor_profile_selection"):
                    st.warning("Vendor Role detected. Please select your specific company profile.")
                    selected_vendor = st.selectbox("Company Profile", list(vendor_map.keys()))
                    confirm_login = st.form_submit_button("Confirm Identity & Login")
                    
                    if confirm_login:
                        # Save their actual database ID into the session
                        st.session_state.vendor_id = vendor_map[selected_vendor]
                        st.rerun()
            else:
                st.error("No vendors are registered in the system yet. Please log in as an Admin to register a vendor first.")
                if st.button("Reset Login"):
                    st.session_state.user_role = None
                    st.rerun()
        except Exception as e:
            st.error("Backend connection failed. Make sure Uvicorn is running.")

else:
    # --- ACTIVE SESSION SIDEBAR ---
    st.sidebar.success(f"Active Role: {st.session_state.user_role}")
    
    # Show exactly WHICH vendor they are logged in as
    if st.session_state.user_role == "Vendor" and st.session_state.vendor_id:
        st.sidebar.info(f"Vendor ID Linked: #{st.session_state.vendor_id}")
        
    st.sidebar.write(f"User: {st.session_state.user_email}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user_role = None
        st.session_state.user_email = None
        st.session_state.vendor_id = None
        st.rerun()
        
    st.success(f"Welcome to VendorBridge, {st.session_state.user_role}.")
    st.info("👈 Please select a module from the sidebar to begin operations.")
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
page_header("Vendor Management", "Register and manage your supplier network", "🏢")

API_URL = "http://localhost:8000"

tab1, tab2 = st.tabs(["Vendor Directory", "Register New Vendor"])

# ── TAB 1: DIRECTORY ─────────────────────────────────────────────────────────────
with tab1:
    section_header("Approved Suppliers")
    try:
        res = requests.get(f"{API_URL}/vendors/")
        if res.status_code == 200:
            vendors = res.json()
            if vendors:
                df = pd.DataFrame(vendors)
                display_df = df[["id", "name", "category", "contact_email", "gst_number", "health_score"]]
                display_df.columns = ["ID", "Vendor Name", "Category", "Contact Email", "GST Number", "Health ★"]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No vendors registered yet. Use the Register tab to add one.")
        else:
            st.error("Failed to fetch vendors.")
    except Exception:
        st.error("Cannot connect to backend server.")

# ── TAB 2: REGISTRATION ──────────────────────────────────────────────────────────
with tab2:
    section_header("New Vendor Onboarding")

    if st.session_state.user_role not in ["Admin", "Procurement Officer"]:
        st.error(f"Access Restricted — '{st.session_state.user_role}' cannot onboard vendors.")
        st.stop()

    with st.form("vendor_registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            vendor_name   = st.text_input("Company Name *")
            contact_email = st.text_input("Contact Email *")
        with col2:
            gst_number = st.text_input("GST Number (15 characters) *", max_chars=15)
            category   = st.selectbox("Supply Category *", [
                "Heavy Machinery", "Electronics & Hardware",
                "Software & IT Services", "Raw Materials",
                "Logistics & Transport", "Other"
            ])

        submitted = st.form_submit_button("Register Vendor", use_container_width=True)

        if submitted:
            if not vendor_name or not contact_email or not gst_number:
                st.error("All fields are required.")
            elif len(gst_number) != 15:
                st.error("GST Number must be exactly 15 characters.")
            else:
                payload = {
                    "name": vendor_name,
                    "gst_number": gst_number.upper(),
                    "contact_email": contact_email,
                    "category": category
                }
                try:
                    res = requests.post(f"{API_URL}/vendors/", json=payload)
                    if res.status_code == 200:
                        st.success(f"Vendor '{vendor_name}' registered successfully!")
                        st.balloons()
                    else:
                        st.error(f"Registration failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

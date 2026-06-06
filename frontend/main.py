import streamlit as st
import requests
import sys
import os

# Add utils to path so pages can import it too
sys.path.append(os.path.dirname(__file__))

# MUST be first Streamlit command — only here, NOT in any page file
st.set_page_config(
    page_title="VendorBridge ERP",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.style import apply_global_styles, sidebar_branding

apply_global_styles()

API_URL = "http://localhost:8000"

# Initialize session state
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "vendor_id" not in st.session_state:
    st.session_state.vendor_id = None


# ─── LOGIN SCREEN ──────────────────────────────────────────────────────────────
if st.session_state.user_role is None:

    # Centered login card
    col_l, col_mid, col_r = st.columns([1, 1.4, 1])
    with col_mid:
        st.markdown("""
        <div style="text-align:center; padding: 2.5rem 0 2rem 0;">
            <div style="
                width:56px; height:56px;
                background: linear-gradient(135deg,#F5A623,#FF6B35);
                border-radius:14px;
                display:flex; align-items:center; justify-content:center;
                font-size:1.6rem; margin: 0 auto 1rem auto;
            ">🌉</div>
            <h1 style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:1.8rem; font-weight:800;
                color:#EFF4FB; letter-spacing:-0.03em; margin:0;
            ">VendorBridge</h1>
            <p style="
                font-family:'DM Sans',sans-serif;
                font-size:0.82rem; color:#4A5A72;
                letter-spacing:0.1em; text-transform:uppercase;
                margin:0.3rem 0 0 0;
            ">Procurement & Vendor Management ERP</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            role = st.selectbox(
                "System Role",
                ["Procurement Officer", "Manager", "Admin", "Vendor"],
            )
            user_email = st.text_input("Email Address", placeholder="you@company.com")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not user_email:
                    st.error("Please enter your email address.")
                else:
                    st.session_state.user_role = role
                    st.session_state.user_email = user_email
                    if role != "Vendor":
                        st.rerun()

        # Vendor second step — only show after Vendor role is selected
        if st.session_state.user_role == "Vendor":
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            try:
                res = requests.get(f"{API_URL}/vendors/")
                if res.status_code == 200 and res.json():
                    vendor_map = {v['name']: v['id'] for v in res.json()}
                    with st.form("vendor_select"):
                        st.info("Select your registered company profile to continue.")
                        selected = st.selectbox("Company Profile", list(vendor_map.keys()))
                        confirm = st.form_submit_button("Confirm & Enter", use_container_width=True)
                        if confirm:
                            st.session_state.vendor_id = vendor_map[selected]
                            st.rerun()
                else:
                    st.warning("No vendors registered yet. Log in as Admin first.")
                    if st.button("Reset", use_container_width=True):
                        st.session_state.user_role = None
                        st.rerun()
            except Exception:
                st.error("Cannot connect to backend. Is the server running?")


# ─── AUTHENTICATED SHELL ───────────────────────────────────────────────────────
else:
    sidebar_branding()

    # Role pill
    role_colors = {
        "Admin": "#EF4444",
        "Manager": "#3B82F6",
        "Procurement Officer": "#10B981",
        "Vendor": "#F5A623",
    }
    color = role_colors.get(st.session_state.user_role, "#8B9DB8")
    st.sidebar.markdown(f"""
    <div style="
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.07);
        border-radius:8px;
        padding:0.7rem 1rem;
        margin-bottom:0.5rem;
    ">
        <div style="
            font-family:'DM Sans',sans-serif;
            font-size:0.7rem; font-weight:600;
            letter-spacing:0.08em; text-transform:uppercase;
            color:#4A5A72; margin-bottom:4px;
        ">Active Session</div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="
                display:inline-block; width:8px; height:8px;
                border-radius:50%; background:{color};
                box-shadow:0 0 8px {color}80;
            "></span>
            <span style="
                font-family:'Plus Jakarta Sans',sans-serif;
                font-size:0.85rem; font-weight:600;
                color:#EFF4FB;
            ">{st.session_state.user_role}</span>
        </div>
        <div style="
            font-family:'DM Mono',monospace;
            font-size:0.72rem; color:#4A5A72;
            margin-top:4px; white-space:nowrap;
            overflow:hidden; text-overflow:ellipsis;
        ">{st.session_state.user_email}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.user_role == "Vendor" and st.session_state.vendor_id:
        st.sidebar.markdown(f"""
        <div style="
            font-family:'DM Mono',monospace;
            font-size:0.7rem; color:#4A5A72;
            padding: 0 0.25rem; margin-bottom:0.5rem;
        ">Vendor ID linked: #{st.session_state.vendor_id}</div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.sidebar.button("Sign Out", use_container_width=True):
        st.session_state.user_role = None
        st.session_state.user_email = None
        st.session_state.vendor_id = None
        st.rerun()

    # Home screen content
    st.markdown(f"""
    <div style="padding: 1rem 0 0.5rem 0;">
        <h1 style="
            font-family:'Plus Jakarta Sans',sans-serif;
            font-size:1.5rem; font-weight:800;
            color:#EFF4FB; margin:0; letter-spacing:-0.02em;
        ">Good day — use the sidebar to navigate.</h1>
        <p style="
            font-family:'DM Sans',sans-serif;
            font-size:0.88rem; color:#4A5A72;
            margin:0.5rem 0 0 0;
        ">VendorBridge Procurement ERP · Logged in as {st.session_state.user_role}</p>
    </div>
    """, unsafe_allow_html=True)

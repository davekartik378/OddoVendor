import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(__file__))

st.set_page_config(
    page_title="VendorBridge ERP",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.style import apply_global_styles, sidebar_branding

apply_global_styles()

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

def safe_detail(res, fallback="Unknown error"):
    try:
        return res.json().get("detail", fallback)
    except Exception:
        return res.text or fallback

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for key, default in [
    ("user_role",  None),
    ("user_email", None),
    ("user_id",    None),
    ("vendor_id",  None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── ROLE → PAGES MAP ──────────────────────────────────────────────────────────
PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")

def make_page(filename, label, icon):
    return st.Page(os.path.join(PAGES_DIR, filename), title=label, icon=icon)

ALL_PAGES = {
    "dashboard":   make_page("1_dashboard.py",    "Dashboard",         "📊"),
    "vendors":     make_page("2_vendors.py",       "Vendors",           "🏢"),
    "rfqs":        make_page("3_RFQs.py",          "RFQs",              "📄"),
    "quotations":  make_page("4_quotations.py",    "Submit Quotation",  "💸"),
    "comparison":  make_page("5_comparison.py",    "Compare Quotes",    "⚖️"),
    "approvals":   make_page("6_Approvals.py",     "Approvals",         "✅"),
    "invoices":    make_page("7_invoices.py",       "PO & Invoices",     "🖨️"),
    "logs":        make_page("8_activity_logs.py", "Activity Logs",     "🔐"),
    "reports":     make_page("9_reports.py",        "Reports",           "📈"),
}

ROLE_PAGES = {
    "Admin":               ["dashboard", "vendors", "rfqs", "comparison", "approvals", "invoices", "logs", "reports"],
    "Manager":             ["dashboard", "rfqs", "comparison", "approvals", "logs", "reports"],
    "Procurement Officer": ["dashboard", "vendors", "rfqs", "comparison", "invoices", "reports"],
    "Vendor":              ["dashboard", "quotations"],
}


# ═══════════════════════════════════════════════════════════════════════════════
#  NOT LOGGED IN — Clean light login page
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.user_role is None:

    # Page-level override for login: center layout, no sidebar
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #F0F4FF 0%, #F8FAFC 60%, #F0FDF4 100%) !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .block-container { max-width: 520px !important; padding-top: 4rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # Logo / Brand
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <div style="
            width:52px; height:52px;
            background:linear-gradient(135deg,#4F6AF5,#818CF8);
            border-radius:14px; display:inline-flex;
            align-items:center; justify-content:center;
            font-size:1.5rem; margin-bottom:0.9rem;
            box-shadow:0 4px 16px rgba(79,106,245,0.25);
        ">🌉</div>
        <h1 style="font-family:'Geist',sans-serif; font-size:1.75rem; font-weight:800;
            color:#0F172A; letter-spacing:-0.04em; margin:0;">VendorBridge</h1>
        <p style="font-family:'Geist',sans-serif; font-size:0.8rem; color:#94A3B8;
            letter-spacing:0.1em; text-transform:uppercase; margin:0.3rem 0 0 0;">
            Procurement &amp; Vendor Management ERP
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Card wrapper
    tab_login, tab_signup, tab_vendor = st.tabs(["Sign In", "Staff Account", "Vendor Registration"])

    # ── TAB 1: SIGN IN ────────────────────────────────────────────────────────
    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("Email Address", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                try:
                    res = requests.post(f"{API_URL}/login", params={"email": email, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.user_role  = data["role"]
                        st.session_state.user_email = data["email"]
                        st.session_state.user_id    = data["id"]
                        if data["role"] == "Vendor":
                            vres = requests.get(f"{API_URL}/vendors/")
                            if vres.status_code == 200:
                                for v in vres.json():
                                    if v.get("contact_email", "").lower() == email.lower():
                                        st.session_state.vendor_id = v["id"]
                                        break
                        st.rerun()
                    elif res.status_code == 401:
                        st.error("Incorrect email or password.")
                    else:
                        st.error(f"Login failed: {safe_detail(res)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend. Make sure the FastAPI server is running on port 8000.")

    # ── TAB 2: STAFF ACCOUNT ──────────────────────────────────────────────────
    with tab_signup:
        st.markdown("""
        <p style="font-size:0.83rem; color:#64748B; margin-bottom:0.75rem;">
            For internal staff: Procurement Officers and Managers only.<br>
            <strong>Admin accounts must be created by an existing Admin.</strong>
        </p>
        """, unsafe_allow_html=True)

        with st.form("signup_form"):
            su_email = st.text_input("Email Address", placeholder="you@company.com", key="su_email")
            # Note: Admin cannot be self-registered — only Procurement Officer / Manager
            su_role  = st.selectbox("Your Role", ["Procurement Officer", "Manager"], key="su_role")
            su_pass  = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="su_pass")
            su_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="su_pass2")
            su_sub   = st.form_submit_button("Create Staff Account", use_container_width=True)

        if su_sub:
            if not su_email or not su_pass:
                st.error("All fields are required.")
            elif len(su_pass) < 6:
                st.error("Password must be at least 6 characters.")
            elif su_pass != su_pass2:
                st.error("Passwords do not match.")
            elif "@" not in su_email:
                st.error("Please enter a valid email address.")
            else:
                try:
                    res = requests.post(f"{API_URL}/users/", json={
                        "email": su_email, "password": su_pass, "role": su_role
                    })
                    if res.status_code == 200:
                        st.success("Account created! Sign in from the Sign In tab.")
                    else:
                        st.error(f"Registration failed: {safe_detail(res)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend.")

    # ── TAB 3: VENDOR REGISTRATION ────────────────────────────────────────────
    with tab_vendor:
        st.markdown("""
        <p style="font-size:0.83rem; color:#64748B; margin-bottom:0.75rem;">
            New supplier? Register your company and create your login in one step.
        </p>
        """, unsafe_allow_html=True)

        with st.form("vendor_register_form"):
            vr_company = st.text_input("Company Name *", placeholder="Acme Supplies Ltd.")
            vr_email   = st.text_input("Business Email *", placeholder="contact@acme.com")
            vr_gst     = st.text_input("GST Number (15 chars) *", max_chars=15, placeholder="22AAAAA0000A1Z5")
            vr_cat     = st.selectbox("Supply Category *", [
                "Heavy Machinery", "Electronics & Hardware",
                "Software & IT Services", "Raw Materials",
                "Logistics & Transport", "Other"
            ])
            vr_pass  = st.text_input("Set Password *", type="password", placeholder="Min. 6 characters", key="vr_pass")
            vr_pass2 = st.text_input("Confirm Password *", type="password", placeholder="Repeat password", key="vr_pass2")
            vr_sub   = st.form_submit_button("Register Vendor Account", use_container_width=True)

        if vr_sub:
            if not vr_company or not vr_email or not vr_gst or not vr_pass:
                st.error("All fields marked * are required.")
            elif len(vr_gst) != 15:
                st.error("GST Number must be exactly 15 characters.")
            elif "@" not in vr_email:
                st.error("Please enter a valid email address.")
            elif len(vr_pass) < 6:
                st.error("Password must be at least 6 characters.")
            elif vr_pass != vr_pass2:
                st.error("Passwords do not match.")
            else:
                try:
                    user_res = requests.post(f"{API_URL}/users/", json={
                        "email": vr_email, "password": vr_pass, "role": "Vendor"
                    })
                    if user_res.status_code not in [200, 400]:
                        st.error(f"Account creation failed: {safe_detail(user_res)}")
                        st.stop()
                    vendor_res = requests.post(f"{API_URL}/vendors/", json={
                        "name": vr_company, "gst_number": vr_gst.upper(),
                        "contact_email": vr_email, "category": vr_cat,
                    })
                    if vendor_res.status_code == 200:
                        st.success(f"'{vr_company}' registered successfully! Sign in from the Sign In tab.")
                        st.balloons()
                    else:
                        st.error(f"Vendor profile failed: {safe_detail(vendor_res)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend.")


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTHENTICATED — role-based navigation
# ═══════════════════════════════════════════════════════════════════════════════
else:
    role       = st.session_state.user_role
    page_keys  = ROLE_PAGES.get(role, ["dashboard"])
    nav_pages  = [ALL_PAGES[k] for k in page_keys]

    pg = st.navigation(nav_pages)

    sidebar_branding()

    role_colors = {
        "Admin":               "#4F6AF5",
        "Manager":             "#7C3AED",
        "Procurement Officer": "#059669",
        "Vendor":              "#D97706",
    }
    role_bgs = {
        "Admin":               "#EEF2FF",
        "Manager":             "#F5F3FF",
        "Procurement Officer": "#ECFDF5",
        "Vendor":              "#FFFBEB",
    }
    color = role_colors.get(role, "#64748B")
    bg    = role_bgs.get(role, "#F8FAFC")

    st.sidebar.markdown(f"""
    <div style="
        background:{bg}; border:1px solid {color}30;
        border-radius:8px; padding:0.7rem 1rem; margin-bottom:0.5rem;
    ">
        <div style="font-family:'Geist',sans-serif; font-size:0.65rem; font-weight:700;
            letter-spacing:0.08em; text-transform:uppercase; color:#94A3B8; margin-bottom:4px;">
            Active Session
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="display:inline-block; width:7px; height:7px; border-radius:50%;
                background:{color};"></span>
            <span style="font-family:'Geist',sans-serif; font-size:0.85rem;
                font-weight:600; color:{color};">{role}</span>
        </div>
        <div style="font-family:'Geist Mono',monospace; font-size:0.7rem; color:#94A3B8;
            margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
            {st.session_state.user_email}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if role == "Vendor" and st.session_state.vendor_id:
        st.sidebar.markdown(f"""
        <div style="font-family:'Geist Mono',monospace; font-size:0.7rem;
            color:#94A3B8; padding:0 0.25rem; margin-bottom:0.5rem;">
            Vendor ID: #{st.session_state.vendor_id}
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    if st.sidebar.button("Sign Out", use_container_width=True):
        for key in ["user_role", "user_email", "user_id", "vendor_id"]:
            st.session_state[key] = None
        st.rerun()

    pg.run()

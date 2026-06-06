import streamlit as st


def apply_global_styles():
    """
    Injects the VendorBridge global design system into every Streamlit page.
    Call this as the FIRST thing after session state checks on every page.
    Aesthetic: Industrial dark command center — navy base, amber accents, sharp typography.
    """
    st.markdown("""
    <style>
    /* =============================================
       VENDORBRIDGE DESIGN SYSTEM v1.0
       Aesthetic: Industrial Dark Command Center
    ============================================= */

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    /* ===== DESIGN TOKENS ===== */
    :root {
        --bg-base:       #080E1A;
        --bg-card:       #0D1526;
        --bg-elevated:   #142035;
        --bg-hover:      #1A2C44;
        --accent:        #F5A623;
        --accent-glow:   rgba(245, 166, 35, 0.15);
        --accent-border: rgba(245, 166, 35, 0.35);
        --blue:          #3B82F6;
        --success:       #10B981;
        --success-bg:    rgba(16, 185, 129, 0.1);
        --danger:        #EF4444;
        --danger-bg:     rgba(239, 68, 68, 0.1);
        --warning-bg:    rgba(245, 166, 35, 0.1);
        --text-primary:  #EFF4FB;
        --text-secondary:#8B9DB8;
        --text-muted:    #4A5A72;
        --border:        rgba(255, 255, 255, 0.06);
        --border-strong: rgba(255, 255, 255, 0.12);
        --shadow-sm:     0 2px 8px rgba(0,0,0,0.3);
        --shadow-md:     0 4px 20px rgba(0,0,0,0.45);
        --shadow-lg:     0 8px 40px rgba(0,0,0,0.6);
        --radius:        10px;
        --radius-sm:     6px;
        --radius-lg:     16px;
    }

    /* ===== BASE APP ===== */
    .stApp {
        background-color: var(--bg-base) !important;
        background-image:
            linear-gradient(rgba(245,166,35,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245,166,35,0.025) 1px, transparent 1px);
        background-size: 48px 48px;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Remove default Streamlit padding weirdness */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card) !important;
        border-right: 1px solid var(--border-strong) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.85rem !important;
    }

    /* Sidebar nav links */
    [data-testid="stSidebarNavLink"] {
        border-radius: var(--radius-sm) !important;
        margin: 2px 8px !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebarNavLink"]:hover {
        background-color: var(--bg-hover) !important;
    }

    [data-testid="stSidebarNavLink"][aria-current="page"] {
        background-color: var(--accent-glow) !important;
        border-left: 3px solid var(--accent) !important;
    }

    /* Sidebar success/info/warning alerts */
    [data-testid="stSidebar"] .stAlert {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
    }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }

    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }

    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
    }

    p, span, div, li {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-secondary) !important;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--border-strong) !important;
        box-shadow: var(--shadow-md) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricDelta"] {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.75rem !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-strong) !important;
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.15s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        background-color: var(--bg-hover) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        box-shadow: 0 0 16px var(--accent-glow) !important;
        transform: translateY(-1px) !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #080E1A !important;
        font-weight: 700 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #FFB84D !important;
        border-color: #FFB84D !important;
        color: #080E1A !important;
        box-shadow: 0 0 24px rgba(245,166,35,0.4) !important;
    }

    /* Form submit buttons */
    .stFormSubmitButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.02em !important;
        border-radius: var(--radius-sm) !important;
        background-color: var(--accent) !important;
        border: none !important;
        color: #080E1A !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.15s ease !important;
    }

    .stFormSubmitButton > button:hover {
        background-color: #FFB84D !important;
        box-shadow: 0 0 24px rgba(245,166,35,0.35) !important;
        transform: translateY(-1px) !important;
        color: #080E1A !important;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.9rem !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
        outline: none !important;
    }

    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    /* Date input */
    .stDateInput > div > div > input {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== DATAFRAMES / TABLES ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="stDataFrame"] thead th {
        background-color: var(--bg-elevated) !important;
        color: var(--text-muted) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid var(--border-strong) !important;
    }

    [data-testid="stDataFrame"] tbody tr {
        background-color: var(--bg-card) !important;
        border-bottom: 1px solid var(--border) !important;
        transition: background-color 0.1s ease !important;
    }

    [data-testid="stDataFrame"] tbody tr:hover {
        background-color: var(--bg-elevated) !important;
    }

    [data-testid="stDataFrame"] tbody td {
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid var(--border-strong) !important;
        gap: 0 !important;
        padding: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: var(--text-muted) !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.15s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
        background-color: var(--bg-elevated) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* ===== ALERTS / NOTIFICATIONS ===== */
    .stAlert {
        border-radius: var(--radius) !important;
        border: 1px solid !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.88rem !important;
    }

    div[data-baseweb="notification"] {
        border-radius: var(--radius) !important;
    }

    /* Success */
    .stAlert[data-baseweb="notification"][kind="positive"],
    div.element-container div[data-testid="stAlert"] div[class*="success"] {
        background-color: var(--success-bg) !important;
        border-color: rgba(16, 185, 129, 0.35) !important;
        color: #6EE7B7 !important;
    }

    /* Error */
    div.element-container div[data-testid="stAlert"] div[class*="error"] {
        background-color: var(--danger-bg) !important;
        border-color: rgba(239, 68, 68, 0.35) !important;
        color: #FCA5A5 !important;
    }

    /* Info */
    div.element-container div[data-testid="stAlert"] div[class*="info"] {
        background-color: var(--accent-glow) !important;
        border-color: var(--accent-border) !important;
        color: #FCD34D !important;
    }

    /* Warning */
    div.element-container div[data-testid="stAlert"] div[class*="warning"] {
        background-color: var(--warning-bg) !important;
        border-color: var(--accent-border) !important;
        color: #FCD34D !important;
    }

    /* ===== FORMS ===== */
    [data-testid="stForm"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }

    /* ===== DIVIDER ===== */
    hr {
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        background-color: var(--success-bg) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        color: #6EE7B7 !important;
        border-radius: var(--radius-sm) !important;
        transition: all 0.15s ease !important;
    }

    .stDownloadButton > button:hover {
        background-color: rgba(16, 185, 129, 0.2) !important;
        box-shadow: 0 0 16px rgba(16, 185, 129, 0.2) !important;
        color: #6EE7B7 !important;
    }

    /* ===== HIDE DEFAULT STREAMLIT ELEMENTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """
    Renders a styled page header to replace plain st.title() calls.
    Usage: page_header("Vendor Management", "Manage supplier records", "🏢")
    """
    st.markdown(f"""
    <div style="
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1.75rem;
    ">
        <div style="display:flex; align-items:center; gap: 0.75rem;">
            {'<span style="font-size:1.5rem">'+icon+'</span>' if icon else ''}
            <h1 style="
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 1.6rem;
                font-weight: 800;
                color: #EFF4FB;
                margin: 0;
                letter-spacing: -0.03em;
                line-height: 1.1;
            ">{title}</h1>
        </div>
        {'<p style="margin: 0.4rem 0 0 ' + ('2.25rem' if icon else '0') + '; color: #8B9DB8; font-size: 0.88rem; font-family: DM Sans, sans-serif;">' + subtitle + '</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(label: str):
    """
    Renders a subtle section divider label to replace st.subheader() and st.markdown('---').
    Usage: section_header("Active Vendors")
    """
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.5rem 0 1rem 0;
    ">
        <div style="
            width: 3px;
            height: 1.1rem;
            background: #F5A623;
            border-radius: 2px;
            flex-shrink: 0;
        "></div>
        <span style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #8B9DB8;
        ">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """
    Returns an HTML badge for a procurement status string.
    Usage: st.markdown(status_badge("Approved"), unsafe_allow_html=True)
    """
    colors = {
        "Draft":       ("#4A5A72", "#1A2235"),
        "Open":        ("#3B82F6", "rgba(59,130,246,0.12)"),
        "Under Review":("#F5A623", "rgba(245,166,35,0.12)"),
        "Approved":    ("#10B981", "rgba(16,185,129,0.12)"),
        "Closed":      ("#8B9DB8", "#0D1526"),
        "Submitted":   ("#3B82F6", "rgba(59,130,246,0.12)"),
        "Selected":    ("#10B981", "rgba(16,185,129,0.12)"),
        "Rejected":    ("#EF4444", "rgba(239,68,68,0.12)"),
        "Generated":   ("#F5A623", "rgba(245,166,35,0.12)"),
    }
    color, bg = colors.get(status, ("#8B9DB8", "#1A2235"))
    return f"""<span style="
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        font-family: 'DM Sans', sans-serif;
        color: {color};
        background-color: {bg};
        border: 1px solid {color}40;
    ">{status}</span>"""


def sidebar_branding():
    """
    Renders the VendorBridge logo/brand in the sidebar.
    Call this inside the 'else' block of your session state check in main.py.
    """
    st.sidebar.markdown("""
    <div style="
        padding: 1rem 0 1.25rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 0.5rem;
    ">
        <div style="display:flex; align-items:center; gap:0.6rem;">
            <div style="
                width: 32px; height: 32px;
                background: linear-gradient(135deg, #F5A623, #FF6B35);
                border-radius: 8px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1rem;
                flex-shrink: 0;
            ">🌉</div>
            <div>
                <div style="
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    font-size: 0.95rem;
                    font-weight: 800;
                    color: #EFF4FB;
                    letter-spacing: -0.02em;
                    line-height: 1;
                ">VendorBridge</div>
                <div style="
                    font-family: 'DM Sans', sans-serif;
                    font-size: 0.65rem;
                    color: #4A5A72;
                    letter-spacing: 0.06em;
                    text-transform: uppercase;
                    margin-top: 2px;
                ">Procurement ERP</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

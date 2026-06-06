import streamlit as st


def apply_global_styles():
    """
    VendorBridge Design System v2.0
    Aesthetic: Clean light procurement platform — crisp white, slate accents, indigo highlights.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800&family=Geist+Mono:wght@400;500&display=swap');

    /* ===== DESIGN TOKENS ===== */
    :root {
        --bg-base:        #F8FAFC;
        --bg-card:        #FFFFFF;
        --bg-elevated:    #F1F5F9;
        --bg-hover:       #E8EEF6;
        --accent:         #4F6AF5;
        --accent-light:   rgba(79, 106, 245, 0.10);
        --accent-border:  rgba(79, 106, 245, 0.30);
        --success:        #10B981;
        --success-bg:     rgba(16, 185, 129, 0.08);
        --danger:         #EF4444;
        --danger-bg:      rgba(239, 68, 68, 0.08);
        --warning:        #F59E0B;
        --warning-bg:     rgba(245, 158, 11, 0.08);
        --text-primary:   #0F172A;
        --text-secondary: #475569;
        --text-muted:     #94A3B8;
        --border:         #E2E8F0;
        --border-strong:  #CBD5E1;
        --shadow-sm:      0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md:      0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
        --shadow-lg:      0 8px 32px rgba(0,0,0,0.10);
        --radius:         10px;
        --radius-sm:      6px;
        --radius-lg:      14px;
    }

    /* ===== BASE ===== */
    .stApp {
        background-color: var(--bg-base) !important;
        font-family: 'Geist', sans-serif !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebarNavLink"] {
        border-radius: var(--radius-sm) !important;
        margin: 2px 8px !important;
        color: var(--text-secondary) !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stSidebarNavLink"]:hover {
        background-color: var(--bg-elevated) !important;
        color: var(--accent) !important;
    }

    [data-testid="stSidebarNavLink"][aria-current="page"] {
        background-color: var(--accent-light) !important;
        border-left: 3px solid var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4 {
        font-family: 'Geist', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }

    h1 { font-size: 1.7rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--text-secondary) !important; }

    p, span, div, li {
        font-family: 'Geist', sans-serif !important;
        color: var(--text-secondary) !important;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.2rem 1.4rem !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Geist', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Geist', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Geist', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-strong) !important;
        background-color: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        padding: 0.5rem 1.1rem !important;
        transition: all 0.15s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        background-color: var(--bg-elevated) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    .stButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #3B55E8 !important;
        border-color: #3B55E8 !important;
        color: #FFFFFF !important;
    }

    .stFormSubmitButton > button {
        font-family: 'Geist', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        border-radius: var(--radius-sm) !important;
        background-color: var(--accent) !important;
        border: none !important;
        color: #FFFFFF !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 2px 8px rgba(79,106,245,0.25) !important;
    }

    .stFormSubmitButton > button:hover {
        background-color: #3B55E8 !important;
        box-shadow: 0 4px 16px rgba(79,106,245,0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 0.9rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-light) !important;
        outline: none !important;
    }

    .stTextInput label, .stTextArea label,
    .stNumberInput label, .stSelectbox label, .stDateInput label {
        font-family: 'Geist', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
    }

    .stSelectbox > div > div {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    .stDateInput > div > div > input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== DATAFRAMES ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    [data-testid="stDataFrame"] thead th {
        background-color: var(--bg-elevated) !important;
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
    }

    [data-testid="stDataFrame"] tbody tr { background-color: var(--bg-card) !important; }
    [data-testid="stDataFrame"] tbody tr:hover { background-color: var(--bg-elevated) !important; }
    [data-testid="stDataFrame"] tbody td { color: var(--text-primary) !important; font-size: 0.88rem !important; }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 2px solid var(--border) !important;
        gap: 0 !important; padding: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Geist', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: var(--text-muted) !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.75rem 1.25rem !important;
        transition: all 0.15s !important;
        margin-bottom: -2px !important;
    }

    .stTabs [data-baseweb="tab"]:hover { color: var(--text-secondary) !important; }
    .stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

    /* ===== ALERTS ===== */
    .stAlert {
        border-radius: var(--radius) !important;
        border: 1px solid !important;
        font-family: 'Geist', sans-serif !important;
        font-size: 0.88rem !important;
    }

    /* ===== FORMS ===== */
    [data-testid="stForm"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background-color: var(--success-bg) !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        color: #059669 !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== HIDE DEFAULTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebarNav"] { display: none !important; }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }

    /* ===== SPINNER ===== */
    .stSpinner > div { border-top-color: var(--accent) !important; }

    hr { border-color: var(--border) !important; }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.75rem;">
        <div style="display:flex; align-items:center; gap:0.65rem;">
            {'<span style="font-size:1.4rem">'+icon+'</span>' if icon else ''}
            <h1 style="font-family:'Geist',sans-serif; font-size:1.55rem; font-weight:700;
                color:#0F172A; margin:0; letter-spacing:-0.03em; line-height:1.1;">{title}</h1>
        </div>
        {'<p style="margin:0.4rem 0 0 '+ ('2.1rem' if icon else '0') +'; color:#64748B; font-size:0.875rem;">'+subtitle+'</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(label: str):
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.65rem; margin:1.5rem 0 1rem 0;">
        <div style="width:3px; height:1rem; background:#4F6AF5; border-radius:2px; flex-shrink:0;"></div>
        <span style="font-family:'Geist',sans-serif; font-size:0.7rem; font-weight:700;
            letter-spacing:0.1em; text-transform:uppercase; color:#64748B;">{label}</span>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    configs = {
        "Draft":        ("#64748B", "#F1F5F9", "#CBD5E1"),
        "Open":         ("#4F6AF5", "#EEF2FF", "#C7D2FE"),
        "Under Review": ("#D97706", "#FFFBEB", "#FDE68A"),
        "Approved":     ("#059669", "#ECFDF5", "#A7F3D0"),
        "Closed":       ("#94A3B8", "#F8FAFC", "#E2E8F0"),
        "Submitted":    ("#4F6AF5", "#EEF2FF", "#C7D2FE"),
        "Selected":     ("#059669", "#ECFDF5", "#A7F3D0"),
        "Rejected":     ("#DC2626", "#FEF2F2", "#FECACA"),
        "Generated":    ("#D97706", "#FFFBEB", "#FDE68A"),
    }
    color, bg, border = configs.get(status, ("#64748B", "#F1F5F9", "#CBD5E1"))
    return f"""<span style="
        display:inline-block; padding:0.2rem 0.6rem; border-radius:20px;
        font-size:0.7rem; font-weight:600; letter-spacing:0.04em;
        font-family:'Geist',sans-serif; color:{color};
        background-color:{bg}; border:1px solid {border};
    ">{status}</span>"""


def sidebar_branding():
    st.sidebar.markdown("""
    <div style="padding:1rem 0 1.25rem 0; border-bottom:1px solid #E2E8F0; margin-bottom:0.5rem;">
        <div style="display:flex; align-items:center; gap:0.55rem;">
            <div style="
                width:32px; height:32px;
                background:linear-gradient(135deg,#4F6AF5,#818CF8);
                border-radius:8px; display:flex; align-items:center;
                justify-content:center; font-size:1rem; flex-shrink:0;
            ">🌉</div>
            <div>
                <div style="font-family:'Geist',sans-serif; font-size:0.95rem; font-weight:700;
                    color:#0F172A; letter-spacing:-0.02em; line-height:1.1;">VendorBridge</div>
                <div style="font-family:'Geist',sans-serif; font-size:0.62rem; color:#94A3B8;
                    letter-spacing:0.06em; text-transform:uppercase; margin-top:1px;">Procurement ERP</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def info_card(title: str, body: str, color: str = "#4F6AF5"):
    """A styled info/notice card for in-page callouts."""
    bg = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)"
    border = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.25)"
    st.markdown(f"""
    <div style="background:{bg}; border:1px solid {border}; border-radius:8px;
        padding:0.8rem 1rem; margin:0.5rem 0;
        font-family:'Geist',sans-serif; font-size:0.85rem; color:{color};">
        <strong>{title}</strong>&nbsp; {body}
    </div>
    """, unsafe_allow_html=True)

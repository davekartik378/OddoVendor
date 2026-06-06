import streamlit as st
import requests
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header, status_badge

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Access Denied. Please log in from the main portal.")
    st.stop()

apply_global_styles()
page_header("Dashboard", "Real-time procurement overview and system health", "📊")

API_URL = "http://localhost:8000"

@st.cache_data(ttl=10)
def fetch_data():
    try:
        rfqs = requests.get(f"{API_URL}/rfqs/").json()
        vendors = requests.get(f"{API_URL}/vendors/").json()
        return rfqs, vendors
    except Exception:
        return None, None

rfqs, vendors = fetch_data()

if rfqs is None:
    st.error("Cannot connect to backend. Make sure uvicorn is running on port 8000.")
    st.stop()

# ── METRIC CARDS ────────────────────────────────────────────────────────────────
total_rfqs    = len(rfqs)
open_rfqs     = len([r for r in rfqs if r.get("status") == "Open"])
pending_appr  = len([r for r in rfqs if r.get("status") == "Open"])
approved      = len([r for r in rfqs if r.get("status") == "Approved"])
closed        = len([r for r in rfqs if r.get("status") == "Closed"])
total_vendors = len(vendors)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total RFQs",       total_rfqs)
c2.metric("Open / Active",    open_rfqs)
c3.metric("Pending Approval", pending_appr)
c4.metric("Registered Vendors", total_vendors)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── CHARTS ───────────────────────────────────────────────────────────────────────
section_header("Procurement Lifecycle Breakdown")

if total_rfqs > 0:
    df = pd.DataFrame(rfqs)
    col_chart, col_recent = st.columns([3, 2])

    with col_chart:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.bar_chart(status_counts.set_index("Status"), use_container_width=True, height=260)

    with col_recent:
        section_header("Recent RFQs")
        for r in rfqs[-5:][::-1]:
            badge = status_badge(r.get("status", "Draft"))
            st.markdown(
                f"""<div style="
                    display:flex; justify-content:space-between; align-items:center;
                    padding:0.6rem 0.75rem; margin-bottom:6px;
                    background:#0D1526; border:1px solid rgba(255,255,255,0.06);
                    border-radius:8px;
                ">
                    <span style="font-family:'DM Sans',sans-serif; font-size:0.82rem;
                        color:#EFF4FB; font-weight:500;">
                        #{r['id']} · {r['title'][:28]}{'…' if len(r['title'])>28 else ''}
                    </span>
                    {badge}
                </div>""",
                unsafe_allow_html=True,
            )
else:
    st.info("No procurement data yet. Create your first RFQ to get started.")

# ── VENDOR HEALTH OVERVIEW ───────────────────────────────────────────────────────
if vendors:
    section_header("Vendor Health Snapshot")
    vdf = pd.DataFrame(vendors)[["name", "category", "health_score"]]
    vdf.columns = ["Vendor", "Category", "Health Score ★"]
    st.dataframe(vdf, use_container_width=True, hide_index=True)

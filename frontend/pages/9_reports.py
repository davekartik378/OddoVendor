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
page_header("Reports & Analytics", "Procurement insights, vendor performance, and spending trends", "📈")

API_URL = "http://localhost:8000"

if st.session_state.user_role not in ["Admin", "Manager"]:
    st.error("Access Restricted — only Admins and Managers can view analytics.")
    st.stop()

# ── FETCH ─────────────────────────────────────────────────────────────────────────
try:
    res = requests.get(f"{API_URL}/analytics/summary")
    data = res.json() if res.status_code == 200 else {}
except Exception:
    data = {}
    st.error("Cannot connect to backend.")
    st.stop()

if not data:
    st.info("No data available yet. Start creating RFQs and registering vendors to see analytics.")
    st.stop()

# ── TOP METRICS ROW ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total RFQs",       data.get("total_rfqs", 0))
c2.metric("Total Vendors",    data.get("total_vendors", 0))
c3.metric("Total Quotations", data.get("total_quotations", 0))
c4.metric("Purchase Orders",  data.get("total_pos", 0))

# ── TOP VENDOR + AVG HEALTH ────────────────────────────────────────────────────────
top = data.get("top_vendor")
avg_health = data.get("avg_health_score", 0)

col_top, col_health = st.columns(2)

with col_top:
    if top:
        st.markdown(
            f"""<div style="
                background:#0D1526; border:1px solid rgba(245,166,35,0.2);
                border-radius:10px; padding:1.1rem 1.3rem; margin-top:0.5rem;
            ">
                <div style="font-family:'DM Sans',sans-serif; font-size:0.7rem;
                    font-weight:600; letter-spacing:0.08em; text-transform:uppercase;
                    color:#4A5A72; margin-bottom:0.4rem;">Top Performing Vendor</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:1.2rem; font-weight:700; color:#EFF4FB;">
                    {top['name']}
                </div>
                <div style="font-family:'DM Mono',monospace; font-size:0.82rem;
                    color:#F5A623; margin-top:2px;">
                    Health Score: {top['score']} ★
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

with col_health:
    st.markdown(
        f"""<div style="
            background:#0D1526; border:1px solid rgba(255,255,255,0.06);
            border-radius:10px; padding:1.1rem 1.3rem; margin-top:0.5rem;
        ">
            <div style="font-family:'DM Sans',sans-serif; font-size:0.7rem;
                font-weight:600; letter-spacing:0.08em; text-transform:uppercase;
                color:#4A5A72; margin-bottom:0.4rem;">Network Avg Health Score</div>
            <div style="font-family:'Plus Jakarta Sans',sans-serif;
                font-size:1.2rem; font-weight:700; color:#EFF4FB;">
                {avg_health} / 5.0
            </div>
            <div style="
                margin-top:0.5rem; height:6px; background:#142035;
                border-radius:3px; overflow:hidden;
            ">
                <div style="
                    width:{(avg_health/5)*100:.1f}%; height:100%;
                    background:linear-gradient(90deg,#F5A623,#10B981);
                    border-radius:3px;
                "></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── CHARTS ROW 1: STATUS BREAKDOWN + CATEGORY DISTRIBUTION ────────────────────────
col_status, col_cat = st.columns(2)

with col_status:
    section_header("RFQ Status Breakdown")
    status_data = data.get("status_breakdown", {})
    if status_data:
        df_status = pd.DataFrame(
            list(status_data.items()), columns=["Status", "Count"]
        ).set_index("Status")
        st.bar_chart(df_status, use_container_width=True, height=220)
    else:
        st.info("No RFQ data yet.")

with col_cat:
    section_header("Vendor Category Distribution")
    cat_data = data.get("category_dist", {})
    if cat_data:
        df_cat = pd.DataFrame(
            list(cat_data.items()), columns=["Category", "Vendors"]
        ).set_index("Category")
        st.bar_chart(df_cat, use_container_width=True, height=220)
    else:
        st.info("No vendor data yet.")

# ── CHARTS ROW 2: MONTHLY TREND + VENDOR SPEND ───────────────────────────────────
col_trend, col_spend = st.columns(2)

with col_trend:
    section_header("Monthly RFQ Trend")
    monthly = data.get("monthly_trend", {})
    if monthly:
        df_monthly = pd.DataFrame(
            list(monthly.items()), columns=["Month", "RFQs"]
        ).set_index("Month")
        st.line_chart(df_monthly, use_container_width=True, height=220)
    else:
        st.info("Not enough data for trend analysis.")

with col_spend:
    section_header("Vendor Spend Distribution (₹)")
    spend = data.get("vendor_spend", {})
    if spend:
        df_spend = pd.DataFrame(
            list(spend.items()), columns=["Vendor", "Total Spend (₹)"]
        ).set_index("Vendor")
        st.bar_chart(df_spend, use_container_width=True, height=220)
    else:
        st.info("No completed purchases yet.")

# ── EXPORTABLE SUMMARY TABLE ──────────────────────────────────────────────────────
section_header("Export Summary")

summary_rows = [
    {"Metric": "Total RFQs Created",       "Value": data.get("total_rfqs", 0)},
    {"Metric": "Registered Vendors",        "Value": data.get("total_vendors", 0)},
    {"Metric": "Quotations Received",       "Value": data.get("total_quotations", 0)},
    {"Metric": "Purchase Orders Generated", "Value": data.get("total_pos", 0)},
    {"Metric": "Avg Vendor Health Score",   "Value": f"{avg_health} / 5.0"},
    {"Metric": "Top Vendor",               "Value": top["name"] if top else "N/A"},
]

df_summary = pd.DataFrame(summary_rows)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

# CSV export
csv = df_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Export Report as CSV",
    data=csv,
    file_name="vendorbridge_report.csv",
    mime="text/csv",
)

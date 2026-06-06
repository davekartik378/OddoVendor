import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Dashboard | VendorBridge", page_icon="📊", layout="wide")

# Security Check: Kick user out if not logged in
if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in from the main portal.")
    st.stop()

st.title(f"📊 {st.session_state.user_role} Dashboard")
st.markdown("Real-time procurement analytics and system health.")
st.markdown("---")

API_URL = "http://localhost:8000"

# --- DATA FETCHING ENGINE ---
@st.cache_data(ttl=5) # Caches data for 5 seconds to prevent backend spamming
def fetch_system_data():
    try:
        rfqs_res = requests.get(f"{API_URL}/rfqs/")
        vendors_res = requests.get(f"{API_URL}/vendors/")
        
        rfqs = rfqs_res.json() if rfqs_res.status_code == 200 else []
        vendors = vendors_res.json() if vendors_res.status_code == 200 else []
        return rfqs, vendors
    except requests.exceptions.ConnectionError:
        return None, None

rfqs, vendors = fetch_system_data()

if rfqs is None:
    st.error("🚨 CRITICAL: Cannot connect to FastAPI backend. Ensure uvicorn is running on port 8000.")
    st.stop()

# --- TOP LEVEL METRICS ---
col1, col2, col3, col4 = st.columns(4)

total_rfqs = len(rfqs)
active_rfqs = len([r for r in rfqs if r.get('status') == 'Open'])
total_vendors = len(vendors)

col1.metric(label="Total RFQs Initiated", value=total_rfqs)
col2.metric(label="Open / Active RFQs", value=active_rfqs)
col3.metric(label="Registered Vendors", value=total_vendors)
col4.metric(label="System Status", value="Online", delta="0ms Latency", delta_color="normal")

st.markdown("---")

# --- SMART ANALYTICS (PANDAS IN ACTION) ---
st.subheader("Procurement Lifecycle Activity")

if total_rfqs > 0:
    # Convert the JSON response directly into a Pandas DataFrame
    df = pd.DataFrame(rfqs)
    
    # Group by status to see where everything is bottlenecked
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    col_chart, col_data = st.columns([2, 1])
    
    with col_chart:
        st.bar_chart(status_counts.set_index('Status'), use_container_width=True)
        
    with col_data:
        st.dataframe(status_counts, hide_index=True, use_container_width=True)
else:
    st.info("No active procurement data available. Head to the RFQ module to generate the first request.")
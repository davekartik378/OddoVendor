import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Quotation Matrix", page_icon="⚖️", layout="wide")

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("🔒 Access Denied. Please log in.")
    st.stop()

st.title("⚖️ Quotation Comparison Matrix")
st.markdown("Analyze vendor bids side-by-side and leverage the Smart Advisor engine.")
st.markdown("---")

API_URL = "http://localhost:8000"

if st.session_state.user_role in ["Vendor"]:
    st.error("Action Restricted. Vendors cannot view competitor pricing matrices.")
    st.stop()

# Fetch all RFQs to select from
try:
    rfqs = requests.get(f"{API_URL}/rfqs/").json()
    rfq_dict = {f"RFQ #{r['id']} - {r['title']}": r['id'] for r in rfqs}
except:
    rfq_dict = {}

if not rfq_dict:
    st.info("No RFQs exist in the system yet.")
    st.stop()

selected_rfq = st.selectbox("Select RFQ to Analyze", list(rfq_dict.keys()))
rfq_id = rfq_dict[selected_rfq]

st.markdown("### Submitted Bids")

# Fetch Quotations for this specific RFQ
quotes_res = requests.get(f"{API_URL}/rfqs/{rfq_id}/quotations/")

if quotes_res.status_code == 200 and quotes_res.json():
    quotes = quotes_res.json()
    df = pd.DataFrame(quotes)
    
    # Format the dataframe for the matrix
    display_df = df[['vendor_name', 'unit_price', 'delivery_days', 'health_score', 'remarks']]
    display_df.columns = ['Vendor', 'Unit Price (₹)', 'Delivery (Days)', 'Health (★)', 'Remarks']
    
    # Pandas styling: Highlight the lowest price in green and fastest delivery in light blue
    styled_df = display_df.style.highlight_min(subset=['Unit Price (₹)'], color='#a8e6cf') \
                                .highlight_min(subset=['Delivery (Days)'], color='#dcedc1')
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- NOVELTY 1: THE LOCAL SMART ADVISOR ---
    st.subheader("🧠 Offline Smart Advisor")
    st.write("Click below to run the local heuristic engine. It evaluates price, speed, and historical vendor reliability.")
    
    if st.button("Run Value Optimization Analysis", type="primary"):
        with st.spinner("Crunching data locally via Pandas..."):
            advisor_res = requests.get(f"{API_URL}/engine/advisor/{rfq_id}")
            if advisor_res.status_code == 200:
                data = advisor_res.json()
                st.success(data["recommendation"])
            else:
                st.error("Engine failed to calculate.")

else:
    st.warning("No quotations have been submitted for this RFQ yet.")
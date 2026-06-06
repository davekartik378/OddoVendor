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
page_header("Purchase Orders & Invoices", "Generate, download, and email official procurement documents", "🖨️")

API_URL = "http://localhost:8000"

if st.session_state.user_role not in ["Procurement Officer", "Admin"]:
    st.error("Access Restricted — only Procurement Officers can generate POs and Invoices.")
    st.stop()

# ── FETCH APPROVED RFQs ───────────────────────────────────────────────────────────
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    approved_rfqs = [r for r in rfqs_res.json() if r.get("status") == "Approved"]
except Exception:
    approved_rfqs = []

if not approved_rfqs:
    st.info("No approved RFQs pending fulfillment. Approve a procurement request first.")
    st.stop()

section_header("Approved RFQs — Ready for Fulfillment")

df = pd.DataFrame(approved_rfqs)
display_df = df[["id", "title", "quantity"]].copy()
display_df.columns = ["RFQ ID", "Project Title", "Quantity"]
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── GENERATE PO ───────────────────────────────────────────────────────────────────
section_header("Generate Purchase Order & Invoice")

rfq_options = {f"RFQ #{r['id']} · {r['title']}": r['id'] for r in approved_rfqs}

with st.form("po_generator_form"):
    selected_rfq = st.selectbox("Select Project to Finalise *", list(rfq_options.keys()))
    submitted = st.form_submit_button("Generate Official PO & Invoice PDF", use_container_width=True)

    if submitted:
        target_id = rfq_options[selected_rfq]
        with st.spinner("Compiling PDF document…"):
            res = requests.post(f"{API_URL}/generate-po/{target_id}")

        if res.status_code == 200:
            data = res.json()
            po_number = data["po_number"]

            st.success(f"Generated {po_number} successfully. The RFQ is now Closed.")

            # Store PO number in session so the email form below can use it
            st.session_state["last_po_number"] = po_number

            # Download button
            pdf_res = requests.get(f"{API_URL}/download-invoice/{po_number}")
            if pdf_res.status_code == 200:
                st.download_button(
                    label="Download Invoice PDF",
                    data=pdf_res.content,
                    file_name=f"{po_number}.pdf",
                    mime="application/pdf",
                )
        else:
            st.error(f"PO generation failed: {res.text}")

# ── SEND INVOICE VIA EMAIL ────────────────────────────────────────────────────────
section_header("Send Invoice by Email")

po_number = st.session_state.get("last_po_number", "")

if not po_number:
    st.markdown(
        "<p style='font-size:0.85rem; color:#4A5A72;'>"
        "Generate a PO above first, then send the invoice directly from here."
        "</p>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<p style='font-size:0.85rem; color:#8B9DB8;'>Ready to send: <code style='color:#F5A623'>{po_number}</code></p>",
        unsafe_allow_html=True,
    )
    with st.form("email_form"):
        recipient = st.text_input("Recipient Email *", placeholder="vendor@company.com")
        send = st.form_submit_button("Send Invoice via Email", use_container_width=True)

        if send:
            if not recipient or "@" not in recipient:
                st.error("Please enter a valid email address.")
            else:
                with st.spinner("Sending email…"):
                    res = requests.post(
                        f"{API_URL}/send-invoice/{po_number}?recipient_email={recipient}"
                    )
                if res.status_code == 200:
                    st.success(f"Invoice sent to {recipient} successfully.")
                else:
                    err = res.json().get("detail", res.text)
                    st.error(f"Email failed: {err}")
                    st.info("Tip: Update SENDER_EMAIL and SENDER_PASSWORD in backend/app.py with your Gmail App Password credentials.")

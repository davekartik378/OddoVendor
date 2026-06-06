import streamlit as st
import requests
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import apply_global_styles, page_header, section_header, status_badge, info_card

if "user_role" not in st.session_state or st.session_state.user_role is None:
    st.warning("Please log in to access this page.")
    st.stop()

apply_global_styles()
page_header("Approval Workflow", "Review and authorise procurement decisions", "✅")

API_URL = "http://localhost:8000"

if st.session_state.user_role not in ["Manager", "Admin"]:
    st.error(f"Access Restricted — '{st.session_state.user_role}' cannot authorise procurement.")
    st.stop()

# ── FETCH RFQs READY FOR APPROVAL ────────────────────────────────────────────
# Only RFQs in "Under Review" state are ready for manager approval.
# Procurement Officer must have explicitly submitted them for review.
try:
    rfqs_res = requests.get(f"{API_URL}/rfqs/")
    pending_rfqs = [r for r in rfqs_res.json() if r.get("status") == "Under Review"]
except Exception:
    pending_rfqs = []

if not pending_rfqs:
    st.markdown("""
    <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px;
        padding:2rem; text-align:center;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">✅</div>
        <p style="color:#166534; font-size:0.9rem; margin:0;">
            No RFQs awaiting approval right now. All clear!
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

section_header("Requests Under Review")

rfq_dict = {f"RFQ #{r['id']} · {r['title']}": r['id'] for r in pending_rfqs}
selected_label = st.selectbox("Select Request", list(rfq_dict.keys()))
rfq_id = rfq_dict[selected_label]

# ── QUOTATION TABLE ───────────────────────────────────────────────────────────
section_header("Available Quotations")

quotes_res = requests.get(f"{API_URL}/rfqs/{rfq_id}/quotations/")

if quotes_res.status_code == 200 and quotes_res.json():
    quotes = quotes_res.json()
    df = pd.DataFrame(quotes)

    display_df = df[["id", "vendor_name", "unit_price", "delivery_days", "health_score"]].copy()
    display_df.columns = ["Quote ID", "Vendor", "Unit Price (₹)", "Delivery (Days)", "Health ★"]
    st.dataframe(display_df.style.highlight_min(subset=["Unit Price (₹)"], color="#D1FAE5"),
                 use_container_width=True, hide_index=True)

    # ── APPROVAL FORM ─────────────────────────────────────────────────────────
    section_header("Sign Off & Authorise")

    quote_labels = {
        f"Quote #{q['id']} · {q['vendor_name']} · ₹{q['unit_price']} · {q['delivery_days']} days": q['id']
        for q in quotes
    }

    with st.form("approval_form"):
        selected_quote_label = st.selectbox("Select Winning Bid *", list(quote_labels.keys()))
        remarks = st.text_input(
            "Approval Remarks *",
            placeholder="e.g., Selected for fastest delivery and competitive pricing."
        )

        st.markdown("""
        <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:8px;
            padding:0.75rem 1rem; margin:0.5rem 0;
            font-family:'Geist',sans-serif; font-size:0.82rem; color:#92400E;">
            🔐 Submitting this form generates a SHA-256 cryptographic hash and permanently
            locks this decision into the audit ledger. This action cannot be undone.
        </div>""", unsafe_allow_html=True)

        col_approve, col_reject = st.columns(2)
        with col_approve:
            submitted = st.form_submit_button("✅ Approve & Digitally Sign", use_container_width=True)

        if submitted:
            if not remarks.strip():
                st.error("Approval remarks are required for the audit log.")
            else:
                winning_id = quote_labels[selected_quote_label]
                manager_id = st.session_state.get("user_id") or 1
                res = requests.post(
                    f"{API_URL}/rfqs/{rfq_id}/approve"
                    f"?winning_quote_id={winning_id}&manager_id={manager_id}&remarks={remarks}"
                )
                if res.status_code == 200:
                    st.success("Approved! RFQ locked. Losing vendors marked as rejected.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Approval failed: {res.text}")

    # ── REJECT OPTION ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.expander("❌ Reject this RFQ (return to Open)"):
        reject_reason = st.text_input("Rejection Reason *", placeholder="Explain why this RFQ is being returned…")
        if st.button("Reject & Return to Open", type="primary"):
            if not reject_reason.strip():
                st.error("Please provide a rejection reason.")
            else:
                upd = requests.patch(f"{API_URL}/rfqs/{rfq_id}/status?new_status=Open")
                if upd.status_code == 200:
                    st.warning(f"RFQ #{rfq_id} returned to Open status.")
                    st.rerun()
                else:
                    st.error("Failed to update status.")
else:
    st.markdown("""
    <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:10px;
        padding:1.5rem; text-align:center;">
        <p style="color:#92400E; font-size:0.88rem; margin:0;">
            No quotations submitted for this RFQ yet.
        </p>
    </div>
    """, unsafe_allow_html=True)

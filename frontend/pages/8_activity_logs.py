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
page_header("Activity Logs", "Cryptographically secured procurement audit trail", "🔐")

API_URL = "http://localhost:8000"

# Only Admin and Manager can view full audit trail
if st.session_state.user_role not in ["Admin", "Manager"]:
    st.error("Access Restricted — only Admins and Managers can view the audit ledger.")
    st.stop()

# ── FETCH LOGS ────────────────────────────────────────────────────────────────────
try:
    res = requests.get(f"{API_URL}/audit-logs/")
    logs = res.json() if res.status_code == 200 else []
except Exception:
    logs = []
    st.error("Cannot connect to backend.")
    st.stop()

# ── INTEGRITY BANNER ──────────────────────────────────────────────────────────────
col_stat, col_info = st.columns([1, 3])
with col_stat:
    st.metric("Total Log Entries", len(logs))
with col_info:
    st.markdown(
        """<div style="
            background: rgba(245,166,35,0.07);
            border: 1px solid rgba(245,166,35,0.2);
            border-radius: 10px;
            padding: 0.8rem 1.1rem;
            margin-top: 0.25rem;
        ">
            <span style="
                font-family:'DM Sans',sans-serif; font-size:0.82rem; color:#FCD34D;
            ">
                🔗 Each entry is SHA-256 hashed and chained to the previous record —
                any tampering breaks the hash chain, making this ledger
                cryptographically tamper-evident.
            </span>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

if not logs:
    st.info("No audit entries yet. Approvals and key actions will be logged here automatically.")
    st.stop()

# ── TIMELINE VIEW ─────────────────────────────────────────────────────────────────
section_header("Audit Timeline")

for log in logs:
    timestamp = str(log.get("timestamp", ""))[:19].replace("T", " · ")
    action    = log.get("action", "")
    entry_id  = log.get("id", "")
    curr_hash = log.get("current_hash", "")
    prev_hash = log.get("previous_hash", "")

    st.markdown(
        f"""<div style="
            display: flex;
            gap: 1rem;
            margin-bottom: 0.6rem;
        ">
            <!-- Timeline spine -->
            <div style="
                display: flex; flex-direction: column;
                align-items: center; flex-shrink: 0;
            ">
                <div style="
                    width: 10px; height: 10px; border-radius: 50%;
                    background: #F5A623;
                    box-shadow: 0 0 8px rgba(245,166,35,0.5);
                    margin-top: 4px; flex-shrink: 0;
                "></div>
                <div style="
                    width: 1px; flex: 1; min-height: 32px;
                    background: rgba(245,166,35,0.15);
                    margin-top: 4px;
                "></div>
            </div>
            <!-- Entry card -->
            <div style="
                flex: 1;
                background: #0D1526;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 10px;
                padding: 0.75rem 1rem;
                margin-bottom: 0.2rem;
            ">
                <div style="
                    display: flex; justify-content: space-between;
                    align-items: flex-start; gap: 1rem;
                ">
                    <span style="
                        font-family: 'DM Sans', sans-serif;
                        font-size: 0.88rem; color: #EFF4FB;
                        font-weight: 500; line-height: 1.4;
                        flex: 1;
                    ">{action}</span>
                    <span style="
                        font-family: 'DM Mono', monospace;
                        font-size: 0.7rem; color: #4A5A72;
                        white-space: nowrap; flex-shrink: 0;
                    ">{timestamp}</span>
                </div>
                <div style="
                    margin-top: 0.4rem;
                    display: flex; gap: 1.5rem;
                ">
                    <span style="
                        font-family: 'DM Mono', monospace;
                        font-size: 0.68rem; color: #4A5A72;
                    ">#{entry_id} · Hash: <span style="color:#F5A62390">{curr_hash}</span></span>
                    <span style="
                        font-family: 'DM Mono', monospace;
                        font-size: 0.68rem; color: #2A3A52;
                    ">Prev: {prev_hash}</span>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

# ── RAW TABLE VIEW ────────────────────────────────────────────────────────────────
with st.expander("View as Raw Table"):
    df = pd.DataFrame(logs)
    df.columns = ["ID", "User ID", "Action", "Timestamp", "Hash (truncated)", "Prev Hash"]
    st.dataframe(df, use_container_width=True, hide_index=True)

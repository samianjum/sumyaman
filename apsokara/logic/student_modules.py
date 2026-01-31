import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def render_apply_leave(u):
    st.markdown("""
        <style>
        .premium-card {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 20px !important;
            padding: 25px !important;
            border: 1px solid #E9D5FF !important;
            box-shadow: 0 10px 30px rgba(124, 58, 237, 0.1) !important;
            margin-bottom: 25px !important;
        }
        .history-item {
            background: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
            border-left: 5px solid #7C3AED !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
        }
        .status-badge {
            float: right;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. APPLICATION FORM
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1E1B4B; margin:0;'>📝 Apply for Leave</h2>", unsafe_allow_html=True)
    with st.form("new_leave_form", border=False):
        c1, c2 = st.columns(2)
        start = c1.date_input("From Date", date.today())
        end = c2.date_input("To Date", date.today())
        reason = st.text_area("Reason for Leave")
        if st.form_submit_button("🚀 Submit Request", width='stretch'):
            if reason.strip():
                with sqlite3.connect("db.sqlite3", timeout=30) as conn:
                    conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)", 
                                 (u['id_num'], u.get('full_name', u.get('name')), u['class'], u.get('sec', u.get('section', '')), u.get('wing',''), reason, str(start), str(end), 'Pending'))
                st.success("Application Sent!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. PERSONAL HISTORY (Always Visible)
    st.markdown("<h3 style='color:#4C1D95;'>📜 My Leave History</h3>", unsafe_allow_html=True)
    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
        df = pd.read_sql("SELECT * FROM apsokara_studentleave WHERE student_id=? ORDER BY id DESC", conn, params=(u['id_num'],))
    
    if df.empty:
        st.info("No previous leaves found.")
    else:
        for _, r in df.iterrows():
            color = "#D97706" if r['status'] == "Pending" else ("#16A34A" if r['status'] == "Approved" else "#DC2626")
            st.markdown(f"""
                <div class="history-item">
                    <span class="status-badge" style="background:{color}22; color:{color};">{r['status']}</span>
                    <b style="color:#1E1B4B;">{r['reason']}</b><br>
                    <small style="color:#64748B;">Duration: {r['from_date']} to {r['to_date']}</small>
                </div>
            """, unsafe_allow_html=True)

def render_my_result(u):
    st.title("My Results")

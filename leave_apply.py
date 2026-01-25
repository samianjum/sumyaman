from datetime import datetime
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def render_leave_apply(u):
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid #fee2e2;
            border-radius: 12px;
            padding: 10px 25px;
            color: #b91c1c;
        }
        .stTabs [aria-selected="true"] {
            background: #dc2626 !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(220, 38, 38, 0.1);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        }
        .history-card {
            background: white;
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 12px;
            border-left: 5px solid #dc2626;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        .status-tag {
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📝 Apply New", "📜 My History"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("st_form_new", border=False):
            c1, c2 = st.columns(2)
            start = c1.date_input("From Date", date.today())
            end = c2.date_input("To Date", date.today())
            reason = st.text_area("Reason for Leave", placeholder="Detailed reason...")
            if st.form_submit_button("🚀 Submit Request", use_container_width=True):
                if reason.strip():
                    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
                        conn.execute("INSERT INTO apsokara_studentleave (student_id, class, section, wing, reason, from_date, to_date, status, applied_on) VALUES (?,?,?,?,?,?,?,?,?)", 
                                     (u.get('id'), u.get('class'), u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending', datetime.now()))
                    st.success("Application Sent Successfully!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### Filter History")
        f_date = st.date_input("Select Date", value=None)
        
        query = "SELECT * FROM apsokara_studentleave WHERE student_id=?"
        params = [u['id_num']]
        if f_date:
            query += " AND ? BETWEEN from_date AND to_date"
            params.append(str(f_date))
        
        with sqlite3.connect("db.sqlite3", timeout=30) as conn:
            df = pd.read_sql(query + " ORDER BY id DESC", conn, params=params)
        
        if df.empty: st.info("No records found.")
        for _, r in df.iterrows():
            read_status = "✅ Viewed" if r['is_read'] == 1 else "📩 Unread"
            color = "#fef2f2" if r['status'] == "Pending" else "#f0fdf4"
            txt_color = "#991b1b" if r['status'] == "Pending" else "#166534"
            
            st.markdown(f"""
            <div class="history-card" style="background: {color};">
                <div style="display:flex; justify-content:space-between;">
                    <b style="color:#1e1b4b;">{r['from_date']} to {r['to_date']}</b>
                    <span class="status-tag" style="background:white; color:{txt_color}; border:1px solid {txt_color};">{r['status']}</span>
                </div>
                <p style="margin:10px 0; font-size:0.9rem;">{r['reason']}</p>
                <div style="font-size:0.75rem; color:#64748b; font-weight:bold;">Status: {read_status}</div>
            </div>
            """, unsafe_allow_html=True)

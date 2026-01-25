import streamlit as st
import pandas as pd
import sqlite3

def render_leave_approvals(u):
    u_class, u_wing = u.get('class'), u.get('wing')
    
    st.markdown("""
        <style>
        .request-card {
            background: white !important;
            border-radius: 18px !important;
            padding: 20px !important;
            border: 1px solid #DDD6FE !important;
            border-left: 10px solid #7C3AED !important;
            margin-bottom: 20px !important;
        }
        .search-box {
            background: #F5F3FF !important;
            padding: 20px !important;
            border-radius: 20px !important;
            border: 1px solid #C4B5FD !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # SECTION 1: NEW REQUESTS
    st.markdown("<h2 style='color:#1E1B4B;'>📥 New Leave Requests</h2>", unsafe_allow_html=True)
    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
        pending = pd.read_sql("SELECT * FROM apsokara_studentleave WHERE class=? AND wing=? AND status='Pending'", conn, params=(u_class, u_wing))
    
    if pending.empty:
        st.success("No pending requests today!")
    else:
        for _, r in pending.iterrows():
            st.markdown(f"""<div class="request-card">
                <b style="font-size:18px;">{r['name']}</b> (Roll: {r['student_id']})<br>
                <span style="color:#7C3AED; font-weight:bold;">{r['from_date']} to {r['to_date']}</span>
                <p style="background:#F8FAFC; padding:10px; border-radius:10px; margin-top:10px;">Reason: {r['reason']}</p>
            </div>""", unsafe_allow_html=True)
            c1, c2, _ = st.columns([1,1,2])
            if c1.button("Approve ✅", key=f"ap_{r['id']}", use_container_width=True):
                with sqlite3.connect("db.sqlite3", timeout=30) as conn: conn.execute("UPDATE apsokara_studentleave SET status='Approved' WHERE id=?", (r['id'],))
                st.rerun()
            if c2.button("Reject ❌", key=f"rj_{r['id']}", use_container_width=True):
                with sqlite3.connect("db.sqlite3", timeout=30) as conn: conn.execute("UPDATE apsokara_studentleave SET status='Rejected' WHERE id=?", (r['id'],))
                st.rerun()

    st.divider()

    # SECTION 2: CLASS HISTORY & INTEL
    st.markdown("<h2 style='color:#1E1B4B;'>🏛️ Class Leave History & Search</h2>", unsafe_allow_html=True)
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    s_name = c1.text_input("Search Student Name")
    s_date = c2.date_input("Search by Date", value=None)
    st.markdown('</div>', unsafe_allow_html=True)

    query = "SELECT name, from_date, to_date, status, reason FROM apsokara_studentleave WHERE class=? AND wing=?"
    params = [u_class, u_wing]
    if s_name: query += " AND name LIKE ?"; params.append(f"%{s_name}%")
    if s_date: query += " AND ? BETWEEN from_date AND to_date"; params.append(s_date.isoformat())

    with sqlite3.connect("db.sqlite3", timeout=30) as conn:
        hist = pd.read_sql(query + " ORDER BY id DESC", conn, params=params)
    
    if not hist.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(hist, use_container_width=True, hide_index=True)
    else:
        st.info("No records found in history.")

def render_final_upload(u):
    st.title("Final Uploads")

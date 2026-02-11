
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date, datetime
from attendance_logic import render_student_attendance

# --- DATABASE HELPER ---
def get_mobile_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# --- DIARY CARD COMPONENT ---
def render_mobile_diary_card(row):
    raw_date = str(row['date_posted'])
    dt_parts = raw_date.split(" | ")
    d_str = dt_parts[0]
    t_str = dt_parts[1] if len(dt_parts) > 1 else ""

    st.markdown(f'''
        <div style="background: white; border-radius: 15px; padding: 15px; border-left: 5px solid #1b4332; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                <span style="background: #1b4332; color: #d4af37; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;">{row['subject']}</span>
                <span style="color: #888; font-size: 11px;">{d_str}</span>
            </div>
            <div style="font-size: 16px; color: #111; font-weight: 600; margin-bottom: 5px; line-height: 1.4;">{row['content']}</div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 8px; margin-top: 10px;">
                <span style="font-size: 11px; color: #666;">🕒 {t_str}</span>
                <span style="font-size: 11px; color: #1b4332; font-weight: bold;">Class: {row['class']}-{row['section']}</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    if row['attachment_url'] and os.path.exists(row['attachment_url']):
        if st.button(f"📄 VIEW ATTACHMENT", key=f"mob_diary_{row['id']}", use_container_width=True):
            from diary_engine import show_attachment
            show_attachment(row['attachment_url'])

# --- MAIN DIARY VIEW ---
def render_mobile_diary_view(u, mode="student"):
    conn = get_mobile_db()
    if mode == "teacher":
        query = "SELECT * FROM apsokara_dailydiary WHERE teacher_id = ? ORDER BY id DESC"
        df = pd.read_sql(query, conn, params=(u['id'],))
    else:
        query = "SELECT * FROM apsokara_dailydiary WHERE class = ? AND section = ? ORDER BY id DESC"
        df = pd.read_sql(query, conn, params=(str(u.get('student_class','')), str(u.get('student_section',''))))
    conn.close()

    if df.empty:
        st.info("📭 No diary records found for your profile.")
    else:
        search = st.text_input("🔍 Search keyword...", placeholder="Topic or Subject", key="mob_search_input")
        if search:
            df = df[df['content'].str.contains(search, case=False) | df['subject'].str.contains(search, case=False)]
        
        for _, row in df.iterrows():
            render_mobile_diary_card(row)

# --- MAIN RENDER FUNCTION ---
def render_mobile_view():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
            * { font-family: 'Poppins', sans-serif; }
            .stApp { background-color: #F8F9FA; }
            [data-testid="stSidebar"] { background-color: #1b4332 !important; }
            [data-testid="stSidebar"] * { color: white !important; }
            .mobile-header-v2 {
                background: linear-gradient(90deg, #1b4332 0%, #2d6a4f 100%);
                padding: 15px; border-radius: 0px 0px 20px 20px;
                color: #d4af37; text-align: center;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
            }
            .stButton>button {
                background-color: #1b4332 !important; color: white !important;
                border: 1px solid #d4af37 !important; border-radius: 10px !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.image("sami.png", width=80)
        st.markdown("<h3 style='text-align:center;'>APS MENU</h3>", unsafe_allow_html=True)
        selection = st.radio("Navigate", ["🏠 Home", "📔 Diary", "📊 Attendance", "👤 Profile"])
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown('<div class="mobile-header-v2"><h2>🏛 APS OKARA</h2></div>', unsafe_allow_html=True)

    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        role = st.session_state.get('role', 'student').lower()
        display_name = u.get('full_name') or u.get('student_name') or "User"

        if selection == "🏠 Home":
            st.markdown(f"### Salam, {display_name} ✨")
            with st.container(border=True):
                st.markdown(f"**Role:** {role.upper()}")
                st.markdown(f"**Status:** Active Portal")
            
            st.write("---")
            st.info("Check 'Diary' or 'Attendance' from the menu to see updates.")

        elif selection == "📔 Diary":
            st.markdown("### 📔 Daily Diary")
            render_mobile_diary_view(u, mode=role)

        elif selection == "📊 Attendance":
            st.markdown("### 📊 Attendance")
            render_student_attendance(u)

        elif selection == "👤 Profile":
            st.markdown("### 👤 Profile")
            st.json(u)
    else:
        st.error("Please login again.")

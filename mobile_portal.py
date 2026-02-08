import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    # 1. CSS for Mobile Styling (Sidebar hide karna aur Header set karna)
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .main {padding-top: 0rem;}
            .mobile-header {
                background-color: #1E3A8A;
                padding: 15px;
                border-radius: 0px 0px 15px 15px;
                color: white;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. Header Section
    st.markdown('<div class="mobile-header"><h3>🏛️ APS OKARA PORTAL</h3></div>', unsafe_allow_html=True)

    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        
        # 3. User Welcome Card
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image("sami.png", width=60)
            with col2:
                st.subheader(f"Salam, {u['name']}")
                st.caption(f"ID: {u['id']} | Role: {st.session_state.role}")

        st.divider()

        # 4. Main Body (Attendance Logic)
        st.info("📌 Your Attendance Dashboard")
        render_student_attendance(u)

        st.divider()

        # 5. Bottom Actions
        if st.button("🚪 Logout from Portal", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    else:
        st.error("Session Expired. Please login again.")
        if st.button("Go to Login"):
            st.session_state.logged_in = False
            st.rerun()

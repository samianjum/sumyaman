import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    # 1. CSS for Tight Layout
    st.markdown("""
        <style>
            /* Pure page ki top padding khatam karna */
            .stApp { margin-top: -60px !important; }
            .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
            
            [data-testid="stSidebar"] { background-color: #1b4332 !important; }
            
            .mobile-header-v2 {
                background: linear-gradient(90deg, #1b4332 0%, #2d6a4f 100%);
                padding: 10px; 
                border-radius: 0 0 15px 15px;
                color: #d4af37; 
                text-align: center; 
                margin-top: 5px;
                border-bottom: 2px solid #d4af37;
            }
            
            /* Fuzool gaps points */
            div[data-testid="stVerticalBlock"] > div { gap: 0rem !important; padding-top: 0rem !important; }
        </style>
    """, unsafe_allow_html=True)

    # 2. SIDEBAR
    with st.sidebar:
        st.image("sami.png", width=80)
        selection = st.radio("Navigation", ["🏠 Home", "📊 Attendance", "👤 Profile"])
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 3. HEADER (News patti ke foran baad aaye ga)
    st.markdown('<div class="mobile-header-v2"><h3>🏛️ APS PORTAL</h3></div>', unsafe_allow_html=True)

    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        display_name = u.get('full_name') or u.get('name') or "User"

        if selection == "🏠 Home":
            st.write(f"### Salam, {display_name} 👋")
            col1, col2 = st.columns(2)
            col1.metric("Role", st.session_state.role)
            col2.metric("Status", "Online")
            
        elif selection == "📊 Attendance":
            render_student_attendance(u)
    else:
        st.error("Session Expired.")

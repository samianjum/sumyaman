import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    # 1. Custom CSS for Sidebar & Header
    st.markdown("""
        <style>
            /* Sidebar ko mobile par thora behtar dikhane ke liye */
            section[data-testid="stSidebar"] {
                background-color: #f8f9fa;
            }
            .main { padding-top: 0rem; }
            .stHeader { background-color: rgba(0,0,0,0); }
            
            .mobile-header {
                background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
                padding: 20px;
                border-radius: 0px 0px 20px 20px;
                color: white;
                text-align: center;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                margin-bottom: 25px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. SIDEBAR SECTION (Navigation)
    with st.sidebar:
        st.image("sami.png", width=100)
        st.title("Menu")
        selection = st.radio("Go to", ["🏠 Home", "📊 Attendance", "👤 Profile", "⚙️ Settings"])
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 3. HEADER SECTION
    st.markdown('<div class="mobile-header"><h1>🏛️ APS PORTAL</h1></div>', unsafe_allow_html=True)

    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        display_name = u.get('name') or u.get('student_name') or "User"

        # 4. BODY SECTION
        if selection == "🏠 Home":
            st.subheader(f"Salam, {display_name} 👋")
            st.write("Welcome to your digital campus. Select 'Attendance' from the sidebar to mark your presence.")
            
            # Quick Stats Body
            col1, col2 = st.columns(2)
            col1.metric("Status", "Active")
            col2.metric("Role", st.session_state.role)

        elif selection == "📊 Attendance":
            st.info("📂 Student Attendance System")
            render_student_attendance(u)

        elif selection == "👤 Profile":
            st.subheader("Your Profile")
            st.json(u) # Temporarily showing data

    else:
        st.error("Please login to continue.")
        st.session_state.logged_in = False

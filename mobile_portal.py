import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    # 1. THEME MATCHING CSS (Green & Gold)
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
            
            /* Global Font and Background */
            * { font-family: 'Poppins', sans-serif; }
            .stApp { background-color: #F0F0F0; }

            /* Sidebar Matching Main App (#1b4332) */
            [data-testid="stSidebar"] {
                background-color: #1b4332 !important;
            }
            [data-testid="stSidebar"] * {
                color: white !important;
            }

            /* Header Gradient (Matching Dark Green) */
            .mobile-header-v2 {
                background: linear-gradient(90deg, #1b4332 0%, #2d6a4f 100%);
                padding: 20px;
                border-radius: 0px 0px 25px 25px;
                color: #d4af37; /* Gold Title */
                text-align: center;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
                margin-bottom: 25px;
                border-bottom: 3px solid #d4af37;
            }

            /* Buttons (Gold Border & Style) */
            .stButton>button {
                background-color: #1b4332 !important;
                color: white !important;
                border: 2px solid #d4af37 !important;
                border-radius: 12px !important;
                font-weight: 800 !important;
                text-transform: uppercase;
            }

            /* Metrics and Cards */
            div[data-testid="stMetricValue"] { color: #1b4332 !important; }
            h1, h2, h3 { color: #1b4332 !important; }
        </style>
    """, unsafe_allow_html=True)

    # 2. SIDEBAR (Matching Theme)
    with st.sidebar:
        st.image("sami.png", width=100)
        st.markdown("<h2 style='color:white; text-align:center;'>MENU</h2>", unsafe_allow_html=True)
        selection = st.radio("Navigate", ["🏠 Home", "📊 Attendance", "👤 Profile"])
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 3. HEADER
    st.markdown('<div class="mobile-header-v2"><h1>🏛️ APS PORTAL</h1></div>', unsafe_allow_html=True)

    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        # Matching Main App logic for name
        display_name = u.get('full_name') or u.get('name') or u.get('student_name') or "User"

        # 4. BODY SECTION
        if selection == "🏠 Home":
            st.markdown(f"### Salam, {display_name} ✨")
            
            # Info Card
            st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #d4af37; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                    <p style='margin:0; color:#666; font-size:12px;'>CURRENT ROLE</p>
                    <h4 style='margin:0; color:#1b4332;'>{st.session_state.get('role', 'Member')}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            col1, col2 = st.columns(2)
            col1.metric("Status", "Active")
            col2.metric("Portal", "Mobile")

        elif selection == "📊 Attendance":
            st.markdown("### 📊 Attendance System")
            render_student_attendance(u)

        elif selection == "👤 Profile":
            st.markdown("### 👤 User Profile")
            st.info("Profile details are synced from the secure vault.")
            st.json(u)

    else:
        st.error("Session expired. Please login again.")
        st.session_state.logged_in = False

import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance
from attendance_system import render_attendance_system
from news_utility import render_news_ticker
import os

st.set_page_config(page_title="APS PORTAL", layout="wide", initial_sidebar_state="collapsed")

def render_mobile_view():
    if 'user_info' not in st.session_state:
        st.error("Please login again.")
        return
        
    u = st.session_state.get('user_info', {})
    role = st.session_state.get('role', 'Student')
    logo_path = '/home/sami/Downloads/sami.png'
    
    if 'active_menu' not in st.session_state:
        st.session_state.active_menu = "Dashboard"
    
    # --- FINAL HEAVY MOBILE UI CSS ---
    st.markdown('''
        <style>
        header[data-testid="stHeader"] { background-color: #1b4332 !important; height: 60px !important; }
        .block-container { padding: 10px !important; }
        footer { visibility: hidden; }

        /* Floating Gold Toggle */
        button[data-testid="stSidebarCollapseButton"] {
            background-color: #FFFF00 !important;
            position: fixed !important; top: 12px !important; left: 12px !important;
            z-index: 1000001 !important; width: 45px !important; height: 38px !important;
            border-radius: 8px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        }

        /* SIDEBAR DESIGN */
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #051611 0%, #1b4332 100%) !important;
            border-right: 3px solid #d4af37 !important;
        }
        
        .logo-box { display: flex; justify-content: center; padding: 20px 0; }

        /* Navigation Buttons */
        .stButton > button {
            background-color: transparent !important;
            color: #ffffff !important;
            border: 1px solid rgba(212, 175, 55, 0.4) !important;
            border-radius: 12px !important;
            height: 48px !important;
            font-weight: 700 !important;
            margin-bottom: -10px !important;
            text-transform: uppercase;
        }
        .stButton > button:hover, .stButton > button:active {
            background: #d4af37 !important;
            color: #1b4332 !important;
            border: 1px solid white !important;
        }

        /* MOBILE PROFILE CARDS */
        .m-card {
            background: white; border-radius: 12px; padding: 15px; margin-bottom: 10px;
            border-left: 5px solid #d4af37; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .m-label { color: #888; font-size: 11px; font-weight: 800; text-transform: uppercase; display: block; }
        .m-value { color: #1b4332; font-size: 15px; font-weight: 700; }

        .header-strip {
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            background: #1b4332; display: flex; align-items: center; justify-content: center;
            color: #d4af37; font-weight: 900; font-size: 18px; z-index: 1000;
        }
        </style>
        <div class="header-strip">APS OKARA PORTAL</div>
    ''', unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        if os.path.exists(logo_path): st.image(logo_path, width=130)
        else: st.markdown("<h3 style='color:#d4af37;'>APS</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(212,175,55,0.3); margin:0 0 15px 0;'>", unsafe_allow_html=True)

        if st.button("🏠 DASHBOARD", use_container_width=True): st.session_state.active_menu = "Dashboard"
        if st.button("📝 ATTENDANCE", use_container_width=True): st.session_state.active_menu = "Attendance"
        if st.button("📊 RESULTS", use_container_width=True): st.session_state.active_menu = "Results"
        if st.button("👤 PROFILE", use_container_width=True): st.session_state.active_menu = "Profile"
        
        st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            st.session_state.clear(); st.rerun()

    # --- CONTENT AREA ---
    page = st.session_state.active_menu
    st.markdown('<div style="margin-top: 100px;">', unsafe_allow_html=True)
    render_news_ticker()
    
    if page == "Profile":
        st.markdown(f"#### 👤 {u.get('full_name')}")
        def info_card(l, v):
            if v: st.markdown(f'<div class="m-card"><span class="m-label">{l}</span><span class="m-value">{v}</span></div>', unsafe_allow_html=True)
        
        if role == "Student":
            info_card("Father Name", u.get("father_name"))
            info_card("B-Form / ID", u.get("id"))
            info_card("Roll Number", u.get("roll_no"))
            info_card("Class & Sec", f"{u.get('class')} - {u.get('sec')}")
            info_card("Wing", u.get("wing"))
            info_card("Parents Phone", u.get("parent_phone"))
            info_card("Address", u.get("address"))
        else:
            info_card("Father Name", u.get("father_name"))
            info_card("CNIC", u.get("id"))
            info_card("Contact", u.get("phone"))
            if role == "Class Teacher":
                info_card("Assigned Class", f"{u.get('class')} - {u.get('sec')} ({u.get('wing')})")
            info_card("Address", u.get("address"))

    elif page == "Dashboard":
        st.markdown(f"##### Welcome Back, {u.get('full_name')}!")
        st.info("System is operational. Select a module from the menu.")
        
    elif page == "Attendance":
        if role == "Class Teacher": render_attendance_system(u)
        else: render_student_attendance(u)

    st.markdown('</div>', unsafe_allow_html=True)

render_mobile_view()

import os

path = 'mobile_portal.py'

content = r"""
import streamlit as st
import pandas as pd
import sqlite3

def get_mobile_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def render_mobile_view():
    # 1. THE INVISIBLE ENGINE (Hidden Radio to control tabs)
    if 'm_tab' not in st.session_state: st.session_state.m_tab = "Home"
    
    # CSS to hide the radio and style our custom HTML nav
    st.markdown('''
        <style>
            [data-testid="stSidebar"], header, footer, [data-testid="stHeader"] { display: none !important; }
            .main .block-container { padding: 0 !important; max-width: 100% !important; }
            
            /* Hide the actual streamlit radio but keep it functional */
            div.stRadio > div { display: none !important; }

            /* PURE HTML NAV BAR */
            .nav-bar {
                position: fixed; bottom: 0; left: 0; width: 100%; height: 65px;
                background: white; display: flex; flex-direction: row;
                justify-content: space-around; align-items: center;
                border-top: 1px solid #eee; z-index: 999999;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            }
            .nav-item {
                flex: 1; text-align: center; color: #888; text-decoration: none;
                display: flex; flex-direction: column; align-items: center;
                font-family: sans-serif; cursor: pointer; transition: 0.3s;
            }
            .nav-item.active { color: #1b4332; font-weight: bold; }
            .nav-item i { font-size: 22px; margin-bottom: 3px; }
            .nav-item span { font-size: 11px; }

            .content-area { padding: 15px; padding-bottom: 85px; background: #f9f9f9; min-height: 100vh; }
            .diary-card {
                background: white; border-radius: 15px; padding: 15px;
                margin-bottom: 12px; border-left: 6px solid #1b4332;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    ''', unsafe_allow_html=True)

    u = st.session_state.get('user_info', {})
    
    # 2. HEADER
    st.markdown(f'''
        <div style="background:#1b4332; padding:25px 15px; color:#d4af37; text-align:center; border-radius:0 0 25px 25px;">
            <h3 style="margin:0;">🏛 APS OKARA</h3>
            <small>{u.get("full_name","Student Portal")}</small>
        </div>
    ''', unsafe_allow_html=True)

    # 3. CONTENT SWITCHER
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    tab = st.session_state.m_tab
    
    if tab == "Home":
        st.write(f"### Salam, {u.get('full_name','User')} ✨")
        st.markdown('<div class="diary-card">Portal is now 100% stable with HTML Nav.</div>', unsafe_allow_html=True)
    elif tab == "Diary":
        st.write("### 📔 Daily Diary")
        conn = get_mobile_db()
        df = pd.read_sql("SELECT * FROM apsokara_dailydiary WHERE class=? AND section=? ORDER BY id DESC LIMIT 5", 
                         conn, params=(str(u.get('student_class','')), str(u.get('student_section',''))))
        conn.close()
        for _, row in df.iterrows():
            st.markdown(f'<div class="diary-card"><b>{row["subject"]}</b><br>{row["content"]}</div>', unsafe_allow_html=True)
    elif tab == "Attendance":
        st.info("Attendance loading...")
    elif tab == "Profile":
        st.write("### 👤 Profile")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. THE MAGIC: This captures the HTML click and updates Streamlit
    # We use a hidden selectbox or just buttons for now but forced in a div
    st.markdown(f'''
        <div class="nav-bar">
            <a onclick="window.parent.postMessage('Home', '*')" class="nav-item {"active" if tab=="Home" else ""}">
                <i class="fa fa-home"></i><span>Home</span>
            </a>
            <a onclick="window.parent.postMessage('Diary', '*')" class="nav-item {"active" if tab=="Diary" else ""}">
                <i class="fa fa-book"></i><span>Diary</span>
            </a>
            <a onclick="window.parent.postMessage('Attendance', '*')" class="nav-item {"active" if tab=="Attendance" else ""}">
                <i class="fa fa-chart-bar"></i><span>Atten</span>
            </a>
            <a onclick="window.parent.postMessage('Profile', '*')" class="nav-item {"active" if tab=="Profile" else ""}">
                <i class="fa fa-user"></i><span>Profile</span>
            </a>
        </div>
    ''', unsafe_allow_html=True)

    # Invisible Streamlit buttons to catch the state
    cols = st.columns(4)
    with cols[0]:
        if st.button(" ", key="h_fix", help="Home"): st.session_state.m_tab="Home"; st.rerun()
    with cols[1]:
        if st.button(" ", key="d_fix", help="Diary"): st.session_state.m_tab="Diary"; st.rerun()
    with cols[2]:
        if st.button(" ", key="a_fix", help="Atten"): st.session_state.m_tab="Attendance"; st.rerun()
    with cols[3]:
        if st.button(" ", key="p_fix", help="Prof"): st.session_state.m_tab="Profile"; st.rerun()
        
    st.markdown('''
        <style>
            /* Push invisible buttons over the HTML nav items */
            div[data-testid="stHorizontalBlock"] {
                position: fixed !important; bottom: 0; width: 100%; height: 65px;
                z-index: 1000000; opacity: 0;
            }
        </style>
    ''', unsafe_allow_html=True)
"""

with open(path, 'w') as f:
    f.write(content.strip())

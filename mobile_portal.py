import streamlit as st
import base64
import os
from news_utility import render_news_ticker

st.session_state['is_mobile'] = True

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def render_mobile_view():
    u = st.session_state.user_info
    logo_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], .stAppHeader, footer, [data-testid="stHeader"] {{ display: none !important; }}
        .block-container {{ padding: 0 !important; margin: 0 !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0 !important; padding: 0 !important; }}
        
        /* Fixed Top Section */
        .fixed-header-top {{ 
            position: fixed; top: 0; left: 0; right: 0; z-index: 10001; 
            height: 50px; background: #1b4332; display: flex; 
            align-items: center; padding: 0 15px; border-bottom: 2px solid #d4af37; 
        }}
        
        /* The Gap Killer Body */
        .main-scroll-body {{ 
            margin-top: -45px !important; /* NEGATIVE MARGIN: Khali jagah ko khich lega */
            padding: 12px; 
            padding-bottom: 100px !important;
        }}

        .stats-card {{
            background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
            border-radius: 12px; padding: 15px; color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}

        .action-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; }}
        .action-item {{ background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #eee; }}

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {{
            position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important;
            background-color: #1b4332 !important; border-top: 2px solid #d4af37 !important;
            z-index: 10002 !important; height: 55px !important;
        }}
        </style>

        <div class="fixed-header-top">
            <img src="data:image/png;base64,{logo_base64}" style="height:25px; margin-right:10px;">
            <div style="color:white; font-weight:800; font-size:14px;">APS PORTAL</div>
        </div>
    """, unsafe_allow_html=True)

    render_news_ticker()

    tab_home, tab_atten, tab_prof = st.tabs(["🏠 HOME", "📅 ATTEN", "👤 PROF"])

    with tab_home:
        # Negative margin container starts here
        st.markdown('<div class="main-scroll-body">', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="stats-card">
                <div style="font-size: 10px; opacity: 0.8; letter-spacing: 1px;">DASHBOARD</div>
                <div style="font-size: 18px; font-weight: 800; margin-top: 2px;">{u.get('full_name', 'Student').upper()}</div>
                <div style="display: flex; justify-content: space-between; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div><small style="font-size:9px;">ATTENDANCE</small><br><b style="font-size:15px;">85%</b></div>
                    <div style="text-align:right;"><small style="font-size:9px;">FEES</small><br><b style="color:#ffcc00; font-size:14px;">PAID</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-weight: 700; font-size:12px; color: #1b4332; margin: 12px 0 8px 2px;">QUICK ACTIONS</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="action-grid">
                <div class="action-item"><span style="font-size:20px;">📝</span><br><small style="font-weight:600;">Homework</small></div>
                <div class="action-item"><span style="font-size:20px;">🏆</span><br><small style="font-weight:600;">Results</small></div>
                <div class="action-item"><span style="font-size:20px;">💳</span><br><small style="font-weight:600;">Fee Slip</small></div>
                <div class="action-item"><span style="font-size:20px;">📢</span><br><small style="font-weight:600;">Events</small></div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

render_mobile_view()

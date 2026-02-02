import streamlit as st
import base64
import os
from news_utility import render_news_ticker

# Force session state for news_utility to pick mobile style
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
        
        .fixed-header-top {{ 
            position: fixed; top: 0; left: 0; right: 0; z-index: 10001; 
            height: 50px; background: #1b4332; display: flex; 
            align-items: center; padding: 0 15px; border-bottom: 2px solid #d4af37; 
        }}
        
        /* Clear any conflicting styles for the ticker */
        .main-scroll-body {{ margin-top: 78px; padding: 15px; padding-bottom: 70px; }}

        .stTabs [data-baseweb="tab-list"] {{
            position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important;
            background-color: #1b4332 !important; border-top: 2px solid #d4af37 !important;
            z-index: 10002 !important; height: 50px !important;
        }}
        </style>

        <div class="fixed-header-top">
            <img src="data:image/png;base64,{logo_base64}" style="height:25px; margin-right:10px;">
            <div style="color:white; font-weight:800; font-size:14px;">APS PORTAL</div>
        </div>
    """, unsafe_allow_html=True)

    # Now call the utility - it will finally take control!
    render_news_ticker()

    tab_home, tab_atten, tab_prof = st.tabs(["🏠 HOME", "📅 ATTEN", "👤 PROF"])

    with tab_home:
        st.markdown('<div class="main-scroll-body">', unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #1b4332; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                <div style="font-size:14px; color:#666;">WELCOME,</div>
                <div style="font-size:20px; font-weight:800; color:#1b4332;">{u.get('full_name', 'Student').upper()}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

render_mobile_view()

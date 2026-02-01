import streamlit as st
import base64
from news_utility import render_news_ticker

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

def render_mobile_view():
    u = st.session_state.user_info
    role = u.get("role", "Student").title()
    logo_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], .stAppHeader, footer {{ display: none !important; }}
        .stApp {{ background-color: #f8f9fa; }}
        .block-container {{ padding: 0 !important; margin: 0 !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
        
        /* 1. HEADER - BIGGER & BOLDER */
        .mobile-header {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 65px; background: #1b4332;
            color: white; display: flex; align-items: center;
            padding: 0 15px; z-index: 10001;
        }}
        .header-logo {{ height: 35px; width: auto; margin-right: 12px; }}
        .header-text-main {{ font-size: 16px; font-weight: 800; letter-spacing: 0.5px; }}
        .header-text-sub {{ font-size: 10px; color: #d4af37; font-weight: 600; text-transform: uppercase; }}

        /* 2. NEWS TICKER - TOUCH SCROLLABLE & VISIBLE */
        .aps-ticker-container {{
            position: fixed !important; 
            top: 65px !important; margin: 0 !important; padding: 0 !important; margin-top: 0 !important; 
            left: 0 !important; width: 100% !important;
            height: 35px !important; background: #d4af37 !important;
            z-index: 10000 !important;
            display: flex; align-items: center;
            overflow-x: scroll !important; pointer-events: auto !important; cursor: grab; /* Manual Scroll Enable */
            overflow-y: hidden;
            -webkit-overflow-scrolling: touch;
        }}
        
        .ticker-content-wrapper {{ 
            display: flex;
            white-space: nowrap;
            animation: marquee-move 60s linear infinite; display: inline-block; 
        }}

        /* Scroll functionality and Pause */
        .aps-ticker-container:active .ticker-content-wrapper,
        .aps-ticker-container:focus .ticker-content-wrapper {{
            animation-play-state: paused !important;
        }}

        .moving-text {{ 
            font-size: 0.85rem !important; 
            color: #1b4332 !important; 
            font-weight: 800; 
            padding: 0 20px;
        }}

        @keyframes marquee-move {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .aps-label {{ display: none !important; }}

        /* 3. HERO SECTION */
        .hero-section {{
            background: #1b4332; color: white;
            padding: 20px 15px; margin-top: 99px; /* 65 + 35 - slight overlap */
            border-bottom: 4px solid #d4af37;
        }}
        </style>
        
        <div class="mobile-header">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo">
            <div class="header-text">
                <div class="header-text-main">ARMY PUBLIC SCHOOL</div>
                <div class="header-text-sub">Official Digital Portal</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Ticker area
    render_news_ticker()

    # Hero Section
    st.markdown(f'''
        <div class="hero-section">
            <div style="font-size: 11px; color: #d4af37; font-weight: 700;">USER PROFILE</div>
            <div style="font-size: 24px; font-weight: 900; margin-top:2px;">{u.get("full_name","User")}</div>
            <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">{role} | Okara Cantt</div>
        </div>
        <div style="padding: 15px; padding-bottom: 80px;">
    ''', unsafe_allow_html=True)

    # Buttons
    grid_items = [
        ("📅", "ATTENDANCE") if role == "Student" else ("✅", "MARK ATTEN"),
        ("📖", "DIARY") if role == "Student" else ("📊", "RESULTS")
    ]
    
    st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div style="background: white; padding: 25px 10px; text-align: center; border-radius: 6px; border: 1px solid #ddd; border-bottom: 4px solid #d4af37;">
                <div style="font-size: 28px;">{grid_items[0][0]}</div><div style="font-size: 12px; font-weight: 800; color: #1b4332; margin-top:5px;">{grid_items[0][1]}</div>
            </div>
            <div style="background: white; padding: 25px 10px; text-align: center; border-radius: 6px; border: 1px solid #ddd; border-bottom: 4px solid #d4af37;">
                <div style="font-size: 28px;">{grid_items[1][0]}</div><div style="font-size: 12px; font-weight: 800; color: #1b4332; margin-top:5px;">{grid_items[1][1]}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Bottom Nav
    st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; height: 60px; background: #1b4332; display: flex; justify-content: space-around; align-items: center; z-index: 10002; border-top: 3px solid #d4af37;">
            <div style="text-align: center; color: #d4af37;">🏠<span style="font-size: 9px; display: block; font-weight:700;">HOME</span></div>
            <div style="text-align: center; color: #ced4da;">📊<span style="font-size: 9px; display: block;">STATS</span></div>
            <div style="text-align: center; color: #ced4da;">🔔<span style="font-size: 9px; display: block;">ALERTS</span></div>
            <div style="text-align: center; color: #ced4da;">👤<span style="font-size: 9px; display: block;">PROFILE</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

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
    role = u.get("role", "Student").title() # Teacher ya Student auto-pick karega
    logo_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    st.markdown(f"""
        <style>
        /* Force Remove All Default Spacings */
        [data-testid="stSidebar"], .stAppHeader, footer {{ display: none !important; }}
        .stApp {{ background-color: #f8f9fa; }}
        .block-container {{ padding: 0 !important; margin: 0 !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}

        /* 1. Header (Fixed) */
        .mobile-header {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 55px; background: #1b4332;
            color: white; display: flex; align-items: center;
            padding: 0 15px; z-index: 10001;
            border: none;
        }}

        .header-logo {{ height: 26px; width: auto; margin-right: 12px; }}

        /* 2. News Ticker (ZERO GAP ATTACHMENT) */
        .aps-ticker-container {{
            position: fixed !important; 
            top: 55px !important; /* Header ke end point se start */
            left: 0 !important; width: 100% !important;
            height: 30px !important; background: #d4af37 !important;
            z-index: 10000 !important; display: flex !important; align-items: center !important;
            margin: 0 !important; border: none !important;
        }}

        .ticker-content-wrapper {{ animation: marquee-move 50s linear infinite; }}
        @keyframes marquee-move {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .moving-text {{ font-size: 0.75rem !important; color: #1b4332 !important; font-weight: 800; }}
        .aps-label {{ display: none !important; }}

        /* 3. Hero Section (Seamless with Ticker) */
        .hero-section {{
            background: #1b4332; color: white;
            padding: 25px 15px 15px 15px; 
            margin-top: 85px; /* Header(55) + Ticker(30) */
            border-bottom: 3px solid #d4af37;
        }}

        /* 4. Bottom Nav */
        .bottom-nav {{
            position: fixed; bottom: 0; left: 0; right: 0;
            height: 60px; background: #1b4332;
            display: flex; justify-content: space-around; align-items: center;
            z-index: 10002; border-top: 2px solid #d4af37;
        }}
        .nav-item {{ text-align: center; color: #ced4da; font-size: 20px; }}
        .nav-item.active {{ color: #d4af37; }}
        .nav-text {{ font-size: 9px; display: block; margin-top: 2px; }}
        </style>
        
        <div class="mobile-header">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo">
            <div class="header-text">
                <div style="font-size: 13px; font-weight: 800;">ARMY PUBLIC SCHOOL</div>
                <div style="font-size: 9px; color: #d4af37; font-weight: 400; text-transform: uppercase;">
                    Okara Cantt | Official Digital Portal
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    render_news_ticker()

    # Body Starts
    st.markdown(f'''
        <div class="hero-section">
            <div style="font-size: 11px; color: #d4af37; font-weight: 600;">PORTAL DASHBOARD</div>
            <div style="font-size: 22px; font-weight: bold; margin-top:2px;">{u.get("full_name","User")}</div>
            <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                {role} ID: {u.get("roll_number") if role == "Student" else u.get("teacher_id", "N/A")}
            </div>
        </div>
        <div style="padding: 15px; padding-bottom: 80px;">
    ''', unsafe_allow_html=True)

    # Dynamic Action Grid based on Role
    if role == "Student":
        st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="background: white; padding: 20px; text-align: center; border-radius: 8px; border-bottom: 2px solid #d4af37;">
                    <div style="font-size: 24px;">📅</div><div style="font-size: 12px; font-weight: 700;">ATTENDANCE</div>
                </div>
                <div style="background: white; padding: 20px; text-align: center; border-radius: 8px; border-bottom: 2px solid #d4af37;">
                    <div style="font-size: 24px;">📖</div><div style="font-size: 12px; font-weight: 700;">DIARY</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div style="background: white; padding: 20px; text-align: center; border-radius: 8px; border-bottom: 2px solid #d4af37;">
                    <div style="font-size: 24px;">✅</div><div style="font-size: 12px; font-weight: 700;">MARK ATTEN</div>
                </div>
                <div style="background: white; padding: 20px; text-align: center; border-radius: 8px; border-bottom: 2px solid #d4af37;">
                    <div style="font-size: 24px;">📊</div><div style="font-size: 12px; font-weight: 700;">RESULTS</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Bottom Nav
    st.markdown("""
        <div class="bottom-nav">
            <div class="nav-item active">🏠<span class="nav-text">Home</span></div>
            <div class="nav-item">📊<span class="nav-text">Stats</span></div>
            <div class="nav-item">🔔<span class="nav-text">Alerts</span></div>
            <div class="nav-item">👤<span class="nav-text">Profile</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

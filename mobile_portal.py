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
    
    # 1. CSS Injection - Fixed Positions & Zero Gaps
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], .stAppHeader, footer {{ display: none !important; }}
        .stApp {{ background-color: #f8f9fa; }}
        .block-container {{ padding: 0 !important; margin: 0 !important; }}
        [data-testid="stVerticalBlock"] {{ gap: 0 !important; }}
        
        /* HEADER FIXED */
        .mobile-header {{
            position: fixed; top: 0; left: 0; right: 0;
            height: 65px; background: #1b4332;
            color: white; display: flex; align-items: center;
            padding: 0 15px; z-index: 10005;
        }}
        .header-logo {{ height: 32px; width: auto; margin-right: 12px; }}
        .header-text-main {{ font-size: 15px; font-weight: 800; letter-spacing: 0.5px; }}
        .header-text-sub {{ font-size: 9px; color: #d4af37; font-weight: 600; }}

        /* TICKER FIXED - NO GAP, NO COVER */
        .aps-ticker-container {{
            position: fixed !important; top: 65px !important; left: 0 !important; 
            width: 100% !important; height: 35px !important; 
            background: #d4af37 !important; z-index: 10004 !important;
            display: flex !important; align-items: center !important;
            padding: 0 !important; margin: 0 !important;
            overflow-x: auto !important; pointer-events: auto !important;
            -webkit-overflow-scrolling: touch;
        }}
        .aps-label {{ display: none !important; width: 0 !important; }} /* Removes Left Cover */
        .moving-text {{ font-size: 0.85rem !important; color: #1b4332 !important; font-weight: 800; padding: 0 20px; }}

        /* IDENTITY STRIP */
        .identity-strip {{
            background: #245d44; color: white;
            padding: 15px 20px; margin-top: 100px; /* 65 + 35 */
            border-bottom: 3px solid #d4af37;
        }}
        .id-name {{ font-size: 20px; font-weight: 700; line-height: 1.1; }}
        .id-unit {{ font-size: 13px; color: #d4af37; font-weight: 600; margin-top: 2px; }}
        .id-parent {{ font-size: 11px; opacity: 0.7; margin-top: 1px; }}
        </style>
        
        <div class="mobile-header">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo">
            <div class="header-text">
                <div class="header-text-main">ARMY PUBLIC SCHOOL</div>
                <div class="header-text-sub">OFFICIAL DIGITAL PORTAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Ticker Area
    render_news_ticker()

    # User details
    name = u.get("full_name", "User").upper()
    f_name = u.get("father_name", u.get("husband_name", "N/A")).upper()
    cls = u.get("class", u.get("assigned_class", "N/A"))
    sec = u.get("section", "N/A")
    wing = u.get("wing", "N/A")

    if "Teacher" in role:
        unit_info = f"Class Teacher • {cls}–{sec}"
        sub_info = u.get("department", "Academic Faculty").upper()
    else:
        unit_info = f"{cls}–{sec} • {wing} Wing"
        sub_info = f"S/o {f_name}"

    st.markdown(f"""
        <div class="identity-strip">
            <div class="id-name">{name}</div>
            <div class="id-unit">{unit_info}</div>
            <div class="id-parent">{sub_info}</div>
        </div>
        <div style="padding: 15px; padding-bottom: 80px;">
    """, unsafe_allow_html=True)

    # Grid Buttons Logic
    grid_items = [
        ("📅", "ATTENDANCE") if role == "Student" else ("✅", "MARK ATTEN"),
        ("📖", "DIARY") if role == "Student" else ("📊", "RESULTS")
    ]

    st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div style="background: white; padding: 22px 10px; text-align: center; border-radius: 4px; border: 1px solid #eee; border-bottom: 3px solid #d4af37;">
                <div style="font-size: 24px;">{grid_items[0][0]}</div>
                <div style="font-size: 11px; font-weight: 800; color: #1b4332; margin-top:5px;">{grid_items[0][1]}</div>
            </div>
            <div style="background: white; padding: 22px 10px; text-align: center; border-radius: 4px; border: 1px solid #eee; border-bottom: 3px solid #d4af37;">
                <div style="font-size: 24px;">{grid_items[1][0]}</div>
                <div style="font-size: 11px; font-weight: 800; color: #1b4332; margin-top:5px;">{grid_items[1][1]}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Bottom Nav
    st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; height: 60px; background: #1b4332; display: flex; justify-content: space-around; align-items: center; z-index: 10006; border-top: 2px solid #d4af37;">
            <div style="text-align: center; color: #d4af37;">🏠<span style="font-size: 9px; display: block; font-weight:700;">HOME</span></div>
            <div style="text-align: center; color: #ced4da;">📊<span style="font-size: 9px; display: block;">STATS</span></div>
            <div style="text-align: center; color: #ced4da;">🔔<span style="font-size: 9px; display: block;">ALERTS</span></div>
            <div style="text-align: center; color: #ced4da;">👤<span style="font-size: 9px; display: block;">PROFILE</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

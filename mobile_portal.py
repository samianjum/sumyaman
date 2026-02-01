import streamlit as st
from news_utility import render_news_ticker

def render_mobile_view():
    u = st.session_state.user_info
    
    st.markdown(
        """
        <style>
        /* 1. Reset */
        [data-testid="stSidebar"], .stAppHeader, footer { display: none !important; }
        
        /* 2. Header */
        .mobile-header {
            position: fixed; top: 0; left: 0; right: 0;
            height: 45px; background: #1b4332;
            color: white; display: flex; align-items: center;
            padding: 0 15px; z-index: 10001;
            border: none;
        }

        /* 3. Pure Gold Ticker - No Labels, No Covers */
        .aps-ticker-container {
            position: fixed !important;
            top: 45px !important;
            left: 0 !important; width: 100% !important;
            height: 32px !important;
            background: #d4af37 !important;
            margin: 0 !important;
            padding: 0 !important;
            z-index: 10000 !important;
            display: flex !important;
            align-items: center !important;
            overflow: hidden !important;
            border-bottom: 1px solid #1b4332;
        }

        /* Cover/Label ko khatam kar diya */
        .aps-label { display: none !important; visibility: hidden !important; }

        .ticker-content-wrapper {
            display: inline-block;
            padding-left: 10px;
            animation: marquee-move 55s linear infinite;
        }

        @keyframes marquee-move {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        .aps-ticker-container:active .ticker-content-wrapper {
            animation-play-state: paused !important;
        }

        .moving-text {
            font-size: 0.85rem !important;
            line-height: 32px !important; 
            color: #1b4332 !important;
            font-weight: 700 !important;
        }

        /* 4. Body Content */
        .app-body { padding-top: 77px !important; padding-left: 0px; padding-right: 0px; }
        
        /* Dashboard Strip */
        .summary-strip {
            display: flex; background: #1b4332;
            padding: 12px 5px; margin: 0;
            border-bottom: 2px solid #d4af37;
        }

        .stat-box {
            flex: 1; text-align: center;
            border-right: 1px solid rgba(212, 175, 55, 0.3);
            color: white;
        }
        .stat-box:last-child { border-right: none; }
        .stat-val { font-size: 13px; font-weight: bold; display: block; }
        .stat-lbl { font-size: 8px; color: #d4af37; text-transform: uppercase; letter-spacing: 0.5px; }

        .stTabs { margin-top: 5px !important; padding: 0 10px; }
        </style>
        
        <div class="mobile-header"><b>APS OKARA</b></div>
    """, unsafe_allow_html=True)

    render_news_ticker()

    st.markdown('<div class="app-body">', unsafe_allow_html=True)
    
    # Dashboard Summary Strip
    st.markdown("""
        <div class="summary-strip">
            <div class="stat-box"><span class="stat-lbl">Today</span><span class="stat-val">PRESENT</span></div>
            <div class="stat-box"><span class="stat-lbl">Monthly %</span><span class="stat-val">94%</span></div>
            <div class="stat-box"><span class="stat-lbl">Fees</span><span class="stat-val" style="color:#4dff88;">PAID</span></div>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏠 Home", "📊 Atten", "🏆 Result", "👤 Profile"])
    
    with tabs[0]:
        st.markdown(f'''
            <div style="margin: 15px; padding: 15px; background: white; border-radius: 12px; border-left: 5px solid #1b4332; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="font-size: 12px; color: #666;">Student Profile</div>
                <div style="font-size: 20px; font-weight: bold; color: #1b4332;">{u.get("full_name","Student")}</div>
                <div style="font-size: 13px; color: #d4af37; font-weight: 600;">{u.get("student_class","N/A")} - {u.get("student_section","A")}</div>
            </div>
        ''', unsafe_allow_html=True)

    with tabs[1]: st.info("Attendance details loading...")
    with tabs[3]: 
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

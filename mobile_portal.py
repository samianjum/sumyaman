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
    logo_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    st.markdown(f"""
        <style>
        [data-testid="stSidebar"], .stAppHeader, footer {{ display: none !important; }}
        .block-container {{ padding: 0 !important; }}
        .fixed-header {{ 
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000; 
            height: 60px; background: #1b4332; display: flex; 
            align-items: center; padding: 0 15px; border-bottom: 2px solid #d4af37; 
        }}
        .main-content {{ margin-top: 70px; padding: 15px; padding-bottom: 55px; }}
        
        .stTabs [data-baseweb="tab-list"] {{
            position: fixed !important; bottom: 0 !important; left: 0 !important; right: 0 !important;
            background-color: #1b4332 !important; border-top: 2px solid #d4af37 !important;
            display: flex !important; justify-content: space-around !important;
            z-index: 10000 !important; height: 48px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            flex: 1 !important; height: 48px !important; color: #ffffff99 !important;
        }}
        .stTabs [aria-selected="true"] {{ color: #d4af37 !important; background-color: #245d44 !important; }}
        
        /* Dashboard Card Styling */
        .stat-card {{
            background: white; padding: 15px; border-radius: 10px; 
            border-left: 5px solid #d4af37; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        </style>

        <div class="fixed-header">
            <img src="data:image/png;base64,{logo_base64}" style="height:30px; margin-right:10px;">
            <div style="color:white; font-weight:800; font-size:14px;">APS PORTAL</div>
        </div>
    """, unsafe_allow_html=True)

    render_news_ticker()

    tab_home, tab_atten, tab_prof = st.tabs(["🏠 HOME", "📅 ATTEN", "👤 PROF"])

    with tab_home:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        # --- Student Info Card ---
        st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:12px; color:#666;">WELCOME BACK,</div>
                <div style="font-size:18px; font-weight:800; color:#1b4332;">{u.get('full_name', 'Student').upper()}</div>
                <div style="font-size:11px; color:#d4af37; font-weight:600;">CLASS: {u.get('class','N/A')} - {u.get('section','N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick Action Buttons
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📝 View Diary", use_container_width=True)
        with col2:
            st.button("📊 Exam Result", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_atten:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown("### 📅 Monthly Attendance")
        # Sample Attendance Data
        import pandas as pd
        data = {
            "Date": ["01 Feb", "02 Feb", "03 Feb"],
            "Status": ["Present", "Present", "Absent"],
            "Time In": ["07:50 AM", "07:45 AM", "-"]
        }
        df = pd.DataFrame(data)
        st.table(df) # Mobile pe table direct simple lagta hai
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_prof:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown("### 👤 My Profile")
        st.json(u) # Baad mein isay sundar banayenge
        if st.button("Logout", type="primary"):
            st.session_state.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

render_mobile_view()

import os
import sys
import django
import streamlit as st
import base64

# Django Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    except: return ""

st.set_page_config(page_title="APSACS HQ", layout="wide", initial_sidebar_state="collapsed")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    logo_b64 = get_base64_image("/home/sami/Downloads/sami.png")
    logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-color: #F1F3F2 !important; }}
    header {{visibility: hidden !important;}}
    
    .stForm {{
        background-color: white !important;
        padding: 40px 60px !important;
        border-radius: 12px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
        border-top: 12px solid #2F3E46 !important;
        max-width: 800px !important; 
        margin: 80px auto !important;
    }}

    .stForm::before {{
        content: "";
        display: block;
        width: 110px; height: 110px;
        margin: 0 auto 20px auto;
        border-radius: 50%;
        border: 4px solid #F1F3F2;
        background-image: url('{logo_url}');
        background-size: cover;
    }}

    /* H1 and H2 Hierarchy */
    .h1-title {{
        color: #2F3E46;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        margin: 0 !important;
        white-space: nowrap !important;
        text-align: center;
        border-bottom: 2px solid #F1F3F2;
        padding-bottom: 10px;
    }}
    
    .h2-subtitle {{
        color: #52796F;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 2px;
        margin: 15px 0 35px 0 !important;
        text-align: center;
        text-transform: uppercase;
    }}
    
    div[data-baseweb="input"] {{ 
        border-radius: 6px !important;
        margin-bottom: 10px !important;
    }}
    
    .stButton>button {{
        width: 100% !important; background-color: #2F3E46 !important;
        color: white !important; font-weight: 800 !important; 
        font-size: 1.1rem !important; height: 55px !important;
        border-radius: 6px !important;
    }}
    
    .footer-area {{
        text-align: center; color: #6C757D; font-size: 13px;
        font-weight: 600; margin-top: -40px;
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.05, 2, 0.05])
    with col2:
        with st.form("login_box"):
            st.markdown('<h1 class="h1-title">Army Public School & College System</h1>', unsafe_allow_html=True)
            st.markdown('<h2 class="h2-subtitle">Okara Cantt | HQ Management Panel</h2>', unsafe_allow_html=True)
            
            # New Credentials Applied Here
            user = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
            pwd = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            
            if st.form_submit_button("AUTHORIZE SYSTEM ACCESS"):
                if user == "sami" and pwd == "summaya":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Credentials")
        
        st.markdown('<div class="footer-area">© 2026 APSACS OKARA CANTT | OFFICIAL PORTAL</div>', unsafe_allow_html=True)

# --- DASHBOARD PAGE ---
else:
    logo_b64 = get_base64_image("/home/sami/Downloads/sami.png")
    logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

    st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    [data-testid="stSidebar"] {{display: none !important;}}
    .main .block-container {{padding: 0 !important; max-width: 100% !important;}}
    .app-header {{position: fixed; top: 0; left: 0; right: 0; height: 60px; background-color: #2F3E46; color: white; display: flex; align-items: center; padding: 0 24px; z-index: 10000;}}
    .app-sidebar {{position: fixed; top: 60px; left: 0; width: 240px; bottom: 0; background-color: #E3E6E4; border-right: 1px solid #C9CECC; z-index: 9999; padding-top: 20px; display: flex; flex-direction: column; align-items: center;}}
    .logo-sidebar {{width: 80px; height: 80px; border-radius: 50%; border: 2px solid #52796F; background-image: url('{logo_url}'); background-size: cover; margin-bottom: 10px;}}
    .nav-link {{display: block; width: 200px; padding: 12px; background-color: #CAD2C5; border-left: 5px solid #52796F; border-radius: 4px; color: #1F2A30 !important; font-weight: 700; text-decoration: none; margin-top: 20px;}}
    [data-testid="stMain"] {{margin-left: 240px !important; padding-top: 80px !important;}}
    .element-container:has(#logout-btn-marker) + div button {{position: fixed !important; bottom: 20px !important; left: 20px !important; width: 200px !important; z-index: 100000 !important; background-color: #354F52 !important; color: white !important;}}
    </style>
    <div class="app-header"><span>APSACS HQ | OKARA CANTT</span></div>
    <div class="app-sidebar">
        <div class="logo-sidebar"></div>
        <div style="font-weight:800; font-size:11px; color:#2F3E46; text-align:center; padding:0 10px;">APSACS OKARA CANTT</div>
        <a href="/?page=dashboard" class="nav-link">🏠 DASHBOARD</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 20px 40px;"><h1>🏠 Admin Dashboard</h1></div>', unsafe_allow_html=True)
    st.markdown('<div id="logout-btn-marker"></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout System"):
        st.session_state.logged_in = False
        st.rerun()

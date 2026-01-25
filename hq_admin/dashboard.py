import os
import sys
import django
import streamlit as st
import base64

# Django Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
django.setup()

from auth_gate import check_access, logout_user

def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except: return None

st.set_page_config(page_title="APSACS HQ", layout="wide", initial_sidebar_state="collapsed")

if check_access():
    img_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    logo_url = f"data:image/png;base64,{img_base64}" if img_base64 else ""

    # CSS - Strictly Escaped
    st.markdown(f"""<style>
    header {{visibility: hidden !important;}}
    [data-testid="stSidebar"] {{display: none !important;}}
    .main .block-container {{padding: 0 !important; max-width: 100% !important; margin: 0 !important;}}
    .app-header {{position: fixed; top: 0; left: 0; right: 0; height: 60px; background-color: #2F3E46; color: #FAFAF8; display: flex; align-items: center; padding: 0 24px; z-index: 10000; border-bottom: 2px solid #52796F;}}
    .app-sidebar {{position: fixed; top: 60px; left: 0; width: 240px; bottom: 0; background-color: #E3E6E4; border-right: 1px solid #C9CECC; z-index: 9999; padding-top: 20px; display: flex; flex-direction: column; align-items: center;}}
    .logo-container {{width: 100px; height: 100px; border-radius: 50%; border: 3px solid #52796F; background-image: url('{logo_url}'); background-size: cover; background-position: center; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}}
    .school-name {{color: #2F3E46; font-size: 13px; font-weight: 800; text-align: center; margin-bottom: 25px; padding: 0 15px; line-height: 1.3; text-transform: uppercase;}}
    .nav-link-btn {{display: block !important; width: 200px !important; padding: 12px 15px !important; background-color: #CAD2C5 !important; border-left: 5px solid #52796F !important; border-radius: 4px !important; color: #1F2A30 !important; font-weight: 700 !important; text-decoration: none !important; text-align: left !important;}}
    [data-testid="stMain"] {{margin-left: 240px !important; padding-top: 60px !important;}}
    .app-footer {{position: fixed; bottom: 0; left: 240px; right: 0; height: 40px; background-color: #E3E6E4; border-top: 1px solid #C9CECC; z-index: 10001; display: flex; align-items: center; justify-content: center; color: #5F6F73; font-size: 12px;}}
    .element-container:has(#logout-btn-marker) + div button {{position: fixed !important; bottom: 20px !important; left: 20px !important; width: 200px !important; z-index: 100000 !important; background-color: #354F52 !important; color: white !important; font-weight: 600 !important; border: none !important;}}
    </style>""", unsafe_allow_html=True)

    # Sidebar - NO NEW LINES inside tags
    st.markdown(f'''<div class="app-header"><span>APSACS HQ | OKARA CANTT</span></div><div class="app-sidebar"><div class="logo-container"></div><div class="school-name">APSACS OKARA CANTT</div><div style="width: 85%; border-top: 1px solid #C9CECC; margin-bottom: 20px;"></div><a href="/?page=dashboard" target="_self" class="nav-link-btn">🏠 &nbsp; DASHBOARD</a></div><div class="app-footer"><span>© 2026 Academic Management System</span></div>''', unsafe_allow_html=True)

    # Main Content
    st.markdown('<div style="padding: 40px;">', unsafe_allow_html=True)
    st.title("🏠 Admin Dashboard")
    st.markdown("---")
    st.success("Sami bhai, ab ye code text hamesha ke liye gayab ho gaya hai. Ab sirf professional button hai.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div id="logout-btn-marker"></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout System"):
        logout_user()

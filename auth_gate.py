import streamlit as st
import base64
import os

def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except: return None

def login_page():
    # Load Logo
    img_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    logo_url = f"data:image/png;base64,{img_base64}" if img_base64 else ""

    # Full CSS for Login
    st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    [data-testid="stAppViewContainer"] {{
        background-color: #F1F3F2 !important;
    }}
    
    /* Login Box */
    .login-card {{
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-top: 6px solid #2F3E46;
        text-align: center;
        margin-bottom: -50px;
    }}

    .login-logo {{
        width: 100px; height: 100px;
        border-radius: 50%;
        border: 3px solid #52796F;
        background-image: url('{logo_url}');
        background-size: cover; background-position: center;
        margin: 0 auto 15px auto;
    }}

    .school-title {{
        color: #2F3E46; font-size: 1.2rem; font-weight: 800;
        margin-bottom: 5px; text-transform: uppercase;
    }}

    .login-footer {{
        position: fixed; bottom: 20px; left: 0; right: 0;
        text-align: center; color: #5F6F73; font-size: 13px;
        font-weight: 500;
    }}

    /* Styling Streamlit Inputs */
    div[data-baseweb="input"] {{
        border-radius: 8px !important;
    }}
    
    div.stButton > button {{
        width: 100%;
        background-color: #52796F !important;
        color: white !important;
        border: none !important;
        padding: 10px !important;
        font-weight: 600 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Centering Layout
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown(f"""
        <div class="login-card">
            <div class="login-logo"></div>
            <div class="school-title">ARMY PUBLIC SCHOOL & COLLEGE SYSTEM</div>
            <p style="color: #52796F; font-weight: 600; margin-bottom: 20px;">OKARA CANTT | HQ PANEL</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Form inside col2
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Enter username")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("LOGIN TO HQ")
            
            if submit:
                if user == "admin" and pwd == "admin123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")

    st.markdown('<div class="login-footer">© 2026 APSACS OKARA | ACADEMIC MANAGEMENT SYSTEM</div>', unsafe_allow_html=True)

def check_access():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
        return False
    return True

def logout_user():
    st.session_state.logged_in = False
    st.rerun()

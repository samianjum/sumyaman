import streamlit as st
import sqlite3
import os
import base64

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def login_page():
    img_base64 = get_base64_image("/home/sami/Downloads/sami.png")
    logo_url = f"data:image/png;base64,{img_base64}" if img_base64 else ""

    st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    [data-testid="stAppViewContainer"] {{ background-color: #F1F3F2 !important; }}
    .login-card {{
        background-color: white; padding: 40px; border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-top: 6px solid #2F3E46;
        text-align: center; margin-bottom: -50px;
    }}
    .login-logo {{
        width: 100px; height: 100px; border-radius: 50%; border: 3px solid #52796F;
        background-image: url('{logo_url}'); background-size: cover; margin: 0 auto 15px auto;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card"><div class="login-logo"></div><div class="school-title">APS OKARA PORTAL</div></div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["🎓 STUDENT LOGIN", "👨‍🏫 STAFF LOGIN"])

    with t1:
        b_form = st.text_input("B-Form / ID Number", key="s_uid")
        s_dob = st.date_input("Date of Birth", key="s_dob")
        if st.button("Student Login"):
            # Check DB (Pseudocode logic for matching)
            conn = sqlite3.connect('db.sqlite3')
            user = conn.execute("SELECT * FROM apsokara_student WHERE b_form=? AND dob=?", (b_form, str(s_dob))).fetchone()
            if user:
                handle_login_flow(user, "Student")
            else:
                st.error("Invalid Credentials")
            conn.close()

    with t2:
        cnic = st.text_input("CNIC Number", key="t_uid")
        t_dob = st.date_input("Date of Birth", key="t_dob")
        if st.button("Staff Login"):
            conn = sqlite3.connect('db.sqlite3')
            user = conn.execute("SELECT * FROM apsokara_teacher WHERE cnic=? AND dob=?", (cnic, str(t_dob))).fetchone()
            if user:
                # Check Role (Class Teacher or Teacher)
                role = "Class Teacher" if user[10] == 1 else "Teacher" # Assuming index 10 is is_class_teacher
                handle_login_flow(user, role)
            else:
                st.error("Invalid Credentials")
            conn.close()

def handle_login_flow(user_data, role):
    user_info = {'id': user_data[0], 'name': user_data[1], 'b_form': user_data[2], 'cnic': user_data[3]}
    
    # 2-Step Check
    conn = sqlite3.connect('db.sqlite3')
    table = 'apsokara_student' if role == 'Student' else 'apsokara_teacher'
    status = conn.execute(f"SELECT face_status FROM {table} WHERE id=?", (user_info['id'],)).fetchone()
    conn.close()

    if status and str(status[0]).upper() == 'ENROLLED':
        st.session_state.temp_user = user_info
        st.session_state.temp_role = role
        st.session_state.needs_face_auth = True
    else:
        st.session_state.user_info = user_info
        st.session_state.role = role
        st.session_state.logged_in = True
    st.rerun()

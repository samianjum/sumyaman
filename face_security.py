import streamlit as st
import sqlite3
import time
import face_recognition
import numpy as np
from PIL import Image

def render_face_lock_setup(user_info):
    role = st.session_state.get('role', 'Student')
    # Table selection
    table = "apsokara_student" if role == "Student" else "apsokara_teacher"
    
    # Universal ID Fetch
    user_actual_id = user_info.get('id')
    
    with sqlite3.connect('db.sqlite3', timeout=10) as conn:
        # Hum sirf 'id' column use karenge jo dono tables mein lazmi hota hai
        query = f"SELECT face_encoding, face_status FROM {table} WHERE id = ?"
        res = conn.execute(query, (user_actual_id,)).fetchone()
        saved_enc_bytes, db_status = res if res else (None, 'NOT_SET')

    st.markdown("""
        <style>
        .sec-card { background: rgba(0,0,0,0.4); border: 2px solid #d4af37; border-radius: 15px; padding: 20px; text-align: center; }
        div[data-testid="stCameraInput"] { max-width: 280px !important; margin: 0 auto !important; border-radius: 50% !important; overflow: hidden !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)

    # --- 1. BIOMETRIC GATE ---
    if st.session_state.get('needs_face_auth'):
        st.markdown("<h3 style='color:#d4af37;'>🔐 Face Verification</h3>", unsafe_allow_html=True)
        img = st.camera_input("Scan Face", key="gate_scan")
        
        if img and saved_enc_bytes:
            curr_img = Image.open(img).convert('RGB')
            curr_enc = face_recognition.face_encodings(np.array(curr_img))
            if curr_enc:
                master_enc = np.frombuffer(saved_enc_bytes, dtype=np.float64)
                if face_recognition.compare_faces([master_enc], curr_enc[0], tolerance=0.45)[0]:
                    st.success("Identity Verified!")
                    st.session_state.needs_face_auth = False; st.session_state.face_auth_verified = True
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Face Mismatch!")
        st.stop()

    # --- 2. MANAGEMENT PANEL ---
    st.markdown(f"<h4>🛡️ {role} Security Settings</h4>", unsafe_allow_html=True)
    
    if db_status == 'ENROLLED':
        st.success("Face ID is Active")
        with st.expander("Reset Biometrics"):
            # Simple credentials check for reset
            c_dob = st.date_input("Confirm Date of Birth", key="res_dob")
            if st.button("RESET NOW"):
                if str(c_dob) == str(user_info.get('dob')):
                    with sqlite3.connect('db.sqlite3') as conn:
                        conn.execute(f"UPDATE {table} SET face_encoding=NULL, face_status='NOT_SET' WHERE id=?", (user_actual_id,))
                    st.success("Wiped! Refreshing...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("DOB Mismatch!")
    else:
        st.info("No Face ID found.")
        reg_img = st.camera_input("Enroll Face", key="enroll_cam")
        if reg_img:
            encs = face_recognition.face_encodings(np.array(Image.open(reg_img).convert('RGB')))
            if encs:
                if st.button("LOCK IDENTITY"):
                    with sqlite3.connect('db.sqlite3') as conn:
                        conn.execute(f"UPDATE {table} SET face_encoding=?, face_status='ENROLLED' WHERE id=?", (encs[0].tobytes(), user_actual_id))
                    st.success("Face ID Saved!")
                    time.sleep(1)
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

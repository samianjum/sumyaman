import streamlit as st
import sqlite3
import time
import face_recognition
import numpy as np
from PIL import Image

def render_face_lock_setup(user_info):
    role = st.session_state.get('role', 'Student')
    table = "apsokara_student" if role == "Student" else "apsokara_teacher"
    user_actual_id = user_info.get('id')
    
    with sqlite3.connect('db.sqlite3', timeout=10) as conn:
        query = f"SELECT face_encoding, face_status FROM {table} WHERE id = ?"
        res = conn.execute(query, (user_actual_id,)).fetchone()
        saved_enc_bytes, db_status = res if res else (None, 'NOT_SET')

    # --- ADVANCED CYBER UI CSS ---
    st.markdown("""
        <style>
        .main-vault {
            background: linear-gradient(145deg, #0d1b15, #1b4332);
            border: 2px solid #d4af37;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            margin-bottom: 25px;
        }
        .security-badge {
            background: rgba(212, 175, 55, 0.1);
            color: #d4af37;
            padding: 8px 20px;
            border-radius: 50px;
            border: 1px solid #d4af37;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .scan-overlay {
            border: 4px dashed #d4af37;
            border-radius: 50% !important;
            padding: 10px;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); }
            70% { box-shadow: 0 0 0 20px rgba(212, 175, 55, 0); }
            100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
        }
        div[data-testid="stCameraInput"] {
            border-radius: 50% !important;
            overflow: hidden !important;
            width: 280px !important;
            height: 280px !important;
            margin: 0 auto !important;
            border: 5px solid #d4af37 !important;
        }
        .info-text { color: #ffffff; opacity: 0.8; font-size: 14px; margin-top: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-vault">', unsafe_allow_html=True)

    # --- MODE 1: THE LOCK SCREEN (Pop-up Style) ---
    if st.session_state.get('needs_face_auth'):
        st.markdown("<div class='security-badge'>Identity Verification Required</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:white; margin-top:20px;'>🛡️ APS Biometric Vault</h2>", unsafe_allow_html=True)
        st.markdown("<p class='info-text'>Position your face in the center of the scanner</p>", unsafe_allow_html=True)
        
        st.markdown("<div class='scan-overlay'>", unsafe_allow_html=True)
        img = st.camera_input("", key="gate_scan_v2")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if img and saved_enc_bytes:
            with st.spinner("🤖 AI Analysing Features..."):
                curr_img = Image.open(img).convert('RGB')
                curr_enc = face_recognition.face_encodings(np.array(curr_img))
                if curr_enc:
                    master_enc = np.frombuffer(saved_enc_bytes, dtype=np.float64)
                    dist = face_recognition.face_distance([master_enc], curr_enc[0])[0]
                    match_score = int((1 - dist) * 100)
                    
                    if dist < 0.45:
                        st.balloons()
                        st.toast(f"Match Confirmed: {match_score}%", icon="✅")
                        st.success(f"Access Granted! Identity Verified.")
                        st.session_state.needs_face_auth = False
                        st.session_state.face_auth_verified = True
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"Mismatch ({match_score}%). Access Denied.")
                        st.toast("Identity Mismatch", icon="❌")
                else:
                    st.warning("No face detected in frame.")
        st.stop()

    # --- MODE 2: THE MANAGEMENT DASHBOARD ---
    st.markdown(f"<h2 style='color:#d4af37;'>🔒 {role} Security Center</h2>", unsafe_allow_html=True)
    
    if db_status == 'ENROLLED':
        st.markdown("<div class='security-badge'>Account Secured</div>", unsafe_allow_html=True)
        st.markdown(f"<p class='info-text'>Verified ID: <b>{user_actual_id}</b></p>", unsafe_allow_html=True)
        
        st.markdown("---")
        with st.expander("🛠️ Advanced Settings & Reset"):
            st.write("To disable Face ID, confirm your Date of Birth.")
            c_dob = st.date_input("Confirm DOB", key="res_dob_v2")
            if st.button("🔥 PERMANENTLY REMOVE FACE ID", use_container_width=True):
                if str(c_dob) == str(user_info.get('dob')):
                    with sqlite3.connect('db.sqlite3') as conn:
                        conn.execute(f"UPDATE {table} SET face_encoding=NULL, face_status='NOT_SET' WHERE id=?", (user_actual_id,))
                    st.toast("Security Profile Deleted", icon="🗑️")
                    st.success("Wiping biometric data...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credential mismatch. Action blocked.")
    else:
        st.markdown("<div class='security-badge' style='color:#f87171; border-color:#f87171;'>Unprotected</div>", unsafe_allow_html=True)
        st.markdown("<p class='info-text'>Enroll your biometric profile to enable 2-Factor Face Authentication.</p>", unsafe_allow_html=True)
        
        reg_img = st.camera_input("Register Primary Face", key="enroll_cam_v2")
        if reg_img:
            with st.spinner("🖋️ Mapping Face Features..."):
                encs = face_recognition.face_encodings(np.array(Image.open(reg_img).convert('RGB')))
                if encs:
                    if st.button("🚀 ACTIVATE BIOMETRIC LOCK", use_container_width=True):
                        with sqlite3.connect('db.sqlite3') as conn:
                            conn.execute(f"UPDATE {table} SET face_encoding=?, face_status='ENROLLED' WHERE id=?", (encs[0].tobytes(), user_actual_id))
                        st.toast("Security Activated!", icon="🛡️")
                        st.success("Face ID Profile Created Successfully!")
                        time.sleep(1.5)
                        st.rerun()
                else:
                    st.error("Face not clear enough. Please ensure good lighting.")

    st.markdown('</div>', unsafe_allow_html=True)

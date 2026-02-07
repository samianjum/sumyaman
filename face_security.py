import streamlit as st
import sqlite3
import time
import face_recognition
import numpy as np
from PIL import Image

def render_face_lock_setup(user_info):
    # Professional Glass-morphism UI
    st.markdown("""
        <style>
        .stCameraInput { border: 4px solid #d4af37 !important; border-radius: 15px !important; }
        .auth-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px; border-radius: 15px; border: 1px solid #d4af37;
            text-align: center; margin-bottom: 20px;
        }
        .status-badge {
            padding: 5px 15px; border-radius: 50px; font-size: 0.8rem;
            font-weight: bold; text-transform: uppercase;
        }
        .match { background: #1e4620; color: #4ade80; }
        .mismatch { background: #442727; color: #f87171; }
        .pending { background: #1e3a8a; color: #60a5fa; }
        </style>
    """, unsafe_allow_html=True)

    role = st.session_state.get('role', 'Student')
    table = "apsokara_student" if role == "Student" else "apsokara_teacher"
    
    with sqlite3.connect('db.sqlite3') as conn:
        res = conn.execute(f"SELECT face_encoding FROM {table} WHERE id=?", (user_info['id'],)).fetchone()
        saved_enc_bytes = res[0] if res else None

    # --- THE SECURE GATE ---
    if st.session_state.get('needs_face_auth'):
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#d4af37;'>🔐 Biometric Vault</h2>", unsafe_allow_html=True)
        
        # Real-time Status Logic
        status_msg = "Awaiting Capture"
        status_class = "pending"
        
        img_file = st.camera_input("Verify your identity", key="final_gate")
        
        if img_file and saved_enc_bytes:
            img = Image.open(img_file).convert('RGB')
            img_array = np.array(img)
            
            # AI Detection
            face_locs = face_recognition.face_locations(img_array)
            if face_locs:
                curr_encs = face_recognition.face_encodings(img_array, face_locs)
                saved_enc = np.frombuffer(saved_enc_bytes, dtype=np.float64)
                
                # Compare (Strict Distance 0.45)
                dist = face_recognition.face_distance([saved_enc], curr_encs[0])[0]
                match_score = int((1 - dist) * 100)
                
                if dist < 0.45:
                    st.markdown(f"<span class='status-badge match'>MATCH: {match_score}%</span>", unsafe_allow_html=True)
                    st.success("Access Granted. Redirecting...")
                    time.sleep(1.2)
                    st.session_state.needs_face_auth = False
                    st.rerun()
                else:
                    st.markdown(f"<span class='status-badge mismatch'>MISMATCH: {match_score}%</span>", unsafe_allow_html=True)
                    st.error("Identity could not be verified.")
            else:
                st.warning("No face detected. Please center your face.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # --- MANAGEMENT TAB ---
    else:
        if saved_enc_bytes:
            st.success("✅ Your account is protected with AI Face ID.")
            if st.button("🔴 RESET BIOMETRIC DATA"):
                with sqlite3.connect('db.sqlite3') as conn:
                    conn.execute(f"UPDATE {table} SET face_encoding=NULL, face_status='NOT_SET' WHERE id=?", (user_info['id'],))
                st.rerun()
        else:
            st.info("Setup Face ID to secure your portal.")
            reg_img = st.camera_input("Enroll Primary Profile")
            if reg_img:
                img = Image.open(reg_img).convert('RGB')
                encs = face_recognition.face_encodings(np.array(img))
                if encs:
                    if st.button("🔒 LOCK IDENTITY"):
                        with sqlite3.connect('db.sqlite3') as conn:
                            conn.execute(f"UPDATE {table} SET face_encoding=?, face_status='ENROLLED' WHERE id=?", (encs[0].tobytes(), user_info['id']))
                        st.success("Identity Locked Successfully!")
                        st.rerun()

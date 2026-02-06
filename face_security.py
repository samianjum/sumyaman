import streamlit as st
import sqlite3
import time

def render_face_lock_setup(user_info):
    # Ultimate CSS: No Gaps, Pure Circle, Centered Video
    st.markdown("""
        <style>
        div[data-testid="stCameraInput"], 
        div[data-testid="stCameraInput"] > div,
        div[data-testid="stCameraInput"] > div > div {
            width: 300px !important; height: 300px !important;
            padding: 0 !important; margin: 0 auto !important;
            border-radius: 50% !important;
        }
        div[data-testid="stCameraInput"] {
            border: 6px solid #d4af37 !important;
            overflow: hidden !important;
            box-shadow: 0 0 50px rgba(212, 175, 55, 0.8) !important;
            background: #000 !important; position: relative !important;
        }
        div[data-testid="stCameraInput"] video {
            object-fit: cover !important; width: 100% !important; height: 100% !important;
            transform: scale(1.1) !important; position: absolute !important;
            top: 0 !important; left: 0 !important;
        }
        [data-testid="stCameraInput"] button {
            opacity: 0 !important; width: 100% !important; height: 100% !important;
            position: absolute !important; z-index: 100 !important; cursor: pointer !important;
        }
        [data-testid="stCameraInput"] label, [data-testid="stCameraInput"] span { display: none !important; }

        .scan-line {
            position: relative; width: 300px; height: 0; margin: 0 auto; z-index: 101; pointer-events: none;
        }
        .line {
            position: absolute; width: 100%; height: 4px;
            background: linear-gradient(to right, transparent, #00ff00, #fff, #00ff00, transparent);
            box-shadow: 0 0 25px #00ff00;
            animation: move 2s infinite ease-in-out;
        }
        @keyframes move { 0% { top: 10px; opacity: 0; } 50% { opacity: 1; } 100% { top: 290px; opacity: 0; } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#d4af37;'>🔐 FACE ID SETUP</h2>", unsafe_allow_html=True)

    if 'face_setup_step' not in st.session_state: st.session_state.face_setup_step = 'idle'

    if st.session_state.face_setup_step == 'idle':
        st.write("<p style='text-align:center;'>Click below to start your biometric enrollment.</p>", unsafe_allow_html=True)
        if st.button("✨ START ENROLLMENT", use_container_width=True):
            st.session_state.face_setup_step = 'scanning'
            st.rerun()

    elif st.session_state.face_setup_step == 'scanning':
        st.markdown('<div class="scan-line"><div class="line"></div></div>', unsafe_allow_html=True)
        img = st.camera_input("SCAN", label_visibility="hidden", key="setup_cam_vfinal")
        st.info("💡 Center your face and TAP THE CIRCLE to capture.")
        
        if img:
            st.session_state.temp_face_img = img
            st.session_state.face_setup_step = 'review'
            st.rerun()

    elif st.session_state.face_setup_step == 'review':
        st.success("✅ SCAN COMPLETE")
        st.image(st.session_state.temp_face_img, width=300)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 RETAKE", use_container_width=True):
                st.session_state.face_setup_step = 'scanning'
                st.rerun()
        with col2:
            if st.button("🔒 SAVE & LOCK", use_container_width=True):
                conn = sqlite3.connect('db.sqlite3')
                conn.execute("UPDATE apsokara_student SET face_encoding='ENROLLED' WHERE id=?", (user_info['id'],))
                conn.commit()
                conn.close()
                st.session_state.face_setup_step = 'idle'
                st.balloons()
                st.success("Face ID Linked!")
                time.sleep(1.5)
                st.rerun()

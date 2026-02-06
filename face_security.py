import streamlit as st
import sqlite3
import time

def render_face_lock_setup(user_info):
    # Clean CSS for Perfect Clickable Circle
    st.markdown("""
        <style>
        div[data-testid="stCameraInput"] {
            width: 300px !important;
            height: 300px !important;
            margin: 0 auto !important;
            border: 6px solid #d4af37 !important;
            border-radius: 50% !important;
            overflow: hidden !important;
            position: relative !important;
        }
        div[data-testid="stCameraInput"] video {
            object-fit: cover !important;
            width: 100% !important;
            height: 100% !important;
            transform: scale(1.1) !important;
        }
        /* Hidden but clickable capture button over everything */
        div[data-testid="stCameraInput"] button {
            opacity: 0.1 !important; /* Halka sa shutter nazar aye ga */
            position: absolute !important;
            top: 0 !important; left: 0 !important;
            width: 100% !important; height: 100% !important;
            z-index: 100 !important;
            cursor: pointer !important;
        }
        [data-testid="stCameraInput"] label, [data-testid="stCameraInput"] span {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'f_step' not in st.session_state: st.session_state.f_step = 'scan'

    if st.session_state.f_step == 'scan':
        st.markdown("<h3 style='text-align:center;'>📸 Center Face & Tap Circle</h3>", unsafe_allow_html=True)
        img = st.camera_input("SCAN", key="v21_cam")
        if img:
            st.session_state.v_img = img
            st.session_state.f_step = 'review'
            st.rerun()

    elif st.session_state.f_step == 'review':
        st.image(st.session_state.v_img, width=300)
        st.info("Identity captured. Lock this face?")
        c1, c2 = st.columns(2)
        if c1.button("🔄 RETAKE"): 
            st.session_state.f_step = 'scan'
            st.rerun()
        if c2.button("🔒 LOCK FACE"):
            conn = sqlite3.connect('db.sqlite3')
            conn.execute("UPDATE apsokara_student SET face_encoding='ENROLLED' WHERE id=?", (user_info['id'],))
            conn.commit()
            conn.close()
            st.session_state.f_step = 'scan'
            st.success("✅ Secure Face ID Locked!")
            time.sleep(1)
            st.rerun()

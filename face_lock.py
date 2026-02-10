import streamlit as st
from face_handler import register_face

def render_face_lock_setup(user_info, role):
    st.markdown("### 🔒 Biometric Security Setup")
    current_status = user_info.get('face_status', 'NOT_SET')
    
    if current_status == 'ENROLLED':
        st.success("🛡 Aapka Face ID pehle se active hai.")
        if st.button("Delete & Re-register"):
            st.info("Re-registration feature coming soon...")
    else:
        st.info("Apna face register karne ke liye niche camera use karein.")
        img_file = st.camera_input("Scan your face")
        if img_file is not None:
            if st.button("Confirm & Save Face ID", type="primary"):
                with st.spinner("💾 Saving..."):
                    success, msg = register_face(user_info['id'], role, img_file)
                    if success:
                        st.success(msg)
                        st.session_state.user_info['face_status'] = 'ENROLLED'
                        st.rerun()
                    else:
                        st.error(msg)

def show_face_verification_gate():
    import streamlit as st
    from face_handler import verify_face
    
    st.markdown("<h2 style='text-align:center;'>🔒 Biometric Verification Required</h2>", unsafe_allow_html=True)
    u = st.session_state.get('pending_user')
    role = st.session_state.get('pending_role')
    
    if not u:
        st.error("No pending user found.")
        if st.button("Back to Login"):
            st.session_state.show_face_gate = False
            st.rerun()
        return

    img = st.camera_input("Verify your face to continue", key="gate_cam")
    
    if img:
        success, msg = verify_face(u['id'], role, img)
        if success:
            st.success("✅ Access Granted!")
            st.session_state.user_info = u
            st.session_state.user_role = role
            st.session_state.role = role
            st.session_state.logged_in = True
            st.session_state.show_face_gate = False
            st.rerun()
        else:
            st.error(msg)
    
    if st.button("Cancel & Back to Login"):
        st.session_state.show_face_gate = False
        st.rerun()

import streamlit as st
from face_handler import register_face

def render_face_lock_setup(user_info, role):
    st.markdown("### 🔒 Smart Biometric Security")
    st.write("Apne portal ko 2-Step Verification se secure karein.")
    
    status = user_info.get('face_status', 'NOT_SET')
    
    if status == 'ENROLLED':
        st.success("✅ Face ID is Active")
        if st.button("Reset Face ID"):
            # Yahan reset ka logic baad mein daal sakte hain
            pass
    else:
        st.warning("⚠️ Face ID not registered.")
        img = st.camera_input("Apna chehra scan karein register karne ke liye")
        
        if img:
            if st.button("Save Face ID"):
                with st.spinner("Processing biometric data..."):
                    success, msg = register_face(user_info['id'], role, img)
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.info("Agli baar login par aap se Face Scan manga jayega.")
                    else:
                        st.error(msg)

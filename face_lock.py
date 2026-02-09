import streamlit as st

def render_face_lock_setup(user_info, role):
    st.header("🛡️ Face Lock Registration")
    st.info(f"Welcome {user_info.get('name', 'User')}. Please set up your Face ID for enhanced security.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Capture Face")
        st.write("Apna chehra camera ke samne rakhein aur 'Capture' dabayein.")
        img_file = st.camera_input("Take a photo")
        
    with col2:
        st.subheader("2. Status")
        if img_file:
            st.success("Face Captured Successfully!")
            st.button("Register Face ID")
        else:
            st.warning("Waiting for camera input...")

    st.markdown("---")
    st.write("💡 **Note:** Face lock enable karne ke baad, login ke waqt aapko camera se verify karna hoga.")

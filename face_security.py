import streamlit as st

def render_face_lock_setup(user_info):
    st.header("🔒 Face Security System")
    st.info("Set up facial recognition to secure your portal access.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Register Face")
        st.write("Current Status: 🔴 Not Registered")
        if st.button("Open Camera & Scan"):
            st.warning("Face scanning module is being initialized...")
            # Yahan hum OpenCV ya deep learning logic future mein dalenge
            
    with col2:
        st.subheader("2. Security Settings")
        st.toggle("Enable Face Login", value=False)
        st.toggle("Lock Portal on Face Change", value=False)
        
    st.markdown("---")
    st.write("### 🛡️ Secure Activity Log")
    st.caption("No recent security events found.")

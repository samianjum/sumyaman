import streamlit as st
import os
import socket

SESSION_FILE = ".hq_session"
ALLOWED_MACHINE = "debian"

def get_machine_id():
    return socket.gethostname()

def check_access():
    if "hq_authenticated" not in st.session_state:
        st.session_state["hq_authenticated"] = False

    if os.path.exists(SESSION_FILE):
        st.session_state["hq_authenticated"] = True

    if not st.session_state["hq_authenticated"]:
        st.markdown("<h1 style='color: #FF4B4B; text-align: center;'>🛡️ HQ BIOMETRIC GATE</h1>", unsafe_allow_html=True)
        
        current_machine = get_machine_id()
        if current_machine != ALLOWED_MACHINE:
            st.error(f"🚨 ACCESS DENIED: Unauthorized Device ({current_machine})")
            return False

        with st.form("secure_login"):
            u = st.text_input("👤 ADMIN ID")
            p = st.text_input("🔑 SECRET KEY", type="password")
            if st.form_submit_button("AUTHORIZE"):
                if u == "sami" and p == "summaya":
                    with open(SESSION_FILE, "w") as f:
                        f.write("verified")
                    st.session_state["hq_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
        return False
    return True

def logout_user():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    st.session_state["hq_authenticated"] = False
    st.rerun()

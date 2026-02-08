import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    st.title("📱 APS Mobile Portal")
    
    if 'user_info' in st.session_state:
        u = st.session_state.user_info
        # Connection hum main_app se pass karenge ya yahan dobara banayenge
        # Filhal render_student_attendance ko user_info pass kar rahe hain
        render_student_attendance(u)
    else:
        st.error("User info not found. Please login again.")

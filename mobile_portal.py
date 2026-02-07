import streamlit as st
import pandas as pd
from attendance_logic import render_student_attendance

def render_mobile_view():
    st.title("📱 APS Mobile Portal")
    st.write("Welcome to the student/teacher portal.")
    render_student_attendance()

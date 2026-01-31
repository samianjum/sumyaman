import streamlit as st
import pandas as pd
from apsokara.models import Attendance, Student

def show_attendance_viewer():
    st.header("📅 Attendance Radar")
    
    col1, col2 = st.columns(2)
    with col1:
        target_date = st.date_input("Select Date")
    with col2:
        view_type = st.selectbox("View By", ["All", "Boys Wing", "Girls Wing"])

    # Query Attendance
    qs = Attendance.objects.filter(date=target_date)
    
    if view_type != "All":
        wing_name = "Boys" if "Boys" in view_type else "Girls"
        qs = qs.filter(student__wing=wing_name)

    if qs.exists():
        data = []
        for att in qs:
            data.append({
                "Student": att.student.full_name,
                "Roll No": att.student.roll_number,
                "Class": att.student.student_class,
                "Status": att.status
            })
        df = pd.DataFrame(data)
        
        # Stats Cards
        p_count = len(df[df['Status'] == 'Present'])
        a_count = len(df[df['Status'] == 'Absent'])
        
        c1, c2 = st.columns(2)
        c1.metric("Present ✅", p_count)
        c2.metric("Absent ❌", a_count)
        
        st.dataframe(df, width='stretch')
    else:
        st.warning(f"No attendance records found for {target_date}")

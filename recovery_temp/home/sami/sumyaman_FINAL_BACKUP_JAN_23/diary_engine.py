import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def render_diary(u):
    st.subheader("📓 Digital School Diary")
    conn = sqlite3.connect('db.sqlite3')
    
    # Safe data fetching from session
    is_student = "student_class" in u
    c_name = u.get('student_class') or u.get('incharge_class') or "N/A"
    sec = u.get('student_section') or u.get('incharge_section') or "N/A"
    wing = u.get('wing') or "Boys"

    if not is_student:
        st.markdown("### 🖋️ Post New Entry")
        with st.form("diary_form"):
            subj_val = st.text_input("Subject Name")
            content = st.text_area("Diary Message")
            if st.form_submit_button("Post to Class"):
                cur = conn.cursor()
                query = "INSERT INTO apsokara_diary (class_name, section, wing, subject_name, diary_content, date_posted, teacher_name) VALUES (?,?,?,?,?,?,?)"
                cur.execute(query, (c_name, sec, wing, subj_val, content, date.today().isoformat(), u.get('full_name', 'Teacher')))
                conn.commit()
                st.success("Diary posted successfully!")

    st.markdown("---")
    st.markdown("### 📅 Recent Diary Entries")
    query = "SELECT date_posted, subject_name, diary_content FROM apsokara_diary WHERE class_name=? AND section=? AND wing=? ORDER BY id DESC LIMIT 10"
    try:
        df = pd.read_sql(query, conn, params=(c_name, sec, wing))
        if df.empty:
            st.info("No diary entries found for your class.")
        else:
            for _, row in df.iterrows():
                with st.expander(f"📌 {row['date_posted']} - {row['subject_name']}"):
                    st.write(row['diary_content'])
    except Exception as e:
        st.error(f"Error: {e}")
    
    conn.close()

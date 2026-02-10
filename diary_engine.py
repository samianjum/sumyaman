import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def get_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# ======================== TEACHER SIDE ========================
def render_teacher_diary(u):
    st.markdown("<h2 style='text-align: center;'>📓 Teacher Diary Manager</h2>", unsafe_allow_html=True)
    
    teacher_id = u.get('id')
    conn = get_db()
    
    # Check assignments
    query = "SELECT student_class, section, wing, subject_id FROM apsokara_subjectassignment WHERE teacher_id = ?"
    assignments = [dict(row) for row in conn.execute(query, (teacher_id,)).fetchall()]
    
    if not assignments:
        st.warning("No classes assigned to you.")
        conn.close()
        return

    mode = st.segmented_control("Select Mode", ["Post New Diary", "View History"], default="Post New Diary")
    st.markdown("---")

    if mode == "Post New Diary":
        class_options = [f"{a['student_class']}-{a['section']} ({a['wing']})" for a in assignments]
        selected_class = st.selectbox("🎯 Select Class to Post", class_options)
        
        target = assignments[class_options.index(selected_class)]

        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                subject_name = st.text_input("📚 Subject / Chapter Name")
            with col2:
                post_date = st.date_input("📅 Posting Date", date.today())
            
            diary_text = st.text_area("📝 Diary Content", height=200)
            
            if st.button("🚀 Publish Diary", use_container_width=True, type="primary"):
                if diary_text and subject_name:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO apsokara_dailydiary 
                                 (teacher_id, teacher_name, class, section, subject, content, date_posted) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                                 (teacher_id, u.get('full_name'), target['student_class'], 
                                  target['section'], subject_name, diary_text, post_date))
                    conn.commit()
                    st.success(f"✅ Diary Published for {selected_class}!")
                else:
                    st.error("Please fill all details.")
    else:
        # History
        df = pd.read_sql("SELECT date_posted, class, section, subject, content FROM apsokara_dailydiary WHERE teacher_id=? ORDER BY date_posted DESC", conn, params=(teacher_id,))
        if not df.empty:
            for _, row in df.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['date_posted']} | Class {row['class']}-{row['section']} | {row['subject']}**")
                    st.write(row['content'])
        else:
            st.info("No records found.")
    conn.close()

# ======================== STUDENT SIDE ========================
def render_student_diary(u):
    st.markdown("<h2 style='text-align: center;'>📅 My Class Diary</h2>", unsafe_allow_html=True)
    
    # Important: Hum 'student_class' aur 'student_section' sessions se utha rahe hain
    # Jo login ke waqt humne session_state 'u' mein save kiye thay
    s_class = u.get('student_class') or u.get('class_name')
    s_sec = u.get('student_section') or u.get('section')
    
    if not s_class or not s_sec:
        st.error("Class or Section not found in your profile.")
        return

    st.info(f"📍 Viewing Diary for: **Class {s_class}-{s_sec}**")
    
    conn = get_db()
    # Connection: Fetching diary where class and section matches student's profile
    query = """SELECT date_posted, subject, content, teacher_name 
                 FROM apsokara_dailydiary 
                 WHERE class=? AND section=? 
                 ORDER BY date_posted DESC LIMIT 15"""
    
    df = pd.read_sql(query, conn, params=(str(s_class), str(s_sec)))
    conn.close()

    if not df.empty:
        # Latest diary entry special highlight
        latest = df.iloc[0]
        st.markdown("#### ✨ Latest Entry")
        with st.container(border=True):
            st.markdown(f"### {latest['subject']}")
            st.caption(f"🗓 {latest['date_posted']} | 👨‍🏫 {latest['teacher_name']}")
            st.write(latest['content'])
        
        st.markdown("---")
        st.markdown("#### 📜 Previous Entries")
        for i in range(1, len(df)):
            row = df.iloc[i]
            with st.expander(f"📅 {row['date_posted']} - {row['subject']}"):
                st.write(row['content'])
                st.caption(f"Posted by: {row['teacher_name']}")
    else:
        st.warning("No diary entries found for your class yet.")
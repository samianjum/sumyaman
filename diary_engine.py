import sqlite3
import pandas as pd
import streamlit as st
from datetime import date

def get_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def draw_aps_banner(title, subtitle):
    st.markdown(f'''
        <div style="background-color: #1b4332; padding: 25px; border-radius: 15px; margin-bottom: 25px; border-bottom: 5px solid #d4af37; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <h1 style="color: #d4af37; margin: 0; font-size: 28px; font-family: 'Arial'; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{title}</h1>
            <p style="color: #ffffff; margin: 0; opacity: 0.9; font-weight: bold;">{subtitle}</p>
        </div>
    ''', unsafe_allow_html=True)

def render_teacher_diary(u):
    draw_aps_banner("TEACHER DIARY PORTAL", f"Welcome: {u.get('full_name')} | APS Okara")
    teacher_id = u.get('id')
    conn = get_db()
    
    # Accurate JOIN logic using 'name' column from apsokara_subject
    query = """
        SELECT a.student_class, a.section, a.wing, a.subject_id, s.name as sub_name 
        FROM apsokara_subjectassignment a
        LEFT JOIN apsokara_subject s ON a.subject_id = s.id
        WHERE a.teacher_id = ?
    """
    assignments = [dict(row) for row in conn.execute(query, (teacher_id,)).fetchall()]
    
    if not assignments:
        st.warning("No assigned classes or subjects found.")
        conn.close()
        return

    mode = st.segmented_control("Action", ["🖋 Write New", "📜 History"], default="🖋 Write New")

    if mode == "🖋 Write New":
        # Format: Class 10-D | Mathematics
        class_options = [f"{a['student_class']}-{a['section']} | {a['sub_name'] if a['sub_name'] else 'Unknown'}" for a in assignments]
        selected_raw = st.selectbox("Select Class & Subject:", class_options)
        
        target = assignments[class_options.index(selected_raw)]
        final_sub_name = target['sub_name'] if target['sub_name'] else f"Subject {target['subject_id']}"

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                # Hum ne subject name ko ab text input mein lock kar diya hai jo edit ho sakta hai
                subj_input = st.text_input("📚 Subject", value=final_sub_name)
            with col2:
                post_date = st.date_input("📅 Date", date.today())
            
            diary_text = st.text_area("📝 Homework Details", height=150)
            
            if st.button("🚀 PUBLISH TO PORTAL", use_container_width=True, type="primary"):
                if diary_text and subj_input:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO apsokara_dailydiary 
                                 (teacher_id, teacher_name, class, section, subject, content, date_posted) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                                 (teacher_id, u.get('full_name'), target['student_class'], 
                                  target['section'], subj_input, diary_text, post_date))
                    conn.commit()
                    st.success(f"✅ Diary Published for {subj_input}!")
                else:
                    st.error("Missing Subject or Content!")
    else:
        df = pd.read_sql("SELECT date_posted, class, section, subject, content FROM apsokara_dailydiary WHERE teacher_id=? ORDER BY date_posted DESC", conn, params=(teacher_id,))
        for _, row in df.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['date_posted']} | {row['class']}-{row['section']} | {row['subject']}**")
                st.write(row['content'])
    conn.close()

def render_student_diary(u):
    draw_aps_banner("STUDENT DAILY DIARY", f"Student: {u.get('full_name')} | Class: {u.get('student_class')}-{u.get('student_section')}")
    s_class, s_sec = u.get('student_class'), u.get('student_section')
    
    conn = get_db()
    query = """SELECT date_posted, subject, content, teacher_name 
                 FROM apsokara_dailydiary WHERE class=? AND section=? 
                 ORDER BY date_posted DESC LIMIT 15"""
    df = pd.read_sql(query, conn, params=(str(s_class), str(s_sec)))
    conn.close()

    if not df.empty:
        for _, row in df.iterrows():
            st.markdown(f'''
                <div style="background-color: white; border-radius: 12px; border: 1px solid #e0e0e0; border-top: 6px solid #1b4332; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <span style="font-size: 20px; font-weight: 800; color: #1b4332;">📘 {row['subject']}</span>
                        <span style="background-color: #d4af37; color: #1b4332; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold;">📅 {row['date_posted']}</span>
                    </div>
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #d4af37; color: #333; line-height: 1.6; font-size: 16px; margin-bottom: 15px;">
                        {row['content']}
                    </div>
                    <div style="text-align: right; border-top: 1px solid #eee; padding-top: 10px;">
                        <span style="color: #666; font-style: italic; font-size: 13px;">👨‍🏫 Teacher: <b>{row['teacher_name']}</b></span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No diary entries found.")
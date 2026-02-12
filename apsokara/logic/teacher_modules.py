import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def render_marks_entry(u):
    st.subheader('🎯 Marks Entry Portal')
    conn = sqlite3.connect('db.sqlite3')
    today = date.today().isoformat()
    q_exams = 'SELECT DISTINCT e.* FROM exams e JOIN apsokara_subjectassignment sa ON sa.student_class = e.class_group WHERE e.start_date <= ? AND e.end_date >= ? AND sa.teacher_id = ?'
    active_exams = pd.read_sql_query(q_exams, conn, params=(today, today, u['id']))
    if active_exams.empty:
        st.info('📢 No active exams found for your assigned classes.')
        conn.close()
        return
    exam_option = st.selectbox('Select Active Exam', active_exams['name'].tolist())
    sel_exam = active_exams[active_exams['name'] == exam_option].iloc[0]
    q_assign = 'SELECT sa.id, sa.student_class, sa.section, sa.wing, sub.name as sub_name, sub.id as sub_id FROM apsokara_subjectassignment sa JOIN apsokara_subject sub ON sa.subject_id = sub.id WHERE sa.teacher_id = ? AND sa.student_class = ?'
    assigns = pd.read_sql_query(q_assign, conn, params=(u['id'], sel_exam['class_group']))
    if assigns.empty:
        st.error('No subjects assigned to you for this class group.')
        return
    labels = [f"{r['student_class']}-{r['section']} ({r['wing']}) - {r['sub_name']}" for _, r in assigns.iterrows()]
    target = st.selectbox('Select Class & Subject', labels)
    target_row = assigns.iloc[labels.index(target)]
    check_lock = pd.read_sql_query('SELECT is_locked FROM student_marks WHERE exam_id=? AND subject_id=? LIMIT 1', conn, params=(int(sel_exam['id']), int(target_row['sub_id'])))
    locked = not check_lock.empty and check_lock.iloc[0]['is_locked'] == 1
    if locked: st.warning('🔒 Result finalized by Class Teacher. Editing disabled.')
    q_stu = 'SELECT id, full_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?'
    students = pd.read_sql_query(q_stu, conn, params=(target_row['student_class'], target_row['section'], target_row['wing']))
    with st.form('marks_form'):
        total_m = st.number_input('Total Marks', min_value=1, value=100, disabled=locked)
        marks_data = []
        for _, s in students.iterrows():
            prev = pd.read_sql_query('SELECT obtained_marks, remarks FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id=?', conn, params=(int(sel_exam['id']), s['id'], int(target_row['sub_id'])))
            val, rem = (prev.iloc[0]['obtained_marks'], prev.iloc[0]['remarks']) if not prev.empty else (0.0, '')
            c1, c2, c3 = st.columns([2, 1, 2])
            c1.write(f'**{s["full_name"]}**')
            obt = c2.number_input('Obt', key=f'm_{s["id"]}', value=float(val), max_value=float(total_m), disabled=locked)
            rmk = c3.text_input('Remarks', key=f'r_{s["id"]}', value=rem, disabled=locked)
            marks_data.append((s['id'], obt, rmk))
        if st.form_submit_button('Submit Marks') and not locked:
            c = conn.cursor()
            for sid, m, r in marks_data:
                c.execute('INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, ?, ?, ?, ?, ?, 0)', (int(sel_exam['id']), sid, int(target_row['sub_id']), u['id'], total_m, m, r))
            conn.commit()
            st.success('✅ Marks Saved!')
    conn.close()
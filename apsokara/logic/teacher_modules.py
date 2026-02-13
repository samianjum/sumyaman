import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime

def render_marks_entry(u):
    conn = sqlite3.connect('db.sqlite3')
    today = date.today().isoformat()
    
    q_exams = 'SELECT DISTINCT e.* FROM exams e JOIN apsokara_subjectassignment sa ON sa.student_class = e.class_group WHERE e.start_date <= ? AND e.end_date >= ? AND sa.teacher_id = ?'
    active_exams = pd.read_sql_query(q_exams, conn, params=(today, today, u['id']))
    
    if active_exams.empty:
        st.info('NO ACTIVE EXAMS FOUND')
        conn.close()
        return

    st.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:15px;'><span style='background:#1b4332; color:white; padding:2px 10px; border-radius:4px; font-size:10px; font-weight:800;'>LIVE</span><span style='color:#666; font-size:12px; font-weight:600; letter-spacing:1px;'>ACADEMIC DATABASE ACCESS</span></div>", unsafe_allow_html=True)
    exam_names = active_exams['name'].tolist()
    sel_exam_name = st.segmented_control("EXAM SESSION", options=exam_names, default=exam_names[0])
    sel_exam = active_exams[active_exams['name'] == sel_exam_name].iloc[0]

    q_assign = 'SELECT sa.id, sa.student_class, sa.section, sa.wing, sub.name as sub_name, sub.id as sub_id FROM apsokara_subjectassignment sa JOIN apsokara_subject sub ON sa.subject_id = sub.id WHERE sa.teacher_id = ? AND sa.student_class = ?'
    assigns = pd.read_sql_query(q_assign, conn, params=(u['id'], sel_exam['class_group']))
    
    if assigns.empty:
        st.error('NO SUBJECTS ASSIGNED')
        conn.close()
        return

    # --- UPDATED DROPDOWN LABELS FOR CLARITY ---
    labels = [f"{r['sub_name'].upper()} | CLASS: {r['student_class']}-{r['section']} | WING: {r['wing'].upper()}" for _, r in assigns.iterrows()]
    target = st.selectbox('IDENTIFY ASSIGNMENT (SUBJECT | CLASS | WING)', labels)
    target_row = assigns.iloc[labels.index(target)]

    # --- HIGH VISIBILITY 3-COLUMN BANNER ---
    c_class = str(target_row['student_class'])
    c_sec = str(target_row['section'])
    c_wing = str(target_row['wing']).upper()
    c_exam = str(sel_exam_name)
    c_end = str(sel_exam['end_date'])

    h = '<div style="background: #1b4332; padding: 35px 45_px; border-radius: 15px; border-bottom: 8px solid #d4af37; color: white; margin: 25px 0; display: grid; grid-template-columns: 1.5fr 1fr 1fr; align-items: center; box-shadow: 0 15px 35px rgba(0,0,0,0.3);">'
    h += '  <div style="text-align: left; border-right: 2px solid rgba(255,255,255,0.15); padding-right: 20px;">'
    h += '      <div style="font-size: 13px; color: #d4af37; font-weight: 800; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px;">Current Session</div>'
    h += '      <div style="font-size: 42px; font-weight: 900; text-transform: uppercase; line-height: 1; color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">' + c_exam + '</div>'
    h += '  </div>'
    h += '  <div style="text-align: center;">'
    h += '      <div style="font-size: 12px; color: #d4af37; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">Closing Date</div>'
    h += '      <div style="font-size: 24px; font-weight: 800; color: #ffffff; margin-top: 5px;">' + c_end + '</div>'
    h += '      <div style="font-size: 10px; color: #88ff88; font-weight: 600; margin-top: 5px;">● SYSTEM ONLINE</div>'
    h += '  </div>'
    h += '  <div style="text-align: right; border-left: 2px solid rgba(255,255,255,0.15); padding-left: 20px;">'
    h += '      <div style="font-size: 32px; font-weight: 900; color: #d4af37; line-height: 1;">' + c_class + ' - ' + c_sec + '</div>'
    h += '      <div style="font-size: 15px; font-weight: 700; color: #ffffff; margin-top: 8px; letter-spacing: 1px;">' + c_wing + ' WING</div>'
    h += '  </div>'
    h += '</div>'

    st.markdown(h, unsafe_allow_html=True)

    q_final = 'SELECT id FROM student_marks WHERE exam_id=? AND CAST(subject_id AS INTEGER)=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?) LIMIT 1'
    locked = not pd.read_sql_query(q_final, conn, params=(int(sel_exam['id']), target_row['student_class'], target_row['section'], target_row['wing'])).empty

    if locked:
        st.markdown('<div style="background:#800000; color:#ffffff; padding:15px; border-radius:8px; text-align:center; font-weight:900; margin-bottom:25px; border:2px solid #ff0000; letter-spacing:1px;">ACCESS DENIED: PORTAL LOCKED BY CLASS TEACHER</div>', unsafe_allow_html=True)

    students = pd.read_sql_query('SELECT id, full_name, father_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?', conn, params=(target_row['student_class'], target_row['section'], target_row['wing']))
    
    with st.form('marks_entry_form'):
        col_t, col_info = st.columns([1, 2])
        total_m = col_t.number_input('MAX MARKS', min_value=1, value=100, disabled=locked)
        col_info.markdown(f"<div style='text-align:right; color:#666; font-weight:600; padding-top:10px;'>Total Students: {len(students)}</div>", unsafe_allow_html=True)
        st.divider()
        
        marks_data = []
        for _, s in students.iterrows():
            prev = pd.read_sql_query('SELECT obtained_marks, remarks FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id=?', conn, params=(int(sel_exam['id']), s['id'], int(target_row['sub_id'])))
            val, rem = (prev.iloc[0]['obtained_marks'], prev.iloc[0]['remarks']) if not prev.empty else (0.0, '')
            
            c1, c2 = st.columns([2.5, 3])
            c1.markdown(f"<div style='border-left:4px solid #1b4332; padding-left:10px;'><b style='font-size:16px;'>{s['full_name']}</b><br><span style='color:#555; font-size:12px;'>ROLL: {s['roll_number']} | S/O: {s['father_name'].upper()}</span></div>", unsafe_allow_html=True)
            m_col, r_col = c2.columns([1, 2])
            obt = m_col.number_input('Marks', key=f'm_{s["id"]}', value=float(val), max_value=float(total_m), disabled=locked, label_visibility='collapsed')
            rmk = r_col.text_input('Remarks', key=f'r_{s["id"]}', value=rem, placeholder='Required...', disabled=locked, label_visibility='collapsed')
            marks_data.append((s['id'], obt, rmk))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button('AUTHORIZE & COMMIT DATA', use_container_width=True, type='primary') and not locked:
            if any(not str(m[2]).strip() for m in marks_data):
                st.warning('FIELD ERROR: ALL REMARKS ARE MANDATORY')
            else:
                c = conn.cursor()
                for sid, m, r in marks_data:
                    c.execute('INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, ?, ?, ?, ?, ?, 0)', (int(sel_exam['id']), sid, int(target_row['sub_id']), u['id'], total_m, m, r))
                conn.commit()
                st.toast('DATA SECURED SUCCESSFULLY')
                st.rerun()
    conn.close()

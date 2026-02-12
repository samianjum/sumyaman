import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

def render_apply_leave(u):
    st.markdown('<h2 style="color:#1E1B4B;">📝 Apply for Leave</h2>', unsafe_allow_html=True)
    with st.form("leave_form"):
        c1, c2 = st.columns(2)
        f_date = c1.date_input("From Date", min_value=date.today())
        t_date = c2.date_input("To Date", min_value=date.today())
        reason = st.text_area("Reason for Leave")
        submitted = st.form_submit_button("Submit Request")
        if submitted:
            if reason:
                with sqlite3.connect('db.sqlite3') as conn:
                    conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, wing, from_date, to_date, reason, status) VALUES (?,?,?,?,?,?,?,?)",
                                 (u['id'], u['full_name'], u['student_class'], u['wing'], f_date.isoformat(), t_date.isoformat(), reason, 'Pending'))
            else: st.error("Please provide a reason.")

def render_my_result(u):
    st.markdown('<h2 style="color:#1E1B4B;">🏆 Academic Performance Portal</h2>', unsafe_allow_html=True)
    conn = sqlite3.connect('db.sqlite3')
    s_id = u.get('id')
    
    # Query for exams student has participated in
    query = """
        SELECT DISTINCT e.id, e.name, e.end_date 
        FROM exams e
        JOIN student_marks m ON e.id = m.exam_id
        WHERE m.student_id = ?
        ORDER BY e.end_date DESC
    """
    available_exams = pd.read_sql_query(query, conn, params=(s_id,))
    
    if available_exams.empty:
        st.info('📢 Abhi tak aapka koi result publish nahi hua.')
        conn.close()
        return

    exam_list = available_exams['name'].tolist()
    sel_exam_name = st.selectbox('Select Exam', exam_list)
    ex_id = int(available_exams[available_exams['name'] == sel_exam_name].iloc[0]['id'])

    # FIXED QUERY: Using MAX(id) and GROUP BY to remove duplicates
    q_marks = """
        SELECT sub.name as Subject, m.total_marks, m.obtained_marks, m.remarks
        FROM student_marks m
        JOIN apsokara_subject sub ON m.subject_id = sub.id
        WHERE m.exam_id = ? AND m.student_id = ?
        GROUP BY m.subject_id
        HAVING m.id = MAX(m.id)
    """
    marks_df = pd.read_sql_query(q_marks, conn, params=(ex_id, s_id))

    if not marks_df.empty:
        total_obt = marks_df['obtained_marks'].sum()
        total_max = marks_df['total_marks'].sum()
        perc = (total_obt / total_max * 100) if total_max > 0 else 0
        grade = 'A+' if perc >= 90 else 'A' if perc >= 80 else 'B' if perc >= 70 else 'C' if perc >= 60 else 'D' if perc >= 50 else 'F'
        status = 'PASSED' if perc >= 33 else 'FAILED'
        
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 15px; border: 2px solid #E2E8F0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
            <h3 style="text-align:center; color:#1E1B4B;">{sel_exam_name.upper()}</h3>
            <div style="display:flex; justify-content:space-around; font-weight:bold; margin-top:15px;">
                <div style="text-align:center;"><small>Score</small><br>{total_obt}/{total_max}</div>
                <div style="text-align:center;"><small>Percentage</small><br>{perc:.1f}%</div>
                <div style="text-align:center;"><small>Grade</small><br>{grade}</div>
                <div style="text-align:center;"><small>Status</small><br><span style="color:{'green' if status=='PASSED' else 'red'};">{status}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)
        
        st.write("### Subject Wise Details")
        st.table(marks_df)
    else:
        st.warning('Result process ho raha hai...')
    conn.close()
import streamlit as st
import pandas as pd
import sqlite3

def render_leave_approvals(u):
    u_class, u_wing = u.get('class'), u.get('wing')
    st.markdown('<h2 style="color:#1E1B4B;">📥 New Leave Requests</h2>', unsafe_allow_html=True)
    with sqlite3.connect('db.sqlite3', timeout=30) as conn:
        pending = pd.read_sql("SELECT * FROM apsokara_studentleave WHERE class=? AND wing=? AND status='Pending'", conn, params=(u_class, u_wing))
    if pending.empty:
        st.success('No pending requests today!')
    else:
        for _, r in pending.iterrows():
            st.info(f"{r['name']} (Roll: {r['student_id']})")
            if st.button('Approve ✅', key=f'ap_{r["id"]}'):
                with sqlite3.connect('db.sqlite3') as conn: conn.execute('UPDATE apsokara_studentleave SET status="Approved" WHERE id=?', (r['id'],))
                st.rerun()

def render_final_upload(u):
    st.subheader(f'📤 Final Result Dashboard: {u.get("class")}-{u.get("sec")}')
    conn = sqlite3.connect('db.sqlite3')
    
    # 1. Sirf wahi exam uthao jo is class group ke liye active hai
    exam = pd.read_sql_query('SELECT * FROM exams WHERE class_group=? AND is_active=1', conn, params=(u['class'],))
    if exam.empty:
        st.info('📢 Abhi is Class Group ka koi Exam active nahi hai.')
        return
    
    ex_id = int(exam.iloc[0]['id'])
    st.markdown(f'### Status for: **{exam.iloc[0]["name"]}**')

    # 2. SAKHT FILTER: Sirf wahi assignments jo is specific Class-Section-Wing ke hain
    q_status = """
        SELECT sub.name as Subject, t.full_name as Teacher,
        (SELECT COUNT(*) FROM student_marks 
         WHERE exam_id=? AND subject_id=sub.id 
         AND teacher_id=t.id 
         AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)) as entries
        FROM apsokara_subjectassignment sa
        JOIN apsokara_subject sub ON sa.subject_id = sub.id
        JOIN apsokara_teacher t ON sa.teacher_id = t.id
        WHERE sa.student_class=? AND sa.section=? AND sa.wing=?
    """
    params = (ex_id, u['class'], u['sec'], u['wing'], u['class'], u['sec'], u['wing'])
    status_df = pd.read_sql_query(q_status, conn, params=params)
    
    # Status Table Display
    def highlight_status(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'

    if not status_df.empty:
        st.write('#### 📋 Teachers Submission Status')
        # Displaying a cleaner version
        display_df = status_df.copy()
        display_df['Status'] = display_df['entries'].apply(lambda x: '✅ Submitted' if x > 0 else '❌ Pending')
        st.table(display_df[['Subject', 'Teacher', 'Status']])
    
    # 3. Finalization Logic
    is_ready = (status_df['entries'] > 0).all() if not status_df.empty else False
    
    if is_ready:
        st.success('🎯 Sab teachers ne marks jama kar diye hain. Ab aap bacho ki progress check karein.')
        # Auto-Calculation Section
        students = pd.read_sql_query('SELECT id, full_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?', conn, params=(u['class'], u['sec'], u['wing']))
        
        all_remarks_filled = True
        for _, s in students.iterrows():
            m_df = pd.read_sql_query('SELECT obtained_marks, total_marks FROM student_marks WHERE exam_id=? AND student_id=?', conn, params=(ex_id, s['id']))
            t_obt, t_max = m_df['obtained_marks'].sum(), m_df['total_marks'].sum()
            perc = (t_obt / t_max * 100) if t_max > 0 else 0
            status = 'Pass' if perc >= 33 else 'Fail' # Default 33% logic
            
            with st.expander(f"{s['full_name']} (Roll: {s['roll_number']}) - {perc:.1f}% [{status}] "):
                rem = st.text_area(f'Class Teacher Remarks for {s["full_name"]}', key=f'rem_{s["id"]}')
                if not rem: all_remarks_filled = False
        
        if all_remarks_filled and st.button('🚀 FINAL PUBLISH RESULT'):
            st.balloons()
            st.success('Result Finalize ho gaya aur lock ho gaya!')
    elif status_df.empty:
        st.warning('Is class ke liye koi subjects assign nahi kiye gaye.')
    else:
        st.warning('⏳ Jab tak saare subject teachers marks upload nahi karte, aap finalize nahi kar sakte.')
    
    conn.close()
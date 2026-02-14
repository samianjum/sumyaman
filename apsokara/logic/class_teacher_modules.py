import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

def render_leave_approvals(u):
    st.markdown('<div style="background:#1b4332; padding:15px; border-radius:10px; border-left:8px solid #d4af37; margin-bottom:20px;"><h3 style="color:white; margin:0;">📥 LEAVE APPROVALS</h3></div>', unsafe_allow_html=True)
    with sqlite3.connect('db.sqlite3') as conn:
        pending = pd.read_sql("SELECT * FROM apsokara_studentleave WHERE class=? AND wing=? AND status='Pending'", conn, params=(u.get('class'), u.get('wing')))
    if pending.empty:
        st.info('No pending requests.')
    else:
        for _, r in pending.iterrows():
            with st.container():
                st.write(f"**{r['name']}** (Roll: {r['student_id']})")
                if st.button('Approve', key=f'ap_{r["id"]}'):
                    with sqlite3.connect('db.sqlite3') as conn: 
                        conn.execute('UPDATE apsokara_studentleave SET status="Approved" WHERE id=?', (r['id'],))
                    st.rerun()


def render_final_upload(u):
    conn = sqlite3.connect('db.sqlite3')
    today = date.today().isoformat()
    
    # Check for exam that is BOTH active AND within date range
    query = 'SELECT * FROM exams WHERE class_group=? AND is_active=1 AND start_date <= ? AND end_date >= ?'
    exam = pd.read_sql_query(query, conn, params=(u['class'], today, today))
    
    if exam.empty:
        st.markdown(f'<div style="background:linear-gradient(90deg, #1b4332, #081c15); padding:20px; border-radius:15px; border-bottom:5px solid #d4af37; text-align:center; margin-bottom:25px;"><h2 style="color:white; margin:0;">📤 FINAL RESULT DASHBOARD</h2><p style="color:#d4af37; margin:0;">{u.get("class")} - {u.get("sec")} | {u.get("wing")}</p></div>', unsafe_allow_html=True)
        st.info('📢 NO LIVE EXAM SESSION FOUND. Deactivated by HQ or Session Expired.')
        conn.close()
        return

    
    ex_name = exam.iloc[0]['name']
    ex_id = int(exam.iloc[0]['id'])

    st.markdown(f'''
        <div style="background:linear-gradient(135deg, #1b4332 0%, #081c15 100%); padding:25px; border-radius:15px; border-bottom:5px solid #d4af37; text-align:center; margin-bottom:25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="font-size:12px; color:#d4af37; font-weight:bold; text-transform:uppercase; letter-spacing:2px;">Publishing Portal</div>
            <h2 style="color:white; margin:5px 0; font-size:26px;">{ex_name}</h2>
            <div style="height:1px; background:rgba(212,175,55,0.3); width:50%; margin:10px auto;"></div>
            <p style="color:#ffffff; margin:0; font-size:14px; opacity:0.9;">{u.get("class")} {u.get("sec")} | {u.get("wing")}</p>
        </div>
    ''', unsafe_allow_html=True)
    
    q_status = """SELECT sub.name as Subject, t.full_name as Teacher, 
                 (SELECT COUNT(*) FROM student_marks WHERE exam_id=? AND subject_id=sub.id 
                  AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)) as entries 
                 FROM apsokara_subjectassignment sa 
                 JOIN apsokara_subject sub ON sa.subject_id = sub.id 
                 JOIN apsokara_teacher t ON sa.teacher_id = t.id 
                 WHERE sa.student_class=? AND sa.section=? AND sa.wing=?"""
    status_df = pd.read_sql_query(q_status, conn, params=(ex_id, u['class'], u['sec'], u['wing'], u['class'], u['sec'], u['wing']))
    
    q_is_published = "SELECT COUNT(*) FROM student_marks WHERE exam_id=? AND subject_id=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)"
    published_count = conn.execute(q_is_published, (ex_id, u['class'], u['sec'], u['wing'])).fetchone()[0]
    
    if published_count > 0:
        st.markdown('<div style="padding:40px; background:#f8fafc; border:2px dashed #1b4332; border-radius:15px; text-align:center;"><h3 style="color:#1b4332; margin:0;">✅ RESULT FINALIZED</h3><p style="color:#64748b; margin-top:10px;">The results for <b>'+ex_name+'</b> have been officially published. All data is now securely locked.</p></div>', unsafe_allow_html=True)
        conn.close()
        return

    st.markdown('### 📋 Submission Status')
    cols = st.columns(3)
    for i, (_, row) in enumerate(status_df.iterrows()):
        done = row['entries'] > 0
        bg, border = ('#f0fdf4', '#16a34a') if done else ('#fff7ed', '#ea580c')
        cols[i % 3].markdown(f'<div style="background:{bg}; border:1px solid {border}; padding:10px; border-radius:8px; margin-bottom:10px;"><div style="font-size:10px; font-weight:bold; color:{border};">{"● SUBMITTED" if done else "○ PENDING"}</div><div style="font-size:13px; font-weight:700; color:#1b4332;">{row["Subject"]}</div><div style="font-size:10px; color:#64748b;">{row["Teacher"]}</div></div>', unsafe_allow_html=True)

    is_ready = (status_df['entries'] > 0).all() if not status_df.empty else False
    
    if is_ready:
        st.markdown('---')
        st.markdown('### 📊 Class Performance & Remarks')
        students = pd.read_sql_query('SELECT id, full_name, father_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?', conn, params=(u['class'], u['sec'], u['wing']))
        
        with st.form("final_publish_form"):
            remarks_dict = {}
            for _, s in students.iterrows():
                marks_q = "SELECT obtained_marks, total_marks, subject_id FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id > 0"
                m_df = pd.read_sql_query(marks_q, conn, params=(ex_id, s['id']))
                total_obt = m_df['obtained_marks'].sum()
                total_max = m_df['total_marks'].sum()
                perc = (total_obt / total_max * 100) if total_max > 0 else 0
                # Ensure unique subjects for the current exam to avoid duplicate fail counting
                unique_marks = m_df.drop_duplicates(subset=['subject_id'])
                fails = len(unique_marks[unique_marks['obtained_marks'] < (unique_marks['total_marks'] * 0.33)])
                status_color = "#ef4444" if fails > 0 else "#16a34a"
                
                st.markdown(f'''
                    <div style="background:white; padding:12px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:5px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <b style="color:#1b4332;">{s["full_name"]}</b> <small>s/o {s["father_name"]}</small>
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:14px; font-weight:bold; color:{status_color};">{perc:.1f}% ({fails} Fails)</span>
                            </div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                remarks_dict[s['id']] = st.text_area('Remark', key=f"rem_{s['id']}", height=60, label_visibility='collapsed', placeholder=f'Summary for {s["full_name"]}...')
            
            if st.form_submit_button('🚀 PUBLISH & LOCK RESULT'):
                cursor = conn.cursor()
                for sid, rmk in remarks_dict.items():
                    cursor.execute("INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, 0, ?, 0, 0, ?, 1)", (ex_id, sid, u['id'], rmk))
                cursor.execute("UPDATE student_marks SET is_locked = 1 WHERE exam_id = ? AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)", (ex_id, u['class'], u['sec'], u['wing']))
                conn.commit()
                st.success('🌟 Result Successfully Published!')
                st.balloons()
                st.rerun()
    else:
        st.warning(f'⏳ Final Upload for **{ex_name}** is disabled until all subjects are submitted.')
    conn.close()

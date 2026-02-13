import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

def render_apply_leave(u):
    # --- ROYAL THEME FOR LEAVE ---
    st.markdown("""
        <style>
        .premium-card {
            background: #ffffff !important;
            border-radius: 15px !important;
            padding: 25px !important;
            border-left: 8px solid #1b4332 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
            margin-bottom: 25px !important;
        }
        .history-item {
            background: #f8f9fa !important;
            border-radius: 10px !important;
            padding: 15px !important;
            margin-bottom: 10px !important;
            border-right: 4px solid #d4af37 !important;
        }
        .status-badge {
            float: right;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color:#1b4332; margin:0;'>📝 LEAVE APPLICATION</h2>", unsafe_allow_html=True)
    with st.form("new_leave_form", border=False):
        c1, c2 = st.columns(2)
        start = c1.date_input("Start Date", date.today())
        end = c2.date_input("End Date", date.today())
        reason = st.text_area("Reason / Remarks")
        if st.form_submit_button("SUBMIT TO CLASS TEACHER", use_container_width=True):
            if reason.strip():
                with sqlite3.connect("db.sqlite3") as conn:
                    conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)", 
                                 (u['id'], u.get('full_name'), u['class'], u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending'))
                st.success("Application successfully transmitted.")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h3 style='color:#1b4332; letter-spacing:1px;'>PREVIOUS HISTORY</h3>", unsafe_allow_html=True)
    with sqlite3.connect("db.sqlite3") as conn:
        df = pd.read_sql("SELECT * FROM apsokara_studentleave WHERE student_id=? ORDER BY id DESC", conn, params=(u['id'],))
    
    if df.empty:
        st.info("No leave records found.")
    else:
        for _, r in df.iterrows():
            color = "#D97706" if r['status'] == "Pending" else ("#16A34A" if r['status'] == "Approved" else "#DC2626")
            st.markdown(f"""
                <div class="history-item">
                    <span class="status-badge" style="background:{color}; color:white;">{r['status']}</span>
                    <b style="color:#1b4332;">{r['reason']}</b><br>
                    <small style="color:#666;">Period: {r['from_date']} to {r['to_date']}</small>
                </div>
            """, unsafe_allow_html=True)

def render_my_result(u):
    conn = sqlite3.connect('db.sqlite3')
    
    # --- SEARCH FOR PUBLISHED EXAMS ONLY (subject_id=0 means published) ---
    q_published = """
        SELECT DISTINCT e.id, e.name 
        FROM exams e 
        JOIN student_marks sm ON e.id = sm.exam_id 
        WHERE sm.student_id = ? AND sm.subject_id = 0
    """
    published_exams = pd.read_sql_query(q_published, conn, params=(u['id'],))

    if published_exams.empty:
        st.markdown("<div style='text-align:center; padding:50px;'><h1 style='color:#ccc;'>😶</h1><h3>NO RESULTS PUBLISHED YET</h3><p>Results will appear here once finalized by your Class Teacher.</p></div>", unsafe_allow_html=True)
        conn.close()
        return

    sel_exam_name = st.selectbox("SELECT EXAMINATION", published_exams['name'])
    sel_exam_id = published_exams[published_exams['name'] == sel_exam_name].iloc[0]['id']

    # --- THE ROYAL REPORT CARD BANNER ---
    st.markdown(f"""
        <div style="background:#1b4332; padding:30px; border-radius:15px; border-bottom:8px solid #d4af37; color:white; text-align:center; margin-bottom:25px;">
            <div style="font-size:12px; color:#d4af37; font-weight:800; letter-spacing:2px;">OFFICIAL PROGRESS REPORT</div>
            <h1 style="margin:5px 0; font-size:35px;">{sel_exam_name.upper()}</h1>
            <div style="font-size:18px; opacity:0.9;">{u['full_name']} | Roll: {u.get('roll_number', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- GET SUBJECT MARKS ---
    q_marks = """
        SELECT s.name as Subject, sm.total_marks, sm.obtained_marks, sm.remarks
        FROM student_marks sm
        JOIN apsokara_subject s ON sm.subject_id = s.id
        WHERE sm.id IN (
            SELECT MAX(id) FROM student_marks 
            WHERE exam_id = ? AND student_id = ? AND subject_id > 0 
            GROUP BY subject_id
        )
    """
    marks_df = pd.read_sql_query(q_marks, conn, params=(int(sel_exam_id), u['id']))
    
    # --- GET CLASS TEACHER REMARKS (From subject_id=0) ---
    q_final = "SELECT remarks FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id=0"
    final_remarks = conn.execute(q_final, (int(sel_exam_id), u['id'])).fetchone()
    ct_remark = final_remarks[0] if final_remarks else "No remarks provided."

    if not marks_df.empty:
        # Display Table
        st.dataframe(marks_df, use_container_width=True, hide_index=True)
        
        # Summary Stats
        t_obt = marks_df['obtained_marks'].sum()
        t_max = marks_df['total_marks'].sum()
        perc = (t_obt / t_max * 100) if t_max > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("TOTAL MARKS", f"{int(t_obt)} / {int(t_max)}")
        c2.metric("PERCENTAGE", f"{perc:.1f}%")
        c3.metric("STATUS", "PASSED" if perc >= 33 else "FAILED")

        # Class Teacher Remarks Section
        st.markdown(f"""
            <div style="background:#f0f7f4; padding:20px; border-radius:10px; border-left:5px solid #1b4332; margin-top:20px;">
                <b style="color:#1b4332;">CLASS TEACHER'S REMARKS:</b><br>
                <p style="margin-top:10px; font-style:italic; color:#444;">"{ct_remark}"</p>
            </div>
        """, unsafe_allow_html=True)
    
    conn.close()

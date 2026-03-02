import streamlit as st
import sqlite3
import pandas as pd
import base64
from datetime import date

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

def render_apply_leave(u):
    # Classy Header Design
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%); 
                    padding: 20px; border-radius: 12px; border-left: 10px solid #d4af37; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 25px;'>
            <h2 style='color: white; margin: 0; font-family: sans-serif; letter-spacing: 1px;'>📥 LEAVE APPLICATIONS</h2>
            <p style='color: #d4af37; margin: 5px 0 0 0; font-size: 0.9em;'>Submit your official leave requests here</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("leave_form"):
        c1, c2 = st.columns(2)
        start = c1.date_input("From", date.today())
        end = c2.date_input("To", date.today())
        reason = st.text_area("Reason for Leave")
        if st.form_submit_button("Submit Official Request"):
            with sqlite3.connect("db.sqlite3") as conn:
                conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)", 
                             (u['id'], u['full_name'], u['class'], u['sec'], u['wing'], reason, str(start), str(end), 'Pending'))
            st.success("Your request has been sent to the administration.")

def render_my_result(u):
    conn = sqlite3.connect('db.sqlite3')
    logo_b64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    st.markdown("""
        <style>
        .exam-card {
            background: white; border-radius: 18px; padding: 25px;
            border: 1px solid #f0f0f0; border-top: 6px solid #1b4332;
            margin-bottom: 20px; transition: all 0.4s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .exam-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.12);
            border-top: 6px solid #d4af37;
        }
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 9999;
            display: flex; justify-content: center; align-items: flex-start;
            overflow-y: auto; padding: 40px 15px;
        }
        .modal-content {
            background: white; padding: 45px; border-radius: 8px;
            width: 100%; max-width: 850px; position: relative; color: black;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        /* Classy X Button */
        .stButton > button[kind="primary"] {
            position: fixed !important; top: 70px !important; right: 310px !important;
            z-index: 10000 !important; border-radius: 50% !important;
            width: 45px !important; height: 45px !important; border: none !important;
            background: #cc0000 !important; color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    q_exams = "SELECT DISTINCT e.id, e.name, e.end_date, e.class_group FROM exams e JOIN student_marks sm ON e.id = sm.exam_id WHERE sm.student_id = ? AND sm.subject_id = 0"
    exams_df = pd.read_sql_query(q_exams, conn, params=(u['id'],))

    if exams_df.empty:
        st.info("No published academic results found at this time.")
        conn.close()
        return

    # --- CLASSY FILTER SECTION ---
    st.markdown("<h3 style='color: #1b4332;'>🔍 Academic Records</h3>", unsafe_allow_html=True)
    f_col1, f_col2 = st.columns([3, 1])
    search = f_col1.text_input("", placeholder="Type exam name to search...")
    sort_order = f_col2.selectbox("", ["Latest First", "Oldest First"])
    
    if search:
        exams_df = exams_df[exams_df['name'].str.contains(search, case=False)]
    
    exams_df['end_date'] = pd.to_datetime(exams_df['end_date'])
    # Logic for Oldest/Latest as requested
    exams_df = exams_df.sort_values(by='end_date', ascending=(sort_order == "Oldest First"))

    st.markdown("<br>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (_, ex) in enumerate(exams_df.iterrows()):
        with cols[i % 2]:
            st.markdown(f'''
                <div class="exam-card">
                    <div style="font-size:10px; color:#d4af37; font-weight:700; letter-spacing:2px; margin-bottom:8px;">OFFICIAL REPORT CARD</div>
                    <div style="font-size:22px; font-weight:800; color:#1b4332; margin-bottom:5px;">{ex['name'].upper()}</div>
                    <div style="font-size:14px; color:#888;">Exam Date: {ex['end_date'].strftime('%B %d, %Y')}</div>
                    <div style="margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px;">
                        <span style="color:#1b4332; font-weight:600; font-size:13px;">Status: Published</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            if st.button(f"VIEW REPORT DETAILS", key=f"btn_{ex['id']}", use_container_width=True):
                st.session_state['active_report'] = ex['id']
                st.rerun()

    if 'active_report' in st.session_state:
        # Invisible background closer
        if st.button(" ", key="overlay_close"):
            del st.session_state['active_report']
            st.rerun()

        # The X button
        if st.button("✖", type="primary"):
            del st.session_state['active_report']
            st.rerun()

        rid = st.session_state['active_report']
        r_info = exams_df[exams_df['id']==rid].iloc[0]

        q_marks = """SELECT s.name as Subject, sm.total_marks as Total, sm.obtained_marks as Obtained, sm.remarks as Remarks
                    FROM student_marks sm JOIN apsokara_subject s ON sm.subject_id = s.id
                    WHERE sm.id IN (SELECT MAX(id) FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id > 0 GROUP BY subject_id)"""
        marks = pd.read_sql_query(q_marks, conn, params=(int(rid), u['id']))
        ct_remark = conn.execute("SELECT remarks FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id=0", (int(rid), u['id'])).fetchone()

        rows = ""
        t_obt, t_max = 0, 0
        for _, r in marks.iterrows():
            t_obt += r['Obtained']; t_max += r['Total']
            rows += f'<tr><td style="border:1px solid #000;padding:12px;">{r["Subject"]}</td><td style="border:1px solid #000;padding:12px;text-align:center;">{int(r["Total"])}</td><td style="border:1px solid #000;padding:12px;text-align:center;">{int(r["Obtained"])}</td><td style="border:1px solid #000;padding:12px;">{r["Remarks"]}</td></tr>'
        
        perc = (t_obt/t_max*100) if t_max > 0 else 0
        
        st.markdown(f'''
        <div class="modal-overlay">
            <div class="modal-content">
                <div style="text-align:center; border-bottom:4px solid #1b4332; padding-bottom:15px; margin-bottom:25px;">
                    <img src="data:image/png;base64,{logo_b64}" width="120">
                    <h1 style="margin:10px 0; color:#1b4332; font-size:26px; font-weight:900;">ARMY PUBLIC SCHOOL OKARA CANTONMENT</h1>
                    <p style="margin:0; font-weight:bold; letter-spacing:1px; color:#555;">{r_info['name']} - PROGRESS REPORT</p>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; margin-bottom:25px; font-size:15px; border:1px solid #000; padding:20px;">
                    <div><b>Student Name:</b> {u['full_name']}<br><b>Father Name:</b> {u.get('father_name','-')}<br><b>Roll Number:</b> {u.get('roll_number','-')}</div>
                    <div><b>Class:</b> {u['class']}-{u.get('sec','')}<br><b>Wing:</b> {u.get('wing','-').upper()}<br><b>Issue Date:</b> {date.today()}</div>
                </div>
                <table style="width:100%; border-collapse:collapse; margin-bottom:25px; font-size:14px;">
                    <tr style="background:#f2f2f2;">
                        <th style="border:1px solid #000;padding:12px;text-align:left;">SUBJECT</th>
                        <th style="border:1px solid #000;padding:12px;">MAX MARKS</th>
                        <th style="border:1px solid #000;padding:12px;">OBTAINED</th>
                        <th style="border:1px solid #000;padding:12px;">REMARKS</th>
                    </tr>
                    {rows}
                </table>
                <div style="border:1px solid #000; padding:20px; background:#fafafa;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:18px; margin-bottom:15px; color:#1b4332;">
                        <span>AGGREGATE: {int(t_obt)} / {int(t_max)}</span>
                        <span>PERCENTAGE: {perc:.1f}%</span>
                    </div>
                    <b>CLASS TEACHER'S REMARKS:</b>
                    <p style="margin-top:8px; font-style:italic; color:#333;">"{ct_remark[0] if ct_remark else 'Keep working hard to achieve your goals.'}"</p>
                </div>
                <p style="font-size:11px; text-align:center; color:#777; margin-top:30px; border-top:1px dashed #ccc; padding-top:15px;">
                    Note: This is an electronically generated document. For verification, contact school admin.
                </p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    conn.close()

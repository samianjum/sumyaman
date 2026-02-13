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
    st.markdown("<div style='background:#1b4332; padding:15px; border-radius:10px; border-left:8px solid #d4af37; margin-bottom:20px;'><h3 style='color:white; margin:0;'>📥 LEAVE APPLICATIONS</h3></div>", unsafe_allow_html=True)
    with st.form("leave_form"):
        c1, c2 = st.columns(2)
        start = c1.date_input("From", date.today())
        end = c2.date_input("To", date.today())
        reason = st.text_area("Reason")
        if st.form_submit_button("Submit Request"):
            with sqlite3.connect("db.sqlite3") as conn:
                conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)", 
                             (u['id'], u['full_name'], u['class'], u['sec'], u['wing'], reason, str(start), str(end), 'Pending'))
            st.success("Sent!")

def render_my_result(u):
    conn = sqlite3.connect('db.sqlite3')
    logo_b64 = get_base64_image("/home/sami/Downloads/sami.png")
    
    # --- ADVANCED CSS FOR ROYAL UI ---
    st.markdown("""
        <style>
        .exam-card {
            background: #ffffff;
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-top: 5px solid #1b4332;
            margin-bottom: 20px;
            transition: 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .exam-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        }
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 999999;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            overflow-y: auto;
            padding: 30px 10px;
        }
        .modal-content {
            background: white;
            padding: 40px;
            border-radius: 4px;
            width: 100%;
            max-width: 850px;
            position: relative;
            color: black;
        }
        .close-icon {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 30px;
            cursor: pointer;
            color: #888;
            font-weight: bold;
            text-decoration: none;
        }
        .close-icon:hover { color: #cc0000; }
        </style>
    """, unsafe_allow_html=True)

    q_exams = "SELECT DISTINCT e.id, e.name, e.end_date, e.class_group FROM exams e JOIN student_marks sm ON e.id = sm.exam_id WHERE sm.student_id = ? AND sm.subject_id = 0"
    exams_df = pd.read_sql_query(q_exams, conn, params=(u['id'],))

    if exams_df.empty:
        st.info("No published results found.")
        conn.close()
        return

    # --- FILTERS ---
    st.markdown("### 🔍 Filter Results")
    f_col1, f_col2 = st.columns([2, 1])
    search = f_col1.text_input("Search Exam Name...", placeholder="e.g. Mid Term")
    sort_order = f_col2.selectbox("Sort By", ["Latest First", "Oldest First"])
    
    if search:
        exams_df = exams_df[exams_df['name'].str.contains(search, case=False)]
    
    exams_df['end_date'] = pd.to_datetime(exams_df['end_date'])
    exams_df = exams_df.sort_values(by='end_date', ascending=(sort_order == "Oldest First"))

    st.markdown("---")
    
    # --- DISPLAY EXAM CARDS ---
    cols = st.columns(2)
    for i, (_, ex) in enumerate(exams_df.iterrows()):
        with cols[i % 2]:
            st.markdown(f'''
                <div class="exam-card">
                    <div style="font-size:11px; color:#d4af37; font-weight:900; letter-spacing:1px; margin-bottom:5px;">OFFICIAL RELEASE</div>
                    <div style="font-size:20px; font-weight:800; color:#1b4332; margin-bottom:10px;">{ex['name'].upper()}</div>
                    <div style="font-size:13px; color:#666; margin-bottom:15px;">Session Completion: {ex['end_date'].strftime('%d %b, %Y')}</div>
                </div>
            ''', unsafe_allow_html=True)
            if st.button(f"VIEW REPORT", key=f"btn_{ex['id']}", use_container_width=True):
                st.session_state['active_report'] = ex['id']

    # --- THE MODAL OVERLAY ---
    if 'active_report' in st.session_state:
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
            rows += f'<tr><td style="border:1px solid #000;padding:8px;">{r["Subject"]}</td><td style="border:1px solid #000;padding:8px;text-align:center;">{int(r["Total"])}</td><td style="border:1px solid #000;padding:8px;text-align:center;">{int(r["Obtained"])}</td><td style="border:1px solid #000;padding:8px;">{r["Remarks"]}</td></tr>'
        
        perc = (t_obt/t_max*100) if t_max > 0 else 0
        
        report_html = f'''
        <div class="modal-overlay">
            <div class="modal-content">
                <div style="text-align:center; border-bottom:4px solid #1b4332; padding-bottom:15px; margin-bottom:25px;">
                    <img src="data:image/png;base64,{logo_b64}" width="110">
                    <h1 style="margin:10px 0; color:#1b4332; font-size:28px; font-weight:900;">ARMY PUBLIC SCHOOL OKARA CANTONMENT</h1>
                    <p style="margin:0; font-weight:bold; letter-spacing:1px; text-transform:uppercase;">{r_info['name']} - ACADEMIC PROGRESS REPORT</p>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; margin-bottom:25px; font-size:15px; border:1px solid #000; padding:20px;">
                    <div><b>Student Name:</b> {u['full_name']}<br><b>Father Name:</b> {u.get('father_name','-')}<br><b>Roll Number:</b> {u.get('roll_number','-')}</div>
                    <div><b>Class:</b> {u['class']}-{u.get('sec','')}<br><b>Wing:</b> {u.get('wing','-').upper()}<br><b>Issue Date:</b> {date.today()}</div>
                </div>
                <table style="width:100%; border-collapse:collapse; margin-bottom:25px; font-size:14px; color:black;">
                    <tr style="background:#f2f2f2;">
                        <th style="border:1px solid #000;padding:10px;text-align:left;">SUBJECT</th><th style="border:1px solid #000;padding:10px;">TOTAL</th><th style="border:1px solid #000;padding:10px;">OBTAINED</th><th style="border:1px solid #000;padding:10px;">REMARKS</th>
                    </tr>
                    {rows}
                </table>
                <div style="border:1px solid #000; padding:15px; margin-bottom:30px;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:16px; margin-bottom:10px;">
                        <span>AGGREGATE: {int(t_obt)} / {int(t_max)}</span>
                        <span>PERCENTAGE: {perc:.1f}%</span>
                    </div>
                    <b>CLASS TEACHER'S REMARKS:</b><br>
                    <p style="margin-top:5px; font-style:italic;">"{ct_remark[0] if ct_remark else '-'}"</p>
                </div>
                <p style="font-size:10px; text-align:center; color:#555; border-top:1px dashed #ccc; padding-top:20px;">
                    This is a computer-generated report. It is official and does not require a physical signature or stamp.
                </p>
            </div>
        </div>
        '''
        st.markdown(report_html, unsafe_allow_html=True)
        
        # This acts as the close button outside the HTML but functionally works
        if st.button("✖ CLOSE REPORT", use_container_width=True, type="primary"):
            del st.session_state['active_report']
            st.rerun()

    conn.close()

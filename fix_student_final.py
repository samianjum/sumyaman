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

file_path = 'apsokara/logic/student_modules.py'
logo_b64 = get_base64_image("/home/sami/Downloads/sami.png")

new_code = f"""
import streamlit as st
import sqlite3
import pandas as pd
import base64
from datetime import date

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
    
    # Custom CSS for Overlay/Modal and Banners
    st.markdown(\"\"\"
        <style>
        .exam-banner {{
            background: linear-gradient(90deg, #1b4332 0%, #2d6a4f 100%);
            padding: 25px;
            border-radius: 12px;
            border-right: 8px solid #d4af37;
            color: white;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            overflow-y: auto;
            padding: 20px;
        }}
        .modal-content {{
            background: white;
            padding: 40px;
            border-radius: 5px;
            width: 100%;
            max-width: 850px;
            position: relative;
            color: black;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            .modal-overlay {{ position: relative; background: white; }}
        }}
        </style>
    \"\"\", unsafe_allow_html=True)

    q_exams = \"\"\"SELECT DISTINCT e.id, e.name, e.end_date FROM exams e 
                 JOIN student_marks sm ON e.id = sm.exam_id 
                 WHERE sm.student_id = ? AND sm.subject_id = 0\"\"\"
    exams_df = pd.read_sql_query(q_exams, conn, params=(u['id'],))

    if exams_df.empty:
        st.info("No published results available.")
        return

    st.markdown("### 📊 ACADEMIC RECORD DASHBOARD")
    
    for _, ex in exams_df.iterrows():
        # Banner UI
        st.markdown(f'''
            <div class="exam-banner">
                <div>
                    <div style="font-size:10px; color:#d4af37; font-weight:bold; letter-spacing:1px;">RESULT PUBLISHED</div>
                    <div style="font-size:22px; font-weight:800; text-transform:uppercase;">{ex['name']}</div>
                    <div style="font-size:12px; opacity:0.8;">Dated: {ex['end_date']}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"OPEN REPORT CARD", key=f"v_{ex['id']}", use_container_width=True):
            st.session_state['active_report'] = ex['id']

    # Result Card Logic (The Overlay)
    if 'active_report' in st.session_state:
        ex_id = st.session_state['active_report']
        ex_name = exams_df[exams_df['id']==ex_id]['name'].values[0]

        q_marks = \"\"\"SELECT s.name as Subject, sm.total_marks as Total, sm.obtained_marks as Obtained, sm.remarks as Remarks
                    FROM student_marks sm JOIN apsokara_subject s ON sm.subject_id = s.id
                    WHERE sm.id IN (SELECT MAX(id) FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id > 0 GROUP BY subject_id)\"\"\"
        marks = pd.read_sql_query(q_marks, conn, params=(ex_id, u['id']))
        ct_remark = conn.execute("SELECT remarks FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id=0", (ex_id, u['id'])).fetchone()

        # Build Report HTML
        rows = ""
        t_obt, t_max = 0, 0
        for _, r in marks.iterrows():
            t_obt += r['Obtained']; t_max += r['Total']
            rows += f'<tr><td style="border:1px solid #000;padding:8px;">{{r["Subject"]}}</td><td style="border:1px solid #000;padding:8px;text-align:center;">{{int(r["Total"])}}</td><td style="border:1px solid #000;padding:8px;text-align:center;">{{int(r["Obtained"])}}</td><td style="border:1px solid #000;padding:8px;">{{r["Remarks"]}}</td></tr>'
        
        perc = (t_obt/t_max*100) if t_max > 0 else 0
        
        report_html = f'''
        <div class="modal-overlay">
            <div class="modal-content">
                <div style="text-align:center; border-bottom:3px solid #1b4332; padding-bottom:10px; margin-bottom:20px;">
                    <img src="data:image/png;base64,{logo_b64}" width="100">
                    <h1 style="margin:5px 0; color:#1b4332; font-size:26px;">ARMY PUBLIC SCHOOL OKARA CANTONMENT</h1>
                    <p style="margin:0; font-weight:bold; text-transform:uppercase;">{ex_name} - SESSION 2025-26</p>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; margin-bottom:20px; font-size:14px; border:1px solid #ddd; padding:15px; border-radius:5px;">
                    <div><b>Name:</b> {u['full_name']}<br><b>Father Name:</b> {u.get('father_name','-')}<br><b>Roll No:</b> {u.get('roll_number','-')}</div>
                    <div><b>Class:</b> {u['class']}-{u.get('sec','')}<br><b>Wing:</b> {u.get('wing','-').upper()}<br><b>Date:</b> {date.today()}</div>
                </div>
                <table style="width:100%; border-collapse:collapse; margin-bottom:20px; font-size:14px;">
                    <tr style="background:#f2f2f2;">
                        <th style="border:1px solid #000;padding:8px;">Subject</th><th style="border:1px solid #000;padding:8px;">Total</th><th style="border:1px solid #000;padding:8px;">Obtained</th><th style="border:1px solid #000;padding:8px;">Teacher Remarks</th>
                    </tr>
                    {rows}
                </table>
                <div style="border:1px solid #000; padding:10px; margin-bottom:20px;">
                    <b>Summary:</b> Obtained {int(t_obt)} out of {int(t_max)} ({perc:.1f}%) <br>
                    <b>Class Teacher's Remark:</b> <i>{ct_remark[0] if ct_remark else '-'}</i>
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:40px; font-weight:bold;">
                    <div style="border-top:1px solid #000; width:150px; text-align:center;">Class Teacher</div>
                    <div style="border-top:1px solid #000; width:150px; text-align:center;">Principal / Stamp</div>
                </div>
            </div>
        </div>
        '''
        st.markdown(report_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("❌ CLOSE AND GO BACK", use_container_width=True):
            del st.session_state['active_report']
            st.rerun()

    conn.close()
"""

with open(file_path, 'w') as f:
    f.write(new_code)

import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import pytz
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('db.sqlite3', timeout=60)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    try:
        yield conn
    finally:
        conn.close()

def render_attendance_system(u):
    pk_tz = pytz.timezone("Asia/Karachi")
    today_obj = datetime.datetime.now(pk_tz).date()
    today = today_obj.isoformat()
    teacher_name = u.get('name', 'Teacher')
    c_name = u.get('class', None)
    u_wing = u.get('wing', None)
    u_sec = u.get('section', u.get('sec', ''))

    if not c_name or not u_wing:
        st.error("❌ No Class/Wing assigned to this teacher profile.")
        return

    st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap'); * { font-family: 'Plus Jakarta Sans', sans-serif; }</style>""", unsafe_allow_html=True)
    st.markdown(f'''<div style="background: linear-gradient(-45deg, #f0f9ff, #e0f2fe, #dbeafe, #f8fafc); padding: 30px; border-radius: 28px; border: 1px solid rgba(59, 130, 246, 0.3); display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;"><div><h1 style="margin:0; background: linear-gradient(90deg, #1e3a8a, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{u_wing} Administration</h1><p style="color: #475569; font-weight: 600;">✨ {teacher_name} | Section {c_name}-{u_sec}</p></div><div style="background: white; padding: 10px 20px; border-radius: 15px; border: 1px solid #bfdbfe; text-align: center;"><span style="color: #3b82f6; font-size: 10px; letter-spacing: 2px; display: block;">TIMELINE</span><b style="color: #1e40af; font-size: 18px;">{today_obj.strftime('%d %B, %Y')}</b></div></div>''', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖋️ MARKING", "📅 ARCHIVE", "💎 INTEL"])

    with get_db() as conn:
        with tab1:
            lock_res = conn.execute("SELECT MAX(edit_count) FROM apsokara_attendance WHERE date=? AND student_class=? AND wing=? AND student_section=?", (today, c_name, u_wing, u_sec)).fetchone()
            edit_cnt = lock_res[0] if lock_res[0] is not None else 0

            if edit_cnt >= 2:
                st.markdown(f'''<div style="background: rgba(34, 197, 94, 0.1); border-left: 5px solid #22c55e; padding: 25px; border-radius: 15px; text-align: center; border: 1px solid rgba(34, 197, 94, 0.2);"><div style="font-size: 50px;">🛡️</div><h2 style="color: #15803d; margin: 10px 0;">ATTENDANCE SECURED</h2><p style="color: #166534; font-weight: 500;">Today's record for <b style="color: #059669;">{c_name}-{u_sec}</b> is locked.</p><div style="display: inline-block; background: #22c55e; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold;">FINALIZED</div></div>''', unsafe_allow_html=True)
                st.balloons()
            else:
                if edit_cnt == 0:
                    st.markdown('''<div style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 15px; border-radius: 12px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px;"><span style="font-size: 20px;">💡</span><span style="color: #1e40af; font-weight: 500;"><b>Instruction:</b> Check all students carefully. You can edit this <b>once</b> after syncing.</span></div>''', unsafe_allow_html=True)
                else:
                    st.markdown('''<div style="background: #fff1f2; border: 1px solid #fecdd3; padding: 15px; border-radius: 12px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; animation: pulse 2s infinite;"><span style="font-size: 20px;">⚠️</span><span style="color: #9f1239; font-weight: 600;"><b>CRITICAL:</b> This is your <b>LAST CHANCE</b>. Database will LOCK after this sync.</span></div><style>@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }</style>''', unsafe_allow_html=True)

                students = pd.read_sql("SELECT id, roll_no, full_name, session_year FROM apsokara_student WHERE student_class=? AND wing=? AND student_section=? AND is_active=1 ORDER BY CAST(roll_no AS INTEGER)", conn, params=(c_name, u_wing, u_sec))
                
                if students.empty:
                    st.warning(f"No students in {c_name}-{u_sec}")
                else:
                    attendance_results = {}
                    for _, s in students.iterrows():
                        st.markdown(f"**{s['full_name']}** (Roll: {s['roll_no']})")
                        attendance_results[s['id']] = {
                            'status': st.segmented_control("Status", ["Present", "Absent", "Leave"], default="Present", key=f"s_{s['id']}", label_visibility="collapsed"),
                            'year': s['session_year']
                        }
                    
                    st.markdown("---")
                    if st.toggle("Verify All Entries", key="verify_toggle"):
                        btn_label = "🚀 FINAL LOCK & SYNC" if edit_cnt == 1 else "🚀 SYNC TO DATABASE"
                        if st.button(btn_label, use_container_width=True, type="primary"):
                            with st.status("Writing to Secure Storage...", expanded=False) as status:
                                try:
                                    cur = conn.cursor()
                                    cur.execute("BEGIN IMMEDIATE TRANSACTION;")
                                    cur.execute("DELETE FROM apsokara_attendance WHERE date=? AND student_class=? AND wing=? AND student_section=?", (today, c_name, u_wing, u_sec))
                                    final_data = [(today, sid, edit_cnt+1, c_name, u_sec, u_wing, d['year'], d['status'], teacher_name) for sid, d in attendance_results.items()]
                                    cur.executemany("INSERT INTO apsokara_attendance (date, student_id, edit_count, student_class, student_section, wing, session_year, status, marked_by) VALUES (?,?,?,?,?,?,?,?,?)", final_data)
                                    conn.commit()
                                    status.update(label="Sync Complete!", state="complete")
                                    st.success("✅ Attendance Successfully Synced.")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"Critical Error: {e}")

        with tab2:
            v_date = st.date_input("Select Date", today_obj)
            hist = pd.read_sql("SELECT s.roll_no, s.full_name, IFNULL(a.status, 'Not Marked') as status FROM apsokara_student s LEFT JOIN apsokara_attendance a ON s.id = a.student_id AND a.date=? WHERE s.student_class=? AND s.wing=? AND s.student_section=? ORDER BY CAST(s.roll_no AS INTEGER)", conn, params=(v_date.isoformat(), c_name, u_wing, u_sec))
            st.dataframe(hist, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown("""<style>
                .main-card { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-radius: 25px; padding: 25px; border: 1px solid #e2e8f0; }
                .stat-hero { background: white; border-radius: 20px; padding: 20px; text-align: center; border-bottom: 5px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
                .stat-hero h1 { font-size: 45px; margin: 0; color: #1e3a8a; }
                .stat-hero p { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; margin: 0; }
                .glass-list { background: rgba(255,255,255,0.6); backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); padding: 15px; }
            </style>""", unsafe_allow_html=True)

            st.markdown("<h2 style='color: #1e3a8a; font-weight: 800;'>💎 Student Intelligence Center</h2>", unsafe_allow_html=True)
            s_query = st.text_input("🔍 Search Student Name", placeholder="Type name and press Enter...", label_visibility="collapsed")

            if s_query:
                s_data = pd.read_sql("SELECT id, roll_no, full_name, father_name FROM apsokara_student WHERE (full_name LIKE ? OR father_name LIKE ?) AND student_class=? AND wing=? AND student_section=?", conn, params=(f"%{s_query}%", f"%{s_query}%", c_name, u_wing, u_sec))
                if not s_data.empty:
                    sel = s_data.iloc[0]; sid = int(sel["id"])
                    stats_df = pd.read_sql("SELECT date, status FROM apsokara_attendance WHERE student_id=? ORDER BY date DESC", conn, params=(sid,))
                    t_days, t_pres = len(stats_df), len(stats_df[stats_df["status"] == "Present"])
                    t_abs, t_leave = len(stats_df[stats_df["status"] == "Absent"]), len(stats_df[stats_df["status"] == "Leave"])
                    perc = (t_pres / t_days * 100) if t_days > 0 else 0

                    # --- Row 1: Hero Analytics ---
                    st.markdown(f"### 📊 Academic Overview: {sel['full_name']}")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.markdown(f'<div class="stat-hero" style="border-color: #3b82f6;"><p>Sessions</p><h1>{t_days}</h1></div>', unsafe_allow_html=True)
                    with c2: st.markdown(f'<div class="stat-hero" style="border-color: #22c55e;"><p>Present</p><h1>{t_pres}</h1></div>', unsafe_allow_html=True)
                    with c3: st.markdown(f'<div class="stat-hero" style="border-color: #ef4444;"><p>Absent</p><h1>{t_abs}</h1></div>', unsafe_allow_html=True)
                    with c4: st.markdown(f'<div class="stat-hero" style="border-color: #f59e0b;"><p>Leave</p><h1>{t_leave}</h1></div>', unsafe_allow_html=True)

                    # --- Row 2: The "Intesting" Gauge Chart ---
                    st.markdown("---")
                    g1, g2 = st.columns([1.5, 1])
                    with g1:
                        st.markdown("#### ⚡ Attendance Reliability Score")
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = perc,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Current Integrity", 'font': {'size': 16}},
                            gauge = {
                                'axis': {'range': [None, 100], 'tickwidth': 1},
                                'bar': {'color': "#1e3a8a"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "#e2e8f0",
                                'steps': [
                                    {'range': [0, 50], 'color': "#fee2e2"},
                                    {'range': [50, 80], 'color': "#fef9c3"},
                                    {'range': [80, 100], 'color': "#dcfce7"}],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 75}}))
                        fig.update_layout(height=300, margin=dict(t=30, b=0, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)

                    with g2:
                        st.markdown("#### 🎯 Quick Status Search")
                        target_date = st.date_input("Pick a date to verify", today_obj, key="final_intel_date")
                        match = stats_df[stats_df["date"] == target_date.isoformat()]
                        if not match.empty:
                            s_val = match.iloc[0]["status"]
                            color = "#22c55e" if s_val=="Present" else "#ef4444" if s_val=="Absent" else "#f59e0b"
                            st.markdown(f'''<div style="background: {color}; color: white; padding: 45px 20px; border-radius: 25px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-top:10px;">
                                <h2 style="margin:0;">{s_val}</h2><p style="opacity: 0.8; margin:0;">Record for {target_date}</p></div>''', unsafe_allow_html=True)
                        else:
                            st.info("No record found for this date.")

                    # --- Row 3: History & Export ---
                    st.markdown("---")
                    st.markdown("#### 📜 Full Detailed Log")
                    st.dataframe(stats_df, use_container_width=True, height=250)
                    
                    def make_pdf():
                        b = io.BytesIO(); c = canvas.Canvas(b, pagesize=letter)
                        c.drawString(100, 750, f"INTEL REPORT: {sel['full_name']}"); y=700
                        for _, r in stats_df.iterrows(): c.drawString(100, y, f"{r['date']}: {r['status']}"); y-=20
                        c.save(); return b.getvalue()
                    st.download_button("📥 Download Official PDF History", make_pdf(), f"{sel['full_name']}_Intel.pdf", "application/pdf", use_container_width=True)
                else: st.error("No student found in your assigned section.")

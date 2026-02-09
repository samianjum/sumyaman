from leave_utils import check_on_leave
import sys, os; sys.path.append(os.getcwd()); sys.path.append(os.path.join(os.getcwd(), "apsokara/logic"))
from apsokara.logic.teacher_modules import render_marks_entry
from apsokara.logic.student_modules import render_my_result
from apsokara.logic.class_teacher_modules import render_final_upload
from apsokara.logic.teacher_modules import render_marks_entry
from apsokara.logic.student_modules import render_my_result
from news_utility import render_news_ticker
import streamlit as st
from news_utility import render_news_ticker
import base64
import datetime
import base64
import sqlite3
import pandas as pd
import plotly.graph_objects as go # Donut chart ke liye
from mobile_portal import render_mobile_view

# 1. Page Config
st.set_page_config(page_title="APS OKARA PORTAL", page_icon="/home/sami/Downloads/sami.png", layout="wide", initial_sidebar_state="expanded")


st.markdown("""
    <link rel='manifest' href='./static/app_assets/manifest_v3.json'>
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('./static/app_assets/sw.js');
""", unsafe_allow_html=True)




    if ('serviceWorker' in navigator) {

    
    
render_news_ticker()

# --- LEAVE SYSTEM HELPER FUNCTIONS ---
def check_on_leave(student_id):
    try:
        import sqlite3
        import datetime
        conn = sqlite3.connect('db.sqlite3')
        today = datetime.date.today().isoformat()
        cur = conn.cursor()
        # Naye table 'apsokara_studentleave' se check karna
        query = "SELECT id FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN from_date AND to_date"
        cur.execute(query, (student_id, today))
        res = cur.fetchone()
        conn.close()
        return True if res else False
    except Exception as e:
        return False

def get_pending_count(u):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM apsokara_leaverequests WHERE student_class=? AND student_section=? AND wing=? AND status='Pending'", (u.get('class'), u.get('sec'), u.get('wing')))
        count = cur.fetchone()[0]
        conn.close()
    except: return ""

# --- PROFESSIONAL NOTIFICATION SYSTEM (INJECTED) ---
def display_notifications():
    try:
        conn = sqlite3.connect("db.sqlite3", timeout=30)
        cur = conn.cursor()
        cur.execute("SELECT title, content, date_posted FROM apsokara_schoolnotice WHERE is_active=1 ORDER BY date_posted DESC LIMIT 8")
        notices = cur.fetchall()
        conn.close()
        count = len(notices)
        notices_html = ""
        for n in notices:
            notices_html += f"""
            <div style="padding:12px; border-bottom:1px solid #f0f0f0; transition: background 0.3s;">
            </div>
            """
        if not notices:
            notices_html = "<div style='padding:30px; text-align:center; color:#999;'>No new notifications</div>"

        st.markdown(f"""
        <div class="notif-wrapper" tabindex="0">
            <div class="notif-window">
                <div class="notif-header">🔔 Recent Notifications</div>
            </div>
            <div class="notif-bell">
                <span>🔔</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except: pass

def display_ticker():
    try:
        conn = sqlite3.connect("db.sqlite3", timeout=30)
        cur = conn.cursor()
        cur.execute("SELECT title, content, scheme FROM apsokara_schoolnotice WHERE is_active=1 ORDER BY date_posted DESC LIMIT 5")
        notices = cur.fetchall()
        conn.close()
        if notices:
            st.markdown(f"""
            <div class="ticker-wrapper">
                <div class="live-label">Live Updates</div>
                <div class="ticker-scroll-container">
                </div>
            </div>
            """, unsafe_allow_html=True)
    except: pass

display_ticker()
display_notifications()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def get_base64(file_path):
    try:
        with open(file_path, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return ""

LOGO_PATH = '/home/sami/Downloads/sami.png'
img_base64 = get_base64(LOGO_PATH)

def get_history_df(student_id):
    conn = sqlite3.connect('db.sqlite3')
    q = "SELECT date, status FROM apsokara_attendance WHERE student_id=? AND session_year = (SELECT session_year FROM apsokara_student WHERE id=?) GROUP BY date ORDER BY date DESC"
    df = pd.read_sql_query(q, conn, params=(u['id'], u['id']))
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['Day'] = df['date'].dt.strftime('%A')
        df['Date'] = df['date'].dt.strftime('%d-%m-%Y')
        return df[['Date', 'Day', 'Status']]
    return pd.DataFrame()

def get_student_overall_stats(student_id):
    conn = sqlite3.connect('db.sqlite3')
    # Count only unique dates for this student
    q = "SELECT status, COUNT(*) as count FROM apsokara_attendance WHERE student_id=? AND session_year = (SELECT session_year FROM apsokara_student WHERE id=?) GROUP BY status"
    df = pd.read_sql_query(q, conn, params=(u['id'], u['id']))
    conn.close()
    for _, row in df.iterrows():
        stats[row['status']] = row['count']
    stats['Total'] = sum([stats['P'], stats['A'], stats['L']])
    return stats

def check_attendance_state(t_class, t_sec, t_wing):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    cursor.execute("""SELECT MAX(edit_count) FROM apsokara_attendance 
                      WHERE student_class=? AND student_section=? AND date=? 
                      AND student_id IN (SELECT cnic FROM apsokara_student WHERE wing=?)""", 
                   (t_class, t_sec, today, t_wing))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res[0] is not None else 0

def save_attendance(attendance_data, t_class, t_sec, is_edit=False):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()
    new_count = 2 if is_edit else 1
    try:
        for s_id, status in attendance_data.items():
            cursor.execute("DELETE FROM apsokara_attendance WHERE student_id=? AND session_year = (SELECT session_year FROM apsokara_student WHERE id=?) AND date=?", (s_id, today))
            cursor.execute('''INSERT INTO apsokara_attendance 
                            (student_id, date, status, class, student_section, edit_count) 
                            VALUES (?, ?, ?, ?, ?, ?)''', (s_id, today, status, t_class, t_sec, new_count))
        conn.commit()
        return True
    except: return False
    finally: conn.close()




def fetch_user_data(user_id, dob_val, user_type):
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        if user_type == "Teacher":
            q = "SELECT *, assigned_wing as wing, assigned_class as class, assigned_section as sec FROM apsokara_teacher WHERE cnic = ? AND dob = ?"
        else:
            q = "SELECT *, student_class as class, student_section as sec FROM apsokara_student WHERE b_form = ? AND dob = ?"
        
        cursor.execute(q, (user_id, dob_val))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Module compatibility fix
            if 'id' in data:
                data['id_num'] = data['id']
            # Yahan asali jaadu hai:
            if user_type == "Teacher" and row['is_class_teacher'] == 1:
                data['role_db'] = "Class Teacher"
            else:
                data['role_db'] = user_type
            return data
        return None
    except Exception as e:
        return None
    finally:
        conn.close()




def get_daily_analytics(t_class, t_sec, t_wing):
    conn = sqlite3.connect('db.sqlite3')
    today = datetime.date.today().isoformat()
    q_total = "SELECT COUNT(*) FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?"
    total = pd.read_sql_query(q_total, conn, params=(t_class, t_sec, t_wing)).iloc[0,0]
    q_stats = """SELECT status, COUNT(*) as count FROM apsokara_attendance 
                 WHERE student_class=? AND student_section=? AND date=?
                 AND student_id IN (SELECT cnic FROM apsokara_student WHERE wing=?)
                 GROUP BY status"""
    df_stats = pd.read_sql_query(q_stats, conn, params=(t_class, t_sec, today, t_wing))
    conn.close()
    for _, row in df_stats.iterrows():
        key = "Present" if row['status'] == 'P' else ("Absent" if row['status'] == 'A' else "Leave")
        stats[key] = row['count']
    return stats

# --- CUSTOM CSS ---
role = st.session_state.role
if True: primary, secondary, accent, btn_color = "#1b4332", "#f0fdf4", "#0c0d0e", "#d4af37" # APS Student
elif False: pass # APS Class Teacher
elif False: pass # APS Subject Teacher
else: primary, secondary, accent, btn_color = "#1b4332", "#F4F7F6", "#333333", "#2196F3"

st.markdown(f'''
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

def show_dashboard():
    role = st.session_state.role
    u = st.session_state.user_info
    if role == "Student":
        tag, tag_col = "🎓 STUDENT PORTAL", "#1b4332"
    elif role == "Class Teacher":
        tag, tag_col = "👨‍🏫 CLASS INCHARGE", "#1b4332"
    else:
        tag, tag_col = "📖 SUBJECT TEACHER", "#1b4332"

    st.markdown(f'''
    <div class="hero-card">
        <div class="hero-info">
            <div class="details-row">
            </div>
        </div>
    </div>

    if role == "Student": tabs_list = ["🏠 HOME", "📅 DAILY DIARY", "📜 ATTENDANCE HISTORY", "📝 APPLY LEAVE", "🏆 MY RESULT", "🔒 FACE LOCK"]
    else: tabs_list = ["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY", "📝 ATTENDANCE", "🔒 FACE LOCK"]
    
    active_tabs = st.tabs(tabs_list)
    for i, tab in enumerate(active_tabs):
        with tab:
            t_full_name = tabs_list[i].upper()
            if 'FACE LOCK' in t_full_name:
                st.stop()
                st.stop()  # Is ke baad ka saara kachra tab mein nahi dikhega
            if "MY RESULT" in t_full_name or "RESULT" in t_full_name:
                from apsokara.logic.student_modules import render_my_result
                render_my_result(u)
            elif "ATTENDANCE HISTORY" in t_full_name:
                from attendance_logic import render_student_attendance
                render_student_attendance(u)
            elif "MARKS ENTRY" in t_full_name:
                from apsokara.logic.teacher_modules import render_marks_entry
                render_marks_entry(u)
            elif "FINAL UPLOAD" in t_full_name:
                from apsokara.logic.class_teacher_modules import render_final_upload
                render_final_upload(u)
            elif "ATTENDANCE SYSTEM" in t_full_name or "ATTENDANCE" in t_full_name:
                from attendance_system import render_attendance_system
                render_attendance_system(u)
            elif "LEAVE" in t_full_name:
                from apsokara.logic.student_modules import render_apply_leave
                render_apply_leave(u)
            elif "FACE LOCK" in t_full_name:
                c1, c2, c3 = st.columns(3)
                with c1: st.info("📅 Today: " + str(datetime.date.today()))
                with c2: st.success("✅ System Status: Active")
                with c3: st.warning("🔔 New Notices: Check Notifications")
                st.divider()
                st.image("https://img.freepik.com/free-vector/education-background-with-books-lamp_23-2147501981.jpg", width='stretch')
def show_login():
    t1, t2= st.tabs(["🎓 STUDENT LOGIN", "👨‍🏫 STAFF LOGIN"])
    with t1:
        id_s = st.text_input("B-Form Number", key="s_login")
        if st.session_state.get('bio_toggle'):
            st.camera_input('FaceID', key='login_cam', label_visibility='hidden')
            st.markdown('</div>', unsafe_allow_html=True)
        if st.session_state.get('bio_toggle'):
            st.camera_input('Scan to Authenticate', key='login_cam')
        dob_s = st.date_input("Birth Date", value=datetime.date(2010,1,1), key="s_dob")
        if st.button("ENTER STUDENT PORTAL", key="s_btn"):
            d = fetch_user_data(id_s, str(dob_s), "Student")
            if d:
                import sqlite3; _c=sqlite3.connect('db.sqlite3', timeout=10); _r=_c.execute('SELECT face_status FROM apsokara_student WHERE id=?', (d['id'],)).fetchone(); _c.close(); st.session_state.needs_face_auth = True if (_r and str(_r[0]).strip().upper()=='ENROLLED') else False; st.session_state.user_info, st.session_state.role, st.session_state.logged_in = d, 'Student', True; st.toast('Syncing Secure Data...', icon='🔄');
                st.rerun()
    with t2:
        id_t = st.text_input("CNIC Number", key="t_login")
        dob_t = st.date_input("Birth Date ", value=datetime.date(1990,1,1), key="t_dob")
        if st.button("ENTER STAFF PORTAL", key="t_btn"):
            d = fetch_user_data(id_t, str(dob_t), "Teacher")
            if d:
                import sqlite3; _c=sqlite3.connect('db.sqlite3', timeout=10); _r=_c.execute('SELECT face_status FROM apsokara_teacher WHERE id=?', (d['id'],)).fetchone(); _c.close(); st.session_state.needs_face_auth = True if (_r and str(_r[0]).strip().upper()=='ENROLLED') else False; st.session_state.user_info, st.session_state.role, st.session_state.logged_in = d, d.get('role_db', 'Teacher'), True; st.toast('Syncing Staff Vault...', icon='🔄');
                st.rerun()


# --- MOBILE & SECURITY GUARD ---
import streamlit_javascript as st_js

width = st_js.st_javascript("window.innerWidth")

if st.session_state.get('logged_in'):
    # A. Mobile View Check
    if width is not None and width < 700:
        render_mobile_view()
        st.stop()
    
    # B. Face ID Check

    # --- SECURE BIOMETRIC GATE ---
    if st.session_state.get('needs_face_auth'):
        st.stop()

    # --- AI BIOMETRIC LOCK ---
    if st.session_state.get('needs_face_auth'):
        st.stop()

    # --- AI BIOMETRIC GATEWAY ---
    if st.session_state.get('needs_face_auth'):
        st.stop()

# --- FINAL ROUTING ---
if not st.session_state.get('logged_in'):
    show_login()
else:
    show_dashboard()


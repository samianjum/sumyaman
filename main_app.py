import face_security
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

# 1. Page Config
st.set_page_config(page_title="ARMY PUBLIC SCHOOL & COLLAGE SYSTEM Portal", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #1b4332 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Global Button and Tab Overrides */
    .stButton>button { border: 2px solid #d4af37 !important; transition: 0.3s !important; }
    .stButton>button:hover { background-color: #ffffff !important; color: #1b4332 !important; border: 2px solid #1b4332 !important; }
    
    /* Header and Text Gold touches */
    h1, h2, h3 { color: #1b4332 !important; }
    .stTabs [aria-selected="true"] { border-top: 5px solid #d4af37 !important; }
</style>
''', unsafe_allow_html=True)
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
        return f" ({count})" if count > 0 else ""
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
        badge_val = f"{count}" if count <= 9 else "9+"
        notices_html = ""
        for n in notices:
            notices_html += f"""
            <div style="padding:12px; border-bottom:1px solid #f0f0f0; transition: background 0.3s;">
                <div style="font-weight:700; color:#1b4332; font-size:14px; margin-bottom:3px;">{n[0]}</div>
                <div style="color:#444; font-size:13px; line-height:1.4;">{n[1]}</div>
                <div style="color:#999; font-size:10px; margin-top:5px; text-align:right;">{n[2]}</div>
            </div>
            """
        if not notices:
            notices_html = "<div style='padding:30px; text-align:center; color:#999;'>No new notifications</div>"

        st.markdown(f"""
        <style>
            .notif-wrapper {{ position: fixed; bottom: 30px; right: 30px; z-index: 999999; }}
            .notif-bell {{ background: #FF0000; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 2px solid white; font-size: 28px; position: relative; }}
            .notif-badge {{ position: absolute; top: -5px; right: -5px; background: #1b4332; color: white; border-radius: 50%; width: 26px; height: 26px; font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
            .notif-window {{ position: absolute; bottom: 80px; right: 0; width: 330px; max-height: 450px; background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); display: none; flex-direction: column; overflow: hidden; border: 1px solid #ddd; animation: popUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
            @keyframes popUp {{ from {{ transform: scale(0.8) translateY(20px); opacity: 0; }} to {{ transform: scale(1) translateY(0); opacity: 1; }} }}
            .notif-wrapper:focus-within .notif-window {{ display: flex; }}
            .notif-header {{ background: #1b4332; color: white; padding: 15px; font-weight: 800; font-size: 16px; border-bottom: 2px solid #FFD700; }}
            .notif-content {{ overflow-y: auto; background: #fff; }}
        </style>
        <div class="notif-wrapper" tabindex="0">
            <div class="notif-window">
                <div class="notif-header">🔔 Recent Notifications</div>
                <div class="notif-content">{notices_html}</div>
            </div>
            <div class="notif-bell">
                <span>🔔</span>
                <div class="notif-badge">{badge_val}</div>
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
            items = "".join([f"<span style='background:{n[2]};padding:2px 8px;border-radius:4px;font-size:11px;margin-right:8px;color:white;font-weight:bold;'>NEWS</span><b style='color:#FFD700;font-size:16px;'> {n[0]}: </b><span style='color:white;font-size:15px;'>{n[1]}</span> &nbsp;&nbsp;&nbsp; ⚡ &nbsp;&nbsp;&nbsp; " for n in notices])
            st.markdown(f"""
            <style>
                .ticker-wrapper {{ display: flex; background: #1b4332; border-radius: 10px; overflow: hidden; border: 1px solid #333; height: 50px; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); position: relative; margin-bottom: 20px; }}
                .live-label {{ background: #ff0000; color: white; padding: 0 25px; height: 100%; display: flex; align-items: center; font-weight: 900; font-size: 14px; z-index: 10; box-shadow: 10px 0 20px rgba(0,0,0,0.5); text-transform: uppercase; }}
                .ticker-scroll-container {{ flex-grow: 1; overflow: hidden; white-space: nowrap; position: relative; display: flex; align-items: center; mask-image: linear-gradient(to right, transparent, black 5%, black 95%, transparent); }}
                .ticker-text {{ display: inline-block; padding-left: 100%; animation: tv-marquee 40s linear infinite; color: white; }}
                @keyframes tv-marquee {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}
                .live-label::after {{ content: ""; width: 10px; height: 10px; background: white; border-radius: 50%; margin-left: 10px; animation: pulse-dot 1s infinite; }}
                @keyframes pulse-dot {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.2; }} 100% {{ opacity: 1; }} }}
            </style>
            <div class="ticker-wrapper">
                <div class="live-label">Live Updates</div>
                <div class="ticker-scroll-container">
                    <div class="ticker-text">{items} {items}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except: pass

display_ticker()
display_notifications()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_info = {}

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
        df.refull_name(columns={'status': 'Status'}, inplace=True)
        return df[['Date', 'Day', 'Status']]
    return pd.DataFrame()

def get_student_overall_stats(student_id):
    conn = sqlite3.connect('db.sqlite3')
    # Count only unique dates for this student
    q = "SELECT status, COUNT(*) as count FROM apsokara_attendance WHERE student_id=? AND session_year = (SELECT session_year FROM apsokara_student WHERE id=?) GROUP BY status"
    df = pd.read_sql_query(q, conn, params=(u['id'], u['id']))
    conn.close()
    stats = {"P": 0, "A": 0, "L": 0, "Total": 0}
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
        st.error(f"Database Error: {e}")
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
    stats = {"Present": 0, "Absent": 0, "Leave": 0, "Total": 0}
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
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    * {{ font-family: 'Poppins', sans-serif; color: {accent}; }}
    .stApp {{ background-color: {secondary}; }}
    .hero-card {{ background: #F0F0F0; border-radius: 25px; padding: 30px 40px; margin-bottom: 30px; display: flex !important; flex-direction: row !important; align-items: center !important; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 2px solid {primary}; position: relative; }}
    .hero-logo-container {{ flex: 0 0 130px !important; height: 130px !important; background: white; border-radius: 20px; display: flex !important; align-items: center !important; justify-content: center !important; margin-right: 35px !important; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
    .hero-logo-container img {{ width: 90px !important; }}
    .welcome-text {{ font-size: 34px !important; font-weight: 800 !important; margin: 0 0 15px 0 !important; color: {primary}; line-height: 1.1; }}
    .details-row {{ display: flex !important; flex-wrap: wrap !important; gap: 12px !important; margin-top: 5px !important; }}
    .detail-item {{ background: white; padding: 8px 16px; border-radius: 12px; border: 1px solid {primary}33; }}
    .detail-item b {{ display: block; font-size: 10px; text-transform: uppercase; margin-bottom: 2px; color: {primary}; opacity: 0.8; }}
    .detail-item span {{ font-size: 14px !important; font-weight: 600 !important; color: {accent}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 15px !important; justify-content: center !important; display: flex !important; width: 100% !important; background-color: transparent !important; margin: 20px 0 30px 0 !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; background-color: {secondary}; border-radius: 12px; padding: 10px 25px; font-weight: 600; border: 1px solid {primary}33; transition: all 0.3s; }}
    .stTabs [aria-selected="true"] {{ background-color: {primary} !important; color: white !important; border-bottom: none !important; }}
    .stButton>button {{ background-color: {btn_color} !important; color: {"#000000" if role == "Subject Teacher" else "white"} !important; font-weight: 800 !important; border-radius: 12px !important; border: none !important; padding: 15px 30px !important; text-transform: uppercase !important; width: 100%; }}
    .stat-card {{ background: white; padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #ddd; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .stat-val {{ font-size: 28px; font-weight: 800; color: {primary}; }}
    .stat-lbl {{ font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; }}
</style>
''', unsafe_allow_html=True)

def show_dashboard():
    role = st.session_state.role
    u = st.session_state.user_info
    if role == "Student":
        tag, tag_col = "🎓 STUDENT PORTAL", "#1b4332"
        extra = f'''<div class="detail-item"><b>👨‍👦 Father</b><span>{u.get("father_name")}</span></div><div class="detail-item"><b>🆔 CNIC</b><span>{u.get("cnic")}</span></div><div class="detail-item"><b>📅 DOB</b><span>{u.get("dob")}</span></div><div class="detail-item"><b>☪️ Religion</b><span>{u.get("religion")}</span></div><div class="detail-item"><b>📞 Contact</b><span>{u.get("contact")}</span></div><div class="detail-item"><b>🏠 Address</b><span>{u.get("address")}</span></div><div class="detail-item"><b>🏫 Assigned</b><span>{u.get("class")}-{u.get("sec")} ({u.get("wing")})</span></div>'''
    elif role == "Class Teacher":
        tag, tag_col = "👨‍🏫 CLASS INCHARGE", "#1b4332"
        extra = f'''<div class="detail-item"><b>👨‍👦 Father</b><span>{u.get("father_name")}</span></div><div class="detail-item"><b>🆔 CNIC</b><span>{u.get("cnic")}</span></div><div class="detail-item"><b>📅 DOB</b><span>{u.get("dob")}</span></div><div class="detail-item"><b>☪️ Religion</b><span>{u.get("religion")}</span></div><div class="detail-item"><b>📞 Contact</b><span>{u.get("contact")}</span></div><div class="detail-item"><b>🏠 Address</b><span>{u.get("address")}</span></div><div class="detail-item"><b>🏫 Assigned</b><span>{u.get("class")}-{u.get("sec")} ({u.get("wing")})</span></div>'''
    else:
        tag, tag_col = "📖 SUBJECT TEACHER", "#1b4332"
        extra = f'''<div class="detail-item"><b>👨‍👦 Father</b><span>{u.get("father_name")}</span></div><div class="detail-item"><b>🆔 CNIC</b><span>{u.get("cnic")}</span></div><div class="detail-item"><b>📅 DOB</b><span>{u.get("dob")}</span></div><div class="detail-item"><b>☪️ Religion</b><span>{u.get("religion")}</span></div><div class="detail-item"><b>📞 Contact</b><span>{u.get("contact")}</span></div><div class="detail-item"><b>🏠 Address</b><span>{u.get("address")}</span></div><div class="detail-item"><b>🏫 Assigned</b><span>{u.get("class")}-{u.get("sec")} ({u.get("wing")})</span></div>'''

    st.markdown(f'''
    <div class="hero-card">
        <div style="position: absolute; top: 15px; right: 15px; z-index: 1000;"><a href="/" target="_self" style="text-decoration: none;"><button style="background: {primary}; border: none; color: white; padding: 10px 18px; border-radius: 12px; cursor: pointer; font-size: 13px; font-weight: 700;">🚪 LOGOUT</button></a></div>
        <div class="hero-logo-container"><img src="data:image/png;base64,{img_base64}"></div>
        <div class="hero-info">
            <div style="font-size:11px; font-weight:800; letter-spacing:2px; color:{tag_col}; margin-bottom:5px;">{tag}</div>
            <div class="welcome-text">Welcome Back, {u.get('full_name', u.get('full_name', 'User'))}! ✨</div>
            <div class="details-row">
                <div class="detail-item"><b>👤 Full Name</b><span>{u.get('full_name', u.get('full_name', 'User'))}</span></div>
                <div class="detail-item"><b>🏢 Wing</b><span>{u.get('wing')} Wing</span></div>
                {extra}
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    if role == "Student": tabs_list = ["🏠 HOME", "📅 DAILY DIARY", "📜 ATTENDANCE HISTORY", "📝 APPLY LEAVE", "🏆 MY RESULT", "🔒 FACE LOCK"]
    elif role == "Class Teacher": tabs_list = ["🏠 DASHBOARD", "📓 POST DIARY", "📝 ATTENDANCE SYSTEM", f"📥 LEAVE APPROVALS{get_pending_count(u)}", "🔒 FACE LOCK"]
    else: tabs_list = ["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY", "📝 ATTENDANCE", "🔒 FACE LOCK"]
    
    active_tabs = st.tabs(tabs_list)
    for i, tab in enumerate(active_tabs):
        with tab:
            t_full_name = tabs_list[i].upper()
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
                import face_security
                face_security.render_face_lock_setup(u)
                st.markdown(f"## 🏛️ Welcome, {st.session_state.user_info.get('full_name', st.session_state.user_info.get('full_name', 'User'))}!")
                c1, c2, c3 = st.columns(3)
                with c1: st.info("📅 Today: " + str(datetime.date.today()))
                with c2: st.success("✅ System Status: Active")
                with c3: st.warning("🔔 New Notices: Check Notifications")
                st.divider()
                st.image("https://img.freepik.com/free-vector/education-background-with-books-lamp_23-2147501981.jpg", width='stretch')
                st.write(f'## Welcome, {st.session_state.user_info.get('full_name', st.session_state.user_info.get('full_name', 'User'))}!')
def show_login():
    st.markdown(f'''<div style="text-align:center; padding-top:0px;"><img src="data:image/png;base64,{img_base64}" width="100"><h1 style="color:#000000; font-weight:800;">ARMY PUBLIC SCHOOL & COLLAGE SYSTEM PORTAL</h1></div>''', unsafe_allow_html=True)
    t1, t2= st.tabs(["🎓 STUDENT LOGIN", "👨‍🏫 STAFF LOGIN"])
    with t1:
        id_s = st.text_input("B-Form Number", key="s_login")
        dob_s = st.date_input("Birth Date", value=datetime.date(2010,1,1), key="s_dob")
        if st.button("ENTER STUDENT PORTAL", key="s_btn"):
            d = fetch_user_data(id_s, str(dob_s), "Student")
            if d:
                st.session_state.user_info, st.session_state.role, st.session_state.logged_in = d, "Student", True
                st.rerun()
    with t2:
        id_t = st.text_input("CNIC Number", key="t_login")
        dob_t = st.date_input("Birth Date ", value=datetime.date(1990,1,1), key="t_dob")
        if st.button("ENTER STAFF PORTAL", key="t_btn"):
            d = fetch_user_data(id_t, str(dob_t), "Teacher")
            if d:
                st.session_state.user_info, st.session_state.role, st.session_state.logged_in = d, d['role_db'], True
                st.rerun()

# --- MOBILE DETECTION ---
import streamlit_javascript as st_js
from mobile_portal import render_mobile_view
width = st_js.st_javascript("window.innerWidth")
if width is not None and width < 700:
    if st.session_state.logged_in:
        render_mobile_view()
        st.stop()
# ------------------------
if not st.session_state.logged_in: show_login()
else: show_dashboard()


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
st.markdown('''
<style>
    /* Global Font Clarity */
    html, body, [class*="st-"] {
        color: #0c0d0e !important; /* Super Dark Font */
        font-weight: 500;
    }
    
    /* Headers ko mazeed prominent karna */
    h1, h2, h3, h4 { 
        color: #1b4332 !important; 
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    /* Tabs ko Light aur Sophisticated banana */
    .stTabs [data-baseweb="tab"] {
        background-color: #f0fdf4 !important; /* Very Light Mint */
        color: #1b4332 !important;
        border: 1px solid #d1fae5 !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 10px 20px !important;
        margin-right: 5px !important;
    }
    
    /* Selected Tab highlight */
    .stTabs [aria-selected="true"] {
        background-color: #1b4332 !important;
        color: #d4af37 !important; /* Gold text on Green background */
        border-bottom: 3px solid #d4af37 !important;
    }

    /* Hero Cards (Bande ki info wala box) */
    .hero-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px rgba(27, 67, 50, 0.1) !important;
    }

    /* Sidebar text clarity */
    section[data-testid="stSidebar"] .stText, section[data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
</style>
''', unsafe_allow_html=True)

st.markdown('''
<style>
    /* Dark Fonts Everywhere */
    * { color: #0c0d0e; }
    
    /* Sidebar Fix */
    [data-testid="stSidebar"] { background-color: #1b4332 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* Tabs Styling - Light & Modern */
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc !important;
        color: #1b4332 !important;
        border: 1px solid #e2e8f0 !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1b4332 !important;
        color: #d4af37 !important;
        border-bottom: 4px solid #d4af37 !important;
    }
    
    /* Buttons - Gold & Bold */
    .stButton>button {
        background-color: #d4af37 !important;
        color: #1b4332 !important;
        font-weight: 900 !important;
        border: 2px solid #1b4332 !important;
        box-shadow: 0 4px 0 #b08d28 !important;
    }
    .stButton>button:active { transform: translateY(2px); box-shadow: none !important; }

    /* Stat Cards */
    .stat-card { background: #ffffff !important; border: 2px solid #1b4332 !important; }
    .stat-val { color: #1b4332 !important; }
</style>
''', unsafe_allow_html=True)

# UNIVERSAL THEME FORCE

st.markdown('''
<style>
    /* 1. Force background and text globally */
    .stApp { background-color: #f0fdf4 !important; }
    * { font-family: 'Poppins', sans-serif; color: #0c0d0e !important; }

    /* 2. Force all Buttons in all modules */
    div.stButton > button {
        background-color: #d4af37 !important;
        color: #1b4332 !important;
        border: 2px solid #1b4332 !important;
        font-weight: 800 !important;
        border-radius: 8px !important;
        text-transform: uppercase !important;
    }

    /* 3. Force all DataFrames/Tables and Inputs */
    .stDataFrame, [data-testid="stTable"] { border: 1px solid #1b4332 !important; }
    input, textarea, select { border: 1px solid #1b4332 !important; border-radius: 5px !important; }

    /* 4. Force specific tags that might be used in modules */
    h1, h2, h3, h4, b, strong { color: #1b4332 !important; }
    
    /* 5. Highlight Green for Success/Info boxes inside modules */
    .stAlert { background-color: #f0fdf4 !important; border: 1px solid #1b4332 !important; color: #1b4332 !important; }

    /* 6. Tabs Clarity Fix */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab"] {
        color: #1b4332 !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1b4332 !important;
        color: #d4af37 !important;
    }
</style>
''', unsafe_allow_html=True)

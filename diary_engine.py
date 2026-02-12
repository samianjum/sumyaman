import sqlite3
import pandas as pd
import streamlit as st
from datetime import date, datetime
import os

def get_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def draw_aps_banner(title, subtitle):
    st.markdown(f'''
        <div style="background: linear-gradient(90deg, #1b4332 0%, #081c15 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px; border-bottom: 5px solid #d4af37; text-align: center;">
            <h1 style="color: #d4af37; margin: 0; font-size: 26px;">{title}</h1>
            <p style="color: white; margin: 5px 0 0 0; opacity: 0.8; font-size: 14px;">{subtitle}</p>
        </div>
    ''', unsafe_allow_html=True)

@st.dialog("📋 DIARY ATTACHMENT")
def show_attachment(file_path):
    st.markdown("### Reference Material")
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(file_path, use_container_width=True)
    else:
        st.success("📄 Document file is ready.")
    with open(file_path, "rb") as f:
        st.download_button("📥 Download File", f, file_name=os.path.basename(file_path), use_container_width=True, type="primary")



def render_teacher_diary(u):
    teacher_id, teacher_name = u.get('id'), u.get('full_name')
    draw_aps_banner("🏛️ TEACHER PORTAL", f"Instructor: {teacher_name} | APS OKARA")
    conn = get_db()
    
    query = "SELECT a.student_class, a.section, a.wing, a.subject_id, s.name as sub_name FROM apsokara_subjectassignment a LEFT JOIN apsokara_subject s ON a.subject_id = s.id WHERE a.teacher_id = ?"
    assignments = [dict(row) for row in conn.execute(query, (teacher_id,)).fetchall()]
    
    if not assignments:
        st.warning("⚠️ No classes assigned.")
        return

    tab1, tab2 = st.tabs(["📝 PUBLISH", "📂 MANAGE HISTORY"])
    
    with tab1:
        options = [f"{a['sub_name']} | Class {a['student_class']}-{a['section']} ({a['wing']} Wing)" for a in assignments]
        selected_idx = st.selectbox("🎯 Target", range(len(options)), format_func=lambda x: options[x])
        target = assignments[selected_idx]
        
        with st.container(border=True):
            content = st.text_area("✍️ Homework Details", height=150)
            uploaded_file = st.file_uploader("📎 Attachment", type=['png', 'jpg', 'jpeg', 'pdf'])
            is_sch = st.toggle("⏰ Schedule?")
            post_date = st.date_input("📅 Date", date.today()) if is_sch else date.today()
            lock = st.checkbox("🔒 Confirm Content")
            
            
            
            if st.button("🚀 PUBLISH", type="primary", use_container_width=True, disabled=not lock):
                if content.strip():
                    file_p = None
                    if uploaded_file:
                        if not os.path.exists('uploads'): os.makedirs('uploads')
                        file_p = f"uploads/{datetime.now().timestamp()}_{uploaded_file.name}"
                        with open(file_p, "wb") as f: f.write(uploaded_file.getbuffer())
                    
                    # Capture exact Date and Time
                    now = datetime.now()
                    time_str = now.strftime("%I:%M %p")
                    full_timestamp = f"{post_date} | {time_str}"
                    
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO apsokara_dailydiary 
                                 (teacher_id, teacher_name, class, section, subject, content, date_posted, attachment_url, is_scheduled, wing) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                 (teacher_id, teacher_name, str(target['student_class']), str(target['section']), 
                                  str(target['sub_name']), content, full_timestamp, file_p, is_sch, target['wing']))
                    conn.commit()
                    
                    
                    # --- BROADCAST NOTIFICATION (Fixed Columns) ---
                    
                    try:
                        from notification_system import add_notification
                        import sqlite3
                        t_conn = sqlite3.connect("db.sqlite3")
                        cur_notif = t_conn.cursor()
                        cur_notif.execute("SELECT roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?", (str(target["student_class"]), str(target["section"]), str(target["wing"])))
                        for s in cur_notif.fetchall(): add_notification(user_id=str(s[0]), title=f"New Diary: {target['sub_name']}", message=f"Teacher {teacher_name} posted a new task.", category=f"diary_id_{cur.lastrowid}")
                        t_conn.close()
                    except Exception as e: print(f"Notif Error: {e}")

                    except Exception as e:
                        print(f"Notification Error: {e}")
                    # -----------------------------------------------
                    st.success(f"✅ Published at {time_str}!")
    
    
    

    with tab2:
        df_h = pd.read_sql("SELECT * FROM apsokara_dailydiary WHERE teacher_id=? ORDER BY id DESC", conn, params=(teacher_id,))
        if not df_h.empty:
            for _, row in df_h.iterrows():
                with st.container(border=True):
                    main_col, side_col = st.columns([5, 1.8])
                    with main_col:
                        # Extracting date and time parts for better styling
                        raw_date = str(row['date_posted'])
                        date_part = raw_date.split(" | ")[0] if " | " in raw_date else raw_date
                        time_part = raw_date.split(" | ")[1] if " | " in raw_date else "--:--"
                        
                        st.markdown(f'''
                            <div style="margin-bottom: 10px;">
                                <div style="font-size: 24px; font-weight: 800; color: #1b4332; line-height: 1.2;">📘 {row['subject']}</div>
                                <div style="font-size: 14px; color: #d4af37; font-weight: bold; margin-top: 5px;">
                                    📅 {date_part} <span style="color: #666; margin-left:10px;">🕒 {time_part}</span>
                                </div>
                            </div>
                            <div style="color: #111; font-size: 18px; line-height: 1.6; background: #fdfdfd; padding: 5px; border-radius: 4px;">{row['content']}</div>
                            <div style="font-size: 13px; color: #777; margin-top: 15px; padding-top: 8px; border-top: 1px dashed #ccc; display: flex; gap: 20px;">
                                <span><b>📍 CLASS:</b> {row['class']}-{row['section']}</span>
                                <span><b>🏛️ WING:</b> {row.get('wing','N/A')}</span>
                            </div>
                        ''', unsafe_allow_html=True)
                    with side_col:
                        if row['attachment_url'] and os.path.exists(row['attachment_url']):
                            st.write(" ")
                            if st.button("🖼️ VIEW FILE", key=f"th_tm_fin_{row['id']}", use_container_width=True):
                                show_attachment(row['attachment_url'])
                    
                st.markdown(f'''
                    <script>
                        var target = window.parent.document.getElementById("diary_{row['id']}");
                        if (target) {{
                            target.scrollIntoView({{ behavior: "smooth", block: "center" }});
                        }}
                    </script>
                ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                        
                        
                    
        else:
            st.info("No history found.")

    conn.close()





def render_student_diary(u):
    s_class, s_sec, s_wing = str(u.get('student_class')), str(u.get('student_section')), u.get('wing', 'General')
    conn = get_db()
    today = date.today()
    
    # Fetch all visible diaries (Today and Past)
    df = pd.read_sql("SELECT * FROM apsokara_dailydiary WHERE class=? AND section=? AND wing=? AND SUBSTR(date_posted, 1, 10) <= ? ORDER BY id DESC", 
                     conn, params=(s_class, s_sec, s_wing, today.isoformat()))
    conn.close()

    # --- INFORMATIVE SMART BANNER ---
    total_today = len(df[df['date_posted'] == today.isoformat()])
    st.markdown(f'''
        <div style="background: #1b4332; padding: 20px; border-radius: 12px; border-left: 8px solid #d4af37; margin-bottom: 20px; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin:0; color: #d4af37;">📅 STUDENT DIARY PORTAL</h2>
                    <p style="margin:0; opacity: 0.8;">{s_wing} Wing | Class {s_class}-{s_sec}</p>
                </div>
                <div style="text-align: right; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px;">
                    <span style="font-size: 24px; font-weight: bold; color: #d4af37;">{total_today}</span><br>
                    <span style="font-size: 10px; text-transform: uppercase;">Tasks for Today</span>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    if not df.empty:
        # --- HEAVY FILTERS SECTION ---
        with st.container(border=True):
            st.markdown("🔍 **HEAVY SEARCH ENGINE**")
            c1, c2, c3 = st.columns([1.5, 1, 1])
            with c1:
                search = st.text_input("⌨️ Search Content", placeholder="Topic, keyword, teacher name...")
            with c2:
                sub_filter = st.selectbox("📚 Subject", ["All Subjects"] + sorted(df['subject'].unique().tolist()))
            with c3:
                date_filter = st.date_input("📆 Filter by Date", None)

        # Multi-Layer Filter Logic
        f_df = df.copy()
        if search:
            f_df = f_df[f_df['content'].str.contains(search, case=False) | f_df['subject'].str.contains(search, case=False) | f_df['teacher_name'].str.contains(search, case=False)]
        if sub_filter != "All Subjects":
            f_df = f_df[f_df['subject'] == sub_filter]
        if date_filter:
            f_df = f_df[f_df['date_posted'] == date_filter.isoformat()]

        st.markdown(f"**Showing {len(f_df)} results**")

        for _, row in f_df.iterrows():
            is_focus = str(st.session_state.get('focus_diary')) == str(row['id'])
            if 'is_focus' in locals() and is_focus:
                st.markdown('<div style="border:2px solid #d4af37; border-radius:10px; padding:5px; background:#fff9e6;">', unsafe_allow_html=True)
            is_focus = str(st.session_state.get('focus_diary')) == str(row['id'])
            if 'is_focus' in locals() and is_focus:
                st.markdown('<div style="border:2px solid #d4af37; border-radius:10px; padding:5px; background:#fff9e6;">', unsafe_allow_html=True)
            # Navigation Highlight Logic
            is_focus = str(st.session_state.get('focus_diary')) == str(row['id'])
            if 'is_focus' in locals() and is_focus:
                st.markdown('<div style="background:#fff9e6; border:2px solid #d4af37; border-radius:10px; padding:2px; margin-bottom:10px;">', unsafe_allow_html=True)
            
            with st.container(border=True):
                main_col, side_col = st.columns([5, 1.5])
                with main_col:
                    st.markdown(f"**📘 {row['subject']}** | <small style='color:#d4af37;'>{row['date_posted']}</small>", unsafe_allow_html=True)
                    st.write(row['content'])
                    st.markdown(f"<div style='font-size:11px; color:gray;'>Instructor: {row['teacher_name']}</div>", unsafe_allow_html=True)
                with side_col:
                    if row['attachment_url'] and os.path.exists(row['attachment_url']):
                        st.write("") # Spacer
                        if st.button("🖼️ VIEW FILE", key=f"sv_{row['id']}", use_container_width=True):
                            show_attachment(row['attachment_url'])
                    
            if 'is_focus' in locals() and is_focus:
                st.markdown(f'''
                    <script>
                        var target = window.parent.document.getElementById("diary_{row['id']}");
                        if (target) {{
                            target.scrollIntoView({{ behavior: "smooth", block: "center" }});
                        }}
                    </script>
                ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                        
                        
                    
    else:
        st.info("No active diary entries found for your class.")


import sqlite3
import streamlit as st
import streamlit.components.v1 as components

def get_db_connection():
    return sqlite3.connect('school_database.db', check_same_thread=False)

def add_notification(user_id, title, message, category='general'):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO notifications (user_id, title, message, category, is_read) VALUES (?, ?, ?, ?, 0)",
                  (user_id, title, message, category))
        conn.commit()
        conn.close()
        return True
    except: return False

def render_notification_ui():
    u = st.session_state.get('user_info', {})
    role = st.session_state.get('role')
    
    # AGAR USER TEACHER HAI TO YAHAN SE WAPAS CHALE JAO (Bell mat dikhao)
    if str(role).lower() != 'student':
        return

    u = st.session_state.get('user_info', {})
    user_id = str(u.get('roll_number', u.get('username', u.get('id', ''))))
    if not user_id: return

    # Click handling logic
    params = st.query_params
    if "click_notif" in params:
        try:
            conn = get_db_connection()
            conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            st.query_params.clear()
            st.session_state['active_tab'] = "📔 Daily Diary"
            st.rerun()
        except: pass

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read=0", (str(user_id),))
    count = c.fetchone()[0]
    c.execute("SELECT title, message, id FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
    rows = c.fetchall()
    conn.close()

    # Sanitized HTML generation using triple quotes to avoid syntax errors
    notif_items = ""
    if rows:
        for r in rows:
            notif_items += f"""
            <div style='padding:10px; border-bottom:1px solid #eee; cursor:pointer;' 
                 onclick='window.parent.location.search="?click_notif={r[2]}"'>
                <b style='color:#1b4332; font-size:13px;'>{r[0]}</b><br>
                <small style='color:#666;'>{r[1]}</small>
            </div>
            """
    else:
        notif_items = "<div style='padding:15px; color:gray; text-align:center;'>No new notifications.</div>"

    badge = f"<div style='position:absolute; top:-5px; right:-5px; background:red; color:white; border-radius:50%; width:20px; height:20px; font-size:11px; display:flex; align-items:center; justify-content:center; border:2px solid white; font-family:sans-serif;'>{count}</div>" if count > 0 else ""

    html_code = f"""
        <div style="position:fixed; bottom:10px; right:10px; font-family:sans-serif;">
            <div id="box" style="display:none; width:260px; background:white; border:1px solid #1b4332; border-radius:10px; margin-bottom:10px; box-shadow:0 5px 15px rgba(0,0,0,0.3); overflow:hidden;">
                <div style="background:#1b4332; color:#d4af37; padding:10px; font-weight:bold; font-size:14px;">Notifications</div>
                <div style="max-height:220px; overflow-y:auto; background:white;">{notif_items}</div>
            </div>
            <div onclick="var b=document.getElementById('box'); b.style.display=(b.style.display=='none'?'block':'none')" 
                 style="width:55px; height:55px; background:#d4af37; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; position:relative; border:2px solid #1b4332; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <span style="font-size:24px;">🔔</span> {badge}
            </div>
        </div>
    """
    components.html(html_code, height=350)

    st.markdown("<style>iframe[title='streamlit.components.v1.html'] {position:fixed !important; bottom:0 !important; right:0 !important; z-index:999999 !important; border:none !important;}</style>", unsafe_allow_html=True)

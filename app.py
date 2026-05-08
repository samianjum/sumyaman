from flask import Flask, render_template_string, request, jsonify, session
import sqlite3, datetime, pytz
from functools import wraps

app = Flask(__name__)
app.secret_key = "aps_okara_ultimate_final_v3"

# --- CONFIG ---

from flask import session
def get_db_path():
    # Agar user login hai aur uska school ID session mein hai
    if 'school_id' in session:
        return f"databases/{session['school_id']}.sqlite3"
    return 'db.sqlite3' # Default fallback

PK_TZ = pytz.timezone("Asia/Karachi")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return '<script>window.location.href="/";</script>'
        return f(*args, **kwargs)
    return decorated_function

# --- DIARY BACKEND ROUTES ---

# --- UI TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>APS OKARA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0f172a; margin: 0; display: flex; justify-content: center; min-height: 100vh; overflow: hidden; }
        .app-shell { width: 100%; max-width: 450px; height: 100vh; background: #ffffff; display: flex; flex-direction: column; position: relative; overflow: hidden; }
        .app-header { background: #1B4332; color: white; padding: 40px 20px 25px; border-radius: 0 0 30px 30px; flex-shrink: 0; z-index: 20; }
        .app-body { flex: 1; overflow-y: auto; padding: 20px 20px 100px; }
        .app-nav { position: absolute; bottom: 0; width: 100%; height: 75px; background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); display: flex; justify-content: space-around; align-items: center; border-top: 1px solid #f1f5f9; z-index: 100; left: 0; }
        .nav-btn { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; }
        .nav-btn span:last-child { font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
        .active-nav span { color: #1B4332 !important; }
        .glass-card { background: white; border-radius: 20px; padding: 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
        .hidden { display: none !important; }
        .btn-sync { background: #1B4332; color: white; width: 100%; padding: 15px; border-radius: 15px; font-weight: 800; margin-top: 20px; }
        .status-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800; }
    </style>
</head>
<body>
    <div class="app-shell">
        {% if not logged_in %}
        <div class="fixed inset-0 bg-gray-50 flex items-center justify-center p-6 z-[9999]">
            <div class="w-full max-w-[380px] bg-white rounded-[2.5rem] shadow-2xl overflow-hidden border border-gray-100">
                <div class="bg-[#1B4332] pt-12 pb-10 px-6 text-center relative">
                    <div class="w-24 h-24 bg-white rounded-full mx-auto flex items-center justify-center shadow-lg mb-4 border-2 border-[#D4AF37]">
                        <img src="/app_logo" class="w-[75%] h-[75%] object-contain" onerror="this.src='https://img.icons8.com/ios-filled/100/1B4332/school.png'">
                    </div>
                    <h1 class="text-white text-2xl font-black tracking-tight uppercase">APS OKARA</h1>
                </div>
                <div class="p-8">
                    <div class="flex bg-gray-100 p-1 rounded-xl mb-8 border border-gray-200">
                        <button onclick="setRole('Student')" id="sBtn" class="flex-1 py-3 rounded-lg font-black text-[11px] bg-[#D4AF37] text-[#1B4332]">STUDENT</button>
                        <button onclick="setRole('Teacher')" id="tBtn" class="flex-1 py-3 rounded-xl font-black text-[11px] text-gray-400">STAFF</button>
                    </div>
                    <div class="space-y-5">
                        <input type="text" id="uid" placeholder="Enter ID Number" class="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 outline-none font-bold">
                        <input type="date" id="dob" class="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 outline-none font-bold">
                        <button onclick="doLogin()" class="w-full bg-[#1B4332] text-white py-4 rounded-xl font-black uppercase tracking-widest">Sign In</button>
                    </div>
                </div>
            </div>
        </div>
        {% else %}
        <div id="main-header" class="app-header shadow-md p-4 bg-gradient-to-r from-[#1B4332] to-[#2D6A4F]">
            <div class="flex items-center gap-3">
                <div class="w-14 h-14 rounded-full border-2 border-white/30 bg-white flex items-center justify-center overflow-hidden">
                    <img src="/app_logo" class="w-[80%] h-[80%] object-contain">
                </div>
                <div>
                    <h2 class="text-lg font-black leading-tight">{{ user.full_name }}</h2>
                    <span class="text-[8px] font-black bg-black/20 px-2 py-0.5 rounded uppercase text-[#D4AF37]">{{ user.role }}</span>
                </div>
            </div>
        </div>

        <div class="app-body">
            <div id="page-home" class="grid grid-cols-2 gap-4">
                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 border-b-4 border-green-600">
                    <div class="text-4xl mb-3">📋</div>
                    <h4 class="font-black text-[11px] uppercase">Attendance</h4>
                </div>
                {% endif %}

                    <div class="text-4xl mb-3">📒</div>
                    <h4 class="font-black text-[11px] uppercase">Class Diary</h4>
                </div>

                {% if user.role == 'Student' %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 border-b-4 border-blue-600">
                    <div class="text-4xl mb-3">📊</div>
                    <h4 class="font-black text-[11px] uppercase">Reports</h4>
                </div>
                {% endif %}
                <div onclick="showTab('profile')" class="glass-card flex flex-col items-center justify-center p-6 border-b-4 border-purple-600">
                    <div class="text-4xl mb-3">👤</div>
                    <h4 class="font-black text-[11px] uppercase">My Vault</h4>
                </div>
            </div>


            const role = '{{ user.role }}';
            if (role === 'Teacher') showTab('diary-hub');
        }

        // --- TEACHER LOGIC ---

        function showTab(t) {
            document.querySelectorAll('[id^="page-"]').forEach(p => p.classList.add('hidden'));
            const target = document.getElementById('page-' + t);
            if(target) target.classList.remove('hidden');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active-nav'));
            if(document.getElementById('n-' + t)) document.getElementById('n-' + t).classList.add('active-nav');
        }
    </script>
</body>
</html>
"""

@app.route('/app_logo')
def get_app_logo():
    import os
    from flask import send_file
    path = "/home/sami/Downloads/sami.png"
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return "", 404

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, logged_in='user' in session, user=session.get('user'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    uid, dob, role = str(data.get('uid', '')).strip(), str(data.get('dob', '')).strip(), data.get('role', 'Student')
    uid_int = int(uid) if uid.isdigit() else -1
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if role == "Student":
        cur.execute("SELECT * FROM apsokara_student WHERE (b_form=? OR id=? OR roll_number=?) AND dob=?", (uid, uid_int, uid, dob))
    else:
        cur.execute("SELECT * FROM apsokara_teacher WHERE (cnic=? OR id=?) AND dob=?", (uid, uid_int, dob))
    user = cur.fetchone()
    if user:
        u_dict = dict(user)
        u_dict['role'] = role
        u_dict['assigned_class'] = u_dict.get('student_class') or u_dict.get('assigned_class')
        u_dict['assigned_section'] = u_dict.get('student_section') or u_dict.get('assigned_section')
        u_dict['wing'] = u_dict.get('wing') or u_dict.get('assigned_wing')
        if role == "Teacher":
            cur.execute("SELECT s.name as s_name, sa.student_class as c_num, sa.section as s_sec, sa.wing as w_wing FROM apsokara_subjectassignment sa LEFT JOIN apsokara_subject s ON sa.subject_id = s.id WHERE sa.teacher_id = ?", (u_dict['id'],))
            u_dict['assignments'] = [dict(r) for r in cur.fetchall()]
        session['user'] = u_dict
        conn.close()
        return jsonify({"success": True})
    conn.close()
    return jsonify({"success": False})

@app.route('/logout')
def logout():
    session.clear()
    return '<script>window.location.href="/";</script>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

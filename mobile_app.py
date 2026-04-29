from student_result import init_student_routes
from finalize_module import init_finalize_routes
from flask import send_file, send_from_directory, make_response, send_from_directory, Flask, render_template_string, request, jsonify, session
import os, sqlite3, datetime, pytz
from functools import wraps

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "aps_okara_ultimate_final_v3"

# --- CONFIG ---
DB_PATH = 'db.sqlite3'
PK_TZ = pytz.timezone("Asia/Karachi")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'offline_or_logged_out'}), 401
            return '<script>window.location.href="/";</script>'
        return f(*args, **kwargs)
    return decorated_function
from teacher_api import init_teacher_routes
from marks_engine import init_marks_routes
init_finalize_routes(app, DB_PATH)
init_teacher_routes(app, login_required)
init_marks_routes(app, login_required)
init_student_routes(app, DB_PATH)


@app.route('/api/update-profile-pic', methods=['POST'])
@login_required
def update_profile_pic():
    try:
        data = request.json
        action = data.get('action')
        user = session['user']
        table = 'apsokara_student' if user['role'] == 'Student' else 'apsokara_teacher'
        
        conn = sqlite3.connect(DB_PATH)
        if action == 'upload':
            img_data = data.get('image')
            if not img_data: return jsonify({'error': 'No image'}), 400
            
            import base64
            header, encoded = img_data.split(",", 1)
            file_ext = header.split("/")[1].split(";")[0]
            filename = f"pfp_{user['id']}_{int(datetime.datetime.now().timestamp())}.{file_ext}"
            filepath = os.path.join('static/uploads/profile_pics', filename)
            
            with open(filepath, "wb") as fh:
                fh.write(base64.b64decode(encoded))
            
            db_path = f"/static/uploads/profile_pics/{filename}"
            conn.execute(f"UPDATE {table} SET profile_pic = ? WHERE id = ?", (db_path, user['id']))
            session['user']['profile_pic'] = db_path
            session.modified = True
            
        elif action == 'remove':
            conn.execute(f"UPDATE {table} SET profile_pic = NULL WHERE id = ?", (user['id'],))
            session['user']['profile_pic'] = None
            session.modified = True
            
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    user_id = user['id']
    role = user['role']
    
    table = "apsokara_student" if role == "Student" else "apsokara_teacher"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        if action == 'upload':
            img_data = data.get('image')
            cur.execute(f"UPDATE {table} SET address = ? WHERE id = ?", (f"IMG_DATA:{img_data}", user_id))
        elif action == 'remove':
            cur.execute(f"UPDATE {table} SET address = NULL WHERE id = ?", (user_id,))
        
        conn.commit()
        # Update session
        session['user']['profile_pic'] = img_data if action == 'upload' else None
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()


# --- UI TEMPLATE ---
HTML_TEMPLATE = '''
<script>
window.safeLogout = async function(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    
    console.log("Checking connection for logout...");
    
    // Check 1: navigator.onLine
    

        if (!navigator.onLine) {
        if (window.showToast) showToast("❌ OFFLINE: Internet required to logout!", "error");
        else alert("❌ Offline: Internet required.");
        return false;
    }

    // Confirmation using your custom modal
    if (window.askUser) {
        const ok = await askUser("Logout Session? Active internet is required.");
        if (!ok) return false;
    } else if (!confirm("Logout now?")) {
        return false;
    }

    // Check 2: Final Ping right before redirect
    try {
        const ping = await fetch('/app_logo', { method: 'HEAD', cache: 'no-store' });
        if (ping.ok) {
            localStorage.clear();
            window.location.replace('/logout');
        } else {
            throw new Error();
        }
    } catch (err) {
        showToast("❌ SERVER UNREACHABLE: Logout blocked!", "error");
    }
    return false;
};
</script>




    <script>
     else {
                alert("❌ OFFLINE: Internet connection is required to logout.");
            }
            return false; // Stop everything
        }
        
        if (confirm("Are you sure you want to logout?")) {
            localStorage.clear();
            window.location.replace('/logout');
        }
    }

    // Login logic protection
    setTimeout(() => {
        if (window.doLogin && !window.doLogin._guarded) {
            const _oldLogin = window.doLogin;
            window.doLogin = async function() {
                

        if (!navigator.onLine) {
                    if (typeof showToast === 'function') showToast("❌ OFFLINE: Login Disabled", "error");
                    else alert("❌ No Internet Connection");
                    return;
                }
                return await _oldLogin();
            };
            window.doLogin._guarded = true;
        }
    }, 1000);
    </script>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#1B4332">
    <script>
        if ("serviceWorker" in navigator) {
            window.addEventListener("load", () => {
                
            });
        }
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AXIS</title>
    <link rel="icon" type="image/png" href="/app_logo">
    <script src="/static/tailwind.min.css"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: #0f172a; margin: 0; display: flex; justify-content: center; min-height: 100vh; overflow: hidden; }
        .app-shell { width: 100%; max-width: 450px; height: 100vh; background: #ffffff; display: flex; flex-direction: column; position: relative; overflow: hidden; }
        .app-header { 
    background: linear-gradient(180deg, #0B132B 0%, #0F1B3D 100%); 
    padding: 8px 16px; 
    border-bottom: 1px solid rgba(111,255,233,0.12); 
    flex-shrink: 0; 
    z-index: 20; 
    min-height: 140px; 
    display: flex; 
    flex-direction: column; 
    justify-content: space-between;
}
        .app-body { flex: 1; overflow-y: auto; padding: 20px 20px 100px; }
        .app-nav { 
            position: absolute; 
            bottom: 20px; 
            left: 5%;
            width: 90%; 
            height: 70px; 
            background: rgba(11, 19, 43, 0.9); 
            backdrop-filter: blur(15px); 
            display: flex; 
            justify-content: space-around; 
            align-items: center; 
            border: 1px solid rgba(111, 255, 233, 0.15); 
            border-radius: 25px;
            z-index: 100; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .nav-btn { 
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            cursor: pointer; 
            transition: all 0.3s ease;
        }
        .nav-btn svg { 
            width: 22px; 
            height: 22px; 
            stroke: rgba(255,255,255,0.5); 
            transition: all 0.3s ease;
        }
        .nav-btn span:last-child { 
            font-size: 9px; 
            font-weight: 800; 
            color: rgba(255,255,255,0.4); 
            text-transform: uppercase; 
            margin-top: 4px; 
            letter-spacing: 0.05em;
        }
        .active-nav svg { 
            stroke: #6FFFE9 !important; 
            filter: drop-shadow(0 0 8px rgba(111, 255, 233, 0.8)) !important;
            transform: translateY(-3px);
            stroke-width: 3px;
        }
        .active-nav span { 
            color: #6FFFE9 !important; 
        }
        
        /* --- PROFESSIONAL DARK BLUE THEME OVERRIDES --- */
        
        .saas-card { 
            background: #F8FAFC; 
            border-radius: 20px; 
            padding: 20px 10px; 
            border: 1.5px solid #F1F5F9; 
            transition: all 0.2s ease-in-out; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            text-align: center;
            color: #1E3A8A; 
            position: relative;
            overflow: hidden;
        }
        .saas-card:active { 
            transform: scale(0.95); 
            background: #f1f5f9; 
            box-shadow: none;
        }
        .saas-card svg { 
            width: 32px !important; 
            height: 32px !important; 
            margin-bottom: 14px; 
            transition: transform 0.3s ease;
        }
        .group:hover svg { transform: translateY(-3px); }
        
        /* Dynamic Colors for Icons based on parent accent */
        /* .saas-card:nth-child(1) svg color disabled */ #0891b2 !important; } /* Cyan */
        /* .saas-card:nth-child(2) svg color disabled */ #2563eb !important; } /* Blue */
        /* .saas-card:nth-child(3) svg color disabled */ #7c3aed !important; } /* Purple */
        /* .saas-card:nth-child(4) svg color disabled */ #059669 !important; } /* Emerald */
        
        .saas-card h4 { 
            color: #0F172A !important; 
            font-weight: 900; 
            font-size: 12px; 
            letter-spacing: 0.02em; 
            text-transform: uppercase; 
            margin-bottom: 4px;
        }
        .saas-card p { 
            color: #64748b !important; 
            font-size: 9px; 
            font-weight: 600; 
            letter-spacing: 0.01em;
        }
        .saas-accent { 
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            opacity: 0.8;
        }
 /* Rangeen side-bars hide kar diye */
        
        /* Baaki sub-cards (Diary/History) ko bhi unified dark blue border dena */
        #page-home .glass-card { border-left-color: #0B132B !important; }
    
        .glass-card { background: white; border-radius: 20px; padding: 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
        .hidden { display: none !important; }
        .btn-sync { background: #1B4332; color: white; width: 100%; padding: 15px; border-radius: 15px; font-weight: 800; margin-top: 20px; }
        
        .status-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800; }
.shake-anim { animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both; }        @keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); } }
        {% if user.role == 'Student' %}
        .teacher-only { display: none !important; }
        {% endif %}
    
    
        /* Sexy Toast Styles */
        #toast-container { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 100000; width: 90%; max-width: 400px; pointer-events: none; }
        .toast-msg { background: rgba(15, 23, 42, 0.95); color: white; padding: 16px 20px; border-radius: 20px; margin-bottom: 10px; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); display: flex; items-center; justify-content: center; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); animation: toast-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .toast-success { border-bottom: 4px solid #10b981; }
        .toast-error { border-bottom: 4px solid #ef4444; }
        .toast-warning { border-bottom: 4px solid #f59e0b; }
        @keyframes toast-in { from { opacity: 0; transform: translateY(-100%) scale(0.9); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .toast-out { animation: toast-out 0.3s ease forwards !important; }
        @keyframes toast-out { to { opacity: 0; transform: translateY(-20px) scale(0.95); } }

    
        @keyframes zoom-in { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
        .animate-zoom-in { animation: zoom-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .net-status { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .net-online { background: #10b981; box-shadow: 0 0 10px #10b981; }
        .net-offline { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
        .sync-badge { position: absolute; top: -5px; right: 10px; background: #ef4444; color: white; font-size: 8px; padding: 2px 5px; border-radius: 10px; font-weight: 900; }


    
        .axis-input {
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 0 !important;
            color: white !important;
            padding: 12px 0 !important;
            transition: all 0.3s ease;
        }
        .axis-input:focus {
            border-bottom: 1px solid #6FFFE9 !important;
            outline: none !important;
            box-shadow: 0 4px 10px -5px rgba(111, 255, 233, 0.2);
        }
        .tab-text {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.2em;
            color: rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        }
        .tab-active {
            color: #6FFFE9 !important;
        }
        .tab-indicator {
            height: 2px;
            background: #6FFFE9;
            width: 100%;
            margin-top: 4px;
            box-shadow: 0 0 8px #6FFFE9;
        }
    
    
        
        .saas-card:active { transform: scale(0.95); }
        
        .no-scrollbar::-webkit-scrollbar { display: none; }
    
    
        .leave-error-blink { 
            border: 3px solid #ef4444 !important; 
            animation: error-pulse 0.8s infinite alternate;
        }
        @keyframes error-pulse { 
            from { border-color: #ef4444; box-shadow: 0 0 5px #ef4444; } 
            to { border-color: #fca5a5; box-shadow: 0 0 20px #ef4444; } 
        }
</style>
<script src="/static/student_view.js"></script>

    <script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register("/sw.js")
                .then(reg => console.log('SW Registered!', reg))
                .catch(err => console.log('SW Registration Failed!', err));
        });
    }
    </script>

    

    



<script>
    const OFFLINE_KEY = 'aps_offline_queue';

    // INTERCEPTOR WITH SECURITY
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        const url = args[0];
        const options = args[1];

        // RULE 1: Sensitive URLs hamesha ONLINE honi chahiye
        const sensitiveUrls = ['/api/login', '/logout', '/api/change-password'];
        const isSensitive = sensitiveUrls.some(u => url.includes(u));

        if (isSensitive) {
            

        if (!navigator.onLine) {
                alert("❌ SECURITY ERROR: Internet is required for Login/Logout.");
                throw new Error("Offline Sensitive Action");
            }
            return originalFetch(...args); // Direct bypass to server
        }

        // RULE 2: Baaki POST requests (Attendance, Leave, Diary) ko Offline handle karo
        if (!navigator.onLine && options && options.method === 'POST') {
            let payload = {};
            
            // Check for Files in Diary/Leave
            if (options.body instanceof FormData) {
                let hasFiles = false;
                options.body.forEach((v) => { if(v instanceof File && v.size > 0) hasFiles = true; });
                if (hasFiles) {
                    alert("⚠️ INTERNET REQUIRED: Files cannot be sent offline.");
                    throw new Error("Offline Files");
                }
                options.body.forEach((v, k) => { payload[k] = v; });
            } else {
                try { payload = JSON.parse(options.body); } catch(e) { payload = options.body; }
            }

            const queue = JSON.parse(localStorage.getItem(OFFLINE_KEY) || '[]');
            queue.push({url, data: payload, time: Date.now()});
            localStorage.setItem(OFFLINE_KEY, JSON.stringify(queue));

            return new Response(JSON.stringify({success: true, status: "offline"}), {
                status: 200, headers: {'Content-Type': 'application/json'}
            });
        }

        return originalFetch(...args);
    };

    // Auto-Sync Background Function
    async function syncNow() {
        if(!navigator.onLine) return;
        const queue = JSON.parse(localStorage.getItem(OFFLINE_KEY) || '[]');
        if(queue.length === 0) return;
        
        for(let i=0; i < queue.length; i++) {
            try {
                const res = await originalFetch(queue[i].url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(queue[i].data)
                });
                if(res.ok) queue.splice(i, 1);
            } catch(e) {}
        }
        localStorage.setItem(OFFLINE_KEY, JSON.stringify(queue));
    }
    setInterval(syncNow, 10000); // Check every 10 seconds
</script>

    <script src="/static/js/dexie.js"></script>
    <script src="/static/js/db.js"></script>
</head>

<body>
    
    <div id="custom-confirm" class="hidden fixed inset-0 z-[999999] flex items-center justify-center p-6 bg-[#0B132B]/80 backdrop-blur-md animate-fade-in">
        <div class="bg-[#1C2541] w-full max-w-[320px] rounded-[40px] p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)] scale-95 animate-zoom-in border border-white/10 text-center">
            <div class="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-blue-500/20">
                <svg class="w-10 h-10 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
            </div>
            <h3 id="confirm-msg" class="text-xl font-bold text-white leading-tight mb-8 tracking-tight">Are you sure you want to proceed?</h3>
            <div class="flex flex-col gap-3">
                <button id="confirm-yes" class="w-full py-4 rounded-2xl font-bold text-sm uppercase bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-900/20 active:scale-95 transition-all">Yes, Confirm</button>
                <button id="confirm-no" class="w-full py-4 rounded-2xl font-bold text-[11px] uppercase bg-white/5 text-gray-400 hover:bg-white/10 active:scale-95 transition-all tracking-widest">Cancel</button>
            </div>
        </div>
    </div>

    </div>

    <div id="toast-container"></div>
    <div class="app-shell">
        
        {% if not logged_in %}
        <div class="app-body flex flex-col items-center px-10 h-full justify-between pt-6 pb-12" style="background: #0B132B; color: white;">
            <div class="mt-0 flex flex-col items-center">
                <div class="w-20 h-20 mb-2">
                    <img src="/app_logo?v=1776620591" class="w-full h-full object-contain filter brightness-125" alt="AXIS">
                </div>
                <h1 class="text-2xl font-black tracking-[0.4em] text-white">AXIS</h1>
            </div>

            <div class="w-full space-y-12">
                <div class="flex justify-center gap-10">
                    <div onclick="setRole('Student')" id="sBtn" class="tab-text cursor-pointer tab-active">STUDENT<div id="sInd" class="tab-indicator"></div></div>
                    <div onclick="setRole('Teacher')" id="tBtn" class="tab-text cursor-pointer">STAFF<div id="tInd" class="tab-indicator hidden"></div></div>
                </div>

                <div class="space-y-6">
                    <input type="text" id="uid" placeholder="ID / B-FORM" class="w-full axis-input text-sm">
                    <input type="date" id="dob" value="2010-01-01" class="w-full axis-input text-sm opacity-50">
                </div>
            </div>

            <div class="w-full mb-4">
                <button onclick="doLogin()" class="w-full bg-[#6FFFE9] text-[#0B132B] py-4 rounded-full font-black text-[12px] tracking-[0.2em] uppercase active:scale-95 transition-all shadow-[0_10px_30px_-10px_rgba(111,255,233,0.4)]">
                    ENTER TERMINAL
                </button>
                <p class="text-[9px] font-bold tracking-[0.3em] uppercase opacity-50 text-center mt-12">© 2026 AXIS OS • V1.0.1</p>
            </div>
        </div>
        {% else %}
    
        
        
        
        
        
        <div id="main-header" class="app-header">
            <div class="flex justify-between items-center w-full">
                <span class="text-[13px] font-[800] text-[#6FFFE9] tracking-[0.15em] uppercase">AXIS</span>
                <span id="current-time" class="text-[11px] text-white/70 font-medium">00:00 AM</span>
            </div>

            <div id="header-identity-section">
                <div class="flex items-center gap-[12px] mt-0">
                    <div class="w-[34px] h-[34px] flex-shrink-0 bg-white/5 rounded-xl overflow-hidden shadow-sm border border-white/10">
                        <img src="/app_logo" class="w-full h-full object-contain" alt="Logo">
                    </div>
                    <div class="flex flex-col min-w-0 flex-1">
                        <h2 class="text-[18px] font-[800] text-white leading-tight truncate uppercase tracking-tight">{{ user.full_name }}</h2>
                        <span class="text-[12px] text-white/65 font-medium">
                            {% if user.role == "Student" %}
                                {{ user.assigned_class }}-{{ user.assigned_section }}
                            {% else %}
                                {{ user.role }}
                            {% endif %}
                        </span>
                    </div>
                </div>
                <div class="flex items-center gap-2 mt-0 pt-2 border-t border-white/5">
                    <div class="w-[6px] h-[6px] rounded-full bg-[#6FFFE9] shadow-[0_0_8px_#6FFFE9]"></div>
                    <span class="text-[10px] font-bold text-white/40 uppercase tracking-widest">Online • Secure Session</span>
                </div>
            </div>
            
            <div id="header-compact-section" class="hidden flex items-center gap-3 mt-1">
                <button onclick="showTab('home')" class="text-[#6FFFE9] text-xl">←</button>
                <h1 id="page-display-title" class="text-white font-[800] text-[16px] uppercase tracking-tight">PAGE</h1>
            </div>
        </div>

        <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('current-time').innerText = now.toLocaleTimeString('en-GB', { hour12: true, hour: '2-digit', minute: '2-digit' }).toUpperCase();
        }
        setInterval(updateClock, 1000);
        updateClock();

        async function loadFinalizeStatus() {
            const area = document.getElementById('finalize-content-area');
            if(!area) return;
            area.innerHTML = '<div class="p-8 text-center"><div class="animate-spin text-2xl mb-2">🔄</div><p class="text-[10px] font-black uppercase text-gray-400">Loading Status...</p></div>';
            try {
                const r = await fetch('/api/class-finalize-status');
                const d = await r.json();
                if(!d.success) { area.innerHTML = `<p class="text-rose-500 font-bold">${d.error}</p>`; return; }
                let html = `<div class="glass-card mb-4 border-l-4 border-orange-500 bg-orange-50/50"><h4 class="text-[10px] font-black text-orange-600 uppercase">${d.exam_name}</h4><p class="text-sm font-black text-slate-800">CLASS READINESS</p></div>`;
                d.status.forEach(s => {
                    html += `<div class="glass-card flex items-center justify-between py-2 px-3 mb-2"><div><p class="text-[10px] font-black uppercase">${s.subject}</p><p class="text-[8px] text-gray-400">${s.teacher}</p></div><span class="${s.submitted ? 'text-emerald-600' : 'text-rose-600'} font-black text-[9px]">${s.submitted ? '✓ READY' : '× PENDING'}</span></div>`;
                });
                if(d.is_ready) html += `<button onclick="publishResult(${d.exam_id})" class="w-full bg-[#1B4332] text-white py-3 rounded-xl font-black text-xs mt-0">🚀 PUBLISH RESULT</button>`;
                area.innerHTML = html;
            } catch(e) { area.innerHTML = "Error!"; }
        }
        async function publishResult(id) {
            if(!confirm("Lock all marks?")) return;
            const r = await fetch('/api/publish-final-result', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({exam_id:id})});
            if((await r.json()).success) { alert("Published!"); loadFinalizeStatus(); }
        }
        function showTab(t) {
            document.querySelectorAll('[id^="page-"]').forEach(p => p.classList.add('hidden'));
            const target = document.getElementById('page-' + t);
            if(target) { target.classList.remove('hidden'); if(t === 'final-upload') loadFinalizeStatus(); }
        }
        </script>






        <div class="app-body">
            
            
            
            
            
            <div id="page-home" class="space-y-6 animate-zoom-in">
                

                <div class="grid grid-cols-2 gap-4">
                    {% if user.role == 'Student' %}
                    <div onclick="openDiaryHub()" class="saas-card group">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Diary</h4>
                        <p class="text-[8px] text-slate-500 font-medium mt-1">Daily Homework</p>
                    </div>
                    <div onclick="showTab('mark')" class="saas-card group">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Reports</h4>
                        <p class="text-[8px] text-slate-500 font-medium mt-1">Performance</p>
                    </div>
                    {% endif %}

                    {% if user.role == 'Teacher' %}
                    <div onclick="openDiaryHub()" class="saas-card group">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Post Diary</h4>
                    </div>
                    <div onclick="navToMarks()" class="saas-card group hidden">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Marks Entry</h4>
                    </div>
                    {% endif %}

                    {% if user.is_class_teacher %}
                    <div onclick="showTab('mark')" class="saas-card group">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 002-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Attendance</h4>
                    </div>
                    {% endif %}

                    <div onclick="openLeaveHub()" class="saas-card group">
                        
                        <svg class="w-6 h-6 mb-3 text-inherit" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                        <h4 class="font-bold text-[12px] tracking-normal">Leave Hub</h4>
                    </div>
                </div>

            </div>

            <div id='page-results' class='hidden animate-slide-up pb-24'>
        
        <div id='student-result-container' class='space-y-4'></div>
    </div>
    <div id='page-marks-entry' class='hidden space-y-4 max-w-md mx-auto'><div id='teacher-assign-list'></div></div>
    <div id='page-final-upload' class='hidden space-y-4 max-w-md mx-auto'>
        <div class='flex items-center justify-between mb-2'>
            <h3 class='font-black text-xl text-[#1B4332] uppercase tracking-tighter'>Final Upload</h3>
            <button onclick="showTab('home')" class='bg-gray-100 px-3 py-1 rounded-lg text-[10px] font-black text-gray-500'>BACK</button>
        </div>
        <div id='finalize-main-container' class='w-full space-y-4'>
            <div id="finalize-content-area" class="space-y-4"></div>
        </div>
    </div>
            
    <div id="page-leave" class="hidden animate-slide-up pb-10">
        
        <div id="leave-content-area" class="space-y-4"></div>
    </div>
    
<div id="page-diary" class="hidden space-y-4">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="font-black text-xl text-[#1B4332]">Diary Hub</h3>
                    <button onclick="showTab('home')" class="text-xs font-bold text-gray-400">← BACK</button>
                </div>

                {% if user.role == 'Teacher' %}
                <div id="teacher-diary-controls" class="space-y-3">
                    <div onclick="showDiaryForm()" class="glass-card flex items-center p-5 border-l-8 border-purple-600">
                        <div class="text-3xl mr-4">✍️</div>
                        <div><h4 class="font-black text-sm uppercase">Write New Diary</h4><p class="text-[10px] text-gray-400">Post for your classes</p></div>
                    </div>
                    <div onclick="loadDiaryHistory()" class="glass-card flex items-center p-5 border-l-8 border-gray-400">
                        <div class="text-3xl mr-4">📂</div>
                        <div><h4 class="font-black text-sm uppercase">Manage History</h4><p class="text-[10px] text-gray-400">View/Search past posts</p></div>
                    </div>
                </div>

                <div id="diary-post-form" class="hidden glass-card p-4 space-y-3">
                    <select id="diary-target" class="w-full p-3 rounded-xl bg-gray-50 border-none text-xs font-bold"></select>
                    <textarea id="diary-content" placeholder="Enter Homework details..." class="w-full p-4 rounded-xl bg-gray-50 border-none text-sm min-h-[120px]"></textarea>
                    
                    <div class="flex items-center space-x-2 p-2 bg-yellow-50 rounded-lg">
                        <input type="checkbox" id="diary-sch-check" onchange="toggleSchDate()">
                        <label class="text-[10px] font-bold text-yellow-700 uppercase">Schedule Post?</label>
                        <input type="date" id="diary-sch-date" class="hidden p-1 text-[10px] border-none bg-transparent">
                    </div>

                    
                    <div id="attach-preview-zone" class="hidden mb-2 p-2 bg-blue-50/50 rounded-xl border border-dashed border-blue-200">
                        <div class="flex justify-between items-center mb-2 px-1">
                            <span id="attach-count" class="text-[9px] font-black text-blue-700 uppercase">0 Files Attached</span>
                            <button type="button" onclick="clearAttaches()" class="text-[9px] font-bold text-red-500">RESET</button>
                        </div>
                        <div id="attach-list" class="flex flex-wrap gap-1"></div>
                    </div>

                    <div class="flex items-center justify-between">
                        <label class="flex items-center cursor-pointer bg-blue-50 px-4 py-2 rounded-xl">
                            <span class="text-[10px] font-bold text-blue-600">📎 ATTACH (MAX 50)</span>
                            <input type="file" id="diary-files" multiple class="hidden">
                        </label>
                        <button onclick="submitDiary()" id="btn-pub" class="bg-[#1B4332] text-white px-6 py-2 rounded-xl font-black text-xs uppercase shadow-lg">🚀 Publish</button>
                    </div>
                </div>
                {% endif %}

                <div id="diary-display-list" class="space-y-4 pb-20"></div>
            </div>

            <div id="page-mark" class="hidden space-y-4">
                <h3 class="font-black text-xl text-[#1B4332]">Attendance Hub</h3>
                <div onclick="openAttendanceTab('marking')" class="glass-card flex items-center p-5 border-l-8 border-[#1B4332]">
                    <div class="text-3xl mr-4">🖋️</div>
                    <div><h4 class="font-black text-sm">MARK ENTRIES</h4><p id="lock-status-text" class="text-[10px] text-gray-400 font-bold">Checking status...</p></div>
                </div>
                <div onclick="openAttendanceTab('archive')" class="glass-card flex items-center p-5 border-l-8 border-[#D4AF37]">
                    <div class="text-3xl mr-4">📅</div>
                    <div><h4 class="font-black text-sm">ARCHIVE</h4><p class="text-[10px] text-gray-400">History Search</p></div>
                </div>
                <div onclick="showTab('intel-view'); loadIntel();" class="glass-card flex items-center p-5 border-l-8 border-blue-600">
                    <div class="text-3xl mr-4">💎</div>
                    <div><h4 class="font-black text-sm">INTEL</h4><p class="text-[10px] text-gray-400">Analytics</p></div>
                </div>
            </div>

            
            <div id="page-marking-view" class="hidden space-y-4">
                <button onclick="showTab('marks-entry')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest">← Back</button>
                <div id="marking-area-v2" class="space-y-3"></div>
            </div>
            <div id="page-attendance-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest">← Back</button>
                <div id="lock-banner"></div>
                <div id="marking-area" class="space-y-3"></div>
                <div id="marking-footer"></div>
            </div>

            <div id="page-archive-view" class="hidden space-y-4 pb-10">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">← Back</button>
                
                {% if user.role == 'Student' %}
                <div class="p-5 rounded-3xl text-white shadow-xl relative overflow-hidden" style="background: linear-gradient(135deg, #0F2A44 0%, #173A5E 100%);">
                    <div class="relative z-10">
                        <p class="text-[10px] font-bold uppercase tracking-widest opacity-70">Attendance Overview</p>
                        <div class="flex justify-between items-end mt-2">
                            <h2 class="text-3xl font-black" id="archive-month-title">...</h2>
                            <div class="text-right">
                                <p class="text-[10px] uppercase tracking-widest opacity-70">Rate</p>
                                <h3 class="text-xl font-black text-emerald-400" id="archive-rate-text">0%</h3>
                            </div>
                        </div>
                        <div class="w-full bg-white/10 h-2 rounded-full overflow-hidden mt-4">
                            <div id="archive-progress-bar" class="bg-emerald-400 h-full transition-all duration-700" style="width:0%"></div>
                        </div>
                        <div class="flex justify-between mt-5 text-xs font-bold bg-black/20 p-3.5 rounded-2xl backdrop-blur-sm border border-white/5">
                            <div class="flex flex-col items-center"><span class="text-emerald-400 text-base" id="stat-present" onclick="setArchiveFilter('Present')" style="cursor:pointer;">0</span><span class="text-[9px] uppercase opacity-70 mt-1">Present</span></div>
                            <div class="flex flex-col items-center"><span class="text-rose-400 text-base" id="stat-absent" onclick="setArchiveFilter('Absent')" style="cursor:pointer;">0</span><span class="text-[9px] uppercase opacity-70 mt-1">Absent</span></div>
                            <div class="flex flex-col items-center"><span class="text-amber-400 text-base" id="stat-leave" onclick="setArchiveFilter('Leave')" style="cursor:pointer;">0</span><span class="text-[9px] uppercase opacity-70 mt-1">Leave</span></div>
                        </div>
                    </div>
                    <div class="absolute -right-8 -bottom-8 text-[140px] opacity-5">🧭</div>
                </div>

                <div class="flex gap-2 overflow-x-auto py-3 mt-1" style="scrollbar-width: none;" id="archive-filters">
                    <button onclick="setArchiveFilter('week')" id="filter-week" class="filter-chip px-5 py-2.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-all shadow-sm" style="background: #E8EEF7; color: #0F2A44;">This Week</button>
                    <button onclick="setArchiveFilter('month')" id="filter-month" class="filter-chip px-5 py-2.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-all shadow-sm" style="background: #2F80ED; color: white;">This Month</button>
                    <button onclick="setArchiveFilter('all')" id="filter-all" class="filter-chip px-5 py-2.5 rounded-full text-[11px] font-bold whitespace-nowrap transition-all shadow-sm" style="background: #E8EEF7; color: #0F2A44;">All Time</button>
                    <input type="date" id="filter-custom" onchange="setArchiveFilter('custom')" class="filter-chip px-3 py-2 rounded-full text-[11px] font-bold shadow-sm border-none outline-none cursor-pointer" style="background: #E8EEF7; color: #0F2A44;">
                </div>

                <div id="student-archive-list" class="mt-2 space-y-3 pb-10"></div>
                {% else %}
                <input type="date" id="archive-date" onchange="loadArchive()" placeholder="Select date for specific day" class="w-full p-3 rounded-xl bg-gray-50 border-none font-bold">
                <div id="archive-results" class="space-y-2"></div>
                {% endif %}
            </div>
            
            
            
            
            
            
            <div id="page-intel-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">← Back to Hub</button>
                <div id="intel-view" class="space-y-6"></div>
            </div>
            
            <div id="page-profile" class="hidden pb-24 animate-fade-in">
                <div class="bg-gradient-to-b from-[#0F172A] to-[#1E3A8A] p-8 pb-12 rounded-b-[40px] flex flex-col items-center text-white shadow-xl">
                    <div class="relative group">
                        <div id="profile-avatar-container" class="w-28 h-28 rounded-full border-4 border-white/30 shadow-2xl overflow-hidden bg-white/10 flex items-center justify-center backdrop-blur-md">
                            {% if user.profile_pic %}
                                <img id="user-pfp" src="{{ user.profile_pic }}" class="w-full h-full object-cover">
                            {% else %}
                                <span id="user-initial" class="text-4xl font-black text-blue-600">{{ user.full_name[0]|upper }}</span>
                            {% endif %}
                        </div>
                        <button onclick="openPfpMenu()" class="absolute bottom-0 right-0 bg-white text-blue-600 p-2 rounded-full shadow-lg hover:scale-110 transition-transform">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        </button>
                    </div>
                    <h1 class="mt-4 text-2xl font-black tracking-tight">{{ user.full_name|title }}</h1>
                    <div class="flex items-center space-x-2 mt-1 opacity-90">
                        <span class="bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest">{% if user.role == "Teacher" and user.is_class_teacher %}Class Teacher{% else %}{{ user.role }}{% endif %}</span>
                        <span class="text-sm">•</span>
                        <span class="text-sm font-medium">{% if user.role == "Student" %}{{ user.student_class }}-{{ user.student_section }}{% else %}{% endif %}</span>
                    </div>
                </div>

                <div class="px-6 -mt-8 space-y-4">
                    <div class="bg-white rounded-3xl p-6 shadow-sm border border-gray-100">
                        <div class="flex items-center space-x-3 mb-4 text-blue-900">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path></svg>
                            <h2 class="font-black text-sm uppercase tracking-wider">{% if user.role == "Student" %}Academic Details{% else %}Professional Duties{% endif %}</h2>
                        </div>
                        <div class="grid grid-cols-1 gap-4">
                            {% if user.role == "Student" %}
                            <div class="grid grid-cols-2 gap-4">
                                <div><p class="text-[10px] text-gray-400 uppercase font-bold">Roll Number</p><p class="font-bold text-gray-800">{{ user.roll_number or 'N/A' }}</p></div>
                                <div><p class="text-[10px] text-gray-400 uppercase font-bold">Wing</p><p class="font-bold text-gray-800">{{ user.wing }}</p></div>
                                <div><p class="text-[10px] text-gray-400 uppercase font-bold">Section</p><p class="font-bold text-gray-800">{{ user.student_section }}</p></div>
                                <div><p class="text-[10px] text-gray-400 uppercase font-bold">Status</p><p class="text-green-600 font-bold text-xs flex items-center">● Active</p></div>
                            </div>
                            {% else %}
                                {% if user.is_class_teacher %}
                                <div><p class="text-[10px] text-gray-400 uppercase font-bold">Assigned Class</p><p class="font-bold text-blue-900 text-sm">{{ user.assigned_class }}-{{ user.assigned_section }} ({{ user.assigned_wing }})</p></div>
                                {% endif %}
                                <div>
                                    <p class="text-[10px] text-gray-400 uppercase font-bold mb-2">Assigned Subjects</p>
                                    <div class="flex flex-wrap gap-2">
                                        {% for sub in user.assignments %}
                                        <span class="px-2 py-1 bg-gray-100 border border-gray-200 rounded-lg text-[10px] font-bold text-inherit">
                                            {{ sub.name|upper }} {{ sub.student_class }}-{{ sub.section }}-{% if sub.wing|lower in ['girls', 'g'] %}Girl{% elif sub.wing|lower in ['boys', 'b'] %}Boy{% else %}{{ sub.wing }}{% endif %}
                                        </span>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endif %}
                        </div>
                    </div>

                    <details class="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden group">
                        <summary class="flex items-center justify-between p-6 cursor-pointer list-none">
                            <div class="flex items-center space-x-3 text-inherit font-black text-sm uppercase tracking-wider">
                                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                                <span>Personal Profile</span>
                            </div>
                            <svg class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                        </summary>
                        <div class="px-6 pb-6 space-y-4 border-t border-gray-50 pt-4">
                            <div><p class="text-[10px] text-gray-400 font-bold uppercase">Father's Name</p><p class="font-medium text-inherit">{{ user.father_name|title }}</p></div>
                            <div><p class="text-[10px] text-gray-400 font-bold uppercase">Date of Birth</p><p class="font-medium text-inherit">{{ user.dob }}</p></div>
                            <div><p class="text-[10px] text-gray-400 font-bold uppercase">CNIC / B-Form</p><p class="font-medium text-inherit">{{ user.cnic or user.b_form }}</p></div>
                            <div><p class="text-[10px] text-gray-400 font-bold uppercase">Mobile Number</p><p class="font-medium text-inherit">{{ user.contact or user.parents_phone or "N/A" }}</p></div>
                            <div><p class="text-[10px] text-gray-400 font-bold uppercase">Address</p><p class="font-medium text-xs text-gray-600 leading-relaxed">{{ user.address if "IMG_DATA:" not in user.address else "Primary Residence" }}</p></div>
                        </div>
                    </details>

                    <button onclick="safeLogout(event)" class="w-full bg-[#1E3A8A] text-white p-5 rounded-3xl font-black text-sm flex items-center justify-center space-x-2 border-2 border-slate-800 hover:bg-blue-900 transition-all shadow-lg">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                        <span>LOGOUT FROM APP</span>
                    </button>

                    <div class="text-center pb-12 pt-6">
                        <a href="https://instagram.com/ftsamiii" target="_blank" class="inline-flex flex-col items-center group active:scale-95 transition-transform">
                            <div class="mb-2 p-[2px] rounded-xl bg-gradient-to-tr from-[#f9ce34] via-[#ee2a7b] to-[#6228d7] shadow-lg shadow-pink-500/20">
                                <div class="bg-white p-1.5 rounded-[10px]">
                                    <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M12 7C9.23858 7 7 9.23858 7 12C7 14.7614 9.23858 17 12 17C14.7614 17 17 14.7614 17 12C17 9.23858 14.7614 7 12 7ZM9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12Z" fill="url(#ig_grad)"/>
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M18 5C17.4477 5 17 5.44772 17 6C17 6.55228 17.4477 7 18 7C18.5523 7 19 6.55228 19 6C19 5.44772 18.5523 5 18 5Z" fill="url(#ig_grad)"/>
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12ZM12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4Z" fill="url(#ig_grad)"/>
                                        <defs>
                                            <linearGradient id="ig_grad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                                                <stop stop-color="#f9ce34"/>
                                                <stop offset="0.5" stop-color="#ee2a7b"/>
                                                <stop offset="1" stop-color="#6228d7"/>
                                            </linearGradient>
                                        </defs>
                                    </svg>
                                </div>
                            </div>
                            <p class="text-[11px] font-black text-slate-800 tracking-[0.25em] uppercase mb-1">AXIS | Digital Architecture</p>
                            <p class="text-[9px] font-medium text-slate-400 tracking-normal">Tap to connect with developer</p>
                        </a>
                    </div>
                </div>
            </div>

            <div id="pfp-modal" class="fixed inset-0 bg-black/40 z-[100] hidden backdrop-blur-sm flex items-center justify-center p-4">
                <div class="w-full max-w-sm bg-white rounded-[24px] p-6 shadow-2xl scale-95 transition-transform">
                    <div class="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-6"></div>
                    <h3 class="text-xl font-black text-gray-800 mb-6 text-center">Manage Profile Picture</h3>
                    <div class="space-y-3">
                        <button onclick="document.getElementById('pfp-input').click()" class="w-full bg-blue-600 text-white p-4 rounded-2xl font-bold flex items-center justify-center space-x-3">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                            <span>Upload New Photo</span>
                        </button>
                        <button onclick="removePfp()" class="w-full bg-gray-100 text-red-600 p-4 rounded-2xl font-bold flex items-center justify-center space-x-3">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            <span>Remove Current</span>
                        </button>
                        <button onclick="closePfpMenu()" class="w-full text-gray-500 p-4 font-bold">Cancel</button>
                    </div>
                    <input type="file" id="pfp-input" class="hidden" accept="image/*" onchange="handlePfpUpload(this)">
                </div>
            </div>


        </div>

        <div class="app-nav">
            <div onclick="showTab('home')" id="n-home" class="nav-btn active-nav">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
                <span>Dashboard</span>
            </div>
            
            {% if user.role == 'Student' or (user.role == 'Teacher' and user.is_class_teacher) %}
            <div onclick="showTab('mark')" id="n-mark" class="nav-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                <span>{{ 'Activity' if user.role == 'Student' else 'Attend' }}</span>
            </div>
            {% endif %}

            <div onclick="showTab('profile')" id="n-profile" class="nav-btn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                <span>Account</span>
            </div>
        </div>
        {% endif %}
    </div>



    <script>
        let currentEditCount = 0;
        let isLocked = false;

        function setRole(r) {
            window.currentRole = r;
            document.getElementById('sBtn').classList.toggle('tab-active', r === 'Student');
            document.getElementById('tBtn').classList.toggle('tab-active', r === 'Teacher');
            document.getElementById('sInd').classList.toggle('hidden', r !== 'Student');
            document.getElementById('tInd').classList.toggle('hidden', r !== 'Teacher');
        }
        window.currentRole = 'Student';

        
        async function doLogin() {
            const loginBtn = event.target;
            const originalText = loginBtn.innerText;

            // Step 1: Strict Internet Check
            

        if (!navigator.onLine) {
                showToast("❌ OFFLINE: Internet connection required to login!", "error");
                return;
            }

            try {
                // UI Feedback
                loginBtn.disabled = true;
                loginBtn.innerText = "⏳ AUTHENTICATING...";

                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        uid: document.getElementById('uid').value, 
                        dob: document.getElementById('dob').value, 
                        role: window.currentRole
                    })
                });

                if (res.status === 503) {
                    throw new Error("Offline Mode Active");
                }

                const data = await res.json();
                
                if(data.success) { 
                    localStorage.setItem("isLoggedIn", "true"); 
                    showToast("✅ Login Successful! Redirecting...", "success");
                    if(window.location.pathname === "/login" || window.location.pathname === "/") { 
                        window.location.replace("/?login=" + Date.now()); 
                    } 
                } else {
                    showToast("❌ Login Failed: " + (data.error || "Invalid Credentials"), "error");
                }
            } catch (err) {
                console.error("Login Error:", err);
                showToast("❌ CONNECTION ERROR: Cannot reach server!", "error");
            } finally {
                loginBtn.disabled = false;
                loginBtn.innerText = originalText;
            }
        }
    

        
    let diaryAssignments = [];
    
    
    async function openDiaryHub() { markDiariesAsRead();
        showTab('diary');
        
        // Reset UI Elements
        const btn = document.getElementById('btn-pub');
        if(btn) {
            btn.disabled = false;
            btn.innerText = "🚀 Publish";
        }
        const contentInput = document.getElementById('diary-content');
        if(contentInput) contentInput.value = '';
        
        const fileInput = document.getElementById('diary-files');
        if(fileInput) fileInput.value = '';

        {% if user.role == 'Teacher' %}
            const res = await fetch('/api/diary/init-teacher');
            diaryAssignments = await res.json();
            document.getElementById('teacher-diary-controls').classList.remove('hidden');
            document.getElementById('diary-post-form').classList.add('hidden');
            document.getElementById('diary-display-list').innerHTML = '';
        {% else %}
            loadStudentDiary();
        {% endif %}
    }

    function showDiaryForm() {
        const select = document.getElementById('diary-target');
        select.innerHTML = diaryAssignments.map(a => `<option value='${JSON.stringify(a)}'>${a.sub_name} | Class ${a.student_class}-${a.section} (${a.wing})</option>`).join('');
        document.getElementById('teacher-diary-controls').classList.add('hidden');
        document.getElementById('diary-post-form').classList.remove('hidden');
    }

    function toggleSchDate() {
        document.getElementById('diary-sch-date').classList.toggle('hidden', !document.getElementById('diary-sch-check').checked);
    }

    
    async function submitDiary() {
        const btn = document.getElementById('btn-pub');
        const contentVal = document.getElementById('diary-content').value;
        if(!contentVal) return alert("Please write some content!");
        
        btn.disabled = true; 
        btn.innerText = "Sending...";
        
        try {
            const target = JSON.parse(document.getElementById('diary-target').value);
            const formData = new FormData();
            formData.append('content', contentVal);
            formData.append('class', target.student_class);
            formData.append('section', target.section);
            formData.append('wing', target.wing);
            formData.append('subject', target.sub_name);
            
            const schCheck = document.getElementById('diary-sch-check');
            if(schCheck && schCheck.checked) {
                formData.append('schedule_date', document.getElementById('diary-sch-date').value);
            }
            
            const files = document.getElementById('diary-files').files;
            for(let i=0; i<files.length; i++) formData.append('files', files[i]);

            const res = await fetch('/api/diary/post', { method: 'POST', body: formData });
            
            
            if(result.success) {
                alert("✅ Diary Published Successfully!");
                // This will reset the button and clear the form
                await openDiaryHub(); 
            } else {
                alert("❌ Error: " + result.msg);
                btn.disabled = false;
                btn.innerText = "🚀 Publish";
            }
        } catch (e) {
            alert("⚠️ Error: " + e.message);
            btn.disabled = false;
            btn.innerText = "🚀 Publish";
        }
    }

    
    async function loadStudentDiary() {
        const list = document.getElementById('diary-display-list');
        list.innerHTML = '<p class="text-center text-xs font-bold text-gray-400 py-10">Fetching...</p>';
        
        let u = JSON.parse(localStorage.getItem('user') || '{}');
        let role = u.role || 'Student';

        try {
            const res = await fetch('/api/diary/fetch');
            const diaries = await res.json();
            
            if(!diaries || diaries.length === 0) {
                list.innerHTML = '<div class="text-center py-10 opacity-40"><div class="text-5xl mb-2">📭</div><p class="font-black text-xs">No diary entries found</p></div>';
                return;
            }

            list.innerHTML = diaries.map(d => {
                // Teacher kelye Class-Section, Student kelye Teacher ka naam
                const metaInfo = (role === "Teacher") ? `FOR: ${d.class}-${d.section} (${d.wing})` : `BY: ${d.teacher_name}`;
                const datePart = d.date_posted ? d.date_posted.split('|')[0] : '---';
                
                return `
                <div class="glass-card p-4 border-l-4 border-amber-500 mb-3 animate-fade-in">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-black text-sm text-[#1B4332]">${d.subject}</h4>
                        <span class="text-[9px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-lg">${datePart}</span>
                    </div>
                    <p class="text-xs text-gray-600 leading-relaxed mb-3">${d.content}</p>
                    <div class="flex justify-between items-center mt-0 pt-2 border-t border-gray-100">
                        <span class="text-[8px] font-bold text-gray-400 uppercase">${metaInfo}</span>
                        <div class="flex space-x-2">
                            ${d.attachments ? d.attachments.split(',').filter(x=>x).map((url, idx) => `
                                <button onclick="viewMedia('${url}', ${idx})" class="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-lg">👁️ View ${idx+1}</button>
                            `).join('') : ''}
                        </div>
                    </div>
                </div>`;
            }).join('');
        } catch (e) {
            console.error(e);
            list.innerHTML = '<p class="text-center text-red-500 text-xs py-10">Error loading diary.</p>';
        }
    }


    async function loadDiaryHistory() {
        document.getElementById('teacher-diary-controls').classList.add('hidden');
        loadStudentDiary(); // Reuse the same display logic
    }

        function showTab(t) {
            // Auto-lock profile if moving away or coming back to it
            if (t === "profile") { /* Vault check removed */ }

            const pages = ['home', 'diary', 'mark', 'results', 'marks-entry', 'final-upload', 'profile', 'marking-view', 'attendance-view', 'archive-view', 'intel-view', 'leave', 'marks-portal'];
            pages.forEach(p => {
                const el = document.getElementById('page-' + p);
                if (el) el.classList.add('hidden');
                if (t === 'results') loadStudentResults();
            });

            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active-nav'));
            
            const targetPage = document.getElementById('page-' + t);
            if (targetPage) targetPage.classList.remove('hidden');
            
            if(document.getElementById('n-' + t)) {
                document.getElementById('n-' + t).classList.add('active-nav');
            } else if (t === 'archive-view' || t === 'marking-view' || t === 'attendance-view') {
                // Agar sub-pages pe hon tab bhi Activity tab ko glow rakho
                const markTab = document.getElementById('n-mark');
                if(markTab) markTab.classList.add('active-nav');
            }

            // --- ADAPTIVE HEADER LOGIC ---
            const header = document.getElementById('main-header');
            const identity = document.getElementById('header-identity-section');
            const compact = document.getElementById('header-compact-section');
            const pageTitle = document.getElementById('page-display-title');
            const clock = document.getElementById('current-time');

            const titles = {
                'home': 'Home',
                'diary': 'Daily Diary',
                'mark': 'Attendance',
                'leave': 'Leave Hub',
                'profile': 'User Profile',
                'results': 'Exam Results',
                'marks-entry': 'Marks Entry',
                'final-upload': 'Finalize & Submit',
                'marking-view': 'Grading Portal',
                'attendance-view': 'Attendance Mark',
                'archive-view': 'History Archive',
                'intel-view': 'System Intel'
            };

            // Removed marking-view and attendance-view from here so header stays visible
            const fullScreenPages = ['archive-view', 'intel-view'];
            
            if (fullScreenPages.includes(t)) {
                header.classList.add('hidden');
            } else {
                header.classList.remove('hidden');
                if (t === 'home') {
                    // Home: Full Header Mode
                    identity.classList.remove('hidden');
                    compact.classList.add('hidden');
                    clock.classList.remove('hidden');
                    header.style.minHeight = '80px';
                } else {
                    // Inner Pages: Compact Mode
                    identity.classList.add('hidden');
                    compact.classList.remove('hidden');
                    clock.classList.add('hidden');
                    header.style.minHeight = '30px';
                    if(titles[t]) pageTitle.innerText = titles[t];
                }
            }

            if(t === 'mark') {
                if('{{ user.role }}' === 'Student') {
                    showTab('archive-view');
                    loadArchive();
                } else {
                    checkLockStatus();
                }
            }
        }

        async function checkLockStatus() {
            const res = await fetch('/api/check-lock');
            const data = await res.json();
            currentEditCount = data.edit_count;
            isLocked = currentEditCount >= 2;
            document.getElementById('lock-status-text').innerText = isLocked ? "STATUS: LOCKED 🛡️" : (currentEditCount === 1 ? "STATUS: 1 EDIT LEFT" : "STATUS: OPEN");
        }

        async function openAttendanceTab(type) {
            if(type === 'marking') {
                await checkLockStatus();
                showTab('attendance-view');
                loadMarkingInterface();
            } else {
                showTab(type + '-view');
                if(type === 'archive') loadArchive();
                if(type === 'intel') loadIntel();
            }
        }

        async function loadMarkingInterface() {
            const list = document.getElementById('marking-area');
            const banner = document.getElementById('lock-banner');
            const footer = document.getElementById('marking-footer');
            
            if(isLocked) {
                banner.innerHTML = '<div class="glass-card bg-green-50 text-center border-green-200"><h2 class="text-3xl">🛡️</h2><h4 class="font-black text-green-700">ATTENDANCE SECURED</h4><p class="text-[10px] font-bold">Database is finalized for today.</p></div>';
                footer.innerHTML = '';
            } else {
                banner.innerHTML = currentEditCount === 1 ? '<div class="p-3 bg-red-50 text-red-600 text-[10px] font-black rounded-xl border border-red-100 uppercase">⚠️ Last chance to edit. Database will lock after sync.</div>' : '<div class="p-3 bg-yellow-50 text-yellow-700 text-[10px] font-black rounded-xl border border-yellow-100 uppercase">💡 Marking active. You can edit once after saving.</div>';
                footer.innerHTML = '<button onclick="syncAttendance()" class="btn-sync">🚀 FINAL LOCK & SYNC</button>';
            }

            const res = await fetch('/api/students-marking');
            const data = await res.json();
            list.innerHTML = data.students.map(s => {
                let statusControl = '';
                if(isLocked) {
                    statusControl = `<span class="status-pill ${s.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${s.status || 'N/A'}</span>`;
                } else if(s.on_leave > 0) {
                    // Logic for locked leave status
                    statusControl = `<span class="bg-amber-100 text-amber-700 text-[10px] font-black px-3 py-1.5 rounded-full border border-amber-200 animate-pulse">📝 ON LEAVE</span>
                                     <input type="hidden" id="s_${s.id}" value="Leave">`;
                } else {
                    // Normal dropdown
                    statusControl = `
                    <select id="s_${s.id}" class="text-xs font-black bg-gray-50 p-2 rounded-lg border-none outline-none">
                        <option value="Present" ${s.status === 'Present' ? 'selected' : ''}>Present</option>
                        <option value="Absent" ${s.status === 'Absent' ? 'selected' : ''}>Absent</option>
                        <option value="Leave" ${s.status === 'Leave' ? 'selected' : ''}>Leave</option>
                    </select>`;
                }
                return `
                <div class="glass-card flex justify-between items-center ${s.on_leave > 0 ? 'bg-amber-50/40 border-amber-200' : ''}">
                    <div><p class="text-[9px] font-bold text-gray-400">#${s.roll_number}</p><h4 class="font-black text-sm">${s.full_name}</h4></div>
                    ${statusControl}
                </div>`;
            }).join('');
        }

        async function syncAttendance() {
            if(!(await askUser("Lock this record?"))) return;
            const students = document.querySelectorAll('[id^="s_"]');
            const attendance = Array.from(students).map(s => ({ id: s.id.split('_')[1], status: s.value }));
            
            const res = await fetch('/api/sync-attendance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ attendance })
            });
            const data = await res.json();
            if(data.success) { alert("Successfully Synced!"); showTab('mark'); } else { alert("Error syncing: " + data.error); }
        }

        let currentArchiveFilter = 'month';
        let rawArchiveData = [];

        function setArchiveFilter(f) {
            const stats=['Present','Absent','Leave']; if(stats.includes(f)){ window.statusFilter=(window.statusFilter===f)?null:f; } else { currentArchiveFilter=f; window.statusFilter=null; }
            document.querySelectorAll('.filter-chip').forEach(c => {
                c.style.background = '#E8EEF7';
                c.style.color = '#0F2A44';
            });
            const active = document.getElementById('filter-' + f);
            if(active) {
                active.style.background = '#2F80ED';
                active.style.color = 'white';
            }
            renderStudentArchive();
        }

        async function loadArchive() {
            if ('{{ user.role }}' === 'Student') {
                document.getElementById('student-archive-list').innerHTML = '<div class="flex justify-center py-10"><div class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div></div>';
                const res = await fetch('/api/archive');
                rawArchiveData = await res.json();
                renderStudentArchive();
            } else {
                const dateInput = document.getElementById('archive-date') ? document.getElementById('archive-date').value : '';
                let date = dateInput || new Date().toISOString().split('T')[0];
                const res = await fetch('/api/archive?date=' + date);
                const data = await res.json();
                const container = document.getElementById('archive-results');
                if(container) {
                    container.innerHTML = data.map(s => `
                        <div class="flex justify-between items-center p-4 bg-gray-50 rounded-2xl">
                            <div>
                                <span class="text-[9px] font-bold text-gray-400">${s.date || ''}</span>
                                <h4 class="text-xs font-black">${s.full_name || 'My Record'}</h4>
                            </div>
                            <span class="status-pill ${s.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${s.status}</span>
                        </div>
                    `).join('') || '<p class="text-center text-xs py-10 font-bold text-slate-500">No history found.</p>';
                }
            }
        }

        function renderStudentArchive() {
            if (!rawArchiveData || rawArchiveData.length === 0) {
                document.getElementById('student-archive-list').innerHTML = '<p class="text-center text-xs py-10 font-bold text-slate-500">No attendance history found.</p>';
                return;
            }
            const now = new Date();
            let filtered = [];
            
            if (currentArchiveFilter === 'week') {
                const weekAgo = new Date();
                weekAgo.setDate(now.getDate() - 7);
                filtered = rawArchiveData.filter(s => new Date(s.date) >= weekAgo);
            } else if (currentArchiveFilter === 'month') {
                const monthAgo = new Date();
                monthAgo.setMonth(now.getMonth() - 1);
                filtered = rawArchiveData.filter(s => new Date(s.date) >= monthAgo);
            } else {
            const now = new Date();
            if (currentArchiveFilter === 'week') {
                const weekAgo = new Date(); weekAgo.setDate(now.getDate() - 7);
                filtered = rawArchiveData.filter(s => new Date(s.date) >= weekAgo);
            } else if (currentArchiveFilter === 'month') {
                const monthAgo = new Date(); monthAgo.setMonth(now.getMonth() - 1);
                filtered = rawArchiveData.filter(s => new Date(s.date) >= monthAgo);
            } else if (currentArchiveFilter === 'custom') {
                const sel = document.getElementById('filter-custom').value;
                filtered = sel ? rawArchiveData.filter(s => s.date.startsWith(sel)) : rawArchiveData;
            } else { filtered = rawArchiveData; }
            if (window.statusFilter) { filtered = filtered.filter(s => s.status === window.statusFilter); }
            }

            let p=0, a=0, l=0;
            filtered.forEach(s => {
                if(s.status === 'Present') p++;
                else if(s.status === 'Absent') a++;
                else if(s.status === 'Leave') l++;
            });
            const total = p + a + l;
            const rate = total > 0 ? Math.round((p / total) * 100) : 0;

            const titleEl = document.getElementById('archive-month-title');
            if(titleEl) {
                titleEl.innerText = currentArchiveFilter === 'all' ? 'All Time' : currentArchiveFilter === 'week' ? 'This Week' : now.toLocaleString('default', { month: 'long', year: 'numeric' });
                document.getElementById('archive-rate-text').innerText = rate + '%';
                document.getElementById('archive-progress-bar').style.width = rate + '%';
                document.getElementById('stat-present').innerText = p;
                document.getElementById('stat-absent').innerText = a;
                document.getElementById('stat-leave').innerText = l;
            }

            document.getElementById('student-archive-list').innerHTML = filtered.map(s => {
                const d = new Date(s.date);
                const dayName = d.toLocaleDateString('en-US', { weekday: 'short' });
                const dayNum = d.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
                const yearNum = d.getFullYear();
                
                let dotColor, bgColor, textColor;
                if(s.status === 'Present') { dotColor = 'bg-emerald-500'; bgColor = 'bg-[rgba(34,197,94,0.15)]'; textColor = 'text-[#22C55E]'; }
                else if(s.status === 'Absent') { dotColor = 'bg-rose-500'; bgColor = 'bg-[rgba(239,68,68,0.15)]'; textColor = 'text-[#EF4444]'; }
                else { dotColor = 'bg-amber-500'; bgColor = 'bg-[rgba(245,158,11,0.15)]'; textColor = 'text-[#F59E0B]'; }

                return `
                <div class="flex justify-between items-center bg-white border border-black/5 rounded-[14px] p-4 shadow-sm">
                    <div class="flex items-center gap-4">
                        <div class="w-2.5 h-2.5 rounded-full ${dotColor} shadow-sm"></div>
                        <div>
                            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">${dayName}</p>
                            <h4 class="text-sm font-black text-slate-800">${dayNum}  ${yearNum}</h4>
                        </div>
                    </div>
                    <span class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${bgColor} ${textColor}">${s.status}</span>
                </div>`;
            }).join('') || '<p class="text-center text-xs py-10 font-bold text-slate-500">No records in this period.</p>';
        }

        
        
        
        
        /* Vault Function Removed */


        
        async function loadIntel() {
            const container = document.getElementById('intel-view');
            if(!container) return;
            const res = await fetch('/api/students-marking');
            const data = await res.json();
            const total = data.students.length;
            const leaves = data.students.filter(s => s.on_leave > 0).length;

            container.innerHTML = `
                <div class="space-y-6 animate-fade-in pb-20 w-full px-2">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="glass-card bg-[#1B4332] text-white p-6 border-none shadow-xl rounded-3xl">
                            <p class="text-[10px] font-black opacity-70 uppercase tracking-widest">Total Students</p>
                            <h2 class="text-4xl font-black">${total}</h2>
                        </div>
                        <div class="glass-card bg-amber-500 text-white p-6 border-none shadow-xl rounded-3xl">
                            <p class="text-[10px] font-black opacity-70 uppercase tracking-widest">On Leave</p>
                            <h2 class="text-4xl font-black">${leaves}</h2>
                        </div>
                    </div>
                    <div class="glass-card p-5 bg-white shadow-lg border-2 border-[#1B4332]/5 rounded-3xl">
                        <label class="text-xs font-black text-[#1B4332] uppercase mb-3 block">Select Student Record</label>
                        <select onchange="fetchStudentDeepStats(this.value)" class="w-full p-4 rounded-2xl border-none bg-gray-100 text-base font-bold shadow-inner outline-none">
                            <option value="">Choose Student...</option>
                            ${data.students.map(s => `<option value="${s.id}">${s.full_name} s/o ${s.father_name}</option>`).join('')}
                        </select>
                    </div>
                    <div id="intel-details-area" class="w-full min-h-[300px]">
                        <div class="flex flex-col items-center justify-center py-20 opacity-50">
                            <div class="text-8xl">💎</div>
                            <p class="font-black uppercase mt-4 tracking-tighter text-lg text-center">Detailed Analytics</p>
                        </div>
                    </div>
                </div>`;
        }

        async function fetchStudentDeepStats(sid) {
            if(!sid) return;
            const area = document.getElementById('intel-details-area');
            area.innerHTML = '<div class="flex justify-center py-20"><div class="animate-spin h-12 w-12 border-4 border-[#1B4332] border-t-transparent rounded-full"></div></div>';
            const res = await fetch('/api/student-detailed-stats/' + sid);
            const data = await res.json();
            const s = data.stats;
            const perc = s.total_days > 0 ? Math.round((s.presents / s.total_days) * 100) : 0;

            area.innerHTML = `
                <div class="space-y-5 animate-slide-up w-full">
                    <div class="glass-card p-8 bg-gradient-to-br from-[#1B4332] to-[#081C15] text-white border-none shadow-2xl rounded-[2rem] relative overflow-hidden">
                        <div class="relative z-10">
                            <p class="text-xs font-black opacity-60 uppercase tracking-widest">Attendance Performance</p>
                            <h2 class="text-6xl font-black my-2">${perc}%</h2>
                            <div class="w-full bg-white/10 h-3 rounded-full overflow-hidden mt-4">
                                <div class="bg-white h-full" style="width:${perc}%"></div>
                            </div>
                            <p class="text-xs mt-4 font-bold italic">${perc >= 75 ? '🟢 Meeting Criteria' : '🔴 Low Attendance'}</p>
                        </div>
                        <div class="absolute right-[-10px] bottom-[-20px] text-[10rem] opacity-5">💎</div>
                    </div>
                    <div class="grid grid-cols-3 gap-3">
                        <div class="glass-card text-center py-6 bg-green-50 rounded-3xl">
                            <h4 class="text-3xl font-black text-green-700">${s.presents}</h4>
                            <p class="text-[10px] font-black text-gray-400 uppercase">Presents</p>
                        </div>
                        <div class="glass-card text-center py-6 bg-red-50 rounded-3xl">
                            <h4 class="text-3xl font-black text-red-700">${s.absents}</h4>
                            <p class="text-[10px] font-black text-gray-400 uppercase">Absents</p>
                        </div>
                        <div class="glass-card text-center py-6 bg-amber-50 rounded-3xl">
                            <h4 class="text-3xl font-black text-amber-700">${s.leaves}</h4>
                            <p class="text-[10px] font-black text-gray-400 uppercase">Leaves</p>
                        </div>
                    </div>
                    <div class="glass-card p-0 overflow-hidden bg-white shadow-xl rounded-[2rem]">
                        <div class="bg-gray-50 p-5 border-b"><h4 class="text-xs font-black text-gray-500 uppercase">Recent Attendance Log</h4></div>
                        <div class="divide-y divide-gray-50">
                            ${data.history.map(h => `
                                <div class="flex justify-between items-center p-5">
                                    <div class="flex items-center gap-4">
                                        <div class="w-3 h-3 rounded-full ${h.status === 'Present' ? 'bg-green-500' : h.status === 'Leave' ? 'bg-amber-500' : 'bg-red-500'}"></div>
                                        <span class="text-sm font-black text-gray-800">${h.date}</span>
                                    </div>
                                    <span class="text-[10px] font-black px-4 py-1.5 rounded-full ${h.status === 'Present' ? 'bg-green-100 text-green-700' : h.status === 'Leave' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}">${h.status}</span>
                                </div>`).join('')}
                        </div>
                    </div>
                </div>`;
        }
async function markDiariesAsRead() {
        try {
            const res = await fetch('/api/diary/unread-status');
            const data = await res.json();
            if(data.latest_id) {
                localStorage.setItem('diary_last_seen_id', data.latest_id);
                const badge = document.getElementById('diary-badge');
                if(badge) badge.classList.add('hidden');
            }
        } catch(e) { console.error("Mark Read Error:", e); }
    }

    setInterval(updateDiaryBadge, 60000); // Check every 1 minute
    document.addEventListener('DOMContentLoaded', updateDiaryBadge);
</script>



<style>
    #master-viewer { transition: opacity 0.3s ease; }
    .viewer-btn { background: rgba(255,255,255,0.1); backdrop-filter: blur(5px); border-radius: 50%; width: 50px; height: 50px; display: flex; items-center; justify-content: center; color: white; transition: all 0.2s; }
    .viewer-btn:hover { background: rgba(255,255,255,0.2); transform: scale(1.1); }

        /* Sexy Toast Styles */
        #toast-container { position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 100000; width: 90%; max-width: 400px; pointer-events: none; }
        .toast-msg { background: rgba(15, 23, 42, 0.95); color: white; padding: 16px 20px; border-radius: 20px; margin-bottom: 10px; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2); display: flex; items-center; justify-content: center; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); animation: toast-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .toast-success { border-bottom: 4px solid #10b981; }
        .toast-error { border-bottom: 4px solid #ef4444; }
        .toast-warning { border-bottom: 4px solid #f59e0b; }
        @keyframes toast-in { from { opacity: 0; transform: translateY(-100%) scale(0.9); } to { opacity: 1; transform: translateY(0) scale(1); } }
        .toast-out { animation: toast-out 0.3s ease forwards !important; }
        @keyframes toast-out { to { opacity: 0; transform: translateY(-20px) scale(0.95); } }

    
        @keyframes zoom-in { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
        .animate-zoom-in { animation: zoom-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
        .net-status { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .net-online { background: #10b981; box-shadow: 0 0 10px #10b981; }
        .net-offline { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
        .sync-badge { position: absolute; top: -5px; right: 10px; background: #ef4444; color: white; font-size: 8px; padding: 2px 5px; border-radius: 10px; font-weight: 900; }


    
        .axis-input {
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 0 !important;
            color: white !important;
            padding: 12px 0 !important;
            transition: all 0.3s ease;
        }
        .axis-input:focus {
            border-bottom: 1px solid #6FFFE9 !important;
            outline: none !important;
            box-shadow: 0 4px 10px -5px rgba(111, 255, 233, 0.2);
        }
        .tab-text {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.2em;
            color: rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        }
        .tab-active {
            color: #6FFFE9 !important;
        }
        .tab-indicator {
            height: 2px;
            background: #6FFFE9;
            width: 100%;
            margin-top: 4px;
            box-shadow: 0 0 8px #6FFFE9;
        }
    
    
        
        .saas-card:active { transform: scale(0.95); }
        
        .no-scrollbar::-webkit-scrollbar { display: none; }
    
    
        .leave-error-blink { 
            border: 3px solid #ef4444 !important; 
            animation: error-pulse 0.8s infinite alternate;
        }
        @keyframes error-pulse { 
            from { border-color: #ef4444; box-shadow: 0 0 5px #ef4444; } 
            to { border-color: #fca5a5; box-shadow: 0 0 20px #ef4444; } 
        }
</style>

<div id="master-viewer" class="hidden fixed inset-0 z-[10000] bg-black/95 flex flex-col items-center justify-center">
    <button onclick="closeMasterViewer()" class="absolute top-6 right-6 text-white text-4xl font-light hover:text-amber-500">&times;</button>
    
    <div class="relative w-full max-w-4xl px-12 flex items-center justify-center">
        <button id="v-prev" onclick="changeMedia(-1)" class="viewer-btn absolute left-2 text-2xl">❮</button>
        
        <div class="w-full flex items-center justify-center overflow-hidden rounded-2xl shadow-2xl bg-black/20" style="height: 70vh;">
            <img id="v-img" src="" class="max-w-full max-h-full object-contain hidden border border-white/10">
            <div id="v-file" class="hidden text-center text-white">
                <div class="text-8xl mb-4">📁</div>
                <p class="font-bold text-lg">Document / File</p>
                <p class="text-xs opacity-50">Cannot be previewed</p>
            </div>
        </div>

        <button id="v-next" onclick="changeMedia(1)" class="viewer-btn absolute right-2 text-2xl">❯</button>
    </div>

    <div class="mt-6 flex flex-col items-center gap-3">
        <span id="v-count" class="text-white/40 text-[10px] font-black tracking-widest uppercase">File 1 of 1</span>
        <div class="flex gap-4">
            <a id="v-download" href="#" download class="bg-amber-500 hover:bg-amber-600 text-black font-black px-10 py-3 rounded-full text-xs shadow-lg transition-all flex items-center gap-2">
                <span>📥 DOWNLOAD FILE</span>
            </a>
        </div>
    </div>
</div>




<script>
    var mediaGallery = [];
    var mediaIdx = 0;

    window.viewMedia = function(urls, index) {
        console.log("Opening Viewer with:", urls, "Index:", index);
        if(!urls) return alert("No files found!");
        
        mediaGallery = urls.split(',').map(u => u.trim());
        mediaIdx = parseInt(index);
        
        const viewer = document.getElementById('master-viewer');
        if(viewer) {
            viewer.classList.remove('hidden');
            updateViewer();
        } else {
            console.error("Viewer element not found!");
        }
    };

    window.updateViewer = function() {
        let path = mediaGallery[mediaIdx];
        if(!path.startsWith('/')) path = '/' + path;
        
        const fullUrl = window.location.origin + path;
        const img = document.getElementById('v-img');
        const file = document.getElementById('v-file');
        const dl = document.getElementById('v-download');
        const count = document.getElementById('v-count');

        img.classList.add('hidden');
        file.classList.add('hidden');
        
        document.getElementById('v-prev').classList.toggle('hidden', mediaGallery.length <= 1);
        document.getElementById('v-next').classList.toggle('hidden', mediaGallery.length <= 1);

        count.innerText = `FILE ${mediaIdx + 1} OF ${mediaGallery.length}`;
        dl.href = fullUrl;

        const ext = path.split('.').pop().toLowerCase();
        const images = ['jpg', 'jpeg', 'png', 'gif', 'webp'];

        if(images.includes(ext)) {
            img.src = fullUrl;
            img.onload = () => img.classList.remove('hidden');
            img.onerror = () => {
                img.classList.add('hidden');
                file.classList.remove('hidden');
            };
        } else {
            file.classList.remove('hidden');
        }
    };

    window.changeMedia = function(dir) {
        mediaIdx = (mediaIdx + dir + mediaGallery.length) % mediaGallery.length;
        updateViewer();
    };

    window.closeMasterViewer = function() {
        document.getElementById('master-viewer').classList.add('hidden');
        document.getElementById('v-img').src = '';
    };
</script>


<script>
    let tempFileStorage = [];

    document.addEventListener('change', function(e) {
        if(e.target && e.target.id === 'diary-files') {
            const newFiles = Array.from(e.target.files);
            newFiles.forEach(f => {
                // Duplicate check
                if(!tempFileStorage.some(existing => existing.name === f.name && existing.size === f.size)) {
                    tempFileStorage.push(f);
                }
            });
            updateAttachUI();
            
            // Critical: Sync with the actual input for the original submitDiary function
            syncFilesToInput();
        }
    });

    function updateAttachUI() {
        const zone = document.getElementById('attach-preview-zone');
        const list = document.getElementById('attach-list');
        const count = document.getElementById('attach-count');
        
        if(tempFileStorage.length > 0) {
            zone.classList.remove('hidden');
            count.innerText = `${tempFileStorage.length} Files Attached`;
            list.innerHTML = '';
            tempFileStorage.forEach((f, i) => {
                list.innerHTML += `<span class="bg-white border border-blue-100 text-blue-600 text-[8px] font-bold px-2 py-1 rounded shadow-sm">📎 ${f.name}</span>`;
            });
        } else {
            zone.classList.add('hidden');
        }
    }

    function syncFilesToInput() {
        const input = document.getElementById('diary-files');
        const dataTransfer = new DataTransfer();
        tempFileStorage.forEach(file => dataTransfer.items.add(file));
        input.files = dataTransfer.files; // This updates the original input
    }

    window.clearAttaches = function() {
        tempFileStorage = [];
        document.getElementById('diary-files').value = '';
        updateAttachUI();
    };
</script>


<script>


window.updateLeaveStatus = async function(id, status) {
    if(!(await askUser(`Confirm ${status.toUpperCase()}?`))) return;
    try {
        const res = await fetch('/api/leave/action', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id, status })
        });
        const result = await res.json();
        if(result.success) {
            alert("Leave " + status + " successfully!");
            renderLeaveHistory('Pending');
        } else {
            alert("Error: " + result.error);
        }
    } catch(e) {
        alert("Action failed. Check connection.");
    }
};

window.openLeaveHub = function() {
    showTab('leave');
    const area = document.getElementById('leave-content-area');
    const role = "{{ user.role }}";
    
    if(role === 'Student') {
        area.innerHTML = `
            <div id="leave-menu" class="flex flex-col gap-3 animate-fade-in">
                <div onclick="renderLeaveApply()" class="bg-white p-4 rounded-2xl border border-black/5 flex items-center shadow-sm active:scale-95 transition-all cursor-pointer">
                    <div class="w-12 h-12 rounded-xl bg-[#E8EEF7] text-[#2F80ED] flex items-center justify-center mr-4 shrink-0">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </div>
                    <div class="flex-1">
                        <h4 class="font-bold text-[#0F2A44] text-sm">Apply Leave</h4>
                        <p class="text-[11px] text-gray-500 mt-0.5">Create a new leave request</p>
                    </div>
                </div>
                
                <div onclick="renderLeaveHistory()" class="bg-white p-4 rounded-2xl border border-black/5 flex items-center shadow-sm active:scale-95 transition-all cursor-pointer">
                    <div class="w-12 h-12 rounded-xl bg-gray-50 text-gray-600 flex items-center justify-center mr-4 shrink-0 border border-gray-100">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <div class="flex-1">
                        <h4 class="font-bold text-[#0F2A44] text-sm">My Requests</h4>
                        <p class="text-[11px] text-gray-500 mt-0.5">Track approval status</p>
                    </div>
                </div>
            </div>
            <div id="leave-dynamic-inner" class="hidden animate-slide-up"></div>`;
            
    } else {
        area.innerHTML = `
            <div id="leave-menu" class="flex flex-col gap-6 animate-fade-in">
                <div class="bg-[#0F2A44] p-6 rounded-b-[2.5rem] -mx-4 -mt-4 text-white shadow-lg mb-2">
                    <h2 class="text-3xl font-black tracking-tight">Leave Center</h2>
                    <div class="flex items-center gap-2 mt-2 opacity-90">
                        <span class="text-[10px] font-black uppercase tracking-widest bg-blue-500/30 px-2 py-1 rounded-md border border-blue-400/20">Class {{ user.assigned_class }}-{{ user.assigned_section }}</span>
                        <span class="text-[10px] font-black uppercase tracking-widest bg-white/10 px-2 py-1 rounded-md">{{ user.assigned_wing }} Wing</span>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-3">
                    <div onclick="renderLeaveHistory('History')" class="bg-white p-3 rounded-2xl border border-gray-100 shadow-sm text-center active:scale-95 transition-all cursor-pointer">
                        <p class="text-[9px] font-black text-gray-400 uppercase">Today</p>
                        <p class="text-xl font-black text-[#0F2A44] mt-1" id="stat-today">0</p>
                    </div>
                    <div onclick="renderLeaveHistory('Pending')" class="bg-amber-50 p-3 rounded-2xl border border-amber-100 shadow-sm text-center active:scale-95 transition-all cursor-pointer">
                        <p class="text-[9px] font-black text-amber-600 uppercase">Waiting</p>
                        <p id="stat-pending" class="text-xl font-black text-amber-700 mt-1">0</p>
                    </div>
                    <div onclick="renderLeaveHistory('Approved')" class="bg-blue-50 p-3 rounded-2xl border border-blue-100 shadow-sm text-center active:scale-95 transition-all cursor-pointer">
                        <p class="text-[9px] font-black text-blue-600 uppercase">Approved</p>
                        <p class="text-xl font-black text-blue-700 mt-1" id="stat-done">0</p>
                    </div>
                </div>

                <div onclick="renderLeaveHistory('Pending')" class="relative bg-[#0F2A44] p-5 rounded-3xl flex items-center shadow-xl active:scale-95 transition-all cursor-pointer overflow-hidden group">
                    <div class="absolute right-0 top-0 bottom-0 w-32 bg-blue-500/10 skew-x-12 translate-x-10"></div>
                    <div class="w-12 h-12 rounded-2xl bg-blue-500 text-white flex items-center justify-center mr-4 shrink-0 shadow-lg">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                    </div>
                    <div class="flex-1 z-10">
                        <h4 class="font-black text-white text-sm uppercase tracking-tight">Review Leave Requests</h4>
                        <p class="text-blue-200 text-[11px] mt-0.5 font-bold"><span id="card-leave-badge-text">0</span> students waiting for approval</p>
                    </div>
                    <div class="text-blue-400 z-10">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M13 7l5 5-5 5M6 7l5 5-5 5"></path></svg>
                    </div>
                </div>

                <div onclick="renderLeaveHistory('History')" class="bg-white p-5 rounded-3xl border border-gray-100 flex items-center shadow-sm active:scale-95 transition-all cursor-pointer group">
                    <div class="w-12 h-12 rounded-2xl bg-gray-50 text-gray-400 flex items-center justify-center mr-4 shrink-0 group-hover:bg-gray-100 transition-colors">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <div class="flex-1">
                        <h4 class="font-black text-[#0F2A44] text-sm uppercase tracking-tight">Leave Records</h4>
                        <p class="text-[11px] text-gray-400 mt-0.5 font-medium">View past decisions & history</p>
                    </div>
                    <div class="text-gray-300">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </div>
                </div>
            </div>
            <div id="leave-dynamic-inner" class="hidden animate-slide-up"></div>`;
        
        // Sync badge and local stats
        setTimeout(() => {
            updateLeaveBadge();
            const b = document.getElementById('card-leave-badge');
            if(b) document.getElementById('stat-pending').innerText = b.innerText;
        }, 150);
    }\n};


window.updateFileName = function() {
    const fileInput = document.getElementById('l-file');
    const file = fileInput.files[0];
    const span = document.querySelector('label span') || document.querySelector('#l-file').previousElementSibling;
    
    if(file && span) {
        span.innerHTML = `
            <div class="flex flex-col items-center gap-1">
                <span class="text-[#1E3A8A]">📎 ${file.name}</span>
                <span onclick="event.preventDefault(); event.stopPropagation(); removeFile();" class="text-[9px] text-rose-500 font-black border-b border-rose-200">REMOVE FILE</span>
            </div>
        `;
    }
};

window.removeFile = function() {
    const fileInput = document.getElementById('l-file');
    const span = document.querySelector('label span') || document.querySelector('#l-file').previousElementSibling;
    fileInput.value = ""; // Clear file
    if(span) {
        span.innerHTML = "Tap to upload document";
        span.classList.remove('text-[#1E3A8A]');
    }
};
window.renderLeaveApply = function() { 
    document.getElementById('leave-menu').classList.add('hidden');
    const inner = document.getElementById('leave-dynamic-inner');
    inner.classList.remove('hidden');
    
    inner.innerHTML = `
        <button onclick="openLeaveHub()" class="mb-5 flex items-center gap-2 text-[11px] font-bold text-[#1E3A8A] bg-blue-50 px-4 py-2 rounded-full active:scale-90 transition-all">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"></path></svg>
            BACK TO MENU
        </button>

        <div class="space-y-4 pb-10">
            <div class="bg-white p-5 rounded-[22px] border-l-[6px] border-[#1E3A8A] shadow-sm space-y-4">
                <div class="flex items-center justify-between">
                    <h4 class="text-[10px] font-black text-[#1E3A8A] uppercase tracking-[1.5px]">Leave Duration</h4>
                    <span id="days-counter" class="text-[11px] font-bold text-[#1E3A8A] bg-blue-50 px-3 py-1 rounded-lg">0 Days</span>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1">
                        <p class="text-[9px] font-bold text-gray-400 uppercase ml-1">Start Date</p>
                        <input type="date" id="l-start" onchange="calculateDays()" class="w-full p-4 bg-[#F1F5F9] rounded-xl text-xs font-bold border-none focus:ring-2 ring-[#1E3A8A]/20 transition-all">
                    </div>
                    <div class="space-y-1">
                        <p class="text-[9px] font-bold text-gray-400 uppercase ml-1">End Date</p>
                        <input type="date" id="l-end" onchange="calculateDays()" class="w-full p-4 bg-[#F1F5F9] rounded-xl text-xs font-bold border-none focus:ring-2 ring-[#1E3A8A]/20 transition-all">
                    </div>
                </div>
            </div>

            <div class="bg-white p-5 rounded-[22px] shadow-sm border border-gray-100 space-y-3">
                <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-[1.5px]">Reason for Leave</h4>
                <textarea id="l-reason" placeholder="Explain why you are applying..." class="w-full p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-sm min-h-[120px] focus:ring-2 ring-[#1E3A8A]/10 transition-all outline-none"></textarea>
            </div>

            <div class="bg-white p-5 rounded-[22px] shadow-sm border border-gray-100 space-y-3">
                <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-[1.5px]">Document (Optional)</h4>
                <label class="flex flex-col items-center justify-center w-full p-6 border-2 border-dashed border-[#CBD5E1] rounded-xl bg-[#F8FAFC] cursor-pointer active:scale-[0.98] transition-all">
                    <svg class="w-6 h-6 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    <span class="text-[11px] font-bold text-gray-500">Tap to upload document</span>
                    <input type="file" id="l-file" class="hidden" onchange="updateFileName()">
                </label>
            </div>

            <button onclick="submitLeaveRequest()" id="l-sub-btn" class="w-full bg-[#1E3A8A] text-white py-5 rounded-[22px] font-black text-xs uppercase tracking-[2px] shadow-lg shadow-blue-900/10 active:scale-95 transition-all">
                🚀 Submit Request
            </button>
        </div>
    `;
};

// UX Helper: Calculate Days Difference
window.calculateDays = function() {
    const start = document.getElementById('l-start').value;
    const end = document.getElementById('l-end').value;
    const counter = document.getElementById('days-counter');
    
    if (start && end) {
        const d1 = new Date(start);
        const d2 = new Date(end);
        const diff = Math.ceil((d2 - d1) / (1000 * 60 * 60 * 24)) + 1;
        
        if (diff > 0) {
            counter.innerText = diff + (diff === 1 ? ' Day' : ' Days');
            counter.className = "text-[11px] font-bold text-[#1E3A8A] bg-blue-50 px-3 py-1 rounded-lg";
        } else {
            counter.innerText = "Invalid Dates";
            counter.className = "text-[11px] font-bold text-red-600 bg-red-50 px-3 py-1 rounded-lg";
        }
    }
};
\n\n


window.showLeaveDetails = function(l) {
    const role = "{{ user.role }}"; // Force local role definition
    // 1. Path Clean-up & Encoding
    let rawPath = l.attachment ? l.attachment.replace(/^\/+/, '') : '';
    if (rawPath && !rawPath.startsWith('static/')) {
        rawPath = 'static/' + rawPath;
    }
    
    // Professional URL Encoding to handle special chars like ] or spaces
    const encodedPath = rawPath.split('/').map(part => encodeURIComponent(part)).join('/');
    const finalUrl = '/' + encodedPath;

    const attachmentHtml = l.attachment ? `
        <div class="mb-8 p-5 bg-[#1B3A57]/5 rounded-[30px] border border-[#1B3A57]/10 flex items-center justify-between">
            <div>
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Document</p>
                <p class="text-xs font-black text-[#1B3A57]">Attached File Found</p>
            </div>
            <button onclick="handleFileView('${finalUrl}')" 
                    class="bg-[#1B3A57] text-white text-[10px] font-black px-5 py-3 rounded-2xl active:scale-90 transition-all shadow-md shadow-[#1B3A57]/20">
                VIEW ATTACHMENT
            </button>
        </div>
    ` : '';

    const drawer = document.createElement('div');
    drawer.className = "fixed inset-0 bg-black/60 z-[100] flex items-end animate-in fade-in duration-300 backdrop-blur-sm";
    drawer.innerHTML = `
        <div class="bg-white w-full rounded-t-[40px] p-8 pb-12 animate-in slide-in-from-bottom duration-500 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div class="w-12 h-1.5 bg-gray-200 rounded-full mx-auto mb-8"></div>
            <div class="flex justify-between items-start mb-6">
                <div>
                    <span class="text-[10px] font-black px-3 py-1 rounded-full uppercase bg-[#1B3A57]/5 text-[#1B3A57] border border-[#1B3A57]/10 mb-2 inline-block">${l.status}</span>
                    <h3 class="text-2xl font-black text-[#1B3A57] leading-tight">${l.reason}</h3>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-8">
                <div class="bg-gray-50 p-5 rounded-[30px] border border-gray-100">
                    <p class="text-[9px] font-bold text-gray-400 uppercase mb-1">Start Date</p>
                    <p class="font-black text-[#1B3A57]">${l.start_date}</p>
                </div>
                <div class="bg-gray-50 p-5 rounded-[30px] border border-gray-100">
                    <p class="text-[9px] font-bold text-gray-400 uppercase mb-1">End Date</p>
                    <p class="font-black text-[#1B3A57]">${l.end_date}</p>
                </div>
            </div>
            ${attachmentHtml}
            ${(role === 'Teacher' && ((l.status.trim() === 'Pending' || l.status.trim() === 'Pending ') || l.status === 'Offline')) ? `
                <div class="flex gap-3 mt-4">
                    <button onclick="handleLeaveAction(${l.id}, 'Approved', '${l.status}'); this.closest('.fixed').remove()" 
                            class="flex-1 bg-emerald-500 text-white font-black py-5 rounded-[30px] active:scale-95 transition-all shadow-lg shadow-emerald-500/20 uppercase tracking-widest text-[10px]">
                        Approve
                    </button>
                    <button onclick="handleLeaveAction(${l.id}, 'Rejected', '${l.status}'); this.closest('.fixed').remove()" 
                            class="flex-1 bg-rose-500 text-white font-black py-5 rounded-[30px] active:scale-95 transition-all shadow-lg shadow-rose-500/20 uppercase tracking-widest text-[10px]">
                        Reject
                    </button>
                </div>
                <button onclick="this.closest('.fixed').remove()" class="w-full mt-4 text-gray-400 font-bold text-[10px] uppercase tracking-widest">Dismiss</button>
            ` : `
                <button onclick="this.closest('.fixed').remove()" 
                        class="w-full bg-[#1B3A57] text-white font-black py-5 rounded-[30px] active:scale-95 transition-all shadow-lg shadow-[#1B3A57]/20 uppercase tracking-widest text-xs">
                    Close Details
                </button>
            `}
        </div>
    `;
    document.body.appendChild(drawer);
};

window.handleFileView = function(fullUrl) {
    const isPdf = fullUrl.toLowerCase().endsWith('.pdf');
    if (isPdf) {
        window.open(fullUrl, '_blank');
    } else {
        openImageLightbox(fullUrl);
    }
};

window.openImageLightbox = function(url) {
    const lb = document.createElement('div');
    lb.className = "fixed inset-0 bg-black/95 z-[200] flex items-center justify-center animate-in zoom-in duration-200 p-4";
    lb.innerHTML = `
        <button onclick="this.parentElement.remove()" class="absolute top-8 right-8 text-white p-4 z-[210] bg-white/10 rounded-full">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        <img src="${url}" class="max-w-full max-h-[85vh] object-contain shadow-2xl rounded-xl">
    `;
    document.body.appendChild(lb);
};

window.renderLeaveHistory = async function(filterMode = 'All', highlightId = null) {
    if(document.getElementById('leave-menu')) document.getElementById('leave-menu').classList.add('hidden');
    const inner = document.getElementById('leave-dynamic-inner');
    inner.classList.remove('hidden');

    // 1. Top Navigation & Filters
    inner.innerHTML = `
        <div class="flex items-center gap-4 mb-6">
            <button onclick="openLeaveHub()" class="p-2 bg-gray-100 rounded-full active:scale-90 transition-all">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
            </button>
            <h2 class="text-xl font-black text-[#1B3A57]">Leave History</h2>
        </div>
        
        <div class="flex gap-2 mb-6 overflow-x-auto pb-2 no-scrollbar">
            ${['All', 'Pending', 'Approved', 'Rejected'].map(f => `
                <button onclick="renderLeaveHistory('${f}')" 
                class="px-5 py-2 rounded-full text-xs font-bold transition-all whitespace-nowrap
                ${filterMode === f ? 'bg-[#1B3A57] text-white shadow-md' : 'bg-gray-100 text-gray-500'}">
                    ${f}
                </button>
            `).join('')}
        </div>
        <div id="leave-cards-container" class="space-y-4">
            <div class="flex justify-center py-10"><div class="animate-spin h-8 w-8 border-4 border-[#1B3A57] border-t-transparent rounded-full"></div></div>
        </div>`;

    try {
        const res = await fetch('/api/leave/list');
        const serverData = await res.json();
        let combinedData = Array.isArray(serverData) ? serverData : [];

        // Offline Data Fetch
        const offlinePending = await db.syncQueue.where('url').equals('/api/leave/submit').toArray();
        const mappedOffline = offlinePending.map(item => ({
            id: 'off-' + item.id,
            reason: item.body.reason,
            start_date: item.body.start_date,
            end_date: item.body.end_date,
            status: 'Offline',
            is_offline: true
        }));

        combinedData = [...mappedOffline, ...combinedData];

        // Filtering Logic
        if (filterMode !== 'All') {
            combinedData = combinedData.filter(l => l.status === filterMode || (filterMode === 'Pending' && l.status === 'Offline'));
        }

        const container = document.getElementById('leave-cards-container');
        if (combinedData.length === 0) {
            container.innerHTML = `<div class="text-center py-10 text-gray-400 font-bold">No ${filterMode} requests found</div>`;
            return;
        }

        // 2. Render Cards (The Google UX Way)
        container.innerHTML = combinedData.map(l => {
            const statusStyles = {
                'Approved': 'bg-emerald-50 text-emerald-600 border-emerald-100',
                'Pending': 'bg-amber-50 text-amber-600 border-amber-100',
                'Offline': 'bg-blue-50 text-blue-600 border-blue-100',
                'Rejected': 'bg-rose-50 text-rose-600 border-rose-100'
            };
            const sClass = statusStyles[l.status] || 'bg-gray-50 text-gray-600';

            return `
            <div onclick="showLeaveDetails(${JSON.stringify(l).replace(/"/g, '&quot;')})" 
                 class="bg-white p-4 rounded-3xl border-l-[6px] border-[#1B3A57] shadow-sm active:scale-[0.98] transition-all flex justify-between items-center cursor-pointer ${l.id == highlightId ? 'leave-error-blink' : ''}" id="leave-card-${l.id}">
                <div class="flex-1 pr-4">
                    <h4 class="font-bold text-[#1B3A57] text-sm truncate w-48">${l.reason}</h4>
                    <p class="text-[10px] font-medium text-gray-400 mt-1">${l.start_date} — ${l.end_date}</p>
                </div>
                <div class="flex flex-col items-end gap-2">
                    <span class="text-[9px] font-black px-3 py-1 rounded-full uppercase border ${sClass}">
                        ${l.status}
                    </span>
                    <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"/></svg>
                </div>
            </div>`;
        }).join('');

    } catch (err) {
        document.getElementById('leave-cards-container').innerHTML = `<div class="text-center py-10 font-black text-rose-600 uppercase">Load Failed</div>`;
    }
};

// 3. Detail View (Bottom Sheet Style)

const Object_from_iterable = (iter) => { const obj = {}; for (const [k, v] of iter) { if(k!=="attachment") obj[k] = v; } return obj; };
window.submitLeaveRequest = async function() {
    const btn = document.getElementById('l-sub-btn');
    const start = document.getElementById('l-start').value;
    const end = document.getElementById('l-end').value;
    const reason = document.getElementById('l-reason').value;
    const file = document.getElementById('l-file').files[0];

    if(!start || !end || !reason) return alert("Please fill all required fields!");

    // INTERNET CHECK FOR ATTACHMENT
    if (file && !navigator.onLine) {
        if(!confirm("Internet is required for attachments. Submit text-only locally?")) {
            return;
        }
    }

    // OFFLINE LOGIC (TEXT ONLY)
    if (!navigator.onLine) {
        const offlineData = { start_date: start, end_date: end, reason: reason };
        try {
            btn.disabled = true;
            btn.innerText = "SAVING LOCALLY...";
            await saveOffline('/api/leave/submit', 'POST', offlineData);
            alert("📡 Saved Offline! It will sync when you are online.");
            renderLeaveHistory();
        } catch (e) {
            alert("❌ Offline Save Failed: " + e.message);
        } finally {
            btn.disabled = false;
            btn.innerText = "🚀 Submit Request";
        }
        return;
    }

    // ONLINE LOGIC (WITH ATTACHMENT)
    const fd = new FormData();
    fd.append('start_date', start);
    fd.append('end_date', end);
    fd.append('reason', reason);
    if(file) fd.append('attachment', file);

    try {
        btn.disabled = true;
        btn.innerText = "PROCESSING...";
        const res = await fetch('/api/leave/submit', {method:'POST', body:fd});
        const result = await res.json();
        
        if(result.success) {
            showToast("🚀 Leave Submitted Successfully!", "success");
            renderLeaveHistory();
        } else if(result.conflict_id) {
            showToast(result.error, "error");
            renderLeaveHistory('Approved', result.conflict_id);
        } else {
            throw new Error(result.error || "Submission failed");
        }
    } catch (e) {
        alert("❌ Error: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerText = "🚀 Submit Request";
    }
};

window.handleLeaveAction = async function(id, status, currentFilter) {
    if(!(await askUser('Are you sure you want to proceed?'))) return;
    await fetch('/api/leave/action', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({id, status})
    });
    renderLeaveHistory(currentFilter);
    updateLeaveBadge();
};
</script>

<script>

window.viewLeaveFile = function(url) {
    const masterModal = document.getElementById('master-viewer');
    if(!masterModal) return alert("Viewer not found!");

    masterModal.classList.remove('hidden');

    const img = document.getElementById('v-img');
    const fileDiv = document.getElementById('v-file');
    const downloadBtn = document.getElementById('v-download');
    
    // Reset Views
    if(img) img.classList.add('hidden');
    if(fileDiv) fileDiv.classList.add('hidden');
    
    // Hide nav arrows for single attachment
    if(document.getElementById('v-prev')) document.getElementById('v-prev').style.display = 'none';
    if(document.getElementById('v-next')) document.getElementById('v-next').style.display = 'none';

    const isImg = url.match(/\\.(jpg|jpeg|png|gif|webp)$/i);
    const path = url.startsWith('/') ? url : '/' + url;
    
    if(isImg) {
        if(img) { img.src = path; img.classList.remove('hidden'); }
    } else {
        if(fileDiv) fileDiv.classList.remove('hidden');
    }
    
    if(downloadBtn) { downloadBtn.href = path; }
};

</script>
<script>


window.updateLeaveBadge = async function() {
    try {
        const res = await fetch('/api/leave/stats');
        const data = await res.json();
        
        // Home Badge
        const mb = document.getElementById('leave-badge');
        if(mb) { mb.innerText = data.pending; data.pending > 0 ? mb.classList.remove('hidden') : mb.classList.add('hidden'); }

        // Grid Stats
        const st = document.getElementById('stat-today');
        const sp = document.getElementById('stat-pending');
        const sd = document.getElementById('stat-done');
        if(st) st.innerText = data.today;
        if(sp) sp.innerText = data.pending;
        if(sd) sd.innerText = data.done;

        // Card Text
        const ct = document.getElementById('card-leave-badge-text');
        if(ct) ct.innerText = data.pending;
    } catch(e) { console.error(e); }
};


// Auto-run on load
document.addEventListener('DOMContentLoaded', updateLeaveBadge);
// Update when returning home
const originalShowTab = window.showTab;
window.showTab = function(id) {
    if(originalShowTab) originalShowTab(id);
    if(id === 'home') updateLeaveBadge();
};

</script>
<script>

window.showToast = function(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    
    // Auto-detect type based on common emojis if not provided
    let toastClass = 'toast-success';
    if(msg.includes('❌') || msg.includes('Error') || msg.includes('Failed')) toastClass = 'toast-error';
    if(msg.includes('⚠️') || msg.includes('Ghalti')) toastClass = 'toast-warning';
    if(type === 'error') toastClass = 'toast-error';

    toast.className = `toast-msg ${toastClass}`;
    toast.innerHTML = `<span>${msg}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 10000);
};

// Global Override: Replace default alert with our sexy toast
window.alert = function(msg) {
    window.showToast(msg);
};

</script>
<script>

window.askUser = function(message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('custom-confirm');
        const msgEl = document.getElementById('confirm-msg');
        const yesBtn = document.getElementById('confirm-yes');
        const noBtn = document.getElementById('confirm-no');
        
        msgEl.innerText = message;
        modal.classList.remove('hidden');
        
        const cleanup = (result) => {
            modal.classList.add('hidden');
            yesBtn.onclick = null;
            noBtn.onclick = null;
            resolve(result);
        };
        
        yesBtn.onclick = () => cleanup(true);
        noBtn.onclick = () => cleanup(false);
    });
};

</script>
<script src="/static/finalize.js"></script>
<script src="/static/marks.js"></script>
<script src="/static/marks_v3.js"></script>
<script src="/static/marks_v3.js">
window.openPfpMenu = () => document.getElementById('pfp-modal').classList.remove('hidden');
window.closePfpMenu = () => document.getElementById('pfp-modal').classList.add('hidden');

window.handlePfpUpload = async (input) => {
    if (!input.files || !input.files[0]) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
        const base64 = e.target.result;
        const res = await fetch('/api/update-profile-pic', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'upload', image: base64})
        });
        const data = await res.json();
        if(data.success) location.reload();
        else showToast("Failed to upload!", "error");
    };
    reader.readAsDataURL(input.files[0]);
};

window.removePfp = async () => {
    const res = await fetch('/api/update-profile-pic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'remove'})
    });
    const data = await res.json();
    if(data.success) location.reload();
    else showToast("Error removing photo", "error");
};

</script>

<script>
function openPfpMenu() { 
    const m = document.getElementById('pfp-modal');
    m.classList.remove('hidden'); m.classList.add('flex');
}
function closePfpMenu() { 
    const m = document.getElementById('pfp-modal');
    m.classList.add('hidden'); m.classList.remove('flex');
}
async function handlePfpUpload(input) {
    if (!input.files || !input.files[0]) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
        const res = await fetch('/api/update-profile-pic', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'upload', image: e.target.result})
        });
        if(res.ok) { window.location.href = window.location.pathname + '?t=' + Date.now(); } else { alert('Upload failed'); }
    };
    reader.readAsDataURL(input.files[0]);
}
async function removePfp() {
    const res = await fetch('/api/update-profile-pic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'remove'})
    });
    if(res.ok) { window.location.href = window.location.pathname + '?t=' + Date.now(); } else { alert('Upload failed'); }
}
// Close modal on click outside
window.onclick = (e) => { if(e.target.id == 'pfp-modal') closePfpMenu(); }
</script>

</body>
    <script>
        window.addEventListener("online", async () => {
            const pending = JSON.parse(localStorage.getItem("pending_sync") || "[]");
            if (pending.length > 0) {
                console.log("Internet back! Syncing " + pending.length + " items...");
                for (const item of pending) {
                    try {
                        await fetch(item.url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(item.body)});
                    } catch (e) { console.error("Sync failed for item", e); }
                }
                localStorage.removeItem("pending_sync");
                alert("✅ All offline marks have been synced to server!");
            }
        });
    </script>

<script>
// JS Cleaned for New Engine

    const res = await fetch('/api/teacher/save_marks_v2', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({exam_id: eid, sub_id: sid, total_marks: total_m, marks: marks})
    });
    
    if(result.status === 'success') { alert('DATA SAVED!'); showTab('marks-entry'); }
}

async function _old_load() {
    const eid = document.getElementById('exam-selector').value;
    const list = document.getElementById('teacher-assign-list');
    if(!eid || eid.includes('No')) return;
    list.innerHTML = '<div class="p-10 text-center text-gray-400 font-bold text-[10px]">FETCHING...</div>';
    try {
        const res = await fetch(`/api/teacher/assignments_v2/${eid}`);
        const data = await res.json();
        list.innerHTML = data.map(a => `
            <div class="glass-card flex items-center justify-between border-l-8 border-indigo-600 active:scale-95 transition-all">
                <div>
                    <span class="bg-indigo-100 text-indigo-700 text-[8px] font-black px-2 py-0.5 rounded uppercase">${a.sub_name}</span>
                    <h4 class="font-black text-gray-800 text-sm mt-1 uppercase">CLASS ${a.student_class}-${a.section} (${a.wing.toUpperCase()})</h4>
                </div>
                <button class="bg-indigo-600 text-white p-2 rounded-lg shadow-lg">➔</button>
            </div>`).join('') || '<div class="p-10 text-center text-gray-400 text-[10px]">NO DATA</div>';
    } catch(e) { list.innerHTML = '<div class="text-center text-red-500 font-bold">ERROR</div>'; }
}
</script>

</html>
    <script>
        window.addEventListener("online", async () => {
            const pending = JSON.parse(localStorage.getItem("pending_sync") || "[]");
            if (pending.length > 0) {
                console.log("Internet back! Syncing " + pending.length + " items...");
                for (const item of pending) {
                    try {
                        await fetch(item.url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(item.body)});
                    } catch (e) { console.error("Sync failed for item", e); }
                }
                localStorage.removeItem("pending_sync");
                alert("✅ All offline marks have been synced to server!");
            }
        });
    </script>
'''

# --- BACKEND ROUTES ---


@app.route('/app_logo')
def serve_app_logo():
    try:
        return send_file('static/logo.png', mimetype='image/png')
    except Exception:
        return "Logo not found", 404
    except FileNotFoundError:
        return send_file('static/logo.png', mimetype='image/png')
    return "", 404
    import os
    path = "/home/sami/Downloads/sami.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "", 404


@app.route('/api/school-logo')
def get_school_logo():
    try:
        return send_file('/home/sami/Music/logo.png', mimetype='image/png', max_age=0)
    except FileNotFoundError:
        return send_file('static/logo.png', mimetype='image/png')

@app.route('/')
def index():
    resp = make_response(render_template_string(HTML_TEMPLATE, logged_in='user' in session, user=session.get('user')))
    if not request.path.startswith('/static/'): resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    print(f'SAVE ATTEMPT -> EID: {data.get("eid")}, SID: {data.get("sid")}')
    uid, dob, role = str(data.get('uid', '')).strip(), str(data.get('dob', '')).strip(), data.get('role', 'Student')
    uid_int = int(uid) if uid.isdigit() else -1
    conn = sqlite3.connect(DB_PATH)
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
        u_dict['assigned_class'] = u_dict.get('assigned_class') or u_dict.get('student_class')
        u_dict['assigned_section'] = u_dict.get('assigned_section') or u_dict.get('student_section')
        u_dict['wing'] = u_dict.get('assigned_wing') or u_dict.get('wing')
        u_dict['is_class_teacher'] = u_dict.get('is_class_teacher', 0)
        
        
        
        
        
        # --- NEW: Fetch Subject Assignments for Teachers ---
        if role == "Teacher":
            t_id = u_dict.get('id')
            cur.execute("""
                SELECT 
                    COALESCE(s.name, 'Subject ' || sa.subject_id) AS name,
                    sa.student_class AS student_class, 
                    sa.section AS section, 
                    sa.wing AS wing
                FROM apsokara_subjectassignment sa
                LEFT JOIN apsokara_subject s ON sa.subject_id = s.id
                WHERE sa.teacher_id = ?""", (t_id,))
            rows = cur.fetchall()
            u_dict['assignments'] = [dict(r) for r in rows]
            # Debug: print(f"Assignments found: {u_dict['assignments']}")
        # ---------------------------------------------------




        
        session['user'] = {k: v for k, v in u_dict.items() if k not in ['bio', 'pfp_base64']}

        conn.close()
        return jsonify({"success": True})
    conn.close()
    return jsonify({"success": False})

@app.route('/api/check-lock')
@login_required
def check_lock():
    u = session['user']
    today = datetime.datetime.now(PK_TZ).date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    # Check max edit count for this class today
    res = conn.execute("""SELECT MAX(edit_count) FROM apsokara_attendance a 
                        JOIN apsokara_student s ON a.student_id = s.id 
                        WHERE a.date=? AND s.student_class=? AND s.student_section=? AND s.wing=?""", 
                        (today, u['assigned_class'], u['assigned_section'], u['wing'])).fetchone()
    conn.close()
    return jsonify({"edit_count": res[0] if res[0] is not None else 0})


@app.route('/api/students-marking')
@login_required
def students_marking():
    u = session['user']
    if u['role'] != 'Teacher' or not u.get('is_class_teacher'):
        return jsonify({"students": [], "error": "Unauthorized"}), 403
    today = datetime.datetime.now(PK_TZ).date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Query checking both attendance table AND approved leaves for today
    query = """
        SELECT s.id, s.full_name, s.father_name, s.roll_number, a.status,
        (SELECT COUNT(*) FROM apsokara_studentleave l 
         WHERE l.student_id = s.id 
         AND l.status = 'Approved' 
         AND ? BETWEEN l.start_date AND l.end_date) as on_leave
        FROM apsokara_student s 
        LEFT JOIN apsokara_attendance a ON s.id = a.student_id AND a.date=?
        WHERE s.student_class=? AND s.student_section=? AND s.wing=? 
        ORDER BY CAST(s.roll_number AS INTEGER)
    """
    cur = conn.execute(query, (today, today, u['assigned_class'], u['assigned_section'], u['wing']))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"students": rows})


@app.route('/api/sync-attendance', methods=['POST'])
@login_required
def sync_attendance():
    try:
        data = request.json
        attendance_list = data.get('attendance', [])
        u = session['user']
        today = datetime.datetime.now(PK_TZ).date().isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        for item in attendance_list:
            # Check if record already exists
            existing = conn.execute("SELECT id, edit_count FROM apsokara_attendance WHERE student_id=? AND date=?", 
                                 (item['id'], today)).fetchone()
            
            if existing:
                new_count = (existing[1] or 0) + 1
                conn.execute("UPDATE apsokara_attendance SET status=?, edit_count=? WHERE student_id=? AND date=?",
                            (item['status'], new_count, item['id'], today))
            else:
                conn.execute("INSERT INTO apsokara_attendance (date, status, student_id, marked_by, edit_count) VALUES (?, ?, ?, ?, ?)",
                            (today, item['status'], item['id'], u['full_name'], 0))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Attendance Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/archive')
@login_required
def api_archive():
    date = request.args.get('date')
    u = session['user']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    if u['role'] == 'Student':
        if date:
            cur.execute("""SELECT a.date, a.status, a.marked_by, 
                         (SELECT COUNT(*) FROM apsokara_attendance WHERE student_id=a.student_id AND status='Present') * 100.0 / 
                         (SELECT COUNT(*) FROM apsokara_attendance WHERE student_id=a.student_id) as stats
                         FROM apsokara_attendance a 
                         WHERE a.student_id = ? AND a.date = ? 
                         ORDER BY a.date DESC""", (u['id'], date))
        else:
            cur.execute("""SELECT a.date, a.status, a.marked_by,
                         (SELECT COUNT(*) FROM apsokara_attendance WHERE student_id=a.student_id AND status='Present') * 100.0 / 
                         (SELECT COUNT(*) FROM apsokara_attendance WHERE student_id=a.student_id) as stats
                         FROM apsokara_attendance a 
                         WHERE a.student_id = ? 
                         ORDER BY a.date DESC""", (u['id'],))
    else:
        if not date:
            return jsonify({"error": "Date required for staff"}), 400
        cur.execute("""SELECT s.full_name, a.status, a.date 
                     FROM apsokara_student s 
                     JOIN apsokara_attendance a ON s.id = a.student_id 
                     WHERE a.date=? AND s.student_class=? AND s.student_section=? AND s.wing=?""", 
                     (date, u['assigned_class'], u['assigned_section'], u['wing']))
    
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(res)

# Removed the old duplicated block that was below this point



# Vault Route Removed


@app.route('/api/intel')
@login_required
def api_intel():
    u = session['user']
    if u['role'] == 'Student':
        return jsonify({"flags": [], "error": "Access Denied"}), 403
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("""SELECT s.full_name, COUNT(a.id) as total, SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as pres 
                        FROM apsokara_student s LEFT JOIN apsokara_attendance a ON s.id = a.student_id 
                        WHERE s.student_class=? AND s.student_section=? AND s.wing=? GROUP BY s.id""", (u['assigned_class'], u['assigned_section'], u['assigned_wing'], 'Pending'))
    flags = []
    for r in cur.fetchall():
        perc = (r['pres'] / r['total'] * 100) if r['total'] > 0 else 100
        if perc < 75: flags.append({"full_name": r['full_name'], "perc": int(perc)})
    conn.close()
    return jsonify({"flags": flags})


@app.route('/api/student-detailed-stats/<int:sid>')
@login_required
def student_detailed_stats(sid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    stats = conn.execute("SELECT COUNT(*) as total_days, SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as presents, SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END) as absents, SUM(CASE WHEN status='Leave' THEN 1 ELSE 0 END) as leaves FROM apsokara_attendance WHERE student_id = ?", (sid,)).fetchone()
    history = conn.execute("SELECT date, status FROM apsokara_attendance WHERE student_id = ? ORDER BY date DESC LIMIT 15", (sid,)).fetchall()
    conn.close()
    return jsonify({"stats": dict(stats), "history": [dict(h) for h in history]})

@app.route('/logout')
def logout():
    session.clear()
    response = make_response('<script>localStorage.clear(); window.location.replace("/?v=" + Date.now());</script>')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


# ==========================================
#        NEW DIARY SYSTEM BACKEND
# ==========================================

@app.route('/api/diary/init-teacher')
@login_required
def diary_init_teacher():
    u = session['user']
    if u['role'] != 'Teacher': return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Get unique assignments for this teacher
    query = """
        SELECT DISTINCT sa.student_class, sa.section, sa.wing, s.name as sub_name 
        FROM apsokara_subjectassignment sa 
        JOIN apsokara_subject s ON sa.subject_id = s.id 
        WHERE sa.teacher_id = ?
    """
    rows = conn.execute(query, (u['id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/diary/post', methods=['POST'])
@login_required
def diary_post_new():
    try:
        u = session['user']
        if u['role'] != 'Teacher': return jsonify({'success': False, 'msg': 'Only teachers can post'}), 403
        uploaded_files = request.files.getlist('files')
        file_paths = []
        if not os.path.exists('uploads/diary'): os.makedirs('uploads/diary')
        for file in uploaded_files:
            if file and file.filename:
                filename = f"{int(datetime.datetime.now().timestamp())}_{file.filename}"
                path = os.path.join('uploads/diary', filename)
                file.save(path)
                file_paths.append(path)
        data = request.form
        content_text, target_class = data.get('content'), data.get('class')
        target_section, target_wing = data.get('section'), data.get('wing')
        if target_wing and target_wing.lower().startswith('g'): target_wing = 'Girls'
        if target_wing and target_wing.lower().startswith('b'): target_wing = 'Boys'
        subject = data.get('subject')
        is_scheduled = 1 if data.get('schedule_date') else 0
        post_date = data.get('schedule_date') if is_scheduled else datetime.datetime.now().strftime('%Y-%m-%d')
        full_ts = f"{post_date} {datetime.datetime.now().strftime('%I:%M %p')}"
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO apsokara_dailydiary (teacher_id, teacher_name, class, section, wing, subject, content, date_posted, is_scheduled, attachments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                     (u['id'], u['full_name'], target_class, target_section, target_wing, subject, content_text, full_ts, is_scheduled, ",".join(file_paths)))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'msg': 'Diary Published!'})
    except Exception as e: return jsonify({'success': False, 'msg': str(e)})

@app.route('/api/diary/fetch')
@login_required
def diary_fetch_list():
    u = session['user']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if u['role'] == 'Student':
        # Student sirf apni class ki diaries dekhega jo schedule date tak pohanch chuki hain
        query = """
            SELECT * FROM apsokara_dailydiary 
            WHERE class=? AND section=? 
            AND (wing=? OR wing LIKE SUBSTR(?, 1, 1) || '%')
            ORDER BY id DESC
        """
        rows = conn.execute(query, (u.get('student_class', u.get('assigned_class')), u.get('student_section', u.get('assigned_section')), u['wing'], u['wing'])).fetchall()
    else:
        # Teacher apni saari history dekhega
        query = "SELECT * FROM apsokara_dailydiary WHERE teacher_id=? ORDER BY id DESC"
        rows = conn.execute(query, (u['id'],)).fetchall()
    
    conn.close()
    return jsonify([dict(r) for r in rows])

# ==========================================




@app.route('/api/diary/unread-status')
@login_required
def diary_unread_status():
    u = session.get('user')
    if not u or u.get('role') != 'Student': return jsonify({'count': 0, 'latest_id': 0})
    last_seen = request.args.get('last_seen', 0, type=int)
    conn = sqlite3.connect(DB_PATH)
    s_class, s_sec, s_wing = str(u.get('student_class','')), str(u.get('student_section','')), u.get('wing','')
    query = "SELECT COUNT(*), MAX(id) FROM apsokara_dailydiary WHERE class=? AND section=? AND (wing=? OR wing LIKE SUBSTR(?, 1, 1) || '%') AND id > ?"
    row = conn.execute(query, (s_class, s_sec, s_wing, s_wing, last_seen)).fetchone()
    conn.close()
    return jsonify({'count': row[0] or 0, 'latest_id': row[1] or 0})



@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory("uploads/diary", filename)

# ==========================================
# STRICT LEAVE MANAGEMENT SYSTEM (BACKEND)
# ==========================================

@app.route('/api/leave/submit', methods=['POST'])
@login_required
def submit_leave_v2():
    u = session['user']
    if u.get('role') != 'Student':
        return jsonify({'success': False, 'error': 'Only students can apply'})
    
    import time
    file_path = ""
    if 'attachment' in request.files:
        f = request.files['attachment']
        if f and f.filename != '':
            os.makedirs('static/uploads/leaves', exist_ok=True)
            fname = f"LV_{u['id']}_{int(time.time())}_{f.filename}"
            f.save(os.path.join('static/uploads/leaves', fname))
            file_path = f"static/uploads/leaves/{fname}"
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Improved Logic: Handle both Form and JSON for Offline/Online Sync
            data = request.form if request.form else (request.get_json() if request.is_json else {})
            
            s_date = data.get('start') or data.get('start_date')

            # Professional Overlap Check
            from datetime import datetime
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            check_sql = """
                SELECT start_date, end_date FROM apsokara_studentleave 
                WHERE student_id = ? AND status = 'Approved' 
                AND ? BETWEEN date(start_date) AND date(end_date)
                LIMIT 1
            """
            existing = conn.execute("SELECT id, start_date, end_date FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN date(start_date) AND date(end_date) LIMIT 1", (u['id'], today_str)).fetchone()
            
            if existing:
                msg = f"❌ Action Blocked: You already have an Approved leave from {existing[1]} to {existing[2]}."
                return jsonify({'success': False, 'error': msg, 'conflict_id': existing[0]})
    
            e_date = data.get('end') or data.get('end_date')
            reason = data.get('reason')

            conn.execute("""INSERT INTO apsokara_studentleave 
                (student_id, full_name, roll_number, class, section, wing, start_date, end_date, reason, attachment) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (u['id'], u['full_name'], u.get('roll_number', 'N/A'), u.get('assigned_class', 'N/A'), 
                 u.get('assigned_section', 'N/A'), u.get('wing', 'N/A'), 
                 s_date, e_date, reason, file_path))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/leave/list')
@login_required
def list_leaves_v2():
    u = session['user']
    role = u.get('role')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    if role == 'Student':
        # Student sirf apni history dekhega
        res = conn.execute("SELECT * FROM apsokara_studentleave WHERE student_id = ? ORDER BY id DESC", (u['id'],)).fetchall()
    else:
        # Teacher sirf apni assigned class ki leaves dekhega
        # Hum is_class_teacher ka check pehle hi UI me laga chuke honge
        res = conn.execute("""SELECT * FROM apsokara_studentleave 
                            WHERE class=? AND section=? AND (wing=? OR wing LIKE SUBSTR(?, 1, 1) || '%') 
                            ORDER BY status DESC, id DESC""",
                            (u.get('assigned_class'), u.get('assigned_section'), u.get('assigned_wing'), u.get('assigned_wing'))).fetchall()
    
    data = [dict(row) for row in res]
    conn.close()
    return jsonify(data)

@app.route('/api/leave/action', methods=['POST'])
@login_required
def leave_action_v2():
    u = session['user']
    if not u.get('is_class_teacher'):
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    d = request.json
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE apsokara_studentleave SET status=? WHERE id=? AND class=? AND section=? AND (wing=? OR wing LIKE SUBSTR(?, 1, 1) || '%')", 
                        (d['status'], d['id'], u.get('assigned_class'), u.get('assigned_section'), u.get('assigned_wing'), u.get('assigned_wing')))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("""SELECT COUNT(*) FROM apsokara_studentleave 
                             WHERE class=? AND section=? AND (wing=? OR wing LIKE SUBSTR(?, 1, 1) || '%') AND status='Pending'""",
                             (u.get('assigned_class'), u.get('assigned_section'), u.get('assigned_wing'), u.get('assigned_wing'))).fetchone()[0]
        conn.close()
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})



@app.route('/sw.js')
def serve_sw():
    return send_from_directory("static", "sw.js")


@app.route('/api/leave/stats')
@login_required
def get_leave_stats_v2():
    u = session['user']
    if not u.get('is_class_teacher'):
        return jsonify({'pending': 0, 'today': 0, 'done': 0})
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        c, s, w = u.get('assigned_class'), u.get('assigned_section'), u.get('assigned_wing')
        
        # Pending for this teacher only
        pending = conn.execute("SELECT COUNT(*) FROM apsokara_studentleave WHERE class=? AND section=? AND wing=? AND status='Pending'", (c,s,w)).fetchone()[0]
        
        # Today's applied (Using date comparison)
        today = conn.execute("SELECT COUNT(*) FROM apsokara_studentleave WHERE class=? AND section=? AND wing=? AND (start_date LIKE '%2026-04-29%' OR date(start_date) = date('now'))", (c,s,w)).fetchone()[0]
        
        # Total Approved Only
        done = conn.execute("SELECT COUNT(*) FROM apsokara_studentleave WHERE class=? AND section=? AND wing=? AND status='Approved'", (c,s,w)).fetchone()[0]
        
        conn.close()
        return jsonify({'pending': int(pending), 'today': int(today), 'done': int(done)})
    except:
        return jsonify({'pending': 0, 'today': 0, 'done': 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.after_request
def add_header(response):
    # Allow home page and static files to be cached for offline use
    if request.path.startswith('/static/') or request.path in ['/sw.js', '/']:
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response
    if request.path.startswith('/static/') or request.path == '/sw.js':
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

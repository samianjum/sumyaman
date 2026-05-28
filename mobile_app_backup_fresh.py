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
        const ping = await fetch('/static/logo.png', { method: 'HEAD', cache: 'no-store' });
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
    <title>APS OKARA</title>
    <script src="/static/tailwind.min.css"></script>
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
    <div id="custom-confirm" class="hidden fixed inset-0 z-[200000] flex items-center justify-center p-6 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
        <div class="bg-white w-full max-w-sm rounded-[35px] p-8 shadow-2xl scale-95 animate-zoom-in border border-gray-100">
            <div class="text-4xl mb-4 text-center">🤔</div>
            <h3 id="confirm-msg" class="text-lg font-black text-slate-800 text-center leading-tight mb-8 uppercase tracking-tighter">Are you sure?</h3>
            <div class="flex gap-3">
                <button id="confirm-no" class="flex-1 py-4 rounded-2xl font-black text-xs uppercase bg-gray-100 text-gray-500 active:scale-95 transition-all">Cancel</button>
                <button id="confirm-yes" class="flex-1 py-4 rounded-2xl font-black text-xs uppercase bg-rose-600 text-white shadow-lg shadow-rose-200 active:scale-95 transition-all">Yes, Proceed</button>
            </div>
        </div>
    </div>

    <div id="toast-container"></div>
    <div class="app-shell">
        {% if not logged_in %}
        <div class="app-body flex flex-col justify-center">
            <div class="text-center mb-10">
                <div class="w-20 h-20 bg-[#1B4332] rounded-[2rem] mx-auto flex items-center justify-center text-4xl mb-4 shadow-lg">🏫</div>
                <h1 class="text-3xl font-black text-[#1B4332]">APS OKARA</h1>
            </div>
            <div class="bg-gray-50 p-6 rounded-[35px] border border-gray-100">
                <div class="flex bg-gray-200 p-1.5 rounded-2xl mb-6">
                    <button onclick="setRole('Student')" id="sBtn" class="flex-1 py-3 rounded-xl font-black text-sm bg-[#D4AF37] text-[#1B4332]">STUDENT</button>
                    <button onclick="setRole('Teacher')" id="tBtn" class="flex-1 py-3 rounded-xl font-black text-sm text-gray-400">STAFF</button>
                </div>
                <input type="text" id="uid" placeholder="ID / B-Form" class="w-full p-4 mb-4 rounded-2xl outline-none">
                <input type="date" id="dob" value="2010-01-01" class="w-full p-4 mb-6 rounded-2xl outline-none">
                <button onclick="doLogin()" class="w-full bg-[#1B4332] text-white py-4 rounded-2xl font-black shadow-xl">LOGIN</button>
            </div>
        </div>
        {% else %}





        <div id="main-header" class="app-header shadow-md p-4 bg-gradient-to-r from-[#1B4332] to-[#2D6A4F]">
            <div class="flex justify-between items-center mb-3 opacity-80 border-b border-white/10 pb-2">
                <span id="current-date" class="text-[9px] font-bold tracking-tighter uppercase">-- --- ----</span>
                <span id="current-time" class="text-[9px] font-black tracking-widest text-[#D4AF37]">00:00:00</span> <div id="net-ind" class="net-status net-online"></div>
            </div>

            <div class="flex items-center gap-3">
                <div class="flex-shrink-0">
                    <div class="w-14 h-14 rounded-full border-2 border-white/30 bg-white flex items-center justify-center overflow-hidden shadow-sm">
                        <img src="/app_logo" alt="Logo" class="w-[80%] h-[80%] object-contain">
                    </div>
                </div>

                <div class="flex-grow">
                    <h2 class="text-lg font-black leading-tight">{{ user.full_name }}</h2>
                    <p class="text-[10px] font-bold opacity-90">S/O: {{ user.father_name }}</p>

                    <div class="mt-1 flex items-center gap-2">
                        <span class="text-[8px] font-black bg-black/20 px-2 py-0.5 rounded uppercase tracking-tighter text-[#D4AF37]">{{ user.role }}</span>
                        {% if user.role == 'Student' %}
                            <span class="text-[9px] font-bold opacity-80 border-l border-white/30 pl-2">Class: {{ user.assigned_class }}-{{ user.assigned_section }}</span>
                        {% elif user.role == 'Teacher' and user.is_class_teacher %}
                            <span class="text-[9px] font-bold opacity-80 border-l border-white/30 pl-2">IC: {{ user.assigned_class }}-{{ user.assigned_section }}</span>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>

        <script>
        function updateClock() {
            const now = new Date();
            const options = { day: '2-digit', month: 'short', year: 'numeric' };
            document.getElementById('current-date').innerText = now.toLocaleDateString('en-GB', options).toUpperCase();
            document.getElementById('current-time').innerText = now.toLocaleTimeString('en-GB', { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
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
                if(d.is_ready) html += `<button onclick="publishResult(${d.exam_id})" class="w-full bg-[#1B4332] text-white py-3 rounded-xl font-black text-xs mt-2">🚀 PUBLISH RESULT</button>`;
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




            <div id="page-home" class="grid grid-cols-2 gap-4">
                {% if user.role == 'Student' or (user.role == 'Teacher' and user.is_class_teacher) %}
                <div onclick="openLeaveHub()" class="relative glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-rose-500 active:scale-95 transition-all cursor-pointer">
                    <span id="leave-badge" class="hidden absolute top-3 right-3 bg-red-600 text-white text-[10px] font-black h-5 w-5 flex items-center justify-center rounded-full shadow-lg border-2 border-white animate-bounce">0</span>
                    <div class="text-4xl mb-3 drop-shadow-md">✉️</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Leave Hub</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Status & Apply</p>
                </div>
                {% endif %}
                {% if user.role == 'Teacher' and user.assignments %}
                <div onclick="openDiaryHub()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-purple-600 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">📓</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Daily Diary</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Post Homework</p>
                </div>
                {% endif %}

                {% if user.role == 'Student' %}
                <div onclick="openDiaryHub()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-amber-500 active:scale-95 transition-all cursor-pointer relative">
                    <div id="diary-badge" class="hidden absolute -top-2 -right-2 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded-full animate-bounce">0</div>
                    <div class="text-4xl mb-3 drop-shadow-md">📖</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Diary</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Check Homework</p>
                </div>
                {% endif %}

                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-green-600 active:scale-95 transition-all">
                    <div class="text-4xl mb-3 drop-shadow-md">📋</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Attendance</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Mark Daily Presence</p>
                </div>
                {% endif %}


                {% if user.role == 'Student' %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-blue-600 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">📊</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Reports</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">View Progress</p>
                </div>
                {% endif %}

                {% if user.role == 'Student' %}
                <div onclick="showTab('results'); loadStudentResults();" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-emerald-500 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">🏆</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">My Result</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Official Record</p>
                </div>
                {% endif %}
                {% if user.role == 'Teacher' %}
                <div onclick="navToMarks()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-indigo-600 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">🎯</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Marks Entry</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Grading Portal</p>
                </div>
                {% endif %}
                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('final-upload'); loadFinalizeStatus();" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-orange-500 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">📤</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Finalize</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Submit Class</p>
                </div>
                {% endif %}
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

    <div id="page-leave" class="hidden animate-slide-up pb-24">
        <div class="flex items-center justify-between mb-6 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
            <div>
                <h3 class="font-black text-2xl text-rose-600 uppercase tracking-tighter">Leave Hub</h3>
            </div>
            <button onclick="showTab('home')" class="bg-gray-100 p-3 rounded-xl active:scale-90 transition-all">
                <span class="text-xs font-black text-gray-500">BACK</span>
            </button>
        </div>
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

            <div id="page-archive-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400">← Back</button>
                <input type="date" id="archive-date" onchange="loadArchive()" placeholder="Select date for specific day" class="w-full p-3 rounded-xl bg-gray-50 border-none font-bold">
                <div id="archive-results" class="space-y-2"></div>
            </div>






            <div id="page-intel-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">← Back to Hub</button>
                <div id="intel-view" class="space-y-6"></div>
            </div>
            <div id="page-profile" class="hidden space-y-4">
                <div class="glass-card bg-[#1B4332] text-white">
                    <h3 class="font-black text-lg">🔒 {{ user.role }} Vault</h3>
                    <p class="text-[10px] opacity-80">Identity & Record Verification</p>
                </div>

                <div id="vault-auth" class="glass-card space-y-3">
                    <input type="text" id="v-auth-id" placeholder="{{ 'Confirm B-Form' if user.role == 'Student' else 'Confirm CNIC' }}" class="w-full p-3 bg-gray-50 rounded-xl text-sm font-bold outline-none border border-gray-100">
                    <input type="date" id="v-dob" class="w-full p-3 bg-gray-50 rounded-xl text-sm font-bold outline-none border border-gray-100">
                    <button onclick="unlockVault()" class="w-full bg-[#D4AF37] text-[#1B4332] py-3 rounded-xl font-black text-sm shadow-md">UNLOCK PROFILE</button>
                </div>

                <div id="profile-details" class="hidden space-y-3">
                    <div class="glass-card p-4">
                        <p class="text-[9px] font-bold text-gray-400 uppercase">Personal Record</p>
                        <div class="mt-2 space-y-2 text-sm font-bold text-gray-700">
                            <div class="flex justify-between border-b pb-1"><span>Full Name:</span><span>{{ user.full_name }}</span></div>
                            <div class="flex justify-between border-b pb-1"><span>Father Name:</span><span id="p-father">***</span></div>
                            <div class="flex justify-between border-b pb-1"><span>{{ 'B-Form:' if user.role == 'Student' else 'CNIC:' }}</span><span id="p-uid-val">***</span></div>
                            <div class="flex justify-between border-b pb-1"><span>DOB:</span><span id="p-dob-val">***</span></div>
                            <div class="flex justify-between border-b pb-1"><span>Religion:</span><span id="p-rel">***</span></div>
                            <div class="flex justify-between border-b pb-1"><span>Contact:</span><span id="p-contact">***</span></div>
                            <div class="flex justify-between border-b pb-1"><span>Address:</span><span id="p-addr" class="text-[10px] text-right">***</span></div>
                        </div>
                    </div>

                    {% if user.role == 'Teacher' and user.is_class_teacher %}
                    <div class="glass-card p-4 border-l-4 border-blue-600">
                        <p class="text-[9px] font-bold text-gray-400 uppercase">Professional Status</p>
                        <div class="mt-2 space-y-2 text-sm font-bold text-gray-700">
                            <div class="flex justify-between border-b pb-1"><span>Class Teacher:</span><span>YES</span></div>
                            <div class="flex justify-between border-b pb-1"><span>In-charge of:</span><span>{{ user.assigned_class }}-{{ user.assigned_section }} ({{ user.wing }})</span></div>
                        </div>
                    </div>
                    {% endif %}

                    {% if user.role == 'Teacher' and user.assignments %}
                    <div class="glass-card p-4 border-l-4 border-purple-600">
                        <p class="text-[9px] font-bold text-gray-400 uppercase">📚 Subject Assignments</p>
                        <div class="mt-2 space-y-2">
                            {% for sub in user.assignments %}
                            <div class="flex justify-between items-center text-[11px] font-bold bg-gray-50 p-2 rounded-lg border border-purple-100">
                                <span class="text-purple-700">{{ sub.s_name if sub.s_name else 'Subject' }}</span>
                                <span class="text-gray-500">{{ sub.c_num }}-{{ sub.s_sec }} ({{ sub.w_wing }})</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}

                    {% if user.role == 'Student' %}
                    <div class="glass-card p-4 border-l-4 border-[#1B4332]">
                        <p class="text-[9px] font-bold text-gray-400 uppercase">Academic Info</p>
                        <div class="mt-2 space-y-2 text-sm font-bold text-gray-700">
                            <div class="flex justify-between border-b pb-1"><span>Roll No:</span><span>{{ user.roll_number }}</span></div>
                            <div class="flex justify-between border-b pb-1"><span>Class:</span><span>{{ user.assigned_class }}-{{ user.assigned_section }}</span></div>
                        </div>
                    </div>
                    {% endif %}


                    <button onclick="safeLogout(event)" class="w-full bg-red-50 text-red-600 py-4 rounded-2xl font-black text-sm border border-red-100 mt-4">LOGOUT SESSION</button>
                </div>
            </div>

        </div>

        <div class="app-nav">
            <div onclick="showTab('home')" id="n-home" class="nav-btn active-nav"><span>🏠</span><span>Home</span></div>
            {% if user.role == 'Student' or (user.role == 'Teacher' and user.is_class_teacher) %}
            <div onclick="showTab('mark')" id="n-mark" class="nav-btn"><span>📋</span><span>{{ 'History' if user.role == 'Student' else 'Attend' }}</span></div>
            {% endif %}
            <div onclick="showTab('profile')" id="n-profile" class="nav-btn"><span>👤</span><span>Profile</span></div>
            <div onclick="safeLogout(event)" class="nav-btn text-red-400"><span>🚪</span><span>Exit</span></div>
        </div>
        {% endif %}
    </div>

    <script>
        let currentEditCount = 0;
        let isLocked = false;

        function setRole(r) {
            window.currentRole = r;
            document.getElementById('sBtn').className = r === 'Student' ? "flex-1 py-3 rounded-xl font-black text-sm bg-[#D4AF37] text-[#1B4332]" : "flex-1 py-3 rounded-xl font-black text-sm text-gray-400";
            document.getElementById('tBtn').className = r === 'Teacher' ? "flex-1 py-3 rounded-xl font-black text-sm bg-[#D4AF37] text-[#1B4332]" : "flex-1 py-3 rounded-xl font-black text-sm text-gray-400";
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
                    <div class="flex justify-between items-center mt-2 pt-2 border-t border-gray-100">
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
            if (t !== 'profile') {
                const details = document.getElementById('profile-details');
                const vault = document.getElementById('vault-auth');
                if(details) details.classList.add('hidden');
                if(vault) vault.classList.remove('hidden');
                document.getElementById('v-auth-id').value = '';
            }

            const pages = ['home', 'diary', 'mark', 'results', 'marks-entry', 'final-upload', 'profile', 'marking-view', 'attendance-view', 'archive-view', 'intel-view', 'leave', 'marks-portal'];
            pages.forEach(p => {
                const el = document.getElementById('page-' + p);
                if (el) el.classList.add('hidden');
                if (t === 'results') loadStudentResults();
            });

            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active-nav'));

            const targetPage = document.getElementById('page-' + t);
            if (targetPage) targetPage.classList.remove('hidden');

            if(document.getElementById('n-' + t)) document.getElementById('n-' + t).classList.add('active-nav');

            // --- HEADER VISIBILITY LOGIC ---
            const header = document.getElementById('main-header');
            const fullScreenPages = ['marking-view', 'attendance-view', 'archive-view', 'intel-view'];
            if (fullScreenPages.includes(t)) {
                header.classList.add('hidden');
            } else {
                header.classList.remove('hidden');
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

        async function loadArchive() {
            const dateInput = document.getElementById('archive-date').value;
            let date = dateInput;
            // Agar Student hai aur date select nahi ki, to date parameter khali bhejo
            if ('{{ user.role }}' === 'Student' && !dateInput) {
                date = '';
            } else if (!dateInput) {
                date = new Date().toISOString().split('T')[0];
            }
            const res = await fetch('/api/archive?date=' + date);
            const data = await res.json();
            document.getElementById('archive-results').innerHTML = data.map(s => `
                <div class="flex justify-between items-center p-4 bg-gray-50 rounded-2xl">
                    <div>
                        <span class="text-[9px] font-bold text-gray-400">${s.date || ''}</span>
                        <h4 class="text-xs font-black">${s.full_name || 'My Record'}</h4>
                    </div>
                    <span class="status-pill ${s.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${s.status}</span>
                </div>
            `).join('') || '<p class="text-center text-xs py-10 font-bold text-gray-300">No history found.</p>';
        }





        async function unlockVault() {
            const auth_id = document.getElementById('v-auth-id').value;
            const dob = document.getElementById('v-dob').value;
            if(!auth_id || !dob) { alert("Please fill both fields"); return; }

            const res = await fetch('/api/unlock-vault', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ auth_id, dob })
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('vault-auth').classList.add('hidden');
                document.getElementById('profile-details').classList.remove('hidden');
                document.getElementById('p-father').innerText = data.info.father_name;
                document.getElementById('p-uid-val').innerText = data.info.uid;
                document.getElementById('p-dob-val').innerText = data.info.dob;
                document.getElementById('p-rel').innerText = data.info.religion;
                document.getElementById('p-contact').innerText = data.info.contact;
                document.getElementById('p-addr').innerText = data.info.address;
            } else {
                showToast("Verification Failed!", "error");
            }
        }



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
                        <div class="flex flex-col items-center justify-center py-20 opacity-20">
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
    if(!confirm(`Are you sure you want to ${status} this leave?`)) return;
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
            <div id="leave-menu" class="grid grid-cols-1 gap-4 animate-fade-in">
                <div onclick="renderLeaveApply()" class="glass-card flex items-center p-6 border-l-8 border-rose-500 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mr-5">📝</div>
                    <div>
                        <h4 class="font-black text-sm uppercase text-slate-800">Apply New Leave</h4>
                        <p class="text-[10px] text-gray-400 font-bold">Submit a new request</p>
                    </div>
                </div>
                <div onclick="renderLeaveHistory()" class="glass-card flex items-center p-6 border-l-8 border-slate-700 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mr-5">📜</div>
                    <div>
                        <h4 class="font-black text-sm uppercase text-slate-800">Leave History</h4>
                        <p class="text-[10px] text-gray-400 font-bold">Track your previous status</p>
                    </div>
                </div>
            </div>
            <div id="leave-dynamic-inner" class="hidden animate-slide-up"></div>`;

    } else {
        area.innerHTML = `
            <div id="leave-menu" class="grid grid-cols-1 gap-4 animate-fade-in">
                <div class="bg-rose-50 p-5 rounded-3xl border border-rose-100 mb-2">
                    <h4 class="font-black text-rose-900 text-sm uppercase">Class Management</h4>
                    <p class="text-[10px] text-rose-600 font-bold opacity-80 italic">{{ user.assigned_class }} - {{ user.assigned_section }} ({{ user.assigned_wing }})</p>
                </div>

                <div onclick="renderLeaveHistory('Pending')" class="relative glass-card flex items-center p-6 border-l-8 border-amber-500 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mr-5">📥</div>
                    <div>
                        <h4 class="font-black text-sm uppercase text-slate-800">Pending Requests</h4>
                        <p class="text-[10px] text-gray-400 font-bold">New leaves waiting for action</p>
                    </div>
                    <span id="card-leave-badge" class="hidden absolute top-4 right-4 bg-red-600 text-white text-[10px] font-black h-6 w-6 flex items-center justify-center rounded-full shadow-lg border-2 border-white animate-pulse">0</span>
                </div>

                <div onclick="renderLeaveHistory('History')" class="glass-card flex items-center p-6 border-l-8 border-blue-600 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mr-5">📚</div>
                    <div>
                        <h4 class="font-black text-sm uppercase text-slate-800">Leave Archive</h4>
                        <p class="text-[10px] text-gray-400 font-bold">Past Approved/Rejected records</p>
                    </div>
                </div>
            </div>
            <div id="leave-dynamic-inner" class="hidden animate-slide-up"></div>`;

        // Sync badge on card load
        setTimeout(updateLeaveBadge, 100);
    }

};


window.renderLeaveApply = function() {
    document.getElementById('leave-menu').classList.add('hidden');
    const inner = document.getElementById('leave-dynamic-inner');
    inner.classList.remove('hidden');
    inner.innerHTML = `<button onclick="openLeaveHub()" class="mb-4 flex items-center gap-2 text-[10px] font-black text-rose-600 uppercase bg-rose-50 px-4 py-2 rounded-full w-fit active:scale-90 transition-all">← Back to Menu</button>` + `
        <div class="glass-card p-6 space-y-5 border-t-4 border-rose-500">
            <div class="space-y-1">
                <label class="text-[10px] font-black text-gray-400 uppercase">Duration</label>
                <div class="grid grid-cols-2 gap-2">
                    <input type="date" id="l-start" class="w-full p-4 bg-gray-50 rounded-2xl text-xs font-bold border-none focus:ring-2 ring-rose-500">
                    <input type="date" id="l-end" class="w-full p-4 bg-gray-50 rounded-2xl text-xs font-bold border-none focus:ring-2 ring-rose-500">
                </div>
            </div>
            <div class="space-y-1">
                <label class="text-[10px] font-black text-gray-400 uppercase">Reason for Leave</label>
                <textarea id="l-reason" placeholder="Explain your reason here..." class="w-full p-4 bg-gray-50 rounded-2xl text-sm min-h-[120px] border-none focus:ring-2 ring-rose-500"></textarea>
            </div>
            <div class="space-y-1">
                <label class="text-[10px] font-black text-gray-400 uppercase">Attachment (Optional)</label>
                <input type="file" id="l-file" class="text-[10px] w-full bg-blue-50/50 p-3 rounded-xl border border-dashed border-blue-200">
            </div>
            <button onclick="submitLeaveRequest()" id="l-sub-btn" class="w-full bg-rose-600 text-white py-5 rounded-3xl font-black text-xs uppercase tracking-widest shadow-xl shadow-rose-200 active:scale-95 transition-all">🚀 Submit Request</button>
        </div>`;
     };


window.renderLeaveHistory = async function(filterMode = 'All') {
    if(document.getElementById('leave-menu')) document.getElementById('leave-menu').classList.add('hidden');
    const inner = document.getElementById('leave-dynamic-inner');
    inner.classList.remove('hidden');
    inner.innerHTML = `<button onclick="openLeaveHub()" class="mb-4 flex items-center gap-2 text-[10px] font-black text-rose-600 uppercase bg-rose-50 px-4 py-2 rounded-full w-fit active:scale-90 transition-all">← Back to Menu</button>
                      <div class="flex justify-center py-10"><div class="animate-spin h-8 w-8 border-4 border-rose-600 border-t-transparent rounded-full"></div></div>`;

    let serverData = [];
    let isOfflineMode = false;

    try {
        const res = await fetch('/api/leave/list'); // Teacher/Student both use same route but backend filters by session
        const json = await res.json();
        serverData = Array.isArray(json) ? json : [];
    } catch (e) {
        console.warn("📡 Using Offline Mode for History");
        isOfflineMode = true;
    }

    try {
        const offlinePending = await db.syncQueue.where('url').equals('/api/leave/submit').toArray();
        const mappedOffline = offlinePending.map(item => ({
            id: 'off-' + item.id,
            full_name: 'You (Sync Pending)',
            reason: item.body.reason,
            start_date: item.body.start_date,
            end_date: item.body.end_date,
            status: 'Offline',
            is_offline: true
        }));

        let combinedData = [...mappedOffline, ...serverData];

        if(filterMode === 'Pending') combinedData = combinedData.filter(l => l.status === 'Pending' || l.status === 'Offline');
        else if(filterMode === 'History') combinedData = combinedData.filter(l => l.status !== 'Pending' && l.status !== 'Offline');

        if (combinedData.length === 0) {
            inner.innerHTML = `<button onclick="openLeaveHub()" class="mb-4 flex items-center gap-2 text-[10px] font-black text-rose-600 uppercase bg-rose-50 px-4 py-2 rounded-full w-fit">← Back</button>
                              <div class="text-center py-10 text-gray-400 font-bold">No Leave Requests Found ${isOfflineMode ? '(Offline)' : ''}</div>`;
            return;
        }

        // --- RENDER LOGIC START ---
        const userRole = '{{ user.role }}';
        let html = `<button onclick="openLeaveHub()" class="mb-4 flex items-center gap-2 text-[10px] font-black text-rose-600 uppercase bg-rose-50 px-4 py-2 rounded-full w-fit active:scale-90 transition-all">← Back to Menu</button>
                    <div class="space-y-4">`;

        combinedData.forEach(l => {
            const sClass = l.status === 'Approved' ? 'bg-emerald-50 text-emerald-600' : (l.status === 'Offline' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600');
            html += `<div class="bg-white p-5 rounded-3xl border border-gray-100 shadow-sm relative overflow-hidden">
                        ${l.is_offline ? '<div class="absolute top-0 right-0 bg-amber-500 text-[8px] text-white px-3 py-1 rounded-bl-xl font-black uppercase tracking-tighter">Sync Pending</div>' : ''}
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <h4 class="font-black text-gray-900 text-sm capitalize">${l.reason}</h4>
                                ${ (userRole === 'Teacher' && l.status === 'Pending') ? `
                                <div class="flex gap-2 mt-3">
                                    <button onclick="updateLeaveStatus(${l.id}, 'Approved')" class="bg-emerald-600 text-white text-[10px] font-black px-4 py-2 rounded-xl active:scale-95 transition-all shadow-sm shadow-emerald-200">APPROVE</button>
                                    <button onclick="updateLeaveStatus(${l.id}, 'Rejected')" class="bg-rose-600 text-white text-[10px] font-black px-4 py-2 rounded-xl active:scale-95 transition-all shadow-sm shadow-rose-200">REJECT</button>
                                </div>
                                ` : '' }
                                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">${l.start_date} to ${l.end_date}</p>
                            </div>
                            <span class="text-[9px] font-black px-3 py-1 rounded-full uppercase ${sClass}">${l.status}</span>
                        </div>
                    </div>`;
        });
        html += `</div>`;
        inner.innerHTML = html;
        // --- RENDER LOGIC END ---

    } catch (err) {
        inner.innerHTML = `<div class="text-center py-10 font-black text-rose-600 uppercase">Critical UI Error</div>`;
    }
};



const Object_from_iterable = (iter) => { const obj = {}; for (const [k, v] of iter) { if(k!=="attachment") obj[k] = v; } return obj; };
window.submitLeaveRequest = async function() {
    const btn = document.getElementById('l-sub-btn');
    const start = document.getElementById('l-start').value;
    const end = document.getElementById('l-end').value;
    const reason = document.getElementById('l-reason').value;
    const file = document.getElementById('l-file').files[0];

    if(!start || !end || !reason) return alert("Please fill all required fields!");

    const fd = new FormData();
    fd.append('start_date', start);
    fd.append('end_date', end);
    fd.append('reason', reason);
    if(file) fd.append('attachment', file);

    try {
        btn.disabled = true;
        btn.innerText = "PROCESSING...";

        if (!navigator.onLine) {
            const offlineData = {};
            fd.forEach((value, key) => { if(!(value instanceof File)) offlineData[key] = value; });
            await saveOffline('/api/leave/submit', 'POST', offlineData);
            alert("📡 Offline Mode: Leave saved locally!");
            renderLeaveHistory();
            return;
        }

        const res = await fetch('/api/leave/submit', {method:'POST', body:fd});
        const result = await res.json();

        // Handle both server success and Service Worker offline fallback
        if(result.success || result.status === 'offline') {
            if(result.status === 'offline') {
                const offlineData = {};
                fd.forEach((value, key) => { if(!(value instanceof File)) offlineData[key] = value; });
                await saveOffline('/api/leave/submit', 'POST', offlineData);
                alert("📡 Network Flaky: Saved to Offline Storage!");
            } else {
                alert("🚀 Leave Submitted Successfully!");
            }
            renderLeaveHistory();
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
    const mainBadge = document.getElementById('leave-badge');
    const cardBadge = document.getElementById('card-leave-badge');

    try {
        const res = await fetch('/api/leave/pending-count');
        const data = await res.json();
        const count = data.count || 0;

        if(mainBadge) {
            if(count > 0) { mainBadge.innerText = count; mainBadge.classList.remove('hidden'); }
            else { mainBadge.classList.add('hidden'); }
        }

        if(cardBadge) {
            if(count > 0) { cardBadge.innerText = count; cardBadge.classList.remove('hidden'); }
            else { cardBadge.classList.add('hidden'); }
        }
    } catch(e) {}
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
    }, 3000);
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
<script src="/static/marks_v3.js"></script>
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
def get_app_logo():
    import os
    path = "/home/sami/Downloads/sami.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "", 404
    import os
    path = "/home/sami/Downloads/sami.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "", 404


@app.route('/api/school-logo')
def get_school_logo():
    return send_file('/home/sami/Downloads/sami.png', mimetype='image/png')

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
                    COALESCE(s.name, 'Subject ' || sa.subject_id) AS s_name,
                    sa.student_class AS c_num,
                    sa.section AS s_sec,
                    sa.wing AS w_wing
                FROM apsokara_subjectassignment sa
                LEFT JOIN apsokara_subject s ON sa.subject_id = s.id
                WHERE sa.teacher_id = ?""", (t_id,))
            rows = cur.fetchall()
            u_dict['assignments'] = [dict(r) for r in rows]
            # Debug: print(f"Assignments found: {u_dict['assignments']}")
        # ---------------------------------------------------





        session['user'] = u_dict

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



@app.route('/api/unlock-vault', methods=['POST'])
@login_required
def unlock_vault():
    data = request.json
    print(f'SAVE ATTEMPT -> EID: {data.get("eid")}, SID: {data.get("sid")}')
    u = session['user']
    auth_id, dob = str(data.get('auth_id')).strip(), str(data.get('dob')).strip()
    # Check role to compare against correct column
    stored_uid = str(u.get('b_form') if u['role'] == 'Student' else u.get('cnic')).strip()

    if auth_id == stored_uid and dob == str(u.get('dob')):
        return jsonify({
            "success": True,
            "info": {
                "father_name": u.get('father_name'),
                "uid": stored_uid,
                "dob": u.get('dob'),
                "religion": u.get('religion'),
                "contact": u.get('parents_phone' if u['role'] == 'Student' else 'contact'),
                "address": u.get('address')
            }
        })
    return jsonify({"success": False}), 401


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



@app.route('/api/leave/pending-count')
@login_required
def get_pending_leave_count():
    u = session['user']
    if not u.get('is_class_teacher'):
        return jsonify({'count': 0})
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

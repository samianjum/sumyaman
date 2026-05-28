from flask import Flask, render_template_string, request, jsonify, session
import sqlite3, datetime, pytz
from functools import wraps

app = Flask(__name__)
app.secret_key = "aps_okara_ultimate_final_v3"

# --- CONFIG ---
DB_PATH = 'db.sqlite3'
PK_TZ = pytz.timezone("Asia/Karachi")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return '<script>window.location.href="/";</script>'
        return f(*args, **kwargs)
    return decorated_function


# --- NEW DIARY SYSTEM (CONNECTED TO DB.SQLITE3) ---

@app.route('/api/diary/teacher-classes')
@login_required
def get_diary_classes():
    user = session['user']
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    query = """
        SELECT a.student_class, a.section, a.wing, a.subject_id, s.name as sub_name
        FROM apsokara_subjectassignment a
        LEFT JOIN apsokara_subject s ON a.subject_id = s.id
        WHERE a.teacher_id = ?
    """
    rows = conn.execute(query, (user["id"],)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])
@app.route('/api/diary/submit', methods=['POST'])
@login_required
def submit_diary_entry():
    user = session['user']
    conn = sqlite3.connect('db.sqlite3')
    try:
        data = request.json
        conn.execute('''
            INSERT INTO apsokara_dailydiary (teacher_id, teacher_name, class, section, subject, content, wing, date_posted)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_DATE)
        ''', (user['id'], user['full_name'], data['class'], data['section'], data['subject'], data['content'], data['wing']))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()


@app.route('/api/diary/student-view')
@login_required
def get_student_diary():
    user = session['user']
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    s_class = user.get('student_class')
    s_sec = user.get('student_section')
    s_wing = user.get('wing')
    query = 'SELECT * FROM apsokara_dailydiary WHERE class=? AND section=? AND wing=? ORDER BY id DESC LIMIT 15'
    rows = conn.execute(query, (s_class, s_sec, s_wing)).fetchall()
    query = 'SELECT * FROM apsokara_dailydiary WHERE class=? AND section=? AND wing=? ORDER BY id DESC LIMIT 15'
    rows = conn.execute(query, (s_class, s_sec, s_wing)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])
        .app-body { flex: 1; overflow-y: auto; padding: 20px 20px 100px; }
        .app-nav { position: absolute; bottom: 0; width: 100%; height: 75px; background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); display: flex; justify-content: space-around; align-items: center; border-top: 1px solid #f1f5f9; z-index: 100; left: 0; }
        .nav-btn { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; }
        .nav-btn span:last-child { font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
        .active-nav span { color: #1B4332 !important; }
        .glass-card { background: white; border-radius: 20px; padding: 18px; border: 1px solid #f1f5f9; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
        .hidden { display: none !important; }
        .btn-sync { background: #1B4332; color: white; width: 100%; padding: 15px; border-radius: 15px; font-weight: 800; margin-top: 20px; }

        .status-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800; }
        {% if user.role == 'Student' %}
        .teacher-only { display: none !important; }
        {% endif %}

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
                    <p class="text-[#D4AF37] text-[10px] font-bold tracking-widest uppercase mt-1 opacity-90">Official School Portal</p>
                </div>

                <div class="p-8">
                    <div class="flex bg-gray-100 p-1 rounded-xl mb-8 border border-gray-200">
                        <button onclick="setRole('Student')" id="sBtn" class="flex-1 py-3 rounded-lg font-black text-[11px] bg-[#D4AF37] text-[#1B4332] shadow-sm transition-all">STUDENT</button>
                        <button onclick="setRole('Teacher')" id="tBtn" class="flex-1 py-3 rounded-xl font-black text-[11px] text-gray-400 transition-all">STAFF</button>
                    </div>

                    <div class="space-y-5">
                        <div class="relative">
                            <label class="text-[10px] font-bold text-gray-400 uppercase ml-1">Identity ID</label>
                            <input type="text" id="uid" placeholder="Enter ID Number"
                                class="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 mt-1 outline-none font-bold text-[#1B4332] focus:border-[#1B4332] transition-all">
                        </div>

                        <div class="relative">
                            <label class="text-[10px] font-bold text-gray-400 uppercase ml-1">Date of Birth</label>
                            <input type="date" id="dob" value="2010-01-01"
                                class="w-full bg-gray-50 border border-gray-200 rounded-xl p-4 mt-1 outline-none font-bold text-[#1B4332] focus:border-[#1B4332] transition-all">
                        </div>

                        <button onclick="doLogin()"
                            class="w-full bg-[#1B4332] text-white py-4 rounded-xl font-black text-sm shadow-lg active:scale-95 transition-all mt-6 uppercase tracking-widest">
                            Sign In
                        </button>
                    </div>
                </div>

                <div class="pb-8 text-center">
                    <p class="text-[8px] text-gray-400 font-bold tracking-widest uppercase italic">APS Academic Ledger</p>
                </div>
            </div>
        </div>
        {% else %}

















        <div id="main-header" class="app-header shadow-md p-4 bg-gradient-to-r from-[#1B4332] to-[#2D6A4F]">
            <div class="flex justify-between items-center mb-3 opacity-80 border-b border-white/10 pb-2">
                <span id="current-date" class="text-[9px] font-bold tracking-tighter uppercase">-- --- ----</span>
                <span id="current-time" class="text-[9px] font-black tracking-widest text-[#D4AF37]">00:00:00</span>
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
        </script>






        <div class="app-body">

            <div id="page-diary-hub" class="hidden space-y-4">
                <button onclick="showTab('home')" class="text-[10px] font-black text-gray-400">← HOME</button>
                <div onclick="initTeacherDiary()" class="glass-card flex items-center p-5 border-l-8 border-[#1B4332] active:scale-95 transition-all">
                    <div class="text-3xl mr-4">📝</div>
                    <div><h4 class="font-black text-sm uppercase">Publish Diary</h4><p class="text-[9px] text-gray-400 font-bold">Post New Homework</p></div>
                </div>
                <div onclick="loadTeacherHistory()" class="glass-card flex items-center p-5 border-l-8 border-[#D4AF37] opacity-60">
                    <div class="text-3xl mr-4">📂</div>
                    <div><h4 class="font-black text-sm uppercase">Manage History</h4><p class="text-[9px] text-gray-400 font-bold">Past Records</p></div>
                </div>
            </div>


            <div id="page-diary-grid" class="hidden space-y-4">
                <button onclick="showTab('diary-hub')" class="text-[10px] font-black text-gray-400">← BACK</button>
                <div class="sticky top-0 bg-white/95 backdrop-blur-md pb-3 z-10">
                    <h3 class="font-black text-2xl text-[#1B4332] uppercase tracking-tighter">Choose Class</h3>
                    <input type="text" id="diary-search" onkeyup="filterDiaryClasses()" placeholder="🔍 Search class or subject..." class="w-full p-4 mt-2 rounded-2xl bg-gray-50 border-2 border-gray-100 font-bold text-sm outline-none focus:border-[#1B4332]">
                </div>
                <div id="diary-classes-container" class="grid grid-cols-1 gap-4"></div>
            </div>

            <div id="page-diary-editor" class="hidden space-y-4">
                <button onclick="showTab('diary-grid')" class="text-[10px] font-black text-gray-400">← BACK</button>
                <div class="glass-card shadow-2xl p-6 border-t-8 border-[#1B4332]">
                    <h3 id="ed-title" class="font-black text-2xl text-[#1B4332]">Subject</h3>
                    <p id="ed-sub" class="text-[10px] font-black text-[#D4AF37] mb-4 uppercase"></p>
                    <textarea id="diary-content" rows="6" class="w-full bg-gray-50 rounded-2xl p-4 text-sm font-bold border-2 border-gray-100 focus:border-[#1B4332] outline-none" placeholder="Write homework or announcement..."></textarea>

                    <div class="mt-4 space-y-3">
                        <div class="flex items-center justify-between bg-gray-50 p-4 rounded-2xl border-2 border-dashed border-gray-200" onclick="document.getElementById('diary-files').click()">
                            <div class="flex items-center gap-3">
                                <span class="text-xl">📎</span>
                                <div class="text-left">
                                    <p class="text-[10px] font-black text-gray-500 uppercase">Attachments</p>
                                    <p id="file-count" class="text-[9px] font-bold text-[#1B4332]">UP TO 100 FILES</p>
                                </div>
                            </div>
                            <input type="file" id="diary-files" multiple class="hidden" onchange="document.getElementById('file-count').innerText = this.files.length + ' FILES SELECTED'">
                        </div>

                        <div class="flex items-center justify-between bg-gray-100 p-4 rounded-2xl">
                            <label class="text-[10px] font-black text-gray-500">⏰ SCHEDULE POST?</label>
                            <input type="checkbox" id="is-sched" class="w-6 h-6 accent-[#1B4332]" onchange="document.getElementById('sched-date-box').classList.toggle('hidden', !this.checked)">
                        </div>
                        <div id="sched-date-box" class="hidden animate-pulse">
                            <input type="date" id="sched-date" class="w-full p-4 rounded-2xl border-2 border-[#D4AF37] font-bold text-sm">
                        </div>
                    </div>
                    <button onclick="submitDiary()" class="w-full bg-[#1B4332] text-white py-5 rounded-2xl font-black mt-6 shadow-xl active:scale-95 transition-all">🚀 PUBLISH DIARY</button>
                </div>
            </div>

            <div id="page-diary-history" class="hidden space-y-4">
                <button onclick="showTab('diary-hub')" class="text-[10px] font-black text-gray-400">← BACK</button>
                <h3 class="font-black text-2xl text-[#1B4332]">MY HISTORY</h3>
                <div id="history-list" class="space-y-4 pb-20"></div>
            </div>

            <div id="page-home" class="grid grid-cols-2 gap-4">
                {% if user.role == 'Teacher' and user.is_class_teacher %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-green-600 active:scale-95 transition-all">
                    <div class="text-4xl mb-3 drop-shadow-md">📋</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Attendance</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Mark Daily Presence</p>
                </div>
                {% endif %}

                <div onclick="openDiarySystem()" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-yellow-500 active:scale-95 transition-all">
                    <div class="text-4xl mb-3 drop-shadow-md">📒</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Class Diary</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">Manage Work</p>
                </div>

                {% if user.role == 'Student' %}
                <div onclick="showTab('mark')" class="glass-card flex flex-col items-center justify-center p-6 text-center border-b-4 border-blue-600 active:scale-95 transition-all cursor-pointer">
                    <div class="text-4xl mb-3 drop-shadow-md">📊</div>
                    <h4 class="font-black text-[11px] uppercase tracking-tighter">Reports</h4>
                    <p class="text-[8px] opacity-60 font-bold mt-1">View Progress</p>
                </div>

            <div id="page-diary-hub" class="hidden space-y-4">
                <h3 class="font-black text-xl text-[#1B4332]">Diary Hub</h3>
                <div onclick="initTeacherDiary()" class="glass-card flex items-center p-5 border-l-8 border-[#1B4332] active:scale-95 transition-all">
                    <div class="text-3xl mr-4">📝</div>
                    <div><h4 class="font-black text-sm uppercase">Publish Diary</h4><p class="text-[9px] text-gray-400 font-bold">Post New Homework</p></div>
                </div>
                <div onclick="loadTeacherHistory()" class="glass-card flex items-center p-5 border-l-8 border-[#D4AF37] opacity-60">
                    <div class="text-3xl mr-4">📂</div>
                    <div><h4 class="font-black text-sm uppercase">Manage History</h4><p class="text-[9px] text-gray-400 font-bold">Past Records</p></div>
                </div>
            </div>

            <div id="page-diary-grid" class="hidden space-y-4">
                <button onclick="showTab('diary-hub')" class="text-[10px] font-black text-gray-400">← BACK</button>
                <h3 class="font-black text-[#1B4332] text-center uppercase">Select Class</h3>
                <div id="diary-classes-container" class="grid grid-cols-2 gap-4"></div>
            </div>

            <div id="page-diary-editor" class="hidden space-y-4">
                <button onclick="showTab('diary-grid')" class="text-[10px] font-black text-gray-400">← BACK</button>
                <div class="glass-card">
                    <h4 id="editor-subtitle" class="text-[10px] font-black text-[#D4AF37] mb-1"></h4>
                    <h3 id="editor-title" class="font-black text-[#1B4332] mb-4 uppercase">Subject</h3>
                    <textarea id="diary-text" rows="8" class="w-full bg-gray-50 rounded-2xl p-4 text-sm font-bold outline-none border-2 border-transparent focus:border-[#1B4332]" placeholder="Write homework details here..."></textarea>
                    <button onclick="saveDiary()" class="w-full bg-[#1B4332] text-white py-4 rounded-xl font-black mt-4 shadow-lg active:scale-95 transition-all">🚀 PUBLISH NOW</button>
                </div>
            </div>

            <div id="page-diary-student" class="hidden space-y-4">
                <h3 class="font-black text-xl text-[#1B4332]">Class Diary</h3>
                <div id="student-diary-list" class="space-y-4"></div>
            </div>
                {% endif %}
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
                <div onclick="openAttendanceTab('intel')" class="glass-card flex items-center p-5 border-l-8 border-blue-600">
                    <div class="text-3xl mr-4">💎</div>
                    <div><h4 class="font-black text-sm">INTEL</h4><p class="text-[10px] text-gray-400">Analytics</p></div>
                </div>
            </div>

            <div id="page-marking-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400 uppercase tracking-widest">← Back</button>
                <div id="lock-banner"></div>
                <div id="marking-list" class="space-y-3"></div>
                <div id="marking-footer"></div>
            </div>

            <div id="page-archive-view" class="hidden space-y-4">
                <button onclick="showTab('mark')" class="text-[10px] font-black text-gray-400">← Back</button>
                <input type="date" id="archive-date" onchange="loadArchive()" placeholder="Select date for specific day" class="w-full p-3 rounded-xl bg-gray-50 border-none font-bold">
                <div id="archive-results" class="space-y-2"></div>
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


                    <button onclick="window.location.href='/logout'" class="w-full bg-red-50 text-red-600 py-4 rounded-2xl font-black text-sm border border-red-100 mt-4">LOGOUT SESSION</button>
                </div>
            </div>

        </div>

        <div class="app-nav">
            <div onclick="showTab('home')" id="n-home" class="nav-btn active-nav"><span>🏠</span><span>Home</span></div>
            {% if user.role == 'Student' or (user.role == 'Teacher' and user.is_class_teacher) %}
            <div onclick="showTab('mark')" id="n-mark" class="nav-btn"><span>📋</span><span>{{ 'History' if user.role == 'Student' else 'Attend' }}</span></div>
            {% endif %}
            <div onclick="showTab('profile')" id="n-profile" class="nav-btn"><span>👤</span><span>Profile</span></div>
            <div onclick="window.location.href='/logout'" class="nav-btn text-red-400"><span>🚪</span><span>Exit</span></div>
        </div>
        {% endif %}
    </div>

    <script>
        let currentEditCount = 0;
        let isLocked = false;

        function setRole(r) {
            window.currentRole = r;
            document.getElementById('dob').value = (r === 'Teacher') ? '1990-01-01' : '2010-01-01';
            document.getElementById('sBtn').className = r === 'Student' ? "flex-1 py-3 rounded-xl font-black text-sm bg-[#D4AF37] text-[#1B4332]" : "flex-1 py-3 rounded-xl font-black text-sm text-gray-400";
            document.getElementById('tBtn').className = r === 'Teacher' ? "flex-1 py-3 rounded-xl font-black text-sm bg-[#D4AF37] text-[#1B4332]" : "flex-1 py-3 rounded-xl font-black text-sm text-gray-400";
        }
        window.currentRole = 'Student';

        async function doLogin() {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({uid: document.getElementById('uid').value, dob: document.getElementById('dob').value, role: window.currentRole})
            });
            const data = await res.json();
            if(data.success) window.location.reload(); else alert("Login Failed!");
        }


        let selectedTask = null;
        function openDiarySystem() {
            const role = '{{ user.role }}';
            if (role === 'Teacher') showTab('diary-hub');
            else loadStudentDiary();
        }

        async function initTeacherDiary() {
            const res = await fetch('/api/diary/teacher-classes');
            const data = await res.json();
            const container = document.getElementById('diary-classes-container');
            if(!data.length) { alert("No assigned classes found."); return; }
            container.innerHTML = data.map(c => `
                <div onclick='openEditor(${JSON.stringify(c)})' class="bg-[#1B4332] p-5 rounded-[2rem] border-2 border-[#D4AF37] text-center active:scale-90 transition-all shadow-md">
                    <div class="text-white font-black text-sm">${c.student_class}-${c.section}</div>
                    <div class="text-[#D4AF37] text-[8px] font-bold uppercase mt-1">${c.sub_name}</div>
                </div>
            `).join('');
            showTab('diary-grid');
        }

        function openEditor(c) {
            selectedTask = c;
            document.getElementById('editor-title').innerText = c.sub_name;
            document.getElementById('editor-subtitle').innerText = "CLASS " + c.student_class + "-" + c.section;
            showTab('diary-editor');
        }

        async function saveDiary() {
            const content = document.getElementById('diary-text').value;
            if(!content) return alert("Please enter content");
            const res = await fetch('/api/diary/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    class: selectedTask.student_class, section: selectedTask.section,
                    subject: selectedTask.sub_name, wing: selectedTask.wing, content: content
                })
            });
            if((await res.json()).success) {
                alert("✅ Diary Published!");
                document.getElementById('diary-text').value = '';
                showTab('diary-hub');
            }
        }

        async function loadStudentDiary() {
            showTab('diary-student');
            const res = await fetch('/api/diary/student-view');
            const data = await res.json();
            const list = document.getElementById('student-diary-list');
            list.innerHTML = data.length ? data.map(d => `
                <div class="glass-card border-l-4 border-[#1B4332] mb-3 p-4 bg-white shadow-sm">
                    <div class="flex justify-between items-start mb-2">
                        <span class="font-black text-[#1B4332] text-sm">${d.subject}</span>
                        <span class="text-[9px] font-bold text-gray-400">${d.date_posted}</span>
                    </div>
                    <p class="text-[12px] font-bold text-gray-700 leading-relaxed">${d.content}</p>
                    <div class="mt-3 text-[9px] font-black text-[#D4AF37] uppercase">Teacher: ${d.teacher_name}</div>
                </div>
            `).join('') : '<div class="text-center py-10"><p class="font-bold text-gray-300 uppercase text-xs">No diary entries found.</p></div>';
        }


        let allMyClasses = [];
        async function initTeacherDiary() {
            const res = await fetch('/api/diary/teacher-classes');
            allMyClasses = await res.json();
            renderDiaryGrid(allMyClasses);
            showTab('diary-grid');
        }

        function renderDiaryGrid(data) {
            const container = document.getElementById('diary-classes-container');
            container.innerHTML = data.map(c => `
                <div onclick='openDiaryEditor(${JSON.stringify(c)})' class="bg-white border-2 border-gray-100 p-5 rounded-[2rem] shadow-sm active:scale-95 transition-all flex justify-between items-center">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="bg-[#1B4332] text-white text-[9px] px-2 py-0.5 rounded-full font-black uppercase">${c.wing}</span>
                            <span class="text-[#D4AF37] text-[10px] font-black uppercase">${c.sub_name}</span>
                        </div>
                        <h2 class="text-xl font-black text-gray-800 mt-1">CLASS ${c.student_class}-${c.section}</h2>
                    </div>
                    <div class="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center text-[#1B4332] font-black">→</div>
                </div>
            `).join('');
        }

        function filterDiaryClasses() {
            const q = document.getElementById('diary-search').value.toLowerCase();
            const filtered = allMyClasses.filter(c => (c.sub_name + c.student_class + c.section).toLowerCase().includes(q));
            renderDiaryGrid(filtered);
        }

        function openDiaryEditor(c) {
            window.selectedDiaryClass = c;
            document.getElementById('ed-title').innerText = c.sub_name;
            document.getElementById('ed-sub').innerText = `CLASS ${c.student_class}-${c.section} | ${c.wing} WING`;
            showTab('diary-editor');
        }

        async function submitDiary() {
            const content = document.getElementById('diary-content').value;
            if(!content) return alert("Please enter diary content!");

            const fd = new FormData();
            fd.append('content', content);
            fd.append('class', selectedDiaryClass.student_class);
            fd.append('section', selectedDiaryClass.section);
            fd.append('subject', selectedDiaryClass.sub_name);
            fd.append('wing', selectedDiaryClass.wing);
            fd.append('is_scheduled', document.getElementById('is-sched').checked ? '1' : '0');
            fd.append('post_date', document.getElementById('sched-date').value);

            const files = document.getElementById('diary-files').files;
            for(let i=0; i<files.length; i++) fd.append('files', files[i]);

            const res = await fetch('/api/diary/submit', { method: 'POST', body: fd });
            const data = await res.json();
            if(data.success) {
                alert("✅ Diary Published Successfully!");
                document.getElementById('diary-content').value = '';
                showTab('diary-hub');
            }
        }

        async function loadTeacherHistory() {
            showTab('diary-history');
            const res = await fetch('/api/diary/teacher-history');
            const data = await res.json();
            const list = document.getElementById('history-list');
            list.innerHTML = data.map(d => `
                <div class="glass-card p-5 border-l-4 border-${d.is_scheduled ? '[#D4AF37]' : '[#1B4332]'}">
                    <div class="flex justify-between items-start">
                        <p class="text-[9px] font-black text-gray-400 uppercase">${d.date_posted}</p>
                        ${d.is_scheduled ? '<span class="text-[8px] bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded font-black">SCHEDULED</span>' : ''}
                    </div>
                    <h4 class="font-black text-sm text-[#1B4332] mt-1">${d.subject} - CLASS ${d.student_class}-${d.section}</h4>
                    <p class="text-xs font-bold text-gray-600 mt-2 line-clamp-3">${d.content}</p>
                    ${d.attachments ? `<p class="text-[9px] text-blue-600 font-black mt-2">📎 ${d.attachments.split(',').length} Attachments</p>` : ''}
                </div>
            `).join('') || '<p class="text-center py-10 text-gray-300 font-bold">No history found.</p>';
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

            const pages = ['home', 'mark', 'profile', 'marking-view', 'archive-view', 'intel-view', 'diary-hub', 'diary-grid', 'diary-editor', 'diary-student', 'diary-history'];
            pages.forEach(p => {
                const el = document.getElementById('page-' + p);
                if (el) el.classList.add('hidden');
            });
            if (document.getElementById("page-" + t)) document.getElementById("page-" + t).classList.remove("hidden");

            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active-nav'));

            const targetPage = document.getElementById('page-' + t);
            if (targetPage) targetPage.classList.remove('hidden');

            if(document.getElementById('n-' + t)) document.getElementById('n-' + t).classList.add('active-nav');

            // --- HEADER VISIBILITY LOGIC ---
            const header = document.getElementById('main-header');
            const fullScreenPages = ['marking-view', 'archive-view', 'intel-view'];
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
                showTab('marking-view');
                loadMarkingInterface();
            } else {
                showTab(type + '-view');
                if(type === 'archive') loadArchive();
                if(type === 'intel') loadIntel();
            }
        }

        async function loadMarkingInterface() {
            const list = document.getElementById('marking-list');
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
            list.innerHTML = data.students.map(s => `
                <div class="glass-card flex justify-between items-center">
                    <div><p class="text-[9px] font-bold text-gray-400">#${s.roll_number}</p><h4 class="font-black text-sm">${s.full_name}</h4></div>
                    ${isLocked ? `<span class="status-pill ${s.status === 'Present' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">${s.status}</span>` : `
                    <select id="s_${s.id}" class="text-xs font-black bg-gray-50 p-2 rounded-lg border-none outline-none">
                        <option value="Present" ${s.status === 'Present' ? 'selected' : ''}>Present</option>
                        <option value="Absent" ${s.status === 'Absent' ? 'selected' : ''}>Absent</option>
                        <option value="Leave" ${s.status === 'Leave' ? 'selected' : ''}>Leave</option>
                    </select>`}
                </div>
            `).join('');
        }

        async function syncAttendance() {
            if(!confirm("Are you sure? This action might lock the record.")) return;
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
                alert("❌ Verification Failed!");
            }
        }


        async function loadIntel() {
            const res = await fetch('/api/intel');
            const data = await res.json();
            document.getElementById('intel-flags').innerHTML = data.flags.map(f => `
                <div class="flex justify-between items-center p-2 border-b border-red-100 text-xs font-bold">
                    <span>${f.full_name}</span><span class="text-red-600">${f.perc}%</span>
                </div>
            `).join('') || "Perfect attendance across section!";
        }
    </script>
</body>
</html>
'''

# --- BACKEND ROUTES ---


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
    # Get students and their today's status if exists
    cur = conn.execute("""SELECT s.id, s.full_name, s.roll_number, a.status
                        FROM apsokara_student s
                        LEFT JOIN apsokara_attendance a ON s.id = a.student_id AND a.date=?
                        WHERE s.student_class=? AND s.student_section=? AND s.wing=?
                        ORDER BY CAST(s.roll_number AS INTEGER)""", (today, u['assigned_class'], u['assigned_section'], u['wing']))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({"students": rows})

@app.route('/api/sync-attendance', methods=['POST'])
@login_required
def sync_attendance():
    u = session['user']
    today = datetime.datetime.now(PK_TZ).date().isoformat()
    data = request.json.get('attendance', [])

    conn = sqlite3.connect(DB_PATH)
    try:
        # Get current edit count
        res = conn.execute("""SELECT MAX(edit_count) FROM apsokara_attendance a
                            JOIN apsokara_student s ON a.student_id = s.id
                            WHERE a.date=? AND s.student_class=? AND s.student_section=? AND s.wing=?""",
                            (today, u['assigned_class'], u['assigned_section'], u['wing'])).fetchone()
        count = (res[0] if res[0] is not None else 0)

        if count >= 2:
            return jsonify({"success": False, "error": "Record is Locked!"})

        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE TRANSACTION;")
        # Delete old entries for today
        cur.execute("""DELETE FROM apsokara_attendance WHERE date=? AND student_id IN
                     (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)""",
                     (today, u['assigned_class'], u['assigned_section'], u['wing']))

        # Insert new entries with incremented count
        final_data = [(s['id'], s['status'], today, count+1, u['full_name']) for s in data]
        cur.executemany("INSERT INTO apsokara_attendance (student_id, status, date, edit_count, marked_by) VALUES (?,?,?,?,?)", final_data)
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

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
                        WHERE s.student_class=? AND s.student_section=? AND s.wing=? GROUP BY s.id""", (u['assigned_class'], u['assigned_section'], u['wing']))
    flags = []
    for r in cur.fetchall():
        perc = (r['pres'] / r['total'] * 100) if r['total'] > 0 else 100
        if perc < 75: flags.append({"full_name": r['full_name'], "perc": int(perc)})
    conn.close()
    return jsonify({"flags": flags})

@app.route('/logout')
def logout():
    session.clear()
    return '<script>window.location.href="/";</script>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

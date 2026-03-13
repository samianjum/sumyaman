import re

fname = 'mobile_app.py'
with open(fname, 'r') as f:
    content = f.read()

# 1. Update the Marks Entry UI (Replacing the placeholder)
new_ui = """
    <div id='page-marks-entry' class='hidden space-y-4 pb-24'>
        <div class='flex items-center justify-between mb-2'>
            <h3 class='font-black text-xl text-[#1B4332] uppercase tracking-tighter'>Marks Entry</h3>
            <button onclick="showTab('home')" class='bg-gray-100 px-3 py-1 rounded-lg text-[10px] font-black text-gray-500 tracking-widest'>BACK</button>
        </div>
        
        <div class="glass-card p-4 border-l-4 border-indigo-600 mb-4">
            <label class="text-[9px] font-black text-gray-400 uppercase mb-2 block">Select Subject & Class</label>
            <select id="marks-assignment-id" onchange="loadStudentsForMarks()" class="w-full p-3 rounded-xl bg-gray-50 border-none text-xs font-bold focus:ring-2 focus:ring-indigo-500">
                <option value="">Loading Assignments...</option>
            </select>
        </div>

        <div id="active-exam-banner" class="hidden bg-indigo-900 p-4 rounded-2xl text-white mb-4 shadow-lg">
            <div class="flex justify-between items-center">
                <div>
                    <p class="text-[8px] font-black text-indigo-300 uppercase">Active Session</p>
                    <h4 id="exam-name-display" class="font-black text-sm uppercase">---</h4>
                </div>
                <div class="text-right">
                    <p class="text-[8px] font-black text-indigo-300 uppercase">Closing</p>
                    <p id="exam-date-display" class="text-[10px] font-bold">---</p>
                </div>
            </div>
        </div>

        <div id="marks-students-container" class="space-y-3">
            </div>
        
        <div id="marks-footer" class="hidden mt-6">
            <button onclick="submitMarks()" class="w-full bg-[#1B4332] text-white p-4 rounded-2xl font-black shadow-xl active:scale-95 transition-all text-sm uppercase tracking-widest">
                Authorize & Commit Data
            </button>
        </div>
    </div>
"""

# Surgical Replace for the UI
content = re.sub(r"<div id='page-marks-entry'.*?", new_ui + "\n    ", content, flags=re.DOTALL)

# 2. Add the API Routes for Marks (Fetching Exams and Subjects)
marks_api = """
@app.route('/api/teacher/get-marks-init')
@login_required
def get_marks_init():
    u = session['user']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    today = datetime.datetime.now().date().isoformat()
    
    # Get Active Exam
    exam = conn.execute('SELECT * FROM exams WHERE is_active=1 AND start_date <= ? AND end_date >= ? LIMIT 1', (today, today)).fetchone()
    
    # Get Teacher Assignments
    query = \"\"\"
        SELECT sa.id, sa.student_class, sa.section, sa.wing, s.name as sub_name, s.id as sub_id 
        FROM apsokara_subjectassignment sa 
        JOIN apsokara_subject s ON sa.subject_id = s.id 
        WHERE sa.teacher_id = ?
    \"\"\"
    assigns = conn.execute(query, (u['id'],)).fetchall()
    conn.close()
    
    return jsonify({
        'exam': dict(exam) if exam else None,
        'assignments': [dict(a) for a in assigns]
    })

@app.route('/api/teacher/get-students-for-marks')
@login_required
def get_students_for_marks():
    class_name = request.args.get('class')
    section = request.args.get('section')
    wing = request.args.get('wing')
    subject_id = request.args.get('subject_id')
    exam_id = request.args.get('exam_id')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get Students
    students = conn.execute('SELECT id, full_name, father_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=? ORDER BY CAST(roll_number AS INTEGER)', (class_name, section, wing)).fetchall()
    
    # Get Existing Marks
    marks_rows = conn.execute('SELECT student_id, obtained_marks, remarks FROM student_marks WHERE exam_id=? AND subject_id=?', (exam_id, subject_id)).fetchall()
    marks_map = {m['student_id']: {'obt': m['obtained_marks'], 'rem': m['remarks']} for m in marks_rows}
    
    conn.close()
    return jsonify({
        'students': [dict(s) for s in students],
        'existing_marks': marks_map
    })

@app.route('/api/teacher/save-marks', methods=['POST'])
@login_required
def save_marks():
    data = request.json
    u = session['user']
    exam_id = data.get('exam_id')
    subject_id = data.get('subject_id')
    marks_list = data.get('marks')
    
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        for m in marks_list:
            cur.execute('''INSERT OR REPLACE INTO student_marks 
                (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)''', 
                (exam_id, m['sid'], subject_id, u['id'], 100, m['obt'], m['rem']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()
"""

if '@app.route(\'/api/teacher/get-marks-init\')' not in content:
    content += "\n" + marks_api

with open(fname, 'w') as f:
    f.write(content)
print("✅ Python Backend Fixed!")

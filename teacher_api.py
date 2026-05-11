from flask import jsonify, session, request
import pg_shim as sqlite3, datetime, pytz

DB_PATH = 'db.sqlite3'
PK_TZ = pytz.timezone("Asia/Karachi")

def init_teacher_routes(app, login_required):
    @app.route('/api/teacher/init_marks')
    @login_required
    def init_marks():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        uid = session['user']['id']
        today = datetime.datetime.now(PK_TZ).strftime('%Y-%m-%d')
        q = 'SELECT DISTINCT e.* FROM exams e JOIN apsokara_subjectassignment sa ON sa.student_class = e.class_group WHERE e.is_active = 1 AND ? BETWEEN e.start_date AND e.end_date AND sa.teacher_id = ?'
        exams = conn.execute(q, (today, uid)).fetchall()
        conn.close()
        return jsonify({'exams': [dict(ix) for ix in exams]})

    @app.route('/api/teacher/assignments_v2/<int:exam_id>')
    @login_required
    def get_assignments_v2(exam_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        uid = session['user']['id']
        exam = conn.execute('SELECT class_group FROM exams WHERE id = ?', (exam_id,)).fetchone()
        if not exam: return jsonify([])
        # Added sa.wing here specifically
        q = 'SELECT sa.id, sa.student_class, sa.section, sa.wing, sub.name as sub_name, sub.id as sub_id FROM apsokara_subjectassignment sa JOIN apsokara_subject sub ON sa.subject_id = sub.id WHERE sa.teacher_id = ? AND sa.student_class = ?'
        assigns = conn.execute(q, (uid, exam['class_group'])).fetchall()
        conn.close()
        return jsonify([dict(a) for a in assigns])

    @app.route('/api/teacher/students_v2/<int:exam_id>/<int:sub_id>')
    @login_required
    def get_students_v2(exam_id, sub_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        uid = session['user']['id']
        assign_info = conn.execute('SELECT student_class, section, wing FROM apsokara_subjectassignment WHERE subject_id=? AND teacher_id=?', (sub_id, uid)).fetchone()
        locked = False
        if assign_info:
            q_lock = 'SELECT id FROM student_marks WHERE exam_id=? AND CAST(subject_id AS INTEGER)=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?) LIMIT 1'
            if conn.execute(q_lock, (exam_id, assign_info['student_class'], assign_info['section'], assign_info['wing'])).fetchone(): locked = True
        q_students = 'SELECT s.id, s.full_name, s.roll_number, m.obtained_marks, m.remarks, m.total_marks FROM apsokara_student s JOIN apsokara_subjectassignment sa ON s.student_class = sa.student_class AND s.student_section = sa.section AND s.wing = sa.wing LEFT JOIN student_marks m ON s.id = m.student_id AND m.exam_id = ? AND m.subject_id = ? WHERE sa.subject_id = ? AND sa.teacher_id = ?'
        students = conn.execute(q_students, (exam_id, sub_id, sub_id, uid)).fetchall()
        conn.close()
        return jsonify({'students': [dict(s) for s in students], 'locked': locked})

    @app.route('/api/teacher/save_marks', methods=['POST'])
    @login_required
    def save_marks():
        data = request.json
        conn = sqlite3.connect(DB_PATH)
        try:
            for m in data['marks']:
                conn.execute('INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, ?, ?, ?, ?, ?, 0)', (data['exam_id'], m['sid'], data['sub_id'], session['user']['id'], data['total_marks'], m['obt'], m['rem']))
            conn.commit()
            return jsonify({'status': 'success'})
        except Exception as e: return jsonify({'status': 'error', 'msg': str(e)})
        finally: conn.close()

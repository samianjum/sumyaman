import sqlite3, datetime, pytz
from flask import jsonify, session, request

def add_routes(app, DB_PATH, PK_TZ, login_required):
    @app.route('/api/class-finalize-status')
    @login_required
    def class_finalize_status():
        u = session['user']
        conn = sqlite3.connect(DB_PATH)
        today = datetime.datetime.now(PK_TZ).date().isoformat()
        exam = conn.execute("SELECT id, name FROM exams WHERE is_active=1 AND start_date <= ? AND end_date >= ? ORDER BY id DESC LIMIT 1", (today, today)).fetchone()
        if not exam: return jsonify({"success": False, "error": "No Active Exam Session Found"})
        ex_id, ex_name = exam
        subjects = conn.execute('''SELECT s.id, s.name, t.full_name FROM apsokara_subjectassignment sa JOIN apsokara_subject s ON sa.subject_id = s.id JOIN apsokara_teacher t ON sa.teacher_id = t.id WHERE sa.student_class=? AND sa.section=? AND sa.wing=?''', (u['assigned_class'], u['assigned_section'], u['wing'])).fetchall()
        status_list = []; all_submitted = True
        for sid, sname, tname in subjects:
            count = conn.execute('''SELECT COUNT(*) FROM student_marks WHERE exam_id=? AND subject_id=? AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)''', (ex_id, sid, u['assigned_class'], u['assigned_section'], u['wing'])).fetchone()[0]
            submitted = count > 0
            if not submitted: all_submitted = False
            status_list.append({"subject": sname, "teacher": tname, "submitted": submitted})
        performance = []
        if all_submitted:
            students = conn.execute("SELECT id, full_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?", (u['assigned_class'], u['assigned_section'], u['wing'])).fetchall()
            for sid, sname, sroll in students:
                marks = conn.execute("SELECT SUM(obtained_marks), SUM(total_marks) FROM student_marks WHERE exam_id=? AND student_id=?", (ex_id, sid)).fetchone()
                obt, tot = marks[0] or 0, marks[1] or 0
                perc = round((obt/tot*100), 1) if tot > 0 else 0
                performance.append({"id": sid, "name": sname, "roll": sroll, "perc": perc, "total": tot, "obtained": obt})
        conn.close()
        return jsonify({"success": True, "exam_name": ex_name, "exam_id": ex_id, "status": status_list, "is_ready": all_submitted, "performance": performance})

    @app.route('/api/publish-final-result', methods=['POST'])
    @login_required
    def publish_final_result():
        data = request.json
        u, ex_id, remarks = session['user'], data.get('exam_id'), data.get('remarks', {})
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            for sid, rmk in remarks.items():
                stats = conn.execute("SELECT SUM(obtained_marks), SUM(total_marks) FROM student_marks WHERE exam_id=? AND student_id=?", (ex_id, sid)).fetchone()
                cur.execute('''INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, 0, ?, ?, ?, ?, 1)''', (ex_id, sid, u['id'], stats[1] or 0, stats[0] or 0, rmk))
            cur.execute('''UPDATE student_marks SET is_locked = 1 WHERE exam_id = ? AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)''', (ex_id, u['assigned_class'], u['assigned_section'], u['wing']))
            conn.commit()
            return jsonify({"success": True})
        except Exception as e: return jsonify({"success": False, "error": str(e)})
        finally: conn.close()

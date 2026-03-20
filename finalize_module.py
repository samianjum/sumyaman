import sqlite3
import datetime
import pytz
from flask import jsonify, session, request

PK_TZ = pytz.timezone('Asia/Karachi')

def init_finalize_routes(app, DB_PATH):
    @app.route('/api/class-finalize-status')
    def get_finalize_status_v2():
        u = session.get('user')
        if not u or not u.get('is_class_teacher'):
            return jsonify({"success": False, "error": "Unauthorized Access"})
        
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        today = datetime.datetime.now(PK_TZ).date().isoformat()
        cl, sec, wing = u['assigned_class'], u['assigned_section'], u['assigned_wing']
        
        try:
            exam = conn.execute("SELECT id, name FROM exams WHERE class_group=? AND is_active=1 AND start_date <= ? AND end_date >= ? ORDER BY id DESC LIMIT 1", (cl, today, today)).fetchone()
            if not exam: return jsonify({"success": True, "no_exam": True})
            
            ex_id = exam["id"]
            total_students = conn.execute("SELECT COUNT(*) FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?", (cl, sec, wing)).fetchone()[0]
            
            is_published = conn.execute('SELECT COUNT(*) FROM student_marks WHERE exam_id=? AND subject_id=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)', (ex_id, cl, sec, wing)).fetchone()[0] > 0
            
            subjects = conn.execute("""
                SELECT s.id, s.name, t.full_name as teacher,
                (SELECT COUNT(DISTINCT student_id) FROM student_marks WHERE exam_id=? AND subject_id=s.id 
                 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?)) as entries
                FROM apsokara_subjectassignment sa 
                JOIN apsokara_subject s ON sa.subject_id = s.id 
                JOIN apsokara_teacher t ON sa.teacher_id = t.id 
                WHERE sa.student_class=? AND sa.section=? AND sa.wing=?
            """, (ex_id, cl, sec, wing, cl, sec, wing)).fetchall()
            
            status_list = [{"id": r['id'], "subject": r['name'], "teacher": r['teacher'], "submitted": r['entries'] >= total_students and total_students > 0, "count": f"{r['entries']}/{total_students}"} for r in subjects]
            all_ready = all(s['submitted'] for s in status_list)
            
            students_data = []
            if all_ready and not is_published:
                st_rows = conn.execute("SELECT id, full_name, father_name FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?", (cl, sec, wing)).fetchall()
                for st in st_rows:
                    m = conn.execute('SELECT SUM(obtained_marks) as obt, SUM(total_marks) as tot FROM student_marks WHERE exam_id=? AND student_id=? AND subject_id > 0', (ex_id, st['id'])).fetchone()
                    obt, tot = (m['obt'] or 0), (m['tot'] or 0)
                    perc = round((obt/tot*100), 1) if tot > 0 else 0
                    students_data.append({"id": st['id'], "name": st['full_name'], "father_name": st['father_name'], "perc": perc, "obt": obt, "tot": tot})
            
            # Sort by percentage descending
            return jsonify({"success": True, "exam_name": exam['name'], "exam_id": ex_id, "is_published": is_published, "status": status_list, "is_ready": all_ready, "students": sorted(students_data, key=lambda x: x['perc'], reverse=True)})
        except Exception as e: return jsonify({"success": False, "error": str(e)})
        finally: conn.close()

    @app.route('/api/get-subject-marks-details')
    def get_sub_details():
        ex_id, sub_id = request.args.get('exam_id'), request.args.get('subject_id')
        u = session.get('user')
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        marks = conn.execute("""
            SELECT st.full_name, st.father_name, m.obtained_marks, m.total_marks 
            FROM student_marks m JOIN apsokara_student st ON m.student_id = st.id 
            WHERE m.exam_id=? AND m.subject_id=? AND st.student_class=? AND st.student_section=? AND st.wing=?
            ORDER BY m.obtained_marks DESC
        """, (ex_id, sub_id, u['assigned_class'], u['assigned_section'], u['assigned_wing'])).fetchall()
        
        # Calculate pass/fail (33% passing criteria)
        res = [{"name": r['full_name'], "father": r['father_name'], "obt": r['obtained_marks'], "tot": r['total_marks'], "is_pass": float(r['obtained_marks'] or 0) >= (float(r['total_marks'] or 1)*0.33)} for r in marks]
        conn.close()
        return jsonify({"success": True, "marks": res})

    @app.route('/api/get-student-report-card')
    def get_rep():
        ex_id, st_id = request.args.get('exam_id'), request.args.get('student_id')
        u = session.get('user')
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        
        # JOIN to get subject name AND teacher name
        marks = conn.execute("""
            SELECT s.name as subject_name, m.obtained_marks, m.total_marks, t.full_name as teacher_name
            FROM student_marks m 
            JOIN apsokara_subject s ON m.subject_id = s.id 
            JOIN apsokara_subjectassignment sa ON (s.id = sa.subject_id AND sa.student_class=? AND sa.section=? AND sa.wing=?)
            JOIN apsokara_teacher t ON sa.teacher_id = t.id
            WHERE m.exam_id=? AND m.student_id=? AND m.subject_id > 0
        """, (u['assigned_class'], u['assigned_section'], u['assigned_wing'], ex_id, st_id)).fetchall()
        
        conn.close()
        return jsonify({"success": True, "report": [dict(r) for r in marks]})

    @app.route('/api/publish-final-result', methods=['POST'])
    def publish_final():
        data = request.json; u = session.get('user'); ex_id = data.get('exam_id'); remarks = data.get('remarks', {})
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute("BEGIN TRANSACTION")
            for s_id, rmk in remarks.items():
                conn.execute("INSERT OR REPLACE INTO student_marks (exam_id, student_id, subject_id, teacher_id, total_marks, obtained_marks, remarks, is_locked) VALUES (?, ?, 0, ?, 0, 0, ?, 1)", (ex_id, s_id, u['id'], rmk))
                conn.execute("UPDATE student_marks SET is_locked=1 WHERE exam_id=? AND student_id=?", (ex_id, s_id))
            conn.commit(); return jsonify({"success": True})
        except: conn.rollback(); return jsonify({"success": False})
        finally: conn.close()

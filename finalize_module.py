import sqlite3
import datetime
import pytz
from flask import jsonify, session, request

PK_TZ = pytz.timezone('Asia/Karachi')

def init_finalize_routes(app, db_path_input):
    # Ensure DB_PATH is a string, not a function reference
    DB_PATH = db_path_input() if callable(db_path_input) else db_path_input

    @app.route('/api/class-finalize-status')
    def get_finalize_status_v2():
        u = session.get('user')
        if not u or not u.get('is_class_teacher'):
            return jsonify({"success": False, "error": "Unauthorized Access"})

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            today = datetime.datetime.now(PK_TZ).date().isoformat()
            cl, sec, wing = u['assigned_class'], u['assigned_section'], u['assigned_wing']

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

            conn.close()
            return jsonify({"success": True, "exam_name": exam['name'], "exam_id": ex_id, "is_published": is_published, "status": status_list, "is_ready": all_ready, "students": sorted(students_data, key=lambda x: x['perc'], reverse=True)})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    # ... baaki routes bhi isi logic pe update honge ...

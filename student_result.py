import pg_shim as sqlite3
from flask import jsonify, session

def init_student_routes(app, DB_PATH):
    @app.route('/api/student/my-results', methods=['GET'])
    def get_my_results():
        if 'user' not in session or session['user'].get('role') != 'Student':
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        s_id = session['user']['id']
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        try:
            student = conn.execute('SELECT * FROM apsokara_student WHERE id = ?', (s_id,)).fetchone()
            
            # Fetch exams (Badi ID first)
            exams_raw = conn.execute('''
                SELECT DISTINCT e.* FROM exams e
                JOIN student_marks m ON e.id = m.exam_id
                WHERE m.student_id = ? AND m.is_locked = 1 AND LENGTH(e.name) >= 1
                ORDER BY e.id DESC
            ''', (s_id,)).fetchall()
            
            exams_list = []
            for e_row in exams_raw:
                e_id, e_name, e_end = e_row['id'], e_row['name'], e_row['end_date']

                att = conn.execute('''
                    SELECT COUNT(*) as t, 
                    SUM(CASE WHEN status="Present" THEN 1 ELSE 0 END) as p 
                    FROM apsokara_attendance 
                    WHERE student_id=? AND date <= ?
                ''', (s_id, e_end)).fetchone()

                rank_res = conn.execute('''
                    SELECT student_id, SUM(obtained_marks) as obt 
                    FROM student_marks 
                    WHERE exam_id=? AND is_locked = 1
                    GROUP BY student_id 
                    ORDER BY obt DESC
                ''', (e_id,)).fetchall()
                
                pos = "N/A"
                for i, r in enumerate(rank_res):
                    if r['student_id'] == s_id:
                        rank_num = i + 1
                        if 11 <= rank_num <= 13: suffix = 'th'
                        else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(rank_num % 10, 'th')
                        pos = f"{rank_num}{suffix}"
                        break

                marks_res = conn.execute('''
                    SELECT m.*, s.name as sub_name, t.full_name as teacher 
                    FROM student_marks m 
                    LEFT JOIN apsokara_subject s ON m.subject_id = s.id 
                    LEFT JOIN apsokara_teacher t ON m.teacher_id = t.id
                    WHERE m.student_id=? AND m.exam_id=? AND m.is_locked = 1
                ''', (s_id, e_id)).fetchall()

                subjects = []
                ct_remark = "Maintain your focus on academic excellence."
                
                for m in marks_res:
                    if m['subject_id'] == 0 or m['sub_name'] is None:
                        if m['remarks']: ct_remark = m['remarks']
                    else:
                        subjects.append({
                            "name": m['sub_name'],
                            "obt": m['obtained_marks'],
                            "tot": m['total_marks'],
                            "rem": m['remarks'] or "Good performance.",
                            "teacher": m['teacher'] or "N/A"
                        })

                if subjects:
                    exams_list.append({
                        "id": e_id,
                        "name": e_name,
                        "subjects": subjects,
                        "ct_remark": ct_remark,
                        "pos": pos,
                        "start": e_row['start_date'],
                        "end": e_end,
                        "att": {"p": att['p'] or 0, "t": att['t'] or 0}
                    })

            # Strictly sort by ID to ensure latest is at index 0
            exams_list.sort(key=lambda x: x['id'], reverse=True)
            return jsonify({"success": True, "student": dict(student), "exams": exams_list})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
        finally:
            conn.close()

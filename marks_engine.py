import sqlite3
from flask import jsonify, request, session
from datetime import date

def init_marks_routes(app, login_required):
    
    @app.route('/api/marks/init')
    @login_required
    def marks_init():
        today = date.today().isoformat()
        tid = session['user']['id']
        conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
        q = """
            SELECT DISTINCT e.id, e.name, e.class_group, e.end_date 
            FROM exams e 
            JOIN apsokara_subjectassignment sa ON sa.student_class = e.class_group 
            WHERE e.is_active = 1 AND e.start_date <= ? AND e.end_date >= ? AND sa.teacher_id = ?
        """
        exams = conn.execute(q, (today, today, tid)).fetchall()
        conn.close()
        return jsonify([{'id': e[0], 'name': e[1], 'class_group': e[2], 'end': e[3]} for e in exams])

    @app.route('/api/marks/assignments/<int:eid>/<string:class_group>')
    @login_required
    def marks_assignments(eid, class_group):
        tid = session['user']['id']
        conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
        # Logic to check entry count and overall lock (subject_id=0) per assignment
        q = """
            SELECT sa.id, sa.student_class, sa.section, sa.wing, sub.name, sub.id,
            (SELECT COUNT(*) FROM student_marks m WHERE m.exam_id = ? AND m.subject_id = sub.id AND m.teacher_id = ?) as entry_count,
            (SELECT COUNT(*) FROM student_marks m2 WHERE m2.exam_id = ? AND CAST(m2.subject_id AS INTEGER) = 0 
             AND m2.student_id IN (SELECT id FROM apsokara_student WHERE student_class = sa.student_class AND student_section = sa.section AND wing = sa.wing)) as lock_flag
            FROM apsokara_subjectassignment sa 
            JOIN apsokara_subject sub ON sa.subject_id = sub.id 
            WHERE sa.teacher_id = ? AND sa.student_class = ?
        """
        data = conn.execute(q, (eid, tid, eid, tid, class_group)).fetchall()
        conn.close()
        return jsonify([{
            'class': d[1], 'sec': d[2], 'wing': d[3], 'sub_name': d[4], 'subject_id': d[5],
            'is_completed': d[6] > 0, 'is_locked': d[7] > 0
        } for d in data])

    @app.route('/api/marks/load_students', methods=['POST'])
    @login_required
    def load_students():
        d = request.json
        print(f"DEBUG DATA: {d}")
        conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
        conn.row_factory = sqlite3.Row
        
        lock_q = "SELECT id FROM student_marks WHERE exam_id=? AND CAST(subject_id AS INTEGER)=0 AND student_id IN (SELECT id FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?) LIMIT 1"
        locked = conn.execute(lock_q, (d['eid'], d['cls'], d['sec'], d['wing'])).fetchone() is not None
        
        q_stu = """
            SELECT s.id, s.full_name, s.roll_number, s.father_name, m.obtained_marks, m.remarks, m.total_marks
            FROM apsokara_student s
            LEFT JOIN student_marks m ON s.id = m.student_id AND m.exam_id = ? AND m.subject_id = ?
            WHERE s.student_class = ? AND s.student_section = ? AND s.wing = ?
            ORDER BY CAST(s.roll_number AS INTEGER)
        """
        rows = conn.execute(q_stu, (d['eid'], d.get('sid', d.get('subject_id')), d['cls'], d['sec'], d['wing'])).fetchall()
        conn.close()
        return jsonify({'students': [dict(r) for r in rows], 'locked': locked})

    
    
    
    
    @app.route('/api/marks/save', methods=['POST'])
    @login_required
    def marks_save():
        d = request.json
        print(f"DEBUG SAVE ATTEMPT: {d}")
        tid = session['user']['id']
        conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
        try:
            # Explicitly getting the ID
            sub_id = d.get('subject_id')
            eid = d.get('eid')
            total = d.get('total')
            
            for m in d['marks']:
                # m['sid'] is student_id from JS, m['obt'] is marks
                conn.execute('''
                    INSERT OR REPLACE INTO student_marks 
                    (exam_id, subject_id, student_id, total_marks, obtained_marks, remarks, teacher_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (eid, sub_id, m['sid'], total, m['obt'], m['rem'], tid))
            conn.commit()
            print(f"✅ SUCCESSFULLY SAVED {len(d['marks'])} RECORDS")
            return jsonify({'status': 'success'})
        except Exception as e:
            print(f"❌ SAVE FAILED: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            conn.close()
    
    
    
    

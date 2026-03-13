import sqlite3
from flask import jsonify, session, request

def get_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def patch_backend(app):
    @app.route('/api/teacher/assignments')
    def api_get_assignments():
        if 'user' not in session: return jsonify([])
        u = session['user']
        conn = get_db()
        # Query matching your sqlite3 schema
        q = '''SELECT sa.id, sa.student_class, sa.section, sa.wing, sub.name as sub_name, sub.id as sub_id 
               FROM apsokara_subjectassignment sa 
               JOIN apsokara_subject sub ON sa.subject_id = sub.id 
               WHERE sa.teacher_id = ?'''
        assigns = conn.execute(q, (u['id'],)).fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in assigns])

    @app.route('/api/teacher/students/<class_name>/<section>/<wing>')
    def api_get_students(class_name, section, wing):
        conn = get_db()
        students = conn.execute('SELECT id, full_name, roll_number FROM apsokara_student WHERE student_class=? AND student_section=? AND wing=?', (class_name, section, wing)).fetchall()
        conn.close()
        return jsonify([dict(ix) for ix in students])

# --- FRONTEND JS PATCH ---
# Ye function aapke HTML_TEMPLATE ke script section mein loadTeacherAssignments ko replace karega

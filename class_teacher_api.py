from flask import jsonify, request
import sqlite3

def get_db():
    db = sqlite3.connect('database.db')
    db.row_factory = sqlite3.Row
    return db

def register_class_teacher_routes(app, login_required):
    
    @app.route('/api/class-finalize-status')
    @login_required
    def finalize_status():
        from flask import session
        user_id = session.get('user_id')
        db = get_db()
        
        # Get teacher's class
        user = db.execute('SELECT assigned_class, assigned_section FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user: return jsonify({'success': False, 'error': 'User not found'})
        
        # Get current active exam
        exam = db.execute('SELECT id, exam_name FROM exams ORDER BY id DESC LIMIT 1').fetchone()
        if not exam: return jsonify({'success': False, 'error': 'No active exam found'})
        
        # Check if already published
        pub = db.execute('SELECT id FROM final_results WHERE exam_id = ? AND class_name = ? AND section = ?', 
                        (exam['id'], user['assigned_class'], user['assigned_section'])).fetchone()
        
        # Get status of all subjects for this class
        # Assuming you have a table 'marks_status' or similar
        subjects = db.execute('''
            SELECT subject_name, teacher_name, is_submitted 
            FROM marks_submissions 
            WHERE class_name = ? AND section = ? AND exam_id = ?
        ''', (user['assigned_class'], user['assigned_section'], exam['id'])).fetchall()
        
        status_list = [{'name': s['subject_name'], 'done': bool(s['is_submitted'])} for s in subjects]
        is_ready = all(s['done'] for s in status_list) if status_list else False
        
        # Get students for remarks if ready
        students = []
        if is_ready:
            st_data = db.execute('SELECT id, full_name, roll_no FROM users WHERE assigned_class = ? AND assigned_section = ? AND role = "Student"',
                               (user['assigned_class'], user['assigned_section'])).fetchall()
            students = [{'id': s['id'], 'name': s['full_name'], 'roll': s['roll_no'], 'perc': 0} for s in st_data]

        return jsonify({
            'success': True,
            'exam_name': exam['exam_name'],
            'exam_id': exam['id'],
            'is_published': bool(pub),
            'status': status_list,
            'is_ready': is_ready,
            'students': students
        })

    @app.route('/api/publish-final-result', methods=['POST'])
    @login_required
    def publish_result():
        data = request.json
        # Yahan result lock karne ka logic aayega
        return jsonify({'success': True})

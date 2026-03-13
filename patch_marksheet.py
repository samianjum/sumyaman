import sqlite3

DB_PATH = 'data.db' # Agar aapka DB path different hai to yahan change karein

def patch():
    with open('finalize_module.py', 'r') as f:
        content = f.read()

    # Naya logic jo teacher name bhi return karega
    new_route = """
    @app.route('/api/subject-marksheet/<int:ex_id>/<int:sub_id>')
    def get_subject_marksheet(ex_id, sub_id):
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        try:
            # Teacher aur Subject dono ka data aik saath
            info = conn.execute('''
                SELECT s.name as sub_name, t.full_name as teacher_name 
                FROM apsokara_subject s
                JOIN apsokara_subjectassignment sa ON s.id = sa.subject_id
                JOIN apsokara_teacher t ON sa.teacher_id = t.id
                WHERE s.id=? LIMIT 1
            ''', (sub_id,)).fetchone()
            
            marks = conn.execute(\"\"\"
                SELECT st.full_name, st.father_name, m.total_marks, m.obtained_marks 
                FROM student_marks m JOIN apsokara_student st ON m.student_id = st.id 
                WHERE m.exam_id=? AND m.subject_id=? ORDER BY st.full_name ASC
            \"\"\", (ex_id, sub_id)).fetchall()
            
            rows = []
            for r in marks:
                obt, tot = float(r['obtained_marks'] or 0), float(r['total_marks'] or 1)
                rows.append({"name": r['full_name'], "father": r['father_name'], "total": int(tot), "obtained": int(obt), "status": "PASS" if (obt/tot)*100 >= 33 else "FAIL"})
            
            return jsonify({
                "success": True, 
                "subject": info['sub_name'] if info else "Subject", 
                "teacher": info['teacher_name'] if info else "N/A",
                "marks": rows
            })
        except Exception as e: return jsonify({"success": False, "error": str(e)})
        finally: conn.close()
    """
    
    # Purane function ko replace karna (Simple string replacement strategy)
    import re
    pattern = r"@app\.route\('/api/subject-marksheet/.*?def get_subject_marksheet.*?finally: conn\.close\(\)"
    updated_content = re.sub(pattern, new_route, content, flags=re.DOTALL)
    
    with open('finalize_module.py', 'w') as f:
        f.write(updated_content)
    print("✅ Marksheet Route Patched with Teacher Name!")

if __name__ == "__main__":
    patch()

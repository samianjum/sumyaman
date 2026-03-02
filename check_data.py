import os, sys, sqlite3

# Database path
db_path = 'db.sqlite3'
exam_id = 4 # Test ID

def run_check():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print(f"--- ANALYZING EXAM ID: {exam_id} ---")
        
        # 1. Subject Performance (Sorted by Avg Marks)
        cursor.execute("""
            SELECT s.name, AVG(m.obtained_marks) as avg_score
            FROM student_marks m
            JOIN apsokara_subject s ON m.subject_id = s.id
            WHERE m.exam_id = ?
            GROUP BY s.id ORDER BY avg_score DESC
        """, (exam_id,))
        
        print("\n📊 SUBJECTS PERFORMANCE (Sorted: Best to Worst)")
        subjects = cursor.fetchall()
        for r in subjects:
            print(f"Subject: {r['name']} | Avg Score: {round(r['avg_score'], 2)}")

        # 2. Top 3 Students (Sorted by Total Marks)
        cursor.execute("""
            SELECT st.full_name, st.father_name, SUM(m.obtained_marks) as total
            FROM apsokara_student st
            JOIN student_marks m ON st.id = m.student_id
            WHERE m.exam_id = ?
            GROUP BY st.id ORDER BY total DESC LIMIT 3
        """, (exam_id,))
        
        print("\n🏆 TOP 3 STUDENTS")
        toppers = cursor.fetchall()
        for i, r in enumerate(toppers, 1):
            print(f"{i}. {r['full_name']} s/o {r['father_name']} | Total: {r['total']}")

        # 3. Class/Section/Wing Breakdown
        cursor.execute("""
            SELECT student_class, student_section, wing, COUNT(id) as total_s
            FROM apsokara_student
            GROUP BY student_class, student_section, wing
        """)
        print("\n🏢 CLASS/SECTION/WING STRUCTURE")
        for r in cursor.fetchall():
            print(f"Wing: {r['wing']} | Class: {r['student_class']} | Sec: {r['student_section']} | Students: {r['total_s']}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_check()

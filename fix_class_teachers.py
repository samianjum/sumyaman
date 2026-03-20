import sqlite3
import random

DB_PATH = 'db.sqlite3'

def fix_class_teachers():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Get all unique Class-Section-Wing combinations from Students
    print("🔍 Fetching all existing classes...")
    cur.execute("SELECT DISTINCT student_class, student_section, wing FROM apsokara_student")
    all_classes = cur.fetchall()
    print(f"Total unique classes found: {len(all_classes)}")

    # 2. Get all available teachers
    cur.execute("SELECT id FROM apsokara_teacher")
    teacher_ids = [r[0] for r in cur.fetchall()]
    
    if not teacher_ids:
        print("❌ No teachers found in database!")
        return

    # 3. Reset all teachers to NOT be class teachers first (to start fresh)
    cur.execute("UPDATE apsokara_teacher SET is_class_teacher = 0, assigned_class = NULL, assigned_section = NULL, assigned_wing = NULL")

    # 4. Assign one teacher to each unique class
    print("🎯 Assigning Class Teachers...")
    for i, (cl, sec, wing) in enumerate(all_classes):
        # We use modulo to reuse teachers if classes > 100
        t_id = teacher_ids[i % len(teacher_ids)]
        
        cur.execute("""
            UPDATE apsokara_teacher 
            SET is_class_teacher = 1, 
                assigned_class = ?, 
                assigned_section = ?, 
                assigned_wing = ? 
            WHERE id = ?
        """, (cl, sec, wing, t_id))

    conn.commit()
    conn.close()
    print("✅ All classes now have an assigned Class Teacher!")

if __name__ == "__main__":
    fix_class_teachers()

import sqlite3
import random

DB_PATH = 'db.sqlite3'

def setup_academic_structure():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Create 8 Standard Subjects (Only name as per your schema)
    print("📚 Creating Subjects...")
    subjects_list = [
        ('English',), ('Mathematics',), ('Urdu',),
        ('Science',), ('Islamiat',), ('Social Studies',),
        ('Computer',), ('Physics',)
    ]
    cur.executemany("INSERT OR IGNORE INTO apsokara_subject (name) VALUES (?)", subjects_list)
    
    # Get subject IDs
    cur.execute("SELECT id FROM apsokara_subject")
    subject_ids = [r[0] for r in cur.fetchall()]

    # 2. Get all Teachers
    cur.execute("SELECT id FROM apsokara_teacher")
    teacher_ids = [r[0] for r in cur.fetchall()]

    if not teacher_ids:
        print("❌ Error: No teachers found! Run mega_data_injector.py first.")
        return

    # 3. Get all unique Class-Section-Wing combinations from Students
    print("🔗 Mapping Subjects to Teachers for the whole school...")
    cur.execute("SELECT DISTINCT student_class, student_section, wing FROM apsokara_student")
    classes = cur.fetchall()

    assignments = []
    for cl, sec, wing in classes:
        # Har class ko 5 random subjects assign karo
        chosen_subjects = random.sample(subject_ids, min(len(subject_ids), 5))
        for sub_id in chosen_subjects:
            t_id = random.choice(teacher_ids)
            class_display_name = f"Class {cl}-{sec} ({wing})"
            assignments.append((cl, sec, wing, sub_id, t_id, class_display_name))

    # 4. Bulk Insert Assignments
    cur.executemany("""
        INSERT OR IGNORE INTO apsokara_subjectassignment 
        (student_class, section, wing, subject_id, teacher_id, class_name)
        VALUES (?, ?, ?, ?, ?, ?)
    """, assignments)

    conn.commit()
    conn.close()
    print(f"✅ Setup Complete! Created {len(assignments)} Subject Assignments.")

if __name__ == "__main__":
    setup_academic_structure()

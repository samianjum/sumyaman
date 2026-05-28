import sqlite3
import random
from datetime import date

DB_PATH = 'db.sqlite3'

def apply_30_percent_leaves():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = WAL")

    # 1. Get all students
    print("🔍 Fetching students to select 30% for leaves...")
    cur.execute("SELECT id, full_name, roll_number, student_class, student_section, wing FROM apsokara_student")
    all_students = cur.fetchall()

    total_to_apply = int(len(all_students) * 0.30)
    selected_students = random.sample(all_students, total_to_apply)

    print(f"🚀 Applying leaves for {len(selected_students)} students...")

    leave_entries = []
    today = date.today().isoformat()
    reasons = ["Sick Leave", "Family Emergency", "Urgent Work", "Not Feeling Well"]

    for s in selected_students:
        # s[0]=id, s[1]=name, s[2]=roll, s[3]=class, s[4]=sec, s[5]=wing
        leave_entries.append((
            s[0], s[1], s[2], s[3], s[4], s[5],
            today, today, random.choice(reasons), 'Pending'
        ))

    # 2. Bulk Insert
    cur.executemany("""
        INSERT INTO apsokara_studentleave
        (student_id, full_name, roll_number, class, section, wing, start_date, end_date, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leave_entries)

    conn.commit()
    conn.close()
    print(f"✅ Success! {len(leave_entries)} leaves applied in 'Pending' status.")

if __name__ == "__main__":
    apply_30_percent_leaves()

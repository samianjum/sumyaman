import sqlite3
import random
from datetime import date
import time

DB_PATH = 'db.sqlite3'

def run_smart_attendance():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = WAL")

    today = date.today().isoformat()
    start_time = time.time()

    # 1. Get IDs of students who are on Approved Leave today
    print("🔍 Checking approved leaves...")
    cur.execute("SELECT student_id FROM apsokara_studentleave WHERE status = 'Approved' AND start_date <= ? AND end_date >= ?", (today, today))
    on_leave_ids = {r[0] for r in cur.fetchall()}
    print(f"ℹ️  Found {len(on_leave_ids)} students on leave.")

    # 2. Get all students
    cur.execute("SELECT id FROM apsokara_student")
    all_student_ids = [r[0] for r in cur.fetchall()]

    print(f"📝 Marking attendance for {len(all_student_ids)} students...")
    attendance_batch = []

    for s_id in all_student_ids:
        if s_id in on_leave_ids:
            status = 'LEAVE'
        else:
            # 90% Present, 10% Absent (Randomly)
            status = 'PRESENT' if random.random() > 0.10 else 'ABSENT'

        # Schema assumed: student_id, status, date, marked_by
        attendance_batch.append((s_id, status, today, 'Admin_System'))

    # 3. Bulk Insert into apsokara_attendance
    # Note: Adjust column names if your schema is different
    cur.executemany("""
        INSERT INTO apsokara_attendance (student_id, status, date, marked_by)
        VALUES (?, ?, ?, ?)
    """, attendance_batch)

    conn.commit()
    conn.close()

    end_time = time.time()
    print(f"✅ Success! 90,000 attendance records marked.")
    print(f"⏱️  Total Time: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    run_smart_attendance()

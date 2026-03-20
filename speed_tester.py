import sqlite3
import time

def simulate_portal_load():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    start_time = time.time()
    
    # Simulate a heavy student dashboard load
    # 1. Fetch Diary
    cur.execute("SELECT * FROM apsokara_dailydiary WHERE date_posted = date('now') LIMIT 10")
    diaries = cur.fetchall()
    
    # 2. Fetch Attendance for last 30 days
    cur.execute("SELECT status, COUNT(*) FROM apsokara_attendance WHERE student_id = 5 GROUP BY status")
    stats = cur.fetchall()
    
    # 3. Calculate Overall Rank from 16,000 marks records
    cur.execute("""
        SELECT student_id, (SUM(obtained_marks)*100.0/SUM(total_marks)) as perc 
        FROM student_marks 
        GROUP BY student_id 
        ORDER BY perc DESC
    """)
    ranks = cur.fetchall()
    
    end_time = time.time()
    
    print(f"⏱️  Total Processing Time: {end_time - start_time:.4f} seconds")
    print(f"📊 Processed {len(ranks)} student rankings in this single request.")

if __name__ == "__main__":
    simulate_portal_load()

import sqlite3
import time
import threading

def heavy_query(user_id):
    start = time.time()
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    # Simulating a heavy request (Result + Attendance + Diary)
    cur.execute("SELECT COUNT(*) FROM student_marks")
    cur.execute("SELECT student_id, SUM(obtained_marks) FROM student_marks GROUP BY student_id")
    cur.execute("SELECT * FROM apsokara_attendance LIMIT 500")
    
    conn.close()
    print(f"👤 User {user_id} request finished in {time.time() - start:.4f}s")

threads = []
print("🚀 Simulating 10 simultaneous users hitting the database...")
for i in range(10):
    t = threading.Thread(target=heavy_query, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("✅ Multi-user test complete.")

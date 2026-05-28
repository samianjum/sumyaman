import sqlite3
import time

DB_PATH = 'db.sqlite3'

def approve_all_leaves():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Speed optimization
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = WAL")

    print("⏳ Approving 27,000 leaves... Please wait.")
    start_time = time.time()

    # Sab 'Pending' leaves ko 'Approved' kar do
    cur.execute("UPDATE apsokara_studentleave SET status = 'Approved' WHERE status = 'Pending'")

    rows_affected = cur.rowcount
    conn.commit()
    conn.close()

    end_time = time.time()
    print(f"✅ Success! {rows_affected} leaves approved.")
    print(f"⏱️  Time Taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    approve_all_leaves()

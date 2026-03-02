import sqlite3
from database_logic import fetch_user_data

def test_db():
    print("--- DATABASE DIAGNOSTIC ---")
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    
    # Check if tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]
    print(f"Tables found: {tables}")
    
    # Check Staff count
    if 'apsokara_staff' in tables:
        cur.execute("SELECT COUNT(*) FROM apsokara_staff")
        print(f"Staff Records: {cur.fetchone()[0]}")
    else:
        print("❌ ERROR: apsokara_staff table missing!")
        
    conn.close()

test_db()

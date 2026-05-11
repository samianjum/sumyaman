import pg_shim as sqlite3
import traceback

def audit():
    try:
        conn = sqlite3.connect('niki_db')
        cur = conn.cursor()
        
        print("\n--- [AUDIT: DIARY TABLE STRUCTURE] ---")
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'apsokara_dailydiary'")
        columns = cur.fetchall()
        for col in columns: print(col)
        
        print("\n--- [AUDIT: DATA SAMPLE] ---")
        cur.execute("SELECT * FROM apsokara_dailydiary LIMIT 1")
        row = cur.fetchone()
        if row:
            desc = [d[0] for d in cur.description]
            print(dict(zip(desc, row)))
        else:
            print("!!! TABLE IS EMPTY !!!")

        print("\n--- [AUDIT: TEST JOIN QUERY] ---")
        # Testing the exact query used in fetch_list
        test_query = """
            SELECT d.*, sub.name as subject_name, t.full_name as teacher_name 
            FROM apsokara_dailydiary d 
            LEFT JOIN apsokara_subject sub ON d.subject_id::bigint = sub.id::bigint 
            LEFT JOIN apsokara_teacher t ON d.teacher_id::bigint = t.id::bigint 
            LIMIT 1
        """
        cur.execute(test_query)
        print("SUCCESS: Join query works fine.")
        
        conn.close()
    except Exception:
        print("\n--- [CRASHED: EXACT ERROR BELOW] ---")
        traceback.print_exc()

if __name__ == "__main__":
    audit()

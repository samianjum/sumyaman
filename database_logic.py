import sqlite3

def fetch_user_data(uid, dob, role):
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        if role == 'Teacher':
            # Tables found mein 'apsokara_teacher' hai, 'staff' nahi.
            # Yahan hum CNIC ya ID dono check kar rahe hain
            cur.execute("SELECT *, 'Teacher' as role_db FROM apsokara_teacher WHERE (cnic=? OR id=?) AND dob=?", (uid, uid, dob))
        else:
            # Student login logic
            cur.execute("SELECT *, 'Student' as role_db FROM apsokara_student WHERE (b_form=? OR id=?) AND dob=?", (uid, uid, dob))
            
        user = cur.fetchone()
        return dict(user) if user else None
    except Exception as e:
        print(f"❌ Database Logic Error: {e}")
        return None
    finally:
        conn.close()

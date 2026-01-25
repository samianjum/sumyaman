import sqlite3
import datetime

def check_on_leave(student_id, target_date=None):
    try:
        if target_date is None:
            target_date = datetime.date.today().isoformat()
        
        conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
        cur = conn.cursor()
        # Range check: target_date should be between from_date and to_date
        query = "SELECT id FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN from_date AND to_date"
        cur.execute(query, (student_id, target_date))
        res = cur.fetchone()
        conn.close()
        return True if res else False
    except Exception as e:
        return False

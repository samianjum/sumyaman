import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Naya behtar function jo sirf student_id aur date check karega
new_func = """def check_on_leave(student_id):
    try:
        import sqlite3
        import datetime
        conn = sqlite3.connect('db.sqlite3')
        today = datetime.date.today().isoformat()
        cur = conn.cursor()
        # Naye table 'apsokara_studentleave' se check karna
        query = "SELECT id FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN from_date AND to_date"
        cur.execute(query, (student_id, today))
        res = cur.fetchone()
        conn.close()
        return True if res else False
    except Exception as e:
        return False"""

# Purane function (line 20-29) ko dhoond kar replace karna
pattern = r"def check_on_leave\(student_id\):.*?return False"
content = re.sub(pattern, new_func, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

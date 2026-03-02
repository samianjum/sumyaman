import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
tables = ['exams', 'exam_subjects', 'student_marks']
for t in tables:
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}';")
    if not c.fetchone():
        print(f"⚠️ Warning: Table '{t}' is missing. Need to create it.")
    else:
        print(f"✅ Table '{t}' exists.")
conn.close()

import psycopg2

db_config = {
    'user': 'postgres', # Superuser use kar rahe hain taake permissions set ho saken
    'host': '127.0.0.1',
    'port': '5432'
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS apsokara_student (id SERIAL PRIMARY KEY, full_name TEXT, father_name TEXT, roll_number TEXT, student_class TEXT, student_section TEXT, wing TEXT);
CREATE TABLE IF NOT EXISTS apsokara_teacher (id SERIAL PRIMARY KEY, full_name TEXT, username TEXT UNIQUE, password TEXT, is_class_teacher BOOLEAN DEFAULT FALSE, assigned_class TEXT, assigned_section TEXT, assigned_wing TEXT);
CREATE TABLE IF NOT EXISTS exams (id SERIAL PRIMARY KEY, name TEXT, class_group TEXT, start_date DATE, end_date DATE, is_active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS apsokara_subject (id SERIAL PRIMARY KEY, name TEXT);
CREATE TABLE IF NOT EXISTS apsokara_subjectassignment (id SERIAL PRIMARY KEY, teacher_id INTEGER, subject_id INTEGER, student_class TEXT, section TEXT, wing TEXT);
CREATE TABLE IF NOT EXISTS student_marks (id SERIAL PRIMARY KEY, exam_id INTEGER, student_id INTEGER, subject_id INTEGER, teacher_id INTEGER, total_marks NUMERIC, obtained_marks NUMERIC, remarks TEXT, is_locked INTEGER DEFAULT 0, CONSTRAINT unique_student_exam_subject UNIQUE (student_id, exam_id, subject_id));
CREATE TABLE IF NOT EXISTS apsokara_attendance (id SERIAL PRIMARY KEY, student_id INTEGER, date DATE, status TEXT);
"""

def fix_all():
    # Get database list
    conn = psycopg2.connect(dbname='postgres', **db_config)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datname LIKE '%_db';")
    dbs = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    for db in dbs:
        try:
            print(f"⚙️  Processing {db}...")
            c = psycopg2.connect(dbname=db, **db_config)
            c.autocommit = True
            with c.cursor() as cursor:
                # 1. Ensure ownership and permissions
                cursor.execute(f"ALTER SCHEMA public OWNER TO sami_admin;")
                cursor.execute(f"GRANT ALL ON ALL TABLES IN SCHEMA public TO sami_admin;")
                cursor.execute(f"GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO sami_admin;")
                
                # 2. Deploy Schema
                cursor.execute(SCHEMA_SQL)
            c.close()
            print(f"✅ {db} is ready and permitted.")
        except Exception as e:
            print(f"❌ Failed {db}: {e}")

if __name__ == "__main__":
    fix_all()

import psycopg2
from psycopg2.extras import RealDictCursor

def inspect_db(dbname):
    print(f"\n{'='*20} INSPECTING: {dbname} {'='*20}")
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user='sami_admin',
            password='sami123',
            host='127.0.0.1',
            port='5432'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Get all tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [t['table_name'] for t in cur.fetchall()]
        print(f"Tables found: {tables}")

        # 2. Check structure of core tables
        core_tables = ['apsokara_student', 'apsokara_teacher', 'apsokara_attendance']
        for table in core_tables:
            if table in tables:
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                """)
                cols = cur.fetchall()
                print(f"\n[Table: {table}] Columns:")
                for c in cols:
                    print(f"  - {c['column_name']} ({c['data_type']})")
            else:
                print(f"\n⚠️ WARNING: {table} NOT FOUND in {dbname}")

        conn.close()
    except Exception as e:
        print(f"❌ Error connecting to {dbname}: {e}")

# Pehle main DB check karo, phir MTS wala
inspect_db('sum_db') # Agar tumhare master db ka naam ye hai
inspect_db('mts_db')

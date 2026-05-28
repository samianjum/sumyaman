import psycopg2

db_config = {
    'user': 'sami_admin',
    'password': 'sami123',
    'host': '127.0.0.1',
    'port': '5432'
}

databases = ['sumyaman_db', 'mtss_db', 'apsacs_db', 'ghq_db'] # Add your DBs here

def extract():
    for db in databases:
        print(f"\n{'='*20} SCANNING DB: {db} {'='*20}")
        try:
            conn = psycopg2.connect(dbname=db, **db_config)
            cur = conn.cursor()

            # Get all tables
            cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';")
            tables = cur.fetchall()

            if not tables:
                print(f"Empty DB: {db}")
                continue

            for table in tables:
                t_name = table[0]
                cur.execute(f"SELECT COUNT(*) FROM {t_name};")
                count = cur.fetchone()[0]
                print(f"Table: {t_name:30} | Rows: {count}")

                # Agar student ya teacher table hai to sample dikhao
                if 'student' in t_name or 'teacher' in t_name:
                    cur.execute(f"SELECT * FROM {t_name} LIMIT 1;")
                    sample = cur.fetchone()
                    print(f"   Sample Data: {sample}")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error connecting to {db}: {e}")

if __name__ == "__main__":
    extract()

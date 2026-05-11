import psycopg2
from psycopg2 import sql

db_config = {
    'user': 'sami_admin',
    'password': 'sami123',
    'host': '127.0.0.1',
    'port': '5432'
}

def inspect():
    try:
        # 1. Check all databases
        conn = psycopg2.connect(dbname='postgres', **db_config)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false AND datname != 'postgres';")
        dbs = [r[0] for r in cur.fetchall()]
        print(f"\n📂 Databases Found: {dbs}")
        cur.close()
        conn.close()

        # 2. Check Tables in the main DB (sumyaman_db)
        target_db = 'sumyaman_db' # Ya jo bhi tumhara main hai
        if target_db in dbs:
            print(f"\n📊 Inspecting Schema for: {target_db}")
            conn = psycopg2.connect(dbname=target_db, **db_config)
            cur = conn.cursor()
            
            # Get all apsokara tables
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'apsokara%';")
            tables = [r[0] for r in cur.fetchall()]
            
            for table in tables:
                cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
                cols = cur.fetchall()
                print(f"\n📍 Table: {table}")
                for col in cols:
                    print(f"   - {col[0]} ({col[1]})")
            
            cur.close()
            conn.close()
        else:
            print(f"\n❌ {target_db} not found for inspection!")

    except Exception as e:
        print(f"❌ Error: {e}")

inspect()

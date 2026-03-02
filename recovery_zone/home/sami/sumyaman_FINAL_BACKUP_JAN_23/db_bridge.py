import sqlite3
import pandas as pd

DB_PATH = "db.sqlite3"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def fetch_df(query, params=()):
    with get_connection() as conn:
        try:
            # Query ko clean karke chalana
            return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            print(f"DB Error: {e}")
            return pd.DataFrame()

def execute(query, params=()):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()

def get_active_exam_for_class(class_name):
    # Sirf title uthao jo active ho
    df = fetch_df("SELECT id, title FROM apsokara_examwindow WHERE is_active = 1 LIMIT 1")
    if df.empty:
        return None
    return {"id": df.iloc[0]['id'], "title": df.iloc[0]['title']}

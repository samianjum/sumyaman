import psycopg2
import psycopg2.extras
import os

class PGShimCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, parameters=()):
        # Automatically translate SQLite '?' bindings to PostgreSQL '%s'
        sql = sql.replace('?', '%s')
        self._cursor.execute(sql, parameters)
        return self

    def executemany(self, sql, seq_of_parameters):
        sql = sql.replace('?', '%s')
        self._cursor.executemany(sql, seq_of_parameters)
        return self

    def fetchone(self): return self._cursor.fetchone()
    def fetchall(self): return self._cursor.fetchall()
    def fetchmany(self, size=None): return self._cursor.fetchmany(size) if size else self._cursor.fetchmany()
    def close(self): self._cursor.close()
    
    @property
    def description(self): return self._cursor.description
    
    @property
    def rowcount(self): return self._cursor.rowcount
    
    @property
    def lastrowid(self): return None # Optional: implement if RETURNING id is strictly needed
    
    def __iter__(self): return iter(self._cursor)

class PGShimConnection:
    def __init__(self, dbname):
        self._conn = psycopg2.connect(
            dbname=dbname,
            user='sami_admin',
            password='sami123',
            host='127.0.0.1',
            port='5432',
            cursor_factory=psycopg2.extras.DictCursor # Acts identically to sqlite3.Row
        )
        self.row_factory = None # Absorb any assignments to conn.row_factory

    def cursor(self): return PGShimCursor(self._conn.cursor())

    def execute(self, sql, parameters=()):
        cursor = self.cursor()
        cursor.execute(sql, parameters)
        return cursor

    def commit(self): self._conn.commit()
    def rollback(self): self._conn.rollback()
    def close(self): self._conn.close()

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type: self.rollback()
        else: self.commit()
        self.close()

def connect(database, **kwargs):
    dbname = "sumyaman_db" # Fallback Default DB
    try:
        # If passed a function reference (like get_db_path)
        if callable(database):
            database = database()
            
        if isinstance(database, str):
            if database.endswith('_db'):
                dbname = database
            elif 'tenants/' in database:
                # Extract slug from "tenants/apsokara_school.sqlite3"
                basename = os.path.basename(database)
                slug = basename.replace('_school.sqlite3', '')
                dbname = f"{slug}_db"
            elif database == 'db.sqlite3':
                # Try to guess from Flask context for hardcoded legacy routes
                try:
                    from flask import request, session
                    host = request.host.split(':')[0]
                    subdomain = host.split('.')[0]
                    t = request.args.get('t') or (subdomain if subdomain not in ['localhost', '127', 'www'] else session.get('tenant'))
                    if t: dbname = f"{t}_db"
                except Exception: pass
    except Exception: pass
        
    print(f"[PG-SHIM] Routing connection to PostgreSQL database: {dbname}")
    return PGShimConnection(dbname)

class Row: pass # Dummy class to prevent error on 'sqlite3.Row' imports/references

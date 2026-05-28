import psycopg2, psycopg2.extras
from flask import g, request, session
from urllib.parse import urlparse, parse_qs

def get_current_db_name():
    # 1. Try direct URL parameter
    tenant = request.args.get('t')

    # 2. Try Referer (the URL in the browser address bar)
    if not tenant and request.referrer:
        parsed_ref = urlparse(request.referrer)
        params = parse_qs(parsed_ref.query)
        tenant = params.get('t', [None])[0]

    # 3. Try Session
    if not tenant:
        tenant = session.get('tenant')

    if tenant and tenant not in ['localhost', '127', 'www']:
        return f"{tenant}_db"
    return "sumyaman_db"

def get_db_conn():
    if 'db' not in g:
        db_name = get_current_db_name()
        try:
            g.db = psycopg2.connect(
                dbname=db_name, user='sami_admin', password='sami123', host='127.0.0.1'
            )
            g.db_cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except:
            g.db = psycopg2.connect(dbname='sumyaman_db', user='sami_admin', password='sami123', host='127.0.0.1')
            g.db_cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return g.db

def query_db(query, args=(), one=False):
    conn = get_db_conn()
    cur = g.db_cursor
    query = query.replace('?', '%s')
    try:
        cur.execute(query, args)
        if query.strip().upper().startswith("SELECT"):
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
        else:
            conn.commit()
            return None
    except Exception as e:
        print(f"DB Error: {e}")
        return None

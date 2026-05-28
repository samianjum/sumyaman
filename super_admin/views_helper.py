import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.conf import settings
from django.core.management import call_command
import re

def create_tenant_database(db_name, db_user, db_password, db_host='127.0.0.1', db_port='5432'):
    # Remove dots and make PostgreSQL-safe
    db_name = re.sub(r'[^a-zA-Z0-9_]', '_', db_name)
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
    cur.close()
    conn.close()
    return db_name


def setup_tenant_schema(db_name, admin_user, admin_pass):
    alias = f"tenant_{db_name}"
    db_config = settings.DATABASES['default'].copy()
    db_config['NAME'] = db_name
    settings.DATABASES[alias] = db_config

    from django.core.management import call_command
    call_command('migrate', database=alias, interactive=False, verbosity=0)

    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.using(alias).filter(is_superuser=True).exists():
        User.objects.db_manager(alias).create_superuser(admin_user, 'admin@example.com', admin_pass)
        print(f"Superuser {admin_user} created in {db_name}")

    del settings.DATABASES[alias]

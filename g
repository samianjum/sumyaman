#!/usr/bin/env python3
"""
Final fix for missing columns and import errors.
Run this once after the upgrade script.
"""

import os
import sys
import psycopg2
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')
sys.path.insert(0, str(Path(__file__).parent))

import django
django.setup()

from django.conf import settings
from super_admin.models import SchoolClient

def add_column_if_not_exists(conn, table, column, col_type):
    cur = conn.cursor()
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        conn.commit()
        print(f"   ✅ Added {column} to {table}")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        print(f"   ✓ Column {column} already exists in {table}")
    except Exception as e:
        conn.rollback()
        print(f"   ⚠️ Could not add {column} to {table}: {e}")
    finally:
        cur.close()

def fix_database(db_name):
    print(f"\n🔧 Fixing database: {db_name}")
    db_config = settings.DATABASES['default'].copy()
    db_config['NAME'] = db_name
    try:
        conn = psycopg2.connect(
            dbname=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config['PORT']
        )
        conn.autocommit = False

        # Student table
        add_column_if_not_exists(conn, 'apsokara_student', 'custom_fee', 'DECIMAL(10,2) NULL')

        # FeeRecord table
        add_column_if_not_exists(conn, 'apsokara_feerecord', 'waived', 'BOOLEAN DEFAULT FALSE')
        add_column_if_not_exists(conn, 'apsokara_feerecord', 'waived_reason', 'TEXT NULL')

        # SchoolFeeSettings (for automation)
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'grace_period_days', 'INTEGER DEFAULT 0')
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'penalty_type', 'VARCHAR(20) DEFAULT \'percentage\'')
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'penalty_amount', 'DECIMAL(10,2) DEFAULT 0')
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'max_penalty', 'DECIMAL(10,2) DEFAULT 0')
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'pro_rata_type', 'VARCHAR(20) DEFAULT \'full\'')
        add_column_if_not_exists(conn, 'apsokara_schoolfeesettings', 'notify_email', 'BOOLEAN DEFAULT FALSE')

        conn.close()
    except Exception as e:
        print(f"   ❌ Failed to fix {db_name}: {e}")

# Fix default database
default_db = settings.DATABASES['default']['NAME']
fix_database(default_db)

# Fix all tenant schools
for school in SchoolClient.objects.all():
    fix_database(school.db_name)

# Fix import in fee_views.py
print("\n🔧 Fixing AuditLog import in fee_views.py...")
fee_views_path = Path(__file__).parent / "apsokara" / "fee_views.py"
if fee_views_path.exists():
    with open(fee_views_path, 'r') as f:
        content = f.read()
    if 'from .models import AuditLog' not in content:
        # Add AuditLog to the existing models import line
        content = content.replace(
            'from .models import Student, FeeStructure, FeeRecord, PaymentTransaction, SchoolFeeSettings',
            'from .models import Student, FeeStructure, FeeRecord, PaymentTransaction, SchoolFeeSettings, AuditLog'
        )
        with open(fee_views_path, 'w') as f:
            f.write(content)
        print("   ✅ Added AuditLog import")
    else:
        print("   ✓ AuditLog already imported")

print("\n✅ All fixes applied. Now restart your Django server:")
print("   python manage.py runserver")

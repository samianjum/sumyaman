#!/usr/bin/env python3
"""
APSACS DIAGNOSTIC SCANNER (read‑only)
Collects system state for debugging tenant database issues.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent

def run_command(cmd):
    """Run a shell command and return output or error."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)

def check_postgres_databases():
    """List all PostgreSQL databases containing '_db'."""
    output = run_command("psql -tAc \"SELECT datname FROM pg_database WHERE datname LIKE '%_db'\"")
    if output:
        return [db.strip() for db in output.split("\n") if db.strip()]
    return []

def check_tables_in_db(db_name):
    """Check if apsokara_student table exists in given database."""
    cmd = f"psql -d {db_name} -tAc \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'apsokara_student')\""
    out = run_command(cmd)
    return out == "t"

def get_django_settings():
    """Extract relevant settings without full Django setup (to avoid errors)."""
    settings_file = PROJECT_ROOT / "sumyaman_pro" / "settings.py"
    if not settings_file.exists():
        return {"error": "settings.py not found"}
    
    with open(settings_file, "r") as f:
        content = f.read()
    
    # Extract DATABASES dict (simple regex, not full parsing)
    db_match = re.search(r"DATABASES\s*=\s*({[^;]+})", content, re.DOTALL)
    databases = db_match.group(1) if db_match else "Not found"
    
    # Extract INSTALLED_APPS
    apps_match = re.search(r"INSTALLED_APPS\s*=\s*(\[[^\]]+\])", content, re.DOTALL)
    installed_apps = apps_match.group(1) if apps_match else "Not found"
    
    # Extract MIDDLEWARE
    mid_match = re.search(r"MIDDLEWARE\s*=\s*(\[[^\]]+\])", content, re.DOTALL)
    middleware = mid_match.group(1) if mid_match else "Not found"
    
    return {
        "DATABASES": databases,
        "INSTALLED_APPS": installed_apps,
        "MIDDLEWARE": middleware,
    }

def read_file_safely(path):
    """Read file content or return error."""
    if not path.exists():
        return "File not found"
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading: {e}"

def main():
    print("=" * 60)
    print("APSACS DIAGNOSTIC SCANNER")
    print("=" * 60)
    
    # 1. Django settings
    print("\n--- DJANGO SETTINGS ---")
    settings_info = get_django_settings()
    print(json.dumps(settings_info, indent=2, default=str))
    
    # 2. Database connections in settings.py (raw)
    print("\n--- DATABASES CONFIGURATION (from settings.py) ---")
    settings_file = PROJECT_ROOT / "sumyaman_pro" / "settings.py"
    if settings_file.exists():
        with open(settings_file, "r") as f:
            for line in f:
                if "DATABASES" in line or "'ENGINE'" in line or "'NAME'" in line:
                    print(line.strip())
    
    # 3. Tenant databases in PostgreSQL
    print("\n--- POSTGRESQL TENANT DATABASES (ending with _db) ---")
    dbs = check_postgres_databases()
    for db in dbs:
        exists = check_tables_in_db(db)
        print(f"{db}: tables exist = {exists}")
    
    # 4. Check SchoolClient entries
    print("\n--- SCHOOLCLIENT ENTRIES (from default DB) ---")
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sumyaman_pro.settings")
        import django
        django.setup()
        from super_admin.models import SchoolClient
        schools = SchoolClient.objects.all()
        for s in schools:
            print(f"slug: {s.slug}, name: {s.name}, db_name: {s.db_name}, is_active: {s.is_active}")
    except Exception as e:
        print(f"Could not fetch SchoolClient: {e}")
    
    # 5. Critical file contents (relevant snippets)
    print("\n--- CRITICAL FILE SECTIONS ---")
    
    # urls.py - look for tenant admin redirect and logout
    urls_file = PROJECT_ROOT / "sumyaman_pro" / "urls.py"
    if urls_file.exists():
        with open(urls_file, "r") as f:
            content = f.read()
        # Extract relevant lines
        lines = []
        for line in content.split("\n"):
            if "admin" in line.lower() or "logout" in line.lower() or "redirect" in line.lower():
                lines.append(line.strip())
        print("sumyaman_pro/urls.py (relevant lines):")
        for line in lines[:20]:  # limit output
            print(f"  {line}")
    
    # apsokara/views.py - check for tenant_logout
    views_file = PROJECT_ROOT / "apsokara" / "views.py"
    if views_file.exists():
        with open(views_file, "r") as f:
            content = f.read()
        if "tenant_logout" in content:
            print("apsokara/views.py: tenant_logout view is present.")
        else:
            print("apsokara/views.py: tenant_logout view is MISSING.")
    
    # middleware.py - check TenantMiddleware
    mid_file = PROJECT_ROOT / "sumyaman_pro" / "middleware.py"
    if mid_file.exists():
        with open(mid_file, "r") as f:
            content = f.read()
        if "set_current_db" in content:
            print("sumyaman_pro/middleware.py: TenantMiddleware appears to be active.")
        else:
            print("sumyaman_pro/middleware.py: TenantMiddleware may be missing.")
    
    # settings.py - check DATABASE_ROUTERS
    if settings_file.exists():
        with open(settings_file, "r") as f:
            content = f.read()
        if "DATABASE_ROUTERS" in content:
            print("settings.py: DATABASE_ROUTERS is configured.")
        else:
            print("settings.py: DATABASE_ROUTERS is MISSING.")
    
    # 6. Migrations status (check if migrations have been applied)
    print("\n--- MIGRATIONS STATUS (sample) ---")
    for db in dbs[:3]:  # limit to first 3 to avoid too much output
        print(f"Checking {db} for django_migrations table...")
        cmd = f"psql -d {db} -tAc \"SELECT COUNT(*) FROM django_migrations\""
        out = run_command(cmd)
        if out.isdigit():
            print(f"  {db}: {out} migrations applied.")
        else:
            print(f"  {db}: migrations table missing or error: {out[:100]}")
    
    # 7. Final summary
    print("\n" + "=" * 60)
    print("SCAN COMPLETE. COPY THE ENTIRE OUTPUT AND SHARE IT.")
    print("=" * 60)

if __name__ == "__main__":
    main()

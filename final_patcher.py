#!/usr/bin/env python3
"""
APSACS FINAL PATCHER
- Fixes URL routing to load custom admin (templates/hq_admin_custom)
- Creates missing tenant database and runs migrations
- Ensures SchoolClient entry exists in default DB
"""

import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SETTINGS_MODULE = "sumyaman_pro.settings"

def fix_urls():
    """Remove broken admin_logout_view and admin_login_wrapper references."""
    urls_file = PROJECT_ROOT / "sumyaman_pro" / "urls.py"
    if not urls_file.exists():
        print(f"❌ {urls_file} not found")
        return False

    with open(urls_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove the two problematic lines if they exist
    content = re.sub(
        r"path\('s/<slug:school_slug>/admin/logout/',\s*admin_logout_view,\s*name='admin_logout'\),\n?",
        "",
        content
    )
    content = re.sub(
        r"path\('s/<slug:school_slug>/admin/login/',\s*admin_login_wrapper\),\n?",
        "",
        content
    )

    # 2. Ensure the redirect line is present (only one)
    redirect_line = "    path('s/<slug:school_slug>/admin/', lambda request, school_slug: redirect(f'/s/{school_slug}/')),"
    # Remove any existing redirect lines to avoid duplication
    content = re.sub(
        r"path\('s/<slug:school_slug>/admin/',.*?\),\n",
        "",
        content
    )
    # Insert the redirect line after the super-admin include
    if "path('super-admin/', include('super_admin.urls'),)" in content:
        content = content.replace(
            "path('super-admin/', include('super_admin.urls'),)",
            "path('super-admin/', include('super_admin.urls'),)\n" + redirect_line
        )
    else:
        # Fallback: insert before the apsokara include
        content = content.replace(
            "path('s/<slug:school_slug>/', include('apsokara.urls')),",
            redirect_line + "\n    path('s/<slug:school_slug>/', include('apsokara.urls')),"
        )

    # 3. Make sure redirect is imported
    if "from django.shortcuts import redirect" not in content:
        content = re.sub(
            r"(from django.urls import path, include)",
            r"\1\nfrom django.shortcuts import redirect",
            content
        )

    # Remove duplicate hq-admin lines
    content = re.sub(
        r"path\('hq-admin/', admin_site\.urls\),\s*path\('hq-admin/', admin_site\.urls\),",
        "path('hq-admin/', admin_site.urls),",
        content
    )

    with open(urls_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Fixed sumyaman_pro/urls.py")
    return True

def create_tenant_database(slug):
    """Create PostgreSQL database if it does not exist."""
    db_name = f"{slug}_db"
    try:
        # Check if database exists
        result = subprocess.run(
            ["psql", "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"],
            capture_output=True, text=True
        )
        if result.stdout.strip() == "1":
            print(f"ℹ️ Database '{db_name}' already exists.")
            return True

        # Create database
        print(f"🛠️ Creating database '{db_name}'...")
        subprocess.run(
            ["createdb", db_name],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Database '{db_name}' created.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create database: {e.stderr}")
        return False

def run_migrations(slug):
    """Run Django migrations for the tenant database."""
    db_name = f"{slug}_db"
    try:
        print(f"🔄 Running migrations on '{db_name}'...")
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--database", db_name],
            check=True,
            cwd=PROJECT_ROOT
        )
        print(f"✅ Migrations completed for '{db_name}'.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migrations failed: {e}")
        return False

def ensure_school_client(slug, school_name="Army Public School"):
    """Create SchoolClient entry in default database if missing."""
    import django
    sys.path.insert(0, str(PROJECT_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()

    from super_admin.models import SchoolClient
    from django.db import connection

    # Use the default database
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM super_admin_schoolclient WHERE slug = %s", [slug])
        exists = cursor.fetchone()

    if exists:
        print(f"ℹ️ SchoolClient with slug '{slug}' already exists.")
        return True

    # Create new school
    SchoolClient.objects.create(
        name=school_name,
        slug=slug,
        school_type="co-ed",  # or 'wing-based' as needed
        db_name=f"{slug}_db",
        is_active=True
    )
    print(f"✅ SchoolClient '{slug}' created in default database.")
    return True

def main():
    print("🚀 APSACS Final Patcher starting...")

    # Step 1: Fix URLs
    if not fix_urls():
        print("❌ URL fixing failed. Aborting.")
        sys.exit(1)

    # Step 2: Ask for school slug (or use default)
    slug = input("\nEnter school slug (e.g., 'savs'): ").strip()
    if not slug:
        print("❌ No slug provided.")
        sys.exit(1)

    # Step 3: Create tenant database
    if not create_tenant_database(slug):
        print("❌ Could not create database. Make sure PostgreSQL is running and you have permissions.")
        sys.exit(1)

    # Step 4: Run migrations on tenant database
    if not run_migrations(slug):
        print("❌ Migrations failed. Check your models and database connection.")
        sys.exit(1)

    # Step 5: Ensure SchoolClient exists in default DB
    if not ensure_school_client(slug):
        print("❌ Failed to create SchoolClient entry.")
        sys.exit(1)

    print("\n✨ All done! Now run: python3 manage.py runserver")
    print(f"👉 Visit http://127.0.0.1:8000/s/{slug}/admin/ – it will redirect to your custom dashboard.")
    print("   (If you still see errors, make sure you have run 'python3 manage.py migrate' for the default database first.)")

if __name__ == "__main__":
    main()

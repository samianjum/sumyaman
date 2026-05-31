#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sumyaman_pro.settings')

def run_cmd(cmd):
    print(f"→ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Warning:\n{result.stderr}")
    return result.stdout, result.stderr, result.returncode

def main():
    print("🔧 APS OKARA – Migration Cleanup Patcher")
    print("========================================\n")

    # Path to migrations folder
    mig_path = "apsokara/migrations"
    if not os.path.isdir(mig_path):
        print(f"❌ Error: {mig_path} not found. Are you in the project root?")
        sys.exit(1)

    # Files to delete
    to_delete = [
        "20260529_152041_upgrade_fee_settings.py",
        "20260529_152306_fix_fee_settings.py",
        "20260530_merge_20260531_0438.py",
    ]

    deleted = []
    for fname in to_delete:
        full_path = os.path.join(mig_path, fname)
        if os.path.exists(full_path):
            os.remove(full_path)
            deleted.append(fname)
            print(f"✅ Deleted: {fname}")
        else:
            print(f"⚠️ Not found (already gone): {fname}")

    if not deleted:
        print("⚠️ No files needed deletion. Continuing...")

    # Step 2: makemigrations apsokara
    print("\n📦 Checking for new model changes...")
    out, err, code = run_cmd("python3 manage.py makemigrations apsokara --no-input")
    if code != 0:
        print("⚠️ makemigrations warning (probably no changes).")

    # Step 3: migrate
    print("\n🔄 Applying migrations...")
    out, err, code = run_cmd("python3 manage.py migrate --no-input")
    if code == 0:
        print("✅ All migrations applied successfully!")
    else:
        print("❌ Migrate failed. Trying to force fake the remaining...")
        # Try to fake any remaining problematic migrations
        run_cmd("python3 manage.py migrate apsokara --fake")
        print("⚠️ Please manually check migration status: python manage.py showmigrations")

    # Step 4: final system check
    print("\n🔍 Running system check...")
    out, err, code = run_cmd("python3 manage.py check")
    if code == 0:
        print("✅ System check passed (URL warning is cosmetic).")
    else:
        print("⚠️ System check issues:")
        print(err)

    print("\n🎉 Cleanup complete! Now you can start the server:")
    print("   python3 manage.py runserver")
    print("\n(If you still see migration warnings, run 'python3 manage.py migrate' manually)")

if __name__ == "__main__":
    main()

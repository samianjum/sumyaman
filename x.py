import os
import hashlib
import json
import shutil

# Files jinhe monitor karna hai
FILES_TO_WATCH = [
    'mobile_app.py',
    'static/student_view.js',
    'static/js/db.js',
    'static/marks_v3.js'
]

STATE_FILE = '.axis_state.json'
BACKUP_DIR = '.axis_backups'

def get_hash(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def save_state(current_hashes):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    for f_path in FILES_TO_WATCH:
        if os.path.exists(f_path):
            shutil.copy2(f_path, os.path.join(BACKUP_DIR, os.path.basename(f_path)))

    with open(STATE_FILE, 'w') as f:
        json.dump(current_hashes, f)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def run_guard():
    old_hashes = load_state()
    current_hashes = {}
    changes_detected = False

    if not old_hashes:
        print("🛡️ AXIS GUARD: Initializing Security Snapshot...")
        for f in FILES_TO_WATCH:
            h = get_hash(f)
            if h: current_hashes[f] = h
        save_state(current_hashes)
        print("✅ Snapshot created. Your system is now protected.")
        return

    for f in FILES_TO_WATCH:
        h = get_hash(f)
        if h:
            current_hashes[f] = h
            if f in old_hashes and old_hashes[f] != h:
                print(f"⚠️ ALERT: Change detected in {f}!")
                changes_detected = True

    if not changes_detected:
        print("🛡️ AXIS GUARD: Everything is OK. No backend/JS changes found.")
    else:
        choice = input("\nDo you want to ACCEPT these changes? (y/n): ").lower()
        if choice == 'y':
            save_state(current_hashes)
            print("✅ State updated. New changes are now authorized.")
        else:
            print("🔄 Reverting changes to last stable state...")
            for f in FILES_TO_WATCH:
                backup_path = os.path.join(BACKUP_DIR, os.path.basename(f))
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, f)
            print("✅ System restored to previous OK state.")

if __name__ == "__main__":
    run_guard()

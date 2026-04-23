import os

file_path = 'static/js/db.js'
with open(file_path, 'r') as f:
    content = f.read()

# Add sync lock variable
if 'let isSyncing = false;' not in content:
    content = 'let isSyncing = false;\n' + content

# Prevent overlapping syncs
old_sync_start = 'async function syncOfflineData() {'
new_sync_start = 'async function syncOfflineData() {\n    if (!navigator.onLine || isSyncing) return;\n    isSyncing = true;'
content = content.replace(old_sync_start, new_sync_start)

# Add loadStudentDiary refresh and unlock isSyncing
old_success_block = 'await db.syncQueue.delete(item.id);'
new_success_block = 'await db.syncQueue.delete(item.id);\n                if (typeof loadStudentDiary === "function") loadStudentDiary();'
content = content.replace(old_success_block, new_success_block)

# Final unlock in catch/finally
if 'finally { isSyncing = false; }' not in content:
    content = content.replace('console.error("❌ Sync failed, will retry later:", e);', 
                              'console.error("❌ Sync failed, will retry later:", e);\n        } finally { isSyncing = false; ')

with open(file_path, 'w') as f:
    f.write(content)
print("✅ db.js Fixed: Duplicates prevented.")

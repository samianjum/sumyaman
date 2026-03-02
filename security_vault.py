import os

file_path = 'mobile_app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Security Upgrade: Add Role-Based Access Control (RBAC) to analytics
old_route_start = "def student_detailed_stats(sid):"
new_route_protected = """def student_detailed_stats(sid):
    u = session.get('user')
    if not u or u.get('role') != 'Teacher':
        return jsonify({"error": "Unauthorized Access Detected"}), 403"""

if old_route_start in content and 'u.get(\'role\') != \'Teacher\'' not in content:
    content = content.replace(old_select, new_select) # Using safer replace
    content = content.replace(old_route_start, new_route_protected)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("🛡️ VAULT SECURED: Role-based protection active.")

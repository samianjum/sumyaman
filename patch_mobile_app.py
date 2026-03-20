import sys

with open('mobile_app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

# 1. Imports add karo
new_lines.append("from marks_engine import init_marks_routes, get_marks_html\n")

for i, line in enumerate(lines):
    # Skip Old API Routes (Line 1920 onwards roughly)
    if "@app.route('/api/teacher/students_v2" in line:
        skip = True
    if "@app.route('/api/teacher/save_marks_v2" in line:
        skip = True
    
    # Skip the old HTML block for marks entry
    if "id='page-marks-entry'" in line:
        new_lines.append("        {{ get_marks_html() | safe }}\n")
        skip = True
    if skip and "id='page-final-upload'" in line: # Stop skipping when next tab starts
        skip = False

    # Initialize the new routes
    if "init_teacher_routes(app, login_required)" in line:
        new_lines.append(line)
        new_lines.append("init_marks_routes(app, login_required)\n")
        continue

    # Clean up the broken tail (Indentation error fix)
    if "if __name__ == \"__main__\":" in line:
        skip = False # Ensure we don't skip the main part

    if not skip:
        # Don't add broken lines like lone conn.close() at the end
        if i > 1980 and "conn.close()" in line and "@app.route" not in lines[i-1]:
            continue
        new_lines.append(line)

with open('mobile_app.py', 'w') as f:
    f.writelines(new_lines)

print("✅ mobile_app.py Patched & Cleaned!")

import re

with open('mobile_app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

for line in lines:
    # 1. Purana save_marks_v2_api function khatam karo (Line 1991 ke paas)
    if 'def save_marks_v2_api():' in line:
        skip = True
        continue
    if skip and 'if __name__ == "__main__":' in line:
        skip = False # Stop skipping when we reach the end
    
    if not skip:
        # 2. Naye Engine ko import aur initialize karo
        if "from teacher_api import init_teacher_routes" in line:
            new_lines.append(line)
            new_lines.append("from marks_engine import init_marks_routes\n")
            continue
        if "init_teacher_routes(app, login_required)" in line:
            new_lines.append(line)
            new_lines.append("init_marks_routes(app, login_required)\n")
            continue
            
        new_lines.append(line)

with open('mobile_app.py', 'w') as f:
    f.writelines(new_lines)
print("✅ Patch Applied Safely!")

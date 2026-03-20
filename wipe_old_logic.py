import re

with open('mobile_app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False

for line in lines:
    # 1. Purane marks aur students functions delete karein
    if '@app.route' in line and ('/api/teacher/students_v2' in line or '/api/teacher/save_marks_v2' in line or '/api/teacher/init_marks' in line):
        skip = True
        continue
    
    # 2. Agar function start ho raha hai purana wala toh skip
    if skip and 'def ' in line:
        continue
        
    # 3. Stop skipping at main block
    if 'if __name__ == "__main__":' in line:
        skip = False
    
    if not skip:
        # Naye JS ko inject karo body ke end mein
        if '</body>' in line:
            new_lines.append('<script src="/static/marks_v3.js"></script>\n')
        new_lines.append(line)

with open('mobile_app.py', 'w') as f:
    f.writelines(new_lines)
print("✅ mobile_app.py WIPED and REPLACED with NEW SYSTEM!")

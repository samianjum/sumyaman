import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # 1. Indentation fix: extra spaces khatam karna
        stripped = line.lstrip()
        if stripped.startswith('if students.empty:'):
            # Is line ko sahi level par set karna
            line = "    if students.empty:\n"
        
        # 2. Duplicate key fix: agar key mein abhi bhi purana panga hai
        if 'st.segmented_control' in line:
            # Har martaba refresh pe unique key ensure karna
            import time
            ts = int(time.time())
            line = re.sub(r'key=f"s_.*?"', f'key=f"s_{{s[\'id\']}}_{{index}}_{ts}"', line)
            
        f.write(line)

print("✅ Indentation fixed and keys secured!")

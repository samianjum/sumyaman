import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # 1. Jo lines bhatak gayi hain unki indentation fix karna
    if line.strip().startswith('if students.empty:'):
        new_lines.append('    if students.empty:\n')
    elif line.strip().startswith('st.warning("No students found"):'):
        new_lines.append('        st.warning("No students found")\n')
    elif line.strip().startswith('else:'):
        new_lines.append('    else:\n')
    # 2. Duplicate Key ka khatma (id + index + static safe string)
    elif 'st.segmented_control' in line:
        line = re.sub(r'key=f"s_.*?"', r'key=f"s_{s[\'id\']}_{index}_final"', line)
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)
print("✅ Indentation and Keys have been aligned perfectly!")

import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
found_loop = False

for line in lines:
    # 1. Loop line ko dhonnd kar 'index' add karna
    if 'iterrows()' in line and 'for' in line and 'index' not in line:
        line = re.sub(r'for (.*?) in', r'for index, \1 in', line)
        found_loop = True
    
    # 2. Key mein 'index' ko safeguard karna
    if 'key=f"s_' in line and 'index' not in line:
        line = line.replace('today}"', 'today}_{index}"')
        
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

if found_loop:
    print("✅ Loop synchronized with index!")
else:
    print("⚠️ Loop already has index or structure is different, but keys checked.")

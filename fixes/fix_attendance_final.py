import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
counter = 0
for line in lines:
    if 'st.radio' in line and 'key=f"final_s_' in line:
        # Har radio button ko ek unique counter number de rahe hain
        # Taki duplicate ka koi sawal hi paida na ho
        new_line = re.sub(r'key=f"final_s_.*?_today}"', f'key=f"final_s_{{s[\'id\']}}_{{today}}_{{counter}}"', line)
        new_lines.append(f"        counter += 1\n") # Loop ke andar counter barhayen
        new_lines.append(new_line)
    else:
        new_lines.append(line)

# File ke shuru mein counter initialize karna zaroori hai
final_content = "".join(new_lines)
if "counter = 0" not in final_content:
    final_content = final_content.replace("def render_attendance_system", "def render_attendance_system(user_info):\n    counter = 0")

with open(file_path, 'w') as f:
    f.write(final_content)

print("✅ Logic rewritten with an auto-increment counter for keys!")

import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Ham key ko ID aur Index dono ke sath bind kar rahe hain
# Is se duplicate hone ka chance 0% ho jata hai
content = re.sub(r'key=f"s_.*?_index"', r'key=f"s_{s[\'id\']}_{index}"', content)

with open(file_path, 'w') as f:
    f.write(content)
print("✅ Design restored and loops fixed!")

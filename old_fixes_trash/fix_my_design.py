import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Hum key ko itna simple aur unique kar rahe hain ke error ka sawal hi na rahe
# Original design ko chhere baghair
content = re.sub(r'key=f"s_.*?_today}"', r'key=f"s_{s[\'id\']}_{s[\'roll_no\']}_{today}"', content)

with open(file_path, 'w') as f:
    f.write(content)
print("✅ Design keys updated successfully!")

import re
import uuid

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Hum key ke end mein ek random string add kar rahe hain
# Taki agar loop double bhi chale to keys match na karein
pattern = r'key=f"final_s_.*?_today}"'
# Nayi key: original logic + unique random string
replacement = f'key=f"final_s_{{s[\'id\']}}_{{s[\'roll_no\']}}_{{today}}_{str(uuid.uuid4())[:8]}"'

new_content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("✅ Unique UUID added to keys. Duplicate error should be nuked now!")

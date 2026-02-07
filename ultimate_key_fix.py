import re
import time

file_path = '/home/sami/sumyaman/attendance_system.py'
ts = int(time.time()) # Har dafa aik naya number

with open(file_path, 'r') as f:
    content = f.read()

# Hum key ko bilkul unique kar rahe hain index aur timestamp ke sath
new_content = re.sub(r"key=f\"s_\{s\['id'\]\}_\{today\}_\{index\}\"", f'key=f"s_{{s[\'id\']}}_{{index}}_{ts}"', content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("✅ Keys are now globally unique!")

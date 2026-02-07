import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Ham 'i' ko 'index' se replace kar rahe hain jo pandas iterrows() mein default hota hai
content = content.replace("_{i}_", "_{index}_")

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Indexing fixed!")

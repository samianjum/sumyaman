import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# 1. Query mein is_class_teacher shamil karna
old_q = 'q = "SELECT id, full_name, assigned_wing as wing, assigned_class as class, assigned_section as section FROM apsokara_teacher WHERE cnic = ? AND dob = ?"'
new_q = 'q = "SELECT id, full_name, assigned_wing as wing, assigned_class as class, assigned_section as section, is_class_teacher FROM apsokara_teacher WHERE cnic = ? AND dob = ?"'
content = content.replace(old_q, new_q)

# 2. Variable mapping: Agar is_class_teacher 1 hai to True set karo
content = content.replace("data['role_db'] = user_type", "data['role_db'] = user_type\n            data['is_class_teacher'] = row['is_class_teacher']")

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Attendance logic restored!")

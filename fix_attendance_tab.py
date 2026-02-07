import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Naya query jis mein is_class_teacher shamil hai
new_query = 'q = "SELECT id, full_name, assigned_wing as wing, assigned_class as class, assigned_section as section, is_class_teacher FROM apsokara_teacher WHERE cnic = ? AND dob = ?"'

# Purani query ko update karna
content = re.sub(r'q = "SELECT id, full_name, assigned_wing as wing, assigned_class as class, assigned_section as section FROM apsokara_teacher WHERE cnic = \? AND dob = \?"', new_query, content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Teacher portal updated to check Class Teacher status!")

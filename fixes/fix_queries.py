import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Galat column names ko sahi karna
content = content.replace('father_full_full_name', 'father_name')
content = content.replace('full_full_name', 'full_name')

# SQL Queries ko update karna taake wo naye models se match karein
content = re.sub(r'SELECT \* FROM apsokara_teacher WHERE .*', 'SELECT * FROM apsokara_teacher WHERE cnic = ? AND dob = ?"', content)
content = re.sub(r'SELECT \* FROM apsokara_student WHERE .*', 'SELECT * FROM apsokara_student WHERE b_form = ? AND dob = ?"', content)

with open(file_path, 'w') as f:
    f.write(content)

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Agar data['is_class_teacher'] missing hai to usay row se connect karo
if "data['is_class_teacher'] = row['is_class_teacher']" not in content:
    content = content.replace("data['role_db'] = user_type", "data['role_db'] = user_type\n            data['is_class_teacher'] = row['is_class_teacher']")

with open(file_path, 'w') as f:
    f.write(content)

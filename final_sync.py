file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Role mapping fix: Ensuring 'Teacher' matches the DB query
content = content.replace("setRole('Staff')", "setRole('Teacher')")
content = content.replace("role_db == 'Staff'", "role_db == 'Teacher'")

with open(file_path, 'w') as f:
    f.write(content)
print("✅ Mobile app synced with Teacher table!")

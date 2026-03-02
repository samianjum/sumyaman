file_path = '/home/sami/sumyaman/leave_apply.py'
with open(file_path, 'r') as f:
    content = f.read()

# Query mein is_read shamil karna
old_q = "SELECT from_date, to_date, status, reason FROM apsokara_studentleave"
new_q = "SELECT from_date, to_date, status, reason, is_read FROM apsokara_studentleave"

content = content.replace(old_q, new_q)

with open(file_path, 'w') as f:
    f.write(content)

import re

file_path = '/home/sami/sumyaman/leave_apply.py'
with open(file_path, 'r') as f:
    content = f.read()

# Import datetime agar missing hai
if 'from datetime import datetime' not in content:
    content = "from datetime import datetime\n" + content

# Query fix: applied_on column aur ? placeholder add karna
old_query = 'INSERT INTO apsokara_studentleave (student_id, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?)'
new_query = 'INSERT INTO apsokara_studentleave (student_id, class, section, wing, reason, from_date, to_date, status, applied_on) VALUES (?,?,?,?,?,?,?,?,?)'

content = content.replace(old_query, new_query)

# Values fix: datetime.now() add karna
old_vals = "(u.get('id'), u.get('class'), u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending')"
new_vals = "(u.get('id'), u.get('class'), u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending', datetime.now())"

content = content.replace(old_vals, new_vals)

with open(file_path, 'w') as f:
    f.write(content)

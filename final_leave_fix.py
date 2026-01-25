import re

file_path = '/home/sami/sumyaman/leave_apply.py'
with open(file_path, 'r') as f:
    content = f.read()

# Query ko update karna taake Name aur Section bhi save hon
old_query = 'INSERT INTO apsokara_studentleave (student_id, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?)'
new_query = 'INSERT INTO apsokara_studentleave (student_id, class, section, wing, reason, from_date, to_date, status, name) VALUES (?,?,?,?,?,?,?,?,?)'

# Values mapping ko sahi karna (u.get('full_name') add karna)
old_vals = "(u.get('id'), u.get('class'), u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending')"
new_vals = "(u.get('id'), u.get('class'), u.get('sec'), u.get('wing'), reason, str(start), str(end), 'Pending', u.get('full_name', 'Student'))"

content = content.replace(old_query, new_query)
content = content.replace(old_vals, new_vals)

with open(file_path, 'w') as f:
    f.write(content)

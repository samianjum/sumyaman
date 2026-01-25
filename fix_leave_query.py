file_path = '/home/sami/sumyaman/apsokara/logic/student_modules.py'
with open(file_path, 'r') as f:
    content = f.read()

# Query aur values ko correct karna
old_line = 'conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)",'
new_line = 'conn.execute("INSERT INTO apsokara_studentleave (student_id, name, class, section, wing, reason, from_date, to_date, status) VALUES (?,?,?,?,?,?,?,?,?)",'

# Values array ko fix karna (full_name use karna)
old_vals = "(u['id_num'], u['name'], u['class'], u.get('section',''), u.get('wing',''), reason, start, end, 'Pending'))"
new_vals = "(u['id_num'], u.get('full_name', u.get('name')), u['class'], u.get('sec', u.get('section', '')), u.get('wing',''), reason, str(start), str(end), 'Pending'))"

content = content.replace(old_vals, new_vals)
with open(file_path, 'w') as f:
    f.write(content)

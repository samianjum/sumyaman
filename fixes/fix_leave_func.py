file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Sahi query: table name aur column names badalna
old_query = "SELECT id FROM apsokara_leaverequests WHERE student_id=? AND session_year = (SELECT session_year FROM apsokara_student WHERE id=?) AND status='Approved' AND ? BETWEEN start_date AND end_date"
new_query = "SELECT id FROM apsokara_studentleave WHERE student_id=? AND status='Approved' AND ? BETWEEN from_date AND to_date"

content = content.replace(old_query, new_query)
with open(file_path, 'w') as f:
    f.write(content)

file_path = '/home/sami/sumyaman/main_app.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # Teacher Query Fix: Selecting exact columns from apsokara_teacher
        if 'SELECT * FROM apsokara_teacher' in line:
            f.write('        q = "SELECT id, full_name, assigned_wing, assigned_class, assigned_section FROM apsokara_teacher WHERE cnic = ? AND dob = ?"\n')
        
        # Student Query Fix: Selecting exact columns from apsokara_student
        elif 'SELECT * FROM apsokara_student' in line:
            f.write('        q = "SELECT id, full_name, wing, student_class, student_section FROM apsokara_student WHERE b_form = ? AND dob = ?"\n')
        
        else:
            f.write(line)

print("✅ main_app.py fixed: Teacher (cnic/assigned_wing) and Student (b_form/wing) are now synced!")

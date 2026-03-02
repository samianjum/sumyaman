file_path = '/home/sami/sumyaman/main_app.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # Teacher query fix (cnic use hoga as ID)
        if "SELECT * FROM apsokara_teacher WHERE" in line:
            f.write('        q = "SELECT * FROM apsokara_teacher WHERE cnic = ? AND dob = ?"\n')
        # Student query fix (b_form use hoga as ID)
        elif "SELECT * FROM apsokara_student WHERE" in line:
            f.write('        q = "SELECT * FROM apsokara_student WHERE b_form = ? AND dob = ?"\n')
        # Baki code wese hi rehne dein
        else:
            f.write(line)

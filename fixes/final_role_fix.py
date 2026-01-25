import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Naya accurate fetch function jo 'Class Teacher' role bhejega
new_function = """
def fetch_user_data(user_id, dob_val, user_type):
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        if user_type == "Teacher":
            q = "SELECT id, full_name, assigned_wing as wing, assigned_class as class, assigned_section as section, is_class_teacher FROM apsokara_teacher WHERE cnic = ? AND dob = ?"
        else:
            q = "SELECT id, full_name, wing, student_class as class, student_section as section FROM apsokara_student WHERE b_form = ? AND dob = ?"
        
        cursor.execute(q, (user_id, dob_val))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Yahan asali jaadu hai:
            if user_type == "Teacher" and row['is_class_teacher'] == 1:
                data['role_db'] = "Class Teacher"
            else:
                data['role_db'] = user_type
            return data
        return None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None
    finally:
        conn.close()
"""

# Purane function ko replace karna
pattern = r'def fetch_user_data\(.*?\):.*?finally:.*?conn\.close\(\)'
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Role Mapping Fixed: 'Teacher' is now 'Class Teacher' where applicable!")

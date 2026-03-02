import re

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Student login mapping ko exact database columns ke mutabiq fix karna
old_pattern = r'"Student":\s*{\s*"query":\s*".*?",\s*"mapping":\s*{.*?}\s*}'
new_replacement = """"Student": {
            "query": "SELECT id, full_name, father_full_name, cnic, student_class, student_section, wing, dob FROM apsokara_student WHERE cnic=? AND dob=?",
            "mapping": {
                "id": 0, "full_name": 1, "father_full_name": 2, "cnic": 3, 
                "student_class": 4, "student_section": 5, "wing": 6, "dob": 7
            }
        }"""

content = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

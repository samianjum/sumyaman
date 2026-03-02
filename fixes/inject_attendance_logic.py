import re

file_path = '/home/sami/sumyaman/apsokara/logic/attendance_logic.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Import statement add karna (top par)
if "from main_app import check_on_leave" not in "".join(lines):
    lines.insert(0, "from main_app import check_on_leave\n")

new_content = "".join(lines)

# Radio button ka logic dhoondna aur replace karna
# Hum assume kar rahe hain ke wahan st.radio use ho raha hai P, A, L ke sath
old_radio = r"st\.radio\(.*?,.*?\['P', 'A', 'L'\].*?\)"
# Yahan hum bache ki ID (sid) use kar ke index set karenge
new_radio = "st.radio('Status', ['P', 'A', 'L'], index=2 if check_on_leave(row['student_id']) else 0, key=f'att_{row[\"student_id\"]}')"

# Agar code mein loop 'row' ya 'r' use kar raha hai, uske mutabiq handle karein
new_content = re.sub(r"st\.radio\(.*?\['P', 'A', 'L'\],.*?index=0.*?\)", new_radio, new_content)

with open(file_path, 'w') as f:
    f.write(new_content)

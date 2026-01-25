file_path = '/home/sami/sumyaman/leave_approvals.py'
with open(file_path, 'r') as f:
    content = f.read()

# Masla ye hai ke 'r' loop mein shayad sahi tarah iterrows() nahi ho raha
# Hum logic ko row-by-row iterate karne ke liye fix karte hain
old_logic = "display_name = r['name'] if r['name'] else f\"Student ID: {r['student_id']}\""
new_logic = "display_name = r['name'] if (isinstance(r['name'], str) and r['name'].strip()) else f\"Student ID: {r['student_id']}\""

content = content.replace(old_logic, new_logic)

# Agar loop iterrows use nahi kar raha toh usay bhi target karte hain
content = content.replace("for r in pending:", "for index, r in pending.iterrows():")

with open(file_path, 'w') as f:
    f.write(content)

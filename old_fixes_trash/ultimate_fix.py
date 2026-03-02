file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        if 'st.radio' in line and 'key=f"final_s_' in line:
            # Hum saare temporary variables (i, index) nikaal kar 'id' aur 'roll_no' fix kar rahe hain
            import re
            fixed_line = re.sub(r'key=f"final_s_.*?_today}"', 'key=f"final_s_{s[\'id\']}_{s[\'roll_no\']}_{today}"', line)
            f.write(fixed_line)
        else:
            f.write(line)

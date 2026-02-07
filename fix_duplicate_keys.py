file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # Loop ko enumerate ke saath badalna taake 'i' mil jaye
        if "for index, s in students.iterrows():" in line:
            f.write(line.replace("index, s", "i, s"))
        # Key mein 'i' ka izafa
        elif 'key=f"final_s_' in line:
            import re
            new_line = re.sub(r'key=f"final_s_.*?_today}"', 'key=f"final_s_{s[\'id\']}_{i}_{today}"', line)
            f.write(new_line)
        else:
            f.write(line)

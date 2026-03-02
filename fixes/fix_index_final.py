file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # Purane loop ko dhoond kar index add karna
        if 'for s in students.iterrows():' in line:
            line = line.replace('for s in students.iterrows():', 'for index, s in students.iterrows():')
        elif 'for _, s in students.iterrows():' in line:
            line = line.replace('for _, s in students.iterrows():', 'for index, s in students.iterrows():')
        f.write(line)

print("✅ Loop fixed! 'index' is now defined.")

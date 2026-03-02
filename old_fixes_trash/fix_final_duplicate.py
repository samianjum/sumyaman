file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    counter = 0
    for line in lines:
        if 'key=f"s_{s[\'id\']}_{s[\'roll_no\']}_{today}"' in line:
            # Hum design ki key mein bas aik counter add kar rahe hain
            line = line.replace('key=f"s_{s[\'id\']}_{s[\'roll_no\']}_{today}"', 'key=f"s_{s[\'id\']}_{s[\'roll_no\']}_{today}_{i}"')
        
        # Loop ke shuru mein counter (i) ko handle karna
        if 'for index, s in students.iterrows():' in line:
             line = line.replace('index, s', 'i, s')
        elif 'for i, s in students.iterrows():' in line:
             pass
        elif 'for s in students.iterrows():' in line:
             line = line.replace('s in students.iterrows()', 'i, s in students.iterrows()')
             
        f.write(line)

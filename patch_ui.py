import os

file_path = '/home/sami/sumyaman/static/student_view.js'

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    found_loop = False
    for line in lines:
        # Loop ke andar pehle item ko 'New' badge dena
        if "Object.entries(studentData.exams).forEach(([name, info], index) => {" in line:
            new_lines.append(line)
            found_loop = True
        elif found_loop and 'html += `' in line:
            badge_html = '<span class="bg-rose-500 text-white text-[7px] px-1.5 py-0.5 rounded-full mr-2 animate-pulse">LATEST</span>'
            line = line.replace('<div>', f'<div>${index === 0 ? \'{badge_html}\' : \'\'}')
            new_lines.append(line)
            found_loop = False # Sirf pehle item ke liye
        else:
            new_lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    print("✅ UI Patcher: 'Latest' badge added to the top exam.")
else:
    print("❌ Error: student_view.js not found.")

os.remove(__file__)

import re
import os

file_path = 'mobile_app.py'

if not os.path.exists(file_path):
    print("Error: mobile_app.py nahi mili!")
    exit()

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove All Diary API Routes (Backend)
# Isse @app.route se lekar return tak ka poora function saaf ho jayega
content = re.sub(r"@app\.route\('/api/diary/.*?def .*?return.*?(?=\n@app|\nif __name__)", "", content, flags=re.DOTALL)

# 2. Remove Diary HTML Pages/Tabs (Frontend)
# Hub, Grid, Editor, History, Student - Sab khatam
pages = ['diary-hub', 'diary-grid', 'diary-editor', 'diary-student', 'diary-history']
for page in pages:
    content = re.sub(rf'<div id="page-{page}".*?</div>\s*</div>', '</div>', content, flags=re.DOTALL)
    content = re.sub(rf'<div id="page-{page}".*?</div>', '', content, flags=re.DOTALL)

# 3. Remove "Class Diary" Yellow Box from Home Page
# Dono portals (Teacher/Student) se box uda dega
content = re.sub(r'<div onclick="openDiarySystem\(\)".*?', '', content, flags=re.DOTALL)
content = re.sub(r'<div onclick="openDiarySystem\(\)".*?</div>\s*</div>', '</div>', content, flags=re.DOTALL)

# 4. Remove All Diary JavaScript Functions
js_funcs = [
    'loadStudentDiary', 'initTeacherDiary', 'renderDiaryGrid',
    'filterDiaryClasses', 'openDiaryEditor', 'submitDiary',
    'loadTeacherHistory', 'openDiarySystem'
]
for func in js_funcs:
    content = re.sub(rf'async function {func}\(.*?\}\n', '', content, flags=re.DOTALL)
    content = re.sub(rf'function {func}\(.*?\}\n', '', content, flags=re.DOTALL)

# 5. Clean JS 'pages' array
content = content.replace("'diary-hub', ", "").replace("'diary-grid', ", "").replace("'diary-editor', ", "").replace("'diary-student', ", "").replace("'diary-history', ", "")
content = content.replace("'diary-hub','diary-grid','diary-editor','diary-student','diary-history',", "")

# 6. Final Cleanup: Orphan lines fix
# Agar koi "now =", "file_names =" jaisi lines bach gayi hon
orphan_patterns = [r'^\s*now = datetime.*$', r'^\s*display_date =.*$', r'^\s*fd\.append\(.*$', r'^\s*files = request\.files.*$']
for pat in orphan_patterns:
    content = re.sub(pat, '', content, flags=re.MULTILINE)

# Double newlines ko clean karna taake indentation errors na aayein
content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Diary system ka har nishaan mita diya gaya hai. Ab mobile_app.py check karein.")

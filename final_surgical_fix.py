import re

with open('mobile_app.py', 'r') as f:
    content = f.read()

# 1. Purani JavaScript functions ko urana (navToMarks, loadTeacherAssignments, openMarkingSheet, commitMarks)
# Hum inko delete kar rahe hain taake ye marks_v3.js se takrayein nahi
content = re.sub(r'async function navToMarks\(\).*?async function commitMarks\(.*?\}.*?\}', '// JS Cleaned for New Engine', content, flags=re.DOTALL)

# 2. HTML Tab ko clean karna (page-marks-entry ko khali karna taake naya JS isay fill kare)
# Purana design isi div ke andar hardcoded tha, humne isay khali kar dena hai
content = re.sub(r"<div id='page-marks-entry'.*?</div>\s+<div id='page-final-upload'", 
                 "<div id='page-marks-entry' class='hidden space-y-4 max-w-md mx-auto'><div id='teacher-assign-list'></div></div>\n    <div id='page-final-upload'", 
                 content, flags=re.DOTALL)

# 3. Naye JS file ko script tag ke zariye link karna (Body end se pehle)
if 'static/marks_v3.js' not in content:
    content = content.replace('</body>', '<script src="/static/marks_v3.js"></script>\n</body>')

with open('mobile_app.py', 'w') as f:
    f.write(content)
print("✅ SUCCESS: Old HTML/JS Wiped. New Engine Linked!")

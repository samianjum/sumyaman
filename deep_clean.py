import re

with open('mobile_app.py', 'r') as f:
    content = f.read()

# 1. Python Backend Clean: Niche wala saara kachra urao (tail wala part)
# Jo logic marks_engine mein ja chuka hai usay delete karo
content = re.sub(r'@app\.route\(\'/api/teacher/students_v2/.*?\nif __name__ == "__main__":', 'if __name__ == "__main__":', content, flags=re.DOTALL)

# 2. JS Cleanup: navToMarks, loadTeacherAssignments wagera urao (kyunke wo static/marks.js mein hain)
content = re.sub(r'async function navToMarks\(\).*?// End of marks scripts', '', content, flags=re.DOTALL)

# 3. Insert script tag at the end of HTML
content = content.replace('</body>', '<script src="/static/marks.js"></script>\n</body>')

with open('mobile_app.py', 'w') as f:
    f.write(content)
print("✅ mobile_app.py is now CLEAN and SLIM!")

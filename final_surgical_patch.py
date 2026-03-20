import re

with open('mobile_app.py', 'r') as f:
    content = f.read()

# 1. Purane redundant routes delete karna (save_marks_v2_api wagera)
# Hum 'if __name__ == "__main__":' se pehle ka kachra saaf kar rahe hain
content = re.sub(r'def save_marks_v2_api\(\):.*?finally:.*?conn\.close\(\)', '', content, flags=re.DOTALL)

# 2. Imports aur Init check
if "from marks_engine import init_marks_routes" not in content:
    content = content.replace("from teacher_api import init_teacher_routes", 
                             "from teacher_api import init_teacher_routes\nfrom marks_engine import init_marks_routes")

if "init_marks_routes(app, login_required)" not in content:
    content = content.replace("init_teacher_routes(app, login_required)",
                             "init_teacher_routes(app, login_required)\ninit_marks_routes(app, login_required)")

with open('mobile_app.py', 'w') as f:
    f.write(content)
print("✅ Surgery Successful: mobile_app.py is now cleaner!")

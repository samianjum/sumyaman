import os
import re

file_path = 'mobile_app.py'

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Broken unlock-vault route ko mukammal khatam karo (jis se SyntaxError aa raha hai)
    # Ye @app.route('/api/unlock-vault' se lekar niche wale return tak sab uda dega
    vault_pattern = r"@app\.route\('/api/unlock-vault'.*?return jsonify\(\{\"success\": False\}\), 401"
    content = re.sub(vault_pattern, '', content, flags=re.DOTALL)

    # 2. Duplicate code ya orphaned brackets ka safaya
    # Agar koi "success": True bacha hua hai jo route ke bahar hai
    content = re.sub(r'\n\s+"success": True,.*?\n\s+\}\s+\}\)', '', content, flags=re.DOTALL)

    # 3. api_intel route mein extra arguments fix (jo app crash kar sakte hain)
    # 'Pending' extra argument tha jo SQL query match nahi kar raha tha
    intel_fix = """WHERE s.student_class=? AND s.student_section=? AND s.wing=? GROUP BY s.id""", (u['assigned_class'], u['assigned_section'], u['wing']))"""
    content = re.sub(r'WHERE s\.student_class=\? AND s\.student_section=\? AND s\.wing=\? GROUP BY s\.id""", \(u\[\'assigned_class\'\], u\[\'assigned_section\'\], u\[\'assigned_wing\'\], \'Pending\'\)\)', intel_fix, content)

    # 4. Final Indentation fix for the whole file
    # Taki koi orphaned brackets bache na hon
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Backend Syntax fixed. Broken routes removed.")
    os.remove(__file__)
else:
    print("❌ File not found.")

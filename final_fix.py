import re

with open('mobile_app.py', 'r') as f:
    content = f.read()

# 1. CSS wale if block ko safe banayein (Checking if user exists first)
old_css_if = "{% if user.role == 'Student' %}"
new_css_if = "{% if user and user.role == 'Student' %}"
content = content.replace(old_css_if, new_css_if)

# 2. Count Ifs and Endifs
if_count = len(re.findall(r'{% if', content))
endif_count = len(re.findall(r'{% endif %}', content))

print(f"DEBUG: Ifs={if_count}, Endifs={endif_count}")

# 3. Agar endif kam hain, to aakhir mein balance karein
# Most likely 'page-attendance-view' ke baad ya HTML_TEMPLATE ke end se pehle missing hai
if if_count > endif_count:
    missing = if_count - endif_count
    print(f"⚠️ Adding {missing} missing endif(s)...")
    
    # Hum HTML_TEMPLATE ke khatam hone se pehle (jo ke ''' se pehle hota hai) endifs daal dete hain
    if "'''" in content:
        parts = content.split("'''")
        # Second part (Template ka end) se pehle endifs insert karein
        parts[1] = ("\n{% endif %}" * missing) + "\n" + parts[1]
        content = "'''".join(parts)

with open('mobile_app.py', 'w') as f:
    f.write(content)

print("✅ Fix Applied! Try running the app now.")

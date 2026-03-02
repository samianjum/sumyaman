import re

file_path = 'main_app.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Remove mobile-related imports
content = re.sub(r"from mobile_portal import.*", "", content)
content = re.sub(r"import mobile_portal.*", "", content)

# 2. Fix the routing logic - Remove the width check and mobile rendering
# We look for the part where it checks if not logged_in and simplify it
old_routing_pattern = r"ui_width = st_javascript\('window\.innerWidth'.*?if ui_width is not None and ui_width < 768:.*?render_mobile_view\(\).*?else:.*?show_login\(\)"
# Agar javascript wala logic hai to usay clean karein
content = re.sub(r"ui_width = st_javascript[\s\S]*?render_mobile_view\(\)\n\s+else:", "show_login()", content, flags=re.DOTALL)

# 3. Direct replacement for the error causing part
content = content.replace("render_mobile_view()", "# mobile view removed")

# 4. Clean up any leftover JavaScript imports if they exist
content = re.sub(r"from streamlit_javascript import.*", "", content)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ main_app.py normalized! All mobile dependencies removed.")

file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    content = f.read()

# Sirf Welcome text wali line ko target karna
content = content.replace("Welcome, {u.get('name')}", "Welcome, {u.get('full_name') if st.session_state.role == 'Student' else u.get('name')}")
# Hero card ki welcome heading
content = content.replace('<div class="welcome-text">Welcome, {u["name"]}</div>', 
                          '<div class="welcome-text">Welcome, {u.get("full_name") if st.session_state.role == "Student" else u.get("name")}</div>')

with open(file_path, 'w') as f:
    f.write(content)

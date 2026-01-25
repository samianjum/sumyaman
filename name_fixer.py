file_path = '/home/sami/sumyaman/main_app.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

with open(file_path, 'w') as f:
    for line in lines:
        # Purane 'name' references ko smart references se replace karna
        line = line.replace("{u.get('name')}", "{u.get('full_name', u.get('name'))}")
        line = line.replace("{st.session_state.user_info.get('name', 'User')}", "{st.session_state.user_info.get('full_name', st.session_state.user_info.get('name', 'User'))}")
        f.write(line)

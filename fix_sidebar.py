file_path = '/home/sami/sumyaman/main_app.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Ensure 'is_class_teacher' is being fetched correctly in fetch_user_data
if 'is_class_teacher' not in content:
    content = content.replace("assigned_section", "assigned_section, is_class_teacher")

# 2. Check sidebar logic and force Attendance tab if user is a class teacher
# Hum 'if st.session_state.user_info.get("is_class_teacher")' wali condition ko pakka karte hain
old_tabs = '["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY"]'
new_tabs = '["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY", "📝 ATTENDANCE"]'

# Forcefully injecting the logic if it's missing
if '📝 ATTENDANCE' not in content:
    content = content.replace(
        'tabs = ["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY"]',
        'if st.session_state.user_info.get("is_class_teacher") == 1:\n        tabs = ["🏠 DASHBOARD", "📓 POST DIARY", "📝 ATTENDANCE", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY"]\n    else:\n        tabs = ["🏠 DASHBOARD", "📓 POST DIARY", "📚 TEACHING SCHEDULE", "🎯 MARKS ENTRY"]'
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Sidebar logic fixed! Attendance tab should now appear for Class Teachers.")

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Sahi function import karna aur usey 'get_db' ka naam dena taake baqi code na badalna paray
content = content.replace('from db_bridge import get_connection as get_db', 'from db_bridge import get_connection as get_db')
content = content.replace('from db_bridge import get_db_connection as get_db', 'from db_bridge import get_connection as get_db')

with open(file_path, 'w') as f:
    f.write(content)
print("✅ Database connection bridge fixed!")

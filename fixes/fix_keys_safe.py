import re

file_path = '/home/sami/sumyaman/attendance_system.py'
with open(file_path, 'r') as f:
    content = f.read()

# Ham segmented_control ki key ko enumerate ke baghair bhi unique kar sakte hain 
# bache ke roll_no ko use karke jo aapke design ka hissa hai
content = re.sub(r'key=f"s_{s\[\'id\'\]}_{today}"', r'key=f"s_{s[\'id\']}_{s[\'roll_no\']}_{today}"', content)

with open(file_path, 'w') as f:
    f.write(content)

import os

file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Sirf wo lines rakhen jo valid Python code lag rahi hain
valid_lines = []
for line in lines:
    s_line = line.strip()
    # Skip any line that looks like raw HTML stuck in the middle of Python
    if s_line.startswith('<') or s_line.startswith('<div id="page-mark" class="hidden p-6">
                <div class="flex items-center justify-between mb-6">
                    <button onclick="showTab('att-hub')" class="p-2 bg-gray-100 rounded-lg">🔙</button>
                    <h3 class="font-black text-lg">Daily Marking</h3>
                </div>
                <div id="marking-list" class="space-y-3"></div>
                <button onclick="syncAttendance()" class="w-full mt-8 bg-[#1B4332] text-white py-5 rounded-2xl font-black shadow-lg">🚀 SYNC TO DATABASE</button>
            </div>
"""

if 'id="page-mark"' not in content:
    content = content.replace('', marking_html + '\n            ')

with open(file_path, 'w') as f:
    f.write(content)

import os

file_path = 'mobile_app.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

# Filter out any line that starts with <div or <div id="page-mark" class="hidden p-6">
                <div class="flex items-center justify-between mb-6">
                    <button onclick="showTab('att-hub')" class="p-2 bg-gray-100 rounded-lg">🔙</button>
                    <h3 class="font-black text-lg">Daily Marking</h3>
                </div>
                <div id="marking-list" class="space-y-3"></div>
                <button onclick="syncAttendance()" class="w-full mt-8 bg-[#1B4332] text-white py-5 rounded-2xl font-black shadow-lg">🚀 SYNC TO DATABASE</button>
            </div>
"""

# Inject inside the HTML_TEMPLATE variable safely
if 'id="page-mark"' not in content:
    content = content.replace('', marking_html + '\n            ')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ File structure restored and HTML moved inside Template!")

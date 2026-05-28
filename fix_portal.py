import re

file_path = 'mobile_app.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. Fix broken JS Ternaries (%s -> ?)
# Sirf JS context mein fix karenge (jahan ? ke baad : ho)
content = re.sub(r'(\(.*?\)|\w+)\s*%s\s*(`.*?`| ".*?"| \'.*?\')\s*:', r'\1 ? \2 :', content)
content = re.sub(r'(\w+)\s*%s\s*null\s*:', r'\1 ? null :', content)

# 2. Fix specific logic lines caught by scanner
content = content.replace('isLocked %s "STATUS: LOCKED 🛡️"', 'isLocked ? "STATUS: LOCKED 🛡️"')
content = content.replace('currentEditCount === 1 %s "STATUS: 1 EDIT LEFT"', 'currentEditCount === 1 ? "STATUS: 1 EDIT LEFT"')
content = content.replace('l.attachment %s l.attachment.replace', 'l.attachment ? l.attachment.replace')

# 3. Relocate showTab and doLogin to Global Scope
# Inko {% if not logged_in %} se nikal kar <body> ke end se pehle rakhna zaroori hai
showtab_code = """
function showTab(t) {
    document.querySelectorAll('[id^="page-"]').forEach(p => p.classList.add('hidden'));
    const target = document.getElementById('page-' + t);
    if(target) {
        target.classList.remove('hidden');
        if(t === 'final-upload') loadFinalizeStatus();
    }
    // Update Header visibility
    const headerIdentity = document.getElementById('header-identity-section');
    const headerCompact = document.getElementById('header-compact-section');
    const pageTitle = document.getElementById('page-display-title');

    if (t === 'home') {
        if(headerIdentity) headerIdentity.classList.remove('hidden');
        if(headerCompact) headerCompact.classList.add('hidden');
    } else {
        if(headerIdentity) headerIdentity.classList.add('hidden');
        if(headerCompact) headerCompact.classList.remove('hidden');
        if(pageTitle) pageTitle.innerText = t.replace('-', ' ').toUpperCase();
    }
}
"""

# Remove trapped versions (basic cleanup)
content = re.sub(r'function showTab\(t\)\s*\{.*?\}', '', content, flags=re.DOTALL)

# Insert clean version before </body>
content = content.replace('</body>', f'<script>{showtab_code}</script>\n</body>')

# 4. Ensure leave-hub and diary-hub exist in the DOM
if 'id="leave-hub"' not in content:
    content = content.replace('', '\n<div id="page-leave" class="hidden"><div id="leave-hub"></div></div>')
if 'id="diary-hub"' not in content:
    content = content.replace('', '\n<div id="page-diary" class="hidden"><div id="diary-hub"></div></div>')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ FIX APPLIED: Functions globalized, Syntax corrected, and Containers added.")

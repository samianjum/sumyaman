import os

fname = 'mobile_app.py'
with open(fname, 'r') as f: lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    # Purana kachra saaf karo
    if 'async function loadResults' in line or 'window.location.href="/";' in line:
        continue
    if '@app.route("/api/results/my")' in line or "get_my_results_new" in line:
        skip = True
        continue
    if skip and (line.startswith('@app.route') or line.startswith('if __name__')):
        skip = False
    if not skip:
        new_lines.append(line)

content = "".join(new_lines)

# Fix login_required
bad = "if 'user' not in session:\n            return '<script>window.location.href=\"/\";"
good = "if 'user' not in session:\n            return '<script>window.location.href=\"/\";</script>'\n        return f(*args, **kwargs)\n    return decorated_function"

if bad in content:
    content = content.replace(bad, good)
else:
    # Check for even more broken versions
    import re
    content = re.sub(r"if 'user' not in session:.*?return decorated_function", good, content, flags=re.DOTALL)

# Add Results Logic
logic = """
@app.route('/api/results/my')
def get_my_results_api():
    import sqlite3
    u = session.get('user')
    if not u: return jsonify([])
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    exams = conn.execute('SELECT DISTINCT e.id, e.name, e.end_date FROM exams e JOIN student_marks sm ON e.id = sm.exam_id WHERE sm.student_id = ? AND sm.subject_id = 0', (u['id'],)).fetchall()
    data = []
    for ex in exams:
        marks = conn.execute('SELECT s.name as sub, sm.total_marks as t, sm.obtained_marks as o FROM student_marks sm JOIN apsokara_subject s ON sm.subject_id = s.id WHERE sm.exam_id=? AND sm.student_id=? AND sm.subject_id > 0', (ex['id'], u['id'])).fetchall()
        data.append({'exam': ex['name'], 'date': str(ex['end_date']), 'details': [dict(m) for m in marks]})
    conn.close()
    return jsonify(data)

# JS_INJECTION_POINT
"""
content = content.replace("<p class='text-sm font-bold text-gray-400'>Marksheet Table Coming Soon...</p>", "<div id='results-list-container'></div>")

if 'get_my_results_api' not in content:
    content = content.replace('if __name__ == "__main__":', logic + '\nif __name__ == "__main__":')

with open(fname, 'w') as f: f.write(content)
print("✅ Repair complete. File fixed.")

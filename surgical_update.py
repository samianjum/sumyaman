import re

fname = 'mobile_app.py'
with open(fname, 'r') as f:
    content = f.read()

# 1. Backend: Adding the dynamic Assignments API (Matching your DB schema)
if "@app.route('/api/teacher/assignments')" not in content:
    api_code = """
@app.route('/api/teacher/assignments')
@login_required
def get_teacher_assignments_v3():
    u = session['user']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Query matching your apsokara_subjectassignment schema
    query = '''
        SELECT sa.student_class, sa.section, sa.wing, s.name as sub_name, s.id as sub_id 
        FROM apsokara_subjectassignment sa 
        JOIN apsokara_subject s ON sa.subject_id = s.id 
        WHERE sa.teacher_id = ?
    '''
    rows = conn.execute(query, (u['id'],)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
"""
    # Inserting before the last if __name__ block
    content = content.replace("if __name__ == '__main__':", api_code + "\nif __name__ == '__main__':")

# 2. Frontend: Surgical Strike on the Marks Entry Page only
# Hum sirf page-marks-entry ke andar ka kachra saaf kar rahe hain
new_page_html = """
    <div id='page-marks-entry' class='hidden animate-slide-up pb-24'>
        <div class='flex items-center justify-between mb-6 bg-white p-4 rounded-2xl shadow-sm border border-gray-100'>
            <h3 class='font-black text-2xl text-indigo-600 uppercase tracking-tighter'>Marks Entry</h3>
            <button onclick="showTab('home')" class='bg-gray-100 p-3 rounded-xl active:scale-90 transition-all'>
                <span class='text-xs font-black text-gray-500'>BACK</span>
            </button>
        </div>
        
        <div id='teacher-assign-list' class='space-y-4 px-1'>
            </div>
    </div>
"""

# Purane page-marks-entry ko replace karna (Line 229 to 237 approx)
content = re.sub(r"<div id='page-marks-entry'.*?</div>\s*</div>", new_page_html, content, flags=re.DOTALL)

# 3. Frontend JS: Adding the Fetcher and UI Generator
new_js = """
    async function loadTeacherAssignments() {
        const list = document.getElementById('teacher-assign-list');
        list.innerHTML = '<div class="p-10 text-center animate-pulse text-gray-400 font-bold text-xs uppercase">Connecting to Academic DB...</div>';
        
        try {
            const res = await fetch('/api/teacher/assignments');
            const data = await res.json();
            
            if(data.length === 0) {
                list.innerHTML = '<div class="glass-card p-10 text-center text-gray-400 text-xs font-bold">NO SUBJECTS ASSIGNED TO YOU</div>';
                return;
            }

            let html = '';
            data.forEach(a => {
                html += `
                <div class="glass-card flex items-center justify-between border-l-8 border-indigo-600 active:scale-[0.98] transition-all mb-4">
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-1">
                            <span class="bg-indigo-100 text-indigo-700 text-[9px] font-black px-2 py-0.5 rounded-md uppercase">${a.sub_name}</span>
                        </div>
                        <h4 class="font-black text-gray-800 text-lg leading-tight uppercase">Class ${a.student_class}-${a.section}</h4>
                        <p class="text-[10px] font-bold text-gray-400 tracking-widest uppercase">${a.wing} WING</p>
                    </div>
                    <button class="bg-indigo-600 text-white p-4 rounded-2xl shadow-lg shadow-indigo-100 active:scale-90 transition-all">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"></path></svg>
                    </button>
                </div>`;
            });
            list.innerHTML = html;
        } catch(e) {
            list.innerHTML = '<div class="text-center text-red-500 font-bold p-10 uppercase text-[10px]">Server Connection Failed</div>';
        }
    }

    // Overriding showTab to trigger loading
    const oldShowTab = window.showTab;
    window.showTab = function(t) {
        if(typeof oldShowTab === 'function') oldShowTab(t);
        else {
            document.querySelectorAll('[id^="page-"]').forEach(p => p.classList.add('hidden'));
            document.getElementById('page-' + t).classList.remove('hidden');
        }
        if(t === 'marks-entry') loadTeacherAssignments();
    };
"""

# Inserting JS before the closing </script>
content = content.replace("</script>", new_js + "\n</script>")

with open(fname, 'w') as f:
    f.write(content)
print("✅ SUCCESS: Marks Entry Portal Surgical Update Complete!")

import re

fname = 'mobile_app.py'
with open(fname, 'r') as f:
    content = f.read()

# 1. Frontend: Marks Entry Page Fix
# Hum "Teacher Grading Interface..." wali jagah ko dynamic area se replace kar rahe hain
marks_ui = """
        <div id="exam-selector-area" class="space-y-3">
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Select Active Exam</p>
            <div id="exam-list" class="grid grid-cols-1 gap-2"></div>
        </div>
        <div id="assignment-selector-area" class="hidden space-y-3">
            <div class="flex justify-between items-center">
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Select Subject</p>
                <button onclick="backToExams()" class="text-[10px] font-black text-indigo-600 underline">CHANGE EXAM</button>
            </div>
            <div id="assign-list" class="grid grid-cols-1 gap-2"></div>
        </div>
        <div id="marks-list-area" class="hidden space-y-4">
             <div id="active-banner" class="bg-indigo-900 p-4 rounded-2xl text-white shadow-lg"></div>
             <div class="flex gap-2">
                <input type="number" id="max-marks" placeholder="Max Marks" value="100" class="w-1/3 p-3 rounded-xl bg-gray-100 border-none text-xs font-bold">
                <button onclick="saveAllMarks()" class="w-2/3 bg-emerald-600 text-white rounded-xl font-black text-xs shadow-lg">COMMIT ALL DATA</button>
             </div>
             <div id="student-marks-rows" class="space-y-2"></div>
        </div>
"""

# Replace the boring text with our dynamic UI
content = content.replace("<p class='text-sm font-bold text-gray-400'>Teacher Grading Interface...</p>", marks_ui)

# 2. JavaScript: Logic to fetch and Save
js_logic = """
        let currentExam = null;
        let currentAssign = null;

        async function loadActiveExams() {
            showTab('marks-entry');
            const list = document.getElementById('exam-list');
            list.innerHTML = '<p class="text-center text-xs animate-pulse">Scanning Exams...</p>';
            const res = await fetch('/api/active-exams');
            const exams = await res.json();
            if(exams.length === 0) { list.innerHTML = '<p class="text-xs text-red-500">No Active Exams</p>'; return; }
            let html = '';
            exams.forEach(e => {
                html += `<div onclick="selectExam('${e.id}', '${e.name}')" class="bg-white p-4 rounded-2xl border-l-4 border-indigo-600 shadow-sm font-black text-sm uppercase">${e.name}</div>`;
            });
            list.innerHTML = html;
        }

        function selectExam(id, name) {
            currentExam = {id, name};
            document.getElementById('exam-selector-area').classList.add('hidden');
            document.getElementById('assignment-selector-area').classList.remove('hidden');
            loadTeacherAssignments();
        }

        async function loadTeacherAssignments() {
            const list = document.getElementById('assign-list');
            list.innerHTML = '<p class="text-center text-xs">Fetching Subjects...</p>';
            const res = await fetch('/api/diary/init-teacher');
            const data = await res.json();
            let html = '';
            data.forEach(a => {
                html += `<div onclick="startMarking('${a.student_class}', '${a.section}', '${a.wing}', '${a.sub_name}', '${a.subject_id}')" class="bg-white p-4 rounded-2xl border-l-4 border-emerald-500 shadow-sm">
                    <h4 class="font-black text-xs uppercase">${a.sub_name}</h4>
                    <p class="text-[9px] font-bold text-gray-400">${a.student_class}-${a.section} (${a.wing})</p>
                </div>`;
            });
            list.innerHTML = html;
        }

        async function startMarking(cls, sec, wing, sub, subId) {
            currentAssign = {cls, sec, wing, sub, subId};
            document.getElementById('assignment-selector-area').classList.add('hidden');
            document.getElementById('marks-list-area').classList.remove('hidden');
            document.getElementById('active-banner').innerHTML = `<h2 class="font-black text-sm">${sub}</h2><p class="text-[10px] opacity-70">${cls}-${sec} | ${currentExam.name}</p>`;
            
            const res = await fetch(`/api/students-list?cls=${cls}&sec=${sec}&wing=${wing}`);
            const students = await res.json();
            let html = '';
            students.forEach(s => {
                html += `<div class="bg-white p-3 rounded-xl shadow-sm flex items-center justify-between gap-2">
                    <div class="w-1/2"><p class="font-black text-[10px] uppercase">${s.full_name}</p><p class="text-[8px] text-gray-400">ROLL: ${s.roll_number}</p></div>
                    <input type="number" id="m_${s.id}" placeholder="Obt" class="w-16 p-2 bg-gray-50 rounded-lg border-none text-xs text-center font-bold">
                    <input type="text" id="r_${s.id}" placeholder="Remarks" class="w-24 p-2 bg-gray-50 rounded-lg border-none text-[10px]">
                </div>`;
            });
            document.getElementById('student-marks-rows').innerHTML = html;
        }

        async function saveAllMarks() {
            const rows = document.querySelectorAll('[id^="m_"]');
            let marksData = [];
            rows.forEach(r => {
                const sid = r.id.split('_')[1];
                marksData.append({
                    student_id: sid,
                    obt: r.value,
                    rem: document.getElementById('r_' + sid).value
                });
            });
            // Logic to send to API...
            alert('Data Ready to Sync with Database!');
        }
"""

# Append JS logic before the end of script tag
content = content.replace("</script>", js_logic + "\n</script>")

with open(fname, 'w') as f:
    f.write(content)
print("✅ UI Logic Injected Successfully!")

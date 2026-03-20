async function navToMarks() {
    showTab('marks-entry');
    const sel = document.getElementById('exam-selector');
    if(!sel) return;
    sel.innerHTML = '<option>Loading...</option>';
    try {
        const res = await fetch('/api/teacher/init_marks');
        const data = await res.json();
        if (data.exams && data.exams.length > 0) {
            sel.innerHTML = data.exams.map(e => `<option value="${e.id}">${e.name.toUpperCase()}</option>`).join('');
            loadTeacherAssignments();
        } else { sel.innerHTML = '<option>No Active Exams</option>'; }
    } catch(e) { sel.innerHTML = '<option>Error</option>'; }
}

async function loadTeacherAssignments() {
    const eid = document.getElementById('exam-selector').value;
    const list = document.getElementById('teacher-assign-list');
    list.innerHTML = '<div class="p-10 text-center text-gray-400 font-bold">FETCHING...</div>';
    const res = await fetch(`/api/teacher/assignments_v2/${eid}`);
    const data = await res.json();
    list.innerHTML = data.map(a => `
        <div onclick="openMarkingSheet(${eid}, ${a.sub_id}, '${a.sub_name}')" class="glass-card flex items-center justify-between border-l-8 border-indigo-600 active:scale-95 transition-all mb-3 p-4 bg-white rounded-xl shadow-sm">
            <div>
                <span class="bg-indigo-100 text-indigo-700 text-[8px] font-black px-2 py-0.5 rounded uppercase">${a.sub_name}</span>
                <h4 class="font-black text-gray-800 text-sm mt-1 uppercase">CLASS ${a.student_class}-${a.section} (${a.wing.toUpperCase()})</h4>
            </div>
            <button class="bg-indigo-600 text-white p-2 rounded-lg shadow-lg">✍️</button>
        </div>`).join('');
}

async function openMarkingSheet(eid, sid, sname) {
    showTab('marking-view');
    const area = document.getElementById('marking-area-v2');
    area.innerHTML = '<div class="p-10 text-center text-indigo-600 font-bold">Syncing with Database...</div>';
    const res = await fetch(`/api/teacher/students_v2/${eid}/${sid}`);
    const data = await res.json();
    
    let html = `<div class="mb-4 bg-indigo-900 text-white p-4 rounded-2xl shadow-lg">
        <h2 class="font-black uppercase text-lg">${sname}</h2>
        <p class="text-[10px] opacity-70">RECORDS LOADED FROM DATABASE</p>
        <input type="number" id="total_m" value="100" class="w-full mt-2 p-2 rounded-lg text-black font-bold text-center" placeholder="Max Marks">
    </div>`;

    if (data.students && data.students.length > 0) {
        data.students.forEach(s => {
            const savedMarks = (s.obtained_marks !== null) ? s.obtained_marks : "";
            const savedRemarks = (s.remarks !== null) ? s.remarks : "";
            html += `<div class="glass-card mb-3 p-3 bg-white rounded-xl border border-gray-100 shadow-sm">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-black text-xs text-gray-800 uppercase">${s.full_name}</span>
                    <span class="text-[9px] font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded">ROLL: ${s.roll_number}</span>
                </div>
                <div class="flex gap-2">
                    <input type="number" class="obt-input w-20 p-2 bg-indigo-50 border border-indigo-100 rounded-lg text-sm font-black text-indigo-700" data-sid="${s.student_id || s.id}" value="${savedMarks}" placeholder="0">
                    <input type="text" class="rem-input flex-1 p-2 bg-gray-50 border border-gray-100 rounded-lg text-xs font-bold" data-sid="${s.student_id || s.id}" value="${savedRemarks}" placeholder="Remarks">
                </div>
            </div>`;
        });
    }
    html += `<button onclick="commitMarks(${eid}, ${sid})" class="w-full bg-indigo-600 text-white p-4 rounded-2xl font-black mt-4 shadow-xl mb-20">SAVE & LOCK DATA</button>`;
    area.innerHTML = html;
}

async function commitMarks(eid, sid) {
    const obtInputs = document.querySelectorAll('.obt-input');
    const remInputs = document.querySelectorAll('.rem-input');
    const total_m = document.getElementById('total_m').value;
    let marks = [];
    for(let i=0; i<obtInputs.length; i++) {
        marks.push({ sid: obtInputs[i].dataset.sid, obt: obtInputs[i].value, rem: remInputs[i].value });
    }
    const res = await fetch('/api/teacher/save_marks_v2', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({exam_id: eid, sub_id: sid, total_marks: total_m, marks: marks})
    });
    const result = await res.json();
    if(result.status === 'success') { alert('DATA SAVED!'); showTab('marks-entry'); }
}

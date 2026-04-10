var currentSheetData = {};

const getSmartRemark = (obt, max) => {
    const p = (obt / max) * 100;
    const pool = {
        ex: ["Outstanding grasp of core concepts.", "Exceptional academic achievement.", "Demonstrates profound understanding."],
        vg: ["Maintains a high standard of work.", "Very good progress in all areas.", "Commendable effort and results."],
        gd: ["Solid understanding of the basics.", "Good performance, shows potential.", "Consistent effort in assignments."],
        av: ["Satisfactory, but needs more focus.", "Average result, can do much better.", "Requires consistent hard work."],
        pw: ["Below expectations. Needs attention.", "Critical need for improvement.", "Requires extra guidance and effort."]
    };
    let key = p >= 90 ? 'ex' : p >= 75 ? 'vg' : p >= 50 ? 'gd' : p >= 35 ? 'av' : 'pw';
    return pool[key][Math.floor(Math.random() * pool[key].length)];
};

async function navToMarks() {
    showTab('marks-entry');
    const list = document.getElementById('teacher-assign-list');
    list.innerHTML = '<div class="p-10 text-center font-black animate-pulse text-indigo-600 uppercase text-xs">Accessing Academic Records...</div>';
    
    const res = await fetch('/api/marks/init');
    const exams = await res.json();
    
    if(exams.length === 0) {
        list.innerHTML = '<div class="glass-card p-10 text-center text-red-500 font-bold">NO ACTIVE EXAM SESSIONS FOUND</div>';
        return;
    }

    list.innerHTML = `
        <div id="m-selection-view" class="animate-in fade-in duration-300">
            <div class="glass-card p-5 space-y-4 border-t-4 border-indigo-600 mb-6 shadow-xl">
                <div class="flex items-center gap-3 mb-2">
                    <div class="h-2 w-2 bg-green-500 rounded-full animate-ping"></div>
                    <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Live Academic Session</span>
                </div>
                <select id="m-exam" onchange="updateAssignments()" class="w-full p-4 rounded-2xl bg-gray-50 font-black border-2 border-transparent focus:border-indigo-600 outline-none text-sm shadow-inner transition-all">
                    ${exams.map(e => `<option value="${e.id}" data-group="${e.class_group}">${e.name.toUpperCase()}</option>`).join('')}
                </select>
                <div id="assignment-tags" class="space-y-2 mt-4"></div>
            </div>
        </div>

        <div id="marking-sheet-container" class="hidden min-h-screen pb-32"></div>
        
        <div id="c-modal" class="hidden fixed inset-0 z-[200] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-6">
            <div class="bg-white rounded-3xl w-full max-w-xs p-8 shadow-2xl">
                <div class="text-indigo-600 mb-4 flex justify-center"><svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>
                <h3 class="font-black text-slate-900 mb-2 text-center uppercase tracking-tight">Final Authorization</h3>
                <p class="text-[11px] text-slate-500 mb-6 text-center font-bold">Are you sure you want to commit these records? This action is tracked and permanent.</p>
                <div class="flex gap-3">
                    <button onclick="closeModal()" class="flex-1 p-4 rounded-2xl border-2 font-black text-[10px] text-gray-400 uppercase">Cancel</button>
                    <button onclick="performSave()" class="flex-1 p-4 rounded-2xl bg-indigo-600 text-white font-black text-[10px] uppercase shadow-lg">Confirm</button>
                </div>
            </div>
        </div>`;
    updateAssignments();
}

async function updateAssignments() {
    const examSel = document.getElementById('m-exam');
    const eid = examSel.value;
    const group = examSel.options[examSel.selectedIndex].dataset.group;
    const res = await fetch(`/api/marks/assignments/${eid}/${group}`);
    const assigns = await res.json();
    
    document.getElementById('assignment-tags').innerHTML = assigns.map(a => `
        <div onclick="loadMarkingSheet(${eid}, ${a.subject_id}, '${a.class}', '${a.sec}', '${a.wing}', '${a.sub_name}')" 
             class="p-4 rounded-2xl bg-white border-2 flex justify-between items-center active:scale-95 transition-all cursor-pointer hover:border-indigo-600 shadow-sm ${a.is_locked?'opacity-50 grayscale':''}">
            <div>
                <p class="text-[8px] font-black text-gray-400 uppercase">${a.class}-${a.sec} | ${a.wing}</p>
                <h4 class="font-black text-gray-800 text-xs uppercase">${a.sub_name}</h4>
            </div>
            ${a.is_locked ? '<span class="bg-black text-white text-[7px] font-black px-2 py-1 rounded-lg">LOCKED</span>' : a.is_completed ? '<span class="bg-emerald-100 text-emerald-700 text-[7px] font-black px-2 py-1 rounded-lg">COMPLETED</span>' : '<span class="bg-amber-100 text-amber-700 text-[7px] font-black px-2 py-1 rounded-lg">PENDING</span>'}
        </div>`).join('');
}

async function loadMarkingSheet(eid, sid, cls, sec, wing, subName) {
    currentSheetData = { eid, subject_id: sid, cls, sec, wing, subName };
    const selectionView = document.getElementById('m-selection-view');
    const container = document.getElementById('marking-sheet-container');
    
    // Switch Views
    selectionView.classList.add('hidden');
    container.classList.remove('hidden');
    container.innerHTML = '<div class="p-20 text-center font-black animate-pulse uppercase text-[10px] text-gray-400">Opening Marksheet...</div>';
    
    const res = await fetch('/api/marks/load_students', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(currentSheetData)
    });
    const d = await res.json();
    const isLocked = d.locked;
    const max = d.students[0]?.total_marks || 100;

    let html = `
        <div class="flex items-center gap-4 mb-6">
            <button onclick="navToMarks()" class="p-2 text-indigo-600 font-black text-[10px] uppercase tracking-tighter bg-indigo-50 rounded-xl">← Back</button>
            <div class="flex-1">
                <h2 class="text-xs font-black text-gray-800 uppercase tracking-tighter leading-none">${subName}</h2>
                <p class="text-[8px] font-bold text-gray-400 uppercase">${cls}-${sec} | ${wing}</p>
            </div>
            <div class="bg-indigo-600 text-white px-3 py-2 rounded-xl flex items-center gap-2 shadow-lg ${isLocked?'opacity-50':''}">
                <span class="text-[8px] font-black uppercase">Max</span>
                <input type="number" id="m-total" value="${max}" ${isLocked?'disabled':''} class="w-10 bg-transparent text-center font-black text-xs outline-none border-none">
            </div>
        </div>

        ${isLocked ? '<div class="bg-red-600 text-white p-3 rounded-2xl font-black text-center text-[8px] mb-4 shadow-lg uppercase tracking-widest">Session Finalized - Read Only Access</div>' : ''}
        
        <div class="space-y-3">
    `;
    
    d.students.forEach(s => {
        html += `
            <div id="card-${s.id}" class="glass-card p-4 transition-all duration-300 border-2 border-transparent ${isLocked?'opacity-60 bg-gray-100':''}">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <div class="font-black text-[11px] uppercase text-gray-800">${s.full_name}</div>
                        <div class="text-[8px] font-bold text-gray-400 uppercase tracking-tighter">S/O: ${s.father_name} | ROLL: ${s.roll_number}</div>
                    </div>
                </div>
                <div class="flex gap-2">
                    <div class="w-16">
                        <label class="text-[7px] font-black text-gray-300 uppercase block mb-1 ml-1">Marks</label>
                        <input type="number" step="0.5" class="m-obt w-full p-3 bg-gray-50 rounded-xl font-black text-indigo-700 outline-none text-xs border-2 border-transparent focus:border-indigo-200" 
                               data-sid="${s.id}" value="${s.obtained_marks || ''}" ${isLocked?'disabled':''}>
                    </div>
                    <div class="flex-1 relative">
                        <label class="text-[7px] font-black text-gray-300 uppercase block mb-1 ml-1">Remarks</label>
                        <input type="text" class="m-rem w-full p-3 bg-gray-50 rounded-xl text-[10px] font-bold outline-none border-2 border-transparent focus:border-indigo-200" 
                               id="rem-${s.id}" placeholder="Required..." value="${s.remarks || ''}" ${isLocked?'disabled':''}>
                        ${!isLocked ? `<button onclick="autoFill('${s.id}')" class="absolute right-3 top-7 text-[8px] font-black text-indigo-500 uppercase">Auto</button>` : ''}
                    </div>
                </div>
            </div>`;
    });
    
    if(!isLocked) {
        html += `<div class="mt-8 px-2 pb-10"><button onclick="validateAndConfirm()" class="w-full bg-slate-900 text-white p-5 rounded-3xl font-black shadow-2xl active:scale-95 transition-all text-xs tracking-widest uppercase">Commit Data</button></div>`;
    }
    container.innerHTML = html;
}

function autoFill(sid) {
    const obt = document.querySelector(`.m-obt[data-sid="${sid}"]`).value;
    const max = document.getElementById('m-total').value;
    if(obt !== "" && max) document.getElementById(`rem-${sid}`).value = getSmartRemark(obt, max);
}

function validateAndConfirm() {
    const obts = document.querySelectorAll('.m-obt');
    const rems = document.querySelectorAll('.m-rem');
    const total = parseFloat(document.getElementById('m-total').value);
    let hasError = false;

    obts.forEach((el, i) => {
        const sid = el.dataset.sid;
        const card = document.getElementById(`card-${sid}`);
        const val = parseFloat(el.value);
        const remVal = rems[i].value.trim();

        card.classList.remove('border-red-500', 'bg-red-50');
        if(isNaN(val) || val > total || !remVal) {
            card.classList.add('border-red-500', 'bg-red-50');
            hasError = true;
        }
    });

    if(hasError) {
        alert("VALIDATION ERROR: Please fill all fields correctly.");
        return;
    }
    document.getElementById('c-modal').classList.remove('hidden');
}

function closeModal() { document.getElementById('c-modal').classList.add('hidden'); }

async function performSave() {
    closeModal();
    const obts = document.querySelectorAll('.m-obt');
    const rems = document.querySelectorAll('.m-rem');
    const total = document.getElementById('m-total').value;
    
    const marks = Array.from(obts).map((el, i) => ({
        sid: el.dataset.sid,
        obt: el.value,
        rem: rems[i].value
    }));
    
    if (!navigator.onLine) {
        await saveOffline('/api/marks/save', 'POST', {
            eid: currentSheetData.eid, 
            subject_id: currentSheetData.subject_id, 
            total: total, 
            marks: marks
        });
        alert('📶 OFFLINE: Marks saved locally. Will sync when internet is back.');
        navToMarks();
        return;
    }
    const res = await fetch('/api/marks/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({eid: currentSheetData.eid, subject_id: currentSheetData.subject_id, total: total, marks: marks})
    });
    
    const result = await res.json(); if(result.status === 'success') {
        navToMarks(); } else { alert('SERVER ERROR: ' + result.message); }
    }
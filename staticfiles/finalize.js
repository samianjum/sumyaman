let finalizeData = null;
let currentSubDetails = null; // Store subject data for filters

const style = document.createElement('style');
style.innerHTML = `
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .drawer-glass { background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(30px); border-left: 1px solid rgba(0,0,0,0.05); }
    .drawer-active { transform: translateX(0) !important; }
    .overlay-active { opacity: 1 !important; pointer-events: auto !important; }
    .card-hover:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05); }
    .filter-btn { transition: all 0.2s; }
    .filter-active { ring: 2px; transform: scale(0.95); opacity: 1 !important; }
    .error-shake { animation: shake 0.4s ease-in-out; border: 2px solid #ef4444 !important; }
    @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
    .fade-in { animation: fadeIn 0.5s ease-out forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
`;
document.head.appendChild(style);

// --- UNIVERSAL DRAWER ---
function openDrawer(title, subtitle, contentHtml) {
    document.getElementById('side-drawer')?.remove();
    document.getElementById('drawer-overlay')?.remove();

    const overlay = document.createElement('div');
    overlay.id = 'drawer-overlay';
    overlay.className = "fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[9998] opacity-0 transition-all duration-500";
    overlay.onclick = closeDrawer;
    
    const drawer = document.createElement('div');
    drawer.id = 'side-drawer';
    drawer.className = "fixed top-0 right-0 h-full w-full max-w-md drawer-glass z-[9999] shadow-2xl transform translate-x-full transition-all duration-500 flex flex-col";
    drawer.innerHTML = `
        <div class="p-8 border-b border-slate-100 flex justify-between items-center bg-white/60">
            <div><h3 class="font-black text-slate-900 uppercase text-lg tracking-tight">${title}</h3><p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">${subtitle}</p></div>
            <button onclick="closeDrawer()" class="w-10 h-10 flex items-center justify-center bg-white rounded-xl shadow-sm text-slate-400 hover:text-red-500 transition-colors">✕</button>
        </div>
        <div id="drawer-body" class="flex-1 overflow-y-auto p-6 no-scrollbar bg-slate-50/30">${contentHtml}</div>
    `;
    document.body.appendChild(overlay);
    document.body.appendChild(drawer);
    setTimeout(() => { drawer.classList.add('drawer-active'); overlay.classList.add('overlay-active'); }, 10);
}

function closeDrawer() {
    document.getElementById('side-drawer')?.classList.remove('drawer-active');
    document.getElementById('drawer-overlay')?.classList.remove('overlay-active');
    setTimeout(() => { document.getElementById('side-drawer')?.remove(); document.getElementById('drawer-overlay')?.remove(); }, 500);
}

// --- CUSTOM CONFIRMATION POPUP ---
function showPopup(title, msg, onConfirm) {
    const overlay = document.createElement('div');
    overlay.className = "fixed inset-0 bg-slate-900/60 backdrop-blur-md z-[10001] flex items-center justify-center p-6 fade-in";
    overlay.innerHTML = `
        <div class="bg-white rounded-[2.5rem] w-full max-w-sm p-8 text-center shadow-2xl">
            <div class="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">⚠️</div>
            <h3 class="font-black text-slate-900 uppercase text-xl tracking-tight mb-2">${title}</h3>
            <p class="text-xs font-bold text-slate-400 uppercase tracking-widest leading-relaxed mb-8">${msg}</p>
            <div class="space-y-3">
                <button id="pop-confirm" class="w-full py-4 bg-slate-900 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest shadow-xl active:scale-95 transition-all">Yes, Lock Results</button>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" class="w-full py-4 bg-slate-50 text-slate-500 rounded-2xl font-black text-[10px] uppercase tracking-widest">Cancel</button>
            </div>
        </div>`;
    document.body.appendChild(overlay);
    document.getElementById('pop-confirm').onclick = () => { overlay.remove(); onConfirm(); };
}

// --- MAIN DASHBOARD LOADER ---
async function loadFinalizeStatus() {
    const area = document.getElementById('finalize-content-area');
    const r = await fetch('/api/class-finalize-status');
    const d = await r.json();
    finalizeData = d;

    // 1. NO EXAM STATE
    if(d.no_exam) {
        area.innerHTML = `<div class="flex flex-col items-center justify-center py-32 fade-in">
            <div class="w-24 h-24 bg-white rounded-[2.5rem] shadow-sm border border-slate-100 flex items-center justify-center mb-6 text-4xl">📅</div>
            <h2 class="text-2xl font-black text-slate-800 uppercase tracking-tighter">No Active Session</h2>
            <p class="text-[10px] text-slate-400 font-bold tracking-widest uppercase mt-2">Examination portal is currently dormant</p>
        </div>`;
        return;
    }

    // 2. LOCKED STATE
    if(d.is_published) {
        area.innerHTML = `<div class="flex flex-col items-center justify-center py-32 fade-in">
            <div class="w-24 h-24 bg-emerald-50 rounded-[2.5rem] shadow-sm flex items-center justify-center mb-6 text-4xl text-emerald-500">🔒</div>
            <h2 class="text-2xl font-black text-emerald-600 uppercase tracking-tighter">Result Published & Locked</h2>
            <p class="text-[10px] text-slate-400 font-bold tracking-widest uppercase mt-2">${d.exam_name} • Accessible on Portal</p>
        </div>`;
        return;
    }

    // 3. MAIN DASHBOARD HEADER
    let html = `<div class="mb-10 flex justify-between items-end fade-in">
        <div><h2 class="text-4xl font-black text-slate-900 uppercase tracking-tighter">${d.exam_name}</h2><p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.3em] mt-2">Finalization Console</p></div>
        ${d.is_ready ? `<button onclick="magicFill()" class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-[9px] font-black uppercase rounded-2xl shadow-lg shadow-indigo-200 active:scale-95 transition-all">✨ Magic Remarks</button>` : ''}
    </div>`;

    // 4. SUBJECT PROGRESS TRACKER
    html += `<div class="flex gap-4 overflow-x-auto pb-8 no-scrollbar fade-in" style="animation-delay: 0.1s;">`;
    let submittedCount = 0;
    d.status.forEach(s => {
        if(s.submitted) submittedCount++;
        html += `<div onclick="${s.submitted ? `openSubjectDetails(${d.exam_id}, ${s.id}, '${s.subject}', '${s.teacher}')` : ''}" 
            class="flex-none w-48 p-6 bg-white rounded-[2rem] border ${s.submitted ? 'border-emerald-100 shadow-sm cursor-pointer card-hover' : 'border-slate-50 opacity-50'} transition-all">
            <div class="flex items-center gap-2 mb-4">
                <span class="w-2.5 h-2.5 rounded-full ${s.submitted ? 'bg-emerald-500' : 'bg-amber-400 animate-pulse'}"></span>
                <span class="text-[11px] font-black text-slate-800 uppercase truncate">${s.subject}</span>
            </div>
            <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Prof. ${s.teacher.split(' ')[0]}</p>
            <p class="text-xs font-black mt-4 ${s.submitted ? 'text-emerald-600' : 'text-slate-400'}">${s.count} Marks</p>
        </div>`;
    });
    html += `</div>`;

    // 5. STUDENT CARDS OR PENDING STATE
    if(d.is_ready) {
        html += `<div class="space-y-4 pb-32 fade-in" style="animation-delay: 0.2s;">`;
        d.students.forEach(st => {
            html += `<div class="bg-white rounded-[2.5rem] border border-slate-100 p-8 shadow-sm card-hover transition-all">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <h4 class="text-lg font-black text-slate-900 uppercase tracking-tight">${st.name}</h4>
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">S/O: ${st.father_name}</p>
                    </div>
                    <div class="text-right">
                        <span class="text-3xl font-black text-slate-900">${st.perc}%</span><br>
                        <button onclick="viewReport(${d.exam_id}, ${st.id}, '${st.name}', '${st.father_name}', ${st.obt}, ${st.tot}, ${st.perc})" class="text-[9px] font-black text-indigo-500 uppercase mt-2 hover:text-indigo-700 transition-colors">Detailed Report ➔</button>
                    </div>
                </div>
                <textarea id="rem-${st.id}" oninput="this.classList.remove('error-shake')" class="w-full bg-slate-50 border-none rounded-2xl p-5 text-xs font-bold text-slate-600 focus:ring-2 focus:ring-indigo-200 outline-none transition-all" placeholder="Enter final remarks (Mandatory)..." rows="2"></textarea>
            </div>`;
        });
        html += `</div>
        <div class="fixed bottom-8 left-0 right-0 px-6 max-w-5xl mx-auto z-50 fade-in" style="animation-delay: 0.3s;">
            <button onclick="validateAndFinalize(${d.exam_id})" class="w-full py-6 bg-slate-900 text-white rounded-[2.5rem] font-black text-xs uppercase tracking-[0.4em] shadow-2xl active:scale-95 transition-transform">Lock & Publish Portal</button>
        </div>`;
    } else {
        html += `<div class="p-24 mt-8 bg-slate-50/50 rounded-[3rem] border-2 border-dashed border-slate-200 text-center fade-in">
            <div class="w-16 h-16 mx-auto mb-4 border-4 border-slate-200 border-t-slate-800 rounded-full animate-spin"></div>
            <h3 class="font-black text-slate-800 uppercase tracking-tighter">Awaiting Submissions</h3>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-2">${submittedCount} of ${d.status.length} subjects received</p>
        </div>`;
    }
    area.innerHTML = html;
}

// --- SUBJECT MARKSHEET WITH FILTERS ---
async function openSubjectDetails(exId, subId, subName, teacherName) {
    openDrawer(subName, `Taught by Prof. ${teacherName}`, `<div class="p-20 text-center text-[10px] font-black text-slate-300 uppercase animate-pulse tracking-widest">Compiling...</div>`);
    const r = await fetch(`/api/get-subject-marks-details?exam_id=${exId}&subject_id=${subId}`);
    const d = await r.json();
    currentSubDetails = d.marks; // Save for filtering
    renderSubList('all', d.stats);
}

function renderSubList(filterType, stats = null) {
    // Retain stats if rendering from filter click
    if(!stats) {
        let p=0, f=0;
        currentSubDetails.forEach(m => m.is_pass ? p++ : f++);
        stats = {total: currentSubDetails.length, pass: p, fail: f};
    }

    let filtered = currentSubDetails;
    if(filterType === 'pass') filtered = currentSubDetails.filter(m => m.is_pass);
    if(filterType === 'fail') filtered = currentSubDetails.filter(m => !m.is_pass);

    let html = `
        <div class="grid grid-cols-3 gap-3 mb-6">
            <div onclick="renderSubList('all')" class="filter-btn cursor-pointer bg-slate-100 p-4 rounded-[1.5rem] text-center ${filterType==='all'?'ring-2 ring-slate-400 opacity-100':'opacity-60'}">
                <p class="text-[8px] font-bold text-slate-500 uppercase tracking-widest">Total</p><p class="text-xl font-black text-slate-900">${stats.total}</p>
            </div>
            <div onclick="renderSubList('pass')" class="filter-btn cursor-pointer bg-emerald-50 p-4 rounded-[1.5rem] text-center ${filterType==='pass'?'ring-2 ring-emerald-400 opacity-100':'opacity-60'}">
                <p class="text-[8px] font-bold text-emerald-500 uppercase tracking-widest">Passed</p><p class="text-xl font-black text-emerald-600">${stats.pass}</p>
            </div>
            <div onclick="renderSubList('fail')" class="filter-btn cursor-pointer bg-red-50 p-4 rounded-[1.5rem] text-center ${filterType==='fail'?'ring-2 ring-red-400 opacity-100':'opacity-60'}">
                <p class="text-[8px] font-bold text-red-500 uppercase tracking-widest">Failed</p><p class="text-xl font-black text-red-600">${stats.fail}</p>
            </div>
        </div>
        <div class="space-y-3">
            ${filtered.map(m => `
                <div class="p-5 bg-white border border-slate-100 rounded-[2rem] flex justify-between items-center shadow-sm">
                    <div>
                        <p class="text-[11px] font-black text-slate-800 uppercase">${m.name}</p>
                        <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1">S/O ${m.father}</p>
                    </div>
                    <div class="px-4 py-2 rounded-xl text-[11px] font-black ${m.is_pass ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}">
                        ${m.obt} / ${m.tot}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('drawer-body').innerHTML = html;
}

// --- DETAILED REPORT CARD DRAWER ---
async function viewReport(exId, stId, name, father, obtTotal, maxTotal, perc) {
    openDrawer(name, `S/O: ${father}`, `<div class="p-20 text-center text-[10px] font-black text-slate-300 uppercase animate-pulse tracking-widest">Analyzing...</div>`);
    const r = await fetch(`/api/get-student-report-card?exam_id=${exId}&student_id=${stId}`);
    const d = await r.json();
    
    // Calculate passing subjects
    let passedSubs = 0, failedSubs = 0;
    d.report.forEach(s => {
        let isPass = parseFloat(s.obtained_marks) >= (parseFloat(s.total_marks) * 0.33);
        isPass ? passedSubs++ : failedSubs++;
        s.is_pass = isPass; // Inject for rendering
    });

    let html = `
        <div class="bg-slate-900 rounded-[2.5rem] p-8 text-white mb-6 shadow-xl shadow-slate-200">
            <div class="flex justify-between items-end mb-6">
                <div><p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Overall Score</p><p class="text-4xl font-black">${perc}%</p></div>
                <div class="text-right"><p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Obtained</p><p class="text-xl font-black">${obtTotal}/${maxTotal}</p></div>
            </div>
            <div class="flex gap-2">
                <div class="flex-1 bg-white/10 rounded-2xl p-4 text-center"><p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">Passed</p><p class="text-lg font-black text-emerald-400">${passedSubs}</p></div>
                <div class="flex-1 bg-white/10 rounded-2xl p-4 text-center"><p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">Failed</p><p class="text-lg font-black text-red-400">${failedSubs}</p></div>
            </div>
        </div>
        <div class="space-y-3">
            <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2 px-2">Subject Breakdown</h4>
            ${d.report.map(s => `
                <div class="p-5 bg-white border border-slate-100 rounded-[2rem] flex justify-between items-center shadow-sm">
                    <div>
                        <p class="text-[11px] font-black text-slate-800 uppercase">${s.subject_name}</p>
                        <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1 flex items-center gap-1">
                            <span>Prof. ${s.teacher_name}</span>
                        </p>
                    </div>
                    <div class="text-right">
                        <span class="text-[12px] font-black ${s.is_pass ? 'text-slate-900' : 'text-red-500'}">${s.obtained_marks}/${s.total_marks}</span><br>
                        <span class="text-[7px] font-black uppercase tracking-widest ${s.is_pass ? 'text-emerald-500' : 'text-red-500'}">${s.is_pass ? 'Passed' : 'Failed'}</span>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('drawer-body').innerHTML = html;
}

function magicFill() {
    finalizeData.students.forEach(st => {
        let msg = st.perc >= 80 ? "Outstanding performance. Promoted." : 
                  st.perc >= 50 ? "Satisfactory result. Promoted." : "Needs serious attention in weak subjects.";
        const el = document.getElementById('rem-' + st.id);
        el.value = msg;
        el.classList.remove('error-shake'); // Clear error if magic fill is used
    });
}

function validateAndFinalize(exId) {
    const rems = {};
    let errorId = null;
    finalizeData.students.forEach(st => {
        const el = document.getElementById('rem-' + st.id);
        const val = el.value.trim();
        if(!val) { 
            if(!errorId) errorId = st.id; 
            el.classList.add('error-shake');
        }
        rems[st.id] = val;
    });

    if(errorId) { 
        document.getElementById('rem-' + errorId).scrollIntoView({behavior: 'smooth', block: 'center'});
        return; 
    }

    showPopup("Final System Archive", "You are about to lock the result for the entire class. This action is irreversible and will publish the marks to the student portal.", async () => {
        const r = await fetch('/api/publish-final-result', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({exam_id: exId, remarks: rems})
        });
        const res = await r.json();
        if(res.success) location.reload();
    });
}

loadFinalizeStatus();

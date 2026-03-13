let currentSubjectData = null;

// CSS Injection for clean app feel
const style = document.createElement('style');
style.innerHTML = `
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    .custom-shadow { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); }
`;
document.head.appendChild(style);

async function loadFinalizeStatus() {
    const area = document.getElementById('finalize-content-area');
    if(!area) return;
    area.innerHTML = '<div class="p-20 text-center uppercase font-bold text-slate-300 text-[10px] tracking-[0.3em] animate-pulse">Syncing...</div>';
    try {
        const r = await fetch('/api/class-finalize-status');
        const d = await r.json();
        
        // 1. Check if No Exam is Active (Professional View)
        if(d.no_exam) {
            area.innerHTML = `
                <div class="py-24 px-10 text-center animate-in fade-in zoom-in duration-700">
                    <div class="w-20 h-20 bg-slate-50 text-slate-300 rounded-[2.5rem] flex items-center justify-center mx-auto mb-8 shadow-inner relative">
                        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" opacity="0.3"></path>
                        </svg>
                    </div>
                    <h3 class="font-black text-slate-800 uppercase tracking-tighter text-base">Schedule Idle</h3>
                    <p class="text-[9px] text-slate-400 font-bold uppercase mt-2 tracking-[0.2em] leading-relaxed max-w-[200px] mx-auto opacity-70">
                        Examination portal is currently dormant. Waiting for schedule activation.
                    </p>
                    <button onclick="loadFinalizeStatus()" class="mt-10 px-10 py-4 bg-slate-900 text-white text-[9px] font-black uppercase rounded-2xl tracking-[0.3em] shadow-2xl active:scale-95 transition-all">Check Now</button>
                </div>`;
            return;
        }

        // 2. Handle Errors
        if(!d.success) { 
            area.innerHTML = `
                <div class="py-20 px-10 text-center animate-in fade-in zoom-in duration-500">
                    <div class="w-16 h-16 bg-slate-50 text-slate-200 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">${d.error || "No Active Exam"}</p>
                </div>`; 
            return; 
        }
        
        // 3. Locked/Published Result
        if(d.is_published) {
            area.innerHTML = `
                <div class="p-10 text-center bg-white rounded-[2.5rem] border border-slate-100 custom-shadow animate-in zoom-in duration-500">
                    <div class="w-16 h-16 bg-emerald-50 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl shadow-sm">🔒</div>
                    <h3 class="font-extrabold text-slate-900 uppercase text-lg tracking-tight">Result Locked</h3>
                    <p class="text-[10px] text-slate-400 font-bold uppercase mt-1 tracking-widest">${d.exam_name}</p>
                </div>`;
            return;
        }

        // 4. Main Dashboard UI
        let html = `<div class="mb-8 px-1"><h2 class="text-2xl font-black text-slate-900 uppercase tracking-tight">${d.exam_name}</h2><p class="text-[9px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-1">Finalization Dashboard</p></div>`;
        
        html += `<div class="flex overflow-x-auto gap-3 pb-2 no-scrollbar" style="-webkit-overflow-scrolling: touch;">`;
        d.status.forEach(s => {
            const isDone = s.submitted;
            html += `<div onclick="${isDone ? `openSubjectDetails(${d.exam_id}, ${s.id}, '${s.subject}')` : ''}" class="flex-none w-40 p-4 bg-white rounded-2xl border ${isDone ? 'border-slate-200 custom-shadow cursor-pointer' : 'border-slate-50 opacity-40'} transition-all active:scale-95">
                <p class="text-[11px] font-bold text-slate-800 truncate uppercase">${s.subject}</p>
                <p class="text-[8px] font-bold text-slate-400 uppercase mt-1 mb-2">T: ${s.teacher}</p>
                <div class="flex items-center gap-1.5">
                    <div class="w-1.5 h-1.5 rounded-full ${isDone ? 'bg-emerald-500' : 'bg-slate-200'}"></div>
                    <p class="text-[9px] font-bold uppercase ${isDone ? 'text-emerald-600' : 'text-slate-300'}">${isDone ? 'Completed' : 'Pending'}</p>
                </div>
            </div>`;
        });
        html += `</div>`;

        if(d.is_ready) {
            html += `<div class="mt-8 space-y-4 animate-in slide-in-from-bottom duration-500 pb-10">`;
            d.students.forEach(st => {
                html += `<div id="card-${st.id}" class="bg-white rounded-2xl border border-slate-100 overflow-hidden custom-shadow">
                    <div class="p-5 flex justify-between items-center bg-slate-50/30">
                        <div><p class="text-sm font-bold text-slate-900 uppercase">${st.name}</p><p class="text-[9px] font-bold text-slate-400 uppercase">S/O ${st.father_name}</p></div>
                        <div class="text-right"><p class="text-lg font-black text-slate-900">${st.perc}%</p><button onclick="viewReportCard(${d.exam_id}, ${st.id}, '${st.name}')" class="text-[9px] font-bold text-blue-600 uppercase border-b border-blue-100">Report</button></div>
                    </div>
                    <div class="p-4"><textarea id="rem-${st.id}" class="w-full bg-white border border-slate-100 rounded-xl text-xs font-medium text-slate-600 p-3 outline-none focus:border-slate-300 transition-all" placeholder="Add Final Remarks..." rows="2"></textarea></div>
                </div>`;
            });
            html += `<button onclick="validateAndLock(${d.exam_id}, ${JSON.stringify(d.students.map(s=>s.id))})" class="w-full py-5 bg-slate-900 text-white rounded-2xl font-bold text-[10px] uppercase tracking-widest mt-4 shadow-xl active:scale-95 transition-all">Lock & Publish</button></div>`;
        } else {
            const pendingCount = d.status.filter(s => !s.submitted).length;
            html += `
                <div class="mt-8 p-10 bg-slate-50/50 rounded-[2.5rem] border border-dashed border-slate-200 text-center animate-in fade-in duration-700">
                    <div class="relative w-16 h-16 mx-auto mb-6">
                        <div class="absolute inset-0 border-[3px] border-slate-200 border-t-slate-900 rounded-full animate-spin"></div>
                        <div class="absolute inset-0 flex items-center justify-center text-[10px] font-black text-slate-900">${pendingCount}</div>
                    </div>
                    <h3 class="font-black text-slate-800 uppercase text-xs tracking-tight">Submission Pending</h3>
                    <p class="text-[9px] text-slate-400 font-bold uppercase mt-2 tracking-widest leading-relaxed">Wait for all teachers to submit.</p>
                </div>`;
        }
        area.innerHTML = html;
    } catch(e) { 
        console.error(e);
        area.innerHTML = `<div class="p-20 text-center font-bold text-red-500 text-[10px] uppercase">Sync Error!</div>`;
    }
}

function createModal(id, innerHtml) {
    const overlay = document.createElement('div'); overlay.id = id;
    overlay.className = "fixed inset-0 z-[10000] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-6 animate-in fade-in duration-200";
    const box = document.createElement('div'); box.className = "bg-white w-full max-w-sm rounded-[2.5rem] custom-shadow overflow-hidden animate-in zoom-in-95 duration-300";
    box.innerHTML = innerHtml; overlay.appendChild(box); document.body.appendChild(overlay); return box;
}
function closeModal(id) { const m = document.getElementById(id); if(m) m.remove(); }

async function openSubjectDetails(exId, subId, subName) {
    const box = createModal('sub-modal', '<div class="p-20 text-center font-bold text-[10px] text-slate-300 uppercase animate-pulse">Loading...</div>');
    const r = await fetch(`/api/get-subject-marks-details?exam_id=${exId}&subject_id=${subId}`);
    currentSubjectData = await r.json();
    updateSubjectModalUI(subName);
}

function updateSubjectModalUI(subName, filter = 'all') {
    const box = document.getElementById('sub-modal').firstChild;
    const d = currentSubjectData;
    let fMarks = filter === 'all' ? d.marks : d.marks.filter(m => filter === 'pass' ? m.is_pass : !m.is_pass);
    box.innerHTML = `
        <div class="p-6 border-b border-slate-50 flex justify-between items-center bg-slate-50/20">
            <div><h3 class="font-bold text-slate-900 uppercase text-sm">${subName}</h3><p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Marksheet</p></div>
            <button onclick="closeModal('sub-modal')" class="w-8 h-8 flex items-center justify-center bg-white rounded-full shadow-sm text-slate-300">×</button>
        </div>
        <div class="p-4 grid grid-cols-3 gap-2">
            <div onclick="updateSubjectModalUI('${subName}', 'all')" class="bg-slate-100 p-3 rounded-2xl text-center active:scale-95 transition-all cursor-pointer"><p class="text-[7px] font-bold text-slate-400 uppercase">Total</p><p class="text-xs font-bold">${d.stats.total}</p></div>
            <div onclick="updateSubjectModalUI('${subName}', 'pass')" class="bg-emerald-50 p-3 rounded-2xl text-center active:scale-95 transition-all cursor-pointer"><p class="text-[7px] font-bold text-emerald-400 uppercase">Pass</p><p class="text-xs font-bold text-emerald-600">${d.stats.pass}</p></div>
            <div onclick="updateSubjectModalUI('${subName}', 'fail')" class="bg-red-50 p-3 rounded-2xl text-center active:scale-95 transition-all cursor-pointer"><p class="text-[7px] font-bold text-red-400 uppercase">Fail</p><p class="text-xs font-bold text-red-600">${d.stats.fail}</p></div>
        </div>
        <div class="max-h-[50vh] overflow-y-auto px-4 pb-4 space-y-1 no-scrollbar">
            ${fMarks.map(m => `<div class="p-4 rounded-2xl border border-slate-50 flex justify-between items-center bg-white"><p class="text-[10px] font-bold text-slate-700 uppercase">${m.name}</p><p class="text-[10px] font-bold ${m.is_pass ? 'text-slate-900' : 'text-red-500'}">${m.obt}/${m.tot}</p></div>`).join('')}
        </div>`;
}

async function viewReportCard(exId, stId, name) {
    const box = createModal('rep-modal', '<div class="p-20 text-center font-bold text-[10px] text-slate-300 uppercase animate-pulse">Fetching...</div>');
    const r = await fetch(`/api/get-student-report-card?exam_id=${exId}&student_id=${stId}`);
    const d = await r.json();
    let obt=0, tot=0;
    d.report.forEach(s => { obt+=s.obtained_marks; tot+=s.total_marks; });
    box.innerHTML = `
        <div class="p-6 border-b border-slate-50 flex justify-between items-center">
            <div><h3 class="font-bold text-slate-900 uppercase text-sm">${name}</h3><p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Progress Card</p></div>
            <button onclick="closeModal('rep-modal')" class="w-8 h-8 flex items-center justify-center bg-slate-50 rounded-full text-slate-300">×</button>
        </div>
        <div class="p-5">
            <div class="bg-slate-900 p-6 rounded-[2rem] text-white flex justify-between items-center shadow-xl">
                <div><p class="text-[8px] font-bold opacity-40 uppercase">Total %</p><p class="text-2xl font-black">${tot > 0 ? ((obt/tot)*100).toFixed(1) : 0}%</p></div>
                <div class="text-right"><p class="text-[8px] font-bold opacity-40 uppercase">Status</p><p class="text-xs font-bold uppercase mt-1">Verified</p></div>
            </div>
        </div>
        <div class="max-h-[40vh] overflow-y-auto px-5 pb-6 space-y-2 no-scrollbar">
            ${d.report.map(s => `<div class="p-4 bg-slate-50/50 rounded-2xl border border-white flex justify-between items-center">
                <div><p class="text-[10px] font-bold text-slate-800 uppercase">${s.subject_name}</p><p class="text-[7px] font-bold text-slate-400 uppercase">T: ${s.teacher_name}</p></div>
                <div class="font-bold text-[10px] text-slate-900">${s.obtained_marks}/${s.total_marks}</div>
            </div>`).join('')}
        </div>`;
}

function validateAndLock(exId, stIds) {
    let missing = [];
    stIds.forEach(id => {
        const area = document.getElementById('rem-'+id);
        if(!area.value.trim()) { missing.push(id); area.style.borderColor = '#ef4444'; }
    });
    if(missing.length > 0) { alert("🚨 Please fill all remarks!"); document.getElementById('card-'+missing[0]).scrollIntoView({behavior:'smooth'}); return; }
    createModal('lock-confirm', `
        <div class="p-10 text-center">
            <div class="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold shadow-sm">!</div>
            <h3 class="text-lg font-black text-slate-900 uppercase mb-2">Final Archive</h3>
            <p class="text-[10px] text-slate-400 font-bold uppercase mb-8 leading-relaxed">Result will be locked permanently.</p>
            <div class="space-y-3">
                <button onclick="publishNow(${exId}, ${JSON.stringify(stIds)})" id="final-confirm-btn" class="w-full py-4 bg-red-600 text-white rounded-2xl font-bold text-[10px] uppercase tracking-widest active:scale-95 transition-all shadow-lg">Lock Everything</button>
                <button onclick="closeModal('lock-confirm')" class="w-full py-4 bg-slate-50 text-slate-400 rounded-2xl font-bold text-[10px] uppercase">Cancel</button>
            </div>
        </div>`);
}

async function publishNow(exId, stIds) {
    const btn = document.getElementById('final-confirm-btn'); btn.innerHTML = "LOCKING..."; btn.disabled = true;
    const remarks = {}; stIds.forEach(id => remarks[id] = document.getElementById('rem-'+id).value.trim());
    try {
        const r = await fetch('/api/publish-final-result', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({exam_id:exId, remarks:remarks})});
        const res = await r.json();
        if(res.success) {
            closeModal('lock-confirm');
            createModal('success-anim', `<div class="p-12 text-center"><div class="w-20 h-20 bg-emerald-500 text-white rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl animate-bounce text-2xl">✓</div><h3 class="text-xl font-black text-slate-900 uppercase">Archived</h3></div>`);
            setTimeout(() => { location.reload(); }, 2500);
        }
    } catch(e) { alert("Error: " + e); btn.disabled = false; }
}

loadFinalizeStatus();

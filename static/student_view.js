let studentData = null;

async function loadStudentResults() {
    const container = document.getElementById('student-result-container');
    if(!container) return;
    const response = await fetch('/api/student/my-results');
    const data = await response.json();
    if(data.success) { 
        studentData = data; 
        initDashboard(); 
    }
}

window.initDashboard = function() {
    const container = document.getElementById('student-result-container');
    if (!studentData.exams || studentData.exams.length === 0) {
        container.innerHTML = `<div class="p-4 bg-[#F4F6F8] min-h-screen flex flex-col items-center justify-center py-20 opacity-40">
            <div class="text-6xl mb-4">📄</div>
            <p class="text-xs font-black uppercase tracking-widest text-center">No Results Published Yet</p>
        </div>`;
        return;
    }

    container.innerHTML = `
        <div class="p-4 bg-[#F4F6F8] min-h-screen">
            <input type="text" id="examSearch" oninput="renderExamCards(this.value)" placeholder="SEARCH EXAMS..." 
                class="w-full p-4 mb-5 rounded-2xl border-none shadow-sm text-[11px] font-black uppercase focus:ring-2 focus:ring-[#0B3D2E]">
            <div id="exam-cards-list"></div>
        </div>
        <div id="drawer-overlay" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] hidden transition-opacity duration-300" onclick="closeReport()"></div>
        <div id="result-drawer" class="fixed bottom-0 left-0 w-full h-[95%] bg-white rounded-t-[35px] z-[101] translate-y-full transition-transform duration-500 shadow-2xl flex flex-col overflow-hidden">
            <div class="w-12 h-1.5 bg-gray-200 rounded-full mx-auto my-4"></div>
            <div id="drawer-body" class="flex-1 overflow-y-auto px-5 pb-10"></div>
        </div>`;
    
    renderExamCards("");
};

window.renderExamCards = function(search) {
    const listContainer = document.getElementById('exam-cards-list');
    if(!listContainer) return;

    let html = '';
    studentData.exams.forEach((info, index) => {
        const name = info.name || "";
        if(search && !name.toLowerCase().includes(search.toLowerCase())) return;
        
        html += `
        <div class="bg-white p-5 rounded-2xl shadow-sm mb-4 flex justify-between items-center border-l-[6px] border-[#0B3D2E] active:scale-95 transition-all" onclick="openReport('${index}')">
            <div>
                ${index === 0 ? '<span class="bg-rose-600 text-white text-[7px] px-1.5 py-0.5 rounded-full mr-2 animate-pulse uppercase tracking-tighter">Newest</span>' : ''}
                <p class="text-[9px] font-black text-emerald-700 uppercase mb-1">${info.start} — ${info.end}</p>
                <h3 class="font-black text-sm text-gray-800 uppercase">${name}</h3>
            </div>
            <div class="h-10 w-10 bg-gray-50 rounded-full flex items-center justify-center text-[#0B3D2E] font-black">➔</div>
        </div>`;
    });
    listContainer.innerHTML = html;
};

window.openReport = function(examIdx) {
    const exam = studentData.exams[examIdx];
    const s = studentData.student;
    const att = exam.att;
    const attPer = att.t > 0 ? ((att.p / att.t) * 100).toFixed(0) : 0;
    
    let tObt = 0, tMax = 0;
    exam.subjects.forEach(sub => { tObt += sub.obt; tMax += sub.tot; });
    const per = tMax > 0 ? ((tObt / tMax) * 100).toFixed(1) : 0;

    const body = document.getElementById('drawer-body');
    body.innerHTML = `
        <div class="bg-[#0B3D2E] rounded-2xl p-5 text-white mb-6 shadow-lg">
            <div class="flex justify-between items-start mb-3">
                <img src="/api/school-logo" class="w-12 h-12 bg-white p-1 rounded-lg">
                <div class="text-right"><p class="text-[10px] font-black opacity-70 uppercase">Session</p><p class="text-xs font-black">2025–26</p></div>
            </div>
            <div class="text-center">
                <h1 class="text-sm font-black uppercase tracking-widest">Army Public School & College</h1>
                <p class="text-[10px] font-bold opacity-80 mt-1 uppercase">10th - ${s.assigned_section} | Okara Cantt</p>
            </div>
        </div>

        <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 mb-6">
            <div class="grid grid-cols-2 gap-y-3">
                <div><p class="text-[9px] text-gray-400 font-black uppercase">Name</p><p class="text-[12px] font-black text-gray-800 uppercase">${s.full_name}</p></div>
                <div class="text-right"><p class="text-[9px] text-gray-400 font-black uppercase">Roll No</p><p class="text-[12px] font-black text-gray-800">${s.roll_number || 'N/A'}</p></div>
                <div><p class="text-[9px] text-gray-400 font-black uppercase">Father</p><p class="text-[12px] font-black text-gray-800 uppercase">${s.father_name}</p></div>
            </div>
        </div>

        <div class="space-y-3 mb-8">
            ${exam.subjects.map(sub => {
                const sp = (sub.obt / sub.tot) * 100;
                let g = sp>=80?'A+':sp>=70?'A':sp>=50?'B':'C';
                let clr = sp>=80?'bg-emerald-500':sp>=50?'bg-orange-400':'bg-red-500';
                return `
                <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                    <div class="flex justify-between items-center mb-1">
                        <p class="text-xs font-black text-gray-800 uppercase">${sub.name}</p>
                        <div class="flex items-center gap-3">
                            <p class="text-xs font-black text-gray-700">${sub.obt} / ${sub.tot}</p>
                            <span class="${clr} text-white text-[9px] font-black px-2 py-0.5 rounded-md min-w-[30px] text-center">${g}</span>
                        </div>
                    </div>
                    <p class="text-[9px] font-bold text-gray-400 italic">Remark: ${sub.rem}</p>
                </div>`;
            }).join('')}
        </div>

        <div class="bg-emerald-50 rounded-2xl p-6 text-center border-2 border-emerald-100 mb-6 shadow-inner">
            <h2 class="text-5xl font-black text-emerald-800 mb-2">${per}%</h2>
            <div class="grid grid-cols-3 gap-2 border-t border-emerald-200 mt-4 pt-4">
                <div><p class="text-[8px] font-black text-emerald-600 uppercase">Total</p><p class="text-xs font-black text-gray-800">${tObt}/${tMax}</p></div>
                <div class="border-x border-emerald-200"><p class="text-[8px] font-black text-emerald-600 uppercase">Grade</p><p class="text-xs font-black text-gray-800">${per>=80?'A+':'A'}</p></div>
                <div><p class="text-[8px] font-black text-emerald-600 uppercase">Position</p><p class="text-xs font-black text-emerald-900 font-italic">${exam.pos}</p></div>
            </div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm text-center mb-6">
            <p class="text-[10px] font-black text-gray-400 uppercase mb-2">Attendance: ${att.p}/${att.t} (${attPer}%)</p>
            <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden"><div class="bg-emerald-600 h-full" style="width: ${attPer}%"></div></div>
        </div>
        
        <div class="bg-amber-50 p-5 rounded-2xl border-l-4 border-amber-500 mb-10">
            <p class="text-[9px] font-black text-amber-900 uppercase mb-1">Class Teacher Remark</p>
            <p class="text-[11px] font-bold text-amber-800 italic">"${exam.ct_remark}"</p>
        </div>

        <button onclick="closeReport()" class="w-full py-5 bg-[#0B3D2E] text-white rounded-2xl font-black text-xs uppercase shadow-xl tracking-widest active:scale-95">Close Dashboard</button>
    `;
    
    document.getElementById('drawer-overlay').classList.remove('hidden');
    setTimeout(() => { 
        document.getElementById('drawer-overlay').style.opacity = '1'; 
        document.getElementById('result-drawer').classList.remove('translate-y-full'); 
    }, 10);
};

window.closeReport = function() {
    const d = document.getElementById('result-drawer');
    const o = document.getElementById('drawer-overlay');
    d.classList.add('translate-y-full');
    o.style.opacity = '0';
    setTimeout(() => o.classList.add('hidden'), 400);
};
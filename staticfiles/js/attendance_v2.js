const AttendanceManager = {
    currentEditCount: 0,
    isLocked: false,

    async init() {
        console.log("🚀 Attendance Manager Initialized");
        await this.checkLockStatus();
    },

    async checkLockStatus() {
        try {
            const res = await fetch('/api/check-lock');
            const data = await res.json();
            this.currentEditCount = data.edit_count || 0;
            this.isLocked = (this.currentEditCount >= 2);
            this.updateUIStatus();
        } catch (e) { console.error("Lock check failed", e); }
    },

    updateUIStatus() {
        const statusText = document.getElementById('lock-status-text');
        const banner = document.getElementById('marking-banner');
        if (!statusText) return;

        if (this.isLocked) {
            statusText.innerText = "STATUS: LOCKED 🛡️";
            statusText.className = "text-[10px] text-red-500 font-bold";
        } else {
            statusText.innerText = this.currentEditCount === 1 ? "STATUS: 1 EDIT LEFT" : "STATUS: OPEN";
            statusText.className = "text-[10px] text-green-500 font-bold";
        }
    },

    async loadInterface() {
        const list = document.getElementById('marking-list');
        const banner = document.getElementById('marking-banner');
        const footer = document.getElementById('marking-footer');
        
        list.innerHTML = '<div class="p-10 text-center text-gray-400">Loading Students...</div>';
        
        if (this.isLocked) {
            banner.innerHTML = '<div class="p-4 bg-green-100 text-green-800 rounded-xl font-bold text-center">🛡️ ATTENDANCE SECURED FOR TODAY</div>';
            footer.innerHTML = '';
        } else {
            banner.innerHTML = this.currentEditCount === 1 ? 
                '<div class="p-3 bg-red-50 text-red-600 text-[10px] font-black rounded-xl border border-red-100 uppercase">⚠️ FINAL EDIT: Record will lock after this.</div>' : 
                '<div class="p-3 bg-yellow-50 text-yellow-700 text-[10px] font-black rounded-xl border border-yellow-100 uppercase">💡 Marking active. You can edit once after saving.</div>';
            footer.innerHTML = '<button onclick="AttendanceManager.sync()" class="w-full bg-[#1B4332] text-white p-4 rounded-2xl font-black shadow-lg active:scale-95 transition-all">🚀 SAVE & LOCK ATTENDANCE</button>';
        }

        const res = await fetch('/api/students-marking');
        const data = await res.json();
        
        list.innerHTML = data.students.map(s => `
            <div class="glass-card flex justify-between items-center p-4 bg-white/50 border-b border-gray-100">
                <div class="flex flex-col">
                    <span class="font-black text-sm text-gray-800 uppercase">${s.full_name}</span>
                    <span class="text-[9px] text-gray-400 font-bold">ROLL: ${s.roll}</span>
                </div>
                <select id="s_${s.id}" ${this.isLocked ? 'disabled' : ''} class="bg-gray-50 border-none rounded-lg text-xs font-bold p-2 focus:ring-2 focus:ring-[#1B4332]">
                    <option value="Present" ${s.status === 'Present' ? 'selected' : ''}>Present</option>
                    <option value="Absent" ${s.status === 'Absent' ? 'selected' : ''}>Absent</option>
                    <option value="Leave" ${s.status === 'Leave' ? 'selected' : ''}>Leave</option>
                </select>
            </div>
        `).join('');
    },

    async sync() {
        if (this.isLocked) return;
        const ok = await askUser("Submit and use one edit chance?");
        if (!ok) return;

        const students = document.querySelectorAll('[id^="s_"]');
        const attendance = Array.from(students).map(s => ({ 
            id: s.id.split('_')[1], 
            status: s.value 
        }));

        const res = await fetch('/api/sync-attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ attendance })
        });
        
        const result = await res.json();
                if (result.success) {
            showToast("✅ Attendance Synced!", "success");
            await this.checkLockStatus();
            await this.loadInterface();
        }
            showToast("✅ Attendance Synced!", "success");
            await this.checkLockStatus();
            this.loadInterface();
        } else {
            showToast("❌ Error: " + result.error, "error");
        }
    }
};

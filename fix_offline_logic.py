import re

file_path = "mobile_app.py"
with open(file_path, 'r') as f:
    content = f.read()

# 1. Fix the Object_from_iterable logic and Submit function
old_function_pattern = r"window\.submitLeaveRequest = async function\(\) \{.*?\n\};"
new_function = """window.submitLeaveRequest = async function() {
    const btn = document.getElementById('l-sub-btn');
    const start = document.getElementById('l-start').value;
    const end = document.getElementById('l-end').value;
    const reason = document.getElementById('l-reason').value;
    const file = document.getElementById('l-file').files[0];

    if(!start || !end || !reason) return alert("Please fill all required fields!");

    const fd = new FormData();
    fd.append('start_date', start);
    fd.append('end_date', end);
    fd.append('reason', reason);
    if(file) fd.append('attachment', file);

    try {
        btn.disabled = true;
        btn.innerText = "PROCESSING...";

        if (!navigator.onLine) {
            // OFFLINE PATH
            const offlineData = {};
            fd.forEach((value, key) => { 
                if(!(value instanceof File)) offlineData[key] = value; 
            });
            
            await saveOffline('/api/leave/submit', 'POST', offlineData);
            alert("📡 Offline Mode: Leave saved locally! It will sync when you are online.");
            if(typeof renderLeaveHistory === 'function') renderLeaveHistory();
            btn.disabled = false;
            btn.innerText = "🚀 Submit Request";
            return;
        }

        // ONLINE PATH
        const res = await fetch('/api/leave/submit', {method:'POST', body:fd});
        const result = await res.json();
        
        if(result.success) {
            alert("🚀 Leave Submitted Successfully!");
            if(typeof renderLeaveHistory === 'function') renderLeaveHistory();
        } else {
            throw new Error(result.error || "Server rejected submission");
        }
    } catch (e) {
        console.error(e);
        alert("❌ Error: " + e.message);
    } finally {
        btn.disabled = false;
        btn.innerText = "🚀 Submit Request";
    }
};"""

# Function replace kar rahe hain
content = re.sub(r"window\.submitLeaveRequest = async function\(\) \{.*?\n\};", new_insert=new_function, string=content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Offline Submission Logic Re-engineered!")

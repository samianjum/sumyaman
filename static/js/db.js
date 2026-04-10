// Dexie Database Setup
const db = new Dexie("SchoolOfflineDB");

// Tables: 'syncQueue' mein hum offline data rakhenge
db.version(1).stores({
    syncQueue: '++id, url, method, body, timestamp'
});

// Function: Offline data save karne ke liye
async function saveOffline(url, method, body) {
    await db.syncQueue.add({
        url: url,
        method: method,
        body: body,
        timestamp: new Date().getTime()
    });
    console.log("💾 Data saved to Offline Storage (Dexie)");
}

// Function: Jab net aaye to data sync karein
async function syncOfflineData() {
    if (!navigator.onLine) return;
    
    const pending = await db.syncQueue.toArray();
    if (pending.length === 0) return;

    console.log("🔄 Syncing offline data...");
    
    for (const item of pending) {
        try {
            const res = await fetch(item.url, {
                method: item.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item.body)
            });
            
            const resData = await res.json();
            
            // Sirf tab delete karo jab server sach mein success: true de
            if (res.ok && resData.status !== 'offline' && resData.success === true) {
                await db.syncQueue.delete(item.id);
                console.log("✅ Sync successful and verified by Server for ID:", item.id);
                // Agar history function available hai to refresh karo
                if (typeof renderLeaveHistory === 'function') renderLeaveHistory();
            } else {
                console.warn("⚠️ Server rejected or offline fake response. Data kept safe.", resData);
            }
        } catch (e) {
            console.error("❌ Sync failed, will retry later:", e);
        }
    }
}

// Net aane par khud ba khud sync shuru karein
window.addEventListener('online', syncOfflineData);

// App load hone par aur har 15 second baad double check karein
window.addEventListener('load', () => {
    setTimeout(syncOfflineData, 2000);
    setInterval(syncOfflineData, 15000);
});

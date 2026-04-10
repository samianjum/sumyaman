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
            if (res.ok) {
                await db.syncQueue.delete(item.id);
                alert("🔄 Background Sync Complete!"); console.log("✅ Sync successful for ID:", item.id);
            }
        } catch (e) {
            console.error("❌ Sync failed, will retry later:", e);
        }
    }
}

// Net aane par khud ba khud sync shuru karein
window.addEventListener('online', syncOfflineData);

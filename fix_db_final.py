import os

db_code = """const db = new Dexie("SchoolOfflineDB");
db.version(1).stores({ syncQueue: '++id, url, method, body, timestamp' });

async function saveOffline(url, method, body) {
    await db.syncQueue.add({ url, method, body, timestamp: Date.now() });
    alert("📴 Offline: Application saved locally. It will sync when internet returns.");
}

async function syncOfflineData() {
    if (!navigator.onLine) return;
    const pending = await db.syncQueue.toArray();
    for (const item of pending) {
        try {
            const res = await fetch(item.url, {
                method: item.method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item.body)
            });
            if (res.ok) await db.syncQueue.delete(item.id);
        } catch (e) { console.error("Sync failed:", e); }
    }
}
window.addEventListener('online', syncOfflineData);"""

with open('static/js/db.js', 'w') as f:
    f.write(db_code)
print("[✔] Offline Database Logic Updated.")

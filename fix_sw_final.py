import os

sw_code = """const CACHE_NAME = 'aps-portal-v140';
const ASSETS = ['/', '/static/manifest.json', '/static/logo.png', '/static/tailwind.min.css', '/static/js/dexie.js', '/static/js/db.js'];

self.addEventListener('install', e => {
    self.skipWaiting();
    e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
});

self.addEventListener('activate', e => {
    e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
});

self.addEventListener('fetch', e => {
    // Catch Leave Application (POST) when offline
    if (e.request.method === 'POST' && e.request.url.includes('/api/leave/apply')) {
        e.respondWith(
            fetch(e.request.clone()).catch(async () => {
                // Agar net nahi hai, to response fake karo aur UI ko bolo 'Saved Offline'
                return new Response(JSON.stringify({success: true, offline: true}), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }
    // Default: Cache first, then network
    e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(res => res || fetch(e.request)));
});"""

with open('static/sw.js', 'w') as f:
    f.write(sw_code)
print("[✔] Service Worker is now Offline-Ready.")

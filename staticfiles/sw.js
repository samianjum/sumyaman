const CACHE_NAME = 'aps-portal-v118';
const ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/logo.png',
    '/static/tailwind.min.css',
    '/static/js/dexie.js',
    '/static/js/db.js',
    '/static/finalize.js',
    '/static/marks_v3.js',
    '/static/student_view.js'
];

self.addEventListener('install', e => {
    self.skipWaiting();
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('📦 Caching assets and main page');
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        )).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', e => {
    if (e.request.url.includes('/logout') || e.request.url.includes('/api/login')) {
        if(!navigator.onLine) return new Response('Offline', {status: 503}); return;
    }
    
    // API requests: Network first, then fallback
    if (e.request.url.includes('/api/')) {
        e.respondWith(
            fetch(e.request).then(response => {
                if (response.ok && e.request.method === 'GET') {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(e.request, copy));
                }
                return response;
            }).catch(async () => {
                const cached = await caches.match(e.request);
                return cached || new Response(JSON.stringify({status: 'offline', error: 'No cached data available'}), {
                    headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // Assets & Pages: Cache first, then Network
    e.respondWith(
        caches.match(e.request).then(response => {
            return response || fetch(e.request).then(fetchRes => {
                return caches.open(CACHE_NAME).then(cache => {
                    // Sirf valid GET requests cache karein
                    if (e.request.method === 'GET') {
                        cache.put(e.request, fetchRes.clone());
                    }
                    return fetchRes;
                });
            });
        }).catch(() => {
            // Agar bilkul kuch na mile (Offline & Not in Cache)
            })
    );
});
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('aps-store').then((cache) => cache.addAll([
      '/',
      '/static/manifest.json',
      '/static/logo.png'
    ]))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});

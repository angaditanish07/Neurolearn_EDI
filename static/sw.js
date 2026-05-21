const CACHE_NAME = 'neurolearn-static-v1';
const STATIC_ASSETS = [
    '/static/style.css',
    '/static/script.js',
    '/static/brain.png',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    const url = new URL(event.request.url);
    if (!url.pathname.startsWith('/static/')) return;
    event.respondWith(
        caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
});

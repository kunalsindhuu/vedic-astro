const CACHE = 'vedic-astro-v1';
const APP_SHELL = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    '/static/images/icon-192.png',
    '/static/images/icon-512.png'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);

    if (e.request.method !== 'GET') return;
    if (!url.origin.includes('vedic') && url.origin !== self.location.origin) return;

    if (url.pathname.startsWith('/api/')) {
        e.respondWith(
            fetch(e.request).catch(() =>
                caches.match('/').then((r) => r || new Response('{"error":"offline"}', { status: 503, headers: { 'Content-Type': 'application/json' } }))
            )
        );
        return;
    }

    e.respondWith(
        fetch(e.request)
            .then((res) => {
                const copy = res.clone();
                caches.open(CACHE).then((cache) => cache.put(e.request, copy));
                return res;
            })
            .catch(() => caches.match(e.request).then((hit) => hit || caches.match('/')))
    );
});
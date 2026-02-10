const CACHE_NAME = 'gitasarathi-v3';
const STATIC_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/voice.js',
    '/static/js/api.js',
    '/static/manifest.json',
];

// Install — cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — network first for API, cache first for static
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // API calls: network first
    if (url.pathname.startsWith('/ask') || url.pathname.startsWith('/api/') || url.pathname.startsWith('/shloka/')) {
        event.respondWith(
            fetch(event.request).catch(() =>
                new Response(JSON.stringify({ error: 'ऑफ़लाइन हैं' }), {
                    headers: { 'Content-Type': 'application/json' },
                })
            )
        );
        return;
    }

    // Static: cache first, then network
    event.respondWith(
        caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
});

const CACHE_NAME = 'sociology-pwa-v2';
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/js/db.js',
    '/static/js/sync.js',
    '/static/js/app.js'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME)
                        .map((name) => caches.delete(name))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - network first for HTML/API, cache first for static assets
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    const url = new URL(event.request.url);

    // API requests - always network, never cache
    if (url.pathname.startsWith('/api/')) {
        return;
    }

    // Static JS modules - cache first, then network
    if (url.pathname.startsWith('/static/js/')) {
        event.respondWith(
            caches.match(event.request)
                .then((cached) => {
                    if (cached) {
                        // Return cached, but also update in background
                        fetch(event.request)
                            .then((response) => {
                                if (response.ok) {
                                    caches.open(CACHE_NAME)
                                        .then((cache) => cache.put(event.request, response));
                                }
                            })
                            .catch(() => {}); // Ignore network errors for background update
                        return cached;
                    }
                    // Not cached, fetch and cache
                    return fetch(event.request)
                        .then((response) => {
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME)
                                .then((cache) => cache.put(event.request, responseClone));
                            return response;
                        });
                })
        );
        return;
    }

    // Other static assets - network first, fallback to cache
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Clone the response before caching
                const responseClone = response.clone();
                caches.open(CACHE_NAME)
                    .then((cache) => cache.put(event.request, responseClone));
                return response;
            })
            .catch(() => {
                // Network failed, try cache
                return caches.match(event.request);
            })
    );
});
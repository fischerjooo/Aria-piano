/* Aria Piano: network-first updates and offline support for GitHub Pages. */
const CACHE = 'aria-piano-shell-v3';
const HOME = new URL('./', self.registration.scope).href;
const ASSETS = [
  HOME,
  new URL('manifest.webmanifest', HOME).href,
  new URL('icons/aria.svg', HOME).href,
  new URL('icons/aria-192.png', HOME).href,
  new URL('icons/aria-512.png', HOME).href,
  new URL('icons/aria-maskable-512.png', HOME).href,
];
const STATIC = new Set(ASSETS.slice(1));

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(ASSETS);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith('aria-piano-shell-') && name !== CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate' && (url.pathname === new URL(HOME).pathname || url.pathname === new URL('index.html', HOME).pathname)) {
    // App launches fetch the newest successful Pages deployment, even if the SW code hasn't changed.
    event.respondWith((async () => {
      try {
        const response = await fetch(request, { cache: 'no-store' });
        if (response.ok) {
          const cache = await caches.open(CACHE);
          await cache.put(HOME, response.clone());
        }
        return response;
      } catch (_) {
        return (await caches.match(HOME)) || Response.error();
      }
    })());
  } else if (STATIC.has(url.href)) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      return (await cache.match(request)) || fetch(request);
    })());
  }
});

self.addEventListener('message', (event) => {
  if (!event.data || event.data.type !== 'ARIA_CHECK_UPDATE') return;
  event.waitUntil((async () => {
    try {
      const cache = await caches.open(CACHE);
      const previous = await cache.match(HOME);
      const latest = await fetch(HOME, { cache: 'no-store' });
      if (!latest.ok) return;
      const newContent = await latest.clone().text();
      const oldContent = previous ? await previous.text() : null;
      await cache.put(HOME, latest);
      if (oldContent !== null && oldContent !== newContent && event.source) {
        event.source.postMessage({ type: 'ARIA_UPDATE_AVAILABLE' });
      }
    } catch (_) {
      // Offline checks must never interrupt piano practice.
    }
  })());
});

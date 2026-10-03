/* NaimBH.com service worker — fast repeat visits + offline support */
const VERSION = 'naimbh-v5';
const SHELL = [
  '/', '/freelancer/', '/offline.html', '/site.webmanifest',
  '/favicon.svg', '/favicon.ico', '/icon-192.png', '/icon-512.png', '/logo.svg',
  '/images/naim-bin-hasan-portrait-480.webp', '/images/naim-bin-hasan-portrait-800.webp',
  '/freelancer/images/naim-bin-hasan-full-stack-web-developer-480.webp'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Pages: network first (always fresh), fall back to cache, then the offline page
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(res => {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then(r => r || caches.match('/offline.html')))
    );
    return;
  }

  // Same-origin images/icons and Google Fonts: serve from cache, refresh in the background
  const isFont = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  const isAsset = url.origin === location.origin && /\.(webp|jpg|jpeg|png|svg|ico|pdf|webmanifest)$/.test(url.pathname);
  if (isFont || isAsset) {
    e.respondWith(
      caches.open(VERSION).then(c => c.match(req).then(hit => {
        const net = fetch(req).then(res => { if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone()); return res; }).catch(() => hit);
        return hit || net;
      }))
    );
  }
});

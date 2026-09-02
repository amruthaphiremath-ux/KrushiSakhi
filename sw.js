// Minimal service worker — required by browsers before they'll offer
// "Install app" / "Add to Home Screen". Does simple pass-through caching
// of static files so the app shell loads instantly on repeat opens.

const CACHE_NAME = "krishisakhi-v1";
const CORE_ASSETS = ["/", "/static/style.css", "/static/script.js"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  // Network-first for the /predict API so prices are always fresh;
  // cache-first for everything else (static assets).
  if (event.request.url.includes("/predict")) {
    return; // let it go straight to the network
  }
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});

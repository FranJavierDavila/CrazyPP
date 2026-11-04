/* =====================================================================
 * CRAZY PING PONG · SERVICE WORKER (r109 · hito M3 del roadmap MEJORAS.md)
 * =====================================================================
 * PWA INSTALABLE: icono en el casco, arranque sin teclear URL y
 * actualizaciones que el BUMP GOBIERNA SOLO.
 *
 *  · El NOMBRE de la caché lleva la versión (const CACHE = 'crazypp-vX.Y.Z-SDK6').
 *    bump_version.py parchea ese sello en cada bump: al publicarse una
 *    versión nueva el sw.js cambia de byte → el navegador actualiza el SW →
 *    activate BORRA las cachés viejas → invalidación automática. Adiós ?v=.
 *  · game.html: STALE-WHILE-REVALIDATE (arranque instantáneo desde caché;
 *    la respuesta fresca queda instalada para LA PRÓXIMA visita).
 *  · Datos vivos (PAGES-VERSION.txt, campeonatos, ugc): NETWORK-FIRST con
 *    fallback a caché (offline) — nunca sirven versiones viejas si hay red.
 *  · Assets estáticos (assets/, vendor/, iconos): CACHE-FIRST con relleno
 *    bajo demanda.
 *  · Sólo GET same-origin: el worker de telemetría (workers.dev) y PeerJS
 *    pasan de largo.
 *  · Sin precarga pesada: en install sólo la CÁSCARA (game.html + manifest
 *    + iconos); lo demás se cachea al volar. game.html pesa ~10 MB: la
 *    instalación no duplica el peso.
 * ===================================================================== */

const CACHE = 'crazypp-v3.6.105-SDK6';   // ← SELLO: bump_version.py lo parchea

const SHELL = [
  './game.html',
  './manifest.webmanifest',
  './logo-192.png',
  './logo-512.png',
];

/* Rutas (relativas al scope /CrazyPP/) que son DATOS VIVOS: red primero. */
const VIVAS = [/\/championships\//, /\/ugc\//, /\/PAGES-VERSION\.txt$/, /\/robots\.txt$/, /\/telemetria\.html$/];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // .add en serie con tolerancia: si un miembro de la cáscara falla (red
    // inestable al instalar), la instalación NO se revienta entera.
    for (const url of SHELL) {
      try {
        await cache.add(new Request(url, { cache: 'reload' }));
      } catch (e) { /* se rellenará al volar */ }
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const claves = await caches.keys();
    await Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

async function swr(req) {
  const cache = await caches.open(CACHE);
  const cacheada = await cache.match(req, { ignoreSearch: true });
  const fresca = fetch(req).then((resp) => {
    if (resp && resp.ok) cache.put(req, resp.clone()).catch(() => { });
    return resp;
  }).catch(() => cacheada);
  return cacheada || fresca;
}

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const resp = await fetch(req);
    if (resp && resp.ok) cache.put(req, resp.clone()).catch(() => { });
    return resp;
  } catch (e) {
    const cacheada = await cache.match(req, { ignoreSearch: true });
    if (cacheada) return cacheada;
    throw e;
  }
}

async function cacheFirst(req) {
  const cache = await caches.open(CACHE);
  const cacheada = await cache.match(req, { ignoreSearch: true });
  if (cacheada) return cacheada;
  try {
    const resp = await fetch(req);
    if (resp && resp.ok) cache.put(req, resp.clone()).catch(() => { });
    return resp;
  } catch (e) {
    if (cacheada) return cacheada;
    throw e;
  }
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;   // worker telemetría · PeerJS · Ko-fi
  if (url.pathname.endsWith('/game.html')) {
    event.respondWith(swr(req));
    return;
  }
  if (VIVAS.some((re) => re.test(url.pathname))) {
    event.respondWith(networkFirst(req));
    return;
  }
  event.respondWith(cacheFirst(req));
});

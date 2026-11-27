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
 *  · game.html: RED-PRIMERO con límite 4 s (r98 — era STALE-WHILE-REVALIDATE
 *    y el dueño veía SIEMPRE una visita por detrás: abría, leía la versión
 *    vieja y reportaba «no cambió nada» 4 rondas). Con red manda la red
 *    (no-store); la caché es la red de seguridad offline.
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

const CACHE = 'crazypp-v3.6.238-SDK6';   // ← SELLO: bump_version.py lo parchea

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
    // r96 · claim INMEDIATO, purga DIFERIDA: la página ANTERIOR sigue viva
    // en memoria tras el claim y puede seguir pidiendo sus assets (audio
    // del saque, voces, skins…) — borrar su caché EN EL MISMO INSTANTE fue
    // el presunto bloqueo del arranque en el casco (cache-first → misses
    // en cadena justo cuando se pulsa JUGAR tras una actualización). La
    // caché vieja se borra 5 min después: nadie la necesita ya.
    await self.clients.claim();
    setTimeout(async () => {
      try {
        const claves = await caches.keys();
        await Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
      } catch (e) { /* la próxima activate lo reintenta */ }
    }, 5 * 60 * 1000);
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

async function redPrimero(req, ms) {
  // r98 · game.html pasa de STALE-WHILE-REVALIDATE a RED-PRIMERO con límite:
  // el dueño abría UNA vez, veía la copia cacheada («cacheada || fresca» ga-
  // ranta ver la VIEJA aunque la red responda) y reportaba «no cambió nada»
  // — 4 rondas seguidas. Ahora la red manda (con no-store: ni el HTTP cache
  // de Pages puede colar una copia) y la caché es SOLO la red de seguridad
  // si la red tarda ms o falla (offline / casco sin wifi).
  const cache = await caches.open(CACHE);
  const cacheada = await cache.match(req, { ignoreSearch: true });
  try {
    const resp = await Promise.race([
      fetch(new Request(req, { cache: 'no-store' })),
      new Promise((res, rechaza) => setTimeout(() => rechaza(new Error('tarda')), ms || 4000)),
    ]);
    if (resp && resp.ok) cache.put(req, resp.clone()).catch(() => { });
    return resp;
  } catch (e) {
    if (cacheada) return cacheada;
    throw e;
  }
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
    event.respondWith(redPrimero(req, 4000));
    return;
  }
  if (VIVAS.some((re) => re.test(url.pathname))) {
    event.respondWith(networkFirst(req));
    return;
  }
  event.respondWith(cacheFirst(req));
});

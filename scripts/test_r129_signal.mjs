#!/usr/bin/env node
/* CRAZY PING PONG · A2 (r129 · ola 3) · prueba del interruptor del broker.
 * globalThis.PP_SIGNAL_ENDPOINT → NetLink._signalOpts() (host/port/path/
 * secure) y el comportamiento por defecto: cloud de PeerJS sin opciones,
 * idéntico a como siempre. Importa la fuente REAL c09 (con shim de
 * navegador como los otros arneses). */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-a2' }; } catch (e) { /* getter */ }

let ok = 0, fail = 0;
const chk = (c, l) => {
  console.log((c ? "  ✓ " : "  ✗ FALLO: ") + l);
  ok += c ? 1 : 0;
  fail += c ? 0 : 1;
};

const { NetLink } = await import('/home/z/my-project/src/game/core/c09_red_netlink.js');

// 1 · por defecto: cloud (sin opciones) — comportamiento idéntico al r122
delete globalThis.PP_SIGNAL_ENDPOINT;
chk(NetLink._signalOpts() === undefined, 'sin PP_SIGNAL_ENDPOINT → cloud de PeerJS (undefined)');

// 2 · https con puerto y ruta
globalThis.PP_SIGNAL_ENDPOINT = 'https://sena.crazypp.es:8443/peerjs';
let o = NetLink._signalOpts();
chk(o && o.host === 'sena.crazypp.es' && o.port === 8443 && o.secure === true && o.path === '/peerjs/',
  `https con puerto y ruta → ${JSON.stringify(o)}`);

// 3 · https sin puerto → 443
globalThis.PP_SIGNAL_ENDPOINT = 'https://sena.crazypp.es/peerjs';
o = NetLink._signalOpts();
chk(o && o.port === 443 && o.secure === true, 'https sin puerto → 443 seguro');

// 4 · http local (el gateway Caddy del repo: :81 no aplica, el peer-server va en 3005)
globalThis.PP_SIGNAL_ENDPOINT = 'http://localhost:3005/peerjs';
o = NetLink._signalOpts();
chk(o && o.host === 'localhost' && o.port === 3005 && o.secure === false && o.path === '/peerjs/',
  'http localhost:3005 → sin TLS');

// 5 · ruta con barra final doble → se normaliza
globalThis.PP_SIGNAL_ENDPOINT = 'https://x.es/peerjs/';
o = NetLink._signalOpts();
chk(o && o.path === '/peerjs/', 'barra final doble normalizada a /peerjs/');

// 6 · inválida → undefined con aviso (nunca rompe el arranque)
globalThis.PP_SIGNAL_ENDPOINT = 'no es una url';
chk(NetLink._signalOpts() === undefined, 'URL inválida → undefined con aviso');

// 7 · esquema no http(s) → undefined
globalThis.PP_SIGNAL_ENDPOINT = 'ftp://x/peerjs';
chk(NetLink._signalOpts() === undefined, 'esquema no http(s) → undefined');

delete globalThis.PP_SIGNAL_ENDPOINT;
console.log(`RESULTADO: ${ok} OK · ${fail} FALLOS`);
// c09 arrastra c00 (tunas del shell en Node): salida explícita, patrón de la casa
process.exit(fail ? 1 : 0);

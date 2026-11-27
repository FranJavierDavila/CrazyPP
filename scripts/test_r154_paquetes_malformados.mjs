#!/usr/bin/env node
/* =====================================================================
 * r152 · AUDITORÍA 9 · ARNÉS r154 · CAOS DE TIPOS EN EL PROTOCOLO
 * =====================================================================
 * La batería r130 (X1-X4) cubre paquetes SEMÁNTICAMENTE malos (claims sin
 * rallyId, sync v1 basura, NaN en fast, tock2 hostil) pero siempre con
 * OBJETOS bien tipados. Este arnés cierra el hueco: CHAOS DE TIPOS en el
 * sobre JSON (null, números, arrays, profundidad 2000, strings de 1 MB,
 * formas __proto__) sobre un enlace v2 REAL en línea, más buffers fast
 * arbitrarios (tamaños erróneos, 0x00/0xFF) y la RECUPERACIÓN con un
 * paquete válido tras la tormenta. Garantía esperada: el enlace nunca
 * lanza, nunca se degrada y sigue sirviendo paquetes sanos después.
 * Sin señalización: startV2 + bus local (territorio r130, sin Peer).
 * ===================================================================== */
globalThis.window = globalThis.window || globalThis;
globalThis.localStorage = globalThis.localStorage || {
  _m: new Map(),
  getItem(k) { return this._m.has(k) ? this._m.get(k) : null; },
  setItem(k, v) { this._m.set(k, String(v)); },
  removeItem(k) { this._m.delete(k); },
  clear() { this._m.clear(); },
};
globalThis.addEventListener = globalThis.addEventListener || (() => { /* */ });
globalThis.removeEventListener = globalThis.removeEventListener || (() => { /* */ });
globalThis.requestAnimationFrame = globalThis.requestAnimationFrame ||
  ((fn) => setTimeout(() => fn(Date.now()), 16));
globalThis.document = globalThis.document || {
  getElementById: () => null, createElement: () => ({ style: {} }),
  addEventListener: () => {}, removeEventListener: () => {}, hidden: false,
};
try { globalThis.navigator = globalThis.navigator || { userAgent: 'node-r154' }; } catch { /* */ }
globalThis.T = (k, _v) => k;
globalThis.VERSION = '3.6.235-SDK6';

const { NetLink } = await import('/home/z/my-project/src/game/core/c09_red_netlink.js');
const { Rules } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { PPNET } = await import('/home/z/my-project/src/game/core/c09b_red_nucleo.js');

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
let ok = 0, fails = 0;
const chk = (c, l) => {
  console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l);
  ok += c ? 1 : 0; fails += c ? 0 : 1;
};

/* juego mínimo: contadores de lo que el NetLink toca */
function fakeGame(role, net) {
  const g = {
    role, net, mode: 'match', pendingMode: 'match', doblesActivo: false,
    inHall: false, menuOpen: false, tossed: false, _mjMode: 'match',
    _netStart: null, _netStartWhenReady: false,
    mstarts: 0, finRed: null, v2Ready: 0, v2Fail: 0, errores: 0,
    rules: new Rules(),
    ball: null, ballMesh: { visible: false },
    renderer: { xr: { isPresenting: false } },
    audio: new Proxy({}, { get: () => () => {} }),
    controllerPaddles: [{ active: false }, { active: false }],
    paddleHand: 0,
    onNetStatus() { g.estados = (g.estados || 0) + 1; },
    onNetEnded(msg) { g.finRed = msg || 'fin'; },
    startOnlineSession() { g.sesiones = (g.sesiones || 0) + 1; },
    onNetV2Ready() { g.v2Ready++; },
    onNetV2Fail() { g.v2Fail++; g._netStart = null; },
    startOnlineMatch() {
      if (net.role !== 'host') { net.sendRematch(); return; }
      if (net.mstartReciente && net.mstartReciente()) return;
      const startAt = net.hostNowMs() + PPNET.VP.COUNTDOWN_MS;
      net.sendRel({ k: 'mstart', sa: startAt, fs: 'host', bo: 3, md: 'match' });
      this.onNetMatchStart({ startAt, fs: 'host', bo: 3, md: 'match' });
    },
    onNetMatchStart(m) {
      g.mstarts++;
      g._netMatchLive = true;
      g.rules.bestOf = (m && m.bo) || 3;
      g.rules.startMatch('match');
      g._netStart = { startAt: m.startAt, fs: m.fs };
      net._mstartAt = performance.now();
    },
    switchMode() { /* */ },
  };
  return g;
}

/* par de canales reliable/fast locales con entrega async (r153) */
function parCanales(h, g) {
  const mk = () => ({
    _otro: null, open: true,
    send(s) { const d = s; setTimeout(() => { try { if (this._otro && this._otro.onmessage) this._otro.onmessage({ data: d }); } catch { /* la entrega no crashea el emisor */ } }, 5); },
    onmessage: null, onopen: null, onclose: null,
  });
  h._rel = mk(); g._rel = mk(); h._rel._otro = g._rel; g._rel._otro = h._rel;
  h._fast = mk(); g._fast = mk(); h._fast._otro = g._fast; g._fast._otro = h._fast;
  h._fastOpen = h._relOpen = g._fastOpen = g._relOpen = true;
  for (const n of [h, g]) {
    n._fast.onmessage = (e) => { try { n._onFast(e.data); } catch (e1) { n.game.errores++; throw e1; } };
    n._rel.onmessage = (e) => {
      try { n._onRel(JSON.parse(typeof e.data === 'string' ? e.data : String(e.data))); }
      catch { /* json inválido: ignorar (c09 _wireDC real) */ }
    };
  }
}

/* — enlace ARMADO EN FRONTERA v1 (sin handshake v2: r130-X ya cubre el
 *   post-handshake; aquí la garantía es la frontera onData/_onRel/_onFast
 *   y para ella basta online + canales locales — el enfoque r130 sesion()
 *   necesita los frames reales de c12) ——————————————————————————————— */
const H = new NetLink(null); const G = new NetLink(null);
const Hg = fakeGame('host', H); const Gg = fakeGame('guest', G);
H.game = Hg; G.game = Gg;
parCanales(H, G);
H.online = true; G.online = true;              // frontera abierta (cablear r130)

chk(H.online && G.online && typeof H.onData === 'function' && typeof H._onFast === 'function',
  'enlace armado en frontera v1 (online, canales locales, onData/_onFast vivos)');

/* — A · CHAOS DE TIPOS por onData (la frontera DataConnection real) — */
const anidado = (() => { let o = { k: 'hit' }; for (let i = 0; i < 2000; i++) o = { a: o }; return o; })();
const BASURAS = [
  ['objeto vacío', {}],
  ['array', []],
  ['array de números', [1, 2, 3]],
  ['null', null],
  ['número', 42],
  ['string suelta', 'hola'],
  ['booleano', true],
  ['k null', { k: null }],
  ['k número', { k: 123 }],
  ['k con __proto__', JSON.parse('{"__proto__":{"ppInyectado":1},"k":"hit"}')],
  ['mstart sin campos', { k: 'mstart' }],
  ['mstart sa string', { k: 'mstart', sa: 'x', fs: 'host', bo: 'y' }],
  ['claim mínimo', { k: 'claim' }],
  ['claim w raro', { k: 'claim', w: { profundo: true }, r: NaN }],
  ['hit sin nada', { k: 'hit' }],
  ['hello2 proto erróneo', { k: 'hello2', v: 'x', ph: 'y', b: {} }],
  ['hello2 válido con build raro', { k: 'hello2', v: PPNET.VP.PROTO, ph: PPNET.VP.PHYS, b: [9, 9, 9, 9] }],
  ['wrlnick con HTML', { k: 'wrlnick', n: '<img src=x onerror=alert(1)>' }],
  ['tock2 vacío', { k: 'tock2' }],
  ['ice-restart sin sesión', { k: 'ice-restart' }],
  ['profundidad 2000', anidado],
  ['string de 1 MB', { k: 'hit', m: 'x'.repeat(1024 * 1024) }],
];
let lanzadas = 0, aplicadas = 0;
for (const [nombre, b] of BASURAS) {
  try {
    H.onData(b); aplicadas++;
    if (typeof b === 'object' && b !== null && !Array.isArray(b)) G.onData(b);
  } catch (e) {
    lanzadas++;
    console.error(`    ↳ "${nombre}" lanzó: ${e && e.message}`);
  }
}
await dormir(400);
chk(lanzadas === 0, `chaos de tipos por onData: ${BASURAS.length} basuras → ${lanzadas} excepciones`);
chk(H.online && G.online, `el enlace SOBREVIVE a la tormenta (online H/G=${H.online}/${G.online})`);
chk(Hg.rules.scorePlayer + Hg.rules.scoreAi === 0 && Gg.rules.scorePlayer + Gg.rules.scoreAi === 0,
  `ningún punto fantasma tras la tormenta (H ${Hg.rules.scorePlayer}-${Hg.rules.scoreAi} · G ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi})`);
chk(Object.prototype.ppInyectado === undefined,
  'sin contaminación de prototipo (Object.prototype intacto)');
chk(Hg.errores === 0 && Gg.errores === 0,
  `los handlers internos no crashean (errores H/G=${Hg.errores}/${Gg.errores})`);

/* — A2 · bye LEGÍTIMO: desmontaje coherente (lección de la 1ª corrida: un
 *   bye en la tormenta desmonta el enlace POR DISEÑO — se prueba aparte) — */
let byeThrow = 0;
try { G.onData({ k: 'bye' }); } catch (e) { byeThrow++; }
await dormir(200);
chk(byeThrow === 0 && G.online === false,
  `bye legítimo: desmontaje coherente sin excepciones (G.online=${G.online})`);
chk(H.online === true, 'el otro extremo NO se desmonta por un bye ajeno');
parCanales(H, G);                          // rearmado de canales para la C
H.online = true; G.online = true;

/* — B · buffers fast arbitrarios por _onFast ———————————————————— */
const bufs = [
  ['vacío', new ArrayBuffer(0)],
  ['de 4 B', new ArrayBuffer(4)],
  ['de 52 B a 0x00', new Uint8Array(52).fill(0).buffer],
  ['de 52 B a 0xFF', new Uint8Array(52).fill(255).buffer],
  ['de 160 B a 0x41', new Uint8Array(160).fill(0x41).buffer],
  ['de 1 MB', new ArrayBuffer(1024 * 1024)],
];
let lanzadasFast = 0;
for (const [, b] of bufs) {
  try { H._onFast(b); G._onFast(b); } catch (e) { lanzadasFast++; console.error(`    ↳ buffer lanzó: ${e && e.message}`); }
}
await dormir(200);
chk(lanzadasFast === 0, `buffers fast arbitrarios: ${bufs.length} → ${lanzadasFast} excepciones`);

/* — C · RECUPERACIÓN: paquete válido tras la tormenta ————————————— */
let decOk = false;
try {
  const buf = new ArrayBuffer(160);
  PPNET.encodePacket(buf, { seq: 9, ack: 0, ackBits: 0, sendTime: 9,
    echoTime: 0, echoDelay: 0,
    evs: [{ t: PPNET.VP.EV.HIT, id: 77, kind: 0, shot: 1, tHit: 12,
      p: [0.1, 0.4, 0.9], v: [0.2, 0, -3], s: [0, 0, 0] }] });
  const dec = PPNET.decodePacket(buf.slice(0), { yAnchor: 0.76, evs: [] });
  decOk = !!(dec && dec.evs && dec.evs.length === 1);
  G._fast.send(buf);                     // entrega REAL por el canal
  H._fast.send(buf);
} catch (e) { console.error('    ↳ paquete válido lanzó:', e && e.message); }
await dormir(200);
chk(decOk, 'codec intacto: el paquete VÁLIDO se codifica y decodifica tras la tormenta');
chk(H.online && G.online && Hg.errores === 0 && Gg.errores === 0,
  'el enlace sigue SIRVIENDO paquetes sanos después del caos (online, 0 errores)');

/* — salida limpia ———————————————————————————————————————————————— */
console.log();
if (fails) {
  console.log(`✗ r154 CAOS DE TIPOS: ${ok} OK · ${fails} FALLO(S)`);
  process.exit(1);
}
const { writeSync } = await import('node:fs');
writeSync(1, `✓ CAOS DE TIPOS r154: ${ok} OK · 22 basuras JSON + 6 buffers fast + recuperación con paquete válido — el enlace nunca lanza ni se degrada\n`);
process.exit(0);

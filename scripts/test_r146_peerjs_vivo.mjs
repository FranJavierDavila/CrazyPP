#!/usr/bin/env node
/* =====================================================================
 * r146 · 11ª pasada · ARNÉS VIVO DE PEERJS
 * =====================================================================
 * La batería r130 conduce NetLink directamente (bus local): la CAPA DE
 * SALA — códigos, presencia, rechazos, reconexión, destrucción del
 * broker — jamás se ejercitaba con código real. Este arnés levanta un
 * PeerServer REAL (npm «peer», puerto 3005) y tres NetLink REALES
 * (anfitrión, invitado, intruso) sobre un shim de cliente que habla el
 * protocolo EXACTO sondado en scripts/probe_peer.mjs:
 *   ws://host:port/peerjs?id=…&token=…&key=peerjs + {type:'OPEN'}
 *   · ID-TAKEN → error 'unavailable-id'      (colisión de sala)
 *   · OFFER/ANSWER relayados con src/dst      (join real por broker)
 *   · oferta a id muerto → 'peer-unavailable' (emulado con tope: el
 *     servidor npm no responde; el cloud sí — contrato del cliente)
 *   · cierre del socket → error 'network' + 'disconnected' (r140: el
 *     micro SOBREVIVE a este tipo — recoverable)
 * El canal reliable/fast interno sigue siendo el par local (territorio
 * de la batería r130) pero la SEÑALIZACIÓN y el ciclo de vida cruzan el
 * broker de verdad: sala, join, intrusos, colisión de código y muerte
 * del servidor con el c09 REAL de punta a punta. */
import { createRequire } from 'node:module';
import { WebSocket as WS } from 'ws';
import { EventEmitter } from 'node:events';

const require_ = createRequire(import.meta.url);
import { spawn } from 'node:child_process';

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
let ok = 0, fail = 0;
const chk = (c, l) => {
  console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l);
  ok += c ? 1 : 0; fail += c ? 0 : 1;
};
const espera = async (fn, ms = 4000) => {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch { /* */ } await dormir(20); }
  return false;
};

/* ---------- shims de navegador (mínimos, como la batería) ---------- */
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
try { globalThis.navigator = globalThis.navigator || { userAgent: 'node-r146' }; } catch { /* */ }

const { NetLink } = await import('/home/z/my-project/src/game/core/c09_red_netlink.js');
const { Rules } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { T } = await import('/home/z/my-project/src/game/core/c00_pre_three.js');
// c06 referencia T en BARE (el build ensamblado la pone en el ámbito común);
// en Node aislado el puente por el global va aquí
globalThis.T = T;
const PPNET = (await import('/home/z/my-project/src/game/core/c09b_red_nucleo.js')).PPNET;

/* ---------- mock RTC: la subida v2 necesita piezas para no degradar */
globalThis.RTCPeerConnection = class {
  constructor() { this.signalingState = 'stable'; }
  async createOffer() { return { type: 'offer', sdp: 'x' }; }
  async createAnswer() { return { type: 'answer', sdp: 'x' }; }
  async setLocalDescription(d) { this.localDescription = d; }
  async setRemoteDescription(d) { this.remoteDescription = d; }
  async addIceCandidate() { /* */ }
  createDataChannel() { return { close() { /* */ } }; }   // inertes: el par real lo arma parCanales
  close() { /* */ }
};

/* ---------- shim de CLIENTE peerjs (protocolo sondado) ------------ */
const VIVOS = new Map();          // peerId → PeerShim (broker vivo)
const PARES = new Map();          // connectionId → { a: emisor, b: receptor }
let SHIM_TOKEN = 0;

class ConnShim extends EventEmitter {
  constructor(peer, dst, id, entrante) {
    super();
    this.peer = peer; this.peerId = dst; this.id = id;
    this.open = false; this.dataChannel = null;
    this.entrante = entrante;
  }
  send(d) {
    if (!this.open) return;
    const par = PARES.get(this.id);
    if (!par) return;
    const otro = par.a === this ? par.b : (par.b === this ? par.a : null);
    if (otro && otro.open) otro.emit('data', d);
  }
  close() {
    if (this._cerrada) return;          // idempotente de verdad (r146: la
    this._cerrada = true;               // guardia INVERTIDA tragaba el close
    this.open = false;                  // de las conexiones nunca abiertas —
    const par = PARES.get(this.id);     // los rechazos F1/r122 no cerraban)
    const otro = par ? (par.a === this ? par.b : (par.b === this ? par.a : null)) : null;
    if (par) PARES.delete(this.id);
    this.emit('close');
    if (otro && !otro._cerrada) otro.close();
  }
}

class PeerShim extends EventEmitter {
  constructor(id, opts = {}) {
    super();
    this.id = id || ('pp-auto-' + (++SHIM_TOKEN));
    this._opts = opts || {};
    this._dead = false;
    VIVOS.set(this.id, this);
    const proto = this._opts.secure ? 'wss' : 'ws';
    const port = Number(this._opts.port) || 443;
    const path = this._opts.path || '/';
    // el cliente peerjs real añade el segmento «peerjs» tras el path
    this._url = `${proto}://${this._opts.host}:${port}${path}peerjs` +
      `?id=${encodeURIComponent(this.id)}&token=t${++SHIM_TOKEN}&key=peerjs`;
    this._conectar();
  }
  _conectar() {
    const ws = new WS(this._url);
    this.ws = ws;
    ws.on('open', () => ws.send(JSON.stringify({ type: 'OPEN', payload: { token: 't' } })));
    ws.on('message', (d) => {
      let m = null;
      try { m = JSON.parse(d.toString()); } catch { return; }
      if (!m || !m.type) return;
      switch (m.type) {
        case 'OPEN': this.emit('open'); break;
        case 'ID-TAKEN': {
          this._dead = true;
          try { ws.close(); } catch { /* */ }
          VIVOS.delete(this.id);
          this.emit('error', { type: 'unavailable-id', payload: m.payload });
          break;
        }
        case 'ERROR': {
          this.emit('error', { type: (m.payload && m.payload.type) || 'server-error', payload: m.payload });
          break;
        }
        case 'OFFER': {
          // conexión ENTRANTE: registrar como lado B + responder (peerjs
          // auto-answer). Si el JUEGO la rechaza en el evento (F1/r122),
          // conn queda cerrada y el contestar la respeta (sin ANSWER).
          const cid = m.payload.connectionId;
          const conn = new ConnShim(this, m.src, cid, true);
          let par = PARES.get(cid);
          if (!par) { par = { a: null, b: null }; PARES.set(cid, par); }
          par.b = conn;
          this.emit('connection', conn);
          process.nextTick(() => {
            if (conn._cerrada || conn.open) return;
            try { ws.send(JSON.stringify({ type: 'ANSWER', dst: m.src,
              payload: { connectionId: cid } })); } catch { /* */ }
            conn.open = true;
            conn.emit('open');
          });
          break;
        }
        case 'ANSWER': {
          const par = PARES.get(m.payload.connectionId);
          if (par && par.a && !par.a.open) {
            clearTimeout(par.a._tope);
            par.a.open = true;
            par.a.emit('open');
          }
          break;
        }
        case 'EXPIRE': case 'CANDIDATE': case 'HEARTBEAT': case 'LEAVE': default: break;
      }
    });
    ws.on('close', () => {
      VIVOS.delete(this.id);
      if (this._dead) return;
      // peerjs real: socket muerto = error 'network' + evento disconnected
      this.emit('error', { type: 'network' });
      this.emit('disconnected');
    });
    ws.on('error', () => { /* el 'close' decide */ });
  }
  connect(dst, _opts) {
    const conn = new ConnShim(this, dst, 'c' + (++SHIM_TOKEN), false);
    PARES.set(conn.id, { a: conn });
    // tope de respuesta: el cloud real emite 'peer-unavailable' cuando la
    // oferta queda sin ANSWER (el servidor npm calla — contrato del cliente)
    conn._tope = setTimeout(() => {
      if (!conn.open && !conn._cerrada) {
        conn._cerrada = true; PARES.delete(conn.id);
        this.emit('error', { type: 'peer-unavailable',
          payload: { msg: 'Could not connect to peer ' + dst } });
      }
    }, 1200);
    try {
      this.ws.send(JSON.stringify({ type: 'OFFER', dst,
        payload: { connectionId: conn.id, sdp: 'x' } }));
    } catch { conn._cerrada = true; }
    return conn;
  }
  call(_id, _s) {
    return { answer() { /* */ }, on() { /* */ }, close() { /* */ } };
  }
  reconnect() {
    if (!this._dead) this._conectar();    // intento honesto (fallará si murió)
  }
  destroy() {
    this._dead = true;
    VIVOS.delete(this.id);
    try { this.ws && this.ws.close(); } catch { /* */ }
  }
}
globalThis.Peer = PeerShim;

/* ---------- juego mínimo para los NetLink (territorio batería) ---- */
function fakeGame(role, net) {
  const g = {
    role, net,
    mode: 'match', pendingMode: 'match', doblesActivo: false, inHall: false,
    menuOpen: false, tossed: false, _mjMode: 'match',
    _netStart: null, _netStartWhenReady: false,
    mstarts: 0, finRed: null, v2Ready: 0, v2Fail: 0,
    rules: new Rules(),
    ball: null, ballMesh: { visible: false },
    renderer: { xr: { isPresenting: false } },
    audio: new Proxy({}, { get: () => () => {} }),
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

/* par de canales reliable/fast locales (territorio batería r130) — con los
 * handlers EXACTOS de _wireDC (c09:1429-1451), que en el juego real se
 * adjuntan a los DataChannels de la RTCPeerConnection */
function parCanales(h, g) {
  const mk = (otro) => ({
    _otro: otro, open: true,
    send(s) { setTimeout(() => { try { if (this._otro.onmessage) this._otro.onmessage({ data: s }); } catch { /* */ } }, 8); },
    onmessage: null, onopen: null, onclose: null,
  });
  h._rel = mk(null); g._rel = mk(null);
  h._rel._otro = g._rel; g._rel._otro = h._rel;
  h._fast = mk(null); g._fast = mk(null);
  h._fast._otro = g._fast; g._fast._otro = h._fast;
  h._fastOpen = h._relOpen = g._fastOpen = g._relOpen = true;
  for (const n of [h, g]) {
    n._fast.onmessage = (e) => n._onFast(e.data);
    n._fast.onopen = null; n._fast.onclose = null;
    n._rel.onmessage = (e) => {
      try { n._onRel(JSON.parse(typeof e.data === 'string' ? e.data : String(e.data))); }
      catch { /* json inválido: ignorar (c09:1446) */ }
    };
    n._rel.onopen = null; n._rel.onclose = null;
  }
}

/* ---------- ARRANQUE: PeerServer REAL como proceso hijo en :3005 -- */
// r146 · higiene de puerto: los runs anteriores dejaban el hijo VIVO
// (huérfano sirviendo en :3005 — el hijo nuevo moría por EADDRINUSE y el
// SIGKILL de S7 mataba al nuevo, no al que servía). Se limpia ANTES y se
// mata AL FINAL; la sonda espera un OPEN real antes de seguir.
import { spawnSync } from 'node:child_process';
spawnSync('pkill', ['-f', 'PeerServer'], { stdio: 'ignore' });
await dormir(300);
const broker = spawn(process.execPath, ['-e',
  `require('/home/z/my-project/node_modules/peer/dist/index.cjs')` +
  `.PeerServer({port:3005,path:'/',key:'peerjs'});setInterval(()=>{},1e9);`],
  { stdio: 'ignore' });
{
  // sonda con REINTENTOS: el hijo tarda ~0,5 s en escuchar; un 'refused'
  // temprano no es fatal, se reintenta hasta el tope de 5 s
  const listo = await (async () => {
    const t0 = Date.now();
    while (Date.now() - t0 < 5000) {
      const r = await new Promise((res) => {
        const probe = new WS('ws://127.0.0.1:3005/peerjs?id=pp-probe&token=p&key=peerjs');
        const t = setTimeout(() => { try { probe.close(); } catch { /* */ } res(false); }, 800);
        probe.on('open', () => {
          // el servidor PeerJS exige el mensaje OPEN para responder
          try { probe.send(JSON.stringify({ type: 'OPEN', payload: { token: 'p' } })); } catch { /* */ }
        });
        probe.on('message', (d) => {
          try {
            if (JSON.parse(d.toString()).type === 'OPEN') {
              clearTimeout(t); try { probe.close(); } catch { /* */ } res(true);
            }
          } catch { /* */ }
        });
        probe.on('error', () => { clearTimeout(t); res(false); });
      });
      if (r) return true;
      await dormir(250);
    }
    return false;
  })();
  if (!listo) {
    console.log('✗ PEERJS VIVO: el broker REAL no arrancó en :3005');
    try { broker.kill('SIGKILL'); } catch { /* */ }
    process.exit(1);
  }
}
await dormir(200);

console.log('— S1 · sala REAL por broker + join + subida v2 + mstart');
{
  globalThis.PP_SIGNAL_ENDPOINT = 'http://127.0.0.1:3005';
  const H = new NetLink(null); const G = new NetLink(null);
  const Hg = fakeGame('host', H); const Gg = fakeGame('guest', G);
  H.game = Hg; G.game = Gg;
  H.hostRoom();
  chk(await espera(() => H.status === 'waiting'), `sala creada en el broker REAL (status=${H.status})`);
  const codigo = H.code;
  chk(codigo.length === 5, `código de sala con formato honesto (${codigo})`);
  G.joinRoom(codigo);
  chk(await espera(() => H.online && G.online, 4000),
    `join vivo por broker: AMBOS online (H=${H.status} · G=${G.status})`);
  // la señal del join cruzó el servidor: el conn del invitado apunta a la sala
  chk(G.conn && G.conn.peerId === NetLink.ROOM_PREFIX + codigo,
    'el conn del invitado nace de la SEÑALIZACIÓN real (dst = id de sala)');
  // subida v2 real: sdp/ICE viajan por la DataConnection (broker); los
  // canales internos son el par local (territorio batería r130)
  await dormir(250);
  parCanales(H, G);
  H._v2ChannelsUp(); G._v2ChannelsUp();
  chk(await espera(() => H.v2 === 'ok' && G.v2 === 'ok', 6000),
    `handshake v2 real sobre la sala (H=${H.v2} · G=${G.v2})`);
  chk(Hg.mstarts === 1 && Gg.mstarts === 1 && Gg._netMatchLive,
    `mstart automático del anfitrión en vivo (mstarts H/G=${Hg.mstarts}/${Gg.mstarts} · partida viva)`);
  globalThis.__S1 = { H, G, Hg, Gg, codigo };
}

console.log('— S2 · join a sala MUERTA: peer-unavailable honesto');
{
  const { H, G, Hg, Gg } = globalThis.__S1;
  const G2 = new NetLink(null); const Gg2 = fakeGame('guest', G2);
  G2.game = Gg2;
  G2.joinRoom('ZZZZZ');                    // nadie la registró
  chk(await espera(() => G2.status === 'error', 3000),
    `sala muerta → error (status=${G2.status} · msg=${G2.statusMsg.slice(0, 28)}…`);
  chk(G2.online === false && !G2.peer && !G2.conn,
    'r140 · el fallo de join hace TEARDOWN (peer y conn muertos)');
  chk(Hg.mstarts === 1 && Gg.mstarts === 1,
    'el join fallido NO toca la sesión viva (mstarts intactos)');
}

console.log('— S3 · F1: intruso conecta DIRECTO al id del INVITADO');
{
  const { H, G, Hg, Gg } = globalThis.__S1;
  const X = new NetLink(null); const Xg = fakeGame('guest', X);
  X.game = Xg;
  // el intruso abre un peer y OFRECE una conexión al ID ALEATORIO del invitado
  X.openPeer(null, () => { /* */ });
  await espera(() => X.peer, 2000);
  await dormir(150);
  const idInvitado = G.peer.id;
  const connMal = X.peer.connect(idInvitado);
  await dormir(400);
  if (process.env.DBG) {
    console.log('    [dbg S3] G.status=' + G.status + ' G.online=' + G.online +
      ' G.conn=' + (G.conn ? G.conn.peerId : 'null') + ' G.v2=' + G.v2 +
      ' mstarts=' + Gg.mstarts + ' X.status=' + X.status +
      ' connMal.open=' + connMal.open + ' Xg.sesiones=' + Xg.sesiones);
  }
  chk(G.online && G.conn && G.conn.peerId === NetLink.ROOM_PREFIX + globalThis.__S1.codigo,
    'el invitado CONSERVA su sesión (conn = la sala real, no el intruso)');
  chk(Gg.mstarts === 1 && Gg._netMatchLive && G.v2 === 'ok',
    'partida viva intacta frente al intruso (mstart, v2 ok)');
  chk(!connMal.open && !Xg.sesiones && !Xg.finRed,
    'la conexión del intruso MUERE rechazada (sin «Rival conectado» en nadie)');
}

console.log('— S4 · r122: segundo invitado a la sala ocupada');
{
  const { H, G, Hg, Gg } = globalThis.__S1;
  const X = new NetLink(null); const Xg = fakeGame('guest', X);
  X.game = Xg;
  X.joinRoom(globalThis.__S1.codigo);
  await dormir(400);
  chk(G.online && Hg.mstarts === 1,
    'r122 · el entrante NO reemplaza al invitado vivo (sesión intacta)');
  chk(!Xg.sesiones && !Xg.finRed && (X.status !== 'online'),
    'el intruso NO obtiene sesión (rechazado por el guard de sala)');
}

console.log('— S5 · colisión de código de sala: unavailable-id → regeneración');
{
  const H2 = new NetLink(null); const Hg2 = fakeGame('host', H2);
  H2.game = Hg2;
  // colisión FORZADA con S1: el PRIMER código choca; los reintentos usan
  // la generación real (así el unavailable-id regenera y espera)
  const genReal = NetLink.prototype.genCode;
  H2.genCode = () => (H2._retryIds ? genReal.call(H2) : globalThis.__S1.codigo);
  H2.hostRoom();
  await dormir(250);
  // el ID-TAKEN se DEMUESTRA por la regeneración: si el broker no hubiera
  // rechazado el código, H2 seguiría con el código colisionado de S1
  chk(await espera(() => H2.status === 'waiting' && H2.code !== globalThis.__S1.codigo, 3000),
    `el anfitrión regenera su código y espera (nuevo=${H2.code || '—'})`);
  const { H } = globalThis.__S1;
  chk(H.status === 'online',
    'el anfitrión original sigue EN SU SESIÓN (la colisión no le toca)');
  H2.cancel();
}

console.log('— S6 · fimre y bye REALES por el broker');
{
  const { H, G, Hg, Gg } = globalThis.__S1;
  H.hangup();                               // «bye» por la DataConnection real
  await dormir(300);
  chk(Gg.finRed && G.online === false && G.conn === null,
    `el invitado ve el cierre real (finRed=${Gg.finRed ? 'sí' : 'no'} · status=${G.status})`);
  chk(H.status === 'off' && !H.conn,
    'el anfitrión aterriza limpio tras el hangup');
}

console.log('— S7 · muerte del BROKER: error network, micro preservado');
{
  const H3 = new NetLink(null); const Hg3 = fakeGame('host', H3);
  H3.game = Hg3;
  H3.hostRoom();
  await espera(() => H3.status === 'waiting', 3000);
  await dormir(150);
  broker.kill('SIGKILL');                    // el broker muere de verdad (proceso)
  await dormir(800);
  if (process.env.DBG) {
    console.log('    [dbg S7] H3.status=' + H3.status + ' voiceState=' + H3.voiceState +
      ' online=' + H3.online + ' peer=' + (H3.peer ? 'vivo·ws=' + (H3.peer.ws ? H3.peer.ws.readyState : 'n/a') : 'null'));
  }
  chk(H3.status === 'error', `broker muerto → error honesto (${H3.status})`);
  chk(H3.voiceState === 'off' || H3.voiceState === 'denied' || H3.voiceState === 'error',
    `estado de voz coherente sin sesión (${H3.voiceState})`);
  chk(H3.online === false && !H3.conn, 'sin restos de sesión tras la muerte del broker');
}

console.log(fail === 0
  ? `✓ PEERJS VIVO: ${ok} OK · broker real, sala, join, intruso F1, colisión, bye y muerte del servidor`
  : `✗ PEERJS VIVO: ${ok} OK · ${fail} FALLO(S)`);
try { broker.kill('SIGKILL'); } catch { /* */ }   // sin huérfanos para el siguiente run
process.exit(fail === 0 ? 0 : 1);

#!/usr/bin/env node
/* =====================================================================
 * r152 · REVISIÓN INTEGRAL · ARNÉS r153 · SEÑALIZACIÓN CON EL SERVICIO REAL
 * =====================================================================
 * r146 levantaba un PeerServer INLINE (código -e) con path '/'. Este arnés
 * cierra el hueco que quedó: levanta EL SERVICIO DEL REPO
 * (mini-services/peer-server/server.js, path '/peerjs', el que va detrás
 * del Caddy del dueño) y conduce UN CICLO COMPLETO de partida real sobre
 * él con dos NetLink REALES (c09):
 *
 *   S0  servicio vivo en :3005 (sondeo WS del protocolo real)
 *   S1  sala → join por el broker (señalización de verdad)
 *   S2  handshake v2 + mstart AUTO del anfitrión (sync inicial: sa/bo/md)
 *   S3  RESET/REVANCHA: 2º mstart tras la ventana del guard (8 s) —
 *       mstarts 2/2 y countdown NUEVO (sa2 > sa1)
 *   S4  guard mstartReciente: el 3º arranque inmediato se traga
 *   S5  ciclo de vida: close del invitado → onPeerGone → fuera de online
 *   S6  reconexión a NIVEL SERVICIO: muerto el server.js → error
 *       'network' del micro (recuperable) → REARRANCADO → sala nueva con
 *       ciclo completo otra vez
 *
 * El shim de cliente (protocolo sondado en probe_peer.mjs) es el MISMO de
 * r146 — la inyección es globalThis.Peer. El canal reliable/fast interno
 * sigue siendo el par local (territorio r130); la SEÑALIZACIÓN y el ciclo
 * de vida cruzan el servicio real de punta a punta.
 * Salida: veredicto ÚNICO por writeSync (r140b/r152).
 * Ejecución: node --no-warnings scripts/test_r153_senal_ciclo_real.mjs (≈30 s)
 * ===================================================================== */
import { createRequire } from 'node:module';
import { WebSocket as WS } from 'ws';
import { EventEmitter } from 'node:events';
import { spawn } from 'node:child_process';

const ROOT = '/home/z/my-project';
const SERV = ROOT + '/mini-services/peer-server/server.js';
const EP = 'http://127.0.0.1:3005/peerjs';   // path del server.js real
const PROBE_URL = 'ws://127.0.0.1:3005/peerjs/peerjs';

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
try { globalThis.navigator = globalThis.navigator || { userAgent: 'node-r153' }; } catch { /* */ }

const { NetLink } = await import(ROOT + '/src/game/core/c09_red_netlink.js');
const { Rules } = await import(ROOT + '/src/game/core/c06_logros_stats_ia_rival.js');
const { T } = await import(ROOT + '/src/game/core/c00_pre_three.js');
globalThis.T = T;
const PPNET = (await import(ROOT + '/src/game/core/c09b_red_nucleo.js')).PPNET;

/* ---------- mock RTC: la subida v2 necesita piezas para no degradar */
globalThis.RTCPeerConnection = class {
  constructor() { this.signalingState = 'stable'; }
  async createOffer() { return { type: 'offer', sdp: 'x' }; }
  async createAnswer() { return { type: 'answer', sdp: 'x' }; }
  async setLocalDescription(d) { this.localDescription = d; }
  async setRemoteDescription(d) { this.remoteDescription = d; }
  async addIceCandidate() { /* */ }
  createDataChannel() { return { close() { /* */ } }; }
  close() { /* */ }
};

/* ---------- shim de CLIENTE peerjs (protocolo sondado — r146) ------ */
const VIVOS = new Map();
const PARES = new Map();
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
    if (this._cerrada) return;
    this._cerrada = true;
    this.open = false;
    const par = PARES.get(this.id);
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
      this.emit('error', { type: 'network' });
      this.emit('disconnected');
    });
    ws.on('error', () => { /* el 'close' decide */ });
  }
  connect(dst, _opts) {
    const conn = new ConnShim(this, dst, 'c' + (++SHIM_TOKEN), false);
    PARES.set(conn.id, { a: conn });
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
    if (!this._dead) this._conectar();
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

/* par de canales reliable/fast locales (handlers EXACTOS de _wireDC) */
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
      catch { /* json inválido: ignorar */ }
    };
    n._rel.onopen = null; n._rel.onclose = null;
  }
}

/* ---------- S0 · EL SERVICIO REAL DEL REPO en :3005 ---------------- */
function arrancaServicio() {
  const hijo = spawn(process.execPath, [SERV], {
    cwd: ROOT,
    env: { ...process.env, PORT: '3005' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  hijo.stderr.on('data', (d) => { hijo._errTxt = String(hijo._errTxt || '') + d; });
  return hijo;
}

async function sondeaServicio(intentos = 40) {
  for (let i = 0; i < intentos; i++) {
    const r = await new Promise((res) => {
      const id = 'pp-probe-' + Date.now() + '-' + i;
      const t = setTimeout(() => { try { ws.close(); } catch { /* */ } res(false); }, 900);
      const ws = new WS(`${PROBE_URL}?id=${id}&token=p&key=peerjs`);
      ws.on('message', (d) => {
        try {
          const m = JSON.parse(d.toString());
          if (m && m.type === 'OPEN') { clearTimeout(t); try { ws.close(); } catch { /* */ } res(true); }
        } catch { /* */ }
      });
      ws.on('error', () => { clearTimeout(t); res(false); });
      ws.on('open', () => { try { ws.send(JSON.stringify({ type: 'OPEN', payload: { token: 'p' } })); } catch { /* */ } });
    });
    if (r) return true;
    await dormir(250);
  }
  return false;
}

// limpiar huérfanos de corridas previas (lección r146)
import { spawnSync } from 'node:child_process';
spawnSync('pkill', ['-f', 'PeerServer'], { stdio: 'ignore' });
spawnSync('pkill', ['-f', 'peer-server/server.js'], { stdio: 'ignore' });
await dormir(300);

let broker = arrancaServicio();
console.log('— S0 · EL SERVICIO REAL DEL REPO (mini-services/peer-server/server.js)');
const vivo0 = await sondeaServicio();
chk(vivo0, 'server.js del repo VIVO en :3005 con path /peerjs (sondeo WS real)');
if (!vivo0) {
  console.error('  stderr del hijo:', (broker._errTxt || '').slice(0, 400));
  try { broker.kill('SIGKILL'); } catch { /* */ }
  process.exit(1);
}
await dormir(200);

console.log('— S1 · SALA → JOIN por señalización real (path /peerjs)');
globalThis.PP_SIGNAL_ENDPOINT = EP;
const H = new NetLink(null); const G = new NetLink(null);
const Hg = fakeGame('host', H); const Gg = fakeGame('guest', G);
H.game = Hg; G.game = Gg;
H.hostRoom();
chk(await espera(() => H.status === 'waiting'), `sala creada en el servicio real (status=${H.status})`);
const codigo = H.code;
chk(/^[A-Z0-9]{5}$/.test(codigo || ''), `código de sala con formato honesto (${codigo})`);
G.joinRoom(codigo);
chk(await espera(() => H.online && G.online, 6000),
  `join vivo por el server.js del repo: AMBOS online (H=${H.status} · G=${G.status})`);
chk(!!G.conn && G.conn.peerId === NetLink.ROOM_PREFIX + codigo,
  'el conn del invitado nace de la SEÑALIZACIÓN real (dst = ' + NetLink.ROOM_PREFIX + '…)');

console.log('— S2 · SYNC INICIAL: handshake v2 + mstart AUTO del anfitrión');
await dormir(250);
parCanales(H, G);
H._v2ChannelsUp(); G._v2ChannelsUp();
chk(await espera(() => H.v2 === 'ok' && G.v2 === 'ok', 6000),
  `handshake v2 real sobre la sala (H=${H.v2} · G=${G.v2})`);
chk(await espera(() => Hg.mstarts === 1 && Gg.mstarts === 1, 5000),
  `mstart AUTO del anfitrión cruzó el servicio (mstarts H/G=${Hg.mstarts}/${Gg.mstarts})`);
chk(!!Gg._netMatchLive, 'partida viva en el invitado (_netMatchLive)');
const sa1 = Hg._netStart && Hg._netStart.startAt;
chk(Number.isFinite(sa1) && sa1 > H.hostNowMs(),
  `sync honesto: el saque llega en el FUTURO de ambos (startAt−ahora=${Math.round(sa1 - H.hostNowMs())} ms · bo=${Hg.rules.bestOf} · md=match)`);

console.log('— S3 · RESET/REVANCHA: 2º mstart tras la ventana del guard (8 s)');
await dormir(8300);                       // ventana mstartReciente = 8000 ms
const sa1Prev = sa1;
Hg.startOnlineMatch();
chk(await espera(() => Hg.mstarts === 2 && Gg.mstarts === 2, 5000),
  `RESET: 2º mstart cruzó tras la ventana (mstarts H/G=${Hg.mstarts}/${Gg.mstarts})`);
const sa2 = Hg._netStart && Hg._netStart.startAt;
chk(Number.isFinite(sa2) && sa2 > sa1Prev + 5000,
  `countdown NUEVO en el reset (sa2−sa1=${Math.round((sa2 || 0) - sa1Prev)} ms)`);
chk(Hg._netMatchLive && Gg._netMatchLive, 'la partida sigue viva en AMBOS tras el reset');

console.log('— S4 · GUARD mstartReciente: el 3º arranque inmediato se traga');
Hg.startOnlineMatch();
await dormir(400);
chk(Hg.mstarts === 2 && Gg.mstarts === 2,
  `guard activo en el servicio real (mstarts intactos: ${Hg.mstarts}/${Gg.mstarts})`);

console.log('— S5 · CICLO DE VIDA: close del invitado → onPeerGone');
G.conn.close();
chk(await espera(() => H.status === 'off' || !!Hg.finRed, 5000),
  `el anfitrión detecta la marcha (H.status=${H.status} · finRed=${JSON.stringify(Hg.finRed)})`);
chk(await espera(() => G.status === 'off' || !!Gg.finRed, 5000),
  `el invitado también sale limpio (G.status=${G.status} · finRed=${JSON.stringify(Gg.finRed)})`);

console.log('— S6 · RECONEXIÓN A NIVEL SERVICIO: muerte + REARRANQUE de server.js');
// r152 · lección de la 1ª corrida: el par de S5 fue DESMONTADO por
// teardown() (peer.destroy → _dead) y un peer destruido NO emite 'network'
// — comportamiento correcto del cliente peerjs real. La supervivencia se
// prueba con una sala VIVA al morir el servicio (r146: recoverable).
const H3 = new NetLink(null); const G3 = new NetLink(null);
const H3g = fakeGame('host', H3); const G3g = fakeGame('guest', G3);
H3.game = H3g; G3.game = G3g;
H3.hostRoom();
const sala3Lista = await espera(() => H3.status === 'waiting', 5000);
G3.joinRoom(H3.code);
const par3Vivo = await espera(() => H3.online && G3.online, 6000);
const netErr = { n: 0 }; const disconn = { n: 0 };
for (const nl of [H3, G3]) {
  if (nl.peer && nl.peer.on) {
    nl.peer.on('error', (e) => { if (e && e.type === 'network') netErr.n++; });
    nl.peer.on('disconnected', () => disconn.n++);
  }
}
chk(sala3Lista && par3Vivo, `3ª sala VIVA al matar el servicio (H3=${H3.status} · G3=${G3.status})`);
broker.kill('SIGKILL');
chk(await espera(() => netErr.n >= 1 && disconn.n >= 1, 5000),
  `el micro SOBREVIVE a la muerte del servicio: error 'network' + 'disconnected' (sin crash)`);
await dormir(500);
broker = arrancaServicio();
const vivo2 = await sondeaServicio();
chk(vivo2, 'servicio REARRANCADO en :3005 (reconexión al servicio)');
const H2 = new NetLink(null); const G2 = new NetLink(null);
const H2g = fakeGame('host', H2); const G2g = fakeGame('guest', G2);
H2.game = H2g; G2.game = G2g;
H2.hostRoom();
chk(await espera(() => H2.status === 'waiting' && /^[A-Z0-9]{5}$/.test(H2.code || ''), 5000),
  `sala NUEVA tras el reinicio (status=${H2.status} · code=${H2.code})`);
G2.joinRoom(H2.code);
chk(await espera(() => H2.online && G2.online, 6000),
  `join vivo tras el reinicio (H2=${H2.status} · G2=${G2.status})`);
parCanales(H2, G2);
H2._v2ChannelsUp(); G2._v2ChannelsUp();
chk(await espera(() => H2.v2 === 'ok' && G2.v2 === 'ok', 6000) &&
    await espera(() => H2g.mstarts === 1 && G2g.mstarts === 1, 5000),
  `ciclo completo OTRA VEZ tras la reconexión (v2 ok · mstarts ${H2g.mstarts}/${G2g.mstarts})`);

/* ---------- salida limpia ------------------------------------------ */
try { broker.kill('SIGKILL'); } catch { /* */ }
spawnSync('pkill', ['-f', 'peer-server/server.js'], { stdio: 'ignore' });
console.log();
if (fail) {
  console.log(`✗ r153 SEÑALIZACIÓN REAL: ${ok} OK · ${fail} FALLO(S)`);
  process.exit(1);
}
const { writeSync } = await import('node:fs');
writeSync(1, `✓ SEÑALIZACIÓN REAL r153: ${ok} OK · ciclo completo sala→sync→reset→reconexión sobre el server.js DEL REPO en :3005\n`);
process.exit(0);

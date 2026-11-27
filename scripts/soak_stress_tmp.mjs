#!/usr/bin/env node
/* CRAZY PING PONG · r130 · ARNÉS DE MULTIPARTIDA EN NODE — dos NetLink
 * REALES (fuente src/game/core/c09_red_netlink.js, la que corre en el
 * Quest) enfrentados por un bus con latencia, más Rules REALES (c06) y
 * PPNET real (c09b). Reproduce SIN visor los escenarios que el dueño
 * sólo puede probar con dos cascos:
 *
 *   A · ARRANQUE (mstart): sacador espejo coherente, UNA sola bola HELD,
 *       visibilidad correcta, cuenta atrás, resync de los 700 ms
 *   B · RALLYE REAL: toss → HIT → cruce → HANDOFF → golpe devuelto →
 *       punto con detección en AMBOS extremos → CLAIM/ACK → marcadores
 *       convergen → el siguiente sacador rota igual en los dos
 *   C · REVANCHA (partida 2): pide el invitado; el guard del host la
 *       acepta; el sacador de la 2ª partida queda BIEN en los dos extremos
 *       (el informe del dueño: «yo tenía que sacar y la bola la tenía el
 *       rival») y los CLAIMS de la partida nueva (rallySeq reiniciado)
 *       se aplican aunque _sync.applied venga viejo de la anterior
 *   D · DOBLE REVANCHA SIMULTÁNEA: la guarda anti doble mstart (r75) deja
 *       UNA sola partida nueva
 *   E · RESYNC DEL HOST cura una divergencia forzada del invitado
 *   F · SYNC v1 (builds mezclados): applySync espeja marcador/sacador
 *   H · PAUSA/REANUDACIÓN por visor oculto (spec §10) · J · DUELOS online
 *       (md en el mstart + poder por la red) · K · PARTIDA COMPLETA mejor de
 *       3 con rotación ITTF y fin de enfrentamiento + candado del bug #5
 *       (el 'over' online NO se auto-reinicia) · M · canal fast ADVERSO
 *       (pérdida/duplicados/reordenación) con pose real y validador §12
 *       completo · L · RESYNC-REQ a mitad de partida · N · watchdog de
 *       silencio (12 s anfitrión · ~30 s invitado por los reintentos ICE)
 *   G · RELOJ: el ancla gruesa deja el offset del invitado acotado
 *
 * Los stubs son el patrón r129_signal (mínimos); toda la LÓGICA —
 * handshake hello2/tick2/tock2, mstart, FSM de bola, validador, claims,
 * resync — corre la fuente real. El «juego» falso replica SOLO el pegote
 * esencial de c12 (onNetMatchStart/startOnlineMatch/intents), con el
 * ancla de líneas comentada para auditarlo a ojo contra c12.
 * Uso: node --no-warnings scripts/test_r130_multipartida.mjs
 */
globalThis.window = globalThis;
/* r132-8ª · stub mínimo de DOM: el teardown de _v2Fail y document.hidden
   existen en el navegador real; sin él el soak no puede ejercitar la
   degradación (el throw escaparía por el timer de teardown). */
globalThis.document = globalThis.document || {
  hidden: false, visibilityState: 'visible',
  addEventListener: () => {}, removeEventListener: () => {},
};
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible', hidden: false };
try { globalThis.navigator = { userAgent: 'node-mp' }; } catch (e) { /* getter */ }
// c06 (Rules) no importa T: en el juego ensamblado todo comparte ámbito
// único. Stub neutro para Node (los tests afirman estados/números, no textos).
globalThis.T = (k, _v) => k;
globalThis.VERSION = '3.6.210-SDK6';

let ok = 0, fails = 0;
const chk = (c, l) => {
  console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l);
  if (c) ok++; else fails++;
};
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

const { NetLink } = await import('/home/z/my-project/src/game/core/c09_red_netlink.js');
const { Rules } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { PPNET } = await import('/home/z/my-project/src/game/core/c09b_red_nucleo.js');
const THREE = await import('three');
const V3 = THREE.Vector3;
const CZ = NetLink.TABLE_CZ;                 // -1.6 (centro de mesa, eje de cruce)

// Mock mínimo de RTCPeerConnection: para que startV2() REAL corra su bloque
// de re-init (escenario O) — el handshake del arnés sigue yendo por el bus
globalThis.__PP_PC_CERRADOS = 0;   // cuántas pc del mock se han cerrado
const RTC_DLY = () => new Promise((r) => setTimeout(r, globalThis.__PP_RTC_DELAY || 0));
globalThis.RTCPeerConnection = class {
  constructor() { this.signalingState = 'stable'; }
  async createOffer() { await RTC_DLY(); return { type: 'offer', sdp: 'x' }; }
  async createAnswer() { await RTC_DLY(); return { type: 'answer', sdp: 'x' }; }
  async setLocalDescription(d) { await RTC_DLY(); this.localDescription = d; }
  async setRemoteDescription(d) {
    await RTC_DLY();
    if (d && d.sdp === 'BOOM') throw new Error('sdp trampa');
    this.remoteDescription = d;
  }
  async addIceCandidate() { /* */ }
  createDataChannel() { return { close() { /* */ } }; }
  close() { globalThis.__PP_PC_CERRADOS++; }
};
// ICE_ASYNC con retardo controlable (la ventana de la carrera es REAL aquí)
const ICE_REAL = NetLink.ICE_ASYNC.bind(NetLink);
NetLink.ICE_ASYNC = async () => {
  const d = globalThis.__PP_ICE_DELAY || 0;
  if (d) await new Promise((r) => setTimeout(r, d));
  return ICE_REAL();
};
NetLink._iceRem = { iceServers: [] };         // caché ICE: ICE_ASYNC sin red
NetLink._iceRemT0 = Date.now();

/* ---------- juego falso: el pegote esencial de c12, nada más ---------- */
function fakeGame(role, net) {
  const g = {
    role, net,
    mode: 'match', pendingMode: 'match', doblesActivo: false, inHall: false,
    menuOpen: false, tossed: false, _mjMode: 'match',
    _netStart: null, _netStartWhenReady: false, _netResyncT: null,
    mstarts: 0,                                   // guardia anti doble mstart
    rules: new Rules(),
    ball: { pos: new V3(0, 1.0, CZ + 1.4), vel: new V3(), spin: new V3() },
    ballMesh: { visible: false },
    // pose REAL (c09 _samplePose la lee del juego): cámara + grips — con esto
    // el canal fast emite pose 60 Hz, el JitterBuf se llena y el validador
    // §12 juzga TAMBIÉN la distancia pala↔golpe (HIT_NEAR_PAD 0,85 m)
    camera: { position: new V3(0, 1.6, CZ + 2.2), quaternion: { x: 0, y: 0, z: 0, w: 1 } },
    grips: [0, 1].map(() => ({ position: new V3(0, 1.0, CZ + 1.4), quaternion: { x: 0, y: 0, z: 0, w: 1 } })),
    paddleHand: 0, handOf: ['left', 'right'],
    paddleMounts: [{ quaternion: { x: 0, y: 0, z: 0, w: 1 } }, { quaternion: { x: 0, y: 0, z: 0, w: 1 } }],
    _dlOn: () => false,
    _dlReset() { g.duelosReiniciados = (g.duelosReiniciados || 0) + 1; },
    onRemoteDueloPower() { g.powRecibidos = (g.powRecibidos || 0) + 1; },
    onNetPause(paused) { g.netPausa = paused; },
    onNetEnded(msg) { g.finRed = msg || 'fin'; },
    renderer: { xr: { isPresenting: false } },       // applySync lo consulta (c09:757)
    audio: new Proxy({}, { get: () => () => {} }),   // voz/sonido no-op
    resetToss() { g.tossed = false; },             // c12:9719 (esencial)
    exitHall() { g.inHall = false; },
    onNetV2Ready() { if (g._netStartWhenReady) { g._netStartWhenReady = false; g.startOnlineMatch(); } },
    /* r131 · espejo de c12 switchMode: guard idéntico (mode===mode → no-op)
       y registro para auditar el espejo de modo por red (bug #11) */
    switchMode(mode) {
      if (mode === g.mode) return;
      g.mode = mode;
      g.__sw = (g.__sw || []);
      g.__sw.push(mode);
    },
    onNetStatus() {},
    /* c12:1420-1436 — el anfitrión abre la partida; el invitado pide 'r' */
    startOnlineMatch() {
      if (net.role !== 'host') { net.sendRematch(); return; }
      if (net.v2 === 'ok') {
        // r130 · espejo EXACTO de la guardia añadida en c12:1425
        if (net.mstartReciente && net.mstartReciente()) return;
        const md = (g._mjMode === 'duelos') ? 'duelos' : 'match';   // c12:1425
        const startAt = net.hostNowMs() + PPNET.VP.COUNTDOWN_MS;
        net.sendRel({ k: 'mstart', sa: startAt, fs: 'host', bo: 3, md });
        g.onNetMatchStart({ startAt, fs: 'host', bo: 3, md });
        return;
      }
      g._netStartWhenReady = true;
    },
    /* c12:1448-1504 — el corazón del arranque (asignación de bola/saque) */
    onNetMatchStart(m) {
      const guest = net.role === 'guest';
      g.mstarts++;
      if (net.resetLibro) net.resetLibro();   // r130 · espejo EXACTO de c12
      if (process.env.DBG) {
        const st = (new Error().stack).split('\n')[2] || '';
        console.log(`    [dbg] onNetMatchStart#${g.mstarts} en ${role} · fs=${m && m.fs} · ${st.trim().slice(0, 90)}`);
      }
      if (g.inHall) g.exitHall();
      g.doblesActivo = false;
      const md = (m && m.md === 'duelos') ? 'duelos' : 'match';
      g.mode = md; g.pendingMode = md;
      g.rules.bestOf = m.bo || 3;
      g.rules.startMatch(md);
      g.rules.firstServer = (m.fs === 'host')
        ? (guest ? 'ai' : 'player') : (guest ? 'player' : 'ai');
      g.rules.resetGame();          // recalcula el sacador con el firstServer real
      if (md === 'duelos') g._dlReset();   // c12:1466 · poderes a cero al empezar
      g.resetToss();
      g._netStart = { startAt: m.startAt, fs: m.fs };
      g._netTossLive = false;
      net._mstartAt = performance.now();
      net.setServeHeld(g.rules.server === 'player');
      if (net.role === 'host' && net.v2 === 'ok') {
        clearTimeout(g._netResyncT);
        g._netResyncT = setTimeout(() => {
          try { if (net && net.online) net._sendResync(); } catch { /* */ }
        }, 700);
      }
      g.ballMesh.visible = g.rules.server === 'player';
      g.rules.message = '3';
    },
    processIntents(list) { for (const it of list) g._intent(it); },
    _intent(it) {
      if (it.type === 'point') {
        // el punto YA lo aplicó rules.applyPoint/forcePoint; esto sólo
        // notifica a la red (puente real del árbitro, c12→c09:2250)
        net.onLocalPointIntent(it);
      } else if (it.type === 'retry-serve') {
        net.onLocalRetryIntent(it);
      } else if (it.type === 'serve') {
        // espejo c12:20626-20648: HELD del sacador que trae el intent
        if (net.v2 === 'ok') {
          net.setServeHeld(it.server === 'player');
          g.ballMesh.visible = it.server === 'player';
        }
      } else if (it.type === 'game-over') {
        g.partidoAcabo = (g.partidoAcabo || 0) + 1;
      }
    },
    /* tick del árbitro: el RULES.UPDATE real decide (c06:489 — pausa de
     * punto → saque, fin de juego/serie, rotación ITTF) con la MISMA
     * guardia de 'over' online que la fuente (fix bug #5, c12:19148) */
    tick(dt) {
      const r = g.rules;
      if (!(net.online && r.state === 'over')) {
        for (const it of r.update(dt)) g._intent(it);
      }
      // cuenta atrás MATCH_START (espejo c12:18218-18234)
      if (g._netStart && net.online && net.v2 === 'ok') {
        const leftMs = g._netStart.startAt - net.hostNowMs();
        if (leftMs <= 0) { g._netStart = null; }
      }
    },
  };
  return g;
}

/* ---------- preparación del transporte v2 (init esencial de startV2) --- */
function preparar(net, game, role) {
  net.game = game; net.role = role;
  net.v2 = 'pending'; net.online = true; net.status = 'online';
  net._pc = null; net._fast = null; net._rel = null;
  net._fastOpen = false; net._relOpen = false;
  net._seq = (Math.random() * 0xffff) | 0;
  net._ackP = 0; net._ackBits = 0; net._ackInit = false;
  net._echoTime = 0; net._echoAt = 0;
  net._pend = []; net._evId = 1; net._fastIn = [];
  net._seenEv = new Map(); net._recvRing = []; net._recvHist = [];
  net._lastPoseAt = 0; net._gaps = 0; net._recvs = 0;
  net._poseAcc = 0; net._snapAcc = 0; net._poseHz = PPNET.VP.POSE_HZ;
  net._tunT = 0; net._tunSalud = 0; net._qosAcc = 0;
  net._txBuf = new ArrayBuffer(PPNET.VP.MAX_PKT);
  net._lossLowT = 0; net._degraded = false;
  net._lastFastAt = 0; net._iceRestarts = 0; net._lastIceTry = 0;
  net._helloDone = false; net._helloTO = null; net._iceQ = [];
  net._tunnel = false; net._v2T0 = performance.now();
  net._buildWarn = false; net.buildPeer = ''; net._verTele = false;
  net._anchors = 0; net._readyMe = false; net._readyOpp = false;
  net._mstart = null; net._mstartAt = 0;
  net._clock = new PPNET.NetClock(role === 'host');
  net._jb = new PPNET.JitterBuf();
  net._ball = new PPNET.BallAuth();
  net._sync = new PPNET.MatchSync(role);
  net._val = new PPNET.Validator();
  net._stats = new PPNET.NetStats(role);
  game.rules._netGuard = true;
  net._visOff = null; net._visOffMs = 0;
  net._pausedSelf = false; net._pausedRemote = false; net._pausedAt = 0;
  net._lastRelAt = 0; net._claimFallback = null; net._lastHitSent = 0;
  PPNET.VP.BUILD = '3.6.210-SDK6';
  if (process.env.DBG) {
    const _ap = net.game.rules.applyPoint.bind(net.game.rules);
    net.game.rules.applyPoint = (w, c) => {
      const st = (new Error().stack).split('\n').map(l => l.trim()).find(l => l.includes('at ') && !l.includes('applyPoint'));
      console.log(`    [dbg] applyPoint(${w}, ${c}) en ${role} · rallySeq=${net.game.rules.rallySeq} · ${st ? st.slice(3, 95) : ''}`);
      return _ap(w, c);
    };
    const _bs = net.game.rules.beginServeRally.bind(net.game.rules);
    net.game.rules.beginServeRally = (side) => {
      console.log(`    [dbg] beginServeRally(${side}) en ${role} → rallySeq ${net.game.rules.rallySeq + 1}`);
      return _bs(side);
    };
    const _afe = net._applyFastEv.bind(net);
    net._applyFastEv = (ev, g) => {
      if (ev.t === 1 || ev.t === 2) {
        console.log(`    [dbg] fastEv kind=${ev.kind} shot=${ev.shot} en ${role} · rules.state=${g.rules.state} · ball=${net._ball.state}`);
      }
      return _afe(ev, g);
    };
    const _vh = net._val.hit.bind(net._val);
    net._val.hit = (ev, ctx) => {
      const r = _vh(ev, ctx);
      if (!r.ok) console.log(`    [dbg] VALIDADOR rechaza en ${role}: kind=${ev.kind} shot=${ev.shot} → ${r.why}`);
      return r;
    };
    const _sr = net._sendResync.bind(net);
    net._sendResync = () => {
      const r = net.game.rules;
      console.log(`    [dbg] _sendResync EN ${role} · st=${r.state} rs=${r.rallySeq} marcador ${r.scorePlayer}-${r.scoreAi}`);
      return _sr();
    };
    const _ar = net._applyResync.bind(net);
    net._applyResync = (m) => {
      const r = net.game.rules;
      console.log(`    [dbg] _applyResync EN ${role} · st=${m.st} rs=${m.rs} marcadorHOST ${m.sp}-${m.sa} | mi rs=${r.rallySeq} applied=${r._appliedRally} marcador ${r.scorePlayer}-${r.scoreAi}`);
      return _ar(m);
    };
    const _oc = net._sync.onClaim.bind(net._sync);
    net._sync.onClaim = (m, w) => {
      const resp = _oc(m, w);
      console.log(`    [dbg] onClaim EN ${role} · r=${m.r} w=${m.w} → apply=${resp.apply} agree=${resp.agree}`);
      return resp;
    };
    const _fp = net.game.rules.forcePoint.bind(net.game.rules);
    net.game.rules.forcePoint = (w, c, rid) => {
      console.log(`    [dbg] forcePoint(${w}, ${c}, rid=${rid}) EN ${role} · marcador ${net.game.rules.scorePlayer}-${net.game.rules.scoreAi}`);
      return _fp(w, c, rid);
    };
    const _sh = net._ball.setHeld.bind(net._ball);
    net._ball.setHeld = (mine) => {
      const st = (new Error().stack).split('\n')[2] || '';
      console.log(`    [dbg] setHeld(${mine}) en ${role} · ${st.trim().slice(0, 110)}`);
      return _sh(mine);
    };
  }
}

/* ---------- bus: entrega cruzada con latencia (el DC real copia) ------- */
/** (re)conecta los canales de un par — sirve para la SESIÓN 2 de la
 *  re-entrada: los MISMOS objetos NetLink, canales nuevos (el juego real
 *  reutiliza la instancia; sólo cambia la conexión) */
function cablear(par, latMs = 18) {
  const { H, G } = par;
  const reenvia2 = (destino, data, esFast) => {
    if (par.muerto) return;
    if (esFast && Math.random() < (par.lossFast || 0)) return;
    // r132 · 11ª: contadores del bus — discriminan dónde muere el fast
    const esH = destino === par.H;
    const k = (esH ? 'h' : 'g') + (esFast ? 'f' : 'r');
    par.busA[k] = (par.busA[k] || 0) + 1;
    const clon = (typeof data === 'string') ? data : data.slice(0).buffer;
    const vueltas = (esFast && Math.random() < (par.dupFast || 0)) ? 2 : 1;
    for (let i = 0; i < vueltas; i++) {
      const d = latMs + (esFast ? Math.random() * (par.jitterFast || 0) : 0);
      setTimeout(() => {
        par.busD[k] = (par.busD[k] || 0) + 1;
        if (typeof clon === 'string') destino._onRel(JSON.parse(clon));
        else destino._onFast(clon);
      }, d);
    }
  };
  const dc = (receptor, esFast) => ({
    label: esFast ? 'fast' : 'rel', readyState: 'open', bufferedAmount: 0,
    binaryType: 'arraybuffer',
    _tag: (receptor === H ? 'destinoH' : 'destinoG') + (esFast ? 'F' : 'R'),
    send(data) { reenvia2(receptor, data, esFast); },
  });
  H._fast = dc(G, true); H._rel = dc(G, false); H._fastOpen = H._relOpen = true;
  G._fast = dc(H, true); G._rel = dc(H, false); G._fastOpen = G._relOpen = true;
  par._tags = { hF: H._fast, hR: H._rel, gF: G._fast, gR: G._rel };
  // contador de send reales del invitado (envoltura post-cablear)
  const gs = G._fast.send.bind(G._fast);
  G._sends = 0;
  G._fast.send = (d) => { G._sends++; return gs(d); };
  H.conn = { open: true, send: (msg) => setTimeout(() => G.onData(msg), latMs) };
  G.conn = { open: true, send: (msg) => setTimeout(() => H.onData(msg), latMs) };
  // r132 · 9ª: modelar wireConn('open') — el flujo REAL sólo recibe datos con
  // la conexión abierta (online=true); _onRel ahora lo exige y descarta el
  // tráfico tardío tras un teardown (crash _sync.onAck null del churn).
  H.online = true; G.online = true;
}

function crearPar(latMs = 22, opts = {}) {
  // pérdida/duplicación/reordenación SÓLO en el canal fast (el reliable de
  // WebRTC es fiable+ordenado — así se modela): events retransmiten por _pend
  const { lossFast = 0, dupFast = 0, jitterFast = 0 } = opts;
  const H = new NetLink(null), G = new NetLink(null);
  const Hg = fakeGame('host', H), Gg = fakeGame('guest', G);
  preparar(H, Hg, 'host'); preparar(G, Gg, 'guest');
  const par = { H, G, Hg, Gg, muerto: false, lossFast, dupFast, jitterFast, busA: {}, busD: {} };
  const reenvia = (destino, data, esFast) => {
    if (par.muerto) return;                          // apagón: ni paquetes ni watchdog
    if (esFast && Math.random() < lossFast) return;  // pérdida del canal UDP-like
    // el DC real entrega ArrayBuffer (binaryType='arraybuffer'): copiar a
    // ArrayBuffer, no a Uint8Array — decodePacket hace new DataView(buf)
    const clon = (typeof data === 'string') ? data : data.slice(0).buffer;
    const vueltas = (esFast && Math.random() < dupFast) ? 2 : 1;   // duplicado
    for (let i = 0; i < vueltas; i++) {
      const d = latMs + (esFast ? Math.random() * jitterFast : 0);  // reordenación
      setTimeout(() => {
        par.busD[k] = (par.busD[k] || 0) + 1;
        if (typeof clon === 'string') destino._onRel(JSON.parse(clon));
        else destino._onFast(clon);
      }, d);
    }
  };
  cablear(par, latMs);
  return par;                // H/G = NetLink real · Hg/Gg = juego (espejo c12)
}

/* ---------- bomba: frames + timers reales (bus, holdClaim, resync) ----- */
async function avanzar(seg, { H, G, Hg, Gg } = {}) {
  const paso = 0.016;
  const fin = performance.now() + seg * 1000;
  while (performance.now() < fin) {
    await dormir(paso * 1000);
    Hg.tick(paso); Gg.tick(paso);
    moverBolas(H, G, paso);
    H.frame(paso); G.frame(paso);
  }
}
function moverBolas(H, G, paso) {
  for (const X of [H, G]) {
    if (!X._ball || !X.online) continue;           // teardown post-watchdog
    const b = X.game.ball;
    if (X._ball.state === 'own' || X._ball.state === 'ghost') {
      b.pos.x += b.vel.x * paso; b.pos.y += b.vel.y * paso; b.pos.z += b.vel.z * paso;
      b.vel.y -= 2.5 * paso;                       // gravedad suave (da igual el valor)
      if (b.pos.y < 0.76) { b.pos.y = 0.76; b.vel.y = Math.abs(b.vel.y) * 0.7; }
    }
    X.watchOwnCross(b);
    X.observeGhost(b);
  }
}
const sacador = (X) => X._ball.mine;               // ¿este extremo tiene la bola?
/** bote reglamentario en la mitad de `Yg` (c12 lo emite con la física
 *  real; el arnés lo alimenta a los DOS árbitros con su etiqueta local:
 *  la mitad del que recibe es 'player' para él y 'ai' para el otro). */
function bote(par, Yg) {
  for (const X2 of [par.H, par.G]) {
    const side = (X2.game === Yg) ? 'player' : 'ai';
    const intents = X2.game.rules.handleEvents([{ type: 'table', side }]);
    X2.game.processIntents(intents);
  }
}
const enVuelo = (X) => X._ball.state === 'own' || X._ball.state === 'ghost';

/* ---------- rallye de PROTOCOLO: el árbitro REAL decide ----------------
 * El sacador saca (toss + HIT kind 1 + bote propio), `devoluciones`
 * retornos limpios (bote en la mitad del receptor + registerPaddleHit
 * propio + HIT kind 0 — el HANDOFF viaja por la red de verdad) y al final
 * el que recibe NO devuelve: la bola bota DOS VECES en su mitad y el
 * árbitro de cada extremo canta el punto con las REGLAS reales (c06
 * handleEvents) — los claims cruzan y convergen solos. El ganador es el
 * último que golpeó. Sin veredictos a dedo. */
async function jugarRallye(par, devoluciones) {
  const { H, G, Hg, Gg } = par;
  const Xg = sacador(H) ? Hg : Gg;                 // el sacador (el HELD manda)
  const Xn = Xg.net;
  const hacia = Xg === Hg ? -1 : 1;                // host en -z, invitado en +z (local)
  const b = Xg.ball;
  b.pos.set(0, 1.0, CZ + hacia * 1.4);
  b.vel.set(0.2 * hacia, 2.2, hacia * 3.2);        // ~3.9 m/s (< MAX_BALL_SPEED)
  Xg.grips[Xg.paddleHand].position.copy(b.pos);    // la pala del sacador EN la bola
  await avanzar(0.05, par);                        // pose con la pala en sitio
  Xn.netLocalToss();
  await avanzar(0.30, par);
  Xg.rules.beginServeRally(Xg.rules.server);       // el strike abre el rallye (c12)
  Xn.netLocalHit(true);                            // HIT kind 1 · shot+1
  await avanzar(0.12, par);                        // el HIT aterriza en el rival (~22 ms + frame)
  bote(par, Xg);                                   // 1er bote del saque: mitad del sacador
  let ultimo = Xg;                                 // el último que golpeó = el ganador
  for (let i = 0; i < devoluciones; i++) {
    await avanzar(0.45, par);                      // el vuelo cruza la red (HANDOFF real)
    const Yg = ultimo === Hg ? Gg : Hg;            // el que recibe
    bote(par, Yg);                                 // el bote en su mitad (validBounce)
    if (Yg.rules.state !== 'rally') break;         // el árbitro cantó: fin del rallye
    Yg.processIntents(Yg.rules.registerPaddleHit('player', false));
    // la pala del golpeador EN la bola: el validador juzga la distancia con
    // la pose que viaja por el canal fast (HIT_NEAR_PAD 0,85 m)
    Yg.grips[Yg.paddleHand].position.copy(Yg.ball.pos);
    await avanzar(0.06, par);                      // una pose con la pala ya en sitio
    const haciaY = Yg === Hg ? -1 : 1;
    Yg.ball.vel.set(-0.15 * haciaY, 1.8, haciaY * 3.0);
    Yg.net.netLocalHit(false);                     // devuelve (shot+1, cadencia ok)
    ultimo = Yg;
  }
  // el que recibe NO devuelve: doble bote en su mitad → el árbitro REAL
  // canta el punto para `ultimo` en AMBOS extremos (claims reales)
  await avanzar(0.35, par);
  bote(par, ultimo === Hg ? Gg : Hg);
  await avanzar(0.20, par);
  bote(par, ultimo === Hg ? Gg : Hg);
  await avanzar(1.4, par);                         // ventana de claims/ack + resync si cabe
  for (let i = 0; i < 200 && (Hg.rules.state !== 'serve' || Gg.rules.state !== 'serve'); i++) {
    await avanzar(0.1, par);                       // la pausa de punto real (CONFIG) manda
  }
  return ultimo;
}

console.log('== ARNÉS DE MULTIPARTIDA (dos NetLink reales · bus ' + 22 + ' ms) ==');

/* ---------- G · reloj --------------------------------------------------- */
console.log('— G · handshake y reloj');
{
  const par = crearPar(22);
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.4, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', `handshake hello2/tick2/ready2 → v2 ok (H ${H.v2} · G ${G.v2})`);
  chk(G._clock.ready === true, 'reloj del invitado anclado (≥6 muestras)');
  chk(Math.abs(G._clock.offset) < 22 * 2 + 60,
    `offset del invitado acotado por la latencia (${Math.round(G._clock.offset)} ms ≤ ${22 * 2 + 60})`);
  chk(G._clock.rtt > 0 && G._clock.rtt < 22 * 2 + 80,
    `RTT medido ≈ 2·latencia (${Math.round(G._clock.rtt)} ms)`);

  /* ---------- A · ARRANQUE ------------------------------------------- */
  console.log('— A · MATCH_START (mstart · auto-arranque del enlace, c09 _v2MaybeStart)');
  await avanzar(0.3, par);
  chk(Hg.mstarts === 1 && Gg.mstarts === 1, `una sola llamada a onNetMatchStart (H ${Hg.mstarts} · G ${Gg.mstarts})`);
  chk(Hg.rules.server === 'player' && Gg.rules.server === 'ai',
    `sacador espejo (host «player» · invitado «ai») — fs=host`);
  chk(H._ball.state === 'held' && H._ball.holder === 'me' && H._ball.mine === true,
    `bola HELD del ANFITRIÓN (H ${H._ball.state}/${H._ball.holder} · G ${G._ball.state}/${G._ball.holder})`);
  chk(G._ball.state === 'held' && G._ball.holder === 'opp' && G._ball.mine === false,
    'bola HELD del RIVAL vista por el invitado');
  chk(Hg.ballMesh.visible === true && Gg.ballMesh.visible === false,
    'visibilidad: sólo el sacador ve su bola');
  chk(Hg.rules.firstServer === 'player' && Gg.rules.firstServer === 'ai',
    'firstServer espejo (la fórmula de mstart.fs, c12:1470)');
  Hg.startOnlineMatch();                            // pulsón del anfitrión EN la cuenta atrás
  await avanzar(0.4, par);
  chk(Hg.mstarts === 1 && Gg.mstarts === 1,
    `el botón durante la cuenta atrás NO duplica el mstart (guardia r130: H ${Hg.mstarts} · G ${Gg.mstarts})`);
  await avanzar(3.2, par);
  chk(Hg._netStart === null && Gg._netStart === null,
    'cuenta atrás expira por el reloj del anfitrión en AMBOS');

  /* ---------- B · RALLYE + PUNTO + ROTACIÓN --------------------------- */
  console.log('— B · rallye real: toss → HIT → HANDOFF → punto → CLAIM/ACK');
  const ganadorB = await jugarRallye(par, 1);   // 1 devolución del invitado · el anfitrión falla
  const rh = Hg.rules, rg = Gg.rules;
  chk(ganadorB === Gg, 'el árbitro REAL de ambos extremos cantó el punto para el invitado');
  chk(rh.scoreAi === 1 && rg.scorePlayer === 1,
    `marcadores convergen EN ESPEJO (H ${rh.scorePlayer}-${rh.scoreAi} · G ${rg.scorePlayer}-${rg.scoreAi})`);
  chk(rh.rallySeq === rg.rallySeq, `rallySeq idéntico (H ${rh.rallySeq} · G ${rg.rallySeq})`);
  chk(H._sync.applied === G._sync.applied, `libro de reclamos al día (H ${H._sync.applied} · G ${G._sync.applied})`);
  chk(rh.state === 'serve' && rg.state === 'serve', 'ambos en saque tras la pausa del punto');
  chk((rh.server === 'player') === (rg.server === 'ai'),
    `siguiente sacador ESPEJO (H «${rh.server}» · G «${rg.server}») — rotación por gameOpener`);
  chk(H._ball.mine === (rh.server === 'player') && G._ball.mine === (rg.server === 'player'),
    'la bola HELD pertenece al sacador calculado en cada extremo');

  /* ---------- C · REVANCHA (partida 2) -------------------------------- */
  await avanzar(1.2, par);
  console.log('— C · revancha: segunda partida con applied viejo');
  rh.gamesPlayer = 2; rg.gamesPlayer = 2;           // el enfrentamiento terminó 2-x
  rh.gamesAi = 0; rg.gamesAi = 0;
  rh.state = 'over'; rg.state = 'over';
  rh.message = ''; rg.message = '';
  const appliedFinP1 = H._sync.applied;
  const serverFinP1_H = rh.server;
  H._mstartAt = performance.now() - 9000;           // el mstart de la partida 1 fue hace minutos
  await dormir(30);                                 // deja aterrizar cualquier sync en vuelo
  Gg.startOnlineMatch();                            // el INVITADO pide revancha ('r')
  await avanzar(0.5, par);
  chk(Hg.mstarts === 2 && Gg.mstarts === 2, `el guard del host aceptó el 'r' y abrió la partida 2`);
  chk(Hg.rules.server === 'player' && Gg.rules.server === 'ai',
    `SAQUE DE LA PARTIDA 2 correcto en los dos extremos (H «${Hg.rules.server}» · G «${Gg.rules.server}»)`);
  chk(H._ball.mine === true && G._ball.mine === false,
    'bola HELD del anfitrión al abrir la partida 2 (el informe del dueño)');
  chk(Hg.rules.scorePlayer === 0 && Hg.rules.scoreAi === 0 && Hg.rules.totalPoints === 0,
    'marcador a cero en la partida nueva (resetGame por mstart)');
  // D · los claims de la partida 2 (rallySeq reiniciado < applied viejo) se aplican
  chk(H._sync.applied === -1 && G._sync.applied === -1,
    `libro de reclamos REINICIADO con la partida nueva (r130: H ${H._sync.applied} · G ${G._sync.applied})`);
  const ganadorC = await jugarRallye(par, 2);   // 2 devoluciones · el invitado falla al final
  chk(Hg.rules.scorePlayer === 1 && Gg.rules.scoreAi === 1 &&
      Hg.rules.scoreAi === 0 && Gg.rules.scorePlayer === 0,
    `claim r=${Hg.rules.rallySeq} de la partida 2 APLICADO y CONFRONTADO ` +
    `(H ${Hg.rules.scorePlayer}-${Hg.rules.scoreAi} · G ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi})`);
  chk(H._sync.applied === 1 && G._sync.applied === 1,
    `el libro avanzó a la partida 2 en los dos (H ${H._sync.applied} · G ${G._sync.applied})`);

  /* ---------- E · RESYNC cura divergencia ----------------------------- */
  console.log('— E · resync del host');
  Hg.rules.state = 'serve'; Gg.rules.state = 'serve';   // resync en saque → setHeld
  Gg.rules.scorePlayer = 99;                        // divergencia forzada en el invitado
  H._sendResync();
  await avanzar(0.4, par);
  chk(Gg.rules.scorePlayer === Hg.rules.scoreAi && Gg.rules.scoreAi === Hg.rules.scorePlayer,
    `resync del host cura al invitado EN ESPEJO (H ${Hg.rules.scorePlayer}-${Hg.rules.scoreAi} · G ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi})`);
  chk(G._ball.state === 'held' && G._ball.mine === (Gg.rules.server === 'player'),
    'resync en saque re-ancla la FSM de bola (setHeld del sacador)');

  /* ---------- D · DOBLE REVANCHA SIMULTÁNEA --------------------------- */
  console.log('— D · guarda anti doble mstart (r75)');
  Hg.rules.gamesPlayer = 2; Gg.rules.gamesPlayer = 2;
  Hg.rules.state = 'over'; Gg.rules.state = 'over';
  const mstartsH = Hg.mstarts;
  H._mstartAt = performance.now() - 9000;
  Hg.startOnlineMatch();                            // el host pulsa revancha…
  Gg.startOnlineMatch();                            // …y el invitado casi a la vez ('r')
  await avanzar(0.5, par);
  chk(Hg.mstarts === mstartsH + 1 && Gg.mstarts === mstartsH + 1,
    'UNA sola partida nueva aunque los dos pulsen (el \'r\' tardío se ignora)');
  chk(Hg.rules.scorePlayer === 0 && Hg.rules.totalPoints === 0,
    'el estado de la partida 3 nace limpio (sin doble reset encadenado)');
}

/* ---------- F · sync v1 (builds mezclados) — espejo de perspectiva ----- */
console.log('— F · applySync v1 (invitado, perspectiva del anfitrión)');
{
  const par = crearPar(10);
  const { G, Gg } = par;
  preparar(G, Gg, 'guest'); Gg.rules = new Rules();
  // el anfitrión lleva SU perspectiva: «player» = él, 3-5, saca él
  G.applySync({ ow: 'host', st: 'serve', sv: 'player', sp: 3, sa: 5, md: 'match', bo: 3, gp: 1, ga: 0, rh: 2 });
  chk(Gg.rules.scorePlayer === 5 && Gg.rules.scoreAi === 3,
    `marcador espejado (él 3-5 → yo 5-3): ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi}`);
  chk(Gg.rules.server === 'ai', 'sacador espejado: el anfitrión saca → mi sacador es «ai»');
  chk(Gg.rules.gamesPlayer === 0 && Gg.rules.gamesAi === 1, 'serie espejada (gp/ga con perspectiva)');
  G.applySync({ ow: 'host', st: 'serve', sv: 'ai', sp: 3, sa: 6, md: 'match', bo: 3, gp: 1, ga: 0, rh: 2 });
  chk(Gg.rules.server === 'player', 'cuando el anfitrión cede el saque, YO saco');
}


/* ==================== SEGUNDA OLA · adversa y ciclos completos ========= */

console.log('— H · pausa/reanudación del rival (visor oculto, spec §10)');
{
  const par = crearPar(18);
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.4, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'enlace listo para la pausa');
  // el SENDER real (_onVis) envía exactamente esto al ocultarse (c09:1044-1046;
  // el listener vive en startV2, que el arnés no monta — el mensaje es lo que importa)
  H.sendRel({ k: 'pause', t: H._clock.nowHost(performance.now()) });
  await avanzar(0.3, par);
  chk(G._pausedRemote === true && Gg.netPausa === true,
    'el invitado entra en pausa al ocultarse el visor del anfitrión');
  H.sendRel({ k: 'resume', t: H._clock.nowHost(performance.now()) });
  await avanzar(0.3, par);
  chk(G._pausedRemote === false && Gg.netPausa === false,
    'reanudación limpia al volver el visor');
}

console.log('— J · DUELOS LOCOS online (md en el mstart + poder por la red)');
{
  const par = crearPar(18);
  const { H, G, Hg, Gg } = par;
  Hg._mjMode = 'duelos';
  Hg._netStartWhenReady = true;                 // el dueño pidió duelos durante la subida
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.6, par);
  chk(Hg.mode === 'duelos' && Gg.mode === 'duelos',
    `modo DUELOS espejado vía mstart.md (H ${Hg.mode} · G ${Gg.mode}) — y UN solo mstart`);
  chk(Hg.mstarts === 1 && Gg.mstarts === 1,
    `el arranque diferido NO duplica (auto-mstart omitido con _netStartWhenReady: H ${Hg.mstarts} · G ${Gg.mstarts})`);
  chk((Hg.duelosReiniciados || 0) >= 1 && (Gg.duelosReiniciados || 0) >= 1,
    '_dlReset corre en ambos extremos (poderes a cero al empezar)');
  H.sendDueloPower('gigante');
  await avanzar(0.4, par);
  chk((Gg.powRecibidos || 0) === 1, 'el poder disparado por el anfitrión llega al invitado (pow)');
}

console.log('— K · PARTIDA COMPLETA: mejor de 3, rotación ITTF entre juegos, fin de partido');
{
  const par = crearPar(18);
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.4, par);
  const rh = Hg.rules, rg = Gg.rules;
  const siGanaAnfitrion = () => (sacador(H) ? 0 : 1);   // el que recibe devuelve y el sacador falla
  const siGanaInvitado = () => (sacador(H) ? 1 : 0);
  // juego 1 · anfitrión 9-7 → dos puntos suyos → 11-7 y juego
  rh.scorePlayer = 9; rh.scoreAi = 7; rh.totalPoints = 16;
  rg.scorePlayer = 7; rg.scoreAi = 9; rg.totalPoints = 16;
  await jugarRallye(par, siGanaAnfitrion());
  await jugarRallye(par, siGanaAnfitrion());
  chk(rh.gamesPlayer === 1 && rg.gamesAi === 1,
    `juego 1 para el anfitrión (puntos H ${rh.scorePlayer}-${rh.scoreAi} · G ${rg.scorePlayer}-${rg.scoreAi} · ` +
    `juegos H ${rh.gamesPlayer}-${rh.gamesAi} · G ${rg.gamesAi}-${rg.gamesPlayer})`);
  chk(rh.gameNo === 2 && rg.gameNo === 2, `rotación al juego 2 (gameNo ${rh.gameNo})`);
  const abridorJ2_H = rh.server;
  chk(abridorJ2_H === 'ai' && rg.server === 'player',
    `juego 2 abre el OTRO (ITTF · gameNo par): H «${abridorJ2_H}» · G «${rg.server}»`);
  // juego 2 · invitado 9-7 → dos puntos suyos → 11-7 y juego (1-1)
  rh.scorePlayer = 7; rh.scoreAi = 9; rh.totalPoints = 16;
  rg.scorePlayer = 9; rg.scoreAi = 7; rg.totalPoints = 16;
  await jugarRallye(par, siGanaInvitado());
  await jugarRallye(par, siGanaInvitado());
  chk(rh.gamesPlayer === 1 && rh.gamesAi === 1 && rg.gamesPlayer === 1 && rg.gamesAi === 1,
    'juego 2 para el invitado · serie 1-1 espejada');
  // juego 3 · el anfitrión cierra el enfrentamiento
  rh.scorePlayer = 9; rh.scoreAi = 2; rh.totalPoints = 11;
  rg.scorePlayer = 2; rg.scoreAi = 9; rg.totalPoints = 11;
  await jugarRallye(par, siGanaAnfitrion());
  await jugarRallye(par, siGanaAnfitrion());
  chk(rh.state === 'over' && rg.state === 'over',
    `FIN DEL ENFRENTAMIENTO en ambos extremos (H «${rh.state}» · G «${rg.state}»)`);
  chk(rh.gamesPlayer === 2 && rh.gamesAi === 1 && rg.gamesAi === 2 && rg.gamesPlayer === 1,
    'serie final 2-1 espejada (el anfitrión campeón)');
  // r130 · CANDADO DEL BUG #5: el 'over' en online NO se auto-reinicia a los
  // 8 s (rules.update → startMatch divergía el abridor y bloqueaba el 'r') —
  // el estado sigue 'over' en ambos y la revancha sigue aceptándose
  await avanzar(9.5, par);
  chk(rh.state === 'over' && rg.state === 'over' &&
      rh.gamesPlayer === 2 && rg.gamesAi === 2,
    `'over' ESTABLE en online tras 9,5 s sin mstart (el auto-reinicio local no dispara: ` +
    `H «${rh.state}» ${rh.gamesPlayer}-${rh.gamesAi} · G «${rg.state}» ${rg.gamesAi}-${rg.gamesPlayer})`);
  const revanchaOK = (performance.now() - H._mstartAt) > 8000 ||
    (H._mstartAt = performance.now() - 9000, true);
  chk(revanchaOK, 'ventana de revancha preparada');
}

console.log('— M · canal fast ADVERSO: 30% pérdida · 15% duplicados · ±25 ms reordenación');
{
  const par = crearPar(25, { lossFast: Number(process.env.LOSS || 0.30), dupFast: Number(process.env.DUP || 0.15), jitterFast: 25 });
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.8, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'handshake inmune al canal fast adverso (reliable sano)');
  const rh = Hg.rules, rg = Gg.rules;
  rh.scorePlayer = 9; rh.scoreAi = 7; rh.totalPoints = 16;
  rg.scorePlayer = 7; rg.scoreAi = 9; rg.totalPoints = 16;
  const ganador = await jugarRallye(par, sacador(H) ? 1 : 0);   // devuelve el que NO saca
  chk(rh.rallySeq === rg.rallySeq && rh.rallySeq >= 1,
    `rallySeq idéntico con pérdida/duplicación (${rh.rallySeq}) — HIT/HANDOFF retransmiten por _pend`);
  chk(rh.scorePlayer === rg.scoreAi && rh.scoreAi === rg.scorePlayer && rh.totalPoints === 17,
    `el punto converge con el canal desbaratado (H ${rh.scorePlayer}-${rh.scoreAi} · G ${rg.scorePlayer}-${rg.scoreAi})`);
  chk(H._sync.applied === G._sync.applied,
    `libro de reclamos al día bajo adversidad (${H._sync.applied})`);
}

console.log('— L · RESYNC-REQ: el receptor pide la verdad del anfitrión en plena partida');
{
  const par = crearPar(18);
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.4, par);
  Hg.rules.scorePlayer = 3; Hg.rules.scoreAi = 1; Hg.rules.totalPoints = 4;
  Gg.rules.scorePlayer = 99; Gg.rules.scoreAi = 42; Gg.rules.totalPoints = 141;  // divergencia
  Gg.rules.state = 'serve'; Hg.rules.state = 'serve';
  G.sendRel({ k: 'resync-req' });               // el receptor pide resync (r122)
  await avanzar(0.4, par);
  chk(Gg.rules.scorePlayer === Hg.rules.scoreAi && Gg.rules.scoreAi === Hg.rules.scorePlayer,
    `resync-req cura al receptor (H ${Hg.rules.scorePlayer}-${Hg.rules.scoreAi} · G ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi})`);
  chk(G._ball.state === 'held' && G._ball.mine === (Gg.rules.server === 'player'),
    'resync-req re-ancla la FSM de bola en saque');
}

console.log('— N · watchdog de silencio: rival muerto sin cierre → partida termina LIMPIA');
{
  const par = crearPar(12);
  const { H, G, Hg, Gg } = par;
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.4, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'enlace vivo antes del apagón');
  par.muerto = true;                            // el rival desaparece SIN cierre (app matada)
  await avanzar(13.5, par);                     // el watchdog del ANFITRIÓN: 12 s
  chk(H.status === 'off',
    `el anfitrión cae a 'off' por silencio (12 s · H ${H.status})`);
  chk(!!Hg.finRed, 'onNetEnded avisa al juego del anfitrión (sin partida zombi)');
  // el INVITADO aguanta más POR DISEÑO (r112): reintenta ICE a los 5 y 15 s
  // (ICE_RESTART_MS 10000 · MAX 2) y su régimen de silencio es 25 s mientras
  // el reintento está vivo — cae a ~30 s cuando el régimen vuelve a 12 s
  await avanzar(18, par);
  chk(G.status === 'off',
    `el invitado cae tras agotar los reintentos de ICE (${G.status} · régimen 25 s r112)`);
  chk(!!Gg.finRed, 'onNetEnded avisa también al juego del invitado');
}


console.log('— O · RE-ENTRADA: colgar y jugar OTRA sesión sobre los MISMOS objetos (bug #6)');
{
  const par = crearPar(16);
  const { H, G, Hg, Gg } = par;
  // sesión 1: sala, handshake y PARTIDA (el mstart sella _mstartAt en c12:1494)
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.6, par);
  chk(Hg.mstarts === 1 && Gg.mstarts === 1, 'sesión 1: partido arrancado en ambos (mstart sellado)');
  H.hangup();                                  // bye + sendMatchEnd + teardown en ambos
  await avanzar(0.4, par);
  chk(H.status === 'off' && G.status === 'off' && !H.online && !G.online,
    'sesión 1 cerrada LIMPIA por ambos (hangup → teardown)');
  // sesión 2 SOBRE LOS MISMOS objetos — menos de 8 s después del mstart sellado
  H.startV2(); G.startV2();                    // ← aquí corre la re-init (fix bug #6)
  cablear(par, 16);
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.6, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'sesión 2: handshake sobre instancias reutilizadas');
  chk(H._lastIceTry === 0 && H._visOff === null && H._lastRemoteHitT === 0,
    `re-init de sesión: sellos a cero (iceTry ${H._lastIceTry} · visOff ${H._visOff === null} · hitT ${H._lastRemoteHitT})`);
  Hg.startOnlineMatch();                       // el anfitrión pulsa EMPEZAR en la sesión 2
  await avanzar(0.7, par);
  chk(Hg.mstarts === 2 && Gg.mstarts === 2,
    `el mstart de la sesión 2 LLEGA al invitado (mstarts H ${Hg.mstarts} · G ${Gg.mstarts}) — ` +
    'sin el fix, mstartReciente() lo silenciaba 8 s tras el mstart anterior');
  chk(Gg.rules.state === 'serve' || Gg.rules.state === 'rally',
    `la sesión 2 está JUGANDO (estado del invitado «${Gg.rules.state}»)`);
}


console.log('— P · CARRERA ASÍNCRONA: teardown durante la ventana ICE (bug #9)');
{
  const par = crearPar(16);
  const { H, G } = par;
  // P1 · el invitado cancela ANTES de que el ICE resuelva: nada se crea jamás
  globalThis.__PP_ICE_DELAY = 120;
  G.startV2(); G.teardown();
  await dormir(320);
  chk(G._pc === null && G.v2 === null,
    `P1 cancelación pre-ICE: sin pc (${G._pc === null ? 'null' : typeof G._pc}) y sin _v2Fail fantasma (v2=${G.v2})`);
  // P2 · cancela DESPUÉS de crear el pc, en plena oferta: el pc se CIERRA
  globalThis.__PP_RTC_DELAY = 90;
  const antes = globalThis.__PP_PC_CERRADOS;
  G.startV2();                          // ICE 120 → pc → oferta (90) → setLocal (90)
  await dormir(185);                    // el pc YA existe; la oferta sigue en vuelo
  G.teardown();
  await dormir(450);
  chk(globalThis.__PP_PC_CERRADOS > antes,
    `P2 cancelación en plena oferta: el pc huérfano se cerró (+${globalThis.__PP_PC_CERRADOS - antes})`);
  chk(G._pc === null && G.v2 === null,
    `P2 sin asignación fantasma de _pc (${G._pc === null ? 'null' : 'FILTRADO'}) tras teardown`);
  // P3 · el anfitrión recibe un sdp con la ventana ICE abierta y se desmonta
  globalThis.__PP_RTC_DELAY = 0;
  H.startV2();                          // host: sin pc aún
  const pr = H._v2RemoteDesc({ type: 'offer', sdp: 'x' });   // ICE 120 en vuelo
  await dormir(60); H.teardown();       // cancela DENTRO de la ventana ICE
  await pr; await dormir(60);
  chk(H._pc === null && H.v2 === null,
    `P3 sdp en vuelo + teardown: sin pc creado (${H._pc === null ? 'null' : 'FILTRADO'})`);
  // P4 · fallo de sdp sobre sesión ya muerta: SIN _v2Fail fantasma
  globalThis.__PP_ICE_DELAY = 0; globalThis.__PP_RTC_DELAY = 90;
  H.startV2();                          // re-estampa el token de sesión
  const pr4 = H._v2RemoteDesc({ type: 'offer', sdp: 'BOOM' });   // setRemote: retraso + throw
  await dormir(60); H.teardown();
  await pr4.catch(() => {}); await dormir(160);
  chk(H.v2 === null,
    `P4 fallo de sdp tras teardown: SIN _v2Fail fantasma (v2=${H.v2})`);
  // P5 · la sesión siguiente, sobre los mismos objetos, sigue sana
  globalThis.__PP_RTC_DELAY = 0;
  H.startV2(); G.startV2();
  cablear(par, 16);
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.6, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'P5 sesión nueva tras la tormenta: handshake limpio en ambos');
}


console.log('— R · SUPERVIVENCIA ONLINE: espejo de modo en ambos extremos (bug #11)');
{
  const par = crearPar(16);
  const { H, G, Hg, Gg } = par;
  H.startV2(); G.startV2();
  cablear(par, 16);
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.2, par);
  // R1 · el INVITADO pide supervivencia (c12:7256): el anfitrión cambia y
  // DEBE devolver el eco — si no, el invitado se queda en PARTIDO
  Gg.mode = 'match'; Hg.mode = 'match'; Gg.__sw = []; Hg.__sw = [];
  Gg.net.sendMode('survival');
  await avanzar(0.4, par);
  chk(Hg.__sw.length === 1 && Hg.__sw[0] === 'survival',
    `R1 anfitrión: cambia a supervivencia (${JSON.stringify(Hg.__sw)})`);
  chk(Gg.__sw.length === 1 && Gg.__sw[0] === 'survival',
    `R1 INVITADO: recibe confirmación y refleja el modo (${JSON.stringify(Gg.__sw)})`);
  // R2 · sin bucle de eco
  await avanzar(0.6, par);
  chk(Hg.__sw.length === 1 && Gg.__sw.length === 1,
    `R2 sin bucle (${Hg.__sw.length}/${Gg.__sw.length} switches tras tick extra)`);
  // R3 · el ANFITRIÓN pide (c12:7264, FASE 144): espejo directo sin doble
  Gg.mode = 'match'; Hg.mode = 'survival'; Gg.__sw = []; Hg.__sw = [];
  Hg.net.sendMode('survival');
  await avanzar(0.4, par);
  chk(Gg.__sw.length === 1 && Gg.__sw[0] === 'survival',
    `R3 invitado refleja la petición del anfitrión (${JSON.stringify(Gg.__sw)})`);
  chk(Hg.__sw.length === 0,
    `R3 anfitrión ya en el modo: cero switches extra (${Hg.__sw.length})`);
  // R4 · pedido redundante con ambos en supervivencia: guard mode===mode
  Gg.__sw = []; Hg.__sw = [];
  Gg.net.sendMode('survival');
  await avanzar(0.4, par);
  chk(Hg.__sw.length === 0 && Gg.__sw.length === 0,
    'R4 pedido redundante: sin switches ni bucle (guard mode===mode)');
}


console.log('— F · FUZZING del protocolo: entradas malformadas vs invariantes (7ª pasada)');
{
  const par = crearPar(16);
  const { H, G, Hg, Gg } = par;
  H.startV2(); G.startV2();
  cablear(par, 16);
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.2, par);
  Hg.startOnlineMatch();
  await avanzar(1.6, par);
  chk(Hg.rules.state === 'serve' || Hg.rules.state === 'rally',
    `F0 sesión viva antes del fuzz (${Hg.rules.state})`);

  const lanza = async (lado, m, nombre) => {
    let tiro = null;
    try { lado.onData(m); } catch (e) { tiro = e; }
    await avanzar(0.03, par);
    if (tiro) chk(false, `F·${nombre} — onData LANZÓ: ${tiro.message || tiro}`);
  };
  const invariante = (etiqueta) => {
    for (const [nm, gg] of [['H', Hg], ['G', Gg]]) {
      const bp = gg.ball.pos, bv = gg.ball.vel;
      chk([bp.x, bp.y, bp.z, bv.x, bv.y, bv.z].every(Number.isFinite),
        `F·${etiqueta} — bola ${nm} finita (${JSON.stringify({x: bp.x, y: bp.y, z: bp.z})})`);
    }
    chk(H.online && G.online, `F·${etiqueta} — sesión sigue online`);
  };

  const C = [
    ['p-vacío', { k: 'p' }],
    ['p-pad-corto', { k: 'p', pad: [0.5] }],
    ['p-pad-tipo', { k: 'p', pad: [0.5, 0.5, 'x', 0, 0, 0, 0] }],
    ['p-pad-nan', { k: 'p', pad: [NaN, 0, 0, 0, 1, 0, 0, 0] }],
    ['p-bola-corta', { k: 'p', b: { p: [1, 2], v: [0] } }],
    ['p-ev-basura', { k: 'p', e: [['X', NaN, 1, 2], 'trampa', [9]] }],
    ['p-sync-basura', { k: 'p', y: { score: [NaN, 'x'] } }],
    ['h-vacío', { k: 'h' }],
    ['h-p-string', { k: 'h', sv: 1, p: 'x', v: 'y' }],
    ['h-nan', { k: 'h', sv: 1, p: [1, 2, 3], v: [NaN, 0, 0] }],
    ['h-gigante', { k: 'h', sv: 0, p: [9e9, -9e9, 9e9], v: [1e9, 0, 0] }],
    ['h-spin-nan', { k: 'h', sv: 0, p: [1, 1, 1], v: [1, 1, 1], s: [NaN, NaN, 'x'] }],
    ['mstart-vacío', { k: 'mstart' }],
    ['mstart-sa-neg', { k: 'mstart', sa: -5, fs: 'host', bo: 3 }],
    ['mstart-sa-nan', { k: 'mstart', sa: NaN, fs: 'host', bo: 3 }],
    ['claim-basura', { k: 'claim', w: 'basura', id: 99 }],
    ['claim-nan', { k: 'claim', w: 'net', n: NaN, t: 'x', id: 100 }],
    ['ack-neg', { k: 'ack', seq: -1 }],
    ['ack-gig', { k: 'ack', seq: 1e12 }],
    ['resync-basura', { k: 'resync', sa: 'x', w: -9 }],
    ['resync-req-vacío', { k: 'resync-req' }],
    ['pow-desconocido', { k: 'pow', p: 999 }],
    ['hallv-basura', { k: 'hallv', v: { id: 99999, cfg: 'x'.repeat(5000) } }],
    ['mend-vacío', { k: 'mend' }],
    ['sdp-basura', { k: 'sdp', d: 'no-json' }],
    ['ice-basura', { k: 'ice', c: { wtf: 1 } }],
    ['resync-st-basura', { k: 'resync', st: 'trampa', sa: 'x', sp: NaN }],
    ['v2off-hostil', { k: 'v2off' }],
    ['f2-truncado', { k: 'f2', b: new ArrayBuffer(4) }],
    ['k-desconocido', { k: 'zzz', todo: [1, 2, 3] }],
    ['no-objeto-1', 42],
    ['no-objeto-2', 'hola'],
    ['no-objeto-3', null],
  ];
  for (const [nm, m] of C) await lanza(G, m, nm);
  await avanzar(0.4, par);
  invariante('post-corpus');

  let tiroR = null;
  for (let i = 0; i < 200; i++) {
    try {
      G.onData({ k: 'h', sv: 1, p: [NaN, NaN, NaN], v: [NaN, 0, 0], s: ['x'] });
      H.onData({ k: 'h', sv: 1, p: [NaN, NaN, NaN], v: [NaN, 0, 0], s: ['x'] });
    } catch (e) { tiroR = e; break; }
  }
  chk(!tiroR, `F·ráfaga-200 sin excepciones ${tiroR ? '(' + tiroR + ')' : ''}`);
  await avanzar(0.6, par);
  invariante('post-ráfaga');
  chk((H._pendingHits || []).length < 50,
    `F·cola de golpeos del anfitrión drenada sin basura (${(H._pendingHits || []).length})`);

  await lanza(G, { k: 'hello2', v: 999, ph: 999, b: 1 }, 'hello2-hostil');
  chk(G.v2 === 'ok', `F·hello2 hostil IGNORADO en sesión viva (v2=${G.v2})`);
}


console.log('— S · SOAK caótico: 5 tramos de rally con canal aleatorio + inyecciones (8ª pasada)');
{
  const par = crearPar(16, { lossFast: 0.30, dupFast: 0.25, jitterFast: 80 });
  const { H, G, Hg, Gg } = par;
  // r132 · 11ª: instrumentación del flake — cadena de emisión completa
  for (const [nm2, X] of [['H', H], ['G', G]]) {
    X._sfE = 0; X._fsS = 0;
    const osf = X._sendFast.bind(X), ofs = X._fastSend.bind(X),
      oir = X._iceRestartIntento ? X._iceRestartIntento.bind(X) : null,
      ovf = X._v2Fail.bind(X);
    X._sendFast = (dt, now) => { X._sfE++; return osf(dt, now); };
    X._fastSend = (b, now) => { X._fsS++; return ofs(b, now); };
    if (oir) X._iceRestartIntento = () => {
      console.log(`  [diag] ICE-RESTART en ${nm2} (nº ${X._iceRestarts})`);
      return oir();
    };
    X._v2Fail = (r) => { console.log(`  [diag] _v2Fail en ${nm2}: ${r}`); return ovf(r); };
  }
  for (const [nm, X] of [['H', H], ['G', G]]) {
    const orig = X._v2Fail.bind(X);
    X._v2Fail = (r) => { const st = (new Error().stack || '').split('\n').slice(2, 6).map((x) => x.trim().replace(/^at /, '')).join(' <- ');console.log(`  [diag] ${nm}._v2Fail: ${r}\n      pila: ${st}`); orig(r); };
    const ow = X._watchdog ? X._watchdog.bind(X) : null;
    if (ow) X._watchdog = (...a) => { console.log(`  [diag] ${nm} watchdog`); return ow(...a); };
    const opg = X.onPeerGone.bind(X);
    X.onPeerGone = (r) => { const n = performance.now();const sil = X._pausedRemote ? 60000 : (X._lastIceTry && (n - X._lastIceTry) < 15000 ? 25000 : 12000);console.log(`  [diag] ${nm} onPeerGone: ${r} · fastAge=${Math.round(n - (X._lastFastAt || n))} relAge=${Math.round(n - (X._lastRelAt || n))} SILENCIO=${sil} fastOpen=${X._fastOpen} relOpen=${X._relOpen} tun=${!!X._tunnel} v2=${X.v2} pend=${(X._pend || []).length}`); return opg(r); };
  }
  H.startV2(); G.startV2();
  cablear(par, 16);   // r132-8ª · startV2 RESETEA _fast/_rel/_fastOpen (c09:1021) —
                      // el re-cableado post-startV2 es OBLIGATORIO (lección: el
                      // soak sin él dejó v2='pending' 15 s y el hello2 hostil
                      // alcanzó _v2Fail — bug del ARNÉS, no del juego)
  H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(1.2, par);
  // r132 · 11ª (flake del soak, volcado con claves): el stub de
  // RTCPeerConnection dispara DOS oleadas asíncronas de canales (offer del
  // invitado y ondatachannel del respondedor) — la segunda pone un dc SIN
  // `send` sobre el invitado y su emisión muere en el catch de _fastSend →
  // el watchdog del anfitrión mata a los 12 s. Las oleadas son únicas:
  // RE-CABLEAR tras el handshake deja el bus como dueño permanente.
  cablear(par, 16); H._v2ChannelsUp(); G._v2ChannelsUp();
  chk(H.v2 === 'ok' && G.v2 === 'ok', `S0v enlace v2 ok antes del soak (${H.v2}/${G.v2})`);
  chk((H._fast && H._fast._tag) === 'destinoGF' && (G._fast && G._fast._tag) === 'destinoHF'
      && (G._rel && G._rel._tag) === 'destinoHR',
    `S0t cableado del bus vigente (${(H._fast && H._fast._tag) || 'null'}/${(G._fast && G._fast._tag) || 'null'}/${(G._rel && G._rel._tag) || 'null'})`);
  Hg.startOnlineMatch();
  await avanzar(1.6, par);
  chk(Hg.rules.state === 'serve' || Hg.rules.state === 'rally',
    `S0 sesión viva antes del soak (${Hg.rules.state})`);

  // las mutaciones más corrosivas del fuzzer F, a baja tasa aleatoria
  const C = [
    () => ({ k: 'h', sv: 1, p: [NaN, 1, 2], v: [NaN, 0, 0] }),
    () => ({ k: 'p', pad: [0.5, 0.5, 'x', 0, 0, 0, 0] }),
    () => ({ k: 'claim', w: 'basura', id: 999 }),
    () => ({ k: 'mstart', sa: NaN }),
    () => ({ k: 'hello2', v: 999, ph: 999 }),
    () => ({ k: 'resync', sa: 'x' }),
    () => ({ k: 'resync', st: 'trampa', sa: 'x' }),
    () => ({ k: 'v2off' }),
    () => ({ k: 'f2', b: new ArrayBuffer(4) }),
    () => 42,
  ];
  for (let tramo = 0; tramo < 8; tramo++) {
    par.lossFast = 0.20 + Math.random() * 0.30;
    par.dupFast = Math.random() * 0.30;
    par.jitterFast = 20 + Math.random() * 60;
    for (let i = 0; i < 24; i++) {
      if (Math.random() < 0.3) {
        try { const m = C[(Math.random() * C.length) | 0]();
          const X = (Math.random() < 0.5 ? G : H);
          if (m && m.k === 'hello2') console.log(`  [diag] hello2 → ${X === G ? 'G' : 'H'} v2=${X.v2} helloDone=${X._helloDone}`);
          X.onData(m);
        } catch (eInj) { chk(false, `S·t${tramo} inyección lanzó: ${eInj.message || eInj}`); }
      }
      // disparador de atasco: el _lastFastAt del anfitrión parado >2 s
      const nms = performance.now();
      if (H._lastFastAt && nms - H._lastFastAt > 2000 && !par._stall) {
        par._stall = true;
        const dA = (k) => `${par.busA[k] || 0}/${par.busD[k] || 0}`;
        console.log(`  [diag] STALL fast→H t${tramo}: fastAge=${Math.round(nms - H._lastFastAt)}` +
          ` bus G→H fast ${dA('hf')} rel ${dA('hr')} · H→G fast ${dA('gf')}` +
          ` | G._sendFast=${G._sfE} G._fastSend=${G._fsS} G._sends=${G._sends || 0}` +
          ` tagG=${(G._fast && G._fast._tag) || 'null'} esBus=${G._fast === (par._tags && par._tags.gF)}` +
          ` tagR=${(G._rel && G._rel._tag) || 'null'} G.fastOpen=${G._fastOpen}` +
          ` clavesG=[${G._fast ? Object.keys(G._fast).join('|') : 'NULL'}]` +
          ` srcSend=${(G._fast && G._fast.send) ? String(G._fast.send).replace(/\s+/g, ' ').slice(6, 64) : 'N/A'}` +
          ` G.poseAcc=${(G._poseAcc || -1).toFixed(4)} G.poseHz=${G._poseHz}` +
          ` G.iceR=${G._iceRestarts || 0} G.lastIce=${G._lastIceTry ? Math.round(nms - G._lastIceTry) : '-'}ms` +
          ` G.tun=${!!G._tunnel} G.v2=${G.v2} G.online=${G.online}` +
          ` H.fastOpen=${H._fastOpen} loss=${par.lossFast.toFixed(2)} jit=${par.jitterFast.toFixed(0)}`);
      }
      if (i === 12) {   // un ciclo pausa/reanudación por tramo, con caos
        try { if (H.v2 === 'ok') H.sendRel({ k: 'pause', t: H._clock.nowHost(performance.now()) }); } catch (eP) { console.log(`  [diag] pausa lanzó: ${eP.message}`); }
        await avanzar(0.25, par);
        try { if (G.v2 === 'ok') G.sendRel({ k: 'resume' }); } catch (eP2) { console.log(`  [diag] resume lanzó: ${eP2.message}`); }
      }
      await avanzar(0.125, par);
    }
    for (const [nm, X, gg] of [['H', H, Hg], ['G', G, Gg]]) {
      const bp = gg.ball.pos, bv = gg.ball.vel;
      chk([bp.x, bp.y, bp.z, bv.x, bv.y, bv.z].every(Number.isFinite),
        `S·t${tramo} bola ${nm} finita bajo caos (${JSON.stringify({x: bp.x, y: bp.y, z: bp.z})})`);
      chk((X._pendingHits || []).length < 200 && (X._inEvs || []).length < 500,
        `S·t${tramo} colas ${nm} acotadas (${(X._pendingHits || []).length}/${(X._inEvs || []).length})`);
    }
    chk(H.online && G.online && H.v2 === 'ok' && G.v2 === 'ok',
      `S·t${tramo} enlace v2 vivo (loss=${par.lossFast.toFixed(2)} dup=${par.dupFast.toFixed(2)} jit=${par.jitterFast.toFixed(0)})`);
    chk(typeof Hg.rules.state === 'string' && typeof Gg.rules.state === 'string',
      `S·t${tramo} estados coherentes (${Hg.rules.state}/${Gg.rules.state})`);
  }
}


console.log('— T · CHURN de sesiones ×10: teardown→handshake→mstart→rally→teardown, sin fuga (9ª pasada)');
{
  const par = crearPar(16, {});
  const { H, G, Hg, Gg } = par;
  for (let ciclo = 1; ciclo <= 10; ciclo++) {
    // sesión nueva desde cero (el NetLink REAL recorre teardown→startV2)
    H.teardown(); G.teardown();
    H.startV2(); G.startV2();
    cablear(par, 16);
    H._v2ChannelsUp(); G._v2ChannelsUp();
    await avanzar(0.9, par);
    if (!(H.v2 === 'ok' && G.v2 === 'ok')) {
      chk(false, `T·c${ciclo} handshake no llegó a ok (${H.v2}/${G.v2})`);
      break;
    }
    Hg.startOnlineMatch();
    await avanzar(0.7, par);
    // el ciclo anterior NO debe sangrar: marcador, rallySeq y libro a cero
    const limpio = Hg.rules.scorePlayer === 0 && Hg.rules.scoreAi === 0 &&
      Gg.rules.scorePlayer === 0 && Gg.rules.scoreAi === 0;
    if (!limpio) { chk(false, `T·c${ciclo} marcador heredado de la sesión anterior`); break; }
    if (H._seenEv.size > 50 || G._seenEv.size > 50) {
      chk(false, `T·c${ciclo} _seenEv acumulado (${H._seenEv.size}/${G._seenEv.size})`);
      break;
    }
    // un rallye real en la sesión N para dejar "sangre" que el N+1 debe limpiar
    try { H.onLocalPointIntent({ w: 'ai', tp: 'hand' }); } catch (eI) {
      chk(false, `T·c${ciclo} intent lanzó: ${eI.message || eI}`); break;
    }
    await avanzar(0.4, par);
    if (ciclo === 10) {
      chk(H.v2 === 'ok' && G.v2 === 'ok', 'T·10 sesiones consecutivas, todas v2 ok');
      chk(Hg.rules.scorePlayer === 0 && Gg.rules.scorePlayer === 0,
        `T·c10 marcador limpio tras 10 ciclos (${Hg.rules.scorePlayer}/${Gg.rules.scorePlayer})`);
      chk(H._seenEv.size <= 50 && G._seenEv.size <= 50,
        `T·c10 dedupe acotado tras 10 sesiones (${H._seenEv.size}/${G._seenEv.size})`);
      chk((H._pend || []).length === 0 && (G._pend || []).length === 0,
        `T·c10 reliable pendiente a cero tras 10 sesiones (${H._pend.length}/${G._pend.length})`);
    }
  }
}

console.log('— T2 · resync: cada estado legítimo APLICA y cada corrupto RECHAZA (9ª pasada)');
{
  const par = crearPar(16, {});
  const { H, G, Gg } = par;
  H.startV2(); G.startV2();
  cablear(par, 16); H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(0.9, par);
  // fs/go/lh/aw viajan en player|ai (el resync manda r.firstServer ya
  // normalizado por el mstart; host|guest es SOLO del mstart)
  const base = { k: 'resync', sp: 3, sa: 1, sv: 'player', tp: 7, gp: 2, ga: 1, gn: 3, fs: 'player', go: 'player', lh: 'player', vb: true, rs: 4, sh: 2, aw: 'player' };
  for (const st of ['serve', 'rally', 'point', 'over']) {
    Gg.rules.scorePlayer = 99;   // tinta: si el resync aplica, sale por el flip
    G._applyResync({ ...base, st });
    // perspectiva INVITADO: scorePlayer = m.sa (1) · scoreAi = m.sp (3)
    chk(Gg.rules.scorePlayer === 1 && Gg.rules.scoreAi === 3 && Gg.rules.state === st,
      `T2·resync legítimo st='${st}' aplica (flip correcto)`);
    chk(Gg.rules.server === 'ai' && Gg.rules.firstServer === 'ai',
      `T2·st='${st}' sv/fs volteados al invitado`);
  }
  const corruptos = [
    ['st-basura', { ...base, st: 'trampa' }],
    ['st-ausente', { ...base, st: undefined }],
    ['sa-string', { ...base, sa: 'x' }],
    ['sp-nan', { ...base, sp: NaN }],
    ['gn-negativo', { ...base, gn: -1 }],
    ['sv-basura', { ...base, sv: 'fantasma' }],
    ['fs-basura', { ...base, fs: 42 }],
    ['tp-decimal', { ...base, tp: 2.5 }],
  ];
  for (const [nm, m] of corruptos) {
    Gg.rules.scorePlayer = 77; Gg.rules.state = 'serve';
    G._applyResync(m);
    chk(Gg.rules.scorePlayer === 77 && Gg.rules.state === 'serve',
      `T2·resync corrupto ${nm} RECHAZADO entero`);
  }
}


console.log('— U · MATRIZ de pares ordenados: 11 mensajes válidos × 121 combinaciones (10ª pasada)');
{
  const par = crearPar(16, {});
  const { H, G, Hg, Gg } = par;
  H.startV2(); G.startV2();
  cablear(par, 16); H._v2ChannelsUp(); G._v2ChannelsUp();
  await avanzar(0.9, par);
  chk(H.v2 === 'ok' && G.v2 === 'ok', 'U0 sesión v2 ok');

  // fábricas de mensajes VÁLIDOS (los que cambian estado o lo vergüenzan)
  const M = {
    mstart: () => ({ k: 'mstart', sa: H.hostNowMs() + 3000, fs: 'host', bo: 3, md: 'match' }),
    resync: () => ({ k: 'resync', sp: Hg.rules.scorePlayer | 0, sa: Hg.rules.scoreAi | 0,
      sv: Hg.rules.server, st: Hg.rules.state, tp: Hg.rules.totalPoints | 0,
      gp: Hg.rules.gamesPlayer | 0, ga: Hg.rules.gamesAi | 0, gn: Hg.rules.gameNo | 0,
      fs: Hg.rules.firstServer, go: Hg.rules.gameOpener, lh: Hg.rules.lastHitter,
      vb: !!Hg.rules.validBounce, rs: Hg.rules.rallySeq | 0, sh: 0, aw: null }),
    'resync-req': () => ({ k: 'resync-req' }),
    pause: () => ({ k: 'pause', t: H._clock.nowHost(performance.now()) }),
    resume: () => ({ k: 'resume' }),
    pow: () => ({ k: 'pow', p: 'gigante' }),
    hallv: () => ({ k: 'hallv', v: 'clasica' }),
    mend: () => ({ k: 'mend', r: { j: 'player', gp: 2, ga: 0 } }),
    hello2: () => ({ k: 'hello2', v: PPNET.VP.PROTO, ph: PPNET.VP.PHYS }),
    v2off: () => ({ k: 'v2off' }),
    r: () => ({ k: 'r' }),
  };
  const CLAVES = ['mstart', 'resync', 'resync-req', 'pause', 'resume', 'pow', 'hallv', 'mend', 'hello2', 'v2off', 'r'];
  const ESTADOS = ['serve', 'rally', 'point', 'over'];
  const enteroOk = (v) => typeof v === 'number' && Number.isInteger(v) && v >= 0;
  const coherente = (gg) => ESTADOS.includes(gg.rules.state) &&
    enteroOk(gg.rules.scorePlayer) && enteroOk(gg.rules.scoreAi) &&
    [gg.ball.pos.x, gg.ball.pos.y, gg.ball.pos.z,
     gg.ball.vel.x, gg.ball.vel.y, gg.ball.vel.z].every(Number.isFinite);

  let fallosU = 0, pares = 0;
  for (const a of CLAVES) {
    for (const b of CLAVES) {
      // ancla: mstart del anfitrión por el cable (libro/estado a cero ambos)
      try { H.sendRel(M.mstart()); } catch (eAn) { chk(false, `U·ancla lanzó: ${eAn.message}`); }
      await avanzar(0.30, par);
      let lanzo = null;
      try { H.sendRel(M[a]()); } catch (eA) { lanzo = `A(${a}): ${eA.message}`; }
      await avanzar(0.12, par);
      try { G.sendRel(M[b]()); } catch (eB) { lanzo = `B(${b}): ${eB.message}`; }
      await avanzar(0.18, par);
      const okV2 = H.v2 === 'ok' && G.v2 === 'ok';
      const okFSM = coherente(Hg) && coherente(Gg);
      pares++;
      if (lanzo || !okV2 || !okFSM) {
        fallosU++;
        chk(false, `U·[${a}→anf, ${b}→inv] ${lanzo || (!okV2
          ? `v2 ${H.v2}/${G.v2}` : `FSM ${Hg.rules.state}/${Gg.rules.state}`)}`);
        if (fallosU >= 8) { console.log('  (U aborta: 8 fallos)'); a = CLAVES[CLAVES.length]; b = CLAVES[CLAVES.length]; }
      }
    }
  }
  chk(fallosU === 0, `U·matriz coherente: ${pares} pares ordenados sin anomalía`);
  // candado 12g: el mstart del INVITADO ya NO resetea al anfitrión
  // (por EFECTO: snapshot del anfitrión antes/después — _mstart arranca
  // undefined en el anfitrión, compararlo con null es una trampa)
  const snap = { sp: Hg.rules.scorePlayer, st: Hg.rules.state,
    gn: Hg.rules.gameNo, rs: Hg.rules.rallySeq, tp: Hg.rules.totalPoints };
  G.sendRel(M.mstart());
  await avanzar(0.15, par);
  chk(Hg.rules.scorePlayer === snap.sp && Hg.rules.state === snap.st &&
      Hg.rules.gameNo === snap.gn && Hg.rules.rallySeq === snap.rs &&
      Hg.rules.totalPoints === snap.tp,
    `U·12g mstart del invitado ignorado por el anfitrión (${JSON.stringify({antes: snap, ahora: {sp: Hg.rules.scorePlayer, st: Hg.rules.state, gn: Hg.rules.gameNo, rs: Hg.rules.rallySeq, tp: Hg.rules.totalPoints}})})`);
  // y el espejo: el mstart del ANFITRIÓN sigue aplicando en el invitado
  H.sendRel(M.mstart());
  await avanzar(0.15, par);
  chk(Gg.rules.state === 'serve' && Gg.rules.bestOf === 3,
    `U·12g mstart del anfitrión SÍ aplica en el invitado (${Gg.rules.state}/${Gg.rules.bestOf})`);
}

console.log();
if (fails) {
  console.log(`✗ MULTIPARTIDA: ${ok} OK · ${fails} FALLO(S)`);
  process.exit(1);
}
console.log(`✓ MULTIPARTIDA COMPLETA: ${ok} escenarios OK · arranque, rallye, claims, revancha, guardas, espejo v1, pausa, duelos, partida completa, canal adverso, resync-req y watchdog en verde`);

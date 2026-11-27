#!/usr/bin/env node
/* VERIFICACIÓN PUNTUAL de la revisión de sincronización (sólo lectura del
 * proyecto: importa las fuentes reales y reproduce 4 hipótesis concretas).
 * Uso: node --no-warnings scripts/tmp_revision_check.mjs */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, removeEventListener: () => {}, hidden: false };
try { globalThis.navigator = { userAgent: 'node-rev' }; } catch { /* */ }
globalThis.T = (k, _v) => k;
globalThis.VERSION = 'rev-check';

const { NetLink } = await import('/home/z/my-project/src/game/core/c09_red_netlink.js');
const { Rules } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { PPNET } = await import('/home/z/my-project/src/game/core/c09b_red_nucleo.js');
const THREE = await import('three');
const V3 = THREE.Vector3;
const CZ = NetLink.TABLE_CZ;

function juego(role, net) {
  const g = {
    role, net, mode: 'match', pendingMode: 'match', doblesActivo: false,
    inHall: false, menuOpen: false, tossed: false, _mjMode: 'match',
    _netStart: null, _netStartWhenReady: false, _netResyncT: null, mstarts: 0,
    rules: new Rules(),
    ball: { pos: new V3(0, 1.0, CZ + 1.4), vel: new V3(), spin: new V3() },
    ballMesh: { visible: false },
    camera: { position: new V3(0, 1.6, CZ + 2.2), quaternion: { x: 0, y: 0, z: 0, w: 1 } },
    grips: [0, 1].map(() => ({ position: new V3(0, 1.0, CZ + 1.4), quaternion: { x: 0, y: 0, z: 0, w: 1 } })),
    paddleHand: 0, handOf: ['left', 'right'],
    paddleMounts: [{ quaternion: { x: 0, y: 0, z: 0, w: 1 } }, { quaternion: { x: 0, y: 0, z: 0, w: 1 } }],
    _dlOn: () => false, _dlReset() {}, onRemoteDueloPower() {}, onNetPause() {},
    onNetEnded() {}, renderer: { xr: { isPresenting: false } },
    audio: new Proxy({}, { get: () => () => {} }),
    resetToss() { g.tossed = false; }, exitHall() { g.inHall = false; },
    onNetV2Ready() {}, onNetStatus() {}, onNetMatchEnd() {},
    switchMode() {}, startFanfare() {}, onBuildMismatch() {}, onNetMatchStartElo() {},
    stats: { recordMatch: () => null, recordPoint: () => null, data: { elo: 1000 } },
    emitStats() {}, celebrate() {},
    startOnlineMatch() { if (net.role !== 'host') { net.sendRematch(); return; } },
    onNetMatchStart() { g.mstarts++; net.setServeHeld(true); },
    processIntents(list) { for (const it of list) g._intent(it); },
    _intent(it) {
      if (it.type === 'point') { g.puntos = (g.puntos || 0) + 1; net.onLocalPointIntent(it); }
      else if (it.type === 'retry-serve') net.onLocalRetryIntent(it);
      else if (it.type === 'serve') net.setServeHeld(it.server === 'player');
    },
    tick(dt) { /* vacío: los puntos llegan por claims/fuerza aquí */ },
  };
  return g;
}
function preparar(net, game, role) {
  net.game = game; net.role = role;
  net.v2 = 'ok'; net.online = true; net.status = 'online';
  net._pc = null; net._fast = null; net._rel = null;
  net._fastOpen = false; net._relOpen = false;
  net._seq = 1; net._ackP = 0; net._ackBits = 0; net._ackInit = false;
  net._echoTime = 0; net._echoAt = 0;
  net._pend = []; net._evId = 1; net._fastIn = [];
  net._seenEv = new Map(); net._recvRing = []; net._recvHist = [];
  net._lastPoseAt = 0; net._gaps = 0; net._recvs = 0;
  net._poseAcc = 0; net._snapAcc = 0; net._poseHz = PPNET.VP.POSE_HZ;
  net._tunT = 0; net._tunSalud = 0; net._qosAcc = 0;
  net._txBuf = new ArrayBuffer(PPNET.VP.MAX_PKT);
  net._lossLowT = 0; net._degraded = false;
  net._lastFastAt = performance.now(); net._iceRestarts = 0; net._lastIceTry = 0;
  net._helloDone = true; net._helloTO = null; net._iceQ = [];
  net._tunnel = false; net._v2T0 = performance.now();
  net._buildWarn = false; net.buildPeer = ''; net._verTele = false;
  net._anchors = 8; net._readyMe = true; net._readyOpp = true;
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
  net._lastRelAt = performance.now(); net._claimFallback = null; net._lastHitSent = 0;
  PPNET.VP.BUILD = 'rev-check';
}
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

/* ============ 1 · CLAIM «legacy» BASURA APLICA UN PUNTO FANTASMA ========= */
console.log('== 1 · claim sin r (legacy) con w basura ==');
{
  const H = new NetLink(null), G = new NetLink(null);
  const Hg = juego('host', H), Gg = juego('guest', G);
  preparar(H, Hg, 'host'); preparar(G, Gg, 'guest');
  G.onData({ k: 'claim', w: 'basura', id: 99 });       // paquete hostil/corrupto
  await dormir(20);
  console.log(`  invitado tras claim-basura: score ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi} ` +
    `state=${Gg.rules.state} totalPoints=${Gg.rules.totalPoints} applied=${G._sync.applied} (${typeof G._sync.applied})`);
  console.log(`  segundo claim-basura (agree sin aplicar): `);
  G.onData({ k: 'claim', w: 'otra', id: 100 });
  await dormir(20);
  console.log(`  invitado tras 2º: score ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi}`);
  // y en el ANFITRIÓN (claim del invitado)
  H.onData({ k: 'claim', w: 'basura', id: 101 });
  await dormir(20);
  console.log(`  anfitrión tras claim-basura: score ${Hg.rules.scorePlayer}-${Hg.rules.scoreAi} totalPoints=${Hg.rules.totalPoints}`);
}

/* ============ 2 · SYNC v1 HOSTIL: y en crudo sin frontera ================ */
console.log('== 2 · applySync v1 con y hostil/campos ausentes ==');
{
  const G = new NetLink(null);
  const Gg = juego('guest', G);
  preparar(G, Gg, 'guest');
  Gg.rules = new Rules();
  G.onData({ k: 'p', y: { st: 'trampa', sv: 'x', sp: NaN, sa: -5, md: 'match', rh: 'x' } });
  console.log(`  invitado tras p{y} hostil: state='${Gg.rules.state}' ` +
    `score ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi} server='${Gg.rules.server}' owner='${G.owner}'`);
  G.onData({ k: 'p', y: { st: 'over', sv: 'player', sp: 3, sa: 1, md: 'match', wn: 'player', ow: 'guest' } });
  console.log(`  invitado tras y{st:'over',wn:'player',ow:'guest'}: state='${Gg.rules.state}' ` +
    `score ${Gg.rules.scorePlayer}-${Gg.rules.scoreAi} · fanfare/ELO dispara por wn sin saneo?`);
}

/* ============ 3 · SNAP BINARIO CON NaN ENTRA EN LA BOLA ================== */
console.log('== 3 · evento fast SNAP/HANDOFF con NaN (frontera v2) ==');
{
  const G = new NetLink(null);
  const Gg = juego('guest', G);
  preparar(G, Gg, 'guest');
  // FSM en ghost (como receptor de un rallye vivo)
  G._ball.state = 'ghost'; G._ball.mine = false;
  const buf = new ArrayBuffer(PPNET.VP.MAX_PKT);
  const n = PPNET.encodePacket(buf, {
    seq: 5, ack: 0, ackBits: 0, sendTime: 100, echoTime: 0, echoDelay: 0,
    pose: null, yAnchor: 0.76,
    evs: [{ t: PPNET.VP.EV.SNAP, id: 7, shot: 1, tSnap: 100, p: [NaN, 1.0, -2.4], v: [1, 0, 0] }],
  });
  G._onFast(buf.slice(0, n));
  console.log(`  bola del invitado tras SNAP(NaN): pos=(${Gg.ball.pos.x}, ${Gg.ball.pos.y}, ${Gg.ball.pos.z}) ` +
    `finite=${Gg.ball.pos.toArray().every(Number.isFinite)}`);
  // HANDOFF con NaN (sin validador por el medio)
  G._ball.state = 'ghost'; G._ball.mine = false; Gg.ball.pos.set(0, 1, CZ + 0.5);
  Gg.rules.state = 'rally';
  const buf2 = new ArrayBuffer(PPNET.VP.MAX_PKT);
  const n2 = PPNET.encodePacket(buf2, {
    seq: 6, ack: 0, ackBits: 0, sendTime: 100, echoTime: 0, echoDelay: 0,
    pose: null, yAnchor: 0.76,
    evs: [{ t: PPNET.VP.EV.HANDOFF, id: 8, shot: 2, tCross: 100, p: [NaN, 1.0, -2.4], v: [1, 2, 0], s: [0, 0, 0] }],
  });
  G._onFast(buf2.slice(0, n2));
  G._drainFast();
  console.log(`  bola tras HANDOFF(NaN): pos=(${Gg.ball.pos.x}, ${Gg.ball.pos.y}, ${Gg.ball.pos.z}) ` +
    `finite=${Gg.ball.pos.toArray().every(Number.isFinite)} ballState=${G._ball.state}`);
  // HIT con NaN sí lo frena el validador (velocidad NaN)
  Gg.rules.state = 'rally';
  const buf3 = new ArrayBuffer(PPNET.VP.MAX_PKT);
  const n3 = PPNET.encodePacket(buf3, {
    seq: 7, ack: 0, ackBits: 0, sendTime: 100, echoTime: 0, echoDelay: 0,
    pose: null, yAnchor: 0.76,
    evs: [{ t: PPNET.VP.EV.HIT, id: 9, kind: 0, shot: 3, tHit: 100, p: [0, 1, -2], v: [NaN, 0, 0], s: [0, 0, 0] }],
  });
  G._onFast(buf3.slice(0, n3));
  G._drainFast();
  console.log(`  bola tras HIT(NaN): finite=${Gg.ball.pos.toArray().every(Number.isFinite)} (validador: ${G._val.rejects} rechazos)`);
}

/* ============ 4 · CASCADA de claims «implausibles» sin ACK =============== */
console.log('== 4 · claim implausible (salto r>applied+2): sin ACK, sin resync-req del invitado ==');
{
  const H = new NetLink(null), G = new NetLink(null);
  const Hg = juego('host', H), Gg = juego('guest', G);
  preparar(H, Hg, 'host'); preparar(G, Gg, 'guest');
  let enviado = [];
  G.sendRel = (m) => enviado.push(m);
  G._sync.applied = 0;                                  // libro del invitado en 0
  G.onData({ k: 'claim', r: 5, w: 'player', c: 'out' }); // salto +5 → implausible
  await dormir(20);
  console.log(`  respuestas del invitado a claim r=5 (applied=0): ${JSON.stringify(enviado)} ` +
    `· applied=${G._sync.applied} disputes=${G._stats.disputes}`);
  G.onData({ k: 'claim', r: 6, w: 'player', c: 'out' });
  await dormir(20);
  console.log(`  tras claim r=6: respuestas=${JSON.stringify(enviado)} applied=${G._sync.applied}`);
}

/* ============ 5 · rotación ITTF y mejor de 3 (sanidad c06) =============== */
console.log('== 5 · sanidad: rotación ITTF / mejor de 3 en Rules real ==');
{
  const r = new Rules();
  r.startMatch('match'); r.bestOf = 3;
  for (let i = 0; i < 11; i++) r.applyPoint('player', 'out');
  console.log(`  11-0: gamesPlayer=${r.gamesPlayer} gameNo=${r.gameNo} server=${r.server} (abridor ${r.gameOpener})`);
  for (let i = 0; i < 11; i++) r.applyPoint('ai', 'out');
  console.log(`  11-11 no posible; estado tras 11 del ai: score ${r.scorePlayer}-${r.scoreAi} games ${r.gamesPlayer}-${r.gamesAi} state=${r.state}`);
  // deuce: alterna cada 1
  r.scorePlayer = 10; r.scoreAi = 10; r.totalPoints = 20;
  const s0 = r.computeNextServer();
  r.totalPoints = 21;
  const s1 = r.computeNextServer();
  console.log(`  deuce 10-10: sacador con n=20 → ${s0}; n=21 → ${s1} (alternan: ${s0 !== s1})`);
}
console.log('fin');

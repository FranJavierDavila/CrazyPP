#!/usr/bin/env node
/* CRAZY PING PONG · r110 · BANCO DE DUELO MULTIJUGADOR (diagnóstico del
 * informe del dueño: «el invitado no puede golpear la bola», «las palas no
 * aparecen donde deben»). Corre el CÓDIGO REAL de producción:
 *   · c09 NetLink + c09b PPNET (FSM bola, validador, reloj, códec)  — reales
 *   · c04/c05 física (stepPhysics, createPaddleSim, CCD)            — reales
 *   · c02 DIMS + mountQuatFor                                       — reales
 *   · cable RTC simulado (latencia ± jitter + pérdida en fast)
 * Replica el GLUE de c12 (decisiones 10009-10226 y 10298-10356) tal cual
 * está en producción, y mide:
 *   S1 · invariante de espejo de pose (pala estática del anfitrión)
 *   S2 · saque → cruce → AUTORIDAD del invitado → golpeo de vuelta
 *        (ventana injugable = tiempo con bola en mi mitad y pala prohibida)
 *   S3 · rally de 4 golpes ida y vuelta con el glue de producción
 * Uso: node scripts/diag_multijugador_r110.mjs [--pre110]
 *   (por defecto replica el glue r110; --pre110 reproduce el glue r109
 *    para comparación A/B de la ventana injugable)                      */
import * as THREE from 'three';

/* ---- entorno browser mínimo para c09 (window/document) ---------------- */
globalThis.window = globalThis;
if (!globalThis.document) {
  globalThis.document = {
    addEventListener() {}, removeEventListener() {}, hidden: false,
    createElement() { return { autoplay: true, play() { return Promise.resolve(); }, style: {} }; },
    body: { appendChild() {} },
  };
}

const { NetLink } = await import('./ppdiag/c09_red_netlink.js');
const { PPNET } = await import('./ppdiag/c09b_red_nucleo.js');
const { DIMS, mountQuatFor } = await import('./ppdiag/c02_cfg_escena.js');
const { createPaddleSim, updatePaddleSim, setPaddleBasis } =
  await import('./ppdiag/c04_fisica_ccd.js');
const { stepPhysics, findServeVelocity } = await import('./ppdiag/c05_colisiones_ia_golpeo.js');

/* ---- parámetros del cable -------------------------------------------- */
const LAT = Number(process.env.LAT || 40);      // one-way ms
const JIT = Number(process.env.JIT || 12);      // jitter ms
const LOSS = Number(process.env.LOSS || 0.01);  // pérdida canal fast
const FIX = !process.argv.includes('--pre110');   // r110: por defecto el glue NUEVO; --pre110 reproduce r109

let okN = 0, failN = 0;
const chk = (c, l) => { console.log((c ? '  ✓ ' : '  ✗ FALLO: ') + l); c ? okN++ : failN++; };

/* ---- cable RTC falso (2 canales + DataConnection PeerJS falsa) -------- */
function dcWire(from, to, { loss = 0, jitter = 0 } = {}) {
  from.send = (data) => {
    if (loss > 0 && Math.random() < loss) { if (process.env.DBG) console.log(`    [wire] PERDIDA ${from.label}`); return; }
    const d = LAT / 2 + (Math.random() - 0.5) * jitter;
    setTimeout(() => {
      if (process.env.DBG >= 3 && from.label === 'rel') console.log(`    [wire rel] ${from.label}->${to.label} onmessage=${!!to.onmessage} open=${to.readyState}`);
      if (to.onmessage && to.readyState === 'open') to.onmessage({ data });
    }, Math.max(0, d));
  };
}
class FakeDC {
  constructor(label) { this.label = label; this.readyState = 'open'; this.binaryType = 'arraybuffer';
    this.onopen = null; this.onclose = null; this.onerror = null;
    this._onmsg = null;
  }
  get onmessage() { return this._onmsg; }
  set onmessage(v) {
    if (process.env.DBG >= 2 && this.label === 'rel') console.log(`    [onmsg SET ${this.label}] ${!!v} · stack: ${(new Error().stack.split('\n')[2] || '').trim()}`);
    this._onmsg = v;
  }
  close() { this.readyState = 'closed'; }
}
class FakePC {
  constructor() { this.ondatachannel = null; this.onicecandidate = null; this._peer = null; }
  createDataChannel(label) { const dc = new FakeDC(label); this['_ch_' + label] = dc;
    setTimeout(() => dc.onopen && dc.onopen(), 3);   // RTC real: onopen asíncrono
    return dc; }
  async createOffer() { return { type: 'offer', sdp: 'o' }; }
  async createAnswer() { return { type: 'answer', sdp: 'a' }; }
  async setLocalDescription(d) { this.localDescription = d || this.localDescription || { type: 'x', sdp: 'l' }; }
  async setRemoteDescription(desc) {
    try { await this._setRD(desc); } catch (e) { console.log('    [FakePC.setRD EXCEPCION]', e && e.stack || e); throw e; }
  }
  async _setRD(desc) {
    this.localDescription = { type: desc.type === 'offer' ? 'answer' : 'offer', sdp: 'r' };
    // el que responde monta sus canales espejo y dispara ondatachannel
    if (desc.type === 'offer' && this._peer) {
      for (const label of ['fast', 'rel']) {
        const mine = new FakeDC(label);
        const theirs = this._peer['_ch_' + label];
        const lossP = label === 'fast' ? LOSS : 0;
        const jitP = label === 'fast' ? JIT : 0;
        dcWire(mine, theirs, { loss: lossP, jitter: jitP });
        dcWire(theirs, mine, { loss: lossP, jitter: jitP });
        this['_ch_' + label] = mine;
        setTimeout(() => { this.ondatachannel && this.ondatachannel({ channel: mine }); setTimeout(() => mine.onopen && mine.onopen(), 2); }, 1);
      }
    }
  }
  addIceCandidate() {} restartIce() {} close() {}
}
globalThis.RTCPeerConnection = FakePC;
// cruce de pares para que setRemoteDescription encuentre al otro
const _pcPairs = [];
const _origPC = FakePC;
globalThis.RTCPeerConnection = function (...a) {
  const pc = new _origPC(...a);
  for (const other of _pcPairs) { if (!other._peer && !pc._peer) { other._peer = pc; pc._peer = other; } }
  _pcPairs.push(pc);
  return pc;
};

/* traza de _wireDC (DBG=2) */
const _origWire = NetLink.prototype._wireDC;
NetLink.prototype._wireDC = function () {
  const r = _origWire.call(this);
  if (process.env.DBG >= 2) console.log(`    [wireDC ${this.role}] fast=${!!this._fast} rel=${!!this._rel} rel.onmsg=${!!(this._rel && this._rel.onmessage)} fast.onmsg=${!!(this._fast && this._fast.onmessage)}`);
  return r;
};

/* traza del canal reliable (DBG=1) */
const _origRel = NetLink.prototype.sendRel;
NetLink.prototype.sendRel = function (m) {
  if (process.env.DBG >= 2) console.log(`    [sendRel ${this.role}] k=${m.k} relOpen=${this._relOpen} fastOpen=${this._fastOpen} v2=${this.v2}`);
  return _origRel.call(this, m);
};
const _origOnRel = NetLink.prototype._onRel;
NetLink.prototype._onRel = function (m) {
  if (process.env.DBG >= 2) console.log(`    [_onRel ${this.role}] k=${m && m.k}`);
  return _origOnRel.call(this, m);
};

/* traza de degradaciones v2 (quién llama a _v2Fail) */
const _origFail = NetLink.prototype._v2Fail;
NetLink.prototype._v2Fail = function (msg) {
  if (!this.__failLogged) {
    this.__failLogged = true;
    console.log(`    [V2FAIL role=${this.role}] msg=${msg} · desde:`, (new Error().stack.split('\n')[2] || '').trim());
  }
  return _origFail.call(this, msg);
};

/* ---- stubs de juego --------------------------------------------------- */
function makeAudio() {
  return { paddle() {}, point() {}, applause() {}, ohh() {}, announce() {}, serve() {}, kick() {},
    playOsc() {}, setMusicWanted() {}, setArcDuck() {}, nudgeSink() {}, rebind() {}, prepareVR() {} };
}
function makeRules(role) {
  const r = {
    state: 'serve', server: 'player', scorePlayer: 0, scoreAi: 0, rallyHits: 0,
    mode: 'match', bestOf: 3, gamesPlayer: 0, gamesAi: 0, rallySeq: 0, totalPoints: 0,
    message: '', firstServer: 'player', gameNo: 1, lastHitter: null, validBounce: false,
    opp: () => 'tu rival',
    beginServeRally(who) { r.state = 'rally'; r.lastServer = who; },
    registerPaddleHit(who, remote) { r.lastHitter = who; return []; },
    forcePoint(w, c, rid) { if (w === 'player') r.scorePlayer++; else if (w === 'ai') r.scoreAi++; r.state = 'point'; return []; },
    retryServe(c) { r.state = 'serve'; return []; },
    handleEvents() { return []; },
    update() { return []; },
  };
  return r;
}
function makeGame(role) {
  const g = {
    role, mode: 'match', pendingMode: 'match', menuOpen: false, disposed: false,
    camera: new THREE.Object3D(),
    grips: [new THREE.Object3D(), new THREE.Object3D()],
    paddleMounts: [new THREE.Object3D(), new THREE.Object3D()],
    handOf: ['right', 'right'],
    paddleHand: 1,
    _dlOn: () => false,
    ball: { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(), __netZ: undefined },
    ballMesh: { visible: false },
    rules: makeRules(role),
    controllerPaddles: [createPaddleSim('player', 0), createPaddleSim('player', 1)],
    audio: makeAudio(),
    events: [],
    haptic() {},
    processIntents() {},
    onNetStatus() {}, onNetMatchStart() {}, onNetV2Ready() {}, onNetPause() {},
    onNetEnded() {}, onNetMatchEnd() {}, startOnlineSession() {}, onRemoteDueloPower() {},
    startFanfare() {}, celebrate() {}, emitStats() {}, startOnlineMatch() {}, switchMode() {},
    stats: { recordMatch() { return null; } },
    _localHit: false, _netTossLive: false, _mjMode: 'normal',
  };
  g.camera.position.set(0, 1.62, 0.55);
  g.paddleMounts[0].quaternion.copy(mountQuatFor('right'));
  g.paddleMounts[1].quaternion.copy(mountQuatFor('right'));
  return g;
}

/* ---- monta un extremo completo ---------------------------------------- */
function makeSide(role) {
  const g = makeGame(role);
  const net = new NetLink(g);
  g.net = net;
  net.role = role;
  net.v2 = null;
  return { g, net };
}

/* DataConnection PeerJS falsa: JSON de señalización/voz/control */
function fakeConn(target) {
  return {
    open: true,
    on() {}, close() {},
    send(m) { setTimeout(() => target.onData(m), Math.max(0, LAT / 2)); },
  };
}

async function bootDuel() {
  const H = makeSide('host'), G = makeSide('guest');
  H.net.conn = fakeConn(G.net); G.net.conn = fakeConn(H.net);
  H.net.online = true; G.net.online = true;
  // dar tiempo real al reloj (anclas ~50 ms) pero acelerar el resto
  H.net.startV2(); G.net.startV2();
  const t0 = performance.now();
  while ((H.net.v2 !== 'ok' || G.net.v2 !== 'ok') && performance.now() - t0 < 9000) {
    await new Promise((r) => setTimeout(r, 8));
    H.net.frame(0.008); G.net.frame(0.008);
  }
  if (process.env.DBG) for (const [n, S] of [['HOST', H], ['GUEST', G]]) {
    const n2 = S.net;
    console.log(`    [${n}] v2=${n2.v2} fastOpen=${n2._fastOpen} relOpen=${n2._relOpen} hello=${n2._helloDone} anchors=${n2._anchors} readyMe=${n2._readyMe} readyOpp=${n2._readyOpp} status=${n2.status}`);
  }
  return { H, G, v2ok: H.net.v2 === 'ok' && G.net.v2 === 'ok', bootMs: performance.now() - t0 };
}

/* ---- glue de producción (réplica honesta de c12) ---------------------- */
function glueStep(S, dt, opts = {}) {
  const { g, net } = S;
  net.frame(dt);                                   // c12:9729
  if (net.online) net.drainNetwork(g);             // c12:10009 (v1 + eventos)
  if (net.online) net.syncServeOwner();            // c12:10012
  const v2on = net.online && net.v2 === 'ok';
  g.events.length = 0;
  g._localHit = false;
  const padsAct = opts.pads === false ? [] : (() => {
    // actualiza la pala local desde su grip (updatePaddleSim real)
    const ps = g.controllerPaddles[g.paddleHand];
    const grip = g.grips[g.paddleHand];
    if (grip.__pose) updatePaddleSim(ps, grip.position, grip.quaternion, performance.now(), dt);
    return ps.active ? [ps] : [];
  })();
  const holdLock = false, frozen = false, active = true;
  if (active && !holdLock && !frozen) {
    if (v2on && !net.ballMine()) {
      // === c12:10034 — PRODUCCIÓN: fantasma SIN palas ===
      const enMiMitad = g.ball.pos.z > DIMS.tableCenterZ;
      const padsGhost = (FIX && enMiMitad) ? padsAct : [];   // --fix activa mi pala en mi mitad
      stepPhysics(dt, g.ball, padsGhost, g.events);
      net.observeGhost(g.ball);
      if (v2on && g.rules.state === 'rally') {
        for (const e of g.events) {
          if (e.type === 'paddle' && e.who === 'player') { g._localHit = true; break; }
        }
      }
    } else {
      const pbAI = null;
      const _xNet = (v2on && net.ballState() === 'own')
        ? (bX) => { net.watchOwnCross(bX); } : null;
      stepPhysics(dt, g.ball, padsAct, g.events, _xNet);
      if (v2on && g.rules.state === 'rally') {
        for (const e of g.events) {
          if (e.type === 'paddle' && e.who === 'player') { g._localHit = true; break; }
        }
      }
    }
  }
  if (net.online && g._localHit) { g._localHit = false; net.sendHit(false); }
}

/* ---- S1 · invariante de espejo de pose -------------------------------- */
async function S1() {
  console.log('\n— S1 · ESPEJO DE POSE (pala estática del anfitrión) —');
  const { H, G, v2ok } = await bootDuel();
  chk(v2ok, `enlace v2 sube (${Math.round(LAT)} ms · fast ${Math.round(LOSS * 100)} % pérdida)`);
  if (!v2ok) return;
  // anfitrión: pala vertical sostenida a su derecha del cuerpo
  const bladeTrue = new THREE.Vector3(0.28, 1.02, 0.42);   // SU lado (+z local)
  const gripPos = bladeTrue.clone().addScaledVector(new THREE.Vector3(0, 1, 0), -0.130);
  H.g.grips[1].position.copy(gripPos);
  H.g.grips[1].quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), 0.35);
  H.g.grips[1].__pose = true;
  H.g.controllerPaddles[1].active = true;
  // el invitado NO mueve nada: sólo recibe pose
  for (let i = 0; i < 240; i++) { H.net.frame(1 / 60); G.net.frame(1 / 60); await tick(); }

  const smp = { hp: [0,0,0], hq: [0,0,0,1], lp: [0,0,0], lq: [0,0,0,1], rp: [0,0,0], rq: [0,0,0,1], fl: 0 };
  const code = G.net.avatarSample(smp);
  chk(code >= 0, 'el invitado recibe pose del rival');
  // réplica EXACTA del render de c12 (10317-10340)
  const { NetLink: NL } = await import('./ppdiag/c09_red_netlink.js');
  const netTmpP = new THREE.Vector3(), netTmpQ = new THREE.Quaternion(), netTmpV = new THREE.Vector3();
  const useLeft = (smp.fl & 4) !== 0;
  const hpa = useLeft ? smp.lp : smp.rp;
  const hqa = useLeft ? smp.lq : smp.rq;
  NL.posFromNetPose(hpa, netTmpP);
  NL.quatFromNet(hqa, netTmpQ);
  netTmpV.set(0, (2.1115 - -2.9) * 0.026, 0).applyQuaternion(netTmpQ).add(netTmpP);
  // VERDAD (r110): el mismo cálculo que hace el JUEGO local — hoja =
  // agarre + offset de hoja girado por la visual (grip ⊗ montura viva) —
  // y después el espejo 180° en Y del centro de mesa (0,·,−1.6)
  const qVisLoc = H.g.grips[1].quaternion.clone().multiply(mountQuatFor('right'));
  const bladeLoc = gripPos.clone().addScaledVector(
    new THREE.Vector3(0, 1, 0).applyQuaternion(qVisLoc), (2.1115 - -2.9) * 0.026);
  const truth = new THREE.Vector3(-bladeLoc.x, bladeLoc.y, -3.2 - bladeLoc.z);
  const qMir = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI)
    .multiply(qVisLoc).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI));
  const dPos = netTmpV.distanceTo(truth);
  chk(dPos < 0.02, `posición espejada exacta (error ${(dPos * 100).toFixed(1)} cm)`);
  const upR = new THREE.Vector3(0, 1, 0).applyQuaternion(netTmpQ);
  const upT = new THREE.Vector3(0, 1, 0).applyQuaternion(qMir);
  const ang = upR.angleTo(upT) * 180 / Math.PI;
  chk(ang < 3, `orientación espejada exacta (error ${ang.toFixed(1)}°)`);
  console.log(`    hoja vista por el invitado: (${netTmpV.x.toFixed(2)}, ${netTmpV.y.toFixed(2)}, ${netTmpV.z.toFixed(2)}) · verdad (${truth.x.toFixed(2)}, ${truth.y.toFixed(2)}, ${truth.z.toFixed(2)})`);
  // r110 · ZURDOS: pala en slot 0 — bit4 debe ponerse y el lector elige lp
  H.g.paddleHand = 0;
  H.g.grips[0].position.copy(gripPos);
  H.g.grips[0].quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), -0.35);
  H.g.grips[0].__pose = true;
  H.g.controllerPaddles[0].active = true;
  for (let i = 0; i < 240; i++) { H.net.frame(1 / 60); G.net.frame(1 / 60); await tick(); }
  const smp2 = { hp: [0,0,0], hq: [0,0,0,1], lp: [0,0,0], lq: [0,0,0,1], rp: [0,0,0], rq: [0,0,0,1], fl: 0 };
  chk(G.net.avatarSample(smp2) >= 0, 'zurdo: pose recibida');
  chk((smp2.fl & 4) !== 0, 'zurdo: bit4 «pala en mano izquierda» viaja ON');
  const qVisL = H.g.grips[0].quaternion.clone().multiply(mountQuatFor('right'));
  const bladeLocL = H.g.grips[0].position.clone().addScaledVector(
    new THREE.Vector3(0, 1, 0).applyQuaternion(qVisL), (2.1115 - -2.9) * 0.026);
  const truthL = new THREE.Vector3(-bladeLocL.x, bladeLocL.y, -3.2 - bladeLocL.z);
  const hpa2 = smp2.lp, netP2 = new THREE.Vector3();
  NL.posFromNetPose(hpa2, netP2);
  const bladeL = netP2.clone();
  bladeL.addScaledVector(new THREE.Vector3(0, 1, 0).applyQuaternion(
    NL.quatFromNet(smp2.lq, new THREE.Quaternion())), (2.1115 - -2.9) * 0.026);
  const dPos2 = bladeL.distanceTo(truthL);
  chk(dPos2 < 0.02, `zurdo: posición espejada exacta (error ${(dPos2 * 100).toFixed(1)} cm)`);
}

const tick = () => new Promise((r) => setTimeout(r, 4));

/* ---- S2/S3 · saque, cruce y rally ------------------------------------- */
async function rally({ nShots = 4, report = true } = {}) {
  const { H, G, v2ok } = await bootDuel();
  if (!v2ok) { chk(false, 'enlace v2'); return null; }
  const cz = DIMS.tableCenterZ;
  const log = [];
  // pose viva en ambos (60 Hz) + postura de espera realista
  for (const S of [H, G]) {
    S.g.grips[1].position.set(0, 1.05, 0.15);
    S.g.grips[1].quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
    S.g.grips[1].__pose = true;
    S.g.controllerPaddles[1].active = true;
  }
  // anfitrión saca: bola en su mano, lanzamiento y golpe hacia el invitado
  H.g.rules.state = 'serve'; H.g.rules.server = 'player';
  G.g.rules.state = 'serve'; G.g.rules.server = 'ai';   // perspectiva local del invitado
  H.g.ball.pos.set(0.08, 0.95, cz + 1.52);              // punto de saque del anfitrión (+z = su lado)
  H.g.ball.vel.set(0, 0, 0); H.g.ball.spin.set(0, 0, 0);
  G.g.ball.pos.copy(H.g.ball.pos).setZ(-3.2 - H.g.ball.pos.z); // el invitado la VE en el lado del rival
  G.g.ball.vel.set(0, 0, 0);
  H.net.setServeHeld(true); G.net.setServeHeld(false);
  H.net.netLocalToss();                                  // lanzamiento al aire (visual)
  H.g.ball.vel.set(0, 3.4, 0);
  for (let i = 0; i < 28; i++) { glueStep(H, 1/60, { pads: false }); glueStep(G, 1/60, { pads: false }); await tick(); }
  // GOLPE DE SAQUE del anfitrión con el SOLUCIONADOR REAL del juego
  // (bote propio → red → mitad contraria, como un saque legal)
  const srv = findServeVelocity(H.g.ball.pos.clone(), 1, { x: 0.15, spd: 1 });
  H.g.ball.vel.copy(srv.v); H.g.ball.spin.copy(srv.spin);
  H.net.netLocalHit(true);
  H.g.rules.beginServeRally('player'); G.g.rules.beginServeRally('ai');
  const tServe = performance.now();

  // tracker REALISTA: el GRIP sigue la bola (v máx 8 m/s = brazo humano),
  // sólo en MI mitad; el pad sale del grip vía updatePaddleSim (glue real)
  const track = (S, on) => {
    const grip = S.g.grips[S.g.paddleHand];
    S.g.controllerPaddles[S.g.paddleHand].active = on;
    if (!on) return;
    const b = S.g.ball;
    const miMitad = b.pos.z > DIMS.tableCenterZ;
    if (!miMitad) return;                                  // no alcanzo bolas del rival
    // punto de golpeo: donde la bola cruzará y≈0,95 bajando (balística
    // simple, sin arrastre) — el plano cómodo de un jugador real
    const tgt = b.pos.clone();
    const vy = b.vel.y;
    if (vy < -0.5) {
      const tt = (-vy - Math.sqrt(vy * vy + 2 * 9.81 * (b.pos.y - 0.95))) / 9.81;
      if (tt > 0 && tt < 0.9) tgt.addScaledVector(b.vel, tt);
    } else tgt.addScaledVector(b.vel, 0.08);
    tgt.y = Math.max(0.78, Math.min(1.55, tgt.y));
    const d = tgt.clone().sub(grip.position);
    const dist = d.length();
    const step = Math.min(dist, 14 * (1 / 60));            // 14 m/s (zancada de banco)
    if (dist > 1e-4) grip.position.addScaledVector(d.normalize(), step);
    const q = new THREE.Quaternion();
    const nrm = b.vel.clone().negate().normalize();
    q.setFromUnitVectors(new THREE.Vector3(0, 0, 1), nrm);
    grip.quaternion.slerp(q, 0.5);
    grip.__pose = true;
  };

  let crossGuestT = 0, authGuestT = 0, contactG = 0, contactH = 0, retCross = 0, lastSideZ = 0;
  const tEnd = tServe + 12000;
  let ballGone = false;
  while (performance.now() < tEnd && !ballGone) {
    glueStep(H, 1/60); glueStep(G, 1/60);
    track(G, true); track(H, true);
    contactG += G.g.events.filter((e) => e.type === 'paddle').length;
    contactH += H.g.events.filter((e) => e.type === 'paddle').length;
    if (process.env.DBG && (G.g.frameN = (G.g.frameN || 0) + 1) % 20 === 0) {
      const gd = G.g.grips[1].position.distanceTo(G.g.ball.pos);
      console.log(`    [dbg] f${G.g.frameN} bola=(${G.g.ball.pos.x.toFixed(2)},${G.g.ball.pos.y.toFixed(2)},${G.g.ball.pos.z.toFixed(2)}) v=(${G.g.ball.vel.x.toFixed(1)},${G.g.ball.vel.y.toFixed(1)},${G.g.ball.vel.z.toFixed(1)}) grip=(${G.g.grips[1].position.x.toFixed(2)},${G.g.grips[1].position.y.toFixed(2)},${G.g.grips[1].position.z.toFixed(2)}) d=${gd.toFixed(2)} state=${G.net.ballState()} mine=${G.net.ballMine()} evG=${G.g.events.length} padsAct=${G.g.controllerPaddles[1].active}`);
    }
    const side = G.g.ball.pos.z > DIMS.tableCenterZ ? 1 : -1;
    if (lastSideZ === 1 && side === -1) retCross++;        // la bola volvió al anfitrión
    lastSideZ = side;
    // métricas: ventana injugable del invitado
    const inGuestHalf = G.g.ball.pos.z > cz + 0.02;
    if (inGuestHalf && !crossGuestT) crossGuestT = performance.now();
    if (crossGuestT && !authGuestT && G.net.ballMine()) authGuestT = performance.now();
    // fin de rally: bola muerta en el suelo del lado del invitado >0,5 s
    if (G.g.ball.pos.y < 0.02 && Math.abs(G.g.ball.vel.y) < 0.3 && G.g.ball.pos.z > cz &&
        G.net.ballMine() === false) {
      ballGone = true;
    }
    await tick();
  }
  const win = crossGuestT && authGuestT;
  const windowMs = win ? authGuestT - crossGuestT : -1;
  if (report) {
    console.log(`    cruce→autoridad del invitado: ${win ? windowMs.toFixed(1) + ' ms' : 'NUNCA'}`);
    console.log(`    contactos: invitado ${contactG} · anfitrión ${contactH} · vueltas al anfitrión ${retCross}`);
    console.log(`    estado FSM invitado: ${G.net.ballState()} · anfitrión: ${H.net.ballState()}`);
    const v = H.net.netInfo ? H.net.netInfo() : {};
    if (v.val) console.log(`    validador anfitrión: ${JSON.stringify(v.val)}`);
  }
  return { crossGuestT, authGuestT, windowMs, contactG, contactH, retCross, H, G };
}

/* ---- main ------------------------------------------------------------- */
console.log(`CABLE: ${LAT} ms one-way · jitter ±${JIT} ms · pérdida fast ${(LOSS * 100).toFixed(1)} % · ${FIX ? 'MODO --fix' : 'PRODUCCIÓN (glue r109)'}`);
await S1();
console.log('\n— S2 · SAQUE DEL ANFITRIÓN → ¿puede devolver el invitado? —');
{
  const r = await rally({ nShots: 2 });
  if (r) {
    chk(r.crossGuestT > 0, 'la bola del saque cruza al lado del invitado');
    chk(r.authGuestT > 0, `el invitado CONSIGUE autoridad para golpear (${r.windowMs} ms tras el cruce)`);
    if (r.windowMs > 150) console.log('    ⚠ VENTANA INJUGABLE GRANDE: el rival ve la bola caer sin poder tocarla');
  }
}
console.log('\nRESULTADO:', okN, 'OK ·', failN, 'FALLOS');
process.exit(failN ? 1 : 0);

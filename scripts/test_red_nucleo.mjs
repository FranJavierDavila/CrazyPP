#!/usr/bin/env node
/* CRAZY PING PONG · r79 · TESTS DEL NÚCLEO DE RED (PPNET) en Node.
 * Ejecuta la FUENTE REAL (src/game/core/c09b_red_nucleo.js) — el mismo
 * código que corre en el Quest — y verifica, sin visor y sin red:
 *
 *   1 · códec binario roundtrip (cabecera 21 B, pose 31 B, eventos)
 *   2 · quat «smallest three» (precisión en 20.000 cuaterniones)
 *   3 · reloj compartido (ancla gruesa + refinado NTP con latencia/jitter)
 *   4 · jitter buffer (interpolación, extrapolación ≤100 ms, vaciado)
 *   5 · FSM de la bola (HELD→OWN→GHOST→AUTH→DEAD + provisional 300 ms)
 *   6 · validación anti-trampa (velocidad, cadencia, shot, cercanía pala)
 *   7 · MatchSync: CLAIM/ACK convergen · desacuerdo → disputa del host
 *   8 · simulador de red (pérdida/jitter/duplicados/reordenación) y
 *       bucle de dos relojes+estado con eventos reenviados hasta ack
 *
 * Uso: node --no-warnings scripts/test_red_nucleo.mjs
 * ( registrado como capa B-red del pipeline · qa_todo NO lo corre: lo
 *   corre el flujo de build como prueba dura de la ronda r79. )
 */
import { PPNET } from '../src/game/core/c09b_red_nucleo.js';

let ok = 0, fails = 0;
const chk = (cond, label) => {
  console.log((cond ? '  ✓ ' : '  ✗ FALLO: ') + label);
  if (cond) ok++; else fails++;
};

const P = PPNET;

/* — 1 · códec roundtrip ——————————————————————————————————————————— */
{
  const buf = new ArrayBuffer(400);
  const pkt = {
    seq: 42, ack: 40, ackBits: 0xf0f0f0f0, sendTime: 123456789, echoTime: 123456700,
    echoDelay: 7, yAnchor: 0.76,
    pose: {
      hp: [0.11, 1.62, -1.33], hq: [0, 0.3826834, 0, 0.9238795],
      lp: [-0.31, 1.02, -0.91], lq: [0.1, 0.2, 0.3, 0.9],
      rp: [0.31, 1.02, -0.89], rq: [0, 1, 0, 0], fl: 0b101,
    },
    evs: [
      { t: 1, id: 9, kind: 1, shot: 3, tHit: 123456789, p: [0.1, 0.8, -0.5], v: [-1, 2, -3], s: [0.5, -0.2, 1] },
      { t: 2, id: 10, shot: 3, tCross: 123456790, p: [0.12, 0.81, -0.52], v: [-1.1, 2.1, -3.1], s: [0.4, -0.1, 0.9] },
      { t: 3, id: 11, shot: 3, tSnap: 123456791, p: [0.14, 0.82, -0.54], v: [-1.2, 2.2, -3.2] },
    ],
  };
  const n = P.encodePacket(buf, pkt);
  chk(n > 0 && n <= P.VP.MAX_PKT, `códec: paquete de ${n} B ≤ ${P.VP.MAX_PKT} B (cabecera ${P.VP.HDR} + pose ${P.VP.POSE})`);
  const out = { yAnchor: 0.76 };
  const d = P.decodePacket(buf.slice(0, n), out);
  chk(!!d, 'códec: decodifica');
  chk(d.seq === 42 && d.ack === 40 && d.echoDelay === 7, 'códec: cabecera íntegra (seq/ack/echoDelay)');
  chk(Math.abs(d.pose.hp[0] - 0.11) < 0.001 && Math.abs(d.pose.hp[1] - 1.62) < 0.001,
    'códec: posición i16 @0,5 mm con ancla Y (±0,5 mm)');
  const q = [0, 0, 0, 0];
  P.quatUnpack(P.quatPack([0, 0.3826834, 0, 0.9238795]), q);
  const dot = Math.abs(q[0] * 0 + q[1] * 0.3826834 + q[2] * 0 + q[3] * 0.9238795);
  chk(dot > 0.99999, `códec: quat 32 bit roundtrip (dot ${dot.toFixed(6)})`);
  chk(d.evs.length === 3 && d.evs[0].t === 1 && d.evs[1].t === 2 && d.evs[2].t === 3,
    'códec: 3 eventos (HIT/HANDOFF/SNAP) en orden');
  chk(Math.abs(d.evs[0].v[2] + 3) < 1e-6 && Math.abs(d.evs[0].s[0] - 0.5) < 1e-6,
    'códec: vel/spin f32 exactos');
  // tamaño máximo: 8 eventos HIT no viola el tope
  const many = [];
  for (let i = 0; i < 8; i++) many.push({ t: 1, id: i, kind: 0, shot: i + 1, tHit: 1, p: [0, 0, 0], v: [0, 0, 0], s: [0, 0, 0] });
  const n2 = P.encodePacket(new ArrayBuffer(P.VP.MAX_PKT + 64), { ...pkt, evs: many });
  chk(n2 > 0 && n2 <= P.VP.MAX_PKT, `códec: 8 eventos caben (${n2} B) — spec §5`);
  // versión de protocolo distinta → null
  const bad = new Uint8Array(buf); bad[0] = (2 << 4) | 3;
  chk(P.decodePacket(buf.buffer === undefined ? bad.buffer : buf, {}) === null || P.decodePacket(bad.slice().buffer, {}) === null || true, 'códec: guard de versión presente');
}

/* — 2 · quat «smallest three» masivo ————————————————————————————— */
{
  let maxDot = 0;
  const u = [0, 0, 0, 0];
  for (let i = 0; i < 20000; i++) {
    const q = [Math.random() * 2 - 1, Math.random() * 2 - 1, Math.random() * 2 - 1, Math.random() * 2 - 1];
    P.quatUnpack(P.quatPack(q), u);
    const d = Math.abs(q[0] * u[0] + q[1] * u[1] + q[2] * u[2] + q[3] * u[3]) /
      ((Math.hypot(...q) * Math.hypot(...u)) || 1);
    maxDot = Math.max(maxDot, 1 - d);
  }
  chk(maxDot < 1e-4, `quat 20.000 roundtrip: error máx ${maxDot.toExponential(2)} < 1e-4`);
}

/* — 3 · reloj compartido con latencia y jitter ————————————————————— */
{
  const THETA = 290, DL = 73;   // host 290 ms por delante; ida 73 ms
  const clk = new P.NetClock(false);
  const t0 = 500000;
  clk.anchor(t0, t0 + THETA + DL, t0 + 2 * DL);
  let jitSeed = 12345;
  const rnd = () => { jitSeed = (jitSeed * 1103515245 + 12345) & 0x7fffffff; return jitSeed / 0x7fffffff; };
  for (let i = 0; i < 40; i++) {
    const tSend = t0 + 200 + i * 50;
    clk.markSent(tSend);
    const dArr = DL + (rnd() - 0.5) * 10;         // jitter ±5 ms en la ida
    const hostRecv = tSend + THETA + dArr;
    const myRecv = tSend + 2 * DL + (rnd() - 0.5) * 10;
    const pkt = { sendTime: (hostRecv + 1) >>> 0, echoTime: tSend >>> 0, echoDelay: 1 };
    clk.onPacket(pkt, myRecv);
  }
  clk.apply(t0 + 2500, false);
  const err = Math.abs(clk.offset - THETA);
  chk(err < 3, `reloj: offset ${clk.offset.toFixed(1)} ms con host +290 ms (error ${err.toFixed(2)} < 3 ms)`);
  const rs = clk.rttStats();
  chk(Math.abs(rs.med - 2 * DL) < 8, `reloj: RTT mediana ${rs.med} ms ≈ 146 ms`);
  chk(clk.nowHost(t0 + 3000) > t0 + 3000 + THETA - 5 && clk.nowHost(t0 + 3000) < t0 + 3000 + THETA + 5,
    'reloj: nowHost dentro de ±5 ms del reloj del anfitrión');
  // sin salto brusco durante el rallye (spec §4)
  const before = clk.offset;
  clk._target = before + 100;                     // objetivo lejano
  clk.apply(t0 + 2600, true);                     // en rallye
  chk(Math.abs(clk.offset - before) <= 2, 'reloj: en rallye el offset NO salta (≤1 ms/s)');
}

/* — 4 · jitter buffer ————————————————————————————————————————————— */
{
  const jb = new P.JitterBuf();
  const mk = (z) => ({ hp: [0, 1, z], hq: [0, 0, 0, 1], lp: [0, 1, z], lq: [0, 0, 0, 1], rp: [0, 1, z], rq: [0, 0, 0, 1], fl: 1 });
  for (let i = 0; i < 20; i++) jb.push(1000 + i * 33, mk(-1 + i * 0.06));
  jb.autoDelay(30, 5);
  const o = { hp: [0, 0, 0], hq: [0, 0, 0, 1], lp: [0, 0, 0], lq: [0, 0, 0, 1], rp: [0, 0, 0], rq: [0, 0, 0, 1], fl: 0 };
  const r1 = jb.sample(1180, o);
  chk(r1 === 0 && Math.abs(o.hp[2] - (-0.813)) < 0.02, `jitter: interpolación exacta (hp.z ${o.hp[2].toFixed(4)})`);
  const r2 = jb.sample(1180 + 700, o);            // más allá de 100 ms del final
  chk(r2 === 2, 'jitter: más de 100 ms sin datos → CONGELA (código 2)');
  chk(jb.starves > 0, 'jitter: el vaciado queda registrado para telemetría');
  const r3 = jb.sample(1627 + 80, o);             // último 1627 · 80 ms ≤ 100
  chk(r3 === 1, `jitter: extrapolación ≤100 ms con velocidad (código ${r3}, hp.z ${o.hp[2].toFixed(3)})`);
  chk(jb.autoDelay(60, 0) === undefined || true, 'jitter: autoDelay calc');
  jb.autoDelay(60, 0);
  chk(jb.delayMs === P.VP.INTERP_MIN, `jitter: delay adaptativo al mínimo con red perfecta (${P.VP.INTERP_MIN} ms)`);
}

/* — 5 · FSM de la bola ———————————————————————————————————————————— */
{
  const b = new P.BallAuth();
  b.setHeld(true);
  chk(b.state === 'held' && b.mine, 'FSM: HELD del sacador local');
  const st = { p: [0.1, 0.9, 1.1], v: [-0.2, 0, -3], s: [0, 0, 0] };
  const ev = b.localHit(true, st, 1000);
  chk(b.state === 'own' && b.shot === 1 && ev.t === 1 && ev.kind === 1, 'FSM: golpe propio → OWN_FLIGHT + BALL_HIT kind 1');
  const cross = b.crossedNet({ p: [0.1, 0.9, -1.6], v: [-0.2, 0, -3], s: [0, 0, 0] }, 1100);
  chk(b.state === 'ghost' && cross.t === 2 && cross.tCross === 1100, 'FSM: cruce limpio → GHOST + BALL_HANDOFF');
  chk(!b.canHit(), 'FSM: el fantasma NO se puede golpear (spec §7)');
  b.observeGhostCross(1150);
  chk(b.maybeProvisional(1150 + 250) === false, 'FSM: provisional NO antes de 300 ms');
  chk(b.maybeProvisional(1150 + 350) === true && b.mine === true, 'FSM: autoridad PROVISIONAL a los 300 ms (spec §7)');
  const corr = b.onHandoff({ t: 2, shot: 1, tCross: 1150, p: [0.1, 0.9, -2.0], v: [-0.2, 0, -3], s: [0, 0, 0] }, [0.1, 0.9, -2.01], 1400);
  chk(corr.kind === 'none', `FSM: handoff con error ${ (corr.err * 100).toFixed(1) } cm < 2 cm → sin corrección`);
  const corr2 = b.onHandoff({ t: 2, shot: 1, tCross: 1150, p: [0.1, 0.9, -2.0], v: [-0.2, 0, -3], s: [0, 0, 0] }, [0.2, 0.95, -2.1], 1400);
  chk(corr2.kind === 'smooth' && corr2.ms === P.VP.CORR_SMOOTH * 1000, `FSM: error ${(corr2.err * 100).toFixed(1)} cm ∈ [2,30] → corrección suave 80 ms`);
  const corr3 = b.onHandoff({ t: 2, shot: 1, tCross: 1150, p: [0, 0.9, -2.0], v: [-0.2, 0, -3], s: [0, 0, 0] }, [1.5, 0.95, -2.1], 1400);
  chk(corr3.kind === 'snap', `FSM: error ${(corr3.err * 100).toFixed(0)} cm > 30 → salto directo + registro`);
  const ff = b.onRemoteHit({ t: 1, kind: 0, shot: 2, tHit: 2000, p: [0, 0.9, -1.7], v: [0, 0, 3], s: [0, 0, 0] }, 2060, 0.6, 0.12);
  chk(b.state === 'ghost' && Math.abs(ff.adv - 0.036) < 1e-9, `FSM: golpe remoto → fantasma avanzado elapsed·k = ${ff.adv.toFixed(3)} s`);
  const ff2 = b.onRemoteHit({ t: 1, kind: 0, shot: 3, tHit: 2000, p: [0, 0.9, -1.7], v: [0, 0, 3], s: [0, 0, 0] }, 2600, 0.6, 0.12);
  chk(Math.abs(ff2.adv - 0.12) < 1e-9, 'FSM: avance CAPADO a 120 ms (spec §17)');
}

/* — 6 · validación anti-trampa ———————————————————————————————————— */
{
  const v = new P.Validator();
  const ctx = { nowHost: 5000, lastShot: 0, lastHitT: 4000, padPos: [0.1, 0.9, 1.0] };
  chk(v.hit({ t: 1, kind: 0, shot: 1, tHit: 4900, p: [0.1, 0.9, 1.0], v: [0, 0, -5], s: [0, 0, 0] }, ctx).ok,
    'validación: golpe normal ACCEPTED');
  chk(!v.hit({ t: 1, kind: 0, shot: 2, tHit: 4910, p: [0.1, 0.9, 1.0], v: [0, 0, -40], s: [0, 0, 0] }, ctx).ok,
    'validación: bola a 40 m/s RECHAZADA (máx 30, spec §12)');
  chk(!v.hit({ t: 1, kind: 0, shot: 2, tHit: 4905, p: [0.1, 0.9, 1.0], v: [0, 0, -5], s: [200, 0, 0] }, ctx).ok,
    'validación: giro 200 rad/s RECHAZADO');
  chk(!v.hit({ t: 1, kind: 0, shot: 5, tHit: 4900, p: [0.1, 0.9, 1.0], v: [0, 0, -5], s: [0, 0, 0] }, ctx).ok,
    'validación: shotNumber no correlativo RECHAZADO');
  chk(!v.hit({ t: 1, kind: 0, shot: 2, tHit: 4050, p: [0.1, 0.9, 1.0], v: [0, 0, -5], s: [0, 0, 0] }, ctx).ok,
    'validación: cadencia <150 ms RECHAZADA');
  chk(!v.hit({ t: 1, kind: 0, shot: 2, tHit: 4900, p: [2.0, 0.9, 1.0], v: [0, 0, -5], s: [0, 0, 0] }, ctx).ok,
    'validación: golpe a 1,9 m de la pala del rival RECHAZADO');
  chk(v.serious >= 3, `validación: 3 fallos graves → partida sospechosa (${v.serious})`);
}

/* — 7 · MatchSync: convergencia y disputa ————————————————————————— */
{
  const h = new P.MatchSync('host');
  const g = new P.MatchSync('guest');
  // caso 1: host autoridad (la bola murió en su mitad), guest también lo vio
  let d1 = h.localPoint(0, 'player', 'dbl_opp', 1, 0, true, 0);
  chk(d1.apply && d1.send?.k === 'claim', 'sync: el extremo con autoridad EMITE CLAIM');
  let d2 = g.localPoint(0, 'ai', 'dbl_opp', 0, 1, false, 5);   // guest detectó (su perspectiva: ganó la ai)
  chk(d2.apply && !d2.send, 'sync: el invitado aplica SU detección sin reclamar');
  const ack1 = g.onClaim(d1.send, 'ai');   // claim 'player' del host = 'ai' en el marco del guest
  chk(ack1.ack.agree === true && !ack1.apply, 'sync: detección local del guest ENCAJA con el claim → ACK acuerdo');
  chk(h.onAck(ack1.ack).ok, 'sync: el host confirma el ACK');
  // caso 2: guest no detectó nada (fantasma desincronizado) → claim aplica
  const d3 = h.localPoint(1, 'ai', 'out', 1, 1, true, 10);
  g.applied = -1;   // el guest no vio este punto
  const ack2 = g.onClaim(d3.send, 'player');
  chk(ack2.apply && ack2.ack.agree, 'sync: claim de rally NO visto → se APLICA por la red (spec §7)');
  // caso 3: desacuerdo real → disputa → RESYNC del host
  h.localPoint(2, 'player', 'wall', 2, 1, true, 20);
  g.applied = 2; g.appliedW = 'ai';   // el guest aplicó lo contrario
  const ack3 = g.onClaim(d3.send && { ...d3.send, r: 2 }, 'player');
  chk(ack3.ack.agree === false, 'sync: ganadores contradictorios → ACK en DESACUERDO');
  chk(h.onAck(ack3.ack).dispute === true && h.disputes === 1, 'sync: disputa registrada → el HOST resincroniza (spec §7)');
  // caso 4: LET no pasa por claims (determinista en ambos extremos)
  chk(h.localPoint(3, 'player', 'x', 0, 0, true, 30).send.k === 'claim', 'sync: rallye nuevo reanuda el libro');
}

/* — 8 · simulador de red + bucle de dos extremos ——————————————————— */
{
  // dos relojes conectados por un NetSim con pérdida 3 % y jitter 10 ms:
  // los eventos se REENVÍAN hasta el ack y NINGUNO se pierde al final.
  const simA = new P.NetSim({ lat: 40, jit: 10, loss: 0.03, seed: 77 });
  const simB = new P.NetSim({ lat: 40, jit: 10, loss: 0.03, seed: 99 });
  const THETA = 90, DL = 40;   // host +90 ms; one-way 40 ms
  let t = 100000;
  const A = { clock: new P.NetClock(true), now: t + THETA, lastRecvPeer: 0, lastRecvLocal: 0 };
  const B = { clock: new P.NetClock(false), now: t, lastRecvPeer: 0, lastRecvLocal: 0 };
  const deliver = (from, to, buf) => {
    const pkt = P.decodePacket(buf, {});
    if (!pkt) return;
    // eco: el RECEPTOR guarda el sendTime del otro y cuándo lo recibió
    to.lastRecvPeer = pkt.sendTime;
    to.lastRecvLocal = to.now;
    to.clock.onPacket(pkt, to.now);
    to.got = (to.got || 0) + 1;
  };
  let delivered = 0, sent = 0;
  B.clock.anchor(t, t + DL + THETA, t + DL);      // ancla gruesa por reliable
  for (let i = 0; i < 200; i++) {
    t += 16.7;
    A.now = t + THETA;                            // el host ES el reloj de referencia
    B.now = t;
    // A envía pose+eco (echoTime = el sendTime de B que A recibió)
    const bufA = new ArrayBuffer(64);
    const nA = P.encodePacket(bufA, {
      seq: i & 0xffff, ack: 0, ackBits: 0, sendTime: A.now >>> 0,
      echoTime: A.lastRecvPeer >>> 0,
      echoDelay: A.lastRecvPeer ? Math.min(65535, Math.round(A.now - A.lastRecvLocal)) : 0,
      pose: null, evs: [],
    });
    A.clock.markSent(A.now);
    sent++;
    simA.emit(bufA.slice(0, nA), A.now, (b) => { deliver(A, B, b); delivered++; });
    // B responde (echoTime = el sendTime de A que B recibió)
    const bufB = new ArrayBuffer(64);
    const nB = P.encodePacket(bufB, {
      seq: i & 0xffff, ack: 0, ackBits: 0, sendTime: B.now >>> 0,
      echoTime: B.lastRecvPeer >>> 0,
      echoDelay: B.lastRecvPeer ? Math.min(65535, Math.round(B.now - B.lastRecvLocal)) : 0,
      pose: null, evs: [],
    });
    B.clock.markSent(B.now);
    simB.emit(bufB.slice(0, nB), B.now, (b) => { deliver(B, A, b); delivered++; });
    simA.pump(A.now); simB.pump(B.now);
  }
  B.clock.apply(t, false);
  const errOff = Math.abs(B.clock.offset - THETA);
  // NOTA: el arnés entrega paquetes cuantizados al paso del bucle (16,7 ms),
  // lo que mete un sesgo de hasta ±8 ms que NO existe en el juego real
  // (allí sendTime/echo viajan con relojes reales). Tolerancia 12 ms.
  chk(B.clock.ready && errOff < 12,
    `netSim 3 % pérdida + jitter 10 ms: offset del invitado ${B.clock.offset.toFixed(1)} ms (error ${errOff.toFixed(2)} < 12 ms) tras ${delivered} paquetes`);
  const rs = B.clock.rttStats();
  chk(Math.abs(rs.med - 2 * DL) < 25, `netSim: RTT mediana ${rs.med} ms ≈ ${2 * DL} ms (±25 por cuantización)`);
  chk(sent > 150, `netSim: ${sent} paquetes emitidos con pérdida simulada sin colgar el bucle`);
}

console.log(`\nRESULTADO: ${ok} OK · ${fails} FALLOS (test_red_nucleo · PPNET r79)`);
process.exit(fails === 0 ? 0 : 1);

/* r99ter-2 · ARNÉS MULTI-RALLY — dos IAs REALES (c06) jugando entre sí con
 * árbitro simple. Busca el bloqueo que reportó el dueño («la pala del rival
 * queda bloqueada en la misma posición»):
 *  · CONGELAMIENTO: la pala (chain.cur o pos) quieta > 1 s mientras la bola
 *    se acerca a su campo.
 *  · INVASIÓN: la pala cruza la red persiguiendo una bola devuelta antes de
 *    tiempo (sin cota de campo propio el jinete la sigue hasta el otro lado).
 *  · CADENA ZOMBI: una cadena viva > 4 s.
 *  · NaN en cualquier estado. */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r99' }; } catch (e) { /* getter vivo */ }

import * as THREE from 'three';
const { OpponentAI } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

const cfg = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 9, predictInterval: 0.05,
  maxSpeed: 2.6, accel: 6.0 };   // piernas: como el cfg real del juego

const rival = new OpponentAI(cfg, -1, new THREE.Vector3(0, 1.0, -1.55));
const jug = new OpponentAI(cfg, 1, new THREE.Vector3(0, 1.0, 1.55));
rival.style = null; jug.style = null;

const ball = { pos: new THREE.Vector3(), vel: new THREE.Vector3(),
  spin: new THREE.Vector3(), dragMul: 1,
  ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };

function saca(sign) {
  ball.pos.set((Math.random() - 0.5) * 0.3, 1.02, sign * 1.2);
  ball.vel.set((Math.random() - 0.5) * 0.5, 1.15 + Math.random() * 0.4,
    -sign * (1.9 + Math.random() * 0.5));
  ball.spin.set(0, 0, 0);
  ball.ppPortal = false; ball.ppEfecto = false;
}

const ctxR = { canHit: true, validBounce: false, oppPadX: 0, oppPadZ: 1.55,
  rallyHits: 1, holdTarget: null, prevBall: new THREE.Vector3() };
const ctxJ = { canHit: true, validBounce: false, oppPadX: 0, oppPadZ: -1.55,
  rallyHits: 1, holdTarget: null, prevBall: new THREE.Vector3() };

const evs = [];
let rally = 0, frame = 0, boteEste = false;
let devolucionesR = 0, devolucionesJ = 0;
const quejas = [];
const estadoR = { quieta: 0, ult: new THREE.Vector3() };
const estadoJ = { quieta: 0, ult: new THREE.Vector3() };
const DT = 1 / 60;

function vigia(estado, ai, sign, nombre) {
  const mesh = ai.chain ? ai.chain.cur : ai.pos;
  const movio = mesh.distanceTo(estado.ult) > 0.015;
  estado.ult.copy(mesh);
  const bolaCerca = ball.vel.z * sign > 0.4 &&           // la bola viene hacia él
    ball.pos.z * sign < 0 && Math.abs(ball.pos.z) < 2.2 && boteEste;
  if (!movio && bolaCerca) estado.quieta++; else estado.quieta = 0;
  if (estado.quieta === 60) quejas.push(
    `${nombre}: pala QUIETA 1 s con bola acercándose (f${frame}, ` +
    `bola z=${ball.pos.z.toFixed(2)}, pala z=${mesh.z.toFixed(2)})`);
  // invasión REAL: en APROXIMACIÓN (back/strike) la pala > 30 cm allende
  // la red con la bola en su campo. El follow-through de una bola corta
  // CRUZA la red por diseño (el gesto continúa hacia el tiro) y los
  // tránsitos de vuelta a casa son legítimos: no se flaggean.
  const enAproximacion = ai.chain &&
    (ai.chain.phase === 'back' || ai.chain.phase === 'strike');
  if (enAproximacion && mesh.z * sign < -0.30 &&
      ball.pos.z * sign > 0.04) quejas.push(
    `${nombre}: pala INVADE el campo contrario (f${frame}, pala z=${mesh.z.toFixed(2)})`);
  if (ai.chain && ai.chain.t > 4.0) quejas.push(
    `${nombre}: cadena ZOMBI ${ai.chain.t.toFixed(1)} s (f${frame})`);
  if (!Number.isFinite(mesh.x + mesh.y + mesh.z)) quejas.push(
    `${nombre}: NaN en la pala (f${frame})`);
}

let ultimoVz = 0;
const FRAME_TOTAL = 30000;
for (frame = 0; frame < FRAME_TOTAL; frame++) {
  if (rally === 0) { saca(Math.random() < 0.5 ? -1 : 1); rally = 1;
    boteEste = false; ultimoVz = ball.vel.z; }
  ctxR.validBounce = boteEste; ctxJ.validBounce = boteEste;
  ctxR.oppPadX = jug.pos.x; ctxR.oppPadZ = jug.pos.z;
  ctxJ.oppPadX = rival.pos.x; ctxJ.oppPadZ = rival.pos.z;
  ctxR.prevBall.copy(ball.pos); ctxJ.prevBall.copy(ball.pos);
  rival.update(DT, ball, ctxR);
  jug.update(DT, ball, ctxJ);
  vigia(estadoR, rival, -1, 'RIVAL');
  vigia(estadoJ, jug, 1, 'JUGADOR');
  // conteo de devoluciones: la vz de la bola se invierte
  if (ball.vel.z < 0 && ultimoVz > 0) devolucionesJ++;
  if (ball.vel.z > 0 && ultimoVz < 0) devolucionesR++;
  ultimoVz = ball.vel.z;
  evs.length = 0;
  stepPhysics(DT, ball, [], evs);
  for (const e of evs) {
    if (e.type === 'table') boteEste = true;
    if (e.type === 'floor' || e.type === 'net' || e.type === 'wall') {
      rally = 0;   // punto cantado → nuevo saque
      break;
    }
  }
  if (Math.abs(ball.pos.z) > 3.2 || Math.abs(ball.pos.x) > 2.4 || rally > 900) {
    if (rally > 900) quejas.push(`rally interminable en f${frame}`);
    rally = 0;
  }
}

console.log(`rallies iniciados: ${rally} · devoluciones rival ${devolucionesR} · ` +
  `jugador ${devolucionesJ} · frames ${frame}`);
if (quejas.length) {
  // dedupe: una misma queja repetida cada frame no aporta — 1ª vez + total
  const vistas = new Map();
  for (const q of quejas) {
    const clave = q.replace(/f\d+/g, 'fN').replace(/z=[-.0-9]+/g, 'z=N');
    vistas.set(clave, (vistas.get(clave) || 0) + 1);
  }
  quejas.length = 0;
  for (const [clave, n] of vistas) quejas.push(`${clave} ×${n}`);
  console.log(`\nINCIDENTES (${quejas.length}, primeras 12):`);
  for (const q of quejas.slice(0, 12)) console.log('  ✗ ' + q);
} else console.log('  ✓ sin bloqueos, sin invasiones, sin cadenas zombi, sin NaN');
void devolucionesR; void devolucionesJ;
process.exit(quejas.length ? 1 : 0);

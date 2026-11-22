/* r99ter · DEBUG del jinete: por frame, dRem/tRem/vC/speed/dist y la curva */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r99' }; } catch (e) { /* getter vivo */ }
import * as THREE from 'three';
const { OpponentAI } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

const cfg = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 10, predictInterval: 0.05 };
const ai = new OpponentAI(cfg, -1, new THREE.Vector3(0, 1.0, -1.55));
ai.style = null;
const ball = { pos: new THREE.Vector3(0.05, 1.05, -0.55),
  vel: new THREE.Vector3(0.0, -1.6, -2.6), spin: new THREE.Vector3(),
  dragMul: 1, ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
const ctxPrev = new THREE.Vector3();
const evs = [];
let bote = -1;
for (let f = 0; f < 100; f++) {
  ctxPrev.copy(ball.pos);
  const ctx = { canHit: true, validBounce: bote >= 0, oppPadX: 0, oppPadZ: 1.5,
    rallyHits: 1, holdTarget: null, prevBall: ctxPrev };
  const r = ai.update(1 / 60, ball, ctx);
  const ch = ai.chain;
  if (f % 3) { } else if (ch) {
    const d = ai._disparo;
    console.log(`f${String(f).padStart(2)} ${ch.phase.padEnd(7)} ` +
      `sC=${ch.sC.toFixed(2)} speed=${ch.speed.toFixed(1)} ` +
      `cur=(${ch.cur.x.toFixed(2)},${ch.cur.y.toFixed(2)},${ch.cur.z.toFixed(2)}) ` +
      `bola=(${ball.pos.x.toFixed(2)},${ball.pos.y.toFixed(2)},${ball.pos.z.toFixed(2)}) ` +
      `d=${ch.cur.distanceTo(ball.pos).toFixed(2)} ` +
      (d ? `disp.t=${d.t.toFixed(2)} tCruce=${d.tCruce.toFixed(2)} disp.pos=(${d.pos.x.toFixed(2)},${d.pos.y.toFixed(2)},${d.pos.z.toFixed(2)})` : 'sin-disparo') +
      (ch.persec ? ' PERSEC' : '') +
      (ai.predictValid ? ` pred=(${ai.predict.x.toFixed(2)},${ai.predict.y.toFixed(2)},${ai.predict.z.toFixed(2)}) T=${ai.predictT.toFixed(2)}` : ' sin-pred') +
      (r ? ' ⟹ SALIDA' : ''));
  } else {
    console.log(`f${String(f).padStart(2)} SIN-CADENA` + (r ? ' ⟹ SALIDA' : ''));
  }
  evs.length = 0;
  stepPhysics(1 / 60, ball, [], evs);
  if (bote < 0 && evs.some((e) => e.type === 'table')) bote = f;
  if (r) break;
}

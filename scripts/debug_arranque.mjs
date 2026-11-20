/* r99ter-2 · sonda: el estado del AI del test del disparo (cfg incompleto) */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r99' }; } catch (e) { /* getter vivo */ }
import * as THREE from 'three';
const { OpponentAI } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

const cfgT = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 10, predictInterval: 0.05 };
const ai = new OpponentAI(cfgT, -1, new THREE.Vector3(0, 1.0, -1.55));
ai.style = null;
const bola = { pos: new THREE.Vector3(0.05, 1.05, -0.55),
  vel: new THREE.Vector3(0.0, -1.6, -2.6), spin: new THREE.Vector3(), dragMul: 1,
  ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
const ctxPrev = new THREE.Vector3();
const ctx = { canHit: true, validBounce: false, oppPadX: 0, oppPadZ: 1.5,
  rallyHits: 1, holdTarget: null, prevBall: ctxPrev };
for (let f = 0; f <= 40; f++) {
  if (f > 0) {
    ctxPrev.copy(bola.pos);
    ai.update(1 / 60, bola, ctx);
    stepPhysics(1 / 60, bola, [], []);
  }
  if (f % 10 === 0) console.log('f' + f,
    'pos NaN?', !Number.isFinite(ai.pos.x),
    'vel NaN?', !Number.isFinite(ai.vel.x),
    'chain?', !!ai.chain,
    ai.chain ? 'cur NaN? ' + !Number.isFinite(ai.chain.cur.x) : '',
    'predV?', ai.predictValid);
}

/* r100 · sonda: dónde se va la longitud del arco (tercios de la tabla) */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r99' }; } catch (e) { /* getter */ }
import * as THREE from 'three';
const { OpponentAI } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

const cfg = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 10, predictInterval: 0.05,
  maxSpeed: 2.6, accel: 6.0 };
const ai = new OpponentAI(cfg, -1, new THREE.Vector3(0, 1.0, -1.55));
ai.style = null;
const bola = { pos: new THREE.Vector3(0.05, 1.05, -0.55),
  vel: new THREE.Vector3(0.0, -1.6, -2.6), spin: new THREE.Vector3(), dragMul: 1,
  ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
const prev = new THREE.Vector3();
const ctx = { canHit: true, validBounce: false, oppPadX: 0, oppPadZ: 1.5,
  rallyHits: 1, holdTarget: null, prevBall: prev };
for (let f = 0; f <= 20; f++) {
  if (f > 0) {
    prev.copy(bola.pos);
    ai.update(1 / 60, bola, ctx);
    stepPhysics(1 / 60, bola, [], []);
  }
  if (f === 20 && ai.chain) {
    const ch = ai.chain, cv = ch.curva;
    const min = new THREE.Vector3(9, 9, 9), max = new THREE.Vector3(-9, -9, -9);
    for (const p of cv.pts) {
      min.min(p); max.max(p);
    }
    console.log('f20 · total=', cv.total.toFixed(2),
      '· tercios:', cv.len[15].toFixed(2), cv.len[31].toFixed(2),
      '· sC=', ch.sC.toFixed(2));
    console.log('  caja: x', min.x.toFixed(2), '..', max.x.toFixed(2),
      '· y', min.y.toFixed(2), '..', max.y.toFixed(2),
      '· z', min.z.toFixed(2), '..', max.z.toFixed(2));
    console.log('  hombro=(', ch.hombro.x.toFixed(2), ch.hombro.y.toFixed(2),
      ch.hombro.z.toFixed(2), ') restP=(', ch.restP.x.toFixed(2),
      ch.restP.y.toFixed(2), ch.restP.z.toFixed(2), ')');
    console.log('  contact=(', ch.contact.x.toFixed(2), ch.contact.y.toFixed(2),
      ch.contact.z.toFixed(2), ') pos=(', ai.pos.x.toFixed(2),
      ai.pos.y.toFixed(2), ai.pos.z.toFixed(2), ')');
    console.log('  s=', ch.s.toFixed(2), ' speed=', ch.speed.toFixed(2),
      ' persec=', ch.persec, ' kind=', ch.kind, ' jit=', ch.jit.toFixed(2));
    if (ch.kDBG) for (let k = 0; k < 4; k++)
      console.log('  K' + k + '=(' + ch.kDBG[k].x.toFixed(2) + ',' +
        ch.kDBG[k].y.toFixed(2) + ',' + ch.kDBG[k].z.toFixed(2) + ')');
    // puntos clave de la tabla (inicio/fin de cada tercio)
    for (const i of [0, 15, 16, 31, 32, 47])
      console.log('  pts[' + i + ']=(' + cv.pts[i].x.toFixed(2) + ',' +
        cv.pts[i].y.toFixed(2) + ',' + cv.pts[i].z.toFixed(2) + ')');
  }
}

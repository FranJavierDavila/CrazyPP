#!/usr/bin/env node
/* CRAZY PING PONG · BENCH FÍSICO (roadmap P1 · presupuesto de rendimiento).
 * Mide el coste REAL de los bucles internos de la física (c04) sobre la
 * fuente del juego en Node. Lo consume scripts/qa_rendimiento.py: si un
 * cambio mete una asignación o un O(n) en el camino caliente, suena aquí
 * ANTES de llegar al casco.
 * r129 · C1 (ola 3): añade el SOLVER COMPUESTO de tiro (c05) — el pico real
 * del frame del golpeo que las primitivas no captan. solverFresh64 = 64
 * tiros con blancos distintos (solve completo, el coste sin caché);
 * solverHot64 = 64 repeticiones del mismo tiro (con la caché LRU: casi
 * gratis). Salida: una línea JSON en ms. */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-bench' }; } catch (e) { /* getter */ }
import * as c04 from '../src/game/core/c04_fisica_ccd.js';

const V = c04.tmpV.constructor;

// 1 · barrido CCD bola↔hoja (el camino caliente del golpeo): 200k rayos
// con patrón determinista que alterna impacto frontal/canto/rasante/miss
let t0 = performance.now();
let acc = 0;
for (let i = 0; i < 200000; i++) {
  const f = i & 3;
  acc += c04.sweepBallVsBlade(f * 0.01, 0.001 * (i % 7), 0.12, -0.03, 0.002, -0.12, 0.075, 0.004, 0.02);
}
const sweep200k = performance.now() - t0;

// 2 · bote slip-coupled en mesa: 100k
const vel = new V(1.2, -3.5, -2.0), spin = new V(0, 0, 90);
t0 = performance.now();
for (let i = 0; i < 100000; i++) c04.bounceOnTable(vel, spin, 2 + (i % 30) / 10);
const bounce100k = performance.now() - t0;

// 3 · aerodinámica (drag + Magnus): 200k
const vel2 = new V(3, -4, -6), spin2 = new V(0, 80, 0);
t0 = performance.now();
for (let i = 0; i < 200000; i++) c04.applyAerodynamics(vel2, spin2, 1 / 240);
const aero200k = performance.now() - t0;

// 4 · C1 (r129 · ola 3) · SOLVER COMPUESTO de tiro (c05): 64 solves reales
// con blancos distintos vs 64 repeticiones que la caché LRU responde.
const c05 = await import('../src/game/core/c05_colisiones_ia_golpeo.js');
const DIMS = (await import('../src/game/core/c02_cfg_escena.js')).DIMS;
const fromSol = new V(0, DIMS.tableTopY + 0.45, DIMS.tableCenterZ + 1.15);
const toSol = new V(0.3, DIMS.tableTopY + DIMS.ballRadius, DIMS.tableCenterZ - 0.8);
const spinSol = new V(0, 2, 0);
t0 = performance.now();
for (let i = 0; i < 64; i++) {
  toSol.x = 0.3 + 0.004 * (i % 17);
  toSol.z = -0.8 - 0.003 * (i % 23);
  acc += c05.computeShotVelocityReal(fromSol, toSol, 0.7 + 0.01 * (i % 5), 9, spinSol).lengthSq();
}
const solverFresh64 = performance.now() - t0;
t0 = performance.now();
for (let i = 0; i < 6400; i++) {
  acc += c05.computeShotVelocityReal(fromSol, toSol, 0.7, 9, spinSol).lengthSq();
}
const solverHot64 = performance.now() - t0;   // 6400 hits: GC amortizado

if (!isFinite(acc)) throw new Error('banch imposible');   // el JIT no puede eliminar el bucle
console.log(JSON.stringify({
  sweep200k: +sweep200k.toFixed(1),
  bounce100k: +bounce100k.toFixed(1),
  aero200k: +aero200k.toFixed(1),
  solverFresh64: +solverFresh64.toFixed(1),
  solverHot64: +solverHot64.toFixed(1),
}));
// C1 (r129): la importación de c05 arrastra c00_pre_three, que registra los
// temporizadores del shell (flush de telemetría 30 s, avisos) — en Node
// eso mantiene vivo el event loop para siempre. El JSON ya está impreso:
// salida explícita, el patrón de siempre en los arneses que tocan c00.
process.exit(0);


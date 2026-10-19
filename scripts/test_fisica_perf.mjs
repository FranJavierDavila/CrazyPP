#!/usr/bin/env node
/* CRAZY PING PONG · BENCH FÍSICO (roadmap P1 · presupuesto de rendimiento).
 * Mide el coste REAL de los bucles internos de la física (c04) sobre la
 * fuente del juego en Node. Lo consume scripts/qa_rendimiento.py: si un
 * cambio mete una asignación o un O(n) en el camino caliente, suena aquí
 * ANTES de llegar al casco.
 * Salida: una línea JSON {sweep200k, bounce100k, aero200k} en ms. */
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

if (!isFinite(acc)) throw new Error('banch imposible');   // el JIT no puede eliminar el bucle
console.log(JSON.stringify({
  sweep200k: +sweep200k.toFixed(1),
  bounce100k: +bounce100k.toFixed(1),
  aero200k: +aero200k.toFixed(1),
}));

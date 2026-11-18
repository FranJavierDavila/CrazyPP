#!/usr/bin/env node
/* CRAZY PING PONG · TESTS DE FÍSICA DETERMINISTAS · C05 (r57, auditoría R2).
 * Ejecuta la FUENTE REAL (c05_colisiones_ia_golpeo.js + c04 + c02) en Node —
 * el mismo código que corre en el Quest — sobre escenarios fijos y compara
 * el HASH SHA256 de cada escenario con scripts/fisica_golden_c05.json.
 *
 * Cubre el núcleo de c05: stepPhysics (vuelo, botes slip-coupled, red,
 * suelo/paredes, golpe de pala, apoyo/arraastre, arkanoid, bola marcada por
 * el Súper Efecto), predictStrike (la IA), testPaddleContact (online),
 * simulateServePath y computeShotVelocity (solver de saque).
 *
 * Igual que test_fisica.mjs (c04): si alguien toca la física de c05 y cambia
 * UNA décima de un decimal en un solo caso, el test se rompe.
 *
 * Uso:
 *   node --no-warnings scripts/test_fisica_c05.mjs            # verificar
 *   node --no-warnings scripts/test_fisica_c05.mjs --update   # refrescar
 *                                                             # (solo tras
 *                                                             # un cambio
 *                                                             # FÍSICO
 *                                                             # intencional)
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

/* patrón del repo (bench_fisica_v305, arnes_rallies…): los globals del
 * navegador los aporta EL ARNÉS, la fuente no se toca para los tests. */
globalThis.window = globalThis.window || globalThis;

/* c05 tiene jitter DELIBERADO en el golpe de canto (v3.0.5 P1, c05:207:
 * Math.random). Para el golden, PRNG sembrado (mulberry32): la secuencia es
 * idéntica en cada corrida y el bamboleo queda bajo contrato. */
const _mr = Math.random;
let _seed = 0x9e3779b9;
Math.random = () => {
  _seed |= 0; _seed = (_seed + 0x6d2b79f5) | 0;
  let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const { c05, c04, DIMS, SERVE_TUNE } = await (async () => {
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const m4 = await import(fileURLToPath(new URL('../src/game/core/c04_fisica_ccd.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c05: m5, c04: m4, DIMS: m2.DIMS, SERVE_TUNE: m2.SERVE_TUNE };
})();

const GOLDEN_PATH = new URL('./fisica_golden_c05.json', import.meta.url).pathname;

/* — hashing canónico: JSON con decimales fijos (idéntico al arnés c04) —— */
const r9 = (n) => Number(n.toFixed(9));
const canon = (v) => JSON.stringify(v, (k, x) => (typeof x === 'number' ? r9(x) : x));
const sha = (v) => createHash('sha256').update(canon(v)).digest('hex').slice(0, 16);

let ok = 0, fails = 0;
const resultados = {};

function escenario(nombre, datos) {
  const h = sha(datos);
  resultados[nombre] = h;
  console.log(`  · ${nombre.padEnd(34)} ${h}`);
  return h;
}

/* — fábricas deterministas ———————————————————————————————————————————— */
function bolaBase(x, y, z, vx, vy, vz, wx = 0, wy = 0, wz = 0) {
  return {
    pos: new THREE.Vector3(x, y, z),
    vel: new THREE.Vector3(vx, vy, vz),
    spin: new THREE.Vector3(wx, wy, wz),
    __ppRestIdx: -1,
  };
}

function palaBase(who, index, x, y, z, vx = 0, vy = 0, vz = 0) {
  const p = c04.createPaddleSim(who, index);
  p.pos.set(x, y, z);
  p.prev.copy(p.pos);
  p.vel.set(vx, vy, vz);
  p.active = true;
  p.serveFlight = false;
  p.intercambio = false;
  p.extraReach = 0;
  return p;
}

function snapEstado(ball) {
  return {
    pos: ball.pos.toArray(),
    vel: ball.vel.toArray(),
    spin: ball.spin.toArray(),
  };
}

function snapEventos(events) {
  return events.map(e => {
    const o = { type: e.type };
    if ('speed' in e) o.speed = e.speed;
    if ('side' in e) o.side = e.side;
    if ('who' in e) o.who = e.who;
    if ('edge' in e) o.edge = e.edge;
    if ('paddleIndex' in e) o.paddleIndex = e.paddleIndex;
    if ('imanAim' in e) o.imanAim = e.imanAim;
    if (e.pos) o.pos = e.pos.toArray();
    return o;
  });
}

/* — 1 · stepPhysics: vuelo libre con giro (gravedad + aero + Magnus) ——— */
{
  const b = bolaBase(0, 1.2, 0, 1.5, 0.5, -3.5, 0, 0, 30);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 40; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (f % 8 === 0) caps.push(snapEstado(b));
  }
  escenario('stepPhysics.vueloLibre', { caps });
}

/* — 2 · stepPhysics: bote TOPSPIN slip-coupled en la mitad IA ————————— */
{
  const b = bolaBase(0.1, DIMS.tableTopY + 0.35, DIMS.tableCenterZ - 0.5, 0.3, -2.5, -1.5, -40, 0, 0);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 90; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (ev.length) { caps.push({ ev: snapEventos(ev), ...snapEstado(b) }); ev.length = 0; }
  }
  escenario('stepPhysics.boteTopspin', { caps, fin: snapEstado(b) });
}

/* — 3 · stepPhysics: bote BACKSPIN slip-coupled ———————————————————————— */
{
  const b = bolaBase(0.1, DIMS.tableTopY + 0.35, DIMS.tableCenterZ - 0.5, 0.3, -2.5, -1.5, 40, 0, 0);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 90; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (ev.length) { caps.push({ ev: snapEventos(ev), ...snapEstado(b) }); ev.length = 0; }
  }
  escenario('stepPhysics.boteBackspin', { caps, fin: snapEstado(b) });
}

/* — 4 · stepPhysics: choque con la RED (vuelo bajo que cruza el plano) — */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0, 0.9, C - 0.3, 0, -0.5, 4.5, 0, 0, 0);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 30; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (ev.length) { caps.push({ ev: snapEventos(ev), ...snapEstado(b) }); ev.length = 0; }
  }
  escenario('stepPhysics.red', { caps, fin: snapEstado(b) });
}

/* — 5 · stepPhysics: suelo y paredes (bola fuera de mesa hasta el reposo) */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0.5, 0.8, C + DIMS.tableHalfLength + 0.3, 0.2, -1, 0.5);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 240; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (ev.length) { caps.push({ ev: snapEventos(ev) }); ev.length = 0; }
  }
  escenario('stepPhysics.sueloParedes', { caps, fin: snapEstado(b) });
}

/* — 6 · stepPhysics: GOLPE de pala (barrido CCD sobre bola que llega) —— */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0, 0.9, C + 0.45, 0, 0, 2.2, 0, 0, 12);
  const p = palaBase('player', 0, 0, 0.9, C + 0.72);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 20; f++) {
    c05.stepPhysics(1 / 60, b, [p], ev);
    caps.push({ f, cooldown: p.cooldown, ...snapEstado(b), ev: snapEventos(ev) });
    ev.length = 0;
  }
  escenario('stepPhysics.golpePala', { caps });
}

/* — 7 · stepPhysics: APOYO quieto + rodadura al inclinar la pala ——————— */
{
  const b = bolaBase(0, 0, 0, 0, 0, 0);
  b.__ppRestIdx = 0; b.__ppRestSide = 1; b.__ppRestLx = 0; b.__ppRestDy = 0;
  b.__ppRestSx = 0; b.__ppRestSy = 0; b.__ppRestT = 0;
  const p = palaBase('player', 0, 0, 0.9, DIMS.tableCenterZ + 0.65);
  // recolocar la bola SOBRE la cara de la hoja (como la deja el contacto)
  const base = new THREE.Vector3().copy(p.pos).addScaledVector(p.up, DIMS.bladeCenterUp);
  b.pos.copy(base).addScaledVector(p.normal, DIMS.ballRadius + 0.001);
  const ev = [];
  const caps = [];
  for (let f = 0; f < 30; f++) {
    c05.stepPhysics(1 / 60, b, [p], ev);
    if (f % 5 === 0 || ev.length) caps.push({ f, rest: b.__ppRestIdx, ...snapEstado(b), ev: snapEventos(ev) });
    ev.length = 0;
  }
  // inclinar la pala: la normal se desvía → la bola rueda cuesta abajo
  const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), 0.35);
  const n0 = p.normal.clone(), u0 = p.up.clone(), r0 = p.right.clone();
  p.normal.copy(n0).applyQuaternion(q);
  p.up.copy(u0).applyQuaternion(q);
  p.right.copy(r0).applyQuaternion(q);
  for (let f = 0; f < 40; f++) {
    c05.stepPhysics(1 / 60, b, [p], ev);
    if (f % 8 === 0 || ev.length) caps.push({ f: 100 + f, rest: b.__ppRestIdx, ...snapEstado(b), ev: snapEventos(ev) });
    ev.length = 0;
  }
  escenario('stepPhysics.apoyoRodadura', { caps });
}

/* — 8 · stepPhysics: ARKANOID (juega sin red) ——————————————————————————— */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0, 0.9, C - 0.3, 0, -0.5, 4.5);
  b.ignoreNet = true;
  const ev = [];
  const caps = [];
  for (let f = 0; f < 30; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (f % 6 === 0 || ev.length) caps.push({ f, z: b.pos.z, ev: snapEventos(ev) });
    ev.length = 0;
  }
  escenario('stepPhysics.arkanoidSinRed', { caps });
}

/* — 9 · stepPhysics: bola MARCADA por el Súper Efecto (Magnus ×2,2) ———— */
{
  const b = bolaBase(0, 1.2, 0, 1.5, 0.5, -3.5, 0, 0, 30);
  b.ppEfecto = true;
  const ev = [];
  const caps = [];
  for (let f = 0; f < 40; f++) {
    c05.stepPhysics(1 / 60, b, [], ev);
    if (f % 8 === 0) caps.push(snapEstado(b));
  }
  escenario('stepPhysics.efectoMarcado', { caps });
}

/* — 10 · predictStrike: TOPSPIN con bote previo (IA no ciega) ————————— */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0.1, 1.0, C - 0.8, 0.2, -1.2, -3.0, -30, 0, 0);
  const r = c05.predictStrike(b, -1, true);
  escenario('predictStrike.topspin', {
    punto: r && r.point ? r.point.toArray() : null,
    t: r && r.t, urgent: r && r.urgent,
  });
}

/* — 11 · predictStrike: SMASH plano rápido ————————————————————————————— */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(-0.05, 1.1, C - 0.6, 0, -0.5, -9);
  const r = c05.predictStrike(b, -1, false);
  escenario('predictStrike.smash', {
    punto: r && r.point ? r.point.toArray() : null,
    t: r && r.t, urgent: r && r.urgent,
  });
}

/* — 12 · predictStrike: bola CORTA que no llega (null / planePoint) ———— */
{
  const C = DIMS.tableCenterZ;
  const b = bolaBase(0, 0.8, C - 0.4, 0, 0.2, -1.2);
  const r = c05.predictStrike(b, -1, false);
  escenario('predictStrike.corta', {
    punto: r && r.point ? r.point.toArray() : null,
    t: r && r.t, urgent: r && r.urgent,
  });
}

/* — 12b · predictStrike: bola al BORDE (canto + media bola) — r57 R2b ———
 * La mesa REAL boté con |x| ≤ halfWidth + ballRadius·0,5 (collideTable);
 * antes de alinear, la IA predicía con halfWidth EXACTO y daba la bola
 * por perdida cuando en la sim real SÍ bota. El centro cae a media bola
 * del canto: dentro del margen real, fuera del margen estrecho. */
{
  const C = DIMS.tableCenterZ;
  const xBorde = DIMS.tableHalfWidth + DIMS.ballRadius * 0.25;
  const b = bolaBase(xBorde, 1.0, C - 0.7, 0, -1.5, -2.5, 0, 0, 0);
  const r = c05.predictStrike(b, -1, false);
  escenario('predictStrike.borde', {
    punto: r && r.point ? r.point.toArray() : null,
    t: r && r.t, urgent: r && r.urgent,
  });
}

/* — 13 · testPaddleContact: online, barrido sin integrar (toque y no toque) */
{
  const C = DIMS.tableCenterZ;
  // 13a: la bola pasa lejos de la pala
  const b1 = bolaBase(0.5, 0.9, C + 0.4, 0, 0, 2);
  const p1 = palaBase('player', 0, 0, 0.9, C + 0.72);
  const ev1 = [];
  c05.testPaddleContact(b1, b1.pos.clone().add(new THREE.Vector3(0, 0, -0.05)), [p1], ev1);
  // 13b: la bola cruza justo la hoja
  const b2 = bolaBase(0, 0.9, C + 0.45, 0, 0, 2.2, 0, 0, 12);
  const p2 = palaBase('player', 0, 0, 0.9, C + 0.72);
  const ev2 = [];
  c05.testPaddleContact(b2, new THREE.Vector3(0, 0.9, C + 0.40), [p2], ev2);
  escenario('testPaddleContact.online', {
    miss: { ev: snapEventos(ev1), ...snapEstado(b1) },
    hit: { ev: snapEventos(ev2), ...snapEstado(b2) },
  });
}

/* — 14 · simulateServePath: trayectoria de saque válida ———————————————— */
{
  const C = DIMS.tableCenterZ;
  const from = new THREE.Vector3(0, 1.0, C + 0.75);
  const target = new THREE.Vector3(0.1, DIMS.tableTopY + DIMS.ballRadius, C - 0.55);
  const v0 = c05.computeShotVelocity(from, target, 0.7, 6);
  const r = c05.simulateServePath(from, v0, new THREE.Vector3(0, 0, 0), 1);
  const sim = (r && r.sim) ? r.sim.slice(0, 24).map(p => (p && p.toArray) ? p.toArray() : p) : null;
  escenario('simulateServePath.saque', { v0: v0.toArray(), err: r && r.err, w: r && r.w, sim });
}

/* — 15 · computeShotVelocity: parábola que pasa la red ————————————————— */
{
  const C = DIMS.tableCenterZ;
  const v = c05.computeShotVelocity(
    new THREE.Vector3(0, 1.0, C + 0.75),
    new THREE.Vector3(0.1, DIMS.tableTopY + DIMS.ballRadius, C - 0.55), 0.7, 6);
  escenario('computeShotVelocity.parabola', { v: v.toArray() });
}

/* — verificación contra el golden ——————————————————————————————————————— */
const dorado = existsSync(GOLDEN_PATH)
  ? JSON.parse(readFileSync(GOLDEN_PATH, 'utf8'))
  : null;

if (!dorado || process.argv.includes('--update')) {
  writeFileSync(GOLDEN_PATH, JSON.stringify(resultados, null, 2) + '\n');
  console.log(`\n${dorado ? 'GOLDEN ACTUALIZADO' : 'GOLDEN CREADO'} → ${GOLDEN_PATH} (${Object.keys(resultados).length} escenarios)`);
  process.exit(0);
}

for (const [nombre, h] of Object.entries(resultados)) {
  if (dorado[nombre] === h) { ok++; }
  else { fails++; console.error(`  ✗ DESVIACIÓN ${nombre}: golden ${dorado[nombre]} ≠ real ${h}`); }
}
const extra = Object.keys(dorado).filter(k => !(k in resultados));
if (extra.length) { fails += extra.length; console.error(`  ✗ escenarios en golden que ya no existen: ${extra.join(', ')}`); }

console.log(`\nFÍSICA c05 · ${ok} OK · ${fails} FALLOS (golden ${Object.keys(dorado).length} escenarios)`);
process.exit(fails ? 1 : 0);

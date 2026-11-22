#!/usr/bin/env node
/* CRAZY PING PONG · ARNÉS P0 r86 — los seis correctivos de física del
 * informe «Análisis profundo de la física de CrazyPP» (V3.6.177-SDK6).
 * Ejecuta la FUENTE REAL en Node (patrón test_fisica / test_fisica_c05) y
 * verifica COMPORTAMIENTO (no hash: los umbrales son afirmaciones):
 *   P0-1/P0-2 · agujas estáticas del reanclaje del saque + altura absoluta
 *   P0-3      · scoop con pala viva NO capturado → golpe normal con evento
 *   P0-4      · despegue analógico por empuje sostenido (+ temblor no dispara)
 *   P0-5      · fondo de mesa: la banda insideSlab resuelve por mínima
 *               penetración INCLUIDA la vertical
 *   P0-6      · rescate fuera de la huella + guardián honesto (agujas)
 * Uso: node --no-warnings scripts/test_fisica_p0_r86.mjs
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

globalThis.window = globalThis.window || globalThis;
const _mr = Math.random;
let _seed = 0x9e3779b9;
Math.random = () => {
  _seed |= 0; _seed = (_seed + 0x6d2b79f5) | 0;
  let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const { c05, c04, DIMS } = await (async () => {
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const m4 = await import(fileURLToPath(new URL('../src/game/core/c04_fisica_ccd.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c05: m5, c04: m4, DIMS: m2.DIMS, SERVE_TUNE: m2.SERVE_TUNE };
})();

const RAIZ = new URL('..', import.meta.url).pathname;
const src = (f) => readFileSync(RAIZ + f, 'utf-8');
const c00s = src('src/game/core/c00_pre_three.js');
const c02s = src('src/game/core/c02_cfg_escena.js');
const c05s = src('src/game/core/c05_colisiones_ia_golpeo.js');
const c12s = src('src/game/core/c12_pingponggame.js');

let ok = 0, fails = 0;
function aguja(nombre, cond, detalle = '') {
  if (cond) { ok++; console.log(`  ✓ ${nombre}`); }
  else { fails++; console.log(`  ✗ ${nombre}${detalle ? ' — ' + detalle : ''}`); }
}
const C = DIMS.tableCenterZ;

function bolaBase(x, y, z, vx = 0, vy = 0, vz = 0) {
  return {
    pos: new THREE.Vector3(x, y, z), vel: new THREE.Vector3(vx, vy, vz),
    spin: new THREE.Vector3(), __ppRestIdx: -1,
  };
}
function palaBase(who, index, x, y, z, vx = 0, vy = 0, vz = 0) {
  const p = c04.createPaddleSim(who, index);
  p.pos.set(x, y, z); p.prev.copy(p.pos); p.vel.set(vx, vy, vz);
  p.active = true; p.serveFlight = false; p.intercambio = false; p.extraReach = 0;
  return p;
}
/** pala CARA ARRIBA (la pose de acunar del dueño): normal +y, la bola reposa
 *  sobre la hoja — la gravedad es puramente normal y el apoyo es estable. */
function palaCaraArriba(who, index, x, y, z) {
  const p = palaBase(who, index, x, y, z);
  p.normal.set(0, 1, 0); p.up.set(0, 0, -1); p.right.set(1, 0, 0);
  p.prevNormal.copy(p.normal); p.prevUp.copy(p.up); p.prevRight.copy(p.right);
  return p;
}
function bolaApoyada(p) {
  const b = bolaBase(0, 0, 0);
  b.__ppRestIdx = p.index; b.__ppRestSide = 1;
  b.__ppRestLx = 0; b.__ppRestDy = 0;
  b.__ppRestSx = 0; b.__ppRestSy = 0; b.__ppRestT = 0; b.__ppRestPush = 0;
  const base = new THREE.Vector3().copy(p.pos).addScaledVector(p.up, DIMS.bladeCenterUp);
  b.pos.copy(base).addScaledVector(p.normal, DIMS.ballRadius + 0.001);
  return b;
}

/* — P0-3 · scoop con pala VIVA: no captura, golpe normal con evento ———— */
{
  // bola que baja MANSA (0,2 m/s) hacia una pala que SUBE con intención
  // (0,8 m/s): vRelN ≈ 0,2 ≤ paddleRestSpeed PERO pad.vel² > restPadSpeed²
  // ⇒ NO apoyo: el scoop atraviesa a la vía de golpe normal (evento + vida).
  // La bola apunta al CENTRO DE LA HOJA (14 cm sobre el agarre).
  const b = bolaBase(0, 1.10, C + 0.70, 0, -0.15, 0.2);
  const p = palaBase('player', 0, 0, 0.90, C + 0.72, 0, 0.8, 0);
  const ev = [];
  for (let f = 0; f < 12; f++) c05.stepPhysics(1 / 60, b, [p], ev);
  aguja('P0-3 · scoop con pala viva NO se captura', b.__ppRestIdx < 0,
    `restIdx=${b.__ppRestIdx}`);
  // el toque lento (0,2 m/s < restEventMin 0,35) es un GOLPE MUDO por diseño
  // (FEEL1): no emite evento, pero TAMPOCO secuestra — la bola atraviesa a la
  // vía de golpe, recibe reflejo + suelo de salida y sale CON VIDA.
  aguja('P0-3 · el scoop atraviesa al golpe (no capturada + salida con vida)',
    b.__ppRestIdx < 0 && b.vel.lengthSq() > 0.25,
    `restIdx=${b.__ppRestIdx} vel=${b.vel.length().toFixed(3)}`);

  // CONTRA: bola mansa sobre pala QUIETA ⇒ apoyo (el acunado de r101 intacto)
  const b2 = bolaBase(0, 1.10, C + 0.70, 0, -0.15, 0.2);
  const p2 = palaBase('player', 0, 0, 0.90, C + 0.72);
  const ev2 = [];
  for (let f = 0; f < 25 && b2.__ppRestIdx < 0; f++) c05.stepPhysics(1 / 60, b2, [p2], ev2);
  aguja('P0-3 · contra: pala quieta SÍ acuna (r101 intacto)', b2.__ppRestIdx === 0,
    `restIdx=${b2.__ppRestIdx}`);
}

/* — P0-4 · despegue analógico por EMPUJE SOSTENIDO ————————————————————— */
{
  // bola APOYADA sobre pala cara-arriba y pala que EMPUJA hacia ella a
  // 0,25 m/s sostenido (velInst; p.vel queda bajo el carry 0,30 a propósito)
  const p = palaCaraArriba('player', 0, 0, 0.9, C + 0.65, 0, 0.05, 0);
  const b = bolaApoyada(p);
  p.velInst.set(0, 0.25, 0);                    // empuje hacia la bola (normal +y)
  const ev = [];
  let fDespegue = -1, exitDespegue = 0;
  for (let f = 0; f < 30; f++) {
    c05.stepPhysics(1 / 60, b, [p], ev);
    if (fDespegue < 0 && b.__ppRestIdx < 0) {
      fDespegue = f;
      const eHit = ev.find(e => e.type === 'paddle' && e.who === 'player');
      exitDespegue = eHit ? eHit.speed : -1;   // el evento lleva la SALIDA exacta
    }
  }
  aguja('P0-4 · el empuje sostenido DESPEGA (por debajo del carry)',
    fDespegue >= 0, 'nunca despegó en 30 frames');
  aguja('P0-4 · el despegue emite GOLPE contable (evento paddle who player)',
    ev.some(e => e.type === 'paddle' && e.who === 'player'),
    `ev=${JSON.stringify(ev.map(e => e.type))}`);
  aguja('P0-4 · la salida es SUAVE y en la normal (0,35 ≤ exit ≤ 1,84)',
    exitDespegue >= DIMS.paddleRestPushMin - 1e-3 &&
    exitDespegue <= DIMS.minExitSpeed * 0.8 + 1e-3,
    `exit=${exitDespegue.toFixed(3)}`);

  // TEMBLOR real (pico corto): 0,15 m/s UN frame — la fuga exponencial lo
  // disipa (2,5 mm < gap 10 mm) y el apoyo permanece
  const p3 = palaCaraArriba('player', 0, 0, 0.9, C + 0.65);
  const b3 = bolaApoyada(p3);
  p3.velInst.set(0, 0.15, 0);
  c05.stepPhysics(1 / 60, b3, [p3], []);
  p3.velInst.set(0, 0, 0);
  for (let f = 0; f < 60 && b3.__ppRestIdx >= 0; f++) c05.stepPhysics(1 / 60, b3, [p3], []);
  aguja('P0-4 · el temblor NO dispara el despegue (fuga exponencial)',
    b3.__ppRestIdx >= 0, `restIdx=${b3.__ppRestIdx}`);
}

/* — P0-5 · fondo de mesa: resolución por mínima penetración CON vertical — */
{
  // bola dentro de la banda (0,69..0,78) SUBIENDO cerca del fondo:
  // penDown (0,024) < penUp (0,066) < penX/penZ (0,78) ⇒ sale por ABAJO
  const b = bolaBase(0, 0.714, C, 0, 2.0, 0);
  const ev = [];
  c05.stepPhysics(1 / 60, b, [], ev);
  const botY = DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius;
  aguja('P0-5 · bola bajo el tablero sale por el FONDO (no de lado)',
    ev.some(e => e.type === 'table' && e.edge) &&
    Math.abs(b.pos.x) < 1e-6 && b.pos.y <= botY + 1e-6 && b.vel.y < 0,
    `pos=(${b.pos.x.toFixed(4)},${b.pos.y.toFixed(4)},${b.pos.z.toFixed(4)}) vel.y=${b.vel.y.toFixed(3)}`);
}

/* — P0-6a · el rescate nace FUERA de la huella del tablero ————————————— */
{
  const b = bolaBase(100, 0.1, 0);              // perdida en el más allá
  c05.stepPhysics(1 / 60, b, [], []);
  const zEsperado = C + DIMS.tableHalfLength + 0.5;
  aguja('P0-6a · rescate VISIBLE: detrás de la línea de fondo, a la altura del pecho',
    Math.abs(b.pos.x) < 1e-2 && Math.abs(b.pos.y - 1.0) < 1e-2 &&
    Math.abs(b.pos.z - zEsperado) < 1e-2,
    `pos=(${b.pos.x.toFixed(3)},${b.pos.y.toFixed(3)},${b.pos.z.toFixed(3)})`);
  aguja('P0-6a · el punto de rescate está FUERA de la huella',
    Math.abs(b.pos.z - C) > DIMS.tableHalfLength + DIMS.ballRadius);
}

/* — P0-2 · matemática de la altura absoluta del toss ———————————————————— */
{
  const vyAbs = (ySuelta) => {
    const dH = (DIMS.tableTopY + DIMS.ballRadius + 0.10) - ySuelta;
    return dH > 0 ? Math.sqrt(2 * Math.abs(DIMS.gravity) * dH) : 0;
  };
  aguja('P0-2 · soltar a 0,50 m (30 cm bajo el tablero) sube ≥ topR+0,10',
    vyAbs(0.5) >= 2.7 &&
    0.5 + vyAbs(0.5) * vyAbs(0.5) / (2 * Math.abs(DIMS.gravity)) >= DIMS.tableTopY + 0.099,
    `vyAbs=${vyAbs(0.5).toFixed(3)}`);
  aguja('P0-2 · soltar POR ENCIMA de la cota objetivo no añade nada (dH ≤ 0)',
    vyAbs(DIMS.tableTopY + DIMS.ballRadius + 0.11) === 0);
}

/* — agujas ESTÁTICAS: los seis correctivos viven en la fuente ———————————— */
{
  aguja('AGUJA c02 · carry 0,30 y muS 0,18 + tres constantes de empuje',
    /paddleRestCarry: 0\.30/.test(c02s) && /paddleRestMuS: 0\.18/.test(c02s) &&
    /paddleRestPushGap: 0\.010/.test(c02s) && /paddleRestPushOut: 0\.6/.test(c02s) &&
    /paddleRestPushMin: 0\.35/.test(c02s));
  aguja('AGUJA c05 · P0-3 la captura exige pala quieta (restPadSpeed²)',
    /pad\.vel\.lengthSq\(\) <= SERVE_TUNE\.restPadSpeed \* SERVE_TUNE\.restPadSpeed/.test(c05s) &&
    /P0-3/.test(c05s));
  aguja('AGUJA c05 · P0-4 el transporte acumula compresión y suelta con golpe',
    /__ppRestPush > DIMS\.paddleRestPushGap/.test(c05s) &&
    /Math\.exp\(-6 \* dt\)/.test(c05s) && /P0-4/.test(c05s));
  aguja('AGUJA c05 · P0-5 la banda insideSlab resuelve en 3 ejes',
    /eje = 'up'/.test(c05s) && /eje = 'down'/.test(c05s) && /P0-5/.test(c05s));
  aguja('AGUJA c05 · P0-6a rescate fuera de la huella',
    /tableCenterZ \+ DIMS\.tableHalfLength \+ 0\.5/.test(c05s) && /P0-6/.test(c05s));
  aguja('AGUJA c12 · P0-1 reanclaje del saque + aviso i18n por intento',
    c12s.includes("T('srv_reancla')") && /_srvReanclaAviso/.test(c12s) && /P0-1/.test(c12s));
  aguja('AGUJA c12 · P0-2 altura absoluta del lanzamiento asistido',
    /2 \* Math\.abs\(DIMS\.gravity\) \* dH/.test(c12s) && /P0-2/.test(c12s));
  aguja('AGUJA c12 · P0-6b guardián honesto (tossAlSuelo/tossMuertaEnMesa + hint_dropped)',
    /tossAlSuelo/.test(c12s) && /tossMuertaEnMesa/.test(c12s) &&
    c12s.includes("T('hint_dropped')") && /P0-6/.test(c12s));
  aguja('AGUJA i18n · srv_reancla en ES y EN',
    c00s.includes("srv_reancla: 'Bola recolocada · saca tras la línea de fondo'") &&
    c00s.includes("srv_reancla: 'Ball repositioned · serve behind the end line'"));
}

console.log(`\nARNÉS P0 r86 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

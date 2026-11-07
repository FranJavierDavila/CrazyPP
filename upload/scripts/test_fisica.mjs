#!/usr/bin/env node
/* CRAZY PING PONG · TESTS DE FÍSICA DETERMINISTAS (roadmap P1).
 * Ejecuta la FUENTE REAL (src/game/core/c04_fisica_ccd.js + c02_cfg_escena.js)
 * en Node — el mismo código que corre en el Quest — sobre escenarios fijos
 * y compara el HASH SHA256 de cada escenario con scripts/fisica_golden.json.
 *
 * Garantiza: si alguien toca la física (CCD, aerodinámica, botes, perks) y
 * cambia UNA décima de un decimal en un solo caso, el test se rompe.
 * Cero aleatoriedad: todos los escenarios son funciones puras del tiempo.
 *
 * Uso:
 *   node --no-warnings scripts/test_fisica.mjs            # verificar
 *   node --no-warnings scripts/test_fisica.mjs --update   # refrescar golden
 *                                                         # (solo tras un
 *                                                         #  cambio FÍSICO
 *                                                         #  intencional)
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

const RAIZ = new URL('..', import.meta.url).pathname;
const { c04, DIMS, SERVE_TUNE } = await (async () => {
  const m4 = await import(fileURLToPath(new URL('../src/game/core/c04_fisica_ccd.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c04: m4, DIMS: m2.DIMS, SERVE_TUNE: m2.SERVE_TUNE };
})();

const GOLDEN_PATH = new URL('./fisica_golden.json', import.meta.url).pathname;

/* — hashing canónico: JSON con decimales fijos ———————————————————— */
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

/* — 1 · SDF de la hoja (disco con canto redondeado) ———————————————— */
{
  const puntos = [];
  for (let x = -0.09; x <= 0.09; x += 0.03)
    for (let y = -0.09; y <= 0.09; y += 0.03)
      for (const z of [-0.006, 0, 0.006])
        puntos.push(c04.sdfBlade(x, y, z, 0.075, 0.004));
  escenario('sdfBlade.grid', puntos);
}

/* — 2 · barrido CCD bola↔hoja ————————————————————————————————————— */
{
  const R = 0.075, hT = 0.004, ballR = 0.02;
  const rayos = [
    // cara frontal directa (impacto centrado)
    [0, 0, 0.12, 0, 0, -0.12],
    // canto (llega de lado)
    [0.12, 0, 0, -0.12, 0, 0],
    // esquina redondeada
    [0.09, 0.09, 0.06, -0.18, -0.09, -0.12],
    // rasante que no llega (miss largo)
    [0, 0.30, 0.05, 0, -0.60, 0.05],
    // ya en contacto (t = 0)
    [0, 0, 0.035, 0, 0, -0.02],
    // segmento degenerado
    [0.01, 0.02, 0.06, 0.01, 0.02, 0.06],
    // cruzando el plano por detrás de la hoja
    [0.03, -0.02, -0.30, 0.03, -0.02, 0.30],
    // diagonal lejana (miss claro)
    [0.4, 0.4, 0.4, 0.6, 0.6, 0.6],
  ];
  const t = rayos.map(r => c04.sweepBallVsBlade(...r, R, hT, ballR));
  escenario('sweepBallVsBlade.rayos', t);
  const tc = [
    [0, 0.10, 0, 0, -0.10, 0, 0.02, 0.11, 0.012, 0.02],   // cruza la cápsula
    [0, 0.16, 0, 0, 0.02, 0, 0.02, 0.11, 0.012, 0.02],    // entra por arriba
    [0.2, 0.05, 0, -0.2, 0.05, 0, 0.02, 0.11, 0.012, 0.02], // miss lateral
    [0, 0.05, 0, 0, 0.05, 0.001, 0.02, 0.11, 0.012, 0.02],  // ya dentro
  ];
  escenario('sweepBallVsCapsuleY.rayos', tc.map(r => c04.sweepBallVsCapsuleY(...r)));
}

/* — 3 · normales locales (cara/canto/esquina) ————————————————————— */
{
  const n = new THREE.Vector3();
  const casos = [[0, 0, 0.0041], [0.08, 0, 0], [0.074, 0.004, 0.0038],
                 [0, -0.05, -0.0041], [0.05, 0.05, 0.002]];
  const fuera = casos.map(p => Array.from(c04.bladeNormalLocal(...p, 0.075, 0.004, n).toArray()));
  escenario('bladeNormalLocal.casos', fuera);
}

/* — 4 · seguimiento del mando (swing sintético de 120 frames) ——————— */
{
  const ps = c04.createPaddleSim('player', 0);
  const dt = 1 / 120;
  const q = new THREE.Quaternion(), e = new THREE.Euler();
  const pos = new THREE.Vector3();
  for (let i = 0; i < 120; i++) {
    const s = i / 119;
    // swing: arco en XZ con subida en Y + rotación de muñeca (Y luego Z)
    pos.set(0.15 - 0.30 * s, 0.9 + 0.25 * Math.sin(s * Math.PI), -0.2 + 0.35 * s);
    e.set(s * 1.1, s * 2.0, 0.3 * Math.sin(s * 3.0));
    q.setFromEuler(e);
    c04.updatePaddleSim(ps, pos, q, i * dt, dt);
  }
  c04.setPaddleBasis(ps, q);
  escenario('paddleSim.swing120', {
    vel: ps.vel.toArray(), velInst: ps.velInst.toArray(), omega: ps.omega.toArray(),
    normal: ps.normal.toArray(), right: ps.right.toArray(), up: ps.up.toArray(),
    prevT: ps.prevT, buf: ps.velBuf.length, quatInit: ps.quatInit,
  });
}

/* — 5 · aerodinámica (480 substeps fijos) —————————————————————————— */
{
  const vel = new THREE.Vector3(3.0, -4.0, -6.0);
  const spin = new THREE.Vector3(0, 80, 0);
  const h = 1 / 240;
  for (let i = 0; i < 480; i++) c04.applyAerodynamics(vel, spin, h);
  escenario('aero.topspin480', { vel: vel.toArray(), spin: spin.toArray() });
  const vel2 = new THREE.Vector3(-6, -1, 4), spin2 = new THREE.Vector3(30, -20, 55);
  for (let i = 0; i < 480; i++) c04.applyAerodynamics(vel2, spin2, h, 0.30);
  escenario('aero.bomba480.dragMul', { vel: vel2.toArray(), spin: spin2.toArray() });
}

/* — 6 · botes en mesa (slip-coupled v3.0.5-FIS1) ——————————————————— */
{
  const casos = [
    // topspin puro: patea hacia delante
    { vel: [1.2, -3.5, -2.0], spin: [0, 0, 90], impact: 3.5 },
    // backspin: frena en seco
    { vel: [1.0, -2.8, -1.0], spin: [0, 0, -70], impact: 2.8 },
    // lateral: desvía
    { vel: [0.4, -4.2, -3.0], spin: [65, 0, 10], impact: 4.2 },
    // impacto suave (grip mínimo)
    { vel: [0.2, -0.8, -0.3], spin: [0, 0, 20], impact: 0.8 },
  ];
  const fuera = casos.map(c => {
    const v = new THREE.Vector3(...c.vel), s = new THREE.Vector3(...c.spin);
    c04.bounceOnTable(v, s, c.impact);
    return { vel: v.toArray(), spin: s.toArray() };
  });
  escenario('bounceOnTable.casos', fuera);
  const v3 = new THREE.Vector3(1, -2, -1), s3 = new THREE.Vector3(10, 0, -40);
  c04.applyBounceSpin(v3, s3);
  escenario('applyBounceSpin.caso', { vel: v3.toArray(), spin: s3.toArray() });
}

/* — 7 · perks de pala (skin por defecto: clasica) —————————————————— */
{
  escenario('paddlePerkFor.clasica', [
    c04.paddlePerkFor('player', 1), c04.paddlePerkFor('player', -1),
    c04.paddlePerkFor('ai', 1),
  ]);
}

/* — 8 · constantes de tuning (cualquier cambio de física SUENA aquí) — */
{
  escenario('tuning.constantes', {
    CCD: { eps: c04.CCD_TUNE.eps, maxIter: c04.CCD_TUNE.maxIter, glaze: c04.CCD_TUNE.glaze },
    DIMS: {
      ballRadius: DIMS.ballRadius, airDragK: DIMS.airDragK, magnus: DIMS.magnus,
      spinDecayAir: DIMS.spinDecayAir, tableRestitution: DIMS.tableRestitution,
      bounceGripMin: DIMS.bounceGripMin, bounceGripMax: DIMS.bounceGripMax,
      bounceSpinKick: DIMS.bounceSpinKick, paddleVelClamp: DIMS.paddleVelClamp,
    },
    SERVE: { velWindow: SERVE_TUNE.velWindow, velLerp: SERVE_TUNE.velLerp },
  });
}

/* — verificación contra el golden —————————————————————————————————— */
const modoUpdate = process.argv.includes('--update');
if (modoUpdate) {
  writeFileSync(GOLDEN_PATH, JSON.stringify({
    nota: 'HASHES de física determinista (test_fisica.mjs). Refrescar SOLO con un cambio físico intencional: node --no-warnings scripts/test_fisica.mjs --update',
    version: JSON.parse(readFileSync(new URL('../src/game/VERSION.json', import.meta.url).pathname, 'utf-8')).version,
    hashes: resultados,
  }, null, 2) + '\n');
  console.log(`\nGOLDEN REFRESCADO (${Object.keys(resultados).length} escenarios) → fisica_golden.json`);
  process.exit(0);
}

if (!existsSync(GOLDEN_PATH)) {
  console.log('\nFALLO: no existe fisica_golden.json — genera el primero con --update');
  process.exit(1);
}
const golden = JSON.parse(readFileSync(GOLDEN_PATH, 'utf-8')).hashes;
const faltan = Object.keys(resultados).filter(k => !(k in golden));
const sobran = Object.keys(golden).filter(k => !(k in resultados));
const distintos = Object.keys(resultados).filter(k => k in golden && golden[k] !== resultados[k]);
for (const k of distintos) console.log(`  ✗ FÍSICA CAMBIÓ: ${k} (golden ${golden[k]} ≠ actual ${resultados[k]})`);
for (const k of faltan) console.log(`  ✗ escenario nuevo SIN golden: ${k}`);
for (const k of sobran) console.log(`  ✗ escenario retirado que sigue en el golden: ${k}`);
console.log(`\nRESULTADO: ${Object.keys(resultados).length} escenarios · ${distintos.length + faltan.length + sobran.length} desviaciones`);
process.exit((distintos.length || faltan.length || sobran.length) ? 1 : 0);

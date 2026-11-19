#!/usr/bin/env node
/* =====================================================================
 * ARNÉS ITTF §12.1 (r90) — adopción real del estudio de física
 * ---------------------------------------------------------------------
 * Tres pruebas del §12.1 corriendo la FÍSICA REAL del motor
 * (c05.stepPhysics + c04.applyAerodynamics), no réplicas:
 *
 *   T1 REBOTE ITTF — caída libre de 300 mm sobre el tablero, bola parada
 *      y sin giro: el apex del rebote ∈ [230, 260] mm (regla ITTF).
 *      Calibra la curva de restitución vertical de la mesa.
 *   T2 VELOCIDAD TERMINAL — caída larga con arrastre cuadrático real:
 *      |v_t − 8,8| ≤ 0,2 m/s (región de crisis de arrastre, Cd≈0,445).
 *   T3 TÚNEL 10 000 BOLAS — 10 000 golpes dirigidos generados por la
 *      herramienta de la casa (computeShotVelocityReal) con objetivos,
 *      tiempos y efectos aleatorios sembrados, volando por stepPhysics
 *      completo: ≥99 % cruzan la red y botan en campo rival · 0 NaN ·
 *      vmax ≤ 16 · 0 penetraciones bajo la losa · 0 túneles de red.
 *
 * Uso: node scripts/test_fisica_ittf.mjs [--rapido]   (--rapido: 2 000 bolas)
 * Salida: ITTF §12.1 · N OK · N FALLOS (exit 1 si algo falla).
 * ===================================================================== */
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

globalThis.window = globalThis.window || globalThis;   // c00 en Node

/* c05 tiene jitter DELIBERADO en el golpe de canto (v3.0.5 P1): PRNG
 * sembrado (mulberry32) para que el túnel sea determinista. */
let _seed = 0xC0FFEE | 0;
Math.random = () => {
  _seed = (_seed + 0x6d2b79f5) | 0;
  let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const { c05, DIMS } = await (async () => {
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c05: m5, DIMS: m2.DIMS };
})();

let ok = 0, fails = 0;
const dije = (nombre, bien, detalle) => {
  if (bien) { ok++; console.log(`  ✓ ${nombre}${detalle ? ' · ' + detalle : ''}`); }
  else { fails++; console.log(`  ✗ FALLO ${nombre}${detalle ? ' · ' + detalle : ''}`); }
};

const topR = DIMS.tableTopY + DIMS.ballRadius;
const C = DIMS.tableCenterZ;

const bolaNueva = () => ({
  pos: new THREE.Vector3(),
  vel: new THREE.Vector3(),
  spin: new THREE.Vector3(),
  dragMul: 1,
  ppEfecto: false,
  ignoreNet: false,
  ignoreTable: false,
  __ppRestIdx: -1,
  __serveGrace: 0,
});

/* ===================== T1 · REBOTE ITTF (300 → 230-260 mm) ============ */
{
  const ball = bolaNueva();
  ball.pos.set(0.05, topR + 0.300, C - 0.5);   // sobre el tablero, 300 mm
  const events = [];
  const DT = 1 / 120;
  let botado = false, apex = 0, vyAntes = 0;
  for (let i = 0; i < 3 * 120; i++) {
    vyAntes = ball.vel.y;
    c05.stepPhysics(DT, ball, [], events);
    if (!botado) {
      const bote = events.find(ev => ev.type === 'table' && !ev.edge);
      if (bote) botado = true;
    } else {
      if (ball.pos.y - topR > apex) apex = ball.pos.y - topR;
      if (ball.vel.y < 0 && i > 12) break;      // pasó el apex del rebote
    }
    events.length = 0;
  }
  const mm = apex * 1000;
  dije('T1 rebote ITTF · apex ∈ [230, 260] mm tras caída de 300 mm',
    botado && mm >= 230 && mm <= 260,
    botado ? `apex ${mm.toFixed(1)} mm` : 'sin bote registrado');
}

/* ===================== T2 · VELOCIDAD TERMINAL (8,8 m/s) ============= */
{
  const k = DIMS.airDragK, g = -DIMS.gravity;
  const vtAnalitica = Math.sqrt(g / k);
  dije('T2 v_t analítica √(g/k) ∈ [8.6, 9.0]',
    vtAnalitica >= 8.6 && vtAnalitica <= 9.0, `v_t = ${vtAnalitica.toFixed(3)} m/s (k=${k})`);

  const ball = bolaNueva();
  ball.pos.set(8, 40, 8);                       // lejos de mesa y red
  const DT = 1 / 120;
  let vmax = 0, vFinal = 0;
  for (let i = 0; i < 15 * 120; i++) {
    c05.stepPhysics(DT, ball, [], []);
    const sp = ball.vel.length();
    if (sp > vmax) vmax = sp;
    vFinal = sp;
    if (ball.pos.y < DIMS.ballRadius + 0.005 && ball.vel.y <= 0) break; // suelo
  }
  dije('T2 v_t simulada (caída real de 40 m) ∈ [8.6, 9.0]',
    vmax >= 8.6 && vmax <= 9.0, `vmax ${vmax.toFixed(3)} · final ${vFinal.toFixed(3)}`);
}

/* ===================== T3 · TÚNEL 10 000 BOLAS ======================= */
{
  const rapido = process.argv.includes('--rapido');
  const N = rapido ? 2000 : 10000;
  const DT = 1 / 120;
  let validos = 0, nan = 0, vmax = 0, bajoLosa = 0, tunelRed = 0, muertas = 0;

  for (let n = 0; n < N; n++) {
    const from = new THREE.Vector3(
      (Math.random() - 0.5) * 0.7,
      0.85 + Math.random() * 0.5,
      C + DIMS.tableHalfLength + 0.20 + Math.random() * 0.15);
    const target = new THREE.Vector3(
      (Math.random() - 0.5) * 1.8 * DIMS.tableHalfWidth,
      topR,
      C - DIMS.tableHalfLength * (0.25 + 0.7 * Math.random()));
    const spin = new THREE.Vector3();
    const modo = Math.random();
    if (modo < 0.45) spin.set(-(30 + Math.random() * 30), 0, 0);            // top
    else if (modo < 0.65) spin.set(20 + Math.random() * 25, 0, 0);          // back
    else if (modo < 0.85) spin.set(0, (Math.random() - 0.5) * 70, 0);       // side
    const v0 = c05.computeShotVelocityReal(from, target, 0.45 + Math.random() * 0.4, 14, spin);

    const ball = bolaNueva();
    ball.pos.copy(from);
    ball.vel.copy(v0);
    ball.spin.copy(spin);
    const events = [];
    let vivo = true, valide = false, zAntes = ball.pos.z, t = 0;
    while (vivo && t < 2.5) {
      c05.stepPhysics(DT, ball, [], events);
      t += DT;
      const sp = ball.vel.length();
      if (sp > vmax) vmax = sp;
      if (!Number.isFinite(ball.pos.x + ball.pos.y + ball.pos.z + sp)) { nan++; break; }
      // penetración bajo la losa (el resolvedor debe impedirlo)
      if (Math.abs(ball.pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius &&
          Math.abs(ball.pos.z - C) <= DIMS.tableHalfLength + DIMS.ballRadius &&
          ball.pos.y < DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius - 1e-4) bajoLosa++;
      // túnel de red: cruza el plano de la red por DEBAJO del canto sin evento
      if ((ball.pos.z - C) * (zAntes - C) < 0 &&
          ball.pos.y < DIMS.netTopY - DIMS.ballRadius &&
          !events.some(ev => ev.type === 'net')) tunelRed++;
      zAntes = ball.pos.z;
      for (const ev of events) {
        if (ev.type === 'table' && ev.side === 'ai' && !ev.edge) valide = true;   // botó en campo rival
        if (ev.type === 'net' || ev.type === 'table' && ev.side === 'player') vivo = false;
      }
      events.length = 0;
      if (ball.pos.y < DIMS.ballRadius + 0.005 && ball.vel.y <= 0) { vivo = false; muertas++; }
      if (valide) vivo = false;
    }
    if (valide) validos++;
  }

  dije('T3 túnel · ≥99 % cruzan la red y botan en campo rival',
    validos >= N * 0.99, `${validos}/${N} válidos`);
  dije('T3 túnel · 0 NaN', nan === 0, `${nan} NaN`);
  dije('T3 túnel · vmax ≤ 16 m/s', vmax <= 16, `vmax ${vmax.toFixed(2)} m/s`);
  dije('T3 túnel · 0 penetraciones bajo la losa', bajoLosa === 0, `${bajoLosa}`);
  dije('T3 túnel · 0 túneles de red', tunelRed === 0, `${tunelRed}`);
}

console.log(`\nITTF §12.1 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

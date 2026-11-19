#!/usr/bin/env node
/* =====================================================================
 * ARNÉS CADENA CINEMÁTICA r91 — el golpe humano del rival
 * ---------------------------------------------------------------------
 * 1. QUÍNTICO (mínimo jerk): extremos y velocidades EXACTOS, sin NaN.
 * 2. IK 2 HUESOS: codo en rango anatómico, alcance clamped (objetivo
 *    imposible ⇒ estirado, nunca NaN), polo del codo coherente.
 * 3. FASES: reacción+carga+golpeo == tBall exacto (el pico del golpeo
 *    cae en la llegada de la bola); acompañamiento/recuperación en rango.
 * 4. CONTINUIDAD: el re-anclaje parte del estado exacto (cur/vel) — el
 *    salto de velocidad entre el plan viejo y el nuevo es ≈ 0.
 * 5. VARIABILIDAD FUNCIONAL: dos planes con la misma entrada → amplitudes
 *    distintas (poses distintas) pero el MISMO contacto (0 mm).
 * 6. IMPACTO: cadenaContacto sincroniza el golpe al punto real con v1
 *    alineada a la salida de la bola (el fin del «empujón» invisible).
 * 7. FÍSICA ÚNICA POR MODALIDAD: determinismo de stepPhysics (mismo estado
 *    ⇒ misma trayectoria, entrenamiento y partida comparten motor) y
 *    0 overrides de constantes físicas fuera de c02.
 * ===================================================================== */
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { readFileSync } from 'node:fs';

globalThis.window = globalThis.window || globalThis;   // c00 en Node

const { c06, DIMS } = await (async () => {
  const m6 = await import(fileURLToPath(new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c06: m6, DIMS: m2.DIMS };
})();

let ok = 0, fails = 0;
const dije = (nombre, bien, detalle) => {
  if (bien) { ok++; console.log(`  ✓ ${nombre}${detalle ? ' · ' + detalle : ''}`); }
  else { fails++; console.log(`  ✗ FALLO ${nombre}${detalle ? ' · ' + detalle : ''}`); }
};

const AI_HOME = () => new THREE.Vector3(0, 1.0, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.55);
const mkAI = () => new c06.OpponentAI({ missBase: 0.05 }, -1, AI_HOME());
const CONTACT = () => new THREE.Vector3(0.18, 1.02, DIMS.tableCenterZ - DIMS.tableHalfLength + 0.25);
const VOUT = () => new THREE.Vector3(0.35, 0.9, 6.2);

/* ---------- 1 · quíntico ---------- */
{
  const p0 = new THREE.Vector3(0, 1, -2.4), p1 = new THREE.Vector3(0.4, 1.1, -2.0);
  const v0 = new THREE.Vector3(1, 0, 0), v1 = new THREE.Vector3(0, 0.5, -1);
  const out = new THREE.Vector3(), vel = new THREE.Vector3(), T = 0.25;
  c06.mjQuintic(0, p0, v0, p1, v1, T, out);
  const e0 = out.distanceTo(p0) < 1e-9;
  c06.mjQuintic(1, p0, v0, p1, v1, T, out);
  const e1 = out.distanceTo(p1) < 1e-9;
  c06.mjQuinticVel(0, p0, v0, p1, v1, T, vel);
  const v0ok = vel.distanceTo(v0) < 1e-9;
  c06.mjQuinticVel(1, p0, v0, p1, v1, T, vel);
  const v1ok = vel.distanceTo(v1) < 1e-9;
  let nan = 0;
  for (let i = 0; i <= 60; i++) {
    c06.mjQuintic(i / 60, p0, v0, p1, v1, T, out);
    c06.mjQuinticVel(i / 60, p0, v0, p1, v1, T, vel);
    if (!Number.isFinite(out.x + out.y + out.z + vel.x + vel.y + vel.z)) nan++;
  }
  dije('quíntico · extremos y velocidades exactos + 0 NaN',
    e0 && e1 && v0ok && v1ok && nan === 0, `${nan} NaN`);
  // mínimo jerk (v0=v1=0): velocidad nula en ambos extremos
  const z0 = new THREE.Vector3(), z1 = new THREE.Vector3();
  c06.mjQuinticVel(0, p0, z0, p1, z1, T, vel);
  const m0 = vel.length() < 1e-9;
  c06.mjQuinticVel(1, p0, z0, p1, z1, T, vel);
  const m1 = vel.length() < 1e-9;
  dije('quíntico · mínimo jerk (v=0 en los extremos con v0=v1=0)', m0 && m1);
}

/* ---------- 2 · IK ---------- */
{
  const S = new THREE.Vector3(0, 1.16, -2.57);
  const E = new THREE.Vector3();
  const alcanzable = new THREE.Vector3(0.15, 1.02, -2.30);
  const r1 = c06.solveArmIK(S, alcanzable, 0.26, 0.24, new THREE.Vector3(0, -1, 0), E);
  const d1 = E.distanceTo(alcanzable) < 1e-6;   // alcanzable ⇒ E-W exacto... (E es codo; W debe salir a dist)
  const inRange = r1.flex >= 25 && r1.flex <= 145;
  const imposible = new THREE.Vector3(0.8, 1.8, -1.2);
  const r2 = c06.solveArmIK(S, imposible, 0.26, 0.24, new THREE.Vector3(0, -1, 0), E);
  const clampOk = Math.abs(r2.dist - 0.94 * 0.50) < 1e-9;
  let nan = 0;
  for (let i = 0; i < 200; i++) {
    const W = new THREE.Vector3((Math.random() - 0.5) * 2, Math.random() * 2, -2.6 + Math.random() * 1.2);
    c06.solveArmIK(S, W, 0.26, 0.24, new THREE.Vector3(0, -1, 0), E);
    if (!Number.isFinite(E.x + E.y + E.z)) nan++;
  }
  dije('IK · codo en rango anatómico [25°,145°] + objetivo imposible clamped + 0 NaN',
    inRange && clampOk && nan === 0, `flex ${r1.flex.toFixed(1)}° · dist ${r2.dist.toFixed(3)} · ${nan} NaN${d1 ? '' : ' (E-W: revisar)'}`);
}

/* ---------- 3 · fases y timing ---------- */
{
  const ai = mkAI();
  const C = CONTACT();
  ai.planCadena(C, 0.70, 'drive', 1);
  const sgs = ai.chain.segs;
  const tHit = sgs[0].T + sgs[1].T + sgs[2].T;
  const durOk = Math.abs(tHit - 0.70) < 1e-9;
  const fases = sgs.map(s => s.phase).join(',');
  const ordenOk = fases === 'react,back,strike,follow,recover';
  const strikeFin = sgs[2].p1.distanceTo(C) < 1e-9;
  dije('fases · reacción+carga+golpeo == tBall exacto y orden correcto',
    durOk && ordenOk && strikeFin, `${tHit.toFixed(3)} s · ${fases}`);
}

/* ---------- 4 · continuidad en el re-anclaje ---------- */
{
  const ai = mkAI();
  const C = CONTACT();
  ai.predictValid = true;
  ai.predict.copy(C); ai.predictT = 0.70;
  ai.planCadena(C, 0.70, 'drive', 1);
  // avanza 0,20 s de reacción
  for (let i = 0; i < 24; i++) ai.updateCadena(1 / 120);
  const vAntes = ai.chain.vel.clone();
  // la predicción se refina 6 cm más arriba
  const C2 = C.clone(); C2.y += 0.06;
  ai.predict.copy(C2); ai.predictT = 0.55;
  ai.updateCadena(1 / 120);                     // dispara el re-anclaje
  const salto = ai.chain.vel.distanceTo(vAntes);
  dije('continuidad · re-anclaje con salto de velocidad ≈ 0 (< 0,15 m/s)',
    salto < 0.15, `salto ${salto.toFixed(4)} m/s`);
  // el plan re-anclado corre LIMPIO hasta el final natural del stroke:
  // vivo en plena recuperación (0,85 s) y nulo tras el stroke completo
  let t = 0, vivoT1 = null, vivoFin = null;
  while (ai.chain && t < 2.0) { ai.updateCadena(1 / 120); t += 1 / 120;
    if (t > 0.60 && vivoT1 === null) vivoT1 = ai.chain !== null;
    if (t > 0.85 && vivoFin === null) vivoFin = ai.chain !== null;
  }
  dije('continuidad · el plan vive hasta el FIN del stroke (sin muerte NaN)',
    vivoT1 === true && vivoFin === true && ai.chain === null && t > 0.95 && t < 1.9,
    `vivo a 0,60 s: ${vivoT1} · vivo a 0,85 s: ${vivoFin} · fin ${t.toFixed(2)} s`);
}

/* ---------- 5 · variabilidad funcional ---------- */
{
  const a1 = mkAI(), a2 = mkAI();
  const C = CONTACT();
  a1.planCadena(C, 0.70, 'drive', 1);
  a2.planCadena(C, 0.70, 'drive', 1);
  const B1 = a1.chain.segs[1].p1, B2 = a2.chain.segs[1].p1;
  const difPose = B1.distanceTo(B2) > 0.002;                    // poses distintas
  const mismoContacto = a1.chain.contact.distanceTo(a2.chain.contact) < 1e-9;  // mismo punto
  dije('variabilidad · poses distintas con el MISMO contacto', difPose && mismoContacto,
    `Δ backswing ${(B1.distanceTo(B2) * 100).toFixed(1)} mm`);
}

/* ---------- 6 · impacto sincronizado ---------- */
{
  const ai = mkAI();
  const C = CONTACT();
  ai.planCadena(C, 0.70, 'drive', 1);
  for (let i = 0; i < 40; i++) ai.updateCadena(1 / 120);   // dentro de la carga
  const CR = C.clone(); CR.x += 0.04;                      // punto real del barrido
  const v = VOUT();
  ai.cadenaContacto(CR.x, CR.y, CR.z, v);
  const s0 = ai.chain.segs[0];
  const finOk = s0.phase === 'strike' && s0.p1.distanceTo(CR) < 1e-9;
  const vOk = s0.v1.distanceTo(v.clone().multiplyScalar(c06.CADENA_GOLPE.drive.vPeakMul)) < 1e-9;
  const tRem = s0.T + ai.chain.segs[1].T + ai.chain.segs[2].T;
  dije('impacto · strike termina en el punto REAL con v1 alineada a la salida',
    finOk && vOk, `T_strike ${s0.T.toFixed(3)} s · plan ${tRem.toFixed(2)} s`);
}

/* ---------- 7 · física única por modalidad ---------- */
{
  // determinismo: el mismo estado inicial da la MISMA trayectoria (el motor
  // es UNO — entrenamiento y partida corren el mismo stepPhysics)
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const cor1 = [], cor2 = [];
  for (const cor of [cor1, cor2]) {
    const ball = {
      pos: new THREE.Vector3(0.12, DIMS.tableTopY + 0.4, DIMS.tableCenterZ + 1.2),
      vel: new THREE.Vector3(-0.3, 2.2, -4.4),
      spin: new THREE.Vector3(-25, 4, 0),
      dragMul: 1, ppEfecto: false, ignoreNet: false, __ppRestIdx: -1,
    };
    for (let i = 0; i < 180; i++) {
      m5.stepPhysics(1 / 120, ball, [], []);
      cor.push(ball.pos.x + ball.pos.y * 3.1 + ball.pos.z * 7.7);
    }
  }
  let iden = true;
  for (let i = 0; i < cor1.length; i++)
    if (Math.abs(cor1[i] - cor2[i]) > 1e-12) { iden = false; break; }
  dije('física única · mismo estado ⇒ misma trayectoria (motor compartido)', iden);

  // 0 overrides de constantes físicas fuera de c02 (la unificación por
  // construcción: ninguna modalidad toca restitución/drag/gravedad en vivo)
  const leer = f => readFileSync(fileURLToPath(new URL(f, import.meta.url)), 'utf-8');
  let overrides = 0;
  for (const f of ['../src/game/core/c04_fisica_ccd.js', '../src/game/core/c05_colisiones_ia_golpeo.js',
    '../src/game/core/c06_logros_stats_ia_rival.js', '../src/game/core/c12_pingponggame.js',
    '../src/game/core/c13_ui_arranque.js']) {
    const t = leer(f);
    const hits = t.match(/DIMS\.(tableRestitution|airDragK|gravity|magnus|tableFriction|paddleRestitution)\s*=[^=]/g);
    if (hits) { overrides += hits.length; console.log(`    · override en ${f}: ${hits.join(' ')}`); }
  }
  dije('física única · 0 overrides de constantes físicas fuera de c02', overrides === 0,
    `${overrides} encontrados`);
}

console.log(`\nCADENA r91 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

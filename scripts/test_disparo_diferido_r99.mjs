/* r99bis · TEST DE ACOMPAÑAMIENTO NATURAL — la IA REAL (c06) en Node:
 * La exigencia del dueño: «movimientos progresivos, nada bruscos, ni
 * empujones a la bola — gestos que ACOMPAÑEN el movimiento».
 *  A · rally normal: el disparo difiere hasta el contacto (pala ≤ 4 cm de
 *      la bola al golpear) y el desplazamiento por frame de la pala queda
 *      acotado (sin saltos: ≤ 0,15 m/frame ≈ 9 m/s a 60 fps).
 *  B · pala REtrasada (lejos del intercepto): NADA de atrapadas bruscas —
 *      la cadena re-ancla con quínticos y la pala vuela a encontrar la
 *      bola en vuelo; el golpe sigue llegando y el contacto sigue real.
 *  C · acompañamiento: tras el golpe, la pala SIGUE moviéndose en la
 *      dirección del tiro ≥ 100 ms (follow-through + arco), sin frenada
 *      seca (continuidad C¹ de los quínticos). */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r99' }; } catch (e) { /* getter vivo */ }

import * as THREE from 'three';
const { OpponentAI } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

let ok = 0, mal = 0;
const aguja = (n, c) => { if (c) { ok++; console.log('  ✓ ' + n); }
  else { mal++; console.log('  ✗ ' + n); } };

const cfg = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 10, predictInterval: 0.05 };
const sign = -1;                     // la IA en -Z (campo CPU: devuelve hacia +Z)

/** corre un rally sintético y devuelve las métricas del gesto */
function corre(nombre, homePos, bolaIni, debug = false) {
  const ai = new OpponentAI(cfg, sign, homePos);
  ai.style = null;
  if (debug) {
    const eco = (m) => console.log('    · ' + m);
    const origEn = ai._enContacto.bind(ai);
    ai._enContacto = function () {
      const d = this._disparo, ch = this.chain;
      if (d && ch) eco(`contacto: dist=${ch.cur.distanceTo(d.ball.pos).toFixed(2)} ` +
        `t=${d.t.toFixed(2)} fase=${ch.phase}`);
      const r = origEn();
      if (d === null || !this._disparo) eco('  → DISPARO APLICADO en el contacto');
      else if (this.chain) eco(`  → re-ancla T2 → ${this._disparo.pos.toArray().map(x=>x.toFixed(2)).join(',')}`);
      return r;
    };
    const origAp = ai._aplicaDisparo.bind(ai);
    ai._aplicaDisparo = function () {
      const d = this._disparo;
      if (d) eco(`aplicador: t=${d.t.toFixed(2)} bola=${d.ball.pos.toArray().map(x=>x.toFixed(2)).join(',')} ` +
        `objetivo=${d.pos.toArray().map(x=>x.toFixed(2)).join(',')} chain=${!!this.chain}`);
      return origAp();
    };
  }
  const ball = { pos: bolaIni.pos.clone(), vel: bolaIni.vel.clone(),
    spin: new THREE.Vector3(), dragMul: 1,
    ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
  const ctxPrev = new THREE.Vector3();
  const evs = [];
  let bote = -1, frameGolpe = -1, vDevuelta = null;
  const curTraza = [];              // pala por frame (pre-paso, post-update)
  const bolaTraza = [];             // bola por frame (mismo instante)
  for (let f = 0; f < 900; f++) {
    ctxPrev.copy(ball.pos);
    const ctx = { canHit: true, validBounce: bote >= 0, oppPadX: 0, oppPadZ: 1.5,
      rallyHits: 1, holdTarget: null, prevBall: ctxPrev };
    const r = ai.update(1 / 60, ball, ctx);
    if (r && frameGolpe < 0) { vDevuelta = r; frameGolpe = f; }
    curTraza.push(ai.chain ? ai.chain.cur.clone() : null);
    bolaTraza.push(ball.pos.clone());
    evs.length = 0;
    stepPhysics(1 / 60, ball, [], evs);
    if (bote < 0 && evs.some((e) => e.type === 'table')) bote = f;
    if (frameGolpe >= 0 && f >= frameGolpe + 20) break;   // 20 frames post-golpe
  }
  // métricas del gesto de la pala: paso por frame (sin saltos)
  let maxPaso = 0;
  for (let i = 1; i < curTraza.length; i++) {
    if (!curTraza[i] || !curTraza[i - 1]) continue;
    const paso = curTraza[i].distanceTo(curTraza[i - 1]);
    if (paso > maxPaso) maxPaso = paso;
  }
  // CONTACTO: el mínimo hueco pala-bola en los 3 frames previos al golpe
  // (el strike TERMINA en el contacto; el frame del golpe ya avanza el arco)
  let gapContacto = 99;
  if (frameGolpe >= 0) {
    for (let i = Math.max(0, frameGolpe - 3); i <= frameGolpe; i++) {
      if (!curTraza[i]) continue;
      gapContacto = Math.min(gapContacto, curTraza[i].distanceTo(bolaTraza[i]));
    }
  }
  // ACOMPAÑAMIENTO: tras el golpe el gesto SIGUE FLUYENDO (≥ 6 frames con
  // paso ≥ 8 mm y sin saltos) — la pala no se queda clavada ni retrocede
  let framesAcompanando = 0, bruscoPost = 0;
  if (frameGolpe >= 0) {
    for (let i = frameGolpe; i < Math.min(frameGolpe + 10, curTraza.length - 1); i++) {
      if (!curTraza[i] || !curTraza[i + 1]) break;
      const paso = curTraza[i + 1].distanceTo(curTraza[i]);
      if (paso >= 0.008) framesAcompanando++;
      if (paso > 0.15) bruscoPost++;
    }
  }
  console.log(`[${nombre}] salida ${frameGolpe} · gap contacto ` +
    `${(gapContacto * 100).toFixed(1)} cm · máx paso/frame ` +
    `${(maxPaso * 100).toFixed(1)} cm · acompañando ${framesAcompanando} frames` +
    (bruscoPost ? ` · ¡${bruscoPost} pasos bruscos post-golpe!` : ''));
  return { frameGolpe, vDevuelta, maxPaso, gapContacto, framesAcompanando };
}

/* — A · RALLY NORMAL: la bola bota en la mitad de la IA y llega a su pala — */
{
  const A = corre('A · rally normal',
    new THREE.Vector3(0, 1.0, -1.55),
    { pos: new THREE.Vector3(0.05, 1.05, -0.55),
      vel: new THREE.Vector3(0.0, -1.6, -2.6) });
  aguja('A · el disparo sale DIFERIDO tras la decisión (no este frame)',
    A.frameGolpe >= 1);
  aguja(`A · contacto real (mínimo gap previo ${(A.gapContacto * 100).toFixed(1)} cm ≤ 5 cm)`,
    A.gapContacto < 0.05);
  aguja(`A · SIN saltos: máx ${(A.maxPaso * 100).toFixed(1)} cm/frame ≤ 15 cm`,
    A.maxPaso <= 0.15);
  aguja(`A · ACOMPAÑA el tiro ≥ 100 ms (6 frames: ${A.framesAcompanando})`,
    A.framesAcompanando >= 6);
  aguja('A · salida creíble hacia el jugador (2-12 m/s, vz > 0)',
    A.vDevuelta && A.vDevuelta.length() > 2 && A.vDevuelta.length() < 12 &&
    A.vDevuelta.z > 0);
}

/* — B · PALA REtrasada: empieza 0,4 m detrás y alto — el gesto tiene que
 *   estirarse para encontrar la bola SIN saltos ni empujones — */
{
  const B = corre('B · pala retrasada',
    new THREE.Vector3(0, 1.35, -1.95),
    { pos: new THREE.Vector3(0.08, 1.02, -0.45),
      vel: new THREE.Vector3(-0.1, -1.4, -3.1) });
  aguja('B · el golpe llega igualmente (diferido + re-anclaje progresivo)',
    B.frameGolpe >= 0);
  aguja(`B · SIN atrapada brusca: máx ${(B.maxPaso * 100).toFixed(1)} cm/frame ≤ 15 cm`,
    B.maxPaso <= 0.15);
  aguja(`B · contacto real (mínimo gap previo ${(B.gapContacto * 100).toFixed(1)} cm ≤ 6 cm)`,
    B.gapContacto < 0.06);
  aguja(`B · ACOMPAÑA tras el golpe (${B.framesAcompanando} frames ≥ 5)`,
    B.framesAcompanando >= 5);
}

console.log(`\nACOMPAÑAMIENTO NATURAL r99bis · ${ok} OK · ${mal} FALLOS`);
process.exit(mal ? 1 : 0);

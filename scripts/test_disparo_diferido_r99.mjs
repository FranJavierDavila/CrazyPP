/* r99 · TEST DEL DISPARO DIFERIDO — la IA REAL (c06) en Node:
 * 1 · el golpe NO sale el frame que se decide (la bola sigue su vuelo);
 * 2 · la salida llega el frame en que la cadena COMPLETA el strike;
 * 3 · en ese frame la pala (chain.cur) está SOBRE la bola (gap < 4 cm);
 * 4 · sin el diferido la salida nacía a ≥10 cm del contacto — ahora NO. */
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
const home = new THREE.Vector3(0, 1.0, -1.55);
const ai = new OpponentAI(cfg, sign, home);
ai.style = null;

/* bola entrando como una devolución del jugador: cae y BOTA en la mitad
 * de la IA (z +0,9), levanta y llega a la pala del rival */
const ball = { pos: new THREE.Vector3(0.05, 1.05, -0.55),
  vel: new THREE.Vector3(0.0, -1.6, -2.6),
  spin: new THREE.Vector3(), dragMul: 1,
  ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };

let frame = 0, bote = -1, frameDecision = -1, frameGolpe = -1, vDevuelta = null;
const traza = [];
const evs = [];
const ctxPrev = new THREE.Vector3();
for (frame = 0; frame < 900 && !vDevuelta; frame++) {
  ctxPrev.copy(ball.pos);
  const ctx = { canHit: true, validBounce: bote >= 0, oppPadX: 0, oppPadZ: -1.5,
    rallyHits: 1, holdTarget: null, prevBall: ctxPrev };
  const r = ai.update(1 / 60, ball, ctx);
  // r99 · traza PRE-paso: el estado EXACTO en que la IA entrega la salida
  traza.push({ f: frame, bola: ball.pos.clone(), pala: ai.chain ? ai.chain.cur.clone() : null,
    fase: ai.chain ? ai.chain.phase : '-', hayDisparo: !!ai._disparo });
  if (r) { vDevuelta = r; frameGolpe = frame; }
  evs.length = 0;
  stepPhysics(1 / 60, ball, [], evs);
  if (bote < 0 && evs.some((e) => e.type === 'table')) bote = frame;
}
// la DECISIÓN = el primer frame con _disparo preparado (pre-paso)
frameDecision = traza.findIndex((t) => t.hayDisparo);
const frameRetorno = traza.findIndex((t) => false);

console.log(`frames: ${frame} · bote ${bote} · decisión (disparo guardado) ${frameDecision} · salida aplicada ${frameGolpe}`);
if (frameGolpe >= 0 && frameDecision >= 0) {
  const delay = frameGolpe - frameDecision;
  aguja(`el golpe se decide en el vuelo (${frameDecision}) y sale DIFERIDO en el contacto (${frameGolpe}: +${delay} frames)`, delay >= 1);
  const t = traza[frameGolpe];
  const gap = t.pala ? t.pala.distanceTo(t.bola) : 99;
  aguja(`la pala está SOBRE la bola al golpear (gap ${(gap * 100).toFixed(1)} cm < 4 cm)`, gap < 0.04);
  aguja(`la fase del golpe completó el strike (${t.fase})`,
    t.fase === 'follow' || t.fase === 'recover');
  aguja('la velocidad de salida es creíble (2-12 m/s)',
    vDevuelta.length() > 2 && vDevuelta.length() < 12);
  aguja('la bola sale hacia el JUGADOR (vz > 0 con sign −1)', vDevuelta.z > 0);
  // el hueco que HABÍA antes del arreglo (la salida nacía en la decisión):
  const td = traza[frameDecision];
  const gapViejo = td.pala ? td.pala.distanceTo(td.bola) : 99;
  console.log(`  · hueco en la decisión: ${(gapViejo * 100).toFixed(1)} cm · hueco en el golpe: ${(gap * 100).toFixed(1)} cm`);
  aguja('MEJORA REAL: el hueco se reduce al menos ×3', gap < gapViejo / 3);
} else {
  aguja('la IA golpea tras el bote (900 frames)', false);
  console.log('  · trace tail:', traza.slice(-4).map((t) =>
    `${t.fase}@${t.f}:b${t.bola.y.toFixed(2)},z${t.bola.z.toFixed(2)}`).join(' | '));
}

console.log(`\nDISPARO DIFERIDO r99 · ${ok} OK · ${mal} FALLOS`);
process.exit(mal ? 1 : 0);

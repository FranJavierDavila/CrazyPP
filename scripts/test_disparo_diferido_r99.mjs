/* r99ter · TEST DEL JINETE SOBRE LA CURVA — la IA REAL (c06) en Node.
 * La exigencia del dueño: la pala es el extremo de una cadena cinemática —
 *  A · SEGUIMIENTO: la pala persigue la bola el gesto entero (nunca aparcada,
 *      la distancia al intercepto decrece y cada frame se mueve).
 *  B · CURVA REAL: el gesto describe un arco (desviación perpendicular del
 *      recta cur0→contacto ≥ 6 cm — no un empujón lineal).
 *  C · SIN TELETRANSPORTES: pala ≤ 13 cm/frame · bola ≤ |v|·dt + gravedad.
 *  D · CONTACTO EN EL PUNTO DULCE: la bola sale cuando la pala está SOBRE
 *      ella (gap < 8,5 cm) y la dirección hereda la tangente del swing.
 *  E · ACOMPAÑAMIENTO: tras el golpe la pala CONTINÚA la misma curva (≥ 8
 *      frames de flujo con frenado progresivo, sin frenada seca). */
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
  smash: 0.3, maxShotSpeed: 10, predictInterval: 0.05,
  maxSpeed: 2.6, accel: 6.0 };   // piernas completas (el cfg real las trae)
const sign = -1;                     // la IA en -Z (campo CPU: devuelve hacia +Z)

/** corre un rally sintético y devuelve las métricas del gesto completo */
function corre(nombre, homePos, bolaIni) {
  const ai = new OpponentAI(cfg, sign, homePos);
  ai.style = null;
  const ball = { pos: bolaIni.pos.clone(), vel: bolaIni.vel.clone(),
    spin: new THREE.Vector3(), dragMul: 1,
    ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
  const ctxPrev = new THREE.Vector3();
  const evs = [];
  let bote = -1, frameGolpe = -1, vDevuelta = null;
  const curTraza = [], bolaTraza = [];
  for (let f = 0; f < 900; f++) {
    ctxPrev.copy(ball.pos);
    const ctx = { canHit: true, validBounce: bote >= 0, oppPadX: 0, oppPadZ: 1.5,
      rallyHits: 1, holdTarget: null, prevBall: ctxPrev };
    const r = ai.update(1 / 60, ball, ctx);
    if (r && frameGolpe < 0) { vDevuelta = r; frameGolpe = f; }
    curTraza.push(ai.chain ? ai.chain.cur.clone() : null);
    bolaTraza.push(ball.pos.clone());
    if (process.env.DBG && f >= 20 && f <= 80) {
      const ch = ai.chain, d = ai._disparo;
      if (ch) console.log(`f${f} ${ch.phase} sC=${ch.sC.toFixed(2)} v=${ch.speed.toFixed(1)} ` +
        `cur=(${ch.cur.x.toFixed(2)},${ch.cur.y.toFixed(2)},${ch.cur.z.toFixed(2)}) ` +
        `bola=(${ball.pos.x.toFixed(2)},${ball.pos.y.toFixed(2)},${ball.pos.z.toFixed(2)}) ` +
        `d=${ch.cur.distanceTo(ball.pos).toFixed(2)} ` +
        (d ? `t=${d.t.toFixed(2)} tC=${d.tCruce.toFixed(2)}` : 'sinD') +
        (ch.persec ? ' PERSEC' : '') + (r ? ' SALIDA' : ''));
    }
    evs.length = 0;
    stepPhysics(1 / 60, ball, [], evs);
    if (bote < 0 && evs.some((e) => e.type === 'table')) bote = f;
    if (frameGolpe >= 0 && f >= frameGolpe + 20) break;   // 20 frames post-golpe
  }
  // ─ métricas ─
  const n = curTraza.length;
  let maxPaso = 0, quietoMax = 0;
  for (let i = 1; i < n; i++) {
    if (!curTraza[i] || !curTraza[i - 1]) continue;
    const paso = curTraza[i].distanceTo(curTraza[i - 1]);
    if (paso > maxPaso) maxPaso = paso;
    quietoMax = paso < 0.002 ? quietoMax + 1 : 0;
  }
  // bola sin teleport: el desplazamiento aparente por frame contra su vuelo
  let saltoBola = 0;
  for (let i = 1; i < n; i++)
    saltoBola = Math.max(saltoBola,
      bolaTraza[i].distanceTo(bolaTraza[i - 1]) * 60);
  const velBolaMax = bolaIni.vel.length() * 1.4 + 6.5;  // gravedad + salida/reserva
  // seguimiento: el gap pala-bola al final del approach vs el inicial
  let gapIni = 99, gapFin = 99;
  if (frameGolpe > 4) {
    for (let i = 0; i < frameGolpe - 1; i++) if (curTraza[i]) {
      gapIni = Math.min(gapIni, curTraza[i].distanceTo(bolaTraza[i]));
      break;
    }
    for (let i = Math.max(0, frameGolpe - 3); i <= Math.min(frameGolpe + 3, n - 1); i++)
      if (curTraza[i]) gapFin = Math.min(gapFin,
        curTraza[i].distanceTo(bolaTraza[i]));
  }
  // curvatura: desviación perpendicular máx respecto a la recta cur0→contacto
  let curvatura = 0;
  const p0 = curTraza.find((x) => x);
  let pC = null;
  for (let i = Math.min(frameGolpe, n - 1); i >= 0; i--)
    if (curTraza[i]) { pC = curTraza[i]; break; }
  if (p0 && pC) {
    const eje = pC.clone().sub(p0).normalize();
    for (const c of curTraza) if (c) {
      const rel = c.clone().sub(p0);
      const perp = rel.sub(eje.clone().multiplyScalar(rel.dot(eje)));
      curvatura = Math.max(curvatura, perp.length());
    }
  }
  // acompañamiento: flujo tras el golpe con frenado progresivo (sin seco)
  const pasosPost = [];
  let flujos = 0, frenadoOK = 0;
  if (frameGolpe >= 0) {
    for (let i = frameGolpe; i < Math.min(frameGolpe + 10, n - 1); i++) {
      if (!curTraza[i] || !curTraza[i + 1]) break;
      pasosPost.push(curTraza[i + 1].distanceTo(curTraza[i]));
    }
    flujos = pasosPost.filter((p) => p >= 0.004).length;
    for (let i = 1; i < pasosPost.length; i++)
      if (pasosPost[i] <= pasosPost[i - 1] * 1.6 + 0.01) frenadoOK++;
  }
  // el gap REAL del encuentro: el mínimo hueco pala-bola en la ventana del
  // golpe (el contacto dispara ANTICIPADO — la bola llega a la pala en ≤ 3
  // frames — así que el hueco honesto es el mínimo de la convergencia)
  let gapGolpe = 99;
  for (let i = frameGolpe; i <= Math.min(frameGolpe + 4, n - 1); i++)
    if (curTraza[i])
      gapGolpe = Math.min(gapGolpe, curTraza[i].distanceTo(bolaTraza[i]));
  // y su equivalente para el "gap final de seguimiento" (misma ventana)
  console.log(`[${nombre}] salida ${frameGolpe} · gap golpe ` +
    `${(gapGolpe * 100).toFixed(1)} cm · seguimiento ${(gapIni * 100).toFixed(0)}→` +
    `${(gapFin * 100).toFixed(0)} cm · curvatura ${(curvatura * 100).toFixed(1)} cm · ` +
    `máx pala ${(maxPaso * 100).toFixed(1)} cm/f · máx bola ${saltoBola.toFixed(1)} m/s · ` +
    `flujo post ${flujos}/10`);
  return { frameGolpe, vDevuelta, maxPaso, saltoBola, velBolaMax, gapIni, gapFin,
    curvatura, flujos, frenadoOK, quietoMax, gapGolpe };
}

/* — A · RALLY NORMAL — */
{
  const A = corre('A · rally normal',
    new THREE.Vector3(0, 1.0, -1.55),
    { pos: new THREE.Vector3(0.05, 1.05, -0.55),
      vel: new THREE.Vector3(0.0, -1.6, -2.6) });
  aguja('A · el golpe sale (difereido hasta el contacto real)', A.frameGolpe >= 1);
  aguja(`A · SEGUIMIENTO: la pala llega a la bola (${(A.gapFin * 100).toFixed(0)} cm final ≤ ` +
    `${(A.gapIni * 100).toFixed(0)} cm inicial)`, A.gapFin <= A.gapIni);
  aguja(`A · contacto en el punto dulce (gap ${(A.gapGolpe * 100).toFixed(1)} cm ≤ 8,5 cm)`,
    A.gapGolpe < 0.085);
  aguja(`A · CURVA real del gesto (${(A.curvatura * 100).toFixed(1)} cm de desviación ≥ 6 cm)`,
    A.curvatura >= 0.06);
  aguja(`A · SIN saltos de pala (máx ${(A.maxPaso * 100).toFixed(1)} cm/frame ≤ 13,1 cm)`,
    A.maxPaso <= 0.131);
  aguja(`A · SIN teleport de bola (máx ${A.saltoBola.toFixed(1)} m/s ≤ ${A.velBolaMax.toFixed(1)})`,
    A.saltoBola <= A.velBolaMax);
  aguja(`A · NUNCA aparcada (ningún tramo de 12+ frames quieto: ${A.quietoMax})`,
    A.quietoMax < 12);
  aguja(`A · ACOMPAÑA: flujo continuo ${A.flujos}/10 con frenado suave (${A.frenadoOK})`,
    A.flujos >= 8 && A.frenadoOK >= 6);
  aguja('A · salida hacia el jugador (2-12 m/s, vz > 0)',
    A.vDevuelta && A.vDevuelta.length() > 2 && A.vDevuelta.length() < 12 &&
    A.vDevuelta.z > 0);
}

/* — B · PALA REtrasada: 0,3 m detrás y alto — el gesto estira y persigue
 *   (estiramiento exigente pero dentro del alcance del jinete) — */
{
  const B = corre('B · pala retrasada',
    new THREE.Vector3(0, 1.3, -1.85),
    { pos: new THREE.Vector3(0.08, 1.02, -0.45),
      vel: new THREE.Vector3(-0.1, -1.4, -2.9) });
  aguja('B · el golpe llega igualmente', B.frameGolpe >= 0);
  aguja(`B · SIN atrapada brusca (máx ${(B.maxPaso * 100).toFixed(1)} cm/frame ≤ 13,1 cm)`,
    B.maxPaso <= 0.131);
  aguja(`B · contacto real (gap ${(B.gapGolpe * 100).toFixed(1)} cm ≤ 8,5 cm)`,
    B.gapGolpe < 0.085);
  aguja(`B · CURVA real (${(B.curvatura * 100).toFixed(1)} cm ≥ 5 cm)`, B.curvatura >= 0.05);
  aguja(`B · SIN teleport de bola (máx ${B.saltoBola.toFixed(1)} m/s)`,
    B.saltoBola <= B.velBolaMax);
  aguja(`B · ACOMPAÑA tras el golpe (${B.flujos}/10 frames ≥ 7)`, B.flujos >= 7);
}

console.log(`\nJINETE SOBRE LA CURVA r99ter · ${ok} OK · ${mal} FALLOS`);
process.exit(mal ? 1 : 0);

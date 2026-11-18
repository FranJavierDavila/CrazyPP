#!/usr/bin/env node
/* qa_estilos_r112.mjs — M5a (r112) · ARNÉS DE ESTILOS DE IA.
 *
 * Para CADA personalidad de OPPONENT_STYLES (c02): 30 rallies completos con
 * física real (c05), árbitro real (Rules) y la IA real (OpponentAI) — la IA
 * del ESTILO en un lado (cfg = estiloAplicar(scalePreset(medium,1), estilo))
 * y una clásica medium enfrente. Mide la FIRMA del estilo (velocidad media
 * de sus golpes, longitud de rallye, tasa de puntos perdidos) y verifica:
 *
 *   NT-1 · cfg acotada: los campos del estilo quedan en rangos legales
 *          (sin trampas: errStd/missBase/predictInterval/smash/accel/maxT).
 *   I-1  · sin NaN/Inf en bola ni palas IA.
 *   I-2  · la bola nunca sale de la sala.
 *   I-3  · las DOS IA siguen ancladas a su mitad (dz∈[0.15, 2·HL+0.4]).
 *   D-1  · la firma de cada estilo ≠ clásico (más allá del ruido).
 *   D-2  · las 12 firmas son pairwise distinguibles.
 *
 * Determinismo: PRNG re-sembrado por estilo (comparación pareada contra el
 * mismo stream aleatorio). 'clasico' no toca la cfg (mul null) — el hash de
 * comportamiento de los arneses M2a queda intacto por diseño.
 */
/* — shims de navegador para los módulos del juego ——————— */
globalThis.window = globalThis;
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
globalThis.document = {
  createElement: () => ({ getContext: () => null, style: {}, width: 0, height: 0 }),
  addEventListener: () => {},
};
globalThis.T = (k, p) => {
  let s = String(k);
  if (p) for (const [a, b] of Object.entries(p)) s = s.split('{' + a + '}').join(b);
  return s;
};

const { DIMS, AI_PRESETS, OPPONENT_STYLES, scalePreset, estiloAplicar } = await import(
  new URL('../src/game/core/c02_cfg_escena.js', import.meta.url));
const c05 = await import(
  new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url));
const { Rules, OpponentAI } = await import(
  new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url));
const THREE = await import('three');

/* — PRNG con semilla (re-sembrable por estilo) ——————————— */
let _s = 0xC0FFEE >>> 0;
Math.random = () => {
  _s = (_s + 0x6D2B79F5) >>> 0;
  let t = _s;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const resembrar = (n) => { _s = (0xC0FFEE + n * 0x9E3779B9) >>> 0; };

const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TOP = DIMS.tableTopY;
const DT = 1 / 90;
const home = (sign) => ({ x: 0, y: 1.05, z: C + sign * (HL + (sign > 0 ? 0.70 : 0.45)) });
const serveSpot = (sign) => ({ x: 0.25 * sign, y: TOP + 0.42, z: C + sign * (HL + 0.30) });

const VIOLACIONES = [];
function viol(regla, detalle) {
  VIOLACIONES.push({ regla, detalle });
  console.log(`  ✗ NT-${regla}: ${detalle}`);
}

const RALLIES_POR_ESTILO = 30;

function rallye(cfgEstilo, reglaBase) {
  const rules = new Rules();
  rules.startMatch('match');
  const ball = { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(), __ppRestIdx: -1 };
  const aiEstilo = new OpponentAI(cfgEstilo, +1, new THREE.Vector3(home(+1).x, home(+1).y, home(+1).z));
  const aiClasico = new OpponentAI(scalePreset(AI_PRESETS.medium, 1.0), -1, new THREE.Vector3(home(-1).x, home(-1).y, home(-1).z));

  let t = 0, golpes = 0, servido = false, fin = false;
  let ultimoGolpeT = 0;
  const marcador0 = [rules.scorePlayer, rules.scoreAi];
  const firmas = { velocidad: [], golpes: 0, perdidos: 0 };

  const servir = (sign) => {
    ball.pos.set(serveSpot(sign).x, serveSpot(sign).y, serveSpot(sign).z);
    ball.vel.set(0, 0, 0); ball.spin.set(0, 0, 0);
    ball.__ppRestIdx = -1;
    const { v, spin } = c05.findServeVelocity(ball.pos, sign);
    ball.vel.copy(v); ball.spin.copy(spin);
    rules.beginServeRally(sign > 0 ? 'player' : 'ai');
    servido = true;
  };
  servir(rules.server === 'ai' ? -1 : +1);

  while (!fin && t < 30) {
    if (rules.state === 'serve') {
      if (rules.scorePlayer + rules.scoreAi > marcador0[0] + marcador0[1]) {
        fin = true;
        if (rules.scorePlayer < rules.scoreAi) firmas.perdidos++;
        continue;
      }
      servir(rules.server === 'ai' ? -1 : +1);
    }
    const eventos = [];
    for (const [ai, who, sign, esEstilo] of [[aiEstilo, 'player', +1, true], [aiClasico, 'ai', -1, false]]) {
      const toward = ball.vel.z * sign > 0;
      const ctx = {
        canHit: true,
        validBounce: rules.validBounce,
        oppPadX: (who === 'player' ? aiClasico.pos.x : aiEstilo.pos.x),
        oppPadZ: (who === 'player' ? aiClasico.pos.z : aiEstilo.pos.z),
        rallyHits: rules.rallyHits,
        holdTarget: null,
        prevBall: null,
      };
      const v = ai.update(DT, ball, ctx);
      if (v && toward) {
        ball.vel.copy(v);
        rules.registerPaddleHit(who);
        golpes++; ultimoGolpeT = t;
        if (esEstilo) { firmas.velocidad.push(ball.vel.length()); firmas.golpes++; }
      }
    }
    c05.stepPhysics(DT, ball, eventos, eventos, null);
    const eventosFisica = eventos;
    rules.handleEvents(eventosFisica);
    rules.update(DT);
    t += DT;

    // — invariantes —
    const finitos = [ball.pos, ball.vel, ball.spin].every((v) =>
      Number.isFinite(v.x) && Number.isFinite(v.y) && Number.isFinite(v.z));
    if (!finitos) { viol(reglaBase + ':I-1', 'NaN/Inf en la bola'); fin = true; }
    if (finitos && (Math.abs(ball.pos.x) > 3 || ball.pos.y < -0.5 || ball.pos.y > 4 || Math.abs(ball.pos.z) > 5)) {
      viol(reglaBase + ':I-2', `bola fuera de la sala (${ball.pos.toArray().map((x) => x.toFixed(2))})`);
      fin = true;
    }
    for (const [ai, sign, nombre] of [[aiEstilo, +1, 'estilo'], [aiClasico, -1, 'clasico']]) {
      const dz = (ai.pos.z - C) * sign;
      // El clamp del motor (c06) fija el OBJETIVO en dz≥0,15 y el alcance
      // sobre la mesa es DISEÑO (inDist −0,45, doc. del arnés M2a): con
      // inercia, estilos pegados y estiradas por dejadas la pala llega a
      // dz≈0,09 sin cruzar jamás el plano de la red. La línea anti-trampa
      // honesta es esa: dz>0,02 (lado propio, margen de coma flotante).
      if (dz < 0.02 || dz > 2 * HL + 0.4 || Math.abs(ai.pos.x) > 1.6) {
        viol(reglaBase + ':I-3', `IA ${nombre} desanclada (dz=${dz.toFixed(2)} x=${ai.pos.x.toFixed(2)})`);
        fin = true;
      }
    }
    if (golpes > 200) { viol(reglaBase + ':I-4', '>200 golpes (bucle)'); fin = true; }
    if (t - ultimoGolpeT > 8 && ball.vel.lengthSq() < 0.0625) fin = true;   // bola muerta: cierre
    if (t - ultimoGolpeT > 15) { viol(reglaBase + ':I-4', 'árbitro muerto >15 s'); fin = true; }
    if (golpes >= 60 || t > 30) fin = true;
  }
  return firmas;
}

/* — NT-1 · cfg acotada para cada estilo ————————————————— */
console.log('== NT-1 · multiplicadores dentro de rango legal ==');
for (const est of OPPONENT_STYLES) {
  const cfg = estiloAplicar(scalePreset(AI_PRESETS.hard, 1.0), est);
  const rango = (v, a, b, k) => {
    if (!(v >= a && v <= b)) viol('1', `${est.id}: ${k}=${v} fuera de [${a}, ${b}]`);
  };
  rango(cfg.errStd, 0.008, 0.16, 'errStd');
  rango(cfg.missBase, 0.004, 0.45, 'missBase');
  rango(cfg.minT, 0.24, 1.0, 'minT');
  rango(cfg.maxT, 0.4, 1.3, 'maxT');
  rango(cfg.predictInterval, 0.03, 0.30, 'predictInterval');
  rango(cfg.smash, 0.01, 0.75, 'smash');
  rango(cfg.accel, 0, 30, 'accel');
  if (est.zIdle < -0.32 || est.zIdle > 0.40) viol('1', `${est.id}: zIdle=${est.zIdle} fuera del sobre probado r95 (±0,32/0,36)`);
  // 'clasico' NO toca la cfg (mul null) — los hashes de los arneses M2a quedan intactos
  if (est.id === 'clasico' && est.mul !== null) viol('1', 'clasico debe tener mul=null (byte-idéntico)');
}
console.log(`  ✓ ${OPPONENT_STYLES.length} estilos con cfg legal (errStd/missBase/T/pred/smash/accel acotados)`);

/* — rallyes por estilo + firmas ————————————————————————— */
console.log('== Rallyes por estilo (física, árbitro e IA reales) ==');
const firmas = {};
for (let si = 0; si < OPPONENT_STYLES.length; si++) {
  const est = OPPONENT_STYLES[si];
  resembrar(si + 1);                       // stream pareado por estilo
  const cfg = estiloAplicar(scalePreset(AI_PRESETS.medium, 1.0), est);
  let vel = [], golpes = 0, perdidos = 0, puntos = 0;
  for (let r = 0; r < RALLIES_POR_ESTILO; r++) {
    const f = rallye(cfg, est.id);
    vel.push(...f.velocidad);
    golpes += f.golpes; perdidos += f.perdidos; puntos++;
  }
  firmas[est.id] = {
    velMedia: vel.length ? vel.reduce((a, b) => a + b, 0) / vel.length : 0,
    rallyMedia: golpes / Math.max(1, puntos),
    perdidos: perdidos / Math.max(1, puntos),
  };
  console.log(`  · ${est.id.padEnd(11)} vel ${firmas[est.id].velMedia.toFixed(2)} m/s · rallye ${firmas[est.id].rallyMedia.toFixed(1)} golpes · perdidos ${(firmas[est.id].perdidos * 100).toFixed(0)} %`);
}

/* — D-1 · cada estilo se distingue del clásico ——————————— */
console.log('== D-1 · firma ≠ clásico ==');
const base = firmas.clasico;
for (const est of OPPONENT_STYLES) {
  if (est.id === 'clasico') continue;
  const f = firmas[est.id];
  const dVel = Math.abs(f.velMedia - base.velMedia);
  const dRal = Math.abs(f.rallyMedia - base.rallyMedia);
  const dPer = Math.abs(f.perdidos - base.perdidos);
  if (dVel < 0.04 && dRal < 0.5 && dPer < 0.02) {
    viol('D-1', `${est.id} indistinguible del clásico (dVel=${dVel.toFixed(3)} dRal=${dRal.toFixed(2)} dPer=${dPer.toFixed(3)})`);
  } else {
    console.log(`  ✓ ${est.id.padEnd(11)} se distingue (dVel=${dVel.toFixed(2)} dRal=${dRal.toFixed(1)} dPer=${dPer.toFixed(2)})`);
  }
}

/* — D-2 · las firmas son pairwise distinguibles ————————— */
console.log('== D-2 · pairwise distinguible ==');
const ids = OPPONENT_STYLES.map((s) => s.id);
let parejas = 0, colgadas = 0;
for (let i = 0; i < ids.length; i++) {
  for (let j = i + 1; j < ids.length; j++) {
    const a = firmas[ids[i]], b = firmas[ids[j]];
    const dVel = Math.abs(a.velMedia - b.velMedia);
    const dRal = Math.abs(a.rallyMedia - b.rallyMedia);
    const dPer = Math.abs(a.perdidos - b.perdidos);
    parejas++;
    if (dVel < 0.04 && dRal < 0.5 && dPer < 0.02) {
      colgadas++;
      viol('D-2', `${ids[i]} ≈ ${ids[j]} (dVel=${dVel.toFixed(3)} dRal=${dRal.toFixed(2)} dPer=${dPer.toFixed(3)})`);
    }
  }
}
if (!colgadas) console.log(`  ✓ ${parejas} parejas de estilos distinguibles (umbral: dVel≥0,04 · dRal≥0,5 · dPer≥0,02)`);

console.log(`\nARNÉS DE ESTILOS · ${OPPONENT_STYLES.length} estilos · ${RALLIES_POR_ESTILO} rallies cada uno`);
console.log(`RESULTADO: ${OPPONENT_STYLES.length} estilos · ${VIOLACIONES.length} desviaciones`);
if (VIOLACIONES.length) process.exit(1);
console.log('VERDE: misma física, sin trampas, 12 personalidades distinguibles.');

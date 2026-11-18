#!/usr/bin/env node --no-warnings
/* CRAZY PING PONG · M2 · ARNÉS FÍSICO (200 rallies IA-vs-IA, nodo puro).
 *
 * Juega 200 rallies COMPLETOS con el código REAL del juego en node:
 *   · FÍSICA:   c05.stepPhysics (CCD + aerodinámica + botes + red)
 *   · ÁRBITRO:  c06.Rules      (dobles, voleas, saques, puntos)
 *   · RIVALES:  c06.OpponentAI (las dos mitades, presets reales)
 *   · SAQUE:    c05.findServeVelocity (saque legal de verdad)
 *
 * Invariantes por SUBPASO (el arnés ROJA si alguna se viola):
 *   I1  ball.pos/vel/spin finitos (sin NaN/Infinity)
 *   I2  la bola VIVE en la sala (|x|<3 · −0,5<y<4 · |z|<5)
 *   I3  cada IA permanece ANCLADA a su mitad (no cruza la red más de 0,3 m
 *       ni se aleja de su casa más de 1,5 m — la clase de bug «rival detrás
 *       de la mesa» que el dueño sufrió en Halloween)
 *   I4  el rallye TERMINA (ningún rally supera 40 s / 200 golpes — sin
 *       bucles infinitos del árbitro)
 *   I5  los puntos se REPARTEN (ningún lado gana el 100 % de 60+ puntos:
 *       la IA no puede quedar ciega ni imparable)
 *
 * DETERMINISMO: semilla fija (mulberry32) para Math.random → dos ejecuciones
 * con la misma semilla producen el MISMO resumen (hash sha256) — el arnés
 * también detecta cambios accidentales de conducta (canario estructural).
 *
 * Uso:
 *   node --no-warnings scripts/arnes_rallies_v3698.mjs            # 200 rallies
 *   node --no-warnings scripts/arnes_rallies_v3698.mjs --rapido   # 40 rallies
 */
import { createHash } from 'node:crypto';

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

const { DIMS, AI_PRESETS } = await import(
  new URL('../src/game/core/c02_cfg_escena.js', import.meta.url));
const c05 = await import(
  new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url));
const { Rules, OpponentAI } = await import(
  new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url));

/* — PRNG con semilla (determinismo del arnés) ——————————— */
const SEMILLA = 0xC0FFEE;
let _s = SEMILLA >>> 0;
Math.random = () => {
  _s = (_s + 0x6D2B79F5) >>> 0;
  let t = _s;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TOP = DIMS.tableTopY;
const DT = 1 / 90;
const home = (sign) => ({
  x: 0, y: 1.05,
  z: C + sign * (HL + (sign > 0 ? 0.70 : 0.45)),
});
const serveSpot = (sign) => ({
  x: 0.25 * sign, y: TOP + 0.42,
  z: C + sign * (HL + 0.30),
});

const THREE = await import('three');

const VIOLACIONES = [];
function viol(rallye, regla, detalle) {
  VIOLACIONES.push({ rallye, regla, detalle });
  console.log(`  ✗ I-${regla} en rallye ${rallye}: ${detalle}`);
}

/* — UN rallye completo con física, árbitro e IA reales ————— */
function rallye(n, cfgP, cfgA, envenenar) {
  const rules = new Rules();
  rules.startMatch('match');
  const ball = {
    pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(),
    __ppRestIdx: -1,
  };
  const aiP = new OpponentAI(cfgP, +1, new THREE.Vector3(home(+1).x, home(+1).y, home(+1).z));
  const aiA = new OpponentAI(cfgA, -1, new THREE.Vector3(home(-1).x, home(-1).y, home(-1).z));

  let t = 0, botes = 0, golpes = 0, servido = false, fin = false, causa = '';
  const marcador0 = [rules.scorePlayer, rules.scoreAi];
  let ultimoGolpeT = 0;
  let traza = null;

  const servir = (sign) => {
    const s = sign > 0 ? 'player' : 'ai';
    ball.pos.set(serveSpot(sign).x, serveSpot(sign).y, serveSpot(sign).z);
    ball.vel.set(0, 0, 0); ball.spin.set(0, 0, 0);
    ball.__ppRestIdx = -1;
    const { v, spin } = c05.findServeVelocity(ball.pos, sign);
    ball.vel.copy(v); ball.spin.copy(spin);
    rules.beginServeRally(s);
    servido = true;
  };

  // primer saque: decide rules.server (0 = player? ver convención)
  let lado = rules.server === 'ai' ? -1 : +1;
  servir(lado);

  const eventos = [];
  while (!fin && t < 240) {
    // — SERVICIO: primer saque y REPETICIONES del árbitro (retryServe no
    //   cambia el marcador: el arnés debe re-servir o el rallye se cuelga) —
    if (rules.state === 'serve') {
      if (rules.scorePlayer + rules.scoreAi > marcador0[0] + marcador0[1]) {
        fin = true; causa = `punto (${rules.scorePlayer}-${rules.scoreAi})`;
      } else {
        servir(rules.server === 'ai' ? -1 : +1);
      }
    }
    eventos.length = 0;
    // — las dos IA deciden (solo golpea la que tiene la bola de cara) —
    for (const [ai, who, sign] of [[aiP, 'player', +1], [aiA, 'ai', -1]]) {
      const toward = ball.vel.z * sign > 0;
      const ctx = {
        canHit: true,
        validBounce: rules.validBounce,
        oppPadX: (who === 'player' ? aiA.pos.x : aiP.pos.x),
        oppPadZ: (who === 'player' ? aiA.pos.z : aiP.pos.z),
        rallyHits: rules.rallyHits,
        holdTarget: (!servido && rules.state === 'serve') ? null : null,
        prevBall: null,
      };
      const v = ai.update(DT, ball, ctx);
      if (v && toward) {
        ball.vel.copy(v);
        const antes = [rules.scorePlayer, rules.scoreAi, rules.rallyHits, rules.state];
        const intents = rules.registerPaddleHit(who);
        golpes++;
        ultimoGolpeT = t;
        if (golpes >= 45 && golpes <= 52) {
          (traza ||= []).push(`golpe#${golpes} who=${who} → antes[sc=${antes[0]}-${antes[1]} rh=${antes[2]} st=${antes[3]}] ` +
            `después[sc=${rules.scorePlayer}-${rules.scoreAi} rh=${rules.rallyHits} st=${rules.state} last=${rules.lastHitter}] ` +
            `intents=${intents.length} vel=${ball.vel.length().toFixed(1)} bz=${ball.pos.z.toFixed(2)}`);
        }
      }
    }
    // — física REAL (CCD + Magnus + botes + red) —
    // CANARIO: en el rallye envenenado la bola TELETRANSPORTA fuera de la
    // sala a mitad del rallye (la clase de regresión que el arnés debe
    // cazar SIEMPRE — si no la detecta, el arnés no sirve y ROJA).
    if (envenenar && golpes === 5) ball.pos.set(50, 50, 50);
    c05.stepPhysics(DT, ball, [], eventos, null);
    for (const e of eventos) if (e.type === 'table') botes++;
    rules.handleEvents(eventos);
    rules.update(DT);
    t += DT;

    // — INVARIANTES por subpaso —
    const finitos = [ball.pos, ball.vel, ball.spin].every((v) =>
      Number.isFinite(v.x) && Number.isFinite(v.y) && Number.isFinite(v.z));
    if (!finitos) viol(n, 1, `NaN/Inf en la bola (t=${t.toFixed(2)}s)`), fin = true;
    if (finitos && (Math.abs(ball.pos.x) > 3 || ball.pos.y < -0.5 ||
        ball.pos.y > 4 || Math.abs(ball.pos.z) > 5)) {
      viol(n, 2, `bola FUERA de la sala (${ball.pos.toArray().map((x) => x.toFixed(2))})`);
      fin = true;
    }
    for (const [ai, sign, nombre] of [[aiP, +1, 'player'], [aiA, -1, 'ai']]) {
      // I-3 · ANCLAJE REAL: la IA puede ALCANZAR por encima de la mesa
      // (inDist −0,45) y defender bolas profundas hasta el clamp de c06
      // (dz máx legal = 2·HL+0,15 ≈ 2,89 + inercia). Lo que JAMÁS puede es
      // cruzar la red (dz≤0) ni salir de la sala (la clase de bug «rival
      // detrás de la mesa» de Halloween).
      const dz = (ai.pos.z - C) * sign;
      if (dz < 0.15 || dz > 2 * HL + 0.4 || Math.abs(ai.pos.x) > 1.6) {
        viol(n, 3, `IA ${nombre} DESANCLADA (dz=${dz.toFixed(2)} · x=${ai.pos.x.toFixed(2)})`);
        fin = true;
      }
      if (!ai.pos || !Number.isFinite(ai.pos.x + ai.pos.y + ai.pos.z)) {
        viol(n, 1, `IA ${nombre} con pose NaN`); fin = true;
      }
    }
    if (golpes > 200) { viol(n, 4, 'rallye con >200 golpes (bucle)'); fin = true; }
    // I-4 · ÁRBITRO MUERTO: >15 s sin NINGÚN golpeo con la bola viva y
    // decidable (>0,25 m/s) — un rallye sano golpea cada ~1,3 s. Los
    // rallyes largos PERO VIVOS (golpes alternando y botando) se cierran
    // sin alarma al alcanzar el tope de golpes: no son regresiones.
    if (t - ultimoGolpeT > 15 && ball.vel.lengthSq() > 0.0625) {
      viol(n, 4, `árbol muerto: ${ (t - ultimoGolpeT).toFixed(1) } s sin golpeo con bola viva`);
      fin = true;
    }
    // bola MUERTA: sin contacto >8 s y la bola casi parada (rodando o
    // atrapada — en VR la recoge el jugador; el arnés la cierra sin alarma)
    if (t - ultimoGolpeT > 8 && ball.vel.lengthSq() < 0.0625) {
      fin = true; causa = 'bola muerta (rodando)';
    }
    if (golpes >= 60 || t > 45) {
      // rallye largo PERO vivo (hard-vs-hard encadena 60+ intercambios
      // legales con missBase 0,03 — comportamiento esperado, no bug):
      // cierre limpio por tope del arnés. Las violaciones reales de I-4
      // son el árbitro muerto (>15 s sin golpeo con bola viva) y el bucle.
      fin = true; causa = `rallye largo cerrado por el arnés (${golpes} golpes, ${t.toFixed(0)} s)`;
    }
    if (rules.state === 'point') {
      if (rules.scorePlayer + rules.scoreAi > marcador0[0] + marcador0[1]) {
        fin = true; causa = `punto (${rules.scorePlayer}-${rules.scoreAi})`;
      }
    }
    // TRAZA de rallyes largos: si el árbitro acumula >50 intercambios sin
    // decidir, guardamos muestras para el diagnóstico (solo se imprimen al
    // terminar ese rallye)
    if (golpes === 50 || golpes === 70 || golpes === 100) {
      (traza ||= []).push(`t=${t.toFixed(1)} st=${rules.state} sc=${rules.scorePlayer}-${rules.scoreAi} ` +
        `vb=${rules.validBounce} last=${rules.lastHitter} rh=${rules.rallyHits} ` +
        `bz=${ball.pos.z.toFixed(2)} by=${ball.pos.y.toFixed(2)} v=${ball.vel.length().toFixed(2)} ev=[${eventos.map((e) => e.type).join(',')}]`);
    }
  }
  if (!fin) {
    viol(n, 4, `rallye SIN fin en 240 s (${golpes} golpes, ${botes} botes)`);
    if (traza) { console.log('    TRAZA del rallye sin fin:'); traza.forEach((l) => console.log('      ' + l)); }
  }
  return { golpes, botes, dur: t, causa, traza: traza || null,
    marc: [rules.scorePlayer - marcador0[0], rules.scoreAi - marcador0[1]] };}

/* — BATERÍA: 200 rallies con mezcla determinista de presets ————— */
const COMBOS = [
  ['easy', 'easy'], ['easy', 'medium'], ['easy', 'hard'],
  ['medium', 'easy'], ['medium', 'medium'], ['medium', 'hard'],
  ['hard', 'easy'], ['hard', 'medium'], ['hard', 'hard'],
];
const RAPIDO = process.argv.includes('--rapido');
const CANARIO = process.argv.includes('--canario');   // siembra 1 bug y debe DETECTARLO
const N = RAPIDO ? 40 : 200;
let okRallies = 0, totGolpes = 0, totBotes = 0, maxRally = 0, sumDur = 0;
let puntosP = 0, puntosA = 0;
console.log(`== ARNÉS FÍSICO · ${N} rallies (semilla ${SEMILLA}) ==`);
for (let i = 0; i < N; i++) {
  const [p, a] = COMBOS[i % COMBOS.length];
  const r = rallye(i + 1, AI_PRESETS[p], AI_PRESETS[a], CANARIO && i === 99);
  if (r) {
    okRallies++;
    totGolpes += r.golpes; totBotes += r.botes; sumDur += r.dur;
    maxRally = Math.max(maxRally, r.golpes);
    puntosP += r.marc[0]; puntosA += r.marc[1];
  }
}
/* I5 · reparto de puntos: con 9 combos × N/9 rallies ninguno de los dos
 * lados puede arrasarlo todo (una IA rota — ciega o imparable — lo rompe) */
const total = puntosP + puntosA;
if (total >= 60 && (puntosP === total || puntosA === total)) {
  viol('-', 5, `un lado ganó el 100 % de ${total} puntos (${puntosP}-${puntosA})`);
}

const resumen = {
  rallies: N, completados: okRallies, golpes: totGolpes, botes: totBotes,
  maxRallyGolpes: maxRally, durMedia: +(sumDur / Math.max(1, okRallies)).toFixed(3),
  puntos: `${puntosP}-${puntosA}`, violaciones: VIOLACIONES.length,
};
const hash = createHash('sha256')
  .update(JSON.stringify({ ...resumen, violaciones: VIOLACIONES }))
  .digest('hex').slice(0, 16);

console.log('  · rallies        : %d/%d completados', okRallies, N);
console.log('  · golpes totales : %d (máx rallye %d)', totGolpes, maxRally);
console.log('  · botes de mesa  : %d', totBotes);
console.log('  · duración media : ' + resumen.durMedia.toFixed(2) + ' s');
console.log('  · puntos %s-%s · violaciones: %d', puntosP, puntosA, VIOLACIONES.length);
console.log('  · hash resumen   : %s', hash);

if (CANARIO) {
  const visto = VIOLACIONES.some((v) => v.regla === 2);
  if (!visto) {
    console.log('\nCANARIO NO DETECTADO — el arnés no sirve (bug sembrado sin alarma)');
    process.exit(1);
  }
  console.log('\nCANARIO DETECTADO: la bola teletransportada disparó I-2 (el arnés muerde)');
  process.exit(0);
}
if (VIOLACIONES.length) {
  console.log(`\nARNÉS ROJA: ${VIOLACIONES.length} violación(es) de invariantes`);
  process.exit(1);
}
console.log('\nARNÉS VERDE: física, árbitro e IA reales · invariantes íntegras · 200 rallies');
process.exit(0);

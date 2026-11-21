/* r102 · ARNÉS SEGUNDO TOQUE — reproduce el informe del dueño tras V3.6.199
 * («la pala se queda bloqueada a partir del segundo toque») con el ÁRBITRO
 * REAL (Rules de c06) + física real (c05) + dos IA reales (c06): el arnés
 * r99ter usaba un mini-árbitro propio y NO podía ver el hueco árbitro↔cadena.
 * Mide:
 *  · PARQUE: pala quieta ≥ 1,0 s mientras la bola entra a su campo, con el
 *    estado completo (dRem, _disparo, validBounce, predictT, fase).
 *  · PASÓ SIN TOQUE: la bola cruza la línea de fondo del receptor en rally
 *    sin registerPaddleHit — con el volcado del estado de la IA en ese frame.
 *  · CADENA ZOMBI (> 3,5 s) y NaN.
 * Salida: resumen + primeros incidentes con causa apuntada.                  */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r102' }; } catch (e) { /* getter */ }
// el árbitro usa el traductor global T (en el juego lo monta el boot):
// en el arnés, pasarela (claves sin traducir)
globalThis.T = (k, _o) => k;

import * as THREE from 'three';
const { OpponentAI, Rules } = await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { DIMS } = await import('/home/z/my-project/src/game/core/c02_cfg_escena.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');

const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TOP = DIMS.tableTopY;
const DT = 1 / 60, FRAMES = 90000;   // 1500 s de partido

const cfg = { missBase: 0.0, errStd: 0.05, minT: 0.5, maxT: 1.1,
  smash: 0.3, maxShotSpeed: 9, predictInterval: 0.05,
  maxSpeed: 2.6, accel: 6.0 };

const rules = new Rules();
const rival = new OpponentAI(cfg, -1, new THREE.Vector3(0, 1.0, C - 1.55));
const jug = new OpponentAI(cfg, 1, new THREE.Vector3(0, 1.0, C + 1.55));
rival.style = null; jug.style = null;
const ais = { ai: rival, player: jug };
const otro = { ai: 'player', player: 'ai' };

const ball = { pos: new THREE.Vector3(), vel: new THREE.Vector3(),
  spin: new THREE.Vector3(), dragMul: 1,
  ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };

let server = 'player';           // el juego abre con sacador propio (base)
let pausa = 0;                   // temporizador entre puntos
let serveWait = 0;

function saca(quien) {
  const s = quien === 'ai' ? -1 : 1;
  rules.beginServeRally(quien);
  ball.pos.set((Math.random() - 0.5) * 0.2, 1.06, C + s * 1.05);
  // tiro plano y bajo: primer bote en el CAMPO PROPIO (reglamento) y luego
  // cruzar; la física y el árbitro reales juzgan el resto
  ball.vel.set((Math.random() - 0.5) * 0.3, -0.9, -s * (3.4 + Math.random() * 0.4));
  ball.spin.set(0, 0, 0);
  ball.ppEfecto = false; ball.ppPortal = false;
}

/* ---------- instrumentación ---------- */
const inc = [];
function nota(who, tipo, f, extra) {
  inc.push({ f, who, tipo, ...extra });
}
const vigia = {};
for (const who of ['ai', 'player']) {
  vigia[who] = { ult: new THREE.Vector3(), quieta: 0, ultHit: -1,
    devoluciones: 0, pasoSinToque: 0 };
}
function dump(who, f) {
  const ai = ais[who], ch = ai.chain;
  return {
    fase: ch ? ch.phase : '—', dRem: ch ? +(ch.sC - ch.s).toFixed(3) : null,
    disparo: !!ai._disparo, vB: rules.validBounce, mBO: rules.mustBounceOpp,
    pT: +ai.predictT.toFixed(2), pV: !!ai.predictValid,
    t: ch ? +ch.t.toFixed(2) : null,
    distBola: +ai.pos.distanceTo(ball.pos).toFixed(2),
    hits: rules.rallyHits,
  };
}

let frames = 0;
for (let f = 0; f < FRAMES; f++) {
  frames = f;
  const dt = DT;

  /* ── máquina de estados del partido (como c12: pausa → saque) ── */
  if (rules.state === 'point') {
    pausa += dt;
    if (pausa > 1.2) { pausa = 0; rules.state = 'serve'; server = rules.computeNextServer(); serveWait = 0; }
  } else if (rules.state === 'serve') {
    serveWait += dt;
    if (serveWait > 0.8) saca(server);
  }

  /* ── física real ── */
  const events = [];
  stepPhysics(dt, ball, [], events, null);
  if (rules.state === 'rally') rules.handleEvents(events);

  /* ── IA reales con ctx del árbitro REAL ── */
  for (const who of ['ai', 'player']) {
    const ai = ais[who], sign = ai.sign;
    const ctx = {
      canHit: rules.state === 'rally',
      validBounce: rules.validBounce,
      oppPadX: ais[otro[who]].pos.x, oppPadZ: ais[otro[who]].pos.z,
      rallyHits: rules.rallyHits, holdTarget: null,
      prevBall: null,
    };
    const hit = ai.update(dt, ball, ctx);
    if (hit && rules.state === 'rally') {
      ball.vel.copy(hit);
      vigia[who].devoluciones++;
      vigia[who].ultHit = f;
      const ints = rules.registerPaddleHit(who);
      if (ints && ints.length) { /* punto por doble golpe — raro aquí */ }
    }
    /* PARQUE: pala quieta ≥ 1,0 s con bola entrando a su campo */
    const v = vigia[who];
    const entra = rules.state === 'rally' && ball.vel.z * sign > 0 &&
      (ball.pos.z - C) * sign > 0;
    const chain = ai.chain;
    const pala = chain ? chain.cur : ai.pos;
    if (pala.distanceTo(v.ult) < 0.0015) v.quieta += dt; else v.quieta = 0;
    v.ult.copy(pala);
    if (v.quieta > 1.0 && entra && !(v._anotado === f)) {
      v._anotado = f;
      nota(who, 'PARQUE', f, dump(who, f));
      v.quieta = 0.6;   // re-anota cada 0,4 s si sigue
    }
    /* PASÓ SIN TOQUE: la bola cruzó su línea de fondo en rally sin golpe suyo
       desde el último golpe del rival */
    const fondo = C - sign * (HL + 0.35);
    if (rules.state === 'rally' && (ball.pos.z - C) * sign < -(HL + 0.35) &&
        v.ultHit < v._ultHitRival) {
      v.pasoSinToque++;
      nota(who, 'PASO_SIN_TOQUE', f, dump(who, f));
      v.ultHit = f;   // anota una vez por vuelo
    }
    v._ultHitRival = vigia[otro[who]].ultHit;
  }

  /* fin de punto por árbitro */
  if (rules.state === 'point') { /* la pausa de arriba lo gestiona */ }
}

/* ---------- resumen ---------- */
console.log(`rallies=${rules.totalPoints} · devoluciones rival=${vigia.ai.devoluciones} · jugador=${vigia.player.devoluciones} · frames=${frames}`);
const parques = inc.filter(i => i.tipo === 'PARQUE');
const pasos = inc.filter(i => i.tipo === 'PASO_SIN_TOQUE');
const porCausa = (arr) => {
  const m = {};
  for (const i of arr) {
    const k = i.disparo ? 'con_disparo' : (i.vB ? 'vB_true_sin_disparo' : 'vB_false');
    m[k] = (m[k] || 0) + 1;
  }
  return m;
};
console.log(`PARQUES ≥1s: ${parques.length} · causas:`, JSON.stringify(porCausa(parques)));
console.log(`PASÓ_SIN_TOQUE: ${pasos.length}`);
console.log('— primeros 12 PARQUES —');
for (const i of parques.slice(0, 12)) console.log(`f${i.f} ${i.who}`, JSON.stringify(i));
console.log('— primeros 8 PASOS_SIN_TOQUE —');
for (const i of pasos.slice(0, 8)) console.log(`f${i.f} ${i.who}`, JSON.stringify(i));

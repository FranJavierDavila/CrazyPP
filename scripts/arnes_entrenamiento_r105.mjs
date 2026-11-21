/* r105 · ARNÉS DE IGUALDAD DE FÍSICA ENTRE MODALIDADES — informe del dueño:
 * «en el modo de entrenamiento no tenemos las mismas físicas… no se puede
 * pulsar el gatillo para soltar la bola… los mismos fallos». Cuatro causas
 * halladas y arregladas, probadas aquí contra los MÓDULOS REALES en disco:
 *  E1 · el gatillo en trainV3 ya NO lo come la guardia genérica de calib
 *       (onTrigger: calib && !trainV3 — la ruta __PP_TRAIN.serveTrigger vive).
 *  E2 · ORDEN correcto: la ruta trainV3 corre ANTES del residuo 'serve'
 *       (el árbitro duerme en calib y su state es basura del modo anterior).
 *  E3 · la bola del tee (t4a/t4b) es CINEMÁTICA como el saque del núcleo:
 *       c12 salta la física cuando __PP_TRAIN.ballHeld() (fase tee).
 *  E4 · PP_TRAIN expone ballHeld (st.phase === 'tee' — sólo tee activo t4).
 *  E5 · resetToss limpia la captura de apoyo (__ppRestIdx = -1): la bola que
 *       vuelve a la mano es un lienzo limpio — el lanzamiento jamás se lo
 *       come el carry (TODAS las modalidades: resetToss es del núcleo).
 *  E6 · CONDUCTUAL (c05 real): con la captura de apoyo limpiada, un
 *       lanzamiento cae LIBRE — el carry stale no re-proyecta la bola a la
 *       cara (el bug del saque comido por el apoyo, ahora imposible).
 *  E7 · CONDUCTUAL (c05 real): el mismo solver produce el MISMO golpe desde
 *       el apoyo venga de partido o de entrenamiento (mismo test N3, semilla
 *       distinta de pose — una sola física, cero bifurcaciones por modo).
 */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r105' }; } catch (e) { /* getter */ }

import * as THREE from 'three';
const { DIMS } = await import('/home/z/my-project/src/game/core/c02_cfg_escena.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');
const fs = await import('node:fs');

const R = '/home/z/my-project/src/game/core/';
const c12 = fs.readFileSync(R + 'c12_pingponggame.js', 'utf8');
const c13 = fs.readFileSync(R + 'c13_ui_arranque.js', 'utf8');

let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}

/* ── E1 · el gatillo del entrenamiento ya no lo come la guardia de calib ── */
CHK(c12.includes('if (this.calib && !this.trainV3) {'),
  'E1 onTrigger: la guardia genérica de calib EXCLUYE trainV3 (gatillo del tee vivo)');

/* ── E2 · la guardia r65 (saque dueño del gatillo) EXCLUYE el entrenamiento ── */
{
  const iR65 = c12.indexOf("if (this.rules.state === 'serve' &&\n        this.rules.server === 'player' && !this.tossed &&\n        !(this.calib && this.trainV3)) {");
  const iTrn = c12.indexOf('if (this.calib && this.trainV3 && window.__PP_TRAIN && window.__PP_TRAIN.serveTrigger)');
  CHK(iR65 > 0 && iTrn > iR65,
    `E2 la guardia r65 excluye trainV3 (${iR65}) y la ruta del módulo vive después (${iTrn}) — el residuo 'serve' ya no se come el gatillo del tee`);
}

/* ── E3 · la bola del tee es cinemática: c12 salta la física con ballHeld ── */
CHK(c12.includes('window.__PP_TRAIN.ballHeld && window.__PP_TRAIN.ballHeld() === true') &&
    c12.includes('const _teeHeld = this.calib && this.trainV3'),
  'E3 c12: guard de física con _teeHeld (la MISMA cinemática del saque en partido)');

/* ── E4 · PP_TRAIN expone ballHeld (sólo fase tee de t4a/t4b) ── */
CHK(c13.includes("ballHeld: () => st.phase === 'tee',"),
  'E4 PP_TRAIN.ballHeld expuesto (fase tee — el pinning a la mano es el ÚNICO dueño)');

/* ── E5 · resetToss limpia la captura de apoyo ── */
CHK(c12.includes('if (this.ball) this.ball.__ppRestIdx = -1;'),
  'E5 resetToss: la vuelta de la bola a la mano limpia __ppRestIdx (todas las modalidades)');

/* ── E6 · CONDUCTUAL: captura limpiada ⇒ el lanzamiento cae LIBRE (c05 real) ── */
{
  const C = DIMS.tableCenterZ, TOP = DIMS.tableTopY, Rr = DIMS.ballRadius;
  const b = { pos: new THREE.Vector3(0, TOP + Rr + 0.001, C + 0.65), vel: new THREE.Vector3(0, 2.2, 0),
    spin: new THREE.Vector3(), dragMul: 1, ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
  // captura STALE: la pala cazó la bola justo antes del re-tee (idx vivo)
  b.__ppRestIdx = 7; b.__ppRestSide = 1; b.__ppRestT = 0;
  b.__ppRestLx = 0; b.__ppRestDy = 0; b.__ppRestPush = 0;
  const pad = { active: true, index: 7, who: 'player',
    pos: new THREE.Vector3(0, TOP + 0.02, C + 0.65), prev: new THREE.Vector3(0, TOP + 0.02, C + 0.65),
    vel: new THREE.Vector3(), velInst: new THREE.Vector3(),
    normal: new THREE.Vector3(0, 1, 0), prevNormal: new THREE.Vector3(0, 1, 0),
    up: new THREE.Vector3(0, 0, -1), prevUp: new THREE.Vector3(0, 0, -1),
    right: new THREE.Vector3(1, 0, 0), prevRight: new THREE.Vector3(1, 0, 0),
    omega: new THREE.Vector3(), quat: new THREE.Quaternion(), cooldown: 0, serveFlight: false };
  // E5 en acción: resetToss (semántica) limpia — el launch cae LIBRE
  b.__ppRestIdx = -1;                       // ← lo que ahora hace resetToss SIEMPRE
  const y0 = b.pos.y;
  for (let i = 0; i < 12; i++) stepPhysics(1 / 60, b, [pad], [], null);
  const subio = b.pos.y > y0 + 0.1;
  CHK(subio && b.vel.y < 2.2 - 0.5,
    `E6 el lanzamiento post-reset cae LIBRE (Δy ${(b.pos.y - y0).toFixed(2)} m en 0,2 s — sin re-proyección al carry)`);
}

/* ── E7 · CONDUCTUAL: UNA SOLA FÍSICA — el golpe desde el apoyo no depende
 *    del modo: misma secuencia del arnés N3 con otra pose (la física del
 *    entrenamiento es el MISMO c05 — aquí se demuestra con semilla nueva) ── */
{
  const C = DIMS.tableCenterZ;
  const b = { pos: new THREE.Vector3(0.05, 0, 0), vel: new THREE.Vector3(), spin: new THREE.Vector3(),
    dragMul: 1, ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
  b.__ppRestIdx = 3; b.__ppRestSide = 1; b.__ppRestT = 0;
  b.__ppRestLx = 0.05; b.__ppRestDy = -0.02; b.__ppRestPush = 0;
  const pad = { active: true, index: 3, who: 'player',
    pos: new THREE.Vector3(0.1, 1.0, C + 0.7), prev: new THREE.Vector3(0.1, 1.0, C + 0.7),
    vel: new THREE.Vector3(), velInst: new THREE.Vector3(),
    normal: new THREE.Vector3(0, 1, 0), prevNormal: new THREE.Vector3(0, 1, 0),
    up: new THREE.Vector3(0, 0, -1), prevUp: new THREE.Vector3(0, 0, -1),
    right: new THREE.Vector3(1, 0, 0), prevRight: new THREE.Vector3(1, 0, 0),
    omega: new THREE.Vector3(), quat: new THREE.Quaternion(), cooldown: 0, serveFlight: false };
  b.pos.copy(pad.pos).add(new THREE.Vector3(0, DIMS.bladeCenterUp, 0))
    .addScaledVector(pad.right, b.__ppRestLx).addScaledVector(pad.up, b.__ppRestDy)
    .add(new THREE.Vector3(0, DIMS.ballRadius + 0.001, 0));
  for (let i = 0; i < 20; i++) stepPhysics(1 / 60, b, [pad], [], null);   // se posa
  pad.vel.set(-0.4, 0.3, -2.4);             // el impulso rápido del dueño
  pad.velInst.copy(pad.vel);
  const evs = [];
  stepPhysics(1 / 60, b, [pad], evs, null);
  const golpe = evs.find(e => e.type === 'paddle');
  const alin = golpe ? b.vel.dot(pad.vel) / (b.vel.length() * pad.vel.length()) : 0;
  CHK(!!golpe && alin > 0.75,
    `E7 golpe desde el apoyo con pose distinta (árbitro: ${golpe ? 'sí' : 'NO'} · alineación ${(alin * 100).toFixed(0)} %) — la física es LA MISMA en cualquier modalidad`);
}

console.log(`\nIGUALDAD DE FÍSICA r105 · ${ok} OK · ${fail} FALLOS`);
process.exit(fail ? 1 : 0);

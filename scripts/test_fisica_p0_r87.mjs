#!/usr/bin/env node
/* CRAZY PING PONG · ARNÉS P0 r87 — los cuatro correctivos del informe del
 * dueño tras la V3.6.177 en el visor (V3.6.178-SDK6). Ejecuta la FUENTE REAL
 * en Node (patrón test_fisica_p0_r86) y verifica COMPORTAMIENTO:
 *   P0-1 REV2 · bola en mano LIBRE: el reanclaje vive SOLO en tossFromHand
 *               (la rama de bola en mano ya NO empuja nada)
 *   P0-7      · la inmunidad del toss exige bola SUBIENDO (vel.y > 0): la
 *               caída vuelve a ver la pala — nunca más la atraviesa
 *   P0-9      · §7.5-LITE: glitch de tracking (salto implícito > 30 m/s) ⇒
 *               velocidad CERO + ventana limpia + cuarentena 100 ms que
 *               BLOQUEA el contacto; un smash real de 12 m/s NO es glitch
 *   P0-8      · conducción natural del rival: objetivo suavizado (goal) +
 *               arco de aproximación + SUELO sobre la mesa (comportamiento)
 * Uso: node --no-warnings scripts/test_fisica_p0_r87.mjs
 */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';

globalThis.window = globalThis.window || globalThis;
const _mr = Math.random;
let _seed = 0x9e3779b9;
Math.random = () => {
  _seed |= 0; _seed = (_seed + 0x6d2b79f5) | 0;
  let t = Math.imul(_seed ^ (_seed >>> 15), 1 | _seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const { c05, c04, c06, DIMS } = await (async () => {
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const m4 = await import(fileURLToPath(new URL('../src/game/core/c04_fisica_ccd.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  const m6 = await import(fileURLToPath(new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url)));
  return { c05: m5, c04: m4, c06: m6, DIMS: m2.DIMS };
})();

const RAIZ = new URL('..', import.meta.url).pathname;
const src = (f) => readFileSync(RAIZ + f, 'utf-8');
// r101 · el bundle, disponible para TODAS las agujas (antes cada bloque lo leía)
const b95 = readFileSync(RAIZ + 'public/game.html', 'utf-8');   // r101 · el bundle, disponible para TODAS las agujas
const c00s = src('src/game/core/c00_pre_three.js');
const c02s = src('src/game/core/c02_cfg_escena.js');
const c04s = src('src/game/core/c04_fisica_ccd.js');
const c05s = src('src/game/core/c05_colisiones_ia_golpeo.js');
const c06s = src('src/game/core/c06_logros_stats_ia_rival.js');
const c12s = src('src/game/core/c12_pingponggame.js');

let ok = 0, fails = 0;
function aguja(nombre, cond, detalle = '') {
  if (cond) { ok++; console.log(`  ✓ ${nombre}`); }
  else { fails++; console.log(`  ✗ ${nombre}${detalle ? ' — ' + detalle : ''}`); }
}
const C = DIMS.tableCenterZ;

/* — P0-1 REV2 · bola en mano LIBRE; el reanclaje vive en tossFromHand ——— */
{
  const i0 = c12s.indexOf('bola apoyada en la mano libre');
  const iFin = c12s.indexOf('} else {', i0);
  const ramaMano = c12s.slice(i0, iFin);
  aguja('P0-1 · la rama de bola en mano NO reancla (bola libre sobre la mesa)',
    i0 > 0 && iFin > i0 && !ramaMano.includes('srv_reancla'));

  const a0 = c12s.indexOf('tossFromHand(i, assisted)');
  const aFin = c12s.indexOf('this.tossed = true;', a0);
  const span = c12s.slice(a0, aFin);
  aguja('P0-1 · el reanclaje nace en tossFromHand ANTES de sellar el toss',
    a0 > 0 && aFin > a0 && span.includes('srv_reancla') &&
    span.includes('DIMS.tableCenterZ + DIMS.tableHalfLength + 0.10'));
  aguja('P0-1 · el aviso sigue siendo UNA vez por intento (_srvReanclaAviso)',
    c12s.includes('_srvReanclaAviso = false') && span.includes('_srvReanclaAviso'));
  // r88 · el reanclaje SOLO procede con la bola DEBAJO del plano del tablero:
  // colocar/soltar la bola pegada a la mesa (encima o al borde) queda LIBRE.
  aguja('P0-1 · r88 · reanclaje exige bola BAJO el plano (colocar pegada = libre)',
    span.includes('this.ball.pos.y < DIMS.tableTopY - DIMS.ballRadius'));
  // r88 · gracia de mano stale: la bola NO salta al pecho en un parpadeo de
  // tracking (600 ms de congelación en la última pose válida).
  aguja('P0-1 · r88 · gracia de mano stale (_srvManoPose, 600 ms) en ambas ramas',
    c12s.includes('_srvManoPose(bh)') &&
    (c12s.match(/_srvManoPose\(bh\)/g) || []).length >= 2 &&
    c12s.includes('performance.now() - this._srvManoT < 600'));
}

/* — P0-7 · inmunidad del toss SOLO mientras la bola sube ——————————————— */
{
  const i0 = c12s.indexOf('const tossImmune');
  const iFin = c12s.indexOf('if (tossImmune) pads.length = 0;', i0);
  const span = c12s.slice(i0, iFin);
  aguja('P0-7 · la inmunidad exige bola SUBIENDO (vel.y > 0)',
    i0 > 0 && iFin > i0 && span.includes('this.ball.vel.y > 0'));
  aguja('P0-7 · la inmunidad sigue vaciando pads (el roce prematuro sigue muerto)',
    iFin > i0);
  aguja('P0-7 · la altura ABSOLUTA del lanzamiento asistido sigue viva (P0-2)',
    c12s.includes('2 * Math.abs(DIMS.gravity) * dH'));
}

/* — P0-9 · §7.5-LITE · glitch de tracking: velocidad CERO + cuarentena —— */
{
  // (a) detección + higiene completa
  const p = c04.createPaddleSim('player', 0);
  const q = new THREE.Quaternion();
  c04.updatePaddleSim(p, new THREE.Vector3(0, 1, 1.01), q, 16.7, 0.016);   // primera muestra
  c04.updatePaddleSim(p, new THREE.Vector3(0, 1, 2.01), q, 16.7 + 16, 0.016); // salto 1 m / 16 ms = 62 m/s
  aguja('P0-9 · salto implícito 62 m/s > 30 ⇒ glitch detectado',
    p.glitchT > 0.08 && p.glitchT < 0.10);
  aguja('P0-9 · velocidad CERO (ni vel ni velInst ni omega contaminadas)',
    p.vel.lengthSq() === 0 && p.velInst.lengthSq() === 0 && p.omega.lengthSq() === 0);
  aguja('P0-9 · ventana de velocidad limpia (el buffer no alimenta el lerp)',
    p.velBuf.length === 0);

  // (b) la cuarentena BLOQUEA el contacto real (mismo barrido que sí golpea)
  //     Cara de la pala mirando a +z (base por defecto), bola entrando
  //     PERPENDICULAR a la cara a la altura del centro de la hoja.
  const yHoja = 1.0 + DIMS.bladeCenterUp;
  const mkBola = () => ({
    pos: new THREE.Vector3(0, yHoja, C + 0.05),
    vel: new THREE.Vector3(0, 0, -2.5), spin: new THREE.Vector3(),
    __ppRestIdx: -1,
  });
  const pC = c04.createPaddleSim('player', 0);
  pC.pos.set(0, 1.0, C); pC.prev.copy(pC.pos); pC.active = true;
  const evs = [];
  pC.glitchT = 0;                       // CONTROL: la bola debe GOLPEAR
  c05.stepPhysics(0.016, mkBola(), [pC], evs);
  const golpearonCtrl = evs.some((e) => e.type === 'paddle');
  const pG = c04.createPaddleSim('player', 1);
  pG.pos.set(0, 1.0, C); pG.prev.copy(pG.pos); pG.active = true;
  pG.glitchT = DIMS.paddleGlitchT;      // CUARENTENA: mismo barrido, sin contacto
  const evsG = [];
  c05.stepPhysics(0.016, mkBola(), [pG], evsG);
  aguja('P0-9 · control: la bola que cae sobre la pala quieta GOLPEA (evento)',
    golpearonCtrl);
  aguja('P0-9 · con glitchT > 0 el MISMO barrido NO fabrica contacto',
    !evsG.some((e) => e.type === 'paddle'));

  // (c) un smash REAL (12 m/s implícitos a dt de frame) NUNCA es glitch
  const pR = c04.createPaddleSim('player', 2);
  c04.updatePaddleSim(pR, new THREE.Vector3(0, 1, 1), q, 40, 0.0833);
  c04.updatePaddleSim(pR, new THREE.Vector3(0, 1, 2), q, 56, 0.0833);  // 1 m / 83 ms = 12 m/s
  aguja('P0-9 · smash real 12 m/s a dt de frame ⇒ SIN cuarentena (vel viva)',
    pR.glitchT === 0 && pR.vel.length() > 5);
  aguja('P0-9 · parámetros en datos (DIMS.paddleGlitchSpeed/T)',
    DIMS.paddleGlitchSpeed === 30 && DIMS.paddleGlitchT === 0.10);
  aguja('P0-9 · la puerta de cuarentena vive en collidePaddleSweep',
    c05s.includes('if (pad.glitchT > 0) return false;'));
}

/* — P0-8 · conducción natural del rival ———————————————————————————————— */
{
  const cfg = { predictInterval: 0.2, errStd: 0.03, maxSpeed: 6, accel: 8,
    missBase: 0.2, smash: 0.3, minT: 0.5, maxT: 0.9, maxShotSpeed: 12 };
  const ai = new c06.OpponentAI(cfg, 1, new THREE.Vector3(0, 1.0, C + DIMS.tableHalfLength + 0.4));
  // (a) SUELO sobre la mesa: pala dentro de la huella y por DEBAJO del tablero
  ai.pos.set(0, DIMS.tableTopY - 0.05, C);
  ai.vel.set(0, -1, 0);
  const bolaLejos = { pos: new THREE.Vector3(0, 2, C - 2), vel: new THREE.Vector3(0, 0, 1),
    spin: new THREE.Vector3() };
  const ctx = { canHit: false, validBounce: false, rallyHits: 0,
    holdTarget: null, prevBall: null };
  ai.update(0.016, bolaLejos, ctx);
  aguja('P0-8 · la pala de la IA JAMÁS queda bajo la mesa (suelo topR + 3 cm)',
    ai.pos.y >= DIMS.tableTopY + 0.029);

  // (b) r88 · steering DIRECTO restaurado (revert del arco/goal de r87 que
  //     añadía camino y retraso: «movimientos curvos muy raros y falla
  //     muchos golpes») + la naturalidad vive en el SWING: roll LIGADO al
  //     efecto real y carga previa (back) que barre a través del contacto.
  aguja('P0-8 · steering directo: sin arco ni goal en el fuente (c06)',
    !c06s.includes('ARCO DE APROXIMACIÓN') && !c06s.includes('this.goal.lerp'));
  aguja('P0-8 · el roll de muñeca se LIGA al efecto real (lift, no azar)',
    c06s.includes('const lift = -spinX * sign') &&
    c06s.includes('roll: THREE.MathUtils.clamp(lift * 0.016'));
  aguja('P0-8 · carga previa del golpe (back) en el swing y en el render',
    c06s.includes('back: carga * (toca ? 0.5 : 1)') &&
    c06s.includes('back: 0.03') &&
    c12s.includes('const bck = (sw.back || 0) * (1 - e)'));
  aguja('P0-8 · rascador retirado con el arco (sin _aiArc)',
    !c06s.includes('_aiArc'));
}

/* — r89 · zona prohibida del saque + mango horizontal ————————————————— */
{
  aguja('r89 · mano libre EXENTA del clamp de mesa (solo la pala golpea)',
    c12s.includes('if (i !== this.ballHand) {') &&
    c12s.includes('this.clampPaddlePose(grip.position, tmpMountQ, true);'));
  aguja('r89 · bola APOYADA en la mesa (apoyo en topR) offline y online',
    (c12s.match(/DIMS.tableTopY - DIMS.tableThickness/g) || []).length >= 2 &&
    c12s.includes('this.ball.pos.y = DIMS.tableTopY + DIMS.ballRadius;'));
  aguja('r90 · cara ⟂ mesa y mango ∥ mesa (eje horizontal cruzado, cierre sobre el eje)',
    (c12s.match(/AIM_BLADE\.set\(0, 0\.22, 0\)/g) || []).length >= 2 &&
    c12s.includes('AIM_BLADE.set(0, 0.25, 0)') &&
    (c12s.match(/closQ\.setFromAxisAngle/g) || []).length >= 3 &&
    c12s.includes('AIM_FACE.y *= 0.35;'));
  aguja('r90 · §12.1 del estudio en DIMS (drag crisis 0.1267 · restitución 0.935)',
    c02s.includes('airDragK: 0.1267') && c02s.includes('tableRestitution: 0.935'));
}

/* — r91 · cadena cinemática del rival (golpe humano creíble) ——————————— */
{
    aguja('r101 · el cerebro de la cadena SIN helpers de brazo (mjQuintic/IK/OneEuro borrados)',
    !c06s.includes('mjQuintic') && !c06s.includes('solveArmIK') &&
    !c06s.includes('OneEuro') && c06s.includes('_clampPalaMesa'));;
  aguja('r91/r99ter · la cadena vive (plan → curva del gesto → jinete con fases)',
    c06s.includes('planCadena(contact, tBall, kind, fh)') &&
    c06s.includes('cadenaContacto(cx, cy, cz, v, TBola)') &&
    c06s.includes('updateCadena(dt, ball)') &&
    c06s.includes("phase = dRem > 0.30 ? 'back' : 'strike';") &&
    c06s.includes("ch.phase = 'follow';") && c06s.includes("ch.phase = 'recover';"));
  aguja('r91 · anclajes: plan con la predicción, impacto real afina (r99: con TBola), swing solo sin plan',
    c06s.includes('this.predictT = strike.t;') &&
    c06s.includes('this.cadenaContacto(cx, cy, cz, v, this._tBolaDe(ball, cx, cy, cz));') &&
    c06s.includes("if (!this.chain || this.chain.phase === 'follow' ||") &&
    c06s.includes('this.updateCadena(dt, ball);'));
  aguja('r99ter · cronómetro del jinete (esprint si el arco no cabe + tope de paso 13 cm)',
    c06s.includes('dRem > tRem * 7.8 ? 7.8') &&
    c06s.includes('if (_cadP.length() > 0.13) {'));
  aguja('r91 · c12 consume la cadena (rama de pose por fases del golpe)',
    c12s.includes("if (who === 'ai' && ai.chain && ai.chain.phase)") &&
    c12s.includes('mesh.position.copy(ch.cur);') &&
    c12s.includes('AIM_FACE.copy(ch.vdir || AIM_FWD);'));
  // r101 · RETIRO DEFINITIVO: el método, las cápsulas y TODOS los drivers
  // están BORRADOS del bundle (decisión del dueño tras r100).
  const bundle101 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  aguja('r101 · RETIRO DEFINITIVO: ni cápsulas ni GLB ni drivers en el bundle',
    !bundle101.includes('updateAIArm') && !bundle101.includes('_cargarArmasGLB') &&
    !bundle101.includes('aiArmGlb') && !bundle101.includes('OneEuro') &&
    bundle101.includes('EL RIVAL ES SOLO LA PALA'));
  // lección del bloqueo del dueño (hotfix r91): el ensamblado RECONSTRUYE los
  // bloques DEPS-FASE2 — cualquier const dentro de ellos DESAPARECE del
  // bundle y el escudo del bucle traga el ReferenceError cada frame (menú
  // vivo, gatillos muertos). Prohibido declarar dentro del bloque.
  const span12 = c12s.slice(c12s.indexOf('DEPS-FASE2-INICIO'), c12s.indexOf('DEPS-FASE2-FIN'));
  ;
  const construido = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  aguja('r101 · cero arañas de brazo (_armS/_gRig) en bundle y fuentes',
    !bundle101.includes('_armS') && !bundle101.includes('_gRigP') &&
    !c12s.includes('_armS') && !c12s.includes('R99_POSE_AGARRE'));
}

/* — identidad del build ————————————————————————————————————————————————— */
const VER_DIN = JSON.parse(readFileSync(RAIZ + 'src/game/VERSION.json', 'utf-8')).version;
{
    aguja('versión · c00 sella ' + VER_DIN, c00s.includes(VER_DIN));;
  aguja('guard · c02 lleva los parámetros del glitch en datos',
    c02s.includes('paddleGlitchSpeed: 30') && c02s.includes('paddleGlitchT: 0.10'));
  // r92 · el BUNDLE lleva el arco del golpe (c06) y la alineación
  // pala-brazo (c12) — los dos fixes del informe del dueño
  const bundle92 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
    aguja('r101 · el BUNDLE lleva el ARCO DEL HOMBRO (nudos a radio de brazo + histéresis de caza)',
    b95.includes('EL HOMBRO MANDA') && b95.includes('HISTÉRESIS de la caza') &&
    b95.includes('_clampPalaMesa'));;
    aguja('r101 · la pala la mueve la cadena (updateAIPaddlePose copia ch.cur y clampPaddlePose cierra)',
    b95.includes('mesh.position.copy(ch.cur)') &&
    b95.includes('clampPaddlePose(mesh.position, mesh.quaternion, false)'));;
}

/* — r93 · brazos GLB ————————————————————————————————————————————— */
{
  // r93 · los BRAZOS GLB van en el bundle (los dos brazos reales del dueño)
  const b93 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
    aguja('r101 · sin driver de brazos GLB (updateAIArmGlb fuera del bundle)',
    !b95.includes('updateAIArmGlb') && !b95.includes('R99_CREASE'));;
  aguja('r93 · el GLB del rival viaja como fichero público',
    readFileSync(RAIZ + 'public/vr_arm.glb').length > 2_000_000);
}

/* — r94 · material de los brazos + marco del rig ————————————————— */
{
  // informe del dueño (video error.mp4): «el material de los brazos no
  // aparece» (spec-gloss retirado de three r163+ → blanco metálico) y
  // «brazos mal colocados, pala no agarrada» (captura/driver en MARCO
  // MUNDO mientras el juego vive en MARCO RIG — el recentrado XR horneara
  // su giro en los brazos)
  const b94 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
    aguja('r101 · la pose del rival es SOLO la cadena (rama chain en updateAIPaddlePose)',
    b95.includes("ai.chain && ai.chain.phase") &&
    b95.includes("ch.phase === 'strike' || ch.phase === 'follow'"));;
  ;
  ;
    aguja('versión · el bundle sella ' + VER_DIN, b95.includes(VER_DIN));;
}

/* — r95 · BRAZOS NATURALES (video mal.mp4 del dueño: dedos retorcidos,
 * temblor tipo descarga, pala no agarrada, bola sin sostener) ——————— */
{
  // r99 · el curl estático r95 pasa al sistema DINÁMICO por pose (plan r99)
    aguja('r101 · el contacto ES la pala: ventana por proximidad con anticipación de frames',
    b95.includes('const cerca = this._disparo && vivo') &&
    b95.includes('anticipa'));;
  // r99 · RETIRO DE BRAZOS: el rival es SOLO la pala flotante
    aguja('r101 · el rival es SOLO pala: ni vr_arm.glb se pide ni cápsulas existen',
    !b95.includes("fetch('./vr_arm.glb')") && !b95.includes('this.aiArm ='));;
  // r99 · DISPARO DIFERIDO: la bola sale SOLO cuando la pala llega al contacto
  aguja('r99 · DISPARO DIFERIDO (contacto real bola-pala visible)',
    b95.includes('_preparaDisparo') && b95.includes('_aplicaDisparo') &&
    b95.includes('this._retPend') && !b95.includes('ball.pos.set(cx, cy, cz);'));
  // r99bis · ACOMPAÑAMIENTO NATURAL: gestos progresivos, sin empujones
    aguja('r101 · SIN teletransportes (tope de paso 13 cm · bola jamás recolocada · misma curva continúa)',
    b95.includes('if (_cadP.length() > 0.13) {') &&
    b95.includes('tCruce') && b95.includes('contactoHecho') &&
    !b95.includes('b.pos.copy(d.pos)'));;
    aguja('r101 · el follow-through ES la cola de la curva (frenado exp. · fin por arco o velocidad)',
    b95.includes("ch.phase = 'follow'") && b95.includes('finCurva'));;
  ;
  ;
  // r99 · el mango vive en la CREASE de los nudillos (offset medido del GLB)
  ;
  aguja('r95 · CODA DE CADENA (la espera funde el último cur: sin tirón de 24 cm)',
    b95.includes('r95 · CODA DE CADENA') &&
    b95.includes('this._codaPala.t') &&
    b95.includes('_ppUltCur.copy(ai.chain.cur'));
  ;
  aguja('r96 · el VIGILANTE DE BLOQUEO viaja en el bundle (beacon js_error + freeze_report + latido VR)',
    b95.includes('r96 · VIGILANTE DE BLOQUEO') &&
    b95.includes("e: 'freeze_report'") &&
    b95.includes("e: 'js_error'") &&
    b95.includes('navigator.sendBeacon(EP') &&
    b95.includes("document.visibilityState !== 'visible'"));
  ;
  ;
  aguja('r97 · el ESCUDO DEL BUCLE habla con el vigía (beacon anim_shield: el try/catch no emite window.onerror)',
    b95.includes("window.__PP_VIGIA = { suelta }") &&
    b95.includes("window.__PP_VIGIA.suelta({ e: 'anim_shield'") &&
    b95.includes('r97 · EL ESCUDO HABLA CON EL VIGÍA'));
  aguja('r98 · AVISO DE VERSIÓN NUEVA: banner rojo que compara con PAGES-VERSION.txt (network-first) y ofrece actualizar',
    b95.includes('r98 · AVISO DE VERSIÓN NUEVA') &&
    b95.includes("getElementById('ppAvisoVer')") &&
    b95.includes('PAGES-VERSION.txt?cb=') &&
    b95.includes("postMessage('SKIP_WAITING')") &&
    b95.includes("NUEVA VERSIÓN ' + nueva + ' DISPONIBLE"));
  aguja('r98 · la página NUCLEAR actualizar.html existe y borra SW + cachés',
    existsSync(RAIZ + '/public/actualizar.html') &&
    readFileSync(RAIZ + '/public/actualizar.html', 'utf-8')
      .includes('serviceWorker.getRegistrations()'));
}

console.log(`\nARNÉS P0 r87 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

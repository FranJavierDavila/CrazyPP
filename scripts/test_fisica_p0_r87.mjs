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
  aguja('r91 · cadena en el cerebro (quíntico + IK + tabla por golpe exportados)',
    c06s.includes('export const CADENA_GOLPE') &&
    c06s.includes('export function mjQuintic') &&
    c06s.includes('export function mjQuinticVel') &&
    c06s.includes('export function solveArmIK') &&
    c06s.includes('export function adivinaKind'));
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
  // r99 · RETIRO DE BRAZOS: el método y las cápsulas quedan MUERTOS en el
  // bundle (revertible) pero la puerta que los pintaba está eliminada.
  aguja('r99 · brazo retirado (método muerto en bundle, gate eliminado, pala sola)',
    c12s.includes('updateAIArm(ai) {') &&
    c12s.includes('solveArmIK(_armS, _armW, 0.26, 0.24, _armP, _armE)') &&
    c12s.includes('new THREE.CapsuleGeometry(0.030, 1, 5, 10)') &&
    c12s.includes('_armW.addScaledVector(_armA, 0.105);') &&
    !c12s.includes('const armVis = this.aiPaddleMesh.visible && !this.net.online && !this.calib;'));
  // lección del bloqueo del dueño (hotfix r91): el ensamblado RECONSTRUYE los
  // bloques DEPS-FASE2 — cualquier const dentro de ellos DESAPARECE del
  // bundle y el escudo del bucle traga el ReferenceError cada frame (menú
  // vivo, gatillos muertos). Prohibido declarar dentro del bloque.
  const span12 = c12s.slice(c12s.indexOf('DEPS-FASE2-INICIO'), c12s.indexOf('DEPS-FASE2-FIN'));
  aguja('r91-hotfix · arañas _arm* FUERA del bloque DEPS (sobreviven al ensamblado)',
    span12.length > 0 && !span12.includes('const _arm') &&
    c12s.slice(c12s.indexOf('DEPS-FASE2-FIN')).includes('const _armS = new THREE.Vector3()'));
  const construido = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  aguja('r91-hotfix · el BUNDLE lleva la declaración _armS y ≥8 referencias',
    construido.includes('const _armS = new THREE.Vector3()') &&
    (construido.match(/_armS/g) || []).length >= 8);
}

/* — identidad del build ————————————————————————————————————————————————— */
{
  aguja('versión · c00 sella 3.6.197-SDK6', c00s.includes('3.6.197-SDK6'));
  aguja('guard · c02 lleva los parámetros del glitch en datos',
    c02s.includes('paddleGlitchSpeed: 30') && c02s.includes('paddleGlitchT: 0.10'));
  // r92 · el BUNDLE lleva el arco del golpe (c06) y la alineación
  // pala-brazo (c12) — los dos fixes del informe del dueño
  const bundle92 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  aguja('r92/r99ter · el BUNDLE lleva el ARCO del golpe (carga al lado + cruce en los nudos de la curva)',
    bundle92.includes('cuerda/tangente del ARCO del golpe') &&
    bundle92.includes('r92 · carga al lado') &&
    bundle92.includes('r92 · cruce al otro'));
  aguja('r92 · el BUNDLE lleva LA PALA ES LA CONTINUACIÓN DEL BRAZO (giro mínimo premultiply)',
    bundle92.includes('LA PALA ES LA CONTINUACIÓN DEL BRAZO') &&
    bundle92.includes('premultiply(_armQ)') &&
    bundle92.includes('const _armBx = new THREE.Vector3()'));
}

/* — r93 · brazos GLB ————————————————————————————————————————————— */
{
  // r93 · los BRAZOS GLB van en el bundle (los dos brazos reales del dueño)
  const b93 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  aguja('r93 · el BUNDLE lleva los brazos GLB (carga + driver rígido)',
    b93.includes("fetch('./vr_arm.glb')") &&
    b93.includes('LOS BRAZOS REALES') &&
    b93.includes('solveArmIKRigido') &&
    b93.includes('zonaDulceNudge') &&
    b93.includes('LA PALA ES LA CONTINUACIÓN DEL BRAZO') &&
    b93.includes('OneEuroV3'));
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
  aguja('r94 · el BUNDLE reconstruye el MATERIAL del GLB (textura difusa embebida + respaldo piel)',
    b94.includes("getDependency('texture', 0)") &&
    b94.includes('SRGBColorSpace') &&
    b94.includes('0xb08a70'));
  aguja('r94 · la CAPTURA del rig es RIG-LOCAL (adiós al giro hornedado del recentrado)',
    b94.includes('CAPTURA EN MARCO DEL RIG') &&
    b94.includes('_rigQinv') &&
    b94.includes('_alRig(body.getWorldPosition'));
  aguja('r94 · el DRIVER convierte rig-local ⇄ mundo (quats deseadas premultiply _gRigQ)',
    (b94.match(/premultiply\(_gRigQ\)/g) || []).length >= 6 &&
    b94.includes('_gRigP.setFromMatrixPosition(this.rig.matrixWorld)'));
  aguja('r94 · versión sella 3.6.197-SDK6 en el bundle',
    b94.includes('3.6.197-SDK6'));
}

/* — r95 · BRAZOS NATURALES (video mal.mp4 del dueño: dedos retorcidos,
 * temblor tipo descarga, pala no agarrada, bola sin sostener) ——————— */
{
  const b95 = readFileSync(RAIZ + 'public/game.html', 'utf-8');
  // r99 · el curl estático r95 pasa al sistema DINÁMICO por pose (plan r99)
  aguja('r99 · el BUNDLE lleva el CURL DINÁMICO por pose (+Y local, relativa al bind)',
    b95.includes('R99_POSE_AGARRE') &&
    b95.includes('multiply(dd.bindQ)') &&
    b95.includes("pulgarY: (c.lado === 'B') ? 1 : -1"));
  // r99 · RETIRO DE BRAZOS: el rival es SOLO la pala flotante
  aguja('r99 · el rival es SOLO pala (GLB de brazos sin cargar, cápsulas ocultas)',
    b95.includes('// this._cargarArmasGLB();') &&
    b95.includes('if (this.aiArm && this.aiArm.visible) this.aiArm.visible = false;'));
  // r99 · DISPARO DIFERIDO: la bola sale SOLO cuando la pala llega al contacto
  aguja('r99 · DISPARO DIFERIDO (contacto real bola-pala visible)',
    b95.includes('_preparaDisparo') && b95.includes('_aplicaDisparo') &&
    b95.includes('this._retPend') && !b95.includes('ball.pos.set(cx, cy, cz);'));
  // r99bis · ACOMPAÑAMIENTO NATURAL: gestos progresivos, sin empujones
  aguja('r99ter · SIN teletransportes (tope de paso · bola jamás recolocada · follow propio)',
    b95.includes('if (_cadP.length() > 0.13) {') &&
    b95.includes('tCruce') && b95.includes('_armaFollow') &&
    !b95.includes('b.pos.copy(d.pos)'));
  aguja('r95 · la zona dulce SOLO en strike (el follow ya no persigue la bola: látigo=0)',
    b95.includes('r95 · zona dulce SOLO en strike') &&
    b95.includes("const enStrike = !!(ch && ch.phase === 'strike')"));
  aguja('r95 · ENVOLTURA NATURAL del alcance (tan 0.96/1.25 · radio 88 % con la mano alta)',
    b95.includes('r95 · ENVOLTURA NATURAL') &&
    b95.includes('Math.tan(bolaAlta ? 1.25 : 0.96)') &&
    b95.includes('0.88 * (R.L1 + R.L2)'));
  aguja('r95 · EL CUERPO ES UNA PERSONA (pecho 0.42 m detrás del borde · x ±1.15 · yaw suave)',
    b95.includes('r95 · EL CUERPO ES UNA PERSONA') &&
    b95.includes('tableHalfLength + 0.42') &&
    b95.includes('R.yaw += (yawDeseado - R.yaw)'));
  // r99 · el mango vive en la CREASE de los nudillos (offset medido del GLB)
  aguja('r99 · EL MANGO VIVE EN LA CREASE DE LA MANO (pala anclada a los nudillos)',
    b95.includes('R99_CREASE') &&
    b95.includes('offCrease[bp.lado]') &&
    b95.includes('D_GRIP - R99_DCREASE'));
  aguja('r95 · CODA DE CADENA (la espera funde el último cur: sin tirón de 24 cm)',
    b95.includes('r95 · CODA DE CADENA') &&
    b95.includes('this._codaPala.t') &&
    b95.includes('_ppUltCur.copy(ai.chain.cur'));
  aguja('r95 · la bola del saque descansa SOBRE la palma (mano −4,5 cm bajo la bola)',
    b95.includes('r95 · la mano DEBAJO de la'));
  aguja('r96 · el VIGILANTE DE BLOQUEO viaja en el bundle (beacon js_error + freeze_report + latido VR)',
    b95.includes('r96 · VIGILANTE DE BLOQUEO') &&
    b95.includes("e: 'freeze_report'") &&
    b95.includes("e: 'js_error'") &&
    b95.includes('navigator.sendBeacon(EP') &&
    b95.includes("document.visibilityState !== 'visible'"));
  aguja('r96 · la muñeca anatómica tiene perpendicular GARANTIZADA (adiós al NaN de la cruz cero)',
    b95.includes('r96 · perpendicular GARANTIZADA') &&
    b95.includes('Math.abs(_gHandY.x) < 0.9') &&
    b95.includes('_gVz.crossVectors(_gHandZ, _gHandY)') &&
    b95.includes('const _gVz = new THREE.Vector3()'));
  aguja('r97 · FIX BLOQUEO: la cruz hand-Z es Vector3 (JAMÁS sobre un Quaternion)',
    b95.includes('r97 · FIX DEL BLOQUEO DEL CASCO') &&
    !/const _gQe = new THREE\.Quaternion\(\)[\s\S]{0,400}_gQe\.crossVectors/.test(b95) &&
    b95.includes('_gMx.makeBasis(_gHandZ, _gHandY, _gVz)'));
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

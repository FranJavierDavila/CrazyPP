export const MAX_SUBSTEP_DT = 1 / 480;
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { DIMS, SERVE_TUNE } from './c02_cfg_escena.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */
export const tmpPrev = new THREE.Vector3();
export const padPos = new THREE.Vector3();
const relPrev = new THREE.Vector3();
const relNow = new THREE.Vector3();
export const crossPoint = new THREE.Vector3();
export const relVel = new THREE.Vector3();
export const tmpN = new THREE.Vector3();
export const tmpM = new THREE.Vector3();
export const tmpS = new THREE.Vector3();
export const tmpT = new THREE.Vector3();
export const tmpD = new THREE.Vector3();
export const tmpV = new THREE.Vector3();
export const tmpSurf = new THREE.Vector3();
export const tmpR = new THREE.Vector3();
const tmpDeltaQ = new THREE.Quaternion();
export const tmpMountQ = new THREE.Quaternion();
const VEL_WINDOW = 0.045;  // v3.1.0-SRV2: el filtro vivo es SERVE_TUNE.velWindow (mismo valor)
// v2.29: base del paso anterior para la colisión barrida CON ROTACIÓN
// (antes solo se interpolaba la posición: en saques con mucha rotación de
// muñeca la hoja "giraba" entre subpasos y el cruce se detectaba tarde)
export const ipNormal = new THREE.Vector3();
export const ipRight = new THREE.Vector3();
export const ipUp = new THREE.Vector3();
export const tmpTarget = new THREE.Vector3();
const tmpShoulder = new THREE.Vector3();
const tmpDir = new THREE.Vector3();

/* =====================================================================
 *  v3.1.2-CCD1 · CCD POR SDF — BARRIDO BOLA↔PALA EN EL ESPACIO LOCAL
 *  ---------------------------------------------------------------------
 *  Requisito del dueño: «me falta precisión en la detección del contacto».
 *  Diagnóstico (túnel): a 90 Hz una bola de 25 m/s avanza 28 cm por frame
 *  (7 diámetros) y la zona de contacto mide ±26 mm — la detección discreta
 *  sólo acierta ~19 % de las veces aunque la pala esté quieta.
 *  Solución: CCD EXACTA. El segmento de la bola (inicio y fin del intervalo)
 *  se transforma al espacio LOCAL de la pala en su pose al inicio (τa) y al
 *  fin (τb) del intervalo — así se absorben DE UNA VEZ el movimiento y la
 *  rotación de la pala — y ahí se resuelve «segmento (con radio) contra una
 *  forma fija» con el SDF del disco con grosor y avance conservador (el SDF
 *  es 1-Lipschitz: dar un paso igual a la distancia libre NUNCA se salta la
 *  superficie). Exacto en caras, bordes y canto; pocas operaciones; sin
 *  motor físico; CERO asignaciones por frame.
 *  LA RESPUESTA DE LA BOLA NO CAMBIA (FIS1 intacto): sólo cómo se detecta
 *  el contacto. Velocidades de la pala SIN suavizar para la geometría
 *  (pad.prev→pad.pos son las poses reales del frame; el filtro de la mano
 *  de updatePaddleSim sigue sólo en el impulso, como siempre).
 *  Todo configurable en CCD_TUNE (vivo en window.__ppDebug.ccdTune).
 * ===================================================================== */
export const CCD_TUNE = {
  bladeHalfT: 0.004,      // semigrosor de la hoja (m) — el VISOR dibuja halfT 0.004
  hanY0: -0.21,           // cápsula del mango (frame centro-de-hoja): y inicial
  hanY1: -0.07,           // y final (el agarre vive a -0.14: banda ly ∈ (-0.26,-0.02))
  hanR: 0.05,             // radio del mango (banda |lx| < 0.05 del detector antiguo)
  eps: 1e-5,              // 0.01 mm: umbral de contacto del barrido
  maxIter: 32,            // iteraciones máximas del avance conservador
  glaze: 2e-4,            // tras maxIter, rasante < 0.2 mm cuenta como contacto
  faceK: 0.7,             // |z| ≥ halfT + r·faceK ⇒ golpe «por la cara» (normal de cara,
                          // idéntica al detector antiguo); menos ⇒ rim (normal SDF)
};

/* SDF del disco con grosor (pala), en espacio LOCAL (origen = centro de la
 * hoja, eje Z = normal de cara). Devuelve distancia con signo al sólido.
 * Fórmula exacta para el cilindro: cara (qy), canto (qx) y esquina
 * (hipotenusa); interior por max. */
export function sdfBlade(x, y, z, R, hT) {
  const qx = Math.hypot(x, y) - R;
  const qy = Math.abs(z) - hT;
  const ox = qx > 0 ? qx : 0, oy = qy > 0 ? qy : 0;
  return Math.min(Math.max(qx, qy), 0) + Math.hypot(ox, oy);
}

/* SDF de cápsula vertical (mango), espacio local del centro de hoja. */
function sdfCapsuleY(x, y, z, y0, y1, r) {
  const cy = y < y0 ? y0 : y > y1 ? y1 : y;
  return Math.hypot(x, y - cy, z) - r;
}

/* Barrido conservador del segmento [a→b] contra el SDF de la HOJA expandido
 * por el radio de la bola. Devuelve t ∈ [0,1] del PRIMER contacto o -1.
 * (Bucle especializado sin closures: CERO asignaciones.) */
export function sweepBallVsBlade(ax, ay, az, bx, by, bz, R, hT, ballR) {
  const eps = CCD_TUNE.eps, maxIter = CCD_TUNE.maxIter;
  const dx = bx - ax, dy = by - ay, dz = bz - az;
  const len = Math.hypot(dx, dy, dz);
  if (sdfBlade(ax, ay, az, R, hT) - ballR <= eps) return 0; // ya en contacto/penetrando
  if (len < 1e-9) return -1;
  let t = 0, dist = 0;
  for (let i = 0; i < maxIter; i++) {
    dist = sdfBlade(ax + dx * t, ay + dy * t, az + dz * t, R, hT) - ballR;
    if (dist <= eps) return t;
    t += dist / len;                 // avance conservador: nunca se salta la superficie
    if (t > 1) return -1;
  }
  return dist < CCD_TUNE.glaze ? t : -1;   // casi rasante tras maxIter: contacto
}

/* Barrido bola↔mango (cápsula vertical), mismas garantías. */
export function sweepBallVsCapsuleY(ax, ay, az, bx, by, bz, y0, y1, r, ballR) {
  const eps = CCD_TUNE.eps, maxIter = CCD_TUNE.maxIter;
  const dx = bx - ax, dy = by - ay, dz = bz - az;
  const len = Math.hypot(dx, dy, dz);
  if (sdfCapsuleY(ax, ay, az, y0, y1, r) - ballR <= eps) return 0;
  if (len < 1e-9) return -1;
  let t = 0, dist = 0;
  for (let i = 0; i < maxIter; i++) {
    dist = sdfCapsuleY(ax + dx * t, ay + dy * t, az + dz * t, y0, y1, r) - ballR;
    if (dist <= eps) return t;
    t += dist / len;
    if (t > 1) return -1;
  }
  return dist < CCD_TUNE.glaze ? t : -1;
}

/* Normal LOCAL del SDF del disco (gradiente analítico): cara, canto o
 * esquina redondeada. Se escribe en el Vector3 `n`. */
export function bladeNormalLocal(x, y, z, R, hT, n) {
  const rho = Math.hypot(x, y);
  const qx = rho - R, qy = Math.abs(z) - hT;
  const sz = z >= 0 ? 1 : -1;
  if (qx > 0 && qy > 0 && rho > 1e-9) {            // esquina redondeada
    n.set(qx * x / rho, qx * y / rho, qy * sz).normalize();
  } else if (qx > qy && rho > 1e-9) {              // canto
    n.set(x / rho, y / rho, 0);
  } else {                                         // cara
    n.set(0, 0, sz);
  }
  return n;
}

/* Scratches de la CCD (preasignados: CERO asignaciones por frame). */
export const ccdPosA = new THREE.Vector3(), ccdPosB = new THREE.Vector3();
export const ccdNrmA = new THREE.Vector3(), ccdNrmB = new THREE.Vector3();
export const ccdRgtA = new THREE.Vector3(), ccdRgtB = new THREE.Vector3();
export const ccdUpA = new THREE.Vector3(), ccdUpB = new THREE.Vector3();
export const ccdC0 = new THREE.Vector3(), ccdC1 = new THREE.Vector3();
export const ccdP = new THREE.Vector3();
export const ccdNL = new THREE.Vector3();

export function createPaddleSim(who, index) {
  return {
    pos: new THREE.Vector3(),
    prev: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    velInst: new THREE.Vector3(),   // v2.29: velocidad instantánea (sin media móvil)
    omega: new THREE.Vector3(),
    prevQuat: new THREE.Quaternion(),
    quatInit: false,
    velBuf: [],
    prevT: -1,
    normal: new THREE.Vector3(0, 0, 1),
    right: new THREE.Vector3(1, 0, 0),
    up: new THREE.Vector3(0, 1, 0),
    // v2.29: base del frame anterior (colisión barrida con rotación)
    prevNormal: new THREE.Vector3(0, 0, 1),
    prevRight: new THREE.Vector3(1, 0, 0),
    prevUp: new THREE.Vector3(0, 1, 0),
    cooldown: 0,
    who,
    index,
    active: false,
  };
}

export function setPaddleBasis(p, q) {
  p.normal.set(0, 0, 1).applyQuaternion(q);
  p.right.set(1, 0, 0).applyQuaternion(q);
  p.up.set(0, 1, 0).applyQuaternion(q);
}

/** Aerodinámica (arrastre + Magnus + decaimiento del giro) compartida
 *  por la física real y TODOS los simuladores: una sola ecuación. */
export function applyAerodynamics(vel, spin, h, dragMul) {
  // v2.102: dragMul — la bola-bomba PESA (0.30 en el asedio): corta el aire
  // y los tiros altos llegan a la diana (el drag 0.142 del ping-pong se
  // comía la mitad de la velocidad en 1 s y la bomba caía 2-4 m antes).
  const dm = (dragMul === undefined) ? 1 : dragMul;
  const sp = vel.length();
  if (sp > 1e-6) {
    vel.multiplyScalar(Math.max(0, 1 - DIMS.airDragK * dm * sp * h));
  }
  if (spin.lengthSq() > 1e-4) {
    tmpM.crossVectors(spin, vel).multiplyScalar(DIMS.magnus * h);
    vel.add(tmpM);
    spin.multiplyScalar(Math.max(0, 1 - DIMS.spinDecayAir * h));
  }
}

/**
 * Seguimiento de precisión del mando:
 *  - velocidad lineal = media móvil en una ventana de 70 ms (estable ante
 *    el jitter del tracking, imprescindible para golpes reproducibles);
 *  - velocidad angular (rad/s) a partir del delta de cuaterniones, para
 *    poder dar efecto con la muñeca como con una pala real.
 */
export function updatePaddleSim(ps, pos, quat, now, dt) {
  ps.prev.copy(ps.pos);
  // v2.29: conservar la base ORIENTADA del frame anterior (barrido con giro)
  ps.prevNormal.copy(ps.normal);
  ps.prevRight.copy(ps.right);
  ps.prevUp.copy(ps.up);
  ps.pos.copy(pos);
  setPaddleBasis(ps, quat);

  if (ps.prevT > 0 && dt > 0) {
    tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt);
    // v2.29: velocidad INSTANTÁNEA disponible (con techo anti-picos)
    ps.velInst.copy(tmpV);
    if (ps.velInst.length() > DIMS.paddleVelClamp) ps.velInst.setLength(DIMS.paddleVelClamp);
    ps.velBuf.push({ t: now, x: tmpV.x, y: tmpV.y, z: tmpV.z });
  }
  while (ps.velBuf.length && now - ps.velBuf[0].t > SERVE_TUNE.velWindow) ps.velBuf.shift();
  if (ps.velBuf.length) {
    tmpV.set(0, 0, 0);
    for (const s of ps.velBuf) {
      tmpV.x += s.x; tmpV.y += s.y; tmpV.z += s.z;
    }
    tmpV.divideScalar(ps.velBuf.length);
    // v2.29: respuesta más ágil (lerp configurable v3.1.0-SRV2) y techo de
    // velocidad: el impulso deja de llegar "esponja" en swings rápidos sin
    // meter jitter de tracking
    ps.vel.lerp(tmpV, SERVE_TUNE.velLerp);
    if (ps.vel.length() > DIMS.paddleVelClamp) ps.vel.setLength(DIMS.paddleVelClamp);
  }

  if (!ps.quatInit) {
    ps.prevQuat.copy(quat);
    ps.quatInit = true;
  }
  tmpDeltaQ.copy(ps.prevQuat).invert().premultiply(quat);
  if (tmpDeltaQ.w < 0) tmpDeltaQ.set(-tmpDeltaQ.x, -tmpDeltaQ.y, -tmpDeltaQ.z, -tmpDeltaQ.w);
  const ang = 2 * Math.acos(Math.min(1, tmpDeltaQ.w));
  if (ang > 1e-4 && dt > 0) {
    const s = Math.sqrt(Math.max(1e-12, 1 - tmpDeltaQ.w * tmpDeltaQ.w));
    tmpV.set(tmpDeltaQ.x / s, tmpDeltaQ.y / s, tmpDeltaQ.z / s).multiplyScalar(ang / dt);
    ps.omega.lerp(tmpV, 0.5);
  } else {
    ps.omega.multiplyScalar(Math.max(0, 1 - dt * 8));
  }
  ps.prevQuat.copy(quat);
  ps.prevT = now;
}

/** Efecto del giro al botar en la mesa: topspin acelera, backspin frena, lateral desvía. */
export function applyBounceSpin(vel, spin) {
  vel.x -= DIMS.bounceSpinKick * spin.z;
  vel.z += DIMS.bounceSpinKick * spin.x;
  spin.multiplyScalar(0.72);
}

/** v3.0.5-FIS1 · P2 — BOTE FÍSICO con deslizamiento (slip-coupled).
 *  UNA sola ecuación COMPARTIDA por collideTable (física real),
 *  predictStrike (IA) y simulateServePath (solver de saque): los tres
 *  predicen con la MISMA física nueva, sin réplicas a mano.
 *  · velocidad de la superficie de contacto: ux = vx + r·ωz, uz = vz − r·ωx
 *  · impulso tangencial que frena el deslizamiento con inercia de CASCARÓN
 *    (m_eff = 2/5·m para la bola reglamentaria hueca)
 *  · agarre de la mesa según el IMPACTO (grip 0,22 → 0,60) + tope de Coulomb
 *  · Δω = (rc × J)/I con I = 2/3·m·r² → Δωx = −(3/2r)·Δvz · Δωz = +(3/2r)·Δvx
 *  Resultado: el TOPSPIN patea al botar y conserva/gana giro, el BACKSPIN
 *  frena en seco y la mesa le come el efecto, el LATERAL desvía — y todo
 *  ESCALA con la velocidad de impacto. `impact` = |vel.y| de entrada. */
export function bounceOnTable(vel, spin, impact) {
  const r = DIMS.ballRadius;
  vel.y = impact * DIMS.tableRestitution;
  const ux = vel.x + r * spin.z;
  const uz = vel.z - r * spin.x;
  const g = DIMS.bounceGripMin + (DIMS.bounceGripMax - DIMS.bounceGripMin) *
            Math.min(1, impact / 4.5);
  // Δv (por unidad de masa) que anularía el deslizamiento: −u·m_eff/m = −u·2/5
  // con tope de Coulomb: |Δv| ≤ grip·(1+e)·impacto
  let dvx = -ux * 0.4 * g;
  let dvz = -uz * 0.4 * g;
  const dvm = Math.hypot(dvx, dvz);
  const cap = g * (1 + DIMS.tableRestitution) * impact;
  if (dvm > cap) { const s = cap / dvm; dvx *= s; dvz *= s; }
  vel.x += dvx;
  vel.z += dvz;
  // acoplo giro-velocidad del cascarón: Δωx = −(3/2r)·Δvz · Δωz = +(3/2r)·Δvx
  const kf = 1.5 / r;
  spin.x += -kf * dvz;
  spin.z += +kf * dvx;
}

/* =====================================================================
 *  v3.0.5-FIS1 · PALAS CON CARÁCTER
 *  Las skins del PRO TRAINING (conseguidas con puntos) ya son JUEGO:
 *  cada goma modula el golpe del JUGADOR (la IA siempre juega neutra).
 *    spin    → multiplicador de efecto (brush + agarre tangencial de la goma)
 *    power   → multiplicador de potencia (restitución + empuje del cuerpo)
 *    control → >1 el canto PERDONA (menos penalización de punto dulce),
 *              <1 el canto castiga más
 *    dual    → DOBLE GOMA: cada CARA de la hoja tiene su propia goma
 *              (cara de la normal = «A», cara trasera = «B»), como las
 *              palas reales de goma roja/negra
 *  Interruptor DIMS.paddlePerks (0 = todas las palas neutras, como siempre).
 *  La skin equipada vive en el perfil del entrenamiento (ppxr_train_v1) y
 *  el módulo la sincroniza con __PP_SET_PADDLE_SKIN; aquí además se lee al
 *  arrancar por si el módulo aún no ha despertado.
 * ===================================================================== */
const PADDLE_PERKS = {
  clasica:  { tag: 'perk_eq', col: '#8fa0b8', spin: 1.00, power: 1.00, control: 1.00 },
  fuego:    { tag: 'perk_of', col: '#ff7a4a', spin: 1.08, power: 1.12, control: 0.85 },
  hielo:    { tag: 'perk_de', col: '#63c8f0', spin: 1.00, power: 0.90, control: 1.30 },
  oro:      { tag: 'perk_po', col: '#f2c14e', spin: 0.94, power: 1.16, control: 1.00 },
  arcoiris: { tag: 'perk_ef', col: '#c07aff', spin: 1.22, power: 0.96, control: 1.00 },
  carbon:   { tag: 'perk_dg', col: '#ff2d2d', spin: 1.06, power: 1.06, control: 1.06,
              dual: { '1': { spin: 1.20, power: 1.00 },     // cara A: goma de GIRO
                     '-1': { spin: 0.92, power: 1.18 } } }, // cara B: goma DURA
};
let __ppEquippedSkin = 'clasica';
try {
  window.__PP_PADDLE_PERKS = PADDLE_PERKS;
  window.__PP_SET_PADDLE_SKIN = __ppSetPaddleSkin;
} catch (e) { /* */ }
function __ppSetPaddleSkin(id) {
  __ppEquippedSkin = (PADDLE_PERKS[id] ? id : 'clasica');
  try { window.__PP_PADDLE_SKIN = __ppEquippedSkin; } catch (e) { /* */ }
}
try {
  const rawSk = localStorage.getItem('ppxr_train_v1');
  if (rawSk) __ppSetPaddleSkin((JSON.parse(rawSk).skin) || 'clasica');
} catch (e) { /* sin localStorage: clásica */ }
/** Perks del golpe actual. `faceSide` = cara de la hoja que golpea
 *  (+1 = la que mira la normal de la pala, −1 = la trasera). */
export function paddlePerkFor(who, faceSide) {
  if (who !== 'player' || DIMS.paddlePerks < 0.5) return null;
  const p = PADDLE_PERKS[__ppEquippedSkin] || PADDLE_PERKS.clasica;
  if (p.dual) {
    const f = p.dual[faceSide] || {};
    return { spin: f.spin || 1, power: f.power || 1, control: p.control || 1 };
  }
  return { spin: p.spin, power: p.power, control: p.control };
}

/** v3.1.2-CCD1 · envoltorio compatible con la firma antigua: pose única en k
 *  (labs de QA, solver hook, rutas online). */

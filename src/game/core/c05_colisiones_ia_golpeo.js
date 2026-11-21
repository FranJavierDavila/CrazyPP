export function collidePaddle(ball, pad, k, events) {
  return collidePaddleSweep(ball, pad, k, k, events);
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T } from './c00_pre_three.js';
import { DIMS, SERVE_TUNE } from './c02_cfg_escena.js';
import { BOTE_TUNE, CCD_TUNE, MAX_SUBSTEP_DT, SOLVER_TUNE, applyAerodynamics, applyBounceSpin, bladeNormalLocal, bounceOnTable, ccdC0, ccdC1, ccdNL, ccdNrmA, ccdNrmB, ccdP, ccdPosA, ccdPosB, ccdRgtA, ccdRgtB, ccdUpA, ccdUpB, crossPoint, integraVuelo, ipNormal, ipRight, ipUp, padPos, paddlePerkFor, relVel, sweepBallVsBlade, sweepBallVsCapsuleY, tmpD, tmpM, tmpN, tmpPrev, tmpR, tmpS, tmpSurf, tmpT } from './c04_fisica_ccd.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

// r113 · temporales de la DIRECCIÓN AL OBJETIVO (módulo-local, cero colisión
// con los temporales compartidos de c04)
const tmpAim = new THREE.Vector3();
const tmpAim2 = new THREE.Vector3();

/* v3.1.2-CCD1 · DETECCIÓN CCD POR SDF (reemplaza al cruce de plano + disco).
 * Barrido del segmento de bola [tmpPrev → ball.pos] contra la pala barrida
 * entre las poses kA y kB del frame (pad.prev → pad.pos). kA/kB son las
 * fracciones del frame de cada extremo del SUBPASO (spec D: subpasos
 * alineados con P0→P1, no acumulador fijo). La pala se mueve y GIRA dentro
 * del subpaso y el barrido la absorbe de una vez (spec C: el inicio del
 * segmento se transforma con la pose τa y el fin con la pose τb).
 * Devuelve true si hubo golpe (respuesta clásica ya aplicada). */
export function collidePaddleSweep(ball, pad, kA, kB, events) {
  let imanAimUsado = false;   // v3.6.49: el golpe de este subpaso fue GUIADO por el Súper Imán
  // r87 · §7.5-LITE · CUARENTENA: con la pala en glitch (salto de tracking
  // recién detectado) NO hay contacto — el par prev→pos cruza el espacio y
  // el barrido fabricaría un golpe imposible. Los test headless fijan pos a
  // mano sin updatePaddleSim: glitchT indefinido ⇒ undefined > 0 = false.
  if (pad.glitchT > 0) return false;
  // --- poses A (kA) y B (kB) de la pala dentro del frame (nlerp como v2.29) ---
  ccdPosA.copy(pad.prev).lerp(pad.pos, kA);
  ccdNrmA.copy(pad.prevNormal).lerp(pad.normal, kA).normalize();
  ccdRgtA.copy(pad.prevRight).lerp(pad.right, kA).normalize();
  ccdUpA.copy(pad.prevUp).lerp(pad.up, kA).normalize();
  ccdPosB.copy(pad.prev).lerp(pad.pos, kB);
  ccdNrmB.copy(pad.prevNormal).lerp(pad.normal, kB).normalize();
  ccdRgtB.copy(pad.prevRight).lerp(pad.right, kB).normalize();
  ccdUpB.copy(pad.prevUp).lerp(pad.up, kB).normalize();

  // v3.1.0-SRV2 · margen extra de detección SOLO en el vuelo del saque
  // (bola recién lanzada): tolerancia PEQUEÑA, sin golpes a distancia.
  const extra = pad.extraReach || 0;
  const inPlane = pad.serveFlight ? SERVE_TUNE.serveFlightAssist : DIMS.hitAssistRadius;
  // v3.1.1-FEEL1 · GRACE del saque: ventana viva ⇒ el radio en el plano
  // crece lateInPlane durante el barrido (lo que se ve, cuenta).
  const grace = pad.serveFlight && (ball.__serveGrace || 0) > 0;

  // Radio de la HOJA en el plano: asistencia del juego incluida (rally
  // hitAssistRadius, saque serveFlightAssist + tiers). El SDF expansiona por
  // el radio de la bola APARTE — equivalente al reach antiguo (que sumaba
  // ballR al radio del disco).
  const Rb = DIMS.bladeRadius + inPlane + extra +
    (grace ? SERVE_TUNE.lateInPlane : 0);
  const hT = CCD_TUNE.bladeHalfT;
  const rB = DIMS.ballRadius;

  // Centros de hoja en mundo: C = pos + up·bladeCenterUp (la hoja vive sobre
  // el agarre; el plano de cara pasa por ambos, la normal es la misma).
  ccdC0.copy(ccdPosA).addScaledVector(ccdUpA, DIMS.bladeCenterUp);
  ccdC1.copy(ccdPosB).addScaledVector(ccdUpB, DIMS.bladeCenterUp);
  // --- segmento de la bola al espacio LOCAL de la pala ---
  ccdP.copy(tmpPrev).sub(ccdC0);
  const a0x = ccdP.dot(ccdRgtA), a0y = ccdP.dot(ccdUpA), a0z = ccdP.dot(ccdNrmA);
  ccdP.copy(ball.pos).sub(ccdC1);
  const b1x = ccdP.dot(ccdRgtB), b1y = ccdP.dot(ccdUpB), b1z = ccdP.dot(ccdNrmB);

  // Barrido contra la hoja y, en su defecto, contra el mango (cápsula)
  let t = sweepBallVsBlade(a0x, a0y, a0z, b1x, b1y, b1z, Rb, hT, rB);
  let onHandle = false;
  if (t < 0) {
    t = sweepBallVsCapsuleY(a0x, a0y, a0z, b1x, b1y, b1z,
      CCD_TUNE.hanY0, CCD_TUNE.hanY1, CCD_TUNE.hanR, rB);
    onHandle = t >= 0;
  }
  if (t < 0) {
    // v3.1.1-FEEL1 · armar la GRACE: golpe muy justo junto al borde, SOLO en
    // el vuelo del saque — misma condición que FEEL1 (pegada al plano en el
    // margen lateSkin y junto al borde en lateInPlane); la ventana caduca
    // sola (unos ms) y no inventa golpes a distancia.
    if (pad.serveFlight && !grace) {
      const reach0 = DIMS.bladeRadius + inPlane + extra;
      // el umbral incluye el radio de la bola (el SDF lo expansiona aparte,
      // pero el ARMADO se mide sobre el centro de la bola — semántica FEEL1:
      // reach antiguo = bladeR + ballR + asistencia)
      const nearBlade = Math.hypot(b1x, b1y) <=
        rB + reach0 + SERVE_TUNE.lateInPlane;
      const nearPlane = Math.abs(b1z) <= rB + SERVE_TUNE.skin +
        (extra ? SERVE_TUNE.skinServe : 0) + SERVE_TUNE.lateSkin;
      if (nearBlade && nearPlane) ball.__serveGrace = SERVE_TUNE.lateMs / 1000;
    }
    return false;
  }

  // ---- reconstrucción del impacto: pose de la pala en el instante t ----
  padPos.copy(ccdPosA).lerp(ccdPosB, t);
  ipNormal.copy(ccdNrmA).lerp(ccdNrmB, t).normalize();
  ipRight.copy(ccdRgtA).lerp(ccdRgtB, t).normalize();
  ipUp.copy(ccdUpA).lerp(ccdUpB, t).normalize();
  // Centro de la bola en el impacto y coordenadas locales (origen = agarre,
  // como el detector antiguo: lx en el plano, ly desde el agarre, dyy desde
  // el centro de la hoja).
  crossPoint.copy(tmpPrev).lerp(ball.pos, t);
  ccdC1.copy(padPos).addScaledVector(ipUp, DIMS.bladeCenterUp);
  ccdP.copy(crossPoint).sub(ccdC1);
  const lx = ccdP.dot(ipRight);
  const dyy = ccdP.dot(ipUp);
  const ly = dyy + DIMS.bladeCenterUp;

  // Normal de contacto (spec C). Golpe «por la cara» (llegó a la cara, no
  // rozó el rim): normal de CARA firmada por POSICIÓN — idéntico al FEEL1
  // (en reposo la posición manda; una bola que se separa no contacta y el
  // flip por velocidad ya no teleporta nada). Rim LATERAL (entradas que el
  // detector antiguo perdía): gradiente del SDF = canto exacto.
  const lhz = a0z + (b1z - a0z) * t;
  relVel.copy(ball.vel).sub(pad.vel);
  if (onHandle || Math.abs(lhz) >= hT + rB * CCD_TUNE.faceK) {
    tmpN.copy(ipNormal);
    if (lhz < 0) tmpN.negate();
  } else {
    bladeNormalLocal(lx, dyy, lhz, Rb, hT, ccdNL);
    tmpN.set(0, 0, 0)
      .addScaledVector(ipRight, ccdNL.x)
      .addScaledVector(ipUp, ccdNL.y)
      .addScaledVector(ipNormal, ccdNL.z);
  }
  const vRelN = relVel.dot(tmpN);
  if (vRelN >= 0) return false;   // ya se separan: no es un golpe (spec F)

  /* ================================================================
   * r100/r101 · CONTACTO DE REPOSO pala-bola (el estándar Eleven).
   * r100 lo estrenó con umbral dual 0,95 (pala lenta) / 0,65 (pala
   * viva) y el dueño lo devolvió: «no has sabido resolver lo del
   * contacto de la bola parada y has estropeado los saques» — con
   * 0,95 la pala SECUESTRABA botes legítimos (botar la bola sobre la
   * pala moría al tercer toque; llegadas suaves quedaban pegadas en
   * pleno intercambio). r101: umbral ÚNICO 0,25 m/s — se posa SÓLO
   * una bola realmente quieta (el redil de gravedad por frame ~0,14
   * m/s a 72 Hz queda dentro: el apoyo re-captura en silencio cada
   * frame, sin trompicones) y todo lo que llegue con vida BOTA por la
   * vía de golpe normal (restitución, spin y suelo FEEL1 de siempre,
   * byte a byte). El transporte en stepPhysics (bloque r100) sigue
   * arrastrando la bola apoyada 1:1 y el swing la suelta limpio:
   * levantar la pala la lanza al aire — Eleven. */
  // r86 · P0-3 · la captura exige además PALA QUIETA (restPadSpeed, el mismo
  // test del cooldown en stepPhysics): un levantamiento con intención (scoop,
  // pala subiendo) atraviesa a la vía de golpe normal y el suelo escalado le
  // da el toque suave — antes el secuestro de reposo se lo quedaba MUDO
  // (por debajo de restEventMin ni evento ni árbitro: «golpear la bola por
  // debajo de la altura de la mesa falla»).
  if (pad.who === 'player' && !pad.serveFlight && !onHandle &&
      Math.abs(lhz) >= hT &&
      -vRelN <= DIMS.paddleRestSpeed &&
      pad.vel.lengthSq() <= SERVE_TUNE.restPadSpeed * SERVE_TUNE.restPadSpeed) {
    // proyección a la cara (mismo patrón que la colocación del golpe)
    ball.pos.copy(padPos).addScaledVector(tmpN, rB + 0.001)
      .addScaledVector(ipRight, lx).addScaledVector(ipUp, ly);
    // anular la aproximación normal (la bola comparte la normal de la pala)
    ball.vel.addScaledVector(tmpN, -vRelN);
    // fricción tangencial + acople de giro (rueda en vez de vibrar)
    relVel.copy(ball.vel).sub(pad.vel);
    relVel.addScaledVector(tmpN, -relVel.dot(tmpN));      // tangencial relativa
    const slipR = relVel.length();
    if (slipR > 1e-4) {
      let dvR = slipR * DIMS.paddleRestFric;
      if (dvR > slipR) dvR = slipR;
      relVel.setLength(-dvR);
      ball.vel.add(relVel);
      // Δω = −(3/2r)·(N × Δv): el mismo acople cascarón del bote (FIS1)
      ball.spin.addScaledVector(tmpD.copy(tmpN).cross(relVel), -1.5 / DIMS.ballRadius);
    }
    const nuevo = ball.__ppRestIdx !== pad.index ||
      (ball.__ppRestT === undefined) || ball.__ppRestT > DIMS.paddleRestDrop;
    ball.__ppRestIdx = pad.index;
    ball.__ppRestSide = tmpN.dot(ipNormal) >= 0 ? 1 : -1;
    ball.__ppRestLx = lx;
    ball.__ppRestDy = dyy;
    ball.__ppRestT = 0;
    if (nuevo) {
      ball.__ppRestPush = 0;   // r86 P0-4: apoyo NUEVO = compresión a cero
      events.push({ type: 'restTouch', speed: -vRelN, pos: crossPoint.clone() });
    }
    return true;   // padHit: el subpaso aplaza mesa/red (la bola está en la pala)
  }

  // v3.0.5 P1: PUNTO DULCE — offC: 0 = centro de la hoja, 1 = canto.
  // El canto pega «sordo» (menos restitución), dispersa y da menos efecto.
  // El anillo de asistencia del saque (fuera de la hoja) penalización fija
  // suave para no castigar el saque asistido; el mango, zona muerta moderada.
  const bladeDist = Math.hypot(lx, dyy);
  let offC;
  if (onHandle) offC = 0.8;
  else if (bladeDist > DIMS.bladeRadius) offC = 0.55;
  else offC = bladeDist / DIMS.bladeRadius;
  // v3.0.5 · PALAS CON CARÁCTER: cara golpeada (+1 normal / −1 trasera) y
  // goma del jugador (null = IA o interruptor off → todo neutro como v2.x)
  const faceSide = tmpN.dot(ipNormal) >= 0 ? 1 : -1;
  const PK = (DIMS.physicsRealism >= 0.5) ? paddlePerkFor(pad.who, faceSide) : null;
  const ctl = PK ? PK.control : 1;
  const FIS = DIMS.physicsRealism >= 0.5;

  // Reflexión con pala "infinitamente masiva" en movimiento. Con FIS la
  // restitución baja con el punto dulce (el canto pega sordo) y la goma del
  // jugador modula la potencia.
  const ePad = DIMS.paddleRestitution * (PK ? PK.power : 1) *
               (1 - (FIS ? DIMS.edgeRestLoss : 0) * offC * offC / ctl);
  ball.vel.addScaledVector(tmpN, -(1 + ePad) * vRelN);

  // Golpe con CUERPO: transfiere parte de la velocidad de la pala en la
  // dirección de salida (acelerar la mano = bola más rápida, siempre)
  // r113 · FÍSICA DEL GOLPE FUERTE (petición del dueño: la bola debe salir
  // con la VELOCIDAD REAL del swing): 0,22 sólo transfería una quinta parte
  // del empuje — un smash de 10 m/s aportaba 2,2 m/s y el golpe «no se
  // sentía». 0,40 transfiere el doble sin romper los toques suaves (el
  // término sólo opera con padN > 0: pala acercándose a la bola).
  const padN = pad.vel.dot(tmpN);
  if (padN > 0) ball.vel.addScaledVector(tmpN, padN * 0.40 * (PK ? PK.power : 1));

  // v3.0.5 P1: bamboleo del canto — golpes cerca del borde dispersan
  if (FIS && offC > 0.7) {
    const j = DIMS.edgeJitter * (offC - 0.7) / 0.3 / ctl;
    ball.vel.x += (Math.random() * 2 - 1) * j;
    ball.vel.z += (Math.random() * 2 - 1) * j;
  }

  // Velocidad mínima de salida para jugabilidad (golpes siempre sólidos).
  // v3.1.0-SRV2 · en el VUELO DEL SAQUE el suelo es serveMinExit: un roce
  // sale flojo y el árbitro lo juzga (falta) — el suelo pleno de 2,3 m/s
  // disfrazaba los roces como saques válidos.
  // v3.1.1-FEEL1 · el suelo es de los GOLPES, no del rebote (requisito del
  // dueño): escala con la velocidad de la pala — quieta => sin suelo y los
  // botes decaen con la restitución natural hasta pararse; swing real =>
  // suelo pleno de 2,3 m/s INTACTO (el resto del juego no cambia).
  const vn = ball.vel.dot(tmpN);
  let exitFloor;
  if (pad.serveFlight) {
    exitFloor = SERVE_TUNE.serveMinExit;
  } else {
    const floorK = THREE.MathUtils.clamp(
      (pad.vel.length() - SERVE_TUNE.exitFloorFrom) /
      (SERVE_TUNE.exitFloorTo - SERVE_TUNE.exitFloorFrom), 0, 1);
    exitFloor = DIMS.minExitSpeed * floorK;
  }
  if (vn < exitFloor) ball.vel.addScaledVector(tmpN, exitFloor - vn);

  // r113 · DIRECCIÓN AL OBJETIVO (petición del dueño: «cuesta apuntar hacia
  // donde apunto»): la salida reflejaba sobre la NORMAL de la cara — con la
  // hoja un poco girada la bola se iba a donde apuntaba LA MADERA, no el
  // brazo. En un golpe real la dirección la manda el SWING: giramos la
  // componente horizontal de la salida hacia la dirección del movimiento de
  // la pala (proporcional a la energía del swing y SOLO en swings vivos —
  // los toques suaves no se tocan). Jugador only (la IA ya apunta con su
  // solver), nunca en vuelo de saque (el solver valida esa trayectoria) y
  // sólo en intercambio (misma puerta honesta del súper efecto, r55).
  if (pad.who === 'player' && !pad.serveFlight &&
      pad.intercambio !== false && FIS) {
    const swing = pad.vel.length();
    if (swing > 2.5) {
      // mezcla hasta 45°: k = 0..0.45 según la energía por encima del umbral
      const kAim = 0.45 * Math.min(1, (swing - 2.5) / 6);
      tmpAim.copy(pad.vel); tmpAim.y = 0;
      if (tmpAim.lengthSq() > 1e-6) {
        tmpAim.normalize();
        tmpAim2.set(ball.vel.x, 0, ball.vel.z);
        const spH = tmpAim2.length();
        if (spH > 1e-4) {
          tmpAim2.divideScalar(spH).lerp(tmpAim, kAim).normalize();
          // guardia: el giro JAMÁS invierte el sentido de cruce (la salida
          // hacia el lado rival se conserva: mismo signo de z)
          if (tmpAim2.z * ball.vel.z >= 0) {
            ball.vel.x = tmpAim2.x * spH;
            ball.vel.z = tmpAim2.z * spH;
          }
        }
      }
    }
  }

  // Límite de velocidad
  const sp = ball.vel.length();
  if (sp > DIMS.maxBallSpeed) ball.vel.multiplyScalar(DIMS.maxBallSpeed / sp);

  // Efecto según el movimiento de la pala: barrer hacia arriba = lift,
  // hacia los lados = sidespin, hacia abajo = slice. Se usa la velocidad
  // de la SUPERFICIE de contacto (lineal + rotación de la muñeca).
  tmpSurf.copy(pad.omega).cross(tmpR.copy(pad.up).multiplyScalar(DIMS.bladeCenterUp))
    .multiplyScalar(DIMS.paddleWristSpin).add(pad.vel);
  tmpS.copy(tmpSurf).cross(tmpN).multiplyScalar(DIMS.spinImpulse);
  // v3.6.36 · SÚPER EFECTO: ×2 al brush GENERADO por el golpe del jugador
  // (pad.ppEfectoMul lo pone el núcleo SOLO con el poder activo) — NUNCA
  // al giro acumulado que ya traía la bola — con tope de seguridad 2×
  // spinMax. Sin poder el multiplicador es 1: física IDÉNTICA (golden).
  // v3.6.47 · EL EFECTO SOLO VIVE EN EL INTERCAMBIO (spec del dueño, r55):
  // «SOLO debe aplicar el efecto durante el intercambio de pelotas NUNCA
  // sobre el saca ni mío ni del rival» — con la pala EN VUELO DE SAQUE
  // (pad.serveFlight, mi saca) o FUERA DEL RALLY (pad.intercambio en false:
  // ventana del rival, arkanoid, punto muerto) la pala es HONESTA: sin
  // brush ×2, sin marca, sin clasificación — todo juego normal.
  const eMul = (pad.ppEfectoMul || 1) > 1 && !pad.serveFlight &&
    pad.intercambio !== false ? pad.ppEfectoMul : 1;
  const eTope = DIMS.spinMax * (eMul > 1 ? (DIMS.efectoSpinTope || 2) : 1);
  if (eMul > 1) tmpS.multiplyScalar(eMul);
  if (tmpS.length() > eTope) tmpS.setLength(eTope);

  if (FIS) {
    // v3.0.5 P1a · REVERSIÓN PARCIAL del spin entrante: la goma NO limpia el
    // efecto que llega — lo invierte parcialmente (−35 %) y el brush nuevo se
    // suma. Bloquear un topspin devuelve la bola «cargada» (lucha contra el
    // efecto en lugar de borrarlo). El punto dulce atenúa el brush nuevo.
    const spinMul = (PK ? PK.spin : 1) *
                    (1 - DIMS.edgeSpinLoss * offC * offC / ctl);
    ball.spin.multiplyScalar(-0.35).addScaledVector(tmpS, spinMul);
    // v3.6.36 · tope de seguridad sobre el RESULTADO con el súper efecto
    // activo (reversión −35 % del giro entrante + brush duplicado) y
    // MARCA de la bola: Magnus y bote amplificados hasta que la IA la
    // golpee (c06 limpia la marca) o el efecto acabe.
    if (eMul > 1) {
      if (ball.spin.length() > eTope) ball.spin.setLength(eTope);
      ball.ppEfecto = true;
    }

    // v3.0.5 P1b · FRICCIÓN TANGENCIAL de la goma (impulso de contacto con
    // I de cascarón, m_eff = 2/5·m): rozar ARRASTRA la bola, no sólo le da
    // efecto. Deslizamiento de la superficie de contacto incluyendo el giro
    // de la bola (por eso el bloque del topspin «lucha»: Δω de reversión).
    tmpM.copy(ball.vel).sub(tmpSurf);                       // relativa pala↔bola
    tmpT.copy(ball.spin).cross(tmpD.copy(tmpN).multiplyScalar(-DIMS.ballRadius));
    tmpM.add(tmpT);                                         // + superficie por giro
    tmpM.addScaledVector(tmpN, -tmpM.dot(tmpN));            // parte tangencial
    const slip = tmpM.length();
    if (slip > 1e-4) {
      const gripR = DIMS.rubberGrip * (PK ? PK.spin : 1) / ctl;
      let dv = slip * 0.4 * gripR;
      const cap = DIMS.rubberMu * (1 + DIMS.paddleRestitution) * Math.abs(vRelN);
      if (dv > cap) dv = cap;
      tmpM.setLength(-dv);                                  // Δv tangencial
      ball.vel.add(tmpM);
      // Δω = −(3/2r)·(N × Δv): el mismo roce que arrastra imprime el giro
      ball.spin.addScaledVector(tmpD.copy(tmpN).cross(tmpM), -1.5 / DIMS.ballRadius);
    }
  } else {
    ball.spin.copy(tmpS);
    if (eMul > 1) ball.ppEfecto = true;   // v3.6.36: bola marcada
  }

  // v3.6.46 · CLASIFICACIÓN del SPIN (ronda 54, spec del dueño): con el
  // Súper Efecto activo, el movimiento REAL de la pala al golpear decide
  // el tipo — barrido de abajo hacia arriba = TOPSPIN (liftado), de arriba
  // hacia abajo = BACKSPIN (cortado), lateral = SIDESPIN (lado del barrido,
  // +x = derecha del jugador). Golpe SIN barrido claro (recto o por debajo
  // del umbral) no lleva tipo: bote FÍSICO PURO (el acople ×2,4 de la r51
  // quedó RETIRADO en la r57 — un bote amplificado podía salir «amable»
  // y favorecer al rival; la ventaja del bote es SÓLO la firma tipificada).
  // El tipo viaja en la bola y lo traduce el BOTE en c05/collideTable; la
  // marca la limpia la IA al devolver.
  if (eMul > 1) {
    const pvx = pad.vel.x, pvy = pad.vel.y;
    const avx = Math.abs(pvx), avy = Math.abs(pvy);
    if (Math.max(avx, avy) <= (DIMS.efectoTipoUmbral || 0.55)) {
      ball.ppEfectoTipo = '';
      ball.ppEfectoLado = 0;
    } else if (avy >= avx) {
      ball.ppEfectoTipo = pvy > 0 ? 'top' : 'back';
      ball.ppEfectoLado = 0;
    } else {
      ball.ppEfectoTipo = 'side';
      ball.ppEfectoLado = pvx > 0 ? 1 : -1;
    }
  } else {
    ball.ppEfectoTipo = '';
    ball.ppEfectoLado = 0;
  }
  // v3.6.49 · PALA HONESTA TOTAL (bug del dueño, r57: «persiste más allá
  // del tiempo indicado»): un golpe SIN poder activo (eMul = 1) MATA la
  // marca vieja que la bola pudiera arrastrar (ventana expirada, saque,
  // rebote loco). La marca nace SOLO de un golpe con la ventana viva y
  // muere con el reloj (c12/_efectoFin), con la devolución de la IA (c06)
  // y con CUALQUIER golpe honesto — jamás sobrevive a los 10 s.
  if (eMul <= 1 && ball.ppEfecto) ball.ppEfecto = false;

  // Colocar la bola sobre la cara de contacto
  const front = DIMS.ballRadius + 0.002;
  ball.pos
    .copy(padPos)
    .addScaledVector(tmpN, front)
    .addScaledVector(ipRight, lx)
    .addScaledVector(ipUp, ly);
  // r100 · un GOLPE rompe cualquier apoyo previo (el transporte r100 en
  // stepPhysics jamás persigue una bola ya golpeada)
  ball.__ppRestIdx = -1;
  ball.__ppRestT = 0;

  // v3.6.49 · SÚPER IMÁN — GUÍA DE TIRO EN EL GOLPE (spec literal r57):
  // la trayectoria real del golpe se prolonga hacia la mitad rival y se
  // CLAMPA dentro de la mesa (LA corrección de dirección del dueño);
  // computeShotVelocityReal — el solver de la casa, con arrastre real y
  // despeje de red garantizado, el mismo que usa la IA — reconstruye la
  // velocidad para BOTAR EXACTAMENTE en el objetivo (bote correcto
  // asegurado). Potencia: piso fuerte + empuje ×1,2 con tope honesto.
  // GUARDAS: sólo pala del jugador (ppImanAim la arma el núcleo SOLO con
  // la ventana viva), NUNCA en vuelo de saque (serveFlight), NUNCA fuera
  // del rally (intercambio) y sólo tiros hacia la mitad rival (vel.z <
  // −0,4): el saque propio y los tiros hacia atrás son juego normal.
  // Simuladores y golden jamás lo ven (ventana apagada — patrón r56).
  if (pad.ppImanAim && pad.who === 'player' && !pad.serveFlight &&
      pad.intercambio !== false &&
      ball.vel.z < (DIMS.imanAimVzMin || -0.4)) {
    const tz0 = DIMS.tableCenterZ -
      DIMS.tableHalfLength * (DIMS.imanAimProfundidad || 0.62);
    let tx0 = ball.pos.x + ball.vel.x * ((tz0 - ball.pos.z) / ball.vel.z);
    const lim0 = DIMS.tableHalfWidth - DIMS.ballRadius - 0.05;
    tx0 = THREE.MathUtils.clamp(tx0, -lim0, lim0);   // LA corrección de dirección
    _imObjetivo.set(tx0, DIMS.tableTopY + DIMS.ballRadius, tz0);
    const sp0 = ball.vel.length();
    const vMax0 = Math.min(DIMS.maxBallSpeed * (DIMS.imanAimTopeFrac || 0.8),
      Math.max(sp0 * (DIMS.imanAimEmpuje || 1.2), DIMS.imanAimPisoVel || 9.5));
    const D0 = Math.hypot(_imObjetivo.x - ball.pos.x, _imObjetivo.z - ball.pos.z);
    const T0 = THREE.MathUtils.clamp(D0 / (vMax0 * 0.82), 0.32, 0.85);
    ball.vel.copy(computeShotVelocityReal(ball.pos, _imObjetivo, T0, vMax0, _imSpinCero));
    ball.spin.set(0, 0, 0);              // misil guiado: cero Magnus (bote seguro)
    ball.ppEfecto = false;               // el imán manda la trayectoria: bola limpia
    ball.ppEfectoTipo = '';
    ball.ppEfectoLado = 0;
    imanAimUsado = true;
  }

  // v3.1.1-FEEL1 · el evento (audio, háptica, árbitro, contadores) sólo
  // existe si el impacto es de verdad: los micro-contactos de REPOSO (botes
  // decrecientes sobre pala quieta) son mudos y no alimentan a nadie. En el
  // VUELO DEL SAQUE el evento SIEMPRE emite: el árbitro y la conversión del
  // lanzamiento necesitan ver TAMBIÉN los roces flojos (semántica SRV2).
  if (pad.serveFlight || Math.abs(vRelN) >= SERVE_TUNE.restEventMin) {
    pad.cooldown = DIMS.paddleHitCooldown;
    events.push({ type: 'paddle', who: pad.who, speed: Math.abs(vRelN), pos: ball.pos.clone(), paddleIndex: pad.index, imanAim: imanAimUsado });
  }
  return true;
}

/* ================================================================
 * r102 · §6 DEL ESTUDIO · APOYO PERSISTENTE EN MESA (micro-solver
 * compliant). Consume SOLVER_TUNE. La bola en apoyo NO rebota por
 * impulso: contacto continuo muelle-amortiguador en la vertical
 * (F = k·δ + c·δ̇, F ≥ 0, gravitación incluida UNA vez: el vuelo
 * RK4 ya aplicó la suya y aquí se compensa) y fricción de Coulomb
 * REGULARIZADA sobre el deslizamiento del cascarón con el MISMO
 * convenio de bounceOnTable (ux = vx + r·ωz, uz = vz − r·ωx, acoplo
 * Δω = (3/2r)·Δv). La bola se posa, RUEDA con su efecto real
 * (topspin acelera y rueda, backspin frena), responde al empuje en
 * continuo y sale rodando por el borde. El árbitro ve UN bote (el
 * de la entrada) — ningún evento mientras dura el apoyo.
 * Cero asignaciones; ~40 escalares por subpaso (presupuesto 20 µs).
 * ================================================================ */
function apoyoMesa(ball, h) {
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const { pos, vel, spin } = ball;
  // despegues: voló (golpe de pala), rodó fuera del tablero o quedó en vuelo
  if (pos.y > topR + SOLVER_TUNE.mesaDespega ||
      Math.abs(pos.x) > DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 ||
      Math.abs(pos.z - DIMS.tableCenterZ) > DIMS.tableHalfLength) {
    ball.__ppMesa = 0;
    return;
  }
  const delta = topR - pos.y;                        // penetración (≥0 en contacto)
  if (delta < -0.012) { ball.__ppMesa = 0; return; } // teletransporte/reset: fuera
  // vertical: el RK4 ya metió la gravedad — se compensa y aquí manda el muelle
  vel.y -= DIMS.gravity * h;
  const dDot = -vel.y;                               // velocidad de compresión
  let Fn = SOLVER_TUNE.mesaK * delta;
  if (delta > 0 && dDot > 0) Fn += SOLVER_TUNE.mesaC * dDot;
  if (Fn < 0) Fn = 0;
  vel.y += (DIMS.gravity + Fn) * h;
  // tangencial: Coulomb regularizado sobre el deslizamiento del cascarón
  const r = DIMS.ballRadius;
  const ux = vel.x + r * spin.z;
  const uz = vel.z - r * spin.x;
  const uLen = Math.hypot(ux, uz);
  if (uLen > 1e-6) {
    const Ft = Math.min(SOLVER_TUNE.mesaMu * Fn, SOLVER_TUNE.mesaKT * uLen);
    const dvx = -Ft * (ux / uLen) * h;
    const dvz = -Ft * (uz / uLen) * h;
    vel.x += dvx;
    vel.z += dvz;
    const kAc = (BOTE_TUNE.cascaronAcoplo / r);
    spin.x += -kAc * dvz;
    spin.z += +kAc * dvx;
  }
  // rodadura: resistencia lineal al deslizamiento residual (se posa sin vibrar)
  const rr = Math.max(0, 1 - SOLVER_TUNE.mesaRueda * h);
  vel.x *= rr;
  vel.z *= rr;
  ball.__ppMesa += h;
}

function collideTable(ball, prevY, events) {
  // v2.98: el ASEDIO juega SIN mesa (sólo la mesita de madera del
  // módulo): la bola puede DESACTIVAR la mesa del núcleo igual que
  // hace con la red (ball.ignoreNet)
  if (ball.ignoreTable) return;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const { pos, vel, spin } = ball;
  const C = DIMS.tableCenterZ;
  const inX = Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5;
  const inZ = Math.abs(pos.z - C) <= DIMS.tableHalfLength;

  if (vel.y < 0 && prevY >= topR && pos.y < topR && inX && inZ && !ball.__ppMesa) {
    pos.y = topR;
    const impact = -vel.y;
    // v3.6.46 · con TIPO claro (top/back/side) el bote lleva la FIRMA
    // tipificada de abajo. Las bolas marcadas SIN tipo bote FÍSICO PURO:
    // v3.6.49 (r57, regla del dueño «la ventaja del bote sólo es para el
    // jugador, el perjudicado siempre es el rival») RETIRA el acople
    // ×2,4 de la r51 — un bote amplificado dependía del giro real y
    // podía salir amable (bola muerta o bote alto y cómodo) y BENEFICIAR
    // AL RIVAL. La ventaja del efecto en los botes es hoy SÓLO la firma
    // tipificada, que siempre castiga: top acelera y achica, back mata
    // el ritmo en su campo, side patada lateral a perseguir.
    // v3.6.47 · «siempre en el bote sobre la MESA DEL RIVAL» (spec r55):
    // TODO el Súper Efecto vive SOLO en la mitad del rival (z < C); un
    // bote en NUESTRA mitad (mishit, bola loca) es juego normal.
    const boteRival = pos.z < C;
    // r102 · §6 · impacto FLOJO ⇒ APOYO PERSISTENTE (micro-solver compliant):
    // el impulso rebotaría hasta el infinito (rest 0,935 → micro-bote zombi
    // que además goteaba pocks r66); el apoyo muelle-amortiguador lo POSA,
    // lo hace RODAR con su efecto real y responde al empuje en continuo.
    // El evento de bote sale igual abajo (el árbitro cuenta el contacto).
    if (impact < SOLVER_TUNE.mesaEnter) {
      ball.__ppMesa = 1e-6;
      vel.y = 0;
    } else if (DIMS.physicsRealism >= 0.5) {
      // v3.0.5-FIS1 · P2: bote físico con deslizamiento (slip-coupled)
      bounceOnTable(vel, spin, impact);
    } else {
      vel.y = impact * DIMS.tableRestitution;
      vel.x *= DIMS.tableFriction;
      vel.z *= DIMS.tableFriction;
      applyBounceSpin(vel, spin);
    }
    // v3.6.46 · SPIN TIPIFICADO — el bote traduce el giro (spec literal
    // del dueño, ronda 54):
    //   TOPSPIN  → «al botar la pelota sale muy acelerada hacia delante
    //              del bote» (y baja: bote tenso de ataque);
    //   BACKSPIN → «la pelota prácticamente se queda parada con muy poca
    //              velocidad» (bola muerta en la mesa del rival);
    //   SIDESPIN → «dependiendo del lado exagera el bote en la dirección
    //              del efecto» (patada lateral proporcional al vuelo).
    // v3.6.47 · las tres firmas SOLO en la mitad del RIVAL (boteRival).
    if (boteRival && ball.ppEfectoTipo === 'top') {
      const vz0 = vel.z;
      if (Math.abs(vz0) > 1e-3) {
        const fwd = vz0 > 0 ? 1 : -1;
        vel.z = fwd * Math.min(
          Math.abs(vz0) * (DIMS.efectoBoteTopAvance || 1.55) + 0.4,
          DIMS.maxBallSpeed);
        vel.y *= (DIMS.efectoBoteTopVy || 0.62);
      }
    } else if (boteRival && ball.ppEfectoTipo === 'back') {
      vel.z *= (DIMS.efectoBoteBackH || 0.16);
      vel.x *= (DIMS.efectoBoteBackFx || 0.35);
      vel.y *= (DIMS.efectoBoteBackVy || 0.32);
    } else if (boteRival && ball.ppEfectoTipo === 'side') {
      const lado = ball.ppEfectoLado || 1;
      const kick = THREE.MathUtils.clamp(
        Math.abs(vel.z) * (DIMS.efectoBoteSideKick || 0.42),
        0.45, DIMS.efectoBoteSideMax || 1.5);
      vel.x += lado * kick;
    }
    events.push({ type: 'table', side: pos.z > C ? 'player' : 'ai', speed: impact, pos: pos.clone() });
    return;
  }

  const botY = DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius;
  if (vel.y > 0 && prevY <= botY && pos.y > botY && inX && inZ) {
    pos.y = botY;
    vel.y = -vel.y * 0.45;
    spin.multiplyScalar(0.5);
    return;
  }

  const insideSlab =
    Math.abs(pos.x) < DIMS.tableHalfWidth + DIMS.ballRadius &&
    Math.abs(pos.z - C) < DIMS.tableHalfLength + DIMS.ballRadius &&
    pos.y > DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius &&
    pos.y < topR;
  if (insideSlab && !ball.__ppMesa) {
    // r102 §6 · una bola EN APOYO descansa a topR−δ (dentro de la banda por
    // definición): no es «dentro de la losa» — el micro-solver la gobierna.
    // r86 · P0-5 · resolución por MÍNIMA PENETRACIÓN en los TRES ejes (x, z
    // e y-arriba/y-abajo): una bola golpeada desde debajo del tablero (o
    // soltada dentro de la banda) sale por la cara más CERCANA — antes sólo
    // se resolvía x/z y la bola era expulsada DE LADO aunque el fondo estuviese
    // a un centímetro («golpear la bola por debajo de la altura de la mesa
    // falla»: la pala la mandaba arriba y la mesa la teleportaba lateral).
    // Los cantos de siempre se conservan: el eje y sólo gana cuando su
    // penetración es ESTRICTAMENTE menor que x y z.
    const penX = DIMS.tableHalfWidth + DIMS.ballRadius - Math.abs(pos.x);
    const penZ = DIMS.tableHalfLength + DIMS.ballRadius - Math.abs(pos.z - C);
    const botY = DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius;
    const penUp = topR - pos.y;            // salir por ENCIMA (queda sobre la mesa)
    const penDown = pos.y - botY;          // salir por DEBAJO (queda bajo la mesa)
    let eje = 'x';
    let penMin = penX;
    if (penZ < penMin) { penMin = penZ; eje = 'z'; }
    if (penUp < penMin) { penMin = penUp; eje = 'up'; }
    if (penDown < penMin) { penMin = penDown; eje = 'down'; }
    if (eje === 'x') {
      pos.x += Math.sign(pos.x) * penX;
      vel.x *= -0.45;
    } else if (eje === 'z') {
      pos.z = C + Math.sign(pos.z - C) * (DIMS.tableHalfLength + DIMS.ballRadius);
      vel.z *= -0.45;
    } else if (eje === 'up') {
      pos.y = topR;                        // emerge SOBRE la mesa y ahí cae/bota
      vel.y = -Math.abs(vel.y) * 0.45;
    } else {
      pos.y = botY;                        // devuelve POR DEBAJO (la mesa bloquea)
      vel.y = -Math.abs(vel.y) * 0.45;
    }
    spin.multiplyScalar(0.6);
    // Regla ITTF: tocar el canto cuenta como bote válido
    // r62: el evento lleva edge:true — el sonido del CANTO es el «ping»
    // metálico con cola (muestra física propia en c03.tableEdge)
    events.push({ type: 'table', edge: true, side: pos.z > C ? 'player' : 'ai', speed: 1.5, pos: pos.clone() });
  }
}

function collideNet(ball, prevZ, events) {
  const { pos, vel, spin } = ball;
  const nz = DIMS.tableCenterZ;
  const from = prevZ - nz;
  const to = pos.z - nz;
  if (from > 0 === to > 0) return;
  if (Math.abs(pos.x) > DIMS.netHalfWidth) return;
  if (pos.y <= DIMS.tableTopY || pos.y >= DIMS.netTopY + DIMS.ballRadius) return;

  if (pos.y < DIMS.netTopY) {
    pos.z = nz + Math.sign(from) * (DIMS.ballRadius + 0.004);
    vel.z *= -0.18;
    vel.x *= 0.55;
    vel.y *= 0.75;
    spin.multiplyScalar(0.4);
    events.push({ type: 'net', speed: Math.abs(vel.z), pos: pos.clone() });
  } else {
    vel.z *= 0.35;
    vel.y *= 0.4;
    spin.multiplyScalar(0.5);
    events.push({ type: 'net', speed: Math.abs(vel.z), pos: pos.clone() });
  }
}

function collideWorld(ball, events) {
  const { pos, vel, spin } = ball;
  const r = DIMS.ballRadius;

  if (pos.y < r && vel.y < 0) {
    const impact = -vel.y;
    pos.y = r;
    // r74 · ZONA MUERTA DEL SUELO (el «sonido de la bola con el bote
    // infinito» del dueño): una bola en reposo vuelve a tocar el suelo CADA
    // SUBPASO — la gravedad la hunde unas centésimas, la colisión la
    // devuelve y cada toque disparaba un «thud» (y un evento con su
    // pos.clone(): basura por frame). Con bola APARCADA bajo el suelo
    // (salas de campeonato) además rebotaba hacia la sala en bucle.
    // Ahora, con impacto despreciable la bola SE POSA: sin evento, sin
    // sonido, sin rebote fantasma. Un bote real (>= 0,3 m/s ≈ caída de
    // 4,6 mm — el golden de física juega con velocidades de metros/segundo)
    // suena exactamente igual que siempre.
    if (impact < 0.3) {
      vel.y = 0;
      vel.x *= 0.9;
      vel.z *= 0.9;
      spin.multiplyScalar(0.5);
    } else {
      vel.y = impact * 0.45;
      vel.x *= 0.85;
      vel.z *= 0.85;
      spin.multiplyScalar(0.35);
      events.push({ type: 'floor', speed: impact, pos: pos.clone() });
    }
  }
  // v2.101: ball.ignoreWalls — las PRUEBAS al AIRE LIBRE (asedio del oeste)
  // juegan SIN los muros invisibles de la sala (roomHalfX ±3,05 tapaba las
  // dianas de los edificios extremos: la bola rebotaba/explotaba ANTES de
  // llegar). El SUELO sigue siempre activo (la bomba estalla en la arena).
  if (!ball.ignoreWalls) {
    if (pos.y > DIMS.roomHeight - r && vel.y > 0) {
      pos.y = DIMS.roomHeight - r;
      vel.y *= -0.4;
      events.push({ type: 'wall', speed: Math.abs(vel.y), pos: pos.clone() });
    }
    for (const sx of [-1, 1]) {
      if (pos.x * sx > DIMS.roomHalfX - r && vel.x * sx > 0) {
        pos.x = sx * (DIMS.roomHalfX - r);
        vel.x *= -0.4;
        events.push({ type: 'wall', speed: Math.abs(vel.x), pos: pos.clone() });
      }
    }
    if (pos.z > DIMS.roomBackZ - r && vel.z > 0) {
      pos.z = DIMS.roomBackZ - r;
      vel.z *= -0.4;
      events.push({ type: 'wall', speed: Math.abs(vel.z), pos: pos.clone() });
    }
    if (pos.z < DIMS.roomFrontZ + r && vel.z < 0) {
      pos.z = DIMS.roomFrontZ + r;
      vel.z *= -0.4;
      events.push({ type: 'wall', speed: Math.abs(vel.z), pos: pos.clone() });
    }
  }

  if (
    Math.abs(pos.x) > 30 || Math.abs(pos.z) > 30 || pos.y < -5 ||
    !Number.isFinite(pos.x) || !Number.isFinite(pos.y) || !Number.isFinite(pos.z)
  ) {
    // r86 · P0-6 · el punto de rescate sale de la huella del tablero: antes
    // teleportaba a (0 · 0,5 · centro de mesa) — DEBAJO del tablero y dentro
    // de su huella — y la bola reaparecía oculta y empujada lateralmente por
    // la banda insideSlab («no funciona y desaparece la bola»). Ahora nace
    // VISIBLE detrás de la línea de fondo del jugador, a la altura del pecho.
    pos.set(0, 1.0, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.5);
    vel.set(0, 0, 0);
    // r74 · SIN evento: el rescate es un TELETRANSPORTE, no un bote — sonar
    // aquí era uno de los «thud» fantasma del bote infinito (la bola
    // aparcada a -10 m saltaba aquí y caía botando audible e invisible).
  }
}

/* ---------- v3.6.49 (ronda 57) · SÚPER IMÁN REESCRITO — GUÍA DE TIRO ----------
 *  El dueño retira el gancho y el freno («olvidemos el efecto anterior de
 *  atracción y ralentización»): el nuevo Súper Imán «asegura que nuestros
 *  ataques den SIEMPRE en la mesa del rival corrigiendo su dirección y
 *  permitiendo golpes muy fuertes y a gran velocidad; aunque la dirección
 *  sea errónea (siempre que se dirija hacia la parte de la mesa rival)
 *  acertarán sobre su mesa mediante una corrección de su trayectoria…
 *  el poder asegura un bote correcto sobre la mesa del rival (10 segundos
 *  de duración)».
 *  La mecánica ya NO es un campo por subpaso: es GUÍA DE TIRO EN EL GOLPE
 *  y vive DENTRO de collidePaddleSweep (ver el bloque r57 allí): el
 *  solver de la casa computeShotVelocityReal reconstruye la velocidad para
 *  botar EN LA MESA DEL RIVAL con despeje de red garantizado. Sin marcas
 *  por subpaso, sin gasto de cargas por asistencia — la ventana vive SUS
 *  10 s (regla del dueño) y el golden de física jamás la ve. */
const _imObjetivo = new THREE.Vector3();   // objetivo de la guía del imán
const _imSpinCero = new THREE.Vector3();   // spin nulo del misil guiado

/* r100 · TEMPORALES del transporte del apoyo (una pasada por frame: CERO
 * asignaciones en el camino caliente). */
const _rsBase = new THREE.Vector3();
const _rsN = new THREE.Vector3();
const _rsG = new THREE.Vector3();
const _rsSlip = new THREE.Vector3();
const _rsOm = new THREE.Vector3();
// r103 · §6 REAL · tmps del apoyo en el MUNDO (superficie de la pala bajo la bola)
const _rsSurf = new THREE.Vector3();
const _rsU = new THREE.Vector3();
const _rsOff = new THREE.Vector3();

export function stepPhysics(dt, ball, paddles, events, extra) {
  /* ================================================================
   * r100 · TRANSPORTE DEL APOYO (bloque complementario del contacto de
   * reposo en collidePaddleSweep). La bola apoyada en la pala del jugador
   * VIAJA con ella mientras el gesto sea suave: posición re-proyectada a la
   * cara con la pose del frame nuevo (punto local conservado), gravedad
   * tangencial con fricción estática (pala plana = bola quieta; pala
   * inclinada = la bola rueda cuesta abajo) y rodadura del cascarón. Al
   * acelerar la pala (swing, > paddleRestCarry) el apoyo se SUELTA y el
   * barrido CCD del subpaso decide el golpe natural — nunca atraviesa.
   * Despegues: pala rápida, bola deslizada fuera del disco, edad sin
   * re-confirmar > paddleRestDrop o pala ausente (auto-limpieza).        */
  if (ball.__ppRestIdx >= 0) {
    let rp = null;
    for (const p of paddles) if (p && p.index === ball.__ppRestIdx) { rp = p; break; }
    ball.__ppRestT = (ball.__ppRestT || 0) + dt;
    if (!rp || !rp.active || rp.who !== 'player' ||
        ball.__ppRestT > DIMS.paddleRestDrop) {
      ball.__ppRestIdx = -1;                       // despegue PASIVO: física normal
      ball.__ppRestPush = 0;                       // r86 P0-4: compresión fuera
    } else if (rp.vel.lengthSq() > DIMS.paddleRestCarry * DIMS.paddleRestCarry) {
      /* ==============================================================
       * r103 · GOLPE DESDE EL APOYO (bug del dueño: «con la bola parada
       * en la pala, un impulso rápido no la lanza — la atraviesa»). El
       * swing supera el carry ⇒ el contacto YA ES UN GOLPE. Antes el
       * despegue rápido soltaba la bola DONDE ESTABA: con la pose del
       * swing ya adelantada, la hoja la cruzaba sin registrar nada y el
       * barrido la veía detrás, en fuga. Ahora la bola se RE-PROYECTA
       * al frente de la cara ACTUAL (viaja pegada a ella, como venía
       * haciendo el glue) y se LANZA EN LA DIRECCIÓN DEL IMPULSO:
       * velocidad de la pala (KF §7.2, sin lag) + empuje normal de la
       * cara — el mismo formato del despegue por empuje. Con evento
       * 'paddle' el árbitro CUENTA el golpe y el cooldown evita dobles. */
      _rsN.copy(rp.normal).multiplyScalar(ball.__ppRestSide || 1);
      ball.pos.copy(rp.pos).addScaledVector(rp.up, DIMS.bladeCenterUp)
        .addScaledVector(rp.right, ball.__ppRestLx || 0)
        .addScaledVector(rp.up, ball.__ppRestDy || 0)
        .addScaledVector(_rsN, DIMS.ballRadius + 0.001);
      const pushV = Math.max(0, rp.velInst.dot(_rsN));
      const exit = Math.min(
        Math.max(pushV * DIMS.paddleRestPushOut, DIMS.paddleRestPushMin),
        DIMS.minExitSpeed * 0.8);
      ball.vel.copy(rp.vel).addScaledVector(_rsN, exit);
      ball.__ppRestIdx = -1;
      ball.__ppRestPush = 0;
      rp.cooldown = DIMS.paddleHitCooldown;
      events.push({ type: 'paddle', who: rp.who, speed: ball.vel.length(),
        pos: ball.pos.clone(), paddleIndex: rp.index, imanAim: false });
    } else {
      ball.__ppMesa = 0;                           // bola en la pala: sin apoyo de mesa
      _rsN.copy(rp.normal).multiplyScalar(ball.__ppRestSide || 1);  // normal hacia la bola
      // r86 · P0-4 · EMPUJE SOSTENIDO → DESPEGUE ANALÓGICO: la pala que avanza
      // hacia la bola apoyada (velInst·normal > 0) acumula COMPRESIÓN con fuga
      // exponencial (un temblor se disipa; un empuje sostenido llega). Al
      // superar el hueco, el apoyo se suelta con un golpe SUAVE proporcional a
      // la velocidad de empuje — el despegue deja de ser el salto binario del
      // carry y «empujar desde parada» funciona en continuo (queja del dueño).
      // El evento 'paddle' (formato idéntico al golpe de c05:419) hace que el
      // árbitro cuente el empuje como el golpe que es.
      let _restPin = true;
      {
        const pushV = Math.max(0, rp.velInst.dot(_rsN));
        ball.__ppRestPush = (ball.__ppRestPush || 0) * Math.exp(-6 * dt) + pushV * dt;
        if (ball.__ppRestPush > DIMS.paddleRestPushGap) {
          const exit = Math.min(
            Math.max(pushV * DIMS.paddleRestPushOut, DIMS.paddleRestPushMin),
            DIMS.minExitSpeed * 0.8);
          ball.__ppRestIdx = -1;
          ball.__ppRestPush = 0;
          ball.vel.copy(rp.vel).addScaledVector(_rsN, exit);
          rp.cooldown = DIMS.paddleHitCooldown;
          events.push({ type: 'paddle', who: rp.who, speed: exit,
            pos: ball.pos.clone(), paddleIndex: rp.index, imanAim: false });
          _restPin = false;                        // bola en física normal ya
        }
      }
      if (_restPin) {
      /* ============================================================
       * r103 · §6 REAL · EL APOYO VIVE EN EL MUNDO (bug del dueño:
       * «inclino la pala y la bola gira pero siempre sobre el mismo
       * sitio»). Antes el deslizamiento era un vector LOCAL de la pala
       * que sólo integraba gravedad, y el punto de apoyo (Lx, Dy) via-
       * jaba pegado a la cara — girar o inclinar la pala rotaba TODO el
       * conjunto: la bola daba vueltas sin deslizar jamás. Ahora la
       * bola tiene VELOCIDAD PROPIA (ball.vel persiste) y la cara se
       * mueve DEBAJO con su velocidad de superficie real: v_pala +
       * ω_muñeca × r_contacto. El deslizamiento es la DIFERENCIA en el
       * mundo, con fricción de Coulomb (estática si está pegada, ciné-
       * tica regularizada si resbala): inclinar desliza cuesta abajo,
       * girar la muñeca despacio ARRASTRA la bola y rápido la deja
       * REZAGADA — nunca más soldada al punto local.                */
      _rsG.set(0, DIMS.gravity, 0);
      const gn = _rsG.dot(_rsN);                   // componente normal (negativa)
      const Fn = -gn;                              // fuerza normal por unidad de masa
      _rsG.addScaledVector(_rsN, -gn);             // gravedad tangencial (cuesta abajo)
      // superficie de la pala bajo la bola: traslación + giro de muñeca
      const rCx = ball.__ppRestLx || 0, rCy = ball.__ppRestDy || 0;
      _rsOff.set(0, 0, 0).addScaledVector(rp.right, rCx).addScaledVector(rp.up, rCy);
      _rsSurf.copy(rp.vel);
      if (rp.omega && rp.omega.lengthSq() > 1e-8) {
        _rsOm.copy(rp.omega).cross(_rsOff);
        _rsSurf.add(_rsOm);
      }
      // deslizamiento MUNDO tangencial: bola − superficie de la cara
      _rsU.copy(ball.vel);
      _rsU.addScaledVector(_rsN, -_rsU.dot(_rsN));
      _rsU.sub(_rsSurf);
      _rsU.addScaledVector(_rsN, -_rsU.dot(_rsN));
      const uLen = _rsU.length();
      const gtLen = _rsG.length();
      if (uLen < 0.02 && gtLen <= DIMS.paddleRestMuS * Fn) {
        // fricción ESTÁTICA: pegada a la cara — pero el contacto es en el
        // mundo: girar la muñeca LENTO arrastra la bola con la cara (u≈0)
        ball.vel.copy(_rsSurf);
        _rsSlip.set(0, 0, 0);
      } else {
        // fricción CINÉTICA regularizada (Coulomb): se opone a u, tope μk·Fn
        // (μk 0,12 < μs 0,18 — física real: resbalar es más fácil que soltar;
        // suelo de Fn 0,5: pala vertical casi sin apoyo — la bola cae)
        const amax = DIMS.paddleRestFricK * Math.max(Fn, 0.5);
        if (uLen > 1e-9) {
          const fMag = Math.min(amax, 40 * uLen);
          ball.vel.addScaledVector(_rsU, -fMag / uLen * dt);
        }
        ball.vel.addScaledVector(_rsG, dt);        // gravedad tangencial propia
        // la cara la sigue sosteniendo en la normal: v_n = superficie_n
        ball.vel.addScaledVector(_rsN, _rsSurf.dot(_rsN) - ball.vel.dot(_rsN));
        _rsSlip.copy(_rsU);                        // slip real para la rodadura
      }
      // el punto de apoyo AVANZA con el deslizamiento relativo (mundo → local)
      const lx2 = rCx + _rsU.dot(rp.right) * dt, dy2 = rCy + _rsU.dot(rp.up) * dt;
      const rIn = DIMS.bladeRadius - DIMS.ballRadius * 0.35;
      if (lx2 * lx2 + dy2 * dy2 > rIn * rIn) {
        ball.__ppRestIdx = -1;                     // rodó fuera del borde
        ball.__ppRestPush = 0;                     // r86 P0-4: compresión fuera
      } else {
        ball.__ppRestLx = lx2; ball.__ppRestDy = dy2;
        // posición pegada a la cara con la pose del frame nuevo
        _rsBase.copy(rp.pos).addScaledVector(rp.up, DIMS.bladeCenterUp);
        ball.pos.copy(_rsBase)
          .addScaledVector(rp.right, lx2)
          .addScaledVector(rp.up, dy2)
          .addScaledVector(_rsN, DIMS.ballRadius + 0.001);
        // rodadura del cascarón (ω ideal = (N × slip)/r, aproximada suave)
        _rsOm.copy(_rsN).cross(_rsSlip).divideScalar(DIMS.ballRadius);
        ball.spin.lerp(_rsOm, 0.15);
      }
      }   // fin _restPin (r86 P0-4)
    }
  }

  const n = Math.max(1, Math.min(96, Math.ceil(dt / MAX_SUBSTEP_DT)));
  const h = dt / n;

  for (let i = 0; i < n; i++) {
    for (const p of paddles) if (p.cooldown > 0) p.cooldown -= h;

    tmpPrev.copy(ball.pos);
    const prevY = ball.pos.y;
    const prevZ = ball.pos.z;

    // r102 · §7.5 · VUELO RK4 (el estudio): gravedad + arrastre + Magnus con
    // orden 4 — MISMA ecuación que consumen el predictor de la IA y el solver
    // de saque (simulateBounceUntilTable): doctrina v3.0.5-FIS1 intacta.
    integraVuelo(ball.pos, ball.vel, ball.spin, h, ball.dragMul,
      ball.ppEfecto ? (DIMS.efectoMagnusMul || 1.5) : 1);   // v3.6.36: bola marcada
    // r102 · §6 · APOYO PERSISTENTE EN MESA: impactos flojos y rodadura con
    // el micro-solver compliant (muelle + Coulomb del cascarón). Cero coste
    // en vuelo libre (el flag __ppMesa solo vive en apoyos).
    if (ball.__ppMesa) apoyoMesa(ball, h);
    // v3.6.49 (r57): FUERA el campo por subpaso del imán — la guía de tiro
    // del Súper Imán vive ahora EN EL GOLPE (collidePaddleSweep, bloque
    // r57) y el golden de física no ve nada nuevo aquí.

    // v2.29: si la pala golpea en este subpaso, la bola se RECOLOCA sobre la
    // cara de la pala: evaluar mesa/red/suelo EN ESTE MISMO subpaso producía
    // eventos dobles (pala+canto) y rebotes fantasma. Se aplazan al siguiente.
    let padHit = false;
    for (const pad of paddles) {
      if (!pad.active) continue;
      // v3.1.1-FEEL1 · contacto de REPOSO: con la pala quieta el cooldown no
      // bloquea (si no, los botes decrecientes —vuelo < 0,24 s— caerían A
      // TRAVÉS de la hoja). El caso v2.29 (doble golpe de swing rápido) sigue
      // bloqueado: ahí la pala va rápida. En el vuelo del saque, todo igual.
      const still = !pad.serveFlight &&
        pad.vel.lengthSq() <= SERVE_TUNE.restPadSpeed * SERVE_TUNE.restPadSpeed;
      if (pad.cooldown > 0 && !still) continue;
      // v3.1.2-CCD1 · barrido SDF del subpaso: las poses de la pala se
      // interpolan EXACTAMENTE entre los extremos del subpaso (spec D:
      // subpasos alineados con P0→P1 del frame XR).
      if (collidePaddleSweep(ball, pad, i / n, (i + 1) / n, events)) {
        padHit = true;
        ball.__ppMesa = 0;   // r102 §6: la pala la lanza — el apoyo se suelta
      }
    }
    if (padHit) continue;
    // v3.1.1-FEEL1 · la gracia del saque caduca con el tiempo físico
    if (ball.__serveGrace > 0) ball.__serveGrace -= h;

    collideTable(ball, prevY, events);
    // v2.42: la variante ARKANOID juega SIN red (ball.ignoreNet) y añade sus
    // propias colisiones (ladrillos + perímetro + bote mínimo) POR SUBPASO,
    // así no hay túneles a velocidad de smash.
    if (!ball.ignoreNet) collideNet(ball, prevZ, events);
    collideWorld(ball, events);
    if (extra) extra(ball, events);
  }
}

/** v2.19 (online): test de contacto pala-bola SIN integrar la bola — cuando
 *  la bola la simula el rival (llega por red), cada lado solo comprueba si SU
 *  pala toca la bola. tmpPrev hace de posición previa para el CCD. */
export function testPaddleContact(ball, prevPos, paddles, events) {
  for (const p of paddles) if (p.cooldown > 0) p.cooldown -= 0.016;
  if (ball.__serveGrace > 0) ball.__serveGrace -= 0.016;   // v3.1.1-FEEL1
  tmpPrev.copy(prevPos);
  for (const pad of paddles) {
    if (!pad.active || pad.cooldown > 0) continue;
    // v3.1.2-CCD1: el frame completo es el intervalo barrido (pose A = prev,
    // pose B = pos de la pala): máxima fidelidad sin integrar la bola.
    collidePaddleSweep(ball, pad, 0, 1, events);
  }
}

/** Predice el MEJOR punto de golpeo de la bola en el campo de `sign`.
 *  v2.17: `bounced` (ya botó en este campo, lo da rules.validBounce) siembra
 *  el contador de botes — antes, tras el bote la simulación no encontraba
 *  candidatos futuros y devolvía null: la IA se quedaba CIEGA justo cuando
 *  debía golpear y la bola se le pasaba (los fallos "no llega").
 *  r57 · AUDITORÍA R2: el margen de bote en X está ALINEADO con collideTable
 *  (media bola de canto: |x| ≤ halfWidth + r·0,5) — la mesa real SÍ bota una
 *  bola cuyo centro sobresale hasta media bola del canto y la IA no debía
 *  darla por perdida. Mismo margen en simulateBounceUntilTable y
 *  simulateServePath: los TRES simuladores predicen con la física REAL. */
export function predictStrike(ball, sign, bounced) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const pos = ball.pos.clone();
  const vel = ball.vel.clone();
  const spin = ball.spin ? ball.spin.clone() : new THREE.Vector3();
  const h = 1 / 240;
  let t = 0;
  let myBounces = (bounced && (pos.z - C) * sign > 0) ? 1 : 0;
  let best = null;
  let bestScore = -Infinity;
  let planePoint = null;
  const planeZ = C - sign * (DIMS.tableHalfLength + 0.18);

  while (t < 2.2) {
    const prevY = pos.y;
    const prevZ = pos.z;
    // r102 · §7.5 · RK4 compartido: la IA predice con la ecuación del motor
    integraVuelo(pos, vel, spin, h);
    t += h;

    if (vel.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
      pos.y = topR;
      if (DIMS.physicsRealism >= 0.5) {
        // v3.0.5-FIS1 · P2: la IA predice con la MISMA física nueva
        bounceOnTable(vel, spin, -vel.y);
      } else {
        vel.y *= -DIMS.tableRestitution;
        vel.x *= DIMS.tableFriction;
        vel.z *= DIMS.tableFriction;
        applyBounceSpin(vel, spin);
      }
      if ((pos.z - C) * sign > 0) {
        myBounces++;
        if (myBounces >= 2) return { point: pos.clone(), t, urgent: true };
      }
    }
    if ((prevZ - C > 0) !== (pos.z - C > 0) && pos.y < DIMS.netTopY && pos.y > DIMS.tableTopY &&
        Math.abs(pos.x) <= DIMS.netHalfWidth) return best;
    if (pos.y < DIMS.ballRadius * 1.5) return best;
    if (!planePoint && (pos.z - planeZ) * sign <= 0 && t > 0.05) planePoint = pos.clone();

    if (myBounces >= 1 && (pos.z - C) * sign > 0 && Math.abs(pos.z - C) < DIMS.tableHalfLength + 0.8) {
      if (pos.y > 0.55 && pos.y < 1.5) {
        const score = 1.4 - Math.abs(pos.y - 1.02) - t * 0.25;
        if (score > bestScore) {
          bestScore = score;
          best = { point: pos.clone(), t };
        }
      }
    }
  }
  return best || (planePoint ? { point: planePoint, t: 1 } : null);
}

/** Velocidad parabólica hasta `target`, garantizando que pasa la red. */
export function computeShotVelocity(from, target, tIn, maxSpeed) {
  const T = Math.max(0.3, tIn);
  const ty = DIMS.tableTopY + DIMS.ballRadius;
  let vy = (ty - from.y) / T - 0.5 * DIMS.gravity * T;
  let vx = (target.x - from.x) / T;
  let vz = (target.z - from.z) / T;

  const nz = DIMS.tableCenterZ;
  if (vz !== 0) {
    const t0 = (nz - from.z) / vz;
    if (t0 > 0 && t0 < T) {
      let y0 = from.y + vy * t0 + 0.5 * DIMS.gravity * t0 * t0;
      let tries = 0;
      while (y0 < DIMS.netTopY + 0.07 && tries < 3) {
        const T2 = T + 0.09 * (tries + 1);
        vy = (ty - from.y) / T2 - 0.5 * DIMS.gravity * T2;
        vx = (target.x - from.x) / T2;
        vz = (target.z - from.z) / T2;
        const t02 = (nz - from.z) / vz;
        y0 = t02 > 0 ? from.y + vy * t02 + 0.5 * DIMS.gravity * t02 * t02 : DIMS.netTopY + 1;
        tries++;
      }
      if (y0 < DIMS.netTopY + 0.06) {
        vy += (DIMS.netTopY + 0.08 - y0) * 2;
      }
    }
  }

  const v = new THREE.Vector3(vx, vy, vz);
  const sp = v.length();
  if (sp > maxSpeed) v.multiplyScalar(maxSpeed / sp);
  return v;
}

/* ---------- Solver de tiro con FÍSICA REAL (v2.17) ----------
 * computeShotVelocity resuelve la parábola balística PURA (solo gravedad),
 * pero la bola real sufre arrastre cuadrático del aire y Magnus del efecto:
 * los tiros caían 15-27 cm cortos y la CPU parecía que "calculaba mal".
 * Este solver siembra la solución balística y la corrige por SIMULACIÓN con
 * las mismas ecuaciones de la física del juego hasta botar en el objetivo
 * (±4 cm) con holgura de red garantizada. Solo se ejecuta al golpear la IA
 * (unas pocas veces por segundo): ~4000 pasos de simulación por golpe. */
const _svPos = new THREE.Vector3();
const _svVel = new THREE.Vector3();
const _svSpin = new THREE.Vector3();
const _svRes = { land: null, t: 0, netY: null, crossed: false, fell: null };
function simulateBounceUntilTable(from, vel, spin, maxT, out) {
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const C = DIMS.tableCenterZ;
  const h = 1 / 240;
  const pos = _svPos.copy(from);
  const v = _svVel.copy(vel);
  const s = _svSpin.copy(spin);
  let t = 0;
  let netY = null;
  let crossed = false;
  out.land = null;
  out.fell = null;
  out.netY = null;
  out.crossed = false;
  while (t < maxT) {
    const prevY = pos.y;
    const prevZ = pos.z;
    // r102 · §7.5 · RK4 compartido: el simulador predice con la MISMA
    // ecuación de vuelo del motor (doctrina v3.0.5-FIS1, ahora también
    // en el integrador — Euler ✗, RK4 ✓).
    integraVuelo(pos, v, s, h);
    t += h;
    if (!crossed && (prevZ - C) * (pos.z - C) <= 0 && prevZ !== pos.z) {
      const f = (C - prevZ) / (pos.z - prevZ);
      netY = prevY + (pos.y - prevY) * f;
      crossed = true;
    }
    if (v.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
      out.land = pos.clone();
      out.t = t;
      out.netY = netY;
      out.crossed = crossed;
      return out;
    }
    if (pos.y < DIMS.ballRadius) {
      out.fell = pos.clone();
      out.t = t;
      out.netY = netY;
      out.crossed = crossed;
      return out;
    }
  }
  out.t = t;
  out.netY = netY;
  out.crossed = crossed;
  return out;
}

export function computeShotVelocityReal(from, target, tIn, maxSpeed, spin) {
  const T = Math.max(0.3, tIn);
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const v = new THREE.Vector3(
    (target.x - from.x) / T,
    (topR - from.y) / T - 0.5 * DIMS.gravity * T,
    (target.z - from.z) / T,
  );
  const d0 = Math.hypot(target.x - from.x, target.z - from.z) || 1e-6;
  const ux = (target.x - from.x) / d0;
  const uz = (target.z - from.z) / d0;
  const NET_OK = DIMS.netTopY + 0.085;   // margen anti-cinta holgado
  // v2.17b: se guarda el MEJOR iterado (mínimo error de bote con red
  // superada) — las correcciones pueden oscilar con el clamp de velocidad y
  // devolver el último no era fiable (tiros que morían en la red).
  let bestV = null;
  let bestErr = Infinity;
  const cand = new THREE.Vector3();
  for (let it = 0; it < 16; it++) {
    const sp0 = v.length();
    if (sp0 > maxSpeed) v.multiplyScalar(maxSpeed / sp0);
    simulateBounceUntilTable(from, v, spin, 1.7, _svRes);
    if (_svRes.netY !== null && _svRes.netY < NET_OK) {
      v.y += (NET_OK + 0.01 - _svRes.netY) * 1.8;   // más lift para pasar la red
      continue;
    }
    if (!_svRes.land) {
      if (!_svRes.crossed) {
        v.y += 0.3;                       // ni cruzó: más de todo
        v.x *= 1.06;
        v.z *= 1.06;
      } else if (_svRes.fell && (_svRes.fell.z - target.z) * uz < 0) {
        // se quedó corta al caer al suelo: la siguiente iteración decide
      } else {
        v.x *= 0.94;                      // se fue larga: frenar
        v.z *= 0.94;
      }
      continue;
    }
    const ex = _svRes.land.x - target.x;
    const ez = _svRes.land.z - target.z;
    const err = Math.hypot(ex, ez);
    if (err < bestErr) {
      bestErr = err;
      bestV = cand.copy(v);
    }
    if (err < 0.015) break;               // clavado: no hace falta seguir
    const e = ex * ux + ez * uz;          // error a lo largo (>0: se pasó)
    const l = ex * -uz + ez * ux;         // error perpendicular
    const f = THREE.MathUtils.clamp(1 - 0.85 * e / d0, 0.7, 1.5);
    v.x *= f;
    v.z *= f;
    v.x += l * uz / T;
    v.z -= l * ux / T;
  }
  const out = bestV ? bestV : v;
  // seguridad final: el tiro DEBE pasar la red; si no, loft extra y re-sim
  for (let k = 0; k < 4; k++) {
    simulateBounceUntilTable(from, out, spin, 1.7, _svRes);
    if (_svRes.netY === null || _svRes.netY >= DIMS.netTopY + 0.02) break;
    out.y += (DIMS.netTopY + 0.05 - _svRes.netY) * 1.6;
  }
  const sp1 = out.length();
  if (sp1 > maxSpeed) out.multiplyScalar(maxSpeed / sp1);
  return out;
}

/**
 * Simula un saque completo (bote propio -> red -> bote rival) con las
 * mismas constantes que la física real. Devuelve el resultado y dónde botó.
 */
export function simulateServePath(from, v0, spin, ownSign) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const pos = from.clone();
  const vel = v0.clone();
  const sp = spin.clone();
  const h = 1 / 240;
  let t = 0;
  let ownBounce = false;
  let oppBounce = false;
  let netTouch = false;
  let netY = null;   // altura al cruzar el plano de la red (margen anti-LET)

  while (t < 3.2) {
    const prevY = pos.y;
    const prevZ = pos.z;
    // r102 · §7.5 · RK4 compartido: el solver de saque predice con la
    // ecuación del motor (mismo integrador que el vuelo real)
    integraVuelo(pos, vel, sp, h);
    t += h;

    // bote en la mesa
    if (vel.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
      pos.y = topR;
      if (DIMS.physicsRealism >= 0.5) {
        // v3.0.5-FIS1 · P2: el solver de saque usa la MISMA física nueva
        bounceOnTable(vel, sp, -vel.y);
      } else {
        vel.y *= -DIMS.tableRestitution;
        vel.x *= DIMS.tableFriction;
        vel.z *= DIMS.tableFriction;
        applyBounceSpin(vel, sp);
      }
      if ((pos.z - C) * ownSign > 0) {
        if (ownBounce) return { ok: false };           // volvió a botar en el propio
        ownBounce = true;
      } else {
        oppBounce = true;
        return { ok: ownBounce && !netTouch, ownBounce, oppBounce, netTouch, t, oppZ: pos.z, oppX: pos.x, netY };
      }
    }
    // red (misma banda que la colisión real: el centro de la bola toca cuando
    // está por debajo de netTopY + ballRadius)
    if ((prevZ - C > 0) !== (pos.z - C > 0)) {
      if (Math.abs(pos.x) <= DIMS.netHalfWidth) {
        netY = netY === null ? pos.y : Math.max(netY, pos.y);
        if (pos.y < DIMS.netTopY + DIMS.ballRadius && pos.y > DIMS.tableTopY) {
          netTouch = true;
          if (pos.y < DIMS.netTopY - 0.01) return { ok: false }; // se queda en la malla
        }
      }
    }
    // suelo sin bote rival
    if (pos.y < DIMS.ballRadius) return { ok: false };
  }
  return { ok: false };
}

/** Busca (por simulación) una velocidad de saque válida: bote propio y bote
 *  rival. Fase 1: saques RÁPIDOS con bote propio profundo -> el bote rival cae
 *  en el último tercio del campo contrario (saque largo, como los reales).
 *  Fase 2: relaja la profundidad. El saque lento bota y muere en la mesa del
 *  rival: por eso se empieza por los vuelos rápidos.
 *  v3.0.6-SRV1 · `hint` (opcional, SOLO asistencia del saque humano): {x, spd}
 *  — el objetivo lateral y el tiempo de vuelo heredan la dirección y la
 *  energía del swing del jugador (asistencia con «toque», no saque enlatado).
 *  Sin hint (IA, máquina de entrenamiento) el comportamiento es el de siempre. */
export function findServeVelocity(from, ownSign, hint) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const HL = DIMS.tableHalfLength;
  // topspin hacia la red (como un saque real con efecto)
  const spin = new THREE.Vector3(-ownSign * 9, (Math.random() - 0.5) * 4, 0);
  // hint del swing: objetivo lateral del gesto + ritmo (swing rápido = saque
  // tenso; swing suave = saque cómodo). TB escala los tiempos de vuelo.
  const hx = hint
    ? THREE.MathUtils.clamp(hint.x, -0.42, 0.42)
    : (Math.random() * 2 - 1) * 0.22;
  const tb = hint
    ? THREE.MathUtils.clamp(1.7 / Math.max(1, hint.spd), 0.78, 1.45)
    : 1;

  for (let phase = 0; phase < 2; phase++) {
    const minOppDepth = phase === 0 ? HL * 0.5 : 0;
    // bote propio profundo y vuelo rápido: el arrastre aerodinámico frena la
    // bola, así que se barre un factor multiplicador de la velocidad balística
    // hasta que el bote rival cae en la mitad profunda del campo contrario
    const depths = phase === 0 ? [0.78, 0.7, 0.84] : [0.6, 0.7, 0.5, 0.8];
    const times = phase === 0 ? [0.3, 0.24, 0.36, 0.2] : [0.3, 0.4, 0.5, 0.62, 0.75];
    const mults = phase === 0 ? [1.0, 1.15, 1.3, 1.45, 1.6, 1.75] : [1.0];
    for (const depth of depths) {
      for (const T0 of times) {
        const T = T0 * tb;
        for (const m of mults) {
          const p1 = new THREE.Vector3(hx, topR, C + ownSign * depth);
          const v = computeShotVelocity(from, p1, T, 99).multiplyScalar(m);
          if (v.length() > 9.5) continue;
          const res = simulateServePath(from, v, spin, ownSign);
          // despeje real sobre la cinta: el centro debe pasar por encima de
          // netTop + radio de bola + 6 mm -> evita LETs al rozar en la física
          // real (480 Hz) lo que la simulación daba por válido
          if (res.ok && Math.abs(res.oppZ - C) >= minOppDepth &&
              (res.netY === null || res.netY >= DIMS.netTopY + DIMS.ballRadius + 0.006)) {
            return { v, spin };
          }
        }
      }
    }
  }
  // Fallback: saque alto y profundo (casi siempre válido)
  const tz = C - ownSign * (HL * 0.75);
  const v = computeShotVelocity(from, new THREE.Vector3(0, topR, tz), 1.05, 5.5);
  return { v, spin };
}

/* =====================================================================
 *  v3.1.0-SRV2 · ASISTENCIA PROGRESIVA ACOTADA DEL SAQUE (requisito del
 *  dueño, punto D) — reemplaza a la cascada 45 % → 75 % → solver, que
 *  SUSTITUÍA el golpeo real por la velocidad del solver (exactamente lo
 *  que el requisito prohíbe: «no aplicar una fuerza correctora que
 *  redirija automáticamente la bola»).
 *
 *  Contrato (UNA sola pieza compartida por el núcleo y el entrenamiento):
 *    1) Si la trayectoria REAL ya es un saque legal (bote propio + bote
 *       rival) NO se toca nada: el gesto manda al 100 %.
 *    2) Si es un LET (doble bote válido con roce de red) tampoco: la regla
 *       es «repetir saque», no corregir.
 *    3) Si no es legal, se mide el ERROR ANGULAR entre la salida real y
 *       una referencia legal con el toque del swing (findServeVelocity con
 *       hint). Error 0 → mezcla máxima (assistMax × tier.assistMul);
 *       decae LINEALMENTE hasta 0 en el margen (assistAngle ×
 *       tier.angleMul); fuera del margen o bajo assistMinSpeed NO se
 *       corrige nada. La mezcla nunca itera ni valida después: lo que
 *       queda vuela y el árbitro juzga (punto E del requisito).
 *  Devuelve telemetría {err, w, sim} para QA/ajuste (window.__ppDebug.
 *  lastServe cuando SERVE_TUNE.debug). `from` = ball.pos, muta ball.
 * ===================================================================== */
export function applyServeProgressiveAssist(ball, pad, tier) {
  const tune = SERVE_TUNE;
  const out = { err: -1, w: 0, sim: null };
  if (tune.assistMax <= 0 || tune.assistAngle <= 0) return out;
  const sim = simulateServePath(ball.pos, ball.vel, ball.spin, 1);
  out.sim = sim;
  if (sim.ok) { out.err = 0; return out; }                       // legal: sin tocar
  if (sim.ownBounce && sim.oppBounce) { out.err = 0; return out; } // LET: regla, no corrección
  const sp = ball.vel.length();
  if (sp < 1e-3) { out.err = 9; return out; }
  // referencia legal con la energía del swing (hint: dirección lateral y
  // ritmo heredados del gesto — asistencia «con toque», nunca enlatada)
  const ref = findServeVelocity(ball.pos, 1, pad ? {
    x: ball.pos.x * 0.35 + pad.vel.x * 0.22,
    spd: pad.vel.length(),
  } : null);
  const err = ball.vel.angleTo(ref.v);   // rad, 0…π
  out.err = err;
  const margin = tune.assistAngle * ((tier && tier.angleMul) || 1);
  if (err >= margin) return out;                                 // fuera del margen: NADA
  if (sp < tune.assistMinSpeed) return out;                      // roce: NADA
  const w = tune.assistMax * ((tier && tier.assistMul) || 1) * (1 - err / margin);
  out.w = w;
  ball.vel.lerp(ref.v, w);
  ball.spin.lerp(ref.spin, w * 0.5);
  return out;
}
export function __ppServeTelemetry(res, extra) {
  if (!SERVE_TUNE.debug) return;
  try {
    window.__ppDebug.lastServe = Object.assign({ t: performance.now() / 1000,
      err: res && res.err != null ? +res.err.toFixed(4) : null,
      w: res && res.w ? +res.w.toFixed(4) : 0,
      simOk: !!(res && res.sim && res.sim.ok),
      netTouch: !!(res && res.sim && res.sim.netTouch),
      ownBounce: !!(res && res.sim && res.sim.ownBounce),
      oppBounce: !!(res && res.sim && res.sim.oppBounce) }, extra || {});
  } catch (e) { /* nunca rompe */ }
}

/* =====================================================================
 *  ESTADÍSTICAS Y LOGROS · progreso persistente en localStorage
 *  Se guardan victorias, rachas, saques directos y el mejor rallye; los
 *  logros se desbloquean una sola vez (guardan su fecha) y se celebran
 *  con megafonía + confeti dentro y fuera del visor.
 * ===================================================================== */
// v2.27: los nombres/descripciones se resuelven con T() en el punto de uso
// (renderStats, celebrate) — así cambian de idioma sin tocar los datos.

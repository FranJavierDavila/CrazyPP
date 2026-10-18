function collidePaddle(ball, pad, k, events) {
  return collidePaddleSweep(ball, pad, k, k, events);
}

/* v3.1.2-CCD1 · DETECCIÓN CCD POR SDF (reemplaza al cruce de plano + disco).
 * Barrido del segmento de bola [tmpPrev → ball.pos] contra la pala barrida
 * entre las poses kA y kB del frame (pad.prev → pad.pos). kA/kB son las
 * fracciones del frame de cada extremo del SUBPASO (spec D: subpasos
 * alineados con P0→P1, no acumulador fijo). La pala se mueve y GIRA dentro
 * del subpaso y el barrido la absorbe de una vez (spec C: el inicio del
 * segmento se transforma con la pose τa y el fin con la pose τb).
 * Devuelve true si hubo golpe (respuesta clásica ya aplicada). */
function collidePaddleSweep(ball, pad, kA, kB, events) {
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
  const padN = pad.vel.dot(tmpN);
  if (padN > 0) ball.vel.addScaledVector(tmpN, padN * 0.22 * (PK ? PK.power : 1));

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

  // Límite de velocidad
  const sp = ball.vel.length();
  if (sp > DIMS.maxBallSpeed) ball.vel.multiplyScalar(DIMS.maxBallSpeed / sp);

  // Efecto según el movimiento de la pala: barrer hacia arriba = lift,
  // hacia los lados = sidespin, hacia abajo = slice. Se usa la velocidad
  // de la SUPERFICIE de contacto (lineal + rotación de la muñeca).
  tmpSurf.copy(pad.omega).cross(tmpR.copy(pad.up).multiplyScalar(DIMS.bladeCenterUp))
    .multiplyScalar(DIMS.paddleWristSpin).add(pad.vel);
  tmpS.copy(tmpSurf).cross(tmpN).multiplyScalar(DIMS.spinImpulse);
  if (tmpS.length() > DIMS.spinMax) tmpS.setLength(DIMS.spinMax);

  if (FIS) {
    // v3.0.5 P1a · REVERSIÓN PARCIAL del spin entrante: la goma NO limpia el
    // efecto que llega — lo invierte parcialmente (−35 %) y el brush nuevo se
    // suma. Bloquear un topspin devuelve la bola «cargada» (lucha contra el
    // efecto en lugar de borrarlo). El punto dulce atenúa el brush nuevo.
    const spinMul = (PK ? PK.spin : 1) *
                    (1 - DIMS.edgeSpinLoss * offC * offC / ctl);
    ball.spin.multiplyScalar(-0.35).addScaledVector(tmpS, spinMul);

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
  }

  // Colocar la bola sobre la cara de contacto
  const front = DIMS.ballRadius + 0.002;
  ball.pos
    .copy(padPos)
    .addScaledVector(tmpN, front)
    .addScaledVector(ipRight, lx)
    .addScaledVector(ipUp, ly);

  // v3.1.1-FEEL1 · el evento (audio, háptica, árbitro, contadores) sólo
  // existe si el impacto es de verdad: los micro-contactos de REPOSO (botes
  // decrecientes sobre pala quieta) son mudos y no alimentan a nadie. En el
  // VUELO DEL SAQUE el evento SIEMPRE emite: el árbitro y la conversión del
  // lanzamiento necesitan ver TAMBIÉN los roces flojos (semántica SRV2).
  if (pad.serveFlight || Math.abs(vRelN) >= SERVE_TUNE.restEventMin) {
    pad.cooldown = DIMS.paddleHitCooldown;
    events.push({ type: 'paddle', who: pad.who, speed: Math.abs(vRelN), pos: ball.pos.clone(), paddleIndex: pad.index });
  }
  return true;
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

  if (vel.y < 0 && prevY >= topR && pos.y < topR && inX && inZ) {
    pos.y = topR;
    const impact = -vel.y;
    if (DIMS.physicsRealism >= 0.5) {
      // v3.0.5-FIS1 · P2: bote físico con deslizamiento (slip-coupled)
      bounceOnTable(vel, spin, impact);
    } else {
      vel.y = impact * DIMS.tableRestitution;
      vel.x *= DIMS.tableFriction;
      vel.z *= DIMS.tableFriction;
      applyBounceSpin(vel, spin);
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
  if (insideSlab) {
    const penX = DIMS.tableHalfWidth + DIMS.ballRadius - Math.abs(pos.x);
    const penZ = DIMS.tableHalfLength + DIMS.ballRadius - Math.abs(pos.z - C);
    if (penX < penZ) {
      pos.x += Math.sign(pos.x) * penX;
      vel.x *= -0.45;
    } else {
      pos.z = C + Math.sign(pos.z - C) * (DIMS.tableHalfLength + DIMS.ballRadius);
      vel.z *= -0.45;
    }
    spin.multiplyScalar(0.6);
    // Regla ITTF: tocar el canto cuenta como bote válido
    events.push({ type: 'table', side: pos.z > C ? 'player' : 'ai', speed: 1.5, pos: pos.clone() });
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
    vel.y = impact * 0.45;
    vel.x *= 0.85;
    vel.z *= 0.85;
    spin.multiplyScalar(0.35);
    events.push({ type: 'floor', speed: impact, pos: pos.clone() });
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
    pos.set(0, 0.5, DIMS.tableCenterZ);
    vel.set(0, 0, 0);
    events.push({ type: 'floor', speed: 1, pos: pos.clone() });
  }
}

function stepPhysics(dt, ball, paddles, events, extra) {
  const n = Math.max(1, Math.min(96, Math.ceil(dt / MAX_SUBSTEP_DT)));
  const h = dt / n;

  for (let i = 0; i < n; i++) {
    for (const p of paddles) if (p.cooldown > 0) p.cooldown -= h;

    tmpPrev.copy(ball.pos);
    const prevY = ball.pos.y;
    const prevZ = ball.pos.z;

    ball.vel.y += DIMS.gravity * h;
    applyAerodynamics(ball.vel, ball.spin, h, ball.dragMul);
    ball.pos.addScaledVector(ball.vel, h);

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
      if (collidePaddleSweep(ball, pad, i / n, (i + 1) / n, events)) padHit = true;
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
function testPaddleContact(ball, prevPos, paddles, events) {
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
 *  debía golpear y la bola se le pasaba (los fallos "no llega"). */
function predictStrike(ball, sign, bounced) {
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
    vel.y += DIMS.gravity * h;
    applyAerodynamics(vel, spin, h);
    pos.addScaledVector(vel, h);
    t += h;

    if (vel.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
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
function computeShotVelocity(from, target, tIn, maxSpeed) {
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
    v.y += DIMS.gravity * h;
    applyAerodynamics(v, s, h);
    pos.addScaledVector(v, h);
    t += h;
    if (!crossed && (prevZ - C) * (pos.z - C) <= 0 && prevZ !== pos.z) {
      const f = (C - prevZ) / (pos.z - prevZ);
      netY = prevY + (pos.y - prevY) * f;
      crossed = true;
    }
    if (v.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
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

function computeShotVelocityReal(from, target, tIn, maxSpeed, spin) {
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
function simulateServePath(from, v0, spin, ownSign) {
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
    vel.y += DIMS.gravity * h;
    applyAerodynamics(vel, sp, h);
    pos.addScaledVector(vel, h);
    t += h;

    // bote en la mesa
    if (vel.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
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
function findServeVelocity(from, ownSign, hint) {
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
function applyServeProgressiveAssist(ball, pad, tier) {
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
function __ppServeTelemetry(res, extra) {
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


import * as THREE from 'three';

/* =====================================================================
 *  CONSTANTES (unidades SI · mesa reglamentaria ITTF)
 * ===================================================================== */
const DIMS = {
  tableTopY: 0.76,
  tableHalfLength: 1.37,
  tableHalfWidth: 0.7625,
  tableThickness: 0.05,
  netTopY: 0.9125,
  netHalfWidth: 0.915,
  ballRadius: 0.02,
  tableCenterZ: -1.6,
  gravity: -9.81,
  airDrag: 0.12,
  tableRestitution: 0.88,
  tableFriction: 0.94,
  paddleRestitution: 0.78,
  bladeRadius: 0.085,
  paddleHitCooldown: 0.14,
  maxBallSpeed: 12,
  // --- efecto (spin) ---
  magnus: 0.0035,        // curva en el vuelo (fuerza de Magnus)
  bounceSpinKick: 0.012, // empuje horizontal al botar (topspin "dispara")
  spinImpulse: 9,        // efecto impartido por la pala (rad/s por m/s)
  spinMax: 90,           // límite de giro
  spinDecayAir: 0.3,     // pérdida de giro por segundo en el aire
  // --- sala ---
  roomHalfX: 3.05,
  roomBackZ: 2.35,
  roomFrontZ: -5.55,
  roomHeight: 2.85,
};

const AI_PRESETS = {
  easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.20, minT: 0.62, maxT: 0.88, maxShotSpeed: 5.5, predictInterval: 0.16, smash: 0.05, short: 0.06 },
  medium: { maxSpeed: 2.9, accel: 9,  errStd: 0.05,  missBase: 0.10, minT: 0.52, maxT: 0.78, maxShotSpeed: 7.5, predictInterval: 0.10, smash: 0.18, short: 0.10 },
  hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.028, missBase: 0.04, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.12 },
};

const COLORS = {
  tableBlue: 0x17539e, tableEdge: 0x0e3a73, frame: 0x22262b,
  floor: 0x37302b, wall: 0x1a1e23,
  rubberRed: 0xc0392b, rubberBlack: 0x17181a, wood: 0xb98a5a,
  ball: 0xfff8ef, accentAmber: 0xe8b45a, accentGreen: 0x7fb069,
};

const MOUNT_QUAT = new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.22, Math.PI, 0));
const UP = new THREE.Vector3(0, 1, 0);

/* =====================================================================
 *  AUDIO · sintetizado con Web Audio (sin assets externos)
 * ===================================================================== */
class GameAudio {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;
  }
  ensure() {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') void this.ctx.resume();
      return;
    }
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return;
      this.ctx = new Ctor();
      this.master = this.ctx.createGain();
      this.master.gain.value = 0.5;
      this.master.connect(this.ctx.destination);
      const len = Math.floor(this.ctx.sampleRate * 0.25);
      this.noiseBuffer = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
      const data = this.noiseBuffer.getChannelData(0);
      for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    } catch {
      this.ctx = null;
    }
  }
  panNode(pan) {
    if (!this.ctx || !this.master) return null;
    const p = this.ctx.createStereoPanner();
    p.pan.value = Math.max(-1, Math.min(1, pan));
    p.connect(this.master);
    return p;
  }
  playOsc(freq, endFreq, dur, type, gain, pan) {
    if (!this.ctx) return;
    const dest = this.panNode(pan);
    if (!dest) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(Math.max(20, freq), t);
    osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), t + dur);
    g.gain.setValueAtTime(gain, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(g); g.connect(dest);
    osc.start(t); osc.stop(t + dur + 0.02);
  }
  playNoise(dur, filterFreq, q, gain, pan, type = 'bandpass') {
    if (!this.ctx || !this.noiseBuffer) return;
    const dest = this.panNode(pan);
    if (!dest) return;
    const t = this.ctx.currentTime;
    const src = this.ctx.createBufferSource();
    src.buffer = this.noiseBuffer;
    const filter = this.ctx.createBiquadFilter();
    filter.type = type;
    filter.frequency.value = filterFreq;
    filter.Q.value = q;
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(gain, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(filter); filter.connect(g); g.connect(dest);
    src.start(t); src.stop(t + dur + 0.02);
  }
  paddle(pan, strength) {
    const s = Math.max(0.15, Math.min(1, strength));
    this.playNoise(0.05, 1400, 1.2, 0.55 * s, pan);
    this.playOsc(190 - 40 * s, 110, 0.09, 'triangle', 0.5 * s, pan);
  }
  tableBounce(pan, strength) {
    const s = Math.max(0.1, Math.min(1, strength));
    this.playOsc(950, 700, 0.05, 'sine', 0.4 * s, pan);
    this.playNoise(0.02, 3000, 2, 0.18 * s, pan);
  }
  net(pan) {
    this.playOsc(210, 150, 0.1, 'sine', 0.35, pan);
    this.playNoise(0.06, 420, 1, 0.25, pan, 'lowpass');
  }
  thud(pan, strength) {
    const s = Math.max(0.05, Math.min(1, strength));
    this.playOsc(140, 90, 0.09, 'sine', 0.28 * s, pan);
  }
  serve() { this.playNoise(0.14, 650, 0.8, 0.16, 0); }
  point(win) {
    if (win) {
      this.playOsc(660, 660, 0.12, 'sine', 0.3, -0.3);
      window.setTimeout(() => this.playOsc(880, 880, 0.18, 'sine', 0.3, -0.3), 110);
    } else {
      this.playOsc(440, 440, 0.12, 'sine', 0.28, 0.3);
      window.setTimeout(() => this.playOsc(330, 330, 0.2, 'sine', 0.28, 0.3), 110);
    }
  }
}

/* =====================================================================
 *  FÍSICA · integración semi-implícita con sub-pasos fijos (1/240 s),
 *  efecto (spin) con fuerza de Magnus, colisión barrida pala-bola y
 *  rebotes en TODA la mesa: cara superior, cantos, parte inferior y red.
 * ===================================================================== */
const MAX_SUBSTEP_DT = 1 / 240;
const tmpPrev = new THREE.Vector3();
const padPos = new THREE.Vector3();
const relPrev = new THREE.Vector3();
const relNow = new THREE.Vector3();
const crossPoint = new THREE.Vector3();
const relVel = new THREE.Vector3();
const tmpM = new THREE.Vector3();   // Magnus
const tmpS = new THREE.Vector3();   // impulso de giro
const tmpT = new THREE.Vector3();
const tmpD = new THREE.Vector3();
const tmpV = new THREE.Vector3();
const tmpQ = new THREE.Quaternion();
const tmpTarget = new THREE.Vector3();
const tmpShoulder = new THREE.Vector3();
const tmpDir = new THREE.Vector3();

function createPaddleSim(who, index) {
  return {
    pos: new THREE.Vector3(),
    prev: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    normal: new THREE.Vector3(0, 0, 1),
    right: new THREE.Vector3(1, 0, 0),
    up: new THREE.Vector3(0, 1, 0),
    cooldown: 0,
    who,
    index,
    active: false,
  };
}

function setPaddleBasis(p, q) {
  p.normal.set(0, 0, 1).applyQuaternion(q);
  p.right.set(1, 0, 0).applyQuaternion(q);
  p.up.set(0, 1, 0).applyQuaternion(q);
}

/** Efecto del giro al botar en la mesa: topspin acelera, backspin frena, lateral desvía. */
function applyBounceSpin(vel, spin) {
  // contacto con n = (0,1,0): Δv = -K · (n × ω) → Δvx = -K·ωz ; Δvz = +K·ωx
  vel.x -= DIMS.bounceSpinKick * spin.z;
  vel.z += DIMS.bounceSpinKick * spin.x;
  spin.multiplyScalar(0.72);
}

function collidePaddle(ball, pad, k, events) {
  // Posición interpolada de la pala dentro del frame (pad.prev -> pad.pos)
  padPos.copy(pad.prev).lerp(pad.pos, k);

  // Distancia firmada de la bola (antes y ahora) al plano de la pala
  relPrev.copy(tmpPrev).sub(padPos);
  const dPrev = relPrev.dot(pad.normal);
  relNow.copy(ball.pos).sub(padPos);
  const dNow = relNow.dot(pad.normal);

  const crossing = dPrev > 0 !== dNow > 0;
  const touching = Math.abs(dNow) <= DIMS.ballRadius + 0.012;
  if (!crossing && !touching) return;

  // Punto de cruce con el plano de la pala
  if (crossing) {
    const t = Math.min(1, Math.max(0, dPrev / (dPrev - dNow)));
    crossPoint.copy(tmpPrev).lerp(ball.pos, t);
  } else {
    crossPoint.copy(ball.pos);
  }

  // Coordenadas locales del cruce en la superficie de la pala
  const lx = relNow.copy(crossPoint).sub(padPos).dot(pad.right);
  const ly = relNow.dot(pad.up);
  const reach = DIMS.bladeRadius + DIMS.ballRadius;
  const onBlade = lx * lx + ly * ly <= reach * reach;
  // también cuenta el mango (golpes con la mano-pala)
  const onHandle = Math.abs(lx) < 0.024 && ly < -(DIMS.bladeRadius - 0.03) && ly > -(DIMS.bladeRadius + 0.15);
  if (!onBlade && !onHandle) return;

  // Velocidad relativa normal: solo si la bola se acerca a la cara frontal
  const vRelN = relVel.copy(ball.vel).sub(pad.vel).dot(pad.normal);
  if (vRelN >= 0) return;

  // Reflexión con pala "infinitamente masiva" en movimiento
  ball.vel.addScaledVector(pad.normal, -(1 + DIMS.paddleRestitution) * vRelN);

  // Velocidad mínima de salida para jugabilidad
  const vn = ball.vel.dot(pad.normal);
  if (vn < 1.5) ball.vel.addScaledVector(pad.normal, 1.5 - vn);

  // Límite de velocidad
  const sp = ball.vel.length();
  if (sp > DIMS.maxBallSpeed) ball.vel.multiplyScalar(DIMS.maxBallSpeed / sp);

  // Efecto según el movimiento de la pala: barrer hacia arriba = lift (topspin),
  // hacia los lados = sidespin, hacia abajo = slice (backspin)
  tmpS.copy(pad.vel).cross(pad.normal).multiplyScalar(DIMS.spinImpulse);
  if (tmpS.length() > DIMS.spinMax) tmpS.setLength(DIMS.spinMax);
  ball.spin.copy(tmpS);

  // Colocar la bola sobre la superficie frontal de la pala
  const front = DIMS.ballRadius + 0.002;
  ball.pos
    .copy(padPos)
    .addScaledVector(pad.normal, front)
    .addScaledVector(pad.right, lx)
    .addScaledVector(pad.up, ly);

  pad.cooldown = DIMS.paddleHitCooldown;
  events.push({ type: 'paddle', who: pad.who, speed: Math.abs(vRelN), pos: ball.pos.clone(), paddleIndex: pad.index });
}

function collideTable(ball, prevY, events) {
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const { pos, vel, spin } = ball;
  const C = DIMS.tableCenterZ;
  const inX = Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5;
  const inZ = Math.abs(pos.z - C) <= DIMS.tableHalfLength;

  // Rebote en la superficie superior (toda la mesa, incluidas las líneas)
  if (vel.y < 0 && prevY >= topR && pos.y < topR && inX && inZ) {
    pos.y = topR;
    const impact = -vel.y;
    vel.y = impact * DIMS.tableRestitution;
    vel.x *= DIMS.tableFriction;
    vel.z *= DIMS.tableFriction;
    applyBounceSpin(vel, spin);
    events.push({ type: 'table', side: pos.z > C ? 'player' : 'ai', speed: impact, pos: pos.clone() });
    return;
  }

  // Golpe contra la parte inferior del tablero (bola que pasa por debajo)
  const botY = DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius;
  if (vel.y > 0 && prevY <= botY && pos.y > botY && inX && inZ) {
    pos.y = botY;
    vel.y = -vel.y * 0.45;
    spin.multiplyScalar(0.5);
    return;
  }

  // Choque lateral contra el canto de la mesa (los cuatro bordes)
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
    // Impacto directo contra la malla: la bola rebota hacia atrás
    pos.z = nz + Math.sign(from) * (DIMS.ballRadius + 0.004);
    vel.z *= -0.18;
    vel.x *= 0.55;
    vel.y *= 0.75;
    spin.multiplyScalar(0.4);
    events.push({ type: 'net', speed: Math.abs(vel.z), pos: pos.clone() });
  } else {
    // Toca el borde superior (cord): frena pero puede pasar
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

  // Red de seguridad: si la bola escapa del mundo, se considera punto
  if (
    Math.abs(pos.x) > 30 || Math.abs(pos.z) > 30 || pos.y < -5 ||
    !Number.isFinite(pos.x) || !Number.isFinite(pos.y) || !Number.isFinite(pos.z)
  ) {
    pos.set(0, 0.5, DIMS.tableCenterZ);
    vel.set(0, 0, 0);
    events.push({ type: 'floor', speed: 1, pos: pos.clone() });
  }
}

function stepPhysics(dt, ball, paddles, events) {
  const n = Math.max(1, Math.min(48, Math.ceil(dt / MAX_SUBSTEP_DT)));
  const h = dt / n;

  for (let i = 0; i < n; i++) {
    const k = (i + 0.5) / n;
    for (const p of paddles) if (p.cooldown > 0) p.cooldown -= h;

    tmpPrev.copy(ball.pos);
    const prevY = ball.pos.y;
    const prevZ = ball.pos.z;

    // Integración semi-implícita + resistencia del aire + Magnus (efecto)
    ball.vel.y += DIMS.gravity * h;
    if (ball.spin.lengthSq() > 0.5) {
      tmpM.crossVectors(ball.spin, ball.vel).multiplyScalar(DIMS.magnus * h);
      ball.vel.add(tmpM);
    }
    ball.vel.multiplyScalar(Math.max(0, 1 - DIMS.airDrag * h));
    ball.spin.multiplyScalar(Math.max(0, 1 - DIMS.spinDecayAir * h));
    ball.pos.addScaledVector(ball.vel, h);

    for (const pad of paddles) {
      if (!pad.active || pad.cooldown > 0) continue;
      collidePaddle(ball, pad, k, events);
    }

    collideTable(ball, prevY, events);
    collideNet(ball, prevZ, events);
    collideWorld(ball, events);
  }
}

/** Predice el MEJOR punto de golpeo de la bola en el campo de `sign`
 *  (+1 o -1): simula botes, red y efecto; devuelve { point, t } o null
 *  si la bola no entra (así la IA "deja pasar" las bolas fuera). */
function predictStrike(ball, sign) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const pos = ball.pos.clone();
  const vel = ball.vel.clone();
  const spin = ball.spin ? ball.spin.clone() : new THREE.Vector3();
  const h = 1 / 120;
  let t = 0;
  let myBounces = 0;
  let best = null;
  let bestScore = -Infinity;
  let planePoint = null;
  const planeZ = C - sign * (DIMS.tableHalfLength + 0.18);
  const pm = new THREE.Vector3();

  while (t < 2.2) {
    const prevY = pos.y;
    const prevZ = pos.z;
    vel.y += DIMS.gravity * h;
    if (spin.lengthSq() > 0.5) {
      pm.crossVectors(spin, vel);
      vel.addScaledVector(pm, DIMS.magnus * h);
    }
    vel.multiplyScalar(Math.max(0, 1 - DIMS.airDrag * h));
    pos.addScaledVector(vel, h);
    t += h;

    // Bote en la mesa (con efecto)
    if (vel.y < 0 && prevY >= topR && pos.y < topR &&
        Math.abs(pos.x) <= DIMS.tableHalfWidth && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
      pos.y = topR;
      vel.y *= -DIMS.tableRestitution;
      vel.x *= DIMS.tableFriction;
      vel.z *= DIMS.tableFriction;
      applyBounceSpin(vel, spin);
      if ((pos.z - C) * sign > 0) {
        myBounces++;
        if (myBounces >= 2) return { point: pos.clone(), t, urgent: true };
      }
    }
    // Se queda en la red: no llegará
    if ((prevZ - C > 0) !== (pos.z - C > 0) && pos.y < DIMS.netTopY && pos.y > DIMS.tableTopY &&
        Math.abs(pos.x) <= DIMS.netHalfWidth) return best;
    // Cae al suelo
    if (pos.y < DIMS.ballRadius * 1.5) return best;
    // Cruce del plano de seguridad (plan B si nunca bota a buena altura)
    if (!planePoint && (pos.z - planeZ) * sign <= 0 && t > 0.05) planePoint = pos.clone();

    // Punto de golpeo tras botar en su campo (descendiendo, a buena altura)
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

/** Velocidad parabólica hasta `target` (bota en la mesa), garantizando que pasa la red. */
function computeShotVelocity(from, target, tIn, maxSpeed) {
  const T = Math.max(0.3, tIn);
  const ty = DIMS.tableTopY + DIMS.ballRadius;
  let vy = (ty - from.y) / T - 0.5 * DIMS.gravity * T;
  let vx = (target.x - from.x) / T;
  let vz = (target.z - from.z) / T;

  // Verificar holgura sobre la red
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

/* =====================================================================
 *  ÁRBITRO · reglas simplificadas del tenis de mesa
 *  Partido a 11 (ventaja de 2), saque alternado cada 2 puntos.
 *  Saque fallado se repite (modo amable).
 * ===================================================================== */
class Rules {
  constructor() {
    this.state = 'serve';
    this.server = 'player';
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.message = 'Saca cuando quieras: gatillo para lanzar la bola';
    this.totalPoints = 0;
    this.stateTimer = 0;
    this.lastHitter = null;
    this.firstHitter = null;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.isServeBall = false;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  other(s) { return s === 'player' ? 'ai' : 'player'; }

  startMatch() {
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.totalPoints = 0;
    this.server = 'player';
    this.state = 'serve';
    this.stateTimer = 0;
    this.lastHitter = null;
    this.firstHitter = null;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.isServeBall = false;
    this.netTouched = false;
    this.rallyHits = 0;
    this.message = 'Saca cuando quieras: gatillo para lanzar la bola';
  }

  beginRally(who, isServe) {
    this.state = 'rally';
    this.lastHitter = who;
    this.firstHitter = who;
    this.mustBounceOpp = true;
    this.validBounce = false;
    this.isServeBall = isServe;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  registerPaddleHit(who) {
    if (this.state !== 'rally') return;
    if (this.isServeBall && who !== this.firstHitter) this.isServeBall = false;
    this.lastHitter = who;
    this.mustBounceOpp = true;
    this.validBounce = false;
    this.rallyHits++;
  }

  applyPoint(winner, cause) {
    if (winner === 'player') this.scorePlayer++;
    else this.scoreAi++;
    this.totalPoints++;
    this.state = 'point';
    this.stateTimer = 2.1;
    const rallyTxt = this.rallyHits >= 6 ? ` · ${this.rallyHits} golpes` : '';
    this.message = winner === 'player' ? `¡Punto para ti! · ${cause}${rallyTxt}` : `Punto para la CPU · ${cause}${rallyTxt}`;
    return [{ type: 'point', winner, cause }];
  }

  retryServe(cause) {
    this.state = 'serve';
    this.message = `${cause} · repite el saque`;
    return [{ type: 'retry-serve', cause }];
  }

  computeNextServer() {
    const n = this.totalPoints;
    if (this.scorePlayer >= 10 && this.scoreAi >= 10) {
      return n % 2 === 0 ? 'player' : 'ai';
    }
    return Math.floor(n / 2) % 2 === 0 ? 'player' : 'ai';
  }

  handleEvents(events) {
    const intents = [];
    for (const e of events) {
      if (this.state !== 'rally') break;

      switch (e.type) {
        case 'paddle': {
          if (e.who) this.registerPaddleHit(e.who);
          break;
        }
        case 'net': {
          this.netTouched = true;
          break;
        }
        case 'table': {
          if (!e.side || !this.lastHitter) break;
          const own = this.lastHitter;
          const opp = this.other(own);
          if (this.mustBounceOpp) {
            if (e.side === opp) {
              this.mustBounceOpp = false;
              this.validBounce = true;
              this.netTouched = false;
            } else {
              // Bota en el propio campo: falta
              if (this.isServeBall) {
                intents.push(...this.retryServe('Saque a tu campo'));
              } else {
                const cause = own === 'player' ? 'golpeaste tu propio campo' : 'la CPU golpeó su campo';
                intents.push(...this.applyPoint(opp, cause));
              }
            }
          } else if (this.validBounce) {
            if (e.side === opp) {
              // Doble bote en el campo rival: el receptor no llegó
              const cause = own === 'player' ? 'doble bote: la CPU no llegó' : 'doble bote: no llegaste';
              intents.push(...this.applyPoint(own, cause));
            } else {
              // La bola volvió por efecto al campo del que golpeó
              const cause = own === 'player' ? 'la bola volvió a tu campo' : 'la bola volvió al campo de la CPU';
              intents.push(...this.applyPoint(opp, cause));
            }
          }
          break;
        }
        case 'floor':
        case 'wall': {
          if (!this.lastHitter) break;
          if (this.mustBounceOpp) {
            // Nunca botó en el campo rival: falta del último golpeador
            if (this.isServeBall) {
              intents.push(...this.retryServe(this.netTouched ? 'Saque a la red' : 'Saque fuera'));
            } else {
              const cause = this.netTouched
                ? 'se quedó en la red'
                : e.type === 'wall' ? 'a la pared' : 'bola fuera';
              intents.push(...this.applyPoint(this.other(this.lastHitter), cause));
            }
          } else {
            // Botó correctamente y el rival no la devolvió
            const cause = this.lastHitter === 'player' ? 'la CPU no la devolvió' : 'no la devolviste';
            intents.push(...this.applyPoint(this.lastHitter, cause));
          }
          break;
        }
      }
    }
    return intents;
  }

  update(dt) {
    const intents = [];

    if (this.state === 'point') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        const finished =
          (this.scorePlayer >= 11 || this.scoreAi >= 11) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= 2;
        if (finished) {
          this.state = 'over';
          this.stateTimer = 6;
          const winner = this.scorePlayer > this.scoreAi ? 'player' : 'ai';
          this.message = winner === 'player' ? '¡Has ganado el partido!' : 'La CPU gana el partido';
          intents.push({ type: 'game-over', winner });
        } else {
          this.state = 'serve';
          this.server = this.computeNextServer();
          this.message = this.server === 'player' ? 'Tu saque: gatillo para lanzar' : 'Saque de la CPU...';
          intents.push({ type: 'serve', server: this.server });
        }
      }
    } else if (this.state === 'over') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        this.startMatch();
        this.message = 'Nuevo partido · saca con el gatillo';
        intents.push({ type: 'serve', server: this.server });
      }
    }

    return intents;
  }
}

/* =====================================================================
 *  IA · predice dónde botará la bola en SU campo, camina hasta el punto
 *  de golpeo, espera el bote (nada de voleas) y devuelve buscando el
 *  hueco lejos del rival. Puede fallar de forma natural (no llega).
 * ===================================================================== */
function gauss() {
  return (Math.random() * 2 - 1) * 0.7 + (Math.random() * 2 - 1) * 0.3;
}

class OpponentAI {
  /**
   * @param cfg    preset de dificultad
   * @param sign   -1: lado CPU (z negativa) · +1: lado del jugador demo (z positiva)
   * @param home   posición de espera de la pala
   */
  constructor(cfg, sign, home) {
    this.cfg = cfg;
    this.sign = sign;
    this.home = home.clone();
    this.pos = home.clone();
    this.vel = new THREE.Vector3();
    this.predict = new THREE.Vector3();
    this.predictValid = false;
    this.predictTimer = 0;
    this.hitCooldown = 0;
    this.errX = 0;
    this.errY = 0;
    this.bodyX = 0;
  }

  setConfig(cfg) { this.cfg = cfg; }

  reset() {
    this.pos.copy(this.home);
    this.vel.set(0, 0, 0);
    this.predictValid = false;
    this.hitCooldown = 0;
    this.bodyX = 0;
  }

  update(dt, ball, ctx) {
    this.hitCooldown -= dt;
    const C = DIMS.tableCenterZ;
    const sign = this.sign;
    // ¿La bola viaja hacia mi campo?
    const toward = ball.vel.z * sign > 0;

    if (ctx.canHit && toward) {
      this.predictTimer -= dt;
      if (this.predictTimer <= 0) {
        this.predictTimer = this.cfg.predictInterval;
        const strike = predictStrike(ball, sign);
        if (strike) {
          this.predict.copy(strike.point);
          this.errX = gauss() * this.cfg.errStd;
          this.errY = gauss() * this.cfg.errStd * 0.6;
          this.predictValid = true;
        } else {
          // bola que saldrá: no la persigue (la deja pasar)
          this.predictValid = false;
        }
      }
    } else {
      this.predictValid = false;
    }

    // --- objetivo de la pala ---
    if (this.predictValid) {
      // rango permitido: desde detrás de su línea de fondo hasta algo pasado la red
      const baseline = C + sign * DIMS.tableHalfLength;
      let inDist = (this.predict.z - baseline) * -sign;   // distancia "hacia la red"
      inDist = THREE.MathUtils.clamp(inDist, -0.45, DIMS.tableHalfLength + 0.15);
      const zClamp = baseline + inDist * -sign;
      let yClamp = THREE.MathUtils.clamp(this.predict.y + this.errY, 0.55, 1.55);
      // si el punto cae sobre la mesa, la pala no atraviesa el tablero
      const overTable =
        Math.abs(this.predict.x) < DIMS.tableHalfWidth + 0.1 &&
        Math.abs(zClamp - C) < DIMS.tableHalfLength;
      if (overTable) yClamp = Math.max(yClamp, DIMS.tableTopY + 0.08);
      tmpT.set(
        THREE.MathUtils.clamp(this.predict.x + this.errX, -(DIMS.tableHalfWidth + 0.35), DIMS.tableHalfWidth + 0.35),
        yClamp,
        zClamp,
      );
    } else {
      // posición de espera: sigue la bola de lejos
      tmpT.set(
        this.home.x + ball.pos.x * 0.3,
        this.home.y,
        this.home.z + (toward ? -sign * 0.2 : 0),
      );
    }

    // --- movimiento con aceleración (piernas) ---
    tmpD.copy(tmpT).sub(this.pos);
    const dist = tmpD.length();
    const desiredSpeed = Math.min(this.cfg.maxSpeed, dist * 4.5);
    if (dist > 1e-5) tmpD.setLength(desiredSpeed); else tmpD.set(0, 0, 0);
    this.vel.lerp(tmpD, Math.min(1, dt * this.cfg.accel));
    this.pos.addScaledVector(this.vel, dt);

    // --- intento de golpe (solo tras botar en su campo) ---
    if (!ctx.canHit || !ctx.validBounce || !toward || this.hitCooldown > 0) return null;
    const reach = 0.185;
    if (this.pos.distanceToSquared(ball.pos) > reach * reach) return null;
    if ((ball.pos.z - C) * sign < 0.04) return null;              // debe estar en su mitad
    if (ball.pos.y < DIMS.tableTopY - 0.08 || ball.pos.y > 1.65) return null;

    const ballSpeed = ball.vel.length();
    const pMiss = this.cfg.missBase + Math.max(0, ballSpeed - 7) * 0.05;
    this.hitCooldown = 0.55;
    if (Math.random() < pMiss) return null;

    // --- devolución: busca el hueco lejos del rival ---
    const away = ctx.oppPadX !== undefined
      ? -Math.sign(ctx.oppPadX || (Math.random() - 0.5))
      : (Math.random() < 0.5 ? -1 : 1);
    let tx = away * (0.16 + Math.random() * 0.38) + gauss() * this.cfg.errStd * 0.8;
    tx = THREE.MathUtils.clamp(tx, -0.55, 0.55);
    const drop = Math.random() < this.cfg.short;
    const depthRel = drop ? 0.25 + Math.random() * 0.25 : 0.55 + Math.random() * 0.65;
    const tz = C - sign * depthRel * DIMS.tableHalfLength;        // mitad contraria

    // remate si la bola viene alta
    const high = ball.pos.y > 1.15;
    const smash = high && Math.random() < this.cfg.smash;
    const T = smash ? this.cfg.minT * 0.8 : this.cfg.minT + Math.random() * (this.cfg.maxT - this.cfg.minT);
    const maxV = smash ? this.cfg.maxShotSpeed * 1.15 : this.cfg.maxShotSpeed;

    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const v = computeShotVelocity(ball.pos, tmpTarget, T, maxV);

    // efecto del golpe: lift hacia adelante + algo de lateral
    ball.spin.set(
      -sign * (8 + Math.random() * 8),
      (Math.random() - 0.5) * 8,
      0,
    );
    return v;
  }
}

/* =====================================================================
 *  ESCENA · sala, mesa reglamentaria, palas, rival con cuerpo, bola con
 *  estela, sombra proyectada, marcas de bote y marcador
 * ===================================================================== */

/** Sala: suelo, rejilla, paredes, techo, paneles de luz y anillo del jugador. */
function createRoom() {
  const g = new THREE.Group();
  const zC = (DIMS.roomBackZ + DIMS.roomFrontZ) / 2;
  const depth = DIMS.roomBackZ - DIMS.roomFrontZ;

  const floorMat = new THREE.MeshStandardMaterial({ color: COLORS.floor, roughness: 0.9, metalness: 0.05 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0, zC);
  floor.receiveShadow = true;
  g.add(floor);

  const grid = new THREE.GridHelper(Math.max(DIMS.roomHalfX * 2, depth), 20, 0x4a4038, 0x2c2622);
  grid.position.set(0, 0.002, zC);
  g.add(grid);

  const wallMat = new THREE.MeshStandardMaterial({ color: COLORS.wall, roughness: 1 });
  const mkWall = (w, h, pos, rotY) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
    m.position.copy(pos);
    m.rotation.y = rotY;
    g.add(m);
  };
  const cx = DIMS.roomHalfX;
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(-cx, DIMS.roomHeight / 2, zC), Math.PI / 2);
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(cx, DIMS.roomHeight / 2, zC), -Math.PI / 2);
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomBackZ), Math.PI);
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomFrontZ), 0);

  // Techo
  const ceil = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth),
    new THREE.MeshStandardMaterial({ color: 0x14171b, roughness: 1 }),
  );
  ceil.rotation.x = Math.PI / 2;
  ceil.position.set(0, DIMS.roomHeight, zC);
  g.add(ceil);

  // Paneles de luz emisivos en el techo
  const panelMat = new THREE.MeshBasicMaterial({ color: 0xf5efe2 });
  for (const px of [-1.4, 1.4]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.4), panelMat);
    panel.rotation.x = Math.PI / 2;
    panel.position.set(px, DIMS.roomHeight - 0.01, -1.2);
    g.add(panel);
  }

  // Franja LED ámbar a media altura para dar profundidad
  const stripMat = new THREE.MeshBasicMaterial({ color: COLORS.accentAmber });
  for (const sx of [-cx + 0.02, cx - 0.02]) {
    const strip = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, depth * 0.9), stripMat);
    strip.position.set(sx, 2.1, zC);
    g.add(strip);
  }

  // Marca circular en el suelo: punto de referencia del jugador
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.26, 0.33, 48),
    new THREE.MeshBasicMaterial({
      color: COLORS.accentAmber, transparent: true, opacity: 0.45, side: THREE.DoubleSide,
    }),
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.set(0, 0.004, 0);
  g.add(ring);

  return g;
}

/** Mesa reglamentaria con líneas blancas, estructura, patas y red. */
function createTable() {
  const g = new THREE.Group();
  const topY = DIMS.tableTopY;
  const L = DIMS.tableHalfLength * 2;
  const W = DIMS.tableHalfWidth * 2;

  const topMat = new THREE.MeshStandardMaterial({ color: COLORS.tableBlue, roughness: 0.55, metalness: 0.05 });
  const top = new THREE.Mesh(new THREE.BoxGeometry(W, DIMS.tableThickness, L), topMat);
  top.position.set(0, topY - DIMS.tableThickness / 2, DIMS.tableCenterZ);
  top.castShadow = true;
  top.receiveShadow = true;
  g.add(top);

  // Líneas blancas perimetrales (2 cm) + línea central (3 mm)
  const lineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
  const lineH = 0.002;
  const mkLine = (w, d, x, z) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, lineH, d), lineMat);
    m.position.set(x, topY + lineH / 2 - 0.0005, DIMS.tableCenterZ + z);
    g.add(m);
  };
  mkLine(W, 0.02, 0, -DIMS.tableHalfLength + 0.01);
  mkLine(W, 0.02, 0, DIMS.tableHalfLength - 0.01);
  mkLine(0.02, L, -DIMS.tableHalfWidth + 0.01, 0);
  mkLine(0.02, L, DIMS.tableHalfWidth - 0.01, 0);
  mkLine(0.003, L, 0, 0);

  // Estructura y patas
  const frameMat = new THREE.MeshStandardMaterial({ color: COLORS.frame, roughness: 0.7 });
  const apron = new THREE.Mesh(new THREE.BoxGeometry(W * 0.96, 0.1, 0.03), frameMat);
  apron.position.set(0, topY - DIMS.tableThickness - 0.06, DIMS.tableCenterZ - DIMS.tableHalfLength + 0.05);
  g.add(apron);
  const apron2 = apron.clone();
  apron2.position.z = DIMS.tableCenterZ + DIMS.tableHalfLength - 0.05;
  g.add(apron2);

  for (const lx of [-W / 2 + 0.12, W / 2 - 0.12]) {
    for (const lz of [-L / 2 + 0.15, L / 2 - 0.15]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, topY - DIMS.tableThickness, 0.06), frameMat);
      leg.position.set(lx, (topY - DIMS.tableThickness) / 2, DIMS.tableCenterZ + lz);
      leg.castShadow = true;
      g.add(leg);
    }
  }

  // Red (malla procedural con textura de canvas)
  const netCanvas = document.createElement('canvas');
  netCanvas.width = 256;
  netCanvas.height = 64;
  const nctx = netCanvas.getContext('2d');
  if (nctx) {
    nctx.clearRect(0, 0, 256, 64);
    nctx.strokeStyle = 'rgba(20,22,25,0.9)';
    nctx.lineWidth = 2;
    for (let x = 0; x <= 256; x += 10) {
      nctx.beginPath(); nctx.moveTo(x, 0); nctx.lineTo(x, 64); nctx.stroke();
    }
    for (let y = 0; y <= 64; y += 10) {
      nctx.beginPath(); nctx.moveTo(0, y); nctx.lineTo(256, y); nctx.stroke();
    }
  }
  const netTex = new THREE.CanvasTexture(netCanvas);
  netTex.wrapS = THREE.RepeatWrapping;
  netTex.wrapT = THREE.RepeatWrapping;
  netTex.repeat.set(6, 1.2);

  const netMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.netHalfWidth * 2, DIMS.netTopY - topY),
    new THREE.MeshBasicMaterial({ map: netTex, transparent: true, side: THREE.DoubleSide, alphaTest: 0.05 }),
  );
  netMesh.position.set(0, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
  g.add(netMesh);

  // Banda blanca superior de la red
  const band = new THREE.Mesh(
    new THREE.BoxGeometry(DIMS.netHalfWidth * 2, 0.014, 0.006),
    new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.5 }),
  );
  band.position.set(0, DIMS.netTopY, DIMS.tableCenterZ);
  g.add(band);

  // Postes
  const postMat = new THREE.MeshStandardMaterial({ color: 0x30343a, roughness: 0.4, metalness: 0.6 });
  for (const px of [-DIMS.netHalfWidth, DIMS.netHalfWidth]) {
    const post = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, DIMS.netTopY - topY + 0.02, 12),
      postMat,
    );
    post.position.set(px, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
    g.add(post);
  }

  return g;
}

/** Pala: cara roja al frente (+Z local), goma negra detrás, mango de madera. */
function createPaddle() {
  const g = new THREE.Group();
  const R = DIMS.bladeRadius;

  const sideMat = new THREE.MeshStandardMaterial({ color: COLORS.wood, roughness: 0.7 });
  const frontMat = new THREE.MeshStandardMaterial({ color: COLORS.rubberRed, roughness: 0.95 });
  const backMat = new THREE.MeshStandardMaterial({ color: COLORS.rubberBlack, roughness: 0.95 });

  const blade = new THREE.Mesh(
    new THREE.CylinderGeometry(R, R, 0.012, 36),
    [sideMat, frontMat, backMat],
  );
  blade.rotation.x = Math.PI / 2;
  blade.castShadow = true;
  g.add(blade);

  const handle = new THREE.Mesh(
    new THREE.BoxGeometry(0.028, 0.024, 0.11),
    new THREE.MeshStandardMaterial({ color: 0x8a6540, roughness: 0.8 }),
  );
  handle.position.set(0, -0.006, -0.068);
  handle.rotation.x = -0.16;
  handle.castShadow = true;
  g.add(handle);

  return g;
}

/** Bola con estela de puntos. */
function createBall() {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
    new THREE.MeshStandardMaterial({
      color: COLORS.ball, roughness: 0.35, emissive: 0x555044, emissiveIntensity: 0.35,
    }),
  );
  mesh.castShadow = true;

  const TRAIL_N = 22;
  const positions = new Float32Array(TRAIL_N * 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const trail = new THREE.Points(
    geo,
    new THREE.PointsMaterial({
      color: 0xffffff, size: 0.016, transparent: true, opacity: 0.35, depthWrite: false,
    }),
  );
  let idx = 0;
  const trailUpdate = () => {
    positions[idx * 3] = mesh.position.x;
    positions[idx * 3 + 1] = mesh.position.y;
    positions[idx * 3 + 2] = mesh.position.z;
    idx = (idx + 1) % TRAIL_N;
    geo.attributes.position.needsUpdate = true;
  };

  return { mesh, trail, trailUpdate };
}

/** Rival humanoide: torso, cabeza, piernas y brazo procedural que une el
 *  hombro con la pala en todo momento. */
function createOpponent(shirtColor) {
  const group = new THREE.Group();
  const shirt = new THREE.MeshStandardMaterial({ color: shirtColor, roughness: 0.75 });
  const skin = new THREE.MeshStandardMaterial({ color: 0xd9b08c, roughness: 0.6 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x1c2127, roughness: 0.8 });

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.155, 0.34, 6, 16), shirt);
  torso.position.y = 1.08;
  torso.castShadow = true;
  group.add(torso);

  const hips = new THREE.Mesh(new THREE.BoxGeometry(0.30, 0.16, 0.20), dark);
  hips.position.y = 0.84;
  group.add(hips);

  for (const sx of [-0.09, 0.09]) {
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.062, 0.52, 4, 10), dark);
    leg.position.set(sx, 0.42, 0);
    leg.castShadow = true;
    group.add(leg);
    const shoe = new THREE.Mesh(
      new THREE.BoxGeometry(0.11, 0.06, 0.20),
      new THREE.MeshStandardMaterial({ color: 0xe8e6e0, roughness: 0.6 }),
    );
    shoe.position.set(sx, 0.03, -0.03);
    group.add(shoe);
  }

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.105, 20, 16), skin);
  head.position.y = 1.52;
  head.castShadow = true;
  group.add(head);

  const hair = new THREE.Mesh(
    new THREE.SphereGeometry(0.108, 20, 12, 0, Math.PI * 2, 0, Math.PI * 0.55),
    dark,
  );
  hair.position.y = 1.528;
  group.add(hair);

  const brow = new THREE.Mesh(
    new THREE.BoxGeometry(0.13, 0.028, 0.015),
    new THREE.MeshStandardMaterial({ color: 0x10141a, roughness: 0.3, metalness: 0.3 }),
  );
  brow.position.set(0, 1.545, 0.098);
  group.add(brow);

  // Brazo derecho procedural (se orienta cada frame hacia la pala)
  const upper = new THREE.Mesh(new THREE.CapsuleGeometry(0.036, 0.28, 4, 10), skin);
  upper.castShadow = true;
  group.add(upper);
  const hand = new THREE.Mesh(new THREE.SphereGeometry(0.038, 12, 10), skin);
  group.add(hand);

  return { group, upper, hand, phase: Math.random() * 6 };
}

/** Sombra "blob" bajo la bola (ayuda muchísimo a leer la altura en VR). */
function createBlobShadow() {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(0.05, 20),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.3, depthWrite: false }),
  );
  m.rotation.x = -Math.PI / 2;
  m.renderOrder = 2;
  return m;
}

/** Marcas circulares que destellan donde bota la bola (feedback del árbitro). */
function createBounceMarkers() {
  const pool = [];
  for (let i = 0; i < 4; i++) {
    const m = new THREE.Mesh(
      new THREE.RingGeometry(0.02, 0.036, 20),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    m.rotation.x = -Math.PI / 2;
    m.userData.t = 1;
    m.visible = false;
    m.renderOrder = 3;
    pool.push(m);
  }
  return pool;
}

/** Marcador flotante con textura de canvas (visible dentro del visor). */
function createScoreboard() {
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;

  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(1.7, 0.85),
    new THREE.MeshBasicMaterial({ map: tex }),
  );
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(1.76, 0.91, 0.04),
    new THREE.MeshStandardMaterial({ color: 0x101316, roughness: 0.6 }),
  );
  frame.position.z = -0.025;
  group.add(frame);
  group.add(panel);
  group.position.set(0, 1.95, DIMS.roomFrontZ + 0.9);

  let last = '';
  const update = (d) => {
    const key = `${d.player}|${d.ai}|${d.server}|${d.message}`;
    if (key === last) return;
    last = key;

    ctx.fillStyle = '#101418';
    ctx.fillRect(0, 0, 1024, 512);
    ctx.strokeStyle = '#2a3138';
    ctx.lineWidth = 10;
    ctx.strokeRect(10, 10, 1004, 492);

    ctx.fillStyle = '#8b949c';
    ctx.font = '600 34px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('P I N G   P O N G   X R', 512, 70);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#e8b45a';
    ctx.font = '700 52px system-ui, sans-serif';
    ctx.fillText('TÚ', 150, 170);
    if (d.server === 'player') {
      ctx.beginPath();
      ctx.arc(118, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.textAlign = 'right';
    ctx.fillStyle = '#7fb069';
    ctx.font = '700 52px system-ui, sans-serif';
    ctx.fillText('CPU', 874, 170);
    if (d.server === 'ai') {
      ctx.beginPath();
      ctx.arc(906, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.textAlign = 'center';
    ctx.fillStyle = '#f2f4f6';
    ctx.font = '800 190px system-ui, sans-serif';
    ctx.fillText(`${d.player} : ${d.ai}`, 512, 340);

    ctx.fillStyle = '#c8ced4';
    ctx.font = '500 40px system-ui, sans-serif';
    const msg = d.message.length > 46 ? d.message.slice(0, 46) : d.message;
    ctx.fillText(msg, 512, 440);

    tex.needsUpdate = true;
  };

  update({ player: 0, ai: 0, server: 'player', message: '' });
  return { group, update };
}

/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, háptica y bucle principal
 * ===================================================================== */
const SERVE_OFFSET_Y = 0.11;

class PingPongGame {
  constructor(canvas, callbacks = {}) {
    this.canvas = canvas;
    this.callbacks = callbacks;
    this.disposed = false;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight, false);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;
    this.renderer.xr.enabled = true;
    this.renderer.xr.setReferenceSpaceType('local-floor');

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0b0e11);
    this.scene.fog = new THREE.Fog(0x0b0e11, 9, 18);
    this.rig = new THREE.Group();
    this.scene.add(this.rig);

    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.05, 60);
    this.camera.position.set(2.2, 1.5, 1.4);
    this.rig.add(this.camera);

    this.audio = new GameAudio();
    this.rules = new Rules();
    // la bola lleva ahora giro (spin) para el efecto
    this.ball = {
      pos: new THREE.Vector3(0, 1, DIMS.tableCenterZ + 0.4),
      vel: new THREE.Vector3(),
      spin: new THREE.Vector3(),
    };

    this.controllerPaddles = [createPaddleSim('player', 0), createPaddleSim('player', 1)];
    this.grips = null;
    this.connected = [false, false];
    this.sources = [null, null];
    this.attachHand = 0;

    // IA: lado CPU (-Z) y "jugador demo" en escritorio (+Z)
    this.ai = new OpponentAI(
      AI_PRESETS.medium, -1,
      new THREE.Vector3(0, 1.05, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45),
    );
    this.demoAI = new OpponentAI(
      AI_PRESETS.easy, 1,
      new THREE.Vector3(0, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.70),
    );

    this.difficulty = 'medium';
    this.events = [];
    this.lastTime = -1;
    this.orbitAngle = 0.7;
    this.recenterFrames = 0;
    this.aiServeTimer = 1.3;
    this.demoServeTimer = 1.2;
    // saques con lanzamiento real
    this.tossed = false;      // el jugador lanzó la bola y está en el aire
    this.tossTimer = 0;
    this.aiToss = null;       // { timer } lanzamiento visible de la CPU
    this.demoToss = null;

    this.buildScene();
    this.setupControllers();
    this.rules.startMatch();

    window.addEventListener('resize', this.onResize);
    this.renderer.xr.addEventListener('sessionstart', this.onSessionStart);
    this.renderer.xr.addEventListener('sessionend', this.onSessionEnd);
    this.renderer.setAnimationLoop(this.animate);
    // Expuesto para depuración y verificación automatizada
    window.__pingpong = this;
  }

  // ---------- Construcción ----------

  buildScene() {
    const hemi = new THREE.HemisphereLight(0xdfe8f0, 0x30271f, 0.85);
    this.rig.add(hemi);

    const dir = new THREE.DirectionalLight(0xffffff, 2.4);
    dir.position.set(2.2, 3.6, 0.6);
    dir.castShadow = true;
    dir.shadow.mapSize.set(1024, 1024);
    dir.shadow.camera.left = -3;
    dir.shadow.camera.right = 3;
    dir.shadow.camera.top = 3;
    dir.shadow.camera.bottom = -3;
    dir.shadow.camera.near = 0.5;
    dir.shadow.camera.far = 9;
    dir.shadow.bias = -0.0004;
    this.rig.add(dir);
    dir.target.position.set(0, 0.7, DIMS.tableCenterZ);
    this.rig.add(dir.target);

    this.rig.add(createRoom());
    this.rig.add(createTable());

    const { mesh, trail, trailUpdate } = createBall();
    this.ballMesh = mesh;
    this.trailUpdate = trailUpdate;
    this.ballMesh.position.copy(this.ball.pos);
    this.rig.add(mesh);
    this.rig.add(trail);

    // Sombra de la bola + marcas de bote
    this.blob = createBlobShadow();
    this.rig.add(this.blob);
    this.markers = createBounceMarkers();
    this.markerIdx = 0;
    for (const m of this.markers) this.rig.add(m);

    // Rival: pala + cuerpo con brazo
    this.aiPaddleMesh = createPaddle();
    this.rig.add(this.aiPaddleMesh);
    this.aiAvatar = createOpponent(0x2b4a7a);
    this.aiAvatar.group.position.set(0, 0, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45);
    this.aiAvatar.homeZ = this.aiAvatar.group.position.z;
    this.rig.add(this.aiAvatar.group);

    // Avatar del "jugador" para el modo demo (invisible en VR: eres tú)
    this.demoPaddleMesh = createPaddle();
    this.rig.add(this.demoPaddleMesh);
    this.demoAvatar = createOpponent(0x7a2b4a);
    this.demoAvatar.group.position.set(0, 0, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.85);
    this.demoAvatar.homeZ = this.demoAvatar.group.position.z;
    this.demoAvatar.group.rotation.y = Math.PI;
    this.demoAvatar.group.visible = false;
    this.rig.add(this.demoAvatar.group);

    const sb = createScoreboard();
    this.scoreboardUpdate = sb.update;
    this.rig.add(sb.group);
  }

  setupControllers() {
    const grips = [];
    for (let i = 0; i < 2; i++) {
      const grip = this.renderer.xr.getControllerGrip(i);
      const targetRay = this.renderer.xr.getController(i);

      const mount = new THREE.Group();
      mount.quaternion.copy(MOUNT_QUAT);
      mount.position.set(0, 0.015, -0.08);
      mount.add(createPaddle());
      grip.add(mount);

      grip.addEventListener('connected', (e) => {
        this.connected[i] = true;
        this.sources[i] = e.data;
        if (!this.connected[1 - this.attachHand] || e.data.handedness === 'right') {
          this.attachHand = i;
        }
      });
      grip.addEventListener('disconnected', () => {
        this.connected[i] = false;
        this.sources[i] = null;
      });
      const onSelect = () => this.onSelectStart(i);
      grip.addEventListener('selectstart', onSelect);
      targetRay.addEventListener('selectstart', onSelect);

      this.rig.add(grip);
      this.rig.add(targetRay);
      grips.push(grip);
    }
    this.grips = [grips[0], grips[1]];
  }

  // ---------- API pública ----------

  async enterVR() {
    this.audio.ensure();
    const xr = navigator.xr;
    if (!xr) throw new Error('Este navegador no soporta WebXR. Usa Meta Quest Browser.');
    const session = await xr.requestSession('immersive-vr', {
      optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking'],
    });
    await this.renderer.xr.setSession(session);
  }

  setDifficulty(d) {
    this.difficulty = d;
    this.ai.setConfig(AI_PRESETS[d]);
  }

  // ---------- Eventos XR ----------

  onResize = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
  };

  onSessionStart = () => {
    this.recenterFrames = 25;
    this.audio.ensure();
    this.rules.startMatch();
    this.ai.reset();
    this.demoAI.reset();
    this.tossed = false;
    this.aiToss = null;
    this.demoToss = null;
    this.aiServeTimer = 1.3;
    this.demoServeTimer = 1.4;
    this.callbacks.onXRState?.(true);
  };

  onSessionEnd = () => {
    this.rules.startMatch();
    this.tossed = false;
    this.aiToss = null;
    this.demoToss = null;
    this.demoServeTimer = 1.4;
    this.callbacks.onXRState?.(false);
  };

  onSelectStart(i) {
    if (this.disposed) return;
    this.audio.ensure();
    if (!this.renderer.xr.isPresenting) return;

    // reiniciar partido tras la derrota/victoria
    if (this.rules.state === 'over') {
      this.rules.startMatch();
      this.tossed = false;
      return;
    }
    if (this.rules.state !== 'serve' || this.rules.server !== 'player') return;
    if (this.tossed) return;
    if (!this.connected[i] || !this.controllerPaddles[i].active) return;

    this.attachHand = i;
    // SACO REAL: lanzo la bola al aire y luego debo golpearla con la pala
    const pad = this.controllerPaddles[i];
    this.tossed = true;
    this.tossTimer = 0;
    this.ball.vel.copy(pad.vel).multiplyScalar(0.25);
    this.ball.vel.y = 2.75;
    this.ball.vel.addScaledVector(pad.normal, 0.35);
    if (this.ball.vel.z > -0.1) this.ball.vel.z = -0.1;
    this.rules.message = '¡Golpea la bola!';
    this.audio.serve();
    this.haptic(i, 0.45);
  }

  haptic(index, strength) {
    const gp = this.sources[index]?.gamepad;
    const act = gp?.hapticActuators?.[0];
    try {
      act?.pulse?.(Math.min(1, Math.max(0.2, strength)), 45);
    } catch {
      /* algunos navegadores no lo soportan */
    }
  }

  // ---------- Bucle principal ----------

  animate = (time) => {
    if (this.disposed) return;
    const now = time * 0.001;
    const dt = this.lastTime < 0 ? 0.016 : Math.min(now - this.lastTime, 0.05);
    this.lastTime = now;

    const presenting = this.renderer.xr.isPresenting;

    if (presenting && this.recenterFrames > 0) {
      this.updateRecenter();
      this.recenterFrames--;
    }

    // 1) Palas de los mandos (solo en VR)
    if (presenting && this.grips) {
      for (let i = 0; i < 2; i++) {
        const ps = this.controllerPaddles[i];
        const grip = this.grips[i];
        ps.prev.copy(ps.pos);
        ps.pos.copy(grip.position);
        tmpQ.copy(grip.quaternion).multiply(MOUNT_QUAT);
        setPaddleBasis(ps, tmpQ);
        if (dt > 0) {
          tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt);
          ps.vel.lerp(tmpV, 0.55);
        }
        ps.active = this.connected[i];
      }
    }

    // 2) IA(s)
    const canHit = this.rules.state === 'rally';
    const playerPad = this.controllerPaddles[this.attachHand];
    const oppPadX = presenting
      ? (playerPad.active ? playerPad.pos.x : 0)
      : this.demoAI.pos.x;
    const aiHit = this.ai.update(dt, this.ball, {
      canHit,
      validBounce: this.rules.validBounce,
      oppPadX,
    });
    let demoHit = null;
    if (!presenting) {
      demoHit = this.demoAI.update(dt, this.ball, {
        canHit,
        validBounce: this.rules.validBounce,
        oppPadX: this.ai.pos.x,
      });
    }
    if (aiHit) {
      this.ball.vel.copy(aiHit);
      this.rules.registerPaddleHit('ai');
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, aiHit.length() / 9),
      );
    }
    if (demoHit) {
      this.ball.vel.copy(demoHit);
      this.rules.registerPaddleHit('player');
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, demoHit.length() / 9),
      );
    }

    // 3) Preparación del saque (con lanzamiento real)
    if (this.rules.state === 'serve') {
      if (this.rules.server === 'player') {
        if (presenting) {
          const pad = this.controllerPaddles[this.attachHand];
          if (!this.tossed) {
            // bola quieta sobre la pala, esperando el lanzamiento
            this.ball.vel.set(0, 0, 0);
            this.ball.spin.set(0, 0, 0);
            if (pad.active) this.ball.pos.copy(pad.pos).add(tmpV.set(0, SERVE_OFFSET_Y, 0));
          } else {
            this.tossTimer += dt;
            if (this.tossTimer > 4 || (this.ball.pos.y < 0.45 && this.ball.vel.y < 0)) {
              this.tossed = false;
              this.rules.message = 'Otra vez: gatillo para lanzar';
            }
          }
        } else if (!this.demoToss) {
          this.ball.vel.set(0, 0, 0);
          this.ball.spin.set(0, 0, 0);
          this.ball.pos.copy(this.demoAI.pos).add(tmpV.set(0, SERVE_OFFSET_Y, 0));
          this.demoServeTimer -= dt;
          if (this.demoServeTimer <= 0) {
            this.demoToss = { timer: 0.42 };
            this.ball.vel.set(0, 2.3, 0.15);
            this.audio.serve();
          }
        } else {
          this.demoToss.timer -= dt;
          if (this.demoToss.timer <= 0) {
            this.demoToss = null;
            this.serveFromAI('player');
          }
        }
      } else if (!this.aiToss) {
        // la CPU sostiene la bola y luego la lanza
        this.ball.vel.set(0, 0, 0);
        this.ball.spin.set(0, 0, 0);
        this.ball.pos.copy(this.ai.pos).add(tmpV.set(0, SERVE_OFFSET_Y, 0));
        this.aiServeTimer -= dt;
        if (this.aiServeTimer <= 0) {
          this.aiToss = { timer: 0.42 };
          this.ball.vel.set(0, 2.3, -0.15);
          this.audio.serve();
        }
      } else {
        this.aiToss.timer -= dt;
        if (this.aiToss.timer <= 0) {
          this.aiToss = null;
          this.serveFromAI('ai');
        }
      }
    }

    // 4) Física (solo las palas de los mandos colisionan físicamente)
    this.events.length = 0;
    const pads = [];
    if (presenting) {
      const holdLock = this.rules.state === 'serve' && this.rules.server === 'player' && !this.tossed;
      if (!holdLock) {
        for (const ps of this.controllerPaddles) if (ps.active) pads.push(ps);
      }
    }
    stepPhysics(dt, this.ball, pads, this.events);

    // 5) Golpe de saque del jugador: pala toca la bola lanzada -> rally
    if (presenting && this.rules.state === 'serve' && this.rules.server === 'player') {
      for (const e of this.events) {
        if (e.type === 'paddle' && e.who === 'player') {
          this.tossed = false;
          this.rules.beginRally('player', true);
          break;
        }
      }
    }

    // 6) Reglas y eventos
    const intents = this.rules.handleEvents(this.events);
    this.processIntents(intents);
    this.processIntents(this.rules.update(dt));
    this.processEvents(this.events);

    // 7) Sincronizar visuales
    this.ballMesh.position.copy(this.ball.pos);
    this.ballMesh.rotation.x += this.ball.spin.x * dt * 0.05;
    this.ballMesh.rotation.y += this.ball.spin.y * dt * 0.05;
    this.trailUpdate();
    this.updateBlobShadow();

    this.aiPaddleMesh.position.copy(this.ai.pos);
    this.aiPaddleMesh.lookAt(this.ball.pos);
    this.aiPaddleMesh.rotateX(0.18);
    this.demoPaddleMesh.position.copy(this.demoAI.pos);
    this.demoPaddleMesh.lookAt(this.ball.pos);
    this.demoPaddleMesh.rotateX(0.18);

    this.updateAvatar(this.aiAvatar, this.ai.pos, dt, now);
    this.aiAvatar.group.visible = true;
    this.demoAvatar.group.visible = !presenting;
    if (!presenting) this.updateAvatar(this.demoAvatar, this.demoAI.pos, dt, now);

    for (const m of this.markers) {
      if (!m.visible) continue;
      m.userData.t += dt * 2.4;
      if (m.userData.t >= 1) {
        m.visible = false;
        continue;
      }
      m.scale.setScalar(1 + m.userData.t * 1.6);
      m.material.opacity = 0.55 * (1 - m.userData.t);
    }

    this.scoreboardUpdate({
      player: this.rules.scorePlayer,
      ai: this.rules.scoreAi,
      server: this.rules.server,
      message: this.rules.message,
    });
    this.syncDom();

    // 8) Cámara de escritorio (órbita suave)
    if (!presenting) {
      this.orbitAngle += dt * 0.1;
      const r = 2.8;
      const cx = Math.sin(this.orbitAngle) * r;
      const cz = DIMS.tableCenterZ + Math.cos(this.orbitAngle) * r;
      this.camera.position.set(cx, 1.45 + Math.sin(this.orbitAngle * 0.6) * 0.25, cz);
      this.camera.lookAt(0, 0.95, DIMS.tableCenterZ);
    }

    // 9) Render (en XR usa la cámara del visor automáticamente)
    this.renderer.render(this.scene, this.camera);
  };

  /** Recentrado: gira el mundo para que la mesa quede frente al usuario. */
  updateRecenter() {
    const f = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);
    if (Math.abs(f.x) + Math.abs(f.z) < 1e-4) return;
    this.rig.rotation.y = Math.atan2(f.x, f.z) - Math.PI;
  }

  /** Saque de una IA: golpea la bola ya lanzada hacia la mitad del receptor. */
  serveFromAI(side) {
    const toPlayer = side === 'ai';
    const tx = (Math.random() * 2 - 1) * 0.42;
    const depth = 0.35 + Math.random() * 0.95;
    const tz = toPlayer
      ? DIMS.tableCenterZ + depth
      : DIMS.tableCenterZ - depth;
    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const v = computeShotVelocity(this.ball.pos, tmpTarget, 0.85, 6.2);
    this.ball.vel.copy(v);
    this.ball.spin.set(
      toPlayer ? 7 + Math.random() * 6 : -(7 + Math.random() * 6),
      (Math.random() - 0.5) * 5,
      0,
    );
    this.rules.beginRally(side, true);
    this.audio.serve();
  }

  /** Cuerpo del rival: pies siguen la pala (entra a la mesa en botes cortos),
   *  brazo procedural que une hombro y pala. */
  updateAvatar(av, paddlePos, dt, time) {
    const targetX = THREE.MathUtils.clamp(paddlePos.x, -0.62, 0.62);
    av.group.position.x += (targetX - av.group.position.x) * Math.min(1, dt * 5);
    // los pies se acercan a la mesa cuando el punto de golpeo es corto
    const zTarget = av.homeZ + (paddlePos.z - av.homeZ) * 0.35;
    av.group.position.z += (zTarget - av.group.position.z) * Math.min(1, dt * 4);
    av.group.position.y = Math.sin(time * 1.8 + av.phase) * 0.008;

    tmpShoulder.set(0.21, 1.30, 0.02);
    av.group.localToWorld(tmpShoulder);
    tmpDir.copy(paddlePos).sub(tmpShoulder);
    const len = THREE.MathUtils.clamp(tmpDir.length() - 0.10, 0.18, 0.55);
    if (tmpDir.lengthSq() > 1e-8) tmpDir.normalize();
    av.upper.position.copy(tmpShoulder).addScaledVector(tmpDir, len * 0.5 + 0.02);
    av.upper.quaternion.setFromUnitVectors(UP, tmpDir);
    av.upper.scale.set(1, len / 0.352, 1);
    av.hand.position.copy(paddlePos).addScaledVector(tmpDir, -0.03);
  }

  updateBlobShadow() {
    const b = this.ball.pos;
    const over =
      Math.abs(b.x) < DIMS.tableHalfWidth + 0.06 &&
      Math.abs(b.z - DIMS.tableCenterZ) < DIMS.tableHalfLength + 0.06;
    const gy = over ? DIMS.tableTopY : 0;
    this.blob.position.set(b.x, gy + 0.004, b.z);
    const hgt = Math.max(0, b.y - gy);
    this.blob.scale.setScalar(THREE.MathUtils.clamp(1.15 - hgt * 0.45, 0.25, 1.15));
    this.blob.material.opacity = THREE.MathUtils.clamp(0.34 - hgt * 0.12, 0.04, 0.34);
  }

  flashMarker(pos) {
    const m = this.markers[this.markerIdx % this.markers.length];
    this.markerIdx++;
    m.position.set(pos.x, pos.y - DIMS.ballRadius + 0.004, pos.z);
    m.userData.t = 0;
    m.visible = true;
    m.scale.setScalar(1);
    m.material.opacity = 0.55;
  }

  processIntents(intents) {
    for (const it of intents) {
      switch (it.type) {
        case 'point':
          this.audio.point(it.winner === 'player');
          if (this.renderer.xr.isPresenting) {
            this.haptic(this.attachHand, it.winner === 'player' ? 0.8 : 0.35);
          }
          break;
        case 'retry-serve':
          this.tossed = false;
          this.aiToss = null;
          this.demoToss = null;
          if (this.rules.server === 'ai') this.aiServeTimer = 1.2;
          else this.demoServeTimer = 1.2;
          break;
        case 'serve':
          this.tossed = false;
          this.aiToss = null;
          this.demoToss = null;
          if (it.server === 'ai') this.aiServeTimer = 1.3 + Math.random() * 0.6;
          else this.demoServeTimer = 1.4;
          break;
        case 'game-over':
          break;
      }
    }
  }

  processEvents(events) {
    for (const e of events) {
      const pan = THREE.MathUtils.clamp(e.pos.x / 2.5, -1, 1);
      switch (e.type) {
        case 'table':
          this.audio.tableBounce(pan, Math.min(1, e.speed / 6));
          this.flashMarker(e.pos);
          if (this.renderer.xr.isPresenting) this.haptic(this.attachHand, 0.18);
          break;
        case 'net':
          this.audio.net(pan);
          break;
        case 'floor':
          this.audio.thud(pan, Math.min(1, e.speed / 5));
          break;
        case 'wall':
          this.audio.thud(pan, Math.min(0.5, e.speed / 6));
          break;
        case 'paddle':
          this.audio.paddle(pan, Math.min(1, e.speed / 9));
          if (e.paddleIndex !== undefined && e.paddleIndex >= 0) {
            this.haptic(e.paddleIndex, Math.min(1, e.speed / 8));
          }
          break;
      }
    }
  }

  syncDom() {
    const scoreKey = `${this.rules.scorePlayer}-${this.rules.scoreAi}-${this.rules.server}`;
    if (scoreKey !== this.lastSentScore) {
      this.lastSentScore = scoreKey;
      this.callbacks.onScore?.(this.rules.scorePlayer, this.rules.scoreAi, this.rules.server);
    }
    if (this.rules.message !== this.lastSentMessage) {
      this.lastSentMessage = this.rules.message;
      this.callbacks.onMessage?.(this.rules.message);
    }
  }
}

/* =====================================================================
 *  INTERFAZ · overlay, botón VR, dificultad y HUD
 * ===================================================================== */
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const vrbtn = document.getElementById('vrbtn');
const spectateBtn = document.getElementById('spectate');
const hud = document.getElementById('hud');
const hudScore = document.getElementById('hud-score');
const hudMsg = document.getElementById('hud-msg');
const hudInfo = document.getElementById('hud-info');

const game = new PingPongGame(document.getElementById('c'), {
  onScore(player, ai) {
    hudScore.textContent = `${player} : ${ai}`;
  },
  onMessage(message) {
    hudMsg.textContent = message;
  },
  onXRState(inVR) {
    if (inVR) {
      overlay.classList.add('hidden');
      hud.classList.remove('show');
    } else {
      overlay.classList.remove('hidden');
      statusEl.textContent = 'Pausa · pulsa ENTRAR EN VR para continuar la partida.';
    }
  },
});

// Compatibilidad WebXR
if (navigator.xr && navigator.xr.isSessionSupported) {
  navigator.xr.isSessionSupported('immersive-vr')
    .then((ok) => {
      if (ok) {
        vrbtn.disabled = false;
        statusEl.textContent = '✅ Visor compatible detectado. Ponte las gafas y pulsa el botón.';
      } else {
        statusEl.textContent = '🖥️ Sin visor VR: disfruta del modo espectador (IA contra IA).';
      }
    })
    .catch(() => {
      statusEl.textContent = '🖥️ WebXR no disponible aquí: modo espectador activo.';
    });
} else {
  statusEl.textContent = '🖥️ Este navegador no soporta WebXR: modo espectador activo.';
}

vrbtn.addEventListener('click', () => {
  vrbtn.disabled = true;
  statusEl.textContent = 'Iniciando sesión VR…';
  game.enterVR()
    .then(() => {
      vrbtn.disabled = false;
    })
    .catch((err) => {
      vrbtn.disabled = false;
      statusEl.textContent = '⚠️ ' + (err?.message || 'No se pudo iniciar la sesión VR.');
    });
});

// Dificultad
document.querySelectorAll('.diff').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.diff').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    game.setDifficulty(btn.dataset.diff);
  });
});

// Modo espectador / volver a la info
spectateBtn.addEventListener('click', () => {
  overlay.classList.add('hidden');
  hud.classList.add('show');
});
hudInfo.addEventListener('click', () => {
  overlay.classList.remove('hidden');
});


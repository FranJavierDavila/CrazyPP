import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

/* =====================================================================
 *  MODELO DE PALA (GLB del usuario, incrustado en base64)
 *  Ejes del modelo: hoja hacia +Y, mango hacia -Y, cara normal ±Z.
 *  Escala 0.026 m/unidad -> hoja de 16 cm, pala completa de 26 cm.
 * ===================================================================== */
const PALA_GLB_B64 = '__PALA_GLB_B64__';

const PALA_SCALE = 0.026;
// punto de agarre (centro del mango) y centro de la hoja en coordenadas del modelo
const PALA_GRIP_Y = -2.9;
const PALA_BLADE_Y = 2.1115;

function decodeB64(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

/**
 * Corrige mallas del GLB con winding/normales invertidos (cara interna hacia
 * fuera): calcula el volumen firmado y, si es negativo, invierte el orden de
 * los triángulos y niega las normales. Así la iluminación, las sombras y los
 * contornos de la pala se ven SIEMPRE correctos, sin depender del exportador.
 */
function fixInvertedMeshes(root) {
  let fixed = 0;
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const bc = new THREE.Vector3();
  root.traverse((o) => {
    if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return;
    const geo = o.geometry;
    const pos = geo.attributes.position;
    const idx = geo.index;
    const triCount = Math.floor((idx ? idx.count : pos.count) / 3);
    if (!triCount) return;

    let vol = 0;
    for (let i = 0; i < triCount; i++) {
      const i0 = idx ? idx.getX(i * 3) : i * 3;
      const i1 = idx ? idx.getX(i * 3 + 1) : i * 3 + 1;
      const i2 = idx ? idx.getX(i * 3 + 2) : i * 3 + 2;
      a.fromBufferAttribute(pos, i0);
      b.fromBufferAttribute(pos, i1);
      c.fromBufferAttribute(pos, i2);
      vol += a.dot(bc.copy(b).cross(c)) / 6;   // volumen firmado
    }
    if (vol > -1e-10) return;                  // bien orientada o abierta: nada

    if (idx) {
      const arr = idx.array;
      for (let i = 0; i < triCount; i++) {
        const s = i * 3;
        const t = arr[s + 1];
        arr[s + 1] = arr[s + 2];
        arr[s + 2] = t;
      }
      idx.needsUpdate = true;
    } else {
      for (const name of Object.keys(geo.attributes)) {
        const attr = geo.attributes[name];
        const v = attr.array;
        const it = attr.itemSize;
        for (let i = 0; i < triCount; i++) {
          const o1 = (i * 3 + 1) * it;
          const o2 = (i * 3 + 2) * it;
          for (let k = 0; k < it; k++) {
            const t = v[o1 + k];
            v[o1 + k] = v[o2 + k];
            v[o2 + k] = t;
          }
        }
        attr.needsUpdate = true;
      }
    }
    const nor = geo.attributes.normal;
    if (nor) {
      for (let i = 0; i < nor.count; i++) {
        nor.setXYZ(i, -nor.getX(i), -nor.getY(i), -nor.getZ(i));
      }
      nor.needsUpdate = true;
    }
    fixed++;
  });
  return fixed;
}

/** Carga el GLB incrustado; devuelve el modelo o null (fallback procedural). */
function loadPaddleModel() {
  return new Promise((resolve) => {
    try {
      const loader = new GLTFLoader();
      loader.parse(decodeB64(PALA_GLB_B64), '', (gltf) => {
        const model = gltf.scene;
        const fixedMeshes = fixInvertedMeshes(model);
        if (fixedMeshes) {
          console.info(`Pala: ${fixedMeshes} malla(s) con winding/normales invertidos corregida(s)`);
        }
        model.traverse((o) => {
          if (o.isMesh) {
            o.castShadow = true;
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            for (const m of mats) {
              if (!m) continue;
              // Doble cara: evita caras invertidas del GLB; la pala se ve bien
              // por ambos lados (goma roja / madera) desde cualquier ángulo.
              m.side = THREE.DoubleSide;
              m.shadowSide = THREE.DoubleSide;
              m.needsUpdate = true;
              if (m.isMeshStandardMaterial) {
                m.metalness = Math.min(m.metalness ?? 0, 0.35);
                m.roughness = Math.max(m.roughness ?? 0.75, 0.45);
                m.envMapIntensity = 0.9;
              }
            }
          }
        });
        resolve(model);
      }, (err) => {
        console.error('No se pudo cargar el GLB de la pala:', err);
        resolve(null);
      });
    } catch (e) {
      console.error('Error decodificando el GLB:', e);
      resolve(null);
    }
  });
}

/**
 * Instancia de la pala.
 *  mode='grip'  -> el punto de agarre queda en el origen (para el mando)
 *  mode='center'-> el centro de la hoja queda en el origen (para la IA)
 */
function makePaddleVisual(model, mode) {
  const g = new THREE.Group();
  if (model) {
    const inst = model.clone(true);
    inst.scale.setScalar(PALA_SCALE);
    inst.position.y = mode === 'grip'
      ? -PALA_GRIP_Y * PALA_SCALE
      : -PALA_BLADE_Y * PALA_SCALE;
    g.add(inst);
  } else {
    // fallback: pala procedural si el GLB no cargara
    const R = 0.0795;
    const blade = new THREE.Mesh(
      new THREE.CylinderGeometry(R, R, 0.014, 32),
      [
        new THREE.MeshStandardMaterial({ color: 0xb98a5a, roughness: 0.7, side: THREE.DoubleSide }),
        new THREE.MeshStandardMaterial({ color: 0xc0392b, roughness: 0.95, side: THREE.DoubleSide }),
        new THREE.MeshStandardMaterial({ color: 0x17181a, roughness: 0.95, side: THREE.DoubleSide }),
      ],
    );
    blade.rotation.x = Math.PI / 2;
    blade.position.y = mode === 'grip' ? 0.14 : 0;
    blade.castShadow = true;
    g.add(blade);
    const handle = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.02, 0.1),
      new THREE.MeshStandardMaterial({ color: 0x8a6540, roughness: 0.8 }),
    );
    handle.position.set(0, mode === 'grip' ? 0.02 : -0.12, -0.055);
    g.add(handle);
  }
  return g;
}

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
  // AERODINÁMICA REAL (bola reglamentaria de 40 mm y 2,7 g):
  // arrastre cuadrático a = k·|v|·v  con k = ½·ρ·Cd·A/m (ρ=1.225, Cd=0.5)
  airDragK: 0.142,
  tableRestitution: 0.88,   // ITTF: rebote ~23 cm desde 30.5 cm (e ≈ 0.87)
  tableFriction: 0.94,
  paddleRestitution: 0.85,  // goma viva: los golpes salen con cuerpo
  bladeRadius: 0.0795,      // radio de la hoja (16 cm de diámetro)
  bladeCenterUp: 0.14,      // centro de la hoja sobre el punto de agarre
  hitAssistRadius: 0.05,    // margen generoso de detección alrededor de la hoja
  serveExtraReach: 0.06,    // margen EXTRA solo durante el saque (bola lanzada)
  minExitSpeed: 2.3,        // velocidad mínima de salida tras golpear (solidez)
  paddleHitCooldown: 0.08,
  maxBallSpeed: 14,
  // --- efecto (spin) ---
  magnus: 0.0035,           // a = Cm·(ω × v)
  bounceSpinKick: 0.012,
  spinImpulse: 10,
  spinMax: 110,             // ≈ 1.050 rpm
  spinDecayAir: 0.3,
  paddleWristSpin: 0.16,    // contribución de la rotación de la muñeca
  // --- saque (regla ITTF) ---
  tossMinRise: 0.14,        // lanzamiento mínimo ~16 cm (con margen)
  serveEndLineTol: 0.10,    // margen tras la línea de fondo (indulgente)
  serveAssistVy: 2.6,       // vy mínimo del saque asistido (toss más alto = más tiempo para golpear)
  // --- sala ---
  roomHalfX: 3.05,
  roomBackZ: 2.35,
  roomFrontZ: -5.55,
  roomHeight: 2.85,
};

const AI_PRESETS = {
  easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.11,  missBase: 0.22, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },
  medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.06,  missBase: 0.11, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },
  hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.028, missBase: 0.04, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },
};

const COLORS = {
  tableBlue: 0x17539e, tableEdge: 0x0e3a73, frame: 0x22262b,
  floor: 0x37302b, wall: 0x1a1e23,
  ball: 0xfff8ef, accentAmber: 0xe8b45a, accentGreen: 0x7fb069,
};

// Montura de la pala sobre el mando (espacio "grip" de WebXR):
//  · -Z_grip sale por la parte alta del mando siguiendo el mango -> la HOJA
//    continúa la línea del mango: el AGARRE DEL MANDO COINCIDE con el AGARRE
//    DE LA PALA (punto de agarre en el origen del grip, sin desplazamientos).
//  · La cara queda casi vertical (roll ≈83° desde la cara del pulgar), la
//    postura natural de preparación; espejo para la mano izquierda.
const PALA_MOUNT_ROLL = Math.PI / 2 - 0.12;
function makeMountQuat(roll) {
  const pitch = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
  const rollQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), roll);
  return new THREE.Quaternion().multiplyQuaternions(rollQ, pitch);
}
const MOUNT_QUAT_RIGHT = makeMountQuat(PALA_MOUNT_ROLL);
const MOUNT_QUAT_LEFT = makeMountQuat(-PALA_MOUNT_ROLL);
const mountQuatFor = (hand) => (hand === 'left' ? MOUNT_QUAT_LEFT : MOUNT_QUAT_RIGHT);
const UP = new THREE.Vector3(0, 1, 0);

/* =====================================================================
 *  AUDIO · sintetizado con Web Audio (sin assets externos)
 * ===================================================================== */
class GameAudio {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;
    this._wdAcc = 0;
    // El sensor de proximidad de la Quest suspende la pestaña al ajustar el
    // visor; al volver, el contexto de audio queda a veces suspendido.
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.ctx && this.ctx.state !== 'running') {
        this.ctx.resume().catch(() => {});
      }
    });
  }
  ensure() {
    if (this.ctx) {
      if (this.ctx.state !== 'running') void this.ctx.resume();
      return;
    }
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return;
      try {
        this.ctx = new Ctor({ latencyHint: 'interactive' });
      } catch {
        this.ctx = new Ctor();
      }
      this.master = this.ctx.createGain();
      this.master.gain.value = 0.9;
      // Compresor: golpes más presentes y audibles en el altavoz del visor
      const comp = this.ctx.createDynamicsCompressor();
      comp.threshold.value = -16;
      comp.knee.value = 22;
      comp.ratio.value = 5;
      comp.attack.value = 0.002;
      comp.release.value = 0.12;
      this.master.connect(comp);
      comp.connect(this.ctx.destination);
      const len = Math.floor(this.ctx.sampleRate * 0.25);
      this.noiseBuffer = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
      const data = this.noiseBuffer.getChannelData(0);
      for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    } catch {
      this.ctx = null;
    }
  }
  /** Reactiva el audio SIEMPRE antes de sonar: en Quest el contexto puede
   *  quedar suspendido al entrar/salir de la sesión inmersiva. */
  kick() {
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      this.ctx.resume().catch(() => {});
    }
  }
  /** Contexto NUEVO creado dentro de un gesto de usuario (clic ENTRAR EN VR):
   *  nace 'running' y evita arrastrar un contexto viejo suspendido/'interrupted'
   *  que ya no responde a resume() dentro de la sesión inmersiva. */
  rebuildFresh() {
    try { this.ctx?.close?.(); } catch { /* ya estaba cerrado */ }
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;
    this._wdFails = 0;
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      void this.ctx.resume().catch(() => {});
    }
  }
  /** Vigilancia periódica (llamada desde el bucle): si el contexto quedó
   *  suspendido a mitad de partida (proximidad, notificación, cambio de app),
   *  se reactiva solo. Si ni así responde (bug conocido del navegador de la
   *  Quest), se reconstruye el AudioContext desde cero: ya hubo gesto de
   *  usuario (botón ENTRAR EN VR), así que el nuevo nace activo. Sin esto,
   *  el sonido "desaparece" en VR. */
  watchdog(dt) {
    this._wdAcc += dt;
    if (this._wdAcc < 0.7) return;
    this._wdAcc = 0;
    if (!this.ctx || this.ctx.state === 'running') {
      this._wdFails = 0;
      return;
    }
    this.ctx.resume().catch(() => {});
    this._wdFails = (this._wdFails || 0) + 1;
    if (this._wdFails >= 5) {
      try { this.ctx.close(); } catch { /* ya está muerto */ }
      this.ctx = null;
      this._wdFails = 0;
      this.ensure();
      console.info('Audio: contexto reconstruido tras quedar suspendido');
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
    this.kick();
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
    this.kick();
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
  /** Pitido corto del punto muerto del saque (señal para golpear). */
  tick() { this.playOsc(1320, 1150, 0.05, 'sine', 0.22, 0); }
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
 *  efecto (spin) con fuerza de Magnus, colisión barrida pala-bola (dos
 *  caras) y rebotes en TODA la mesa: cara superior, cantos, parte
 *  inferior y red.
 * ===================================================================== */
const MAX_SUBSTEP_DT = 1 / 480;
const tmpPrev = new THREE.Vector3();
const padPos = new THREE.Vector3();
const relPrev = new THREE.Vector3();
const relNow = new THREE.Vector3();
const crossPoint = new THREE.Vector3();
const relVel = new THREE.Vector3();
const tmpN = new THREE.Vector3();
const tmpM = new THREE.Vector3();
const tmpS = new THREE.Vector3();
const tmpT = new THREE.Vector3();
const tmpD = new THREE.Vector3();
const tmpV = new THREE.Vector3();
const tmpSurf = new THREE.Vector3();
const tmpR = new THREE.Vector3();
const tmpDeltaQ = new THREE.Quaternion();
const tmpMountQ = new THREE.Quaternion();
const VEL_WINDOW = 0.07;   // ventana de suavizado de velocidad del mando (s)
const tmpTarget = new THREE.Vector3();
const tmpShoulder = new THREE.Vector3();
const tmpDir = new THREE.Vector3();

function createPaddleSim(who, index) {
  return {
    pos: new THREE.Vector3(),
    prev: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    omega: new THREE.Vector3(),
    prevQuat: new THREE.Quaternion(),
    quatInit: false,
    velBuf: [],
    prevT: -1,
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

/** Aerodinámica (arrastre + Magnus + decaimiento del giro) compartida
 *  por la física real y TODOS los simuladores: una sola ecuación. */
function applyAerodynamics(vel, spin, h) {
  const sp = vel.length();
  if (sp > 1e-6) vel.multiplyScalar(Math.max(0, 1 - DIMS.airDragK * sp * h));
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
function updatePaddleSim(ps, pos, quat, now, dt) {
  ps.prev.copy(ps.pos);
  ps.pos.copy(pos);
  setPaddleBasis(ps, quat);

  if (ps.prevT > 0 && dt > 0) {
    tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt);
    ps.velBuf.push({ t: now, x: tmpV.x, y: tmpV.y, z: tmpV.z });
  }
  while (ps.velBuf.length && now - ps.velBuf[0].t > VEL_WINDOW) ps.velBuf.shift();
  if (ps.velBuf.length) {
    tmpV.set(0, 0, 0);
    for (const s of ps.velBuf) {
      tmpV.x += s.x; tmpV.y += s.y; tmpV.z += s.z;
    }
    tmpV.divideScalar(ps.velBuf.length);
    ps.vel.lerp(tmpV, 0.7);
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
function applyBounceSpin(vel, spin) {
  vel.x -= DIMS.bounceSpinKick * spin.z;
  vel.z += DIMS.bounceSpinKick * spin.x;
  spin.multiplyScalar(0.72);
}

function collidePaddle(ball, pad, k, events) {
  padPos.copy(pad.prev).lerp(pad.pos, k);
  // margen extra de detección (solo en el saque: bola recién lanzada)
  const extra = pad.extraReach || 0;

  relPrev.copy(tmpPrev).sub(padPos);
  const dPrev = relPrev.dot(pad.normal);
  relNow.copy(ball.pos).sub(padPos);
  const dNow = relNow.dot(pad.normal);

  const crossing = dPrev > 0 !== dNow > 0;
  const touching = Math.abs(dNow) <= DIMS.ballRadius + 0.03 + (extra ? 0.045 : 0);
  if (!crossing && !touching) return;

  if (crossing) {
    const t = Math.min(1, Math.max(0, dPrev / (dPrev - dNow)));
    crossPoint.copy(tmpPrev).lerp(ball.pos, t);
  } else {
    crossPoint.copy(ball.pos);
  }

  // Coordenadas locales del cruce (origen = punto de agarre del mando)
  const lx = relNow.copy(crossPoint).sub(padPos).dot(pad.right);
  const ly = relNow.dot(pad.up);
  // hoja: disco de radio R centrado en bladeCenterUp sobre el agarre
  // (+ zona de asistencia para que no haga falta milimetrar el golpe)
  const dyy = ly - DIMS.bladeCenterUp;
  const reach = DIMS.bladeRadius + DIMS.ballRadius + DIMS.hitAssistRadius + extra;
  const onBlade = lx * lx + dyy * dyy <= reach * reach;
  // mango: zona alrededor del propio agarre
  const onHandle = Math.abs(lx) < 0.05 && ly > -0.12 && ly < 0.12;
  if (!onBlade && !onHandle) return;

  // Normal efectiva: la bola puede golpear cualquiera de las dos caras
  relVel.copy(ball.vel).sub(pad.vel);
  tmpN.copy(pad.normal);
  if (relVel.dot(tmpN) > 0) tmpN.negate();
  const vRelN = relVel.dot(tmpN);
  if (vRelN >= 0) return;

  // Reflexión con pala "infinitamente masiva" en movimiento
  ball.vel.addScaledVector(tmpN, -(1 + DIMS.paddleRestitution) * vRelN);

  // Golpe con CUERPO: transfiere parte de la velocidad de la pala en la
  // dirección de salida (acelerar la mano = bola más rápida, siempre)
  const padN = pad.vel.dot(tmpN);
  if (padN > 0) ball.vel.addScaledVector(tmpN, padN * 0.22);

  // Velocidad mínima de salida para jugabilidad (golpes siempre sólidos)
  const vn = ball.vel.dot(tmpN);
  if (vn < DIMS.minExitSpeed) ball.vel.addScaledVector(tmpN, DIMS.minExitSpeed - vn);

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
  ball.spin.copy(tmpS);

  // Colocar la bola sobre la cara de contacto
  const front = DIMS.ballRadius + 0.002;
  ball.pos
    .copy(padPos)
    .addScaledVector(tmpN, front)
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
  const n = Math.max(1, Math.min(96, Math.ceil(dt / MAX_SUBSTEP_DT)));
  const h = dt / n;

  for (let i = 0; i < n; i++) {
    const k = (i + 0.5) / n;
    for (const p of paddles) if (p.cooldown > 0) p.cooldown -= h;

    tmpPrev.copy(ball.pos);
    const prevY = ball.pos.y;
    const prevZ = ball.pos.z;

    ball.vel.y += DIMS.gravity * h;
    applyAerodynamics(ball.vel, ball.spin, h);
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

/** Predice el MEJOR punto de golpeo de la bola en el campo de `sign`. */
function predictStrike(ball, sign) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const pos = ball.pos.clone();
  const vel = ball.vel.clone();
  const spin = ball.spin ? ball.spin.clone() : new THREE.Vector3();
  const h = 1 / 240;
  let t = 0;
  let myBounces = 0;
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
      vel.y *= -DIMS.tableRestitution;
      vel.x *= DIMS.tableFriction;
      vel.z *= DIMS.tableFriction;
      applyBounceSpin(vel, spin);
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
      vel.y *= -DIMS.tableRestitution;
      vel.x *= DIMS.tableFriction;
      vel.z *= DIMS.tableFriction;
      applyBounceSpin(vel, sp);
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
 *  rival: por eso se empieza por los vuelos rápidos. */
function findServeVelocity(from, ownSign) {
  const C = DIMS.tableCenterZ;
  const topR = DIMS.tableTopY + DIMS.ballRadius;
  const HL = DIMS.tableHalfLength;
  // topspin hacia la red (como un saque real con efecto)
  const spin = new THREE.Vector3(-ownSign * 9, (Math.random() - 0.5) * 4, 0);

  for (let phase = 0; phase < 2; phase++) {
    const minOppDepth = phase === 0 ? HL * 0.5 : 0;
    // bote propio profundo y vuelo rápido: el arrastre aerodinámico frena la
    // bola, así que se barre un factor multiplicador de la velocidad balística
    // hasta que el bote rival cae en la mitad profunda del campo contrario
    const depths = phase === 0 ? [0.78, 0.7, 0.84] : [0.6, 0.7, 0.5, 0.8];
    const times = phase === 0 ? [0.3, 0.24, 0.36, 0.2] : [0.3, 0.4, 0.5, 0.62, 0.75];
    const mults = phase === 0 ? [1.0, 1.15, 1.3, 1.45, 1.6, 1.75] : [1.0];
    for (const depth of depths) {
      for (const T of times) {
        for (const m of mults) {
          const p1 = new THREE.Vector3(
            (Math.random() * 2 - 1) * 0.22,
            topR,
            C + ownSign * depth,
          );
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

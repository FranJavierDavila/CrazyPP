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
  easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.15, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },
  medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.05,  missBase: 0.08, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },
  hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.024, missBase: 0.03, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },
};

/** Escala un preset de IA por un factor de habilidad k (0,7…2,2):
 *  k > 1 → más rápida, precisa y agresiva; k < 1 → más lenta y falona.
 *  Se usa para la IA ADAPTATIVA (según el marcador) y el modo SUPERVIVENCIA
 *  (la CPU acelera rallye a rallye). Devuelve un preset NUEVO. */
function scalePreset(cfg, k) {
  const kk = THREE.MathUtils.clamp(k, 0.7, 2.2);
  return {
    maxSpeed: cfg.maxSpeed * THREE.MathUtils.clamp(kk, 0.55, 1.9),
    accel: Math.min(30, cfg.accel * Math.pow(kk, 1.4)),
    errStd: cfg.errStd / Math.max(0.6, Math.pow(kk, 0.8)),
    missBase: THREE.MathUtils.clamp(cfg.missBase * Math.max(0.25, 2 - kk), 0.005, 0.45),
    minT: THREE.MathUtils.clamp(cfg.minT / Math.max(0.6, Math.pow(kk, 0.5)), 0.24, 1.0),
    maxT: THREE.MathUtils.clamp(cfg.maxT / Math.max(0.6, Math.pow(kk, 0.5)), 0.4, 1.3),
    maxShotSpeed: cfg.maxShotSpeed * THREE.MathUtils.clamp(kk, 0.5, 1.8),
    predictInterval: cfg.predictInterval / Math.max(0.6, Math.pow(kk, 0.8)),
    smash: THREE.MathUtils.clamp(cfg.smash * Math.max(0.5, kk), 0.01, 0.75),
    short: cfg.short,
  };
}

const COLORS = {
  tableBlue: 0x17539e, tableEdge: 0x0e3a73, frame: 0x22262b,
  floor: 0x37302b, wall: 0x1a1e23,
  ball: 0xfff8ef, accentAmber: 0xe8b45a, accentGreen: 0x7fb069,
};

/* =====================================================================
 *  TEMAS DE SALA (v2.14): ambientes visuales intercambiables al vuelo.
 *  Cada tema redefine suelo/paredes/techo/paneles de luz/tira LED/rejilla,
 *  las tres luces de la escena, el fondo y la niebla. La mesa, las vallas
 *  LED y la bola NO cambian (legibilidad del juego).
 *  Ciclo en VR: flick LATERAL del stick (los ejes están libres; el click
 *  de stick ya es dificultad, B modo, Y entrenamiento, A/X mano de la pala).
 * ===================================================================== */
const ROOM_THEMES = [
  {
    key: 'pabellon', name: 'Pabellón', emoji: '🏓',
    floor: 0x37302b, gridC: 0x4a4038, gridG: 0x2c2622,
    wall: 0x1a1e23, ceil: 0x14171b, panel: 0xf5efe2,
    strip: 0xe8b45a, ring: 0xe8b45a,
    bg: 0x0b0e11, fogNear: 9, fogFar: 18,
    hemiSky: 0xffe6c4, hemiGround: 0x35271b, hemiInt: 0.95,
    dirCol: 0xfff1dc, dirInt: 2.4, spotCol: 0xffe2b8, spotInt: 0.5,
    envInt: 0.75,
  },
  {
    key: 'neon', name: 'Neón', emoji: '💜',
    floor: 0x10121f, gridC: 0x2b3f8f, gridG: 0x181d3a,
    wall: 0x0a0c16, ceil: 0x05060d, panel: 0xbfe3ff,
    strip: 0x35f0ff, ring: 0xff3fa4,
    bg: 0x04050b, fogNear: 10, fogFar: 20,
    hemiSky: 0x8ab5ff, hemiGround: 0x0a0e1a, hemiInt: 0.7,
    dirCol: 0xbfd4ff, dirInt: 1.7, spotCol: 0x57c7ff, spotInt: 0.75,
    envInt: 0.45,
  },
  {
    key: 'atardecer', name: 'Atardecer', emoji: '🌅',
    floor: 0x4a3527, gridC: 0x7a5136, gridG: 0x402c1e,
    wall: 0x3a2430, ceil: 0x241a22, panel: 0xffd9a8,
    strip: 0xff8a5c, ring: 0xffb070,
    bg: 0x1a0f14, fogNear: 9, fogFar: 18,
    hemiSky: 0xffc08a, hemiGround: 0x4a2330, hemiInt: 1.0,
    dirCol: 0xffb070, dirInt: 2.1, spotCol: 0xff9a6a, spotInt: 0.6,
    envInt: 0.8,
  },
  {
    key: 'artico', name: 'Ártico', emoji: '❄️',
    floor: 0x2e3a42, gridC: 0x55707f, gridG: 0x2c3a44,
    wall: 0x1c2830, ceil: 0x111a20, panel: 0xffffff,
    strip: 0x8fd3e8, ring: 0xbfe3ff,
    bg: 0x0d1418, fogNear: 9, fogFar: 19,
    hemiSky: 0xeaf4ff, hemiGround: 0x2a3a44, hemiInt: 1.0,
    dirCol: 0xffffff, dirInt: 2.3, spotCol: 0xdff0ff, spotInt: 0.55,
    envInt: 0.85,
  },
];

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
    this._wdFails = 0;
    this._lastRebuild = 0;
    this.hadGesture = false;   // ya hubo gesto de usuario (clic, gatillo XR…)
    this.rebuilds = 0;
    this.xrActive = false;     // sesión XR inmersiva activa (lo marca el juego)
    this._lastAlive = 0;
    this._lastCT = -1;         // último currentTime medido (watchdog)
    this._ctAdvanced = true;   // ¿el reloj de audio avanza? (estado 'running' vivo)
    this._ctStalls = 0;        // ticks consecutivos con el reloj congelado
    // --- ambiente de torneo (v2.11) ---
    this.ambience = true;      // murmullo + aplausos + megafonía
    try { this.ambience = localStorage.getItem('ppxr_amb_v1') !== '0'; } catch { /* */ }
    this._amb = null;          // nodos del murmullo en marcha
    this._ambBuffer = null;    // buffer de ruido "grumoso" reutilizable
    this._lastOhh = 0;
    this._lastAnnounce = 0;
    // El sensor de proximidad de la Quest suspende la pestaña al ajustar el
    // visor; al volver, el contexto de audio queda a veces suspendido.
    // Al recuperar visibilidad: rescate SUAVE (resume + recrear solo si el
    // contexto no arranca; nunca destruye uno sano).
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.hadGesture = true;
        this.kick();
      }
    });
    // RECUPERACIÓN DEL FOCO DE LA VENTANA: al volver de la interfaz del
    // sistema (Quest Link / menú universal) el navegador puede dejar el
    // contexto suspendido o con la salida re-enrutada. Rescate suave + blip
    // de confirmación: si el usuario OYE el blip al enfocar la ventana, la
    // salida funciona; si no, el chip en pared dirá si el contexto vive.
    window.addEventListener('focus', () => {
      this.hadGesture = true;
      this.kick();
      if (this.ctx && this.ctx.state === 'running' && this.xrActive) {
        this.blipAlive();
      }
    });
    // CUALQUIER toque en la página (menú 2D, dificultad, HUD…) es un gesto
    // válido para reactivar el audio: vía de rescate principal fuera de VR.
    const gesture = () => { this.hadGesture = true; this.kick(); };
    document.addEventListener('pointerdown', gesture, { passive: true });
    document.addEventListener('click', gesture, { passive: true });
  }

  /** Cablea el grafo de salida (master -> compresor -> destino) y el buffer
   *  de ruido SOBRE un contexto dado. */
  _wire(ctx) {
    this.master = ctx.createGain();
    this.master.gain.value = 0.9;
    // Compresor: golpes más presentes y audibles en el altavoz del visor
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -16;
    comp.knee.value = 22;
    comp.ratio.value = 5;
    comp.attack.value = 0.002;
    comp.release.value = 0.12;
    this.master.connect(comp);
    comp.connect(ctx.destination);
    const len = Math.floor(ctx.sampleRate * 0.25);
    this.noiseBuffer = ctx.createBuffer(1, len, ctx.sampleRate);
    const data = this.noiseBuffer.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
  }

  /** Observador de estado por contexto: reintenta y avisa al recover() global. */
  _hookState(ctx) {
    if (!ctx || ctx.__ppHooked) return;
    ctx.__ppHooked = true;
    ctx.addEventListener?.('statechange', () => {
      if (this.ctx !== ctx) return;
      console.info('[Audio] estado ->', ctx.state, this.xrActive ? '(VR)' : '(2D)');
      if (ctx.state === 'running') {
        this._wdFails = 0;
        if (this.xrActive) this.blipAlive();  // el jugador OYE que el audio volvió
      } else if (ctx.state === 'suspended' && this.xrActive) {
        void ctx.resume().catch(() => {});
        window.setTimeout(() => {
          if (this.ctx === ctx && ctx.state !== 'running' && this.xrActive) {
            this.tryFreshRunning('statechange (suspended en VR)');
          }
        }, 900);
      }
    });
  }

  _create() {
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return false;
      try {
        this.ctx = new Ctor({ latencyHint: 'interactive' });
      } catch {
        this.ctx = new Ctor();
      }
      this._wire(this.ctx);
      this._hookState(this.ctx);
      this.rebuilds++;
      console.info('[Audio] contexto creado · estado:', this.ctx.state);
      return true;
    } catch (e) {
      console.warn('[Audio] no se pudo crear el contexto:', e?.message);
      this.ctx = null;
      this.master = null;
      this.noiseBuffer = null;
      return false;
    }
  }

  /** Crea un contexto NUEVO y lo adopta SOLO si consigue arrancar 'running'.
   *  Si no lo consigue, lo descarta y CONSERVA el contexto anterior: el audio
   *  NUNCA queda peor que antes del intento.
   *  (v2.8 cerraba el contexto viejo ANTES de crear el nuevo; si el nuevo
   *  nacía suspendido dentro de la sesión XR de la Quest, el resultado era
   *  mudez total e irreversible. Con esta política eso es imposible.) */
  tryFreshRunning(reason) {
    const now = performance.now();
    if (now - this._lastRebuild < 900) return false;
    this._lastRebuild = now;
    const old = this.ctx;
    let fresh = null;
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return false;
      try { fresh = new Ctor({ latencyHint: 'interactive' }); }
      catch { fresh = new Ctor(); }
    } catch (e) {
      console.warn('[Audio] contexto nuevo falló:', e?.message);
      return false;
    }
    this.rebuilds++;
    console.info('[Audio] contexto nuevo ·', fresh.state, '·', reason);
    this._hookState(fresh);
    let done = false;
    const adopt = () => {
      if (done) return;
      done = true;
      this.master = null;
      this.noiseBuffer = null;
      if (old && old !== fresh) { try { old.close(); } catch { /* ya cerrado */ } }
      this.ctx = fresh;
      try { this._wire(fresh); } catch { /* playOsc/playNoise quedan inermes */ }
      this._wdFails = 0;
      console.info('[Audio] contexto NUEVO ADOPTADO (running) ·', reason);
      if (this.xrActive) this.blipAlive();
    };
    const discard = () => {
      if (done) return;
      done = true;
      try { fresh.close(); } catch { /* */ }
      console.info('[Audio] contexto nuevo descartado · se conserva el anterior ·', reason);
    };
    const decide = () => {
      if (done || !fresh) return;
      if (fresh.state === 'running') { adopt(); return; }
      void fresh.resume().catch(() => {});
      window.setTimeout(() => {
        if (done || !fresh) return;
        if (fresh.state === 'running') adopt(); else discard();
      }, 600);
    };
    decide();
    return true;
  }

  /** Blip doble de confirmación: suena cuando el audio (re)arranca dentro de
   *  la sesión VR, para que el jugador sepa que ya hay sonido otra vez. */
  blipAlive() {
    const now = performance.now();
    if (now - this._lastAlive < 4000) return;
    this._lastAlive = now;
    this.playOsc(880, 1320, 0.14, 'sine', 0.35, 0);
    window.setTimeout(() => this.playOsc(1320, 1760, 0.18, 'sine', 0.3, 0), 160);
  }

  ensure() {
    if (this.ctx) {
      const st = this.ctx.state;
      if (st === 'running') return;
      // 'closed'/'failed': un resume() ya no sirve NUNCA -> recrear.
      // (Antes este caso quedaba en silencio para siempre: la causa raíz
      // del "no suena nada".)
      if (st === 'closed' || st === 'failed') {
        this.ctx = null;
        this.master = null;
        this.noiseBuffer = null;
        this._create();
        return;
      }
      void this.ctx.resume().catch(() => {});
      return;
    }
    this._create();
  }

  /** Reactiva el audio SIEMPRE antes de sonar. Si tras el resume() el
   *  contexto sigue sin arrancar y ya hubo gesto de usuario, se RECONSTRUYE
   *  dentro de ese gesto: un AudioContext nuevo creado durante el gatillo
   *  de la Quest nace 'running'. */
  kick() {
    this.hadGesture = true;
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      void this.ctx.resume().catch(() => {});
      // Intento recreativo SIN destruir el actual: si el nuevo arranca, se
      // adopta; si no, se conserva el previo (nunca queda peor).
      this.tryFreshRunning('kick (resume sin efecto)');
    }
  }

  /** Preparación AL PULSAR ENTRAR EN VR (gesto garantizado): repara un
   *  contexto enfermo y deja uno 'running' antes de la sesión inmersiva.
   *  NO destruye un contexto sano (era contraproducente en la Quest). */
  prepareVR() {
    this.hadGesture = true;
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      this.tryFreshRunning('preparación VR (contexto enfermo)');
    }
  }

  /** RE-VINCULACIÓN al entrar/salir de VR: crea un contexto nuevo dentro de
   *  la sesión (nace ligado a la salida activa del casco) y lo adopta SOLO si
   *  arranca 'running'; en caso contrario conserva el anterior. */
  rebind(reason) {
    this.hadGesture = true;
    this.tryFreshRunning(reason || 're-vinculación de salida');
  }

  /** ¿El reloj de audio avanza? (false = estado 'running' pero grafo muerto) */
  clockAlive() {
    return this._ctAdvanced !== false;
  }

  watchdog(dt) {
    this._wdAcc += dt;
    if (this._wdAcc < 0.7) return;
    this._wdAcc = 0;
    if (!this.ctx) {
      if (this.hadGesture) this._create();
      return;
    }
    if (this.ctx.state === 'running') {
      this._wdFails = 0;
      // DETECCIÓN DE GRAFO MUERTO: el estado dice 'running' pero el reloj
      // de audio (currentTime) lleva congelado ~2,8 s (4 ticks). Algunos
      // navegadores/VR dejan el contexto en ese estado zombi al cambiar el
      // foco de la ventana o re-enrutar la salida. Recreación de rescate
      // (adoptar-solo-si-running: nunca queda peor que antes).
      const ct = this.ctx.currentTime;
      this._ctAdvanced = Number.isFinite(ct) && ct > this._lastCT + 1e-4;
      this._lastCT = ct;
      if (this._ctAdvanced) {
        this._ctStalls = 0;
      } else if (++this._ctStalls >= 4 && this.hadGesture) {
        this._ctStalls = 0;
        this.tryFreshRunning('watchdog (reloj de audio congelado)');
      }
      return;
    }
    this.ctx.resume().catch(() => {});
    this._wdFails++;
    if (this._wdFails >= 5 && this.hadGesture) {
      this.tryFreshRunning('watchdog (suspended persistente)');
    }
  }

  panNode(pan) {
    if (!this.ctx || !this.master) return null;
    const p = this.ctx.createStereoPanner();
    // NaN/Infinity -> 0 (un valor no finito aquí LANZA y mata el frame)
    p.pan.value = Number.isFinite(pan) ? Math.max(-1, Math.min(1, pan)) : 0;
    p.connect(this.master);
    return p;
  }

  playOsc(freq, endFreq, dur, type, gain, pan) {
    try {
      this.kick();
      if (!this.ctx || !this.master) return;
      if (![freq, endFreq, dur, gain].every(Number.isFinite)) return;
      const dest = this.panNode(pan);
      if (!dest) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const g = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(Math.max(20, freq), t);
      osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), t + dur);
      g.gain.setValueAtTime(Math.max(0.001, gain), t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(g); g.connect(dest);
      osc.start(t); osc.stop(t + dur + 0.02);
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  playNoise(dur, filterFreq, q, gain, pan, type = 'bandpass') {
    try {
      this.kick();
      if (!this.ctx || !this.noiseBuffer) return;
      if (![dur, filterFreq, q, gain].every(Number.isFinite)) return;
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
      g.gain.setValueAtTime(Math.max(0.001, gain), t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      src.connect(filter); filter.connect(g); g.connect(dest);
      src.start(t); src.stop(t + dur + 0.02);
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
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

  /** FANFARRIA de fin de partido.
   *  Victoria: arpegio mayor ascendente (C5-E5-G5) + acorde final brillante
   *  con capa de octava y platillo -> "¡ta-da!".
   *  Derrota: "trombón triste" descendente (bend hacia abajo + lowpass). */
  fanfare(win) {
    try {
      this.kick();
      if (!this.ctx || !this.master) return;
      const t0 = this.ctx.currentTime + 0.06;
      const seq = win
        ? [
            [523.25, 0.00, 0.17, 0.30],
            [659.25, 0.14, 0.17, 0.30],
            [783.99, 0.28, 0.17, 0.32],
            [1046.50, 0.42, 0.75, 0.34],
            [1318.51, 0.42, 0.75, 0.20],
            [1567.98, 0.62, 0.55, 0.14],
          ]
        : [
            [329.63, 0.00, 0.32, 0.28],
            [293.66, 0.32, 0.32, 0.28],
            [261.63, 0.64, 0.32, 0.28],
            [246.94, 0.96, 0.32, 0.26],
            [220.00, 1.28, 0.95, 0.30],
          ];
      for (const [f, dt, dur, vol] of seq) {
        const t = t0 + dt;
        const o = this.ctx.createOscillator();
        const g = this.ctx.createGain();
        o.type = win ? 'triangle' : 'sawtooth';
        o.frequency.setValueAtTime(f, t);
        if (!win) o.frequency.linearRampToValueAtTime(f * 0.93, t + dur);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.02);
        g.gain.setValueAtTime(vol, t + Math.max(0.03, dur - 0.07));
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        o.connect(g);
        if (win) {
          g.connect(this.master);
        } else {
          const lp = this.ctx.createBiquadFilter();
          lp.type = 'lowpass';
          lp.frequency.value = 900;
          g.connect(lp); lp.connect(this.master);
        }
        o.start(t); o.stop(t + dur + 0.05);
        if (win) {
          // capa de brillo una octava arriba
          const o2 = this.ctx.createOscillator();
          const g2 = this.ctx.createGain();
          o2.type = 'sine';
          o2.frequency.setValueAtTime(f * 2, t);
          g2.gain.setValueAtTime(0.0001, t);
          g2.gain.linearRampToValueAtTime(vol * 0.32, t + 0.02);
          g2.gain.linearRampToValueAtTime(0.0001, t + dur);
          o2.connect(g2); g2.connect(this.master);
          o2.start(t); o2.stop(t + dur + 0.05);
        }
      }
      if (win) this.playNoise(0.4, 6200, 0.7, 0.2, 0, 'highpass');
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  /* ================= AMBIENTE DE TORNEO (v2.11) ================= */

  /** Activa/desactiva el ambiente (murmullo + aplausos + megafonía).
   *  Se guarda en localStorage para recordar la preferencia. */
  setAmbience(on) {
    this.ambience = !!on;
    try { localStorage.setItem('ppxr_amb_v1', this.ambience ? '1' : '0'); } catch { /* */ }
    if (!this.ambience) this.stopMurmur();
  }

  /** Murmullo de público de fondo: bucle de ruido filtrado con vaivén lento.
   *  Se arranca al entrar en VR y se detiene al salir / apagar el ambiente. */
  startMurmur() {
    try {
      this.kick();
      if (!this.ctx || !this.master || this._amb || !this.ambience) return;
      if (!this._ambBuffer) {
        const len = Math.floor(this.ctx.sampleRate * 2);
        const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
        const d = buf.getChannelData(0);
        let acc = 0;
        for (let i = 0; i < len; i++) {
          // ruido rosa "grumoso": media móvil = murmullo, no siseo
          acc = acc * 0.92 + (Math.random() * 2 - 1) * 0.08;
          d[i] = acc * 8;
        }
        this._ambBuffer = buf;
      }
      const src = this.ctx.createBufferSource();
      src.buffer = this._ambBuffer;
      src.loop = true;
      const lp = this.ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.value = 520;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(0.0001, this.ctx.currentTime);
      g.gain.linearRampToValueAtTime(0.05, this.ctx.currentTime + 1.5);
      const lfo = this.ctx.createOscillator();
      lfo.frequency.value = 0.13;
      const lfoG = this.ctx.createGain();
      lfoG.gain.value = 0.02;
      lfo.connect(lfoG); lfoG.connect(g.gain);
      src.connect(lp); lp.connect(g); g.connect(this.master);
      src.start();
      lfo.start();
      this._amb = { src, lfo, gain: g };
    } catch { /* nunca rompe el juego */ }
  }

  stopMurmur() {
    const amb = this._amb;
    if (!amb || !this.ctx) return;
    this._amb = null;
    try {
      const t = this.ctx.currentTime;
      amb.gain.gain.cancelScheduledValues(t);
      amb.gain.gain.setValueAtTime(amb.gain.gain.value, t);
      amb.gain.gain.linearRampToValueAtTime(0.0001, t + 0.8);
      window.setTimeout(() => {
        try { amb.src.stop(); amb.lfo.stop(); } catch { /* ya parado */ }
      }, 900);
    } catch { /* */ }
  }

  /** APLAUSOS sintetizados: ruido con envolvente "espiky" aleatoria
   *  (cientos de micro-chasquidos = público aplaudiendo). big = ovación. */
  applause(big) {
    try {
      this.kick();
      if (!this.ctx || !this.master || !this.noiseBuffer || !this.ambience) return;
      if (![this.ctx.currentTime].every(Number.isFinite)) return;
      const t = this.ctx.currentTime + 0.02;
      const dur = big ? 2.6 : 1.15;
      const vol = big ? 0.5 : 0.3;
      for (let layer = 0; layer < (big ? 2 : 1); layer++) {
        const src = this.ctx.createBufferSource();
        src.buffer = this.noiseBuffer;
        src.loop = true;
        const bp = this.ctx.createBiquadFilter();
        bp.type = 'bandpass';
        bp.frequency.value = 1500 + Math.random() * 700;
        bp.Q.value = 0.55;
        const g = this.ctx.createGain();
        const N = 72;
        const curve = new Float32Array(N);
        for (let i = 0; i < N; i++) {
          const spiky = Math.random() < 0.55 ? Math.random() : Math.random() * 0.3;
          curve[i] = spiky;
        }
        // arranque rápido y cola que se apaga
        for (let i = 0; i < N; i++) {
          const f = i / (N - 1);
          curve[i] *= Math.min(1, f * 6) * (1 - f * f);
        }
        const t0 = t + layer * 0.18;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.setValueCurveAtTime(curve.map((v) => Math.max(0.0001, v * vol)), t0, dur * 0.82);
        g.gain.setValueAtTime(0.0001, t0 + dur * 0.82 + 0.01);
        g.gain.linearRampToValueAtTime(0.0001, t0 + dur);
        const pan = this.ctx.createStereoPanner();
        pan.pan.value = layer === 0 ? -0.35 : 0.35;
        src.connect(bp); bp.connect(g); g.connect(pan); pan.connect(this.master);
        src.start(t0);
        src.stop(t0 + dur + 0.15);
      }
    } catch { /* */ }
  }

  /** "Ohh" del público (red, bola fuera…): dos sierras graves con formantes
   *  de vocal, hinchándose y apagándose. Throttle interno de 3,5 s. */
  ohh() {
    try {
      const now = performance.now();
      if (now - this._lastOhh < 3500) return;
      this._lastOhh = now;
      this.kick();
      if (!this.ctx || !this.master || !this.ambience) return;
      const t = this.ctx.currentTime + 0.02;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(0.15, t + 0.24);
      g.gain.setValueAtTime(0.15, t + 0.42);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.95);
      for (const [f0, fq, q] of [[112, 470, 2.2], [138, 920, 2.6]]) {
        const o = this.ctx.createOscillator();
        o.type = 'sawtooth';
        o.frequency.setValueAtTime(f0, t);
        o.frequency.linearRampToValueAtTime(f0 * 0.82, t + 0.95);
        const bp = this.ctx.createBiquadFilter();
        bp.type = 'bandpass';
        bp.frequency.value = fq;
        bp.Q.value = q;
        o.connect(bp); bp.connect(g);
        o.start(t); o.stop(t + 1.05);
      }
      g.connect(this.master);
    } catch { /* */ }
  }

  /** MEGAFONÍA del marcador: chime de torneo + voz ("5-3, saque para ti").
   *  Usa speechSynthesis si está disponible (en la Quest, es-ES); si no,
   *  queda el chime + el texto en el marcador. Throttle de 6 s salvo force. */
  announce(text, force) {
    try {
      const now = performance.now();
      if (!force && now - this._lastAnnounce < 6000) return;
      this._lastAnnounce = now;
      if (!this.ambience) return;
      this.playOsc(660, 660, 0.12, 'sine', 0.2, 0);
      window.setTimeout(() => this.playOsc(990, 990, 0.16, 'sine', 0.2, 0), 140);
      const ss = window.speechSynthesis;
      if (!ss || typeof SpeechSynthesisUtterance === 'undefined') return;
      ss.cancel();
      const u = new SpeechSynthesisUtterance(String(text));
      u.lang = 'es-ES';
      u.rate = 0.98;
      u.pitch = 0.78;
      u.volume = 0.95;
      try {
        const v = ss.getVoices().find((x) => x.lang && x.lang.toLowerCase().startsWith('es'));
        if (v) u.voice = v;
      } catch { /* voz por defecto */ }
      ss.speak(u);
    } catch { /* */ }
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

/* =====================================================================
 *  ESTADÍSTICAS Y LOGROS · progreso persistente en localStorage
 *  Se guardan victorias, rachas, saques directos y el mejor rallye; los
 *  logros se desbloquean una sola vez (guardan su fecha) y se celebran
 *  con megafonía + confeti dentro y fuera del visor.
 * ===================================================================== */
const ACHIEVEMENTS = [
  { key: 'primera',  emoji: '🥇', name: 'Primera victoria', desc: 'Gana tu primer partido' },
  { key: 'racha3',   emoji: '🔥', name: 'En racha',         desc: '3 victorias seguidas' },
  { key: 'gigante',  emoji: '💪', name: 'Gigante',          desc: 'Vence en dificultad Difícil' },
  { key: 'maraton',  emoji: '🏃', name: 'Maratonista',      desc: 'Rallye de 20 o más golpes' },
  { key: 'superviv', emoji: '⏱️', name: 'Superviviente',    desc: '25 o más golpes en Supervivencia' },
  { key: 'aces10',   emoji: '🎯', name: 'Saque directo',    desc: '10 saques ganados sin respuesta' },
];

class GameStats {
  constructor() {
    this.KEY = 'ppxr_stats_v1';
    this.data = {
      won: 0, lost: 0, streak: 0, bestStreak: 0,
      pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
      winsByDiff: { easy: 0, medium: 0, hard: 0 },
      ach: {},
    };
    try {
      const raw = localStorage.getItem(this.KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        Object.assign(this.data, saved);
        this.data.winsByDiff = Object.assign({ easy: 0, medium: 0, hard: 0 }, saved.winsByDiff || {});
        this.data.ach = saved.ach || {};
      }
    } catch { /* datos corruptos: se recrean limpios */ }
  }

  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.data)); } catch { /* */ }
  }

  unlock(key) {
    if (this.data.ach[key]) return false;
    this.data.ach[key] = Date.now();
    this.save();
    return true;
  }

  /** Punto de PARTIDO (a 11). Devuelve las claves de logros nuevos. */
  recordPoint(winner, rallyHits) {
    const out = [];
    if (winner === 'player') {
      this.data.pointsWon++;
      // SAQUE DIRECTO (ace): solo tocó la bola el sacador
      if (rallyHits === 1) {
        this.data.aces++;
        if (this.data.aces >= 10 && this.unlock('aces10')) out.push('aces10');
      }
    } else {
      this.data.pointsLost++;
    }
    out.push(...this.recordRally(rallyHits));
    this.save();
    return out;
  }

  /** Rallye terminado en cualquier modo. Devuelve logros nuevos. */
  recordRally(rallyHits) {
    const out = [];
    const n = rallyHits || 0;
    if (n > this.data.bestRally) this.data.bestRally = n;
    if (n >= 20 && this.unlock('maraton')) out.push('maraton');
    return out;
  }

  /** Rallye de SUPERVIVENCIA: récord histórico + logro dedicado. */
  recordSurvivalRally(golpes, bestEver) {
    const out = this.recordRally(golpes);
    if (bestEver >= 25 && this.unlock('superviv')) out.push('superviv');
    this.save();
    return out;
  }

  /** Fin de PARTIDO. Devuelve logros nuevos. */
  recordMatch(win, difficulty) {
    const out = [];
    if (win) {
      this.data.won++;
      this.data.streak++;
      if (this.data.streak > this.data.bestStreak) this.data.bestStreak = this.data.streak;
      this.data.winsByDiff[difficulty] = (this.data.winsByDiff[difficulty] || 0) + 1;
      if (this.unlock('primera')) out.push('primera');
      if (this.data.streak >= 3 && this.unlock('racha3')) out.push('racha3');
      if (difficulty === 'hard' && this.unlock('gigante')) out.push('gigante');
    } else {
      this.data.lost++;
      this.data.streak = 0;
    }
    this.save();
    return out;
  }
}

/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, saque con mano libre,
 *  háptica y bucle principal
 * ===================================================================== */
// v2.28: arte de la cabecera del MENÚ PRINCIPAL (data URL JPEG incrustado
// por build_html.py — recorte del logo CRAZY PING PONG del arte del juego)
const MENU_LOGO_SRC = '__MENU_LOGO_B64__';

const BALL_HAND_LIFT = 0.08;   // bola "apoyada" sobre la palma de la mano libre
const AI_TOSS_T = 0.55;        // duración del lanzamiento (y swing) del saque de la IA

// temporales del sistema de pose de las palas IA (no compartir con física)
const poseE = new THREE.Euler();
const poseQ = new THREE.Quaternion();
const poseD = new THREE.Vector3();
const swingV = new THREE.Vector3();   // vector del follow-through (v2.17)
// v2.22 · orientación de la cara de la pala (base ortonormal)
const aimV = new THREE.Vector3();     // dirección deseada de la normal de cara
const aimX = new THREE.Vector3();     // eje lateral del marco de la cara
const aimY = new THREE.Vector3();     // eje "arriba" de la hoja
const aimM = new THREE.Matrix4();     // base -> cuaternión
const aimUP = new THREE.Vector3(0, 1, 0);
const aimRollQ = new THREE.Quaternion();
const aimPitchQ = new THREE.Quaternion();
const AIM_Z = new THREE.Vector3(0, 0, 1);   // normal local de la cara (IA)
const AIM_XA = new THREE.Vector3(1, 0, 0);  // eje local X (pitch de muñeca)
// v2.23 · POSE POR GOLPE: la pala se compone desde DOS direcciones mundiales
// (eje de la hoja mango→punta + normal de la cara) y un roll de muñeca.
const AIM_FWD = new THREE.Vector3();      // hacia el campo contrario
const AIM_RIGHT = new THREE.Vector3();    // lado de la mano derecha del jugador
const AIM_BLADE = new THREE.Vector3();    // eje de la hoja deseado
const AIM_FACE = new THREE.Vector3();     // normal de la cara deseada
const AIM_BX = new THREE.Vector3();
const AIM_BY = new THREE.Vector3();
const AIM_BZ = new THREE.Vector3();

/** Firma de cada golpe (v2.23) — hace que la pala GIRE como la giraría un
 *  jugador real en vez de quedarse vertical:
 *  side0  inclinación de la punta hacia el lado del golpe en el contacto
 *  side1  cruce de la punta al lado contrario al terminar el follow-through
 *  fwd0/fwd1  inclinación de la hoja hacia delante (tap vertical en la
 *             cortada, barrido diagonal en el drive)
 *  clos0  cierre de la cara en el contacto (+ liftado · − cortada/slice)
 *  clos1  cierre extra durante el follow-through
 *  rise   elevación del brazo al terminar
 *  cross  cruce del cuerpo (posición) al terminar */
const SWING_POSE = {
  drive:   { side0: 0.55, side1: 0.42, fwd0: 0.20, fwd1: 0.34, clos0: 0.14, clos1: 0.20, rise: 0.13, cross: 1.0 },
  smash:   { side0: 0.50, side1: 0.36, fwd0: 0.15, fwd1: 0.40, clos0: 0.24, clos1: 0.16, rise: 0.07, cross: 1.0 },
  push:    { side0: 0.42, side1: 0.26, fwd0: 0.06, fwd1: 0.16, clos0: -0.16, clos1: -0.08, rise: 0.05, cross: 0.6 },
  dejada:  { side0: 0.50, side1: 0.30, fwd0: 0.10, fwd1: 0.20, clos0: -0.12, clos1: -0.04, rise: 0.12, cross: 0.7 },
  bloqueo: { side0: 0.30, side1: 0.18, fwd0: 0.10, fwd1: 0.15, clos0: 0.05, clos1: 0.03, rise: 0.04, cross: 0.5 },
};

// temporales del anti-clipping de palas (mesa / red / suelo)
const pcA = new THREE.Vector3();
const pcN = new THREE.Vector3();
const pcC = new THREE.Vector3();
const pcT = new THREE.Vector3();

// temporales del MENÚ DE MUÑECA (v2.15, espacio mundo; no compartir)
const muGrip = new THREE.Vector3();
const muHead = new THREE.Vector3();
const muDir = new THREE.Vector3();
const muPos = new THREE.Vector3();
const muQ = new THREE.Quaternion();
const muRaycaster = new THREE.Raycaster();
const netTmpP = new THREE.Vector3();   // v2.19: poses del rival por red
const netTmpQ = new THREE.Quaternion();
muRaycaster.far = 2.5;

class PingPongGame {
  constructor(canvas, paddleModel, callbacks = {}) {
    this.canvas = canvas;
    this.callbacks = callbacks;
    this.disposed = false;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,   // necesario para passthrough (immersive-ar)
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight, false);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.xr.enabled = true;
    this.renderer.xr.setReferenceSpaceType('local-floor');
    // Nitidez máxima en el visor: sin foveación (borde nítido en toda la
    // lente) y framebuffer sobredimensionado (Quest 3 tiene GPU de sobra
    // para esta escena).
    this.renderer.xr.setFoveation(0);
    this.renderer.xr.setFramebufferScaleFactor(1.7);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0b0e11);
    this.scene.fog = new THREE.Fog(0x0b0e11, 9, 18);
    this.rig = new THREE.Group();
    this.scene.add(this.rig);

    // Entorno PBR para que la pala (materiales metálicos/texturizados) luzca real
    try {
      const pmrem = new THREE.PMREMGenerator(this.renderer);
      this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
      this.scene.environmentIntensity = 0.75;
    } catch { /* si falla, iluminación clásica */ }

    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.05, 60);
    this.camera.position.set(2.2, 1.5, 1.4);
    this.rig.add(this.camera);

    this.audio = new GameAudio();
    this.rules = new Rules();
    this.ball = {
      pos: new THREE.Vector3(0, 1, DIMS.tableCenterZ + 0.4),
      vel: new THREE.Vector3(),
      spin: new THREE.Vector3(),
    };

    // seguimiento de ambos mandos (uno lleva la pala, otro la bola)
    this.paddleModelRef = paddleModel;
    this.controllerPaddles = [createPaddleSim('player', 0), createPaddleSim('player', 1)];
    this.paddleHand = 0;         // mando con la pala (0 izq / 1 der)
    this.manualHand = false;     // el usuario cambió de mano con A/X
    this.gripDown = [false, false];
    this.btn4Prev = [false, false];
    this.connected = [false, false];
    this.sources = [null, null];
    this.handOf = ['right', 'right'];   // lateralidad de cada mando

    // Ajuste del agarre (offsets sobre la montura natural) y modo entrenamiento
    this.gripOffset = { px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0 };
    this.gripOffsetQ = new THREE.Quaternion();
    this.gripName = 'Natural';
    this.calib = false;
    this.preCalibMode = 'match';  // modo al que se vuelve al salir del entrenamiento
    this.pendingCalib = false;
    this.feedTimer = 1.5;
    this.feedIdle = 0;
    this.panelDirty = true;
    this.btnPrev = {};
    // MENÚ DE MUÑECA (v2.15): un solo acceso a modo/dificultad/sala/ambiente
    this.menuOpen = false;
    this.menuHover = [-1, -1];   // hover INDEPENDIENTE por mando (v2.16)
    this.menuRects = [];
    this._menuState = '';
    this.lastFeedTap = 0;
    // v2.24: three.js emite selectstart/squeezestart por TODOS los espacios
    // del mismo mando (targetRay, grip y hand — WebXRController.dispatchEvent).
    // Con listeners duplicados cada pulsación disparaba onSelectStart DOS
    // veces: los basculantes volvían a su estado (parecían muertos) y el
    // teclado del código escribía cada letra por duplicado. Además del
    // listener único, guardia temporal por mando.
    this._lastSelect = [0, 0];
    // ESTELA de la bola (v2.18): conmutable desde el menú y persistente
    try { this.showTrail = localStorage.getItem('ppxr_trail_v1') !== '0'; } catch { this.showTrail = true; }
    // MULTIJUGADOR ONLINE (v2.19): P2P por WebRTC (PeerJS) + voz
    this.net = new NetLink(this);
    this.menuPage = 'main';       // 'main' | 'multi' | 'join' (teclado)
    this.menuSec = 'match';       // v2.28: sección ABIERTA del acordeón
    this._menuAnchorUntil = 0;    // v2.28: flotación inicial del panel
    this._joinCode = '';
    this._localHit = false;       // golpeo propio pendiente de enviar este frame
    // fanfarria de fin de partido (banner + confeti)
    this.fanfareWin = false;
    this.fanfareT = 0;

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
    // --- modos de juego (v2.11) ---
    this.mode = 'match';          // 'match' | 'survival' (en curso)
    this.pendingMode = 'match';   // modo que se aplicará al entrar en VR
    this.pendingAR = false;       // próxima sesión en passthrough (immersive-ar)
    this.inAR = false;            // sesión actual ES passthrough
    this.adaptive = true;         // IA adaptativa según el marcador
    this.survivalRallies = 0;     // rallyes completados en la sesión actual
    try {
      this.survivalBest = Math.max(0, parseInt(localStorage.getItem('ppxr_surv_best') || '0', 10) || 0);
    } catch { this.survivalBest = 0; }
    this.stats = new GameStats();  // victorias, rachas y logros persistentes
    this.confettiBurst = 0;        // ráfaga de confeti al desbloquear logros
    this.events = [];
    this.lastTime = -1;
    this.orbitAngle = 0.7;
    this.recenterFrames = 0;
    this.aiServeTimer = 1.3;
    this.demoServeTimer = 1.2;
    // saque del jugador: bola en la mano libre -> lanzamiento físico
    this.tossed = false;
    this.tossTimer = 0;
    this.tossReleaseY = 0;
    this.tossMaxY = 0;
    this.preVy = 0;
    this.apexSignaled = false;
    this.apexPulse = 0;
    this.aiToss = null;
    this.demoToss = null;
    // saque de la IA / demo: posición reglamentaria fija + postura lateral
    this.aiServeSpot = new THREE.Vector3();
    this.aiServeStance = new THREE.Vector3();
    this.demoServeSpot = new THREE.Vector3();
    this.demoServeStance = new THREE.Vector3();
    this.aiServeWait = 0;
    this.demoServeWait = 0;
    this.aiStrikeT = 0;
    this.demoStrikeT = 0;

    this.buildScene(paddleModel);
    this.setupControllers();
    this.buildMenu();
    // tema de sala persistente (v2.14): aplica antes del primer render
    this.theme = this.loadTheme();
    this.applyTheme(this.theme);
    this.rules.startMatch();
    this.setupAIServe();
    this.setupDemoServe();
    this.emitGrips();   // poblar el selector de agarres del menú

    window.addEventListener('resize', this.onResize);
    this.renderer.xr.addEventListener('sessionstart', this.onSessionStart);
    this.renderer.xr.addEventListener('sessionend', this.onSessionEnd);
    this.renderer.setAnimationLoop(this.animate);
    window.__pingpong = this;
  }

  // ---------- Construcción ----------

  buildScene(paddleModel) {
    // Luz cálida de pabellón (v2.11): hemisférica ámbar + direccional suave
    // (refs guardadas: los TEMAS DE SALA v2.14 las recolorean en vivo)
    const hemi = new THREE.HemisphereLight(0xffe6c4, 0x35271b, 0.95);
    this.rig.add(hemi);
    this.hemi = hemi;

    const dir = new THREE.DirectionalLight(0xfff1dc, 2.4);
    this.dirLight = dir;
    dir.position.set(2.2, 3.6, 0.6);
    dir.castShadow = true;
    dir.shadow.mapSize.set(2048, 2048);
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

    // focos cálidos sobre la mesa (ambiente de torneo)
    this.spots = [];
    for (const px of [-1.15, 1.15]) {
      const spot = new THREE.PointLight(0xffe2b8, 0.5, 6.5, 1.6);
      spot.position.set(px, 2.65, DIMS.tableCenterZ + 0.7);
      this.rig.add(spot);
      this.spots.push(spot);
    }

    // La sala guarda referencia: en passthrough (immersive-ar) se oculta
    this.roomGroup = createRoom();
    this.rig.add(this.roomGroup);
    this.rig.add(createTable());

    // receptor de sombras para passthrough (sombra de mesa/bola sobre el suelo real)
    this.shadowCatcher = new THREE.Mesh(
      new THREE.PlaneGeometry(7, 9),
      new THREE.ShadowMaterial({ opacity: 0.32 }),
    );
    this.shadowCatcher.rotation.x = -Math.PI / 2;
    this.shadowCatcher.position.set(0, 0.001, (DIMS.roomBackZ + DIMS.roomFrontZ) / 2);
    this.shadowCatcher.receiveShadow = true;
    this.shadowCatcher.visible = false;
    this.rig.add(this.shadowCatcher);

    const { mesh, trail, trailUpdate } = createBall();
    this.ballMesh = mesh;
    this.trailUpdate = trailUpdate;
    this.trailObj = trail;
    trail.visible = this.showTrail !== false;   // v2.18: interruptor de estela
    this.ballMesh.position.copy(this.ball.pos);
    this.rig.add(mesh);
    this.rig.add(trail);

    this.blob = createBlobShadow();
    this.rig.add(this.blob);
    this.markers = createBounceMarkers();
    this.markerIdx = 0;
    for (const m of this.markers) this.rig.add(m);

    // Pala de la IA y del jugador demo: modelo GLB con la hoja en el origen.
    // Sin cuerpos: solo la pala flotante del rival (más limpio y no estorba).
    this.aiPaddleMesh = makePaddleVisual(paddleModel, 'center');
    this.rig.add(this.aiPaddleMesh);

    this.demoPaddleMesh = makePaddleVisual(paddleModel, 'center');
    this.rig.add(this.demoPaddleMesh);

    const sb = createScoreboard();
    this.scoreboardUpdate = sb.update;
    this.rig.add(sb.group);

    // Panel de ajuste de pala (visible solo en el modo entrenamiento).
    // Fuera de la mesa a la IZQUIERDA (el borde de la mesa está en x=-0.76):
    // el panel de 0,46 m girado 0,62 rad llega hasta x=-0,85, sin solapar.
    this.calibPanel = createCalibPanel();
    this.calibPanel.group.position.set(
      -1.04, 1.42, DIMS.tableCenterZ + DIMS.tableHalfLength - 0.02,
    );
    this.calibPanel.group.rotation.y = 0.62;
    this.calibPanel.group.visible = false;
    this.rig.add(this.calibPanel.group);

    // Banner de fin de partido (¡VICTORIA! / DERROTA) + confeti 3D
    this.fanfareBanner = createFanfareBanner();
    this.rig.add(this.fanfareBanner.group);
    this.confetti = createConfetti();
    this.rig.add(this.confetti.points);
    // Mini-indicador del estado del audio (bajo el marcador): si el audio
    // fallara en VR, el propio casco muestra "reconectando / pulsa gatillo".
    this.audioStatus = createAudioStatus();
    this.rig.add(this.audioStatus.group);
  }

  setupControllers() {
    this.paddleMounts = [];
    this.grips = [];
    this.rays = [];          // espacios targetRay (el menú apunta con uno)
    for (let i = 0; i < 2; i++) {
      const grip = this.renderer.xr.getControllerGrip(i);
      const targetRay = this.renderer.xr.getController(i);

      // pala (solo visible en el mando activo). Sin desplazamiento: el punto
      // de agarre de la pala coincide EXACTAMENTE con el del mando y la hoja
      // sigue la dirección del mango (colisionador y visual alineados).
      const mount = new THREE.Group();
      mount.quaternion.copy(MOUNT_QUAT_RIGHT);
      mount.position.set(0, 0, 0);
      mount.add(makePaddleVisual(this.paddleModelRef, 'grip'));
      mount.visible = i === this.paddleHand;
      grip.add(mount);
      this.paddleMounts.push(mount);

      grip.addEventListener('connected', (e) => {
        this.connected[i] = true;
        this.sources[i] = e.data;
        this.handOf[i] = e.data.handedness === 'left' ? 'left' : 'right';
        this.applyGripOffset();
        if (e.data.handedness === 'right' && !this.manualHand) this.setPaddleHand(i);
        else if (!this.connected[this.paddleHand]) this.setPaddleHand(i);
      });
      grip.addEventListener('disconnected', () => {
        this.connected[i] = false;
        this.sources[i] = null;
      });

      // v2.24: UN SOLO listener por evento. Antes 'selectstart' estaba en
      // grip Y targetRay (y el squeeze en ambos): three.js despacha el evento
      // de sesión a todos los espacios del mando, así que cada pulsación
      // entraba DOS veces → toggles sin efecto y letras duplicadas.
      const onSelect = () => this.onSelectStart(i);
      targetRay.addEventListener('selectstart', onSelect);
      const onSqueezeStart = () => {
        this.audio.kick();       // el grip también reactiva el audio en VR
        this.gripDown[i] = true;
      };
      const onSqueezeEnd = () => {
        if (this.gripDown[i]) this.releaseBallHand(i);
        this.gripDown[i] = false;
      };
      grip.addEventListener('squeezestart', onSqueezeStart);
      grip.addEventListener('squeezeend', onSqueezeEnd);

      this.rig.add(grip);
      this.rig.add(targetRay);
      this.grips.push(grip);
      this.rays.push(targetRay);
    }
  }

  setPaddleHand(i) {
    if (i === this.paddleHand) return;
    this.paddleHand = i;
    for (let k = 0; k < 2; k++) {
      if (this.paddleMounts[k]) this.paddleMounts[k].visible = k === this.paddleHand;
      const ps = this.controllerPaddles[k];
      ps.prev.copy(ps.pos);
      ps.vel.set(0, 0, 0);
      ps.omega.set(0, 0, 0);
      ps.velBuf.length = 0;
      ps.quatInit = false;
      ps.prevT = -1;
    }
  }

  get ballHand() { return 1 - this.paddleHand; }

  // ---------- Agarres guardados y modo entrenamiento ----------

  loadGripsStore() {
    try { return JSON.parse(localStorage.getItem('ppxr_grips_v1') || '{}') || {}; }
    catch { return {}; }
  }
  saveGripsStore(store) {
    try { localStorage.setItem('ppxr_grips_v1', JSON.stringify(store)); } catch { /* sin storage */ }
  }
  gripList() { return Object.keys(this.loadGripsStore()); }
  emitGrips() { this.callbacks.onGrips?.(this.gripList(), this.gripName); }

  /** Aplica el offset de agarre a la montura (visual) y a la base física. */
  applyGripOffset(off = this.gripOffset) {
    this.gripOffset = off;
    this.gripOffsetQ.setFromEuler(new THREE.Euler(off.rx, off.ry, off.rz, 'XYZ'));
    for (let i = 0; i < 2; i++) {
      const m = this.paddleMounts[i];
      if (m) {
        m.quaternion.copy(mountQuatFor(this.handOf[i])).multiply(this.gripOffsetQ);
        m.position.set(off.px, off.py, off.pz);
      }
    }
    for (const ps of this.controllerPaddles) {
      ps.quatInit = false;
      ps.velBuf.length = 0;
    }
    this.panelDirty = true;
  }

  saveCurrentGrip(name) {
    const store = this.loadGripsStore();
    const clean = (name || '').trim() || ('Agarre ' + (Object.keys(store).length + 1));
    store[clean] = { ...this.gripOffset };
    this.saveGripsStore(store);
    this.gripName = clean;
    this.panelDirty = true;
    this.emitGrips();
    return clean;
  }
  loadGripByName(name) {
    const g = this.loadGripsStore()[name];
    if (!g) return false;
    this.applyGripOffset({ px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0, ...g });
    this.gripName = name;
    this.panelDirty = true;
    this.emitGrips();
    return true;
  }
  deleteGripByName(name) {
    const store = this.loadGripsStore();
    if (!store[name]) return;
    delete store[name];
    this.saveGripsStore(store);
    if (this.gripName === name) this.gripName = 'Natural';
    this.panelDirty = true;
    this.emitGrips();
  }
  cycleGripVR() {
    const names = this.gripList();
    if (!names.length) return;
    const i = Math.max(0, names.indexOf(this.gripName));
    this.loadGripByName(names[(i + 1) % names.length]);
    this.audio.serve();
  }
  resetGripNatural() {
    this.applyGripOffset({ px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0 });
    this.gripName = 'Natural';
    this.panelDirty = true;
    this.emitGrips();
  }

  handIndex(hand) { return this.handOf[0] === hand ? 0 : 1; }
  readButton(i, b) {
    const gp = this.sources[i]?.gamepad;
    const pressed = !!gp?.buttons?.[b]?.pressed;
    const key = i + ':' + b;
    const edge = pressed && !this.btnPrev[key];
    this.btnPrev[key] = pressed;
    return edge;
  }
  stickAxis(i) {
    const gp = this.sources[i]?.gamepad;
    if (!gp || !gp.axes || gp.axes.length < 4) return { x: 0, y: 0 };
    return { x: gp.axes[2] || 0, y: gp.axes[3] || 0 };
  }

  enterCalib() {
    this.calib = true;
    this.closeMenu();            // el entrenamiento tiene su propio panel
    this.preCalibMode = this.mode;   // recordar el modo actual para volver a él
    this.calibPanel.group.visible = true;
    this.panelDirty = true;
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.feedTimer = 1.1;
    this.feedIdle = 0;
    this.haptic(this.paddleHand, 0.5);
  }
  exitCalib() {
    this.calib = false;
    this.calibPanel.group.visible = false;
    // Volver al modo en el que estábamos antes de entrenar (partido o
    // supervivencia) — antes siempre se caía a un partido nuevo, perdiendo
    // la sesión de supervivencia en curso.
    const back = this.preCalibMode === 'survival' ? 'survival' : 'match';
    this.preCalibMode = 'match';
    this.mode = back;
    this.rules.startMatch(back);
    this.applyAISkill();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.ai.reset();
    this.setupAIServe();
    this.setupDemoServe();
    this.haptic(this.paddleHand, 0.4);
  }

  /** CAMBIO DE MODO EN VR (botón B del mando derecho): Partido ⇄ Supervivencia
 *  sin salir de la sesión. Reinicia el encuentro en el nuevo modo, reancla la
 *  IA y anuncia el cambio por megafonía. En entrenamiento no actúa: allí B
 *  recorre los agarres guardados. */
  switchMode(mode) {
    if (this.calib || this.mode === mode) return;
    this.mode = mode;
    this.survivalRallies = 0;
    this.rules.startMatch(mode);
    this.applyAISkill();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.ai.reset();
    this.setupAIServe();
    this.setupDemoServe();
    this.audio.announce(mode === 'survival'
      ? T('mode_survival')
      : T('mode_match'), true);
    this.haptic(this.paddleHand, 0.6, 130);
  }

  /* ---------- v2.19 · SESIÓN ONLINE (PeerJS P2P) ----------
   * El anfitrión lleva las reglas y el marcador; el invitado recibe el
   * estado por red (reglas sombra). Cada lado simula la bola cuando es su
   * dueño (último golpeador / sacador) y la emite a 20 Hz. */
  startOnlineSession() {
    if (this.calib) this.exitCalib();
    this.closeMenu();
    this.rules.oppLabel = 'rival';   // v2.27: clave (T('opp_rival'))
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.audio.announce(T('opp_connected'), true);
    if (this.net.role === 'host') {
      this.startOnlineMatch();
    } else {
      // v2.25: el primer saque es del anfitrión — el estado sombra del
      // invitado arranca ya en perspectiva correcta (antes el primer paquete
      // de sync tardaba ~50 ms y el invitado veía un "tu saque" falso)
      this.rules.server = 'ai';
      this.rules.message = T('online_first');
    }
  }

  /** Partido online nuevo (anfitrión, o revancha pedida por el invitado). */
  startOnlineMatch() {
    if (this.net.role !== 'host') { this.net.sendRematch(); return; }
    this.rules.startMatch(this.mode);
    this.net.owner = 'host';
    this.resetToss();
    this.rules.message = T('online_serve');
  }

  /** El rival se desconecta: vuelta al juego local contra la CPU. */
  onNetEnded(msg) {
    this.rules.oppLabel = 'cpu';
    this.resetToss();
    this.aiToss = null;
    this.rules.startMatch(this.mode);
    this.rules.message = T('net_ended', { msg: msg || T('opp_disconnected') });
    this.audio.announce(T('opp_disconnected'), true);
  }

  /** El estado de la red cambió (repinta el menú si está abierto). */
  onNetStatus() {
    if (this.menuOpen) this.drawMenu();
  }

  /** Máquina de bolas: saque reglamentario (bote propio + bote rival) hacia
   *  el campo del jugador, para entrenar golpes con el agarre ajustado. */
  feedPracticeBall() {
    this.feedTimer = 2.2 + Math.random() * 1.5;
    this.feedIdle = 0;
    this.resetToss();
    this.ball.pos.set(
      (Math.random() * 2 - 1) * 0.15,
      1.02,
      DIMS.tableCenterZ - DIMS.tableHalfLength - 0.28,
    );
    const { v, spin } = findServeVelocity(this.ball.pos, -1);
    this.ball.vel.copy(v);
    this.ball.spin.copy(spin);
    this.audio.serve();
  }

  updateCalibration(dt) {
    const Li = this.handIndex('left');
    const Ri = this.handIndex('right');
    const L = this.stickAxis(Li);
    const R = this.stickAxis(Ri);
    const gripL = !!this.sources[Li]?.gamepad?.buttons?.[1]?.pressed;
    const gripR = !!this.sources[Ri]?.gamepad?.buttons?.[1]?.pressed;
    const dz = (v) => (Math.abs(v) < 0.16 ? 0 : v);
    const adj = (cur, delta) => Math.max(-1.2, Math.min(1.2, cur + delta));
    const off = this.gripOffset;
    const rot = 1.1 * dt;
    const pos = 0.13 * dt;
    let moved = false;
    if (dz(R.x)) { off.ry = adj(off.ry, dz(R.x) * rot); moved = true; }
    if (dz(R.y)) { off.rx = adj(off.rx, -dz(R.y) * rot); moved = true; }
    if (gripR && dz(R.x)) { off.rz = adj(off.rz, dz(R.x) * rot); moved = true; }
    if (dz(L.x)) { off.px = adj(off.px, dz(L.x) * pos); moved = true; }
    if (dz(L.y)) { off.py = adj(off.py, -dz(L.y) * pos); moved = true; }
    if (gripL && dz(L.y)) { off.pz = adj(off.pz, -dz(L.y) * pos); moved = true; }
    if (moved) this.applyGripOffset();

    if (this.readButton(Ri, 4)) {                       // A: guardar
      this.saveCurrentGrip(this.gripName === 'Natural' ? '' : this.gripName);
      this.audio.point(true);
    }
    if (this.readButton(Ri, 5)) this.cycleGripVR();     // B: siguiente agarre
    if (this.readButton(Li, 4)) this.resetGripNatural(); // X: agarre natural

    // máquina de bolas: alimenta cuando la bola está muerta o por tiempo
    this.feedTimer -= dt;
    const b = this.ball;
    const restingFloor = b.pos.y < DIMS.ballRadius + 0.04 && Math.abs(b.vel.y) < 0.6;
    const onTable = Math.abs(b.pos.x) < DIMS.tableHalfWidth + 0.05 &&
      Math.abs(b.pos.z - DIMS.tableCenterZ) < DIMS.tableHalfLength + 0.05;
    const restingTable = onTable && b.pos.y < DIMS.tableTopY + 0.06 && b.vel.length() < 0.45;
    this.feedIdle = (restingFloor || restingTable) ? this.feedIdle + dt : 0;
    if (this.feedIdle > 0.8 || this.feedTimer <= 0) this.feedPracticeBall();
  }

  // ---------- API pública ----------

  async enterVR(startCalib = false, useAR = false, mode = 'match') {
    // Preparación de audio DENTRO de este clic (gesto de usuario): repara un
    // contexto enfermo (suspendido/cerrado) recreándolo, pero NO destruye un
    // contexto sano. Si la sesión XR lo suspende, el kick() recreativo de los
    // gatillos/grips lo recupera dentro del propio gesto del mando.
    this.audio.prepareVR();
    this.pendingCalib = !!startCalib;
    this.pendingAR = !!useAR;
    this.pendingMode = mode === 'survival' ? 'survival' : 'match';
    const xr = navigator.xr;
    if (!xr) throw new Error('Este navegador no soporta WebXR. Usa Meta Quest Browser.');
    const session = await xr.requestSession(
      useAR ? 'immersive-ar' : 'immersive-vr',
      { optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking', 'dom-overlay'] },
    );
    await this.renderer.xr.setSession(session);
  }

  setDifficulty(d) {
    this.difficulty = d;
    this.applyAISkill();
  }

  // ---------- Temas de sala (v2.14) ----------

  loadTheme() {
    try {
      const k = localStorage.getItem('ppxr_theme');
      if (k && ROOM_THEMES.some((t) => t.key === k)) return k;
    } catch { /* almacenamiento no disponible */ }
    return 'pabellon';
  }

  /** Cambia el tema visual de la sala. silent=true (overlay 2D) aplica sin
   *  megafonía; el flick en VR anuncia y vibra. Persiste en localStorage. */
  setTheme(key, silent = false) {
    const t = ROOM_THEMES.find((x) => x.key === key);
    if (!t || key === this.theme) return;
    this.theme = key;
    try { localStorage.setItem('ppxr_theme', key); } catch { /* */ }
    this.applyTheme(key);
    this.callbacks.onTheme?.(key);
    if (!silent) {
      const roomName = t.nameKey ? T(t.nameKey) : t.name;
      this.rules.message = T('msg_room', { r: roomName.toUpperCase() });
      this.audio.announce(T('ann_room', { room: roomName }), true);
      if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.5, 90);
    }
  }

  cycleTheme(dir) {
    const i = ROOM_THEMES.findIndex((t) => t.key === this.theme);
    const next = ROOM_THEMES[(i + dir + ROOM_THEMES.length) % ROOM_THEMES.length];
    this.setTheme(next.key);
  }

  /** Recolorea sala + luces + fondo/niebla con el tema dado. En passthrough
   *  (inAR) la sala está oculta y el fondo es null: solo toca las luces. */
  applyTheme(key) {
    const t = ROOM_THEMES.find((x) => x.key === key) || ROOM_THEMES[0];
    const ud = this.roomGroup?.userData;
    if (ud) {
      ud.floorMat?.color.set(t.floor);
      ud.wallMat?.color.set(t.wall);
      ud.ceilMat?.color.set(t.ceil);
      ud.panelMat?.color.set(t.panel);
      ud.stripMat?.color.set(t.strip);
      ud.ringMat?.color.set(t.ring);
      if (ud.grid) this.rebuildGrid(t);
    }
    if (this.hemi) {
      this.hemi.color.set(t.hemiSky);
      this.hemi.groundColor.set(t.hemiGround);
      this.hemi.intensity = t.hemiInt;
    }
    if (this.dirLight) {
      this.dirLight.color.set(t.dirCol);
      this.dirLight.intensity = t.dirInt;
    }
    for (const s of this.spots || []) {
      s.color.set(t.spotCol);
      s.intensity = t.spotInt;
    }
    this.scene.environmentIntensity = t.envInt;
    if (!this.inAR) {
      if (this.scene.background?.isColor) this.scene.background.set(t.bg);
      if (this.scene.fog) {
        this.scene.fog.color.set(t.bg);
        this.scene.fog.near = t.fogNear;
        this.scene.fog.far = t.fogFar;
      }
    }
  }

  /** La rejilla del suelo hornea sus colores en los vértices: se reemplaza. */
  rebuildGrid(t) {
    const ud = this.roomGroup.userData;
    const old = ud.grid;
    if (old) {
      this.roomGroup.remove(old);
      old.geometry?.dispose?.();
      old.material?.dispose?.();
    }
    const zC = (DIMS.roomBackZ + DIMS.roomFrontZ) / 2;
    const depth = DIMS.roomBackZ - DIMS.roomFrontZ;
    const grid = new THREE.GridHelper(
      Math.max(DIMS.roomHalfX * 2, depth), 20, t.gridC, t.gridG,
    );
    grid.position.set(0, 0.002, zC);
    this.roomGroup.add(grid);
    ud.grid = grid;
  }

  // ---------- MENÚ PRINCIPAL (v2.28) ----------
  // UN gran panel flotante DELANTE del jugador (antes: bandeja de muñeca).
  // Se abre SOLO al entrar en VR y con B (mando derecho). Cabecera con el
  // arte del juego + dos palas con bandera (selector de idioma); cuerpo en
  // ACORDEÓN: solo UNA sección desplegada cada vez (Jugar Partido /
  // Entrenar / Supervivencia / Crazy / Opciones). Se apunta con CUALQUIER
  // mando (la pala incluida) y se elige con el GATILLO.
  // v2.16: rayo, láser, cursor y hover INDEPENDIENTES por mando se mantienen.

  buildMenu() {
    this.menuGroup = new THREE.Group();
    this.menuCanvas = document.createElement('canvas');
    this.menuCanvas.width = 1024;
    this.menuCanvas.height = 1536;
    this.menuTex = new THREE.CanvasTexture(this.menuCanvas);
    this.menuTex.colorSpace = THREE.SRGBColorSpace;
    this.menuTex.anisotropy = 4;
    this.menuMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.72, 1.08),
      new THREE.MeshBasicMaterial({ map: this.menuTex, transparent: true, depthTest: false }),
    );
    this.menuMesh.renderOrder = 990;
    this.menuGroup.add(this.menuMesh);

    this.menuGroup.visible = false;
    this.scene.add(this.menuGroup);   // espacio MUNDO: inmune al recentrado

    // v2.28: arte de la cabecera + palas de idioma (data URLs; los PNG viven
    // en la portada 2D, de donde se leen las mismas imágenes)
    this.menuLogo = new Image();
    this.menuLogo.onload = () => { if (this.menuOpen) this.drawMenu(); };
    this.menuLogo.src = MENU_LOGO_SRC;
    this.padES = new Image();
    this.padES.onload = () => { if (this.menuOpen) this.drawMenu(); };
    this.padES.src = (document.getElementById('padEs') || {}).src || '';
    this.padEN = new Image();
    this.padEN.onload = () => { if (this.menuOpen) this.drawMenu(); };
    this.padEN.src = (document.getElementById('padEn') || {}).src || '';

    // UN HAZ LÁSER y UN cursor POR MANDO: cualquiera de los dos puede
    // apuntar (el de la pala incluido) y el hover es independiente por mano.
    // v2.17: cilindro fino en vez de THREE.Line — las líneas dibujan 1 px y
    // en el visor eran invisibles (por eso solo se veía el resaltado).
    const beamGeo = new THREE.CylinderGeometry(0.0022, 0.0022, 1, 8, 1, true);
    beamGeo.rotateX(Math.PI / 2);      // eje del cilindro -> Z
    beamGeo.translate(0, 0, -0.5);     // nace en el origen y crece hacia -Z
    this.menuLines = [];
    this.menuDots = [];
    for (let h = 0; h < 2; h++) {
      const beam = new THREE.Mesh(
        beamGeo,
        new THREE.MeshBasicMaterial({
          color: h === 0 ? 0xe8b45a : 0x7fd4e8,
          transparent: true, opacity: 0.85, depthTest: false,
        }),
      );
      beam.renderOrder = 940;          // sobre la escena, bajo el panel (990)
      beam.visible = false;
      beam.frustumCulled = false;
      this.scene.add(beam);
      this.menuLines.push(beam);

      const dot = new THREE.Mesh(
        new THREE.CircleGeometry(0.009, 24),
        new THREE.MeshBasicMaterial({
          color: h === 0 ? 0xe8b45a : 0x7fd4e8, depthTest: false, transparent: true, opacity: 0.95,
        }),
      );
      dot.renderOrder = 991;
      dot.visible = false;
      this.menuGroup.add(dot);
      this.menuDots.push(dot);
    }

    this.drawMenu();
  }


  /** Cabecera común de TODAS las páginas (v2.28): franja azul con el arte
   *  del juego a la izquierda y las DOS PALAS DE IDIOMA a la derecha. */
  drawMenuHeader(rects) {
    const c = this.menuCanvas.getContext('2d');
    const g = c.createLinearGradient(0, 16, 0, 198);
    g.addColorStop(0, '#1d5ad4');
    g.addColorStop(1, '#0c2e83');
    c.beginPath();
    if (c.roundRect) c.roundRect(16, 16, 992, 182, 24);
    else c.rect(16, 16, 992, 182);
    c.fillStyle = g;
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.55)';
    c.lineWidth = 2;
    c.stroke();
    // arte del juego (logo CRAZY PING PONG)
    if (this.menuLogo.complete && this.menuLogo.naturalWidth) {
      const lh = 152;
      const lw = lh * (this.menuLogo.naturalWidth / this.menuLogo.naturalHeight);
      c.drawImage(this.menuLogo, 44, 31, lw, lh);
    } else {
      c.fillStyle = '#f2f4f6';
      c.font = '800 46px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillText('CRAZY PING PONG', 48, 108);
    }
    this._langPaddle(rects, 'es', 746, 48);
    this._langPaddle(rects, 'en', 874, 48);
  }

  /** Pala-bandera del selector de idioma (v2.28): anillo dorado si activa. */
  _langPaddle(rects, lang, x, y) {
    const c = this.menuCanvas.getContext('2d');
    const img = lang === 'es' ? this.padES : this.padEN;
    const act = TLang() === lang;
    const hovered = this.menuHover.includes(rects.length);
    const S = 118;
    c.save();
    c.beginPath();
    c.arc(x + S / 2, y + S / 2, S / 2 - 2, 0, Math.PI * 2);
    c.closePath();
    c.fillStyle = 'rgba(255,255,255,0.12)';
    c.fill();
    c.strokeStyle = act ? '#ffd257' : 'rgba(255,255,255,0.4)';
    c.lineWidth = act ? 6 : 3;
    c.stroke();
    c.clip();
    if (img && img.complete && img.naturalWidth) {
      const k = Math.max(S / img.naturalWidth, S / img.naturalHeight) * 0.96;
      const w = img.naturalWidth * k;
      const h = img.naturalHeight * k;
      c.drawImage(img, x + (S - w) / 2, y + (S - h) / 2, w, h);
    } else {
      c.fillStyle = '#f2f4f6';
      c.font = '800 40px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(lang.toUpperCase(), x + S / 2, y + S / 2 + 4);
    }
    c.restore();
    if (hovered) {
      c.beginPath();
      c.arc(x + S / 2, y + S / 2, S / 2 + 4, 0, Math.PI * 2);
      c.closePath();
      c.strokeStyle = '#ffffff';
      c.lineWidth = 5;
      c.stroke();
    }
    rects.push({ x: x - 6, y: y - 6, w: S + 12, h: S + 12, id: 'lang:' + lang });
  }

  /** Página MULTIJUGADOR: crear/unirse por código, estado y voz (v2.19;
   *  v2.28 reescala al panel grande 1024×1536). */
  drawMenuMulti(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const net = this.net;
    const st = net.online ? 'online' : net.status;

    this.drawMenuHeader(rects);
    label(T('mj_head'), 244, 26);

    if (st === 'online') {
      c.fillStyle = '#7fb069';
      c.font = '800 52px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('mj_connected'), 512, 336);
      c.fillStyle = '#cfd8e0';
      c.font = '600 28px system-ui, sans-serif';
      c.fillText(T('mj_rival', { code: net.code, st: this.rules.state === 'over' ? T('mj_over') : T('mj_playing') }), 512, 396);
      const voz = net.voiceState === 'on'
        ? (net.micOn ? T('voz_on_mic') : T('voz_on_silent'))
        : net.voiceState === 'asking' ? T('voz_asking')
        : net.voiceState === 'denied' ? T('voz_denied')
        : T('voz_off');
      c.fillStyle = '#9aa7b4';
      c.font = '500 24px system-ui, sans-serif';
      c.fillText(voz, 512, 440);
      btn('net:mic', 56, 486, 448, 76, T('btn_voz', { v: net.micOn ? T('yes') : T('no') }), net.micOn && net.voiceState === 'on', undefined, !!net.micOn, 26);
      btn('net:hangup', 520, 486, 448, 76, T('btn_hangup'), false, undefined, undefined, 26);
      c.fillStyle = '#9aa7b4';
      c.font = '500 22px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('mj_rematch_hint'), 512, 606);
    } else if (st === 'waiting') {
      c.fillStyle = '#e8b45a';
      c.font = '700 30px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('mj_room_code'), 512, 316);
      c.fillStyle = '#f2f4f6';
      c.font = '900 124px ui-monospace, monospace';
      c.fillText(net.code, 512, 420);
      c.fillStyle = '#9aa7b4';
      c.font = '500 24px system-ui, sans-serif';
      c.fillText(T('mj_waiting'), 512, 512);
      btn('net:cancel', 56, 566, 912, 76, T('btn_cancel_room'), false, undefined, undefined, 26);
    } else if (st === 'creating' || st === 'joining') {
      c.fillStyle = '#e8b45a';
      c.font = '700 34px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(st === 'creating' ? T('mj_creating') : T('mj_connecting', { code: net.code }), 512, 340);
      btn('net:cancel', 56, 420, 912, 76, T('btn_cancel'), false, undefined, undefined, 26);
    } else if (st === 'error') {
      c.fillStyle = '#ff6b57';
      c.font = '700 30px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      wrapText(c, net.statusMsg || T('mj_error'), 512, 330, 880, 42);
      btn('net:host', 56, 450, 448, 76, T('btn_retry'), false, undefined, undefined, 26);
      btn('net:cancel', 520, 450, 448, 76, T('btn_back'), false, undefined, undefined, 26);
    } else {
      // off
      c.fillStyle = '#cfd8e0';
      c.font = '600 28px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('mj_off_hint'), 512, 316);
      btn('net:host', 56, 366, 912, 86, T('btn_host'), false, 'green', undefined, 27);
      btn('net:join', 56, 472, 912, 86, T('btn_join'), false, undefined, undefined, 27);
    }

    c.fillStyle = '#75828f';
    c.font = '500 21px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('mj_p2p'), 512, 640);
    c.fillText(T('mj_mic_hint'), 512, 678);
    btn('tab:main', 56, 1380, 912, 76, '◀  ' + T('btn_back'), false, undefined, undefined, 28);
  }

  /** Página JOIN: teclado en el panel para escribir el código (v2.19;
   *  v2.28 reescala al panel grande 1024×1536). */
  drawMenuJoin(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // sin 0/O/1/I/L

    this.drawMenuHeader(rects);
    label(T('join_title'), 240, 26);

    // 5 huecos del código
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    for (let i = 0; i < 5; i++) {
      const x = 56 + i * 186;
      c.beginPath();
      if (c.roundRect) c.roundRect(x, 268, 156, 112, 16);
      else c.rect(x, 268, 156, 112);
      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.fill();
      c.strokeStyle = i === this._joinCode.length ? '#e8b45a' : 'rgba(255,255,255,0.18)';
      c.lineWidth = i === this._joinCode.length ? 5 : 2;
      c.stroke();
      const ch = this._joinCode[i];
      if (ch) {
        c.fillStyle = '#f2f4f6';
        c.font = '800 68px ui-monospace, monospace';
        c.fillText(ch, x + 78, 324);
      }
    }

    // teclado 7×5
    for (let i = 0; i < CHARS.length; i++) {
      const col = i % 7, row = Math.floor(i / 7);
      btn(`key:${CHARS[i]}`, 56 + col * 128, 430 + row * 96, 118, 86, CHARS[i], false, undefined, undefined, 34);
    }
    btn('key:del', 56 + 4 * 128, 430 + 4 * 96, 118, 86, '⌫', false, undefined, undefined, 34);
    btn('key:ok', 56, 940, 448, 82, T('btn_connect'), this._joinCode.length === 5, 'green', undefined, 28);
    btn('key:cancel', 520, 940, 448, 82, T('btn_back'), false, undefined, undefined, 28);
    btn('tab:main', 56, 1380, 912, 76, '◀  ' + T('btn_back'), false, undefined, undefined, 28);
  }

  /** Pinta el panel y deja en menuRects las zonas clicables (px canvas).
   *  v2.28: página principal en ACORDEÓN — las secciones se contraen y solo
   *  se despliega la que se selecciona (menuSec). */
  drawMenu() {
    const c = this.menuCanvas.getContext('2d');
    if (!c) return;
    const W = 1024, H = 1536;
    const rects = [];
    const over = this.rules.state === 'over';

    const rr = (x, y, w, h, r) => {
      c.beginPath();
      c.moveTo(x + r, y);
      c.arcTo(x + w, y, x + w, y + h, r);
      c.arcTo(x + w, y + h, x, y + h, r);
      c.arcTo(x, y + h, x, y, r);
      c.arcTo(x, y, x + w, y, r);
      c.closePath();
    };

    // tarjeta
    c.clearRect(0, 0, W, H);
    rr(8, 8, W - 16, H - 16, 36);
    c.fillStyle = 'rgba(10,13,20,0.95)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.6)';
    c.lineWidth = 4;
    c.stroke();

    // botón genérico (compartido por todas las páginas)
    // v2.23: activos responden al apuntado, casilla ☑/☐ explícita y zona
    // táctil más grande que el dibujo. v2.28: fuentes grandes (fsize) para
    // el panel grande.
    const btn = (id, x, y, w, h, label2, active, style, check, fsize) => {
      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 14);
      if (active) {
        c.fillStyle = style === 'green'
          ? (hovered ? '#93c97e' : '#7fb069')
          : style === 'surv'
            ? (hovered ? '#ffa25e' : '#f0873f')
            : (hovered ? '#f4ca79' : '#e8b45a');
        c.fill();
        if (hovered) {
          c.strokeStyle = '#ffffff';
          c.lineWidth = 4;
          c.stroke();
        }
        c.fillStyle = style === 'surv' ? '#1a1006' : '#10131a';
      } else {
        c.fillStyle = 'rgba(255,255,255,0.07)';
        c.fill();
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.18)';
        c.lineWidth = hovered ? 4 : 2;
        if (style === 'green') c.strokeStyle = hovered ? '#bfe3a9' : 'rgba(127,176,105,0.55)';
        if (style === 'surv') c.strokeStyle = hovered ? '#ffc09a' : 'rgba(240,135,63,0.55)';
        c.stroke();
        c.fillStyle = style === 'green' ? '#bfe3a9'
          : style === 'surv' ? '#ffc09a' : '#cfd8e0';
      }
      c.font = `700 ${fsize || 26}px system-ui, sans-serif`;
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      let tx = x + w / 2;
      if (check !== undefined) {
        const bs = 13, bx = x + 26, by = y + h / 2;
        c.lineWidth = 3;
        if (check) {
          c.fillStyle = active ? 'rgba(16,19,26,0.88)' : 'rgba(207,216,224,0.92)';
          c.fillRect(bx - bs, by - bs, bs * 2, bs * 2);
          c.strokeStyle = active ? '#e8b45a' : '#10131a';
          c.beginPath();
          c.moveTo(bx - 7, by + 1);
          c.lineTo(bx - 2, by + 6);
          c.lineTo(bx + 7.5, by - 6);
          c.stroke();
        } else {
          c.strokeStyle = active ? 'rgba(16,19,26,0.8)' : 'rgba(255,255,255,0.55)';
          c.strokeRect(bx - bs, by - bs, bs * 2, bs * 2);
        }
        tx += 18;
      }
      c.fillText(label2, tx, y + h / 2 + 1);
      rects.push({ x: x - 5, y: y - 3, w: w + 10, h: h + 6, id });
    };
    this._menuBtn = btn;
    this._menuRects = rects;
    const label = (txt, y, size = 24, col = '#9aa7b4', align = 'left') => {
      c.fillStyle = col;
      c.font = `700 ${size}px system-ui, sans-serif`;
      c.textAlign = align;
      c.textBaseline = 'middle';
      c.fillText(txt, align === 'center' ? 512 : 56, y);
    };
    this._menuLabel = label;

    if (this.menuPage === 'multi') {
      this.drawMenuMulti(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    if (this.menuPage === 'join') {
      this.drawMenuJoin(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }

    this.drawMenuHeader(rects);

    // ---------- ACORDEÓN (v2.28) ----------
    // Encabezados SIEMPRE visibles; solo la sección elegida (menuSec)
    // despliega su contenido. Pulsar su cabecera la abre (o la cierra si ya
    // estaba abierta) y CONTRAE las demás.
    const diffName = { easy: T('diff_easy_btn'), medium: T('diff_medium_btn'), hard: T('diff_hard_btn') }[this.difficulty] || '';
    const themeDef = ROOM_THEMES.find((t) => t.key === this.theme);
    const themeName = themeDef ? (themeDef.nameKey ? T(themeDef.nameKey) : themeDef.name) : '';
    const SECS = [
      ['match', T('sec_match'), this.net.online ? T('tab_multi') : diffName],
      ['train', T('sec_train'), ''],
      ['surv', T('sec_surv'), this.survivalBest > 0 ? T('best_surv', { n: this.survivalBest }) : ''],
      ['crazy', T('sec_crazy'), ''],
      ['opts', T('sec_opts'), themeName],
    ];
    let y = 232;
    for (const [key, title, hint] of SECS) {
      const open = this.menuSec === key;
      const hov = this.menuHover.includes(rects.length);
      rr(40, y, 944, 86, 20);
      c.fillStyle = open
        ? (hov ? 'rgba(232,180,90,0.30)' : 'rgba(232,180,90,0.16)')
        : (hov ? 'rgba(255,255,255,0.13)' : 'rgba(255,255,255,0.06)');
      c.fill();
      c.strokeStyle = open ? 'rgba(232,180,90,0.85)'
        : hov ? '#ffffff' : 'rgba(255,255,255,0.2)';
      c.lineWidth = open ? 4 : hov ? 4 : 2;
      c.stroke();
      c.fillStyle = open ? '#ffd257' : '#f2f4f6';
      c.font = '800 30px system-ui, sans-serif';
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillText(title, 68, y + 44);
      if (hint) {
        c.fillStyle = open ? 'rgba(255,210,87,0.75)' : '#75828f';
        c.font = '600 22px system-ui, sans-serif';
        c.textAlign = 'right';
        c.fillText(hint.length > 22 ? hint.slice(0, 21) + '…' : hint, 908, y + 44);
      }
      // chevron ▸ / ▾
      c.fillStyle = '#e8b45a';
      c.beginPath();
      if (open) {
        c.moveTo(930, y + 38);
        c.lineTo(950, y + 38);
        c.lineTo(940, y + 52);
      } else {
        c.moveTo(934, y + 34);
        c.lineTo(948, y + 44);
        c.lineTo(934, y + 54);
      }
      c.closePath();
      c.fill();
      rects.push({ x: 40, y: y - 3, w: 944, h: 92, id: 'sec:' + key });
      y += 86 + 10;

      if (!open) continue;

      // ---- contenido de la sección desplegada ----
      if (key === 'match') {
        if (over) {
          btn('revancha', 56, y, 912, 70, T('btn_rematch'), false, 'green', undefined, 30);
          y += 82;
        }
        btn('start', 56, y, 912, 86, T('btn_start'), false, 'green', undefined, 33);
        y += 98;
        label(T('diff_label'), y + 14, 22);
        y += 34;
        btn('diff:easy', 56, y, 292, 58, T('diff_easy_btn'), this.difficulty === 'easy', undefined, undefined, 24);
        btn('diff:medium', 360, y, 292, 58, T('diff_medium_btn'), this.difficulty === 'medium', undefined, undefined, 24);
        btn('diff:hard', 664, y, 292, 58, T('diff_hard_btn'), this.difficulty === 'hard', undefined, undefined, 24);
        y += 72;
        label(T('online_lbl'), y + 14, 22);
        y += 34;
        const st = this.net.online ? 'online' : this.net.status;
        if (st === 'off') {
          btn('net:host', 56, y, 912, 64, T('btn_host'), false, undefined, undefined, 25);
          y += 76;
          btn('net:join', 56, y, 912, 64, T('btn_join'), false, undefined, undefined, 25);
          y += 76;
        } else if (st === 'waiting') {
          label(`${T('mj_room_code')}: ${this.net.code} · ${T('mj_waiting')}`, y + 16, 24, '#e8b45a');
          y += 42;
          btn('net:cancel', 56, y, 912, 60, T('btn_cancel_room'), false, undefined, undefined, 24);
          y += 72;
        } else if (st === 'creating' || st === 'joining') {
          label(st === 'creating' ? T('mj_creating') : T('mj_connecting', { code: this.net.code }), y + 16, 24, '#e8b45a');
          y += 42;
          btn('net:cancel', 56, y, 912, 60, T('btn_cancel'), false, undefined, undefined, 24);
          y += 72;
        } else if (st === 'error') {
          label(this.net.statusMsg || T('mj_error'), y + 16, 24, '#ff6b57');
          y += 42;
          btn('net:host', 56, y, 448, 60, T('btn_retry'), false, undefined, undefined, 24);
          btn('net:cancel', 520, y, 448, 60, T('btn_back'), false, undefined, undefined, 24);
          y += 72;
        } else if (st === 'online') {
          btn('net:mic', 56, y, 448, 64, T('btn_voz', { v: this.net.micOn ? T('yes') : T('no') }), this.net.micOn && this.net.voiceState === 'on', undefined, !!this.net.micOn, 24);
          btn('net:hangup', 520, y, 448, 64, T('btn_hangup'), false, undefined, undefined, 24);
          y += 76;
        }
        // acceso a la página completa de multijugador (voz, código grande)
        btn('tab:multi', 56, y, 912, 60, T('tab_multi'), false, undefined, undefined, 24);
        y += 72;
      } else if (key === 'train') {
        btn('traingo', 56, y, 912, 86, T('btn_train_go'), false, 'green', undefined, 32);
        y += 100;
        c.fillStyle = '#9aa7b4';
        c.font = '500 23px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        wrapText(c, T('train_hint'), 512, y + 22, 860, 32);
        y += 76;
      } else if (key === 'surv') {
        btn('survgo', 56, y, 912, 86, T('btn_start_surv'), false, 'surv', undefined, 30);
        y += 100;
        c.fillStyle = '#9aa7b4';
        c.font = '500 23px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        wrapText(c, T('surv_hint'), 512, y + 22, 860, 32);
        y += 44;
        label(this.survivalBest > 0 ? T('best_surv', { n: this.survivalBest }) : '', y + 34, 24, '#f0873f', 'center');
        y += 60;
      } else if (key === 'crazy') {
        rr(56, y, 912, 128, 20);
        c.fillStyle = 'rgba(232,180,90,0.12)';
        c.fill();
        c.strokeStyle = 'rgba(232,180,90,0.5)';
        c.lineWidth = 2;
        c.setLineDash([14, 10]);
        c.stroke();
        c.setLineDash([]);
        c.fillStyle = '#ffd98a';
        c.font = '800 40px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText(T('crazy_msg'), 512, y + 64);
        y += 142;
      } else if (key === 'opts') {
        label(T('room_label'), y + 14, 22);
        y += 34;
        const themes = [
          ['theme:pabellon', T('theme_pabellon')], ['theme:neon', T('theme_neon')],
          ['theme:atardecer', T('theme_atardecer')], ['theme:artico', T('theme_artico')],
        ];
        themes.forEach(([id, name], i) => {
          btn(id, 56 + (i % 2) * 464, y + Math.floor(i / 2) * 70, 448, 60, name, this.theme === id.split(':')[1], undefined, undefined, 24);
        });
        y += 140;
        const yn = (v) => (v ? T('yes') : T('no'));
        btn('amb', 56, y, 912, 62, T('btn_amb', { v: yn(this.audio.ambience) }), !!this.audio.ambience, undefined, !!this.audio.ambience, 24);
        y += 74;
        btn('voz', 56, y, 912, 62, T('btn_mic', { v: yn(this.audio.voice) }), !!this.audio.voice, undefined, !!this.audio.voice, 24);
        y += 74;
        btn('trail', 56, y, 912, 62, T('btn_trail', { v: yn(this.showTrail) }), !!this.showTrail, undefined, !!this.showTrail, 24);
        y += 74;
      }
      y += 14;
    }

    // cierre inferior (siempre visible)
    btn('close', 56, 1392, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
    c.fillStyle = '#5c6672';
    c.font = '500 20px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('menu_hint'), 512, 1484);

    this.menuRects = rects;
    this._menuState = this.rules.state;
    this.menuTex.needsUpdate = true;
  }

  toggleMenu() {
    if (this.calib) return;   // en entrenamiento manda el panel propio
    this.menuOpen = !this.menuOpen;
    this.menuGroup.visible = this.menuOpen;
    for (const l of this.menuLines) l.visible = false;
    for (const d of this.menuDots) d.visible = false;
    this.menuHover = [-1, -1];
    if (this.menuOpen) {
      this.anchorMenu();          // v2.28: DELANTE del jugador, no en la muñeca
      this.rules.message = T('menu_open');
      this.drawMenu();
      this.audio.playOsc(660, 990, 0.07, 'sine', 0.15, 0);
      if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.4, 70);
    } else {
      this.audio.playOsc(990, 660, 0.06, 'sine', 0.1, 0);
    }
  }

  closeMenu() {
    if (this.menuOpen) this.toggleMenu();
  }

  /** v2.28: coloca el gran panel DELANTE de la cabeza (1,08 m), un poco por
   *  debajo de la línea de ojos, mirando a la cara. Durante ~1,8 s sigue
   *  suavemente a la cabeza (flotación) y después queda FIJO en el mundo. */
  anchorMenu() {
    this.camera.getWorldPosition(muHead);
    this.camera.getWorldQuaternion(muQ);
    muDir.set(0, 0, -1).applyQuaternion(muQ);
    muDir.y = 0;
    if (muDir.lengthSq() < 1e-6) muDir.set(0, 0, -1);
    muDir.normalize();
    this.menuGroup.position.copy(muHead).addScaledVector(muDir, 1.08);
    this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.05);
    this.menuGroup.lookAt(muHead);
    this._menuAnchorUntil = performance.now() / 1000 + 1.8;
  }

  /** Coloca el panel (flotación inicial) y hace el hit-test del rayo de
   *  apuntado DE CADA MANDO: la pala también puede seleccionar, cada mano
   *  tiene su láser y su hover (v2.16, se mantiene en v2.28). */
  updateMenu() {
    // flotación inicial: el panel acompaña a la cabeza antes de fijarse
    if ((performance.now() / 1000) < (this._menuAnchorUntil || 0)) this.anchorMenu();

    // estado del partido cambió (p.ej. fin) → repintar botones
    if (this.rules.state !== this._menuState) this.drawMenu();

    // --- rayo de apuntado INDEPENDIENTE por mando (ambos seleccionan)
    let dirty = false;
    for (let h = 0; h < 2; h++) {
      const ray = this.rays[h];
      const line = this.menuLines[h];
      const dot = this.menuDots[h];
      let idx = -1;
      if (ray && this.connected[h]) {
        ray.getWorldPosition(muGrip);
        ray.getWorldQuaternion(muQ);
        muDir.set(0, 0, -1).applyQuaternion(muQ);
        muRaycaster.set(muGrip, muDir);
        const hit = muRaycaster.intersectObject(this.menuMesh, false)[0] || null;

        // v2.24: se descartan intersecciones degeneradas (el mando tocando el
        // propio plano del panel, distancia ~0) para no pintar un cursor falso.
        if (hit && hit.uv && hit.distance > 0.02) {
          const px = hit.uv.x * 1024;
          const py = (1 - hit.uv.y) * 1536;
          idx = this.menuRects.findIndex((r) =>
            px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h);
          // cursor sobre el panel (uv -> plano 0.72×1.08). El eje Y del plano
          // es uv.y=1 ARRIBA (v2.24: nunca se pinta espejado en vertical).
          dot.visible = true;
          dot.position.set((hit.uv.x - 0.5) * 0.72, (hit.uv.y - 0.5) * 1.08, 0.004);
        } else {
          dot.visible = false;
        }

        line.visible = true;
        line.position.copy(muGrip);
        line.quaternion.copy(muQ);
        line.scale.z = hit ? hit.distance : 0.5;
        // el haz engorda al pasar sobre un botón (feedback extra)
        const thick = idx >= 0 ? 1.7 : 1;
        line.scale.x = thick;
        line.scale.y = thick;
      } else {
        line.visible = false;    // mando ausente: sin láser (no dejarlo congelado)
        dot.visible = false;
      }
      if (idx !== this.menuHover[h]) { this.menuHover[h] = idx; dirty = true; }
    }
    if (dirty) this.drawMenu();   // un solo repintado aunque ambas manos cambien
  }

  menuClick(idx) {
    const r = this.menuRects[idx];
    if (!r) return;
    const [ns, arg] = r.id.split(':');
    switch (ns) {
      case 'sec':
        // v2.28 ACORDEÓN: abrir la sección elegida y CONTRAER las demás
        // (pulsar de nuevo la abierta la contrae: todas cerradas)
        this.menuSec = this.menuSec === arg ? '' : arg;
        // CRAZY: al pulsarlo, directamente el mensaje (modo en desarrollo)
        if (arg === 'crazy' && this.menuSec === 'crazy') {
          this.rules.message = T('crazy_msg');
          this.audio.playOsc(880, 1320, 0.09, 'triangle', 0.14, 0);
          window.setTimeout(() => {
            if (!this.disposed) this.audio.playOsc(1100, 1660, 0.12, 'triangle', 0.12, 0);
          }, 110);
        } else {
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        }
        this.drawMenu();
        break;
      case 'start':
        // ARRANQUE RÁPIDO: partido contra la CPU (o revancha online)
        if (this.net.online) {
          this.startOnlineMatch();   // anfitrión reinicia; invitado pide revancha
        } else {
          if (this.mode !== 'match') this.switchMode('match');
          else { this.rules.startMatch('match'); this.resetToss(); }
        }
        this.closeMenu();
        break;
      case 'survgo':
        // SUPERVIVENCIA desde el menú (el invitado online lo pide por red)
        if (this.net.online) {
          if (this.net.role === 'guest') this.net.sendMode('survival');
          this.rules.message = T('msg_guest_mode');
          this.drawMenu();
          break;
        }
        if (this.mode !== 'survival') this.switchMode('survival');
        else { this.rules.startMatch('survival'); this.resetToss(); }
        this.closeMenu();
        break;
      case 'traingo':
        // ENTRENAR desde el menú: máquina de bolas + panel de agarre
        this.closeMenu();
        this.enterCalib();
        break;
      case 'lang':
        // v2.27: selector de idioma (palas con bandera en la cabecera) —
        // cambia textos, banco de voz del megáfono y cartel; persistente.
        if (arg === 'es' || arg === 'en') {
          setLang(arg, this);
          this.rules.message = '';
          this.syncDom();
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        }
        this.drawMenu();
        break;
      case 'tab':
        // v2.28: pestaña 'multi' abre la página completa; 'main' vuelve
        this.menuPage = arg === 'multi' ? 'multi' : 'main';
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      case 'net':
        if (arg === 'host') { this.menuPage = 'multi'; this.net.hostRoom(); }
        else if (arg === 'join') { this.menuPage = 'join'; this._joinCode = ''; }
        else if (arg === 'cancel') { this.net.cancel(); }
        else if (arg === 'hangup') { this.net.hangup(); }
        else if (arg === 'mic') { this.net.toggleMic(); if (!this.net.micStream) this.net.initVoice().catch(() => {}); }
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      case 'key':
        if (arg === 'del') this._joinCode = this._joinCode.slice(0, -1);
        else if (arg === 'ok') {
          if (this._joinCode.length === 5) {
            this.menuPage = 'multi';
            this.net.joinRoom(this._joinCode);
          }
        } else if (arg === 'cancel') { this.menuPage = 'multi'; }
        else if (this._joinCode.length < 5) this._joinCode += arg;
        this.drawMenu();
        break;
      case 'diff': {
        if (this.net.online) {
          this.rules.message = T('msg_no_cpu');
          this.drawMenu();
          break;
        }
        this.setDifficulty(arg);
        const lb = { easy: T('diff_easy_btn'), medium: T('diff_medium_btn'), hard: T('diff_hard_btn') }[arg] || arg;
        this.rules.message = T('msg_diff', { d: lb.toUpperCase() });
        this.audio.announce(T(arg === 'easy' ? 'diff_easy' : arg === 'medium' ? 'diff_medium' : 'diff_hard'), true);
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      }
      case 'theme':
        this.setTheme(arg);        // anuncia, vibra y pinta el mensaje
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      case 'amb':
        this.audio.setAmbience(!this.audio.ambience);   // v2.18: basculante
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      case 'trail': {
        // v2.18: mostrar/ocultar la estela de la bola (persistente)
        this.showTrail = !this.showTrail;
        try { localStorage.setItem('ppxr_trail_v1', this.showTrail ? '1' : '0'); } catch { /* */ }
        if (this.trailObj) this.trailObj.visible = this.showTrail;
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.rules.message = T('msg_trail', { v: this.showTrail ? T('yes') : T('no') });
        this.drawMenu();
        break;
      }
      case 'voz': {
        // v2.22: megáfono del marcador (narrador) sí/no, persistente e
        // independiente del ambiente de torneo
        this.audio.setVoice(!this.audio.voice);
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.rules.message = T('msg_mic', { v: this.audio.voice ? T('yes') : T('no') });
        this.drawMenu();
        break;
      }
      case 'revancha':
        this.closeMenu();
        if (this.net.online) this.startOnlineMatch();   // invitado: pide por red
        else {
          this.rules.startMatch(this.mode);
          this.resetToss();
        }
        break;
      case 'close':
        this.closeMenu();
        break;
    }
  }

  emitStats() {
    this.callbacks.onStats?.(this.stats.data);
  }

  /** Celebración de logro(s) desbloqueado(s): megafonía, confeti y vibración. */
  celebrate(keys) {
    if (!keys || !keys.length) return;
    for (const k of keys) {
      const d = ACHIEVEMENTS.find((a) => a.key === k);
      if (!d) continue;
      this.rules.message = `LOGRO · ${d.name}`;
      this.audio.announce(T('ann_ach', { name: d.name }), true);
    }
    this.confettiBurst = 2.4;
    if (this.renderer.xr.isPresenting) {
      this.haptic(this.paddleHand, 0.7, 100);
      window.setTimeout(() => this.haptic(this.paddleHand, 0.5, 120), 180);
    }
  }

  /** Nivel EFECTIVO de la CPU = preset base de la dificultad × habilidad:
   *  (1) IA ADAPTATIVA: si vas ganando, aprieta; si vas perdiendo, afloja
   *      (rallyes igualados); (2) SUPERVIVENCIA: acelera un 8% por rallye
   *      completado hasta doblar su velocidad. */
  applyAISkill() {
    const base = AI_PRESETS[this.difficulty] || AI_PRESETS.medium;
    let k = 1;
    if (this.adaptive) {
      const diff = this.rules.scorePlayer - this.rules.scoreAi;
      k += diff > 0 ? Math.min(diff, 6) * 0.055 : Math.max(diff, -6) * 0.05;
    }
    if (this.mode === 'survival') {
      k *= Math.min(2.1, 1 + this.survivalRallies * 0.08);
    }
    this.aiSkillK = THREE.MathUtils.clamp(k, 0.7, 2.2);
    this.ai.setConfig(scalePreset(base, this.aiSkillK));
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
    // ---- PASSTHROUGH (immersive-ar): ocultar sala virtual, fondo y niebla
    const session = this.renderer.xr.getSession?.();
    this.inAR = !!(session && session.environmentBlendMode &&
      session.environmentBlendMode !== 'opaque');
    if (this.inAR) {
      this._savedBg = this.scene.background;
      this._savedFog = this.scene.fog;
      this.scene.background = null;
      this.scene.fog = null;
      this.roomGroup.visible = false;
      this.shadowCatcher.visible = true;
    }
    // ---- modo de juego (normal / supervivencia)
    this.mode = this.pendingMode;
    this.survivalRallies = 0;
    this.rules.startMatch(this.mode);
    this.applyAISkill();
    // v2.28: el MENÚ PRINCIPAL recibe al jugador — gran panel flotante
    // delante con JUGAR PARTIDO ya desplegado: un gatillo y estás jugando.
    // El saque de la CPU queda congelado mientras el menú esté abierto.
    this.menuPage = 'main';
    this.menuSec = 'match';
    this.menuOpen = true;
    if (this.menuGroup) {
      this.menuGroup.visible = true;
      this.anchorMenu();
      this.drawMenu();
    }
    this.rules.message = T('menu_open');
    // RE-VINCULACIÓN al entrar en VR: el contexto creado en 2D puede perder la
    // salida al pasar a inmersivo. Se crea uno nuevo DENTRO de la sesión
    // (ligado a la salida activa del casco) y se adopta SOLO si arranca
    // 'running'; si no, se conserva el anterior (nunca queda peor).
    this.audio.xrActive = true;
    this.audio.rebind('entrada en VR: salida re-vinculada al casco');
    // Reintentos suaves: si el contexto nuevo nace suspendido, kick() reanuda
    // y el tardío prueba un contexto fresco (también adopta-solo-si-running).
    for (const t of [400, 1200, 2500]) window.setTimeout(() => this.audio.kick(), t);
    window.setTimeout(() => {
      if (this.audio.ctx?.state !== 'running') {
        this.audio.tryFreshRunning('reintento tardío en VR');
      }
    }, 3400);
    window.setTimeout(() => this.audio.serve(), 350);  // blip de confirmación
    console.info(
      '[Audio] estado en VR:', this.audio.ctx?.state,
      '· recreaciones:', this.audio.rebuilds,
    );
    // gatillo y grip DENTRO de la sesión son eventos de intención del usuario:
    // sirven para reactivar el audio si el navegador lo suspendió en VR
    if (session && !this.__audioHooks) {
      this.__audioHooks = true;
      const kickAudio = () => this.audio.kick();
      session.addEventListener('selectstart', kickAudio);
      session.addEventListener('squeezestart', kickAudio);
      session.addEventListener('inputsourceschange', kickAudio);
    }
    // AMBIENTE DE TORNEO: murmullo del público + megafonía de bienvenida
    window.setTimeout(() => this.audio.startMurmur(), 900);
    window.setTimeout(() => {
      this.audio.announce(this.mode === 'survival'
        ? T('mode_survival')
        : T('welcome'), true);
    }, 1400);
    this.hapticProbe();
    this.ai.reset();
    this.demoAI.reset();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.setupAIServe();
    this.setupDemoServe();
    this.callbacks.onXRState?.(true);
    if (this.pendingCalib) {
      this.pendingCalib = false;
      this.enterCalib();
    }
  };

  onSessionEnd = () => {
    // Salida de VR: re-vincular el audio a la salida 2D del navegador
    // (adoptar-solo-si-running; el contexto del casco se cierra tras el cambio).
    this.audio.xrActive = false;
    this.audio.rebind('salida de VR: salida re-vinculada al navegador');
    // fin del ambiente de torneo
    this.audio.stopMurmur();
    try { window.speechSynthesis?.cancel(); } catch { /* */ }
    // restaurar la sala virtual si la sesión fue passthrough
    if (this.inAR) {
      this.scene.background = this._savedBg;
      this.scene.fog = this._savedFog;
      this.roomGroup.visible = true;
      this.shadowCatcher.visible = false;
      this.inAR = false;
    }
    this.mode = 'match';
    this.pendingMode = 'match';
    this.rules.startMatch();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.demoServeTimer = 1.4;
    // v2.28: sin sesión XR el menú principal no se pinta en el mundo 2D
    this.menuOpen = false;
    if (this.menuGroup) this.menuGroup.visible = false;
    for (const l of this.menuLines || []) l.visible = false;
    for (const d of this.menuDots || []) d.visible = false;
    this.callbacks.onXRState?.(false);
  };

  resetToss() {
    this.tossed = false;
    this.tossTimer = 0;
    this.apexSignaled = false;
    this.gripDown[0] = false;
    this.gripDown[1] = false;
  }

  onSelectStart(i) {
    if (this.disposed) return;
    this.audio.ensure();
    if (!this.renderer.xr.isPresenting) return;
    // v2.24: guardia anti-duplicado por mando (three.js puede entregar el
    // mismo 'selectstart' por varios espacios; dos disparos reales humanos
    // nunca distan < 70 ms). Sin esto, cada clic entraba 2 veces.
    const nowSel = performance.now() / 1000;
    if (nowSel - (this._lastSelect[i] || 0) < 0.07) return;
    this._lastSelect[i] = nowSel;

    // en modo ajuste, el gatillo lanza una bola de entrenamiento
    if (this.calib) {
      const now = performance.now() / 1000;
      if (now - this.lastFeedTap > 0.3) {
        this.lastFeedTap = now;
        this.feedPracticeBall();
      }
      return;
    }
    // MENÚ ABIERTO: el gatillo de CUALQUIER mando hace clic en el panel
    // (ni saque ni revancha). Antes solo valía el mando que aloja el panel:
    // apuntar con la pala no hacía nada.
    if (this.menuOpen) {
      const hov = this.menuHover[i];
      if (hov >= 0) this.menuClick(hov);
      return;
    }
    if (this.rules.state === 'over') {
      this.rules.startMatch(this.mode);   // revancha en el MISMO modo de juego
      this.resetToss();
      return;
    }
    // gatillo en CUALQUIER mando = saque asistido (v2.18: la gente buscaba el
    // gatillo en la mano de la pala y no pasaba nada). El lanzamiento usa
    // siempre la mano que SUJETA la bola.
    if (this.rules.state === 'serve' && this.rules.server === 'player' && !this.tossed) {
      this.tossFromHand(this.ballHand, true);
    }
  }

  /** Suelta la bola con la velocidad REAL de la mano (saque natural). */
  releaseBallHand(i) {
    if (this.calib || this.menuOpen) return;
    if (this.rules.state !== 'serve' || this.rules.server !== 'player') return;
    if (this.tossed || i !== this.ballHand) return;
    if (!this.renderer.xr.isPresenting) return;
    const hand = this.controllerPaddles[i];
    if (!hand.active) return;
    const v = hand.vel;
    if (v.length() < 0.5 && v.y < 0.05) {
      this.rules.message = 'Suelta el GRIP lanzando la mano hacia arriba';
      return;
    }
    this.tossFromHand(i, false);
  }

  tossFromHand(i, assisted) {
    const hand = this.controllerPaddles[i];
    const v = new THREE.Vector3().copy(hand.vel);
    if (assisted && v.y < DIMS.serveAssistVy) {
      v.y = DIMS.serveAssistVy;
      v.x *= 0.4;
      v.z *= 0.4;
    }
    this.tossed = true;
    this.tossTimer = 0;
    this.apexSignaled = false;
    this.tossReleaseY = this.ball.pos.y;
    this.tossMaxY = this.ball.pos.y;
    this.ball.vel.copy(v);
    this.ball.spin.set(0, 0, 0);
    this.rules.message = T('hint_hit');
    this.audio.serve();
    this.haptic(i, 0.45);
  }

  // Vibración háptica robusta (Quest Browser): el XRInputSource guardado en
  // 'connected' puede quedar obsoleto (el gamepad se re-crea al cambiar de
  // modo, con hand tracking, etc.), así que se resuelve el mando EN VIVO
  // desde la sesión XR y se prueban las distintas APIs de actuador.
  haptic(index, strength, ms = 45) {
    const s = Math.min(1, Math.max(0.2, strength));
    const hand = this.handOf?.[index] || (index === 0 ? 'right' : 'left');
    const gps = [];
    // 1) fuente en vivo de la sesión (fuente de verdad)
    try {
      const live = this.renderer.xr.getSession?.()?.inputSources;
      if (live) {
        for (const src of live) {
          if (!src.gamepad) continue;
          if (src.handedness === hand) gps.unshift(src.gamepad);
          else if (src.handedness === 'none') gps.push(src.gamepad);
        }
      }
    } catch { /* sesión cerrada entre frames */ }
    // 2) referencia cacheada del evento 'connected'
    if (this.sources[index]?.gamepad) gps.push(this.sources[index].gamepad);
    for (const gp of gps) {
      const acts = [];
      if (Array.isArray(gp.hapticActuators) && gp.hapticActuators[0]) acts.push(gp.hapticActuators[0]);
      else if (gp.hapticActuator) acts.push(gp.hapticActuator);
      if (gp.vibrationActuator) acts.push(gp.vibrationActuator);
      for (const act of acts) {
        try {
          if (typeof act.pulse === 'function' && act.pulse(s, ms) !== false) return true;
        } catch { /* probar siguiente API */ }
        try {
          if (typeof act.playEffect === 'function') {
            act.playEffect('dual-rumble', { startDelay: 0, duration: ms, weakMagnitude: s, strongMagnitude: s });
            return true;
          }
        } catch { /* probar siguiente actuador */ }
      }
    }
    return false;
  }

  // Diagnóstico único al entrar en VR: confirma con un pulso cada mando con
  // actuador (se SIENTE la vibración de prueba) y lo registra en consola.
  hapticProbe() {
    window.setTimeout(() => {
      let n = 0;
      try {
        const live = this.renderer.xr.getSession?.()?.inputSources;
        if (live) {
          for (const src of live) {
            if (!src.gamepad) continue;
            const act = (Array.isArray(src.gamepad.hapticActuators) && src.gamepad.hapticActuators[0])
              || src.gamepad.hapticActuator || src.gamepad.vibrationActuator || null;
            const usable = !!(act && (typeof act.pulse === 'function' || typeof act.playEffect === 'function'));
            console.log(`[Haptics] ${src.handedness}: actuador=${act ? 'sí' : 'no'} usable=${usable}`);
            if (usable) { n++; this.haptic(src.handedness === 'left' ? 1 : 0, 0.5, 120); }
          }
        }
      } catch { /* sin sesión */ }
      console.log(`[Haptics] ${n} mando(s) con vibración disponible`);
    }, 700);
  }

  // ---------- Bucle principal ----------

  animate = (time) => {
    if (this.disposed) return;
    const now = time * 0.001;
    const dt = this.lastTime < 0 ? 0.016 : Math.min(now - this.lastTime, 0.05);
    this.lastTime = now;

    const presenting = this.renderer.xr.isPresenting;

    // vigilancia del audio: si el contexto quedó suspendido a mitad de
    // partida (proximidad del visor, notificación...), o su reloj se
    // congeló con estado 'running' (grafo zombi), se reactiva solo
    this.audio.watchdog(dt);
    this.audioStatus.update(this.audio.ctx?.state || 'none', {
      alive: this.audio.clockAlive(),
      builds: this.audio.rebuilds,
      focus: document.hasFocus(),
      xr: !!this.renderer.xr.isPresenting,
    });

    if (presenting && this.recenterFrames > 0) {
      this.updateRecenter();
      this.recenterFrames--;
    }

    // 0) botón A/X: el mando donde se pulsa pasa a llevar la pala
    if (presenting && !this.calib) {
      for (let i = 0; i < 2; i++) {
        const gp = this.sources[i]?.gamepad;
        const b4 = !!gp?.buttons?.[4]?.pressed;
        if (b4 && !this.btn4Prev[i]) {
          this.manualHand = true;
          this.setPaddleHand(i);
        }
        this.btn4Prev[i] = b4;
      }
    }

    // 0.5) botón Y (mando izquierdo): modo ajuste de pala + entrenamiento
    if (presenting && this.readButton(this.handIndex('left'), 5)) {
      if (this.calib) this.exitCalib();
      else this.enterCalib();
    }

    // 0.6) botón B (mando derecho): MENÚ DE MUÑECA — todo configurable desde
    //      un panel anclado a la muñeca libre (modo, dificultad, sala, ambiente).
    //      Dentro del entrenamiento B sigue cambiando el agarre.
    if (presenting && !this.calib &&
        this.readButton(this.handIndex('right'), 5)) {
      this.toggleMenu();
    }

    // 0.7) menú abierto: anclar a la muñeca libre + rayo de apuntado
    if (presenting && this.menuOpen) this.updateMenu();

    // 0.8) v2.19: red online — emitir pose/bola/sync a 20 Hz
    if (this.net.online) this.net.tick(dt);

    // 1) Palas de los mandos (solo en VR)
    if (presenting && this.grips) {
      const servingToss = !this.calib && this.tossed &&
        this.rules.state === 'serve' && this.rules.server === 'player';
      for (let i = 0; i < 2; i++) {
        const ps = this.controllerPaddles[i];
        const grip = this.grips[i];
        tmpMountQ.copy(grip.quaternion).multiply(mountQuatFor(this.handOf[i])).multiply(this.gripOffsetQ);
        // la pala nunca atraviesa la mesa: se frena sobre la superficie
        this.clampPaddlePose(grip.position, tmpMountQ, true);
        updatePaddleSim(ps, grip.position, tmpMountQ, now, dt);
        ps.active = this.connected[i];
        // margen de detección extra SOLO mientras la bola del saque vuela:
        // golpear de forma natural no exige milimetrar la muñeca
        ps.extraReach = servingToss ? DIMS.serveExtraReach : 0;
      }
    }

    // 2) IA(s) — en online el rival es humano y llega por red (v2.19)
    const canHit = this.rules.state === 'rally';
    const playerPad = this.controllerPaddles[this.paddleHand];
    const oppPadX = presenting
      ? (playerPad.active ? playerPad.pos.x : 0)
      : this.demoAI.pos.x;
    const oppPadZ = presenting
      ? (playerPad.active ? playerPad.pos.z : DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4)
      : this.demoAI.pos.z;
    const aiServing = !this.calib && this.rules.state === 'serve' && this.rules.server === 'ai';
    const aiHit = (this.calib || this.net.online)
      ? null
      : this.ai.update(dt, this.ball, {
      canHit,
      validBounce: this.rules.validBounce,
      oppPadX,
      oppPadZ,
      rallyHits: this.rules.rallyHits,
      holdTarget: aiServing ? this.aiServeStance : null,
    });
    let demoHit = null;
    if (!presenting) {
      const demoServing = !this.calib && this.rules.state === 'serve' && this.rules.server === 'player';
      demoHit = this.demoAI.update(dt, this.ball, {
        canHit,
        validBounce: this.rules.validBounce,
        oppPadX: this.ai.pos.x,
        oppPadZ: this.ai.pos.z,
        rallyHits: this.rules.rallyHits,
        holdTarget: demoServing ? this.demoServeStance : null,
      });
    }
    if (aiHit) {
      this.ball.vel.copy(aiHit);
      // registro opcional para tests headless (solo si un test lo activa)
      if (window.__logAiHits) {
        (window.__aiHits = window.__aiHits || []).push({
          from: [+this.ball.pos.x.toFixed(3), +this.ball.pos.y.toFixed(3),
                 +this.ball.pos.z.toFixed(3)],
          v: [+aiHit.x.toFixed(3), +aiHit.y.toFixed(3), +aiHit.z.toFixed(3)],
          spin: [+this.ball.spin.x.toFixed(1), +this.ball.spin.y.toFixed(1)],
        });
      }
      this.processIntents(this.rules.registerPaddleHit('ai'));
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, aiHit.length() / 9),
      );
    }
    if (demoHit) {
      this.ball.vel.copy(demoHit);
      this.processIntents(this.rules.registerPaddleHit('player'));
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, demoHit.length() / 9),
      );
    }

    // 3) Preparación del saque
    let holdLock = false;
    if (this.rules.state === 'serve' && !this.calib) {
      if (this.rules.server === 'player') {
        if (presenting) {
          if (!this.tossed) {
            // bola apoyada en la mano libre (cinemática pura)
            holdLock = true;
            const bh = this.controllerPaddles[this.ballHand];
            this.ball.vel.set(0, 0, 0);
            this.ball.spin.set(0, 0, 0);
            if (bh.active) {
              this.ball.pos.copy(bh.pos);
              this.ball.pos.y += BALL_HAND_LIFT;
            } else {
              this.ball.pos.set(0.3, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4);
            }
          } else {
            // bola lanzada: física real
            this.tossTimer += dt;
            const vy = this.ball.vel.y;
            if (this.preVy > 0 && vy <= 0 && !this.apexSignaled) {
              // PUNTO MUERTO: señal clara para golpear de forma natural
              this.apexSignaled = true;
              this.apexPulse = 1;
              this.audio.tick();
              this.haptic(this.paddleHand, 0.22);
            }
            this.preVy = vy;
            if (this.tossMaxY < this.ball.pos.y) this.tossMaxY = this.ball.pos.y;
            if (this.tossTimer > 8) {
              this.resetToss();
              this.rules.message = 'Repite el lanzamiento';
            }
          }
        } else {
          // ESPECTADOR: la demo saca desde su posición reglamentaria
          if (!this.demoToss) {
            holdLock = true;
            this.ball.vel.set(0, 0, 0);
            this.ball.spin.set(0, 0, 0);
            this.ball.pos.copy(this.demoServeSpot);
            this.demoServeWait += dt;
            const near = this.demoAI.pos.distanceTo(this.demoServeStance) < 0.09;
            if (near || this.demoServeWait > 3) this.demoServeTimer -= dt;
            if (this.demoServeTimer <= 0) {
              this.demoToss = { timer: AI_TOSS_T };
              this.ball.vel.set(0, DIMS.serveAssistVy, -0.05);
              this.audio.serve();
            }
          } else {
            this.preVy = this.ball.vel.y;
            this.demoToss.timer -= dt;
            if (this.demoToss.timer <= 0) {
              this.demoToss = null;
              this.demoStrikeT = 0.22;
              this.serveFromAI('player');
            }
          }
        }
      } else if (this.net.online) {
        // v2.19: saque del rival humano — la bola llega por su emisión de red
      } else if (!this.aiToss) {
        // la CPU camina a su posición de saque, sostiene la bola y la lanza:
        // nada de sacar desde donde la pilló el punto anterior
        holdLock = true;
        this.ball.vel.set(0, 0, 0);
        this.ball.spin.set(0, 0, 0);
        this.ball.pos.copy(this.aiServeSpot);
        this.aiServeWait += dt;
        const near = this.ai.pos.distanceTo(this.aiServeStance) < 0.09;
        // v2.28: con el menú principal abierto la CPU NO saca — el partido
        // espera al primer EMPEZAR/cierre del menú
        if (!this.menuOpen && (near || this.aiServeWait > 3)) this.aiServeTimer -= dt;
        if (this.aiServeTimer <= 0) {
          this.aiToss = { timer: AI_TOSS_T };
          this.ball.vel.set(0, DIMS.serveAssistVy, 0.05);
          this.audio.serve();
        }
      } else {
        this.preVy = this.ball.vel.y;
        this.aiToss.timer -= dt;
        if (this.aiToss.timer <= 0) {
          this.aiToss = null;
          this.aiStrikeT = 0.22;
          this.serveFromAI('ai');
        }
      }
    }

    // 4) Física (solo la pala del mando activo colisiona)
    this.events.length = 0;
    this._localHit = false;
    if (this.net.online) this.net.drainNetwork(this);   // v2.19: rival por red
    if (!holdLock) {
      const pads = [];
      if (presenting) {
        const ps = this.controllerPaddles[this.paddleHand];
        if (ps.active) pads.push(ps);
      }
      if (this.net.online && this.net.owner !== this.net.mySide()) {
        // v2.19: la bola la simula el rival — seguir su emisión y solo
        // comprobar el contacto de MI pala contra ella
        const prevB = this._netPrevBall || (this._netPrevBall = new THREE.Vector3());
        prevB.copy(this.ball.pos);
        if (this.net.applyBallStream(this.ball, dt)) {
          testPaddleContact(this.ball, prevB, pads, this.events);
          for (const e of this.events) {
            if (e.type === 'paddle') { this._localHit = true; break; }
          }
        }
      } else {
        stepPhysics(dt, this.ball, pads, this.events);
      }
    }

    // 5) Golpe de saque del jugador: validar regla ITTF RELAJADA (v2.18).
    //    Se eliminó la exigencia del punto muerto: cualquier contacto tras el
    //    lanzamiento es válido (el asistente endereza la trayectoria igual).
    if (presenting && !this.calib && this.tossed && this.rules.state === 'serve' && this.rules.server === 'player') {
      for (const e of this.events) {
        if (e.type !== 'paddle' || e.who !== 'player') continue;
        if (this.tossMaxY - this.tossReleaseY < DIMS.tossMinRise) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = T('hint_toss_high');
          break;
        }
        if (this.ball.pos.z < DIMS.tableCenterZ + DIMS.tableHalfLength - DIMS.serveEndLineTol) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = T('hint_behind');
          break;
        }
        // golpe de saque válido
        e.consumed = true;
        this.tossed = false;
        // SOLIDEZ: si la trayectoria real no cumpliría el saque (bote propio
        // + bote rival), se endereza conservando parte del toque del jugador.
        const fix = findServeVelocity(this.ball.pos, 1);
        if (!simulateServePath(this.ball.pos, this.ball.vel, this.ball.spin, 1).ok) {
          this.ball.vel.lerp(fix.v, 0.65);
          this.ball.spin.lerp(fix.spin, 0.5);
          if (!simulateServePath(this.ball.pos, this.ball.vel, this.ball.spin, 1).ok) {
            this.ball.vel.copy(fix.v);
            this.ball.spin.copy(fix.spin);
          }
        }
        if (this.ball.vel.length() < 3.2) this.ball.vel.setLength(3.2);
        this.rules.beginServeRally('player');
        if (this.net.online) { this.net.sendHit(true); this._localHit = false; }
        this.haptic(e.paddleIndex ?? this.paddleHand, 0.8, 90);
        break;
      }
      // lanzamiento fallido: la bola tocó algo sin ser golpeada
      if (this.tossed) {
        for (const e of this.events) {
          if (e.type === 'table' || e.type === 'floor' || e.type === 'wall') {
            this.resetToss();
            this.rules.message = T('hint_dropped');
            break;
          }
        }
      }
    }

    // 5.5) Golpeos sólidos en el rally: si tras golpear el jugador la bola
    // marcha hacia atrás o queda sin fuerza, se endereza hacia el campo
    // rival (nunca bolas muertas ni golpes "esponja").
    if (presenting && this.rules.state === 'rally') {
      for (const e of this.events) {
        if (e.type !== 'paddle' || e.who !== 'player' || e.consumed) continue;
        const v = this.ball.vel;
        if (v.z > 0.5 || v.length() < 2.2) {
          const tz = DIMS.tableCenterZ - DIMS.tableHalfLength * (0.4 + Math.random() * 0.35);
          const tx = THREE.MathUtils.clamp(v.x * 0.4 + (Math.random() - 0.5) * 0.35, -0.52, 0.52);
          tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
          const fixed = computeShotVelocity(this.ball.pos, tmpTarget, 0.72, DIMS.maxBallSpeed);
          v.lerp(fixed, v.z > 0.5 ? 0.6 : 0.4);
        }
        break;
      }
    }

    // 5.6) v2.19 online: anunciar MI golpeo al rival (con la velocidad final,
    //      ya enderezada por el asistente del 5.5)
    if (this.net.online && this._localHit) {
      this._localHit = false;
      this.net.sendHit(false);
    }

    // 6) Reglas y eventos (en modo ajuste: sin marcador, solo físicas y sonido;
    //    en online el INVITADO no puntúa: el marcador llega del anfitrión)
    if (!this.calib && !(this.net.online && this.net.role === 'guest')) {
      this.processIntents(this.rules.handleEvents(this.events));
      this.processIntents(this.rules.update(dt));
    }
    this.processEvents(this.events);
    if (this.net.online) this.net.collectEvents(this.events);
    if (this.calib) this.updateCalibration(dt);

    // 7) Sincronizar visuales
    this.ballMesh.position.copy(this.ball.pos);
    this.ballMesh.rotation.x += this.ball.spin.x * dt * 0.05;
    this.ballMesh.rotation.y += this.ball.spin.y * dt * 0.05;
    this.apexPulse = Math.max(0, this.apexPulse - dt * 2.2);
    const ballHeld = holdLock;
    this.ballMesh.material.emissiveIntensity = ballHeld
      ? 0.75 + Math.sin(now * 6) * 0.25
      : 0.35 + this.apexPulse * 1.2;
    if (this.showTrail) this.trailUpdate(this.ball, dt);   // v2.18: se puede ocultar
    this.updateBlobShadow();

    // poses de las palas IA: postura natural, saque con toss y swing real
    this.aiStrikeT = Math.max(0, this.aiStrikeT - dt);
    this.demoStrikeT = Math.max(0, this.demoStrikeT - dt);
    if (this.net.online) {
      // v2.19: la pala del rival humano llega por red (marco espejo 180° en Y)
      const rp = this.net.remotePaddle;
      if (rp) {
        NetLink.posFromNet(rp.p, netTmpP);
        NetLink.quatFromNet(rp.q, netTmpQ);
        this.aiPaddleMesh.position.copy(netTmpP);
        this.aiPaddleMesh.quaternion.copy(netTmpQ);
      }
      this.aiPaddleMesh.visible = true;
    } else {
      this.updateAIPaddlePose(this.aiPaddleMesh, this.ai, 'ai', dt);
    }
    this.demoPaddleMesh.visible = !presenting;
    if (!presenting) this.updateAIPaddlePose(this.demoPaddleMesh, this.demoAI, 'player', dt);

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

    // fanfarria de fin de partido: entra con rebote, pulsa y se retira al
    // empezar la revancha (state deja de ser 'over')
    if (this.fanfareBanner.group.visible) {
      this.fanfareT += dt;
      if (this.rules.state !== 'over') {
        this.fanfareBanner.group.visible = false;
      } else {
        const s = Math.min(1, this.fanfareT / 0.45);
        const ease = 1 - Math.pow(1 - s, 3);
        const pulse = 1 + Math.sin(this.fanfareT * 5.2) * 0.045 * Math.max(0, 1 - this.fanfareT / 4);
        this.fanfareBanner.group.scale.setScalar(0.2 + 0.8 * ease * pulse);
        this.fanfareBanner.group.rotation.y = Math.sin(this.fanfareT * 1.3) * 0.06;
      }
    }
    if (this.confettiBurst > 0) this.confettiBurst = Math.max(0, this.confettiBurst - dt);
    this.confetti.update(
      dt,
      (this.fanfareBanner.group.visible && this.fanfareWin) || this.confettiBurst > 0,
    );

    if (this.calib && this.panelDirty) {
      this.calibPanel.update({ name: this.gripName, off: this.gripOffset });
      this.panelDirty = false;
    }
    // gancho de diagnóstico (solo lectura en tests headless; no afecta al juego)
    if (typeof window !== 'undefined' && window.__wantSolverHook && !window.__solverHook) {
      window.__solverHook = { computeShotVelocityReal, predictStrike, stepPhysics,
        DIMS, applyAerodynamics };
    }
    this.scoreboardUpdate({
      player: this.rules.scorePlayer,
      ai: this.rules.scoreAi,
      server: this.rules.server,
      message: this.calib ? T('calib_msg') : this.rules.message,
      oppLabel: this.rules.oppLabel,
      mode: this.mode,
      rally: this.rules.rallyHits,
      rallyes: this.survivalRallies,
      best: this.survivalBest,
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

    // 9) Render
    this.renderer.render(this.scene, this.camera);
  };

  /** Recentrado: gira el mundo para que la mesa quede frente al usuario. */
  updateRecenter() {
    const f = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);
    if (Math.abs(f.x) + Math.abs(f.z) < 1e-4) return;
    this.rig.rotation.y = Math.atan2(f.x, f.z) - Math.PI;
  }

  /**
   * Posición de saque reglamentaria de la IA/demo: bola tras la línea de
   * fondo (0,3 m) a una altura natural y pala a su lado derecho (postura
   * lateral real). Cada saque varía la posición lateral.
   */
  setupAIServe() {
    const s = this.ai.sign;                    // -1 (fondo -Z)
    const x = (Math.random() * 2 - 1) * 0.2;
    this.aiServeSpot.set(x, 1.02, DIMS.tableCenterZ + s * (DIMS.tableHalfLength + 0.3));
    // v2.23: postura diestra — el cuerpo queda al OTRO lado de la bola, que
    // sale junto a la mano derecha (coherente con el swing del saque)
    this.aiServeStance.set(
      x - s * 0.17, 1.0,
      DIMS.tableCenterZ + s * (DIMS.tableHalfLength + 0.44),
    );
    this.aiServeTimer = 0.9 + Math.random() * 0.6;
    this.aiServeWait = 0;
    this.aiStrikeT = 0;
  }
  setupDemoServe() {
    const s = this.demoAI.sign;                // +1 (fondo +Z)
    const x = (Math.random() * 2 - 1) * 0.2;
    this.demoServeSpot.set(x, 1.02, DIMS.tableCenterZ + s * (DIMS.tableHalfLength + 0.3));
    this.demoServeStance.set(
      x - s * 0.17, 1.0,
      DIMS.tableCenterZ + s * (DIMS.tableHalfLength + 0.44),
    );
    this.demoServeTimer = 1.0 + Math.random() * 0.6;
    this.demoServeWait = 0;
    this.demoStrikeT = 0;
  }

  /** Saque de una IA: trayectoria válida por simulación (bote propio + rival). */
  serveFromAI(side) {
    const ownSign = side === 'ai' ? -1 : 1;
    const { v, spin } = findServeVelocity(this.ball.pos, ownSign);
    this.ball.vel.copy(v);
    this.ball.spin.copy(spin);
    this.rules.beginServeRally(side);
    this.audio.serve();
  }

  /**
   * Pose de la pala de la IA (v2.23) y de la demo. ANTES se construía la
   * rotación con el mango siempre hacia abajo (base con eje Y vertical):
   * la pala quedaba una pared vertical perpetua. AHORA se compone desde dos
   * direcciones independientes — el EJE DE LA HOJA (mango→punta) y la NORMAL
   * DE LA CARA — más un roll de muñeca:
   *  · espera: hoja inclinada hacia delante y hacia el lado de la bola.
   *  · saque: postura diestra (bola junto a la mano derecha), cara abierta
   *    bajo la bola que va cerrando al golpear.
   *  · rallye: la punta carga hacia el lado del golpe (derecha/revés según
   *    de dónde venga la bola), la cara se CIERRA con liftado y se ABRE con
   *    cortada, y el follow-through CRUZA el cuerpo girando la hoja —
   *    golpes de izquierda y de derecha creíbles, hoja vertical u horizontal
   *    según el golpe.
   */
  updateAIPaddlePose(mesh, ai, who, dt) {
    const s = ai.sign;                       // -1 = CPU, +1 = demo
    AIM_FWD.set(0, 0, s < 0 ? 1 : -1);       // hacia el campo contrario
    AIM_RIGHT.set(s, 0, 0);                  // mano derecha: -X (CPU) / +X (demo)
    const stance = who === 'ai' ? this.aiServeStance : this.demoServeStance;
    const spot = who === 'ai' ? this.aiServeSpot : this.demoServeSpot;
    const toss = who === 'ai' ? this.aiToss : this.demoToss;
    const strikeT = who === 'ai' ? this.aiStrikeT : this.demoStrikeT;
    const serving = !this.calib && this.rules.state === 'serve' && this.rules.server === who;
    const fhServe = 1;   // postura de saque diestra (la bola sale a la derecha)

    /** poseQ = base ortonormal del disco de la pala a partir del eje de hoja
     *  (+Y local: mango→punta) y la normal de cara (+Z local), más DOS giros
     *  de muñeca en espacio LOCAL: pitch alrededor de X (cerrar la cara =
     *  topspin · abrirla = slice) y roll alrededor de Z. El pitch se aplica
     *  DESPUÉS de ortogonalizar: la apertura/cierre no se deforma nunca. */
    const bladePose = (bladeDir, faceDir, roll, pitch) => {
      AIM_BY.copy(bladeDir);
      if (AIM_BY.lengthSq() < 1e-8) AIM_BY.set(0, 1, 0);
      AIM_BY.normalize();
      AIM_BZ.copy(faceDir);
      if (AIM_BZ.lengthSq() < 1e-8) AIM_BZ.copy(AIM_FWD);
      AIM_BZ.addScaledVector(AIM_BY, -AIM_BZ.dot(AIM_BY));   // cara ⟂ hoja
      if (AIM_BZ.lengthSq() < 1e-7) {          // cara degenerada (paralela)
        AIM_BZ.copy(AIM_FWD).addScaledVector(AIM_BY, -AIM_FWD.dot(AIM_BY));
      }
      AIM_BZ.normalize();
      AIM_BX.crossVectors(AIM_BY, AIM_BZ).normalize();
      AIM_BZ.crossVectors(AIM_BX, AIM_BY);     // re-ortogonaliza (base exacta)
      aimM.makeBasis(AIM_BX, AIM_BY, AIM_BZ);
      poseQ.setFromRotationMatrix(aimM);
      if (pitch) {
        aimPitchQ.setFromAxisAngle(AIM_XA, pitch);
        poseQ.multiply(aimPitchQ);
      }
      if (roll) {
        aimRollQ.setFromAxisAngle(AIM_Z, roll);
        poseQ.multiply(aimRollQ);
      }
      return poseQ;
    };

    if (serving) {
      if (toss) {
        // swing del saque: de la postura cargada (derecha-arriba) al contacto
        const p = 1 - Math.max(0, toss.timer) / AI_TOSS_T;
        const e = Math.pow(p, 1.7);            // aceleración natural del brazo
        const bx = spot.x + s * 0.24;
        const by = spot.y + 0.15;
        const bz = spot.z + s * 0.12;
        const cx = this.ball.pos.x + s * 0.05;
        const cy = this.ball.pos.y - 0.02;
        const cz = this.ball.pos.z + s * 0.05;
        mesh.position.set(bx + (cx - bx) * e, by + (cy - by) * e, bz + (cz - bz) * e);
        // HOJA: punta cargada al lado derecho y girando hacia delante al golpear
        AIM_BLADE.set(0, 1 - 0.42 * e, 0)
          .addScaledVector(AIM_RIGHT, fhServe * (0.55 * (1 - e) + 0.12 * e))
          .addScaledVector(AIM_FWD, 0.2 + 0.35 * e);
        // CARA: por DEBAJO de la bola (mirándola) y cerrando al golpear;
        // el pitch de muñeca abre la cara al principio y la cierra al final
        AIM_FACE.copy(this.ball.pos).sub(mesh.position);
        if (AIM_FACE.lengthSq() < 1e-8) AIM_FACE.copy(AIM_FWD);
        AIM_FACE.normalize();
        bladePose(AIM_BLADE, AIM_FACE, fhServe * 0.2 * (1 - e), -0.2 * (1 - e) + 0.06 * e);
        mesh.quaternion.copy(poseQ);
        this.clampPaddlePose(mesh.position, mesh.quaternion, false);
        return;
      }
      if (strikeT > 0) {
        // instante del impacto: cara hacia donde sale el SAQUE (hoja aún
        // inclinada hacia delante, acabando de barrer bajo la bola)
        mesh.position.set(
          this.ball.pos.x + s * 0.05,
          this.ball.pos.y - 0.03,
          this.ball.pos.z + s * 0.05,
        );
        AIM_FACE.copy(this.ball.vel);
        if (AIM_FACE.lengthSq() < 1e-8) AIM_FACE.copy(AIM_FWD);
        AIM_FACE.normalize();
        // v2.23: hoja ⟂ a la salida (mango arriba, guiño al lado del saque):
        // la cara queda EXACTAMENTE hacia donde vuela la bola
        AIM_BLADE.set(0, 1, 0)
          .addScaledVector(AIM_FACE, -AIM_FACE.y)
          .addScaledVector(AIM_RIGHT, fhServe * 0.25);
        bladePose(AIM_BLADE, AIM_FACE, 0.12, 0.05);
        mesh.quaternion.copy(poseQ);
        this.clampPaddlePose(mesh.position, mesh.quaternion, false);
        return;
      }
      // preparación del saque: pala cargada al lado derecho, punta arriba y
      // cara abierta MIRANDO a la bola (como el jugador que espera el bote)
      mesh.position.copy(stance);
      AIM_FACE.copy(this.ball.pos).sub(mesh.position);
      if (AIM_FACE.lengthSq() < 1e-8) AIM_FACE.copy(AIM_FWD);
      AIM_FACE.normalize();
      AIM_BLADE.set(0, 0.9, 0)
        .addScaledVector(AIM_FWD, 0.3)
        .addScaledVector(AIM_RIGHT, fhServe * 0.55);
      bladePose(AIM_BLADE, AIM_FACE, fhServe * 0.18, -0.18);
      mesh.quaternion.copy(poseQ);
      this.clampPaddlePose(mesh.position, mesh.quaternion, false);
      return;
    }

    // rally / espera (v2.17: movimiento natural — v2.23: golpes con lado y giro)
    if (ai.swing) {
      const sw = ai.swing;
      const p = Math.min(1, sw.t / sw.dur);
      // follow-through: arranca con energía y frena (ease-out potente)
      const e = 1 - Math.pow(1 - p, 2.4);
      const K = SWING_POSE[sw.kind] || SWING_POSE.drive;
      const fh = sw.fh || 1;
      const amp = 0.26 * sw.speed;
      swingV.copy(sw.dir).multiplyScalar(amp * e);
      // cruce del cuerpo: el brazo termina al OTRO lado (de derecha a izquierda
      // en el drive, al revés en el revés)
      swingV.addScaledVector(AIM_RIGHT, -fh * 0.13 * K.cross * e);
      mesh.position.set(
        sw.contact.x + swingV.x,
        Math.max(0.42, sw.contact.y + swingV.y * 0.55 + 0.05 * (1 - e) + K.rise * e),
        sw.contact.z + swingV.z,
      );
      // HOJA: la punta parte cargada hacia el lado del golpe y CRUZA al lado
      // contrario mientras el brazo termina (el giro que le faltaba a la pala);
      // la inclinación hacia delante es PROPIA de cada golpe (tap vertical en
      // la cortada, barrido diagonal en el drive)
      AIM_BLADE.set(0, 1 - 0.3 * e, 0)
        .addScaledVector(AIM_FWD, K.fwd0 + K.fwd1 * e)
        .addScaledVector(AIM_RIGHT, fh * (K.side0 * (1 - e) - K.side1 * e));
      // CARA: hacia donde vuela la bola; el PITCH de muñeca la CIERRA con
      // liftado (topspin) y la ABRE con cortada (slice), cerrándose un poco
      // más durante el follow-through (firma de cada golpe)
      AIM_FACE.copy(sw.vdir || this.ball.vel);
      if (AIM_FACE.lengthSq() < 1e-8) AIM_FACE.copy(AIM_FWD);
      AIM_FACE.normalize();
      bladePose(AIM_BLADE, AIM_FACE,
        (sw.roll || 0) * (0.35 + 0.85 * e) + fh * (0.24 - 0.46 * e),
        K.clos0 + K.clos1 * e);
      mesh.quaternion.slerp(poseQ, Math.min(1, dt * 18));
    } else {
      const bob = Math.sin(performance.now() / 1000 * 3.0 + (who === 'ai' ? 0 : 2.1)) * 0.012;
      mesh.position.set(
        ai.pos.x + ai.prep.x,
        Math.max(0.42, ai.pos.y + ai.prep.y + bob),
        ai.pos.z + ai.prep.z,
      );
      // espera: postura de jugador real — hoja delante, inclinada hacia el
      // lado donde está la bola (nunca una pared vertical), cara ofrecida al
      // balón (algo abierta si viene baja, cerrada si viene alta) y vaivén
      // de muñeca relajado
      const side = THREE.MathUtils.clamp((this.ball.pos.x - mesh.position.x) * s * 2.6, -1, 1);
      AIM_BLADE.set(0, 1, 0)
        .addScaledVector(AIM_FWD, 0.32)
        .addScaledVector(AIM_RIGHT, side * 0.3);
      AIM_FACE.copy(AIM_FWD).multiplyScalar(0.85);
      AIM_FACE.x += (this.ball.pos.x - mesh.position.x) * 0.7;
      const sway = Math.sin(performance.now() / 1000 * 1.7 + (who === 'ai' ? 1.3 : 4.2)) * 0.06;
      // bola alta: cara algo cerrada por encima · bola baja: cara abierta
      bladePose(AIM_BLADE, AIM_FACE, sway, this.ball.pos.y > 1.25 ? 0.1 : -0.12);
      mesh.quaternion.slerp(poseQ, Math.min(1, dt * 9));
    }
    this.clampPaddlePose(mesh.position, mesh.quaternion, false);
  }

  // ---------- Anti-clipping: la pala no atraviesa mesa, red ni suelo ----------
  // Desplaza pos (ancla de la pala) lo mínimo necesario para que la hoja
  // (disco fino orientado) y el mango no penetren la geometría.
  //   fromGrip=true  -> ancla en el mango (pala del jugador: eje hoja -Z,
  //                     normal de cara +Y local, incluye offset de calibración)
  //   fromGrip=false -> ancla en el centro de la hoja (IA/demo: eje +Y, normal +Z)
  clampPaddlePose(pos, q, fromGrip) {
    const R = DIMS.bladeRadius, halfT = 0.004, hR = 0.014;
    const D = 0.1303;                                  // mango -> centro de hoja
    pcA.set(0, fromGrip ? 0 : 1, fromGrip ? -1 : 0).applyQuaternion(q);  // eje hoja
    pcN.set(0, fromGrip ? 1 : 0, fromGrip ? 0 : 1).applyQuaternion(q);   // normal cara
    pcC.copy(pos);
    if (fromGrip) {
      // ancla en el mango: centro de hoja = pos + offset + eje_hoja·D
      pcT.set(this.gripOffset.px, this.gripOffset.py, this.gripOffset.pz).applyQuaternion(q);
      pcC.add(pcT).addScaledVector(pcA, D);
    }
    // (fromGrip=false: pos ya ES el centro de la hoja)

    // semianchura del disco proyectada en cada eje (espesor incluido)
    const spanX = R * Math.sqrt(Math.max(0, 1 - pcN.x * pcN.x)) + halfT * Math.abs(pcN.x);
    const spanY = R * Math.sqrt(Math.max(0, 1 - pcN.y * pcN.y)) + halfT * Math.abs(pcN.y);
    const spanZ = R * Math.sqrt(Math.max(0, 1 - pcN.z * pcN.z)) + halfT * Math.abs(pcN.z);

    // punto más bajo de la pala (hoja + mango)
    const handleDown = hR * Math.sqrt(Math.max(0, 1 - pcA.y * pcA.y));
    let low = pcC.y - spanY;
    low = fromGrip
      ? Math.min(low, Math.min(pos.y, pcC.y) - handleDown)
      : Math.min(low, pcC.y - D * Math.max(0, pcA.y) - handleDown);

    // 1) losa de la mesa: solo si la pala la SOLAPA (con la mano bajo la
    //    mesa se mueve libre, sin saltos); resuelve por mínima penetración
    const skin = 0.004;
    const slabBottom = DIMS.tableTopY - DIMS.tableThickness;
    const overTable = Math.abs(pcC.x) < DIMS.tableHalfWidth + R * 0.85 &&
      Math.abs(pcC.z - DIMS.tableCenterZ) < DIMS.tableHalfLength + R * 0.85;
    if (overTable && low < DIMS.tableTopY && pcC.y + spanY > slabBottom) {
      const up = (DIMS.tableTopY + skin) - low;
      const down = (pcC.y + spanY + skin) - slabBottom;
      if (down < up) { pos.y -= down; pcC.y -= down; low -= down; }
      else           { pos.y += up;   pcC.y += up;   low += up;   }
    }

    // 2) red: losa vertical en z = C (tampoco la atraviesa al llegarse)
    const depth = 0.008 + spanZ - Math.abs(pcC.z - DIMS.tableCenterZ);
    if (depth > 0 &&
        Math.abs(pcC.x) < DIMS.netHalfWidth + spanX &&
        pcC.y - spanY < DIMS.netTopY && pcC.y + spanY > DIMS.tableTopY) {
      pos.z += (pos.z >= DIMS.tableCenterZ ? 1 : -1) * depth;
    }

    // 3) suelo
    if (low < 0.015) pos.y += 0.015 - low;
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
        case 'point': {
          // v2.25: el anfitrión captura el punto ESTRUCTURADO para el
          // invitado (con su causa host-relativa; el invitado la remapea)
          if (this.net.online && this.net.role === 'host' && !it.survival) {
            this.net.lastPoint = { w: it.winner, c: it.cause || '', rh: it.rallyHits || 0 };
          }
          if (it.survival) {
            // SUPERVIVENCIA: récord de rallye + la CPU acelera cada rallye
            const golpes = it.rallyHits || 0;
            if (golpes > this.survivalBest) {
              this.survivalBest = golpes;
              try { localStorage.setItem('ppxr_surv_best', String(this.survivalBest)); } catch { /* */ }
              this.audio.applause(true);
              this.audio.announce(T('ann_rally_record', { n: golpes }), true);
              if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.9, 150);
            } else if (golpes >= 8) {
              this.audio.applause(false);
            }
            this.survivalRallies = this.rules.rallyesSurvived;
            this.applyAISkill();   // la CPU acelera rallye a rallye
            this.celebrate(this.stats.recordSurvivalRally(golpes, this.survivalBest));
            this.emitStats();
            if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.25, 70);
          } else {
            // PARTIDO: punto + adaptativa + ambiente de torneo
            this.audio.point(it.winner === 'player');
            if (it.winner === 'player') {
              this.audio.applause(false);
            } else if (it.cause && NetLink.OHH_CAUSES.has(it.cause)) {
              this.audio.ohh();
            }
            if (this.renderer.xr.isPresenting) {
              this.haptic(this.paddleHand, it.winner === 'player' ? 0.85 : 0.4, it.winner === 'player' ? 110 : 60);
            }
            this.applyAISkill();   // IA adaptativa según el marcador
            this.celebrate(this.stats.recordPoint(it.winner, it.rallyHits || 0));
            this.emitStats();
          }
          break;
        }
        case 'retry-serve':
          // v2.25: el LET viaja al invitado (causa neutra) para su mensaje
          if (this.net.online && this.net.role === 'host') {
            this.net.lastRetry = it.cause || '';
          }
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (!this.net.online) {
            if (this.rules.server === 'ai') this.setupAIServe();
            else this.setupDemoServe();
          }
          break;
        case 'serve':
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (this.net.online) {
            // v2.19: la bola del saque la lleva quien saca (humano remoto o yo)
            this.net.owner = it.server === 'player' ? this.net.mySide() : this.net.oppSide();
          } else if (it.server === 'ai') this.setupAIServe();
          else this.setupDemoServe();
          // MEGAFONÍA: el marcador anuncia el resultado y quién saca
          if (this.rules.mode !== 'survival') {
            const s = this.rules;
            this.audio.announce(T('ann_score', {
              p: s.scorePlayer, q: s.scoreAi,
              who: it.server === 'player' ? T('who_you') : T(this.net.online ? 'opp_rival' : 'opp_machine'),
            }));
          }
          break;
        case 'game-over':
          this.startFanfare(it.winner === 'player');
          this.audio.applause(it.winner === 'player');
          this.audio.announce(
            it.winner === 'player'
              ? T('ann_victory', { p: this.rules.scorePlayer, q: this.rules.scoreAi })
              : T('ann_match_end', { opp: this.rules.opp(), p: this.rules.scoreAi, q: this.rules.scorePlayer }),
            true,
          );
          this.celebrate(this.stats.recordMatch(it.winner === 'player', this.difficulty));
          this.emitStats();
          break;
      }
    }
  }

  /** Fanfarria de fin de partido: sonido + banner 3D + confeti + vibración. */
  startFanfare(win) {
    this.fanfareWin = win;
    this.fanfareT = 0;
    this.audio.fanfare(win);
    this.fanfareBanner.draw(win, this.rules.scorePlayer, this.rules.scoreAi);
    this.fanfareBanner.group.visible = true;
    this.fanfareBanner.group.scale.setScalar(0.2);
    if (this.renderer.xr.isPresenting) {
      if (win) {
        this.haptic(this.paddleHand, 0.55, 90);
        window.setTimeout(() => this.haptic(this.paddleHand, 0.75, 90), 150);
        window.setTimeout(() => this.haptic(this.paddleHand, 1.0, 170), 300);
      } else {
        this.haptic(this.paddleHand, 0.3, 260);
        window.setTimeout(() => this.haptic(this.paddleHand, 0.22, 380), 300);
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
          if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.18);
          break;
        case 'net':
          this.audio.net(pan);
          this.audio.ohh();   // el público reacciona a la red
          break;
        case 'floor':
          this.audio.thud(pan, Math.min(1, e.speed / 5));
          break;
        case 'wall':
          this.audio.thud(pan, Math.min(0.5, e.speed / 6));
          break;
        case 'paddle':
          this.audio.paddle(pan, Math.min(1, e.speed / 9));
          // vibración clara del mando al golpear la bola (el canto, los
          // bloqueos y los golpeos suaves también se sienten)
          if (e.paddleIndex !== undefined && e.paddleIndex >= 0) {
            this.haptic(e.paddleIndex, Math.min(1, 0.5 + e.speed / 9), 70);
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
 *  INTERFAZ · PORTADA ANIMADA + botón JUGAR EN VR + HUD (v2.28)
 *  Portada minimalista: arte de cabecera, palas de idioma y el gran botón
 *  cartoon JUGAR/PLAY EN VR. La dificultad, las salas, el online y los
 *  ajustes viven DENTRO del menú principal de VR (panel flotante acordeón).
 * ===================================================================== */
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const vrbtn = document.getElementById('vrbtn');
const spectateBtn = document.getElementById('spectate');
const arBtn = document.getElementById('arbtn');
const hud = document.getElementById('hud');
const hudScore = document.getElementById('hud-score');
const hudMsg = document.getElementById('hud-msg');
const hudInfo = document.getElementById('hud-info');
const playEs = document.getElementById('playEs');
const playEn = document.getElementById('playEn');

// v2.28: el gran botón cartoon cambia JUGAR <-> PLAY según el idioma
function renderPlayBtn() {
  const en = TLang() === 'en';
  if (playEs && playEn) {
    playEs.style.display = en ? 'none' : '';
    playEn.style.display = en ? '' : 'none';
  }
}

// v2.28: la portada ya no muestra agarres ni estadísticas — los callbacks
// se conservan (el progreso sigue persistiendo y anunciándose en el juego)
function refreshGrips() { /* el ajuste de agarres vive en VR (Entrenar) */ }
function renderStats() { /* el progreso persiste; sin chips en la portada */ }

// wrapText: parte un texto en líneas ajustadas al ancho dado. El menú lo
// usaba desde v2.19 SIN DEFINIR (bug latente en el estado de error de red):
// corregido en v2.28.
function wrapText(c, text, x, y, maxW, lh) {
  const words = String(text || '').split(/\s+/);
  let line = '';
  let yy = y;
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (c.measureText(test).width > maxW && line) {
      c.fillText(line, x, yy);
      line = w;
      yy += lh;
    } else line = test;
  }
  if (line) c.fillText(line, x, yy);
  return yy;
}

// Cargar el modelo de la pala antes de arrancar la escena
loadPaddleModel().then((paddleModel) => {
  const game = new PingPongGame(document.getElementById('c'), paddleModel, {
    onScore(player, ai) {
      hudScore.textContent = `${player} : ${ai}`;
    },
    onMessage(message) {
      hudMsg.textContent = message;
    },
    onGrips(list, active) {
      refreshGrips(list, active);
    },
    onStats(stats) {
      renderStats(stats);
    },
    onTheme() { /* los chips de tema eran de la tarjeta antigua (2D) */ },
    onXRState(inVR) {
      if (inVR) {
        overlay.classList.add('hidden');
        hud.classList.remove('show');
        window.__ppMusic?.pause();    // v2.28: la música de portada se queda fuera
      } else {
        overlay.classList.remove('hidden');
        statusEl.textContent = T('status_pause');
        window.__ppMusic?.resume();   // de vuelta en la portada suena otra vez
      }
    },
  });
  window.__game = game;
  window.__NetLink = NetLink;   // accesible para pruebas headless (módulo ES)
  // v2.27: ganchos de i18n para pruebas headless (el módulo no expone globales)
  window.__T = T; window.__TLang = TLang; window.__setLang = setLang;
  window.__applyLangDOM = applyLangDOM;
  // gancho de depuración para pruebas headless (física de saque y constantes)
  window.__ppDebug = { findServeVelocity, simulateServePath, DIMS };
  renderPlayBtn();

  // Compatibilidad WebXR (estado bajo el gran botón de la portada)
  let lastStatusKey = 'status_vr_checking';
  const setStatusKey = (k) => { lastStatusKey = k; statusEl.textContent = T(k); };
  let xrOK = false;
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr')
      .then((ok) => {
        xrOK = ok;
        setStatusKey(ok ? 'status_vr_ok' : 'status_no_vr');
      })
      .catch(() => {
        setStatusKey('status_no_webxr');
      });
    if (arBtn) {
      navigator.xr.isSessionSupported('immersive-ar')
        .then((ok) => { arBtn.disabled = !ok; })
        .catch(() => { arBtn.disabled = true; });
    }
  } else {
    setStatusKey('status_no_2d');
  }

  // GRAN BOTÓN CARTOON (v2.28): entra en VR directamente. Sin visor avisa y
  // deja el modo demo al alcance (enlace discreto del pie de portada).
  vrbtn.addEventListener('click', () => {
    game.audio.ensure();
    if (!navigator.xr || !navigator.xr.isSessionSupported) {
      setStatusKey('status_no_vr');
      return;
    }
    if (!xrOK) { setStatusKey('status_no_vr'); return; }
    setStatusKey('status_starting_vr');
    game.enterVR()
      .catch((err) => {
        statusEl.textContent = '⚠️ ' + (err?.message || T('status_vr_fail'));
      });
  });

  // PASSTHROUGH: juega en TU habitación real (enlace discreto del pie)
  if (arBtn) {
    arBtn.addEventListener('click', () => {
      if (arBtn.disabled) return;
      setStatusKey('status_starting_ar');
      game.enterVR(false, true)
        .catch((err) => {
          statusEl.textContent = '⚠️ ' + (err?.message || T('status_ar_fail'));
        });
    });
  }

  // v2.27 · SELECTOR DE IDIOMA (palas con bandera de la portada + menú VR)
  document.querySelectorAll('[data-lang]').forEach((b) => {
    b.addEventListener('click', () => setLang(b.dataset.lang, game));
  });
  document.addEventListener('pp-lang', () => {
    renderPlayBtn();
    statusEl.textContent = T(lastStatusKey);
  });
  applyLangDOM();   // primera pintura de la portada en el idioma guardado
});

spectateBtn.addEventListener('click', () => {
  overlay.classList.add('hidden');
  hud.classList.add('show');
});
hudInfo.addEventListener('click', () => {
  overlay.classList.remove('hidden');
});

/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, saque con mano libre,
 *  háptica y bucle principal
 * ===================================================================== */
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
      ? 'Modo supervivencia. ¡Aguanta el rallye!'
      : 'Modo partido. ¡Buena suerte!', true);
    this.haptic(this.paddleHand, 0.6, 130);
  }

  /* ---------- v2.19 · SESIÓN ONLINE (PeerJS P2P) ----------
   * El anfitrión lleva las reglas y el marcador; el invitado recibe el
   * estado por red (reglas sombra). Cada lado simula la bola cuando es su
   * dueño (último golpeador / sacador) y la emite a 20 Hz. */
  startOnlineSession() {
    if (this.calib) this.exitCalib();
    this.closeMenu();
    this.rules.oppLabel = 'tu rival';
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.audio.announce('Rival conectado. ¡A jugar!', true);
    if (this.net.role === 'host') {
      this.startOnlineMatch();
    } else {
      // v2.25: el primer saque es del anfitrión — el estado sombra del
      // invitado arranca ya en perspectiva correcta (antes el primer paquete
      // de sync tardaba ~50 ms y el invitado veía un "tu saque" falso)
      this.rules.server = 'ai';
      this.rules.message = '¡Conectado! Esperando al anfitrión…';
    }
  }

  /** Partido online nuevo (anfitrión, o revancha pedida por el invitado). */
  startOnlineMatch() {
    if (this.net.role !== 'host') { this.net.sendRematch(); return; }
    this.rules.startMatch(this.mode);
    this.net.owner = 'host';
    this.resetToss();
    this.rules.message = 'Partido online · tu saque (GATILLO para lanzar)';
  }

  /** El rival se desconecta: vuelta al juego local contra la CPU. */
  onNetEnded(msg) {
    this.rules.oppLabel = 'la CPU';
    this.resetToss();
    this.aiToss = null;
    this.rules.startMatch(this.mode);
    this.rules.message = `${msg || 'Rival desconectado'} · partido local reiniciado`;
    this.audio.announce('Rival desconectado', true);
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
      this.rules.message = `SALA: ${t.name.toUpperCase()}`;
      this.audio.announce(`Sala ${t.name}`, true);
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

  // ---------- Menú de muñeca (v2.15) ----------
  // UN solo acceso a toda la configuración: B (mando derecho) abre un panel
  // anclado a la muñeca libre como una bandeja; se apunta con CUALQUIER mando
  // (la pala incluye) y se elige con el GATILLO. Sustituye al stick-click
  // (dificultad) y al flick (sala).
  // v2.16: rayo, láser, cursor y hover INDEPENDIENTES por mando — antes solo
  // el mando que aloja el panel podía seleccionar y apuntar con la pala no
  // hacía nada. Anclaje: panel SOBRE la muñeca (pegado a la mano); la
  // distancia de lectura la controla el propio brazo, no flota hacia la cara.

  buildMenu() {
    this.menuGroup = new THREE.Group();
    this.menuCanvas = document.createElement('canvas');
    this.menuCanvas.width = 512;
    this.menuCanvas.height = 640;
    this.menuTex = new THREE.CanvasTexture(this.menuCanvas);
    this.menuTex.colorSpace = THREE.SRGBColorSpace;
    this.menuMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.28, 0.35),
      new THREE.MeshBasicMaterial({ map: this.menuTex, transparent: true, depthTest: false }),
    );
    this.menuMesh.renderOrder = 990;
    this.menuGroup.add(this.menuMesh);

    this.menuGroup.visible = false;
    this.scene.add(this.menuGroup);   // espacio MUNDO: inmune al recentrado

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


  /** Zona inferior común del menú: pestañas + cerrar (v2.19). */
  drawMenuBottom(yTabs, rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    btn('tab:main', 28, yTabs, 222, 42, 'AJUSTES', this.menuPage === 'main');
    btn('tab:multi', 262, yTabs, 222, 42, 'MULTIJUGADOR', this.menuPage !== 'main');
    btn('close', 28, yTabs + 52, 456, 46, 'Cerrar menú', false);
  }

  /** Página MULTIJUGADOR: crear/unirse por código, estado y voz (v2.19). */
  drawMenuMulti() {
    const c = this.menuCanvas.getContext('2d');
    const rects = this._menuRects;
    const btn = this._menuBtn;
    const net = this.net;
    const st = net.online ? 'online' : net.status;

    c.fillStyle = '#9aa7b4';
    c.font = '700 14px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText('JUEGA CONTRA OTRA PERSONA POR INTERNET', 28, 112);

    if (st === 'online') {
      c.fillStyle = '#7fb069';
      c.font = '800 30px system-ui, sans-serif';
      c.textAlign = 'center';
      c.fillText('CONECTADO', 256, 152);
      c.fillStyle = '#cfd8e0';
      c.font = '600 18px system-ui, sans-serif';
      c.fillText(`rival: ${net.code} · ${this.rules.state === 'over' ? 'partido terminado' : 'jugando'}`, 256, 186);
      const voz = net.voiceState === 'on'
        ? (net.micOn ? 'Voz activa (micrófono abierto)' : 'Voz activa (tu micro está en silencio)')
        : net.voiceState === 'asking' ? 'Pidiendo micrófono…'
        : net.voiceState === 'denied' ? 'Micrófono denegado'
        : 'Sin voz (pulsa Voz para activarla)';
      c.fillStyle = '#9aa7b4';
      c.font = '500 16px system-ui, sans-serif';
      c.fillText(voz, 256, 214);
      btn('net:mic', 28, 240, 222, 48, `Voz: ${net.micOn ? 'Sí' : 'No'}`, net.micOn && net.voiceState === 'on', undefined, !!net.micOn);
      btn('net:hangup', 262, 240, 222, 48, 'COLGAR', false);
      c.fillStyle = '#9aa7b4';
      c.font = '500 15px system-ui, sans-serif';
      c.textAlign = 'center';
      c.fillText('La revancha está en la pestaña AJUSTES.', 256, 330);
    } else if (st === 'waiting') {
      c.fillStyle = '#e8b45a';
      c.font = '700 18px system-ui, sans-serif';
      c.textAlign = 'center';
      c.fillText('CÓDIGO DE LA SALA', 256, 146);
      c.fillStyle = '#f2f4f6';
      c.font = '900 72px ui-monospace, monospace';
      c.fillText(net.code, 256, 210);
      c.fillStyle = '#9aa7b4';
      c.font = '500 16px system-ui, sans-serif';
      c.fillText('Esperando al rival… comparte este código', 256, 258);
      btn('net:cancel', 28, 290, 456, 48, 'CANCELAR SALA', false);
    } else if (st === 'creating' || st === 'joining') {
      c.fillStyle = '#e8b45a';
      c.font = '700 24px system-ui, sans-serif';
      c.textAlign = 'center';
      c.fillText(st === 'creating' ? 'Creando sala…' : `Conectando a ${net.code}…`, 256, 180);
      btn('net:cancel', 28, 240, 456, 48, 'CANCELAR', false);
    } else if (st === 'error') {
      c.fillStyle = '#ff6b57';
      c.font = '700 22px system-ui, sans-serif';
      c.textAlign = 'center';
      wrapText(c, net.statusMsg || 'Error de red', 256, 150, 440, 28);
      btn('net:host', 28, 240, 222, 48, 'REINTENTAR', false);
      btn('net:cancel', 262, 240, 222, 48, 'VOLVER', false);
    } else {
      // off
      c.fillStyle = '#cfd8e0';
      c.font = '600 18px system-ui, sans-serif';
      c.textAlign = 'center';
      c.fillText('Crea una sala o únete con un código.', 256, 152);
      btn('net:host', 28, 200, 456, 52, 'CREAR SALA (código para tu rival)', false, 'green');
      btn('net:join', 28, 268, 456, 52, 'INTRODUCIR CÓDIGO DE UN AMIGO', false);
    }

    c.fillStyle = '#75828f';
    c.font = '500 14px system-ui, sans-serif';
    c.textAlign = 'center';
    c.fillText('P2P directo (WebRTC). Necesita internet en ambos visores.', 256, 396);
    c.fillText('La voz usa el micrófono: acepta el permiso del navegador.', 256, 420);
    this.drawMenuBottom(454, rects);
  }

  /** Página JOIN: teclado en el panel para escribir el código (v2.19). */
  drawMenuJoin() {
    const c = this.menuCanvas.getContext('2d');
    const rects = this._menuRects;
    const btn = this._menuBtn;
    const CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // sin 0/O/1/I/L

    c.fillStyle = '#9aa7b4';
    c.font = '700 14px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText('CÓDIGO DE LA SALA DE TU AMIGO', 28, 112);

    // 5 huecos del código
    for (let i = 0; i < 5; i++) {
      const x = 28 + i * 96;
      c.beginPath();
      if (c.roundRect) c.roundRect(x, 124, 74, 66, 12);
      else c.rect(x, 124, 74, 66);
      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.fill();
      c.strokeStyle = i === this._joinCode.length ? '#e8b45a' : 'rgba(255,255,255,0.18)';
      c.lineWidth = i === this._joinCode.length ? 3 : 1.5;
      c.stroke();
      const ch = this._joinCode[i];
      if (ch) {
        c.fillStyle = '#f2f4f6';
        c.font = '800 44px ui-monospace, monospace';
        c.textAlign = 'center';
        c.fillText(ch, x + 37, 158);
      }
    }

    // teclado 7×5
    c.textAlign = 'center';
    for (let i = 0; i < CHARS.length; i++) {
      const col = i % 7, row = Math.floor(i / 7);
      btn(`key:${CHARS[i]}`, 28 + col * 66, 210 + row * 50, 60, 44, CHARS[i], false);
    }
    btn('key:del', 28 + 5 * 66, 210 + 4 * 50, 60, 44, '⌫', false);
    btn('key:ok', 28, 470, 222, 48, 'CONECTAR', this._joinCode.length === 5, 'green');
    btn('key:cancel', 262, 470, 222, 48, 'VOLVER', false);
    this.drawMenuBottom(528, rects);
  }

  /** Pinta el panel y deja en menuRects las zonas clicables (px canvas). */
  drawMenu() {
    const c = this.menuCanvas.getContext('2d');
    if (!c) return;
    const W = 512, H = 640;
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
    rr(4, 4, W - 8, H - 8, 26);
    c.fillStyle = 'rgba(11,14,18,0.94)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.6)';
    c.lineWidth = 3;
    c.stroke();

    // cabecera
    c.fillStyle = '#f2f4f6';
    c.font = '800 32px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('MENÚ', 200, 46);
    c.fillStyle = '#9aa7b4';
    c.font = '600 15px system-ui, sans-serif';
    c.fillText('apunta con la pala y elige con el GATILLO', 200, 76);
    c.textAlign = 'right';
    c.fillStyle = '#e8b45a';
    c.font = '700 16px system-ui, sans-serif';
    c.fillText('B · cerrar', W - 26, 46);

    // botón genérico (compartido por todas las páginas)
    // v2.23: (1) los botones ACTIVOS también responden al apuntado (antes
    // las casillas marcadas parecían muertas: sin hover ni respuesta);
    // (2) los basculantes llevan CASILLA explícita ☑/☐ que refleja su
    // estado; (3) la zona táctil es más grande que el dibujo (los botones
    // de ~2 cm eran imposibles de puntear con el láser en el visor).
    const btn = (id, x, y, w, h, label, active, style, check) => {
      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 12);
      if (active) {
        c.fillStyle = style === 'green'
          ? (hovered ? '#93c97e' : '#7fb069')
          : (hovered ? '#f4ca79' : '#e8b45a');
        c.fill();
        if (hovered) {
          c.strokeStyle = '#ffffff';
          c.lineWidth = 3;
          c.stroke();
        }
        c.fillStyle = '#10131a';
      } else {
        c.fillStyle = 'rgba(255,255,255,0.07)';
        c.fill();
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.18)';
        c.lineWidth = hovered ? 3 : 1.5;
        if (style === 'green') c.strokeStyle = hovered ? '#bfe3a9' : 'rgba(127,176,105,0.55)';
        c.stroke();
        c.fillStyle = style === 'green' ? '#bfe3a9' : '#cfd8e0';
      }
      c.font = '700 20px system-ui, sans-serif';
      c.textAlign = 'center';
      let tx = x + w / 2;
      if (check !== undefined) {
        const bs = 9, bx = x + 18, by = y + h / 2;
        c.lineWidth = 2;
        if (check) {
          c.fillStyle = active ? 'rgba(16,19,26,0.88)' : 'rgba(207,216,224,0.92)';
          c.fillRect(bx - bs, by - bs, bs * 2, bs * 2);
          c.strokeStyle = active ? '#e8b45a' : '#10131a';
          c.beginPath();
          c.moveTo(bx - 5, by + 0.5);
          c.lineTo(bx - 1.5, by + 4.5);
          c.lineTo(bx + 5.5, by - 4.5);
          c.stroke();
        } else {
          c.strokeStyle = active ? 'rgba(16,19,26,0.8)' : 'rgba(255,255,255,0.55)';
          c.strokeRect(bx - bs, by - bs, bs * 2, bs * 2);
        }
        tx += 13;
      }
      c.fillText(label, tx, y + h / 2 + 1);
      rects.push({ x: x - 5, y: y - 3, w: w + 10, h: h + 6, id });
    };
    this._menuBtn = btn;
    this._menuRects = rects;
    const label = (txt, y) => {
      c.fillStyle = '#9aa7b4';
      c.font = '700 14px system-ui, sans-serif';
      c.textAlign = 'left';
      c.fillText(txt, 28, y);
    };

    if (this.menuPage === 'multi') {
      this.drawMenuMulti();
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    if (this.menuPage === 'join') {
      this.drawMenuJoin();
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }

    // MODO (v2.18: filas compactas para dejar sitio a EXTRAS)
    label('MODO DE JUEGO', 110);
    btn('mode:match', 28, 120, 222, 44, 'Partido', this.mode === 'match');
    btn('mode:survival', 262, 120, 222, 44, 'Supervivencia', this.mode === 'survival');

    // DIFICULTAD
    label('DIFICULTAD DE LA CPU', 176);
    btn('diff:easy', 28, 186, 136, 42, 'Fácil', this.difficulty === 'easy');
    btn('diff:medium', 188, 186, 136, 42, 'Media', this.difficulty === 'medium');
    btn('diff:hard', 348, 186, 136, 42, 'Difícil', this.difficulty === 'hard');

    // SALA (2×2)
    label('SALA', 242);
    const themes = [
      ['theme:pabellon', 'Pabellón'], ['theme:neon', 'Neón'],
      ['theme:atardecer', 'Atardecer'], ['theme:artico', 'Ártico'],
    ];
    themes.forEach(([id, name], i) => {
      btn(id, 28 + (i % 2) * 234, 252 + Math.floor(i / 2) * 50, 222, 42,
        name, this.theme === id.split(':')[1]);
    });

    // EXTRAS (v2.18; v2.22 añade el MEGÁFONO; v2.23: casillas ☑/☐): los
    // tres basculantes muestran su estado con la casilla y responden al
    // apuntado aunque estén activos.
    label('EXTRAS', 356);
    btn('amb', 28, 366, 222, 40, `Ambiente: ${this.audio.ambience ? 'Sí' : 'No'}`, !!this.audio.ambience, undefined, !!this.audio.ambience);
    btn('trail', 262, 366, 222, 40, `Estela: ${this.showTrail ? 'Sí' : 'No'}`, !!this.showTrail, undefined, !!this.showTrail);
    btn('voz', 28, 414, 456, 40, `Megáfono del marcador: ${this.audio.voice ? 'Sí' : 'No'}`, !!this.audio.voice, undefined, !!this.audio.voice);

    // REVANCHA (solo con el partido terminado)
    let yNext = 460;
    if (over) {
      btn('revancha', 28, yNext, 456, 46, 'REVANCHA', false, 'green');
      yNext += 54;
    }

    // pestañas + cerrar (v2.19)
    btn('tab:main', 28, yNext, 222, 40, 'AJUSTES', true);
    btn('tab:multi', 262, yNext, 222, 40, 'MULTIJUGADOR', false);
    btn('close', 28, yNext + 46, 456, 42, 'Cerrar menú', false);

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
      this.rules.message = 'Menú · apunta y pulsa el GATILLO';
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

  /** Ancla el panel a la muñeca libre (bandeja sobre la mano), lo orienta a
   *  la cara y hace el hit-test del rayo de apuntado DE CADA MANDO: la pala
   *  también puede seleccionar, cada mano tiene su láser y su hover. */
  updateMenu() {
    const ci = 1 - this.paddleHand;
    const grip = this.grips[ci];
    if (!this.connected[ci] || !grip) {
      this.menuGroup.visible = false;
      for (const l of this.menuLines) l.visible = false;
      for (const d of this.menuDots) d.visible = false;
      return;
    }
    this.menuGroup.visible = true;

    // --- anclaje: bandeja SOBRE la muñeca a distancia CONSTANTE (pegada a la
    //     mano); la orientación sí sigue a la cara para leerla de frente.
    //     Antes flotaba hacia la cabeza (0,15 m + 0,09 arriba) y quedaba
    //     pegada a los ojos; la distancia de lectura la manda el brazo.
    grip.getWorldPosition(muGrip);
    this.camera.getWorldPosition(muHead);
    muPos.copy(muGrip);
    muPos.y += 0.16;
    this.menuGroup.position.copy(muPos);
    this.menuGroup.lookAt(muHead);

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
          const px = hit.uv.x * 512;
          const py = (1 - hit.uv.y) * 640;
          idx = this.menuRects.findIndex((r) =>
            px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h);
          // cursor sobre el panel (uv -> plano 0.28×0.35).
          // v2.24 FIX: el eje Y del plano es uv.y=1 ARRIBA (+0.175). Antes se
          // pintaba (0.5 - uv.y) y el punto aparecía ESPEJADO en vertical:
          // el usuario apuntaba con el punto (no con el impacto real) y los
          // clics caían en el botón equivocado ("zonas desplazadas").
          dot.visible = true;
          dot.position.set((hit.uv.x - 0.5) * 0.28, (hit.uv.y - 0.5) * 0.35, 0.004);
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
      case 'tab':
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
      case 'mode':
        // v2.23: ya NO cierra el menú — el cambio se VE (la casilla marcada
        // salta de botón) y el mensaje dice cómo seguir. Antes el menú se
        // cerraba y el usuario no sabía si el modo había cambiado.
        if (this.net.online && this.net.role === 'guest') {
          this.net.sendMode(arg === 'survival' ? 'survival' : 'match');
          this.rules.message = 'Pidiendo cambio de modo al anfitrión…';
        } else {
          this.switchMode(arg === 'survival' ? 'survival' : 'match');
          this.rules.message = `Modo: ${arg === 'survival' ? 'SUPERVIVENCIA' : 'PARTIDO'} · cierra el menú para jugar`;
        }
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      case 'diff': {
        if (this.net.online) {
          this.rules.message = 'En online no hay CPU · la dificultad no aplica';
          this.drawMenu();
          break;
        }
        this.setDifficulty(arg);
        const lb = { easy: 'Fácil', medium: 'Media', hard: 'Difícil' }[arg] || arg;
        this.rules.message = `DIFICULTAD: ${lb.toUpperCase()}`;
        this.audio.announce(`Dificultad ${lb}`, true);
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
        this.rules.message = this.showTrail ? 'Estela de la bola: Sí' : 'Estela de la bola: No';
        this.drawMenu();
        break;
      }
      case 'voz': {
        // v2.22: megáfono del marcador (narrador) sí/no, persistente e
        // independiente del ambiente de torneo
        this.audio.setVoice(!this.audio.voice);
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.rules.message = this.audio.voice ? 'Megáfono del marcador: Sí' : 'Megáfono del marcador: No';
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
      this.audio.announce(`¡Logro desbloqueado: ${d.name}!`, true);
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
    // el menú empieza SIEMPRE cerrado en cada sesión
    this.menuOpen = false;
    if (this.menuGroup) this.menuGroup.visible = false;
    for (const l of this.menuLines || []) l.visible = false;
    for (const d of this.menuDots || []) d.visible = false;
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
        ? 'Modo supervivencia. ¡Aguanta el rallye!'
        : 'Bienvenido al partido. ¡Buena suerte!', true);
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
    this.rules.message = '¡Golpea la bola hacia la mesa con la pala!';
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
        if (near || this.aiServeWait > 3) this.aiServeTimer -= dt;
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
          this.rules.message = 'Lanza la bola un poco más arriba';
          break;
        }
        if (this.ball.pos.z < DIMS.tableCenterZ + DIMS.tableHalfLength - DIMS.serveEndLineTol) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Saca desde detrás de la línea de fondo';
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
            this.rules.message = 'Bola caída · repite el lanzamiento';
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
      message: this.calib ? 'ENTRENAMIENTO · Y: volver al modo anterior' : this.rules.message,
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
              this.audio.announce(`¡Rallye de ${golpes} golpes! Nuevo récord`, true);
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
            } else if (it.cause && /red|fuera|pared/.test(it.cause)) {
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
            this.audio.announce(
              `${s.scorePlayer} a ${s.scoreAi}, saque para ${it.server === 'player' ? 'ti' : (this.net.online ? 'tu rival' : 'la máquina')}`,
            );
          }
          break;
        case 'game-over':
          this.startFanfare(it.winner === 'player');
          this.audio.applause(it.winner === 'player');
          this.audio.announce(
            it.winner === 'player'
              ? `¡Victoria! ${this.rules.scorePlayer} a ${this.rules.scoreAi}`
              : `Partido para ${this.rules.opp()}. ${this.rules.scoreAi} a ${this.rules.scorePlayer}`,
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
 *  INTERFAZ · overlay, botón VR, dificultad y HUD
 * ===================================================================== */
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const vrbtn = document.getElementById('vrbtn');
const trainBtn = document.getElementById('trainbtn');
const spectateBtn = document.getElementById('spectate');
const survBtn = document.getElementById('survbtn');
const arBtn = document.getElementById('arbtn');
const ambBtn = document.getElementById('ambbtn');
const hud = document.getElementById('hud');
const hudScore = document.getElementById('hud-score');
const hudMsg = document.getElementById('hud-msg');
const hudInfo = document.getElementById('hud-info');

// UI de agarres guardados (localStorage del navegador de la Quest)
const gripSel = document.getElementById('gripSel');
const gripNameInput = document.getElementById('gripName');
function refreshGrips(list, active) {
  gripSel.innerHTML = '';
  for (const n of list) {
    const o = document.createElement('option');
    o.value = n;
    o.textContent = n;
    gripSel.appendChild(o);
  }
  if (active && list.includes(active)) gripSel.value = active;
}

// UI de estadísticas y logros (progreso persistente)
const statsLine = document.getElementById('statsLine');
const achRow = document.getElementById('achRow');
function renderStats(s) {
  if (!s || !statsLine || !achRow) return;
  statsLine.textContent =
    `${s.won} victorias · ${s.lost} derrotas · racha ${s.streak} (máx. ${s.bestStreak})` +
    ` · mejor rallye ${s.bestRally} · saques directos ${s.aces}`;
  achRow.innerHTML = '';
  for (const a of ACHIEVEMENTS) {
    const chip = document.createElement('span');
    chip.className = 'ach' + (s.ach && s.ach[a.key] ? ' on' : '');
    chip.title = a.desc;
    chip.textContent = `${a.emoji} ${a.name}`;
    achRow.appendChild(chip);
  }
}
const statsResetBtn = document.getElementById('statsReset');
statsResetBtn.addEventListener('click', () => {
  const g = window.__game;
  if (!g) return;
  g.stats.data = {
    won: 0, lost: 0, streak: 0, bestStreak: 0,
    pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
    winsByDiff: { easy: 0, medium: 0, hard: 0 },
    ach: {},
  };
  g.stats.save();
  g.survivalBest = 0;
  try { localStorage.removeItem('ppxr_surv_best'); } catch { /* */ }
  renderStats(g.stats.data);
});

// Chips de TEMAS DE SALA del overlay (se sincronizan también con el flick
// del stick en VR vía callback onTheme)
const themBtns = [...document.querySelectorAll('[data-theme]')];
const renderTheme = (key) => {
  themBtns.forEach((b) => b.classList.toggle('active', b.dataset.theme === key));
};

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
    onTheme(key) {
      renderTheme(key);
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
  window.__game = game;
  window.__NetLink = NetLink;   // accesible para pruebas headless (módulo ES)
  renderStats(game.stats.data);   // pintar el progreso persistente al arrancar
  renderTheme(game.theme);        // pintar el tema de sala persistente
  // gancho de depuración para pruebas headless (física de saque y constantes)
  window.__ppDebug = { findServeVelocity, simulateServePath, DIMS };

  // Compatibilidad WebXR
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr')
      .then((ok) => {
        if (ok) {
          vrbtn.disabled = false;
          trainBtn.disabled = false;
          survBtn.disabled = false;
          statusEl.textContent = '✅ Visor compatible detectado. Ponte las gafas y pulsa el botón.';
        } else {
          statusEl.textContent = '🖥️ Sin visor VR: disfruta del modo espectador (IA contra IA).';
        }
      })
      .catch(() => {
        statusEl.textContent = '🖥️ WebXR no disponible aquí: modo espectador activo.';
      });
    navigator.xr.isSessionSupported('immersive-ar')
      .then((ok) => { arBtn.disabled = !ok; })
      .catch(() => { arBtn.disabled = true; });
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

  // Entrenamiento en VR: máquina de bolas + ajuste del agarre con panel 3D
  trainBtn.addEventListener('click', () => {
    trainBtn.disabled = true;
    statusEl.textContent = 'Iniciando VR en modo entrenamiento…';
    game.enterVR(true)
      .then(() => {
        trainBtn.disabled = false;
      })
      .catch((err) => {
        trainBtn.disabled = false;
        statusEl.textContent = '⚠️ ' + (err?.message || 'No se pudo iniciar la sesión VR.');
      });
  });

  // SUPERVIVENCIA: la CPU acelera rallye a rallye, ¿cuántos golpes aguantas?
  survBtn.addEventListener('click', () => {
    survBtn.disabled = true;
    statusEl.textContent = 'Iniciando VR en modo supervivencia…';
    game.enterVR(false, false, 'survival')
      .then(() => {
        survBtn.disabled = false;
      })
      .catch((err) => {
        survBtn.disabled = false;
        statusEl.textContent = '⚠️ ' + (err?.message || 'No se pudo iniciar la sesión VR.');
      });
  });

  // PASSTHROUGH: juega en TU habitación real (immersive-ar)
  arBtn.addEventListener('click', () => {
    arBtn.disabled = true;
    statusEl.textContent = 'Iniciando passthrough…';
    game.enterVR(false, true)
      .then(() => {
        arBtn.disabled = false;
      })
      .catch((err) => {
        arBtn.disabled = false;
        statusEl.textContent = '⚠️ ' + (err?.message || 'No se pudo iniciar el passthrough.');
      });
  });

  // Ambiente de torneo (murmullo + aplausos + megafonía): SÍ/NO
  const ambLabel = () => {
    ambBtn.textContent = game.audio.ambience
      ? '🔊 Ambiente de torneo: SÍ'
      : '🔇 Ambiente de torneo: NO';
  };
  ambLabel();
  ambBtn.addEventListener('click', () => {
    game.audio.setAmbience(!game.audio.ambience);
    ambLabel();
  });

  // Guardar / cargar / borrar agarres desde el menú
  document.getElementById('gripSave').addEventListener('click', () => {
    game.saveCurrentGrip(gripNameInput.value);
    gripNameInput.value = '';
  });
  document.getElementById('gripLoad').addEventListener('click', () => {
    game.loadGripByName(gripSel.value);
  });
  document.getElementById('gripDel').addEventListener('click', () => {
    game.deleteGripByName(gripSel.value);
  });
  document.getElementById('gripReset').addEventListener('click', () => {
    game.resetGripNatural();
  });

  document.querySelectorAll('.diff').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.diff').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      game.setDifficulty(btn.dataset.diff);
    });
  });

  // Temas de sala: aplicar en vivo (silent: el cambio ya se VE al instante)
  themBtns.forEach((btn) => {
    btn.addEventListener('click', () => game.setTheme(btn.dataset.theme, true));
  });
});

spectateBtn.addEventListener('click', () => {
  overlay.classList.add('hidden');
  hud.classList.add('show');
});
hudInfo.addEventListener('click', () => {
  overlay.classList.remove('hidden');
});

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

// temporales del anti-clipping de palas (mesa / red / suelo)
const pcA = new THREE.Vector3();
const pcN = new THREE.Vector3();
const pcC = new THREE.Vector3();
const pcT = new THREE.Vector3();

class PingPongGame {
  constructor(canvas, paddleModel, callbacks = {}) {
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
    this.pendingCalib = false;
    this.feedTimer = 1.5;
    this.feedIdle = 0;
    this.panelDirty = true;
    this.btnPrev = {};
    this.lastFeedTap = 0;
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
    const hemi = new THREE.HemisphereLight(0xdfe8f0, 0x30271f, 0.85);
    this.rig.add(hemi);

    const dir = new THREE.DirectionalLight(0xffffff, 2.4);
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

    this.rig.add(createRoom());
    this.rig.add(createTable());

    const { mesh, trail, trailUpdate } = createBall();
    this.ballMesh = mesh;
    this.trailUpdate = trailUpdate;
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

      const onSelect = () => this.onSelectStart(i);
      grip.addEventListener('selectstart', onSelect);
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
      targetRay.addEventListener('squeezestart', onSqueezeStart);
      targetRay.addEventListener('squeezeend', onSqueezeEnd);

      this.rig.add(grip);
      this.rig.add(targetRay);
      this.grips.push(grip);
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
    this.rules.startMatch();
    this.resetToss();
    this.ai.reset();
    this.setupAIServe();
    this.setupDemoServe();
    this.haptic(this.paddleHand, 0.4);
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

  async enterVR(startCalib = false) {
    // Preparación de audio DENTRO de este clic (gesto de usuario): repara un
    // contexto enfermo (suspendido/cerrado) recreándolo, pero NO destruye un
    // contexto sano. Si la sesión XR lo suspende, el kick() recreativo de los
    // gatillos/grips lo recupera dentro del propio gesto del mando.
    this.audio.prepareVR();
    this.pendingCalib = !!startCalib;
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
    const session = this.renderer.xr.getSession?.();
    if (session && !this.__audioHooks) {
      this.__audioHooks = true;
      const kickAudio = () => this.audio.kick();
      session.addEventListener('selectstart', kickAudio);
      session.addEventListener('squeezestart', kickAudio);
      session.addEventListener('inputsourceschange', kickAudio);
    }
    this.hapticProbe();
    this.rules.startMatch();
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

    // en modo ajuste, el gatillo lanza una bola de entrenamiento
    if (this.calib) {
      const now = performance.now() / 1000;
      if (now - this.lastFeedTap > 0.3) {
        this.lastFeedTap = now;
        this.feedPracticeBall();
      }
      return;
    }
    if (this.rules.state === 'over') {
      this.rules.startMatch();
      this.resetToss();
      return;
    }
    // gatillo en la mano de la bola = saque asistido (con impulso mínimo)
    if (this.rules.state === 'serve' && this.rules.server === 'player' && !this.tossed && i === this.ballHand) {
      this.tossFromHand(i, true);
    }
  }

  /** Suelta la bola con la velocidad REAL de la mano (saque natural). */
  releaseBallHand(i) {
    if (this.calib) return;
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
    this.rules.message = '¡Golpea al oír el pitido (punto muerto) o al caer!';
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
    // partida (proximidad del visor, notificación...), se reactiva solo
    this.audio.watchdog(dt);
    this.audioStatus.update(this.audio.ctx?.state || 'none');

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

    // 2) IA(s)
    const canHit = this.rules.state === 'rally';
    const playerPad = this.controllerPaddles[this.paddleHand];
    const oppPadX = presenting
      ? (playerPad.active ? playerPad.pos.x : 0)
      : this.demoAI.pos.x;
    const aiServing = !this.calib && this.rules.state === 'serve' && this.rules.server === 'ai';
    const aiHit = this.calib ? null : this.ai.update(dt, this.ball, {
      canHit,
      validBounce: this.rules.validBounce,
      oppPadX,
      holdTarget: aiServing ? this.aiServeStance : null,
    });
    let demoHit = null;
    if (!presenting) {
      const demoServing = !this.calib && this.rules.state === 'serve' && this.rules.server === 'player';
      demoHit = this.demoAI.update(dt, this.ball, {
        canHit,
        validBounce: this.rules.validBounce,
        oppPadX: this.ai.pos.x,
        holdTarget: demoServing ? this.demoServeStance : null,
      });
    }
    if (aiHit) {
      this.ball.vel.copy(aiHit);
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
    if (!holdLock) {
      const pads = [];
      if (presenting) {
        const ps = this.controllerPaddles[this.paddleHand];
        if (ps.active) pads.push(ps);
      }
      stepPhysics(dt, this.ball, pads, this.events);
    }

    // 5) Golpe de saque del jugador: validar regla ITTF (con margen amplio)
    if (presenting && !this.calib && this.tossed && this.rules.state === 'serve' && this.rules.server === 'player') {
      for (const e of this.events) {
        if (e.type !== 'paddle' || e.who !== 'player') continue;
        if (this.preVy > 0.6) {          // margen ±60 ms alrededor del punto muerto
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Golpea la bola en el punto muerto o al caer';
          break;
        }
        if (this.tossMaxY - this.tossReleaseY < DIMS.tossMinRise) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Lanza la bola al menos 16 cm hacia arriba';
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

    // 6) Reglas y eventos (en modo ajuste: sin marcador, solo físicas y sonido)
    if (!this.calib) {
      this.processIntents(this.rules.handleEvents(this.events));
      this.processIntents(this.rules.update(dt));
    }
    this.processEvents(this.events);
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
    this.trailUpdate();
    this.updateBlobShadow();

    // poses de las palas IA: postura natural, saque con toss y swing real
    this.aiStrikeT = Math.max(0, this.aiStrikeT - dt);
    this.demoStrikeT = Math.max(0, this.demoStrikeT - dt);
    this.updateAIPaddlePose(this.aiPaddleMesh, this.ai, 'ai', dt);
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
    this.confetti.update(dt, this.fanfareBanner.group.visible && this.fanfareWin);

    if (this.calib && this.panelDirty) {
      this.calibPanel.update({ name: this.gripName, off: this.gripOffset });
      this.panelDirty = false;
    }
    this.scoreboardUpdate({
      player: this.rules.scorePlayer,
      ai: this.rules.scoreAi,
      server: this.rules.server,
      message: this.calib ? 'ENTRENAMIENTO · Y: volver al partido' : this.rules.message,
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
    this.aiServeStance.set(
      x + s * 0.17, 1.0,
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
      x + s * 0.17, 1.0,
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
   * Pose de la pala de la IA. Nada de lookAt hacia la bola: con la bola justo
   * encima (fase de saque) lookAt es degenerado y volteaba la pala mostrando
   * el canto. Ahora la orientación es por euler con yaw limitado y pitch
   * acotado, y el saque tiene animación completa: postura lateral con la cara
   * abierta -> swing acelerado hasta el punto de contacto -> cara cerrada.
   */
  updateAIPaddlePose(mesh, ai, who, dt) {
    const s = ai.sign;                       // -1 = CPU, +1 = demo
    const faceYaw = s < 0 ? 0 : Math.PI;     // mirar hacia el campo contrario
    const stance = who === 'ai' ? this.aiServeStance : this.demoServeStance;
    const spot = who === 'ai' ? this.aiServeSpot : this.demoServeSpot;
    const toss = who === 'ai' ? this.aiToss : this.demoToss;
    const strikeT = who === 'ai' ? this.aiStrikeT : this.demoStrikeT;
    const serving = !this.calib && this.rules.state === 'serve' && this.rules.server === who;

    // postura base: cara hacia el rival, levemente cerrada; sigue la bola solo
    // en horizontal y con el pitch acotado (sin volteos ni canto visible)
    poseD.copy(this.ball.pos).sub(ai.pos);
    let yaw = Math.atan2(poseD.x, poseD.z);
    let dy = yaw - faceYaw;
    while (dy > Math.PI) dy -= 2 * Math.PI;
    while (dy < -Math.PI) dy += 2 * Math.PI;
    yaw = faceYaw + THREE.MathUtils.clamp(dy, -1.15, 1.15);
    const hd = Math.hypot(poseD.x, poseD.z);
    const pitch = THREE.MathUtils.clamp(-Math.atan2(poseD.y, Math.max(0.05, hd)) * 0.5, -0.55, 0.4) + 0.14;
    poseE.set(pitch, yaw, 0, 'YXZ');
    poseQ.setFromEuler(poseE);

    if (serving) {
      if (toss) {
        // swing: de la postura abierta (arriba-atrás) al contacto con la bola
        const p = 1 - Math.max(0, toss.timer) / AI_TOSS_T;
        const e = Math.pow(p, 1.7);            // aceleración natural del brazo
        const bx = spot.x + s * 0.24;
        const by = spot.y + 0.15;
        const bz = spot.z + s * 0.12;
        const cx = this.ball.pos.x + s * 0.05;
        const cy = this.ball.pos.y - 0.02;
        const cz = this.ball.pos.z + s * 0.05;
        poseE.set(-0.8 + 0.98 * e, faceYaw, 0, 'YXZ');
        poseQ.setFromEuler(poseE);
        mesh.position.set(bx + (cx - bx) * e, by + (cy - by) * e, bz + (cz - bz) * e);
        mesh.quaternion.copy(poseQ);
        this.clampPaddlePose(mesh.position, mesh.quaternion, false);
        return;
      }
      if (strikeT > 0) {
        // instante del impacto: cara ligeramente cerrada junto a la bola
        mesh.position.set(
          this.ball.pos.x + s * 0.05,
          this.ball.pos.y - 0.03,
          this.ball.pos.z + s * 0.05,
        );
        poseE.set(0.18, faceYaw, 0, 'YXZ');
        poseQ.setFromEuler(poseE);
        mesh.quaternion.copy(poseQ);
        this.clampPaddlePose(mesh.position, mesh.quaternion, false);
        return;
      }
      // preparación: pala al lado de la bola, cara abierta hacia arriba
      mesh.position.copy(stance);
      poseE.set(-0.5, faceYaw, 0, 'YXZ');
      poseQ.setFromEuler(poseE);
      mesh.quaternion.copy(poseQ);
      this.clampPaddlePose(mesh.position, mesh.quaternion, false);
      return;
    }

    // rally / espera
    mesh.position.set(ai.pos.x, ai.pos.y, ai.pos.z);
    mesh.quaternion.slerp(poseQ, Math.min(1, dt * 9));
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
        case 'point':
          this.audio.point(it.winner === 'player');
          if (this.renderer.xr.isPresenting) {
            this.haptic(this.paddleHand, it.winner === 'player' ? 0.85 : 0.4, it.winner === 'player' ? 110 : 60);
          }
          break;
        case 'retry-serve':
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (this.rules.server === 'ai') this.setupAIServe();
          else this.setupDemoServe();
          break;
        case 'serve':
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (it.server === 'ai') this.setupAIServe();
          else this.setupDemoServe();
          break;
        case 'game-over':
          this.startFanfare(it.winner === 'player');
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
  // gancho de depuración para pruebas headless (física de saque y constantes)
  window.__ppDebug = { findServeVelocity, simulateServePath, DIMS };

  // Compatibilidad WebXR
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr')
      .then((ok) => {
        if (ok) {
          vrbtn.disabled = false;
          trainBtn.disabled = false;
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
});

spectateBtn.addEventListener('click', () => {
  overlay.classList.add('hidden');
  hud.classList.add('show');
});
hudInfo.addEventListener('click', () => {
  overlay.classList.remove('hidden');
});

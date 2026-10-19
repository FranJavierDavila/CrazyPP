export class PingPongGame {
  constructor(canvas, paddleModel, callbacks = {}) {
    this.canvas = canvas;
    this.callbacks = callbacks;
    this.disposed = false;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,   // necesario para passthrough (immersive-ar)
      powerPreference: 'high-performance',
      // v2.84 (AUDITORÍA DE RENDIMIENTO): preserveDrawingBuffer forzaba al
      // driver a COPIAR el framebuffer cada frame en lugar de descartarlo —
      // coste real de memoria en GPUs móviles (Quest). El juego NO lo usa
      // para nada; solo lo necesitan las capturas de los tests headless,
      // que activan window.__PP_KEEP_FRAMEBUFFER antes de arrancar.
      preserveDrawingBuffer: typeof window !== 'undefined' &&
        (window.__PP_KEEP_FRAMEBUFFER === true || window.__pp2DPlay === true),
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight, false);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.xr.enabled = true;
    this.renderer.xr.setReferenceSpaceType('local-floor');
    // v3.6.6 (ronda 10 · AUDITORÍA DE FPS): la telemetría vr_end midió 38
    // fps de media en sesión larga — GPU saturada por nitidez máxima
    // (1.7× = ~2.9× píxeles/ojo + foveation 0 + sombras PCFSoft 2048²).
    // v3.6.11 (ronda 14 · REVERSIÓN POR DATOS): la regla pre-comprometida
    // («media < 72 → volver a 1.4») se cumplió en la 1.ª sesión real en
    // 3.6.10: vr_end 63 fps de media (41-82) en 8,9 min con el 1.5×,
    // frente a 78 (63-88) en 4,1 min con el 1.4× (y 55 en 49 min con
    // 1.4× en la 3.6.7). Fluidez primero: se vuelve a 1.4× «Extra
    // Sharpness» + foveation 0.5. Si el dueño prefiere nitidez sobre
    // fluidez, el compromiso intermedio (1.45) o el escalado adaptativo
    // son el siguiente paso POR DATOS (con la curva vr_ping delante).
    this.renderer.xr.setFoveation(0.5);
    this.renderer.xr.setFramebufferScaleFactor(1.4);

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
    // v2.50 · FASE 1 · CONFORO: háptica desactivable + consejos de 1ª vez
    try { this.hapticsOn = localStorage.getItem('pp_hapt') !== '0'; } catch { this.hapticsOn = true; }
    try { this.showTips = localStorage.getItem('pp_tips_v1') !== '0'; } catch { this.showTips = true; }
    this._tipsIdx = -1;          // -1 = sin ciclo activo; 0..2 = consejos; 3 = despedida
    this._tipsTimer = 0;
    // MULTIJUGADOR ONLINE (v2.19): P2P por WebRTC (PeerJS) + voz
    this.net = new NetLink(this);
    this.menuPage = 'main';       // 'main' | 'multi' | 'join' | 'name' | 'rank'
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

    // v3.0.9-HALL1 · la dificultad SE RECUERDA entre sesiones (y con ella
    // el nivel de asistencia del saque: fácil más ayuda, difícil menos).
    this.difficulty = (() => {
      try {
        const d = localStorage.getItem('ppxr_dif');
        return (d === 'easy' || d === 'medium' || d === 'hard') ? d : 'medium';
      } catch (e) { return 'medium'; }
    })();
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
    this.freezeT = 0;              // v2.40: s restantes de PARTIDA CONGELADA
                                   // (anuncio épico del superpoder del rival)
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
    // v2.38: la mesa se guarda — la prueba ARKANOID la sustituye por el muro
    this.tableGroup = createTable();
    this.rig.add(this.tableGroup);

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
    this.scoreboardGroup = sb.group;   // v2.38: ocultable durante ARKANOID
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
    // v2.69 · CAMPEONATOS = CARPETAS: La Locura vive en championships/
    // locura/ y ChampLoader la descubre, importa y arranca igual que
    // cualquier otro campeonato. El núcleo YA NO CONOCE campeonato alguno:
    // todos los ganchos (partida, pruebas, pistola, bola doble, menú,
    // reinicio) pasan por los métodos genéricos de ChampLoader.
    // v2.53: campeonatos externos en carpetas (clones de la estructura de
    // La Locura). Cargador mínimo: índice + import() + los mismos ganchos.
    this.champs = new ChampLoader(this);
    // v2.80 · TROQUELES DE CARTÓN del campeonato ACTIVO (decorado POR
    // campeonato: el módulo declara su config en «decor» y el núcleo la
    // monta aquí, anclada a la mesa en el RIG — lección v2.62). Al cambiar
    // de campeonato el set se destruye y se construye el nuevo; un módulo
    // sin «decor» deja la sala limpia. En createChampDecor está el detalle.
    this.champDecor = createChampDecor(this);
    this.rig.add(this.champDecor.group);
    this.champDecorHidden = false;   // v2.95: las PRUEBAS lo activan
    // v2.85 · DECORADO DE SALA («room») del campeonato ACTIVO: mismo
    // contrato que champDecor pero vistiendo los 6 PLANOS de la sala
    // (suelo, techo y 4 paredes). Sin grupo propio: opera sobre los
    // materiales de roomGroup creados en createRoom(). En update está
    // el refuerzo por frame; clearRoom() restaura el tema del jugador.
    this.champRoom = createChampRoom(this);

    // v3.0.9-HALL1 · HALL DEL ANFITRIÓN: estancia de bienvenida decorada
    // con logros. Nace OCULTA: enterHall() la enciende al entrar en VR y
    // exitHall() la apaga al salir a la cancha (nunca ambas a la vez).
    this.hallGroup = createHall();
    this.hallGroup.visible = false;
    this.scene.add(this.hallGroup);
    this.inHall = false;
    // v2.30: FUERA el mini-indicador "♪ audio" bajo el marcador — era un
    // estímulo de depuración que desconcentraba al jugador (el diagnóstico
    // del audio sigue disponible vía consola/tereados, no en el campo visual).
  }

  setupControllers() {
    this.paddleMounts = [];
    this.gunMounts = [];     // v2.38: monturas de la pistola por mando
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

      // v2.38: pistola de rayos (superpoder ARKANOID) en el mando libre —
      // espacio grip SIN cuaternión de pala: cañón hacia -Z, mango abajo
      const gunMount = new THREE.Group();
      gunMount.visible = false;
      grip.add(gunMount);
      this.gunMounts.push(gunMount);

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

  /** v3.0.3 · Cierra el PRO TRAINING si siguiera abierto (MÓDULOS ESTANCOS):
   *  lo invocan el cambio de modo, la entrada en VR y el arranque de un
   *  campeonato — el entrenamiento NUNCA contamina a otro módulo. */
  closeTrainingV3() {
    const trn = (typeof window !== 'undefined') && window.__PP_TRAIN;
    if (trn && (this.trainV3 || this.trainV3Hub)) {
      this.trainV3 = null;
      this.trainV3Hub = false;
      try { trn.teardown(this); } catch (e) { /* nunca rompe */ }
    }
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
    // v3.0.3 · ESTANQUEIDAD: si el entrenamiento V3 seguía abierto (salida
    // directa), se recoge SU escena completa (marcas/panel/máquina) antes de
    // restaurar el modo — nunca más paneles del entrenamiento flotando en
    // un partido o en un campeonato.
    const trnX = (typeof window !== 'undefined') && window.__PP_TRAIN;
    if (trnX && (this.trainV3 || this.trainV3Hub)) {
      this.trainV3 = null;
      this.trainV3Hub = false;
      try { trnX.teardown(this); } catch (e) { /* nunca rompe */ }
    }
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
    this.closeTrainingV3();   // v3.0.3 · estanqueidad
    if (this.calib || this.mode === mode) return;
    this.exitHall();          // v3.1.0-SRV2: arrancar un modo saca del hall
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
    this.exitHall();          // v3.1.0-SRV2: la sesión online se juea en la cancha
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
    if (this.trainV3) return;   // v3.0: PRO TRAINING lleva su propia rutina (máquina/jueces)
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
    // v2.31 · RE-VÍNCULO DENTRO DEL GESTO (capa principal del rescate de
    // audio en VR): requestSession+setSession resuelven todavía dentro de la
    // ventana de activación del tap sobre JUGAR EN VR. Un contexto creado
    // AQUÍ nace 'running' y ligado a la salida vigente (el casco). Si
    // sessionstart ya adoptó uno 'running', vrBound lo evita: no hay churn.
    if (!this.audio.vrBound) {
      this.audio.rebind('entrada en VR: contexto dentro del gesto de solicitud');
    }
    this.audio.nudgeSink();
    // Primer gatillo de la sesión = segunda oportunidad dentro de gesto real:
    // los hooks XR (selectstart/squeezestart) llaman gestureKick(), que
    // re-crea el contexto si sigue sin estar confirmado (vrBound).
  }

  setDifficulty(d) {
    this.difficulty = d;
    try { localStorage.setItem('ppxr_dif', d); } catch (e) { /* almacenamiento no disponible */ }
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
      // v2.85: las 4 paredes tienen material propio (mismo color de tema);
      // con room del campeonato activo, champRoom vuelve a forzar blanco.
      if (ud.wallMats) { for (const wm of ud.wallMats) wm?.color.set(t.wall); }
      else ud.wallMat?.color.set(t.wall);
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
    // v3.0.1 · sello de versión en TODAS las páginas del menú (bajo las palas
    // de idioma, franja libre y 168-198): el dueño verifica la build EN EL CASCO.
    c.fillStyle = 'rgba(255,210,87,0.88)';
    c.font = '700 17px system-ui, sans-serif';
    c.textAlign = 'right';
    c.textBaseline = 'alphabetic';
    c.fillText('V' + (typeof window !== 'undefined' && window.__PP_VERSION ? window.__PP_VERSION : '3.0.4-EXP.TV1'), 996, 190);
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

  /** v2.66 · Página TU NOMBRE: teclado 7×4 (A–Z + espacio + ⌫), caja con
   *  el nombre en curso y guardar/volver. El nombre preside el ranking. */
  drawMenuName(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    this.drawMenuHeader(rects);
    label(T('name_title'), 240, 26);
    // caja del nombre (12 caracteres máximo) con cursor fino
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    const nm = this._nameBuf || '';
    c.beginPath();
    if (c.roundRect) c.roundRect(112, 268, 800, 112, 16);
    else c.rect(112, 268, 800, 112);
    c.fillStyle = 'rgba(255,255,255,0.06)';
    c.fill();
    c.strokeStyle = '#e8b45a';
    c.lineWidth = 5;
    c.stroke();
    c.fillStyle = '#f2f4f6';
    c.font = '800 64px ui-monospace, monospace';
    c.fillText(nm + '_', 512, 324);
    c.fillStyle = '#75828f';
    c.font = '600 22px system-ui, sans-serif';
    c.fillText(nm.length + ' / 12', 512, 402);
    // teclado 7×4: 26 letras + ␣ + ⌫
    for (let i = 0; i < CHARS.length; i++) {
      const col = i % 7, row = Math.floor(i / 7);
      btn('nkey:' + CHARS[i], 56 + col * 128, 430 + row * 96, 118, 86, CHARS[i], false, undefined, undefined, 34);
    }
    btn('nkey:sp', 56 + 5 * 128, 430 + 3 * 96, 118, 86, '␣', false, undefined, undefined, 34);
    btn('nkey:del', 56 + 6 * 128, 430 + 3 * 96, 118, 86, '⌫', false, undefined, undefined, 34);
    // v2.108: fila de DÍGITOS bajo las letras (86 px de ancho, paso 90) —
    // nombres con números (p.ej. FORO3D del modo depuración, «Juan2»…).
    // Termina en x≈956 y y≈892: no roza ni las letras (fin 804) ni los
    // botones GUARDAR/VOLVER (y 940).
    for (let d = 0; d <= 9; d++) {
      btn('nkey:' + d, 56 + d * 90, 814, 86, 78, String(d), false, undefined, undefined, 30);
    }
    btn('nkey:ok', 56, 940, 448, 82, T('name_save'), true, 'green', undefined, 28);
    btn('nkey:cancel', 520, 940, 448, 82, T('btn_back'), false, undefined, undefined, 28);
    label(T('name_hint'), 1080, 20, '#75828f', 'center');
    btn('tab:main', 56, 1380, 912, 76, '◀  ' + T('btn_back'), false, undefined, undefined, 28);
  }

  /** v2.67 · Página RANKING MUNDIAL: top 10 por campeonato con nombre,
   *  puntos y logros al lado. Desplegable ‹ › para elegir el campeonato
   *  (La Locura = victorias; magia = puntos) y ↻ para revalidar. Sin
   *  conexión muestra el último ranking guardado en caché local. */
  drawMenuRank(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    this.drawMenuHeader(rects);
    label(T('sec_rank'), 240, 26);

    // v2.125: el campeonato de portada manda (eager del índice), no un literal
    const _portada = this.champs ? this.champs.portadaId : 'locura';
    const ids = [_portada].concat(this.champs ? this.champs.list().map((x) => x.id) : [])
      .filter((v, i, a2) => a2.indexOf(v) === i);
    if (!this._wrlChamp || !ids.includes(this._wrlChamp)) this._wrlChamp = ids[0];
    const wrLabel = (id) => {
      if (id === _portada) return T('arc_title');
      const ch = this.champs && this.champs.list().find((x) => x.id === id);
      // ch.label llega como '▶  TÍTULO': se quita el prefijo para el chip
      return ch ? String(ch.label).replace(/^▶\s*/, '') : String(id).toUpperCase();
    };
    // v2.70: todos los campeonatos puntúan por VICTORIAS (arquitectura común)
    const ptsLbl = T('wrl_wins');

    // desplegable ‹ campeonato ›
    btn('wrl:left', 56, 268, 110, 68, '‹', false, undefined, undefined, 40);
    btn('wrl:right', 858, 268, 110, 68, '›', false, undefined, undefined, 40);
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.beginPath();
    if (c.roundRect) c.roundRect(178, 268, 668, 68, 14); else c.rect(178, 268, 668, 68);
    c.fillStyle = 'rgba(232,180,90,0.14)';
    c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.5)';
    c.lineWidth = 2;
    c.stroke();
    c.fillStyle = '#ffd257';
    c.font = '800 25px system-ui, sans-serif';
    c.fillText(wrLabel(this._wrlChamp), 512, 303);

    // cabecera de columnas
    c.fillStyle = '#75828f';
    c.font = '700 20px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('wrl_col_name'), 150, 372);
    c.textAlign = 'right';
    c.fillText(ptsLbl, 872, 372);
    c.fillText(T('wrl_col_logros'), 986, 372);

    // filas top 10
    const rows = WORLDRANK.list(this._wrlChamp).slice(0, 10);
    const my = (ppPlayerName() || '').toLowerCase();
    for (let i = 0; i < 10; i++) {
      const e = rows[i];
      const ry = 396 + i * 48;
      if (!(i % 2)) {
        c.beginPath();
        if (c.roundRect) c.roundRect(56, ry - 3, 912, 44, 10); else c.rect(56, ry - 3, 912, 44);
        c.fillStyle = 'rgba(255,255,255,0.045)';
        c.fill();
      }
      c.textBaseline = 'middle';
      c.textAlign = 'left';
      const isMe = !!(e && my && e.n.toLowerCase() === my);
      c.font = '700 24px system-ui, sans-serif';
      c.fillStyle = e ? '#cfd8e0' : '#4a5560';
      c.fillText(String(i + 1), 74, ry + 19);
      c.font = (isMe ? '800 ' : '600 ') + '25px system-ui, sans-serif';
      c.fillStyle = isMe ? '#ffd257' : (e ? '#f2f4f6' : '#4a5560');
      const nm = e ? e.n : '—';
      c.fillText(nm.length > 15 ? nm.slice(0, 14) + '…' : nm, 150, ry + 19);
      if (isMe) {
        c.fillStyle = '#e8b45a';
        c.font = '800 18px system-ui, sans-serif';
        c.fillText(T('wrl_you'), 452, ry + 20);
      }
      c.textAlign = 'right';
      c.font = '800 25px system-ui, sans-serif';
      c.fillStyle = e ? '#9fe088' : '#4a5560';
      c.fillText(e ? String(e.p) : '·', 872, ry + 19);
      c.font = '700 23px system-ui, sans-serif';
      c.fillStyle = e ? '#ffd257' : '#4a5560';
      // v2.75: los CAMPEONES (a === '🏆') lucen SU insignia del campeonato
      // en la columna LOGROS; el resto queda exactamente igual.
      const _bg = e && e.a === '🏆' ? wrlBadgeImg(this._wrlChamp) : null;
      if (_bg && _bg.complete && _bg.naturalWidth > 0) {
        const _s = 38 / Math.max(_bg.naturalWidth, _bg.naturalHeight);
        const _w = _bg.naturalWidth * _s, _h = _bg.naturalHeight * _s;
        c.drawImage(_bg, 986 - _w / 2, ry + 19 - _h / 2, _w, _h);
      } else {
        c.fillText(e ? (e.a || '·') : '·', 986, ry + 19);
      }
    }

    // estado de la conexión + botón de refresco
    let stTxt = T('wrl_loading');
    let stCol = '#e8b45a';
    if (WORLDRANK.status === 'online') { stTxt = T('wrl_online'); stCol = '#93c97e'; }
    else if (WORLDRANK.status === 'offline') { stTxt = T('wrl_offline'); stCol = '#f0873f'; }
    c.textAlign = 'left';
    c.textBaseline = 'middle';
    c.fillStyle = stCol;
    c.font = '600 20px system-ui, sans-serif';
    c.fillText(stTxt, 70, 914);
    btn('wrl:refresh', 700, 882, 268, 62, T('wrl_refresh'), false, undefined, undefined, 22);

    // sin nombre: recordatorio de que puede firmar sus registros
    if (!ppPlayerName()) label(T('wrl_need_name'), 966, 19, '#75828f', 'center');
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
    // v2.66: página TU NOMBRE (teclado en pantalla, igual que 'join')
    if (this.menuPage === 'name') {
      this.drawMenuName(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    // v2.67: página RANKING MUNDIAL (top 10 por campeonato)
    if (this.menuPage === 'rank') {
      this.drawMenuRank(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    // v2.110 · páginas del HUB: CAMPEONATOS y AJUSTES
    if (this.menuPage === 'champs') {
      this.drawMenuChamps(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    if (this.menuPage === 'opts') {
      this.drawMenuOpts(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    // v3.1.1-FEEL1 · página PROMPT «Menú Principal ¿SI/No?» (botón B fuera
    // del hall): panel mínimo con las dos respuestas, sin acordeón ni secciones.
    if (this.menuPage === 'hallask') {
      this.drawMenuHallAsk(rects);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    // v3.0 · PRO TRAINING: páginas del hub de entrenamiento
    if (this.menuPage === 'train' && window.__PP_TRAIN) {
      window.__PP_TRAIN.drawHub(this, c, rects, this._menuBtn, this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }
    if (this.menuPage === 'trainarea' && window.__PP_TRAIN) {
      window.__PP_TRAIN.drawArea(this, c, rects, this._menuBtn, this._menuLabel);
      this.menuRects = rects;
      this._menuState = this.rules.state;
      this.menuTex.needsUpdate = true;
      return;
    }

    this.drawMenuHeader(rects);

    // ---------- v2.110 · HUB DE MODOS ----------
    // Tarjetas grandes con ACCESO DIRECTO a cada modo (adiós acordeón):
    // Partido · Entrenar · Supervivencia · Multijugador · Campeonatos ·
    // Ranking. Debajo, dificultad de la CPU y AJUSTES RÁPIDOS; TODAS las
    // opciones siguen vivas: las completas en la página AJUSTES y en las
    // páginas propias (Multijugador, Campeonatos, Ranking, Tu nombre).
    this.drawMenuHub(rects);

    this.menuRects = rects;
    this._menuState = this.rules.state;
    this.menuTex.needsUpdate = true;
  }

  /* ================== v2.110 · MENÚ HUB ==================
   * El feedback fue claro: el acordeón quedó «lioso» y con demasiadas
   * opciones a la vista. Ahora el menú es un HUB de TARJETAS grandes,
   * cada una un ACCESO DIRECTO a un modo, con icono, color propio y una
   * sola línea de contexto. La dificultad de la CPU queda a la vista
   * (afecta a PARTIDO) y los mandos frecuentes en AJUSTES RÁPIDOS; el
   * resto de opciones NO desaparece: vive en la página AJUSTES y en las
   * páginas propias (Multijugador, Campeonatos, Ranking, Tu nombre). */

  /** Tarjeta de modo: degradado + insignia circular con icono + títulos. */
  _modeCard(rects, id, x, y, w, h, title, sub, g0, g1, icon, gold) {
    const c = this.menuCanvas.getContext('2d');
    const hovered = this.menuHover.includes(rects.length);
    c.beginPath();
    if (c.roundRect) c.roundRect(x, y, w, h, 22); else c.rect(x, y, w, h);
    const g = c.createLinearGradient(x, y, x, y + h);
    g.addColorStop(0, g0);
    g.addColorStop(1, g1);
    c.fillStyle = g;
    c.fill();
    c.strokeStyle = hovered ? '#ffffff'
      : (gold ? 'rgba(255,210,87,0.85)' : 'rgba(255,255,255,0.24)');
    c.lineWidth = hovered ? 5 : 2;
    c.stroke();
    // insignia circular con el icono del modo
    const cx = x + 76, cy = y + h / 2;
    c.beginPath(); c.arc(cx, cy, 50, 0, Math.PI * 2);
    c.fillStyle = 'rgba(0,0,0,0.30)'; c.fill();
    c.strokeStyle = 'rgba(255,255,255,0.4)'; c.lineWidth = 2.5; c.stroke();
    try { icon(c, cx, cy); } catch (e) { /* icono decorativo */ }
    // títulos (v2.110: AUTOAJUSTE — el título nunca pisa el chevron y el
    // subtítulo se recorta con ellipsis; mismas reglas en todos los modos)
    c.textAlign = 'left';
    c.textBaseline = 'alphabetic';
    const avail = w - 134 - 58;
    let fs = 36;
    c.font = '800 ' + fs + 'px system-ui, sans-serif';
    while (fs > 24 && c.measureText(title).width > avail) {
      fs -= 2;
      c.font = '800 ' + fs + 'px system-ui, sans-serif';
    }
    c.fillStyle = '#ffffff';
    c.fillText(title, x + 134, y + h / 2 - 4);
    let sub2 = sub || '';
    c.font = '600 19px system-ui, sans-serif';
    if (c.measureText(sub2).width > avail) {
      while (sub2.length > 1 && c.measureText(sub2 + '…').width > avail) {
        sub2 = sub2.slice(0, -1);
      }
      sub2 += '…';
    }
    c.fillStyle = 'rgba(255,255,255,0.85)';
    c.fillText(sub2, x + 134, y + h / 2 + 30);
    // chevron ›
    c.fillStyle = 'rgba(255,255,255,0.85)';
    c.beginPath();
    c.moveTo(x + w - 46, y + h / 2 - 15);
    c.lineTo(x + w - 26, y + h / 2);
    c.lineTo(x + w - 46, y + h / 2 + 15);
    c.closePath(); c.fill();
    rects.push({ x, y: y - 3, w, h: h + 6, id });
  }

  /** v3.1.1-FEEL1 · página del PROMPT B: «MENÚ PRINCIPAL — ¿SI / No?».
   *  SI  => goHomeHall() (recoger todo + hall con el menú principal delante).
   *  NO  => cerrar el prompt y seguir en la escena actual, tal cual.
   *  Sin botón «cerrar»: NO ya cierra, y B también la cierra. */
  drawMenuHallAsk(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;

    // título
    label(T('hallask_title'), 240, 54, '#e8b45a', 'center');
    label(T('hallask_sub'), 310, 28, '#9aa7b4', 'center');
    // separador fino
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 2;
    c.beginPath(); c.moveTo(132, 360); c.lineTo(892, 360); c.stroke();

    // las dos respuestas, grandes y sin ambigüedad
    btn('hallask_si', 132, 470, 760, 170, T('hallask_yes_btn'), true, 'green', undefined, 46);
    btn('hallask_no', 132, 700, 760, 170, T('hallask_no_btn'), false, undefined, undefined, 46);

    // ayuda
    label(T('hallask_hint'), 940, 22, '#5c6672', 'center');
    this.menuRects = rects;
    this._menuState = this.rules.state;
    this.menuTex.needsUpdate = true;
  }

  /** Página principal: el HUB. 6 tarjetas (2×3) + dificultad + tarjeta
   *  AJUSTES contraída (v2.123: el dock de AJUSTES RÁPIDOS se retiró — el
   *  apartado de opciones va plegado y con la MISMA estética que el resto;
   *  todo su contenido sigue vivo en la página AJUSTES). */
  drawMenuHub(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const over = this.rules.state === 'over';
    const diffName = { easy: T('diff_easy_btn'), medium: T('diff_medium_btn'),
      hard: T('diff_hard_btn') }[this.difficulty] || '';

    this.drawMenuHeader(rects);

    const CW = 456, CH = 176, GX = 32, GY = 18;
    const X0 = 40, X1 = X0 + CW + GX;
    let y = 240;
    // fila 1 · PARTIDO — ENTRENAR
    this._modeCard(rects, 'start', X0, y, CW, CH, T('hub_match'),
      over ? T('btn_rematch') : T('hub_vs', { v: diffName }),
      '#2f9e44', '#1e7c33', PP_ICONS.match);
    this._modeCard(rects, 'traingo', X1, y, CW, CH, T('sec_train'),
      T('hub_train_sub'), '#1c7ed6', '#145c9e', PP_ICONS.train);
    y += CH + GY;
    // fila 2 · SUPERVIVENCIA — MULTIJUGADOR
    this._modeCard(rects, 'survgo', X0, y, CW, CH, T('sec_surv'),
      this.survivalBest > 0 ? T('best_surv', { n: this.survivalBest })
        : T('hub_surv_sub'),
      '#e8590c', '#b0420a', PP_ICONS.surv);
    this._modeCard(rects, 'tab:multi', X1, y, CW, CH, T('hub_multi'),
      this.net.online ? T('hub_multi_on', { c: this.net.code })
        : T('hub_multi_sub'),
      '#7048e8', '#4c2bb0', PP_ICONS.multi);
    y += CH + GY;
    // fila 3 · CAMPEONATOS — RANKING MUNDIAL
    this._modeCard(rects, 'page:champs', X0, y, CW, CH, T('sec_crazy'),
      (this.champs && this.champs.menuHint()) || T('hub_champ_sub'),
      '#b8860b', '#7c5a08', PP_ICONS.champ, true);
    this._modeCard(rects, 'wrl:open', X1, y, CW, CH, T('sec_rank'),
      WORLDRANK.status === 'online' ? T('wrl_online') : T('hub_rank_sub'),
      '#0ca678', '#087354', PP_ICONS.rank);
    y += CH + GY;

    // dificultad de la CPU (afecta a PARTIDO) — siempre visible
    label(T('hub_diff'), y + 24, 22, '#9aa7b4', 'center');
    btn('diff:easy', 56, y + 46, 292, 60, T('diff_easy_btn'),
      this.difficulty === 'easy', undefined, undefined, 25);
    btn('diff:medium', 366, y + 46, 292, 60, T('diff_medium_btn'),
      this.difficulty === 'medium', undefined, undefined, 25);
    btn('diff:hard', 676, y + 46, 292, 60, T('diff_hard_btn'),
      this.difficulty === 'hard', undefined, undefined, 25);

    y += 130;

    // v3.1.0-SRV2 · EL HALL ES EL HUB: en plena partida (o campeonato) el
    // menú ofrece la vuelta a la estancia del anfitrión — el hall es donde
    // se cambian ajustes y modalidad. En el propio hall NO aparece (ya
    // estás en casa) ni en online (el hall no existe allí).
    if (!this.inHall && !this.net.online) {
      btn('homehall', 40, y, 944, 64, T('hall_home_btn'), false, undefined, undefined, 27);
      c.fillStyle = '#5c6672';
      c.font = '500 17px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(T('hall_home_hint'), 512, y + 80);
      y += 100;
    }

    // v2.123 · OPCIONES CONTRAÍDAS: una sola TARJETA (misma estética que el
    // resto del HUB) que abre la página AJUSTES, donde vive TODO: sala,
    // música, ambiente, megáfono, vibración, estela, consejos, nombre…
    // El subtítulo resume el estado vivo para no perder info de un vistazo.
    const yn = (v) => (v ? T('yes') : T('no'));
    const short = (k) => T(k, { v: yn(true) }).split(':')[0];
    const themeDef = ROOM_THEMES.find((t) => t.key === this.theme);
    const themeName = themeDef ? (themeDef.nameKey ? T(themeDef.nameKey) : themeDef.name) : '';
    const optsSub = (themeName ? themeName + ' · ' : '')
      + short('btn_music') + ': ' + yn(this.audio.musicOn)
      + ' · ' + T('dock_mic') + ': ' + yn(this.audio.voice);
    this._modeCard(rects, 'page:opts', 40, y, 944, CH, T('opts_title'), optsSub,
      '#5f7183', '#43525f', PP_ICONS.opts);

    // cierre + ayuda
    btn('close', 56, y + CH + 28, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
    c.fillStyle = '#5c6672';
    c.font = '500 20px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('menu_hint'), 512, y + CH + 124);
  }

  /** v2.110 · página CAMPEONATOS: música global + TARJETA por campeonato
   *  (insignia + récord) con sus controles propios debajo (igual que en el
   *  acordeón: música, atajos de pruebas, récord… los declare el módulo). */
  drawMenuChamps(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    this.drawMenuHeader(rects);
    btn('page:main', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);
    c.fillStyle = '#ffd257';
    c.font = '900 42px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('page_champs'), 664, 246);

    let y = 304;
    // música global de los campeonatos (v2.78 — mismo canal del núcleo)
    const AM = this.audio;
    label(T('arc_music_global'), y + 10, 22);
    y += 32;
    btn('chmus:off', 56, y, 316, 58,
      AM.arcMute ? T('arc_music_muted') : '♪ ' + T('yes'), !AM.arcMute,
      undefined, undefined, 24);
    btn('chmus:down', 388, y, 150, 58, '−', false, undefined, undefined, 24);
    btn('chmus:up', 554, y, 150, 58, '+', false, undefined, undefined, 24);
    c.fillStyle = '#ffd257';
    c.font = '800 30px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(AM.arcMute ? T('arc_music_off_word')
      : Math.round(AM.arcVol * 100) + '%', 810, y + 29);
    y += 76;

    const chList = this.champs ? this.champs.list() : [];
    if (!chList.length) {
      label(T('arc_no_data'), y + 12, 22, '#75828f', 'center');
      y += 44;
    }
    for (const ch of chList) {
      const hovered = this.menuHover.includes(rects.length);
      // récord propio del campeonato (victorias de SU storage)
      let hint = '';
      let done = false;   // v2.128: ¿campeonato superado?
      let leyenda = false;   // v3.6.18 (ronda 24): ¿sellado 5/5 en leyenda?
      try {
        const ent = (this.champs.entries || []).find((e) => e.id === ch.id);
        const base = String((ent && ent.storage) || '').replace(/\*$/, '');
        // v3.6.17 (ronda 21 · TU CAMINO TE ESPERA): precedencia
        // SUPERADO > etapa en curso > victorias
        if (base) hint = this.champs._stageHint(ch.id, base) || hint;
        if (base && !hint) {
          const w = parseInt(localStorage.getItem(base + 'wins') || '0', 10) || 0;
          if (w > 0) hint = T('best_arcade', { n: w });
        }
        // v2.128: campeonato SUPERADO → hint propio + cinta ★ SUPERADO
        try { if (this.champs.championFlag(ch.id)) { done = true; hint = T('champ_done_hint'); } } catch (e) { /* */ }
        // v3.6.18 (ronda 24): LEYENDA pisa a SUPERADO en la tarjeta
        try { if (this.champs.leyendaFlag && this.champs.leyendaFlag(ch.id)) { done = true; hint = T('champ_leyenda_hint'); leyenda = true; } } catch (eL2) { /* */ }
      } catch (e) { /* sin registro */ }
      // tarjeta del campeonato
      c.beginPath();
      if (c.roundRect) c.roundRect(56, y, 912, 110, 18); else c.rect(56, y, 912, 110);
      const g = c.createLinearGradient(56, y, 56, y + 110);
      g.addColorStop(0, hovered ? '#4a3a12' : '#3a2e0e');
      g.addColorStop(1, hovered ? '#2e240c' : '#241d09');
      c.fillStyle = g;
      c.fill();
      c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,210,87,0.65)';
      c.lineWidth = hovered ? 5 : 2;
      c.stroke();
      const img = wrlBadgeImg(ch.id);
      if (img && img.complete && img.naturalWidth) {
        const S = 86;
        const k = Math.min(S / img.naturalWidth, S / img.naturalHeight);
        const w = img.naturalWidth * k, h = img.naturalHeight * k;
        c.drawImage(img, 74 + (S - w) / 2, y + (110 - h) / 2, w, h);
      } else {
        c.font = '800 44px system-ui, sans-serif';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText('🏆', 117, y + 55);
      }
      c.textAlign = 'left';
      c.textBaseline = 'alphabetic';
      c.fillStyle = '#ffe9b3';
      c.font = '800 32px system-ui, sans-serif';
      c.fillText(String(ch.label || '').replace(/^▶\s*/, ''), 186, y + 48);
      c.fillStyle = '#9aa7b4';
      c.font = '600 21px system-ui, sans-serif';
      c.fillText(hint || T('hub_champ_hint'), 186, y + 82);
      if (done) {
        // v2.128: cinta dorada «★ SUPERADO» en la tarjeta del vencido
        c.save();
        c.font = '900 22px system-ui, sans-serif';
        const chipTxt = leyenda ? T('champ_leyenda_chip') : T('champ_done_chip');   // v3.6.18 (ronda 24)
        const chipW = c.measureText(chipTxt).width + 36;
        const chipH = 40;
        const chipX = 944 - chipW / 2 - 18, chipY = y + 20;
        c.fillStyle = 'rgba(10,14,20,0.88)';
        c.strokeStyle = '#ffd257'; c.lineWidth = 3;
        if (c.roundRect) {
          c.beginPath(); c.roundRect(chipX - chipW / 2, chipY - chipH / 2, chipW, chipH, 23);
          c.fill(); c.stroke();
        } else {
          c.fillRect(chipX - chipW / 2, chipY - chipH / 2, chipW, chipH);
          c.strokeRect(chipX - chipW / 2, chipY - chipH / 2, chipW, chipH);
        }
        c.fillStyle = '#ffd257';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(chipTxt, chipX, chipY + 1);
        c.restore();
      }
      c.fillStyle = 'rgba(255,210,87,0.9)';
      c.beginPath();
      c.moveTo(924, y + 40); c.lineTo(944, y + 55); c.lineTo(924, y + 70);
      c.closePath(); c.fill();
      rects.push({ x: 56, y: y - 3, w: 912, h: 116, id: 'ppchamp:' + ch.id });
      y += 122;
      // controles propios del módulo (música, atajos, récord…)
      const chMod = this.champs.moduleIfLoaded(ch.id);
      const chItems = (chMod && chMod.menuItems) ? chMod.menuItems() : [];
      for (const it of chItems) {
        if (it.row === 'label') {
          label(it.text, y + 14, 22);
          y += 34;
        } else if (it.row === 'btnrow') {
          (it.btns || []).forEach((b, bi) => {
            const XW = [[56, 316], [388, 150], [554, 150]][bi];
            if (XW) btn('champact:' + ch.id + '\u203A' + b.act, XW[0], y, XW[1], 58, b.label, !!b.on, undefined, undefined, 24);
          });
          c.fillStyle = '#ffd257';
          c.font = '800 30px system-ui, sans-serif';
          c.textAlign = 'center';
          c.textBaseline = 'middle';
          c.fillText(it.pct || '', 810, y + 29);
          c.fillStyle = '#5c6672';
          c.font = '600 22px system-ui, sans-serif';
          c.textAlign = 'left';
          c.fillText(it.hint || '', 886, y + 29);
          y += 70;
        } else if (it.row === 'btn') {
          btn('champact:' + ch.id + '\u203A' + it.act, 56, y, 912, it.h || 74, it.label, false, it.tone || 'surv', undefined, it.fs || 27);
          y += (it.h || 74) + 12;
        } else if (it.row === 'locked') {
          label(it.text, y + 12, 22, '#75828f', 'center');
          y += 40;
        } else if (it.row === 'locked2') {
          label(it.text, y + 10, 20, '#75828f', 'center');
          y += 36;
        } else if (it.row === 'center') {
          label(it.text || '', y + 20, 24, it.color || '#ffd98a', 'center');
          y += 48;
        }
      }
    }
    c.fillStyle = '#9aa7b4';
    c.font = '500 22px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    wrapText(c, T('arcade_hint'), 512, y + 22, 860, 30);
    y += 56;
    const closeY = Math.min(Math.max(y + 4, 1392), 1428);
    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
  }

  /** v2.110 · página AJUSTES: TODAS las opciones juntas (nada se pierde:
   *  sala, ambiente, voz, música, vibración, estela, consejos, prueba de
   *  sonido, telemetría, nombre, reinicio y Ko-fi). */
  drawMenuOpts(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    this.drawMenuHeader(rects);
    btn('page:main', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);
    c.fillStyle = '#ffd257';
    c.font = '900 42px system-ui, sans-serif';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText(T('opts_title'), 664, 246);

    let y = 310;
    label(T('room_label'), y + 10, 22);
    y += 34;
    const themes = [
      ['theme:pabellon', T('theme_pabellon')], ['theme:neon', T('theme_neon')],
      ['theme:atardecer', T('theme_atardecer')], ['theme:artico', T('theme_artico')],
    ];
    themes.forEach(([id, name], i) => {
      btn(id, 56 + (i % 2) * 464, y + Math.floor(i / 2) * 64, 448, 56, name,
        this.theme === id.split(':')[1], undefined, undefined, 23);
    });
    y += 136;
    const yn = (v) => (v ? T('yes') : T('no'));
    btn('amb', 56, y, 448, 56, T('btn_amb', { v: yn(this.audio.ambience) }), !!this.audio.ambience, undefined, !!this.audio.ambience, 23);
    btn('voz', 520, y, 448, 56, T('btn_mic', { v: yn(this.audio.voice) }), !!this.audio.voice, undefined, !!this.audio.voice, 23);
    y += 64;
    btn('music', 56, y, 448, 56, T('btn_music', { v: yn(this.audio.musicOn) }), !!this.audio.musicOn, undefined, !!this.audio.musicOn, 23);
    btn('hapt', 520, y, 448, 56, T('btn_hapt', { v: yn(this.hapticsOn) }), !!this.hapticsOn, undefined, !!this.hapticsOn, 23);
    y += 64;
    btn('trail', 56, y, 448, 56, T('btn_trail', { v: yn(this.showTrail) }), !!this.showTrail, undefined, !!this.showTrail, 23);
    btn('tips', 520, y, 448, 56, T('btn_tips', { v: yn(this.showTips) }), !!this.showTips, undefined, !!this.showTips, 23);
    y += 64;
    // prueba de sonido con AUTO-REPARACIÓN (v2.29) + telemetría (v2.50)
    btn('sndtest', 56, y, 448, 56, T('btn_sndtest'), false, undefined, undefined, 23);
    btn('tele', 520, y, 448, 56, T('btn_tele', { v: yn(__PP_TELE.on) }), !!__PP_TELE.on, undefined, !!__PP_TELE.on, 23);
    y += 66;
    const _pn = ppPlayerName();
    btn('pname', 56, y, 448, 58, T('opts_name', { v: _pn || T('no_name') }), !!_pn, undefined, undefined, 22);
    btn('reset', 520, y, 448, 58, this._resetArm ? T('reset_arm') : T('reset_btn'), false, this._resetArm ? 'surv' : undefined, undefined, 21);
    y += 70;
    // apoyo Ko-fi (v2.50)
    btn('kofi', 56, y, 912, 56, T('btn_kofi'), false, 'green', undefined, 23);
    y += 68;
    label(T('tele_hint'), y + 10, 18, '#75828f');
    y += 30;
    const closeY = Math.min(Math.max(y + 4, 1392), 1428);
    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);
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
      // v2.29: música de fondo mientras el menú esté abierto (fundido de entrada)
      this.audio.setMusicWanted(true);
      // v2.67: calienta el RANKING MUNDIAL para que la sección esté lista
      WORLDRANK.load(false).then(() => {
        if (this.menuOpen) this.drawMenu();
      }).catch(() => { /* nunca rompe */ });
    } else {
      this.audio.playOsc(990, 660, 0.06, 'sine', 0.1, 0);
      // v2.29: al cerrar el menú la música se apaga con fundido (partido en marcha)
      this.audio.setMusicWanted(false);
    }
    // v2.37: la BSO del campeonato se SILENCIA mientras el menú esté abierto
    // y vuelve EXACTAMENTE al volumen que tenía al cerrarse el menú.
    this.audio.setArcDuck(this.menuOpen);
  }

  /* v3.1.1-FEEL1 · PROMPT «MENÚ PRINCIPAL ¿SI/No?» (requisito del dueño):
   * en cualquier estancia que NO sea el hall, B muestra la pregunta en un
   * panel flotante delante (misma mecánica que el menú: rayo y gatillo).
   * NO devuelve a la escena tal cual; SI lleva al hall con el menú abierto. */
  openHallAsk() {
    if (this.calib) return;
    this.menuPage = 'hallask';
    this.menuSec = '';
    this.menuOpen = true;
    this.menuGroup.visible = true;
    this.menuHover = [-1, -1];
    this.anchorMenu();
    this.rules.message = '';
    this.drawMenu();
    this.audio.playOsc(520, 660, 0.08, 'sine', 0.12, 0);
    if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.35, 60);
  }

  /* v3.1.1-FEEL1 · recogida estanca + salto al HALL con el menú principal
   * delante. Compartido por «⌂ VOLVER AL HALL» (menuClick 'homehall') y por
   * el SI del prompt B ('hallask_si'). Online/passthrough: no aplica. */
  goHomeHall() {
    if (this.net.online || this.inAR) return false;
    this.closeTrainingV3();
    if (this.calib) this.exitCalib();   // recoge panel/entrenamiento y restaura
    if (this.champs) this.champs.leaveAll();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.enterHall();
    return true;
  }

  closeMenu() {
    this._resetArm = false;   // v2.66: cerrar el menú desarma el borrado
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
    // v2.69: se conserva TODO tras el primer ':' (antes se perdía el
    // segundo) — necesario para champact:<id>›<acción[:<modo>]>
    const ci0 = r.id.indexOf(':');
    const ns = ci0 < 0 ? r.id : r.id.slice(0, ci0);
    const arg = ci0 < 0 ? '' : r.id.slice(ci0 + 1);
    switch (ns) {
      case 'sec':
        // v2.28 ACORDEÓN: abrir la sección elegida y CONTRAER las demás
        // (pulsar de nuevo la abierta la contrae: todas cerradas)
        this.menuSec = this.menuSec === arg ? '' : arg;
        // CRAZY/ARCADE: al abrirlo, el megáfono presenta el campeonato
        if (arg === 'crazy' && this.menuSec === 'crazy') {
          this.rules.message = T('msg_arcade_menu');
          this.audio.playOsc(880, 1320, 0.09, 'triangle', 0.14, 0);
          window.setTimeout(() => {
            if (!this.disposed) this.audio.playOsc(1100, 1660, 0.12, 'triangle', 0.12, 0);
          }, 110);
        } else {
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        }
        // v2.67: al abrir RANKING MUNDIAL se revalida el top 10 (silencioso)
        if (arg === 'rank' && this.menuSec === 'rank') {
          WORLDRANK.load(true).then(() => {
            if (this.menuOpen && this.menuSec === 'rank' && this.menuPage === 'main') this.drawMenu();
          }).catch(() => { /* nunca rompe */ });
        }
        this.drawMenu();
        break;
      case 'page':
        // v2.110 · HUB: navegación entre páginas del menú
        if (arg === 'main' || arg === 'champs' || arg === 'opts') {
          this.menuPage = arg;
          this._resetArm = false;
          if (arg === 'champs') {
            // el megáfono presenta los campeonatos al entrar (v2.28)
            this.rules.message = T('msg_arcade_menu');
            this.audio.playOsc(880, 1320, 0.09, 'triangle', 0.14, 0);
            window.setTimeout(() => {
              try { if (!this.disposed) this.audio.playOsc(1100, 1660, 0.12, 'triangle', 0.12, 0); } catch (e) { /* */ }
            }, 110);
          } else {
            this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
          }
          this.drawMenu();
        }
        break;
      case 'themecyc': {
        // v2.110 · ciclo rápido de SALA desde el HUB (las 4 en AJUSTES)
        const ti = ROOM_THEMES.findIndex((t) => t.key === this.theme);
        const nxt = ROOM_THEMES[(ti + 1 + ROOM_THEMES.length) % ROOM_THEMES.length];
        this.setTheme(nxt.key);
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      }
      case 'ppchamp':
        // v2.53: CAMPEONATO DE CARPETA — la carpeta entera se carga por
        // import() dinámico. v2.69: La Locura también llega por aquí.
        if (this.champs) this.champs.launch(arg);
        else this.rules.message = T('arc_no_data');
        break;
      case 'champact': {
        // v2.69: acción de un campeonato de carpeta. arg = '<id>›<acción>'
        const ci2 = arg.indexOf('\u203A');
        if (ci2 > 0 && this.champs) {
          this.champs.menuAction(arg.slice(0, ci2), arg.slice(ci2 + 1));
        }
        break;
      }
      case 'trv3':
        // v3.0 · PRO TRAINING: acciones del hub de entrenamiento
        if (window.__PP_TRAIN) window.__PP_TRAIN.menuAction(this, arg);
        break;
      case 'homehall': {
        // v3.1.0-SRV2 · EL HALL ES EL HUB: en partida/entrenamiento/campeonato
        // el menú ofrece la vuelta a la estancia del anfitrión — allí se
        // cambian ajustes y modalidad. v3.1.1-FEEL1: la recogida estanca
        // vive en goHomeHall() (compartida con el SI del prompt B).
        if (this.goHomeHall()) {
          if (!this.menuOpen) this.toggleMenu();
          else { this.anchorMenu(); this.drawMenu(); }
        }
        break;
      }
      case 'hallask_si': {
        // v3.1.1-FEEL1 · SI del prompt B: al HALL con el menú principal en
        // pantalla (misma recogida estanca que «⌂ VOLVER AL HALL»). El prompt
        // se convierte en el menú normal de la estancia.
        this.menuPage = 'main';
        if (this.goHomeHall()) {
          if (!this.menuOpen) this.toggleMenu();
          else { this.anchorMenu(); this.drawMenu(); }
        }
        break;
      }
      case 'hallask_no':
        // v3.1.1-FEEL1 · NO del prompt B: cerrar la ventana y SEGUIR en la
        // escena actual, sin tocar modo, saque ni nada de lo activo.
        this.menuPage = 'main';
        this.closeMenu();
        break;
      case 'start':
        // ARRANQUE RÁPIDO: partido contra la CPU (o revancha online)
        this.closeTrainingV3();   // v3.0.3 · estanqueidad
        if (this.champs) this.champs.leaveAll();   // v2.53: y el campeonato externo
        this.exitHall();          // v3.1.0-SRV2: arrancar un modo saca del hall
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
        this.closeTrainingV3();   // v3.0.3 · estanqueidad
        if (this.champs) this.champs.leaveAll();   // v2.53
        this.exitHall();          // v3.1.0-SRV2: arrancar un modo saca del hall
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
        // v3.0: ENTRENAR abre el HUB PRO TRAINING (la posición de la pala
        // queda como subapartado 0 y se añaden los modos profesionales)
        if (this.champs) this.champs.leaveAll();   // v2.53
        this.menuPage = 'train';
        this.drawMenu();
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
      case 'pname':
        // v2.66: abrir la página de escritura del nombre precargada
        this._nameBuf = ppPlayerName();
        this.menuPage = 'name';
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.drawMenu();
        break;
      case 'nkey':
        // v2.66: teclado del nombre (A–Z, espacio, borrar, guardar, volver)
        if (arg === 'del') this._nameBuf = (this._nameBuf || '').slice(0, -1);
        else if (arg === 'sp') {
          if ((this._nameBuf || '').length < 12 && this._nameBuf.slice(-1) !== ' ') this._nameBuf += ' ';
        } else if (arg === 'ok') {
          const _nm = (this._nameBuf || '').replace(/\s+/g, ' ').trim().slice(0, 12);
          try {
            if (_nm) localStorage.setItem('pp_player_name', _nm);
            else localStorage.removeItem('pp_player_name');
          } catch { /* */ }
          // v2.108: re-evalúa el MODO DEPURACIÓN con el nombre recién guardado
          try { if (window.ppDebugRefresh) window.ppDebugRefresh(); } catch { /* */ }
          this._nameBuf = '';
          this.menuPage = 'main';
          if (this.champs) this.champs.refreshAll();   // v2.69: todos los módulos
          this.audio.playOsc(660, 990, 0.09, 'triangle', 0.14, 0);
        } else if (arg === 'cancel') {
          this._nameBuf = '';
          this.menuPage = 'main';
        } else if ((this._nameBuf || '').length < 12) {
          this._nameBuf = (this._nameBuf || '') + arg;
        }
        this.drawMenu();
        break;
      case 'reset':
        // v2.66: REINICIAR REGISTROS — 1ª pulsación ARMA, 2ª BORRA TODO.
        if (!this._resetArm) {
          this._resetArm = true;
          if (this._resetArmT) window.clearTimeout(this._resetArmT);
          this._resetArmT = window.setTimeout(() => {
            this._resetArm = false;
            if (this.menuOpen) this.drawMenu();
          }, 5000);
          this.audio.playOsc(220, 180, 0.12, 'sawtooth', 0.12, 0);
        } else {
          this._resetArm = false;
          if (this._resetArmT) { window.clearTimeout(this._resetArmT); this._resetArmT = 0; }
          this.resetAllRecords();
          this.rules.message = T('reset_done');
          this.audio.playOsc(660, 220, 0.25, 'sawtooth', 0.14, 0);
          window.setTimeout(() => { if (!this.disposed) this.audio.playOsc(440, 880, 0.18, 'triangle', 0.12, 0); }, 260);
        }
        this.drawMenu();
        break;
      case 'wrl':
        // v2.67: RANKING MUNDIAL — abrir página, cambiar campeonato o refrescar
        if (arg === 'open') {
          this.menuPage = 'rank';
          WORLDRANK.load(true).then(() => {
            if (this.menuOpen && this.menuPage === 'rank') this.drawMenu();
          }).catch(() => { /* nunca rompe */ });
        } else if (arg === 'left' || arg === 'right') {
          // v2.125: portada dinámica (eager del índice) en vez de 'locura'
          const _ids = [this.champs ? this.champs.portadaId : 'locura']
            .concat(this.champs ? this.champs.list().map((x) => x.id) : [])
            .filter((v, i, a2) => a2.indexOf(v) === i);
          let _i = _ids.indexOf(this._wrlChamp);
          _i = (_i < 0) ? 0 : (_i + (arg === 'right' ? 1 : _ids.length - 1)) % _ids.length;
          this._wrlChamp = _ids[_i];
        } else if (arg === 'refresh') {
          WORLDRANK.load(true).then(() => {
            if (this.menuOpen && this.menuPage === 'rank') this.drawMenu();
          }).catch(() => { /* nunca rompe */ });
        }
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
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
      case 'chmus': {
        // v2.78: MÚSICA DE LOS CAMPEONATOS — GLOBAL (mismo canal pp_arcade_vol
        // que ya usaba La Locura; la BSO del Wizard lo sigue en vivo).
        const AM = this.audio;
        if (arg === 'off') AM.setArcMute(!AM.arcMute);
        else if (arg === 'down') AM.setArcVol(AM.arcVol - 0.1);
        else if (arg === 'up') AM.setArcVol(AM.arcVol + 0.1);
        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.rules.message = T('arc_music_msg', {
          v: AM.arcMute ? T('arc_music_off_word') : Math.round(AM.arcVol * 100) + '%',
        });
        this.drawMenu();
        break;
      }
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
      case 'music': {
        // v2.29: música de fondo (portada + menú en VR), preferencia
        // compartida con el botón 🔊 de la portada
        this.audio.setMusic(!this.audio.musicOn);
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.rules.message = T('msg_music', { v: this.audio.musicOn ? T('yes') : T('no') });
        this.drawMenu();
        break;
      }
      case 'sndtest': {
        // v2.29: prueba de sonido; la 2ª pulsación seguida repara el audio
        const repaired = this.audio.testSound();
        this.rules.message = repaired ? T('msg_sndrepair') : T('msg_sndtest');
        this.drawMenu();
        break;
      }
      case 'hapt': {
        // v2.50 · FASE 1: vibración de los golpes sí/no (confort, persistente)
        this.hapticsOn = !this.hapticsOn;
        try { localStorage.setItem('pp_hapt', this.hapticsOn ? '1' : '0'); } catch { /* */ }
        this.rules.message = T('msg_hapt', { v: this.hapticsOn ? T('yes') : T('no') });
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      }
      case 'tips': {
        // v2.50 · FASE 1: consejos de primera sesión sí/no (onboarding)
        this.showTips = !this.showTips;
        try { localStorage.setItem('pp_tips_v1', this.showTips ? '1' : '0'); } catch { /* */ }
        if (!this.showTips) this._tipsIdx = -1;   // corta el ciclo en marcha
        this.rules.message = T('msg_tips', { v: this.showTips ? T('yes') : T('no') });
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      }
      case 'tele': {
        // v2.50 · FASE 1: telemetría anónima (opt-out inmediato y persistente)
        __PP_TELE.on = !__PP_TELE.on;
        try { localStorage.setItem('pp_tele', __PP_TELE.on ? '1' : '0'); } catch { /* */ }
        if (!__PP_TELE.on) { __PP_TELE.st.q = []; __PP_TELE.flush(); }
        this.rules.message = T('msg_tele', { v: __PP_TELE.on ? T('yes') : T('no') });
        this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
        this.drawMenu();
        break;
      }
      case 'kofi': {
        // v2.50 · FASE 1: apoyar el proyecto — abre la página de Ko-fi en el
        // navegador (en Quest: se cambia a la pestaña nueva). Sin URL
        // configurada, se muestra en pantalla para copiarla a mano.
        const url = (typeof window.PP_KOFI_URL === 'string' && window.PP_KOFI_URL) || '';
        let opened = false;
        if (url) {
          try { opened = !!window.open(url, '_blank', 'noopener'); } catch { opened = false; }
        }
        this.rules.message = opened ? T('msg_kofi') : (url || T('btn_kofi'));
        this.audio.playOsc(720, 990, 0.08, 'triangle', 0.14, 0);
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
   *      completado hasta doblar su velocidad; (3) v2.44: CLOWN Nv. 2/3 del
   *      campeonato son MÁS listos (×1,22 / ×1,5). */
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
    // v2.44/2.69: nivel del rival del campeonato (Nv.2 ×1,22 · Nv.3 ×1,5)
    // — lo decide cada módulo en su aiMul(); locura devuelve ×1 si no es
    // una PARTIDA contra el Clown.
    // v2.53: nivel del rival del campeonato externo (Nv.2 ×1,22 · Nv.3 ×1,5)
    if (this.champs && this.champs.active) k *= this.champs.aiMul();
    this.aiSkillK = THREE.MathUtils.clamp(k, 0.7, 2.2);
    this.ai.setConfig(scalePreset(base, this.aiSkillK));
  }

  /** v2.66 · REINICIO TOTAL de registros («empezar de cero»): borra el
   *  ranking, récords, logros y poderes del NÚCLEO (estadísticas y
   *  supervivencia), de LA LOCURA (rank/wins/streak/powers/stage/trophy)
   *  y de TODOS los campeonatos externos cargados (método opcional
   *  resetRecords() de cada módulo). AJUSTES, IDIOMA y NOMBRE se conservan. */
  resetAllRecords() {
    const KEYS = [
      'ppxr_stats_v1', 'ppxr_surv_best',
      'pp_arcade_rank', 'pp_arcade_wins', 'pp_arcade_streak',
      'pp_arcade_powers', 'pp_arcade_stage', 'pp_arcade_trophy',
      'pp_worldrank_cache',   // v2.67: caché local del ranking mundial
      'pp_seen_v1',           // v2.68: consejos de 1ª sesión → vuelven a mostrarse
    ];
    for (const k of KEYS) { try { localStorage.removeItem(k); } catch { /* */ } }
    // núcleo: estadísticas y logros
    if (this.stats && this.stats.data) {
      this.stats.data = {
        won: 0, lost: 0, streak: 0, bestStreak: 0,
        pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
        winsByDiff: { easy: 0, medium: 0, hard: 0 },
        ach: {},
      };
      this.stats.save();
    }
    this.survivalBest = 0;
    // v2.69: TODOS los campeonatos (La Locura incluida — ahora es una
    // carpeta) resetean aquí su estado vivo y sus claves de storage.
    if (this.champs && this.champs.resetRecords) this.champs.resetRecords();
    // v2.108: por seguridad, el MODO DEPURACIÓN se re-evalúa tras borrar
    // registros (borrar no toca el nombre, pero así el rótulo y los
    // bloqueos de escritura quedan siempre coherentes).
    try { if (window.ppDebugRefresh) window.ppDebugRefresh(); } catch { /* */ }
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
    // v3.1.2-CCD1 · spec A: pedir la MAYOR tasa de refresco disponible hasta
    // 120 Hz — más muestras de la mano = trayectoria más fiel para la CCD.
    try {
      if (session && session.supportedFrameRates && session.updateTargetFrameRate) {
        let best = 0;
        for (const f of session.supportedFrameRates) {
          if (f <= 120.5 && f > best) best = f;
        }
        if (best > 0 && best > (session.frameRate || 0)) session.updateTargetFrameRate(best);
      }
    } catch (e) { /* sin soporte: la tasa por defecto del runtime */ }
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
    this.closeTrainingV3();   // v3.0.3 · estanqueidad al entrar en VR
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
    this.audio.setArcDuck(true);   // v2.37: menú abierto -> BSO del arcade en silencio
    this.rules.message = T('menu_open');
    // v3.0.9-HALL1 · NACER EN EL HALL: la primera vez (y cada sesión) el
    // jugador aparece en la estancia del anfitrión, no en la cancha vacía.
    this.enterHall();
    // RE-VINCULACIÓN al entrar en VR: el contexto creado en 2D puede perder
    // la salida al pasar a inmersivo ('running' pero MUDO). v2.31:
    // markVRStart() re-apunta la salida al dispositivo vigente (setSinkId) y
    // se re-crea el contexto SOLO si aún no hay uno confirmado (vrBound).
    this.audio.markVRStart();
    if (!this.audio.vrBound) {
      this.audio.rebind('entrada en VR: salida re-vinculada al casco');
    }
    // Reintentos suaves: si el contexto nuevo nace suspendido, kick() reanuda
    // y el tardío prueba un contexto fresco (también adopta-solo-si-running).
    for (const t of [400, 1200, 2500]) window.setTimeout(() => this.audio.kick(), t);
    window.setTimeout(() => {
      if (this.audio.ctx?.state !== 'running' || !this.audio.vrBound) {
        this.audio.tryFreshRunning('reintento tardío en VR');
      }
    }, 3400);
    window.setTimeout(() => this.audio.serve(), 350);  // blip de confirmación
    // v2.29: la MÚSICA del menú arranca dentro de VR (bucle WebAudio del
    // contexto del casco; el tema de la portada 2D queda pausado)
    this.audio.setMusicWanted(true);
    console.info(
      '[Audio] estado en VR:', this.audio.ctx?.state,
      '· recreaciones:', this.audio.rebuilds,
    );
    // gatillo y grip DENTRO de la sesión son eventos de intención del usuario:
    // sirven para reactivar el audio si el navegador lo suspendió en VR.
    // v2.31: gestureKick() — si el audio sigue sin estar confirmado en el
    // casco (vrBound), RE-CREA el contexto dentro de este gesto aunque el
    // actual diga 'running' (un contexto nacido fuera puede ser mudo).
    // v2.29: por SESIÓN (antes, el guardia __audioHooks persistía y al
    // re-entrar en VR con una sesión NUEVA el selectstart ya no reactivaba
    // el audio -> mudez hasta reiniciar la página)
    if (session && this.__audioHooksSession !== session) {
      this.__audioHooksSession = session;
      const kickAudio = () => this.audio.gestureKick();
      session.addEventListener('selectstart', kickAudio);
      session.addEventListener('squeezestart', kickAudio);
      session.addEventListener('inputsourceschange', kickAudio);
    }
    // AMBIENTE DE TORNEO: murmullo del público + megafonía de bienvenida
    window.setTimeout(() => this.audio.startMurmur(), 900);
    window.setTimeout(() => {
      // v2.139 · BIENVENIDA HABLADA: el MENÚ PRINCIPAL recibe al jugador
      // (abierto en este momento) — la voz da la bienvenida y guía a escoger
      // modalidad. Banco de voz por WebAudio: audible en VR (speechSynthesis
      // no suena en inmersivo); respaldo 2D intacto. Al escoger modalidad,
      // el menú anuncia la suya (modo_partido/modo_survival como siempre).
      this.audio.announce(T('welcome_menu'), true);
    }, 1400);
    this.hapticProbe();
    this.ai.reset();
    this.demoAI.reset();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.setupAIServe();
    this.setupDemoServe();
    // v2.50 · FASE 1: telemetría anónima — inicio de sesión VR + onboarding
    // v2.77: flag anónimo de multijugador (rival P2P conectado en este momento)
    try { __PP_TELE.ev('vr_start', { mode: this.mode, multi: !!(this.net && this.net.online) }); } catch { /* */ }
    this._vrT0 = Date.now();
    try { __PP_TELE.resetFps(); } catch { /* */ }
    // ronda 12: LATIDO EN VR — un vr_ping cada 5 min mientras dura la sesión;
    // si el casco muere sin vr_end, el último ping fecha el fin real.
    try { __PP_TELE.vrPing(true); } catch { /* */ }
    if (this.showTips) {
      let seen = false;
      try { seen = localStorage.getItem('pp_seen_v1') === '1'; } catch { /* */ }
      if (!seen) { this._tipsIdx = 0; this._tipsTimer = 7; }
    }
    // v2.38/2.69: la prueba a mitad (ARKANOID de La Locura o la de
    // cualquier campeonato de carpeta) se retoma al volver a VR.
    if (this.champs) this.champs.reenter();
    this.callbacks.onXRState?.(true);
    if (this.pendingCalib) {
      this.pendingCalib = false;
      this.enterCalib();
    }
  };

  onSessionEnd = () => {
    // Salida de VR: re-vincular el audio a la salida 2D del navegador
    // (adoptar-solo-si-running; el contexto del casco se cierra tras el cambio).
    // v2.50 · FASE 1: fin de sesión VR (duración + FPS medios, anónimos)
    try {
      __PP_TELE.ev('vr_end', {
        dur: this._vrT0 ? Math.round((Date.now() - this._vrT0) / 1000) : 0,
        fps: __PP_TELE.fpsAvg(),
        fpsMin: __PP_TELE.fpsLo(),
        fpsMax: __PP_TELE.fpsHi(),
      });
      // v2.76: la sesión VR terminó → mandar el lote YA (no esperar 30 s;
      // si el casco cierra el visor justo después, el beacon de pagehide
      // puede no llegar a dispararse).
      __PP_TELE.flush(true);
    } catch { /* */ }
    // ronda 12: parar el latido de VR (el vr_end ya lleva dur + fps + min/max)
    try { __PP_TELE.vrPing(false); } catch { /* */ }
    this._vrT0 = 0;
    this.audio.xrActive = false;
    this.audio.vrBound = false;   // v2.31: sin contexto confirmado hasta la próxima sesión
    this.audio.rebind('salida de VR: salida re-vinculada al navegador');
    // v2.29: la música del menú se apaga al salir de VR (la portada reanuda
    // la suya vía __ppMusic.resume dentro de onXRState)
    this.audio.setMusicWanted(false);
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
    this.exitHall();   // v3.0.9-HALL1: salir de VR limpia el hall y recoloca el rig
    this.mode = 'match';
    this.pendingMode = 'match';
    this.rules.startMatch();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.demoServeTimer = 1.4;
    // v2.28: sin sesión XR el menú principal no se pinta en el mundo 2D
    this.menuOpen = false;
    // v2.124: en la PORTADA manda la música 2D — la BSO del campeonato NO
    // vuelve aquí (antes setArcDuck(false) la reanimaba sobre la portada y
    // se pisaba con la música del menú). Vuelve sola al reanudar el duelo
    // (el menú de VR hace el duck/un-duck al cerrarse).
    this.audio.setArcDuck(true);
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
    this.audio.gestureKick();   // v2.31: gesto XR = rescate de audio si hace falta
    if (!this.renderer.xr.isPresenting) return;
    // v2.24: guardia anti-duplicado por mando (three.js puede entregar el
    // mismo 'selectstart' por varios espacios; dos disparos reales humanos
    // nunca distan < 70 ms). Sin esto, cada clic entraba 2 veces.
    const nowSel = performance.now() / 1000;
    if (nowSel - (this._lastSelect[i] || 0) < 0.07) return;
    this._lastSelect[i] = nowSel;

    // v2.107 · CARTEL EXPLICATIVO EN PANTALLA: el gatillo lo CIERRA (su
    // callback arranca la prueba al momento). La MISMA pulsación no hace
    // nada más: ni saque, ni disparo de pistola, ni clic de menú.
    // v2.130 · modo EMPEZAR: el gatillo SOLO cierra si impacta el botón.
    if (this._instr) {
      if (this._instr.waitBtn && !this._instrBtnHit(i)) return;
      this.hideInstrucciones(false);
      return;
    }

    // v2.130 · INTRO DE CAMPEONATO: el gatillo lanza la partida SOLO desde
    // el botón JUGAR (el vídeo de la historia es OPCIONAL). Un gatillo que
    // no impacta el botón reintenta el audio del vídeo (gesto del usuario).
    if (this.champIntro) {
      if (this._champIntroHit(i)) { this.hideChampIntro(true); return; }
      if (this.champIntro.video) this._champIntroPlay();
      return;
    }

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
    // v2.38/2.69: PISTOLA DE RAYOS (superpoder de la PRUEBA 2) — el
    // gatillo de la mano LIBRE dispara el rayo con la bola en juego. El
    // módulo activo decide si está armada (variante 2, fase de juego).
    // v2.89: el DUELO del forajido además habilita el gatillo de la mano
    // de la PALA (convertida en revólver) vía champs.paddleGunArmed.
    if (this.champs && this.champs.gunArmed &&
        (i !== this.paddleHand || this.champs.paddleGunArmed === true) &&
        (this.rules.state === 'rally' || this.rules.state === 'arkanoid')) {
      this.champs.fireGun(i);
      return;
    }
    // v2.96: REJUGAR etapas superadas — el gatillo cae con la pala
    // apuntando a un nodo ya desbloqueado del mapa del camino: relanza
    // ESA etapa. Sólo en saque/fin/prueba (nunca con la bola en juego).
    if (this.champs) {
      const stR = this.rules.state;
      if ((stR === 'serve' || stR === 'over' || stR === 'arkanoid' ||
           stR === CHAMPS_STATE) && this.champs.replayConsume()) return;
    }
    // v2.41/2.69: PRUEBA (ARKANOID o la del campeonato de carpeta) — el
    // GATILLO lanza la bola (mismo flujo; el módulo ignora si no toca)
    if ((this.rules.state === 'arkanoid' || this.rules.state === CHAMPS_STATE) &&
        this.champs) {
      try { this.champs.serveTrigger(i); } catch (e) { /* */ }
      return;
    }
    // v2.53: el gatillo lanza la bola en la PRUEBA del campeonato externo
    // (mismo flujo que ARKANOID: el módulo ignora si no está en saque)
    if (this.rules.state === CHAMPS_STATE && this.champs) {
      this.champs.serveTrigger(i);
      return;
    }
    // v3.0.6-SRV1 · PRO TRAINING: el gatillo lanza la bola del soporte de
    // saque (t4a/t4b). En entrenamiento el árbitro duerme y su rules.state
    // es un RESIDUO del modo anterior: esta rama debe correr ANTES para que
    // el gatillo no dispare el saque del núcleo contra el soporte del módulo.
    if (this.calib && this.trainV3 && window.__PP_TRAIN && window.__PP_TRAIN.serveTrigger) {
      try { window.__PP_TRAIN.serveTrigger(); } catch (e) { /* nunca rompe */ }
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

  /** Suelta la bola con la velocidad REAL de la mano (saque natural).
   *  v2.44 · LANZAMIENTO LIBRE RECUPERADO: soltar el grip SIEMPRE lanza la
   *  bola al aire. v3.1.0-SRV2 (requisito A): la velocidad inicial es
   *  EXACTAMENTE la de la mano — el asistente ya no da «subida mínima» al
   *  soltar flojo (eso reescribía el gesto); si la mano no impulsa, la bola
   *  cae y se repite. La ayuda explícita es el GATILLO (tossFromHand
   *  asistido). Luego la golpeas con la pala cuando quieras. */
  releaseBallHand(i) {
    // v3.0.8-TRN1 · ENTRENAMIENTO t4a/t4b: soltar el grip con la bola en la
    // mano libre LANZA el saque del módulo (el mismo gesto natural que un
    // partido). El módulo decide: en fase 'tee' lanza con la velocidad real
    // de la mano; en cualquier otra fase ignora el gesto.
    if (this.calib && this.trainV3 && window.__PP_TRAIN && window.__PP_TRAIN.serveRelease) {
      if (i === this.ballHand) { try { window.__PP_TRAIN.serveRelease(i); } catch (e) { /* nunca rompe */ } }
      return;
    }
    if (this.calib || this.menuOpen) return;
    // v2.45/2.69 · PRUEBA (1 y 2 o la del campeonato de carpeta): soltar
    // el grip con la bola en la mano libre SIRVE IGUAL QUE EN UNA PARTIDA
    // NORMAL (el módulo valida su fase de saque).
    if ((this.rules.state === 'arkanoid' || this.rules.state === CHAMPS_STATE) &&
        this.champs && i === this.ballHand) {
      this.champs.serveTrigger(i);
      return;
    }
    if (this.rules.state !== 'serve' || this.rules.server !== 'player') return;
    if (this.tossed || i !== this.ballHand) return;
    if (!this.renderer.xr.isPresenting) return;
    const hand = this.controllerPaddles[i];
    if (!hand.active) return;
    // v3.1.0-SRV2 · LANZAMIENTO SIEMPRE NATURAL al soltar el grip (requisito
    // A: «se liberará con una velocidad inicial calculada a partir del
    // movimiento de la mano… no se debe reposicionar ni redirigir la bola»).
    // El asistente NO reescribe el gesto: si la mano no sube, la bola cae y
    // se repite. La subida mínima asistida queda SOLO en el gatillo
    // (tossFromHand con assisted=true), que es la ayuda explícita.
    this.tossFromHand(i, false);
  }

  tossFromHand(i, assisted) {
    const hand = this.controllerPaddles[i];
    const v = new THREE.Vector3().copy(hand.vel);
    // v3.0.9-HALL1 · subida mínima del saque asistido según dificultad
    const vyMin = this.serveTier().vy;
    if (assisted && v.y < vyMin) {
      v.y = vyMin;
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
    if (this.hapticsOn === false) return false;   // v2.50: ajuste de confort
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

  /* ======================================================================
   *  v2.106/107 · CARTEL EXPLICATIVO de las PRUEBAS DE HABILIDAD (todos
   *  los campeonatos): panel con título + líneas de texto bien maquetadas
   *  (envuelto con measureText — NUNCA se corta), fade de entrada/salida
   *  y callback al terminar. v2.107: ESTÉTICA DE CADA CAMPEONATO —
   *  'oeste' pergamino de cartel de recompensa, 'locura' carpa de circo
   *  con banderines y 'magia' pergamino arcano violeta con destellos;
   *  misma geometría y misma maquetación en los tres. Y el gatillo LO
   *  CIERRA (onSelectStart → hideInstrucciones → arranca la prueba).
   *  game.showInstrucciones(titulo, filas, dur, cb, tema). El panel
   *  cuelga del RIG (delante del jugador), renderOrder altísimo y
   *  depthTest off.
   *  ==================================================================== */
  /* v2.128 · INSIGNIA «¡CONSEGUIDO!» — panel GRANDE colgado del RIG al
   *  ganar el duelo FINAL de un campeonato: insignia del módulo (por
   *  convención championships/<id>/assets/insignia.png), texto gigante
   *  ¡CONSEGUIDO!, título del campeonato y aviso de rejuego libre (el
   *  campeonato queda ABIERTO). Entra con pop elástico, pulsa suave y
   *  se retira solo. Los módulos la llaman vía window.__PP_CORE. */
  showChampConseguido(id, opts) {
    try {
      if (!this.rig) return;
      this._hideChampConseguido();
      opts = opts || {};
      const W = 1280, H = 880;
      const cv = document.createElement('canvas');
      cv.width = W; cv.height = H;
      const c = cv.getContext('2d');
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const group = new THREE.Group();
      const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(1.58, 1.086),
        new THREE.MeshBasicMaterial({
          map: tex, transparent: true, depthWrite: false, depthTest: false,
          side: THREE.DoubleSide,
        }),
      );
      mesh.renderOrder = 60;
      group.add(mesh);
      group.position.set(0, 1.74, DIMS.tableCenterZ + 0.5);
      group.visible = false;
      this.rig.add(group);
      // título por defecto: el nombre del campeonato (manifest del índice)
      let ttl = String(opts.title || '');
      if (!ttl) {
        try {
          const ent = ((this.champs && this.champs.entries) || []).find((x) => x.id === id);
          const tt = ent && ent.title;
          if (tt) ttl = String((__ppLang === 'en') ? (tt.en || tt.es) : (tt.es || tt.en)) || '';
        } catch (e0) { /* */ }
      }
      this.champDone = {
        id, group, cv, c, tex, t: 0, dur: opts.dur || 9.5,
        title: ttl, img: null, mat: mesh.material,
        stats: Array.isArray(opts.stats) ? opts.stats.slice(0, 3) : null,   // v3.6.18 (ronda 24): coronación con estadísticas
        campeon: !!opts.campeon,   // v3.6.18 (ronda 24): coronación = más confeti
      };
      try {
        const img = new Image();
        img.onload = () => {
          if (this.champDone) { this.champDone.img = img; this._paintChampConseguido(); }
        };
        img.onerror = () => { /* sin insignia: escudo dibujado */ };
        img.src = new URL('championships/' + id + '/assets/insignia.png', document.baseURI).href;
      } catch (e1) { /* */ }
      this._paintChampConseguido();
      group.visible = true;
      group.scale.setScalar(0.2);
      try { this.confettiBurst = Math.max(this.confettiBurst || 0, this.champDone && this.champDone.campeon ? 14 : 8); } catch (e2) { /* */ }   // v3.6.18 (ronda 24)
      try { this.audio.announce(opts.msg || T('champdone_msg'), true); } catch (e3) { /* */ }
      if (this.renderer && this.renderer.xr && this.renderer.xr.isPresenting) {
        try { this.haptic(this.paddleHand, 1.0, 300); } catch (e4) { /* */ }
        window.setTimeout(() => { try { this.haptic(this.paddleHand, 0.7, 200); } catch (e5) { /* */ } }, 420);
      }
    } catch (e) { console.warn('[champDone] show', e); }
  }

  /** Pintado del panel (textura estática: solo se repinta si cambia algo). */
  _paintChampConseguido() {
    const S = this.champDone;
    if (!S) return;
    try {
      const W = S.cv.width, H = S.cv.height, c = S.c;
      c.clearRect(0, 0, W, H);
      // fondo cósmico + rayos dorados radiales
      const bg = c.createRadialGradient(W / 2, H * 0.42, 60, W / 2, H * 0.5, 980);
      bg.addColorStop(0, 'rgba(26,36,60,0.97)');
      bg.addColorStop(0.55, 'rgba(13,19,34,0.95)');
      bg.addColorStop(1, 'rgba(6,9,16,0.97)');
      c.fillStyle = bg;
      if (c.roundRect) { c.beginPath(); c.roundRect(0, 0, W, H, 56); c.fill(); }
      else c.fillRect(0, 0, W, H);
      c.save();
      c.translate(W / 2, H * 0.40);
      for (let i = 0; i < 14; i++) {
        c.rotate(Math.PI * 2 / 14);
        const g = c.createLinearGradient(0, 0, 0, -640);
        g.addColorStop(0, 'rgba(255,210,87,0.15)');
        g.addColorStop(1, 'rgba(255,210,87,0)');
        c.fillStyle = g;
        c.beginPath();
        c.moveTo(0, 0); c.lineTo(-74, -640); c.lineTo(74, -640);
        c.closePath(); c.fill();
      }
      c.restore();
      // marco dorado doble
      c.strokeStyle = 'rgba(255,210,87,0.9)';
      c.lineWidth = 10;
      if (c.roundRect) { c.beginPath(); c.roundRect(14, 14, W - 28, H - 28, 48); c.stroke(); }
      else c.strokeRect(14, 14, W - 28, H - 28);
      c.strokeStyle = 'rgba(255,236,170,0.5)';
      c.lineWidth = 3;
      if (c.roundRect) { c.beginPath(); c.roundRect(34, 34, W - 68, H - 68, 38); c.stroke(); }
      else c.strokeRect(34, 34, W - 68, H - 68);
      // INSIGNIA en grande con halo y anillo
      const bs = 330, bx = W / 2, by = H * 0.40;
      const halo = c.createRadialGradient(bx, by, 40, bx, by, 300);
      halo.addColorStop(0, 'rgba(255,210,87,0.5)');
      halo.addColorStop(1, 'rgba(255,210,87,0)');
      c.fillStyle = halo;
      c.beginPath(); c.arc(bx, by, 300, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.arc(bx, by, bs / 2 + 26, 0, Math.PI * 2);
      c.fillStyle = 'rgba(8,12,20,0.92)'; c.fill();
      c.strokeStyle = '#ffd257'; c.lineWidth = 12; c.stroke();
      c.strokeStyle = 'rgba(255,236,170,0.65)'; c.lineWidth = 4;
      c.beginPath(); c.arc(bx, by, bs / 2 + 44, 0, Math.PI * 2); c.stroke();
      if (S.img && S.img.complete && S.img.naturalWidth) {
        const k = Math.min(bs / S.img.naturalWidth, bs / S.img.naturalHeight);
        const w = S.img.naturalWidth * k, h = S.img.naturalHeight * k;
        c.drawImage(S.img, bx - w / 2, by - h / 2, w, h);
      } else {
        c.fillStyle = '#ffd257';
        c.font = '900 200px system-ui, sans-serif';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText('🏆', bx, by + 6);
      }
      // textos
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillStyle = '#ffd257';
      c.shadowColor = 'rgba(255,196,40,0.85)'; c.shadowBlur = 30;
      c.font = '900 122px system-ui, sans-serif';
      c.fillText(T('champdone_big'), W / 2, H * 0.755);
      c.shadowBlur = 0;
      c.fillStyle = '#f2f4f6';
      c.font = '800 46px system-ui, sans-serif';
      c.fillText(S.title || T('champdone_sub'), W / 2, H * 0.845);
      // v3.6.18 (ronda 24): CORONACIÓN — fila de estadísticas en lugar del
      // recordatorio de rejuego (puntos · duelos ganados · fecha).
      if (S.stats && S.stats.length) {
        const nS = S.stats.length, colW = (W - 220) / Math.max(1, nS);
        for (let i = 0; i < nS; i++) {
          const lab = String((S.stats[i] && S.stats[i][0]) || '');
          const val = String((S.stats[i] && S.stats[i][1]) || '');
          const cx = 110 + colW * (i + 0.5);
          c.fillStyle = '#9fb2c4';
          c.font = '600 28px system-ui, sans-serif';
          c.fillText(lab.toUpperCase(), cx, H * 0.872);
          c.fillStyle = '#ffd257';
          c.font = '900 44px system-ui, sans-serif';
          c.fillText(val, cx, H * 0.922);
        }
      } else {
        c.fillStyle = '#9fb2c4';
        c.font = '600 30px system-ui, sans-serif';
        c.fillText(T('champdone_replay'), W / 2, H * 0.912);
      }
      S.tex.needsUpdate = true;
    } catch (e) { console.warn('[champDone] paint', e); }
  }

  /** Animación por frame: pop elástico + vaivén + fundido y retirada. */
  _updateChampConseguido(dt) {
    const S = this.champDone;
    if (!S || !S.group.visible) return;
    try {
      S.t += dt;
      if (S.t >= S.dur) { this._hideChampConseguido(); return; }
      const inS = Math.min(1, S.t / 0.5);
      const ease = 1 - Math.pow(1 - inS, 3);
      const pulse = 1 + Math.sin(S.t * 4.6) * 0.035 * Math.max(0, 1 - S.t / 5);
      S.group.scale.setScalar(0.2 + 0.8 * ease * pulse);
      S.group.rotation.y = Math.sin(S.t * 1.1) * 0.05;
      S.mat.opacity = Math.min(1, (S.dur - S.t) / 1.2);   // fundido final 1,2 s
    } catch (e) { this._hideChampConseguido(); }
  }

  /** Retirada con dispose completo (regla Quest: nada queda colgado). */
  _hideChampConseguido() {
    const S = this.champDone;
    if (!S) return;
    this.champDone = null;
    try { if (S.group.parent) S.group.parent.remove(S.group); } catch (e) { /* */ }
    try { S.tex.dispose(); } catch (e) { /* */ }
    try { S.mat.dispose(); } catch (e) { /* */ }
    try { S.group.clear(); } catch (e) { /* */ }
  }

  /* ======================================================================
   *  v2.130 · INTRO DE CAMPEONATO (estructura común de TODOS): al entrar
   *  en un campeonato se planta delante del jugador una PANTALLA GRANDE
   *  con el vídeo que cuenta la historia del rival (~30 s, en bucle,
   *  OPCIONAL verlo) y debajo un GRAN botón «JUGAR» que lanza la partida.
   *  ChampLoader.launch() lo invoca tras start() del módulo — ningún
   *  campeonato necesita código propio. Sin vídeo (assets/intro.mp4
   *  ausente) el póster pintado hace de portada y el botón sigue activo.
   *  El gatillo sólo actúa sobre el botón JUGAR (raycast); cualquier otro
   *  gatillo reintenta el audio del vídeo (gesto del usuario).
   *  ==================================================================== */
  showChampIntro(id) {
    try {
      if (!this.rig) return;
      this.hideChampIntro(false);
      // título del campeonato (manifest del índice) + nombre del rival
      let ttl = id;
      try {
        const ent = ((this.champs && this.champs.entries) || []).find((x) => x.id === id);
        const tt = ent && ent.title;
        if (tt) ttl = String((__ppLang === 'en') ? (tt.en || tt.es) : (tt.es || tt.en)) || id;
      } catch (e0) { /* */ }
      const W = 1024, H = 576;
      const cv = document.createElement('canvas');
      cv.width = W; cv.height = H;
      const c = cv.getContext('2d');
      this._pintaIntroPoster(cv, ttl, false);
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const group = new THREE.Group();
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true,
        depthTest: false, depthWrite: false, fog: false });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2.56, 1.44), mat);
      mesh.renderOrder = 60;
      group.add(mesh);
      // --- botón JUGAR (textura propia: repintado barato al apuntar) ---
      const bcv = document.createElement('canvas');
      bcv.width = 560; bcv.height = 170;
      const bmat = new THREE.MeshBasicMaterial({
        map: new THREE.CanvasTexture(bcv), transparent: true,
        depthTest: false, depthWrite: false,
      });
      bmat.map.colorSpace = THREE.SRGBColorSpace;
      const btn = new THREE.Mesh(new THREE.PlaneGeometry(1.34, 0.407), bmat);
      btn.position.set(0, -0.99, 0.02);
      btn.renderOrder = 61;
      group.add(btn);
      group.position.set(0, 1.72, -2.75);
      group.visible = false;
      this.rig.add(group);
      this.champIntro = { id, ttl, group, mesh, mat, tex, cv, c,
        btn, bmat, bcv, video: null, vtex: null,
        t: 0, btnHot: false, swap: false };
      // --- vídeo de la historia (OPCIONAL: si falta, queda el póster) ---
      try {
        const url = new URL('championships/' + id + '/assets/intro.mp4',
          document.baseURI).href;
        const v = document.createElement('video');
        v.src = url; v.loop = true; v.playsInline = true;
        v.crossOrigin = 'anonymous'; v.preload = 'auto'; v.muted = false;
        const vtex = new THREE.VideoTexture(v);
        vtex.colorSpace = THREE.SRGBColorSpace;
        this.champIntro.video = v;
        this.champIntro.vtex = vtex;
        v.addEventListener('loadeddata', () => {
          const S = this.champIntro;
          if (!S || S.id !== id) return;
          S.mat.map = vtex; S.mat.needsUpdate = true; S.swap = true;
          this._champIntroPlay();
        });
        v.addEventListener('error', () => { /* sin vídeo: póster */ });
      } catch (e1) { /* sin vídeo: póster */ }
      this._pintaBtnJugar(false);
      group.visible = true;
      group.scale.setScalar(0.12);
      // v2.130 · la BSO del NÚCLEO (La Locura la comparte) hace duck bajo
      // el audio del vídeo; los módulos con BSO propia usan champIntroPause.
      try { this.audio.setArcDuck(true); } catch (e2) { /* */ }
      try { this.champs.introShown && this.champs.introShown(); } catch (e3) { /* */ }
    } catch (e) { console.warn('[champIntro] show', e); }
  }

  /** Arranque del vídeo con rescate de autoplay (gesto → sin mute). */
  _champIntroPlay() {
    const S = this.champIntro;
    if (!S || !S.video) return;
    try {
      const v = S.video;
      const p = v.play();
      if (p && p.catch) p.catch(() => {
        v.muted = true;
        const p2 = v.play();
        if (p2 && p2.catch) p2.catch(() => { /* póster */ });
      });
    } catch (e) { /* */ }
  }

  /** Póster de la intro (también portada si no hay vídeo): campo
   *  estrellado neutro + título del campeonato + aviso «vídeo opcional». */
  _pintaIntroPoster(cv, ttl, cargando) {
    try {
      const W = cv.width, H = cv.height, c = cv.getContext('2d');
      const bg = c.createLinearGradient(0, 0, 0, H);
      bg.addColorStop(0, '#101828'); bg.addColorStop(0.55, '#0a1120');
      bg.addColorStop(1, '#060a14');
      c.fillStyle = bg; c.fillRect(0, 0, W, H);
      let seed = 21;
      const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
      for (let i = 0; i < 110; i++) {
        const x = rnd() * W, y = rnd() * H, r = rnd() < 0.85 ? 1.7 : 3.2;
        c.fillStyle = rnd() < 0.22 ? '#9fd8ff' : '#e8f2ff';
        c.globalAlpha = 0.35 + rnd() * 0.65;
        c.beginPath(); c.arc(x, y, r, 0, 7); c.fill();
      }
      c.globalAlpha = 1;
      // banda del título
      c.fillStyle = 'rgba(255,210,87,0.14)'; c.fillRect(0, 64, W, 118);
      c.fillStyle = '#ffd257';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      let ts = 62;
      c.font = 'bold ' + ts + 'px "Trebuchet MS", Verdana, sans-serif';
      while (c.measureText(ttl).width > W - 120 && ts > 34) {
        ts -= 3; c.font = 'bold ' + ts + 'px "Trebuchet MS", Verdana, sans-serif';
      }
      c.fillText(ttl, W / 2, 124);
      c.fillStyle = '#dcecff';
      c.font = '30px "Trebuchet MS", Verdana, sans-serif';
      const sub = (typeof __ppLang !== 'undefined' && __ppLang === 'en')
        ? 'The story of your rival — watching it is optional'
        : 'La historia de tu rival — verlo es opcional';
      c.fillText(sub, W / 2, H - 76);
      if (cargando !== false) {
        c.fillStyle = '#7fe8ff';
        c.font = '26px "Trebuchet MS", Verdana, sans-serif';
        c.fillText('···', W / 2, H / 2);
      }
    } catch (e) { /* */ }
  }

  /** Pintado del botón JUGAR (estado normal / apuntado). */
  _pintaBtnJugar(hot) {
    const S = this.champIntro;
    if (!S || !S.bcv) return;
    try {
      const c = S.bcv.getContext('2d');
      const W = S.bcv.width, H = S.bcv.height;
      c.clearRect(0, 0, W, H);
      const lbl = (typeof __ppLang !== 'undefined' && __ppLang === 'en') ? 'PLAY' : 'JUGAR';
      if (c.roundRect) {
        c.fillStyle = 'rgba(0,0,0,0.4)';
        c.beginPath(); c.roundRect(10, 16, W - 20, H - 24, 44); c.fill();
        const g = c.createLinearGradient(0, 0, 0, H);
        if (hot) { g.addColorStop(0, '#ffe08a'); g.addColorStop(1, '#ffb340'); }
        else { g.addColorStop(0, '#ffd257'); g.addColorStop(1, '#e89b2a'); }
        c.fillStyle = g;
        c.beginPath(); c.roundRect(4, 4, W - 8, H - 24, 44); c.fill();
        c.strokeStyle = hot ? '#ffffff' : '#8a5a12'; c.lineWidth = hot ? 9 : 6;
        c.beginPath(); c.roundRect(4, 4, W - 8, H - 24, 44); c.stroke();
      } else {
        c.fillStyle = hot ? '#ffe08a' : '#ffd257'; c.fillRect(4, 4, W - 8, H - 24);
        c.strokeStyle = hot ? '#ffffff' : '#8a5a12'; c.lineWidth = hot ? 9 : 6;
        c.strokeRect(4, 4, W - 8, H - 24);
      }
      c.fillStyle = '#241300';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.font = 'bold ' + (hot ? 84 : 76) + 'px "Trebuchet MS", Verdana, sans-serif';
      c.fillText(lbl, W / 2, (H - 10) / 2);
      if (S.bmat && S.bmat.map) S.bmat.map.needsUpdate = true;
    } catch (e) { /* */ }
  }

  /** ¿el gatillo del mando i impacta el botón JUGAR de la intro? */
  _champIntroHit(i) {
    const S = this.champIntro;
    if (!S || !S.btn) return false;
    try {
      const ray = this.rays && this.rays[i | 0];
      if (!ray || !this.connected || !this.connected[i | 0]) return false;
      if (!this._instrRC) {
        this._instrRC = new THREE.Raycaster();
        this._instrO = new THREE.Vector3();
        this._instrQ = new THREE.Quaternion();
        this._instrD = new THREE.Vector3();
      }
      ray.getWorldPosition(this._instrO);
      ray.getWorldQuaternion(this._instrQ);
      this._instrD.set(0, 0, -1).applyQuaternion(this._instrQ);
      this._instrRC.set(this._instrO, this._instrD);
      return this._instrRC.intersectObject(S.btn, false).length > 0;
    } catch (e) { return false; }
  }

  /** Retira la intro. resume=true → reanuda la BSO del campeonato. */
  hideChampIntro(resume) {
    const S = this.champIntro;
    if (!S) return;
    this.champIntro = null;
    try { if (S.video) { S.video.pause(); S.video.removeAttribute('src'); S.video.load(); } } catch (e) { /* */ }
    try { if (S.vtex) S.vtex.dispose(); } catch (e) { /* */ }
    try { S.bmat.map.dispose(); S.bmat.dispose(); } catch (e) { /* */ }
    try { S.btn.geometry.dispose(); } catch (e) { /* */ }
    try { S.mat.dispose(); S.tex.dispose(); } catch (e) { /* */ }
    try { if (S.group.parent) S.group.parent.remove(S.group); S.group.clear(); } catch (e) { /* */ }
    if (resume) {
      try { this.audio.setArcDuck(false); } catch (e) { /* */ }
      try { this.champs && this.champs.introClosed && this.champs.introClosed(); } catch (e) { /* */ }
    }
  }

  /** Animación de la intro: pop elástico + botón apuntado + pulso. */
  _updateChampIntro(dt) {
    const S = this.champIntro;
    if (!S) return;
    S.t += dt;
    if (S.t < 0.4) {
      const k = 1 - Math.pow(1 - S.t / 0.4, 3);
      S.group.scale.setScalar(0.12 + 0.88 * k);
    } else S.group.scale.setScalar(1);
    let hot = false;
    try {
      const hand = this.paddleHand | 0;
      const ray = this.rays && this.rays[hand];
      if (ray && this.renderer.xr.isPresenting &&
          this.connected && this.connected[hand]) {
        if (!this._instrRC) {
          this._instrRC = new THREE.Raycaster();
          this._instrO = new THREE.Vector3();
          this._instrQ = new THREE.Quaternion();
          this._instrD = new THREE.Vector3();
        }
        ray.getWorldPosition(this._instrO);
        ray.getWorldQuaternion(this._instrQ);
        this._instrD.set(0, 0, -1).applyQuaternion(this._instrQ);
        this._instrRC.set(this._instrO, this._instrD);
        hot = this._instrRC.intersectObject(S.btn, false).length > 0;
      }
    } catch (e) { /* */ }
    if (hot !== S.btnHot) { S.btnHot = hot; this._pintaBtnJugar(hot); }
  }

  /* v2.130 · MODO «EMPEZAR»: las instrucciones de las PRUEBAS DE HABILIDAD
   *  (estructura común de todos los campeonatos) ya NO se van solas —
   *  esperan hasta que el jugador apunta y pulsa el botón EMPEZAR del
   *  propio panel. En 2D (portada/QA headless) se mantiene el desvanecido
   *  automático de siempre para no romper los flujos sin visor.
   *  showInstrucciones(titulo, filas, dur, cb, tema, { empezar:true }). */
  showInstrucciones(titulo, filas, dur, cb, tema, opts) {
    try {
      if (!this.rig) return;
      this.hideInstrucciones(true);        // cancela uno pendiente
      // v2.130 · modo EMPEZAR: sólo con visor puesto (en 2D no hay gatillo)
      const WAIT = !!(opts && opts.empezar && this.renderer &&
        this.renderer.xr && this.renderer.xr.isPresenting);
      const W = 1280, H = 820;
      const cv = document.createElement('canvas');
      cv.width = W; cv.height = H;
      const c = cv.getContext('2d');
      // v2.107 · piel según campeonato (misma maquetación en todos)
      // v2.129 · «estacion»: panel espacial para Estación Orbital (plantilla)
      const th = (tema === 'locura' || tema === 'magia' || tema === 'estacion') ? tema : 'oeste';
      // v2.135 · piel del ARTISTA (clown/wizard/forajido): si el cartel del
      //  campeonato ya está cargado se pinta el panel sobre el arte real con
      //  todo el texto dentro del hueco. Sin imagen → piel dibujada de siempre.
      const NK = NORMAS_SKIN.defs[th];
      const NIMG = NK ? NORMAS_SKIN.imgs[th] : null;
      if (NK && NIMG && NIMG.complete && NIMG.naturalWidth > 0) {
        this._instrArte(titulo, filas, dur, cb, NK, NIMG, WAIT, th);
        return;
      }
      const BH = 150;
      let fFam = 'Georgia, "Times New Roman", serif';
      let colBand = '#7c231a', colBand2 = '#5c160f', colTitle = '#f8edd2';
      let colBody = '#33200f', colBull = '#7c231a';
      if (th === 'locura') {
        /* --- LA LOCURA · CARPA DE CIRCO: rayas rojas/blancas + oro --- */
        fFam = '"Trebuchet MS", Verdana, sans-serif';
        c.fillStyle = '#fff3df'; c.fillRect(0, 0, W, H);
        c.save();
        c.beginPath(); c.rect(0, 0, W, H); c.clip();
        c.fillStyle = '#d23a2a';
        const sw = 46;
        for (let x = -H; x < W + H; x += sw * 2) {
          c.beginPath();
          c.moveTo(x, H); c.lineTo(x + sw, H);
          c.lineTo(x + sw + H, 0); c.lineTo(x + H, 0);
          c.closePath(); c.fill();
        }
        c.restore();
        c.fillStyle = '#fff3df'; c.fillRect(40, 40, W - 80, H - 80);
        c.strokeStyle = '#b8862f'; c.lineWidth = 10;
        c.strokeRect(40, 40, W - 80, H - 80);
        c.strokeStyle = 'rgba(210,58,42,0.55)'; c.lineWidth = 4;
        c.strokeRect(58, 58, W - 116, H - 116);
        colBand = '#c0272d'; colBand2 = '#8a1016'; colTitle = '#ffe9b8';
        colBody = '#33241a'; colBull = '#c0272d';
      } else if (th === 'magia') {
        /* --- MAGIA · PERGAMINO ARCANO: violeta, lavanda y oro --- */
        const g1 = c.createRadialGradient(W / 2, 250, 90, W / 2, 420, 900);
        g1.addColorStop(0, '#33205a'); g1.addColorStop(0.6, '#241440');
        g1.addColorStop(1, '#180d2c');
        c.fillStyle = g1; c.fillRect(0, 0, W, H);
        c.strokeStyle = '#9a7ae8'; c.lineWidth = 14;
        c.strokeRect(10, 10, W - 20, H - 20);
        c.strokeStyle = 'rgba(255,215,110,0.85)'; c.lineWidth = 3;
        c.strokeRect(30, 30, W - 60, H - 60);
        const star = (x, y, r, a) => {     // destello de 4 puntas
          c.save(); c.globalAlpha = a; c.fillStyle = '#ffd76e';
          c.beginPath();
          c.moveTo(x, y - r); c.quadraticCurveTo(x, y, x + r, y);
          c.quadraticCurveTo(x, y, x, y + r);
          c.quadraticCurveTo(x, y, x - r, y);
          c.quadraticCurveTo(x, y, x, y - r);
          c.closePath(); c.fill(); c.restore();
        };
        star(86, 86, 15, 0.85); star(152, 132, 8, 0.5);
        star(W - 92, 92, 13, 0.8); star(W - 162, 152, 8, 0.5);
        star(96, H - 88, 13, 0.7); star(W - 100, H - 92, 15, 0.85);
        colBand = '#5b2f96'; colBand2 = '#3c1f6e'; colTitle = '#ffe08a';
        colBody = '#f0e6ff'; colBull = '#ffd76e';
      } else if (th === 'estacion') {
        /* --- ESTACIÓN ORBITAL · PANEL ESPACIAL (v2.129): noche estrellada,
             marco de acero cian y banda de aviso ámbar — la sala hecha cartel */
        fFam = '"Trebuchet MS", Verdana, sans-serif';
        c.fillStyle = '#0d1524'; c.fillRect(0, 0, W, H);
        // campo de estrellas (determinista: siempre el mismo cartel)
        let seed = 47;
        const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
        for (let i = 0; i < 90; i++) {
          const x = 16 + rnd() * (W - 32), y = 16 + rnd() * (H - 32);
          const r = rnd() < 0.82 ? 1.6 : 3.1;
          c.fillStyle = rnd() < 0.25 ? '#9fd8ff' : '#e8f2ff';
          c.beginPath(); c.arc(x, y, r, 0, 7); c.fill();
        }
        // planeta anillado de la esquina
        const px2 = W - 150, py2 = H - 130;
        c.fillStyle = '#2e6ba8'; c.beginPath(); c.arc(px2, py2, 62, 0, 7); c.fill();
        c.fillStyle = '#4a90cf'; c.beginPath(); c.arc(px2 - 16, py2 - 18, 40, 0, 7); c.fill();
        c.strokeStyle = '#d8c4a0'; c.lineWidth = 9;
        c.beginPath(); c.ellipse(px2, py2, 98, 26, -0.32, 0, 7); c.stroke();
        // marco de acero + remaches
        c.strokeStyle = '#4a5c7c'; c.lineWidth = 14; c.strokeRect(10, 10, W - 20, H - 20);
        c.strokeStyle = '#4fd8ff'; c.lineWidth = 4; c.strokeRect(24, 24, W - 48, H - 48);
        c.fillStyle = '#8fa8c8';
        for (const [rx2, ry2] of [[34, 34], [W - 34, 34], [34, H - 34], [W - 34, H - 34]]) {
          c.beginPath(); c.arc(rx2, ry2, 6, 0, 7); c.fill();
        }
        colBand = '#12324a'; colBand2 = '#0b2033'; colTitle = '#7fe8ff';
        colBody = '#dcecff'; colBull = '#ffb347';
      } else {
        /* --- OESTE · PERGAMINO con doble marco y viñeta (v2.106) --- */
        c.fillStyle = '#f4e8cd'; c.fillRect(0, 0, W, H);
        c.strokeStyle = '#4a2c14'; c.lineWidth = 16; c.strokeRect(8, 8, W - 16, H - 16);
        c.strokeStyle = 'rgba(122,74,34,0.65)'; c.lineWidth = 4;
        c.strokeRect(28, 28, W - 56, H - 56);
      }
      // --- banda del título ---
      c.fillStyle = colBand; c.fillRect(28, 28, W - 56, BH);
      c.fillStyle = colBand2; c.fillRect(28, 28 + BH - 12, W - 56, 12);
      const tTxt = String(titulo || '');
      c.fillStyle = colTitle;
      c.textAlign = 'center'; c.textBaseline = 'middle';
      let tSize = 64;
      c.font = 'bold ' + tSize + 'px ' + fFam;
      while (c.measureText(tTxt).width > W - 200 && tSize > 40) {
        tSize -= 4;
        c.font = 'bold ' + tSize + 'px ' + fFam;
      }
      c.fillText(tTxt, W / 2, 28 + BH / 2);
      if (th === 'locura') {
        // banderines de circo colgando de la banda
        const cols = ['#f6b73c', '#2f7fd4', '#d23a2a'];
        const nP = 26, pw = (W - 116) / nP;
        for (let i = 0; i < nP; i++) {
          c.fillStyle = cols[i % cols.length];
          const x0 = 58 + i * pw, y0 = 28 + BH;
          c.beginPath();
          c.moveTo(x0, y0 + 2); c.lineTo(x0 + pw, y0 + 2);
          c.lineTo(x0 + pw / 2, y0 + 24);
          c.closePath(); c.fill();
        }
      }
      // --- cuerpo: líneas envueltas (NUNCA se cortan) ---
      const filasArr = Array.isArray(filas) ? filas : [String(filas || '')];
      const maxW = W - 220;
      let size = 37, lh = Math.round(size * 1.42);
      const wrapAll = (sz) => {
        c.font = sz + 'px ' + fFam;
        const out = [];
        for (const raw of filasArr) {
          const words = String(raw).split(/\s+/);
          let line = '';
          const pre = raw.trim().startsWith('-') || raw.trim().startsWith('·');
          for (const w of words) {
            const test = line ? line + ' ' + w : w;
            if (c.measureText(test).width > maxW - (pre ? 34 : 0) && line) {
              out.push({ t: line, pre });
              line = w;
            } else line = test;
          }
          if (line) out.push({ t: line, pre });
          out.push(null);   // espacio entre entradas
        }
        if (out.length && out[out.length - 1] === null) out.pop();
        return out;
      };
      let lines = wrapAll(size);
      let y0 = 28 + BH + 52;
      // v2.130: con botón EMPEZAR, el cuerpo reserva la franja inferior
      const maxY = WAIT ? H - 215 : H - 60;
      while (lines.length && y0 + lines.length * lh > maxY && size > 26) {
        size -= 2; lh = Math.round(size * 1.4); lines = wrapAll(size);
      }
      c.textAlign = 'left'; c.textBaseline = 'alphabetic';
      c.fillStyle = colBody;
      let y = y0;
      for (const ln of lines) {
        if (ln === null) { y += lh * 0.55; continue; }
        if (ln.pre) {
          c.fillStyle = colBull;
          c.font = 'bold ' + size + 'px ' + fFam;
          c.fillText('·', 96, y);
          c.fillStyle = colBody;
        }
        c.font = size + 'px ' + fFam;
        c.fillText(ln.t, 128, y);
        y += lh;
      }
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 4;
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true,
        depthTest: false, depthWrite: false, fog: false, opacity: 0 });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(3.15, 2.02), mat);
      mesh.position.set(0, 1.52, -2.75);
      mesh.renderOrder = 9994;
      this.rig.add(mesh);
      this._instr = { mesh, mat, tex, t: 0, dur: Math.max(2.0, dur || 7.5),
        out: 0.45, cb: cb || null };
      if (WAIT) {
        // v2.130 · botón EMPEZAR: mesh hijo del panel con textura propia
        // (460×120 px del lienzo 1280×820), colocado en la franja libre.
        this._instr.tema = th;
        this._instr.fFam = fFam;
        this._instr.colBand = colBand;
        this._instr.colBull = colBull;
        this._instr.colTitle = colTitle;
        this._instr.waitBtn = true;
        this._instr.btnHot = false;
        const bw = 460, bh = 120;
        const bcv = document.createElement('canvas');
        bcv.width = bw; bcv.height = bh;
        const bmat = new THREE.MeshBasicMaterial({
          map: new THREE.CanvasTexture(bcv), transparent: true,
          depthTest: false, depthWrite: false,
        });
        bmat.map.colorSpace = THREE.SRGBColorSpace;
        const bmesh = new THREE.Mesh(
          new THREE.PlaneGeometry(bw * 3.15 / 1280, bh * 2.02 / 820), bmat);
        bmesh.position.set(0, -0.744, 0.015);   // franja inferior del panel
        bmesh.renderOrder = 9995;
        mesh.add(bmesh);
        this._instr.btn = bmesh;
        this._instr.bcv = bcv;
        this._instr.bmat = bmat;
        this._pintaBtnEmpezar(false);
      }
    } catch (e) { console.warn('[instrucciones]', e); }
  }

  /* v2.135 · cartel de NORMAS con el ARTE del artista (clown/wizard/forajido).
   *  Lienzo 1280×640 = proporción 2:1 nativa del arte (el marco NO se deforma)
   *  en un panel de 3,8×1,9 m. Maquetación DENTRO del hueco del cartel:
   *  · título centrado oro/crema con contorno y sombra
   *  · filete dorado con rombo bajo el título
   *  · cuerpo envuelto con measureText (NUNCA se corta): 1 columna si cabe
   *    cómodo; si no, 2 columnas equilibradas con separador central
   *  · velo oscuro suave + sombra de texto: legibilidad perfecta sobre el
   *    hueco (pizarra/pergamino oscuro/piedra) sin tapar el arte
   *  El botón EMPEZAR cuelga PINZADO al marco bajo del cartel (fuera del
   *  hueco: las normas lo ocupan entero) — mismo raycast del v2.130. */
  _instrArte(titulo, filas, dur, cb, SK, img, wait, th) {
    try {
      const W = 1280, H = 640;
      const SC = 1.25;                    // arte 1024×512 → lienzo 1280×640
      const cv = document.createElement('canvas');
      cv.width = W; cv.height = H;
      const c = cv.getContext('2d');
      c.drawImage(img, 0, 0, W, H);
      // hueco interior del cartel (px del lienzo)
      const ix0 = SK.rect[0] * SC, iy0 = SK.rect[1] * SC;
      const ix1 = SK.rect[2] * SC, iy1 = SK.rect[3] * SC;
      const iw = ix1 - ix0, midX = (ix0 + ix1) / 2;
      // velo oscuro suave: unifica el hueco y levanta el contraste
      c.save();
      const vg = c.createLinearGradient(0, iy0, 0, iy1);
      vg.addColorStop(0, 'rgba(8,6,3,0.34)');
      vg.addColorStop(0.45, 'rgba(8,6,3,0.22)');
      vg.addColorStop(1, 'rgba(8,6,3,0.34)');
      c.fillStyle = vg;
      if (c.roundRect) {
        c.beginPath();
        c.roundRect(ix0 + 3, iy0 + 3, iw - 6, iy1 - iy0 - 6, 16);
        c.fill();
      } else {
        c.fillRect(ix0 + 3, iy0 + 3, iw - 6, iy1 - iy0 - 6);
      }
      c.restore();
      // título: oro/crema con contorno y sombra, dentro del hueco
      const tTxt = String(titulo || '');
      c.textAlign = 'center'; c.textBaseline = 'middle';
      let tSize = 46;
      c.font = 'bold ' + tSize + 'px ' + SK.fFam;
      while (c.measureText(tTxt).width > iw - 60 && tSize > 30) {
        tSize -= 2; c.font = 'bold ' + tSize + 'px ' + SK.fFam;
      }
      const tY = iy0 + 8 + tSize / 2;
      c.save();
      c.shadowColor = 'rgba(0,0,0,0.9)'; c.shadowBlur = 7; c.shadowOffsetY = 2;
      c.lineJoin = 'round';
      c.lineWidth = 7; c.strokeStyle = 'rgba(18,9,3,0.92)';
      c.strokeText(tTxt, midX, tY);
      c.fillStyle = SK.colTitle;
      c.fillText(tTxt, midX, tY);
      c.restore();
      // filete dorado con rombo bajo el título
      const dY = tY + tSize / 2 + 8;
      c.save();
      c.strokeStyle = 'rgba(255,214,120,0.5)'; c.lineWidth = 2;
      const dW = Math.min(iw * 0.40, 400);
      c.beginPath();
      c.moveTo(midX - dW / 2, dY); c.lineTo(midX + dW / 2, dY); c.stroke();
      c.fillStyle = 'rgba(255,214,120,0.85)';
      c.beginPath();
      c.moveTo(midX, dY - 5); c.lineTo(midX + 5, dY);
      c.lineTo(midX, dY + 5); c.lineTo(midX - 5, dY);
      c.closePath(); c.fill();
      c.restore();
      // cuerpo: envuelto con measureText (NUNCA se corta) — 1 o 2 columnas
      const filasArr = Array.isArray(filas) ? filas : [String(filas || '')];
      const y0 = dY + 26;                    // aire bajo el filete (sin roce)
      const maxY = iy1 - 18;
      const nlin = (raw, sz, wEff) => {   // nº de líneas de una entrada
        c.font = sz + 'px ' + SK.fFam;
        const words = String(raw).split(/\s+/);
        let line = '', n = 0;
        for (const w of words) {
          const test = line ? line + ' ' + w : w;
          if (c.measureText(test).width > wEff && line) { n++; line = w; }
          else line = test;
        }
        if (line || n === 0) n++;
        return n;
      };
      const wrap = (sz, wEff, from, to, x) => {
        c.font = sz + 'px ' + SK.fFam;
        const out = [];
        for (let i = from; i < to; i++) {
          const raw = filasArr[i];
          const words = String(raw).split(/\s+/);
          let line = '';
          const pre = raw.trim().startsWith('-') || raw.trim().startsWith('·');
          for (const w of words) {
            const test = line ? line + ' ' + w : w;
            if (c.measureText(test).width > wEff && line) {
              out.push({ t: line, pre, x }); line = w;
            } else line = test;
          }
          if (line) out.push({ t: line, pre, x });
          out.push(null);                 // respiro entre entradas
        }
        if (out.length && out[out.length - 1] === null) out.pop();
        return out;
      };
      const alto = (ls, lhh) => {
        let h = 0;
        for (const ln of ls) h += (ln === null ? lhh * 0.38 : lhh);
        return h;
      };
      const textX1 = ix0 + 50, wEff1 = ix1 - textX1 - 26;
      let size = 21, lh = Math.round(21 * 1.36), cols = 1;
      let lines = null, linesR = null;
      for (let sz = 30; sz >= 21; sz -= 1.5) {         // 1 columna si cabe
        const lhh = Math.round(sz * 1.36);
        const ls = wrap(sz, wEff1, 0, filasArr.length, textX1);
        if (y0 + alto(ls, lhh) <= maxY) { size = sz; lh = lhh; lines = ls; break; }
      }
      let sepX = 0;
      if (lines === null) {                 // 2 columnas equilibradas
        cols = 2;
        const txtX2 = Math.round(midX + 28);
        const wEffL = midX - 22 - textX1;
        const wEffR = ix1 - 26 - txtX2;
        for (let sz = 30; sz >= 19; sz -= 1.5) {
          const lhh = Math.round(sz * 1.36);
          let total = 0;
          for (const raw of filasArr) total += nlin(raw, sz, Math.min(wEffL, wEffR));
          let acc = 0, cut = filasArr.length - 1;
          for (let i = 0; i < filasArr.length - 1; i++) {
            acc += nlin(filasArr[i], sz, Math.min(wEffL, wEffR));
            if (acc >= total / 2) { cut = i + 1; break; }
          }
          const lsL = wrap(sz, wEffL, 0, cut, textX1);
          const lsR = wrap(sz, wEffR, cut, filasArr.length, txtX2);
          if (y0 + Math.max(alto(lsL, lhh), alto(lsR, lhh)) <= maxY) {
            size = sz; lh = lhh;
            lines = lsL; linesR = lsR; sepX = midX;
            break;
          }
        }
        if (lines) {                        // separador vertical central
          c.save();
          c.strokeStyle = 'rgba(255,214,120,0.28)'; c.lineWidth = 2;
          c.beginPath();
          c.moveTo(sepX, y0 - 8); c.lineTo(sepX, maxY + 4); c.stroke();
          c.restore();
        }
      }
      if (lines === null) {                 // último recurso: 1 col a 19 px
        cols = 1; size = 19; lh = Math.round(19 * 1.36);
        lines = wrap(19, wEff1, 0, filasArr.length, textX1);
      }
      // pintado del cuerpo (sombra suave para lectura perfecta)
      c.textAlign = 'left'; c.textBaseline = 'alphabetic';
      c.save();
      c.shadowColor = 'rgba(0,0,0,0.85)'; c.shadowBlur = 4; c.shadowOffsetY = 1.5;
      const pintaCol = (ls) => {
        let yy = y0;
        for (const ln of ls) {
          if (ln === null) { yy += lh * 0.38; continue; }
          if (ln.pre) {
            c.fillStyle = SK.colBull;
            c.font = 'bold ' + size + 'px ' + SK.fFam;
            c.fillText('·', ln.x - 28, yy);
          }
          c.fillStyle = SK.colBody;
          c.font = size + 'px ' + SK.fFam;
          c.fillText(ln.t, ln.x, yy);
          yy += lh;
        }
      };
      pintaCol(lines);
      if (linesR) pintaCol(linesR);
      c.restore();
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.anisotropy = 4;
      const PW = 3.8, PH = 1.9;             // 2:1 nativo del arte, sin deformar
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true,
        depthTest: false, depthWrite: false, fog: false, opacity: 0 });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(PW, PH), mat);
      mesh.position.set(0, 1.60, -2.75);
      mesh.renderOrder = 9994;
      this.rig.add(mesh);
      this._instr = { mesh, mat, tex, t: 0, dur: Math.max(2.0, dur || 7.5),
        out: 0.45, cb: cb || null, arte: true, skin: th, cols: cols,
        fuente: size, skinRect: [ix0, iy0, ix1, iy1] };
      if (wait) {
        // v2.135 · botón EMPEZAR pinzado al marco bajo (mismo raycast v2.130)
        this._instr.tema = th;
        this._instr.fFam = SK.fFam;
        this._instr.colBand = SK.colBand;
        this._instr.colBull = SK.colBull;
        this._instr.colTitle = SK.colTitle;
        this._instr.waitBtn = true;
        this._instr.btnHot = false;
        const bw = 420, bh = 110;
        const bcv = document.createElement('canvas');
        bcv.width = bw; bcv.height = bh;
        const bmat = new THREE.MeshBasicMaterial({
          map: new THREE.CanvasTexture(bcv), transparent: true,
          depthTest: false, depthWrite: false,
        });
        bmat.map.colorSpace = THREE.SRGBColorSpace;
        const bmesh = new THREE.Mesh(
          new THREE.PlaneGeometry(bw * PW / W, bh * PH / H), bmat);
        bmesh.position.set(0, -PH / 2 + 0.10, 0.015);   // pinzado al marco bajo
        bmesh.renderOrder = 9995;
        mesh.add(bmesh);
        this._instr.btn = bmesh;
        this._instr.bcv = bcv;
        this._instr.bmat = bmat;
        this._pintaBtnEmpezar(false);
      }
    } catch (e) { console.warn('[instrucciones-arte]', e); }
  }

  /* v2.130 · pintado del botón EMPEZAR (re-pintado barato al apuntar) */
  _pintaBtnEmpezar(hot) {
    const S = this._instr;
    if (!S || !S.bcv) return;
    try {
      const c = S.bcv.getContext('2d');
      const W = S.bcv.width, H = S.bcv.height;
      c.clearRect(0, 0, W, H);
      const lbl = (typeof __ppLang !== 'undefined' && __ppLang === 'en') ? 'START' : 'EMPEZAR';
      const fill = hot ? S.colBull : S.colBand;
      const edge = hot ? '#ffffff' : S.colBull;
      if (c.roundRect) {
        c.fillStyle = 'rgba(0,0,0,0.35)';
        c.beginPath(); c.roundRect(8, 12, W - 16, H - 16, 34); c.fill();
        c.fillStyle = fill;
        c.beginPath(); c.roundRect(4, 4, W - 8, H - 20, 34); c.fill();
        c.strokeStyle = edge; c.lineWidth = hot ? 8 : 5;
        c.beginPath(); c.roundRect(4, 4, W - 8, H - 20, 34); c.stroke();
      } else {
        c.fillStyle = fill; c.fillRect(4, 4, W - 8, H - 20);
        c.strokeStyle = edge; c.lineWidth = hot ? 8 : 5;
        c.strokeRect(4, 4, W - 8, H - 20);
      }
      c.fillStyle = '#ffffff';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.font = 'bold ' + (hot ? 58 : 54) + 'px ' + S.fFam;
      c.fillText(lbl, W / 2, (H - 8) / 2);
      if (S.bmat && S.bmat.map) S.bmat.map.needsUpdate = true;
    } catch (e) { /* */ }
  }

  /* v2.130 · ¿el gatillo del mando i impacta el botón EMPEZAR? */
  _instrBtnHit(i) {
    const it = this._instr;
    if (!it || !it.waitBtn || !it.btn) return true;   // sin botón: como siempre
    try {
      const ray = this.rays && this.rays[i | 0];
      if (!ray || !this.connected || !this.connected[i | 0]) return false;
      if (!this._instrRC) {
        this._instrRC = new THREE.Raycaster();
        this._instrO = new THREE.Vector3();
        this._instrQ = new THREE.Quaternion();
        this._instrD = new THREE.Vector3();
      }
      ray.getWorldPosition(this._instrO);
      ray.getWorldQuaternion(this._instrQ);
      this._instrD.set(0, 0, -1).applyQuaternion(this._instrQ);
      this._instrRC.set(this._instrO, this._instrD);
      return this._instrRC.intersectObject(it.btn, false).length > 0;
    } catch (e) { return false; }
  }
  hideInstrucciones(silent) {
    const it = this._instr;
    if (!it) return;
    this._instr = null;
    try {
      this.rig.remove(it.mesh);
      it.mat.dispose(); it.tex.dispose();
      it.mesh.geometry.dispose();
      if (it.btn) {
        try { it.btn.geometry.dispose(); } catch (e1) { /* */ }
        try { it.bmat.map.dispose(); it.bmat.dispose(); } catch (e2) { /* */ }
      }
    } catch (e) { /* */ }
    if (!silent && it.cb) { const f = it.cb; it.cb = null; f(); }
  }
  _updateInstrucciones(dt) {
    const it = this._instr;
    if (!it) return;
    it.t += dt;
    if (it.t < 0.35) {
      it.mat.opacity = it.t / 0.35;
    } else {
      it.mat.opacity = 1;
    }
    if (it.waitBtn) {
      // v2.130 · modo EMPEZAR: la pantalla NO se va sola; el botón brilla
      // cuando la pala lo apunta (re-pintado sólo al cambiar el estado).
      let hot = false;
      try {
        const hand = this.paddleHand | 0;
        const ray = this.rays && this.rays[hand];
        if (it.btn && ray && this.renderer.xr.isPresenting &&
            this.connected && this.connected[hand]) {
          if (!this._instrRC) {
            this._instrRC = new THREE.Raycaster();
            this._instrO = new THREE.Vector3();
            this._instrQ = new THREE.Quaternion();
            this._instrD = new THREE.Vector3();
          }
          ray.getWorldPosition(this._instrO);
          ray.getWorldQuaternion(this._instrQ);
          this._instrD.set(0, 0, -1).applyQuaternion(this._instrQ);
          this._instrRC.set(this._instrO, this._instrD);
          hot = this._instrRC.intersectObject(it.btn, false).length > 0;
        }
      } catch (e) { /* */ }
      if (hot !== it.btnHot) { it.btnHot = hot; this._pintaBtnEmpezar(hot); }
      return;                          // sin desvanecido automático
    }
    if (it.t < it.dur) {
      it.mat.opacity = 1;
    } else if (it.t < it.dur + it.out) {
      it.mat.opacity = 1 - (it.t - it.dur) / it.out;
    } else {
      this.hideInstrucciones(false);   // dispara el callback (arranca la prueba)
    }
  }

  // ---------- Bucle principal ----------

  animate = (time) => {
    if (this.disposed) return;
    const now = time * 0.001;
    // v3.1.2-CCD1 · dtFrame limitado a 1/30 s (spec A): con un bajón de FPS
    // la física prefiere ir lenta antes que barrer un intervalo enorme con
    // poses P0→P1 degradadas. Orden por frame: leer poses (three.js ya las
    // actualizó de XRFrame antes de este callback) → simular → renderizar.
    const dt = this.lastTime < 0 ? 0.016 : Math.min(now - this.lastTime, 1 / 30);
    this.lastTime = now;
    // LIVE-TV: telemetría del anfitrión (solo lectura, fuera del camino crítico)
    try { if (window.__PP_LIVE) window.__PP_LIVE.frame(this, now); } catch { /* */ }

    const presenting = this.renderer.xr.isPresenting;
    // v2.30 · PORTADA SIN PARTIDA: en 2D (sin visor) el juego está EN PAUSA —
    // solo escena + cámara orbital + música. Sin IA, sin demo, sin física,
    // sin reglas, sin sonidos ni narrador. window.__pp2DPlay=true reactiva
    // el rallies 2D SOLO para las pruebas headless.
    const active = presenting || this.net.online || window.__pp2DPlay === true;

    // v2.40 · ANUNCIO DE SUPERPODER CON LA PARTIDA CONGELADA: mientras
    // freezeT > 0 NO corre simulación alguna (IA, física, saque, árbitro ni
    // la prueba en curso); el cartel épico sigue animando desde arcade.update
    // y, al agotarse el tiempo, TODO se reanuda en el punto exacto en que
    // estaba — se anuncia el superpoder sin molestar a la partida.
    const frozen = this.freezeT > 0;
    if (frozen) this.freezeT = Math.max(0, this.freezeT - dt);

    // vigilancia del audio: si el contexto quedó suspendido a mitad de
    // partida (proximidad del visor, notificación...), o su reloj se
    // congeló con estado 'running' (grafo zombi), se reactiva solo
    this.audio.watchdog(dt);

    // v2.50 · FASE 1: FPS para telemetría + ciclo de CONSEJOS de 1ª sesión
    // (los consejos ceden el cartel al árbitro y solo se marcan la 1ª vez)
    try { __PP_TELE.noteFrame(dt); } catch { /* */ }
    if (presenting && this._tipsIdx >= 0 && this._tipsIdx <= 3) {
      this._tipsTimer -= dt;
      if (this._tipsTimer <= 0) {
        const keys = ['tip_1', 'tip_2', 'tip_3', 'tip_bye'];
        const msg = T(keys[this._tipsIdx]);
        const cur = this.rules.message || '';
        if (!cur || cur.startsWith('CONSEJO') || cur.startsWith('TIP') ||
            cur === msg || cur === T('tip_bye')) {
          this.rules.message = msg;
        }
        this._tipsIdx++;
        this._tipsTimer = 16;
        if (this._tipsIdx > 3) {
          this._tipsIdx = -1;
          try { localStorage.setItem('pp_seen_v1', '1'); } catch { /* */ }
        }
      }
    }

    if (presenting && this.recenterFrames > 0) {
      this.updateRecenter();
      this.recenterFrames--;
    }

    // v3.1.0-SRV2 · EL HALL ES EL HUB (requisito del dueño): cerrar el menú
    // DENTRO del hall NO saca de la estancia — el menú «vive» en el hall y
    // allí se abren modos y ajustes. El guardián antiguo (exitHall en cuanto
    // el menú se cerraba) se elimina: salir al cancha es ahora EXPLÍCITO,
    // en los ARRANQUES DE MODO (switchMode, 'start', 'survgo', sesión
    // online, champs.launch y startMode/startCalib del entrenamiento), que
    // llaman exitHall() ellos mismos. En partida, el menú ofrece el botón
    // «⌂ VOLVER AL HALL» para regresar (cambia de modalidad allí).

    // 0) botón A/X: el mando donde se pulsa pasa a llevar la pala
    // v3.5.0-ESC1 · TAMBIÉN EN EL PRO TRAINING (informe del dueño: «que se
    // pueda cambiar la raqueta de mano como en los campeonatos — un zurdo»):
    // los modos de entrenamiento viven en calib (enterCalib), así que la
    // condición antigua los excluía y A/X no hacía nada ahí. Ahora el swap
    // opera en entrenamiento (this.trainV3 activo); el AJUSTE DE PALA real
    // (calib sin trainV3) sigue sin permitirlo — allí manda el panel propio.
    // Todo lo demás deriva en caliente de paddleHand/ballHand (getters), el
    // saque en mano libre incluido, así que el cambio es seguro en pleno modo.
    if (presenting && (!this.calib || this.trainV3)) {
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

    // 0.5) v2.78 · TECLA Y (mando izquierdo) ANULADA como acceso al
    //      entrenamiento: sacaba de la partida sin querer y el entrenamiento
    //      ya se entra desde el MENÚ (botón ENTRENAR). Se conserva Y SOLO
    //      DENTRO del ajuste de pala para VOLVER al modo anterior (es la
    //      salida documentada en el propio panel; ver createCalibPanel).
    if (presenting && this.calib && this.readButton(this.handIndex('left'), 5)) {
      // v3.0.3 · Dentro del PRO TRAINING, Y sale AL HUB DE ENTRENAMIENTO
      // (menú abierto en «ENTRENAR») cerrando el modo POR COMPLETO — antes
      // caía en un partido con los paneles del entrenamiento sin recoger y
      // el siguiente «volver» llevaba al menú principal.
      const trnY = (typeof window !== 'undefined') && window.__PP_TRAIN;
      if (trnY && (this.trainV3 || this.trainV3Hub)) {
        trnY.stopMode(this);
        this.menuPage = 'train';
        this.menuOpen = true;
        this.menuGroup.visible = true;
        this.anchorMenu();
        this.drawMenu();
        this.audio.setMusicWanted(true);
      } else {
        this.exitCalib();
      }
    }

    // 0.6) botón B (mando derecho): v3.1.1-FEEL1 · en el HALL (y en online/
    //      passthrough, donde el hall no existe) B abre/cierra el menú como
    //      siempre; en CUALQUIER OTRA ESTANCIA muestra el PROMPT «Menú
    //      Principal ¿SI/No?»: NO cierra la ventana y sigues en la escena,
    //      SI sale al HALL con el menú principal delante. Con el menú ya
    //      abierto, B lo cierra (atalajo de siempre).
    if (presenting && !this.calib &&
        this.readButton(this.handIndex('right'), 5)) {
      if (this.menuOpen || this.inHall || this.net.online || this.inAR) {
        // si cerramos el PROMPT con B, la próxima apertura vuelve al menú normal
        if (this.menuOpen && this.menuPage === 'hallask') this.menuPage = 'main';
        this.toggleMenu();
      } else {
        this.openHallAsk();
      }
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
        // v3.1.0-SRV2: margen REBAJADO y pequeño (fácil 6 cm, medio 4,5 cm,
        // difícil 2,8 cm) — la CCD fina garantiza el contacto real; un radio
        // grande creaba golpes a distancia, prohibidos por el requisito
        ps.extraReach = servingToss ? this.serveTier().reach : 0;
        ps.serveFlight = servingToss;   // v3.1.0-SRV2: tolerancias y suelo de saque
      }
    }

    // 2) IA(s) — en online el rival es humano y llega por red (v2.19)
    //    v2.30: en portada 2D (inactiva) NADIE juega: sin IA ni demo.
    const canHit = this.rules.state === 'rally';
    const playerPad = this.controllerPaddles[this.paddleHand];
    const oppPadX = presenting
      ? (playerPad.active ? playerPad.pos.x : 0)
      : this.demoAI.pos.x;
    const oppPadZ = presenting
      ? (playerPad.active ? playerPad.pos.z : DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4)
      : this.demoAI.pos.z;
    const aiServing = !this.calib && this.rules.state === 'serve' && this.rules.server === 'ai';
    const aiHit = (!active || this.calib || this.net.online || frozen)
      ? null
      : this.ai.update(dt, this.ball, {
      canHit,
      validBounce: this.rules.validBounce,
      oppPadX,
      oppPadZ,
      rallyHits: this.rules.rallyHits,
      holdTarget: aiServing ? this.aiServeStance : null,
      prevBall: this._prevBallForAI || null,   // v2.84: barrido anti-túnel
    });
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
    // v2.30: el "jugador demo" del escritorio se retiró — nadie golpea por
    // el lado del jugador en la portada.

    // 3) Preparación del saque
    let holdLock = false;
    if (active && !frozen && this.rules.state === 'serve' && !this.calib) {
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
        } else if (!this.net.online) {
          // ESPECTADOR: la demo saca desde su posición reglamentaria
          // v2.51: NUNCA en online (antes el escritorio 2D sacaba con la
          // demo sin avisar por red: el rival esperaba un saque eterno)
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

    // 4) Física (solo la pala del mando activo colisiona).
    //    v2.30: en portada 2D inactiva la bola queda POSADA en la mesa —
    //    nada de rallies de fondo, sonidos ni narración.
    this.events.length = 0;
    this._localHit = false;
    if (!active) {
      holdLock = true;
      this.ball.vel.set(0, 0, 0);
      this.ball.spin.set(0, 0, 0);
      this.ball.pos.set(0, DIMS.tableTopY + DIMS.ballRadius, DIMS.tableCenterZ + 0.25);
    } else if (this.net.online) this.net.drainNetwork(this);   // v2.19: rival por red
    // v2.91: durante el SAQUE la bola la simula quien saca — el invitado
    // YA PUEDE SACAR (antes su toss era pisado por la emisión del anfitrión)
    if (this.net.online) this.net.syncServeOwner();
    if (active && !holdLock && !frozen &&
        !(this.champs && this.champs.testActive)) {   // prueba con la bola tomada
      const pads = [];
      if (presenting) {
        const ps = this.controllerPaddles[this.paddleHand];
        if (ps.active) pads.push(ps);
      }
      // v3.0.6-SRV1 · INMUNIDAD del inicio del lanzamiento: mientras la bola
      // sube los primeros milímetros del toss, la pala NO colisiona. Antes,
      // con las manos juntas (postura natural de saque), un roce prematuro
      // anulaba el saque y la bola CHISPAZABA de vuelta a la mano: el bucle
      // «lanzamiento anulado» que hacía el saque casi imposible. La misma
      // subida continúa y el golpeo legítimo llega unos cm más arriba.
      const tossImmune = this.tossed && this.rules.state === 'serve' &&
        this.rules.server === 'player' && !this.calib &&
        ((this.tossMaxY || 0) - (this.tossReleaseY || 0)) < DIMS.tossMinRise;
      if (tossImmune) pads.length = 0;
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
        // v2.84: posición de la bola ANTES de integrar — el frame siguiente
        // la IA la usa para BARRER el trayecto (alcance anti-túnel) y
        // detectar contactos que antes se colaban entre frames.
        const pbAI = this._prevBallForAI || (this._prevBallForAI = new THREE.Vector3());
        pbAI.copy(this.ball.pos);
        stepPhysics(dt, this.ball, pads, this.events);
      }
    }
    // v2.38/2.69 · PRUEBA ACTIVA (ARKANOID de La Locura o la del
    // campeonato de carpeta): física PROPIA (stepPhysics + colisionadores
    // extra; el árbitro queda en pausa). Con guard: un error de la prueba
    // JAMÁS congela el bucle de render.
    if (active && !frozen && this.champs && this.champs.testActive) {
      try { this.champs.testStep(dt); }
      catch (e) { console.warn('[champs.testStep]', e); }
    }

    // 4.5) v2.44 · BOLA DOBLE (CLOWN Nv. 3): filtro de muerte ANTES del
    //      árbitro (el clon salva el punto) + física propia del clon
    if (active && !frozen && this.champs && this.champs._split) {
      try {
        this.champs.splitFilterEvents(this.events);
        this.champs.updateSplit(dt);
      } catch (e) { console.warn('[split]', e); }
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
        // v3.1.0-SRV2 · IMPULSO REAL + ASISTENCIA PROGRESIVA ACOTADA
        // (requisito del dueño A-E). La salida ya la ha calculado el modelo
        // de contacto REAL (collidePaddle: orientación de la cara, restitución,
        // fricción, punto dulce) — aquí NO se sustituye por nada:
        //   · sin suelo de velocidad (el 3,2 m/s forzado disfrazaba roces);
        //   · sin cascada 45 % → 75 % → solver (sustituía el golpeo);
        //   · sólo la mezcla ACOTADA si la salida real está cerca de servir.
        // La legalidad la juzga el árbitro con el vuelo real (bote propio →
        // bote rival → LET/falta en rules.handleEvents).
        const hitPad = this.controllerPaddles[e.paddleIndex ?? this.paddleHand];
        if (this.ball.vel.length() > SERVE_TUNE.serveMaxSpeed) {
          this.ball.vel.setLength(SERVE_TUNE.serveMaxSpeed);
        }
        const _res = applyServeProgressiveAssist(this.ball, hitPad, this.serveTier());
        __ppServeTelemetry(_res, { src: 'core', tier: this.difficulty });
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
    //    en online el INVITADO no puntúa: el marcador llega del anfitrión).
    //    v2.30: en portada 2D inactiva el árbitro tampoco corre — ni puntos
    //    ni megafonía de fondo.
    if (active && !this.calib && !frozen && !(this.net.online && this.net.role === 'guest')) {
      this.processIntents(this.rules.handleEvents(this.events));
      this.processIntents(this.rules.update(dt));
    }
    this.processEvents(this.events);
    if (this.net.online) this.net.collectEvents(this.events);
    if (this.calib) this.updateCalibration(dt);
    if (window.__PP_TRAIN) window.__PP_TRAIN.tick(dt);   // v3.0: cosmética global + entrenamiento

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
      // v2.51: SUAVIZADO — llegaba en crudo a 20 Hz y a saltos; ahora
      // interpolación exponencial de posición + slerp de rotación.
      // v2.91: MUERTE ADELANTADA — la posición objetivo se adelanta con la
      // velocidad estimada de las dos últimas muestras (max 120 ms) para
      // absorber el jitter: la pala rival se mueve CONTINUA, no a saltos.
      const rp = this.net.remotePaddle;
      if (rp) {
        NetLink.posFromNet(rp.p, netTmpP);
        const prev = this.net._padPrev;
        if (prev) {
          const dtS = Math.max(1e-3, (rp.t - prev.t) / 1000);
          const age = Math.min(0.12, Math.max(0, (performance.now() - rp.t) / 1000));
          // velocidad en marco RED -> al espejar: (-vx, vy, -vz)
          netTmpP.x -= ((rp.p[0] - prev.p[0]) / dtS) * age;
          netTmpP.y += ((rp.p[1] - prev.p[1]) / dtS) * age;
          netTmpP.z -= ((rp.p[2] - prev.p[2]) / dtS) * age;
        }
        NetLink.quatFromNet(rp.q, netTmpQ);
        const f = 1 - Math.exp(-18 * dt);
        this.aiPaddleMesh.position.lerp(netTmpP, f);
        this.aiPaddleMesh.quaternion.slerp(netTmpQ, f);
      }
      this.aiPaddleMesh.visible = true;
    } else {
      // v2.40: congelado — la pala IA conserva su última pose
      if (!frozen) this.updateAIPaddlePose(this.aiPaddleMesh, this.ai, 'ai', dt);
    }
    // v2.38/2.69: durante la PRUEBA del campeonato activo (ARKANOID de
    // La Locura o la de cualquier carpeta) la pala flotante NO se ve
    if (this.champs && this.champs.testActive) this.aiPaddleMesh.visible = false;
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
    // v2.34/2.69: el campeonato ACTIVO respira (flotación, estados,
    // poderes, cartel, BSO) — La Locura pasa por aquí como los demás.
    // Con guard: un error del campeonato nunca tumba el frame.
    if (this.champs) this.champs.update(dt);
    // v2.106: cartel explicativo de pruebas (fade + callback al terminar)
    this._updateInstrucciones(dt);
    this._updateChampIntro(dt);
    // v2.128: panel ¡CONSEGUIDO! del campeonato superado (pop + fundido)
    this._updateChampConseguido(dt);
    // v2.79: el decorado de troqueles respira con la sala (visibilidad
    // según haya campeonato activo, tambaleos y vaivén)
    if (this.champDecor) this.champDecor.update(dt, now);
    // v2.85: el decorado de SALA (room) del campeonato activo — mapas de
    // los 6 planos + variantes de etapa; refuerzo barato e idempotente
    if (this.champRoom) this.champRoom.update();

    if (this.calib && this.panelDirty) {
      this.calibPanel.update({ name: this.gripName, off: this.gripOffset });
      this.panelDirty = false;
    }
    // gancho de diagnóstico (solo lectura en tests headless; no afecta al juego)
    if (typeof window !== 'undefined' && window.__wantSolverHook && !window.__solverHook) {
      window.__solverHook = { computeShotVelocityReal, predictStrike, stepPhysics,
        DIMS, applyAerodynamics,
        // v3.1.0-SRV2 · piezas del saque realista para QA (los 9 casos del
        // requisito): colisión real, validación y asistencia acotada
        collidePaddle, testPaddleContact, createPaddleSim,
        simulateServePath, findServeVelocity, applyServeProgressiveAssist,
        SERVE_TUNE, SERVE_ASSIST_TIERS,
        // v3.1.2-CCD1 · piezas de la CCD por SDF para QA headless
        collidePaddleSweep, CCD_TUNE, sweepBallVsBlade, sweepBallVsCapsuleY };
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
  /* v3.0.9-HALL1 · ASISTENCIA DEL SAQUE POR DIFICULTAD: la palanca única
   * que usan el núcleo (partido) y el PRO TRAINING (t4a/t4b). fácil = más
   * ayuda · medio = la referencia probada de la TRN1 · difícil = el saque
   * es casi enteramente tuyo. La legalidad (altura del lanzamiento, línea
   * de fondo) NO se toca: son reglas, no asistencia. */
  serveTier() {
    return SERVE_ASSIST_TIERS[this.difficulty] || SERVE_ASSIST_TIERS.medium;
  }

  /* v3.0.9-HALL1 · ENTRAR EN EL HALL DEL ANFITRIÓN — la sesión VR nace en
   * la estancia (nunca en la cancha vacía): el menú principal se abre aquí
   * delante y la pared de trofeos luce lo conseguido. Passthrough (inAR)
   * y online se quedan como estaban: el hall es una sala virtual y ahí no
   * la hay. El jugador aparece junto a la puerta, de cara a los trofeos. */
  enterHall() {
    if (this.inHall || this.inAR) return;
    if (this.net && this.net.online) return;
    this.inHall = true;
    this.rig.position.set(0, 0, HALL.cz + 2.3);
    // v3.5.0-ESC1 · HALL SIN ARRASTRES (informe del dueño: «al volver al Hall
    // desde un campeonato puede quedar la pelota sobre la mesa sin aparecer
    // la mesa»): el hall oculta mesa/marcador/IA pero NO la bola, y si se
    // sale de un DUELO en pleno rally el módulo NO re-arranca el partido
    // (solo lo hacía desde 'champtest') → la bola seguía con física real
    // rodando sobre la mesa invisible. RESET DURA: el hall SIEMPRE nace en
    // estado de SAQUE limpio (la bola en la mano libre — el gesto de siempre,
    // cinemática local al rig), bola en escala/color/base por defecto y sin
    // estela. Los módulos ya restauran lo suyo en leave(); esto es la red de
    // seguridad del NÚCLEO, sirve igual al arrancar sesión.
    this.rules.startMatch(this.mode === 'survival' ? 'survival' : 'match');
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this._hallResetBall(false);
    // v3.0.9-HALL1 · EL MUNDO VIVE DENTRO DEL RIG (mesa, IA y marcador son
    // hijos del rig — así funciona el recentrado de sala completa): al
    // viajar al hall se GUARDAN para que la estancia sea el único decorado
    // activo. La bola se queda: en el hall el jugador la lleva en la mano
    // libre (mismo gesto de saque, cinemática local al rig).
    this._hallHidden = [];
    for (const o of [this.tableGroup, this.aiPaddleMesh, this.demoPaddleMesh,
                     this.scoreboardGroup]) {
      if (o) { this._hallHidden.push(o); o.visible = false; }
    }
    if (this.hallGroup) {
      this.drawHall();
      this.hallGroup.visible = true;
    }
    if (this.roomGroup) this.roomGroup.visible = false;
    this.rules.message = T('hall_welcome');
  }

  /** v3.5.0-ESC1 · reset de la bola y su entorno (bola, estela, sombra):
   *  usado por el HALL al entrar y por exitHall al volver a la cancha. */
  _hallResetBall(hide) {
    const D = DIMS;
    if (this.ball) {
      this.ball.vel.set(0, 0, 0);
      if (this.ball.spin) this.ball.spin.set(0, 0, 0);
      this.ball.ignoreNet = false;
      this.ball.pos.set(0, D.tableTopY + (D.ballRadius || 0.02), D.tableCenterZ + 0.45);
      if (this.ball.__exPrev) this.ball.__exPrev.copy(this.ball.pos);
    }
    if (this.ballMesh) {
      this.ballMesh.visible = !hide;
      this.ballMesh.scale.setScalar(1);
      this.ballMesh.position.copy(this.ball.pos);
      const bm = this.ballMesh.material;
      if (bm) {
        // restaurar color/emisivo por si un campeonato teñió la bola
        try { bm.color.setHex(0xffffff); } catch (e0) { /* */ }
        if (bm.emissive) { try { bm.emissive.setHex(0x000000); } catch (e1) { /* */ } }
      }
    }
    if (this.trailObj) this.trailObj.visible = !hide && this.showTrail !== false;
    if (this.blob) this.blob.visible = !hide;
  }

  /* Volver a la cancha: recoloca el rig en su sitio, saca los muebles del
   * guardapolvo y deja la sala exactamente como estaba (passthrough incl.). */
  exitHall() {
    if (!this.inHall) return;
    this.inHall = false;
    this.rig.position.set(0, 0, 0);
    for (const o of this._hallHidden || []) o.visible = true;
    this._hallHidden = null;
    if (this.hallGroup) this.hallGroup.visible = false;
    if (this.roomGroup && !this.inAR) this.roomGroup.visible = true;
    // v3.5.0-ESC1 · bola limpia al volver a la cancha (nada del hall arrastrado)
    this._hallResetBall(false);
  }

  /* Carga 1 vez la insignia de un campeonato (championships/<id>/assets/
   * insignia.png). Cache en userData.hall.insigniaCache: Texture | false
   * (no existe) | null (en vuelo). Al llegar, se pega en vivo al marco. */
  _loadInsignia(id, ud) {
    ud.insigniaCache[id] = null;
    try {
      const url = 'championships/' + id + '/assets/insignia.png';
      new THREE.TextureLoader().load(url, (t) => {
        t.anisotropy = 4;
        ud.insigniaCache[id] = t;
        try {
          const sl = (ud.champRow.userData.slots || []).find((s2) => s2.id === id);
          if (sl) {
            sl.plate.material.map = t;
            sl.plate.material.color.setHex(0xffffff);
            sl.plate.material.needsUpdate = true;
          }
        } catch (e2) { /* el hall ya no está montado: nada que pegar */ }
      }, undefined, () => { ud.insigniaCache[id] = false; });
    } catch (e) { ud.insigniaCache[id] = false; }
    return null;
  }

  /* REDIBUJA la decoración del hall con lo conseguido: insignias de
   * campeonatos (championFlag), logros CRAZY del núcleo (stats.ach) y
   * PRO CIRCUITO + pieles (perfil ppxr_train_v1). Se llama en enterHall.
   * Barato: 2 canvas 2048×256 + estados de 6 marcos como mucho. */
  drawHall() {
    const ud = this.hallGroup && this.hallGroup.userData.hall;
    if (!ud) return;
    // 1) carteles con el idioma vivo
    drawHallSign(ud.signCv, T('hall_sign'));
    ud.signTex.needsUpdate = true;
    drawHallDoor(ud.doorCv, T('hall_door'));
    ud.doorTex.needsUpdate = true;
    // 2) fila de campeonatos: se reconstruye si cambió el catálogo
    const entries = (this.champs && this.champs.entries) || [];
    const row = ud.champRow;
    const need = Math.min(6, entries.length);
    if (row.userData.n !== need) {
      while (row.children.length) row.remove(row.children[0]);
      row.userData.slots = [];
      for (let i = 0; i < need; i++) {
        const px = (i - (need - 1) / 2) * 0.52;
        const frame = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.46),
          new THREE.MeshStandardMaterial({ color: 0x1a1410, roughness: 0.7,
            emissive: 0x000000, metalness: 0.1 }));
        frame.position.set(px, 1.95, 0);
        const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.36, 0.36),
          new THREE.MeshBasicMaterial({ color: 0x241c14 }));
        plate.position.set(px, 1.95, 0.004);
        row.add(frame, plate);
        row.userData.slots.push({ id: entries[i] ? entries[i].id : null, frame, plate });
      }
      row.userData.n = need;
    }
    for (const sl of row.userData.slots) {
      let won = false;
      if (sl.id) {
        try { won = this.champs.championFlag(sl.id); } catch (e) { won = false; }
      }
      sl.frame.material.emissive.setHex(won ? 0x8a5c1c : 0x000000);
      if (won) {
        let tex = ud.insigniaCache[sl.id];
        if (tex === undefined) tex = this._loadInsignia(sl.id, ud);
        if (tex && tex.isTexture) {
          sl.plate.material.map = tex;
          sl.plate.material.color.setHex(0xffffff);
        } else if (tex === false) {
          sl.plate.material.map = null;              // sin PNG: placa dorada
          sl.plate.material.color.setHex(0xc9932f);
        }
      } else {
        sl.plate.material.map = null;
        sl.plate.material.color.setHex(0x241c14);
      }
      sl.plate.material.needsUpdate = true;
    }
    // 3) LOGROS CRAZY (núcleo)
    const items = ACHIEVEMENTS.map((a) => ({
      on: !!(this.stats && this.stats.data && this.stats.data.ach[a.key]),
      emoji: a.emoji,
      name: T(a.nameKey),
    }));
    drawHallAchs(ud.achsCv, items);
    ud.achsTex.needsUpdate = true;
    // 4) PRO CIRCUITO + pieles (perfil del entrenamiento)
    let prof = null;
    try { prof = JSON.parse(localStorage.getItem('ppxr_train_v1') || 'null'); } catch (e) { prof = null; }
    const achN = (prof && prof.ach) ? Object.keys(prof.ach).length : 0;
    let stars = 0;
    if (prof && prof.stars) for (const k in prof.stars) stars += Math.max(0, Number(prof.stars[k]) || 0);
    const unl = (prof && Array.isArray(prof.unlocked)) ? prof.unlocked : ['clasica'];
    const dots = HALL_SKIN_IDS.map((sid, i) => ({
      c: HALL_SKIN_COLS[i],
      on: unl.indexOf(sid) >= 0,
    }));
    drawHallCirc(ud.circCv, {
      title: T('hall_circ'),
      big: stars + ' ★',
      sub: achN + '/9',
    }, {
      title: T('hall_palas'),
      big: unl.length + '/6',
      dots,
    });
    ud.circTex.needsUpdate = true;
  }

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
    // LIVE-TV: los intents del árbitro (point/serve/game-over) salen por el canal
    try { if (window.__PP_LIVE) window.__PP_LIVE.onIntents(intents); } catch { /* */ }
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
          // v2.34/2.69: el rival del campeonato ACTIVO reacciona a cada
          // punto (arte + voz por estado). Con guard: una excepción aquí
          // nunca tumba el frame.
          if (this.champs) this.champs.onPoint(it);
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
          // v2.34/2.69: cierre del campeonato ACTIVO (ranking + camino +
          // estado final del rival). Con guard: ningún hook del campeonato
          // puede tumbar el bucle (lección del ReferenceError de v2.39).
          if (this.champs) this.champs.onMatchOver(it.winner);
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
          // v2.34: anti-spam de bote — la física puede emitir ráfagas de
          // eventos 'table' en un mismo instante (esquina + canto); el
          // sonido se limita a uno cada 60 ms.
          if (!this._lastBounceSfx || performance.now() - this._lastBounceSfx > 60) {
            this._lastBounceSfx = performance.now();
            this.audio.tableBounce(pan, Math.min(1, e.speed / 6));
          }
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
          // v2.44: en ARKANOID la vibración se REFUERZA (petición expresa:
          // "cuando la pala golpea la bola no tenemos respuesta háptica")
          if (e.paddleIndex !== undefined && e.paddleIndex >= 0) {
            const arkOn = this.rules.state === 'arkanoid';
            this.haptic(e.paddleIndex,
              Math.min(1, (arkOn ? 0.68 : 0.5) + e.speed / 9),
              arkOn ? 85 : 70);
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
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { PP_ICONS, T, TLang, WORLDRANK, __PP_TELE, __ppLang, ppPlayerName, setLang, wrlBadgeImg } from './c00_pre_three.js';
import { makePaddleVisual } from './c01_modelos_3d.js';
import { AI_PRESETS, DIMS, MOUNT_QUAT_RIGHT, ROOM_THEMES, SERVE_ASSIST_TIERS, SERVE_TUNE, mountQuatFor, scalePreset } from './c02_cfg_escena.js';
import { GameAudio } from './c03_audio_voz.js';
import { CCD_TUNE, applyAerodynamics, createPaddleSim, sweepBallVsBlade, sweepBallVsCapsuleY, tmpMountQ, tmpTarget, tmpV, updatePaddleSim } from './c04_fisica_ccd.js';
import { __ppServeTelemetry, applyServeProgressiveAssist, collidePaddle, collidePaddleSweep, computeShotVelocity, computeShotVelocityReal, findServeVelocity, predictStrike, simulateServePath, stepPhysics, testPaddleContact } from './c05_colisiones_ia_golpeo.js';
import { ACHIEVEMENTS, GameStats, OpponentAI, Rules } from './c06_logros_stats_ia_rival.js';
import { createBall, createBlobShadow, createChampDecor, createRoom, createTable } from './c07_escena_sala.js';
import { HALL, HALL_SKIN_COLS, HALL_SKIN_IDS, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createScoreboard, drawHallAchs, drawHallCirc, drawHallDoor, drawHallSign } from './c08_hall_hud.js';
import { NetLink } from './c09_red_netlink.js';
import { AIM_BLADE, AIM_BX, AIM_BY, AIM_BZ, AIM_FACE, AIM_FWD, AIM_RIGHT, AIM_XA, AIM_Z, AI_TOSS_T, BALL_HAND_LIFT, CHAMPS_STATE, MENU_LOGO_SRC, SWING_POSE, aimM, aimPitchQ, aimRollQ, poseQ, swingV } from './c10_menu_saque.js';
import { ChampLoader, NORMAS_SKIN, muDir, muGrip, muHead, muQ, muRaycaster, netTmpP, netTmpQ, pcA, pcC, pcN, pcT } from './c11_champloader.js';
import { wrapText } from './c13_ui_arranque.js';
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
/* DEPS-FASE2-FIN */

/* =====================================================================
 *  INTERFAZ · PORTADA ANIMADA + botón JUGAR EN VR + HUD (v2.28)
 *  Portada minimalista: arte de cabecera, palas de idioma y el gran botón
 *  cartoon JUGAR/PLAY EN VR. La dificultad, las salas, el online y los
 *  ajustes viven DENTRO del menú principal de VR (panel flotante acordeón).
 * ===================================================================== */
export const overlay = document.getElementById('overlay');
export const statusEl = document.getElementById('status');
export const vrbtn = document.getElementById('vrbtn');
export const arBtn = document.getElementById('arbtn');
// v2.30: fuera el botón "Ver demo en pantalla (sin visor)" y su HUD — la
// portada ya no juega ninguna partida de fondo (solo escena + música).
export const playEs = document.getElementById('playEs');
export const playEn = document.getElementById('playEn');

// v2.28: el gran botón cartoon cambia JUGAR <-> PLAY según el idioma

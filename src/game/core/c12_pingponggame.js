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
    // v3.6.34 · MEGA PALA NORMATIVA (núcleo): mecánica que TODOS los
    // campeonatos heredan (implementación junto a haptic()). El aviso es
    // un ICONO sobre el mango + jingle; la carga llega con un rally que
    // supera los 10 golpes; el gatillo la libera con la bola en juego.
    // Conmutador «Pala Mejorada» en la página AJUSTES del menú.
    this._BASE_HIT = DIMS.hitAssistRadius;
    try { this.palaMejorada = localStorage.getItem('pp_pala_mejorada_v1') !== '0'; } catch { this.palaMejorada = true; }
    this._megaT = 0;                  // s restantes de ACTIVA
    this._megaS = 1;                  // escala visual actual de las monturas
    // v3.6.36 · MATRIZ DE PODERES (diseño del dueño): un poder distinto NO
    // sustituye — ENTRA en la matriz (orden de llegada); el joystick ⟷ de
    // cualquier mando CICLA el seleccionado (flechas ‹ › en el icono, sin
    // envolver en los bordes) y el gatillo gasta el SELECCIONADO. En todo
    // momento SOLO UN icono se ve en la pala. Mismo poder → acumula ×2/×3
    // (tope 3, intacto).
    this._megaMatriz = [];            // [{id, n}] en ORDEN DE LLEGADA
    this._megaIdx = 0;                // poder SELECCIONADO de la matriz
    this._megaStick = { x: 0, cd: 0 }; // antirrebote del joystick ⟷
    // v3.6.36 · escritorio: ←/→ ciclan la matriz (mismo camino que el stick)
    try {
      window.addEventListener('keydown', (ev) => {
        if (ev.key === 'ArrowRight') { try { this._megaCicla(1); } catch (eM) { /* */ } }
        else if (ev.key === 'ArrowLeft') { try { this._megaCicla(-1); } catch (eM2) { /* */ } }
      });
    } catch (eK) { /* sin window (entornos de prueba) */ }
    this._megaRallyGrants = 0;        // concesiones ya dadas en ESTE rally
    this._megaWarn = false;           // aviso «se agota» ya disparado
    this._megaPngs = {};              // Images por poder (async)
    this._megaPngHecho = false;
    this._megaPngCarga();             // los PNG llegan en paralelo al juego
    // v3.6.36 · SÚPER EFECTO (segundo poder del registro): ventana PROPIA
    // de 8 s o 5 golpes con efecto (lo que ocurra antes; reglas del dueño).
    this._efectoT = 0;                // s restantes de súper efecto
    this._efectoGolpes = 0;           // golpes potenciados restantes
    this._efectoWarn = false;
    this._efectoFx = null;            // [fx0, fx1] canto cian + onda
    this._efectoFxOn = false;
    this._megaFx = null;              // [fx0, fx1] canto+onda por montura
    this._megaFxOn = false;
    this._megaIcon = null;            // [icon0, icon1] icono de carga
    this._megaIconOn = false;
    this._megaIconPop = 0;            // animación de aparición (1 → 0)
    this._megaTex = null;             // textura del icono (compartida)
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
      // v3.6.30 · en el HALL la pala no se ve (ahí nunca se juega): el cambio
      // de mano por A/X o la reconexión del mando no la resucita.
      if (this.paddleMounts[k]) this.paddleMounts[k].visible =
        !this.inHall && k === this.paddleHand;
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
    this.rules.startMatch(back);   // v3.6.29: PRESERVA bestOf (3 libre · 1 campeonato)
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
    // v3.6.29 · MEJOR DE 3: el PARTIDO libre se disputa al mejor de 3 juegos
    // (2 victorias = campeón del enfrentamiento, petición del dueño).
    this.rules.bestOf = 3;
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
    this.rules.bestOf = 3;   // v3.6.29: el enfrentamiento online también al mejor de 3
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
    this.rules.bestOf = 3;   // v3.6.29: de vuelta con la CPU, seguimos al mejor de 3
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
      // v3.6.31 · VER PRESENTACIÓN (opcional): la intro del rival sólo se
      // muestra SOLA la primera vez que se entra; este botón la re-ve a
      // demanda (launch con opts.intro) — el vídeo deja de ser obligatorio.
      btn('champintro:' + ch.id, 56, y, 912, 52, T('champ_intro_btn'),
        false, undefined, undefined, 22);
      y += 64;
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
    // v3.6.31 · el texto heredado «11-point match vs the Clown… MEGA
    // PADDLE» (hint del ARCADE v2.34) ya NO se pinta al pie del listado:
    // describía una tarjeta vieja, se leía como si aplicara a todos los
    // campeonatos y la MEGA PALA es poder exclusivo de La Locura (Crazy
    // Combo). Cada tarjeta ya cuenta lo suyo.
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
    // v3.6.34 · PALA MEJORADA: conmutador de los superpoderes de la pala
    // (MEGA PALA normativa — rally 11+ la carga, gatillo la suelta).
    // Activada los permite; desactivada la pala se comporta NORMAL.
    btn('pmej', 56, y, 912, 56, T('btn_pmej', { v: yn(this.palaMejorada) }), !!this.palaMejorada, undefined, !!this.palaMejorada, 23);
    y += 68;
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
      case 'champintro':
        // v3.6.31 · VER PRESENTACIÓN: relanza el campeonato mostrando la
        // intro (el vídeo de la historia pasa a ser OPCIONAL — sólo se ve
        // solo la primera vez; aquí se re-ve a demanda).
        if (this.champs) this.champs.launch(arg, { intro: true });
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
          else { this.rules.bestOf = 3; this.rules.startMatch('match'); this.resetToss(); }
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
        // v3.6.30 · el hall no muestra estela (su bola está oculta)
        if (this.trailObj) this.trailObj.visible = this.showTrail && !this.inHall;
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
      case 'pmej': {
        // v3.6.34 · PALA MEJORADA: superpoderes de pala sí/no (persistente).
        // Al apagar, la recogida es INMEDIATA (radio, escala, icono y FX a
        // cero con dispose — la pala queda exacta como siempre).
        this.palaMejorada = !this.palaMejorada;
        try { localStorage.setItem('pp_pala_mejorada_v1', this.palaMejorada ? '1' : '0'); } catch { /* */ }
        if (!this.palaMejorada) this._megaNormReset();
        this.rules.message = T('msg_pmej', { v: this.palaMejorada ? T('yes') : T('no') });
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
          this.rules.bestOf = 3;   // v3.6.29: revancha de menú = enfrentamiento nuevo al mejor de 3
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

    // v3.6.31 · MENÚ PRIORITARIO: si el menú (o el prompt del Hall) está
    // abierto manda ÉL — los clics van a SUS botones aunque la intro del
    // campeonato siga detrás (antes la intro se comía los clics: el menú
    // se abría con B pero era un decorado muerto que no respondía).
    if (this.menuOpen) {
      const hov = this.menuHover[i];
      if (hov >= 0) this.menuClick(hov);
      return;
    }

    // v2.130 · INTRO DE CAMPEONATO: el gatillo lanza la partida SOLO desde
    // el botón JUGAR (el vídeo de la historia es OPCIONAL). Un gatillo que
    // no impacta el botón reintenta el audio del vídeo (gesto del usuario).
    // v3.6.31 · corre DESPUÉS del menú: el menú abierto tiene prioridad.
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
    // v3.6.30 · HALL SIN JUEGO: en la estancia el gatillo sólo vive en el
    // menú (arriba) — ni saque, ni revancha, ni pistola, ni rejugada. Si el
    // menú está cerrado, el gatillo no hace nada (B lo vuelve a abrir).
    if (this.inHall) return;
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
    // v3.6.35 · SUPERPODER DE PALA (núcleo): con la bola en juego el
    // GATILLO DEL MANDO LIBRE suelta el poder en TODOS los campeonatos
    // (conmuta solo al cambiar la pala de mano; si el campeonato ocupa la
    // mano libre — pistola del Oeste armada — el gatillo de la pala queda
    // de respaldo). En 'serve' el gatillo sigue SIENDO DEL SAQUE (cero
    // conflicto). «Pala Mejorada» apagado = pala 100 % normal.
    if (this.rules.state === 'rally' && this.megaTrigger(i)) return;
    if (this.rules.state === 'rally' && this.champs &&
        typeof this.champs.megaTrigger === 'function') {
      let consumed = false;
      try { consumed = this.champs.megaTrigger(i) === true; } catch (e) { /* */ }
      if (consumed) return;
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
      // v3.6.29: PRESERVA bestOf — la revancha por gatillo repite el contexto
      // (libre = nueva serie al mejor de 3; campeonato = duelo a juego único)
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
    if (this.calib || this.menuOpen || this.inHall) return;   // v3.6.30: el hall no saca
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

  /* ============ v3.6.34 · MEGA PALA NORMATIVA (núcleo) ============
   * Correcciones del dueño tras V3.6.33:
   *  · «eliminar el núcleo dorado» — FUERA el núcleo/halo/aro/chispas de
   *    V3.6.33 (y cualquier FX que viva dentro o sobre la hoja). El aviso
   *    de carga es ahora un ICONO pequeño sobre el mango (dibujo de la
   *    pala con flechas de crecida) + jingle característico: el jugador
   *    SABE que la tiene y de qué poder se trata sin que estorbe.
   *  · «se puede activar cuando un rally supera los 10 golpes» — la carga
   *    ya NO se arma al empezar el partido ni se recarga a tiempo: UNA
   *    regla (norma en TODOS los campeonatos): rally de 11+ golpes = carga
   *    (una por rally; sin gastar se conserva hasta usarse).
   *  · «extensivo a todos los campeonatos y las plantillas» — vive en el
   *    NÚCLEO: locura, magia, oeste, orbital, valle_neon y cualquier
   *    campeonato nuevo heredan la mecánica sin escribir una línea (los
   *    módulos corren sobre rules/paddleMounts del núcleo).
   *  · Conmutador «Pala Mejorada» (AJUSTES, pp_pala_mejorada_v1): apagado
   *    = pala 100 % normal (sin carga, sin icono, gatillo intacto).
   * Modelo: CARGADA (icono + jingle) → gatillo en rally → ACTIVA 8 s
   *  (canto de energía BackSide ×1,055 que abraza la SILUETA desde fuera +
   *  pala ×1,30 + radio de detección ×1,38 + onda de choque + power-up
   *  sonoro + háptica) → DORMIDA hasta el siguiente rally de 11+.
   * Todo cuelga de las DOS monturas: viaja sola al cambiar de mano.
   * Construcción PEREZOSA: nada se crea hasta la primera carga (coste
   * cero mientras dormida) y _megaNormReset recoge todo con dispose. */

  /** ¿Permite el dueño los superpoderes de pala? (conmutador AJUSTES).
   *  v3.6.36 · SOLO EN CAMPEONATOS (petición del dueño): «los potenciadores
   *  SOLO aparecen en los campeonatos contra rivales, NO en un partido
   *  contra la máquina fuera de los campeonatos». Con el hall y la
   *  calibración seguimos igual (zona neutra). */
  megaEnabled() {
    if (this.palaMejorada === false) return false;
    return !!(this.champs && this.champs.active);
  }

  /** GATILLO VOLUNTARIO con la bola en juego (todos los campeonatos).
   *  v3.6.35 · diseño aprobado: el gatillo del mando LIBRE (el que no
   *  tiene la pala — conmuta solo al cambiar de mano) suelta el poder;
   *  si un campeonato ocupa la mano libre (pistola del Oeste armada), el
   *  gatillo de la pala queda como respaldo. En escritorio (sin XR) la
   *  pulsación de ratón cuenta como mano libre. En 'serve' el gatillo
   *  sigue SIENDO DEL SAQUE y con «Pala Mejorada» apagado la pala es
   *  100 % normal (false = el núcleo no la consume).
   *  v3.6.36 · suelta el poder SELECCIONADO de la MATRIZ (joystick ⟷
   *  cambia la selección; flechas ‹ › en el icono): MEGA PALA activa +
   *  gatillo = ALARGA (+15 s por carga, el tamaño NUNCA apila); SÚPER
   *  EFECTO activo + gatillo = RECARGA su ventana (8 s / 5 golpes). */
  megaTrigger(i) {
    if (!this.megaEnabled() || this.inHall || this.calib) return false;
    if (!this.rules || this.rules.state !== 'rally') return false;
    const libre = (i !== this.paddleHand) || !this.renderer.xr.isPresenting;
    const gunVive = !!(this.champs && this.champs.gunArmed);
    if (!libre && !gunVive) return false;       // mano de la pala: solo respaldo
    const ent = this._megaSel();
    if (!ent) {
      // sin cargas: aviso honesto + blip grave + háptica corta
      this.rules.message = T('arc_mega_cd');
      try { this.audio.playOsc(220, 150, 0.12, 'sine', 0.08, 0); } catch (e) { /* */ }
      if (this.renderer.xr.isPresenting) {
        try { this.haptic(i, 0.2, 60); } catch (e2) { /* */ }
      }
      return true;
    }
    // v3.6.36 · el gatillo libera el poder SELECCIONADO de la matriz
    if (ent.id === 'efecto') return this._efectoTrigger(ent);
    if (this._megaT > 0) {
      // MEGA ya ACTIVA: una carga nueva ALARGA (+15 s; el tamaño no apila)
      this._megaGasta(ent);
      this._megaT += MEGA_DUR;
      this._megaIconRefresh();
      return true;
    }
    // LIBERAR: MEGA_DUR s de MEGA PALA (el icono cede a lo que quede)
    this._megaGasta(ent);
    this._megaT = MEGA_DUR;
    this._megaWarn = false;
    this._megaFxStart();
    this.rules.message = T('arc_mega_go');
    return true;
  }

  /** v3.6.36 · PODER SELECCIONADO de la matriz (con clamp de índice). */
  _megaSel() {
    if (!this._megaMatriz.length) return null;
    if (this._megaIdx >= this._megaMatriz.length) this._megaIdx = 0;
    return this._megaMatriz[this._megaIdx] || null;
  }

  /** ¿Está ACTIVO ahora mismo el poder seleccionado? (el icono cede a su
   *  efecto: MEGA en marcha o ventana de SÚPER EFECTO en marcha). */
  _megaSelActiva() {
    const ent = this._megaSel();
    if (!ent) return false;
    if (ent.id === 'mega') return this._megaT > 0;
    if (ent.id === 'efecto') return this._efectoT > 0;
    return false;
  }

  /** v3.6.36 · GASTA 1 carga del poder dado (y lo retira de la matriz
   *  si se queda a cero; el índice se CLAMPEA — sin envolver). */
  _megaGasta(ent) {
    ent.n--;
    if (ent.n <= 0) {
      const ix = this._megaMatriz.indexOf(ent);
      if (ix >= 0) this._megaMatriz.splice(ix, 1);
      if (this._megaIdx >= this._megaMatriz.length) {
        this._megaIdx = Math.max(0, this._megaMatriz.length - 1);
      }
    }
    this._megaIconRefresh();
  }

  /** CARGA NORMATIVA v3.6.35: cada 11 golpes del rally (11, 22, 33…)
   *  concede +1 carga de un poder ALEATORIO del registro PODERES_PALA.
   *  MISMO poder → ACUMULA (×2, ×3); con la mano llena (tope ×3), «toc»
   *  de tope y nada. PODER DISTINTO → SUSTITUYE (las cargas viejas se
   *  pierden: úsalas o arriésgate). Icono DEL DUEÑO (PNG) con etiqueta
   *  ×N + VOZ animosa + jingle propio (tríada mayor ascendente + brillo
   *  — firma DISTINTA del arpegio square 420→860→1400 de la activación)
   *  + háptica. La pista «norma nueva» suena UNA sola vez por navegador. */
  _megaCharge() {
    const ids = PODERES_PALA.map((p) => p.id);
    const id = ids[Math.floor(Math.random() * ids.length)] || 'mega';
    let ent = this._megaMatriz.find((e) => e.id === id);
    if (ent) {
      if (ent.n >= MEGA_TOPE) {
        // TOPE ×3 de ESE poder: la mano está llena — «toc» honesto
        this.rules.message = T('arc_mega_full');
        try { this.audio.playOsc(160, 120, 0.12, 'triangle', 0.14, 0); } catch (e) { /* */ }
        return;
      }
      ent.n++;                                // MISMO poder: ACUMULA ×2/×3
    } else {
      // v3.6.36 · PODER DISTINTO: ENTRA en la matriz (posición nueva al
      // final, orden de llegada) y se SELECCIONA solo — su icono y su voz
      // lo anuncian ya (el dueño lo ve y lo oye sin hacer nada).
      ent = { id: id, n: 1 };
      this._megaMatriz.push(ent);
      this._megaIdx = this._megaMatriz.length - 1;
    }
    this._megaIconRefresh();
    if (!this._megaSelActiva()) this._megaIconVis(true);
    let msg = this._poderNombre(id);
    if (ent.n > 1) msg += ' ×' + ent.n;
    try {
      if (!localStorage.getItem('pp_mega_norm_hint')) {
        localStorage.setItem('pp_mega_norm_hint', '1');
        msg = T('arc_mega_hint');
      }
    } catch (e) { /* localStorage bloqueado */ }
    this.rules.message = msg;
    try { this.audio.playOsc(523, 659, 0.09, 'triangle', 0.14, 0); } catch (e) { /* */ }
    try { this.audio.playOsc(659, 784, 0.09, 'triangle', 0.14, 0.09); } catch (e) { /* */ }
    try { this.audio.playOsc(784, 1568, 0.24, 'triangle', 0.16, 0.18); } catch (e) { /* */ }
    try { this.audio.playOsc(2093, 1976, 0.14, 'sine', 0.05, 0.2); } catch (e) { /* */ }
    this._megaVoz(id);
    if (this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.5, 120); } catch (e) { /* */ }
    }
  }

  /** v3.6.35 · VOZ ANIMOSA del poder (petición del dueño: «una voz muy
   *  animosa lo comunique»). MP3 pre-generado EMBEBIDO como data-URI:
   *  cero latencia, cero red, funciona offline en el Quest. Mismo patrón
   *  del _playRivalBuffer: decode una vez + caché por AudioContext; si
   *  algo falla, el audio NUNCA rompe el bucle del juego. */
  _megaVoz(id) {
    try {
      const A = this.audio;
      if (!A || !A.ctx) return;
      // v3.6.36 · voz por PODER y por IDIOMA (petición del dueño: voz
      // nativa castellana; jugando en inglés, el audio traducido).
      const key = id + ((__ppLang === 'en') ? '_en' : '_es');
      A._megaVozBuf = A._megaVozBuf || {};
      const cached = A._megaVozBuf[key];
      const play = (buf) => {
        try {
          if (!A.ctx || !A.master) return;
          const out = A.panNode(0);
          if (!out) return;
          const src = A.ctx.createBufferSource();
          src.buffer = buf;
          const g = A.ctx.createGain();
          g.gain.value = 1.0;          // la voz, bien presente (v2.35)
          src.connect(g); g.connect(out);
          src.start();
        } catch { /* */ }
      };
      if (cached && cached.ctx === A.ctx && cached.buf) { play(cached.buf); return; }
      if (cached && (cached.busy || cached.failed)) return;
      const fuente = this._poderVoz(key);
      if (!fuente) return;
      const entry = { ctx: A.ctx, buf: null, busy: true };
      A._megaVozBuf[key] = entry;
      fetch(fuente)
        .then((r) => r.arrayBuffer())
        .then((ab) => A.ctx.decodeAudioData(ab))
        .then((buf) => { entry.buf = buf; entry.busy = false; play(buf); })
        .catch(() => { entry.busy = false; entry.failed = true; });
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  /** v3.6.36 · nombre (megáfono) y fuente de voz por idioma del registro. */
  _poderNombre(id) {
    const p = PODERES_PALA.find((x) => x.id === id);
    return p ? p.nombre() : T('poder_mega');
  }

  _poderVoz(key) {
    const id = key.replace(/_(es|en)$/, '');
    const en = key.slice(-3) === '_en';
    const p = PODERES_PALA.find((x) => x.id === id);
    if (!p) return null;
    return en ? (p.vozEn || p.voz) : p.voz;
  }

  /** v3.6.36 · CICLO de la matriz con el JOYSTICK (petición del dueño):
   *  empujar el stick ⟷ de CUALQUIER mando cambia el poder seleccionado;
   *  en escritorio, las flechas ←/→. Con UN solo poder no hay nada que
   *  ciclar; en los BORDES no envuelve (índice 0 no va a la izquierda; el
   *  último no va a la derecha) — exactamente como las flechas pintan. */
  _megaCiclo(dt) {
    if (this._megaMatriz.length < 2) {
      this._megaStick.x = 0;
      return;
    }
    const st = this._megaStick;
    if (st.cd > 0) st.cd -= dt;
    let x = 0;
    try {
      const a = this.stickAxis(0) || { x: 0 };
      const b = this.stickAxis(1) || { x: 0 };
      x = (Math.abs(a.x) >= Math.abs(b.x)) ? a.x : b.x;   // el mando más decidido
    } catch (e) { x = 0; }
    if (st.cd <= 0 && Math.abs(x) > 0.62 &&
        Math.abs(st.x) <= 0.62) {                        // flanco de subida
      this._megaCicla(x > 0 ? 1 : -1);
      st.cd = 0.33;
    }
    st.x = x;
  }

  /** Cambia el poder seleccionado (dir = +1 derecha, −1 izquierda). */
  _megaCicla(dir) {
    if (!this.megaEnabled() || this.inHall || this.calib) return;
    const L = this._megaMatriz.length;
    if (L < 2) return;
    const ni = this._megaIdx + dir;
    if (ni < 0 || ni >= L) {
      // BORDE: blip suave y nada — sin envolver (la flecha no existe allí)
      try { this.audio.playOsc(300, 260, 0.06, 'sine', 0.05, 0); } catch (e) { /* */ }
      return;
    }
    this._megaIdx = ni;
    this._megaIconRefresh();
    this._megaIconVis(!this._megaSelActiva());
    try {
      this.audio.playOsc(dir > 0 ? 620 : 520, dir > 0 ? 880 : 380,
        0.09, 'triangle', 0.10, 0);
    } catch (e) { /* */ }
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.25, 50); } catch (e2) { /* */ }
    }
    try { this.rules.message = this._poderNombre(this._megaMatriz[this._megaIdx].id); } catch (e3) { /* */ }
  }

  /** v3.6.36 · SÚPER EFECTO: gatillo con ese poder seleccionado. Ventana
   *  propia del dueño: 8 segundos O 5 golpes con efecto (lo que ocurra
   *  antes). Activo + gatillo con cargas = RECARGA la ventana completa. */
  _efectoTrigger(ent) {
    if (this._efectoT > 0) {
      this._megaGasta(ent);
      this._efectoT = EFECTO_DUR;
      this._efectoGolpes = EFECTO_GOLPES;
      this._efectoWarn = false;
      this._efectoOnda();
      this.rules.message = T('arc_efecto_go');
      return true;
    }
    this._megaGasta(ent);
    this._efectoT = EFECTO_DUR;
    this._efectoGolpes = EFECTO_GOLPES;
    this._efectoWarn = false;
    try { this._buildEfectoFx(); } catch (e) { this._efectoFx = null; }
    this._efectoFxVis(true);
    this._efectoOnda();
    // power-up sonoro PROPIO (firma distinta del arpegio dorado):
    // barrido «de giro» sawtooth 340→760 + remate 760→1280
    try { this.audio.playOsc(340, 760, 0.16, 'sawtooth', 0.12, 0); } catch (e) { /* */ }
    try {
      window.setTimeout(() => {
        try { if (!this.disposed) this.audio.playOsc(760, 1280, 0.2, 'sawtooth', 0.10, 0); } catch (e2) { /* */ }
      }, 110);
    } catch (e) { /* */ }
    this.rules.message = T('arc_efecto_go');
    if (this.renderer.xr && this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.7, 160); } catch (e2) { /* */ }
    }
    return true;
  }

  /** Fin de la ventana de SÚPER EFECTO (8 s agotados o 5.º golpe). */
  _efectoFin() {
    this._efectoT = 0;
    this._efectoGolpes = 0;
    this._efectoFxVis(false);
    this.rules.message = T('arc_efecto_fin');
    try { this.audio.playOsc(660, 330, 0.16, 'sine', 0.12, 0); } catch (e) { /* */ }
  }

  /** LIBERACIÓN del poder: canto de energía + onda de choque + power-up
   *  sonoro + háptica (motor probado de V3.6.33, sin el núcleo). */
  _megaFxStart() {
    try { this._buildMegaFx(); } catch (e) { this._megaFx = null; }
    this._megaFxVis(true);
    this._megaShock();
    try { this.audio.playOsc(420, 860, 0.16, 'square', 0.15, 0); } catch (e) { /* */ }
    try {
      window.setTimeout(() => {
        try { if (!this.disposed) this.audio.playOsc(860, 1400, 0.2, 'square', 0.12, 0); } catch (e2) { /* */ }
      }, 110);
    } catch (e) { /* */ }
    if (this.renderer.xr.isPresenting) {
      try { this.haptic(this.paddleHand, 0.75, 180); } catch (e) { /* */ }
    }
  }

  _fxVis(lista, vis) {
    if (!lista) return;
    for (const fx of lista) {
      if (fx) fx.visible = vis;
    }
  }

  _megaFxVis(vis) {
    this._megaFxOn = vis;
    this._fxVis(this._megaFx, vis);
  }

  _efectoFxVis(vis) {
    this._efectoFxOn = vis;
    this._fxVis(this._efectoFx, vis);
  }

  /** ONDA DE CHOQUE (one-shot por montura, 0,55 s — la anima updateMega). */
  _fxOnda(lista) {
    if (!lista) return;
    for (const fx of lista) {
      if (fx) fx.userData.shockT = 0.55;
    }
  }

  _megaShock() {
    this._fxOnda(this._megaFx);
  }

  _efectoOnda() {
    this._fxOnda(this._efectoFx);
  }

  /** CANTO DE ENERGÍA: clon EXACTO de la pala montada (children[0]) con
   *  materiales BackSide aditivos ×1,055 — el borde dorado abraza la
   *  SILUETA desde fuera y el depth test impide entrar en la hoja (la
   *  lección de V3.6.33 que se conserva). ONDA: anillo one-shot. */
  _buildMegaFx() {
    if (!this._megaFx) this._megaFx = this._fxBuild(0xffc84a);
  }

  _buildEfectoFx() {
    if (!this._efectoFx) this._efectoFx = this._fxBuild(0x54d8f0);
  }

  /** v3.6.36 · constructor de CANTO + ONDA parametrizado por COLOR: oro
   *  para MEGA PALA, cian para SÚPER EFECTO. Los dos efectos pueden
   *  convivir (son ortogonales: tamaño vs. giro) — el cian va ×1,07 para
   *  no pelearse (z-fight) con el oro cuando ambos están activos. */
  _fxBuild(colHex) {
    if (!this.paddleMounts) return null;
    const cian = colHex === 0x54d8f0;
    const lista = [];
    for (let i = 0; i < 2; i++) {
      const m = this.paddleMounts[i];
      if (!m) { lista.push(null); continue; }
      const fx = new THREE.Group();     // espacio MONTURA (identidad)
      fx.visible = false;
      const rim = m.children[0] ? m.children[0].clone(true) : null;
      const rimMats = [];
      if (rim) {
        rim.scale.multiplyScalar(cian ? 1.07 : 1.055);
        rim.traverse((o) => {
          if (!o.isMesh) return;
          const src = Array.isArray(o.material) ? o.material : [o.material];
          const dorados = src.map(() => new THREE.MeshBasicMaterial({
            color: colHex, transparent: true, opacity: 0.55,
            blending: THREE.AdditiveBlending, side: THREE.BackSide,
            depthWrite: false,
          }));
          o.material = Array.isArray(o.material) ? dorados : dorados[0];
          o.castShadow = false;
          o.receiveShadow = false;
          for (const dm of dorados) rimMats.push(dm);
        });
        fx.add(rim);
      }
      const shock = new THREE.Mesh(
        new THREE.TorusGeometry(0.1, 0.006, 8, 48),
        new THREE.MeshBasicMaterial({ color: cian ? 0xaef0ff : 0xffdf8e,
          transparent: true, opacity: 0, blending: THREE.AdditiveBlending,
          depthWrite: false }));
      shock.position.y = 0.14;          // centro de la HOJA
      shock.visible = false;
      fx.add(shock);
      fx.userData = { rim, rimMats, shock, shockT: 0 };
      m.add(fx);
      lista.push(fx);
    }
    return lista;
  }

  /** ICONO DE CARGA v3.6.36: sprite-billboard ANCLADO al mango (la base
   *  de la mano, justo encima del mando — pide el dueño que «forme parte
   *  de la pala y no distraiga»). Textura: el PNG DEL PODER SELECCIONADO
   *  (mega: SuperPala_Crece.png del dueño · efecto: SuperPala_Efecto.png)
   *  + etiqueta ×N cuando hay 2+ cargas + FLECHAS ‹ › de la matriz cuando
   *  hay vecino (sin flechas en los bordes — sin envolver). Si un PNG no
   *  llegara, cae al dibujo canvas de reserva (oro para mega, cian para
   *  efecto). Billboard = legible en cualquier ángulo; SOLO UN icono se
   *  ve en la pala en todo momento (el seleccionado). */
  _megaIconTex() {
    const cv = document.createElement('canvas');
    cv.width = cv.height = 256;
    const c2 = cv.getContext('2d');
    c2.lineJoin = 'round'; c2.lineCap = 'round';
    const ent = this._megaSel();
    const id = ent ? ent.id : 'mega';
    const n = ent ? ent.n : 0;
    let dibujo = false;
    try {
      const png = this._megaPngs[id];
      if (png && png.complete && png.naturalWidth > 0) {
        c2.drawImage(png, 0, 0, 256, 256);
        dibujo = true;
      }
    } catch (e) { dibujo = false; }
    if (!dibujo) {
      if (id === 'efecto') {
        // RESERVA del efecto: bola con flechas de giro (cian)
        c2.beginPath(); c2.arc(128, 122, 62, 0, Math.PI * 2);
        c2.fillStyle = '#fafafa'; c2.fill();
        c2.lineWidth = 8; c2.strokeStyle = '#2b6ea8'; c2.stroke();
        c2.beginPath(); c2.arc(128, 122, 30, 0, Math.PI * 2);
        c2.strokeStyle = '#cfd8e2'; c2.lineWidth = 6; c2.stroke();
        c2.lineWidth = 14; c2.strokeStyle = '#54d8f0';
        c2.beginPath(); c2.arc(128, 122, 92, -1.1, 0.7); c2.stroke();
        c2.beginPath(); c2.arc(128, 122, 92, 2.0, 3.5); c2.stroke();
        c2.fillStyle = '#54d8f0';
        c2.beginPath(); c2.moveTo(214, 92); c2.lineTo(196, 118); c2.lineTo(226, 122);
        c2.closePath(); c2.fill();
      } else {
        // RESERVA: el dibujo dorado de V3.6.34 (pala + 4 flechas de crecida)
        const dor = c2.createLinearGradient(0, 30, 0, 226);
        dor.addColorStop(0, '#ffe9a3'); dor.addColorStop(0.5, '#ffc84a');
        dor.addColorStop(1, '#e8961e');
        // hoja
        c2.beginPath(); c2.arc(128, 92, 56, 0, Math.PI * 2);
        c2.fillStyle = dor; c2.fill();
        c2.lineWidth = 9; c2.strokeStyle = '#5b3a08'; c2.stroke();
        // mango
        c2.beginPath();
        c2.moveTo(114, 138); c2.lineTo(142, 138); c2.lineTo(136, 224);
        c2.lineTo(120, 224); c2.closePath();
        c2.fillStyle = dor; c2.fill(); c2.stroke();
        // 4 flechas diagonales hacia FUERA (crece)
        const arr = [[52, 52, 20, 20], [204, 52, 236, 20],
                     [52, 204, 20, 236], [204, 204, 236, 236]];
        for (const [x1, y1, x2, y2] of arr) {
          c2.lineWidth = 13; c2.strokeStyle = '#ffe9a3';
          c2.beginPath(); c2.moveTo(x1, y1); c2.lineTo(x2, y2); c2.stroke();
          const ang = Math.atan2(y2 - y1, x2 - x1);
          c2.beginPath();
          c2.moveTo(x2, y2);
          c2.lineTo(x2 - Math.cos(ang - 0.5) * 24, y2 - Math.sin(ang - 0.5) * 24);
          c2.lineTo(x2 - Math.cos(ang + 0.5) * 24, y2 - Math.sin(ang + 0.5) * 24);
          c2.closePath();
          c2.fillStyle = '#ffe9a3'; c2.fill();
        }
        // destellos de poder
        c2.fillStyle = '#fff6d8';
        for (const [x, y, r] of [[128, 14, 8], [244, 128, 6], [12, 128, 6]]) {
          c2.beginPath(); c2.arc(x, y, r, 0, Math.PI * 2); c2.fill();
        }
      }
    }
    // ETIQUETA ×N (v3.6.35): cargas del poder seleccionado, la idea «+2»
    if (n >= 2) {
      c2.beginPath(); c2.arc(203, 203, 42, 0, Math.PI * 2);
      c2.fillStyle = '#d92b2b'; c2.fill();
      c2.lineWidth = 7; c2.strokeStyle = '#ffffff'; c2.stroke();
      c2.fillStyle = '#ffffff';
      c2.font = 'bold 46px sans-serif';
      c2.textAlign = 'center'; c2.textBaseline = 'middle';
      c2.fillText('×' + n, 203, 205);
    }
    // FLECHAS de la MATRIZ (v3.6.36): ‹ si hay anterior, › si hay siguiente
    // (en los bordes NO hay flecha — y el joystick tampoco envuelve)
    const chev = (x, dir) => {
      c2.beginPath();
      c2.moveTo(x + dir * 14, 108);
      c2.lineTo(x - dir * 10, 128);
      c2.lineTo(x + dir * 14, 148);
      c2.lineWidth = 13;
      c2.strokeStyle = 'rgba(20,24,34,0.85)'; c2.stroke();
      c2.lineWidth = 8;
      c2.strokeStyle = '#ffe9a3'; c2.stroke();
    };
    if (this._megaIdx > 0) chev(24, -1);
    if (this._megaIdx < this._megaMatriz.length - 1) chev(232, 1);
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }

  /** v3.6.36 · carga ASÍNCRONA de TODOS los PNG del registro (data-URI →
   *  Image). Si alguno llega tarde (p. ej. icono ya construido con el
   *  respaldo), refresca. */
  _megaPngCarga() {
    if (this._megaPngHecho) return;
    this._megaPngHecho = true;
    for (const p of PODERES_PALA) {
      if (!p.png) continue;
      try {
        const im = new Image();
        im.onload = () => { this._megaPngs[p.id] = im; this._megaIconRefresh(); };
        im.onerror = () => { /* sin PNG: respaldo canvas */ };
        im.src = p.png;
      } catch (e) { /* */ }
    }
  }

  /** v3.6.35 · REDIBUJA el icono al cambiar las cargas (×2/×3) o al llegar
   *  el PNG del dueño. Barato: una textura 256px compartida por las dos
   *  monturas; la vieja se dispone (regla Quest: nada queda colgado). */
  _megaIconRefresh() {
    if (!this._megaIcon) { this._megaTex = null; return; }
    try {
      const t = this._megaIconTex();
      if (this._megaTex) this._megaTex.dispose();
      this._megaTex = t;
      for (const sp of this._megaIcon) {
        if (sp) { sp.material.map = t; sp.material.needsUpdate = true; }
      }
    } catch (e) { /* */ }
  }

  _buildMegaIcon() {
    if (this._megaIcon || !this.paddleMounts) return;
    this._megaPngCarga();             // por si el PNG aún no había arrancado
    if (!this._megaTex) this._megaTex = this._megaIconTex();
    const lista = [];
    for (let i = 0; i < 2; i++) {
      const m = this.paddleMounts[i];
      if (!m) { lista.push(null); continue; }
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this._megaTex, transparent: true, opacity: 0.96,
        depthWrite: false }));
      sp.scale.setScalar(MEGA_ICON_S);
      sp.position.set(0, MEGA_ICON_Y, MEGA_ICON_Z);
      sp.renderOrder = 5;
      sp.visible = false;
      sp.userData.ppMegaIcon = true;
      m.add(sp);
      lista.push(sp);
    }
    this._megaIcon = lista;
  }

  _megaIconVis(vis) {
    this._megaIconOn = vis;
    if (!this._megaIcon) {
      if (!vis) return;
      try { this._buildMegaIcon(); } catch (e) { this._megaIcon = null; }
      if (!this._megaIcon) return;
    }
    for (const sp of this._megaIcon) {
      if (sp) sp.visible = vis;
    }
    if (vis) this._megaIconPop = 1;   // el icono ENTRA con un pop
  }

  /** Recogida COMPLETA (regla Quest: nada queda colgado): radio de
   *  siempre, pala a tamaño 1, canto/onda e icono fuera con dispose.
   *  El canto NO dispone geometrías — son las del GLB de la pala. */
  _megaNormReset() {
    DIMS.hitAssistRadius = this._BASE_HIT;
    this._megaT = 0;
    this._megaS = 1;
    this._megaWarn = false;
    this._megaMatriz.length = 0;      // v3.6.36: la matriz se vacía
    this._megaIdx = 0;
    this._megaStick.x = 0; this._megaStick.cd = 0;
    this._megaRallyGrants = 0;
    this._efectoT = 0;                // v3.6.36: el súper efecto duerme
    this._efectoGolpes = 0;
    this._efectoWarn = false;
    this._efectoFxVis(false);
    try {
      if (this.ball && this.ball.ppEfecto) this.ball.ppEfecto = false;
    } catch (e0) { /* */ }
    if (this.controllerPaddles) {
      for (const ps of this.controllerPaddles) {
        if (ps) ps.ppEfectoMul = 1;
      }
    }
    this._megaFxVis(false);
    this._megaIconVis(false);
    this._megaIconOn = false;
    this._megaIconPop = 0;
    if (this.paddleMounts) {
      for (const m of this.paddleMounts) {
        if (m) m.scale.setScalar(1);
      }
    }
    if (this._megaFx) {
      for (const fx of this._megaFx) {
        if (!fx) continue;
        try { if (fx.parent) fx.parent.remove(fx); } catch (e1) { /* */ }
        try {
          const U = fx.userData;
          if (U.rimMats) for (const rm of U.rimMats) rm.dispose();
          if (U.shock) { U.shock.geometry.dispose(); U.shock.material.dispose(); }
        } catch (e2) { /* */ }
      }
      this._megaFx = null;
    }
    this._megaFxOn = false;
    if (this._efectoFx) {
      for (const fx of this._efectoFx) {
        if (!fx) continue;
        try { if (fx.parent) fx.parent.remove(fx); } catch (e1b) { /* */ }
        try {
          const U = fx.userData;
          if (U.rimMats) for (const rm of U.rimMats) rm.dispose();
          if (U.shock) { U.shock.geometry.dispose(); U.shock.material.dispose(); }
        } catch (e2b) { /* */ }
      }
      this._efectoFx = null;
    }
    this._efectoFxOn = false;
    if (this._megaIcon) {
      for (const sp of this._megaIcon) {
        if (!sp) continue;
        try { if (sp.parent) sp.parent.remove(sp); } catch (e3) { /* */ }
        try { sp.material.dispose(); } catch (e4) { /* */ }
      }
      this._megaIcon = null;
    }
    this._megaIconOn = false;
    try {
      if (this._megaTex) { this._megaTex.dispose(); this._megaTex = null; }
    } catch (e5) { /* */ }
  }

  /** v3.6.35 · CORAZÓN de la norma (animate lo llama cada frame). Dos
   *  bloques: CARGA (CADA 11 golpes del rally = +1 carga, tope ×3 — el
   *  rally largo premia con más cargas) y ACTIVA (15 s por carga:
   *  radio ×1,38, pala ×1,30, canto, onda, aviso final). Con «Pala
   *  Mejorada» apagado todo duerme y la pala queda EXACTA como siempre.
   *  Construcción perezosa: sin carga no existe ni una malla. */
  updateMega(dt) {
    if (this.disposed || !this.rules) return;
    const r = this.rules;
    const on = this.megaEnabled() && !this.inHall && !this.calib;
    // CARGA NORMATIVA v3.6.35: cada MEGA_GOLPES golpes del rally actual
    // = +1 carga (11, 22, 33…). Rally nuevo = cuenta nueva; las cargas
    // sin gastar se conservan hasta gastarse con el gatillo libre.
    if (on && r.state === 'rally') {
      const concede = Math.floor((r.rallyHits || 0) / MEGA_GOLPES);
      if (concede > this._megaRallyGrants) {
        this._megaRallyGrants = concede;
        this._megaCharge();
      }
    } else {
      this._megaRallyGrants = 0;        // rally nuevo = cuenta nueva
    }
    // RADIO de detección (física): ×1,38 SOLO mientras ACTIVA
    if (on && this._megaT > 0) {
      this._megaT -= dt;
      DIMS.hitAssistRadius = this._BASE_HIT * 1.38;
      if (this._megaT <= 0) {
        DIMS.hitAssistRadius = this._BASE_HIT;   // fin natural
      } else if (this._megaT < 2 && !this._megaWarn) {
        this._megaWarn = true;   // aviso ÚNICO: el poder se agota
        try { this.audio.playOsc(880, 440, 0.18, 'sine', 0.16, 0); } catch (e) { /* */ }
      }
    } else if (DIMS.hitAssistRadius !== this._BASE_HIT) {
      DIMS.hitAssistRadius = this._BASE_HIT;     // apagado/cero: restaura YA
    }
    // v3.6.36 · SÚPER EFECTO ACTIVO: ventana PROPIA (8 s o 5 golpes con
    // efecto, lo que ocurra antes — reglas del dueño para este poder).
    if (on && this._efectoT > 0) {
      this._efectoT -= dt;
      if (this._efectoT <= 0) {
        this._efectoFin();               // fin natural (tiempo agotado)
      } else if (this._efectoT < 2 && !this._efectoWarn) {
        this._efectoWarn = true;
        try { this.audio.playOsc(760, 380, 0.18, 'sine', 0.14, 0); } catch (e) { /* */ }
      }
    }
    // v3.6.36 · el multiplicador de spin del SÚPER EFECTO viaja EN LA PALA
    // del jugador (lo lee collidePaddleSweep): ×2 al brush GENERADO, con
    // tope de seguridad en c05. Apagado → multiplicador 1 (pala honesta).
    const emul = (on && this._efectoT > 0) ? EFECTO_SPIN_MUL : 1;
    if (this.controllerPaddles) {
      for (const ps of this.controllerPaddles) {
        if (ps) ps.ppEfectoMul = emul;
      }
    }
    // v3.6.36 · CICLO de la matriz con el joystick (⟷, cualquier mando;
    // en escritorio también ←/→ por el listener del constructor)
    if (on) this._megaCiclo(dt);
    // ESCALA visual de la pala (crece rápido, vuelve suave)
    const objS = (on && this._megaT > 0) ? 1.3 : 1.0;
    if (Math.abs(this._megaS - objS) > 0.002) {
      const kk = 1 - Math.exp(-dt * (objS > this._megaS ? 7 : 4));
      this._megaS += (objS - this._megaS) * kk;
      if (Math.abs(this._megaS - objS) <= 0.002) this._megaS = objS;
      const sv = this._megaS > 1.001 ? this._megaS : 1;
      if (this.paddleMounts) {
        for (let i = 0; i < 2; i++) {
          if (this.paddleMounts[i]) this.paddleMounts[i].scale.setScalar(sv);
        }
      }
    }
    // CANTO + ONDA: vivos SOLO mientras dura cada efecto (oro = MEGA,
    // cian = SÚPER EFECTO; pueden convivir, son ortogonales)
    const fxOn = on && this._megaT > 0 && !!this._megaFx;
    if (fxOn !== this._megaFxOn) this._megaFxVis(fxOn);
    const fxOnEf = on && this._efectoT > 0 && !!this._efectoFx;
    if (fxOnEf !== this._efectoFxOn) this._efectoFxVis(fxOnEf);
    for (const par of [[this._megaFx, fxOn, this._megaT],
                       [this._efectoFx, fxOnEf, this._efectoT]]) {
      const lista = par[0];
      if (!par[1] || !lista) continue;
      const tt = performance.now() * 0.001;
      const blink = par[2] < 2
        ? (0.45 + 0.55 * (0.5 + 0.5 * Math.sin(tt * 16))) : 1;
      for (const fx of lista) {
        if (!fx) continue;
        const U = fx.userData;
        if (U.rim && U.rimMats.length) {
          U.rim.visible = true;
          const ro = (0.5 + 0.14 * Math.sin(tt * 5.1)) * blink;
          for (const rm of U.rimMats) rm.opacity = ro;
        }
        if (U.shockT > 0) {
          U.shockT -= dt;
          const ks = 1 - Math.max(0, U.shockT) / 0.55;
          U.shock.visible = U.shockT > 0;
          U.shock.scale.setScalar(0.35 + 5.2 * ks);
          U.shock.material.opacity = 0.85 * (1 - ks);
        } else if (U.shock.visible) {
          U.shock.visible = false;
        }
      }
    }
    // ICONO DE CARGA: el SELECCIONADO de la matriz (SOLO UNO visible en la
    // pala en todo momento), oculto mientras SU efecto está activo
    const icoOn = on && this._megaMatriz.length > 0 && !this._megaSelActiva();
    if (icoOn !== this._megaIconOn) this._megaIconVis(icoOn);
    if (icoOn && this._megaIcon) {
      if (this._megaIconPop > 0) {
        this._megaIconPop = Math.max(0, this._megaIconPop - dt / 0.35);
      }
      const tt = performance.now() * 0.001;
      const pk = 1 - this._megaIconPop;                       // 0 → 1
      const pop = 0.35 + 0.65 * (1 - Math.pow(1 - pk, 3));    // easeOut
      const sc = MEGA_ICON_S * pop * (1 + 0.05 * Math.sin(tt * 3.1));
      const yy = MEGA_ICON_Y + Math.sin(tt * 2.2) * 0.003;
      for (const sp of this._megaIcon) {
        if (!sp) continue;
        sp.scale.setScalar(sc);
        sp.position.y = yy;
      }
    }
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
    // v3.6.31: el haz-puntero de la intro no puede quedar vivo sin intro
    try { if (this.champs && this.champs.introBeamHide) this.champs.introBeamHide(); } catch (eB) { /* */ }
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
    let hp = null;   // v3.6.31: impacto del rayo en la intro (botón o panel)
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
        const hb = this._instrRC.intersectObject(S.btn, false)[0] || null;
        hp = hb || this._instrRC.intersectObject(S.mesh, false)[0] || null;
        hot = !!hb;
        // v3.6.31 · HAZ-PUNTERO (igual que el mapa del camino, v2.98): el
        // rayo de la pala se VE sólo mientras toca la intro — así siempre
        // se sabe a qué se apunta; DORADO sobre el botón JUGAR. Con el
        // menú abierto manda el menú (sin haz; el suyo es otro).
        if (hp && !this.menuOpen && this.champs && this.champs.introBeamShow) {
          try {
            this.champs.introBeamShow(this._instrO, this._instrD,
              Math.max(0.25, this._instrO.distanceTo(hp.point)), hot);
          } catch (eB) { /* nunca tumba el frame */ }
        }
      }
    } catch (e) { /* */ }
    // v3.6.31: sin panel apuntado (o menú abierto) el haz se apaga — no
    // molesta apuntando a otra parte, igual que el mapa.
    if ((!hp || this.menuOpen) && this.champs && this.champs.introBeamHide) {
      try { this.champs.introBeamHide(); } catch (eB2) { /* */ }
    }
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
    //    v3.6.30 · en el HALL la IA duerme (su pala ya está oculta por
    //    _hallHidden): nada de pasear al rival invisible por el museo.
    const aiHit = (!active || this.inHall || this.calib || this.net.online || frozen)
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
    // v3.6.30 · en el HALL no hay saque que preparar: ni la bola en la
    // mano del jugador ni el paseo/saque de la CPU (todo este bloque).
    // La bola quieta, oculta y SIN física — el museo no juega.
    if (active && !frozen && !this.inHall &&
        this.rules.state === 'serve' && !this.calib) {
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
    if (active && !holdLock && !frozen && !this.inHall &&
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

    // 4.9) v3.6.36 · SÚPER EFECTO — golpes CON EFECTO del jugador (máx 5
    //      por ventana): el golpeo del núcleo ya aplicó el brush ×2 y
    //      MARCÓ la bola (ball.ppEfecto); aquí se cuentan los golpes
    //      significativos (|spin| ≥ EFECTO_SPIN_MIN) y el 5.º CIERRA la
    //      ventana (regla del dueño: 8 s o 5 golpes, lo que ocurra antes).
    //      Un golpe sin efecto significativo NO cuenta ni recibe bono.
    if (this._efectoT > 0) {
      for (const e of this.events) {
        if (e.type !== 'paddle' || e.who !== 'player') continue;
        if (this.ball && this.ball.spin &&
            this.ball.spin.length() >= EFECTO_SPIN_MIN) {
          if (--this._efectoGolpes <= 0) { this._efectoFin(); break; }
        }
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
    // v3.6.34 · MEGA PALA NORMATIVA: carga por rally 11+, efecto activo,
    // icono y restauraciones — barato y perezoso (nada vivo si no toca).
    this.updateMega(dt);
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
    // v3.6.27 · HALL OF FAME: las sorpresas del museo respiran SÓLO con la
    // estancia visible (trofeo que rota, haz que respira, anillo que pulsa,
    // bolas doradas en vaivén) — coste cero en la cancha
    if (this.inHall && this.hallGroup) updateHallFx(this.hallGroup, dt, now);

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
      // v3.6.29 · MEJOR DE 3: la serie vive en el marcador
      gamesPlayer: this.rules.gamesPlayer,
      gamesAi: this.rules.gamesAi,
      bestOf: this.rules.bestOf,
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
    this._megaNormReset();   // v3.6.34: el hall es zona neutra — pala como siempre
    this.rig.position.set(0, 0, HALL.cz + 2.3);
    // v3.5.0-ESC1 · HALL SIN ARRASTRES (informe del dueño: «al volver al Hall
    // desde un campeonato puede quedar la pelota sobre la mesa sin aparecer
    // la mesa»): el hall oculta mesa/marcador/IA (v3.6.30: TAMBIÉN la bola, y si se
    // sale de un DUELO en pleno rally el módulo NO re-arranca el partido
    // (solo lo hacía desde 'champtest') → la bola seguía con física real
    // rodando sobre la mesa invisible. RESET DURA: el hall SIEMPRE nace en
    // estado de SAQUE limpio (árbitro a cero, ready para la cancha), bola en
    // escala/color/base por defecto y sin
    // estela. Los módulos ya restauran lo suyo en leave(); esto es la red de
    // seguridad del NÚCLEO, sirve igual al arrancar sesión.
    this.rules.startMatch(this.mode === 'survival' ? 'survival' : 'match');
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    // v3.6.30 · HALL SIN PALA NI BOLA (informe del dueño: «en el hall no
    // tiene sentido que tengamos la pala y la pelota, ahí nunca se va a
    // jugar»): la estancia es un museo, no una cancha. La bola nace OCULTA
    // (mesh + estela + sombra — _hallResetBall es el ÚNICO sitio que toca
    // ballMesh.visible, así que no hay repintado que la resucite) y la pala
    // de AMBOS mandos se apaga (exitHall la reenciende según paddleHand).
    // El gesto de saque sigue intacto al volver a la cancha.
    this._hallResetBall(true);
    for (const m of this.paddleMounts || []) if (m) m.visible = false;
    // v3.0.9-HALL1 · EL MUNDO VIVE DENTRO DEL RIG (mesa, IA y marcador son
    // hijos del rig — así funciona el recentrado de sala completa): al
    // viajar al hall se GUARDAN para que la estancia sea el único decorado
    // activo. v3.6.30: la bola YA NO se queda — oculta arriba con el resto.
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
    // v3.6.30 · la pala vuelve a la mano que le toca (el hall la apagó entera;
    // misma regla de visibilidad que setPaddleHand — UNA pala, la activa)
    for (let k = 0; k < 2; k++) {
      if (this.paddleMounts[k]) this.paddleMounts[k].visible = k === this.paddleHand;
    }
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

  /* REDIBUJA lo VIVO del HALL (v3.6.28): desde FASE 30 las seis caras
   * visten el ARTE DEL ARTISTA (assets/hall/, mapeadas cara a cara en
   * createHall con el patrón de las salas de campeonato) y drawHall ya
   * no repinta paredes — sólo mantiene el TROFEO al día: plateado
   * esperando al primer campeón → dorado (SALÓN DE CAMPEONES) cuando
   * existe algún campeonato coronado. Se llama en enterHall. */
  drawHall() {
    const ud = this.hallGroup && this.hallGroup.userData.hall;
    if (!ud) return;
    const entries = (this.champs && this.champs.entries) || [];
    let anyWon = false;
    try { anyWon = entries.some((e2) => this.champs.championFlag(e2.id)); } catch (e) { anyWon = false; }
    const mat = anyWon ? ud.trophyGold : ud.trophySilver;
    if (ud.trophyCup) ud.trophyCup.material = mat;
    if (ud.trophyHandles) for (const h2 of ud.trophyHandles) h2.material = mat;
    drawHallTrophyPlaque(ud.trophyCv, T(anyWon ? 'hall_trophy_won' : 'hall_trophy_wait'), anyWon);
    ud.trophyTex.needsUpdate = true;
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
            if (it.gameEnd) {
              // v3.6.29 · MEJOR DE 3: juego ganado SIN fin del enfrentamiento
              const ge = it.gameEnd;
              this.audio.announce(ge.winner === 'player'
                ? T('ann_game_you', { p: ge.p, q: ge.q, a: ge.gp, b: ge.ga })
                : T('ann_game_opp', { opp: s.opp(), p: ge.p, q: ge.q, a: ge.gp, b: ge.ga }), true);
              // v3.6.29: el resultado del juego viaja al invitado (como pt/rt)
              if (this.net.online && this.net.role === 'host') {
                this.net.lastGame = { w: ge.winner, p: ge.p, q: ge.q };
              }
            } else {
              this.audio.announce(T('ann_score', {
                p: s.scorePlayer, q: s.scoreAi,
                who: it.server === 'player' ? T('who_you') : T(this.net.online ? 'opp_rival' : 'opp_machine'),
              }));
            }
          }
          break;
        case 'game-over':
          this.startFanfare(it.winner === 'player');
          this.audio.applause(it.winner === 'player');
          // v2.34/2.69: cierre del campeonato ACTIVO (ranking + camino +
          // estado final del rival). Con guard: ningún hook del campeonato
          // puede tumbar el bucle (lección del ReferenceError de v2.39).
          if (this.champs) this.champs.onMatchOver(it.winner);
          // v3.6.29 · MEJOR DE 3: el cierre anuncia el ENFRENTAMIENTO (juegos)
          this.audio.announce(
            it.winner === 'player'
              ? (this.rules.bestOf > 1 && this.rules.mode === 'match'
                ? T('ann_victory_bo', { a: this.rules.gamesPlayer, b: this.rules.gamesAi })
                : T('ann_victory', { p: this.rules.scorePlayer, q: this.rules.scoreAi }))
              : (this.rules.bestOf > 1 && this.rules.mode === 'match'
                ? T('ann_match_end_bo', { opp: this.rules.opp(), a: this.rules.gamesPlayer, b: this.rules.gamesAi })
                : T('ann_match_end', { opp: this.rules.opp(), p: this.rules.scoreAi, q: this.rules.scorePlayer })),
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
import { HALL, HALL_SKIN_COLS, HALL_SKIN_IDS, HALL_SKIN_NAMES, createBounceMarkers, createCalibPanel, createChampRoom, createConfetti, createFanfareBanner, createHall, createScoreboard, drawHallDoor, drawHallHeader, drawHallMedal, drawHallNameplate, drawHallNeon, drawHallQuote, drawHallRanking, drawHallSign, drawHallTrophyPlaque, hallCanvas, updateHallFx } from './c08_hall_hud.js';
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

/* =====================================================================
 *  v3.6.36 · SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO (diseño del
 *  dueño) — REGISTRO EXTENSIBLE: añadir un poder nuevo = una entrada en
 *  PODERES_PALA (id + nombre + voz ES/EN + icono). Un poder distinto NO
 *  sustituye: ENTRA en la matriz (orden de llegada); el joystick ⟷ cicla
 *  el seleccionado (flechas ‹ › en el icono, sin envolver); el gatillo
 *  gasta el SELECCIONADO. Mismo poder → acumula ×2/×3 (tope 3). SOLO EN
 *  CAMPEONATOS. Los assets van EMBEBIDOS como data-URI (cero red,
 *  offline en el Quest):
 *    · PNG_PODER_MEGA — icono del dueño (SuperPala_Crece.png).
 *    · PNG_PODER_EFECTO — icono del poder de giro (el dueño lo traerá;
 *      provisional de la casa hasta entonces).
 *    · VOZ_PODER_* — voces NATIVAS: es_ES-davefx (Piper, la misma de la
 *      megafonía del juego) y en_US-lessac para el inglés.
 *  (Los literales base64 los inserta scripts/_poder36_insertar_assets.py.)
 * ===================================================================== */
const PNG_PODER_EFECTO = 'data:image/png;base64,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';
const VOZ_PODER_MEGA_EN = 'data:audio/mpeg;base64,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';
const VOZ_PODER_EFECTO = 'data:audio/mpeg;base64,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';
const VOZ_PODER_EFECTO_EN = 'data:audio/mpeg;base64,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';
const PNG_PODER_MEGA = 'data:image/png;base64,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';
const VOZ_PODER_MEGA = 'data:audio/mpeg;base64,SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAzAAAAAAAAAAAAAAD/+1TAAAAAAAAAAAAAAAAAAAAAAABJbmZvAAAADwAAAD0AAC6AAAgMDBAUFBgYHCEhJSUpLS0xMTU5OT1CQkZGSk5OUlJWWlpeXmNnZ2tvb3Nzd3t7gICEiIiMjJCUlJiYnKGhpampra2xtbW5ub3CwsbGys7O0tbW2tre4+Pn5+vv7/Pz9/v7/wAAAABMYXZjNjEuMTkAAAAAAAAAAAAAAAAkA9kAAAAAAAAugNrid4QAAAAAAAAAAAAAAAAAAAD/+1TEAAAJfCc6VGEACU0OaIM28AAABoAAAABBDHPJgAAECCERECw8PDw8A/4Cv/8cAAAAAAw8PDx4AAAAAr//7v////nAAAAAN9D/HgAAAACMPD2x4AAAAAjDw8/2AD/2gDdkqHZrJaY0RGUXbQX/lYkhmFBIEBJ607zaFwnYiajqct1qtb6EohiMZOx690VlWdSNowA8NETFLnB/ecUH1WSO2BcgbAiMsG855qlSsaKu/8oqwAJgiS7cCGIsl3f/+1TEBYAKlKthXYWACVYUrCWGDblBgihU8lfbdN/JhiEmt4ZYTK7GQ35caVw+U4pxiMh7SOrE83t5uforN68kHJ373MWuYYc3U6M/CD3HGR1i9b3xzP/xvwBb/LT+vIABAG/hBzYWIVhHIN3eUUrMJVbNAkLpxd98+vitsFQjY6h0eHSR2jE0cfaWgqDJyKWXuW2YvzB6+xYhwNZ6zMohQsGbdBjsIIIUzvqlPsjOiV6//3nVYwCQAjEACXJwJ93/+1TEBYAKYPNr7BhPQV+fLOmGDarWvyaAih3G5ylhry4KowFt3KSDRlhA9gp2yHwWg+dr0YEIEri0W06CFWZ2Zld36jlIXkO4uCnU70VCSMTX+2+X6BDnGQw2OSmiUBACCU6Gu4lqZSz8m8utAA5807MabCljAod3WstnMBycw+5Zi1T6ia6ZVgl6VANWbaMAglrC4RN0sqa9U9jhyqUM5GpRj15D21zv3N0M6t7DxVCje78igARAAADjUwEgr5D/+1TEBYAKxG9fp7EoiVMe7CmDDer0LC4G9CG8eRMB2OzcEi+Hg5iCPSGH01qrFWCoOnT5DNvVR0EQqFARRJNsqocjGEVgw7wqLL/SQ0KCn/p0VE/yfP3FdxNx4K1Evk3tcNIDckoEaEQwhkbanHWiOO7TPmTuNDq9XVpIdlocAijirPjYdMkYl8qaZwU46kSM5RZj8Pr//0wTIvGSBKFd1VWVUbbyadvFKSLaKO2T3LM8YiPRAA4AAAAblwGY4An/+1TEBYAK1NtPrDxLgVidaqmEoTLyupgBQeYQBIRJ7s1fFSgTxgIImqXw/zLNiXUOduqQUG0SqO5OK5gvbyTOeTG9LQINX6dCmR3kMVgyMeUzSLdLZrsafNEyy4nizk9YhIUAJqOgbVSBz2TMqSukDht62ATEQjCAEkxblmGUQmpB+lA4LvPJeIiIFgqQWTnql91DFi4reu01be9fw9RFwpTmw5rUJVlbpn/+I/2+/8ZQAIC6dKWF5KAG3JQKBLj/+1TEBIAKZPtVR5kNEVufKqiUDxklUINQbh5Is5zjOk/FITdAAANgF0NQIW33VAycb7hTVrVA2TzPv8N98RNW6U9xTTkdjhNPJ9x3FRSQkXtbFosr1UxxyXOVubkD9MAoAAJOygSFSMZLCEPBo+jbOCpMmBHcFZGGydRjPN2wXLIPYnLX25oFHCm729onyLvG7lg0AIDQyqvLFEmJthKz9DILiXROvJMkJ3IEghJ4HoUYiigbCLbLHbGS7I2BZhH/+1TEBQAKcPF/p4jRMVEeLjD0jiaOXglxOVs6zX08g7nqzqNHK6VyAp0RmoQRveSc8gAi6bmLRDNuUPtM0i4cwiaFhIGwppvazHTuMPTjPX/jYy7iM77f/3X7umBJjIKIkpAojigNwsLjKM6MQRHBsLN4N5Vcpy3o4/D6WIKgjvDagLwQP1eFZ86DjhpiF+s5xEhJZCKNKtYgkLRS6RQgxA4annl7l/Str8yiYigBs2j/ocinWSyQUUTA4ptH3eL/+1TEBoAJXKN5p7Bn8SoMLzT1oY5bJTsEI9Iw/WJsp3XwP8mi1VlOmz4jVo9e84Kcwo7f92KcPn0jsFbTsP2gYKAoLC8XcJkQdCpwAnVbSP/O19lORFIhspKB0BVLA3FR4aC2vxYibqjsfUBeP2FVrGXcqEpsXjfrbG4LUk1zmNBIVFRz59IyNU0hKFHuSGonBdQXAg4DOGuPEEf96owEuAwBEW8Bz0O16GrZSVmvpqhry4Qh7h3BElepghQBsyv/+1TEEQAJOPVlp6RRASwL7GmHmKp5y0lZIM6KmcVtMTafBjHf+/kzXptaWpSLXZzKk1K/0lslr6fWdoOiQ2BACik8MF5kz6ZCiNF1GseA6aruIrykY1HcnXbkwlKZxTGJICVVvf12tlkVr54saHE3HwpDMqEjZV54+GirEE9oT2kcKT31Bo82MAGVIRAAHZLwHwbISCIC/cj8GsXgb58mVDQ1liqN6FGI7VFW5NrIg1fcx2a7rHDP9ZjGzJopZuf/+1TEHAAJWK1h55hPCS0V7HGHjTZnd39ceYUtPQH517y///lJOXPEgmpEAJTEGahg0myj5jL2ppV1F2jcI6WBOx3gT21rfrvdnMkqt1BsSjIcBmin+XOEfS0svlkyYeHkh2pHFqCCYFVAQNXW5okeWcZpAdkQGNJwCqVTFr4IWFtqUrieGvSzDuO07sBQ3TJoJmIeu2pFCQhLv323ekYLW+Gx8KvuyoqJ9lpS7OdstN2W2tYpBakzcJZ1oxgZACD/+1TEJoEJYM9bTBhPUR0S6r2UjRiBC0jnAsjIhHkypdkjirnvwv0qaIgfgPISQiiwrgN4cQBBFfMIwQWy6O9lp3+5XsvXROISDAq+wPy6cu9h47YRh9JlQIJqYTziaS8gg1FjHlUx4BZG2gV6HmOrG+G8fvHtb0uEamGM+exf61zceZd6ZSkcy9CjCrmanfVT/931bZGQlXIlEEGSIBAixc/SjZ/rY04yioME9HoUF0GyN81MT6V5DWQHMLhwxTf/+1TEMoAI/Ptlh4yxsR0fbjTAilbUsx3ogNlyIUGgxKN9DS7V7EJqIcko5nq9/Iq01nnkfnnmBHczBxVKegpVCUuzQFYAhYbIrmmPLHhbgs7ipGSOmKgE1rY3n61uGCgi008qb3JRjXrZyfS9OCaWIIHA4pz4JkjzUtp7+7WtvodF78XnK5yB4mJVAIxkFUCx2lpglTioUkgXTivHPBSgUwCMFYKJNTpRWMQRjmIQdQwsWcqCSsa/bednU5Ku1Oj/+1TEQAAI2J9Vh5htCTGd63zxibDqsy06dvTu1yOamJBCVBkqbMW0Kopv/bE9CIPhHDJV5vCkDDQ96aSHIaaLKjk1S0wqTEDApJBUE7YGMgVh1fZoOFM+bQyO9zoXX152WH+ywUbQCGxl5HrGyx54NDSoLGjzLu7K0liaYHxxarRjgeDhBTom3+DnJw9dsK21qOOo9H41rhNHYCoJ+j0Leo8ECEPMLZEn1d4nFARHGi3fvNNeraEWIQtfn/2VDAD/+1TES4AJXKdph6RssSyKcD2npPZHpFMRAJNOcDj1OPTGrsuuZAswxWB6WTMrluBFAoqfeXnBMKHInOOyVqPrUTxt/eDX0e03dzpNYsK6FCThfe3/6ffuZ5m/dCmxm5oX/mjocF5bw4A1cIALSkoBqmsWqTD6U5T5L8wSLpUdM0JbjaJWeqxtQ95NJBQCdJm1RN00WCWVjkyzwmYWKBBp9InHvIHHNWkmEgmqQi19KtdTlWia2gAAUm4BQe4vjPL/+1TEVgAKePVn7TBpySyMrXT2GZgaVJJGsg51Iwvj9Zjv2Rkqh7iJAKD+six1rTzwygxKRPr/8NR7sgIn6ZHLe01O14Nr78/fh73dYlGvmCd4cbIjaBATcbrF31pWxvZMlY19uGSQ6WQwDWJ8VEVD6RB8fp9e6+a5Ui26THnT/NODQa8TIrTXvVUvLL89KeU/jff0pwFuZXCXIAQCiOc9VsMxzGSbJyGMmkC4xzdYFiFyGlVSV4lTgMHPRq2rhzb/+1TEXABJWH9zp5hwmRQervGGDRuHNNbNfRPfObLoWatZnaQaIXliWK2khUrlUFiSwjZ95eEBNgAAJJuAK8V3BgKIOAWpycBJBCYtig8E554lovqJrFhUgvBHqGlXiynNHQTV42iSZkOLNiFPmkv2m5uTS1b3Iudd9HvcwFPrJFGIKRpokOJpgWPShZUS4/YbcTlyVNKH0VrpxTmHUHedna4G6E/f6xsoFbrF0FGCOwjz82NOBl1vEUQWu6z7Nvz/+1TEaYAJCHl1h5kM8S4NbXT2IOPcbN5p0otf8Xf/6QaAQBNNwD2xTqp2WizWWyx2XHTdctiuAQTkxacTOUpebSRiqkibvuc81FD6MFMr1zWRVREqr2Ycrm0ikQ4sJKIUVtcibRGEmr/aV72Vf/8VgBaCBACSbgFxjPRXZBEiSIQbiXGgWJfEQlASNkH4q633Ux+6MYof01zfghWm6MFEGeum+v77XbeV7VE7M7qW716N2Y1kHvsccB4y7SwTmm7/+1TEdQAJOJN1p5hwuT8T6+mGFTsQZE04OYfXoAtqjXxAhpYUqQgmUT0j3BTaerlipiZbOSDF9+vKJ+yWgwLKsJlKIUwQoIyeAzLPRCrAjNBDjoIcAEbmgg86cidMsISFS4kKKQCYFOHj7fqVTMA2UnhyDcmvvwSmXQuZ7HAkzk0bwvSH7qEyVkBird7dH5ILyy21agP2SOKUZN9DP7ltDTHZYOkrMHr+VuvQ0ZCz6nK8iCLCYDI51OyUoWg2/O//+1TEfYAJjN9hp7Cp0WuZrnT1jl4UUxFWbZWFDB+xu/gmEQfC5IBgAQATKcA0fJ5sJWBRC9gm0pmNRvmIFDlAYPOdRv7ae4vjsnfhWWhgdgE8uDWm1/rVf+vxGBEw53mIdPaayMZ0S5EYEyV/S9ISveV/7Mn0VIsIbQBTlwGj5LEVCTPQH+7YUwf0JcvlUWDF0ArRPy2ZTbQCgnvM9Ws8YWWl2jWGJKrTBQu94O7ZbG8nbVyqn555F+UyKqQQCKv/+1TEfwAMbPVk7DCt0UIabPT2CXm1aZruRIIAAJPAYKE4JAL1xDTHO1UPkLaH0tlVScuOtXpNdExpcZrmKT26c5C5bZgSB6jTtJP6cktWGJInifc3888ted/Phnmpeh/yqYcoPbzd4JBwgpJTjI5AWq8dsYKZyKBFMQMCqwXZtuyqNGkK2RgOMO1SEnWKhWR19pi3V2cjoyqWy4YxgxnaxUdpaPub20tQyPS7e7xLhhd5Ss6s8qcSKZjA6GiogUT/+1TEeoAJtNVtp6RvCTge7Sj2DXAQ2kVBkaRe34/pAhrIh7e8UHUsRSv56Tux2NYYkRDU6JZUkX8+2qAqvUO/6xrY5PxmHWVJ5a/VNvktuVSmq9ta5sM8t+IkiJWEmkFEJ7MEYesWrhMK4eVh0CZc6+AigKEi5pcVMr8o0RmMaZabw40gkU5fY7Mu1kp/1yIv+IRp8pE+noT2f//waaB2LShy6WE+cPGjTrZaKNjaYEYwSEaFiQAhERRm/IoHyPX/+1TEggAKoSNvR6RH0S0ernTxij6AYBYSgCyGK2T14al3aamt+x6HulZeIJIK+K0PCXro4e0Sjca2QmLL/9n1uPkzxHuhIoBltIIAQgAQABNJ0Ba7MlMZUZEvYJ0VvRzmqlUBsL0njpwKciyeAVyOJ4UlW1sHokjrwZtApfssIlO4lzluNPo/W//3azxcvrB+uq/6XfUQrAYiBGUCBkmYe1cXLZGyOJVMZDxCC7InRlmkRjI9XMqFz2pbKdesbyz/+1TEhwAJaPlrh6RrcTKSrvTzDbc24yhRtFGsEna8QvpeV4ZKUmLnAZYNQKBx29540xlZepiaSLrQKCEjjuFhoicFSEtOM/UJfoeuiazsUVrNN2dbcoKz5Z+FcXAYCxWMG1u9L9iiag2BEHw6DwP4piBe1mqfmZjIMp6qEyHpEezFFFaJ9rKd56U8ouUBAgCrB1v3koAIEAAAEAHxCG0Hu+YnBxo+nw+C1piB51+qWVusrYYMNkyhF6K0MYnpmnb/+1TEkIAJeFFd7DzFCS8U7PT0jX5in1KYzK4zT1oEhmDKkujE614bPWKDBZSwAhKBC2KnlH7t+BreiqXp1+yFLqp0hN+XmdbeK/io4qgfJtUc+6jwCTgFghKPAHCGMEjSAj2GsiIx4tR0uS2c+nTkK8mpGVoTNWTo8DjmHXsNudqRgKv02GlGF2pZC19FQlRwfohHRuY7F3/eyPJesiTOAmexHOoJEpFFQJQc4NJRjJYSfrKZLPaiYiwJ9iCwW8r/+1TEmgALwO9rp6Czkagea3WDIxCMkuBRnBWKh+Gku2iruka0tLKPu45Uarnom1S0eWpgpkLKeq+/85TXvuz34VwzmaN+mqqIixgEgpOSgMwYo6CrHqVhYYp2GUcqcXjqVUsMIA1F82DEs9CVh/q6S+220Y6tLPh/tLSWkGLcpR4BM8n67mHZeueVNkmwohfr+QAxIAAC53cCMCgiJMRaT2R5eQ5euZ6aA3IR0DQCYgnj0Fq62q0xHWOlWyiuxW7/+1TEi4AJwPVrp6SwyUEer3T0CbaSipxRxwxffyQXELas4Fy13+70401sXd5K+c3//7pFCJEEA2SygZIEYsIhjwzXRel/p1WwVTKwQoJWaa1rPh2dtrbLKzKd6gEQgJEde62fOVnMxos5CCCnZyNZrV5n0qXzG2VVCho70IkVslAFxy0CpGn6HDhYBhs6CQjkqTqfaoSdhrSHO82q8xGUGTczSWWoo3Tq+hDUVfZDdWYvM8szojWx1aeEfw9MkVv/+1TEkYAJPJVzp5hs2S6H7HTHsBHUK8JtRensUGmsKkiF82g/i8BGUGUkVfU4dC1YpWrHB9fClVnRSow5tQcCAVmSS/SJOH+XfuV7cl7VjSrInf/8vyKThii8RFqgBrBiYMwytISIBAaFg09YuKIiVXYYFJ3VcxfMmbJxUcCw0bC3NsvSvxS1kmn9lajqjOdjHpPMT1pW23S01JCK0iPr+5XO2V2aZH2MwssyhTTCVQGVAAaTcAwZ481UTw5DfL7/+1TEnAAJPPNnp5hMkR8dbDTyjnIpBFDEVZgGQnQGFFgIDDT2x5ukRw6M++cdNpsTGxjsWt2I23VL5z/CM5lIOusrv3b0arnq6aUMINcAVnlaBiKKA98ViSALkBoERMcFFoQHMBFSzZDh+G9SM6Ztr1TZm6JF2z+lPnfQ2ioeFgP2To9EQwiSmAkE0lhcZlp62PEQhpevrpntThCrwxC9e6QvYQMjHuI7vbu3397vYtOApm8QhAgAAACil4EZZIj/+1TEqIAJRP1fJ7BqsSyfazGEiXY7BfR6l1DA0B5CRyrG6jWo0vRphxKAyKIMbziywCxyBAfEz8ieuo5ZfZWeFXH4eXF8nr9qYGC9CdWmEBPO3K2efMftiobGNC5QYsLukDELAs+GGquSGSezv7eJjCjxx2gRoWPhBtT7loQAQAilKGLsyaNLYAYpSIbtBpJiUMq1dIEPJS1aBB9ccE5CIzY0n0GdtVCbuHlf3PJBFsJCocKqExdo4TrYQinmoKj/+1TEswAJSO1VR5hNkZad7GmWGbd2rUDC6KRZlFtvvxWb23t4L1mdeP23TMUF2JHQ/kz3rJuc9K6UIDNAAQACcvAOIzjPZUkzuQioj0D8swmL4/M8O7648tejU6tThh43wkAzZP/69yCzJSynfpal/bdak/n/X2M+9lhmdJinO+HQPfTrQoJAkIgjBeGdCbKcPdyWLd1DMuUhdfmoaiq1PF/0vMeQFGeY2PBvD0ZSVCQrVp22cyormZCSsoVzJdj/+1TEsIEOYQNbrLDPiZshbPWEmfLI6uvum1WZ7D2WbVziJEQ209HwkNlALStimBnDCgJE3NHc75/VP091ebLLVPQpRXaT1wggOKY/kc4hmJpdASmpbOVbmNMZ2+lzL7239nkdDqqLVq6zFgxrsgrb6PAXWUgCmUVAwjXGXl4NWYuxClAplpiEAnDv3KB1eyoxuvUVDRp+rGFJKjddyzMJu9BB2rpzT5tj9t1W771TsiZD3bkeo6NdC9HSpAAQAAD/+1TEmQAJePFv57BniTSebnD0ihYAVrAmOootx3RBgKFLkk0CwOcBcEemxMBxGaUSpRapmr6Vuc5wCxQmjHbZUN9tseJCgbSFVKdPJOkT0Ve099Gdedv4euMywoiEJmSUjjYAEIeoH22HcnB1E0PphX4UTa7nXdyQLdIYvtRcAvvtlmGQb3cKSrXf69rbddiqyroiVdp23czWY96b51VRiw49lXFqO9C1kEwFM2OA5BcE+WRKSeGQbVCvUmnSlVn/+1TEogAJQPt1h4xRMSee7jT2Fc4qJVahMkkALPns/OQPhinh0Qd452u8yZks3uisxpdr7oU9yLRUfv1o0kzzvfIYSUAICZF9HR0E0QCAFFHMIbhDO8pI0KcUzJqP43lDH7txsxAuHxyM3jDNmfonEO85tuv05b6SsrfKMd4kGI/rSoTDVqFk00npSGX73Y11nDFJF7RtA5TFRj+9/953d46fbfuQrQeiBb+hK4QEAAAAAAVA/PgcFFMY8yVEqlr/+1TErYAJTFdbzD0lwTIbb3zzCe/Qio5FyOPnXERUdEEKhVM/+qtnVLUW2Bo+qems9iKQs4+oqhThvamremUJau7qV4hBLTw+bKpftJ8mQq2wG3WZ91lHC1XZO/fmY3/ubbSIIFRHA6MQjkvDsuAQWwXG1D/GI4TqodxyinfPBiA5naoqquqBWg9OO14SQenvqW4drOPLNFHBY+iMReY2CoiIlnniUbdo4SCQAAACagCCHAeaIyUJxLjGk5Jh3ED/+1TEt4AJzPdvh5hQsYqebbWGGbrbzk8MxwCpV1sY2SFQWD5JJ9Xi0zImkY9Yxr64ZsfilfFVcpoCegpLX3i/9v/vH27p5QWVAAESU8NnoJq3lLOPcKQm5jM6EK10ZMRFm42EQfcE1uomkmTDRK9jJukIuYdoPgY52qFlABQu5RqU/aufDZYaDSA6XcKEv6B5URpSOWEpEppFQc9gLawShVG6wISSk6V8lEgmjApqqappqtrNWeLVmYyYxk2R3J7/+1TEtIAL1H9jp+El2SGULzDBil6SKehiHOOYIdiOUr0e2Ql6P7/e2xb2pZjOYyAjBL+Uk2ioAAM9hg3glTUeyeNFNJB9pVcTBudlrBALtsp1+hrUY5Bj4HY6cfGy66Hx4QMOKXQOQ8xFPONyMFwhzGFuDx1aS4hiXpH3jwlVlwrq9lEAAAgGAOQtzTITo6TxVRkkskP0yG1hyrIRKDclMHC1XGXA5saRLNsBo4sq2uax67iFEW8D32yMr4jWgf7/+1TEtoAJKHlppiRwiS2LbGj0ido5Z3+7h7DDdffuqyEqaRyNkAlEpTBLHkazxXogxyoV6NTx6rypYnsieARnE+4hmUYcZSaKxf9jWQKjn2daqky7L+qUR6u5pNu/vfVdPuzHco4ljH5dIeqxlNkgAEAFQEoXgkVRLHdwWovNyuOZpRY3dYsfeoyS1mEg9G2QiGSue68iIczVnFm7qe28ikuz7LZ7E/31RprutluQEtYRDX+tV07PrKQAXCEYBQH/+1TEwYAJgPNzp6RLcTQWbLD0jTWwMA+uMfEA6BpgNKnBppY/JUmlfQrHVT5KTOAqKzYjITh0gajmmkKxYOuJFicMPLFmqVFRrHG2N+hYa3Fhig6GqpFLbIQCgOSncAJBMD8Ri+TgWJ0w6PFgqJkUDqkl91GKUvOndK9mpSpMrBlZn3W7B36SXRVZldnO+yaI397IW8zGrt4MqESLGX/qkQV0MxAAAAC+EcdgJpZbEi8J4pVK7i6V8Z5vca7hPLH/+1TEyoAJhHdhp7BHySWfLbTxieojosfA9SHGQhAMdD2ZjZ1zHcnu40R4MXOjZ19DhoG9nhGd4nd4l5wnMitnFP/+f5MfCwS/+irof3ZgAIlOgR0WbrrJXJYqH7A0VhoPamkgXvA37R1wUqCY1wxE0a3j7hrevSGwVjZqFIT3Uvtm4R7t4VO/7Owt04Aa5f367hIQuk1wJZGAAAAC8IZUnxQPsuT8l7YfyPZlIqmpDYjV6vr1ZGEUQtOTaQ0FeXn/+1TE1QAJLPVlphhSUSuMLTzEpOBDimdn+hLkWiMdsLiQ7RcESgiIc6GZSHzGViy4OVgTK3NCMEe8nqtUvKNVSXvh4NA0xP/RpE0kRACSSfDQMM96mfdlHg9EgQVy5R1xHgo/t+vWAyveZLpfCS0j4o+czHZwE84l3Ndc0qHl0cFDA1YwoZUbbrHOanPdspr8fql+v3B41H+UNiiEQooiAACCVRUqxIJxXS1Rqy6IM+gvDka37x/FfRoMFiXl2dT/+1TE4AAJQPlvh7BH8VUerHzwjwh4UOZUq5R6gvlokmiuDAxTy8e9Bk0rslMKLaCNF/pQK5r3vTp/RLz0azd2eFT4X/xyVoTLa0QC0W5wjhYDUihDnwr6EIdMcmkuSNEPbOo7+Y0/OMDJ0iosLD0abbbkYp4Q0dCqczUvs9WVYzZ8L/s1FJe5H/Y30yy5w6V6RAWVmJQrvyAeJJJBjaIAKSbdHVZENWeBjYq2+Lz6DbQjExNyM5F405aBMSBU6cP/+1TE5YAJZGttp7zHyXce7DT0jsDhYSfOvnMiMZpM3dzMy//WT90uiFIa7t4Zozw7oy83Jwxp9/4/p923TxB6t/nFuTCDLNXcugBlAARCT42h2YOocc4rGgEBWI26EacLpnT1fIIlyiRJqntjotHAipSEd0j7tiR1QnT8MKe7n+6HSUcBSgSCQnUdkg8Ew69yTBWGmgQogVLi0CFi5b/2wFyAA67OBs7jGRYaTUQ9UmPux0K6aivyry9FgiIEp6z/+1TE5oAKcOttp5h0kVWdLDTxluKnQYAVDSmyETVrlA4f2qUEMm8x6oiVk6qvPpVVR99utao7IdrzBKDOFUnAiAAASiqHsEIaB8Bl0WpkF6AQv62Kkg6AniXQ+i70310pDMxanA1WdupeMB9BNkuHDKo0Ruxn8Cr3b2YrvzT1mto5cnfZDkgXHScQDMxlDggbmhO/TYafpzc/7lvOubjoEgqj9ZIdY3M2GkW21AONhWAtN2o3hRZsKUkx1gg22Af/+1TE54AKkPVrp6BxEWQdbDWEmSp4gtZvoE1WvHESCg3WUoiC3Qqgyi4tSMMOHdHhaai8OyO8IPJS25unJT7wsv/TP/I4hFgxwwHBAjaJ6MmkkAQASUVABwGo8+0DeMd4A6H6IyERAskVJ3vY+fmd/kmU3L86dwe12BAQycSIgAdljIxR4KAboAWWQxmOyZOhmRujmhlEhhlnQDQ8EEX3bxumIogAAAAUm4ACoJlMI0ICxbFofrx4F0iWsMgTGtP/+1TE5gAKxGlXTL2FQSeerCjzChgRL2bKPJHmpiD2yAUmgiHyqdCsO2LhHgNZ4QJDQGgUgpEpxcq2tFgoNcxiBcLVxDRIBABJTdBlDaRJrZPQloh4jA810aa5LgckNQl1iJ7tLXI4Wt7sdm9/PGgOVnTI+9MbO59WS1A1P4pZVzz+r0h2MKrwmc/f80o+svHlcG19hTJ1N24QEz1/7ivKaRIIASTcwHyRhrNfZMBJyfMA18r6s0pk2zqE6bQlVj7/+1TE64AM3PVbTLBzEVSfb/WEjW4vrQQlRAtqLcTzyWbLiYCGMqVziH1LKoq5Ntq1ImYdGB/9buUR2PZSy85r0cN+KYoe9SYmqYSQBIKSbvCLOwzyFIgSJRdkIxKpT9QhF4UVyRLf1VNTxYhqIjrKSIElIszPs56rcupeaU0pUNlT0y9U6rWjuXS+8tNDRIUwI4DDJjYqtv80o8VgwCAAAp7ChTKbMGoNYZkhxljKn9cSGn8dmDGkpIixgxUy9Qn/+1TE4wAKPPV5pgS5MS4OrbzDDhh/qPddUTqTbSchGCkIUkBwsL5ukfuoogShJ/GjH5fg9p2XBD2leF0vu52Ww/xzYZZ5eqRoUpAgBAAAABtSYBCUtpO4VKo8zNR6R7PVwLirNLqEQ9sSR2Uco+6YeZXTgtFuHIqnJxKoUE3GmYCsda6PyzMqidt0Qw9hpmy6yvcpBHuZ7C0GnFeAhpaEvdggsgUAm3bgHebMxMr9d+HFVYWlDFBIJOuOVRPEkSj/+1TE6YALfPNtp4zY0VSfbnTxmnqG4scR5b2To5TFwSYuhCGMZhixYAn/pYlgZS1ZpRLOdorZUKrFKyzGZHhpYkbVPTCtRI1gICkgAAAtcvAdNgAj+CxNPXgs6elLfN2XBCNOt2ysktQ582urWQ5kuqICESEmy3ZVdZFcRtPn/dSEuzEUp9z8YaobsU55H93lQs6ETPMzKrfOZgoM0wRNunGPepNF6yOAPz8Hu6EwlAxVkwBBJTOMi3POj9b4iHb/+1TE5oAKZPVvp5hRGWIaKrGXjeBI1UYHDx9T82DQDBlTtjTh6rMztnmrY4Rc5/T/HeXLPokzKo4WoES1FG9CCAYkOp5GMcZhgWqFHMHH6ZztSVOJcrOXii75MAL/n4KCJa8FM6iUWaAu58HLlLVHIITj1XhcSnpI/Tco/fUGLUJCgmx17gs/n0/GDQic8rlznBYWZqSdHwpceqY77VqqTBgIAA43MBxDmdzC832ZEnJAL2wPbfqs/cdnpVFFYpr/+1TE5gAK7MlZ7DynwUUdKvWWCPi30dIIoz8zNziMVy95ApxJzXcQdUN52r1Vma7rYLelkf6IY321HmdHb9e1wRnTVQCQAACScAnhElAfwO/JkrDMvUqcJ5HRazDMUdJ/niVMhTDt1/ozEpq28bxu2hnXnXxc6TVlB4HwjNjXP/6fr/kk35YUyfrHVv8lyPyiVi2PVKsa3uD7YCPcbYAzQPGDBRznAKFNKIgqOcENTTNb5rbUoMh93YcFAZc51X//+1TE5wALKPdV7CRxASWZbjT2DHbULI1z1bS9pdGjqkPFsLaqyiYYMUY8Rf8pTZozRUNKQZYJIMdsrfkuvxwYBUYKyqrwGsY81pVDvgAf76wPKgDHlfsmVjeRtXLpxIaoPYxYOCwQw4VHvznS2uXpVJ+OdtHrwk1F0cBNP5qR7K5MWfbuAqspFVVbFZggNg8GQ0MxRtCg56AEAREEUj2lLRIBQy1GFwWMu1OP6+7U38gSLOwLBLKhpssNQn60Aq3/+1TE6wAMHM86reBriTUeaKmGChGPq9DovAmiv19JYFGGCxxVptd+72M178RBDDyAAQJ7jRMZcRnkh/+cxGOlUjMWfP8hHaoAsxQDRfceLjBk6/M+sMzJMWLl3HYZGl+5VI//ocA4AY82bU+YEeZUamsy1MeOMohtN9X8VAQcFB0b112k+pCdpJQoWbiNMcTM3FzC7ZJXENsXm5YgJxxUJdJjgQxFHArFIcDSd6vbodFhXoWliCIaNwnDCvHQu+//+1TE6QELTPs5TRh2AVyYZgmnlhBV881AgyN6l3oIQxYIhB/xJEWTMABepFpm+vACJyoQkSKMKDj1Ajj5j+VEY2l0zO34UUjK0WbISzAAjCnwBEBrECOggwiqytIN5WTzrKEPCPAHuFxs6Z4hfDapEQFQqVmUYBSNbbpQ1e5TfdeTCkOxWQbukKw2XJrJ2VIReF3pPLnqIS8i6TEI7RBSCGkchRGTfhxWjuaD3PF0RgXqbK1jLZcabkGSrgF+2TL/+1TE5YAJuLM7TDBpgWWaZVWTCtkMmQXYuhPkJP1mTDK6jum0locIXLkj06soen10uDMfahv2o7UmaRe0kaSGE8Ok6WzX+aJm96X+uy7KLWFr12Ve+KKU1TTDKHNQqMqjjIZIMsTEza4U22UcShEQoA2CJgVTXaY7GoVGNBSNAAAxtzjI7UYbq4J6SsYrOY5lK545r4QOmyhxQdmImFHyBCSV/awp8dFwUrfst3c6ldZxUeVwTDpQsagFAZDC803/+1TE5wESaP00bTzXCgYeaJWsJlkFFJU4w1hcuCn9UeGqhhRlRDESVEkwFcPQB8NRFJ4mcU8DT7LDquzQCNohSRR53XNSPBFXD5sO0k4DEOav2PmRXRTI5nM5bZFnU5tqM35XHuKK4SANu0MzAaVEBiWMgAC6TcDJ8sBpISOscLKT870cc5ICQ2ZevdNYekuyibs6CC5indfKNRgEYFEm/L7dtshRNiwNjfWv677+WGkmzhMPz6wbKap4vRuAC9X/+1TEsgAOpQFxp406cUGRbTTzFaqF1WQKEL1wMrxMegaFJiUPiFkKqEoZQiIQoXQvdr20ZEMHXdVqSObCCW/+td0BodVEWOZAzmSGslVW/ZeVjOgmxTI5twFwREYFDfTYRJEQAVG5AGEM8CWC8H0Po86mU4lzVC2KUuGe66pRq1AgPn39HhOWRmrreVVEiVkgPAuM7/zSxoJck8Q8LpF76+rVyMs7/0uvrCM24c54LnX1qJkjIAKTloCuEUVZmpr/+1TEpIAJmM9155iteSoLrDz0jWkhJIZ02mGM1S/GSqGqCu7NT2B4ojmEQIOA6Z8/mHw1AOiY59v0pozoCnExWrqq3upnsMGlQedujeyzoKs5jrQxisyq8Tf+Ouo/1QAMku4EZHtRxFQni5Qkc7R6kdq68GKptQPGX1ak0NvuC8EhRxBFHT9eMpTGlXORs+OitYhjA2MVEYi6OvbWirfvRqbeYizQcWnz/LqRK61Aj98HuB8cNgWElQHxqhiXGen/+1TErgAKJOtjjCRJ8UUdKvTzDsqgIFF+1fYkIzJLJ+/uNHXRToGpnozvfc+mAr/0gMaLk9L7S3i0vN1X8uGIQETNRhLM0hkMOq9vTK5drAipHmY7B/RSwGkdRqNpoqRQn642jOiIOYWg021CQplzG99U1HbmmoozX7w8NRLI/yW7oneLPaq1ZIw1DE3ARodopFTgAOd/RQAKAAAJIAA0QIfjlE/gpEZMQl5KksxNYtAATSHCgsDzIOND7EPHURL/+1TEsgAKmQtVp5ivETudaXTzCpDhtYoEapRMi9wxqKKTpdGULxkXiaV8XCaFgdhqxeLy1GX9I0Js+iRc3RRWiXaP9zczTNUyfQLuipJav9OaMUDAgBoseETfhkQB8uHxOFhLBVZ1f6BP//yKTEFNRTMuMTAwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/+1TEtYBJlOtXhhhtsSwT6zaeYAaqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/+1TEvwAP9PktGTmAAAAANIOAAASqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=';
/** Registro de poderes (v3.6.36): un poder = una entrada (id + nombre +
 *  voz ES + voz EN + icono). El reparto aleatorio y TODOS los campeonatos
 *  los cogen solos; añadir el tercero = ① entrada aquí + ② i18n
 *  poder_<id> ES/EN + ③ voces embebidas + ④ PNG embebido. */
const PODERES_PALA = [
  { id: 'mega', nombre: () => T('poder_mega'),
    voz: VOZ_PODER_MEGA, vozEn: VOZ_PODER_MEGA_EN, png: PNG_PODER_MEGA },
  { id: 'efecto', nombre: () => T('poder_efecto'),
    voz: VOZ_PODER_EFECTO, vozEn: VOZ_PODER_EFECTO_EN, png: PNG_PODER_EFECTO },
];
const MEGA_DUR = 15;    // s de MEGA PALA por carga (apilable: +15 s cada una)
const MEGA_TOPE = 3;    // cargas máximas de un poder (×3)
const MEGA_GOLPES = 11; // cada 11 golpes del rally = +1 carga
// v3.6.36 · SÚPER EFECTO (reglas del dueño): ×2 al spin GENERADO por el
// golpe (NUNCA al acumulado que ya traía la bola), tope de seguridad 2×// spinMax, ventana de 8 s O 5 golpes con efecto (lo que ocurra antes);
// Magnus y bote amplificados SOLO en la bola marcada (ppEfecto).
const EFECTO_DUR = 8;       // s de ventana
const EFECTO_GOLPES = 5;    // golpes potenciados por ventana
const EFECTO_SPIN_MUL = 2;  // multiplicador del brush generado
const EFECTO_SPIN_MIN = 25; // |spin| mínimo para contar como «con efecto»
// ICONO anclado AL MANGO (petición del dueño): «ligeramente por encima
// del mando de la pala en su base, así forma parte de la pala y no
// distrae». Origen de la montura = punto de agarre; −y = hacia el mando.
const MEGA_ICON_Y = -0.034;   // base de la mano, justo sobre el mando
const MEGA_ICON_Z = 0.004;    // pegado al eje del mango (no «a un lado»)
const MEGA_ICON_S = 0.048;    // 4,8 cm — pequeño, parte de la pala

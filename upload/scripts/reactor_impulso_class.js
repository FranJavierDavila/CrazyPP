/* ============================================================================
 *  v3.4.0 · REACTOR DE IMPULSO (IMP1) — NUEVA ETAPA 4 del campeonato
 *  Estación Orbital (mecánica del dueño, sustituye al ARKANOID II / muro2).
 *  ----------------------------------------------------------------------------
 *  El jugador estabiliza el reactor de impulso de la nave destruyendo los
 *  CUBOS CUÁNTICOS que expulsa durante sus episodios de inestabilidad:
 *    · SALA PROPIA de 6 imágenes del dueño (reactor_impulso/*.jpg|png) sobre
 *      el volumen del núcleo; sin mesa tradicional, sin rival, sin recortes.
 *    · NÚCLEO central con máquina de estados: ESTABLE (azul, rotación
 *      uniforme, sin cubos) ↔ INESTABLE (rojo pulsante, rotación caótica,
 *      alarma y expulsión de cubos), con desaceleración perceptible.
 *    · VENTANAS laterales: efecto de viaje a velocidad lumínica compartido
 *      (estrellas blancas con estelas que se desplazan del centro afuera).
 *    · BASE FLOTANTE (base.png): plataforma cilíndrica achatada que
 *      SUSTITUYE a la mesa como punto de reposición de la pelota.
 *    · 3 OLEADAS (3/5/7 cubos, 120 s independientes cada una).
 *    · PALA: la pelota física de siempre (integración propia por subpasos,
 *      golpeo bumper con la velocidad real de la pala — patrón REACTOR).
 *    · PISTOLA LÁSER (pistol.glb, pegamento del MURO 2 reutilizado) contra
 *      DIANAS cuánticas (diana_quantica.png) con ciclo 1 s visible / 1 s de
 *      espera; cada acierto desata una PERTURBACIÓN.
 *    · PERTURBACIONES: Gravedad 0 (deriva flotante), Atractor (agrupa en el
 *      centro: UN golpe válido destruye TODOS los cubos) y Supergravedad
 *      (caen a ras de suelo y quedan comprimidas). Cambio automático cada
 *      30 s + por diana; mecanismos independientes; la nueva sustituye a la
 *      anterior; la finalización de la oleada tiene prioridad.
 *    · PANTALLA suspendida del techo (pantallainfo.png) con oleada, tiempo,
 *      cubos restantes, estado del reactor y perturbación activa.
 *    · Derrota (tiempo a cero con cubos): banner + astro_laughing.png frente
 *      al jugador y regreso a la sala (escenario de la etapa 1).
 *  Regla Quest: TODO se construye UNA vez (pools); nada se crea por partida.
 *  ========================================================================== */
const IMP_CFG = {
  waves: [3, 5, 7],            // cubos por oleada
  time: 120,                   // segundos por oleada (independiente)
  coreY: 1.55, coreZ: -2.75,   // núcleo en la zona central del escenario
  coreR: 0.30,
  baseX: 0, baseY: 0.80, baseZ: -0.55, baseR: 0.46,   // base flotante (sin mesa)
  ballT: 1.05, ballH: 0.38,    // bote-en-espera sobre la base (periodo/altura)
  graceT: 0.55,                // animación de rebote antes de estar disponible
  respawnT: 0.8,               // reposición de pelota (configurable)
  fragLife: 0.9,               // vida de los fragmentos (configurable)
  dianaVis: 1.0, dianaWait: 1.0, dianaSize: 0.46,     // ciclo 1 s / 1 s
  pertAutoT: 30,               // cambio automático de perturbación
  cubeS: 0.32, cubeHitR: 0.24, // tamaño del cubo y radio de colisión
  minBallOut: 2.5, maxBallOut: 8.5,   // velocidad de la bola tras el golpeo
  spawnFlight: 0.75,           // expulsión del núcleo al spot
  superY: 0.36,                // altura baja de la supergravedad
  atractorPos: { x: 0, y: 1.35, z: -1.95 },   // zona central del atractor
  bounds: { x: 2.5, yMin: 0.34, yMax: 2.25, zMin: -4.6, zMax: -0.85 },
};

class ReactorImpulso {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.built = false;
    this.phase = 'idle';               // intro | play | result
    this.phaseT = 0;
    this.wave = 0;                     // 1..3
    this.waveT = IMP_CFG.time;
    this.aliveCubes = 0;
    this.waveActive = false;
    this.reactorState = 'estable';     // estable | inestable
    this.pert = null;                  // null | 'g0' | 'atractor' | 'super'
    this._pertAutoT = IMP_CFG.pertAutoT;
    this._stableT = 0;                 // pausa estable entre oleadas
    this._t = 0;
    this._spinK = 0;                   // 0 = estable uniforme · 1 = caótico
    this._alarmCd = 0;
    this._hudKey = '';
    this._banner = null;
    this._rivalHome = null;
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    this._tmpC = new THREE.Vector3();
  }

  _A(p) { return this.ctrl._A('reactor_impulso/' + p); }
  _G() { return Math.abs(DIMS.gravity || 9.6); }   // NUC1: DIMS.gravity es NEGATIVO

  /* ---------------- construcción (una sola vez, en start) ---------------- */
  _build() {
    if (this.built) return;
    this.built = true;
    const g = this.game;
    const R = (CORE && CORE.DIMS) || {};
    const hx = R.roomHalfX || 3.05, bz = R.roomBackZ || 2.35,
      fz = R.roomFrontZ || -5.55, hh = R.roomHeight || 2.85;
    this._room = { hx, bz, fz, hh, zc: (bz + fz) / 2, depth: bz - fz };

    this.grp = new THREE.Group();
    this.grp.visible = false;
    g.rig.add(this.grp);               // espacio de la mesa (convención v2.44)

    /* SALA PROPIA: 6 imágenes del dueño sobre el volumen del núcleo */
    const carga = (f) => {
      const t = new THREE.TextureLoader().load(this._A(f));
      t.colorSpace = THREE.SRGBColorSpace;
      this.ctrl._ownTex.add(t);
      return t;
    };
    const plano = (w, h, tex, px, py, pz, ry, rx) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ map: tex }));
      m.position.set(px, py, pz);
      if (ry) m.rotation.y = ry;
      if (rx) m.rotation.x = rx;
      this.grp.add(m);
      return m;
    };
    plano(hx * 2, this._room.depth, carga('suelo.jpg'), 0, 0, this._room.zc, 0, -Math.PI / 2);
    plano(hx * 2, this._room.depth, carga('techo.jpg'), 0, hh, this._room.zc, 0, Math.PI / 2);
    plano(hx * 2, hh, carga('frente.jpg'), 0, hh / 2, fz, 0, 0);
    plano(hx * 2, hh, carga('fondo.jpg'), 0, hh / 2, bz, Math.PI, 0);
    plano(this._room.depth, hh, carga('izquierda.png'), -hx, hh / 2, this._room.zc, Math.PI / 2, 0);
    plano(this._room.depth, hh, carga('derecha.png'), hx, hh / 2, this._room.zc, -Math.PI / 2, 0);

    /* VENTANAS: viaje a velocidad lumínica (el MISMO efecto en ambas) */
    this._warps = [this._warpBuild(-1), this._warpBuild(1)];

    /* NÚCLEO DEL REACTOR (procedural, azul estable / rojo inestable) */
    this.core = new THREE.Group();
    this.core.position.set(0, IMP_CFG.coreY, IMP_CFG.coreZ);
    this.coreBody = new THREE.Mesh(
      new THREE.IcosahedronGeometry(IMP_CFG.coreR, 1),
      new THREE.MeshStandardMaterial({
        color: 0x14243a, roughness: 0.3, metalness: 0.55,
        emissive: 0x2e7cff, emissiveIntensity: 0.9, flatShading: true,
      }));
    this.ring1 = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.035, 10, 48),
      new THREE.MeshStandardMaterial({
        color: 0x0a1626, roughness: 0.4, metalness: 0.5,
        emissive: 0x2e7cff, emissiveIntensity: 0.9, transparent: true, opacity: 0.9,
      }));
    this.ring2 = new THREE.Mesh(new THREE.TorusGeometry(0.60, 0.026, 10, 52),
      new THREE.MeshStandardMaterial({
        color: 0x0a1626, roughness: 0.4, metalness: 0.5,
        emissive: 0x2e7cff, emissiveIntensity: 0.75, transparent: true, opacity: 0.85,
      }));
    this.ring1.rotation.x = Math.PI / 2.4;
    this.ring2.rotation.x = Math.PI / 1.8;
    this.coreGlow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this._texGlow(), color: 0x4d8dff, transparent: true, opacity: 0.55,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    this.coreGlow.scale.setScalar(1.15);
    this.coreLight = new THREE.PointLight(0x4d8dff, 0.9, 7.5, 2);
    this.core.add(this.coreBody, this.ring1, this.ring2, this.coreGlow, this.coreLight);
    this.core.visible = false;
    this.grp.add(this.core);

    /* CUBOS CUÁNTICOS (pool de 7 = oleada máxima) */
    this.cubes = [];
    const cGeo = new THREE.BoxGeometry(IMP_CFG.cubeS, IMP_CFG.cubeS, IMP_CFG.cubeS);
    for (let i = 0; i < 7; i++) {
      const mat = new THREE.MeshStandardMaterial({
        color: 0x8fa9bd, roughness: 0.4, metalness: 0.35,
        emissive: 0xff3524, emissiveIntensity: 0.0,
      });
      const mesh = new THREE.Mesh(cGeo, mat);
      mesh.visible = false;
      mesh.castShadow = true;
      this.grp.add(mesh);
      this.cubes.push({
        mesh, mat, alive: false,
        pos: mesh.position,
        vel: new THREE.Vector3(),
        spot: new THREE.Vector3(),
        from: new THREE.Vector3(),
        fase: Math.random() * Math.PI * 2,
        w1: 0.4 + Math.random() * 0.5, w2: 0.35 + Math.random() * 0.55,
        tumble: new THREE.Vector3(
          (Math.random() < 0.5 ? -1 : 1) * (0.4 + Math.random() * 0.8),
          (Math.random() < 0.5 ? -1 : 1) * (0.4 + Math.random() * 0.8), 0),
        wanderT: 0, thud: false,
        spawnT: 9, from0: 0,
      });
    }

    /* FRAGMENTOS (exclusivamente visuales) + flashes (pool) */
    this.glowTex = this._texGlow();
    this.frags = [];
    const fGeo = new THREE.BoxGeometry(0.055, 0.055, 0.055);
    for (let i = 0; i < 44; i++) {
      const fm = new THREE.Mesh(fGeo, new THREE.MeshStandardMaterial({
        color: 0xb8c6d4, roughness: 0.5, metalness: 0.3,
        emissive: 0xff5a30, emissiveIntensity: 0.7, transparent: true, opacity: 0,
      }));
      fm.visible = false;
      this.grp.add(fm);
      this.frags.push({ mesh: fm, vel: new THREE.Vector3(), t: 9 });
    }
    this.flashes = [];
    for (let i = 0; i < 6; i++) {
      const fl = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.7),
        new THREE.MeshBasicMaterial({
          map: this.glowTex, color: 0x9fe8ff, transparent: true, opacity: 0,
          blending: THREE.AdditiveBlending, depthWrite: false,
          side: THREE.DoubleSide,
        }));
      fl.visible = false;
      fl.renderOrder = 25;
      this.grp.add(fl);
      this.flashes.push({ mesh: fl, t: 9 });
    }

    /* BASE FLOTANTE (sustituye a la mesa: reposición de la pelota) */
    this.baseGrp = new THREE.Group();
    this.baseGrp.position.set(IMP_CFG.baseX, IMP_CFG.baseY, IMP_CFG.baseZ);
    const cuerpo = new THREE.Mesh(
      new THREE.CylinderGeometry(IMP_CFG.baseR, IMP_CFG.baseR + 0.06, 0.10, 40),
      new THREE.MeshStandardMaterial({
        color: 0x2a3542, roughness: 0.35, metalness: 0.7,
        emissive: 0x0a1626, emissiveIntensity: 0.4,
      }));
    const texBase = carga('base.png');
    const tapa = new THREE.Mesh(new THREE.CircleGeometry(IMP_CFG.baseR - 0.005, 40),
      new THREE.MeshBasicMaterial({ map: texBase }));
    tapa.rotation.x = -Math.PI / 2;
    tapa.position.y = 0.051;
    const aro = new THREE.Mesh(new THREE.TorusGeometry(IMP_CFG.baseR + 0.035, 0.016, 8, 48),
      new THREE.MeshStandardMaterial({
        color: 0x0a1626, roughness: 0.4, metalness: 0.5,
        emissive: 0x36d8ff, emissiveIntensity: 1.2, transparent: true, opacity: 0.9,
      }));
    aro.rotation.x = Math.PI / 2;
    aro.position.y = -0.02;
    const bajo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.glowTex, color: 0x36d8ff, transparent: true, opacity: 0.3,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    bajo.scale.setScalar(1.2);
    bajo.position.y = -0.12;
    this.baseGrp.add(cuerpo, tapa, aro, bajo);
    this.baseGrp.visible = false;
    this.grp.add(this.baseGrp);

    /* DIANA CUÁNTICA (una a la vez; sprite = billboard al jugador) */
    const texDiana = carga('diana_quantica.png');
    this.diana = {
      sp: new THREE.Sprite(new THREE.SpriteMaterial({
        map: texDiana, transparent: true, depthWrite: false, opacity: 0.98,
      })),
      fase: 'wait', t: 0.6,
    };
    this.diana.sp.scale.setScalar(IMP_CFG.dianaSize);
    this.diana.sp.visible = false;
    this.diana.sp.renderOrder = 20;
    this.grp.add(this.diana.sp);

    /* PANTALLA suspendida del techo (pantallainfo.png + capa de texto) */
    this.panCv = document.createElement('canvas');
    this.panCv.width = 1024; this.panCv.height = 512;
    this.panTex = this.ctrl._ct(this.panCv);
    this.panMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(2.05, 1.025),
      new THREE.MeshBasicMaterial({ map: this.panTex, transparent: true, depthWrite: false }));
    this.panMesh.position.set(0, 2.44, -3.6);
    this.panMesh.rotation.x = -0.12;
    this.panMesh.renderOrder = 10;
    this.grp.add(this.panMesh);
    this._panImg = null;
    try {
      const img = new Image();
      img.onload = () => { this._panImg = img; this._hudKey = ''; };
      img.src = this._A('pantallainfo.png');
    } catch (e) { /* sin arte: el panel se pinta igual */ }
  }

  _warpBuild(side) {
    const n = 90;
    const pos = new Float32Array(n * 2 * 3);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const lines = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0.75,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    lines.frustumCulled = false;
    lines.visible = false;
    this.grp.add(lines);
    const stars = [];
    for (let i = 0; i < n; i++) {
      stars.push({
        a: Math.random() * Math.PI * 2, r: Math.random() * 2.4,
        sp: 0.55 + Math.random() * 1.1, len: 0.10 + Math.random() * 0.18,
      });
    }
    return {
      lines, pos: geo.attributes.position, stars, n,
      x: side * ((this._room.hx) - 0.03),
      cy: 1.5, cz: this._room.zc,
    };
  }

  _texGlow() {
    const cv = document.createElement('canvas');
    cv.width = 128; cv.height = 128;
    const c = cv.getContext('2d');
    const gr = c.createRadialGradient(64, 64, 2, 64, 64, 62);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.35, 'rgba(120,190,255,0.55)');
    gr.addColorStop(1, 'rgba(120,190,255,0)');
    c.fillStyle = gr; c.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this.ctrl._ownTex.add(t);
    return t;
  }

  /* ---------------- ciclo de vida ---------------- */
  start() {
    if (this.active) return;
    this._build();
    this.active = true;
    this.phase = 'intro';
    this.phaseT = 3.2;
    this.wave = 0;
    this.waveT = IMP_CFG.time;
    this.aliveCubes = 0;
    this.waveActive = false;
    this.pert = null;
    this._pertAutoT = IMP_CFG.pertAutoT;
    this._stableT = 0;
    this._spinK = 0;
    this.reactorState = 'estable';
    this._banner = {
      title: 'REACTOR DE IMPULSO',
      sub: 'Destruye los cubos cuánticos · 3 oleadas',
      col: '#ffd257',
    };
    this._hudKey = '';
    const g = this.game;
    // ESCENARIO: fuera sala del núcleo, mesa, marcador, rival y recortes
    if (g.roomGroup) g.roomGroup.visible = false;    // sala de la estación fuera
    this.grp.visible = true;
    g.tableGroup.visible = false;                    // SIN mesa tradicional
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    if (this.ctrl.rivalMesh) {
      this._rivalHome = this._rivalHome || this.ctrl.rivalMesh.position.clone();
      this.ctrl.rivalMesh.visible = false;           // sin rival durante la prueba
    }
    if (this.ctrl.cartel) this.ctrl.cartel.visible = false;
    if (this.ctrl.powerSign) this.ctrl.powerSign.visible = false;
    try { if (this.ctrl.mapa && this.ctrl.mapa.hide) this.ctrl.mapa.hide(); } catch (e) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = false; } catch (e) { /* */ }
    // pelota disponible sobre la base flotante
    g.ball.ignoreNet = true;
    g.ballMesh.scale.setScalar(1);
    g.ballMesh.visible = true;
    this._ballDisponible(0);
    // núcleo azul estable
    this.core.visible = true;
    this.coreLight.color.setHex(0x4d8dff);
    this.coreLight.intensity = 0.9;
    this.coreGlow.material.color.setHex(0x4d8dff);
    for (const c of this.cubes) { c.alive = false; c.mesh.visible = false; }
    this.diana.sp.visible = false;
    this.diana.fase = 'wait'; this.diana.t = 1;
    g.rules.message = 'REACTOR DE IMPULSO';
    this.hudOn(true);
    g.audio.playOsc(392, 392, 0.12, 'square', 0.11, 0);
    window.setTimeout(() => g.audio.playOsc(523, 523, 0.12, 'square', 0.11, 0), 140);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.2, 'square', 0.12, 0), 280);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  hudOn(on) {
    this.grp.visible = on;
    if (this.baseGrp) this.baseGrp.visible = on;
    if (this.core) this.core.visible = on;
    this._hudKey = '';
  }

  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    if (g.roomGroup) g.roomGroup.visible = false;
    this.hudOn(true);
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (this.ctrl.rivalMesh && this.phase !== 'result') this.ctrl.rivalMesh.visible = false;
    this._hudKey = '';
  }

  stop() {
    this.active = false;
    this.phase = 'idle';
    this.waveActive = false;
    if (!this.built) return;
    const g = this.game;
    this.hudOn(false);
    this.diana.sp.visible = false;
    for (const c of this.cubes) { c.alive = false; c.mesh.visible = false; }
    for (const f of this.frags) { f.t = 9; f.mesh.visible = false; }
    for (const f of this.flashes) { f.t = 9; f.mesh.visible = false; }
    for (const w of this._warps) w.lines.visible = false;
    // la sala de la estación vuelve
    if (g.roomGroup) g.roomGroup.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ball.ignoreNet = false;
    g.ballMesh.scale.setScalar(1);
    g.ballMesh.visible = true;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    try {
      const D = this.ctrl.D;
      g.ball.pos.set(0, D.tableTopY + (D.ballRadius || 0.02), D.tableCenterZ + 0.45);
      if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    } catch (e) { /* */ }
    if (this.ctrl.rivalMesh) {
      if (this._rivalHome) this.ctrl.rivalMesh.position.copy(this._rivalHome);
      this.ctrl.rivalMesh.visible = true;
    }
    try { if (this.ctrl.mapa && this.ctrl.mapa.show) this.ctrl.mapa.show(); } catch (e) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = true; } catch (e) { /* */ }
  }

  /* ---------------- bucle de la prueba ---------------- */
  step(dt) {
    if (!this.active) return;
    const g = this.game;
    this._t += dt;
    if (this.phase === 'intro') {
      this.phaseT -= dt;
      this._ballStep(dt);
      this._anims(dt);
      if (this.phaseT <= 0) {
        this.phase = 'play';
        this._oleadaArranca(1);
      }
      if (this._hudKey !== 'banner') { this._hudKey = 'banner'; this._pantalla(); }
      return;
    }
    if (this.phase === 'play') {
      if (this._stableT > 0) {
        // pausa ESTABLE entre oleadas: el reactor desacelera a azul
        this._stableT -= dt;
        this._ballStep(dt);
        this._anims(dt);
        if (this._stableT <= 0) this._oleadaArranca(this.wave + 1);
        if (this._hudKey !== 'banner') { this._hudKey = 'banner'; this._pantalla(); }
        return;
      }
      this.waveT -= dt;
      if (this.waveT <= 0) {
        this.waveT = 0;
        this._pantalla();
        this._finish(false, 'time');
        return;
      }
      // perturbación AUTOMÁTICA cada 30 s (independiente de las dianas)
      if (this.waveActive && this.aliveCubes > 0) {
        this._pertAutoT -= dt;
        if (this._pertAutoT <= 0) {
          this._pertAutoT = IMP_CFG.pertAutoT;
          this._pertAplica(this._pertAleatoria(), true);
        }
      }
      // alarma sonora mientras dura la inestabilidad
      if (this.reactorState === 'inestable' && this.waveActive) {
        this._alarmCd -= dt;
        if (this._alarmCd <= 0) {
          this._alarmCd = 1.15;
          try { g.audio.playOsc(700, 480, 0.30, 'sawtooth', 0.12, 0); } catch (e) { /* */ }
        }
      }
      this._cubosStep(dt);
      this._dianasStep(dt);
      this._ballStep(dt);
      if (!this.active) return;        // pudo terminar dentro
      this._anims(dt);
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      this._anims(dt);
      if (this.phaseT <= 0) { this._afterResult(); return; }
    }
    this._pantalla();
  }

  /* ---------------- reactor: estados y animación ---------------- */
  _reactorEstado(est) {
    if (this.reactorState === est) return;
    this.reactorState = est;
    this._hudKey = '';
  }

  _anims(dt) {
    const t = this._t;
    // desaceleración perceptible al estabilizar (spec §3)
    const objetivo = this.reactorState === 'inestable' ? 1 : 0;
    this._spinK += (objetivo - this._spinK) * Math.min(1, dt * 1.6);
    const k = this._spinK;
    this.core.rotation.y += (0.55 + k * (2.6 + Math.sin(t * 3.1) * 1.7 + Math.sin(t * 7.3) * 0.9)) * dt;
    this.core.rotation.x += (0.12 + k * Math.sin(t * 2.3) * 1.1) * dt;
    this.ring1.rotation.z += (0.4 + k * (3.2 + Math.sin(t * 4.1) * 2.0)) * dt;
    this.ring2.rotation.x += (0.3 + k * (2.4 + Math.cos(t * 3.7) * 1.6)) * dt;
    const azul = 0x4d8dff, rojo = 0xff3524;
    const mezcla = (a, b) => {
      const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255;
      const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255;
      return (((ar + (br - ar) * k) << 16) | ((ag + (bg - ag) * k) << 8) | (ab + (bb - ab) * k)) >>> 0;
    };
    const col = mezcla(azul, rojo);
    const pulso = 0.9 + k * (0.8 + Math.sin(t * 6) * 0.45);
    this.coreLight.color.setHex(col);
    this.coreLight.intensity = pulso;
    this.coreGlow.material.color.setHex(col);
    this.coreGlow.material.opacity = 0.5 + k * 0.22;
    this.coreBody.material.emissive.setHex(col);
    this.coreBody.material.emissiveIntensity = 0.75 + k * 0.75;
    this.ring1.material.emissive.setHex(col);
    this.ring2.material.emissive.setHex(col);
    // base flotante: leve balanceo energético
    this.baseGrp.position.y = IMP_CFG.baseY + Math.sin(t * 1.4) * 0.015;
    // estrellas de velocidad lumínica (ambas ventanas, el mismo efecto)
    for (const w of this._warps) this._warpStep(w, dt);
    // pulso rojo de los cubos durante la inestabilidad
    if (this.reactorState === 'inestable') {
      for (const c of this.cubes) {
        if (!c.alive) continue;
        c.mat.emissive.setHex(0xff3524);
        c.mat.emissiveIntensity = 0.55 + Math.sin(t * 5 + c.fase) * 0.35;
      }
    }
    this._fxStep(dt);
  }

  _warpStep(w, dt) {
    const pos = w.pos.array;
    for (let i = 0; i < w.n; i++) {
      const s = w.stars[i];
      s.r += (0.5 + s.r * 1.35) * s.sp * dt;
      if (s.r > 2.55) {
        s.r = 0.04 + Math.random() * 0.25;
        s.a = Math.random() * Math.PI * 2;
      }
      const ca = Math.cos(s.a), sa = Math.sin(s.a);
      const px = w.x, py = w.cy + sa * s.r, pz = w.cz + ca * s.r;
      const L = s.len * (0.35 + s.r * 0.5);
      const o = i * 6;
      pos[o] = px; pos[o + 1] = py; pos[o + 2] = pz;
      pos[o + 3] = px; pos[o + 4] = py - sa * L; pos[o + 5] = pz - ca * L;
    }
    w.pos.needsUpdate = true;
    w.lines.visible = true;
  }

  /* ---------------- oleadas ---------------- */
  _oleadaArranca(n) {
    this.wave = n;
    this.waveT = IMP_CFG.time;                    // 120 s INDEPENDIENTES por oleada
    this.aliveCubes = 0;
    this.waveActive = true;
    this.pert = null;
    this._pertAutoT = IMP_CFG.pertAutoT;
    this._stableT = 0;
    // secuencia de activación (spec §3): pantalla → rojo → alarma+expulsión → timer+dianas
    this._reactorEstado('inestable');
    this._alarmCd = 0.2;
    this._expulsar(IMP_CFG.waves[n - 1]);
    this.diana.fase = 'wait'; this.diana.t = 0.7;
    const g = this.game;
    g.rules.message = tx('PERTURBACIÓN ' + n + ' · destruye ' + IMP_CFG.waves[n - 1] + ' cubos',
      'WAVE ' + n + ' · destroy ' + IMP_CFG.waves[n - 1] + ' cubes');
    try { g.audio.announce(tx('Perturbación ' + n, 'Wave ' + n), true); } catch (e) { /* */ }
    g.audio.playOsc(220, 440, 0.30, 'sawtooth', 0.14, 0);
    this._hudKey = '';
  }

  _oleadaCompleta() {
    // se cancelan dianas y perturbaciones de la oleada (prioridad sobre todo)
    this.waveActive = false;
    this.pert = null;
    this.diana.sp.visible = false;
    this.diana.fase = 'wait';
    this._reactorEstado('estable');               // desacelera y vuelve a azul
    const g = this.game;
    g.audio.playOsc(523, 523, 0.12, 'square', 0.12, 0);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.12, 'square', 0.12, 0), 140);
    window.setTimeout(() => g.audio.playOsc(784, 784, 0.2, 'square', 0.13, 0), 280);
    try { g.audio.announce(tx('Reactor estable', 'Reactor stable'), true); } catch (e) { /* */ }
    if (this.wave >= IMP_CFG.waves.length) { this._finish(true); return; }
    this._stableT = 2.3;                          // pausa estable antes de la siguiente
    g.rules.message = tx('¡Reactor estable! Preparando oleada ' + (this.wave + 1) + '…',
      'Reactor stable! Preparing wave ' + (this.wave + 1) + '…');
  }

  /* ---------------- cubos cuánticos ---------------- */
  _spotsPara(n) {
    const B = IMP_CFG.bounds;
    const out = [];
    let guard = 0;
    while (out.length < n && guard++ < 500) {
      const x = (Math.random() * 2 - 1) * B.x;
      const y = B.yMin + Math.random() * (B.yMax - B.yMin);
      const z = B.zMin + Math.random() * (B.zMax - B.zMin);
      this._tmpA.set(x, y, z);
      if (this._tmpA.z > -1.0) continue;                          // no encima del jugador
      if (this._tmpA.distanceTo(this.core.position) < 1.25) continue;   // dentro del reactor NO
      let ok = true;
      for (const q of out) if (q.distanceTo(this._tmpA) < 0.72) { ok = false; break; }
      if (ok) out.push(this._tmpA.clone());                       // sin superposiciones
    }
    while (out.length < n) {
      out.push(new THREE.Vector3((Math.random() * 2 - 1) * B.x,
        B.yMin + Math.random() * (B.yMax - B.yMin),
        B.zMin + Math.random() * (B.zMax - B.zMin)));
    }
    return out;
  }

  _expulsar(n) {
    const spots = this._spotsPara(n);
    for (let i = 0; i < n; i++) {
      const c = this.cubes[i];
      c.alive = true;
      c.mesh.visible = true;
      c.mesh.scale.setScalar(1);
      c.spawnT = -i * 0.12;                       // expulsión escalonada
      c.from0 = IMP_CFG.spawnFlight;
      c.from.copy(this.core.position);
      c.spot.copy(spots[i]);
      c.vel.set(0, 0, 0);
      c.wanderT = 0; c.thud = false;
      c.pos.copy(c.from);
      this.aliveCubes++;
    }
    for (let i = n; i < this.cubes.length; i++) {
      const c = this.cubes[i];
      c.alive = false;
      c.mesh.visible = false;
    }
    const g = this.game;
    g.audio.playOsc(180, 340, 0.24, 'sawtooth', 0.16, 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 80);
  }

  _cubosStep(dt) {
    const t = this._t;
    const B = IMP_CFG.bounds;
    for (const c of this.cubes) {
      if (!c.alive) continue;
      if (c.spawnT < c.from0) {
        c.spawnT += dt;                           // expulsión del núcleo al spot
        const k = Math.max(0, Math.min(1, c.spawnT / c.from0));
        const e = 1 - Math.pow(1 - k, 3);
        c.pos.lerpVectors(c.from, c.spot, e);
        c.mesh.rotation.x += 3 * dt; c.mesh.rotation.y += 4 * dt;
        if (k >= 1) {
          c.vel.set((Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 0.3,
            (Math.random() - 0.5) * 0.5);
        }
        continue;
      }
      if (this.pert === 'g0') {
        // GRAVEDAD 0: deriva flotante caótica suave, sin gravedad aparente
        c.wanderT += dt;
        if (c.wanderT > 1.2) {
          c.wanderT = 0;
          c.vel.set((Math.random() - 0.5) * 0.72, (Math.random() - 0.5) * 0.5,
            (Math.random() - 0.5) * 0.72);
        }
        c.pos.addScaledVector(c.vel, dt);
        c.mesh.rotation.x += c.tumble.x * dt * 0.7;
        c.mesh.rotation.y += c.tumble.y * dt * 0.7;
      } else if (this.pert === 'atractor') {
        // ATRACTOR: convergen a la zona central y orbitan apretados
        this._tmpA.copy(IMP_CFG.atractorPos).sub(c.pos);
        const d = this._tmpA.length() || 0.001;
        this._tmpA.multiplyScalar(1 / d);
        this._tmpB.set(-this._tmpA.z, 0.15 * Math.sin(t * 1.3 + c.fase), this._tmpA.x)
          .normalize();
        const sp = Math.min(1.7, 0.35 + d * 0.95);
        c.vel.copy(this._tmpA).multiplyScalar(sp * Math.min(1, d / 0.4))
          .addScaledVector(this._tmpB, d > 0.5 ? 0.55 : 1.2);
        c.pos.addScaledVector(c.vel, dt);
        c.mesh.rotation.y += 5.5 * dt; c.mesh.rotation.x += 3.2 * dt;
      } else if (this.pert === 'super') {
        // SUPERGRAVEDAD: caen a ras de suelo y quedan comprimidas
        if (c.pos.y > IMP_CFG.superY + 0.005) {
          c.vel.y -= this._G() * 2.3 * dt;
          c.pos.addScaledVector(c.vel, dt);
          c.mesh.scale.set(1, 1, 1);
          if (c.pos.y <= IMP_CFG.superY) {
            c.pos.y = IMP_CFG.superY;
            c.vel.set(0, 0, 0);
          }
        } else if (!c.thud) {
          c.thud = true;                          // compresión VISUAL (colisión intacta)
          c.mesh.scale.set(1.06, 0.78, 1.06);
          this._flash(c.pos, 0xffc9a0);
          try { this.game.audio.playOsc(140, 70, 0.12, 'sine', 0.12, 0); } catch (e) { /* */ }
        }
      } else {
        // caos normal de la inestabilidad (wander sinusoidal sobre el spot)
        c.pos.x = c.spot.x + Math.sin(t * c.w1 + c.fase) * 0.20;
        c.pos.y = c.spot.y + Math.sin(t * c.w2 + c.fase * 1.7) * 0.16;
        c.pos.z = c.spot.z + Math.cos(t * c.w1 * 0.8 + c.fase * 0.6) * 0.18;
        c.mesh.rotation.x += c.tumble.x * dt;
        c.mesh.rotation.y += c.tumble.y * dt;
      }
      // nunca atraviesan paredes ni salen del volumen jugable
      if (c.pos.x > B.x) { c.pos.x = B.x; if (c.vel.x > 0) c.vel.x *= -0.8; }
      if (c.pos.x < -B.x) { c.pos.x = -B.x; if (c.vel.x < 0) c.vel.x *= -0.8; }
      if (c.pos.y > B.yMax) { c.pos.y = B.yMax; if (c.vel.y > 0) c.vel.y *= -0.8; }
      if (c.pos.y < B.yMin) { c.pos.y = B.yMin; if (c.vel.y < 0) c.vel.y *= -0.8; }
      if (c.pos.z > B.zMax) { c.pos.z = B.zMax; if (c.vel.z > 0) c.vel.z *= -0.8; }
      if (c.pos.z < B.zMin) { c.pos.z = B.zMin; if (c.vel.z < 0) c.vel.z *= -0.8; }
    }
  }

  /* ---------------- perturbaciones ---------------- */
  _pertAleatoria() {
    const opts = ['g0', 'atractor', 'super'];
    let k = opts[(Math.random() * opts.length) | 0];
    if (k === this.pert) k = opts[(Math.random() * opts.length) | 0];   // una repetición se re-sorteo
    return k;
  }

  _pertAplica(kind, auto) {
    // seguridad lógica (spec §8): nada nuevo sin oleada activa y cubos vivos
    if (!this.waveActive || this.aliveCubes <= 0) return;
    this.pert = kind;
    for (const c of this.cubes) {
      if (!c.alive) continue;
      // la nueva perturbación SUSTITUYE a la anterior: sin fuerzas acumuladas
      c.vel.set((Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.3,
        (Math.random() - 0.5) * 0.4);
      c.wanderT = 0;
      c.thud = false;
      c.mesh.scale.setScalar(1);
    }
    const g = this.game;
    const nombre = kind === 'g0' ? 'GRAVEDAD 0'
      : kind === 'atractor' ? 'ATRACTOR' : 'SUPERGRAVEDAD';
    g.rules.message = tx('PERTURBACIÓN: ' + nombre, 'PERTURBATION: ' + nombre);
    try { g.audio.announce(nombre, true); } catch (e) { /* */ }
    g.audio.playOsc(220, 880, 0.30, 'sine', 0.12, 0);
    this._flash(this.core.position, 0xc9a6ff);
    this._hudKey = '';
    if (auto) { /* el disparo por diana NUNCA reinicia el temporizador de 30 s */ }
  }

  _cadenaDestruye(primero) {
    // ATRACTOR vigente en el impacto: UN golpe destruye TODOS los cubos vivos
    const g = this.game;
    let n = 0;
    for (const c of this.cubes) {
      if (!c.alive) continue;
      this._destruye(c, true);
      n++;
    }
    if (n > 1) {
      try { g.audio.playNoise(0.4, 500, 0.9, 0.2, 0); } catch (e) { /* */ }
      try { g.audio.playOsc(300, 60, 0.4, 'sawtooth', 0.2, 0); } catch (e) { /* */ }
    }
  }

  _destruye(c, silencioso) {
    if (!c.alive) return;
    c.alive = false;
    c.mesh.visible = false;
    this.aliveCubes--;
    this._fragmenta(c.pos);
    const g = this.game;
    if (!silencioso) {
      const pan = THREE.MathUtils.clamp(c.pos.x / 2.5, -1, 1);
      try { g.audio.playNoise(0.2, 700, 0.6, 0.15, pan); } catch (e) { /* */ }
      try { g.audio.playOsc(300, 90, 0.2, 'square', 0.14, pan); } catch (e) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 70);
    }
    this._hudKey = '';
    if (this.aliveCubes <= 0 && this.waveActive) this._oleadaCompleta();
  }

  /* ---------------- FX (fragmentos y flashes) ---------------- */
  _fragmenta(p) {
    let n = 0;
    for (const f of this.frags) {
      if (f.t < IMP_CFG.fragLife) continue;
      f.t = 0;
      f.mesh.visible = true;
      f.mesh.material.opacity = 1;
      f.mesh.scale.setScalar(1);
      f.mesh.position.copy(p);
      f.mesh.position.x += (Math.random() - 0.5) * 0.16;
      f.mesh.position.y += (Math.random() - 0.5) * 0.16;
      f.mesh.position.z += (Math.random() - 0.5) * 0.16;
      f.vel.set((Math.random() - 0.5) * 2.6, Math.random() * 2.2 + 0.6,
        (Math.random() - 0.5) * 2.6);
      if (++n >= 6) break;
    }
  }

  _flash(p, col) {
    for (const f of this.flashes) {
      if (f.t < 0.4) continue;
      f.t = 0;
      f.mesh.visible = true;
      f.mesh.material.color.setHex(col || 0x9fe8ff);
      f.mesh.material.opacity = 0.9;
      f.mesh.scale.setScalar(1);
      f.mesh.position.copy(p);
      f.mesh.lookAt(this.game.camera ? this.game.camera.getWorldPosition(this._tmpC)
        : this._tmpC.set(0, 1.6, 0.4));
      return;
    }
  }

  _fxStep(dt) {
    for (const f of this.frags) {
      if (f.t >= IMP_CFG.fragLife) { if (f.mesh.visible) f.mesh.visible = false; continue; }
      f.t += dt;
      f.vel.y -= 5.5 * dt;
      f.mesh.position.addScaledVector(f.vel, dt);
      f.mesh.rotation.x += 4 * dt; f.mesh.rotation.y += 3 * dt;
      const k = Math.max(0, 1 - f.t / IMP_CFG.fragLife);
      f.mesh.material.opacity = k;
      f.mesh.scale.setScalar(0.5 + 0.5 * k);
    }
    for (const f of this.flashes) {
      if (f.t >= 0.4) { if (f.mesh.visible) f.mesh.visible = false; continue; }
      f.t += dt;
      const k = Math.max(0, 1 - f.t / 0.4);
      f.mesh.material.opacity = 0.9 * k;
      f.mesh.scale.setScalar(1 + (1 - k) * 1.6);
    }
  }

  /* ---------------- dianas cuánticas (ciclo 1 s / 1 s) ---------------- */
  _dianaPosicion() {
    const B = IMP_CFG.bounds;
    let guard = 0;
    while (guard++ < 200) {
      const x = (Math.random() * 2 - 1) * (B.x + 0.1);
      const y = 0.95 + Math.random() * 1.15;
      const z = B.zMin + 0.3 + Math.random() * ((B.zMax - 0.3) - (B.zMin + 0.3));
      this._tmpA.set(x, y, z);
      if (this._tmpA.z > -1.05) continue;
      if (this._tmpA.distanceTo(this.core.position) < 1.15) continue;
      return this._tmpA.clone();
    }
    return new THREE.Vector3(1.4, 1.6, -2.6);
  }

  _dianasStep(dt) {
    const d = this.diana;
    if (!this.waveActive) { d.sp.visible = false; return; }
    d.t -= dt;
    if (d.fase === 'vis') {
      if (d.t <= 0) { d.fase = 'wait'; d.t = IMP_CFG.dianaWait; d.sp.visible = false; }
    } else if (d.t <= 0) {
      // nueva aparición en OTRA posición
      d.sp.position.copy(this._dianaPosicion());
      d.sp.visible = true;
      d.sp.material.rotation = 0;
      d.fase = 'vis';
      d.t = IMP_CFG.dianaVis;
      try { this.game.audio.playOsc(1180, 1560, 0.07, 'sine', 0.05, 0); } catch (e) { /* */ }
    }
  }

  laserTargets() {
    return (this.diana && this.diana.sp.visible) ? [this.diana.sp] : [];
  }

  /** El LÁSER acierta la diana: destello + perturbación (nunca destruye cubos). */
  _dianaHit(lp) {
    const d = this.diana;
    if (!d.sp.visible || d.fase !== 'vis') return false;   // diana ya desactivada: NO
    d.sp.visible = false;
    d.fase = 'wait';
    d.t = IMP_CFG.dianaWait;
    this._flash(lp, 0xbfe9ff);
    const g = this.game;
    try { g.audio.playOsc(1400, 2200, 0.12, 'sine', 0.14, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(600, 1500, 0.15, 'triangle', 0.1, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.4, 60);
    this._pertAplica(this._pertAleatoria(), false);
    return true;
  }

  /* ---------------- pelota: disponible → lanzada → reposición ---------------- */
  _ballDisponible(grace) {
    const g = this.game;
    this.ballState = 'hold';
    this.holdT = 0;
    this.graceT = grace == null ? IMP_CFG.graceT : grace;
    this.flight = 0;
    this._cdT = 0;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = true;
    if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
  }

  _baseTopY() { return IMP_CFG.baseY + 0.05; }

  _ballStep(dt) {
    const g = this.game;
    const ball = g.ball;
    if (this.ballState === 'respawn') {
      this.deadT -= dt;
      if (this.deadT <= 0) this._ballDisponible(IMP_CFG.graceT);
      return;
    }
    if (this.ballState === 'hold') {
      // física viva (la pala puede liberarla) + bote determinista sobre la base
      this._fisica(dt, true);
      if (this.ballState !== 'hold') return;    // liberada por la pala
      this.holdT += dt;
      if (this.graceT > 0) this.graceT -= dt;
      const pp = (this.holdT % IMP_CFG.ballT) / IMP_CFG.ballT;
      ball.pos.set(IMP_CFG.baseX,
        this._baseTopY() + (DIMS.ballRadius || 0.02) + 0.015 + 4 * IMP_CFG.ballH * pp * (1 - pp),
        IMP_CFG.baseZ);
      ball.vel.set(0, (4 * IMP_CFG.ballH * (1 - 2 * pp)) / IMP_CFG.ballT, 0);
      ball.spin.multiplyScalar(Math.max(0, 1 - dt * 2));
      if (ball.__exPrev) ball.__exPrev.copy(ball.pos);
      return;
    }
    // PLAY: gobernada por la física del juego, responde al impacto real de la pala
    this._fisica(dt, false);
  }

  /** Integración propia por SUBPASOS (sin mesa virtual: aquí no hay mesa).
   *  Golpeo de pala = bumper con la velocidad REAL de la pala (patrón
   *  REACTOR aprobado por el dueño): la dirección no se corrige a mano. */
  _fisica(dt, hold) {
    const g = this.game;
    const ball = g.ball;
    const r = DIMS.ballRadius || 0.02;
    const SUB = 4, h = dt / SUB;
    const R = this._room;
    if (this._cdT > 0) this._cdT -= dt;
    for (let s = 0; s < SUB; s++) {
      this._tmpA.copy(ball.pos);                     // prev
      ball.vel.y -= this._G() * h;
      ball.vel.multiplyScalar(1 - 0.012 * h);
      ball.pos.addScaledVector(ball.vel, h);
      this.flight += h;
      /* GOLPEO DE PALA (bumper esfera-esfera; en hold sólo tras la gracia) */
      this._paddleHit(hold && this.graceT > 0);
      if (this.ballState !== 'play' && !hold) break;
      /* CUBOS: colisión REAL por barrido del segmento prev→cur (no proximidad) */
      this._cubosCollide(this._tmpA, ball.pos, ball.vel, r);
      if (this.ballState === 'respawn') break;
      /* BASE FLOTANTE: superficie superior sólida que rebota */
      const bd = IMP_CFG.baseR + r;
      if (ball.vel.y < 0 &&
          Math.abs(ball.pos.x - IMP_CFG.baseX) < bd &&
          Math.abs(ball.pos.z - IMP_CFG.baseZ) < bd &&
          ball.pos.y - r <= this._baseTopY() + 0.004 &&
          ball.pos.y - r > this._baseTopY() - 0.12) {
        ball.pos.y = this._baseTopY() + r + 0.004;
        ball.vel.y = -ball.vel.y * 0.62;
        ball.vel.x *= 0.94; ball.vel.z *= 0.94;
        try { g.audio.playOsc(300, 260, 0.05, 'sine', 0.12, 0); } catch (e) { /* */ }
      }
      /* NÚCLEO: esfera sólida */
      this._tmpB.copy(ball.pos).sub(this.core.position);
      const rr0 = IMP_CFG.coreR + 0.06 + r;
      if (this._tmpB.lengthSq() < rr0 * rr0) {
        const n = this._tmpB.normalize();
        ball.pos.copy(this.core.position).addScaledVector(n, rr0 + 0.01);
        const into = ball.vel.dot(n);
        if (into < 0) ball.vel.addScaledVector(n, -2 * into).multiplyScalar(0.8);
      }
      /* SALA: paredes y techo sólidos; SUELO y pasado = pelota perdida */
      if (ball.pos.x > R.hx - 0.06 - r) { ball.pos.x = R.hx - 0.06 - r; if (ball.vel.x > 0) ball.vel.x *= -0.82; }
      if (ball.pos.x < -(R.hx - 0.06) + r) { ball.pos.x = -(R.hx - 0.06) + r; if (ball.vel.x < 0) ball.vel.x *= -0.82; }
      if (ball.pos.z < R.fz + 0.06 + r) { ball.pos.z = R.fz + 0.06 + r; if (ball.vel.z < 0) ball.vel.z *= -0.82; }
      if (ball.pos.z > R.bz - 0.06 - r) { ball.pos.z = R.bz - 0.06 - r; if (ball.vel.z > 0) ball.vel.z *= -0.82; }
      if (ball.pos.y > R.hh - 0.06 - r) { ball.pos.y = R.hh - 0.06 - r; if (ball.vel.y > 0) ball.vel.y *= -0.82; }
      if (ball.pos.y - r <= 0.03 && ball.vel.y < 0) { this._bolaPerdida(); break; }
      if (ball.pos.z > 1.6 && ball.vel.z > 0) { this._bolaPerdida(); break; }
      if (this.flight > 12) { this._bolaPerdida(); break; }
    }
  }

  _paddleHit(sinImpacto) {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (!ps || !ps.active || !ps.pos) return;
    if (sinImpacto || this._cdT > 0) return;
    const ball = g.ball;
    const rr = (DIMS.ballRadius || 0.02) + 0.085 + (ps.extraReach || 0);
    this._tmpB.copy(ball.pos).sub(ps.pos);
    if (this._tmpB.lengthSq() > rr * rr) return;
    if (this._tmpB.lengthSq() < 1e-6) this._tmpB.set(0, 0.3, 1);
    this._cdT = 0.25;
    const n = this._tmpB.normalize();
    const v = ball.vel;
    const into = v.dot(n);
    v.addScaledVector(n, -2 * Math.min(0, into)).multiplyScalar(0.42);
    if (ps.vel) v.addScaledVector(ps.vel, 0.85);      // la pala manda (mecánica real)
    const sp = v.length();
    if (sp < IMP_CFG.minBallOut) v.multiplyScalar(IMP_CFG.minBallOut / Math.max(sp, 0.01));
    else if (sp > IMP_CFG.maxBallOut) v.multiplyScalar(IMP_CFG.maxBallOut / sp);
    if (v.y < 0.35) v.y = 0.35 + Math.random() * 0.45;
    if (this.ballState === 'hold') {
      this.ballState = 'play';
      this.flight = 0;
      g.rules.message = tx('¡A por los cubos!', 'Go get the cubes!');
    }
    g.audio.playOsc(430, 620, 0.06, 'square', 0.2, 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.55, 70);
  }

  /** Colisión REAL pelota-cubo: barrido del segmento prev→cur por subpaso.
   *  Sólo con la pelota LANZADA (nunca en bote-en-espera): colisión válida. */
  _cubosCollide(prev, cur, vel, rB) {
    if (this.ballState !== 'play') return;
    const dx = cur.x - prev.x, dy = cur.y - prev.y, dz = cur.z - prev.z;
    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (dist <= 1e-9) return;
    for (const c of this.cubes) {
      if (!c.alive || c.spawnT < c.from0 * 0.85) continue;   // aún expulsándose: NO
      const rr = IMP_CFG.cubeHitR + rB;
      const mx = (cur.x + prev.x) * 0.5 - c.pos.x;
      const my = (cur.y + prev.y) * 0.5 - c.pos.y;
      const mz = (cur.z + prev.z) * 0.5 - c.pos.z;
      if (mx * mx + my * my + mz * mz > (rr + dist * 0.5) * (rr + dist * 0.5)) continue;
      const steps = Math.max(1, Math.ceil(dist / (IMP_CFG.cubeHitR * 0.5)));
      let hx = 0, hy = 0, hz = 0, hit = false;
      for (let s2 = 1; s2 <= steps; s2++) {
        const f = s2 / steps;
        const sx = prev.x + dx * f, sy = prev.y + dy * f, sz = prev.z + dz * f;
        const ex = sx - c.pos.x, ey = sy - c.pos.y, ez = sz - c.pos.z;
        if (ex * ex + ey * ey + ez * ez <= rr * rr) {
          hx = sx; hy = sy; hz = sz; hit = true; break;
        }
      }
      if (!hit) continue;
      // reflejo físico fuera del cubo
      this._tmpB.set(hx - c.pos.x, hy - c.pos.y, hz - c.pos.z);
      if (this._tmpB.lengthSq() < 1e-9) this._tmpB.set(0, 1, 0);
      this._tmpB.normalize();
      const sep = rr + 0.012;
      cur.copy(c.pos).addScaledVector(this._tmpB, sep);
      const into = vel.dot(this._tmpB);
      if (into < 0) vel.addScaledVector(this._tmpB, -2 * into).multiplyScalar(0.45);
      const sp = vel.length();
      if (sp > IMP_CFG.maxBallOut) vel.multiplyScalar(IMP_CFG.maxBallOut / sp);
      // ATRACTOR vigente + cubo agrupado → CADENA (un golpe, todos)
      if (this.pert === 'atractor') { this._cadenaDestruye(c); }
      else { this._destruye(c, false); }
      return;   // un cubo por subpaso
    }
  }

  _bolaPerdida() {
    const g = this.game;
    this.ballState = 'respawn';
    this.deadT = IMP_CFG.respawnT;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = false;
    try { g.audio.playNoise(0.16, 300, 0.3, 0.12, 0); } catch (e) { /* */ }
  }

  /* ---------------- final: victoria y derrota ---------------- */
  _finish(win, reason) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? 4.6 : 4.0;
    this.waveActive = false;
    this.pert = null;
    this.diana.sp.visible = false;
    // la pelota queda en reposo sobre la base
    this.ballState = 'hold';
    this.holdT = 0;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (win) {
      this._reactorEstado('estable');
      if (a._replay) {
        this._banner = { title: '¡REACTOR ESTABILIZADO!', sub: 'Rejugada terminada', col: '#7fb069' };
        try { g.audio.announce('Rejugada terminada', true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: '¡REACTOR ESTABILIZADO!',
          sub: 'Siguiente: ' + sig.name, col: '#7fb069',
        };
        try { g.audio.announce(this._banner.sub, true); } catch (e) { /* */ }
      }
      g.confettiBurst = 3;
      g.audio.fanfare(true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 130), 220);
      }
    } else {
      // DERROTA: el ASTRO se ríe FRENTE al jugador (única aparición de la prueba)
      if (a.rivalMesh) {
        a.rivalMesh.position.set(0, 1.075, -2.1);
        a.rivalMesh.visible = true;
        a.rivalEstado('laughing');
      }
      if (a._replay) {
        this._banner = { title: '¡SE ACABÓ EL TIEMPO!', sub: 'Rejugada terminada', col: '#e06c5a' };
      } else {
        this._banner = {
          title: '¡SE ACABÓ EL TIEMPO!',
          sub: 'Oleada ' + this.wave + ' · cubos restantes: ' + this.aliveCubes,
          col: '#e06c5a',
        };
        a._pruebaFin(false);
      }
      g.audio.fanfare(false);
      try { g.audio.announce(tx('Tiempo agotado', 'Time is up'), true); } catch (e) { /* */ }
    }
    this._hudKey = '';
  }

  _afterResult() {
    const a = this.ctrl;
    this.stop();
    a._despuesDePrueba();
  }

  /* ---------------- pantalla informativa (pantallainfo.png) ---------------- */
  _pantalla() {
    const cv = this.panCv, c = cv.getContext('2d');
    const sec = Math.max(0, Math.ceil(this.waveT));
    const enJuego = this.phase === 'play' && this._stableT <= 0;
    const key = [this.phase, this.wave, sec, this.aliveCubes,
      this.reactorState, this.pert, enJuego].join('|');
    if (key === this._hudKey) return;
    this._hudKey = key;
    c.clearRect(0, 0, 1024, 512);
    if (this._panImg) c.drawImage(this._panImg, 0, 0, 1024, 512);
    else {
      c.fillStyle = 'rgba(6,10,18,0.92)';
      c.fillRect(70, 60, 884, 392);
    }
    const banner = this._banner;
    if (banner && (this.phase === 'intro' || this.phase === 'result')) {
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillStyle = banner.col;
      c.font = '900 64px system-ui, sans-serif';
      c.fillText(banner.title, 512, 218);
      c.fillStyle = '#dfe6ec';
      c.font = '600 36px system-ui, sans-serif';
      c.fillText(banner.sub, 512, 296);
      this.panTex.needsUpdate = true;
      return;
    }
    const mm = Math.floor(sec / 60), ss = sec % 60;
    const tcol = sec <= 10 ? '#ff5a48' : sec <= 30 ? '#ffd257' : '#eef4ff';
    const nombrePert = this.pert === 'g0' ? 'GRAVEDAD 0'
      : this.pert === 'atractor' ? 'ATRACTOR'
        : this.pert === 'super' ? 'SUPERGRAVEDAD' : '—';
    c.textBaseline = 'middle';
    // cabecera
    c.textAlign = 'center';
    c.fillStyle = '#bfe9ff';
    c.font = '800 33px system-ui, sans-serif';
    c.fillText('REACTOR DE IMPULSO · ESTACIÓN ORBITAL', 512, 108);
    // bloque izquierdo: oleada y cubos
    c.textAlign = 'left';
    c.fillStyle = '#ffd257';
    c.font = '900 44px system-ui, sans-serif';
    c.fillText('PERTURBACIÓN ' + Math.max(1, this.wave), 118, 196);
    c.fillStyle = '#8fa3b8';
    c.font = '700 24px system-ui, sans-serif';
    c.fillText('CUBOS RESTANTES', 120, 268);
    c.fillStyle = '#ffffff';
    c.font = '900 58px system-ui, sans-serif';
    c.fillText(this.aliveCubes + ' / ' + (this.wave ? IMP_CFG.waves[this.wave - 1] : 0), 120, 336);
    // bloque central: tiempo
    c.textAlign = 'center';
    c.fillStyle = '#8fa3b8';
    c.font = '700 24px system-ui, sans-serif';
    c.fillText('TIEMPO', 512, 268);
    c.fillStyle = tcol;
    c.font = '900 64px ui-monospace, SFMono-Regular, Menlo, monospace';
    c.fillText(mm + ':' + (ss < 10 ? '0' : '') + ss, 512, 340);
    // bloque derecho: estado del reactor
    c.textAlign = 'right';
    c.fillStyle = this.reactorState === 'inestable' ? '#ff5a48' : '#5aa8ff';
    c.font = '900 40px system-ui, sans-serif';
    c.fillText(this.reactorState === 'inestable' ? 'REACTOR INESTABLE' : 'REACTOR ESTABLE', 906, 196);
    c.fillStyle = '#8fa3b8';
    c.font = '700 24px system-ui, sans-serif';
    c.fillText('PERTURBACIÓN ACTIVA', 906, 268);
    c.fillStyle = this.pert ? '#c9a6ff' : '#5f7186';
    c.font = '900 36px system-ui, sans-serif';
    c.fillText(nombrePert, 906, 336);
    // estado entre oleadas
    if (!enJuego && this.phase === 'play') {
      c.textAlign = 'center';
      c.fillStyle = '#7fb069';
      c.font = '800 30px system-ui, sans-serif';
      c.fillText('REACTOR ESTABLE · PREPARANDO SIGUIENTE OLEADA…', 512, 412);
    }
    this.panTex.needsUpdate = true;
  }
}

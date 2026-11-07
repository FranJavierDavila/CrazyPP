/* ============================================================================
 *  v3.3.0 · REACTOR DE ENERGÍA INESTABLE (etapa 2 del camino)
 *  ----------------------------------------------------------------------------
 *  Sustituye al MURO 1 (arkanoid) en la etapa 2. El dueño la describe así:
 *  «la pala se convierte en un instrumento para estabilizar el reactor de la
 *  nave. Un núcleo energético situado detrás de la mesa (nucleo_gravedad_lp
 *  .glb, con rotaciones caóticas sobre su propio centro) lanza esferas de
 *  plasma hacia el jugador. Este debe golpearlas con la pala y devolverlas a
 *  unas compuertas de energía que aparecen en diferentes posiciones
 *  alcanzables por los golpes de la pelota. Cada impacto correcto estabiliza
 *  el reactor. Los impactos fallidos provocan vibraciones, luces de alarma y
 *  cambios de gravedad. El astronauta se burla cuando fallas y se sorprende
 *  cuando encadenas varios aciertos. Progresión: primero una compuerta
 *  grande; después, varias pequeñas y móviles.»
 *
 *  Arquitectura (patrones de la casa):
 *  · ESFERA DE PLASMA propia (NO la bola real): proyectil único secuencial
 *    con física propia (gravedad variable por el modifier de gravedad),
 *    malla emisiva + glow sprite. La bola REAL queda aparcada (HOLD).
 *  · GOLPEO DE PALA: bumper esfera-vs-esfera con transferencia de velocidad
 *    de la pala (a 4-7 m/s y ≤8,3 ms por frame no hay túnel: 2 subpasos).
 *  · COMPUERTAS: anillo + película de energía; la estabilización es un
 *    CRUCE REAL del plano de la compuerta dentro del radio interior
 *    (segmento prev→pos por frame, como el Burla del núcleo).
 *  · FALLOS: alarma (flashes rojos de sala + halo rojo + zumbido + haptic)
 *    + modifier de gravedad de la PRÓXIMA esfera (pesada/ligera).
 *  · Expresiones del ASTRO: burla ('laughing') al fallar, sorpresa
 *    ('surprised') al encadenar 3 aciertos; base 'focused' durante el juego.
 *  · Progresión: FASE A = 1 compuerta GRANDE fija (3 estabilizaciones);
 *    FASE B = 2 compuertas PEQUEÑAS (una móvil) (5 estabilizaciones).
 *  · Regla Quest: TODOS los pools se crean una vez en el constructor; el
 *    GLB del núcleo se carga con pereza una sola vez (fallback procedural).
 *  ========================================================================== */
const REACTOR_CFG = {
  time: 150, lives: 5,
  objetivoA: 3, objetivoB: 5,          // 3 grandes + 5 pequeñas = 8
  coreY: 1.62, coreZ: -3.35,           // núcleo flotando tras el borde lejano
  coreScale: 0.92,
  sphereR: 0.045, paddleR: 0.085,
  gateRBig: 0.40, gateRSmall: 0.24,
  gateYBase: 1.28,                     // centro medio de compuertas
  launchT: [0.95, 1.25],               // tiempo de vuelo del lanzamiento
  launchCd: [2.6, 3.8],                // pausa entre esferas
  minOut: 2.7, maxOut: 7.2,            // velocidad tras el golpeo
  failGravChance: 0.75,                // prob. de modifier de gravedad al fallar
  /* Spots FIJOS de la FASE A (una compuerta grande, rota por estabilización) */
  spotsA: [
    { x: -0.45, y: 1.30, z: -1.05 },
    { x: 0.42, y: 1.48, z: -1.85 },
    { x: 0.00, y: 1.12, z: -2.35 },
    { x: -0.30, y: 1.55, z: -1.60 },
  ],
};

class ReactorInestable {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.inited = false;
    this.phase = 'idle';               // intro | play | result
    this.phaseT = 0;
    this.time = REACTOR_CFG.time;
    this.lives = REACTOR_CFG.lives;
    this.estabA = 0; this.estabB = 0;  // estabilizaciones por fase
    this.streak = 0;                   // aciertos encadenados (sorpresa del ASTRO)
    this.gravMod = 'normal';           // normal | pesada | ligera
    this._hudDirty = true;
    this._lastSec = -1;
    this._warn30 = false;
    this._banner = null;
    this._msg = ''; this._msgT = 0;
    this._launchCd = 2.2;
    this._sPrev = new THREE.Vector3();
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    this._exprHold = 0;                // retorno programado de la expresión
    this._coreArt = null; this._coreArtLoading = false;
    this._UP = new THREE.Vector3(0, 1, 0);   // reutilizado en _gateOrient
    this._jitterT = 0;                 // vibración del núcleo (alarma)
    this._haloPulse = 0;               // pulso cian del halo (acierto)
    this._alarmT = 0;                  // rojo de alarma restante
    this._flashT = [0, 0, 0];          // vida de cada flash de sala
    this._build();
  }

  /* ---------------- construcción (una sola vez) ---------------- */
  _build() {
    const g = this.game;
    this.group = new THREE.Group();
    g.rig.add(this.group);             // espacio de la mesa (convención v2.44)

    /* NÚCLEO: fallback procedural + GLB del artista con pereza */
    this.core = new THREE.Group();
    this.core.position.set(0, REACTOR_CFG.coreY, REACTOR_CFG.coreZ);
    const matNuc = new THREE.MeshStandardMaterial({
      color: 0x1a2436, roughness: 0.35, metalness: 0.55,
      emissive: 0x36d8ff, emissiveIntensity: 0.55,
    });
    this.coreBody = new THREE.Mesh(new THREE.SphereGeometry(0.30, 28, 20), matNuc);
    const matHalo = new THREE.MeshStandardMaterial({
      color: 0x0a1626, roughness: 0.5, metalness: 0.3,
      emissive: 0x4fd8ff, emissiveIntensity: 0.9, transparent: true, opacity: 0.85,
    });
    this.coreHalo = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.045, 12, 40), matHalo);
    this.coreHalo.rotation.x = Math.PI / 2;
    this.coreLight = new THREE.PointLight(0x66eaff, 0.9, 5.5, 2);
    this.core.add(this.coreBody, this.coreHalo, this.coreLight);
    this.core.visible = false;
    this.group.add(this.core);

    /* ESFERA DE PLASMA (una a la vez; pool de 1) */
    this.sphereMat = new THREE.MeshStandardMaterial({
      color: 0x36e0ff, roughness: 0.25, emissive: 0x36b8ff, emissiveIntensity: 1.6,
    });
    this.sphereMesh = new THREE.Mesh(
      new THREE.SphereGeometry(REACTOR_CFG.sphereR, 22, 16), this.sphereMat);
    this.sphereMesh.visible = false;
    this.group.add(this.sphereMesh);
    this.glowTex = this._texGlow();
    this.sphereGlow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.glowTex, color: 0x66eaff, transparent: true,
      opacity: 0.75, blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    this.sphereGlow.scale.setScalar(0.26);
    this.sphereGlow.visible = false;
    this.group.add(this.sphereGlow);

    /* COMPUERTAS (pool de 2: la B usa ambas) */
    this.gates = [];
    for (let i = 0; i < 2; i++) {
      const gate = { mesh: null, film: null, pos: new THREE.Vector3(), yaw: 0,
        q: new THREE.Quaternion(), qi: new THREE.Quaternion(),
        base: new THREE.Vector3(), ax: 0, ay: 0, w1: 0, w2: 0,
        rIn: REACTOR_CFG.gateRBig, on: false, moving: false, t: Math.random() * 6 };
      const grp = new THREE.Group();
      gate.meshMat = new THREE.MeshStandardMaterial({
        color: 0x123244, roughness: 0.4, metalness: 0.6,
        emissive: 0x4fd8ff, emissiveIntensity: 1.1,
      });
      gate.mesh = new THREE.Mesh(new THREE.TorusGeometry(1, 0.05, 10, 44), gate.meshMat);
      gate.filmMat = new THREE.MeshBasicMaterial({
        map: this.glowTex, color: 0x36d8ff, transparent: true, opacity: 0.28,
        blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
      });
      gate.film = new THREE.Mesh(new THREE.CircleGeometry(1, 36), gate.filmMat);
      grp.add(gate.mesh, gate.film);
      grp.visible = false;
      gate.grp = grp;
      this.group.add(grp);
      this.gates.push(gate);
    }

    /* FLASHES DE ALARMA (3 planos aditivos en la sala) */
    this.alarmSpots = [
      new THREE.Vector3(-2.4, 2.0, -4.0),
      new THREE.Vector3(2.4, 2.0, -4.0),
      new THREE.Vector3(0, 2.5, -4.8),
    ];
    this.flashes = this.alarmSpots.map((p) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.6),
        new THREE.MeshBasicMaterial({
          map: this.glowTex, color: 0xff4030, transparent: true, opacity: 0,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }));
      m.position.copy(p);
      m.visible = false;
      this.group.add(m);
      return m;
    });

    /* HUD (canvas 1024×214, mismo patrón que el muro) */
    this.hudCv = document.createElement('canvas');
    this.hudCv.width = 1024; this.hudCv.height = 214;
    this.hudTex = this.ctrl._ct(this.hudCv);
    this.hudGroup = new THREE.Group();
    this.hudMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1.9, 0.397),
      new THREE.MeshBasicMaterial({ map: this.hudTex, transparent: true }));
    this.hudGroup.add(this.hudMesh);
    this.hudGroup.position.set(0, 2.56, REACTOR_CFG.coreZ + 0.55);
    this.hudGroup.visible = false;
    this.group.add(this.hudGroup);
  }

  _texGlow() {
    const cv = document.createElement('canvas');
    cv.width = 128; cv.height = 128;
    const c = cv.getContext('2d');
    const gr = c.createRadialGradient(64, 64, 2, 64, 64, 62);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.35, 'rgba(140,235,255,0.55)');
    gr.addColorStop(1, 'rgba(140,235,255,0)');
    c.fillStyle = gr; c.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this.ctrl._ownTex.add(t);
    return t;
  }

  /* ---------------- arte del núcleo (GLB con pereza) ---------------- */
  _ensureCoreArt() {
    if (this._coreArt || this._coreArtLoading) return;
    this._coreArtLoading = true;
    try {
      const url = this.ctrl._A('nucleo_gravedad_lp.glb');
      new GLTFLoader().load(url, (gltf) => {
        try { this._mountCoreArt(gltf.scene); }
        catch (e) { console.warn('[estacion] núcleo: montaje KO', e); }
        this._coreArtLoading = false;
      }, undefined, () => {
        console.warn('[estacion] nucleo_gravedad_lp.glb no disponible — fallback procedural');
        this._coreArtLoading = false;
      });
    } catch (e) { this._coreArtLoading = false; }
  }
  _mountCoreArt(root) {
    const box = new THREE.Box3().setFromObject(root);
    const size = box.getSize(new THREE.Vector3());
    const s = size.y > 0.001 ? (REACTOR_CFG.coreScale / size.y) : 1;
    root.scale.setScalar(s);
    box.setFromObject(root);
    const ctr = box.getCenter(new THREE.Vector3());
    root.position.sub(ctr);              // centrado en su propio eje (rota sobre sí)
    root.traverse((o) => {
      if (o.isMesh && o.material) {
        o.material.emissive = new THREE.Color(0x36d8ff);
        o.material.emissiveIntensity = 0.7;
      }
    });
    this.core.remove(this.coreBody, this.coreHalo);
    this.coreBody = null; this.coreHalo = null;
    this.core.add(root);
    this._coreArt = root;
    console.info('[estacion] nucleo_gravedad_lp.glb montado (REACTOR)');
  }

  /* ---------------- ciclo de vida ---------------- */
  start() {
    if (this.active) return;
    this._ensureCoreArt();
    this.active = true;
    this.phase = 'intro';
    this.phaseT = 3.0;
    this.time = REACTOR_CFG.time;
    this._lastSec = Math.ceil(this.time) + 1;
    this._warn30 = false;
    this.lives = REACTOR_CFG.lives;
    this.estabA = 0; this.estabB = 0;
    this.streak = 0;
    this.gravMod = 'normal';
    this._launchCd = 2.0;
    this._banner = {
      title: 'REACTOR INESTABLE',
      sub: 'Estabiliza el núcleo · 8 compuertas',
      col: '#ffd257',
    };
    this._msg = ''; this._msgT = 0;
    this._hudDirty = true;
    const g = this.game;
    this.core.visible = true;
    this.core.position.set(0, REACTOR_CFG.coreY, REACTOR_CFG.coreZ);
    this.coreLight.intensity = 0.9;
    this.coreLight.color.setHex(0x66eaff);
    this._sphereOff();
    this._gateSetup(0);
    g.tableGroup.visible = true;         // la mesa sigue (las compuertas la superan)
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.ballMesh.scale.setScalar(1);
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ball.ignoreNet = true;             // la esfera de plasma ignora la red; la real, aparcada
    if (this.ctrl.rivalMesh) this.ctrl.rivalMesh.visible = true;   // el ASTRO REACCIONA
    if (this.ctrl.cartel) this.ctrl.cartel.visible = false;
    if (this.ctrl.powerSign) this.ctrl.powerSign.visible = false;
    g.rules.state = 'arkanoid';          // estado genérico de PRUEBA (el árbitro duerme)
    g.rules.message = 'REACTOR DE ENERGÍA INESTABLE';
    this.ctrl.rivalEstado('idle');
    this.hudGroup.visible = true;
    this.group.visible = true;
    g.audio.playOsc(392, 392, 0.12, 'square', 0.11, 0);
    window.setTimeout(() => g.audio.playOsc(523, 523, 0.12, 'square', 0.11, 0), 140);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.2, 'square', 0.12, 0), 280);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    this.hudGroup.visible = true;
    this._hudDirty = true;
  }

  stop() {
    this.active = false;
    this.phase = 'idle';
    if (!this.group) return;
    const g = this.game;
    this.core.visible = false;
    this._sphereOff();
    for (const gate of this.gates) { gate.on = false; gate.grp.visible = false; }
    for (const f of this.flashes) { f.visible = false; f.material.opacity = 0; }
    this.hudGroup.visible = false;
    this._alarmT = 0; this._haloPulse = 0; this._jitterT = 0;
    this._exprHold = 0;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ball.ignoreNet = false;
    g.ballMesh.scale.setScalar(1);
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (this.ctrl.rivalMesh) this.ctrl.rivalMesh.visible = true;
  }

  /* ---------------- bucle de la prueba ---------------- */
  step(dt) {
    if (!this.active) return;
    const g = this.game;
    this.inited = true;
    if (this.phase === 'intro') {
      this.phaseT -= dt;
      this._parkBall();
      this._anims(dt, 0);
      if (this.phaseT <= 0) {
        this.phase = 'play';
        this._msg = 'Estabiliza 8 compuertas';
        this._msgT = 2.6;
        this._hudDirty = true;
      }
      if (this._hudDirty) this._hud();
      return;
    }
    if (this.phase === 'play') {
      this.time -= dt;
      if (this.time <= 0) { this.time = 0; this._hudDirty = true; this._finish(false, 'time'); return; }
      const sec = Math.ceil(this.time);
      if (sec !== this._lastSec) {
        this._lastSec = sec;
        this._hudDirty = true;
        if (sec <= 30 && !this._warn30) {
          this._warn30 = true;
          g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0);
          window.setTimeout(() => g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0), 190);
        }
        if (sec <= 10 && sec >= 1) {
          g.audio.playOsc(980, 620, 0.16, 'sawtooth', 0.2, 0);
          if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 60);
        }
      }
      this._parkBall();
      this._updateGates(dt);
      if (this.sphereOn) this._spherePhysics(dt);
      else {
        this._launchCd -= dt;
        if (this._launchCd <= 0) this._launch();
      }
      if (!this.active) return;          // pudo terminar dentro
      this._anims(dt, dt);
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      this._anims(dt, 0);
      if (this.phaseT <= 0) { this._afterResult(); return; }
    }
    if (this._msgT > 0) {
      this._msgT -= dt;
      if (this._msgT <= 0) { this._msg = ''; this._hudDirty = true; }
    }
    if (this._exprHold > 0) {
      this._exprHold -= dt;
      if (this._exprHold <= 0) this.ctrl.rivalEstado('focused');
    }
    if (this._hudDirty) this._hud();
  }

  _parkBall() {
    const g = this.game;
    g.ball.pos.set(HOLD.x, HOLD.T, HOLD.z);
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
  }

  /* ---------------- lanzamiento del núcleo ---------------- */
  _launch() {
    const g = this.game;
    const C = REACTOR_CFG;
    const st = this.stageFactor();
    this.sphereOn = true;
    this.sphereHits = 0;
    this.sphereBounces = 0;
    this.sphereT = 0;
    // DIMS.gravity del núcleo es NEGATIVO (−9,81, convención +y arriba):
    // trabajamos con su MAGNITUD (positive-down) para el arco balístico
    this.sphereG = Math.abs(DIMS.gravity || 9.6) * (this.gravMod === 'pesada' ? 1.45
      : this.gravMod === 'ligera' ? 0.55 : 1);
    const tint = this.gravMod === 'pesada' ? 0xff8a3c
      : this.gravMod === 'ligera' ? 0xc06cff : 0x36e0ff;
    this.sphereMat.color.setHex(tint);
    this.sphereMat.emissive.setHex(tint);
    this.sphereMesh.visible = true;
    this.sphereGlow.visible = true;
    this.sphereGlow.material.color.setHex(tint);
    const oy = C.coreY - 0.42, oz = C.coreZ + 0.30;
    const tx = (Math.random() * 1.1 - 0.55) * (0.85 + st * 0.15);
    const tz = -0.85 + Math.random() * 0.9;
    const ty = DIMS.tableTopY + 0.28 + Math.random() * 0.25;
    const T = C.launchT[0] + Math.random() * (C.launchT[1] - C.launchT[0]);
    this.spherePos = this.spherePos || new THREE.Vector3();
    this.sphereVel = this.sphereVel || new THREE.Vector3();
    this.spherePos.set(0, oy, oz);
    this.sphereVel.set((tx - 0) / T, (ty - oy) / T + 0.5 * this.sphereG * T, (tz - oz) / T);
    this._sPrev.copy(this.spherePos);
    this._launchCd = 0;
    g.audio.playOsc(180, 320, 0.18, 'sawtooth', 0.14, 0);
    this.coreLight.intensity = 2.0;
    this._msg = this.gravMod === 'normal' ? '' :
      (this.gravMod === 'pesada' ? 'GRAVEDAD PESADA' : 'GRAVEDAD LIGERA');
    this._msgT = this._msg ? 2.2 : 0;
    this._hudDirty = true;
  }

  _sphereOff() {
    this.sphereOn = false;
    if (this.sphereMesh) this.sphereMesh.visible = false;
    if (this.sphereGlow) this.sphereGlow.visible = false;
  }

  stageFactor() {
    return (this.estabA >= REACTOR_CFG.objetivoA) ? 1 : 0;   // 0 = fase A, 1 = fase B
  }

  /* ---------------- física de la esfera de plasma ---------------- */
  _spherePhysics(dt) {
    const g = this.game;
    const C = REACTOR_CFG;
    const p = this.spherePos, v = this.sphereVel;
    const r = C.sphereR;
    const SUB = 2, h = dt / SUB;
    for (let s = 0; s < SUB && this.sphereOn; s++) {
      this._sPrev.copy(p);
      v.y -= this.sphereG * h;
      v.multiplyScalar(1 - 0.05 * h);    // arrastre aerodinámico suave
      p.addScaledVector(v, h);
      this.sphereT += h;
      if (this._cdT > 0) this._cdT -= h;
      /* GOLPEO DE PALA (bumper con transferencia de velocidad) */
      this._paddleCollide();
      if (!this.sphereOn) break;
      /* MESA: la esfera sin golpear que toca la mesa = fallo; golpeda bota UNA vez */
      const dentroMesa = Math.abs(p.x) <= DIMS.tableHalfWidth + r &&
        p.z >= DIMS.tableCenterZ - DIMS.tableHalfLength - r &&
        p.z <= DIMS.tableCenterZ + DIMS.tableHalfLength + r;
      if (dentroMesa && p.y - r <= DIMS.tableTopY + 0.004 && v.y < 0) {
        if (this.sphereHits === 0 || this.sphereBounces >= 1) { this._falla('mesa'); break; }
        this.sphereBounces++;
        p.y = DIMS.tableTopY + r + 0.004;
        v.y = -v.y * 0.55; v.x *= 0.92; v.z *= 0.92;
        g.audio.playOsc(240, 200, 0.05, 'sine', 0.16, 0);
      }
      /* SUELO = fallo */
      if (p.y - r <= 0.03) { this._falla('suelo'); break; }
      /* Se le pasa al jugador = fallo */
      if (p.z > 0.85 && v.z > 0) { this._falla('pasada'); break; }
      /* Antiatasco */
      if (v.length() < 0.5 && p.y < (DIMS.netTopY || 0.9125) + 0.35) {
        this._stuckT = (this._stuckT || 0) + h;
        if (this._stuckT > 1.4) { this._stuckT = 0; this._falla('parada'); break; }
      } else this._stuckT = 0;
      /* COMPUERTAS: cruce real del plano dentro del anillo */
      this._gatesCheck(this._sPrev, p);
      if (!this.sphereOn) break;
      if (this.sphereT > 14) { this._falla('tiempo'); break; }
    }
    if (this.sphereOn) {
      this.sphereMesh.position.copy(p);
      this.sphereGlow.position.copy(p);
      this.sphereGlow.material.opacity = 0.62 + Math.sin(this.sphereT * 9) * 0.16;
    }
  }

  _paddleCollide() {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (!ps || !ps.active || !ps.pos) return;
    const p = this.spherePos, v = this.sphereVel;
    const rr = REACTOR_CFG.sphereR + REACTOR_CFG.paddleR + (ps.extraReach || 0);
    this._tmpA.copy(p).sub(ps.pos);
    if (this._tmpA.lengthSq() > rr * rr) return;
    if (this._cdT > 0) return;           // anti-rebote del mismo contacto
    if (this._tmpA.lengthSq() < 1e-6) this._tmpA.set(0, 0.3, 1);
    this._cdT = 0.25;
    const n = this._tmpA.normalize();
    /* reflejo + velocidad de la pala (la pala manda, como en el rally) */
    const into = v.dot(n);
    this._tmpB.copy(n).multiplyScalar(-2 * Math.min(0, into));
    v.add(this._tmpB).multiplyScalar(0.42);
    if (ps.vel) v.addScaledVector(ps.vel, 0.85);
    const sp = v.length();
    if (sp < REACTOR_CFG.minOut) v.multiplyScalar(REACTOR_CFG.minOut / Math.max(sp, 0.01));
    else if (sp > REACTOR_CFG.maxOut) v.multiplyScalar(REACTOR_CFG.maxOut / sp);
    if (v.y < 0.4) v.y = 0.4 + Math.random() * 0.5;   // arco jugable
    this.sphereHits++;
    this.sphereBounces = 0;
    const g2 = this.game;
    g2.audio.playOsc(430, 620, 0.06, 'square', 0.2, 0);
    if (g2.renderer.xr.isPresenting) g2.haptic(g2.paddleHand, 0.55, 70);
  }

  /* ---------------- compuertas ---------------- */
  _gateSetup(mode) {
    // mode 0 = fase A (1 grande fija) · mode 1 = fase B (2 pequeñas, 1 móvil)
    const faseB = mode === 1;
    for (let i = 0; i < this.gates.length; i++) {
      const gate = this.gates[i];
      if (!faseB && i === 1) { gate.on = false; gate.grp.visible = false; continue; }
      gate.rIn = faseB ? REACTOR_CFG.gateRSmall : REACTOR_CFG.gateRBig;
      gate.moving = faseB && i === 1;
      if (faseB) {
        gate.base.set(
          (Math.random() * 1.1 - 0.55),
          1.02 + Math.random() * 0.55,
          -2.45 + Math.random() * 1.75);
        gate.ax = gate.moving ? 0.26 + Math.random() * 0.18 : 0;
        gate.ay = gate.moving ? 0.10 + Math.random() * 0.10 : 0;
        gate.w1 = 0.55 + Math.random() * 0.4;
        gate.w2 = 0.7 + Math.random() * 0.5;
      } else {
        const sp = REACTOR_CFG.spotsA[this.estabA % REACTOR_CFG.spotsA.length];
        gate.base.set(sp.x, sp.y, sp.z);
        gate.ax = 0; gate.ay = 0;
      }
      gate.t = Math.random() * 6;
      gate.on = true;
      gate.mesh.scale.setScalar(gate.rIn);
      gate.film.scale.setScalar(gate.rIn);
      gate.meshMat.color.setHex(faseB ? 0x5a2a12 : 0x123244);
      gate.meshMat.emissive.setHex(faseB ? 0xffa840 : 0x4fd8ff);
      gate.filmMat.color.setHex(faseB ? 0xffb050 : 0x36d8ff);
      gate.grp.visible = true;
      this._gateOrient(gate);
    }
  }
  _gateOrient(gate) {
    gate.pos.copy(gate.base);
    if (gate.moving) {
      gate.pos.x += Math.sin(gate.t * gate.w1) * gate.ax;
      gate.pos.y += Math.sin(gate.t * gate.w2) * gate.ay;
    }
    gate.yaw = Math.atan2(gate.pos.x - 0, gate.pos.z - 0.55);
    gate.q.setFromAxisAngle(this._UP, gate.yaw);
    gate.qi.copy(gate.q).invert();
    gate.grp.position.copy(gate.pos);
    gate.grp.quaternion.copy(gate.q);
  }
  _updateGates(dt) {
    for (const gate of this.gates) {
      if (!gate.on) continue;
      gate.t += dt;
      this._gateOrient(gate);
      const pulse = 1 + Math.sin(gate.t * 3.1) * 0.05;
      gate.mesh.scale.setScalar(gate.rIn * pulse);
      gate.filmMat.opacity = 0.24 + Math.sin(gate.t * 3.1) * 0.10;
    }
  }
  _gatesCheck(prev, cur) {
    if (this.sphereHits < 1) return;     // sin golpeo previo no hay devolución
    for (const gate of this.gates) {
      if (!gate.on) continue;
      this._tmpA.copy(prev).sub(gate.pos).applyQuaternion(gate.qi);
      this._tmpB.copy(cur).sub(gate.pos).applyQuaternion(gate.qi);
      if (this._tmpA.z <= 0 || this._tmpB.z > 0) continue;   // cruce frontal
      const k = this._tmpA.z / (this._tmpA.z - this._tmpB.z);
      const lx = this._tmpA.x + (this._tmpB.x - this._tmpA.x) * k;
      const ly = this._tmpA.y + (this._tmpB.y - this._tmpA.y) * k;
      if (Math.sqrt(lx * lx + ly * ly) <= gate.rIn) { this._estabiliza(gate); return; }
    }
  }

  /* ---------------- acierto y fallo ---------------- */
  _estabiliza(gate) {
    const g = this.game;
    const C = REACTOR_CFG;
    const faseB = this.stageFactor() === 1;
    if (faseB) this.estabB++; else this.estabA++;
    this.streak++;
    const total = this.estabA + this.estabB;
    this._sphereOff();
    this.gravMod = 'normal';             // el acierto re-estabiliza la gravedad
    g.audio.playOsc(660, 990, 0.1, 'square', 0.18, 0);
    window.setTimeout(() => g.audio.playOsc(880, 1320, 0.14, 'square', 0.16, 0), 110);
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 0.7, 90);
      window.setTimeout(() => g.haptic(g.paddleHand, 0.4, 80), 150);
    }
    this._haloPulse = 1.0;
    this.coreLight.color.setHex(0x66eaff);
    this.coreLight.intensity = 2.4;
    this._msg = '¡COMPUERTA ESTABILIZADA! ' + total + '/8';
    this._msgT = 2.0;
    this._hudDirty = true;
    if (!faseB && this.estabA >= C.objetivoA) {
      this._gateSetup(1);
      this._msg = '¡FASE 2! Compuertas pequeñas y móviles';
      this._msgT = 3.0;
    } else {
      this._gateSetup(this.stageFactor());
    }
    if (this.streak >= 3 && (this.streak % 3 === 0)) {
      this.ctrl._exprSet('surprised', 2.2);   // se sorprende con la racha
      this._exprHold = 2.2;
    }
    if (total >= C.objetivoA + C.objetivoB) { this._finish(true); return; }
    this._launchCd = C.launchCd[0] + Math.random() * (C.launchCd[1] - C.launchCd[0]);
  }

  _falla(reason) {
    const g = this.game;
    this._sphereOff();
    this.lives--;
    this.streak = 0;
    this._hudDirty = true;
    /* modifier de gravedad para la PRÓXIMA esfera */
    if (Math.random() < REACTOR_CFG.failGravChance) {
      this.gravMod = Math.random() < 0.6 ? 'pesada' : 'ligera';
    } else this.gravMod = 'normal';
    /* ALARMA: flashes de sala + halo rojo + zumbido + haptics */
    this._alarmT = 1.25;
    this._jitterT = 0.8;
    for (let i = 0; i < this._flashT.length; i++) this._flashT[i] = 0.01 + i * 0.06;
    this.coreLight.color.setHex(0xff4030);
    this.coreLight.intensity = 2.6;
    g.audio.playOsc(320, 140, 0.32, 'sawtooth', 0.22, 0);
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 0.8, 180);
      if (g.ballHand !== g.paddleHand) g.haptic(g.ballHand, 0.5, 140);
    }
    /* el ASTRO SE BURLA */
    this.ctrl._exprSet('laughing', 2.4);
    this._exprHold = 2.4;
    this._msg = reason === 'mesa' ? '¡FALLO! Esfera perdida en la mesa'
      : reason === 'pasada' ? '¡FALLO! Se te pasó'
      : reason === 'parada' ? '¡FALLO! Esfera apagada'
      : '¡FALLO! ' + (this.gravMod === 'pesada' ? 'GRAVEDAD PESADA'
        : this.gravMod === 'ligera' ? 'GRAVEDAD LIGERA' : 'Inestabilidad');
    this._msgT = 2.4;
    if (this.lives <= 0) { this._finish(false, 'estabilidad'); return; }
    this._launchCd = REACTOR_CFG.launchCd[0] + Math.random() * (REACTOR_CFG.launchCd[1] - REACTOR_CFG.launchCd[0]);
  }

  /* ---------------- animaciones ---------------- */
  _anims(dt, playDt) {
    const t = this._t = (this._t || 0) + dt;
    /* rotación CAÓTICA del núcleo sobre su propio centro */
    const calm = this._haloPulse > 0 ? 0.45 : 1;
    this.core.rotation.x += (0.55 + Math.sin(t * 1.7) * 0.5 + Math.sin(t * 4.3) * 0.22) * dt * calm;
    this.core.rotation.y += (0.85 + Math.sin(t * 2.3) * 0.65) * dt * calm;
    this.core.rotation.z += (0.30 + Math.sin(t * 3.1) * 0.45) * dt * calm;
    /* vibración por alarma */
    if (this._jitterT > 0) {
      this._jitterT -= dt;
      const j = Math.min(1, this._jitterT / 0.8) * 0.022;
      this.core.position.set(
        (Math.random() - 0.5) * 2 * j,
        REACTOR_CFG.coreY + (Math.random() - 0.5) * 2 * j,
        REACTOR_CFG.coreZ + (Math.random() - 0.5) * 2 * j);
    } else {
      this.core.position.y = REACTOR_CFG.coreY + Math.sin(t * 1.1) * 0.03;
      this.core.position.x = 0;
      this.core.position.z = REACTOR_CFG.coreZ;
    }
    /* halo: pulso cian de acierto o rojo de alarma */
    if (this._haloPulse > 0) {
      this._haloPulse -= dt;
      if (this._haloPulse <= 0) this.coreLight.intensity = 0.9;
      else this.coreLight.intensity = 1.6 + this._haloPulse * 1.6;
    }
    if (this._alarmT > 0) {
      this._alarmT -= dt;
      const k = Math.max(0, this._alarmT / 1.25);
      this.coreLight.color.setHex(Math.sin(t * 22) > 0 ? 0xff4030 : 0x661410);
      if (this._alarmT <= 0) { this.coreLight.color.setHex(0x66eaff); this.coreLight.intensity = 0.9; }
      for (let i = 0; i < this.flashes.length; i++) {
        const f = this.flashes[i];
        if (this._flashT[i] > 0) {
          this._flashT[i] += dt;
          const kk = this._flashT[i] / 0.5;
          if (kk >= 1) { this._flashT[i] = 0; f.visible = false; continue; }
          f.visible = true;
          f.material.opacity = 0.5 * (1 - kk) * k;
          f.scale.setScalar(0.8 + kk * 0.9);
        }
      }
    } else {
      for (const f of this.flashes) f.visible = false;
    }
  }

  /* ---------------- fin ---------------- */
  _finish(win, reason) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? 4.4 : 3.6;
    this._sphereOff();
    for (const gate of this.gates) { gate.on = false; gate.grp.visible = false; }
    if (win) {
      if (a._replay) {
        this._banner = { title: '¡REACTOR ESTABLE!', sub: 'Rejugada terminada', col: '#7fb069' };
        try { g.audio.announce('Rejugada terminada', true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: '¡REACTOR ESTABLE!',
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
      this.ctrl._exprSet('derrotado', 3.0);
      this._exprHold = 3.0;
    } else {
      if (a._replay) {
        this._banner = { title: reason === 'time' ? '¡SE ACABÓ EL TIEMPO!' : 'REACTOR FUNDIDO',
          sub: 'Rejugada terminada', col: '#e06c5a' };
      } else {
        this._banner = {
          title: reason === 'time' ? '¡SE ACABÓ EL TIEMPO!' : 'REACTOR FUNDIDO',
          sub: 'La prueba se repite: vuelve a intentarlo cuando quieras', col: '#e06c5a',
        };
        a._pruebaFin(false);
      }
      g.audio.fanfare(false);
      this.ctrl._exprSet('triunfante', 3.0);
      this._exprHold = 3.0;
    }
    this._hudDirty = true;
  }

  _afterResult() {
    const a = this.ctrl;
    this.stop();
    a._despuesDePrueba();
  }

  /* ---------------- HUD ---------------- */
  _hud() {
    this._hudDirty = false;
    const cv = this.hudCv, c = cv.getContext('2d');
    const W = 1024, H = 214;
    c.clearRect(0, 0, W, H);
    c.fillStyle = 'rgba(8,14,30,0.92)';
    c.strokeStyle = 'rgba(90,220,255,0.9)';
    c.lineWidth = 7;
    c.beginPath();
    const rr = 30;
    c.moveTo(rr, 6); c.arcTo(W - 6, 6, W - 6, H - 6, rr);
    c.arcTo(W - 6, H - 6, 6, H - 6, rr);
    c.arcTo(6, H - 6, 6, 6, rr);
    c.arcTo(6, 6, W - 6, 6, rr);
    c.closePath(); c.fill(); c.stroke();
    const banner = this._banner;
    if (banner && (this.phase === 'intro' || this.phase === 'result')) {
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillStyle = banner.col;
      c.font = '900 72px system-ui, sans-serif';
      c.fillText(banner.title, 512, this.phase === 'intro' ? 84 : 80);
      c.fillStyle = '#dfe6ec';
      c.font = '600 40px system-ui, sans-serif';
      c.fillText(banner.sub, 512, this.phase === 'intro' ? 158 : 154);
      this.hudTex.needsUpdate = true;
      return;
    }
    const sec = Math.max(0, Math.ceil(this.time));
    const mm = Math.floor(sec / 60), ss = sec % 60;
    const tcol = sec <= 10 ? '#ff5a48' : sec <= 30 ? '#ffd257' : '#eef2f6';
    c.textAlign = 'left'; c.textBaseline = 'middle';
    c.fillStyle = tcol;
    c.font = '900 86px ui-monospace, SFMono-Regular, Menlo, monospace';
    c.fillText(mm + ':' + (ss < 10 ? '0' : '') + ss, 56, 104);
    c.fillStyle = '#9aa7b4';
    c.font = '700 26px system-ui, sans-serif';
    c.fillText('TIEMPO', 58, 172);
    c.textAlign = 'center';
    c.fillStyle = '#eef2f6';
    c.font = '800 52px system-ui, sans-serif';
    c.fillText((this.estabA + this.estabB) + ' / 8', 512, 96);
    c.fillStyle = '#9aa7b4';
    c.font = '700 26px system-ui, sans-serif';
    c.fillText('COMPUERTAS ESTABILIZADAS', 512, 166);
    c.textAlign = 'right';
    const full = REACTOR_CFG.lives;
    let dots = '';
    for (let i = 0; i < full; i++) dots += i < Math.max(0, this.lives) ? '\u25CF ' : '\u25CB ';
    c.fillStyle = this.lives <= 1 ? '#ff5a48' : '#7fb069';
    c.font = '800 46px system-ui, sans-serif';
    c.fillText(dots.trim(), 972, 96);
    c.fillStyle = '#9aa7b4';
    c.font = '700 26px system-ui, sans-serif';
    c.fillText('ESTABILIDAD', 970, 166);
    if (this.gravMod !== 'normal') {
      c.fillStyle = this.gravMod === 'pesada' ? '#ff8a3c' : '#c06cff';
      c.font = '800 34px system-ui, sans-serif';
      c.fillText(this.gravMod === 'pesada' ? 'GRAVEDAD PESADA' : 'GRAVEDAD LIGERA', 968, 44);
    }
    if (this._msg) {
      c.textAlign = 'center';
      c.fillStyle = '#ffd257';
      c.font = '800 40px system-ui, sans-serif';
      c.fillText(this._msg, 512, 40);
    }
    this.hudTex.needsUpdate = true;
  }
}

/* ============================================================================
 *  v3.5.0-ESC1 · ESCUDO DE PALA · DEFENSA DEL CASCO — NUEVA ETAPA 4 del
 *  campeonato Estación Orbital (especificación completa del dueño, borrador
 *  v1.0 «Escudo de Pala · Defensa del Casco»).
 *  ----------------------------------------------------------------------------
 *  Drones piratas han perforado el casco y abordan la cubierta de defensa.
 *  La pala es un ESCUDO MANUAL de energía: devuelve los ORBES DE PLASMA
 *  enemigos contra los drones y, al final, contra los cañones de la nave
 *  abordadora. Mecánica REACTIVA (se opone a la etapa del reactor, que es
 *  proactiva): sin pelota propia, sin base, sin pistola, sin dianas, sin
 *  cubos ni perturbaciones; la derrota llega por INTEGRIDAD DEL CASCO.
 *    · SALA PROPIA de 6 imágenes (arte propio v3.5.0 en escudo_pala/) sobre
 *      un volumen de 10 m ancho × 14 m fondo × 6 m alto; SIN mesa, SIN
 *      pelota estática, SIN rival (sólo en la derrota, astro_laughing).
 *    · FRENTE: brecha con campo de contención y flota pirata; en la fase 3
 *      se acopla la NAVE ABORDADORA (jefe, 3 cañones).
 *    · TRASERA: mamparo con la BARRERA DE CASCO (campo hexagonal): todo
 *      proyectil no devuelto la alcanza (onda en el punto de impacto). Los
 *      proyectiles JAMÁS colisionan con el jugador.
 *    · PALA: física de siempre (bumper con la velocidad real, patrón
 *      REACTOR aprobado) + GOLPE LIMPIO (zona dulce 3,5 cm + ≥4 m/s) que
 *      carga la SOBRECARGA (+20 %): al 100 % el siguiente golpe (≥3 m/s)
 *      lanza un ORBE PERFORANTE. Nunca se corrige la dirección.
 *    · ORBES (pool): ESTÁNDAR (azul) · PESADO (ámbar, restitución baja) ·
 *      INESTABLE (rojo, fusible 2,5 s, explota) · ROTOR (verde, curva).
 *      Gravedad cero, CCD por subpasos, vida 8 s / 25 m.
 *    · FASES: 1 ESCARAMUZA (3 artilleros) → INTERLUDIO (+30 casco) →
 *      2 ASALTO (4 artilleros + CENTINELA de rally) → INTERLUDIO →
 *      3 NAVE ABORDADORA (3 cañones, uno activo cada 8 s).
 *    · PRESIÓN CRECIENTE: tras 90 s de fase (1-2), cada 15 s la cadencia
 *      baja un 8 % (mínimo 50 %).
 *    · PANTALLA del techo (pantallainfo.png + capa de texto) y NOVA narrando.
 *    · DERROTA (casco 0): alarma, «Casco comprometido…», ASTRO riéndose y
 *      regreso a la sala. VICTORIA: el jefe explota y la escena queda limpia.
 *  Regla Quest: TODO se construye UNA vez (pools); nada se crea por partida;
 *  sin asignaciones por frame (vectores _tmp reutilizados).
 *  ========================================================================== */
const ESC_CFG = {
  /* sala propia (jugador en el origen, sobre la plataforma) */
  room: { hx: 5, bz: 2, fz: -12, hh: 6 },
  plataforma: { z: -1.05, r: 1.18, y: 0.02 },
  barrera: { z: 1.82, w: 3.3, h: 2.75, y: 1.62 },
  pantalla: { y: 4.35, z: -6.4, w: 3.1, h: 1.55, tilt: 0.16 },
  /* fases (sección 10): enemigos, cadencia, tope de orbes y mezcla */
  fases: [
    { drones: 3, centinela: 0, cadencia: 2.8, maxOrbes: 3,
      mix: { std: 1.0, pesado: 0, rotor: 0 } },
    { drones: 4, centinela: 1, cadencia: 2.2, maxOrbes: 4,
      mix: { std: 0.6, pesado: 0.2, rotor: 0.2 } },
    { drones: 0, jefe: true, maxOrbes: 5 },
  ],
  /* integridad del casco (sección 6) */
  hullMax: 100, interRegen: 30, alertaUmbral: 30,
  /* máquina de estados (sección 5) */
  prepT: 3, interT: 5,
  /* disparo (sección 8): telegrafía, movimiento de drones, vida de orbes */
  telegrafT: 0.8, droneMovT: 8, droneMinSep: 1.5,
  vidaOrbe: 8, distOrbe: 25,
  /* tipos de orbe (sección 8): radio, velocidad, daño, colores, extras */
  orb: {
    std:    { r: 0.05, v: [9, 11, 13], dano: 10, col: 0x4db8ff },
    pesado: { r: 0.09, v: 5, dano: 25, col: 0xffb84d, restit: 0.30,
              derribaV: 8, atraviesaV: 14 },
    inest:  { r: 0.06, v: 7, dano: 15, col: 0xff4d4d, fusible: 2.5,
              radioExp: 1.5, danoExp: 15, cercaJugador: 2.0 },
    rotor:  { r: 0.05, v: 10, dano: 10, col: 0x6dff8d, curvaAcc: 0.85 },
  },
  /* retorno con la pala: límites físicos del rebote (sin autoapuntado) */
  devMin: 3.5, devMax: 22,
  /* golpe limpio y Sobrecarga (sección 7) */
  sweetR: 0.035, cleanV: 4.0, cleanBonus: 0.20,
  perforanteV: 3.0, perforanteDano: 2,
  /* volúmenes de juego (sección 4) */
  despliegue: { zMin: -11, zMax: -6, xMax: 4, yMin: 1, yMax: 4 },
  ataque: { xMax: 0.9, yMin: 0.7, yMax: 1.8 },
  headSafeR: 0.35,
  /* Centinela (sección 9.2) */
  cent: { z: -8.4, y: 2.05, coreR: 0.42, shieldR: 0.85,
          rallyParaAbrir: 5, sobreT: 3, velGain: 1.10, velMax: 20,
          disparaCada: 4, sesgoJugador: 0.30 },
  /* Nave abordadora (sección 9.3) */
  jefe: { z: -11.0, y: 2.3, canonR: 0.42, hpCanon: 3, canonT: 8,
          cadencia: 3.5, entradaT: 4, explodeT: 4, abanico: 12 },
  /* presión creciente (sección 11) */
  presion: { umbral: 90, paso: 15, reduc: 0.08, minK: 0.5 },
  /* pérdida de tracking de la pala (sección 19) */
  trackTol: 0.5,
  /* HUD (sección 12) */
  msgT: 3.2,
};

class EscudoCasco {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.built = false;
    this.phase = 'idle';          // prep | combate | inter | result
    this.phaseT = 0;
    this.fase = 0;                // 0..2 (índice de ESC_CFG.fases)
    this.faseT = 0;
    this.hull = ESC_CFG.hullMax;
    this.sobrecarga = 0;          // 0..1 (se conserva entre fases)
    this.alerta = false;          // integridad ≤ 30
    this._presionT = 0;           // acumulador de presión creciente
    this._presionK = 1;           // multiplicador de cadencia (1 → 0,5)
    this.rally = 0;               // rally devuelto contra el Centinela
    this._trackLostT = 0;         // pérdida de tracking de la pala
    this._msg = ''; this._msgT = 0; this._msgSub = '';
    this._t = 0;
    this._alarmCd = 0;
    this._win = false;
    /* PANTALLA suspendida del techo (pantallainfo.png + capa de texto) */
    this.panCv = document.createElement('canvas');
    this.panCv.width = 1280; this.panCv.height = 640;
    this.panTex = this.ctrl._ct(this.panCv);
    this._panImg = null;
    try {
      const img = new Image();
      img.onload = () => { this._panImg = img; this._hudKey = ''; };
      img.src = this._A('pantallainfo.png');
    } catch (e) { /* sin arte: el panel se pinta igual */ }
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    this._tmpC = new THREE.Vector3();
    this._tmpQ = new THREE.Quaternion();
  }

  _A(p) { return this.ctrl._A('escudo_pala/' + p); }

  /* ---------------- construcción (una sola vez, en start) ---------------- */
  _build() {
    if (this.built) return;
    this.built = true;
    const g = this.game;
    const R = ESC_CFG.room;
    this._room = { ...R, zc: (R.bz + R.fz) / 2, depth: R.bz - R.fz };

    this.grp = new THREE.Group();
    this.grp.visible = false;
    g.rig.add(this.grp);

    /* SALA PROPIA: 6 imágenes (arte propio v3.5.0, estilo del dueño) */
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
    plano(R.hx * 2, this._room.depth, carga('suelo.jpg'), 0, 0, this._room.zc, 0, -Math.PI / 2);
    plano(R.hx * 2, this._room.depth, carga('techo.jpg'), 0, R.hh, this._room.zc, 0, Math.PI / 2);
    plano(R.hx * 2, R.hh, carga('frente.jpg'), 0, R.hh / 2, R.fz, 0, 0);
    plano(R.hx * 2, R.hh, carga('trasera.jpg'), 0, R.hh / 2, R.bz, Math.PI, 0);
    plano(this._room.depth, R.hh, carga('izquierda.png'), -R.hx, R.hh / 2, this._room.zc, Math.PI / 2, 0);
    plano(this._room.depth, R.hh, carga('derecha.png'), R.hx, R.hh / 2, this._room.zc, -Math.PI / 2, 0);

    /* PLATAFORMA DE DEFENSA (refuerzo 3D sobre el arte del suelo) */
    const PF = ESC_CFG.plataforma;
    this.plataforma = new THREE.Group();
    this.plataforma.position.set(0, PF.y, PF.z);
    const anillo = new THREE.Mesh(
      new THREE.RingGeometry(PF.r * 0.86, PF.r, 56),
      new THREE.MeshBasicMaterial({
        color: 0x35c8ff, transparent: true, opacity: 0.55,
        blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
      }));
    anillo.rotation.x = -Math.PI / 2;
    this.plataforma.add(anillo);
    this.plataforma.add(new THREE.PointLight(0x35c8ff, 0.55, 4.5, 2));
    this.grp.add(this.plataforma);

    /* BARRERA DE CASCO: campo hexagonal en el mamparo trasero (la única
     * cosa que recibe impactos enemigos; los proyectiles jamás tocan al
     * jugador). Textura hexagonal procedural translúcida. */
    const BA = ESC_CFG.barrera;
    this.barreraMat = new THREE.MeshBasicMaterial({
      map: this._hexTex(), color: 0x66d8ff, transparent: true, opacity: 0.34,
      blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
    });
    this.barrera = new THREE.Mesh(new THREE.PlaneGeometry(BA.w, BA.h), this.barreraMat);
    this.barrera.position.set(0, BA.y, BA.z);
    this.barrera.renderOrder = 12;
    this.grp.add(this.barrera);
    const marcoBA = new THREE.Mesh(
      new THREE.RingGeometry(Math.max(BA.w, BA.h) * 0.52, Math.max(BA.w, BA.h) * 0.56, 6, 1),
      new THREE.MeshBasicMaterial({
        color: 0x2b7fb8, transparent: true, opacity: 0.5,
        blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
      }));
    marcoBA.rotation.z = Math.PI / 6;
    marcoBA.scale.set(BA.w / Math.max(BA.w, BA.h) * 1.12, BA.h / Math.max(BA.w, BA.h) * 1.30, 1);
    marcoBA.position.copy(this.barrera.position);
    marcoBA.position.z -= 0.04;
    this.grp.add(marcoBA);
    /* ondas de impacto (pool) */
    this.ondas = [];
    for (let i = 0; i < 7; i++) {
      const w = new THREE.Mesh(new THREE.PlaneGeometry(1, 1),
        new THREE.MeshBasicMaterial({
          map: this._glowTex(), color: 0x8fe4ff, transparent: true, opacity: 0,
          blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
        }));
      w.visible = false;
      w.renderOrder = 22;
      this.grp.add(w);
      this.ondas.push({ m: w, t: 9 });
    }

    /* PANTALLA suspendida del techo (HUD, sección 12) */
    this.panMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(ESC_CFG.pantalla.w, ESC_CFG.pantalla.h),
      new THREE.MeshBasicMaterial({ map: this.panTex, transparent: true, depthWrite: false }));
    this.panMesh.position.set(0, ESC_CFG.pantalla.y, ESC_CFG.pantalla.z);
    this.panMesh.rotation.x = ESC_CFG.pantalla.tilt;
    this.panMesh.renderOrder = 10;
    this.grp.add(this.panMesh);
    const brazo = new THREE.Mesh(
      new THREE.CylinderGeometry(0.025, 0.025, R.hh - ESC_CFG.pantalla.y - ESC_CFG.pantalla.h / 2, 8),
      new THREE.MeshStandardMaterial({ color: 0x2b3138, roughness: 0.5, metalness: 0.6 }));
    brazo.position.set(0, (R.hh + ESC_CFG.pantalla.y + ESC_CFG.pantalla.h / 2) / 2, ESC_CFG.pantalla.z);
    this.grp.add(brazo);

    /* DRONES ARTILLEROS (pool de 4 = máximo de la fase 2) */
    this.drones = [];
    const cuerpoD = new THREE.OctahedronGeometry(0.34, 0);
    const ojoD = new THREE.SphereGeometry(0.12, 14, 10);
    const anilloD = new THREE.TorusGeometry(0.46, 0.028, 8, 28);
    for (let i = 0; i < 4; i++) {
      const grp = new THREE.Group();
      const cuerpo = new THREE.Mesh(cuerpoD, new THREE.MeshStandardMaterial({
        color: 0x39424d, roughness: 0.4, metalness: 0.75, flatShading: true,
        emissive: 0xff3524, emissiveIntensity: 0,
      }));
      cuerpo.rotation.z = Math.PI / 4;
      const ojo = new THREE.Mesh(ojoD, new THREE.MeshStandardMaterial({
        color: 0x1a0d0d, roughness: 0.3, metalness: 0.2,
        emissive: 0xff3524, emissiveIntensity: 1.5,
      }));
      ojo.position.set(0, 0, 0.26);
      const aro = new THREE.Mesh(anilloD, new THREE.MeshStandardMaterial({
        color: 0x22282f, roughness: 0.5, metalness: 0.8,
        emissive: 0xffb84d, emissiveIntensity: 0,
      }));
      aro.rotation.x = Math.PI / 2;
      grp.add(cuerpo, ojo, aro);
      grp.visible = false;
      this.grp.add(grp);
      this.drones.push({
        grp, cuerpo, ojo, aro, alive: false,
        pos: grp.position, spot: new THREE.Vector3(), from: new THREE.Vector3(),
        movT: 0, movD: 1, shootT: 0, chargeT: 9, tipo: 'std',
        thud: Math.random() * Math.PI * 2,
      });
    }

    /* CENTINELA (duelo de rally, fases 2 y 3 como extra de la fase 2) */
    this.cent = new THREE.Group();
    const cuerpoC = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1),
      new THREE.MeshStandardMaterial({
        color: 0x39424d, roughness: 0.4, metalness: 0.75, flatShading: true,
      }));
    this.centCore = new THREE.Mesh(new THREE.SphereGeometry(0.20, 14, 10),
      new THREE.MeshStandardMaterial({
        color: 0x10281c, roughness: 0.3, emissive: 0x35ff9d, emissiveIntensity: 0.25,
      }));
    this.centCore.position.z = -0.05;
    this.centShield = new THREE.Mesh(
      new THREE.SphereGeometry(ESC_CFG.cent.shieldR, 26, 14, 0, Math.PI * 2, 0, Math.PI * 0.52),
      new THREE.MeshStandardMaterial({
        color: 0x2f7fb8, roughness: 0.25, metalness: 0.5, transparent: true,
        opacity: 0.62, side: THREE.DoubleSide, emissive: 0x2f9fe8, emissiveIntensity: 0.5,
      }));
    this.centShield.rotation.x = Math.PI / 2;       // cuenco abierto hacia +Z (jugador)
    this.cent.add(cuerpoC, this.centCore, this.centShield);
    this.cent.position.set(0, ESC_CFG.cent.y, ESC_CFG.cent.z);
    this.cent.visible = false;
    this.grp.add(this.cent);
    this.centOn = false;
    this.centDead = false;
    this.centShootT = 0;
    this.centChargeT = 9;
    this.centSobreT = 0;            // sobrecalentamiento restante (>0 = escudo abierto)

    /* NAVE ABORDADORA (jefe de la fase 3): casco + 3 cañones */
    this.jefe = new THREE.Group();
    const cascoM = new THREE.MeshStandardMaterial({
      color: 0x3a2f2a, roughness: 0.5, metalness: 0.7, flatShading: true,
      emissive: 0xff3524, emissiveIntensity: 0,
    });
    const quilla = new THREE.Mesh(new THREE.BoxGeometry(4.6, 1.5, 2.6), cascoM);
    quilla.position.y = -0.55;
    const puente = new THREE.Mesh(new THREE.SphereGeometry(1.05, 18, 12), cascoM);
    puente.position.set(0, 0.45, 0.35); puente.scale.set(1.25, 0.72, 1);
    this.jefe.add(quilla, puente);
    this.canones = [];
    const canonGeo = new THREE.CylinderGeometry(0.20, 0.26, 1.15, 14);
    const tipGeo = new THREE.SphereGeometry(0.24, 14, 10);
    for (let i = 0; i < 3; i++) {
      const grpC = new THREE.Group();
      const tubo = new THREE.Mesh(canonGeo, new THREE.MeshStandardMaterial({
        color: 0x242a31, roughness: 0.4, metalness: 0.85,
      }));
      tubo.rotation.x = Math.PI / 2;
      const tip = new THREE.Mesh(tipGeo, new THREE.MeshStandardMaterial({
        color: 0x10281c, roughness: 0.3,
        emissive: 0x35ff9d, emissiveIntensity: 0.15,
      }));
      tip.position.z = 0.62;
      grpC.add(tubo, tip);
      grpC.position.set((i - 1) * 1.85, i === 1 ? 0.35 : -0.35, 1.05);
      grpC.visible = false;
      this.jefe.add(grpC);
      this.canones.push({ grp: grpC, tip, hp: ESC_CFG.jefe.hpCanon, dead: false, volT: 0, cola: [] });
    }
    this.jefe.position.set(0, ESC_CFG.jefe.y, ESC_CFG.room.fz - 4.5);
    this.jefe.visible = false;
    this.grp.add(this.jefe);
    this.jefeOn = false;
    this.jefeCanon = -1;            // cañón activo (-1 = entrada)
    this.jefeCanonT = 0;
    this.jefeEntrT = 0;

    /* ORBES DE PLASMA (pool: 5 enemigos + devueltos activos) */
    this.orbes = [];
    const orbGeo = new THREE.SphereGeometry(1, 16, 12);
    for (let i = 0; i < 13; i++) {
      const mat = new THREE.MeshStandardMaterial({
        color: 0x4db8ff, roughness: 0.25, emissive: 0x4db8ff, emissiveIntensity: 1.5,
      });
      const mesh = new THREE.Mesh(orbGeo, mat);
      mesh.visible = false;
      const glow = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this._glowTex(), color: 0x4db8ff, transparent: true, opacity: 0.6,
        blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      glow.visible = false;
      this.grp.add(mesh, glow);
      this.orbes.push({
        mesh, glow, mat, alive: false, owner: 'enemigo', tipo: 'std',
        vel: new THREE.Vector3(), prev: new THREE.Vector3(),
        lifeT: 0, dist: 0, fuse: -1, spinS: 0, clean: false, perf: false,
        rebote: false, r: 0.05, blink: 0,
      });
    }

    /* FX: destellos + fragmentos (exclusivamente visuales) */
    this.flashes = [];
    for (let i = 0; i < 10; i++) {
      const fl = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.7),
        new THREE.MeshBasicMaterial({
          map: this._glowTex(), color: 0x9fe8ff, transparent: true, opacity: 0,
          blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
        }));
      fl.visible = false;
      fl.renderOrder = 24;
      this.grp.add(fl);
      this.flashes.push({ m: fl, t: 9 });
    }
    this.frags = [];
    const fGeo = new THREE.BoxGeometry(0.06, 0.06, 0.06);
    for (let i = 0; i < 40; i++) {
      const fm = new THREE.Mesh(fGeo, new THREE.MeshStandardMaterial({
        color: 0x8f9aa6, roughness: 0.5, metalness: 0.4,
        emissive: 0xff5a30, emissiveIntensity: 0.8, transparent: true, opacity: 0,
      }));
      fm.visible = false;
      this.grp.add(fm);
      this.frags.push({ m: fm, vel: new THREE.Vector3(), t: 9 });
    }

    /* LUZ DE ALARMA (alerta crítica: única luz dinámica extra) */
    this.luzAlarma = new THREE.PointLight(0xff3524, 0, 9, 2);
    this.luzAlarma.position.set(0, 3.2, -4);
    this.grp.add(this.luzAlarma);

    /* referencia al CENTRO DE LA HOJA de la pala (zona dulce, sección 7) */
    this._bladeRefs = [];
    if (g.paddleMounts) {
      for (const m of g.paddleMounts) {
        if (!m) continue;
        const ref = new THREE.Object3D();
        ref.position.set(0, (2.1115 - (-2.9)) * 0.026, 0);   // PALA_BLADE_Y−PALA_GRIP_Y × escala
        m.add(ref);
        this._bladeRefs.push(ref);
      }
    }
  }

  _texGlow() { return this._glowTex(); }
  _glowTex() {
    if (this._gt) return this._gt;
    const cv = document.createElement('canvas');
    cv.width = 128; cv.height = 128;
    const c = cv.getContext('2d');
    const gr = c.createRadialGradient(64, 64, 4, 64, 64, 62);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.4, 'rgba(255,255,255,0.5)');
    gr.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = gr;
    c.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(cv);
    this.ctrl._ownTex.add(t);
    this._gt = t;
    return t;
  }

  _hexTex() {
    if (this._ht) return this._ht;
    const cv = document.createElement('canvas');
    cv.width = 256; cv.height = 256;
    const c = cv.getContext('2d');
    c.strokeStyle = 'rgba(255,255,255,0.85)';
    c.lineWidth = 2;
    const r = 22, h = r * Math.sqrt(3) / 2;
    for (let row = -1; row < 8; row++) {
      for (let col = -1; col < 8; col++) {
        const cx = col * r * 1.5 * 2 + (row % 2 ? r * 1.5 : 0);
        const cy = row * h * 2;
        c.beginPath();
        for (let k = 0; k < 6; k++) {
          const a = Math.PI / 3 * k + Math.PI / 6;
          const px = cx + Math.cos(a) * r, py = cy + Math.sin(a) * r;
          if (k === 0) c.moveTo(px, py); else c.lineTo(px, py);
        }
        c.closePath();
        c.stroke();
      }
    }
    const t = new THREE.CanvasTexture(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(3, 2.5);
    this.ctrl._ownTex.add(t);
    this._ht = t;
    return t;
  }

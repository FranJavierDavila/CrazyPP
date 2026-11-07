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
    this._tmpD = new THREE.Vector3();
    this._tmpE = new THREE.Vector3();
    this._cdO = null; this._cdT = 0; this._eraRebote = null;
    this._evts = [];            // eventos del puente CCD del núcleo
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
        pos: mesh.position,                    // alias: el barrido CCD del núcleo lee ball.pos
        vel: new THREE.Vector3(), prev: new THREE.Vector3(),
        spin: new THREE.Vector3(),             // el barrido CCD del núcleo lo usa
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

  /* ---------------- ciclo de vida ---------------- */
  start() {
    if (this.active) return;
    this._build();
    this.active = true;
    this.phase = 'prep';
    this.phaseT = ESC_CFG.prepT;
    this.fase = 0;
    this.faseT = 0;
    this.hull = ESC_CFG.hullMax;
    this.sobrecarga = 0;
    this.alerta = false;
    this._presionT = 0;
    this._presionK = 1;
    this.rally = 0;
    this._win = false;
    this._trackLostT = 0;
    this._banner = null;
    this._msg = ''; this._msgT = 0;
    this._cdO = null; this._cdT = 0; this._eraRebote = null;
    for (const c of this.canones || []) {
      c.hp = ESC_CFG.jefe.hpCanon; c.dead = false; c.cola.length = 0;
      c.tip.material.emissiveIntensity = 0.15;
    }
    this.jefeCanon = -1;
    this.centSobreT = 0;
    this._limpiaOrbes();
    this._msgNova(tx('Comandante, el casco frontal ha sido perforado y la defensa automática está fuera de línea. Active el escudo manual.',
      'Commander, the frontal hull is breached and automated defense is offline. Activate the manual shield.'), ESC_CFG.prepT + 1.2);
    const g = this.game;
    /* ESCENARIO: fuera sala del núcleo, mesa, marcador, rival y recortes */
    if (g.roomGroup) g.roomGroup.visible = false;
    this.grp.visible = true;
    g.tableGroup.visible = false;            // SIN mesa tradicional
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    if (this.ctrl.rivalMesh) {
      this._rivalHome = this._rivalHome || this.ctrl.rivalMesh.position.clone();
      this.ctrl.rivalMesh.visible = false;   // el ASTRO sólo en la derrota
    }
    if (this.ctrl.cartel) this.ctrl.cartel.visible = false;
    if (this.ctrl.powerSign) this.ctrl.powerSign.visible = false;
    try { if (this.ctrl.mapa && this.ctrl.mapa.hide) this.ctrl.mapa.hide(); } catch (e) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = false; } catch (e1) { /* */ }
    /* SIN pelota, SIN base, SIN pistola: sólo la pala (mano libre ociosa) */
    g.ball.ignoreNet = true;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = false;
    g.ballMesh.scale.setScalar(1);
    try { if (g.trailObj) g.trailObj.visible = false; } catch (e2) { /* */ }
    try { if (g.gunMounts) for (const gm of g.gunMounts) if (gm) gm.visible = false; } catch (e3) { /* */ }
    g.rules.state = 'arkanoid';              // estado genérico de PRUEBA (árbitro duerme)
    g.rules.message = 'ESCUDO DE PALA · DEFENSA DEL CASCO';
    this._hudKey = '';
    g.audio.playOsc(330, 392, 0.12, 'square', 0.11, 0);
    window.setTimeout(() => { try { g.audio.playOsc(494, 523, 0.2, 'square', 0.12, 0); } catch (e4) { /* */ } }, 150);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    if (g.roomGroup) g.roomGroup.visible = false;
    this.grp.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (this.ctrl.rivalMesh && this.phase !== 'result') this.ctrl.rivalMesh.visible = false;
    g.ballMesh.visible = false;
    this._hudKey = '';
  }

  stop() {
    this.active = false;
    this.phase = 'idle';
    this._banner = null;
    this._msg = ''; this._msgT = 0;
    if (this.cargaGlow) this.cargaGlow.visible = false;
    if (!this.built) return;
    const g = this.game;
    this._limpiaOrbes();
    this._fxReset();
    this.grp.visible = false;
    /* la sala de la estación vuelve */
    if (g.roomGroup) g.roomGroup.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ball.ignoreNet = false;
    g.ballMesh.scale.setScalar(1);
    g.ballMesh.visible = true;
    try { if (g.trailObj) g.trailObj.visible = g.showTrail !== false; } catch (e) { /* */ }
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    try {
      const D = this.ctrl.D;
      g.ball.pos.set(0, D.tableTopY + (D.ballRadius || 0.02), D.tableCenterZ + 0.45);
      if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    } catch (e0) { /* */ }
    if (this.ctrl.rivalMesh) {
      if (this._rivalHome) this.ctrl.rivalMesh.position.copy(this._rivalHome);
      this.ctrl.rivalMesh.visible = true;
    }
    try { if (this.ctrl.mapa && this.ctrl.mapa.show) this.ctrl.mapa.show(); } catch (e1) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = true; } catch (e2) { /* */ }
  }

  _limpiaOrbes() {
    for (const o of this.orbes) {
      o.alive = false;
      o.mesh.visible = false;
      o.glow.visible = false;
    }
  }

  _fxReset() {
    for (const f of this.flashes) { f.t = 9; f.m.visible = false; }
    for (const f of this.frags) { f.t = 9; f.m.visible = false; }
    for (const w of this.ondas) { w.t = 9; w.m.visible = false; }
    this.luzAlarma.intensity = 0;
    if (this.jefe) { this.jefe.visible = false; this.jefeOn = false; }
    if (this.cent) { this.cent.visible = false; this.centOn = false; }
    if (this.drones) for (const d of this.drones) { d.alive = false; d.grp.visible = false; }
  }

  /* ---------------- bucle de la prueba ---------------- */
  step(dt) {
    if (!this.active) return;
    const g = this.game;
    this._t += dt;
    if (this._msgT > 0) this._msgT -= dt;
    this._hudDirty();
    /* pérdida de tracking de la pala >0,5 s: los drones suspenden el disparo */
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (ps && ps.active) this._trackLostT = 0;
    else this._trackLostT += dt;
    const trackOk = this._trackLostT < ESC_CFG.trackTol;

    if (this.phase === 'prep') {
      this.phaseT -= dt;
      this._anims(dt);
      if (this.phaseT <= 0) this._faseArranca(0);
    } else if (this.phase === 'combate') {
      this.faseT += dt;
      /* PRESIÓN CRECIENTE (fases 1-2): tras 90 s, cada 15 s −8 % de cadencia */
      const F = ESC_CFG.fases[this.fase];
      if (F && !F.jefe) {
        if (this.faseT > ESC_CFG.presion.umbral) {
          this._presionT += dt;
          if (this._presionT >= ESC_CFG.presion.paso) {
            this._presionT -= ESC_CFG.presion.paso;
            this._presionK = Math.max(ESC_CFG.presion.minK, this._presionK * (1 - ESC_CFG.presion.reduc));
            this._msgNova(tx('Refuerzos enemigos en camino. Ritmo de fuego creciente.',
              'Enemy reinforcements inbound. Fire rate increasing.'), 2.4);
          }
        }
        /* enemigos */
        for (const d of this.drones) if (d.alive) this._dronStep(d, dt, trackOk);
        if (this.centOn) this._centStep(dt, trackOk);
      } else if (F && F.jefe) {
        this._jefeStep(dt, trackOk);
      }
      /* orbes + FX */
      this._orbesStep(dt);
      if (!this.active) return;              // pudo terminar dentro
      this._anims(dt);
      /* alerta crítica (≤30): luces rojas + alarma suave */
      if (this.hull <= ESC_CFG.alertaUmbral) {
        this.luzAlarma.intensity = 1.15 + Math.sin(this._t * 7) * 0.75;
        this._alarmCd -= dt;
        if (this._alarmCd <= 0) {
          this._alarmCd = 1.4;
          try { g.audio.playOsc(620, 430, 0.34, 'sawtooth', 0.1, 0); } catch (e) { /* */ }
        }
      } else {
        this.luzAlarma.intensity *= Math.max(0, 1 - dt * 5);
      }
    } else if (this.phase === 'inter') {
      this.phaseT -= dt;
      this._orbesStep(dt);                   // sólo disolución residual
      this._anims(dt);
      if (this.phaseT <= 0) this._faseArranca(this.fase + 1);
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      this._anims(dt);
      if (this.phaseT <= 0) { this._afterResult(); return; }
    }
  }

  /* ---------------- fases (sección 10) ---------------- */
  _faseArranca(i) {
    this.fase = Math.min(i, 2);
    this.phase = 'combate';
    this.faseT = 0;
    this._presionT = 0;
    this._presionK = 1;
    this.rally = 0;
    const g = this.game;
    const F = ESC_CFG.fases[this.fase];
    if (F.jefe) {
      /* FASE 3: la nave abordadora se acopla en la brecha (entrada 4 s) */
      this.jefeOn = true;
      this.jefeEntrT = ESC_CFG.jefe.entradaT;
      this.jefeCanon = -1;
      this.jefeCanonT = 0;
      this.jefe.visible = true;
      this.jefe.position.set(0, ESC_CFG.jefe.y, ESC_CFG.room.fz - 4.5);
      for (const c of this.canones) { c.grp.visible = !c.dead; c.volT = 0; c.cola.length = 0; }
      this._msgNova(tx('Nave abordadora acoplándose. Destruya sus cañones.',
        'Boarding ship docking. Destroy its cannons.'), 4.4);
      try { g.audio.announce(tx('Nave abordadora detectada', 'Boarding ship detected'), true); } catch (e) { /* */ }
    } else {
      /* FASES 1-2: drones artilleros (+ Centinela en la fase 2) */
      for (let k = 0; k < F.drones; k++) {
        const d = this.drones[k];
        d.alive = true;
        d.grp.visible = true;
        d.grp.scale.setScalar(0.01);
        this._dronSpot(d, true);
        d.movT = ESC_CFG.droneMovT * (0.6 + Math.random() * 0.8);
        d.shootT = ESC_CFG.fases[this.fase].cadencia * (1 + Math.random() * 0.5);
        d.chargeT = 9;
      }
      this.centOn = !!F.centinela;
      this.centDead = false;
      if (this.centOn) {
        this.cent.visible = true;
        this.cent.position.set(0, ESC_CFG.cent.y, ESC_CFG.cent.z);
        this.centShield.material.opacity = 0.62;
        this.centCore.material.emissiveIntensity = 0.25;
        this.centSobreT = 0;
        this.centShootT = ESC_CFG.cent.disparaCada;
        this.centChargeT = 9;
      }
      const nombres = ['Drones de abordaje detectados. Devuelva sus disparos.',
        'Nuevos tipos de munición detectados. Los torpedos pesados exigen un golpe firme.'];
      this._msgNova(tx(nombres[this.fase] || '', nombres[this.fase] || ''), 4.2);
      try { g.audio.announce(tx('Fase ' + (this.fase + 1), 'Phase ' + (this.fase + 1)), true); } catch (e0) { /* */ }
    }
    this._hudKey = '';
  }

  /** Fin de fase: limpia enemigos y orbes con disolución visual (sección 14). */
  _faseCompleta() {
    const g = this.game;
    /* disolución: los drones vivos restantes (si los hubiera) se apagan */
    for (const d of this.drones) if (d.alive) { d.alive = false; d.grp.visible = false; }
    if (this.centOn) { this.centOn = false; this.cent.visible = false; }
    for (const o of this.orbes) if (o.alive) this._orbMuere(o, true);
    if (this.fase >= 2) { this._finish(true); return; }
    this.phase = 'inter';
    this.phaseT = ESC_CFG.interT;
    const antes = this.hull;
    this.hull = Math.min(ESC_CFG.hullMax, this.hull + ESC_CFG.interRegen);
    if (this.hull > ESC_CFG.alertaUmbral) this.alerta = false;
    this._msgNova(tx('Reparaciones de emergencia en curso. Integridad restaurada parcialmente (+' +
      Math.round(this.hull - antes) + ' %).',
      'Emergency repairs underway. Integrity partially restored (+' + Math.round(this.hull - antes) + ' %).'),
      ESC_CFG.interT);
    g.confettiBurst = 0;
    g.audio.fanfare(true);
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 0.7, 130);
      window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.4, 110); } catch (e) { /* */ } }, 200);
    }
    this._hudKey = '';
  }

  /* ---------------- final: victoria y derrota (sección 14) ---------------- */
  _finish(win) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? ESC_CFG.jefe.explodeT + 1.4 : 4.2;
    this._win = win;
    this.jefeOn = false;
    this.centOn = false;
    if (win) {
      /* EL JEFE EXPLOTA (secuencia ~4 s): flashes + fragmentos + sacudida */
      this._jefeExplosion();
      this._msgNova(tx('Amenaza neutralizada. Buen trabajo, comandante.',
        'Threat neutralized. Good work, commander.'), this.phaseT);
      if (a._replay) {
        this._banner = { title: '¡CASCO DEFENDIDO!', sub: 'Rejugada terminada', col: '#7fb069' };
        try { g.audio.announce('Rejugada terminada', true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: '¡CASCO DEFENDIDO!',
          sub: 'Siguiente: ' + sig.name, col: '#7fb069',
        };
        try { g.audio.announce(this._banner.sub, true); } catch (e0) { /* */ }
      }
      g.confettiBurst = 3;
      g.audio.fanfare(true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.5, 130); } catch (e1) { /* */ } }, 220);
      }
    } else {
      /* DERROTA: casco a 0 — alarma, mensaje, ASTRO riéndose y regreso */
      this._msgNova(tx('Casco comprometido…', 'Hull compromised…'), this.phaseT);
      this._banner = { title: '¡CASCO COMPROMETIDO!', sub: 'La defensa ha caído', col: '#e06c5a' };
      g.audio.fanfare(false);
      try { g.audio.announce(tx('Casco comprometido', 'Hull compromised'), true); } catch (e2) { /* */ }
      a._pruebaFin(false);
      if (a.rivalMesh) {
        a.rivalMesh.position.set(0, 1.075, -2.1);
        a.rivalMesh.visible = true;
        a.rivalEstado('laughing');       // astro_laughing, única aparición
      }
      this.luzAlarma.intensity = 1.6;
    }
    this._limpiaOrbes();
    this._hudKey = '';
  }

  _afterResult() {
    const a = this.ctrl;
    this.stop();
    a._despuesDePrueba();
  }

  /* ---------------- drones artilleros (sección 9.1) ---------------- */
  _dronSpot(d, init) {
    const Z = ESC_CFG.despliegue;
    for (let i = 0; i < 24; i++) {
      const x = (Math.random() * 2 - 1) * Z.xMax;
      const y = Z.yMin + Math.random() * (Z.yMax - Z.yMin);
      const z = Z.zMin + Math.random() * (Z.zMax - Z.zMin);
      let ok = true;
      for (const o of this.drones) {
        if (!o.alive || o === d) continue;
        if (o.pos.distanceToSquared(this._tmpA.set(x, y, z)) < ESC_CFG.droneMinSep * ESC_CFG.droneMinSep) { ok = false; break; }
      }
      if (ok) {
        if (init) d.pos.set(x, y, z);
        else { d.from.copy(d.pos); d.spot.set(x, y, z); d.movD = 0; }
        return;
      }
    }
    if (init) d.pos.set(0, 2, -8);
    else { d.from.copy(d.pos); d.spot.copy(d.pos); }
  }

  _dronStep(d, dt, trackOk) {
    const g = this.game;
    /* deriva + reposición cada 8 s (lerp suave hacia el nuevo spot) */
    d.thud += dt;
    d.grp.position.y += Math.sin(d.thud * 1.6) * dt * 0.05;
    d.grp.rotation.y += dt * 0.7;
    if (d.movD < 1) {
      d.movD = Math.min(1, d.movD + dt / 1.6);
      const e = d.movD * d.movD * (3 - 2 * d.movD);
      d.grp.position.lerpVectors(d.from, d.spot, e);
    } else {
      d.movT -= dt;
      if (d.movT <= 0) {
        d.movT = ESC_CFG.droneMovT * (0.7 + Math.random() * 0.6);
        this._dronSpot(d, false);
      }
    }
    /* escala de aparición */
    if (d.grp.scale.x < 1) d.grp.scale.setScalar(Math.min(1, d.grp.scale.x + dt * 1.8));
    /* TELEGRAFÍA 0,8 s (anillo de carga + sonido espacial) y disparo */
    if (d.chargeT < 9) {
      d.chargeT -= dt;
      const k = 1 - Math.max(0, d.chargeT) / ESC_CFG.telegrafT;
      d.aro.material.emissiveIntensity = 0.4 + k * 2.2;
      d.aro.scale.setScalar(1 + Math.sin(this._t * (8 + k * 22)) * 0.06 * (1 - k) + k * 0.25);
      if (d.chargeT <= 0) {
        d.chargeT = 9;
        d.aro.material.emissiveIntensity = 0;
        d.aro.scale.setScalar(1);
        this._orbSpawn(d.tipo, d.pos, null, 'enemigo');
      }
    } else {
      d.shootT -= dt * (trackOk ? 1 : 0);       // sin tracking: sin disparos
      if (d.shootT <= 0 && trackOk) {
        if (this._orbesEnemigos() >= (ESC_CFG.fases[this.fase].maxOrbes || 3)) {
          d.shootT = 0.5;                       // tope de orbes: espera
        } else {
          d.shootT = ESC_CFG.fases[this.fase].cadencia * this._presionK;
          d.tipo = this._tipoOrbe();
          d.chargeT = ESC_CFG.telegrafT;
          try { g.audio.playOsc(240, 340, ESC_CFG.telegrafT * 0.8, 'sine', 0.07, 0); } catch (e) { /* */ }
        }
      }
    }
  }

  /** Destrucción de un dron artillero: fragmentación visual, sonido y
   *  decremento del contador EXACTAMENTE una vez (sección 9.1). */
  _dronMuere(d) {
    if (!d.alive) return;                    // una sola vez (caso límite 19)
    const g = this.game;
    d.alive = false;
    d.grp.visible = false;
    this._frags(d.pos, 10, 0xffb84d);
    this._flash(d.pos, 0x9fe8ff, 1.5);
    try { g.audio.playNoise(0.3, 240, 0.45, 0.2, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(340, 150, 0.25, 'sawtooth', 0.16, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 110);
    this._hudKey = '';
    this._compruebaFase();
  }

  _orbesEnemigos() {
    let n = 0;
    for (const o of this.orbes) if (o.alive && o.owner === 'enemigo') n++;
    return n;
  }

  _tipoOrbe() {
    const mix = ESC_CFG.fases[this.fase].mix;
    const r = Math.random();
    if (r < (mix.pesado || 0)) {
      /* NUNCA dos orbes pesados a la vez (sección 10) */
      for (const o of this.orbes) if (o.alive && o.owner === 'enemigo' && o.tipo === 'pesado') return 'std';
      return 'pesado';
    }
    if (r < (mix.pesado || 0) + (mix.rotor || 0)) return 'rotor';
    return 'std';
  }

  /* ---------------- Centinela (sección 9.2) ---------------- */
  _centStep(dt, trackOk) {
    const g = this.game;
    this.cent.rotation.y = Math.sin(this._t * 0.8) * 0.18;
    this.cent.position.y = ESC_CFG.cent.y + Math.sin(this._t * 1.3) * 0.12;
    if (this.centSobreT > 0) {
      /* ESCUDO ABIERTO (sobrecalentamiento): núcleo expuesto 3 s */
      this.centSobreT -= dt;
      this.centShield.material.opacity = 0.14;
      this.centCore.material.emissiveIntensity = 1.4 + Math.sin(this._t * 12) * 0.5;
      if (this.centSobreT <= 0) {
        this.centShield.material.opacity = 0.62;
        this.centCore.material.emissiveIntensity = 0.25;
        this.rally = 0;                     // cerró sin impacto: rally a 0
        this._hudKey = '';
      }
    }
    /* sus propios orbes estándar cada 4 s */
    if (this.centChargeT < 9) {
      this.centChargeT -= dt;
      if (this.centChargeT <= 0) {
        this.centChargeT = 9;
        this._orbSpawn('std', this.cent.position, null, 'enemigo');
      }
    } else {
      this.centShootT -= dt * (trackOk ? 1 : 0);
      if (this.centShootT <= 0 && trackOk &&
          this._orbesEnemigos() < (ESC_CFG.fases[this.fase].maxOrbes || 4)) {
        this.centShootT = ESC_CFG.cent.disparaCada;
        this.centChargeT = ESC_CFG.telegrafT;
        try { g.audio.playOsc(200, 300, ESC_CFG.telegrafT * 0.8, 'sine', 0.07, 0); } catch (e) { /* */ }
      }
    }
  }

  /** El escudo del Centinela devuelve el orbe: 70 % reflexión física +
   *  30 % hacia el jugador, +10 % de velocidad (tope 20 m/s). */
  _centRebota(o) {
    const sp = o.vel.length();
    this._tmpA.copy(o.vel).normalize();
    /* reflexión especular sobre el plano del escudo (normal +Z) */
    this._tmpA.z = Math.abs(this._tmpA.z);
    this._tmpA.normalize().multiplyScalar(sp);
    /* 30 % de sesgo hacia el jugador */
    this._tmpB.set(0, 1.55, 0.2).sub(o.mesh.position).normalize()
      .multiplyScalar(sp * ESC_CFG.cent.sesgoJugador);
    this._tmpA.add(this._tmpB);
    const v = Math.min(ESC_CFG.cent.velMax, sp * ESC_CFG.cent.velGain);
    o.vel.copy(this._tmpA).normalize().multiplyScalar(v);
    o.owner = 'enemigo';
    o.rebote = true;                         // si lo devuelvo de nuevo: rally++
    o.clean = false;
    o.perf = false;
    o.lifeT = 0;
    o.dist = 0;
    this._hudKey = '';
    const g = this.game;
    this._flash(o.mesh.position, 0x66d8ff, 0.55);
    try { g.audio.playOsc(520, 700, 0.07, 'square', 0.16, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 50);
  }

  _centMuere() {
    const g = this.game;
    this.centOn = false;
    this.centDead = true;
    this.cent.visible = false;
    this._frags(this.cent.position, 12, 0x66d8ff);
    this._flash(this.cent.position, 0x9fe8ff, 1.6);
    try { g.audio.playNoise(0.35, 260, 0.4, 0.2, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(320, 140, 0.3, 'sawtooth', 0.18, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.75, 120);
    this._hudKey = '';
    this._compruebaFase();
  }

  /* ---------------- nave abordadora (sección 9.3) ---------------- */
  _jefeStep(dt, trackOk) {
    const g = this.game;
    this.jefe.rotation.z = Math.sin(this._t * 0.9) * 0.02;
    if (this.jefeCanon < 0) {
      /* ENTRADA 4 s: se desliza desde la brecha; no dispara */
      this.jefeEntrT -= dt;
      const k = 1 - Math.max(0, this.jefeEntrT) / ESC_CFG.jefe.entradaT;
      this.jefe.position.z = ESC_CFG.room.fz - 4.5 + (ESC_CFG.jefe.z - (ESC_CFG.room.fz - 4.5)) * k;
      if (this.jefeEntrT <= 0) {
        this._canonSiguiente();
      }
      return;
    }
    this.jefeCanonT -= dt;
    const c = this.canones[this.jefeCanon];
    /* PATRONES de disparo del cañón activo (cada 3,5 s) */
    if (trackOk && this._orbesEnemigos() < ESC_CFG.fases[2].maxOrbes) {
      c.volT -= dt;
      if (c.volT <= 0) {
        c.volT = ESC_CFG.jefe.cadencia;
        if (this.jefeCanon === 0) {          // IZQUIERDO: 2 rotor alternados
          c.cola.push({ t: 0, tipo: 'rotor' }, { t: 0.9, tipo: 'rotor' });
        } else if (this.jefeCanon === 1) {   // CENTRAL: pesado + inestable
          c.cola.push({ t: 0, tipo: 'pesado' }, { t: 1.0, tipo: 'inest' });
        } else {                             // DERECHO: abanico de 3 estándar
          c.cola.push({ t: 0, tipo: 'std:0' }, { t: 0.25, tipo: 'std:-1' }, { t: 0.5, tipo: 'std:1' });
        }
        try { g.audio.playOsc(210, 300, ESC_CFG.telegrafT * 0.8, 'sine', 0.08, 0); } catch (e) { /* */ }
      }
      for (let i = c.cola.length - 1; i >= 0; i--) {
        const ev = c.cola[i];
        ev.t -= dt;
        if (ev.t <= 0) {
          c.cola.splice(i, 1);
          if (ev.tipo.startsWith('std:')) {
            this._orbSpawn('std', c.grp.position, parseFloat(ev.tipo.slice(4)), 'enemigo');
          } else {
            this._orbSpawn(ev.tipo, c.grp.position, null, 'enemigo');
          }
        }
      }
    }
    /* ciclo del cañón activo: 8 s → siguiente */
    if (this.jefeCanonT <= 0) this._canonSiguiente();
  }

  _canonSiguiente() {
    this.jefeCanonT = ESC_CFG.jefe.canonT;
    const orden = [0, 1, 2];
    const cur = this.jefeCanon;
    for (const i of orden) {
      if (i === cur) continue;
      const c = this.canones[i];
      if (!c.dead) {
        if (cur >= 0) this.canones[cur].tip.material.emissiveIntensity = 0.15;
        this.jefeCanon = i;
        c.grp.visible = true;
        c.tip.material.emissiveIntensity = 1.7;   // resplandor verde: activo
        c.volT = ESC_CFG.jefe.cadencia;
        c.cola.length = 0;
        this._hudKey = '';
        return;
      }
    }
  }

  _jefeCanonDano(c, dano, clean) {
    const g = this.game;
    c.hp -= dano;
    this._flash(c.grp.position, clean ? 0xffd257 : 0x9fe8ff, clean ? 1.2 : 0.8);
    try { g.audio.playOsc(clean ? 760 : 520, clean ? 980 : 620, 0.08, 'square', 0.2, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, clean ? 0.7 : 0.5, 90);
    if (c.hp <= 0) {
      c.dead = true;
      c.grp.visible = false;
      this._frags(c.grp.position, 14, 0xffb84d);
      this._flash(c.grp.position, 0xffb84d, 1.8);
      try { g.audio.playNoise(0.4, 220, 0.5, 0.22, 0); } catch (e0) { /* */ }
      if (this.jefeCanon === this.canones.indexOf(c)) this.jefeCanonT = 0;   // pasa al siguiente
      this._hudKey = '';
      this._compruebaFase();
    }
  }

  _jefeExplosion() {
    const g = this.game;
    for (let i = 0; i < 5; i++) {
      const p = this._tmpA.set((Math.random() - 0.5) * 3.6,
        ESC_CFG.jefe.y + (Math.random() - 0.5) * 1.6, ESC_CFG.jefe.z + Math.random());
      this._flash(p, i % 2 ? 0xffb84d : 0x9fe8ff, 1.4 + Math.random());
      this._frags(p, 6, 0xffb84d);
    }
    this.jefe.visible = false;
    this.jefeOn = false;
    try { g.audio.playNoise(0.9, 160, 0.6, 0.26, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(220, 60, 0.8, 'sawtooth', 0.2, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 1.0, 300);
      window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.7, 200); } catch (e1) { /* */ } }, 420);
    }
  }

  /** Comprueba si la fase termina (victoria de fase tiene prioridad). */
  _compruebaFase() {
    if (!this.active || this.phase !== 'combate') return;
    const F = ESC_CFG.fases[this.fase];
    if (F.jefe) {
      for (const c of this.canones) if (!c.dead) return;
      this._finish(true);                    // tercer cañón → victoria INMEDIA
    } else {
      for (const d of this.drones) if (d.alive) return;
      if (F.centinela && !this.centDead) return;
      this._faseCompleta();
    }
  }

  /* ---------------- orbes de plasma (sección 8) ---------------- */
  _orbLibre() {
    for (const o of this.orbes) if (!o.alive) return o;
    return null;
  }

  /** Lanza un orbe enemigo desde `from` (dron/cañón/centinela). Con
   *  abanico ≠ null desvía el rumbo ±ángulo (patrón del cañón derecho). */
  _orbSpawn(tipo, from, abanico, owner) {
    const o = this._orbLibre();
    if (!o) return;
    const g = this.game;
    const T = ESC_CFG.orb[tipo] || ESC_CFG.orb.std;
    o.alive = true;
    o.owner = 'enemigo';
    o.tipo = tipo;
    o.r = T.r;
    o.mesh.scale.setScalar(T.r);
    o.glow.scale.setScalar(T.r * 7);
    o.mat.color.setHex(T.col);
    o.mat.emissive.setHex(T.col);
    o.glow.material.color.setHex(T.col);
    o.mesh.visible = true;
    o.glow.visible = true;
    o.mesh.position.copy(from);
    o.mesh.position.z += 0.34;               // boca del dron/cañón
    o.prev.copy(o.mesh.position);
    o.vel.set(0, 0, 0);
    o.lifeT = 0;
    o.dist = 0;
    o.fuse = tipo === 'inest' ? ESC_CFG.orb.inest.fusible : -1;
    o.spinS = tipo === 'rotor' ? (Math.random() < 0.5 ? -1 : 1) : 0;
    o.clean = false;
    o.perf = false;
    o.rebote = false;
    o.blink = 0;
    /* objetivo: punto aleatorio de la zona de ataque, FUERA de la zona
     * segura de cabeza (cilindro de 0,35 m alrededor de la cabeza) */
    g.camera.getWorldPosition(this._tmpC);
    const H = ESC_CFG.headSafeR + T.r + 0.12;
    let tx = 0, ty = 1.2;
    for (let i = 0; i < 10; i++) {
      tx = (Math.random() * 2 - 1) * ESC_CFG.ataque.xMax;
      ty = ESC_CFG.ataque.yMin + Math.random() * (ESC_CFG.ataque.yMax - ESC_CFG.ataque.yMin);
      const dx = tx - this._tmpC.x, dy = ty - this._tmpC.y;
      if (dx * dx + dy * dy > H * H) break;
      tx = (tx >= 0 ? 1 : -1) * ESC_CFG.ataque.xMax;   // borde lateral: seguro
      break;
    }
    this._tmpA.set(tx, ty, 0).sub(o.mesh.position).normalize();
    if (abanico) {                            // abanico ±12° del cañón derecho
      const a = abanico * Math.PI / 180;
      const cs = Math.cos(a), sn = Math.sin(a);
      this._tmpB.set(this._tmpA.x * cs - this._tmpA.z * sn, this._tmpA.y,
        this._tmpA.x * sn + this._tmpA.z * cs);
      this._tmpA.copy(this._tmpB);
    }
    const F = ESC_CFG.fases[this.fase];
    let v = T.v;
    if (tipo === 'std') v = T.v[Math.min(this.fase, 2)];
    o.vel.copy(this._tmpA).multiplyScalar(v);
    try { g.audio.playOsc(500, 180, 0.09, 'square', 0.12, 0); } catch (e) { /* */ }
    this._hudKey = '';
  }

  _orbesStep(dt) {
    const SUB = 4, h = dt / SUB;
    if (this._cdT > 0) this._cdT -= dt;
    for (const o of this.orbes) {
      if (!o.alive) continue;
      for (let s = 0; s < SUB && o.alive; s++) {
        o.prev.copy(o.mesh.position);
        /* ROTOR: trayectoria curvada (hasta 0,6 m en el recorrido) */
        if (o.spinS) {
          this._tmpA.set(-o.vel.z, 0, o.vel.x).normalize()
            .multiplyScalar(ESC_CFG.orb.rotor.curvaAcc * o.spinS * h);
          o.vel.add(this._tmpA);
        }
        o.mesh.position.addScaledVector(o.vel, h);
        o.lifeT += h;
        o.dist += o.vel.length() * h;
        /* INESTABLE: fusible 2,5 s con pulso cada vez más rápido */
        if (o.fuse >= 0) {
          o.fuse -= h;
          const k = 1 - Math.max(0, o.fuse) / ESC_CFG.orb.inest.fusible;
          o.blink += h * (5 + k * 26);
          o.mat.emissiveIntensity = 1.2 + (Math.sin(o.blink) > 0 ? k * 1.8 : 0);
          o.glow.material.opacity = 0.45 + (Math.sin(o.blink) > 0 ? 0.35 : 0);
          if (o.fuse <= 0) { this._orbExplota(o); break; }
        }
        /* vida: 8 s o 25 m */
        if (o.lifeT > ESC_CFG.vidaOrbe || o.dist > ESC_CFG.distOrbe) { this._orbMuere(o); break; }
        /* PALA: barrido del segmento prev→cur (esfera de la pala) */
        this._paddleHit(o);
        if (!o.alive) break;
        /* COLISIONES por dueño */
        if (o.owner === 'enemigo') this._impactsEnemigo(o);
        else this._impactsJugador(o);
      }
      if (o.alive) {
        o.glow.position.copy(o.mesh.position);
        o.mesh.rotation.y += 0.1;
      }
    }
  }

  /** Golpe de la PALA: el MISMO barrido esfera–pala del núcleo (CCD1,
   *  espacio local de la hoja) vía window.__PP_PADDLE_SWEEP — la física
   *  habitual de rebote, rozamiento y efecto (spin) con la pala mandando,
   *  sin corrección de dirección (secciones 1 y 8 de la especificación).
   *  Respaldo: bumper esfera-grip (patrón REACTOR) si el puente no existe. */
  _paddleHit(o) {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (!ps || !ps.active || !ps.pos) return;
    if (this._cdO === o && this._cdT > 0) return;
    if (typeof window === 'undefined' || !window.__PP_PADDLE_SWEEP) {
      return this._paddleHitRespaldo(o, ps);
    }
    this._evts.length = 0;
    const hit = window.__PP_PADDLE_SWEEP(o, o.prev, ps, this._evts);
    if (!hit || !this._evts.length) return;    // micro-contacto mudo: nada
    this._cdO = o; this._cdT = 0.22;
    const ev = this._evts[this._evts.length - 1];
    const closing = ev.speed || 0;             // velocidad normal de cierre
    const cp = this._tmpE.copy(ev.pos);        // centro del orbe en el contacto
    /* GOLPE LIMPIO: contacto en la zona dulce (disco central de la cara,
     * radio 3,5 cm — ampliado por el radio del orbe) + ≥4 m/s (sección 7) */
    let clean = false;
    if (closing >= ESC_CFG.cleanV) {
      this._bladeCentro(ps, this._tmpA);
      if (this._tmpA.distanceTo(cp) <= ESC_CFG.sweetR + o.r) clean = true;
    }
    /* SOBRECARGA completa + golpe firme ≥3 m/s → ORBE PERFORANTE */
    if (this.sobrecarga >= 1 && closing >= ESC_CFG.perforanteV) {
      o.perf = true;
      o.clean = true;
      this.sobrecarga = 0;
      o.mat.color.setHex(0xffe27a);
      o.mat.emissive.setHex(0xffe27a);
      o.glow.material.color.setHex(0xffe27a);
      o.vel.multiplyScalar(1.12);
      this._flash(cp, 0xffe27a, 1.5);
      this._msgNova(tx('¡ORBE PERFORANTE! Atravesará todo núcleo en su camino.',
        'PIERCING ORB! It will pierce every core in its path.'), 2.4);
      try { g.audio.playOsc(880, 1400, 0.22, 'sawtooth', 0.2, 0); } catch (e) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 160);
    } else if (clean) {
      o.clean = true;
      this.sobrecarga = Math.min(1, this.sobrecarga + ESC_CFG.cleanBonus);
      if (this.sobrecarga >= 1) {
        this._msgNova(tx('PALA CARGADA: el próximo golpe firme lanza un orbe perforante.',
          'PADDLE CHARGED: the next firm hit fires a piercing orb.'), 3);
        try { g.audio.playOsc(700, 1050, 0.18, 'square', 0.18, 0); } catch (e0) { /* */ }
      }
      this._flash(cp, 0xffd257, 0.9);
      try { g.audio.playOsc(760, 1180, 0.07, 'square', 0.18, 0); } catch (e1) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.62, 80);
    } else {
      o.clean = false;
      /* golpe válido (sucio/canto/mango): también devuelve el orbe */
      this._flash(cp, 0x9fe8ff, 0.6);
      try { g.audio.playOsc(430, 620, 0.06, 'square', 0.2, 0); } catch (e2) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.45, 60);
    }
    o.owner = 'jugador';
    o.lifeT = 0;
    o.dist = 0;
    this._hudKey = '';
    /* rally: un rebote del Centinela que vuelvo a devolver suma (sección 9.2) */
    if (o.rebote) {
      o.rebote = false;
      if (this.centOn) this._rallySube();
    }
  }

  /** Respaldo (sin puente): bumper esfera-grip con la velocidad de la pala. */
  _paddleHitRespaldo(o, ps) {
    const g = this.game;
    const rr = 0.085 + o.r + (ps.extraReach || 0);
    this._tmpA.copy(o.mesh.position).sub(o.prev);
    const dist2 = this._tmpA.lengthSq();
    let t = 0;
    if (dist2 > 1e-9) {
      this._tmpD.copy(ps.pos).sub(o.prev);
      t = Math.max(0, Math.min(1, this._tmpD.dot(this._tmpA) / dist2));
    }
    this._tmpC.copy(o.prev).addScaledVector(this._tmpA, t);
    if (this._tmpC.distanceToSquared(ps.pos) > rr * rr) return;
    const n = this._tmpD.copy(this._tmpC).sub(ps.pos);
    if (n.lengthSq() < 1e-6) n.set(0, 0.2, -1);
    n.normalize();
    const into = o.vel.dot(n);
    if (into < 0) o.vel.addScaledVector(n, -2 * into);
    o.vel.multiplyScalar(o.tipo === 'pesado' ? ESC_CFG.orb.pesado.restit : 0.42);
    if (ps.vel) o.vel.addScaledVector(ps.vel, 0.85);
    const sp = o.vel.length();
    if (sp < ESC_CFG.devMin) o.vel.multiplyScalar(ESC_CFG.devMin / Math.max(sp, 0.01));
    else if (sp > ESC_CFG.devMax) o.vel.multiplyScalar(ESC_CFG.devMax / sp);
    o.clean = false;
    o.owner = 'jugador';
    o.lifeT = 0; o.dist = 0;
    this._flash(this._tmpC, 0x9fe8ff, 0.6);
    try { g.audio.playOsc(430, 620, 0.06, 'square', 0.2, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.45, 60);
    this._hudKey = '';
  }

  _rallySube() {
    this.rally++;
    this._hudKey = '';
    if (this.rally >= ESC_CFG.cent.rallyParaAbrir) {
      this.rally = 0;
      this.centSobreT = ESC_CFG.cent.sobreT;
      this.centShield.material.opacity = 0.14;
      this._flash(this.cent.position, 0x35ff9d, 1.4);
      this._msgNova(tx('¡Escudo del Centinela sobrecalentado! Núcleo expuesto.',
        'Sentinel shield overheated! Core exposed.'), 2.6);
      try { this.game.audio.playOsc(700, 900, 0.2, 'square', 0.2, 0); } catch (e) { /* */ }
    }
  }

  /* impactos de orbes ENEMIGOS: barrera de casco (único objetivo) */
  _impactsEnemigo(o) {
    const g = this.game;
    const R = ESC_CFG.room;
    if (o.mesh.position.z >= ESC_CFG.barrera.z - o.r) {
      /* ONDA visible en el punto exacto de impacto (sección 4) */
      this._onda(o.mesh.position);
      const T = ESC_CFG.orb[o.tipo] || ESC_CFG.orb.std;
      this._cascoDano(o.tipo === 'inest' ? ESC_CFG.orb.inest.danoExp : T.dano);
      /* rebote del Centinela que el jugador no devuelve → rally a 0 */
      if (o.rebote) { o.rebote = false; this.rally = 0; this._hudKey = ''; }
      this._orbMuere(o);
      return;
    }
    if (o.mesh.position.z > R.bz || o.mesh.position.z < R.fz ||
        Math.abs(o.mesh.position.x) > R.hx || o.mesh.position.y > R.hh ||
        o.mesh.position.y < 0.05) {
      this._orbMuere(o);                     // fuera del volumen: se disipa
    }
  }

  /* impactos de orbes DEVUELTOS: enemigos, escudo del Centinela, jefe */
  _impactsJugador(o) {
    const g = this.game;
    const R = ESC_CFG.room;
    const sp = o.vel.length();
    /* DRONES: destrucción por colisión válida (núcleo 0,3 m; el pesado a
     * ≥8 m/s derriba con el cuerpo). Un orbe ENEMIGO nunca daña a drones. */
    for (const d of this.drones) {
      if (!d.alive) continue;
      let hitR = 0.3 + o.r;
      if (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.derribaV) hitR = 0.55 + o.r;
      if (o.perf) hitR = 0.44 + o.r;
      this._tmpA.copy(o.mesh.position).sub(d.pos);
      if (this._tmpA.lengthSq() > hitR * hitR) continue;
      this._dronMuere(d);
      if (!o.perf) { this._orbMuere(o); return; }   // el perforante atraviesa
      continue;
    }
    /* CENTINELA: escudo (rebote) o núcleo (expuesto / pesado 14+ / perforante) */
    if (this.centOn) {
      const cen = this.cent.position;
      if (this.centSobreT <= 0) {
        /* escudo cerrado: plano del cuenco a +0,45 del centro */
        const planoZ = cen.z + 0.45;
        if (o.prev.z > planoZ && o.mesh.position.z <= planoZ) {
          const f = (o.prev.z - planoZ) / Math.max(1e-6, o.prev.z - o.mesh.position.z);
          const hx = o.prev.x + (o.mesh.position.x - o.prev.x) * f;
          const hy = o.prev.y + (o.mesh.position.y - o.prev.y) * f;
          const dx = hx - cen.x, dy = hy - cen.y;
          if (dx * dx + dy * dy <= (ESC_CFG.cent.shieldR + o.r) * (ESC_CFG.cent.shieldR + o.r)) {
            const atraviesa = (o.perf ||
              (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.atraviesaV));
            if (!atraviesa) {
              this._eraRebote = o;
              o.mesh.position.set(hx, hy, planoZ + 0.02);
              this._centRebota(o);
              return;
            }
            /* el pesado a ≥14 m/s y el perforante ATRAVIESAN el escudo */
          }
        }
      }
      /* núcleo */
      this._tmpA.copy(o.mesh.position).sub(cen);
      const coreR = ESC_CFG.cent.coreR + o.r;
      if (this._tmpA.lengthSq() <= coreR * coreR &&
          (this.centSobreT > 0 || o.perf ||
           (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.atraviesaV))) {
        this._centMuere();
        if (!o.perf) { this._orbMuere(o); return; }
      }
    }
    /* JEFE: cañones — sólo el ACTIVO recibe daño; los cerrados son inmunes
     * (incluso el perforante: está protegido, sección 19). */
    if (this.jefeOn && this.jefeCanon >= 0) {
      for (let i = 0; i < 3; i++) {
        const c = this.canones[i];
        if (c.dead || i !== this.jefeCanon) continue;
        this._tmpA.copy(o.mesh.position).sub(c.grp.position);
        const hitR = ESC_CFG.jefe.canonR + o.r;
        if (this._tmpA.lengthSq() > hitR * hitR) continue;
        this._jefeCanonDano(c, o.perf ? 2 : (o.clean ? 2 : 1), o.clean && !o.perf);
        if (!o.perf) { this._orbMuere(o); return; }
        continue;                              // el perforante sigue
      }
    }
    /* paredes: orbe devuelto que no impacta nada se disipa al llegar a la
     * pared del frente; si llega a la BARRERA, falla y el rally cae a 0. */
    if (o.mesh.position.z <= R.fz + o.r) { this._orbMuere(o); return; }
    if (o.mesh.position.z >= ESC_CFG.barrera.z - o.r) {
      if (this.rally > 0) { this.rally = 0; this._hudKey = ''; }
      this._orbMuere(o);
      return;
    }
    if (o.mesh.position.z > R.bz || Math.abs(o.mesh.position.x) > R.hx ||
        o.mesh.position.y > R.hh || o.mesh.position.y < 0.05) this._orbMuere(o);
  }

  _cascoDano(dano) {
    const g = this.game;
    this.hull = Math.max(0, this.hull - dano);
    if (this.hull <= ESC_CFG.alertaUmbral && !this.alerta) {
      this.alerta = true;
      this._msgNova(tx('ALERTA CRÍTICA: integridad del casco al ' + this.hull + ' %.',
        'CRITICAL ALERT: hull integrity at ' + this.hull + ' %.'), 2.8);
    }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.85, 150);
    this._hudKey = '';
    if (this.hull <= 0 && this.phase === 'combate') this._finish(false);
  }

  /** El orbe INESTABLE explota (fusible): radio 1,5 m — destruye drones
   *  cercanos (cada uno una vez); si es enemigo y explota a <2 m del
   *  jugador, daña el casco. Sólo efectos visuales en el resto. */
  _orbExplota(o) {
    const g = this.game;
    const E = ESC_CFG.orb.inest;
    this._flash(o.mesh.position, 0xff6a4d, 2.2);
    try { g.audio.playNoise(0.5, 180, 0.5, 0.22, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(180, 60, 0.35, 'sawtooth', 0.16, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 110);
    for (const d of this.drones) {
      if (!d.alive) continue;
      if (d.pos.distanceTo(o.mesh.position) <= E.radioExp + 0.3) this._dronMuere(d);
    }
    if (o.owner === 'enemigo') {
      g.camera.getWorldPosition(this._tmpA);
      if (this._tmpA.distanceTo(o.mesh.position) < E.cercaJugador ||
          o.mesh.position.z >= ESC_CFG.barrera.z) {
        this._onda(o.mesh.position);
        this._cascoDano(E.danoExp);
      }
    }
    this._orbMuere(o);
  }

  _orbMuere(o, disolv) {
    o.alive = false;
    o.mesh.visible = false;
    o.glow.visible = false;
    if (this._cdO === o) { this._cdO = null; }
    if (this._eraRebote === o) this._eraRebote = null;
    if (disolv) this._flash(o.mesh.position, 0x9fe8ff, 0.5);
  }

  /* ---------------- FX (pools, exclusivamente visuales) ---------------- */
  _flash(p, col, size) {
    for (const f of this.flashes) {
      if (f.t < 0.4) continue;
      f.t = 0;
      f.m.visible = true;
      f.m.position.copy(p);
      f.m.material.color.setHex(col);
      f.m.scale.setScalar(size);
      f.m.material.opacity = 0.9;
      f.m.quaternion.copy(this.game.camera.quaternion);
      return;
    }
  }

  _frags(p, n, col) {
    let usados = 0;
    for (const f of this.frags) {
      if (usados >= n) break;
      if (f.t < 0.95) continue;
      f.t = 0;
      usados++;
      f.m.visible = true;
      f.m.position.copy(p);
      f.m.material.color.setHex(col);
      f.m.material.emissive.setHex(col);
      f.m.material.opacity = 1;
      f.vel.set((Math.random() - 0.5) * 3.2, Math.random() * 2.6, (Math.random() - 0.5) * 3.2);
    }
  }

  /** Onda de la Barrera de Casco en el punto exacto del impacto. */
  _onda(p) {
    for (const w of this.ondas) {
      if (w.t < 0.55) continue;
      w.t = 0;
      w.m.visible = true;
      w.m.position.set(p.x, Math.max(0.5, Math.min(3.4, p.y)), ESC_CFG.barrera.z + 0.06);
      w.m.material.opacity = 0.85;
      w.m.scale.setScalar(0.2);
      return;
    }
  }

  _anims(dt) {
    for (const f of this.flashes) {
      if (f.t > 0.4) continue;
      f.t += dt;
      f.m.material.opacity = Math.max(0, 0.9 * (1 - f.t / 0.4));
      f.m.scale.multiplyScalar(1 + dt * 3.4);
      if (f.t >= 0.4) f.m.visible = false;
    }
    for (const f of this.frags) {
      if (f.t > 0.95) continue;
      f.t += dt;
      f.vel.y -= 2.6 * dt;                   // gravedad suave de escombros
      f.m.position.addScaledVector(f.vel, dt);
      f.m.material.opacity = Math.max(0, 1 - f.t / 0.95);
      f.m.rotation.x += dt * 6; f.m.rotation.y += dt * 4;
      if (f.t >= 0.95) f.m.visible = false;
    }
    for (const w of this.ondas) {
      if (w.t > 0.55) continue;
      w.t += dt;
      const k = w.t / 0.55;
      w.m.scale.setScalar(0.2 + k * 2.6);
      w.m.material.opacity = 0.85 * (1 - k);
      if (w.t >= 0.55) w.m.visible = false;
    }
    /* plataforma y barrera respiran */
    this.plataforma.children[0].material.opacity = 0.42 + Math.sin(this._t * 2.4) * 0.16;
    this.barreraMat.opacity = 0.30 + Math.sin(this._t * 3.1) * 0.07;
    /* pulso del cañón activo del jefe */
    if (this.jefeOn && this.jefeCanon >= 0) {
      const tip = this.canones[this.jefeCanon].tip;
      tip.material.emissiveIntensity = 1.5 + Math.sin(this._t * 8) * 0.45;
    }
    /* glow de PALA CARGADA flotando junto a la hoja */
    const psG = this.game.controllerPaddles && this.game.controllerPaddles[this.game.paddleHand];
    if (this.sobrecarga >= 1 && psG && psG.active) {
      this._bladeCentro(psG, this._tmpA);
      if (!this.cargaGlow) {
        this.cargaGlow = new THREE.Sprite(new THREE.SpriteMaterial({
          map: this._glowTex(), color: 0xffe27a, transparent: true, opacity: 0.85,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }));
        this.cargaGlow.renderOrder = 30;
        this.game.scene.add(this.cargaGlow);
      }
      this.cargaGlow.visible = true;
      this.cargaGlow.position.copy(this._tmpA);
      this.cargaGlow.scale.setScalar(0.3 + Math.sin(this._t * 6) * 0.06);
    } else if (this.cargaGlow) {
      this.cargaGlow.visible = false;
    }
  }

  /* ---------------- pantalla informativa (sección 12) ---------------- */
  _hudDirty() {
    const F = ESC_CFG.fases[this.fase];
    let enem = '';
    if (this.phase === 'combate') {
      if (F.jefe) {
        let vivos = 0;
        for (const c of this.canones) if (!c.dead) vivos++;
        enem = 'CAN' + vivos;
      } else {
        let vivos = 0;
        for (const d of this.drones) if (d.alive) vivos++;
        if (this.centOn) vivos++;
        const total = F.drones + (F.centinela || 0);
        enem = 'EN' + vivos + '/' + total;
      }
    }
    const key = this.phase + '|' + this.fase + '|' + this.hull + '|' + enem + '|' +
      Math.round(this.sobrecarga * 100) + '|' + this.rally + '|' +
      (this._msgT > 0 ? this._msg : '') + '|' + (this._banner ? this._banner.title : '') +
      '|' + (this.centSobreT > 0 ? 'S' : '') + '|' + Math.round(this.faseT);
    if (key === this._hudKey) return;
    this._hudKey = key;
    this._pantalla();
  }

  _msgNova(txt, t) {
    this._msg = txt;
    this._msgSub = 'NOVA · ';
    this._msgT = t || ESC_CFG.msgT;
    this._hudKey = '';
  }

  _pantalla() {
    const c = this.panCv.getContext('2d');
    const W = this.panCv.width, H = this.panCv.height;
    c.clearRect(0, 0, W, H);
    if (this._panImg) {
      c.globalAlpha = 0.96;
      c.drawImage(this._panImg, 0, 0, W, H);
      c.globalAlpha = 1;
    } else {
      c.fillStyle = 'rgba(8,16,30,0.92)';
      c.fillRect(0, 0, W, H);
    }
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    /* cabecera */
    c.fillStyle = '#ffd257';
    c.font = '800 44px system-ui, sans-serif';
    c.fillText('DEFENSA DEL CASCO · NAVE ORBITAL', W / 2, 86);
    const F = ESC_CFG.fases[this.fase];
    const enCombate = this.phase === 'combate';
    /* fila 1: fase + integridad */
    c.font = '700 40px system-ui, sans-serif';
    c.fillStyle = '#e8f2ff';
    c.fillText('FASE ' + (this.fase + 1) + ' / 3', 280, 208);
    const crit = this.hull <= ESC_CFG.alertaUmbral;
    c.fillStyle = crit ? '#ff5a4d' : '#7fd8a8';
    c.fillText('INTEGRIDAD DEL CASCO: ' + Math.round(this.hull) + ' %', 700, 208);
    /* fila 2: enemigos + sobrecarga */
    c.fillStyle = '#e8f2ff';
    if (F.jefe) {
      let vivos = 0;
      for (const cc of this.canones) if (!cc.dead) vivos++;
      c.fillText('CAÑONES: ' + vivos + ' / 3', 280, 296);
    } else {
      let vivos = 0;
      for (const d of this.drones) if (d.alive) vivos++;
      if (this.centOn) vivos++;
      const total = F.drones + (F.centinela || 0);
      c.fillText('ENEMIGOS RESTANTES: ' + vivos + ' / ' + total, 330, 296);
    }
    c.fillStyle = this.sobrecarga >= 1 ? '#ffe27a' : '#8fb8d8';
    c.fillText('SOBRECARGA: ' + Math.round(this.sobrecarga * 100) + ' %', 760, 296);
    /* fila 3: estado + rally */
    const estado = this.phase === 'prep' ? 'PREPARACIÓN'
      : this.phase === 'inter' ? 'REPARACIONES'
      : this.phase === 'result' ? (this._win ? 'VICTORIA' : 'DERROTA')
      : (this.centSobreT > 0 ? '¡NÚCLEO EXPUESTO!' : 'COMBATE');
    c.fillStyle = this.centSobreT > 0 ? '#35ff9d' : '#e8f2ff';
    c.fillText('ESTADO: ' + estado, 330, 384);
    if (this.centOn) {
      c.fillStyle = '#8fe4ff';
      c.fillText('RALLY: ' + this.rally + ' / ' + ESC_CFG.cent.rallyParaAbrir, 760, 384);
    }
    /* mensaje de NOVA (capa independiente, abajo) */
    if (this._msgT > 0 && this._msg) {
      c.fillStyle = 'rgba(6,12,24,0.72)';
      c.fillRect(60, 470, W - 120, 108);
      c.strokeStyle = 'rgba(120,200,255,0.5)';
      c.lineWidth = 2;
      c.strokeRect(60, 470, W - 120, 108);
      c.fillStyle = '#9fd8ff';
      c.font = '700 24px system-ui, sans-serif';
      c.fillText((this._msgSub || '') + 'NOVA', W / 2, 498);
      c.fillStyle = '#f2f8ff';
      c.font = '600 27px system-ui, sans-serif';
      const palabras = String(this._msg).split(' ');
      let linea = '', y = 538;
      const lineas = [];
      for (const p of palabras) {
        if ((linea + ' ' + p).trim().length > 64) { lineas.push(linea.trim()); linea = p; }
        else linea += ' ' + p;
      }
      if (linea.trim()) lineas.push(linea.trim());
      for (const ln of lineas.slice(0, 2)) { c.fillText(ln, W / 2, y); y += 32; }
    }
    /* banner de preparación / resultado */
    const b = this._banner;
    if (b && this.phase === 'result') {
      c.fillStyle = 'rgba(6,10,20,0.78)';
      c.fillRect(150, 150, W - 300, 220);
      c.strokeStyle = b.col;
      c.lineWidth = 4;
      c.strokeRect(150, 150, W - 300, 220);
      c.fillStyle = b.col;
      c.font = '900 62px system-ui, sans-serif';
      c.fillText(b.title, W / 2, 235);
      c.fillStyle = '#e8f2ff';
      c.font = '700 34px system-ui, sans-serif';
      c.fillText(b.sub || '', W / 2, 308);
    } else if (this.phase === 'prep') {
      c.fillStyle = 'rgba(6,10,20,0.78)';
      c.fillRect(150, 150, W - 300, 220);
      c.strokeStyle = '#ff5a4d';
      c.lineWidth = 4;
      c.strokeRect(150, 150, W - 300, 220);
      c.fillStyle = '#ff5a4d';
      c.font = '900 66px system-ui, sans-serif';
      c.fillText('⚠ ALERTA DE ABORDAJE', W / 2, 228);
      c.fillStyle = '#e8f2ff';
      c.font = '700 32px system-ui, sans-serif';
      c.fillText(tx('Activa el escudo manual: tu pala es la defensa', 'Activate the manual shield: your paddle is the defense'), W / 2, 300);
    }
    this.panTex.needsUpdate = true;
  }
}

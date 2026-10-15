/* ============================================================================
 *  Estación Orbital (estacion_orbital) — v3.1 «PLANTILLA FINAL» (V2.131)
 *  ----------------------------------------------------------------------------
 *  v3.2 (V2.132) · «LOS PODERES YA MANDAN» — informe del casco: sin cartels
 *    de superpoder y efectos que no llegan + prueba con la bola inalcanzable.
 *    (1) DISPARO REDUNDANTE: el gancho por PUNTO (onPoint) se queda, pero
 *    el update() dispara también por RALLY (bola viniendo al jugador, patrón
 *    Locura que SÍ funciona en el casco) y con GARANTÍA a los 22 s de duelo
 *    sin poderes (red anti-silencio). (2) CARTEL DEL SUPERPODER con el
 *    medallón + nombre (el «identificador» que el jugador espera): fase
 *    AVISO ámbar «AX-9 PREPARA…» y fase ACTIVA cian. (3) _poderArrancar
 *    blindado: un efecto que falle ya no cuelga la bolsa para siempre.
 *    (4) DIANAS 3D DE VERDAD: asteroide = icosaedro con ruido por vértice
 *    (facetas creíbles, nada de sprites planos), caja blindada = contenedor
 *    metálico con aristas ámbar, núcleo brillante y escudo esférico, dron =
 *    fuselaje + cabina + 4 rotores girando. (5) BOLA-ESPERA ALCANZABLE:
 *    HOLD pasa de z=-0.90 (0,67 m DENTRO de la mesa — inalcanzable, era el
 *    motivo de «imposible destruir los asteroides») a z=-0.50, junto al
 *    borde del jugador (convención Magia tableNearZ−0.38).
 *  v3.1 (V2.131) · FIX RAÍZ del informe del jugador «EO no tiene superpoderes
 *    en las etapas 1/3/5 ni pruebas de habilidad en las 2/4»: el módulo NUNCA
 *    ponía rules.state='champtest' en la SALA. El núcleo sólo enruta el
 *    gatillo al módulo con ese estado (convención oeste/magia: el árbitro
 *    duerme en la sala de espera), así que el gatillo ejecutaba el SAQUE
 *    CLÁSICO: se jugaban partidos normales sin duelo real (sin superpoderes
 *    porque ctrl.state nunca llegaba a 'duelo') y sin pruebas (serveTrigger
 *    jamás llamado). Ahora TODA transición a sala/prueba duerme al árbitro:
 *    startChamp, _empezarPrueba, _despuesDePrueba, onMatchOver (normal y
 *    rejugada — que además ahora SÍ cierra el duelo), reenter y leave
 *    (restitución del árbitro al salir, convención magia). La pala IA sólo
 *    existe en DUELO (en sala manda el standee del AX-9).
 *  ----------------------------------------------------------------------------
 *  Upgrade integral del campeonato plantilla (contrato 1):
 *    · CAMINO DE 5 ETAPAS: duelo → PRUEBA → duelo → PRUEBA → DUELO FINAL
 *      (patrón magia v2.70: la prueba se intercala entre duelos)
 *    · PRUEBAS DE HABILIDAD «DIANAS ORBITALES» (motor propio): física del
 *      núcleo vía stepPhysics + colisionador extra por SUBPASO (anti-túnel,
 *      patrón orbe de Magia), árbitro dormido con rules.state='champtest',
 *      bola en bote-en-espera hasta el primer golpe, cartel explicativo del
 *      núcleo ANTES de entrar (regla v2.106 de todas las pruebas)
 *    · 4 SUPERPODERES del AX-9 (bolsa rotatoria, motor de dos fases):
 *        LLUVIA DE ESTRELLAS (confeti con textura de estrella)
 *        METEORITOS      (rocas caen a TU campo y bloquean la bola, patrón
 *                         Burla v2.127: cruce del segmento prev→actual)
 *        RAYO TRACTOR    (haz del rival que curva la bola hacia el centro)
 *        GRAVEDAD CERO   (la bola flota en ondas verticales)
 *    · ARTE completo del artista PIL (sala 6 planos, AX-9 5 estados,
 *      troqueles, medallones de poder, dianas)
 *    · v2.128 intacto: insignia ¡CONSEGUIDO!, ★ SUPERADO, ranking, campeón
 *      con revancha libre, restauración de progreso (ahora también ETAPA)
 *  Superficie usada (scripts/plataforma/AUDITORIA.md): __PP_CORE solo
 *  lectura, rules.state, audio (playOsc/playNoise/announce), champRoom/
 *  decor por export, __PP_WORLD.submit, haptic, ignoreNet (documentado).
 *  ========================================================================== */
import * as THREE from 'three';   // importmap del núcleo: MISMA instancia

const CORE = (typeof window !== 'undefined' && window.__PP_CORE) || null;
const GAME = { g: null };
let CTRL = null;
let TL = 'es';
let STEP = null;                  // stepPhysics del núcleo (capturado en init)

const tx = (es, en) => (TL === 'en' ? (en || es) : es);

/* ----------------------------- CONFIGURACIÓN ----------------------------- */
const CFG = {
  rival: 'Androide AX-9',
  puntos: 11,
  /* Camino de 5 etapas (índices de etapa 0..4) */
  etapas: [
    { kind: 'duelo', id: 'duelo1', name: 'Duelo 1', aiMul: 0.90 },
    { kind: 'prueba', id: 'cinturon', name: 'Cinturón de asteroides' },
    { kind: 'duelo', id: 'duelo2', name: 'Duelo 2', aiMul: 1.12 },
    { kind: 'prueba', id: 'tormenta', name: 'Tormenta de meteoritos' },
    { kind: 'duelo', id: 'final', name: 'DUELO FINAL', aiMul: 1.42 },
  ],
  /* Superpoderes del AX-9 (máx 4 del esquema) — bolsa rotatoria */
  poderes: [
    { kind: 'confeti', name: 'Lluvia de estrellas', icon: 'assets/powerestrellas.png',
      chance: 0.30, cooldown: 24, duration: 8 },
    { kind: 'custom', name: 'Meteoritos', icon: 'assets/powermeteoritos.png',
      chance: 0.26, cooldown: 30, duration: 11, warn: 2.0, rocas: 3 },
    { kind: 'custom', name: 'Rayo tractor', icon: 'assets/powertractor.png',
      chance: 0.24, cooldown: 32, duration: 7, warn: 2.0 },
    { kind: 'custom', name: 'Gravedad cero', icon: 'assets/powercero.png',
      chance: 0.22, cooldown: 34, duration: 8, warn: 2.0 },
  ],
};

/* cfg de las DOS pruebas (patrón LEVEL + ORBE_COMPLEJO de magia) */
const DIANAS = {
  normal: {
    tiempo: 60, nRocas: 10, nCajas: 0, nDrones: 0,
    orbita: false, escudo: false,
  },
  compleja: {
    tiempo: 70, nRocas: 9, nCajas: 3, nDrones: 2,
    orbita: true, escudo: true, dronBonus: 4,
  },
};

/* v3.2: z=-0.90 quedaba 0,67 m DENTRO de la mesa (borde jugador en -0.23):
 * la bola de espera era INALCANZABLE con la pala («imposible destruir los
 * asteroides»). Ahora espera pegada al borde del jugador, convención Magia
 * (tableNearZ - 0.38 → usamos -0.50, aún más amable). */
const HOLD = { x: 0.26, z: -0.50, T: 0.95, H: 0.42 };   // bote-en-espera

/* ------------------------- TEXTURAS DE CANVAS ---------------------------- */
function _texEstrella() {
  const cv = document.createElement('canvas');
  cv.width = 32; cv.height = 32;
  const c = cv.getContext('2d');
  c.translate(16, 16);
  c.fillStyle = '#ffe27a';
  c.beginPath();
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + Math.PI * i / 5;
    const r = i % 2 === 0 ? 13 : 5.5;
    const x = r * Math.cos(a), y = r * Math.sin(a);
    if (i === 0) c.moveTo(x, y); else c.lineTo(x, y);
  }
  c.closePath();
  c.fill();
  c.fillStyle = '#fff8dc';
  c.beginPath(); c.arc(0, 0, 4, 0, 7); c.fill();
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function _texFlash() {
  const cv = document.createElement('canvas');
  cv.width = 64; cv.height = 64;
  const c = cv.getContext('2d');
  const g = c.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.35, 'rgba(160,240,255,0.9)');
  g.addColorStop(1, 'rgba(120,200,255,0)');
  c.fillStyle = g;
  c.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function _texFragmento() {
  const cv = document.createElement('canvas');
  cv.width = 24; cv.height = 24;
  const c = cv.getContext('2d');
  c.fillStyle = '#968270';
  c.beginPath();
  c.moveTo(4, 14); c.lineTo(9, 4); c.lineTo(19, 7); c.lineTo(21, 17);
  c.lineTo(11, 21); c.closePath();
  c.fill();
  c.fillStyle = '#b7a18c';
  c.fillRect(8, 8, 6, 5);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ============================================================================
 *  DianasOrbitales — LAS PRUEBAS DE HABILIDAD (v3)
 *  ----------------------------------------------------------------------------
 *  Máquina de estados: play → result (banner) → cleanup.
 *  Toma la física con testStep() mientras activa (igual que el orbe de
 *  Magia / ARKANOID de La Locura): rules.state='champtest' duerme al
 *  árbitro y el núcleo deja de integrar la bola principal.
 *  Dianas: SPRITES con el arte del artista (asteroide/caja/dron) con
 *  colisión esférica y barrido por SUBPASO del segmento prev→actual
 *  (ball.__exPrev, patrón orbe): nada de túneles a velocidad de smash.
 *  La bola nace en BOTE-EN-ESPERA (vórtice del jugador) y el primer golpe
 *  de pala la libera (patrón v2.61 de magia). ignoreNet activo durante la
 *  prueba (documentado en AUDITORIA.md, precedente ARKANOID).
 *  ============================================================================ */
class DianasOrbitales {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.built = false;
    this.running = false;         // fase de juego (testActive true)
    this.result = false;          // fase de banner (testActive true también)
    this.compleja = false;
    this.cfg = DIANAS.normal;
    this.targets = [];            // { sp, mat, tipo, r, hp, alive, base, fase, orbit… }
    this.total = 0; this.alive = 0;
    this.tiempo = 0; this.t = 0;
    this.hold = true; this.holdT = 0;
    this.flight = 0; this.deadT = 0;
    this.bannerT = 0;
    this._hudKey = '';
    this._endDone = false;
    this._extra = (ball, events) => this._collide(ball, events);
  }

  _A(p) { return this.ctrl._A(p); }

  /* ------------------------------ ESCENA -------------------------------- */
  build() {
    if (this.built) return;
    this.built = true;
    const g = this.game;
    this.ownTex = new Set();
    this.grp = new THREE.Group();
    this.grp.visible = false;
    g.scene.add(this.grp);

    // texturas compartidas (UNA vez por sesión — viven con el módulo)
    this.texFlash = _texFlash();
    this.texFrag = _texFragmento();
    const carga = (f) => {
      const t = new THREE.TextureLoader().load(this._A(f));
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    };
    this.texRoca1 = carga('asteroide.png');
    this.texRoca2 = carga('asteroide2.png');
    this.texCaja = carga('caja.png');
    this.texDron = carga('dron.png');

    // sprites de dianas creados al vuelo por cfg (≤ 15, material propio)
    this.targets.length = 0;

    // POOL de explosión: destellos + fragmentos (regla Quest: una vez)
    this.fx = [];
    for (let i = 0; i < 22; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.texFlash, transparent: true, depthWrite: false, opacity: 0,
      }));
      s.renderOrder = 30;
      this.grp.add(s);
      this.fx.push({ s, t: 9, life: 0.5, vx: 0, vy: 0, vz: 0, frag: false });
    }
    for (let i = 0; i < 26; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.texFrag, transparent: true, depthWrite: false, opacity: 0,
      }));
      s.renderOrder = 30;
      this.grp.add(s);
      this.fx.push({ s, t: 9, life: 0.9, vx: 0, vy: 0, vz: 0, frag: true });
    }

    // HUD: panel holográfico sobre el fondo de la mesa
    this.hudCv = document.createElement('canvas');
    this.hudCv.width = 640; this.hudCv.height = 150;
    this.hudTex = new THREE.CanvasTexture(this.hudCv);
    this.hudTex.colorSpace = THREE.SRGBColorSpace;
    this.ownTex.add(this.hudTex);
    this.hud = new THREE.Mesh(
      new THREE.PlaneGeometry(1.55, 0.36),
      new THREE.MeshBasicMaterial({ map: this.hudTex, transparent: true, depthWrite: false }));
    const D = (CORE && CORE.DIMS) || { tableCenterZ: -1.6, tableTopY: 0.76 };
    this.hud.position.set(0, D.tableTopY + 1.18, D.tableCenterZ - 1.55);
    this.hud.rotation.x = -0.10;
    this.grp.add(this.hud);

    // BANNER de resultado (oculto hasta el final)
    this.bnCv = document.createElement('canvas');
    this.bnCv.width = 640; this.bnCv.height = 300;
    this.bnTex = new THREE.CanvasTexture(this.bnCv);
    this.bnTex.colorSpace = THREE.SRGBColorSpace;
    this.ownTex.add(this.bnTex);
    this.banner = new THREE.Mesh(
      new THREE.PlaneGeometry(1.7, 0.8),
      new THREE.MeshBasicMaterial({ map: this.bnTex, transparent: true, depthWrite: false }));
    this.banner.position.set(0, D.tableTopY + 1.05, D.tableCenterZ - 0.9);
    this.banner.rotation.x = -0.28;
    this.banner.visible = false;
    this.banner.renderOrder = 40;
    this.grp.add(this.banner);
  }

  /* v3.2 · DIANAS 3D DE VERDAD (petición del jugador: los sprites eran
   * «muy cutres»): asteroide = icosaedro con ruido determinista por vértice
   * + 2 piedras satélite; caja = contenedor metálico con aristas ámbar,
   * núcleo brillante y escudo esférico aditivo; dron = fuselaje con cabina
   * y 4 rotores que giran. Colisión esférica por `r` como antes (el Group
   * respeta .position/.visible — el barrido anti-túnel no cambia). */
  _nuevoTarget(tipo, x, y, z, idx) {
    const grp = new THREE.Group();
    grp.position.set(x, y, z);
    let r = 0.18, mesh = null, escudo = null; const rotores = [];
    if (tipo === 'roca') {
      const R = 0.16 + (idx % 3) * 0.02;
      const geo = new THREE.IcosahedronGeometry(R, 1);
      const p = geo.attributes.position;
      for (let i = 0; i < p.count; i++) {
        const vx = p.getX(i), vy = p.getY(i), vz = p.getZ(i);
        const n = Math.sin(vx * 9.7 + vy * 4.3 + vz * 6.1) * 0.6 +
          Math.sin(vy * 11.3 - vz * 7.9 + vx * 2.9) * 0.4;
        const k = 1 + n * 0.24;
        p.setXYZ(i, vx * k, vy * k, vz * k);
      }
      geo.computeVertexNormals();
      mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: idx % 2 ? 0x8f7d6a : 0x77685a, roughness: 0.96, metalness: 0.04,
        flatShading: true,
      }));
      grp.add(mesh);
      for (let s2 = 0; s2 < 2; s2++) {
        const g2 = new THREE.IcosahedronGeometry(R * 0.28, 0);
        const m2 = new THREE.Mesh(g2, mesh.material);
        const a = s2 * 2.4 + idx * 0.7;
        m2.position.set(Math.cos(a) * R * 0.92, Math.sin(a * 1.7) * R * 0.66, Math.sin(a) * R * 0.92);
        grp.add(m2);
      }
      r = R * 1.18;
    } else if (tipo === 'caja') {
      const geo = new THREE.BoxGeometry(0.30, 0.30, 0.30);
      mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
        color: 0x49566a, roughness: 0.5, metalness: 0.7,
      }));
      grp.add(mesh);
      grp.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo),
        new THREE.LineBasicMaterial({ color: 0xffc247 })));
      grp.add(new THREE.Mesh(new THREE.IcosahedronGeometry(0.07, 1),
        new THREE.MeshBasicMaterial({ color: 0x7ff0ff })));
      if (this.cfg && this.cfg.escudo) {
        escudo = new THREE.Mesh(new THREE.SphereGeometry(0.235, 20, 14),
          new THREE.MeshBasicMaterial({ color: 0x66e0ff, transparent: true,
            opacity: 0.2, blending: THREE.AdditiveBlending, depthWrite: false }));
        grp.add(escudo);
      }
      r = 0.235;
    } else {   // dron
      mesh = new THREE.Mesh(new THREE.SphereGeometry(0.105, 18, 12),
        new THREE.MeshStandardMaterial({ color: 0x39424e, roughness: 0.5, metalness: 0.7 }));
      mesh.scale.set(1, 0.62, 1.25);
      grp.add(mesh);
      const cabina = new THREE.Mesh(new THREE.SphereGeometry(0.055, 14, 10),
        new THREE.MeshBasicMaterial({ color: 0x8ff6ff }));
      cabina.position.set(0, 0.035, 0.078);
      grp.add(cabina);
      for (let q = 0; q < 4; q++) {
        const ax = (q % 2 ? 1 : -1) * 0.135, az = (q < 2 ? 1 : -1) * 0.135;
        const brazo = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.018, 0.022),
          new THREE.MeshStandardMaterial({ color: 0x2b333d, roughness: 0.6, metalness: 0.5 }));
        brazo.position.set(ax * 0.5, 0.012, az * 0.5);
        brazo.rotation.y = Math.atan2(az, ax);
        grp.add(brazo);
        const rotor = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.006, 14),
          new THREE.MeshStandardMaterial({ color: 0x9fb4c8, roughness: 0.4, metalness: 0.6,
            transparent: true, opacity: 0.55 }));
        rotor.position.set(ax, 0.03, az);
        grp.add(rotor);
        rotores.push(rotor);
      }
      r = 0.21;
    }
    this.grp.add(grp);
    return {
      sp: grp, mesh, escudo, rotores, tipo,
      r,
      hp: (tipo === 'caja' && this.cfg.escudo) ? 2 : 1,
      alive: true,
      bx: x, by: y, bz: z,
      fase: Math.random() * Math.PI * 2,
      orbitA: (tipo === 'dron') ? 0.45 : (this.cfg.orbita ? 0.10 : 0.0),
      orbitW: (tipo === 'dron') ? 1.5 : 0.8,
      rollW: tipo === 'caja' ? 0 : (Math.random() < 0.5 ? -1 : 1) * (0.3 + Math.random() * 0.4),
      _hitT: 0,
    };
  }

  /* ------------------------------ CICLO --------------------------------- */
  /** Cartel explicativo ANTES (regla v2.106) lo pinta CTRL; aquí el juego. */
  start(compleja) {
    const g = this.game;
    this.build();
    this.compleja = !!compleja;
    this.cfg = this.compleja ? DIANAS.compleja : DIANAS.normal;
    // limpia dianas previas (v3.2: ahora son MALLAS 3D — dispose completo)
    for (const it of this.targets) {
      this.grp.remove(it.sp);
      try {
        it.sp.traverse((o) => {
          if (o.geometry) { try { o.geometry.dispose(); } catch (e1) { /* */ } }
          if (o.material) {
            const ms = Array.isArray(o.material) ? o.material : [o.material];
            for (const m of ms) { try { m.dispose(); } catch (e2) { /* */ } }
          }
        });
      } catch (e3) { /* */ }
    }
    this.targets.length = 0;

    // posiciones: rejilla 4 filas × 3 carriles SOBRE la mesa, barajada
    // (todas las dianas bien repartidas: sin racimos)
    const D = (CORE && CORE.DIMS) || { tableTopY: 0.76, tableCenterZ: -1.6 };
    const zs = [-1.02, -1.42, -1.82, -2.22];
    const xs = [-0.52, 0.0, 0.52];
    const slots = [];
    for (const z of zs) for (const x of xs) slots.push([x, z]);
    for (let k = slots.length - 1; k > 0; k--) {
      const j = (Math.random() * (k + 1)) | 0;
      [slots[k], slots[j]] = [slots[j], slots[k]];
    }
    let idx = 0;
    const rnd = () => (Math.random() - 0.5);
    const plan = [];
    for (let k = 0; k < this.cfg.nRocas; k++) plan.push('roca');
    for (let k = 0; k < this.cfg.nCajas; k++) plan.push('caja');
    for (let k = 0; k < this.cfg.nDrones; k++) plan.push('dron');
    // barajado determinista simple
    for (let k = plan.length - 1; k > 0; k--) {
      const j = (Math.random() * (k + 1)) | 0;
      [plan[k], plan[j]] = [plan[j], plan[k]];
    }
    for (const tipo of plan) {
      const [sx, sz] = slots[idx % slots.length];
      const x = Math.max(-0.72, Math.min(0.72, sx + rnd() * 0.16));
      const y = D.tableTopY + 0.30 + 0.22 * (idx % 3) + rnd() * 0.06;
      const z = sz + rnd() * 0.10;
      this.targets.push(this._nuevoTarget(tipo, x, y, z, idx));
      idx++;
    }
    this.total = this.alive = this.targets.length;
    this.tiempo = this.cfg.tiempo;
    this.t = 0;
    this.hold = true; this.holdT = 0;
    this.flight = 0; this.deadT = 0;
    this.result = false; this._endDone = false;
    this.banner.visible = false;

    // bola en bote-en-espera (patrón vórtice de magia)
    g.ball.pos.set(HOLD.x, D.tableTopY + 0.12, HOLD.z);
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    g.ballMesh.visible = true;

    // la prueba juega SIN red (documentado: precedente ARKANOID)
    g.ball.ignoreNet = true;
    g.rules.state = 'champtest';       // el árbitro duerme
    this.running = true;
    this.grp.visible = true;
    this._hudKey = '';
    this._pintaHud();
    g.rules.message = tx('¡Destruye las dianas!', 'Destroy the targets!');
    try { g.audio.announce(tx('Prueba', 'Skill test'), true); } catch (e) { /* */ }
  }

  stop() {
    // salida inmediata (leave del campeonato a mitad de prueba)
    if (!this.built) return;
    this.running = false;
    this.result = false;
    const g = this.game;
    try { g.ball.ignoreNet = false; } catch (e) { /* */ }
    if (this.grp) this.grp.visible = false;
  }

  stepActive() { return this.running || this.result; }

  _pintaHud() {
    const c = this.hudCv.getContext('2d');
    const key = Math.ceil(this.tiempo) + '|' + (this.total - this.alive);
    if (key === this._hudKey) return;
    this._hudKey = key;
    c.clearRect(0, 0, 640, 150);
    c.fillStyle = 'rgba(10,16,28,0.86)';
    c.beginPath();
    if (c.roundRect) c.roundRect(6, 6, 628, 138, 26); else c.rect(6, 6, 628, 138);
    c.fill();
    c.strokeStyle = this.tiempo <= 10 ? '#ffb347' : '#4fd8ff';
    c.lineWidth = 6;
    c.beginPath();
    if (c.roundRect) c.roundRect(6, 6, 628, 138, 26); else c.rect(6, 6, 628, 138);
    c.stroke();
    c.textAlign = 'center';
    c.fillStyle = '#eef4ff';
    c.font = 'bold 62px Trebuchet MS, sans-serif';
    c.fillText(tx('DIANAS ', 'TARGETS ') + (this.total - this.alive) + '/' + this.total, 210, 98);
    c.fillStyle = this.tiempo <= 10 ? '#ffb347' : '#7fe8ff';
    c.fillText(Math.ceil(this.tiempo) + ' s', 490, 98);
    this.hudTex.needsUpdate = true;
  }

  _pintaBanner(win, datos) {
    const c = this.bnCv.getContext('2d');
    c.clearRect(0, 0, 640, 300);
    c.fillStyle = win ? 'rgba(18,54,34,0.94)' : 'rgba(64,22,22,0.94)';
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, 624, 284, 34); else c.rect(8, 8, 624, 284);
    c.fill();
    c.strokeStyle = win ? '#69f0ae' : '#ff5c54';
    c.lineWidth = 10;
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, 624, 284, 34); else c.rect(8, 8, 624, 284);
    c.stroke();
    c.textAlign = 'center';
    c.fillStyle = '#ffffff';
    c.font = 'bold 74px Trebuchet MS, sans-serif';
    c.fillText(win ? tx('¡PRUEBA SUPERADA!', 'TEST CLEARED!') : tx('TIEMPO AGOTADO', 'TIME IS UP'), 320, 118);
    c.font = '38px Trebuchet MS, sans-serif';
    c.fillStyle = '#d9e6ff';
    c.fillText(datos, 320, 190);
    c.font = '30px Trebuchet MS, sans-serif';
    c.fillStyle = '#9fb8d8';
    c.fillText(win ? tx('¡Siguiente etapa!', 'Next stage!')
      : tx('La prueba se repite: ¡inténtalo otra vez!', 'The test repeats: try again!'), 320, 248);
    this.bnTex.needsUpdate = true;
    this.banner.visible = true;
  }

  _explosion(x, y, z, grande) {
    let n = 0;
    for (const p of this.fx) {
      if (p.t < p.life) continue;
      p.t = 0;
      p.s.visible = true;
      p.s.position.set(x, y, z);
      const a = Math.random() * Math.PI * 2;
      const sp = 0.5 + Math.random() * 1.4;
      p.vx = Math.cos(a) * sp;
      p.vz = Math.sin(a) * sp * 0.6;
      p.vy = 0.5 + Math.random() * 1.6;
      p.life = p.frag ? (0.7 + Math.random() * 0.5) : 0.45;
      p.s.material.rotation = Math.random() * 6;
      p.s.material.color.setHex(p.frag ? 0xffffff : 0x9fe8ff);
      if (++n >= (grande ? 10 : 7)) break;
    }
  }

  _fxStep(dt) {
    for (const p of this.fx) {
      if (p.t >= p.life) { if (p.s.visible) { p.s.visible = false; p.s.material.opacity = 0; } continue; }
      p.t += dt;
      p.vy -= 3.2 * dt;
      p.s.position.x += p.vx * dt;
      p.s.position.y += p.vy * dt;
      p.s.position.z += p.vz * dt;
      const k = 1 - p.t / p.life;
      p.s.material.opacity = Math.max(0, k);
      const esc = (p.frag ? 0.09 : 0.34) * (0.6 + 0.8 * k);
      p.s.scale.set(esc, esc, 1);
      p.s.material.rotation += dt * 3;
    }
  }

  _sonidoRomper() {
    const g = this.game;
    try { g.audio.playNoise(0.22, 900, 0.5, 0.16, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(520, 150, 0.16, 'square', 0.12, 0); } catch (e) { /* */ }
  }
  _sonidoEscudo() {
    const g = this.game;
    try { g.audio.playOsc(900, 620, 0.09, 'triangle', 0.10, 0); } catch (e) { /* */ }
    try { g.audio.playNoise(0.12, 2400, 0.3, 0.08, 0); } catch (e) { /* */ }
  }

  /* ----------------------- COLISIÓN POR SUBPASO ------------------------- */
  _collide(ball, events) {
    const g = this.game;
    if (!this.running) { if (ball.__exPrev) ball.__exPrev.copy(ball.pos); return; }
    let prev = ball.__exPrev;
    if (!prev) prev = ball.__exPrev = new THREE.Vector3().copy(ball.pos);
    const p = ball.pos;
    const rB = (CORE && CORE.DIMS ? CORE.DIMS.ballRadius : 0.02);
    const dx = p.x - prev.x, dy = p.y - prev.y, dz = p.z - prev.z;
    const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
    if (dist > 1e-9) {
      // rechazo grueso por objetivo y barrido fino del segmento
      for (const it of this.targets) {
        if (!it.alive) continue;
        const mx = (p.x + prev.x) * 0.5 - it.sp.position.x;
        const my = (p.y + prev.y) * 0.5 - it.sp.position.y;
        const mz = (p.z + prev.z) * 0.5 - it.sp.position.z;
        const rr = it.r + rB + dist * 0.5 + 0.06;
        if (mx * mx + my * my + mz * mz > rr * rr) continue;
        const steps = Math.max(1, Math.ceil(dist / (it.r * 0.5)));
        let hit = -1, hx = 0, hy = 0, hz = 0;
        for (let s2 = 1; s2 <= steps; s2++) {
          const f = s2 / steps;
          const sx = prev.x + dx * f, sy = prev.y + dy * f, sz = prev.z + dz * f;
          const ex = sx - it.sp.position.x, ey = sy - it.sp.position.y,
            ez = sz - it.sp.position.z;
          if (ex * ex + ey * ey + ez * ez <= (it.r + rB) * (it.r + rB)) {
            hit = s2; hx = sx; hy = sy; hz = sz; break;
          }
        }
        if (hit < 0) continue;
        // impacto: daño + rebote controlado
        it.hp--;
        const nx = hx - it.sp.position.x, ny = hy - it.sp.position.y,
          nz = hz - it.sp.position.z;
        const nl = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
        const vx = nx / nl, vy = ny / nl, vz = nz / nl;
        // saca la bola de la diana
        const sep = it.r + rB + 0.012;
        ball.pos.set(it.sp.position.x + vx * sep,
          it.sp.position.y + vy * sep,
          it.sp.position.z + vz * sep);
        if (it.hp <= 0) {
          it.alive = false;
          it.sp.visible = false;
          this.alive--;
          this._explosion(it.sp.position.x, it.sp.position.y, it.sp.position.z, it.tipo !== 'roca');
          this._sonidoRomper();
          try { if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.42, 70); } catch (e) { /* */ }
          if (it.tipo === 'dron') {
            this.tiempo += (this.cfg.dronBonus || 4);
            g.rules.message = tx('¡Dron: +' + (this.cfg.dronBonus || 4) + ' s!',
              'Drone: +' + (this.cfg.dronBonus || 4) + ' s!');
            this._hudKey = '';
          }
        } else {
          // escudo: chispazo, la caja aguanta (v3.2: destello del escudo 3D)
          this._explosion(hx, hy, hz, false);
          this._sonidoEscudo();
          it._hitT = 0.5;
          try { if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.2, 50); } catch (e) { /* */ }
        }
        // rebote: reflejo amortiguado con empuje hacia arriba
        const v = ball.vel;
        const dot = v.x * vx + v.y * vy + v.z * vz;
        v.x = (v.x - 2 * dot * vx) * 0.40;
        v.y = Math.max((v.y - 2 * dot * vy) * 0.40, 1.35);
        v.z = (v.z - 2 * dot * vz) * 0.40;
        const spd = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
        if (spd > 4.4) { const k = 4.4 / spd; v.x *= k; v.y *= k; v.z *= k; }
        break;   // una diana por subpaso
      }
    }
    ball.__exPrev.copy(p);
  }

  /* ------------------------------- STEP --------------------------------- */
  step(dt) {
    const g = this.game;
    this.t += dt;
    // fase RESULTADO: banner flotando y cuenta atrás hasta limpiar
    if (this.result) {
      this.bannerT -= dt;
      this.banner.position.y += Math.sin(this.t * 2.1) * 0.0006;
      if (this.bannerT <= 0 && !this._endDone) {
        this._endDone = true;
        this._cleanup();
      }
      return;
    }
    if (!this.running) return;

    this.tiempo -= dt;
    if (this.tiempo <= 0) { this.tiempo = 0; this._pintaHud(); this._fin(false); return; }
    this._pintaHud();

    // animación de dianas (flotación + órbita + rodadura)
    for (const it of this.targets) {
      if (!it.alive) continue;
      const ph = this.t * it.orbitW + it.fase;
      it.sp.position.x = it.bx + Math.sin(ph) * it.orbitA;
      it.sp.position.y = it.by + Math.sin(this.t * 1.7 + it.fase) * 0.035;
      // v3.2 (3D): rodadura del asteroide, rotores del dron, escudo que
      // respira y destella al aguantar un golpe
      if (it.mesh && it.rollW) it.mesh.rotation.y += it.rollW * dt;
      for (const rt of it.rotores) rt.rotation.y += dt * 14;
      if (it.escudo) {
        const obj = (it._hitT > 0) ? 0.55 : 0.18;
        it.escudo.material.opacity += (obj - it.escudo.material.opacity) * Math.min(1, dt * 6);
        if (it._hitT > 0) it._hitT -= dt;
      }
    }

    this._fxStep(dt);

    // recambio tras bola perdida
    if (this.deadT > 0) {
      this.deadT -= dt;
      if (this.deadT <= 0) this._spawnHeld();
    }

    const D = (CORE && CORE.DIMS) || { tableTopY: 0.76, tableCenterZ: -1.6 };
    // física de la bola (stepPhysics del NÚCLEO + colisionador propio)
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (g.renderer.xr.isPresenting && ps && ps.active) ? [ps] : [];
    g.events.length = 0;
    stepPhysicsSafe(dt, g.ball, pads, g.events, this._extra);

    if (this.hold) {
      // primer toque de pala la libera (la vel viene del impacto)
      let hit = false;
      for (const e of g.events) { if (e.type === 'paddle') { hit = true; break; } }
      if (hit) {
        this.hold = false;
        this.flight = 0;
      } else {
        // bote-en-espera determinista (v2.61 de magia)
        this.holdT += dt;
        const T = HOLD.T, H = HOLD.H;
        const pp = (this.holdT % T) / T;
        g.ball.pos.set(HOLD.x, D.tableTopY + 0.12 + 4 * H * pp * (1 - pp), HOLD.z);
        g.ball.vel.set(0, (4 * H * (1 - 2 * pp)) / T, 0);
        g.ball.spin.multiplyScalar(Math.max(0, 1 - dt * 2));
        if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
      }
    } else {
      this.flight += dt;
      const p = g.ball.pos;
      if (p.y < 0.05 || p.z > 1.2 || p.z < D.tableCenterZ - 2.6 || this.flight > 9) {
        this._bolaPerdida();
      }
    }

    // ¿todas las dianas fuera? → victoria
    if (this.alive <= 0) this._fin(true);
  }

  _spawnHeld() {
    const g = this.game;
    const D = (CORE && CORE.DIMS) || { tableTopY: 0.76 };
    this.hold = true;
    this.holdT = 0;
    this.flight = 0;
    g.ball.pos.set(HOLD.x, D.tableTopY + 0.12, HOLD.z);
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    g.ballMesh.visible = true;
    try { g.audio.playOsc(220, 880, 0.16, 'sine', 0.08, 0); } catch (e) { /* */ }
  }

  _bolaPerdida() {
    const g = this.game;
    this.hold = false;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = false;
    this.deadT = 0.7;
    try { g.audio.playNoise(0.18, 300, 0.25, 0.12, 0); } catch (e) { /* */ }
  }

  _fin(win) {
    const g = this.game;
    this.running = false;
    this.result = true;
    this.bannerT = 4.4;
    this._endDone = false;
    const restantes = this.alive;
    const datos = win
      ? tx('Dianas destruidas: ' + this.total + '/' + this.total +
           '  ·  ' + Math.ceil(this.tiempo) + ' s de sobra',
           'Targets destroyed: ' + this.total + '/' + this.total +
           '  ·  ' + Math.ceil(this.tiempo) + ' s to spare')
      : tx('Dianas destruidas: ' + (this.total - restantes) + '/' + this.total,
           'Targets destroyed: ' + (this.total - restantes) + '/' + this.total);
    this._pintaBanner(win, datos);
    if (win) {
      try { g.confettiBurst = Math.max(g.confettiBurst || 0, 3); } catch (e) { /* */ }
      try { g.audio.fanfare(true); } catch (e) { /* */ }
      try { g.audio.announce(tx('¡Prueba superada!', 'Test cleared!'), true); } catch (e) { /* */ }
      try { if (g.renderer.xr.isPresenting) { g.haptic(g.paddleHand, 0.7, 130); window.setTimeout(() => g.haptic(g.paddleHand, 0.5, 120), 220); } } catch (e) { /* */ }
    } else {
      try { g.audio.fanfare(false); } catch (e) { /* */ }
      try { g.audio.announce(tx('Tiempo agotado', 'Time is up'), true); } catch (e) { /* */ }
    }
    // el avance de etapa se registra YA (inmune a salidas a mitad de banner)
    this.ctrl._pruebaFin(win);
  }

  _cleanup() {
    const g = this.game;
    this.result = false;
    this.banner.visible = false;
    try { g.ball.ignoreNet = false; } catch (e) { /* */ }
    this.grp.visible = false;
    // el árbitro vuelve limpio a saque (patrón onMatchOver del stock)
    g.rules.startMatch('match');
    this.ctrl._despuesDePrueba();
  }
}

/** stepPhysics con guard: un fallo de la prueba JAMÁS congela el frame. */
function stepPhysicsSafe(dt, ball, pads, evs, extra) {
  try { STEP(dt, ball, pads, evs, extra); }
  catch (e) { console.warn('[estacion.stepPhysics]', e); }
}

/* ============================================================================
 *  StockController — SALA · CAMINO DE 5 ETAPAS · SUPERPODERES
 *  ============================================================================ */
class StockController {
  constructor(game) {
    this.game = game;
    this.group = new THREE.Group();
    this.state = 'sala';           // sala | duelo | prueba
    this.stage = 0;                // etapa del camino (0..4)
    this.victorias = 0;
    this._champion = false;        // v2.128: insignia ¡CONSEGUIDO! ganada
    this.prueba = new DianasOrbitales(this);
    // restauración v2.128 + v3 (ahora también la ETAPA del camino)
    try { this.victorias = parseInt(localStorage.getItem('pp_champ_estacion_orbital_wins') || '0', 10) || 0; } catch (e) { /* */ }
    try { this._champion = localStorage.getItem('pp_champ_estacion_orbital_champ') === '1'; } catch (e) { /* */ }
    try { this.stage = Math.max(0, Math.min(4, parseInt(localStorage.getItem('pp_champ_estacion_orbital_stage') || '0', 10) || 0)); } catch (e) { /* */ }
    this._ownTex = new Set();
    this._poolTex = new Set();     // viven toda la sesión (regla Quest: pools)
    this._mus = null; this._musBuf = null; this._musBusy = false;
    this._musWanted = false; this._musRamp = 0;
    // poderes
    this._powerCd = 6;
    this._bolsa = [];              // bolsa rotatoria (v2.126 del núcleo)
    this._warn = null;             // { def, t } aviso de dos fases
    this._act = null;              // poder activo { def, t, ... }
    this._t = 0;
  }

  _A(p) { return new URL('./assets/' + p, import.meta.url).href; }
  _ct(cv) {
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(t);
    return t;
  }
  get D() { return (CORE && CORE.DIMS) || { tableCenterZ: -1.6, tableTopY: 0.76, tableHalfLength: 1.37, tableHalfWidth: 0.7625, ballRadius: 0.02, netTopY: 0.9125 }; }
  _etapa() { return CFG.etapas[Math.min(this.stage, CFG.etapas.length - 1)]; }

  /* --------------------------- CONSTRUCCIÓN ----------------------------- */
  build() {
    const g = this.game;
    const D = this.D;
    const zRival = D.tableCenterZ - 1.9;

    // RIVAL: standee del ANDROIDE AX-9 (assets/rival.webp, arte PIL v3)
    // v2.130 · POSICIÓN DEL RIVAL (convención de TODOS los campeonatos):
    // un poco a la DERECHA de la mesa (x = halfWidth + 0,5 ≈ 1,26, la misma
    // DUEL_X de Magia), NO centrado detrás de la mesa. Girado 12° hacia
    // el centro para que la cara mire a la mesa.
    const texRival = new THREE.TextureLoader().load(this._A('rival.webp'));
    texRival.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(texRival);
    this._rival = texRival;
    const rivalMat = new THREE.MeshBasicMaterial({
      map: texRival, transparent: true, alphaTest: 0.25, depthWrite: false,
    });
    this.rivalMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.75), rivalMat);
    this.rivalMesh.position.set((D.tableHalfWidth || 0.7625) + 0.5, 0.875, zRival);
    this.rivalMesh.rotation.y = -0.22;
    this.group.add(this.rivalMesh);
    this.rivalEstado('idle');

    // CARTEL de bienvenida (redibujable por etapa)
    // v2.130 · ANTES flotaba sobre la mesa (0 / 1,38 / −1,05) tapando la
    // vista del rival — petición del artista: la MESA SIEMPRE LIBRE. Va a
    // la pared FRONTAL, a la izquierda del marcador del núcleo (x −1,78),
    // como tablón de misión: visible, aimable y sin estorbar a nadie.
    this.cartelCv = document.createElement('canvas');
    this.cartelCv.width = 512; this.cartelCv.height = 256;
    this.cartelTex = this._ct(this.cartelCv);
    this.cartel = new THREE.Mesh(new THREE.PlaneGeometry(1.15, 0.575),
      new THREE.MeshBasicMaterial({ map: this.cartelTex, depthWrite: false }));
    this.cartel.position.set(-2.2, 1.46, -5.44);
    this.cartel.rotation.set(0, 0.12, 0);
    this.group.add(this.cartel);
    this._pintaCartel();

    // DECORACIÓN viva: dron vigía que patrulla la sala (idle del campeonato)
    if (!this.dron) {
      const texD = new THREE.TextureLoader().load(this._A('dron.png'));
      texD.colorSpace = THREE.SRGBColorSpace;
      this._poolTex.add(texD);
      this.dronMat = new THREE.SpriteMaterial({ map: texD, transparent: true, depthWrite: false });
      this.dron = new THREE.Sprite(this.dronMat);
      this.dron.scale.set(0.42, 0.42, 1);
      this.dron.position.set(1.35, 1.62, D.tableCenterZ - 1.1);
      this.group.add(this.dron);
    }

    // haz del RAYO TRACTOR (oculto salvo poder activo) — pool del poder
    if (!this.beam) {
      const geo = new THREE.CylinderGeometry(0.05, 0.34, 1, 18, 1, true);
      geo.translate(0, -0.5, 0);         // origen arriba, abre hacia abajo
      this.beamMat = new THREE.MeshBasicMaterial({
        color: 0x6fffc8, transparent: true, opacity: 0.0,
        blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
      });
      this.beam = new THREE.Mesh(geo, this.beamMat);
      this.beam.renderOrder = 25;
      this.beam.visible = false;
      g.scene.add(this.beam);
    }

    // motas de GRAVEDAD CERO (pool flotante, una sola vez)
    if (!this.motas) {
      this.motas = [];
      const texM = _texFlash();
      this._poolTex.add(texM);
      for (let i = 0; i < 14; i++) {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({
          map: texM, transparent: true, depthWrite: false, opacity: 0,
          color: 0xbfe8ff,
        }));
        s.renderOrder = 22;
        g.scene.add(s);
        this.motas.push({ s, x: 0, y: 0, z: 0, ph: Math.random() * 6 });
      }
    }

    // METEORITOS: pool de rocas (sprites) del poder
    if (!this.rocas) {
      this.rocas = [];
      const texR1 = new THREE.TextureLoader().load(this._A('asteroide.png'));
      const texR2 = new THREE.TextureLoader().load(this._A('asteroide2.png'));
      texR1.colorSpace = THREE.SRGBColorSpace;
      texR2.colorSpace = THREE.SRGBColorSpace;
      this._poolTex.add(texR1); this._poolTex.add(texR2);
      for (let i = 0; i < 4; i++) {
        const mat = new THREE.SpriteMaterial({
          map: i % 2 ? texR1 : texR2, transparent: true, depthWrite: false, opacity: 0,
        });
        const s = new THREE.Sprite(mat);
        s.renderOrder = 24;
        s.visible = false;
        g.scene.add(s);
        this.rocas.push({ s, mat, on: false, cayendo: false, x: 0, y: 0, z: 0, vy: 0, vida: 0, ph: Math.random() * 6 });
      }
    }

    // CARTEL DEL SUPERPODER (v3.2): el «identificador» que el jugador espera
    // — panel flotante junto al AX-9 con el MEDALLÓN del poder + nombre.
    // Fase AVISO (ámbar, «AX-9 PREPARA…») y fase ACTIVA (cian, ¡NOMBRE!).
    if (!this.powerSign) {
      this._psCv = document.createElement('canvas');
      this._psCv.width = 512; this._psCv.height = 256;
      this._psTex = this._ct(this._psCv);
      this.powerSign = new THREE.Mesh(new THREE.PlaneGeometry(1.05, 0.525),
        new THREE.MeshBasicMaterial({ map: this._psTex, transparent: true, depthWrite: false }));
      // flotando a la DERECHA de la mesa (lado del rival), sobre la altura de
      // la cabeza y girado hacia el jugador: visible sin tapar la mesa
      this.powerSign.position.set(1.02, 1.88, D.tableCenterZ - 1.05);
      this.powerSign.rotation.y = -0.42;
      this.powerSign.renderOrder = 35;
      this.powerSign.visible = false;
      this.group.add(this.powerSign);
      this._psIcons = {};
      for (const p of CFG.poderes) {
        try {
          const img = new Image();
          // v3.2: CFG.icon trae 'assets/…' y _A() YA antepone './assets/' —
          // sin el strip salía 'assets/assets/…' (404s del QA)
          img.src = this._A(String(p.icon || '').replace(/^assets\//, ''));
          this._psIcons[p.name] = img;
        } catch (e) { /* sin icono: círculo de color */ }
      }
    }

    // MAPA DEL CAMPEONATO en la pared izquierda (convención de la casa):
    // ruta de 5 etapas con anillo en la etapa vigente, tapas en las futuras
    // y rejugada por gatillo (v2.96). Se construye UNA vez.
    if (!this.mapa) {
      this.mapa = new MapaEO(this);
      this.mapa.build();
    } else {
      this.mapa.show();
    }

    g.scene.add(this.group);
  }

  /** Cartel de la sala: ETAPA X/5 · nombre (+ ★ SUPERADO si ya campeón). */
  _pintaCartel() {
    const cv = this.cartelCv;
    const c = cv.getContext('2d');
    const et = this._etapa();
    c.clearRect(0, 0, 512, 256);
    c.fillStyle = '#101a2c';
    c.fillRect(0, 0, 512, 256);
    c.strokeStyle = '#4fd8ff'; c.lineWidth = 10;
    c.strokeRect(8, 8, 496, 240);
    c.textAlign = 'center';
    c.fillStyle = '#f4ecdd';
    c.font = 'bold 40px Trebuchet MS, sans-serif';
    c.fillText(tx('ESTACIÓN ORBITAL', 'ORBITAL STATION'), 256, 64);
    c.fillStyle = '#7fe8ff';
    c.font = 'bold 34px Trebuchet MS, sans-serif';
    c.fillText(tx('ETAPA ' + (this.stage + 1) + '/5 · ' + et.name.toUpperCase(),
      'STAGE ' + (this.stage + 1) + '/5 · ' + et.name.toUpperCase()), 256, 124);
    c.fillStyle = '#eef4ff';
    c.font = '24px Trebuchet MS, sans-serif';
    c.fillText(tx('APUNTA Y PULSA EL GATILLO', 'AIM AND PULL THE TRIGGER'), 256, 178);
    c.fillText(tx('para empezar', 'to start'), 256, 214);
    if (this._champion) {
      c.fillStyle = '#ffd740';
      c.font = 'bold 26px Trebuchet MS, sans-serif';
      c.fillText(tx('★ SUPERADO · revancha libre', '★ CLEARED · free rematch'), 256, 248);
    }
    this.cartelTex.needsUpdate = true;
  }

  rivalEstado(estado) {
    // assets/<estado>.webp si existe; si no, mantiene el actual
    try {
      const img = new Image();
      img.onload = () => { this._rival.image = img; this._rival.needsUpdate = true; };
      img.src = this._A(estado + '.webp');
    } catch (e) { /* sin estado: sigue */ }
  }

  /* ------------------------------ MÚSICA --------------------------------
   *  Motor privado siguiendo el patrón magia/oeste v2.124+2.125 (UNA
   *  MELODÍA, decodeAudioData en promesa con copia). */
  _musicEffVol() {
    try {
      const A = this.game && this.game.audio;
      if (!A) return 0.18;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return 0.18; }
  }
  musicOn() {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      if (this._mus && this._mus.src.context !== actx) this._mus = null;
      this._musWanted = true;
      const A0 = g.audio;
      if (A0 && A0.arcPlaying) return;               // UNA MELODÍA
      if (!this._musBuf && !this._musBusy) this._loadMusic(actx);
      else if (this._musBuf && !this._mus) this._startMusic(actx);
    } catch (e) { /* sin música: nunca rompe */ }
  }
  _loadMusic(actx) {
    try {
      let url = null;
      try { url = (this.manifest && this.manifest.audio && this.manifest.audio.music)
        ? new URL('./' + this.manifest.audio.music, import.meta.url).href : this._A('bso.wav');
      } catch (e) { url = this._A('bso.wav'); }
      if (!url || this._musBusy) return;
      this._musBusy = true;
      fetch(url)
        .then((r) => r.arrayBuffer())
        .then((ab) => actx.decodeAudioData(ab.slice(0)))
        .then((buf) => {
          this._musBuf = buf; this._musBusy = false;
          if (this._musWanted) this._startMusic(actx);
        })
        .catch(() => { this._musBusy = false; });
    } catch (e) { /* */ }
  }
  _startMusic(actx) {
    try {
      if (this._mus || !this._musBuf) return;
      const A0 = this.game && this.game.audio;
      if (A0 && A0.arcPlaying) return;               // UNA MELODÍA
      const gain = actx.createGain();
      const t0 = actx.currentTime;
      gain.gain.setValueAtTime(0.0001, t0);
      gain.gain.linearRampToValueAtTime(this._musicEffVol(), t0 + 0.8);
      this._musRamp = t0 + 0.8;
      gain.connect(actx.destination);
      const src = actx.createBufferSource();
      src.buffer = this._musBuf;
      src.loop = true;
      src.connect(gain);
      src.start();
      this._mus = { gain, src };
    } catch (e) { this._mus = null; }
  }
  _syncMusicGain() {
    try {
      const A = this.game && this.game.audio;
      if (this._mus && A && A.ctx && this._mus.src.context !== A.ctx) {
        this._mus = null;                            // re-bind: resucita
        if (this._musWanted && this._musBuf && A.ctx.state === 'running') {
          this._startMusic(A.ctx);
          return;
        }
      }
      if (!this._mus || !this._mus.gain) return;
      const gn = this._mus.gain.gain;
      const eff = this._musicEffVol();
      if (this._musRamp && A && A.ctx && A.ctx.currentTime < this._musRamp) return;
      if (A && A.ctx && Math.abs((gn.value || 0) - eff) > 0.001) {
        const t = A.ctx.currentTime;
        gn.cancelScheduledValues(t);
        gn.setValueAtTime(Math.max(0.0001, gn.value || 0.0001), t);
        gn.linearRampToValueAtTime(eff, t + 0.15);
      }
    } catch (e) { /* */ }
  }
  musicOff() {
    this._musWanted = false;
    if (this._mus) {
      try { this._mus.src.stop(); } catch (e) { /* */ }
      try { this._mus.gain.disconnect(); } catch (e) { /* */ }
      this._mus = null;
    }
  }

  /* --------------------------- CICLO / CONTRATO ------------------------- */
  startChamp() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    this.state = 'sala';
    // v3.1 (V2.131) · EL ÁRBITRO DUERME EN LA SALA (convención oeste/magia):
    // con rules.state='champtest' el gatillo del casco llega a serveTrigger()
    // y arranca la etapa vigente (duelo o prueba). Este era el ajuste que
    // faltaba: sin él la sala jugaba partidos normales sin powers ni pruebas.
    g.rules.state = 'champtest';
    // bola aparcada sobre la mesa (sala limpia mientras se lee el cartel)
    try {
      const D = this.D;
      g.ball.pos.set(0, D.tableTopY + (D.ballRadius || 0.02), D.tableCenterZ + 0.45);
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
      g.ballMesh.visible = true;
    } catch (e) { /* nunca tumba el arranque */ }
    this._pintaCartel();
    if (this.mapa) this.mapa.show();          // v2.130: mapa siempre visible
    g.rules.message = tx('¡Bienvenido a Estación Orbital!', 'Welcome to Orbital Station!');
    this.musicOn();
  }
  leave() {
    const g = this.game;
    this.musicOff();
    this._poderClear();
    this.prueba.stop();
    // v3.1 (V2.131) · restitución del ÁRBITRO al salir (convención magia):
    // si el campeonato se abandona desde la sala/prueba el núcleo quedaría
    // con rules.state='champtest' para siempre (menú sin árbitro).
    try {
      if (g.rules.state === 'champtest') {
        g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
      }
    } catch (e0) { /* */ }
    if (this.mapa) this.mapa.dispose();       // v2.130: sin restos GPU
    if (this.group.parent) this.group.parent.remove(this.group);
    if (this.beam) this.beam.visible = false;
    if (this.motas) for (const m of this.motas) m.s.material.opacity = 0;
    for (const t of this._ownTex) { try { t.dispose(); } catch (e) { /* */ } }
    this._ownTex.clear();
  }
  resetRecords() {
    try {
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf('pp_champ_estacion_orbital_') === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e) { /* */ }
    this.victorias = 0;
    this.stage = 0;
    this._champion = false;   // v2.128: la insignia se retira con los registros
    this._pintaCartel();
    if (this.mapa) this.mapa.refresh();       // v2.130: anillo a la etapa 1
  }

  /* --------- CAMINO DE 5 ETAPAS (duelo → prueba → … → DUELO FINAL) ------ */
  serveTrigger() {
    if (this.state !== 'sala') return;
    const et = this._etapa();
    if (et.kind === 'prueba') this._empezarPrueba(et);
    else this._empezarDuelo(et);
  }

  _empezarDuelo(et) {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('Sin duelo en línea', 'No duel online'); return; }
    this.state = 'duelo';
    this.cartel.visible = false;
    this.rivalEstado('duelo');
    g.rules.oppLabel = 'rival';
    g.rules.startMatch('match');      // marcador a cero + saque propio
    if (g.applyAISkill) { try { g.applyAISkill(); } catch (e) { /* */ } }
    g.rules.message = (et.id === 'final')
      ? tx('¡DUELO FINAL contra ' + CFG.rival + '!', 'FINAL DUEL vs ' + CFG.rival + '!')
      : tx('¡Duelo contra ' + CFG.rival + '!', CFG.rival + ' duel!');
    this._showInstr(et);
    this.musicOn();
    // poderes: bolsa limpia y el primero tarda en llegar
    this._poderClear();
    this._bolsa.length = 0;
    this._powerCd = 6;            // v3.2: antes 8 (el primer poder llega antes)
    this._dueloT = 0;             // v3.2: relojes del disparo redundante
    this._lastPowerT = 0;
    this._toward = false;
  }
  _showInstr(et) {
    try {
      const final = et.id === 'final';
      this.game.showInstrucciones(
        tx('Duelo contra ' + CFG.rival, CFG.rival + ' duel'),
        final ? [
          tx('El AX-9 pelea a MÁXIMA POTENCIA. Primero a ' + CFG.puntos + ' puntos.',
            'AX-9 fights at FULL POWER. First to ' + CFG.puntos + ' points.'),
          tx('¡Gana y la estación es tuya: insignia ¡CONSEGUIDO!!',
            'Win and the station is yours: ACHIEVED badge!'),
        ] : [
          tx('Primero a ' + CFG.puntos + ' puntos. La dificultad sube con cada duelo ganado.',
            'First to ' + CFG.puntos + ' points. Difficulty rises with every duel won.'),
          tx('¡Cuidado con los superpoderes de ' + CFG.rival + '!',
            'Beware ' + CFG.rival + '\'s super powers!'),
        ],
        5.0, null, 'estacion');
    } catch (e) { /* */ }
  }

  _empezarPrueba(et) {
    const g = this.game;
    const compleja = et.id === 'tormenta';
    this.state = 'prueba';
    // v3.1 (V2.131): el árbitro duerme YA (también durante el panel de
    // instrucciones con botón EMPEZAR — el gatillo sólo cierra ese panel)
    g.rules.state = 'champtest';
    this.cartel.visible = false;
    this.rivalEstado('idle');          // el AX-9 no participa en la prueba (v2.63 de magia)
    // CARTEL EXPLICATIVO antes de entrar (regla v2.106, todas las pruebas):
    // lo pinta el núcleo y llama de vuelta a _arrancarPrueba al irse.
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        g.showInstrucciones(
          tx('PRUEBA · ' + et.name.toUpperCase(), 'SKILL TEST · ' + et.name.toUpperCase()),
          compleja ? [
            tx('Derrite 9 asteroides, 3 cajas blindadas (2 golpes) y 2 drones.',
              'Melt 9 asteroids, 3 shielded crates (2 hits) and 2 drones.'),
            tx('Cada dron caído da +' + DIANAS.compleja.dronBonus + ' segundos. Tienes ' + DIANAS.compleja.tiempo + ' s.',
              'Each drone down adds +' + DIANAS.compleja.dronBonus + ' seconds. You have ' + DIANAS.compleja.tiempo + ' s.'),
          ] : [
            tx('Rompe los ' + DIANAS.normal.nRocas + ' asteroides flotando sobre la mesa.',
              'Blast the ' + DIANAS.normal.nRocas + ' asteroids floating over the table.'),
            tx('Golpea la bola con la pala. Tienes ' + DIANAS.normal.tiempo + ' segundos y bolas infinitas.',
              'Hit the ball with the paddle. You have ' + DIANAS.normal.tiempo + ' seconds and endless balls.'),
          ],
          7.5,
          () => {
            this._instrK = null;          // el cartel ya se mostró: la próxima
            // entrada (reintento) vuelve a explicarlo (regla v2.106)
            try { this._arrancarPrueba(compleja); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarPrueba(compleja);
  }
  _arrancarPrueba(compleja) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    this.prueba.start(compleja);
    this.musicOn();
  }

  /** La prueba terminó (victoria o derrota) — persistencia inmediata.
   *  v2.130: en REJUGADA (mapa, campeonato abierto) el progreso REAL no
   *  cambia: la etapa se juega de cortesía y el camino sigue donde estaba. */
  _pruebaFin(win) {
    if (this._replay) {
      this.game.rules.message = tx('Rejugada terminada · camino intacto',
        'Replay finished · path unchanged');
      return;
    }
    if (win) {
      this.stage = Math.min(4, this.stage + 1);
      try { localStorage.setItem('pp_champ_estacion_orbital_stage', String(this.stage)); } catch (e) { /* */ }
    }
    // derrota: la etapa se repite (sin retroceder al duelo previo: flujo amable)
  }
  /** Tras el banner, la prueba devuelve el control a la SALA. */
  _despuesDePrueba() {
    const g = this.game;
    this.state = 'sala';
    g.rules.state = 'champtest';       // v3.1 (V2.131): árbitro dormido en sala
    this.cartel.visible = true;
    this._pintaCartel();
    if (this._replay) {                        // v2.130: fin de rejugada
      this.stage = this._replay.stage;
      this._replay = null;
      this._pintaCartel();
    }
    if (this.mapa) this.mapa.refresh();
    const et = this._etapa();
    g.rules.message = tx('Siguiente: ' + et.name, 'Next: ' + et.name);
    this.rivalEstado('idle');
    this.musicOn();
  }

  aiMul() {
    if (this.state !== 'duelo') return 1;
    const et = this._etapa();
    return (et && et.aiMul) || 1;
  }
  onPoint(it) {
    // superpoder: probabilidad por punto jugado (motor de dos fases).
    // v3.2: es UNO de los dos caminos — el otro (principal en el casco)
    // vive en _poderUpdate: disparo por RALLY + garantía temporal.
    if (this.state === 'duelo') this._quizasPoder();
  }
  onMatchOver(w) {
    const g = this.game;
    // v3.2 · FIX CRÍTICO: el núcleo llama con el GANADOR como STRING
    // ('player'|'rival' — ver case 'game-over' del núcleo). El parámetro se
    // trataba como booleano y 'rival' es truthy: PERDER un duelo AVANZABA la
    // etapa con mensajes de victoria (el QA anterior llamaba con booleanos y
    // no lo vio). Convención Oeste: w = (winner === 'player').
    const won = (w === true) || (w === 'player');
    // v2.130 · REJUGADA por el mapa (campeonato abierto): el progreso REAL
    // no cambia — sin victorias contadas, sin avance, sin insignia.
    if (this._replay) {
      g.rules.message = won
        ? tx('¡Revancha ganada! El camino sigue igual.',
             'Replay won! The path stays the same.')
        : tx('Rejugada perdida · el camino sigue igual.',
             'Replay lost · the path stays the same.');
      this.rivalEstado(won ? 'derrotado' : 'triunfante');
      // v3.1 (V2.131) · la rejugada CIERRA como el resto del camino: el
      // PROGRESO REAL vuelve (antes el estado quedaba en 'duelo', sin cartel,
      // con _replay pegado al siguiente duelo real y el cartel mostrando la
      // etapa rejugada como si fuera la vigente). Vuelta a la sala.
      const real = this._replay.stage | 0;
      this._replay = null;
      this.stage = real;
      try { localStorage.setItem('pp_champ_estacion_orbital_stage', String(this.stage)); } catch (e1) { /* */ }
      this.state = 'sala';
      this.cartel.visible = true;
      this._pintaCartel();
      if (this.mapa) this.mapa.refresh();
      g.rules.startMatch('match');    // marcador a cero
      g.rules.state = 'champtest';    // árbitro dormido: el gatillo es del camino
      this.musicOn();
      return;
    }
    this.rivalEstado(won ? 'derrotado' : 'triunfante');
    const et = this._etapa();
    if (won) {
      this.victorias++;
      try { localStorage.setItem('pp_champ_estacion_orbital_wins', String(this.victorias)); } catch (e) { /* */ }
      if (et.id === 'final' && !this._champion) {
        // v2.128 · ¡¡ESTACIÓN ORBITAL CONSEGUIDA!! (duelo final ganado):
        // INSIGNIA en grande (panel del núcleo) + registro + fila campeona
        // 🏆 en el ranking mundial. El campeonato queda ABIERTO.
        this._champion = true;
        try { localStorage.setItem('pp_champ_estacion_orbital_champ', '1'); } catch (e) { /* */ }
        g.rules.message = tx('¡¡ESTACIÓN ORBITAL CONSEGUIDA!!', 'ORBITAL STATION COMPLETED!!');
        try {
          const C = window.__PP_CORE;
          if (C && C.showChampConseguido) C.showChampConseguido('estacion_orbital');
        } catch (e2) { /* */ }
        try {
          const W = (typeof window !== 'undefined' && window.__PP_WORLD);
          if (W && typeof W.submit === 'function') {
            let nm = '';
            try { nm = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e3) { /* */ }
            Promise.resolve(W.submit('estacion_orbital', { n: nm || 'Anónimo', p: this.victorias | 0, a: '🏆' }))
              .catch(() => { /* nunca rompe */ });
          }
        } catch (e4) { /* */ }
      } else if (et.id === 'final') {
        g.rules.message = tx('¡Revancha ganada! La estación sigue siendo tuya.',
          'Rematch won! The station is still yours.');
      } else {
        const sig = CFG.etapas[Math.min(this.stage + 1, 4)];
        this.stage = Math.min(4, this.stage + 1);
        try { localStorage.setItem('pp_champ_estacion_orbital_stage', String(this.stage)); } catch (e) { /* */ }
        g.rules.message = tx('¡Has ganado el duelo! Siguiente: ' + sig.name,
          'Duel won! Next: ' + sig.name);
      }
    } else {
      g.rules.message = tx(CFG.rival + ' gana… revancha al servir.', CFG.rival + ' wins… rematch on serve.');
    }
    // el camino queda ABIERTO: se vuelve a la sala con la etapa vigente
    this.state = 'sala';
    this.cartel.visible = true;
    this._pintaCartel();
    if (this.mapa) this.mapa.refresh();       // v2.130: anillo a la etapa nueva
    g.rules.startMatch('match');      // el marcador queda limpio
    // v3.1 (V2.131): y el ÁRBITRO vuelve a dormir — sin esto el gatillo
    // tras el duelo hacía saques clásicos en vez de lanzar la etapa nueva
    g.rules.state = 'champtest';
    this.musicOn();
  }

  /* --------- v2.130 · REJUGADA por el MAPA (contrato v2.96 del núcleo) --- */
  replayMap() {
    if (!this.mapa || !this.mapa.group || !this.mapa.group.visible) return null;
    return this.mapa.replayData();
  }
  replayHover(idx) { if (this.mapa) this.mapa.hover(idx | 0); }
  replayLaunch(i) {
    const g = this.game;
    i = i | 0;
    // en pleno duelo o prueba el mapa no lanza nada (el gatillo es del reto)
    if (this.state === 'duelo' || (this.prueba && this.prueba.stepActive())) return;
    if (i >= (this.stage | 0)) {
      // nodo VIGENTE (o el mismo): camino normal, sin rejugada
      this.stage = i;
      try { localStorage.setItem('pp_champ_estacion_orbital_stage', String(this.stage)); } catch (e) { /* */ }
      this.startChamp();
      return;
    }
    // etapa SUPERADA: rejugada — el progreso real vuelve al terminar
    this._replay = { stage: this.stage | 0 };
    this.stage = i;
    g.rules.message = tx('REJUGANDO la etapa ' + (i + 1) + ' · tu progreso no cambia',
      'REPLAYING stage ' + (i + 1) + ' · your progress stays');
    try { g.audio.announce(g.rules.message, true); } catch (e) { /* */ }
    this.startChamp();
  }
  update(dt) {
    const g = this.game;
    this._t += dt;
    this._syncMusicGain();
    // v3.1 (V2.131): la pala IA sólo existe en DUELO — en la sala manda el
    // standee del AX-9 y en la prueba juegas sólo contra las dianas (se
    // ejecuta tras las escrituras de visibilidad del núcleo en el frame)
    try { if (g.aiPaddleMesh) g.aiPaddleMesh.visible = (this.state === 'duelo'); } catch (e) { /* */ }
    // v3.2: pulso del cartel del superpoder (llama la atención sin gritar)
    if (this.powerSign && this.powerSign.visible) {
      this.powerSign.scale.setScalar(1 + Math.sin(this._t * 5.5) * 0.035);
    }
    // dron vigía patrullando la sala
    if (this.dron && this.state !== 'duelo') {
      this.dron.position.x = 1.35 + Math.sin(this._t * 0.6) * 0.55;
      this.dron.position.y = 1.62 + Math.sin(this._t * 1.3) * 0.07;
    } else if (this.dron) {
      this.dron.position.x = -1.75;
      this.dron.position.y = 1.7;
    }
    // poderes solo en DUELO
    if (this.state === 'duelo') this._poderUpdate(dt);
    else if (this._act || this._warn) this._poderClear();
  }
  reenter() {
    // vuelta de VR: la música resucita sola y el árbitro vuelve a su sitio
    // v3.1 (V2.131): en DUELO sigue el partido ('serve'); en sala/prueba duerme
    const g = this.game;
    g.rules.state = (this.state === 'duelo') ? 'serve' : 'champtest';
    this.musicOn();
  }

  /* ===================== SUPERPODERES DEL AX-9 (v3) =====================
   *  Bolsa rotatoria (convención v2.126: todos salen antes de repetir) +
   *  motor de DOS FASES: aviso (2 s, cartel del rival) → efecto.
   *  Meteoritos bloquea la bola con el patrón Burla v2.127 (cruce del
   *  segmento prev→actual de la bola principal). */

  _quizasPoder(force) {
    if (this._act || this._warn) return;
    if (!force && this._powerCd > 0) return;
    const defs = CFG.poderes.filter((p) => p.kind === 'confeti' || p.kind === 'custom');
    if (!defs.length) return;
    if (!this._bolsa.length) {
      this._bolsa = defs.slice();
      for (let i = this._bolsa.length - 1; i > 0; i--) {
        const j = (Math.random() * (i + 1)) | 0;
        [this._bolsa[i], this._bolsa[j]] = [this._bolsa[j], this._bolsa[i]];
      }
    }
    const def = this._bolsa.pop();
    if (force || Math.random() < (def.chance || 0.3)) {
      this._warn = { def, t: def.warn || 2.0 };
      this._lastPowerT = this._dueloT || 0;
      this.game.rules.message = tx(CFG.rival + ' prepara: ¡' + def.name + '!',
        CFG.rival + ' readies: ' + def.name + '!');
      this._psMuestra(def, false);          // v3.2: CARTEL con el identificador
      try { this.game.audio.playOsc(180, 320, 0.3, 'sawtooth', 0.10, 0); } catch (e) { /* */ }
    } else {
      this._bolsa.unshift(def);       // devuélvelo: no salió esta vez
      this._powerCd = 4;              // v3.2: reintento más ágil (antes 6)
    }
  }

  _poderUpdate(dt) {
    const g = this.game;
    if (this._powerCd > 0) this._powerCd -= dt;
    this._dueloT = (this._dueloT || 0) + dt;
    // v3.2 · DISPARO REDUNDANTE (lección del casco: el gancho por PUNTO
    // puede no llegar; La Locura dispara por RALLY y SÍ funciona):
    // (a) en rally con la bola viniendo al jugador (edge vel.z>0.35) y
    // cooldown libre → tirada con la probabilidad del poder;
    // (b) RED DE SEGURIDAD: si en 22 s de duelo no ha saltado NADA, se
    // FUERZA el poder (garantía anti-silencio, pase lo que pase con los
    // eventos del punto).
    if (!this._warn && !this._act) {
      const urgente = (this._dueloT - (this._lastPowerT || 0)) > 22;
      if (urgente) {
        this._powerCd = 0;
        this._quizasPoder(true);
      } else if (g.rules.state === 'rally' && g.ball && g.ball.vel) {
        const toward = g.ball.vel.z > 0.35;
        const edge = toward && !this._toward;
        this._toward = toward;
        if (edge && this._powerCd <= 0) this._quizasPoder();
      } else {
        this._toward = false;
      }
    }
    // FASE 1: aviso
    if (this._warn) {
      this._warn.t -= dt;
      if (this._warn.t <= 0) {
        const def = this._warn.def;
        this._warn = null;
        this._poderArrancar(def);
      }
      return;
    }
    // FASE 2: efecto activo
    if (this._act) {
      const a = this._act;
      a.t -= dt;
      const rally = g.rules.state === 'rally';
      const ball = g.ball;
      if (a.def.kind === 'confeti') {
        this._confetiStep(dt, a);
        if (a.t <= 0) this._poderFin();
      } else if (a.def.kind === 'custom' && a.def.name === 'Meteoritos') {
        this._meteorStep(dt, a, ball, rally);
        if (a.t <= -1.2) this._poderFin();       // deja caer/respirar las rocas
      } else if (a.def.kind === 'custom' && a.def.name === 'Rayo tractor') {
        this._tractorStep(dt, a, ball, rally);
        if (a.t <= 0) this._poderFin();
      } else if (a.def.kind === 'custom' && a.def.name === 'Gravedad cero') {
        this._ceroStep(dt, a, ball, rally);
        if (a.t <= 0) this._poderFin();
      } else if (a.t <= 0) {
        this._poderFin();
      }
    }
  }

  _poderArrancar(def) {
    const g = this.game;
    this._act = { def, t: def.duration || 8 };
    this._lastPowerT = this._dueloT || 0;
    g.rules.message = tx('¡' + def.name.toUpperCase() + '!', def.name.toUpperCase() + '!');
    this._psMuestra(def, true);           // v3.2: CARTEL en fase ACTIVA
    try { g.audio.announce(def.name, true); } catch (e) { /* */ }
    // v3.2: el arranque del efecto va BLINDADO — si un efecto falla, el
    // poder se cierra limpio y la bolsa sigue viva (antes una excepción
    // aquí dejaba _act pegado y BLOQUEABA todos los poderes futuros).
    try {
      if (def.kind === 'confeti') {
        this._confetiStart(def);
      } else if (def.name === 'Meteoritos') {
        const libres = this.rocas.filter((r) => !r.on);
        this._act.n = Math.min(def.rocas || 3, libres.length);
        this._act.spawnT = 0;
        this._act.spawnK = 0;
        try { g.audio.playNoise(0.4, 220, 0.7, 0.2, 0); } catch (e) { /* */ }
      } else if (def.name === 'Rayo tractor') {
        const D = this.D;
        this.beam.visible = true;
        this.beam.position.set(0, 1.62, D.tableCenterZ - 1.62);
        this.beam.scale.set(1, 1.62, 1);           // largo del cono
        this.beam.rotation.z = 0;
        try { g.audio.playOsc(90, 55, 0.6, 'sawtooth', 0.12, 0); } catch (e) { /* */ }
      } else if (def.name === 'Gravedad cero') {
        const D = this.D;
        for (const m of this.motas) {
          m.x = (Math.random() * 2 - 1) * 1.1;
          m.y = 0.8 + Math.random() * 1.2;
          m.z = D.tableCenterZ - 0.8 + Math.random() * 1.6;
          m.s.material.opacity = 0;
        }
        try { g.audio.playOsc(320, 720, 0.7, 'sine', 0.08, 0); } catch (e) { /* */ }
      }
    } catch (e) {
      console.warn('[estacion.poder]', e);
      this._poderFin();
    }
  }
  _poderFin() {
    const a = this._act;
    if (!a) return;
    // limpieza del efecto que termina (cada poder esconde SOLO lo suyo)
    if (a.def.kind === 'confeti') {
      this._confeti = null;
      if (this._poolConfeti) {
        for (const p of this._poolConfeti) { p.on = false; p.s.material.opacity = 0; }
      }
    } else if (a.def.name === 'Meteoritos') {
      for (const r of this.rocas) { r.on = false; r.s.visible = false; r.mat.opacity = 0; }
    } else if (a.def.name === 'Rayo tractor') {
      this.beam.visible = false;
      this.beamMat.opacity = 0;
    } else if (a.def.name === 'Gravedad cero') {
      for (const m of this.motas) m.s.material.opacity = 0;
    }
    this._act = null;
    this._powerCd = 10 + Math.random() * 5;      // v3.2: antes 12+8 (más ágil)
    this._psOculta();                            // v3.2: fuera el cartel
  }
  _poderClear() {
    const g = this.game;
    this._warn = null;
    this._act = null;
    this._toward = false;
    this._psOculta();                            // v3.2: fuera el cartel
    if (this.beam) { this.beam.visible = false; this.beamMat.opacity = 0; }
    if (this.rocas) for (const r of this.rocas) { r.on = false; r.cayendo = false; r.s.visible = false; r.mat.opacity = 0; }
    if (this.motas) for (const m of this.motas) m.s.material.opacity = 0;
    if (this._poolConfeti) for (const p of this._poolConfeti) { p.on = false; p.s.material.opacity = 0; }
    this._confeti = null;
  }

  /* — v3.2 · CARTEL DEL SUPERPODER (identificador del poder en curso) ——
   *  Panel canvas 512×256: medallón del poder (assets/power*.png) + nombre
   *  en grande + banda de fase. _psMuestra(def, activa) pinta y muestra;
   *  _psOculta() lo retira. El pulso vive en update(). */
  _psMuestra(def, activa) {
    if (!this.powerSign) return;
    const c = this._psCv.getContext('2d');
    c.clearRect(0, 0, 512, 256);
    c.fillStyle = 'rgba(8,14,26,0.92)';
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, 496, 240, 30); else c.rect(8, 8, 496, 240);
    c.fill();
    c.strokeStyle = activa ? '#59e6ff' : '#ffb347';
    c.lineWidth = 8;
    c.beginPath();
    if (c.roundRect) c.roundRect(8, 8, 496, 240, 30); else c.rect(8, 8, 496, 240);
    c.stroke();
    try {
      const img = this._psIcons && this._psIcons[def.name];
      if (img && img.complete && img.naturalWidth) {
        c.drawImage(img, 28, 48, 160, 160);
      } else {
        c.fillStyle = activa ? '#59e6ff' : '#ffb347';
        c.beginPath(); c.arc(108, 128, 74, 0, 7); c.fill();
        c.fillStyle = 'rgba(8,14,26,0.85)';
        c.beginPath(); c.arc(108, 128, 52, 0, 7); c.fill();
        c.fillStyle = activa ? '#59e6ff' : '#ffb347';
        c.font = 'bold 64px Trebuchet MS, sans-serif';
        c.textAlign = 'center';
        c.fillText('!', 108, 152);
        c.textAlign = 'left';
      }
    } catch (e) { /* */ }
    c.textAlign = 'left';
    c.fillStyle = activa ? '#59e6ff' : '#ffb347';
    c.font = 'bold 33px Trebuchet MS, sans-serif';
    c.fillText(activa ? '¡SUPERPODER!' : 'AX-9 PREPARA…', 210, 76);
    c.fillStyle = '#ffffff';
    const nm = String(def.name || '').toUpperCase();
    c.font = 'bold ' + (nm.length > 14 ? 36 : 45) + 'px Trebuchet MS, sans-serif';
    c.fillText(nm, 210, 136);
    c.fillStyle = '#9fb8d8';
    c.font = '25px Trebuchet MS, sans-serif';
    c.fillText(activa ? '¡Esquiva la trampa!' : '¡Atento a la mesa!', 210, 190);
    this._psTex.needsUpdate = true;
    this.powerSign.visible = true;
  }
  _psOculta() { if (this.powerSign) this.powerSign.visible = false; }

  /* — LLUVIA DE ESTRELLAS (confeti con estrellas, convención del núcleo) — */
  _confetiStart(p) {
    const g = this.game;
    if (!this._poolConfeti) {
      this._poolConfeti = [];
      const tex = _texEstrella();
      this._poolTex.add(tex);
      for (let i = 0; i < 40; i++) {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({
          map: tex, transparent: true, depthWrite: false, opacity: 0,
        }));
        s.renderOrder = 30;
        const esc = 0.11 + Math.random() * 0.07;   // estrellitas (no pancartas)
        s.scale.set(esc, esc, 1);
        g.rig.add(s);
        this._poolConfeti.push({ s, on: false, x: 0, y: 0, z: 0, vy: 0, vr: 0 });
      }
    }
    this._confeti = { t: 0, dur: (p.duration || 8) };
    try { g.audio.playNoise(0.5, 900, 0.4, 0.05, 0); } catch (e) { /* */ }
  }
  _confetiStep(dt, a) {
    const c = this._confeti;
    if (!c) return;
    c.t += dt;
    const dentro = c.t < c.dur;
    for (const p of this._poolConfeti) {
      if (!p.on && dentro && Math.random() < dt * 8) {
        p.on = true;
        p.x = (Math.random() * 2 - 1) * 1.2;
        p.y = 2.0 + Math.random() * 0.4;
        p.z = -1.50 + Math.random() * 1.55;        // TU campo (convención núcleo)
        p.vy = -(0.35 + Math.random() * 0.3);
        p.vr = (Math.random() - 0.5) * 6;
      }
      if (p.on) {
        p.y += p.vy * dt;
        p.s.material.rotation += p.vr * dt;
        p.s.position.set(p.x, p.y, p.z);
        p.s.material.opacity = Math.min(1, p.y * 2);
        if (p.y < 0.1 || !dentro) { p.on = false; p.s.material.opacity = 0; }
      }
    }
    if (!dentro && c.t > c.dur + 1.5) { this._confeti = null; this._poderFin(); }
  }

  /* — METEORITOS: caen a TU campo y BLOQUEAN la bola (patrón Burla) ------ */
  _meteorStep(dt, a, ball, rally) {
    const g = this.game;
    const D = this.D;
    a.spawnT -= dt;
    // nacimiento escalonado
    if (a.spawnK < a.n && a.spawnT <= 0) {
      const r = this.rocas.find((x) => !x.on);
      if (r) {
        r.on = true; r.cayendo = true;
        r.x = (Math.random() * 2 - 1) * 0.95;
        r.z = -1.45 + Math.random() * 1.35;        // TU campo
        r.y = 2.7 + Math.random() * 0.4;
        r.vy = -2.6;
        r.vida = 0;
        r.s.visible = true;
        r.mat.opacity = 1;
        r.s.scale.set(0.34, 0.34, 1);
        r.tierraY = D.tableTopY + 0.17;
      }
      a.spawnK++;
      a.spawnT = 0.7;
    }
    // física de rocas + bloqueo de la bola (segmento prev→actual, Burla)
    for (const r of this.rocas) {
      if (!r.on) continue;
      if (r.cayendo) {
        r.y += r.vy * dt;
        r.mat.rotation += dt * 2.4;
        if (r.y <= r.tierraY) {
          r.y = r.tierraY;
          r.cayendo = false;
          try { g.audio.playNoise(0.25, 180, 0.5, 0.2, 0); } catch (e) { /* */ }
          try { if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 90); } catch (e) { /* */ }
        }
      } else {
        r.vida += dt;
        r.s.position.y = r.y + Math.sin(this._t * 2.1 + r.ph) * 0.012;
        if (r.vida > 7) r.mat.opacity -= dt * 1.4;
        if (r.mat.opacity <= 0) { r.on = false; r.s.visible = false; continue; }
      }
      r.s.position.x = r.x;
      r.s.position.z = r.z;
      if (r.cayendo) r.s.position.y = r.y;
    }
    // colisión de la bola con rocas VIVAS (solo rally, anti-túnel)
    if (rally && ball && ball.pos && this._bolaPrev) {
      const rB = D.ballRadius;
      const prev = this._bolaPrev;
      const cur = ball.pos;
      for (const r of this.rocas) {
        if (!r.on || r.mat.opacity < 0.6) continue;
        const rr = 0.17 + rB;
        const ex = cur.x - r.x, ey = cur.y - r.s.position.y, ez = cur.z - r.z;
        const dentro = ex * ex + ey * ey + ez * ez < rr * rr;
        // cruce del segmento con la esfera (muestreo)
        let hit = dentro;
        if (!hit) {
          const dx = cur.x - prev.x, dy = cur.y - prev.y, dz = cur.z - prev.z;
          const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
          const steps = Math.max(1, Math.ceil(dist / 0.05));
          for (let s2 = 1; s2 <= steps; s2++) {
            const f = s2 / steps;
            const sx = prev.x + dx * f, sy = prev.y + dy * f, sz = prev.z + dz * f;
            const qx = sx - r.x, qy = sy - r.s.position.y, qz = sz - r.z;
            if (qx * qx + qy * qy + qz * qz < rr * rr) { hit = true; break; }
          }
        }
        if (!hit) continue;
        // la roca ESTALLA y la bola sale REBOTADA hacia arriba
        r.on = false; r.s.visible = false; r.mat.opacity = 0;
        const v = ball.vel;
        v.y = Math.max(2.3, Math.abs(v.y) * 0.5 + 1.4);
        v.x *= 0.5; v.z *= 0.5;
        try { g.audio.playNoise(0.3, 500, 0.5, 0.18, 0); } catch (e) { /* */ }
        try { g.audio.playOsc(300, 90, 0.2, 'square', 0.12, 0); } catch (e) { /* */ }
        try { if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.45, 80); } catch (e) { /* */ }
        break;
      }
    }
    // memoria del segmento bola (anti-túnel del próximo frame)
    if (ball && ball.pos) {
      if (!this._bolaPrev) this._bolaPrev = new THREE.Vector3();
      this._bolaPrev.copy(ball.pos);
    }
  }

  /* — RAYO TRACTOR: el haz curva la bola hacia el eje central ------------ */
  _tractorStep(dt, a, ball, rally) {
    const g = this.game;
    const pulso = 0.34 + Math.sin(this._t * 9) * 0.10;
    this.beamMat.opacity = Math.min(0.5, pulso);
    this.beam.rotation.y += dt * 1.6;
    if (rally && ball && ball.pos) {
      // atracción lateral hacia x=0 (tu retorno se cierra solo)
      ball.vel.x -= ball.pos.x * 0.9 * dt;
    }
  }

  /* — GRAVEDAD CERO: la bola flota en ondas verticales ------------------- */
  _ceroStep(dt, a, ball, rally) {
    const g = this.game;
    const D = this.D;
    for (const m of this.motas) {
      m.y += Math.sin(this._t * 1.4 + m.ph) * 0.0022;
      m.x += Math.cos(this._t * 0.9 + m.ph) * 0.0012;
      m.s.position.set(m.x, m.y, m.z);
      m.s.material.opacity = 0.30 + Math.sin(this._t * 2.2 + m.ph) * 0.18;
      const esc = 0.05 + Math.sin(this._t * 3 + m.ph) * 0.015;
      m.s.scale.set(esc, esc, 1);
    }
    if (rally && ball && ball.vel) {
      // onda de ingravidez: empuje vertical suave alternante
      ball.vel.y += Math.sin(this._t * 3.1 + ball.pos.z * 1.7) * 2.3 * dt;
    }
  }
}

/* ============================================================================
 *  MapaEO (v2.130) — el MAPA DEL CAMPEONATO en la PARED IZQUIERDA (convención
 *  de la casa: misma posición/escala que WizardMap del mago y el mapa del
 *  Oeste: −2,98 / 1,5 / −0,9 mirando al centro; arte 1380×752). Ruta de 5
 *  nodos + insignia final, TAPAS sobre los nodos futuros, anillo dorado en
 *  el nodo vigente, hover azul al apuntar con la pala y REJUGA por gatillo
 *  (contrato replayMap del núcleo, v2.96 — el campeonato superado queda
 *  ABIERTO). PERFECTAMENTE ESTÁTICO salvo el anillo.
 *  Nodos medidos sobre el arte oficial (scripts/make_art_eo_v2.py):
 *   0 DUELO 1 (210,260,r100) · 1 CINTURÓN (455,500,r120) · 2 DUELO 2
 *   (700,260,r100) · 3 TORMENTA (945,500,r120) · 4 DUELO FINAL (1190,260,r100)
 * ========================================================================== */
class MapaEO {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.nodesPx = [
      { x: 210, y: 260, r: 100, tapa: false, ts: 1.0 },
      { x: 455, y: 500, r: 120, tapa: true, ts: 1.2 },
      { x: 700, y: 260, r: 100, tapa: true, ts: 1.0 },
      { x: 945, y: 500, r: 120, tapa: true, ts: 1.2 },
      { x: 1190, y: 260, r: 100, tapa: true, ts: 1.0 },
    ];
    this.currentIdx = 0;
    this.IMG_W = 1380;
    this.IMG_H = 752;
    this.PW = 1.68;
    this.PH = 1.68 * 752 / 1380;
    this.TAPA_W = 165 / 1380 * this.PW;
    this.TAPA_H = this.TAPA_W;
    this.inited = false;
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.group = new THREE.Group();
    // respaldo de acero (como WizardMap)
    const back = new THREE.Mesh(
      new THREE.BoxGeometry(this.PW + 0.06, this.PH + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x1a2436, roughness: 0.85, metalness: 0.1 }),
    );
    back.position.z = -0.013;
    this.group.add(back);
    this.plane = new THREE.Mesh(
      new THREE.PlaneGeometry(this.PW, this.PH),
      new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, opacity: 0 }),
    );
    this.group.add(this.plane);
    this.texs = [];
    const murl = new URL('./assets/mapa.png', import.meta.url).href;
    new THREE.TextureLoader().load(murl, (tex) => {
      tex.colorSpace = THREE.SRGBColorSpace;
      this.texs.push(tex);
      if (this.plane) {
        this.plane.material.map = tex;
        this.plane.material.opacity = 1;
        this.plane.material.needsUpdate = true;
      }
    });
    // tapas sobre los nodos futuros
    this.tapas = [];
    const turl = new URL('./assets/tapa.png', import.meta.url).href;
    new THREE.TextureLoader().load(turl, (tex) => {
      tex.colorSpace = THREE.SRGBColorSpace;
      this.texs.push(tex);
      this.nodesPx.forEach((n, i) => {
        if (!n.tapa) return;
        const m = new THREE.Mesh(
          new THREE.PlaneGeometry(this.TAPA_W * n.ts, this.TAPA_H * n.ts),
          new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }),
        );
        const p = this._pxToLocal(n.x, n.y);
        m.position.set(p[0], p[1], 0.003);
        m.renderOrder = 2;
        this.group.add(m);
        this.tapas.push({ idx: i, mesh: m });
      });
      this.refresh();
    });
    // anillo marcador
    this.marker = new THREE.Mesh(
      new THREE.RingGeometry(0.118, 0.144, 48),
      new THREE.MeshBasicMaterial({
        color: 0xf6d34c, transparent: true, depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    this.marker.material.opacity = 0.9;
    this.marker.position.z = 0.006;
    this.marker.renderOrder = 3;
    this.group.add(this.marker);
    this.group.position.set(-2.98, 1.5, -0.9);
    this.group.rotation.y = Math.PI / 2;
    this.group.visible = true;
    g.rig.add(this.group);
    this.refresh();
  }

  _pxToLocal(px, py) {
    return [(px / this.IMG_W - 0.5) * this.PW, (0.5 - py / this.IMG_H) * this.PH];
  }

  /** Nodo vigente: campeón = ruta completa sin anillo; si no, la etapa. */
  _computeCurrent() {
    if (this.ctrl._champion) return -1;
    return Math.min(Math.max(this.ctrl.stage | 0, 0), 4);
  }

  refresh() {
    if (!this.group) return;
    this.currentIdx = this._computeCurrent();
    const champion = this.currentIdx < 0;
    if (this.tapas && this.tapas.length) {
      for (const t of this.tapas) {
        t.mesh.visible = !champion && this.currentIdx < t.idx;
      }
    }
    if (this.marker) {
      this.marker.material.color.setHex(0xf6d34c);
      this.marker.visible = !champion;
      if (!champion) {
        const n = this.nodesPx[this.currentIdx];
        const p = this._pxToLocal(n.x, n.y);
        this.marker.position.x = p[0];
        this.marker.position.y = p[1];
        this.marker.scale.setScalar(n.r / 120);
      }
    }
  }

  /** v2.96 · REJUGAR: resalta el nodo apuntado (azul, algo mayor). */
  hover(idx) {
    if (!this.marker) return;
    if (idx < 0 || idx >= this.nodesPx.length) { this.refresh(); return; }
    const n = this.nodesPx[idx];
    const p = this._pxToLocal(n.x, n.y);
    this.marker.visible = true;
    this.marker.material.color.setHex(0x7ec8ff);
    this.marker.position.x = p[0];
    this.marker.position.y = p[1];
    this.marker.scale.setScalar((n.r / 120) * 1.22);
  }

  /** Contrato replayMap del núcleo (v2.96): plano + nodos + techo apuntable. */
  replayData() {
    if (!this.plane) return null;
    return {
      plane: this.plane,
      nodesPx: this.nodesPx,
      imgW: this.IMG_W, imgH: this.IMG_H,
      maxIdx: this.ctrl._champion ? 4 : Math.min(this.ctrl.stage | 0, 4),
    };
  }

  hide() { if (this.group) this.group.visible = false; }
  show() { if (this.group) { this.group.visible = true; this.refresh(); } }

  /** Dispose completo (regla Quest: nada queda colgado al salir). */
  dispose() {
    if (!this.inited) return;
    this.inited = false;
    try { if (this.group.parent) this.group.parent.remove(this.group); } catch (e) { /* */ }
    for (const t of (this.texs || [])) { try { t.dispose(); } catch (e) { /* */ } }
    this.texs = [];
    try { this.marker.geometry.dispose(); this.marker.material.dispose(); } catch (e) { /* */ }
    try { this.plane.geometry.dispose(); this.plane.material.dispose(); } catch (e) { /* */ }
    try { this.group.clear(); } catch (e) { /* */ }
    this.group = null; this.plane = null; this.marker = null; this.tapas = [];
  }
}

function D_z(ctrl) {
  return (CORE && CORE.DIMS ? CORE.DIMS.tableCenterZ : -1.6);
}
// (D_z se conserva por compatibilidad con QA por consola)

/* ====================== MÓDULO (contrato ChampLoader) ==================== */
export default {
  id: 'estacion_orbital',
  decor: {"pieces": [{"file": "assets/decor/troquel1.png", "h": 1.2, "x": -2.55, "z": -2.5, "sway": 0.5}, {"file": "assets/decor/troquel2.png", "h": 0.8, "x": 2.1, "z": -2.5, "sway": 0.3}, {"file": "assets/decor/troquel3.png", "h": 1, "x": 2.45, "z": -0.85, "sway": 0.4}]},
  room: {"floor": "assets/sala_floor.jpg", "ceil": "assets/sala_ceil.jpg", "back": "assets/sala_back.jpg", "front": "assets/sala_front.jpg", "left": "assets/sala_left.jpg", "right": "assets/sala_right.jpg"},
  get controller() { return CTRL; },
  /** v2.128: ¿campeonato superado? (cinta ★ SUPERADO del menú) */
  isChampion() { return !!(CTRL && CTRL._champion); },
  /** v2.130 · INTRO de campeonato: silencia la BSO privada mientras suena
   *  el vídeo de la historia del rival (hook opcional del núcleo). */
  champIntroPause(on) {
    if (!CTRL) return;
    try { on ? CTRL.musicOff() : CTRL.musicOn(); } catch (e) { /* */ }
  },
  init(ctx) {
    if (!window.__PP_CORE) {
      throw new Error('estacion_orbital: window.__PP_CORE no disponible (¿se cargó fuera del juego?)');
    }
    GAME.g = ctx.game;
    CTRL = new StockController(ctx.game);
    CTRL.manifest = ctx.manifest || null;   // el núcleo lo entrega (v2.125)
    // v3: física del núcleo para las PRUEBAS (patrón orbe de magia)
    STEP = window.__PP_CORE.stepPhysics || null;
    if (!STEP) console.warn('[estacion_orbital] stepPhysics no disponible: las pruebas de habilidad quedan inoperativas');
    TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    const onLang = () => {
      TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    };
    document.addEventListener('pp-lang', onLang);
  },
  start() { if (CTRL) CTRL.startChamp(); },
  leave() { if (CTRL) CTRL.leave(); },
  resetRecords() { if (CTRL) CTRL.resetRecords(); },
  update(dt) { if (CTRL && CTRL.state) CTRL.update(dt); },
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },
  aiMul() { return CTRL ? CTRL.aiMul() : 1; },
  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },
  reenter() { if (CTRL) CTRL.reenter(); },
  // v2.130 · REJUGADA por el mapa del camino (pared izquierda)
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },
  musicOff() { if (CTRL) CTRL.musicOff(); },   // invariante UNA MELODÍA v2.125
  /** v3: PRUEBA activa → el núcleo NO integra la bola y llama testStep. */
  testActive() { return !!(CTRL && CTRL.prueba && CTRL.prueba.stepActive()); },
  testStep(dt) {
    if (CTRL && CTRL.prueba && CTRL.prueba.stepActive()) {
      try { CTRL.prueba.step(dt); }
      catch (e) { console.warn('[estacion.testStep]', e); }
    }
  },
};


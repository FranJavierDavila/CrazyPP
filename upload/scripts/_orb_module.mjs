/* ============================================================================
 *  Estación Orbital (estacion_orbital) — v3.1 «PLANTILLA FINAL» (V2.131)
 *  ----------------------------------------------------------------------------
 *  v3.2.1 (ORB2) · AJUSTE FINO DEL DECORADO (informe del dueño en casco):
 *    (1) ASTRO al sitio de la casa: convención FORAJIDO (oeste v2.87) —
 *        plano de CUERPO ENTERO de 2,15 m (personaje visible ≈ 1,8 m), PIES
 *        EN EL SUELO, junto al fondo a la derecha (x 1,62 · z −4,5). Antes
 *        flotaba 1,75 m junto a la mesa (z −3,5): se leía «metido en la
 *        pared derecha» y más bajo que el resto de rivales.
 *    (2) MAPA: nodos re-medidos sobre el arte del dueño (el nodo 5 estaba
 *        ~70 px ALTO: y 266 → 335) y tapas del tamaño del arte (240 px
 *        base, lección v2.136 del oeste: los medallones miden ~215-235 px
 *        y las tapas de 165 px NO los cubrían).
 *    (3) CARTEL DE SUPERPODER = el de la CASA: port 1:1 del ArcadePowerSign
 *        de La Locura (v2.40/v2.88) — arte SuperPower!! ENFRENTE DEL JUGADOR
 *        A LA ALTURA DE LA RED (netTopY+0,14, 30 cm hacia el jugador),
 *        coreografía ≈2 s (entra por la izquierda, vaivén con HALO que
 *        respira, sale por la derecha) + MEDALLÓN CIRCULAR del poder
 *        (power*.png) junto al arte. Fuera el panel provisional.
 *    (4) PODERES ENCIMA DE LA MESA: meteoritos (x ±0,60 · z −1,45..−0,45),
 *        haz del tractor SOBRE tu campo (z −1,05, punta en la superficie),
 *        motas de gravedad cero y lluvia de estrellas repartidas por TU
 *        campo. Antes beam/motas/rocas se iban al origen o tras la red y
 *        «no tenían efectos».
 *    (5) EXPRESIONES DEL ASTRO por momento de partida (motor del clown de
 *        La Locura, mismos umbrales): anotas tú → surprised/angry (combo),
 *        anota él → laughing/crazy (racha), rallye largo → picando, va
 *        perdiendo → loosing, match-point en contra → panic, duelo →
 *        duelo, fin → derrotado/triunfante. Sin recargas si el estado no
 *        cambia (la vigilancia corre cada frame).
 *    (6) CARTEL DE BIENVENIDA fuera de la pared del fondo (z −5,44 →
 *        −5,28: antes quedaba a 11 cm del muro y se leía «metido»).
 *  ----------------------------------------------------------------------------
 *  v3.2.0 (ORB1) · DECORADO REAL DEL DUEÑO + MUROS ORBITALES: (1) SALA con
 *    el arte del dueño en los 6 planos (literas, ventanal con la Tierra,
 *    esclusa, suelo y techo — patrón vagón del Oeste). (2) RIVAL ASTRO con
 *    las 12 poses del artista (convención clown assets/<estado>.webp; en
 *    duelo focused, con superpoder crazy, al caer defeated). (3) MAPA nuevo
 *    (1376×768) que define las pruebas como MUROS → port del ARKANOID de
 *    La Locura (2 variantes + pistola láser) con cartel explicativo sobre
 *    la plantilla del artista (normas_astro.png vía NORMAS_SKIN). (4) CARTEL
 *    DE SUPERPODER con la etiqueta de la casa (superpower.png) + miniatura
 *    del poder. (5) RECORTABLES reales por el suelo (cohete, astro, lander,
 *    telescopio). La física CCD/SRV2/FEEL1 del núcleo: INTACTA.
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
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';   // v3.2.0: pistol.glb del MURO 2

const CORE = (typeof window !== 'undefined' && window.__PP_CORE) || null;
const GAME = { g: null };
let CTRL = null;
let TL = 'es';
let STEP = null;                  // stepPhysics del núcleo (capturado en init)

const tx = (es, en) => (TL === 'en' ? (en || es) : es);

/* ----------------------------- CONFIGURACIÓN ----------------------------- */
const CFG = {
  rival: 'ASTRO',   // v3.2.0: el astronauta del arte del dueño
  puntos: 11,
  /* Camino de 5 etapas (índices de etapa 0..4) */
  etapas: [
    { kind: 'duelo', id: 'duelo1', name: 'Duelo 1', aiMul: 0.90 },
    { kind: 'prueba', id: 'muro1', name: 'Arkanoid orbital' },   // v3.2.0: MURO según el mapa del dueño
    { kind: 'duelo', id: 'duelo2', name: 'Duelo 2', aiMul: 1.12 },
    { kind: 'prueba', id: 'muro2', name: 'Arkanoid II' },   // v3.2.0: MURO rojo/azul + láser
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

/* ============================================================================
 *  v3.2.0 · MUROS ORBITALES — port del ARKANOID de La Locura (QA de casas)
 *  ----------------------------------------------------------------------------
 *  El mapa nuevo del dueño dibuja las etapas 2 y 4 como MUROS DE LADRILLOS
 *  (misma iconografía que el mapa del clown): el camino de la plantilla
 *  pasa de las DIANAS a los MUROS. Variante 1: muro clásico de 30 ladrillos
 *  rojos (2 min, 5 vidas). Variante 2: 54 ladrillos rojos/azules + PISTOLA
 *  LÁSER pistol.glb en la mano libre (el azul explota y queda rojo; el rojo
 *  es inmune; los rojos vivos se vuelven azules con el tiempo; ladrillo
 *  negro del tiempo extra = +1 min). Física del núcleo intacta vía
 *  stepPhysics + colisionador extra por subpaso (anti-túnel).
 *  ========================================================================== */
const __CORE = (typeof window !== 'undefined' && window.__PP_CORE) || null;
const T = (k) => ((__CORE && __CORE.T) ? __CORE.T(k) : k);
const DIMS = (CORE && CORE.DIMS) || {
  tableHalfWidth: 0.7625, tableTopY: 0.76, tableCenterZ: -1.6,
  tableHalfLength: 1.37, ballRadius: 0.02, gravity: 9.6,
};
const stepPhysics = (CORE && CORE.stepPhysics) || null;
let GUN_ART_URL = '';
const GUN_MOUNT_PITCH = 0;
const GUN_MUZZLE = new THREE.Vector3(0.0003, 0.092, -0.163);

function arcadeCanvas(w, h) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  return cv;
}

const ARK_CFG = {
  // v2.42 · TODO ALINEADO CON LA MESA (DIMS): el muro ocupa el ancho EXACTO
  // de la mesa y está ENRASADO con su borde de fondo; las 3 paredes del
  // perímetro nacen EN LOS BORDES de la mesa (laterales ±tableHalfWidth,
  // fondo en el borde lejano) y la red se retira (también sus físicas).
  // v2.44 · PAREDES LATERALES +30 cm HACIA EL JUGADOR (sideZ0 = red + 0,30):
  // los cristales llegan MÁS CERCA del jugador y la bola ya no se cuela por
  // los laterales de su campo.
  cols: 6, rows: 5, gap: 0.014, depth: 0.12,
  bw: (DIMS.tableHalfWidth * 2 - 5 * 0.014) / 6,   // 0,2425 m: muro = ancho de mesa
  bh: 0.165,
  baseY: DIMS.tableTopY + 0.005,     // APOYADO en la superficie de la mesa
  sideX: DIMS.tableHalfWidth,        // 0,7625 — cristales EN el borde de la mesa
  // v2.47 · MISMAS DIMENSIONES DE MUROS QUE EL ARKANOID 2 (petición expresa):
  // los cristales del ARKANOID 1 llegan también a red + 80 cm, así ambos
  // niveles comparten el recinto EXACTO (visual y colisión con this.C).
  sideZ0: DIMS.tableCenterZ + 0.80,  // v2.47: red + 80 cm — IGUAL que ARK2
  sideZ1: DIMS.tableCenterZ - DIMS.tableHalfLength,  // -2,97 — borde de FONDO
  backY: 1.5,        // pared del fondo: 1,5 m SOBRE la mesa (sostiene el póster)
  glassY: 1.05,      // cristales laterales: 1,05 m SOBRE la mesa
  // FÍSICA = la de una PARTIDA NORMAL (DIMS.gravity + aerodinámica + Magnus
  // + MISMO golpeo de pala). La mesa otorga FUERZA MÍNIMA de bote (la bola
  // nunca queda muerta) y el recinto pierde energía de forma realista.
  apexMin: 0.38,     // bote mínimo que la mesa OTORGA (sobre la superficie)
  brickRest: 0.86,   // pérdida de la componente normal en el ladrillo
  wallRest: 0.82,    // pérdida en las paredes perimetrales
  time: 120,         // 2 minutos
  lives: 5,          // 5 saques
  serveAutoT: 12,    // saque automático si no actúas (bola nunca atascada)
  variant: 1,        // v2.44: ARKANOID clásico (30 ladrillos rojos + póster)
};

/* ---------- v2.44 · ARKANOID 2 (variante 2 del camino) -----------------
 * · MUCHOS más ladrillos (9 x 6 = 54) y 2,5 minutos.
 * · Ladrillos ROJOS (sólo la PALA los rompe) y AZULES (sólo el LÁSER los
 *   destruye: al impactar, el azul EXPLOTA y queda ROJO, no desaparece).
 * · Parte de los ladrillos nacen AZULES; y los ROJOS que quedan vivos se
 *   van VOLVIENDO AZULES con el tiempo (uno cada pocos segundos).
 * · La pistola láser (pistola.glb) va TODO EL RATO en la mano libre:
 *   sólo desaparece el instante del saque (esa mano lanza la bola).
 * · SIN póster-escondite del superpoder tras el muro: pared neutra.
 * · Cristales laterales OTRO +30 cm hacia el jugador (red + 0,60). */
const ARK2_CFG = Object.assign({}, ARK_CFG, {
  variant: 2,
  cols: 9, rows: 6, gap: 0.012,
  bw: (DIMS.tableHalfWidth * 2 - 8 * 0.012) / 9,   // 0,1586 m
  bh: 0.15,
  // v2.46 · +20 cm MÁS: red + 80 cm (30+30+20). Y ojo: la colisión del
  // perímetro usa SIEMPRE this.C (antes _extraCollide leía ARK_CFG fijo y
  // los 50 cm nuevos NO colisionaban — bug del "cristal sin comportamiento").
  sideZ0: DIMS.tableCenterZ + 0.80,  // v2.46: red + 80 cm hacia ti
  time: 150,         // 2,5 minutos (muro del doble de ladrillos)
  lives: 5,
  blueStart: 0.30,   // ~30% de los ladrillos nacen AZULES
  convertFirst: 12,  // gracia (s) antes de la conversión temporal
  convertEvery: 7,   // cada 7 s un ROJO vivo pasa a AZUL
});
ARK_CFG.z = ARK_CFG.sideZ1 + ARK_CFG.depth / 2 + 0.004;
ARK2_CFG.z = ARK2_CFG.sideZ1 + ARK2_CFG.depth / 2 + 0.004;

/* ---------- texturas del muro v2.41 (biselado + flash de destrucción) -- */
function arkBrickTexture() {
  const cv = arcadeCanvas(128, 64);
  const g2 = cv.getContext('2d');
  // textura en ESCALA DE GRISES: el color del material la multiplica
  const grd = g2.createLinearGradient(0, 0, 0, 64);
  grd.addColorStop(0, '#c9c9c9');
  grd.addColorStop(0.16, '#ffffff');      // bisel superior iluminado
  grd.addColorStop(0.52, '#a2a2a2');
  grd.addColorStop(0.88, '#6e6e6e');      // sombra inferior
  grd.addColorStop(1, '#585858');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 128, 64);
  g2.strokeStyle = 'rgba(0,0,0,0.6)';
  g2.lineWidth = 5;
  g2.strokeRect(0, 0, 128, 64);
  g2.strokeStyle = 'rgba(255,255,255,0.35)';
  g2.lineWidth = 2;
  g2.strokeRect(4, 4, 120, 56);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function arkFlashTexture() {
  const cv = arcadeCanvas(128, 128);
  const g2 = cv.getContext('2d');
  const grd = g2.createRadialGradient(64, 64, 4, 64, 64, 62);
  grd.addColorStop(0, 'rgba(255,240,200,0.95)');
  grd.addColorStop(0.4, 'rgba(255,190,110,0.55)');
  grd.addColorStop(1, 'rgba(255,150,60,0)');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 128, 128);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* v2.44 · textura de las PARTÍCULAS DE VIENTO del abanico (chorro suave) */
function arkWindTexture() {
  const cv = arcadeCanvas(64, 64);
  const g2 = cv.getContext('2d');
  const grd = g2.createRadialGradient(32, 32, 2, 32, 32, 30);
  grd.addColorStop(0, 'rgba(235,250,255,0.95)');
  grd.addColorStop(0.45, 'rgba(160,225,255,0.5)');
  grd.addColorStop(1, 'rgba(140,210,255,0)');
  g2.fillStyle = grd;
  g2.beginPath();
  g2.ellipse(32, 32, 32, 20, 0, 0, Math.PI * 2);
  g2.fill();
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

/* v2.45 · textura del vidrio ESCARCHADO de las paredes laterales: base
 * helada + moteado determinista + panel vertical + brillo diagonal. Da
 * cuerpo al cristal (antes opacity 0,12 liso = "no hay nada"). */
function arkGlassTexture() {
  const cv = arcadeCanvas(256, 256);
  const g2 = cv.getContext('2d');
  const grd = g2.createLinearGradient(0, 0, 0, 256);
  grd.addColorStop(0, '#eaf7fc');
  grd.addColorStop(0.5, '#cfe9f2');
  grd.addColorStop(1, '#b6dae7');
  g2.fillStyle = grd;
  g2.fillRect(0, 0, 256, 256);
  // escarcha (pseudoaleatorio determinista)
  for (let i = 0; i < 460; i++) {
    const x = (i * 97 + 31) % 256, y = (i * 173 + 57) % 256;
    g2.fillStyle = (i % 2) ? 'rgba(255,255,255,0.5)' : 'rgba(110,165,190,0.3)';
    g2.beginPath();
    g2.arc(x, y, 1 + (i % 3) * 0.7, 0, Math.PI * 2);
    g2.fill();
  }
  // banda de brillo diagonal
  const sh = g2.createLinearGradient(0, 256, 256, 0);
  sh.addColorStop(0.32, 'rgba(255,255,255,0)');
  sh.addColorStop(0.5, 'rgba(255,255,255,0.45)');
  sh.addColorStop(0.68, 'rgba(255,255,255,0)');
  g2.fillStyle = sh;
  g2.fillRect(0, 0, 256, 256);
 // junta central del panel de vidrio
  g2.strokeStyle = 'rgba(40,80,100,0.45)';
  g2.lineWidth = 3;
  g2.beginPath(); g2.moveTo(128, 0); g2.lineTo(128, 256); g2.stroke();
  g2.strokeStyle = 'rgba(255,255,255,0.55)';
  g2.lineWidth = 1;
  g2.beginPath(); g2.moveTo(131, 0); g2.lineTo(131, 256); g2.stroke();
  g2.beginPath(); g2.moveTo(125, 0); g2.lineTo(125, 256); g2.stroke();
  // marco sutil
  g2.strokeStyle = 'rgba(30,60,80,0.5)';
  g2.lineWidth = 6;
  g2.strokeRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}


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

class EOArkanoid {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.active = false;
    this.inited = false;
    this.variant = 1;          // v2.44: 1 = clásico · 2 = ARKANOID 2 (rojos/azules)
    this.C = ARK_CFG;          // config ACTIVA (se fija en start())
    this.phase = 'idle';       // intro | serve | play | result
    this.phaseT = 0;
    this.time = ARK_CFG.time;
    this.lives = ARK_CFG.lives;
    this.bricksLeft = 0;
    this._hudDirty = true;
    this._lastSec = -1;
    this._warn60 = false;
    this._banner = null;
    this._msg = '';
    this._msgT = 0;
    this._dying = [];
    this._debris = [];
    this._flashes = [];        // v2.41: flashes de destrucción (pool)
    this._netParts = null;     // v2.41: malla/banda/postes de la red
    this._serveT = 0;          // v2.41: tiempo esperando el saque
    this._crossed = false;     // v2.41: la bola cruzó la red en este intento
    this._stuckT = 0;          // v2.42: anti-atasco (bola no jugable)
    this._tokCd = 0;           // v2.42: anti-spam del «tok» de las paredes
    // v2.44 · conversión temporal ROJO->AZUL (sólo variante 2)
    this._convT = 0;
    // v2.46 · LADRILLO NEGRO del TIEMPO EXTRA (sólo variante 2): aparece
    // en los últimos 30 s en huecos de ladrillos destruidos, salta cada 2 s
    // y al destruirlo (bola o láser) regala +1 minuto (UNA sola vez).
    this._timeBrick = null;    // { slot, t, min, max } — activo o null
    this._timeUsed = false;    // el +1 min ya se cogió en esta prueba
    this._time30 = false;      // el aviso sonoro de apremio ya sonó
    this._extraFx = null;      // { pos, t } — plano "+1 MIN" flotando
    // v2.44 · ABANICO (corriente de aire para desatascar la bola)
    this._fanSamp = [];        // muestras {t, vx} de la velocidad lateral
    this._fanT = 0;            // segundos restantes de viento activo
    this._fanCd = 0;           // cooldown del abanico
    this._fanKick = 0;         // impulso acumulado (0..1) hasta el empujón
    this._fanBlowT = 0;        // temporizador del soplido sonoro
    this._fanHintDone = false; // el aviso del gesto sólo se muestra una vez
    this._wind = [];           // partículas de viento (pool)
    // v2.42: hook de colisiones ARKANOID por SUBPASO de la física NORMAL
    this._extra = (ball) => this._extraCollide(ball);
    this._spot = new THREE.Vector3();
    this._tmpA = new THREE.Vector3();
    this._tmpB = new THREE.Vector3();
    // v2.133 · BOLA CLON del superpoder (CLOWN Nv. 3: bola doble) — la malla
    // se crea AQUÍ (constructor: UNA vez por sesión) y NO en build(): el
    // split sólo sale en el DUELO JEFE (Nv. 3) y llegando a la etapa 5 con
    // sesión fresca el arkanoid nunca llegó a construirse → clon físico e
    // INVISIBLE (reporte del dueño: «el poder de dos bolas no funciona»). Regla
    // Quest intacta: nada se crea por partida (esto corre una vez, al montar).
    const g0 = this.game;
    this.cloneMesh = new THREE.Mesh(
      g0.ballMesh ? g0.ballMesh.geometry
        : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
      new THREE.MeshStandardMaterial({
        color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff, emissiveIntensity: 0.55,
      }));
    this.cloneMesh.castShadow = true;
    this.cloneMesh.visible = false;
    g0.rig.add(this.cloneMesh);
    // cinturón y tirantes: _startSplit puede exigir la malla en cualquier
    // momento (idempotente) — antes vivía SÓLO en el primer build()
    this._makeCloneMesh = () => {
      if (this.cloneMesh) return;
      const gg = this.game;
      this.cloneMesh = new THREE.Mesh(
        gg.ballMesh ? gg.ballMesh.geometry
          : new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
        new THREE.MeshStandardMaterial({
          color: 0xffffff, roughness: 0.3, emissive: 0xbfd4ff,
          emissiveIntensity: 0.55,
        }));
      this.cloneMesh.castShadow = true;
      this.cloneMesh.visible = false;
      gg.rig.add(this.cloneMesh);
    };
  }

  build() {
    // v2.44: build con RECONSTRUCCIÓN por variante — el ARKANOID 2 cambia
    // muro (54 ladrillos rojos/azules), perímetro (cristales +60 cm) y
    // pared del fondo (sin póster). Se rellena sólo si cambia la variante.
    if (this.inited && this._builtV === this.variant) return;
    const g = this.game;
    const first = !this.inited;
    this.inited = true;
    const C = this.C;
    const W = C.cols * C.bw + (C.cols - 1) * C.gap;
    const H = C.rows * C.bh + (C.rows - 1) * C.gap;
    this.wallW = W; this.wallH = H;

    if (first) {
      // contenedores y materiales compartidos del decorado arcade
      this.railMat = new THREE.MeshStandardMaterial({
        color: 0xe8b45a, roughness: 0.4, metalness: 0.3, emissive: 0x3d2c08,
      });
      this.darkMat = new THREE.MeshStandardMaterial({
        color: 0x1b2233, roughness: 0.85, metalness: 0.08,
      });
      // v2.45 · CRISTALES con textura de vidrio ESCARCHADO: el material
      // semitransparente se ve LA PARED (moteado + paneles + brillo), no un
      // cristal invisible — se nota que hay un muro contra el que golpear.
      this.glassMat = new THREE.MeshStandardMaterial({
        color: 0xd6eef6, map: arkGlassTexture(), transparent: true,
        opacity: 0.52, roughness: 0.32, metalness: 0.06,
        side: THREE.DoubleSide, depthWrite: false,
      });
      this.fieldGroup = new THREE.Group();
      this.wallGroup = new THREE.Group();
      g.rig.add(this.fieldGroup);   // v2.44: anclado al rig (espacio de la mesa)
      g.rig.add(this.wallGroup);
      // textura de los ladrillos + materiales por COLOR (rojo/azul)
      const brickTex = arkBrickTexture();
      this.redMats = [0xd94f3d, 0xcf4536, 0xe25a46].map((c) =>
        new THREE.MeshStandardMaterial({
          color: c, map: brickTex, roughness: 0.55, metalness: 0.05,
          emissive: 0x2a0705,
        }));
      this.blueMats = [0x2f7fd4, 0x2a6fbe, 0x3a8ce4].map((c) =>
        new THREE.MeshStandardMaterial({
          color: c, map: brickTex, roughness: 0.42, metalness: 0.12,
          emissive: 0x061c38,
        }));
      this.brickGeo = new THREE.BoxGeometry(C.bw, C.bh, C.depth);
      // pools de escombros y flashes (compartidos)
      const dGeo = new THREE.BoxGeometry(0.05, 0.05, 0.05);
      for (let i = 0; i < 30; i++) {
        const dm = new THREE.Mesh(dGeo, this.redMats[0]);
        dm.visible = false;
        this.wallGroup.add(dm);
        this._debris.push({ mesh: dm, vel: new THREE.Vector3(), life: 0 });
      }
      const flashTex = arkFlashTexture();
      for (let i = 0; i < 6; i++) {
        const fm = new THREE.Mesh(
          new THREE.PlaneGeometry(0.55, 0.55),
          new THREE.MeshBasicMaterial({
            map: flashTex, transparent: true, opacity: 0, depthWrite: false,
            blending: THREE.AdditiveBlending,
          }));
        fm.visible = false;
        fm.renderOrder = 9;
        this.wallGroup.add(fm);
        this._flashes.push({ mesh: fm, t: 0 });
      }
      // v2.44 · PARTÍCULAS DE VIENTO del abanico (pool aditivo)
      const wTex = arkWindTexture();
      for (let i = 0; i < 26; i++) {
        const wm = new THREE.Mesh(
          new THREE.PlaneGeometry(0.05, 0.05),
          new THREE.MeshBasicMaterial({
            map: wTex, transparent: true, opacity: 0, depthWrite: false,
            blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
          }));
        wm.visible = false;
        wm.renderOrder = 8;
        g.rig.add(wm);
        this._wind.push({ mesh: wm, vel: new THREE.Vector3(), life: 0 });
      }
      // v2.133: la BOLA CLON (split) vive en el CONSTRUCTOR — aquí ya no se
      // crea (llegar al duelo JEFE sin build del arkanoid dejaba el clon
      // invisible). _makeCloneMesh sigue disponible como cinturón.
      // identificación de la RED (plano + banda + postes) para ocultarla
      this._netParts = g.tableGroup.children.filter((m) =>
        Math.abs(m.position.z - DIMS.tableCenterZ) < 0.02 &&
        m.position.y > DIMS.tableTopY + 0.01);
      // HUD (tiempo + ladrillos + vidas + banners)
      this.hudCv = arcadeCanvas(1024, 214);
      this.hudTex = new THREE.CanvasTexture(this.hudCv);
      this.hudTex.colorSpace = THREE.SRGBColorSpace;
      this.hudGroup = new THREE.Group();
      this.hudPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(2.4, 2.4 * 214 / 1024),
        new THREE.MeshBasicMaterial({
          map: this.hudTex, transparent: true, depthWrite: false,
        }),
      );
      this.hudGroup.add(this.hudPlane);
      this.hudGroup.position.set(0, 2.56, C.z + 0.05);
      this.hudGroup.visible = false;
      g.rig.add(this.hudGroup);   // v2.44: anclado al rig (espacio de la mesa)
    } else {
      // reconstrucción: vaciar los grupos de la variante anterior
      this._clearGroup(this.fieldGroup);
      this._clearGroup(this.wallGroup);
      // el tamaño de los ladrillos cambia entre variantes
      if (this.brickGeo) this.brickGeo.dispose();
      this.brickGeo = new THREE.BoxGeometry(C.bw, C.bh, C.depth);
    }
    this._builtV = this.variant;
    this.bricks = [];

    /* ---- PERÍMETRO = BORDES DE LA MESA (fieldGroup) ------------------ */
    // pared del FONDO (tras el muro): nace en el suelo; sostiene el PÓSTER
    // de la variante (v2.45: AMBAS variantes tienen arte — en la 1 el
    // superpoder, en la 2 la imagen del VIENTO del jugador).
    const wallH = DIMS.tableTopY + C.backY;
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(2 * C.sideX + 0.12, wallH, 0.08), this.darkMat);
    backWall.position.set(0, wallH / 2, C.sideZ1 - 0.04);
    this.fieldGroup.add(backWall);
    {
      // v2.45 · PÓSTER tras el muro: DETRÁS de los ladrillos y DELANTE de la
      // pared del fondo (a 1 mm), como en el ARKANOID 1 — el arte cambia
      // según la variante (superpoder · viento.png).
      const pw = W - 0.05, ph = pw * 768 / 1365;
      this.posterMat = new THREE.MeshBasicMaterial({
        color: 0x23282e, depthWrite: false,
      });
      this.poster = new THREE.Mesh(
        new THREE.PlaneGeometry(pw, ph), this.posterMat);
      this.poster.position.set(0, C.baseY + H / 2, C.sideZ1 + 0.001);
      this.fieldGroup.add(this.poster);
      // arte embebido (data URL) — llega asíncrono
      const purl = (this.variant === 1) ?
        (typeof window !== 'undefined' && window.__PP_GUNPOSTER_URL) :
        (typeof window !== 'undefined' && window.__PP_WIND_URL);
      if (purl) {
        const pimg = new Image();
        pimg.onload = () => {
          const ptex = new THREE.Texture();
          ptex.colorSpace = THREE.SRGBColorSpace;
          ptex.image = pimg;
          ptex.needsUpdate = true;
          this.posterMat.map = ptex;
          this.posterMat.color.setHex(0xffffff);
          this.posterMat.needsUpdate = true;
        };
        pimg.src = purl;
      }
    }
    // v2.46 · LADRILLO NEGRO del TIEMPO EXTRA: malla negra + reloj.png
    // superpuesto (aparece en huecos de ladrillos destruidos en los últimos
    // 30 s del ARKANOID 2) y plano extra.png "+1 MIN" que flota al reventar.
    this.blackMat = this.blackMat || new THREE.MeshStandardMaterial({
      color: 0x0b0b0e, roughness: 0.35, metalness: 0.5,
      emissive: 0x16181d, emissiveIntensity: 0.5,
    });
    this.timeMesh = new THREE.Mesh(this.brickGeo, this.blackMat);
    this.timeMesh.castShadow = true;
    this.timeMesh.visible = false;
    this.wallGroup.add(this.timeMesh);
    this.timeClockMat = this.timeClockMat || new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.FrontSide,
    });
    this.timeClock = new THREE.Mesh(
      new THREE.PlaneGeometry(C.bw * 0.62, C.bw * 0.62), this.timeClockMat);
    this.timeClock.visible = false;
    this.timeClock.renderOrder = 6;
    this.wallGroup.add(this.timeClock);
    if (!this._relojLoading) {
      this._relojLoading = true;
      const rurl = (typeof window !== 'undefined' && window.__PP_RELOJ_URL);
      if (rurl) {
        const rimg = new Image();
        rimg.onload = () => {
          const rt = new THREE.Texture();
          rt.colorSpace = THREE.SRGBColorSpace;
          rt.image = rimg;
          rt.needsUpdate = true;
          this.timeClockMat.map = rt;
          this.timeClockMat.needsUpdate = true;
        };
        rimg.src = rurl;
      }
    }
    this.extraGeo = this.extraGeo || new THREE.PlaneGeometry(0.34, 0.34);
    this.extraMat = this.extraMat || new THREE.MeshBasicMaterial({
      transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide,
    });
    this.extraPlane = new THREE.Mesh(this.extraGeo, this.extraMat);
    this.extraPlane.visible = false;
    this.extraPlane.renderOrder = 8;
    this.wallGroup.add(this.extraPlane);
    if (!this._extraLoading) {
      this._extraLoading = true;
      const eurl = (typeof window !== 'undefined' && window.__PP_EXTRA_URL);
      if (eurl) {
        const eimg = new Image();
        eimg.onload = () => {
          const et = new THREE.Texture();
          et.colorSpace = THREE.SRGBColorSpace;
          et.image = eimg;
          et.needsUpdate = true;
          this.extraMat.map = et;
          this.extraMat.needsUpdate = true;
        };
        eimg.src = eurl;
      }
    }
    // 2 PAREDES LATERALES de cristal (marco ámbar + rodapié + remate),
    // EN EL BORDE de la mesa (4 mm fuera para no z-fight con el canto).
    // v2.44: longitud C.sideZ0 - C.sideZ1 — con la extensión hacia el
    // jugador (30 cm en la variante 1, 60 cm en la 2) ya NO hay huecos.
    const sl = C.sideZ0 - C.sideZ1;
    const sz = (C.sideZ0 + C.sideZ1) / 2;
    const glassH = DIMS.tableTopY + C.glassY;
    // v2.46 · MARCOS FINOS (2,2 cm) y centrados FUERA del plano del vidrio:
    // antes (5 cm, centrados EN la pared) tapaban las esquinas de los
    // ladrillos de los extremos del muro.
    for (const sx of [-C.sideX - 0.013, C.sideX + 0.013]) {
      const pane = new THREE.Mesh(new THREE.PlaneGeometry(sl, glassH), this.glassMat);
      pane.rotation.y = Math.PI / 2;
      pane.position.set(sx, glassH / 2, sz);
      this.fieldGroup.add(pane);
      const foot = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, 0.035, sl), this.darkMat);
      foot.position.set(sx, 0.0175, sz);
      this.fieldGroup.add(foot);
      const cap = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, 0.022, sl), this.railMat);
      cap.position.set(sx, glassH - 0.011, sz);
      this.fieldGroup.add(cap);
      for (const pz of [C.sideZ0 - 0.011, C.sideZ1 + 0.011]) {
        const post = new THREE.Mesh(
          new THREE.BoxGeometry(0.022, glassH, 0.022), this.railMat);
        post.position.set(sx, glassH / 2, pz);
        this.fieldGroup.add(post);
      }
    }

    /* ---- MURO DE LADRILLOS (wallGroup): SOBRE la mesa, ENRASADO ------ */
    // v2.46 · estructura FINA: pilares de 2,2 cm PEGADOS AL CANTO EXTERIOR
    // (antes 6 cm centrados dentro del muro = tapaban los ladrillos de los
    // extremos) y listón superior fino sin voladizo.
    const stand = new THREE.Mesh(
      new THREE.BoxGeometry(W, 0.03, C.depth + 0.02), this.darkMat);
    stand.position.set(0, C.baseY - 0.016, C.z);
    this.wallGroup.add(stand);
    const mkRail = (w, h, x, y, d) => {
      const r = new THREE.Mesh(new THREE.BoxGeometry(w, h, d || 0.05), this.railMat);
      r.position.set(x, y, C.z);
      this.wallGroup.add(r);
    };
    mkRail(W, 0.016, 0, C.baseY + H + 0.008, 0.04);
    for (const px of [-W / 2 - 0.011, W / 2 + 0.011]) {
      const pil = new THREE.Mesh(
        new THREE.BoxGeometry(0.022, H + 0.02, C.depth), this.railMat);
      pil.position.set(px, C.baseY + (H + 0.02) / 2, C.z);
      this.wallGroup.add(pil);
    }
    // LADRILLOS — variante 1: todos ROJOS · variante 2: rojos + azules
    for (let r = 0; r < C.rows; r++) {
      for (let c = 0; c < C.cols; c++) {
        const blue = this.variant === 2 &&
          ((r * 7 + c * 5 + 3) % 10) < Math.round(C.blueStart * 10);
        const m = new THREE.Mesh(this.brickGeo,
          blue ? this.blueMats[(r * 3 + c) % 3] : this.redMats[(r * 3 + c) % 3]);
        const x = -W / 2 + C.bw / 2 + c * (C.bw + C.gap);
        const y = C.baseY + C.bh / 2 + r * (C.bh + C.gap);
        m.position.set(x, y, C.z);
        m.castShadow = true;
        this.wallGroup.add(m);
        this.bricks.push({
          mesh: m, home: m.position.clone(), alive: true,
          state: blue ? 'blue' : 'red',   // v2.44: color lógico del ladrillo
          matIdx: (r * 3 + c) % 3,        // v2.44: tono dentro de su paleta
          min: new THREE.Vector3(x - C.bw / 2, y - C.bh / 2, C.z - C.depth / 2),
          max: new THREE.Vector3(x + C.bw / 2, y + C.bh / 2, C.z + C.depth / 2),
        });
      }
    }
    this.wallGroup.visible = false;
    this.fieldGroup.visible = false;
    this._hudDirty = true;
  }

  /** Vacía un grupo (v2.44: reconstrucción entre variantes). */
  _clearGroup(gr) {
    if (!gr) return;
    for (let i = gr.children.length - 1; i >= 0; i--) {
      const ch = gr.children[i];
      const isPool = this._debris.some((d) => d.mesh === ch) ||
        this._flashes.some((f) => f.mesh === ch);
      if (isPool) continue;   // los pools sobreviven a la reconstrucción
      gr.remove(ch);
    }
  }

  /* ---------------- ciclo de vida ---------------- */

  start() {
    const g = this.game;
    // v2.44: la ETAPA del camino elige la variante (3 = ARKANOID 2)
    this.variant = (this.ctrl && this.ctrl.stage >= 3) ? 2 : 1;
    this.C = this.variant === 2 ? ARK2_CFG : ARK_CFG;
    this.build();
    if (this.active) return;
    this.active = true;
    this.phase = 'intro';
    this.phaseT = 2.6;
    this.time = this.C.time;
    this._lastSec = Math.ceil(this.time) + 1;
    this._warn60 = false;
    this.lives = this.C.lives;
    // v2.44: estado de la conversión temporal y del abanico
    this._convT = 0;
    this._fanSamp.length = 0;
    this._fanT = 0; this._fanCd = 0; this._fanKick = 0; this._fanBlowT = 0;
    // v2.46: el ladrillo negro del tiempo vuelve a estar disponible en cada
    // intento (UNO por prueba); fuera restos del intento anterior
    this._timeBrick = null;
    this._timeUsed = false;
    this._time30 = false;
    this._extraFx = null;
    if (this.timeMesh) this.timeMesh.visible = false;
    if (this.timeClock) this.timeClock.visible = false;
    if (this.extraPlane) this.extraPlane.visible = false;
    this.bricksLeft = this.bricks.length;
    for (const b of this.bricks) {
      b.alive = true;
      b.mesh.visible = true;
      b.mesh.scale.setScalar(1);
      b.mesh.rotation.set(0, 0, 0);
      b.mesh.position.copy(b.home);
      // v2.44: el material refleja el color lógico (rojo/azul al reiniciar)
      b.mesh.material = b.state === 'blue' ? this.blueMats[b.matIdx] : this.redMats[b.matIdx];
    }
    this._dying.length = 0;
    for (const d of this._debris) d.mesh.visible = false;
    for (const f of this._flashes) { f.t = 0; f.mesh.visible = false; }
    for (const w of this._wind) { w.life = 0; w.mesh.visible = false; }
    this._banner = this.variant === 2
      ? { title: T('ark2_title'), sub: T('ark2_intro'), col: '#ffd257' }
      : { title: T('ark_title'), sub: T('ark_intro'), col: '#ffd257' };
    this._msg = '';
    this._msgT = 0;
    this._hudDirty = true;
    // v2.41: la MESA SIGUE en escena (¡el muro se apoya en ella!) pero SIN
    // RED: esta variante se juega sin red. Marcador y pala IA fuera.
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.ballMesh.scale.setScalar(1);        // v2.42: bola NORMAL (ni x2 ni roja)
    g.ball.ignoreNet = true;              // v2.42: la mesa va SIN red (ni físicas)
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    this._crossed = false;
    this._stuckT = 0;
    this._tokCd = 0;
    const a = this.ctrl;
    if (a.rivalMesh) a.rivalMesh.visible = false;  // v3.2.0: el ASTRO no juega el muro
    if (a.cartel) a.cartel.visible = false;
    if (a.powerSign) a.powerSign.visible = false;
    g.rules.state = 'arkanoid';           // el árbitro queda en pausa
    g.rules.message = T('ark_title');
    this.wallGroup.visible = true;
    this.fieldGroup.visible = true;
    this.hudGroup.visible = true;
    // jingle de arranque
    g.audio.playOsc(523, 523, 0.11, 'square', 0.11, 0);
    window.setTimeout(() => g.audio.playOsc(659, 659, 0.11, 'square', 0.11, 0), 130);
    window.setTimeout(() => g.audio.playOsc(784, 784, 0.2, 'square', 0.12, 0), 260);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  /** Reanudar al volver a VR: el árbitro vuelve a pausa y SAQUE de nuevo
   *  SIN coste de vida (el tiempo y los ladrillos quedan como estaban). */
  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    if (this.phase === 'play' || this.phase === 'intro') {
      this.phase = 'serve';
      this._serveT = 0;
      this._msg = T('ark_serve_hint');
    }
    this._hudDirty = true;
  }

  /** Devuelve la escena a la normalidad (mesa CON red, marcador, rival). */
  stop() {
    this.active = false;
    this.phase = 'idle';
    if (!this.inited) return;
    const g = this.game;
    this.wallGroup.visible = false;
    this.fieldGroup.visible = false;
    this.hudGroup.visible = false;
    for (const b of this.bricks) {
      b.alive = true;
      b.mesh.visible = true;
      b.mesh.scale.setScalar(1);
      b.mesh.rotation.set(0, 0, 0);
      b.mesh.position.copy(b.home);
    }
    this._dying.length = 0;
    for (const d of this._debris) d.mesh.visible = false;
    for (const f of this._flashes) { f.t = 0; f.mesh.visible = false; }
    // v2.46: fuera el ladrillo negro del tiempo y el "+1 MIN"
    this._timeBrick = null;
    this._extraFx = null;
    if (this.timeMesh) this.timeMesh.visible = false;
    if (this.timeClock) this.timeClock.visible = false;
    if (this.extraPlane) this.extraPlane.visible = false;
    // v2.41: la red vuelve a la mesa
    for (const m of this._netParts || []) m.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ballMesh.scale.setScalar(1);
    g.ball.ignoreNet = false;             // v2.42: la red vuelve a colisionar
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
  }

  /* ---------------- bucle de la prueba ---------------- */

  step(dt) {
    if (!this.active || !this.inited) return;
    const g = this.game;
    const ball = g.ball;
    if (this.phase === 'intro') {
      this.phaseT -= dt;
      this._holdBallInHand();       // v2.41: la bola espera en tu mano libre
      if (this.phaseT <= 0) this._enterServe();
    } else if (this.phase === 'serve') {
      // v2.41: SAQUE de partida normal — bola en la mano libre, gatillo
      // para lanzarla. Sin acción, saque automático (nunca se atasca).
      this._serveT += dt;
      this._holdBallInHand();
      if (!this._msg) {
        this._msg = T('ark_serve_hint');
        this._hudDirty = true;
      }
      if (this._serveT > this.C.serveAutoT) {
        this._msg = T('ark_autoserve');
        this.serveTrigger(true);
      }
    } else if (this.phase === 'play') {
      this._tokCd = Math.max(0, this._tokCd - dt);
      this.time -= dt;
      if (this.time <= 0) {
        this.time = 0;
        this._hudDirty = true;
        this._finish(false, 'time');
        return;
      }
      const sec = Math.ceil(this.time);
      if (sec <= 60 && !this._warn60) {
        // AVISO: se baja de 1 minuto (doble pitido)
        this._warn60 = true;
        this._hudDirty = true;
        g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0);
        window.setTimeout(() => g.audio.playOsc(880, 880, 0.12, 'square', 0.16, 0), 190);
      }
      if (sec !== this._lastSec) {
        this._lastSec = sec;
        this._hudDirty = true;
        if (this._warn60 && sec > 10) {
          g.audio.playOsc(760, 760, 0.045, 'sine', 0.07, 0);
        }
        if (sec <= 10 && sec >= 1) {
          // ALARMA: últimos 10 segundos
          g.audio.playOsc(980, 620, 0.16, 'sawtooth', 0.2, 0);
          if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 60);
        }
      }
      // v2.46 · APREMIO: al entrar en los ÚLTIMOS 30 s suena un aviso de
      // urgencia (tres dobles-bips) y se activa el ladrillo negro del
      // TIEMPO EXTRA. Una sola vez: con el +1 min cogido, no repite.
      if (this.variant === 2 && sec <= 30 && !this._time30) {
        this._time30 = true;
        this._hudDirty = true;
        for (let k = 0; k < 3; k++) {
          window.setTimeout(() => {
            g.audio.playOsc(640, 980, 0.09, 'square', 0.13, 0);
          }, k * 230);
          window.setTimeout(() => {
            g.audio.playOsc(640, 980, 0.09, 'square', 0.13, 0);
          }, k * 230 + 105);
        }
      }
      // v2.44 · CONVERSIÓN TEMPORAL ROJO->AZUL (sólo variante 2): cada pocos
      // segundos UN ladrillo ROJO vivo pasa a AZUL. Los AZULES NUNCA se
      // eligen (el bug del ladrillo negro: azul elegido = se rompía la
      // lógica); sólo los ROJOS son candidatos.
      if (this.variant === 2 && this.C.convertEvery) {
        this._convT += dt;
        if (this._convT >= this.C.convertEvery) {
          this._convT -= this.C.convertEvery;
          if (this._convT < 0) this._convT = 0;
          this._convertRandomRed();
        }
      }
      // v2.46 · LADRILLO NEGRO del tiempo extra (aparición y saltos)
      this._timeUpdate(dt);
      // v2.44 · ABANICO: corriente de aire para empujar la bola al muro
      this._fanUpdate(dt);
      this._physics(dt);
      if (!this.active) return;             // pudo terminar dentro
      if (this.bricksLeft <= 0) {
        this._finish(true);
        return;
      }
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      if (this.phaseT <= 0) {
        this._afterResult();
        return;
      }
    }
    this._anims(dt);
    if (this._msgT > 0) {
      this._msgT -= dt;
      if (this._msgT <= 0) { this._msg = ''; this._hudDirty = true; }
    }
    if (this._hudDirty) this._hud();
  }

  /* ---------------- saque (v2.41: como en partida normal) ---------------- */

  /** Fallback del punto de saque (sin mano activa): igual que el del
   *  juego normal (bola sobre la línea de fondo de tu campo). */
  _serveSpot() {
    return this._spot.set(0.3, 1.05,
      DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4);
  }

  /** La bola "apoyada" en la mano libre (igual que el saque normal). */
  _holdBallInHand() {
    const g = this.game;
    const bh = g.controllerPaddles && g.controllerPaddles[g.ballHand];
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    if (bh && bh.active && bh.pos) {
      g.ball.pos.copy(bh.pos);
      g.ball.pos.y += 0.08;                     // BALL_HAND_LIFT
    } else {
      g.ball.pos.copy(this._serveSpot());
    }
  }

  _enterServe() {
    this.phase = 'serve';
    this._serveT = 0;
    this._msg = T('ark_serve_hint');
    this._hudDirty = true;
  }

  /** v2.41 · GATILLO = lanzamiento asistido (mismo gesto que el saque
   *  asistido de una partida normal): la bola sale de la mano libre y la
   *  golpeas con la pala; la física de la prueba la mantiene viva hasta
   *  que la devuelvas al muro. force = saque automático (ignora la mano). */
  serveTrigger(force) {
    if (!this.active || this.phase !== 'serve') return;
    const g = this.game;
    const hand = g.controllerPaddles && g.controllerPaddles[g.ballHand];
    const v = (!force && hand && hand.active && hand.vel)
      ? this._tmpA.copy(hand.vel)
      : this._tmpA.set(0, 0, 0);
    if (v.y < DIMS.serveAssistVy) {
      v.y = DIMS.serveAssistVy;
      v.x *= 0.4;
      v.z *= 0.4;
    }
    // v2.42: asistencia de alcance como en el SAQUE NORMAL (bola recién
    // lanzada); se retira en el primer golpeo de pala
    const ps2 = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (ps2) ps2.extraReach = DIMS.serveExtraReach;
    this.phase = 'play';
    this._lastSec = Math.ceil(this.time) + 1;
    this._crossed = false;
    this._msg = '';
    this._hudDirty = true;
    g.ball.vel.copy(v);
    g.ball.spin.set(0, 0, 0);
    g.audio.serve();
    g.rules.message = T('hint_hit');
    if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.45);
  }

  /* ------------- física (v2.42: la de una PARTIDA NORMAL) ------------- */

  /** FÍSICA DE PARTIDA NORMAL: MISMA integración (gravedad real, arrastre
   *  aerodinámico, Magnus), MISMO golpeo de pala (colocas la bola igual que
   *  en un rally: la pala manda) y MISMA mesa. Los eventos van al array del
   *  juego, así que processEvents() suena solo (pala, mesa, suelo) y el
   *  árbitro los ignora (estado 'arkanoid'). Lo ÚNICO añadido son las
   *  colisiones del recinto, por SUBPASO (this._extra): ladrillos que se
   *  rompen, 3 paredes perimetrales y bote MÍNIMO de mesa. */
  _physics(dt) {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (ps && ps.active) ? [ps] : [];
    stepPhysics(dt, g.ball, pads, g.events, this._extra);
    // el alcance extra del SAQUE se retira en el primer golpeo de pala
    if (ps && ps.extraReach) {
      for (const e of g.events) {
        if (e.type === 'paddle') { ps.extraReach = 0; break; }
      }
    }
    // marcador de cruce (para el coste de vida justo)
    if (!this._crossed && g.ball.pos.z < this.C.sideZ0 - 0.05) {
      this._crossed = true;
    }
    this._checkLost(dt);
  }

  /** Bola perdida: al SUELO o por detrás del jugador (SOLO si cruzó al
   *  campo rival en este intento) o ATASCADA (bola casi parada en zona
   *  rival — p. ej. sobre el muro — o bajo la mesa). Sin cruce previo no
   *  hay coste: saque nuevo sin perder vida (toss fallado, p. ej.). */
  _checkLost(dt) {
    const g = this.game;
    const p = g.ball.pos, v = g.ball.vel;
    let lost = false;
    for (const e of g.events) {
      if (e.type === 'floor') { lost = true; break; }
    }
    if (!lost) {
      const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
      const lostZ = Math.min(2.05, (ps && ps.active && ps.pos)
        ? THREE.MathUtils.clamp(ps.pos.z, -0.5, 1.2) + 0.8 : 1.4);
      if (this._crossed && p.z > lostZ && v.z > 0) lost = true;
    }
    if (!lost && v.length() < 0.6 &&
        (p.z < this.C.sideZ0 || p.y < DIMS.tableTopY - 0.06)) {
      this._stuckT += dt;
      if (this._stuckT > 1.5) lost = true;
    } else {
      this._stuckT = 0;
    }
    if (!lost) return;
    if (this._crossed) this._lifeLost();
    else { this._crossed = false; this._enterServe(); }
  }

  /** v2.42 · COLISIONES ARKANOID (por SUBPASO de la física normal):
   *  1) perímetro EN LOS BORDES DE LA MESA — 2 cristales laterales + pared
   *     del fondo (donde brilla el póster del superpoder): reflexión física
   *     con pequeña pérdida;  2) la MESA OTORGA FUERZA MÍNIMA de bote (la
   *  bola nunca queda muerta sobre la superficie);  3) LADRILLOS: esfera vs
   *  AABB con reflexión ESPECULAR (físicamente correcta: un golpe en la cara
   *  frontal vuelve hacia el jugador, como devolvería cualquier superficie
   *  rígida) + destrucción con efecto. */
  _extraCollide(ball) {
    const p = ball.pos, v = ball.vel;
    const r = DIMS.ballRadius;           // bola NORMAL de 40 mm
    // v2.46 · SIEMPRE la config de la VARIANTE activa: antes leía ARK_CFG
    // fijo y en el ARKANOID 2 la zona ampliada de los cristales (red +80 cm)
    // se veía pero NO colisionaba más allá de red +30 cm.
    const C = this.C;
    if (p.z < C.sideZ0) {
      // --- laterales: EXACTAMENTE en los bordes de la mesa
      if (p.x < -C.sideX + r) {
        p.x = -C.sideX + r;
        if (v.x < 0) { v.x = -v.x * C.wallRest; this._wallTok(p.x); }
      } else if (p.x > C.sideX - r) {
        p.x = C.sideX - r;
        if (v.x > 0) { v.x = -v.x * C.wallRest; this._wallTok(p.x); }
      }
      // --- pared del FONDO (tras el muro: el póster del superpoder)
      if (p.z < C.sideZ1 + 0.032) {
        p.z = C.sideZ1 + 0.032;
        if (v.z < 0) { v.z = -v.z * C.wallRest; this._wallTok(0); }
      }
    }
    // --- MESA con FUERZA MÍNIMA: tras el bote normal de collideTable, si
    // la subida no alcanzaría apexMin se OTORGA la energía que falte
    if (v.y >= 0 && p.y <= DIMS.tableTopY + r + 0.004 &&
        Math.abs(p.x) <= DIMS.tableHalfWidth &&
        Math.abs(p.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength) {
      const need = Math.sqrt(2 * Math.abs(DIMS.gravity) * C.apexMin);
      if (v.y < need) v.y = need;
    }
    // --- LADRILLOS: esfera vs AABB — reflexión especular + rotura
    const r2 = (r + 0.002) * (r + 0.002);
    for (const b of this.bricks) {
      if (!b.alive) continue;
      if (p.z - r > b.max.z || p.z + r < b.min.z) continue;
      if (p.x - r > b.max.x || p.x + r < b.min.x) continue;
      if (p.y - r > b.max.y || p.y + r < b.min.y) continue;
      const cx = THREE.MathUtils.clamp(p.x, b.min.x, b.max.x);
      const cy = THREE.MathUtils.clamp(p.y, b.min.y, b.max.y);
      const cz = THREE.MathUtils.clamp(p.z, b.min.z, b.max.z);
      let nx = p.x - cx, ny = p.y - cy, nz = p.z - cz;
      const d2 = nx * nx + ny * ny + nz * nz;
      if (d2 > r2) continue;
      if (d2 > 1e-9) {
        const d = Math.sqrt(d2);
        nx /= d; ny /= d; nz /= d;
        p.x = cx + nx * (r + 0.003);
        p.y = cy + ny * (r + 0.003);
        p.z = cz + nz * (r + 0.003);
      } else {
        // centro dentro del ladrillo: eje de MÍNIMA penetración
        const dxs = Math.min(p.x - b.min.x, b.max.x - p.x);
        const dys = Math.min(p.y - b.min.y, b.max.y - p.y);
        const dzs = Math.min(p.z - b.min.z, b.max.z - p.z);
        nx = 0; ny = 0; nz = 0;
        if (dzs <= dxs && dzs <= dys) {
          nz = (p.z - (b.min.z + b.max.z) / 2) >= 0 ? 1 : -1;
          p.z = nz > 0 ? b.max.z + r + 0.003 : b.min.z - r - 0.003;
        } else if (dxs <= dys) {
          nx = (p.x - (b.min.x + b.max.x) / 2) >= 0 ? 1 : -1;
          p.x = nx > 0 ? b.max.x + r + 0.003 : b.min.x - r - 0.003;
        } else {
          ny = (p.y - (b.min.y + b.max.y) / 2) >= 0 ? 1 : -1;
          p.y = ny > 0 ? b.max.y + r + 0.003 : b.min.y - r - 0.003;
        }
      }
      const vn = v.x * nx + v.y * ny + v.z * nz;
      if (vn < 0) {
        // reflexión especular y pérdida SOLO de la componente normal
        v.x -= 2 * vn * nx;
        v.y -= 2 * vn * ny;
        v.z -= 2 * vn * nz;
        const vno = v.x * nx + v.y * ny + v.z * nz;
        v.x -= nx * vno * (1 - C.brickRest);
        v.y -= ny * vno * (1 - C.brickRest);
        v.z -= nz * vno * (1 - C.brickRest);
      }
      // v2.44 · LÓGICA POR COLOR: la PALA (bola) sólo rompe los ROJOS; los
      // AZULES REBOTAN (metálico: «clink») — sólo el LÁSER los destruye
      // (explosión y quedan ROJOS, no desaparecen).
      if (b.state === 'blue') {
        this._brickClink(b);
      } else {
        this._breakBrick(b);
      }
      break;   // un ladrillo por subpaso
    }
    // v2.46 · LADRILLO NEGRO del tiempo extra: la bola también lo revienta
    // (misma reflexión especular que los ladrillos + recompensa de +1 min)
    if (this._timeBrick) {
      const tb = this._timeBrick;
      if (p.z - r <= tb.max.z && p.z + r >= tb.min.z &&
          p.x - r <= tb.max.x && p.x + r >= tb.min.x &&
          p.y - r <= tb.max.y && p.y + r >= tb.min.y) {
        const cx = THREE.MathUtils.clamp(p.x, tb.min.x, tb.max.x);
        const cy = THREE.MathUtils.clamp(p.y, tb.min.y, tb.max.y);
        const cz = THREE.MathUtils.clamp(p.z, tb.min.z, tb.max.z);
        let nx = p.x - cx, ny = p.y - cy, nz = p.z - cz;
        const d2 = nx * nx + ny * ny + nz * nz;
        if (d2 <= r2) {
          if (d2 > 1e-9) {
            const d = Math.sqrt(d2);
            nx /= d; ny /= d; nz /= d;
            p.x = cx + nx * (r + 0.003);
            p.y = cy + ny * (r + 0.003);
            p.z = cz + nz * (r + 0.003);
          } else {
            nz = 1;
            p.z = tb.max.z + r + 0.003;
          }
          const vn = v.x * nx + v.y * ny + v.z * nz;
          if (vn < 0) {
            v.x -= 2 * vn * nx;
            v.y -= 2 * vn * ny;
            v.z -= 2 * vn * nz;
            const vno = v.x * nx + v.y * ny + v.z * nz;
            v.x -= nx * vno * (1 - C.brickRest);
            v.y -= ny * vno * (1 - C.brickRest);
            v.z -= nz * vno * (1 - C.brickRest);
          }
          this._breakTimeBrick();
        }
      }
    }
  }

  /** Golpecito sonoro de las paredes del perímetro (v2.41, con anti-spam). */
  _wallTok(x) {
    if (this._tokCd > 0) return;
    this._tokCd = 0.07;
    const g = this.game;
    g.audio.playOsc(320, 210, 0.06, 'triangle', 0.1,
      THREE.MathUtils.clamp(x / 2, -1, 1));
  }

  /** v2.44 · «clink» metálico de la bola contra un ladrillo AZUL (no rompe). */
  _brickClink(b) {
    if (this._tokCd > 0) return;
    this._tokCd = 0.09;
    const g = this.game;
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(1250, 900, 0.05, 'square', 0.09, pan);
    this._flash(b.mesh.position);
  }

  /** v2.44 · LÁSER impacta en un ladrillo: aplica SU lógica.
   *  AZUL  -> destruido por el láser: EXPLOTA y queda ROJO (no desaparece).
   *  ROJO  -> inmune al láser (sólo la pala lo rompe): chispa y «tick». */
  laserHit(b) {
    if (!b || !b.alive) return false;
    if (b.state === 'blue') {
      this._laserConvert(b);
      return true;
    }
    this._laserSpark(b);
    return false;
  }

  /** v2.44 · el láser CONVIERTE el azul en rojo: explosión + cambio de color. */
  _laserConvert(b) {
    const g = this.game;
    b.state = 'red';
    b.mesh.material = this.redMats[b.matIdx];
    this._flash(b.mesh.position);
    // ráfaga de escombros azules (visual: la explosión del láser)
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.45 + Math.random() * 0.2;
      d.mesh.visible = true;
      d.mesh.material = this.blueMats[b.matIdx];
      d.mesh.position.copy(b.mesh.position);
      d.mesh.position.x += (Math.random() - 0.5) * 0.2;
      d.mesh.position.y += (Math.random() - 0.5) * 0.12;
      d.vel.set((Math.random() - 0.5) * 2.0, Math.random() * 1.4,
        0.8 + Math.random() * 1.4);
      if (++spawned >= 5) break;
    }
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playNoise(0.12, 900, 0.9, 0.16, pan);
    g.audio.playOsc(880, 220, 0.16, 'sawtooth', 0.14, pan);
    if (g.renderer.xr.isPresenting) g.haptic(g.ballHand, 0.35, 55);
    this._hudDirty = true;
  }

  /** v2.44 · chispa del láser sobre un ROJO (no hace nada: es inmune). */
  _laserSpark(b) {
    const g = this.game;
    this._flash(b.mesh.position);
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(1600, 1200, 0.04, 'square', 0.07, pan);
  }

  /** v2.44 · conversión temporal: UN ladrillo ROJO vivo pasa a AZUL.
   *  Sólo se eligen ROJOS (los azules ya lo están: nunca «negros»). */
  _convertRandomRed() {
    if (this.variant !== 2) return;
    const cands = this.bricks.filter((b) => b.alive && b.state === 'red');
    if (!cands.length) return;
    const b = cands[(Math.random() * cands.length) | 0];
    b.state = 'blue';
    b.mesh.material = this.blueMats[b.matIdx];
    this._flash(b.mesh.position);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(520, 880, 0.14, 'sine', 0.09, pan);
    this._hudDirty = true;
  }

  /* ---------------------------------------------------------------------
   * v2.46 · LADRILLO NEGRO del TIEMPO EXTRA (sólo ARKANOID 2): cuando el
   * contador baja de 30 s (con sonido de APREMIO) aparece en un hueco de
   * ladrillo ya destruido con un reloj superpuesto, se queda 2 s y SALTA a
   * otro hueco libre distinto. La bola o el láser lo revientan: escombros
   * NEGROS, +1 MINUTO de tiempo y el cartel extra.png flotando. UNO solo
   * por prueba: cogido éste, nunca vuelve a aparecer.
   * ------------------------------------------------------------------- */
  _timeUpdate(dt) {
    if (this.variant !== 2) return;
    if (!this._timeUsed && this.time <= 30 && !this._timeBrick) {
      this._timeSpawn();
    }
    if (!this._timeBrick) return;
    this._timeBrick.t += dt;
    if (this._timeBrick.t >= 2) this._timeJump();
  }

  _freeSlots() {
    return this.bricks.filter((b) => !b.alive);
  }

  _timeSpawn() {
    // v2.46: blindaje — si el extra ya se cogió (o ya está en escena),
    // NUNCA vuelve a aparecer aunque se llame directamente
    if (this._timeUsed || this._timeBrick) return;
    const free = this._freeSlots();
    if (!free.length) return;          // sin huecos destruidos: no aparece
    this._timePlace(free[(Math.random() * free.length) | 0]);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.timeMesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(980, 620, 0.12, 'square', 0.11, pan);
  }

  _timePlace(b) {
    this._timeBrick = { slot: b, t: 0, min: b.min, max: b.max };
    this.timeMesh.visible = true;
    this.timeMesh.scale.setScalar(1);
    this.timeMesh.rotation.set(0, 0, 0);
    this.timeMesh.position.copy(b.home);
    this.timeClock.visible = true;     // reloj ANCLADO al ladrillo especial
    this.timeClock.position.copy(b.home);
    this.timeClock.position.z += this.C.depth / 2 + 0.003;
  }

  _timeJump() {
    const cur = this._timeBrick.slot;
    const free = this._freeSlots().filter((b) => b !== cur);
    if (!free.length) { this._timeBrick.t = 0; return; }  // sólo un hueco
    this._flash(cur.home);             // destello en el hueco que abandona
    this._timePlace(free[(Math.random() * free.length) | 0]);
    const g = this.game;
    const pan = THREE.MathUtils.clamp(this.timeMesh.position.x / 2.5, -1, 1);
    g.audio.playOsc(760, 1150, 0.07, 'sine', 0.08, pan);
  }

  /** La bola o el láser revientan el ladrillo negro: escombros NEGROS,
   *  +1 MINUTO y el plano extra.png "+1 MIN" que sube y se desvanece. */
  _breakTimeBrick() {
    if (!this._timeBrick) return;
    const g = this.game;
    const pos = this.timeMesh.position.clone();
    this._timeBrick = null;
    this._timeUsed = true;             // sólo UN tiempo extra por prueba
    this.timeMesh.visible = false;
    this.timeClock.visible = false;
    this.time += 60;                   // +1 MINUTO al contador
    this._hudDirty = true;
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.55 + Math.random() * 0.25;
      d.mesh.visible = true;
      d.mesh.material = this.blackMat; // trocitos NEGROS
      d.mesh.position.copy(pos);
      d.mesh.position.x += (Math.random() - 0.5) * 0.2;
      d.mesh.position.y += (Math.random() - 0.5) * 0.12;
      d.vel.set((Math.random() - 0.5) * 2.2, Math.random() * 1.5,
        0.7 + Math.random() * 1.5);
      if (++spawned >= 6) break;
    }
    this._flash(pos);
    // "+1 MIN" un poco DELANTE del muro: sube despacio y se apaga en 2 s
    this._extraFx = { pos, t: 0 };
    this.extraPlane.visible = true;
    this.extraPlane.position.copy(pos);
    this.extraPlane.position.z += 0.09;
    this.extraPlane.material.opacity = 1;
    const pan = THREE.MathUtils.clamp(pos.x / 2.5, -1, 1);
    g.audio.playNoise(0.1, 1800, 1.0, 0.12, pan);
    g.audio.playOsc(520, 1040, 0.16, 'sine', 0.16, pan);
    window.setTimeout(() => g.audio.playOsc(780, 1560, 0.22, 'sine', 0.16, pan), 140);
    this._msg = T('ark_extra_min');
    this._msgT = 2.0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 70);
  }

  /* ---------------------------------------------------------------------
   * v2.44 · ABANICAR — anti-atasco divertido: si mueves la pala RÁPIDO de
   * derecha a izquierda (y viceversa) se genera una CORRIENTE DE AIRE que
   * empuja la bola hacia el muro como si la hubieras golpeado. Sirve para
   * alcanzar bolas botando lejos de la mesa (zona inaccesible).
   * · Detección: 2+ inversiones laterales fuertes (|vx| > 1,2 m/s) en 0,55 s.
   * · Efecto: aceleración sostenida hacia el muro + EMPUJÓN final tipo golpe.
   * · Feedback: partículas de viento pala->bola + sonido de soplido.
   * ------------------------------------------------------------------- */
  _fanUpdate(dt) {
    const g = this.game;
    this._fanCd = Math.max(0, this._fanCd - dt);
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const ball = g.ball;
    if (!ball || !ball.pos) return;

    // 1) muestrear la velocidad lateral de la pala (ventana de 0,55 s)
    const nowT = performance.now() / 1000;
    if (ps && ps.active && ps.vel) {
      this._fanSamp.push({ t: nowT, vx: ps.vel.x });
      while (this._fanSamp.length && nowT - this._fanSamp[0].t > 0.55) {
        this._fanSamp.shift();
      }
      if (this._fanCd <= 0 && this._fanT <= 0) {
        // contar INVERSIONES de dirección con impulso suficiente
        let flips = 0;
        let lastSign = 0;
        for (const s of this._fanSamp) {
          if (Math.abs(s.vx) < 1.2) continue;
          const sg = Math.sign(s.vx);
          if (lastSign && sg !== lastSign) flips++;
          lastSign = sg;
        }
        if (flips >= 2) {
          // ¡ABANICO! corriente de aire activa durante 1,2 s
          this._fanT = 1.2;
          this._fanCd = 3.2;
          this._fanKick = 0;
          this._fanBlowT = 0;
          if (!this._fanHintDone) {
            this._fanHintDone = true;
            this._msg = T('fan_hint');
            this._msgT = 2.2;
            this._hudDirty = true;
          }
        }
      }
    }

    // 2) mientras sopla el viento: acelerar la bola hacia el muro
    if (this._fanT > 0) {
      this._fanT -= dt;
      // sólo si la bola está en la zona alejada (no al alcance de la pala)
      const p = ball.pos;
      const padPos = (ps && ps.active && ps.pos) ? ps.pos : null;
      const far = !padPos || p.distanceTo(padPos) > 0.45;
      if (far && p.z < this.C.sideZ0 + 0.2) {
        this._tmpA.set(
          THREE.MathUtils.clamp(p.x, -this.C.sideX * 0.6, this.C.sideX * 0.6),
          DIMS.tableTopY + 0.35,
          this.C.sideZ1 + 0.4,
        ).sub(p);
        if (this._tmpA.lengthSq() > 1e-6) {
          this._tmpA.normalize();
          ball.vel.addScaledVector(this._tmpA, 2.6 * dt);   // corriente continua
          if (p.y < DIMS.tableTopY + 0.15) ball.vel.y += 1.4 * dt;
          // EMPUJÓN final tipo golpe (acumulado ~0,8 s de viento)
          this._fanKick += dt;
          if (this._fanKick >= 0.8) {
            this._fanT = 0;
            const sp = Math.max(3.4, ball.vel.length() * 1.15);
            ball.vel.copy(this._tmpA).multiplyScalar(sp);
            if (ball.vel.y < 1.4) ball.vel.y = 1.4;
            g.audio.playNoise(0.28, 700, 0.7, 0.2, 0);
            g.audio.playOsc(300, 140, 0.2, 'triangle', 0.1, 0);
          }
        }
      }
      // soplido en bucle corto mientras dura la corriente
      this._fanBlowT -= dt;
      if (this._fanBlowT <= 0) {
        this._fanBlowT = 0.16;
        g.audio.playNoise(0.15, 520, 0.6, 0.07, 0);
      }
      // 3) partículas de viento: nacen en la pala y vuelan hacia la bola
      if (ps && ps.active && ps.pos) {
        let spawned = 0;
        for (const w of this._wind) {
          if (w.life > 0) continue;
          w.life = 0.4 + Math.random() * 0.18;
          w.mesh.visible = true;
          w.mesh.position.copy(ps.pos);
          w.mesh.position.y += 0.05;
          this._tmpB.copy(ball.pos).sub(w.mesh.position);
          if (this._tmpB.lengthSq() > 1e-8) this._tmpB.normalize();
          else this._tmpB.set(0, 1, 0);   // v2.120: sin NaN si la bola está encima
          w.vel.copy(this._tmpB).multiplyScalar(2.4 + Math.random() * 1.4);
          w.vel.x += (Math.random() - 0.5) * 0.7;
          w.vel.y += (Math.random() - 0.5) * 0.5;
          w.vel.z += (Math.random() - 0.5) * 0.7;
          if (++spawned >= 2) break;
        }
      }
    }

    // 4) animación de las partículas (siempre)
    for (const w of this._wind) {
      if (w.life <= 0) continue;
      w.life -= dt;
      if (w.life <= 0) { w.mesh.visible = false; continue; }
      w.mesh.position.addScaledVector(w.vel, dt);
      const k = Math.min(1, w.life / 0.4);
      w.mesh.material.opacity = 0.75 * k;
      w.mesh.scale.setScalar(0.7 + (1 - k) * 1.6);
      w.mesh.quaternion.copy(g.camera ? g.camera.quaternion : new THREE.Quaternion());
    }
  }

  /** Flash de destrucción (v2.41): estallido aditivo en el ladrillo roto. */
  _flash(pos) {
    for (const f of this._flashes) {
      if (f.t > 0) continue;
      f.t = 0.0001;
      f.mesh.visible = true;
      f.mesh.position.copy(pos);
      f.mesh.scale.setScalar(0.5);
      return;
    }
  }

  _breakBrick(b) {
    const g = this.game;
    b.alive = false;
    this.bricksLeft--;
    this._dying.push({ mesh: b.mesh, t: 0, spin: (Math.random() - 0.5) * 3 });
    this._flash(b.mesh.position);            // v2.41: estallido de luz
    // escombros
    let spawned = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 0.55 + Math.random() * 0.25;
      d.mesh.visible = true;
      // v2.45 · ESCOMBROS DEL COLOR DEL LADRILLO: rojos → trocitos ROJOS
      // (los azules ya sueltan trocitos AZULES en _laserConvert)
      d.mesh.material = this.redMats[b.matIdx];
      d.mesh.position.copy(b.mesh.position);
      d.mesh.position.x += (Math.random() - 0.5) * 0.3;
      d.mesh.position.y += (Math.random() - 0.5) * 0.15;
      d.vel.set((Math.random() - 0.5) * 2.4, Math.random() * 1.6,
        0.6 + Math.random() * 1.6);
      if (++spawned >= 6) break;
    }
    const pan = THREE.MathUtils.clamp(b.mesh.position.x / 2.5, -1, 1);
    g.audio.playNoise(0.07, 1500, 1.2, 0.15, pan);
    g.audio.playOsc(620 + b.mesh.position.y * 120, 260, 0.09, 'square', 0.13, pan);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 50);
    this._hudDirty = true;
  }

  _lifeLost() {
    const g = this.game;
    this.lives--;
    this._hudDirty = true;
    if (this.lives > 0) {
      this._msg = T('ark_life', { n: this.lives });
      this._msgT = 1.6;
      g.audio.playOsc(392, 240, 0.24, 'triangle', 0.15, 0);
      // v2.41: SAQUE de partida normal (bola en la mano libre)
      this._crossed = false;
      this._enterServe();
      this._msg = T('ark_life', { n: this.lives });   // sobre el hint
      this._msgT = 1.6;
    } else {
      this._finish(false, 'lives');
    }
  }

  _finish(win, reason) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? 4.4 : 3.6;
    if (win) {
      // v3.2.0 · CAMINO EO: la prueba superada AVANZA la etapa (persiste
      // _pruebaFin) y la rejugada deja el camino como estaba (v2.96).
      if (a._replay) {
        this._banner = { title: this.variant === 2 ? T('ark2_win') : T('ark_win'),
          sub: T('replay_done'), col: '#7fb069' };
        try { g.audio.announce(T('replay_done'), true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: this.variant === 2 ? T('ark2_win') : T('ark_win'),
          sub: tx('Siguiente: ' + sig.name, 'Next: ' + sig.name), col: '#7fb069',
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
      // derrota: la etapa se REPITE (flujo amable de la plantilla EO)
      if (a._replay) {
        this._banner = { title: reason === 'lives' ? T('ark_nolives') : T('ark_timeup'),
          sub: T('replay_done'), col: '#e06c5a' };
      } else {
        this._banner = {
          title: reason === 'lives' ? T('ark_nolives') : T('ark_timeup'),
          sub: tx('La prueba se repite: vuelve a intentarlo cuando quieras',
                  'The test repeats: try again any time'), col: '#e06c5a',
        };
        a._pruebaFin(false);
      }
      g.audio.fanfare(false);
    }
    this._hudDirty = true;
    if (a.mapaa) a.mapaa.refresh();
  }

  _afterResult() {
    const a = this.ctrl;
    this.stop();
    // v3.2.0: la SALA retoma el camino (cartel, mapa, árbitro dormido,
    // música) — el flujo propio de la plantilla Estación Orbital.
    a._despuesDePrueba();
  }

  /* ---------------- animaciones y HUD ---------------- */

  _anims(dt) {
    // v2.41: flashes de destrucción (estallido aditivo que crece y muere)
    for (const f of this._flashes) {
      if (f.t <= 0) continue;
      f.t += dt;
      const k = f.t / 0.22;
      if (k >= 1) { f.t = 0; f.mesh.visible = false; continue; }
      f.mesh.material.opacity = 0.85 * (1 - k);
      f.mesh.scale.setScalar(0.5 + k * 1.1);
    }
    for (let i = this._dying.length - 1; i >= 0; i--) {
      const d = this._dying[i];
      d.t += dt * 3.4;
      if (d.t >= 1) {
        d.mesh.visible = false;
        this._dying.splice(i, 1);
        continue;
      }
      d.mesh.scale.setScalar(Math.max(0.01, 1 - d.t));
      d.mesh.rotation.z += d.spin * dt;
      d.mesh.rotation.x += d.spin * 0.6 * dt;
    }
    for (const d of this._debris) {
      if (d.life <= 0) continue;
      d.life -= dt;
      if (d.life <= 0) { d.mesh.visible = false; continue; }
      d.vel.y += DIMS.gravity * 0.72 * dt;   // v2.42: gravedad REAL (escombros)
      d.mesh.position.addScaledVector(d.vel, dt);
      d.mesh.rotation.x += dt * 6;
      d.mesh.rotation.y += dt * 4.4;
      d.mesh.scale.setScalar(Math.max(0.05, Math.min(1, d.life * 2.2)));
    }
    // v2.46 · "+1 MIN" (extra.png): sube despacio y se desvanece en 2 s
    if (this._extraFx && this.extraPlane) {
      const g = this.game;
      const fx = this._extraFx;
      fx.t += dt;
      const k = fx.t / 2;
      if (k >= 1) {
        this._extraFx = null;
        this.extraPlane.visible = false;
      } else {
        this.extraPlane.position.y = fx.pos.y + 0.16 * k;
        this.extraPlane.material.opacity =
          k < 0.15 ? k / 0.15 : Math.max(0, 1 - (k - 0.15) / 0.85);
        this.extraPlane.quaternion.copy(
          g.camera ? g.camera.quaternion : new THREE.Quaternion());
      }
    }
  }

  _hud() {
    this._hudDirty = false;
    const cv = this.hudCv, g2 = cv.getContext('2d');
    const W = 1024, H = 214;
    g2.clearRect(0, 0, W, H);
    // tarjeta
    g2.fillStyle = 'rgba(8,14,30,0.92)';
    g2.strokeStyle = 'rgba(232,180,90,0.9)';
    g2.lineWidth = 7;
    g2.beginPath();
    const rr = 30;
    g2.moveTo(rr, 6); g2.arcTo(W - 6, 6, W - 6, H - 6, rr);
    g2.arcTo(W - 6, H - 6, 6, H - 6, rr);
    g2.arcTo(6, H - 6, 6, 6, rr);
    g2.arcTo(6, 6, W - 6, 6, rr);
    g2.closePath(); g2.fill(); g2.stroke();

    const banner = this._banner;
    if (banner && (this.phase === 'intro' || this.phase === 'result')) {
      g2.textAlign = 'center'; g2.textBaseline = 'middle';
      g2.fillStyle = banner.col;
      g2.font = '900 78px system-ui, sans-serif';
      g2.fillText(banner.title, 512, this.phase === 'intro' ? 88 : 84);
      g2.fillStyle = '#dfe6ec';
      g2.font = '600 40px system-ui, sans-serif';
      g2.fillText(banner.sub, 512, this.phase === 'intro' ? 160 : 156);
      this.hudTex.needsUpdate = true;
      return;
    }
    // línea de juego: tiempo · ladrillos · vidas
    const sec = Math.max(0, Math.ceil(this.time));
    const mm = Math.floor(sec / 60), ss = sec % 60;
    const tcol = sec <= 10 ? '#ff5a48' : sec <= 60 ? '#ffd257' : '#eef2f6';
    g2.textAlign = 'left'; g2.textBaseline = 'middle';
    g2.fillStyle = tcol;
    g2.font = '900 86px ui-monospace, SFMono-Regular, Menlo, monospace';
    g2.fillText(`${mm}:${ss < 10 ? '0' : ''}${ss}`, 56, 104);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_time'), 58, 172);
    g2.textAlign = 'center';
    g2.fillStyle = '#eef2f6';
    g2.font = '800 52px system-ui, sans-serif';
    g2.fillText(`${this.bricks.length - this.bricksLeft} / ${this.bricks.length}`, 512, 96);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_bricks'), 512, 166);
    // vidas
    g2.textAlign = 'right';
    const full = ARK_CFG.lives, lost = full - Math.max(0, this.lives);
    let dots = '';
    for (let i = 0; i < full; i++) dots += i < (full - lost) ? '\u25CF ' : '\u25CB ';
    g2.fillStyle = this.lives <= 1 ? '#ff5a48' : '#7fb069';
    g2.font = '800 46px system-ui, sans-serif';
    g2.fillText(dots.trim(), 972, 96);
    g2.fillStyle = '#9aa7b4';
    g2.font = '700 26px system-ui, sans-serif';
    g2.fillText(T('hud_lives'), 970, 166);
    if (this._msg) {
      g2.textAlign = 'center';
      g2.fillStyle = '#ffd257';
      g2.font = '800 40px system-ui, sans-serif';
      g2.fillText(this._msg, 512, 40);
    }
    this.hudTex.needsUpdate = true;
  }
}

/* ============================================================================
 *  PwSignEO (v3.2.1) — ANUNCIO ÉPICO de «SUPER POWER!!» · port 1:1 del
 *  ArcadePowerSign de La Locura (v2.40 → v2.88), petición del dueño:
 *  «aparece enfrente nuestra a la altura de la red la imagen SuperPower.png
 *  con un símbolo que identifica el superpoder dentro de un círculo próximo».
 *    · Anclado a la RED (bajo el rig, con la mesa): centro a netTopY + 0,14,
 *      30 cm hacia el jugador; gira en XZ para mirar a la cámara.
 *    · Coreografía ≈ 2 s: ENTRADA rápida desde la izquierda (0 → 0,40 s),
 *      PARADA con leve vaivén y HALO DE CONTORNO dorado que respira (hasta
 *      1,45 s), SALIDA rápida por la derecha (1,45 → 1,90 s).
 *    · ICONO CIRCULAR (medallón power*.png del poder anunciado) bajo el
 *      arte, a la derecha — el identificador de la casa (v2.120).
 *  ========================================================================== */
class PwSignEO {
  constructor(ctrl) {
    this.game = ctrl.game;
    this.ctrl = ctrl;
    this.t = -1;                       // -1 = oculto
    this.T_IN = 0.40;                  // entrada rápida desde un lado
    this.T_HOLD = 1.45;                // hasta aquí: parada con vaivén
    this.T_OUT = 1.90;                 // salida rápida por el lado contrario
    this.inited = false;
    this.iconCache = null;
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;

    this.group = new THREE.Group();    // ancla a la RED (posición/rotación)
    this.pivot = new THREE.Group();    // coreografía local del cartel
    this.group.add(this.pivot);

    // arte del cartel (superpower.png de la casa, el sello de locura/magia/oeste)
    this.mat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, depthTest: false, opacity: 0,
    });
    this.mat.renderOrder = 49;
    this.plane = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 0.502), this.mat);
    this.plane.renderOrder = 49;
    this.pivot.add(this.plane);

    // HALO DE CONTORNO — la silueta REAL del arte (su canal alfa) estampada
    // con sombra difusa dorada + halo ámbar exterior (v2.40 de locura).
    this.haloMat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, depthTest: false,
      blending: THREE.AdditiveBlending, opacity: 0,
    });
    this.haloMat.renderOrder = 48;
    this.halo = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 0.502), this.haloMat);
    this.halo.renderOrder = 48;
    this.halo.scale.setScalar(1.2);
    this.pivot.add(this.halo);

    this.group.visible = false;
    // v2.88: bajo el RIG (con la mesa) — anclado a la RED en vez de a la
    // cabeza (a la altura de la red, lejos de la cara del jugador).
    g.rig.add(this.group);

    try {
      const img = new Image();
      img.onload = () => {
        const tex = new THREE.Texture();
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.image = img;
        tex.needsUpdate = true;
        this.mat.map = tex;
        this.mat.needsUpdate = true;
        // aspecto real del arte (1408×768 → 1.833): alto acorde
        const ar = img.width / Math.max(1, img.height);
        const fit = Math.min(1, 1.833 / Math.max(0.5, ar));
        this.plane.scale.set(1, fit, 1);
        this.halo.scale.set(1.2, 1.2 * fit, 1);
        this._buildHaloFrom(img, 512, Math.max(64, Math.round(512 / Math.max(0.5, ar))));
        try { this.ctrl._ownTex.add(tex); } catch (e) { /* */ }
      };
      img.onerror = () => this._fallbackArt();
      img.src = this.ctrl._A('superpower.png');
    } catch (e) { this._fallbackArt(); }

    this.iconCache = new Map();
  }

  /** Halo a partir de la silueta (alfa) del arte — dos pasadas de sombra
   *  difusa: núcleo dorado pegado al contorno + halo ámbar ancho (aditivo). */
  _buildHaloFrom(src, w, h) {
    try {
      const mk = (blur, color) => {
        const cv = document.createElement('canvas');
        cv.width = w; cv.height = h;
        const c = cv.getContext('2d');
        c.shadowColor = color;
        c.shadowBlur = blur;
        c.shadowOffsetX = 0;
        c.shadowOffsetY = 0;
        for (let i = 0; i < 3; i++) c.drawImage(src, 0, 0, w, h);
        return cv;
      };
      const wide = mk(Math.max(14, Math.round(h * 0.16)), 'rgba(255,150,40,0.85)');
      const core = mk(Math.max(8, Math.round(h * 0.07)), 'rgba(255,214,110,0.95)');
      const c2 = core.getContext('2d');
      c2.globalCompositeOperation = 'lighter';
      c2.drawImage(wide, 0, 0);
      const tex = new THREE.CanvasTexture(core);
      tex.colorSpace = THREE.SRGBColorSpace;
      this.haloMat.map = tex;
      this.haloMat.needsUpdate = true;
      try { this.ctrl._ownTex.add(tex); } catch (e) { /* */ }
    } catch (e) { console.warn('[pwSignEO.halo]', e); }
  }

  _fallbackArt() {
    // sin arte: letrero dibujado "SUPER POWER!!" con brillo (respaldo locura)
    try {
      const cv = document.createElement('canvas');
      cv.width = 1024; cv.height = 512;
      const g = cv.getContext('2d');
      g.fillStyle = 'rgba(10,16,38,0.85)';
      g.beginPath();
      if (g.roundRect) g.roundRect(24, 24, 976, 464, 56); else g.rect(24, 24, 976, 464);
      g.fill();
      g.lineWidth = 14;
      g.strokeStyle = '#e8b45a';
      g.stroke();
      g.textAlign = 'center';
      g.textBaseline = 'middle';
      g.shadowColor = '#ffd257';
      g.shadowBlur = 34;
      g.fillStyle = '#ffd257';
      g.font = '900 190px system-ui, sans-serif';
      g.fillText('SUPER', 512, 190);
      g.fillStyle = '#bfe3ff';
      g.font = '900 170px system-ui, sans-serif';
      g.fillText('POWER!!', 512, 380);
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      this.mat.map = tex;
      this.mat.needsUpdate = true;
      this._buildHaloFrom(cv, 512, 256);
      try { this.ctrl._ownTex.add(tex); } catch (e) { /* */ }
    } catch (e) { console.warn('[pwSignEO.fallback]', e); }
  }

  /** show(iconUrl): lanza la coreografía y muestra el ICONO del poder. */
  show(iconUrl) {
    if (!this.inited) this.build();
    this.t = 0;
    this.group.visible = true;
    this._iconShow(iconUrl);
    // parte del lado IZQUIERDO, sin arte visible aún (v2.40)
    if (this.pivot) {
      this.pivot.position.set(-1.15, 0, 0);
      this.pivot.rotation.z = 0;
      this.pivot.scale.setScalar(0.92);
    }
    this.mat.opacity = 0;
    this.haloMat.opacity = 0;
  }

  /** Icono circular bajo el cartel (textura perezosa en caché, v2.120). */
  _iconShow(iconUrl) {
    if (!iconUrl) {
      if (this.iconPlane) this.iconPlane.visible = false;
      return;
    }
    if (!this.iconPlane) {
      this.iconPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(0.30, 0.30),
        new THREE.MeshBasicMaterial({
          transparent: true, depthWrite: false, depthTest: false,
          opacity: 0,
        }));
      // el renderOrder va en el OBJETO (el del material se ignora en el
      // orden transparente) — si no, el propio cartel lo tapaba
      this.iconPlane.renderOrder = 51;
      this.iconPlane.position.set(0.30, -0.16, 0.012);
      this.pivot.add(this.iconPlane);
    }
    const mat = this.iconPlane.material;
    let tex = this.iconCache.get(iconUrl);
    if (!tex) {
      tex = new THREE.TextureLoader().load(iconUrl, () => {
        if (mat) mat.needsUpdate = true;
      }, undefined, () => { /* sin icono: oculto */ });
      tex.colorSpace = THREE.SRGBColorSpace;
      this.iconCache.set(iconUrl, tex);
    }
    mat.map = tex;
    mat.opacity = 1;
    mat.needsUpdate = true;
    this.iconPlane.visible = true;
  }

  hide() {
    this.t = -1;
    if (this.group) this.group.visible = false;
    if (this.iconPlane) this.iconPlane.visible = false;
  }

  update(dt) {
    if (this.t < 0 || !this.group || !this.group.visible) return;
    this.t += dt;
    // el icono acompaña SIEMPRE al fundido del cartel (v2.120)
    if (this.iconPlane && this.iconPlane.visible) {
      this.iconPlane.material.opacity = this.mat.opacity;
    }
    // v2.88: anclado a la RED — centro del cartel a la altura de la red
    // (netTopY + 0,14), 30 cm del lado del jugador; gira en XZ para mirar
    // al jugador.
    const D = this.ctrl.D;
    if (D) {
      this.group.position.set(0, D.netTopY + 0.14, D.tableCenterZ + 0.30);
      try {
        const c = this.game.camera;
        if (c) {
          const dx = c.position.x - this.group.position.x;
          const dz = c.position.z - this.group.position.z;
          if (Math.abs(dx) > 1e-4 || Math.abs(dz) > 1e-4) {
            this.group.rotation.y = Math.atan2(dx, dz);
          }
        }
      } catch (e) { /* se queda mirando al lado del jugador (+Z) */ }
    }
    // v2.40 · COREOGRAFÍA: entrada rápida desde la IZQUIERDA → parada con
    // leve vaivén y halo que respira → salida rápida por la DERECHA.
    const t = this.t;
    const X = 1.15;                    // media anchura del recorrido lateral (m)
    if (t < this.T_IN) {
      const k = t / this.T_IN;
      const e = 1 - Math.pow(1 - k, 3);           // easeOutCubic
      this.pivot.position.x = -X * (1 - e);
      this.pivot.rotation.z = (1 - e) * 0.1;
      this.pivot.scale.setScalar(0.92 + 0.08 * e);
      this.mat.opacity = Math.min(1, t / 0.12);
    } else if (t < this.T_HOLD) {
      this.pivot.position.x = Math.sin(t * 6.4) * 0.012;
      this.pivot.rotation.z = Math.sin(t * 5.1) * 0.035;
      this.pivot.scale.setScalar(1 + Math.sin(t * 8.2) * 0.022);
      this.mat.opacity = 1;
    } else if (t < this.T_OUT) {
      const k = (t - this.T_HOLD) / (this.T_OUT - this.T_HOLD);
      const e = k * k * k;                        // easeInCubic
      this.pivot.position.x = X * e;
      this.pivot.rotation.z = -0.06 * e;
      this.pivot.scale.setScalar(1);
      this.mat.opacity = k > 0.72 ? Math.max(0, 1 - (k - 0.72) / 0.28) : 1;
    } else {
      this.hide();
      return;
    }
    // halo: entra con el cartel y respira mientras está parado
    const breathe = 0.78 + Math.sin(t * 9.0) * 0.22;
    this.haloMat.opacity = this.mat.opacity *
      (t < this.T_IN ? 0.4 : breathe) * 0.9;
    if (t >= this.T_OUT - 0.12) {
      this.haloMat.opacity *= Math.max(0, (this.T_OUT - t) / 0.12);
    }
  }

  /** Dispose completo (regla Quest: nada queda colgado al salir). */
  dispose() {
    try { if (this.group && this.group.parent) this.group.parent.remove(this.group); } catch (e) { /* */ }
    if (this.iconCache) {
      for (const t of this.iconCache.values()) { try { t.dispose(); } catch (e) { /* */ } }
      this.iconCache = null;
    }
    this.group = null; this.pivot = null; this.plane = null; this.halo = null;
    this.iconPlane = null;
    this.inited = false; this.t = -1;
  }
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
    this.prueba = new DianasOrbitales(this);   // motor legacy (sin uso desde v3.2.0)
    // v3.2.0: MUROS ORBITALES (port del ARKANOID de La Locura)
    this.arkanoid = new EOArkanoid(this);
    this._beams = []; this._gunArt = [];
    this._gunLast = 0; this._gunHintDone = false;
    this._gunArtModel = null; this._gunArtLoading = false; this._gunMuzzle = null;
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
    // v3.2.1: cartel SuperPower de la casa + expresiones del ASTRO
    this.pwSign = null;
    this._rivalEstado = '';        // último estado aplicado (anti-recarga)
    this._exprT = 0;               // transitorio de expresión restante
    this._streakP = 0; this._streakAi = 0;
    this._picandoDone = false;
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

    // RIVAL: standee del ASTRO (assets/rival.webp, arte del dueño)
    // v3.2.1 · POSICIÓN DEL RIVAL = convención FORAJIDO (oeste v2.87, informe
    // del dueño: «está mal colocado metiéndose dentro de la pared derecha y
    // debería estar sobre la misma altura que otros rivales como forajido»):
    // CUERPO ENTERO con el plano de 2,15 m del Oeste (personaje visible
    // ≈ 1,8 m — el arte 512×1024 del ASTRO es exactamente la proporción 0,5
    // del forajido), PIES EN EL SUELO (baseY = alto/2) y su mismo spot:
    // junto al fondo, lado derecho (x 1,62 · z −4,5). Sin giros: de cara,
    // como el forajido. Antes: plano de 1,75 m flotando a media sala
    // (x 1,26 · z −3,5), que se leía metido en la pared derecha y bajo.
    const texRival = new THREE.TextureLoader().load(this._A('rival.webp'));
    texRival.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(texRival);
    this._rival = texRival;
    const rivalMat = new THREE.MeshBasicMaterial({
      map: texRival, transparent: true, alphaTest: 0.25, depthWrite: false,
    });
    const RIV_H = 2.15;                       // convención OESTE.spriteHeight
    this.rivalMesh = new THREE.Mesh(new THREE.PlaneGeometry(RIV_H * 0.5, RIV_H), rivalMat);
    this.rivalMesh.position.set(1.62, RIV_H / 2, (D.tableCenterZ || -1.6) - 2.9);
    this.rivalMesh.renderOrder = 6;
    this.group.add(this.rivalMesh);
    this._rivalEstado = '';
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
    this.cartel.position.set(-2.2, 1.5, -5.28);
    this.cartel.rotation.set(0, 0.1, 0);
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

    // CARTEL DEL SUPERPODER (v3.2.1): el ANUNCIO OFICIAL de la casa —
    // port del ArcadePowerSign de La Locura (arte SuperPower!! a la altura
    // de la red + medallón circular del poder). Informe del dueño: el panel
    // provisional «no es como en el resto de campeonatos».
    if (!this.pwSign) {
      this.pwSign = new PwSignEO(this);
      this.pwSign.build();
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
    // assets/<estado>.webp si existe; si no, mantiene el actual.
    // v3.2.1: si el estado no cambia NO recarga — el motor de expresiones
    // vigila cada frame y reasignar el mismo webp 60 veces/s no es gratis
    // (decode + subida a GPU en Quest).
    if (this._rivalEstado === estado) return;
    this._rivalEstado = estado;
    try {
      const img = new Image();
      img.onload = () => { this._rival.image = img; this._rival.needsUpdate = true; };
      img.src = this._A(estado + '.webp');
    } catch (e) { this._rivalEstado = ''; }
  }

  /* — v3.2.1 · EXPRESIONES DEL ASTRO (motor del clown de La Locura) ———
   *  Mismos umbrales que el ArcadeController (picando 7 golpes de rallye,
   *  combo 6, sorpresa 3, ventaja 6, pánico a 10): el ARTE manda, sin voz.
   *  Transitorios con retorno a la cara base del duelo; el aviso de
   *  superpoder ('crazy') tiene prioridad y el final ('derrotado'/'
   *  triunfante') no se pisa. */
  _exprSet(est, t) { this._exprT = t || 0; this.rivalEstado(est); }
  _exprBase() {
    const r = this.game.rules;
    const dif = (r.scorePlayer | 0) - (r.scoreAi | 0);
    if (dif >= 6) return 'loosing';                 // el ASTRO lo está pasando mal
    if ((r.scorePlayer | 0) >= 10) return 'panic';  // match-point en contra
    return 'duelo';                                 // cara de duelo (base)
  }
  _exprOnPoint(it) {
    if (this.state !== 'duelo' || !it || it.survival) return;
    if (it.winner === 'player') {
      this._streakP = (this._streakP || 0) + 1; this._streakAi = 0;
      const hits = it.rallyHits | 0;
      if (hits >= 6) {
        // COMBO del jugador: el ASTRO se ENFADA (como el clown)
        this._exprSet('angry', 2.6);
      } else {
        this._exprSet('surprised', hits >= 3 ? 1.7 : 1.2);
      }
    } else {
      this._streakAi = (this._streakAi || 0) + 1; this._streakP = 0;
      if (this._streakAi >= 2) this._exprSet('crazy', 3.4);   // enloquece
      else this._exprSet('laughing', 2.4);                    // se ríe de ti
    }
  }
  _exprUpdate(dt) {
    if (this.state !== 'duelo') { this._exprT = 0; return; }
    const g = this.game;
    const r = g.rules;
    if (r.state === 'over') return;       // 'derrotado'/'triunfante' mandan
    if (this._exprT > 0) {                // transitorio en curso
      this._exprT -= dt;
      if (this._exprT <= 0) this.rivalEstado(this._exprBase());
      return;
    }
    if (this._warn || this._act) return;  // 'crazy' del aviso de poder manda
    if (r.state === 'rally') {
      if ((r.rallyHits | 0) >= 7 && !this._picandoDone) {
        this._picandoDone = true;         // rallye largo: ¡se pone picado!
        this._exprSet('picando', 2.2);
      } else {
        this.rivalEstado(this._exprBase());
      }
    } else {
      this._picandoDone = false;
      this.rivalEstado(this._exprBase());
    }
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
    if (this.arkanoid) this.arkanoid.stop();   // v3.2.0: fuera el muro
    this._purgeBeams();                        // v2.120: sin rayos huérfanos
    this._restoreGun();                        // v3.2.0: monturas al estado core
    try {
      if (this.game.gunMounts) {
        for (const gm of this.game.gunMounts) if (gm) gm.visible = false;
      }
    } catch (e) { /* */ }
    // v3.1 (V2.131) · restitución del ÁRBITRO al salir (convención magia):
    // si el campeonato se abandona desde la sala/prueba el núcleo quedaría
    // con rules.state='champtest' para siempre (menú sin árbitro).
    try {
      if (g.rules.state === 'champtest') {
        g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
      }
    } catch (e0) { /* */ }
    if (this.mapa) this.mapa.dispose();       // v2.130: sin restos GPU
    if (this.pwSign) this.pwSign.dispose();   // v3.2.1: cartel SuperPower fuera
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
    // v3.2.0: en PRUEBA el gatillo lanza el SAQUE del muro (EOArkanoid)
    if (this.arkanoid && this.arkanoid.active) { this.arkanoid.serveTrigger(); return; }
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
    // v3.2.1: expresiones del ASTRO a cero en cada duelo
    this._streakP = 0; this._streakAi = 0;
    this._exprT = 0; this._picandoDone = false;
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
    // v3.2.0 · MUROS ORBITALES: las pruebas del camino son ahora ARKANOID
    if (et.id === 'muro1' || et.id === 'muro2') { this._empezarMuro(et); return; }
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
  /* — v3.2.0 · MUROS ORBITALES: cartel explicativo (piel del artista vía
   *  NORMAS_SKIN) + arranque del EOArkanoid ——————————————— */
  _empezarMuro(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';       // árbitro dormido durante el cartel
    this.cartel.visible = false;
    this.rivalEstado('idle');
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        const es2 = (et.id === 'muro2');
        g.showInstrucciones(
          tx('PRUEBA · ' + et.name.toUpperCase(), 'SKILL TEST · ' + et.name.toUpperCase()),
          es2 ? [
            tx('Muro de 54 ladrillos: los ROJOS sólo caen con la PALA; los AZULES sólo con el LÁSER (explotan y quedan rojos).',
               '54-brick wall: RED bricks fall to the PADDLE only; BLUE ones to the LASER only (they blow up and turn red).'),
            tx('La PISTOLA LÁSER va en tu mano libre. 2 min 30 s y 5 vidas; los rojos vivos se vuelven azules con el tiempo.',
               'The LASER PISTOL rides your free hand. 2 min 30 s, 5 lives; live reds turn blue over time.'),
          ] : [
            tx('Rompe TODOS los ladrillos del muro golpeando la bola con las palas: el rebote es real, calcula los ángulos.',
               'Break EVERY wall brick by hitting the ball with your paddles: real bounces, work the angles.'),
            tx('Tienes 2 minutos y 5 vidas (saques). Cada ladrillo roto suma.',
               '2 minutes and 5 lives (serves). Every broken brick counts.'),
          ],
          7.5,
          () => {
            this._instrK = null;          // próxima entrada re-explica (regla v2.106)
            try { this._arrancarMuro(et); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarMuro(et);
  }
  _arrancarMuro(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // el núcleo enruta testStep/gatillo/láser
    this.arkanoid.variant = (et.id === 'muro2') ? 2 : 1;
    this.arkanoid.start();
    this.musicOn();
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

  /* ===================== v3.2.0 · PISTOLA LÁSER (MURO 2) ==================
   *  Port del pegamento de La Locura (v2.44/2.74): getter de armado,
   *  disparo con RAYCAST real sobre los ladrillos, carga perezosa del
   *  pistol.glb del artista, encaje normalizado y visibilidad por frame. */
  get gunArmed() {
    const g = this.game;
    const ark = this.arkanoid;
    return !!(this.state === 'prueba' && ark && ark.active && ark.variant === 2 &&
      ark.phase === 'play' &&
      g.gunMounts && g.gunMounts[1 - g.paddleHand] &&
      g.gunMounts[1 - g.paddleHand].visible);
  }

  fireGun(i) {
    const g = this.game;
    const mount = g.gunMounts && g.gunMounts[i];
    if (!mount) return;
    const now = performance.now() / 1000;
    if (now - this._gunLast < 0.16) return;
    this._gunLast = now;
    const pos = new THREE.Vector3();
    const q = new THREE.Quaternion();
    mount.getWorldPosition(pos);
    mount.getWorldQuaternion(q);
    const dir = new THREE.Vector3(0, Math.sin(GUN_MOUNT_PITCH), -Math.cos(GUN_MOUNT_PITCH))
      .applyQuaternion(q).normalize();
    pos.add((this._gunMuzzle || GUN_MUZZLE).clone().applyQuaternion(q));
    // RAYCAST: el primer ladrillo que cruza el haz recibe SU lógica
    let hitDist = 6.0;
    let hitBrick = null;
    let hitTime = false;
    const hitPoint = new THREE.Vector3();
    const ark = this.arkanoid;
    if (ark && ark.active && ark.bricks && ark.bricks.length) {
      const ray = new THREE.Raycaster(pos, dir, 0, 6.0);
      const meshes = ark.bricks.filter((b) => b.alive).map((b) => b.mesh);
      if (ark._timeBrick && ark.timeMesh) meshes.push(ark.timeMesh);
      const hits = ray.intersectObjects(meshes, false);
      if (hits.length) {
        hitDist = hits[0].distance;
        hitPoint.copy(hits[0].point);
        hitBrick = ark.bricks.find((b) => b.mesh === hits[0].object) || null;
        hitTime = !hitBrick && hits[0].object === ark.timeMesh;
      }
    }
    const mid = pos.clone().addScaledVector(dir, hitDist / 2);
    const beam = new THREE.Mesh(
      new THREE.CylinderGeometry(0.0042, 0.0042, hitDist, 6, 1, true),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0.95,
        depthWrite: false, blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      }),
    );
    beam.position.copy(mid);
    beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
    const glow = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, hitDist, 8, 1, true),
      new THREE.MeshBasicMaterial({
        color: 0x66d9ff, transparent: true, opacity: 0.4,
        depthWrite: false, blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      }),
    );
    glow.position.copy(mid);
    glow.quaternion.copy(beam.quaternion);
    g.scene.add(beam);
    g.scene.add(glow);
    this._beams.push({ mesh: beam, glow, t: 0 });
    if (hitBrick) {
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark.laserHit(hitBrick);
    } else if (hitTime) {
      g.rig.updateWorldMatrix(true, false);
      const lp = g.rig.worldToLocal(hitPoint.clone());
      ark._flash(lp);
      ark._breakTimeBrick();
    }
    g.audio.playOsc(1760, 320, 0.1, 'sawtooth', 0.07, 0);
    g.audio.playOsc(2640, 660, 0.08, 'sine', 0.045, 0);
    g.audio.playNoise(0.05, 3400, 2.2, 0.035, 0);
    if (g.renderer.xr.isPresenting) g.haptic(i, 0.4, 60);
  }

  _loadGunArt() {
    const g = this.game;
    if (!g.gunMounts) return;
    if (this._gunArtModel) { this._attachGunArt(); return; }
    if (!GUN_ART_URL || this._gunArtLoading) return;
    this._gunArtLoading = true;
    try {
      new GLTFLoader().load(GUN_ART_URL, (gltf) => {
        this._gunArtLoading = false;
        try {
          const model = this._normalizeGun(gltf.scene);
          if (!model) return;
          this._gunArtModel = model;
          this._attachGunArt();
          console.info('[estacion] pistol.glb del artista montada (MURO 2)');
        } catch (e) { console.warn('[estacion] pistola: normalización KO', e); }
      }, undefined, () => {
        this._gunArtLoading = false;
        console.warn('[estacion] pistol.glb no disponible — se mantiene la del core');
      });
    } catch (e) { this._gunArtLoading = false; }
  }

  _normalizeGun(scene) {
    const box = new THREE.Box3().setFromObject(scene);
    if (box.isEmpty()) return null;
    const size = box.getSize(new THREE.Vector3());
    const root = new THREE.Group();
    root.add(scene);
    const ax = [['x', size.x], ['y', size.y], ['z', size.z]].sort((a, b) => b[1] - a[1]);
    if (ax[0][0] === 'x') scene.rotation.y = Math.PI / 2;
    else if (ax[0][0] === 'y') scene.rotation.x = -Math.PI / 2;
    const s2 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const ax2 = [['x', s2.x], ['y', s2.y]].sort((a, b) => b[1] - a[1])[0][0];
    if (ax2 === 'x') scene.rotateZ(Math.PI / 2);
    const s3 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const len = Math.max(s3.x, s3.y, s3.z) || 1;
    root.scale.setScalar(0.32 / len);
    try {
      root.updateMatrixWorld(true);
      const lv = new THREE.Vector3(), tv = new THREE.Vector3();
      let found = false;
      root.traverse((o) => {
        if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
        const pa = o.geometry.attributes.position;
        if (!pa) return;
        for (let i2 = 0; i2 < pa.count; i2++) {
          tv.fromBufferAttribute(pa, i2).applyMatrix4(o.matrixWorld);
          if (!found || tv.y < lv.y) { lv.copy(tv); found = true; }
        }
      });
      if (found && lv.z < 0) root.rotation.y += Math.PI;
    } catch (e) { /* orientación original si el barrido falla */ }
    const b4 = new THREE.Box3().setFromObject(root);
    const c = b4.getCenter(new THREE.Vector3());
    root.position.set(-c.x, -b4.min.y - 0.055, -c.z);
    try {
      const bFin = new THREE.Box3().setFromObject(root);
      const dimF = bFin.getSize(new THREE.Vector3());
      this._gunMuzzle = new THREE.Vector3(0, dimF.y - 0.075, bFin.min.z + 0.015);
    } catch (e) { this._gunMuzzle = new THREE.Vector3(0, 0.02, -0.16); }
    try {
      const fin = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
      window.__PP_EO_GUN_INFO = {
        len: +fin.z.toFixed(3), alto: +fin.y.toFixed(3), ancho: +fin.x.toFixed(3),
      };
    } catch (e) { /* */ }
    return root;
  }

  _attachGunArt() {
    const g = this.game;
    if (!g.gunMounts || !this._gunArtModel) return;
    this._restoreGun();
    for (const gm of g.gunMounts) {
      if (!gm) continue;
      for (const ch of gm.children) ch.visible = false;
      const art = this._gunArtModel.clone(true);
      art.userData.__eoArt = true;
      gm.add(art);
      this._gunArt.push({ mount: gm, art });
    }
  }

  _restoreGun() {
    for (const rec of this._gunArt || []) {
      const gm = rec.mount;
      if (!gm) continue;
      gm.remove(rec.art);
      for (const ch of gm.children) ch.visible = true;
    }
    this._gunArt = [];
  }

  _gunUpdate(dt) {
    const g = this.game;
    const ark = this.arkanoid;
    const ark2On = !!(ark && ark.active && ark.variant === 2 &&
      g.renderer && g.renderer.xr && g.renderer.xr.isPresenting);
    const holdPhase = ark && (ark.phase === 'serve' || ark.phase === 'intro' ||
      ark.phase === 'result');
    const armed = ark2On && !holdPhase;
    if (armed && !this._gunHintDone) {
      this._gunHintDone = true;
      try { g.rules.message = T('ark_gun_on'); } catch (e) { /* */ }
    }
    if (ark2On && !this._gunArtModel) this._loadGunArt();
    if (ark2On && this._gunArtModel && (this._gunArt || []).length === 0) {
      this._attachGunArt();
    }
    if (g.gunMounts) {
      for (let k = 0; k < 2; k++) {
        if (g.gunMounts[k]) g.gunMounts[k].visible = armed && k === g.ballHand;
      }
    }
    for (let i = this._beams.length - 1; i >= 0; i--) {
      const b = this._beams[i];
      b.t += dt;
      const f = 1 - b.t / 0.16;
      if (f <= 0) {
        for (const m of [b.mesh, b.glow]) {
          if (!m) continue;
          g.scene.remove(m);
          m.geometry.dispose();
          m.material.dispose();
        }
        this._beams.splice(i, 1);
        continue;
      }
      b.mesh.material.opacity = 0.95 * f;
      if (b.glow) b.glow.material.opacity = 0.4 * f;
    }
  }

  _purgeBeams() {
    if (!this._beams || !this._beams.length) return;
    const g = this.game;
    for (const b of this._beams) {
      for (const m of [b.mesh, b.glow]) {
        if (!m) continue;
        g.scene.remove(m);
        try { m.geometry.dispose(); } catch (e) { /* */ }
        try { m.material.dispose(); } catch (e) { /* */ }
      }
    }
    this._beams.length = 0;
  }

  /** v3.2.0 · objeto de PRUEBA activo: el muro primero, las DIANAS legacy
   *  después (el contrato testActive/testStep del núcleo no cambia). */
  _testActivo() {
    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;
    if (this.prueba && this.prueba.stepActive && this.prueba.stepActive()) return this.prueba;
    return null;
  }

  aiMul() {
    if (this.state !== 'duelo') return 1;
    const et = this._etapa();
    return (et && et.aiMul) || 1;
  }
  onPoint(it) {
    this._exprOnPoint(it);   // v3.2.1: expresión según quién anota
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
    // v3.2.0: pistola láser del MURO 2 (montaje/visibilidad/fade de rayos)
    if (this.arkanoid && this.arkanoid.active) this._gunUpdate(dt);
    // v3.2.1: coreografía del cartel SuperPower (ancla a la red + vaivén)
    if (this.pwSign) this.pwSign.update(dt);
    // v3.2.1: EXPRESIONES DEL ASTRO según el momento de la partida
    this._exprUpdate(dt);
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
    this.rivalEstado('crazy');            // v3.2.0: ¡el ASTRO se revuelve!
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
        // v3.2.1: el haz baja SOBRE TU CAMPO (z −1,05, entre la red y el
        // borde cercano) con la punta tocando la superficie de la mesa —
        // antes flotaba en z −3,22, tras el borde lejano (fuera de mesa)
        this.beam.position.set(0, 1.9, (D.tableCenterZ || -1.6) + 0.55);
        this.beam.scale.set(1, 1.14, 1);           // cono: 1,9 m → punta en 0,76
        this.beam.rotation.z = 0;
        try { g.audio.playOsc(90, 55, 0.6, 'sawtooth', 0.12, 0); } catch (e) { /* */ }
      } else if (def.name === 'Gravedad cero') {
        const D = this.D;
        for (const m of this.motas) {
          // v3.2.1: motas flotando sobre TU campo, dentro de la mesa
          m.x = (Math.random() * 2 - 1) * 0.70;
          m.y = 0.85 + Math.random() * 0.95;
          m.z = (D.tableCenterZ || -1.6) + 0.15 + Math.random() * 1.1;
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
    if (this.state === 'duelo') this.rivalEstado('duelo');   // v3.2.0: cara de duelo
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

  /* — v3.2.1 · CARTEL DEL SUPERPODER (anuncio oficial de la casa) ————
   *  Fase AVISO: PwSignEO lanza la coreografía «Super Power!!» con el
   *  medallón circular del poder (~2 s — el efecto se suelta al terminar,
   *  patrón locura v2.36). Fase ACTIVA: sin cartel — el efecto YA es el
   *  aviso (así lo hacen locura/magia/oeste). */
  _psMuestra(def, activa) {
    if (!this.pwSign || activa) return;
    let icon = '';
    try {
      // CFG.icon trae 'assets/…' y _A() YA antepone './assets/' (v3.2)
      icon = this._A(String(def.icon || '').replace(/^assets\//, ''));
    } catch (e) { /* sin icono: cartel solo */ }
    this.pwSign.show(icon || null);
  }
  _psOculta() { if (this.pwSign) this.pwSign.hide(); }

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
    const D = this.D;
    c.t += dt;
    const dentro = c.t < c.dur;
    for (const p of this._poolConfeti) {
      if (!p.on && dentro && Math.random() < dt * 8) {
        p.on = true;
        p.x = (Math.random() * 2 - 1) * 0.85;
        p.y = 2.0 + Math.random() * 0.4;
        // v3.2.1: TU CAMPO y ENCIMA de la mesa (antes −1,50..+0,05 llovía
        // detrás del jugador y se perdía fuera de la mesa)
        p.z = (D.tableCenterZ || -1.6) + 0.15 + Math.random() * 1.15;
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
        // v3.2.1: nacimiento ENCIMA de la mesa, en TU campo (antes x ±0,95
        // y z hasta −0,10: parte de las rocas caía FUERA de la mesa —
        // «no tienen efectos», informe del dueño)
        r.x = (Math.random() * 2 - 1) * 0.60;
        r.z = (D.tableCenterZ || -1.6) + 0.15 + Math.random() * 1.0;
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
 *  Oeste: −2,98 / 1,5 / −0,9 mirando al centro; arte 1376×768). Ruta de 5
 *  nodos + insignia final, TAPAS sobre los nodos futuros, anillo dorado en
 *  el nodo vigente, hover azul al apuntar con la pala y REJUGA por gatillo
 *  (contrato replayMap del núcleo, v2.96 — el campeonato superado queda
 *  ABIERTO). PERFECTAMENTE ESTÁTICO salvo el anillo.
 *  v3.2.1 · NODOS RE-MEDIDOS sobre el arte del dueño (mapa.png 1376×768,
 *  medido sobre la imagen: el nodo 5 del arte está MÁS ABAJO de lo que
 *  se creía — y 266 → 335 — y los medallones reales miden ~215-235 px):
 *   0 DUELO 1 (222,260,r108) · 1 MURO 1 (460,500,r112) · 2 DUELO 2
 *   (725,255,r112) · 3 MURO 2 (962,510,r118) · 4 DUELO FINAL (1197,335,r115)
 *  TAPAS de 240 px base (lección v2.136 del Oeste: la tapa cubre el
 *  medallón ENTERA — las de 165 px dejaban ver los bordes del arte).
 * ========================================================================== */
class MapaEO {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.nodesPx = [
      { x: 222,  y: 260, r: 108, tapa: false, ts: 1.0 },
      { x: 460,  y: 500, r: 112, tapa: true,  ts: 1.12 },
      { x: 725,  y: 255, r: 112, tapa: true,  ts: 1.0 },
      { x: 962,  y: 510, r: 118, tapa: true,  ts: 1.12 },
      { x: 1197, y: 335, r: 115, tapa: true,  ts: 1.02 },
    ];
    this.currentIdx = 0;
    this.IMG_W = 1376;               // v3.2.0: mapa nuevo del dueño
    this.IMG_H = 768;
    this.PW = 1.68;
    this.PH = 1.68 * 768 / 1376;
    this.TAPA_W = 240 / 1376 * this.PW;
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
  decor: {"pieces": [{"file": "assets/decor/escena_cohete.png", "h": 1.15, "x": -2.55, "z": -2.5, "sway": 0.5}, {"file": "assets/decor/escena_astro.png", "h": 1.0, "x": 2.1, "z": -2.5, "sway": 0.3}, {"file": "assets/decor/escena_lander.png", "h": 0.95, "x": 2.45, "z": -0.85, "sway": 0.4}, {"file": "assets/decor/escena_telescopio.png", "h": 0.62, "x": -2.45, "z": -0.85, "sway": 0.35}]},   // v3.2.0: recortables reales del dueño
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
    // v3.2.0: pistola real del artista para el MURO 2 (ARKANOID II)
    try { GUN_ART_URL = new URL('./assets/pistol.glb', import.meta.url).href; } catch (e) { /* */ }
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
  reenter() {   // v3.2.0: en pleno muro, reanuda la prueba
    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {
      try { CTRL.arkanoid.reenter(); } catch (e) { /* */ }
      return;
    }
    if (CTRL) CTRL.reenter();
  },
  // v2.130 · REJUGADA por el mapa del camino (pared izquierda)
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },
  musicOff() { if (CTRL) CTRL.musicOff(); },   // invariante UNA MELODÍA v2.125
  /** v3: PRUEBA activa → el núcleo NO integra la bola y llama testStep. */
  testActive() { return !!(CTRL && CTRL._testActivo()); },   // v3.2.0: muro primero
  testStep(dt) {
    const o = CTRL && CTRL._testActivo();
    if (o) {
      try { o.step(dt); }
      catch (e) { console.warn('[estacion.testStep]', e); }
    }
  },
};


/* ============================================================================
 * PLANTILLA DE CAMPEONATO · CRAZY PING PONG · Ronda 25 (Taller unificado)
 * ----------------------------------------------------------------------------
 * Módulo genérico data-driven: TODO el comportamiento configurable vive en
 * manifest.json (catálogo unificado con lo que los 5 campeonatos tienen entre
 * todos). Crear un campeonato nuevo = copiar esta carpeta, subir el arte,
 * rellenar el manifest y validar (scripts/qa_plantilla.py).
 *
 * Contrato núcleo↔módulo (champ_sdk.js v1.4.0, contract 1):
 *   export default { id, decor, room, controller, isChampion, champIntroPause,
 *     init(ctx), start, leave, resetRecords, update, onPoint, onMatchOver,
 *     aiMul, serveTrigger, reenter, replayMap, replayHover, replayLaunch,
 *     musicOff, testActive, testStep, [gunArmed, fireGun] }
 *
 * Comportamientos incluidos:
 *   · Camino duelo→prueba→duelo→prueba→final (patrón común de los 5), con
 *     dificultad 'formula' (valle) o 'tabla' (oeste/orbital).
 *   · DUELO completo contra el rival (núcleo arbitra a N puntos; curva aiMul;
 *     expresiones del rival por umbrales unificados).
 *   · Prueba 'dianas' con 3 modos (objetivos/movimiento/contrarreloj) —
 *     generalización de DianasDelTaller de valle_neon.
 *   · Motor de SUPERPODERES de dos fases (aviso congelado + efecto) con bolsa
 *     rotatoria (locura) o anti-repetición (magia), activación rally/puntos,
 *     garantía temporal y kinds confeti/globos/bola + hook 'custom'.
 *   · CORONACIÓN épica (panel del núcleo con estadísticas + fecha registrada,
 *     oeste Ronda 24) y RUTA LEYENDA NG+ con 5 sellos (oeste).
 *   · Rejugada por mapa (arte del artista o canvas dibujado), pistola láser
 *     opcional, trofeo al coronar, telemetría y ranking mundial.
 *
 * Puntos de extensión (documentados en ../PLANTILLA-GUIA.md):
 *   PLANTILLA_PRUEBAS  → añadir kinds de prueba nuevos (arkanoid, tren...)
 *   PLANTILLA_PODERES  → añadir kinds de superpoder nuevos
 * ==========================================================================*/
import * as THREE from 'three';
/* r90 · EL GLB DE LA CALABAZA SE RETIRA DEL RUNTIME: calabaza.glb (Sketch-
 * fab) «carga» pero no llega a pintarse en el casco en 4 rondas (r86→r89)
 * — el dueño autorizó «buscar otra forma»: la calabaza ES ahora el cuerpo
 * PROCEDURAL de la casa (lathe con costillas + rabo + zarcillo), garanti-
 * zado desde el frame 1 con el mismo pipeline que el trofeo del Hall. Sin
 * GLB no hay esperas, ni swaps, ni bolas invisibles. El import se CONSER-
 * VA para la pistola láser de la plantilla (playerGun, no activa aquí). */
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import {
  getCore, assetURL, congela, descongela,
  createSfx, createMusic, createPowerSign, createRival, createCartel, createBucle,
} from '../sdk/champ_sdk.js';

/* ------------------------------------------------------------------ */
/* Estado del módulo                                                   */
/* ------------------------------------------------------------------ */
const MOD_URL = import.meta.url;
const A = (p) => assetURL(MOD_URL, p);

let CORE = null;      // window.__PP_CORE vía getCore()
let GAME = null;      // objeto game del núcleo
let MAN = null;       // manifest.json (config unificada)
let CTRL = null;      // PlantillaController
let DIMS = null;      // dimensiones del núcleo
let STATE_NAME = 'champtest';
let SFX = null;
let MUSIC = null;
/* r90 · motores one-shot del zombi (createBucle × sonido) + tick de corte */
let ZONB = null;

const TXT = { es: {}, en: {} };
let DECOR = { pieces: [] };
let ROOM = null;

/* ------------------------------------------------------------------ */
/* Utilidades                                                          */
/* ------------------------------------------------------------------ */
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rand = (a, b) => a + Math.random() * (b - a);
const pick = (arr) => arr[(Math.random() * arr.length) | 0];

function tx(key, params) {
  const lang = (CORE && CORE.lang && CORE.lang()) || 'es';
  let s = (TXT[lang] && TXT[lang][key]) || TXT.es[key] || key;
  if (params) for (const k in params) s = s.split('{' + k + '}').join(params[k]);
  return s;
}

function storageKey(k) {
  const base = (MAN.storage || 'pp_champ_' + MAN.id + '_').replace(/\*$/, '');
  return base + k;
}
function sGet(k) { try { return localStorage.getItem(storageKey(k)); } catch (e) { return null; } }
function sSet(k, v) { try { localStorage.setItem(storageKey(k), String(v)); } catch (e) {} }
function sDel(k) { try { localStorage.removeItem(storageKey(k)); } catch (e) {} }

const CLAVES_REGISTRO = ['stage', 'champ', 'fecha', 'puntos', 'duelwins', 'wins',
  'rank', 'leyenda_1', 'leyenda_2', 'leyenda_3', 'leyenda_4', 'leyenda_5', 'leyenda'];

function nombreJugador() {
  try { return (localStorage.getItem('pp_player_name') || 'Anónimo').slice(0, 12); }
  catch (e) { return 'Anónimo'; }
}

function telemetria(ev, payload) {
  try { if (window.__PP_TELE && window.__PP_TELE.ev) window.__PP_TELE.ev(ev, payload); } catch (e) {}
}
function rankingMundial(a) {
  try {
    if (window.__PP_WORLD && window.__PP_WORLD.submit) {
      const p = MAN.camino && MAN.camino.worldMetric === 'puntos' ? CTRL.puntos() : CTRL.duelwins();
      window.__PP_WORLD.submit(MAN.id, { n: nombreJugador(), p: p | 0, a: a });
    }
  } catch (e) {}
}

/* ------------------------------------------------------------------ */
/* Registro de comportamientos (puntos de extensión)                   */
/* ------------------------------------------------------------------ */
/* Cada kind de prueba es una clase con la misma forma que DianasPrueba:
 *   constructor(ctrl, game, stage, cfg)   — cfg = manifest.pruebas[kind] + stage.rules
 *   start(), stop(), dispose(), step(dt), activa() → bool, lanzar() opcional
 * Para portar un kind existente (arkanoid/orbe/impulso/escudo/tren/asedio),
 * copia su clase desde el campeonato de origen y registra aquí su kind.     */
const PLANTILLA_PRUEBAS = { dianas: null };   // se rellena más abajo (hoisting de clases)
const PLANTILLA_PODERES = {};                 // kind → { inicio(game, power, ctrl, ctx), fin(game, power, ctrl, ctx), paso(dt, ctx) }

/* ------------------------------------------------------------------ */
/* Rival: sprite vía SDK + motor de expresiones unificado              */
/* ------------------------------------------------------------------ */
const EXPR_DEF = { picandoRallyHits: 7, loosingDiff: 6, comboRally: 6, surprisedRally: 3 };

class RivalVivo {
  constructor(game, man) {
    this.game = game;
    this.man = man;
    this.rv = man.rivalVisual || {};
    this.estados = (man.rival && man.rival.states) || ['idle', 'duelo'];
    this.thresholds = Object.assign({}, EXPR_DEF, (man.rival && man.rival.thresholds) || {});
    this.timer = 0; this.base = 'idle'; this.baseDuelo = 'duelo';
    const ALTO = this.rv.alto || 2.15;
    // r87 · INFORME DEL DUEÑO («no aparece el rival»): el node del SDK NUNCA
    // se añadía a la escena (el docstring de createRival lo exige) y la pos
    // por defecto nacía a y=0 (medio cuerpo bajo el suelo). convención del
    // orbital: pies en el suelo · x derecha · z = mesa − 1,70.
    this.r = createRival(THREE, () => this.game, {
      modo: this.rv.modo || 'precarga',
      base: this.rv.base || 'rival.webp',
      ext: this.rv.ext || 'webp',
      estados: this.estados,
      resuelve: (f) => A(f),
      alto: ALTO,
      anchoFijo: this.rv.anchoFijo || 0,
      aspecto: this.rv.aspecto !== false,
      material: this.rv.material || 'basic',
      alphaTest: this.rv.alphaTest != null ? this.rv.alphaTest : 0.25,
      /* r88 · INFORME DEL DUEÑO («el zombi debe aparecer en relación a la
       * mesa algo más a la derecha… se referenciaban a la mesa»): anclaje
       * a la MESA — z = mesa − 1,70 (convención que ya daba menos
       * problemas) y x REFERIDA AL CANTO derecho de la mesa (+0,69).
       * Nada de x absolutos: si la mesa se mueve, el zombi la sigue. */
      pos: this.rv.pos || [
        ((DIMS && DIMS.tableHalfWidth) || 0.7625) + 0.69,
        ALTO / 2,
        ((DIMS && DIMS.tableCenterZ) || -1.6) - 1.70,
      ],
      rotY: this.rv.rotY || 0,
      castShadow: this.rv.material === 'standard',
    });
    // r87 · AL MUNDO (sin esto el zombi no existe: mesh huérfano fuera del
    // grafo — el fallo exacto que veía el dueño). dispose() del SDK lo
    // desengancha del padre; removeRival cubre el caso de re-entrada.
    try { (this.game.scene || this.game.rig).add(this.r.node); } catch (e) { /* */ }
    /* r89 · el PREWARM VISIBLE (pasear las 12 caras a 0,12 s durante ~1,5 s)
     * se RETIRA: el SDK sube ahora cada cara a GPU al llegar con
     * renderer.initTexture — sin parpadeo de poses ni «estados super-
     * puestos» percibidos por el dueño. this.estado manda desde el 1.er frame. */
    this.fallbacks = {
      hungry: ['hungry', 'surprised', 'idle'], surprised: ['surprised', 'idle'],
      crazy: ['crazy', 'laughing', 'idle'], laughing: ['laughing', 'idle'],
      picando: ['picando', 'idle'], loosing: ['loosing', 'idle'],
      panic: ['panic', 'surprised', 'idle'], angry: ['angry', 'idle'],
      defeated: ['defeated', 'derrotado', 'loosing', 'idle'],
      victory: ['victory', 'triunfante', 'idle'],
      derrotado: ['derrotado', 'defeated', 'idle'], triunfante: ['triunfante', 'victory', 'idle'],
      present: ['present', 'idle'], duelo: ['duelo', 'focused', 'idle'],
      focused: ['focused', 'idle'], idle: ['idle'],
    };
  }
  _set(nombre, dur) {
    const cadena = this.fallbacks[nombre] || [nombre, 'idle'];
    const dispo = this.estados;
    let elegido = cadena.find((s) => dispo.indexOf(s) >= 0) || dispo[0] || 'idle';
    this.estado = elegido;
    if (this.r) this.r.rivalEstado(elegido);
    if (dur) this.timer = dur;
  }
  estadoBase(nombre) { this.base = nombre; if (this.timer <= 0) this._set(nombre, 0); }
  /** v3.6.49 (ronda 57) · NORMA DE EMOCIONES DEL RIVAL (regla del dueño,
   *  norma en TODOS los campeonatos): el núcleo reparte la emoción
   *  estándar y el rival la viste con SU arte (convención <estado>.webp
   *  + _set con fallbacks) y la acompaña con SU arte sonoro (r91):
   *  laughing → risas burlonas (el zombi gana el punto), crazy →
   *  zombi_crazy, victory/defeated → las del dueño. Los sonidos del
   *  rival son SIEMPRE (ignoraMute) y el reloj de corte (_zombiSfxTick)
   *  los cierra antes del wrap. */
  rivalEmocion(st) {
    const DUR = {
      idle: 0, crazy: 3.2, angry: 2.2, laughing: 2.2, focused: 2.2,
      picando: 2.2, surprised: 2.0, panic: 2.2, loosing: 2.2,
      victory: 2.4, defeated: 4.0,
    };
    const MAPA = { victory: 'triunfante' };   // convención local del abanico
    this._set(MAPA[st] || st, DUR[st] != null ? DUR[st] : 2.0);
    /* r91 · SONIDO según la norma (los otros campeonatos acompañan la
     * emoción con SU arte sonoro — el zombi no podía quedarse mudo). */
    const SONIDO = { laughing: 'laugh', crazy: 'crazy', victory: 'victory', defeated: 'defeated' };
    if (SONIDO[st] && SFX) SFX.play(SONIDO[st], 0.62);
  }
  enDuelo(en) { this.timer = 0; this.estadoBase(en ? this.baseDuelo : 'idle'); }   // r91: una etapa nueva SIEMPRE recompone la cara
  final(ganaJugador) { this._set(ganaJugador ? 'defeated' : 'triunfante', 4.0); }
  /* r91 · reaccion() SE RETIRA: la reacción al punto la reparte el NÚCLEO
   * (norma r57 — «las reacciones locales de puntos de los módulos quedan
   * SUSTITUIDAS por esta norma») — el doble motor pisaba las emociones
   * del core y el dueño no veía cambios limpios. */
  update(dt, ctx) {
    if (!this.r) return;
    /* r91 · SOLO el temporizador y la flotación: la emoción manda DESDE
     * EL NÚCLEO (rivalEmocion) y el estado base lo fijan enDuelo/sala/
     * final. Fuera el motor legacy (picando/loosing/panic) que pisaba la
     * norma del núcleo cada frame. */
    if (this.timer > 0) { this.timer -= dt; if (this.timer <= 0) this._set(this.base, 0); }
    if (this.rv.flotacion && this.rv.flotacion.activo !== false && this.r.node) {
      // r87 · flotación sobre el node REAL (sin grupo: el mesh va directo)
      const amp = this.rv.flotacion.amplitud || 0.012;
      const per = this.rv.flotacion.periodo || 1.4;
      const base = this.r.node.position.y;
      this.r.node.position.y = base + Math.sin(performance.now() / 1000 * (Math.PI * 2 / per)) * amp - (this._flotAnt || 0);
      this._flotAnt = Math.sin(performance.now() / 1000 * (Math.PI * 2 / per)) * amp;
    }
  }
  risa() { if (SFX && SFX.tiene('laugh')) SFX.play('laugh', 0.55, { pan: 0.4 }); }
  dispose() { if (this.r) { try { this.r.dispose(); } catch (e) {} } this._flotAnt = 0; }
}

/* ------------------------------------------------------------------ */
/* Cartel de bienvenida (createCartel del SDK)                         */
/* ------------------------------------------------------------------ */
function construirCartel(game, man) {
  const c = man.cartel || {};
  /* r88 · INFORME DEL DUEÑO («aparece un cartel metido en la pared
   * izquierda hacia el fondo, que no sé qué está haciendo ahí»): el
   * cartel de bienvenida se RETIRA de Halloween por normativa — la etapa
   * la pinta el HUD, las normas salen al lanzar cada etapa y el cartel
   * de superpoder es el ÚNICO cartel de la sala. Lo decide el manifest
   * (cartel.oculto): los otros campeonatos conservan el suyo. */
  if (c.oculto) return null;
  const cartel = createCartel(THREE, () => game, {
    cvW: c.cvW || 1024, cvH: c.cvH || 512,
    w: c.w || 2.3, h: c.h || 1.15,
    pos: c.pos || [-1.05, 1.62, -3.6],
    rot: c.rot || [0, 0.42, 0],
    transparent: true,
  });
  cartel.pinta((ctx2, W, H) => {
    ctx2.clearRect(0, 0, W, H);
    ctx2.fillStyle = 'rgba(10,12,20,0.72)';
    const r = 28; const w = W - 24, h = H - 24, x = 12, y = 12;
    ctx2.beginPath();
    ctx2.moveTo(x + r, y);
    ctx2.arcTo(x + w, y, x + w, y + h, r); ctx2.arcTo(x + w, y + h, x, y + h, r);
    ctx2.arcTo(x, y + h, x, y, r); ctx2.arcTo(x, y, x + w, y, r);
    ctx2.fill();
    ctx2.fillStyle = '#fbbf24';
    ctx2.font = 'bold 64px sans-serif';
    ctx2.textAlign = 'center';
    ctx2.fillText(man.title.es || man.title.en || man.id, W / 2, 110);
    ctx2.fillStyle = '#e2e8f0';
    ctx2.font = '42px sans-serif';
    const et = CTRL ? CTRL.etapaActual() : null;
    /* v3.6.77 (r85) · el total era «/5» fijo: los campeonatos UGC pueden tener
     * otro número de etapas (el mapa de Halloween trae 5 nodos del artista y
     * los futuros pueden traer lo que quiera) — total REAL del camino. */
    const linea2 = et ? ('Etapa ' + CTRL.indice() + '/' + CTRL.totalEtapas() + ' · ' + et.name) : tx('bienvenida');
    ctx2.fillText(linea2, W / 2, 200);
    ctx2.fillStyle = '#94a3b8';
    ctx2.font = '36px sans-serif';
    ctx2.fillText('VS ' + ((man.rival && man.rival.name) || 'RIVAL') + (CTRL && CTRL.isChampion() ? '  🏆' : ''), W / 2, 275);
    ctx2.font = '32px sans-serif';
    ctx2.fillStyle = '#cbd5e1';
    const lineas = (TXT.es && TXT.es.instr_lineas) || [];
    lineas.slice(0, 3).forEach((l, i) => ctx2.fillText(l, W / 2, 350 + i * 46));
  });
  // r87 · AL MUNDO (igual que el rival: el mesh del SDK no se cuelga solo —
  // el cartel de bienvenida tampoco se veía por este motivo).
  try { game.scene.add(cartel.mesh); } catch (e) { /* */ }
  return cartel;
}

/* ------------------------------------------------------------------ */
/* Mapa del camino: modo 'canvas' (dibujado, valle) o 'arte' (póster)  */
/* ------------------------------------------------------------------ */
class MapaPlantilla {
  constructor(game, man, ctrl) {
    this.game = game; this.man = man; this.ctrl = ctrl;
    const m = man.mapa || {};
    this.modo = m.modo || 'canvas';
    this.planoW = m.planoW || 1.68;
    /* r91 · RECETA WIZARDMAP — LA QUE EL DUEÑO VE «PERFECTAMENTE COLOCADA
 * SOBRE LA PARED IZQUIERDA EN TODOS LOS CAMPEONATOS» (magia v2.60/oeste
 * v2.136): GRUPO colgado del RIG (no de la escena), x −2.98 (7 cm de la
 * pared — los −3.043 a 7 mm morían tras el plano de la pared en el casco),
 * y 1.5, z −0.9, ancho 1.68 + RESPALDO de madera oscura detrás (caja de
 * 22 mm que lo ancla como un cuadro) + material TRANSPARENTE con opacity 0
 * hasta que la textura llega (nunca un rectángulo negro) + SRGB. Tapas,
 * anillo de rejugada y API de contrato intactos. */
    this.pos = m.pos || [-2.98, 1.5, -0.9];
    this.rotY = m.rotY != null ? m.rotY : (Math.PI / 2);
    this.nodos = [];        // [{x,y,r}] en píxeles de la imagen
    this.imgW = 1280; this.imgH = 720;
    this.maxIdx = () => Math.max(0, Math.min(ctrl.totalEtapas() - 1, ctrl.indiceReal() - 1));
    this._hover = -1;
    this._tapas = [];       // r87: tapas sobre las etapas aún no superadas
    this._tapasIdx = -1;    // r87: último maxIdx pintado (refresco barato)
    this._construir();
  }
  _construir() {
    const etapas = this.ctrl.etapas();
    let textura;
    if (this.modo === 'arte' && this.man.mapa.arte) {
      this.imgW = 1380; this.imgH = 752;
      this.nodos = (this.man.mapa.nodos && this.man.mapa.nodos.length === etapas.length)
        ? this.man.mapa.nodos.map((n) => ({ x: n.x, y: n.y, r: n.r || 110, ts: n.ts || 1 }))
        : this._rejilla(etapas.length, this.imgW, this.imgH);
      /* r91b · EL GATE DE OPACITY SE CIERRA PARA SIEMPRE: la sonda r91b
       * cazó el fallo EN VIVO — la textura LLEGABA (244 KB · 1380×752 ·
       * image vivo) y el plano seguía opacity 0: el sondeo con setInterval
       * (120 ms, ventana 15 s) no siempre ve la llegada (el image puede
       * ponerse DESPUÉS del build y el intervalo morir antes, o el closure
       * consultar una textura sustituida). MAGIA (v2.60) NO SONDEA: pasa
       * el material SIN mapa y asigna mapa+opacity 1 DENTRO del callback
       * del TextureLoader — el callback ES el evento de llegada, no puede
       * perderse. ÉSE es el patrón que el dueño ve «perfectamente colo-
       * cado en TODOS los campeonatos»: se porta TAL CUAL. El sondeo viejo
       * queda como RESPALDO (refresco() re-levanta el gate: ver abajo) y
       * el callback manda. */
      this._urlArte = A(String(this.man.mapa.arte).replace(/^assets\//, ''));
    } else {
      const cv = document.createElement('canvas');
      cv.width = 1280; cv.height = 720;
      const g = cv.getContext('2d');
      this.nodos = this._rejilla(etapas.length, 1280, 720);
      g.fillStyle = '#0b1222'; g.fillRect(0, 0, 1280, 720);
      g.strokeStyle = '#1e293b'; g.lineWidth = 10;
      for (let i = 0; i < this.nodos.length - 1; i++) {
        g.beginPath();
        g.moveTo(this.nodos[i].x, this.nodos[i].y);
        g.lineTo(this.nodos[i + 1].x, this.nodos[i + 1].y);
        g.stroke();
      }
      const hecho = this.ctrl.indiceReal() - 1;
      this.nodos.forEach((n, i) => {
        const esTap = i > this.maxIdx();
        g.beginPath(); g.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        g.fillStyle = esTap ? '#1e293b' : (i < hecho ? '#166534' : (i === hecho ? '#b45309' : '#334155'));
        g.fill();
        g.lineWidth = 8; g.strokeStyle = i === hecho ? '#fbbf24' : (i < hecho ? '#86efac' : '#0b1222');
        g.stroke();
        g.fillStyle = esTap ? '#64748b' : '#f8fafc';
        g.font = 'bold 56px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
        g.fillText(esTap ? '?' : (etapas[i].kind === 'duelo' ? '⚔' : '🎯'), n.x, n.y);
        g.font = '30px sans-serif'; g.fillStyle = '#cbd5e1';
        g.fillText(etapas[i].name, n.x, n.y + n.r + 30);
      });
      textura = new THREE.CanvasTexture(cv);
      textura.colorSpace = THREE.SRGBColorSpace;
    }
    const asp = this.imgH / this.imgW;
    /* r91 · GRUPO del patrón WizardMap: respaldo + póster + anillo viven
     * juntos y cuelgan del RIG (el padre que usan TODOS los mapas que el
     * dueño ve bien — el de la escena era el que fallaba en el casco). */
    this.grupo = new THREE.Group();
    this.back = new THREE.Mesh(
      new THREE.BoxGeometry(this.planoW + 0.06, this.planoW * asp + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x2b1d10, roughness: 0.9, metalness: 0.05 }),
    );
    this.back.position.z = -0.013;
    this.grupo.add(this.back);
    this.plane = new THREE.Mesh(
      new THREE.PlaneGeometry(this.planoW, this.planoW * asp),
      /* r91b · patrón magia EXACTO: material SIN mapa + opacity 0 — el
       * mapa y el opacity 1 llegan JUNTOS en el callback del loader (o en
       * el respaldo de refresco()). Nunca un rectángulo negro, nunca un
       * póster invisible. */
      new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, opacity: 0 }),
    );
    this.grupo.add(this.plane);
    this.grupo.position.set(this.pos[0], this.pos[1], this.pos[2]);
    this.grupo.rotation.y = this.rotY;
    this.anillo = new THREE.Mesh(
      new THREE.RingGeometry(0.118, 0.144, 48),
      new THREE.MeshBasicMaterial({ color: 0xf6d34c, transparent: true, depthWrite: false, side: THREE.DoubleSide }),
    );
    this.anillo.material.opacity = 0.9;
    this.anillo.position.z = 0.012;
    this.anillo.renderOrder = 3;
    this.anillo.visible = false;
    this.grupo.add(this.anillo);
    /* r91 · AL RIG — el padre probado en el casco por los 5 campeonatos */
    const raiz = this.game.rig || this.game.scene;
    try { raiz.add(this.grupo); } catch (e) { this.game.scene.add(this.grupo); }
    if (this.modo === 'arte' && this._urlArte) {
      /* r91b · EL CALLBACK DEL LOADER — el patrón de WizardMap (magia),
       * el que el dueño ve bien en todos los campeonatos: la textura se
       * asigna y el gate SE ABRE dentro del callback de llegada. Sin
       * sondeos, sin ventanas que caducan, sin closures a texturas
       * sustituidas. colorSpace+anisotropía AQUÍ (la textura nace sana). */
      const g91 = this.game;
      new THREE.TextureLoader().load(this._urlArte, (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        try { tex.anisotropy = g91.renderer.capabilities.getMaxAnisotropy(); } catch (e) { /* */ }
        if (this.plane) {
          this.plane.material.map = tex;
          this.plane.material.opacity = 1;
          this.plane.material.needsUpdate = true;
        }
        this._texArte = tex;
      });
    } else {
      this.plane.material.opacity = 1;   // canvas: ya está
    }
    // r87 · TAPAS: las etapas aún NO superadas quedan CUBIERTAS (normativa
    // del dueño, igual que el '?' del mapa canvas). Discos hijos del plano
    // (se mueven con él; el rayo de rejugada NO las ve — intersectObject
    // es no-recursivo y sólo cubren nodos no apuntables).
    const texTapa = this._texTapa();
    for (let i = 0; i < this.nodos.length; i++) {
      const n = this.nodos[i];
      const rW = (n.r / this.imgW) * this.planoW;
      const lx = (n.x / this.imgW - 0.5) * this.planoW;
      const ly = (0.5 - n.y / this.imgH) * this.planoW * (this.imgH / this.imgW);
      const tapa = new THREE.Mesh(
        new THREE.CircleGeometry(rW * 1.12, 40),
        new THREE.MeshBasicMaterial({ map: texTapa, transparent: true, depthWrite: false }),
      );
      tapa.position.set(lx, ly, 0.006);
      tapa.renderOrder = 2;
      this.plane.add(tapa);
      this._tapas.push(tapa);
    }
    this._pintaTapas();
  }
  /* r87 · textura de la TAPA: piedra oscura con «?» de hueso y aro sepia —
   * casa con el póster del cementerio (UNA textura compartida). */
  _texTapa() {
    if (MapaPlantilla._texTapa) return MapaPlantilla._texTapa;
    const S = 256;
    const cv = document.createElement('canvas'); cv.width = cv.height = S;
    const g = cv.getContext('2d');
    const r = S / 2;
    const grad = g.createRadialGradient(r, r * 0.86, r * 0.12, r, r, r);
    grad.addColorStop(0, '#3a3128');
    grad.addColorStop(0.78, '#241d16');
    grad.addColorStop(1, '#171209');
    g.fillStyle = grad;
    g.beginPath(); g.arc(r, r, r, 0, Math.PI * 2); g.fill();
    g.lineWidth = 10; g.strokeStyle = '#54463a';
    g.beginPath(); g.arc(r, r, r - 8, 0, Math.PI * 2); g.stroke();
    g.lineWidth = 4; g.strokeStyle = 'rgba(232,223,200,0.28)';
    g.beginPath(); g.arc(r, r, r - 20, 0, Math.PI * 2); g.stroke();
    g.fillStyle = '#e8dfc8';
    g.font = '900 150px Georgia, serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.shadowColor = 'rgba(0,0,0,0.65)'; g.shadowBlur = 10;
    g.fillText('?', r, r + 8);
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    MapaPlantilla._texTapa = t;
    return t;
  }
  /* r87 · pinta/oculta tapas según el progreso: visible ⇔ etapa i aún no
   * desbloqueada (i > maxIdx) — EXACTAMENTE el criterio del '?' canvas. */
  _pintaTapas() {
    const mx = this.maxIdx();
    if (mx === this._tapasIdx) return;
    this._tapasIdx = mx;
    for (let i = 0; i < this._tapas.length; i++) {
      const t = this._tapas[i];
      if (t) t.visible = i > mx;
    }
  }
  /* r87 · el progreso cambia sin rebuild (stage clear) → refresco barato
   * desde update() del módulo (comparación de un entero). */
  refresco() {
    this._pintaTapas();
    /* r91b · RESPALDO DEL GATE (cinturón y tirantes): si el callback del
     * loader llegara a perderse (textura en caché con image tardío, re-
     * entrada del campeonato), refresco corre POR FRAME — si la imagen
     * está viva y el póster sigue apagado, se enciende aquí. Coste: dos
     * comparaciones booleanas cuando ya está abierto. */
    if (this.plane && this.plane.material && !this.plane.material.map &&
        this._texArte && this._texArte.image) {
      this.plane.material.map = this._texArte;
      this.plane.material.opacity = 1;
      this.plane.material.needsUpdate = true;
    } else if (this.plane && this.plane.material && this.plane.material.opacity < 1 &&
               this.plane.material.map && this.plane.material.map.image) {
      this.plane.material.opacity = 1;
      this.plane.material.needsUpdate = true;
    }
  }
  _rejilla(n, W, H) {
    const cols = Math.min(4, n);
    const filas = Math.ceil(n / cols);
    const yTop = 190, dy = Math.min(230, (H - 260) / Math.max(1, filas - 1) || 230);
    const spanX = Math.min(1000, 260 * (cols - 1));
    const out = [];
    for (let i = 0; i < n; i++) {
      const fila = (i / cols) | 0, col = i % cols;
      const enFila = Math.min(cols, n - fila * cols);
      const cx = W / 2 + (enFila > 1 ? (col / (enFila - 1) - 0.5) * spanX : 0);
      out.push({ x: Math.round(cx), y: Math.round(yTop + fila * dy), r: 86, ts: 1 });
    }
    return out;
  }
  hover(idx) {
    if (idx >= 0 && idx <= this.maxIdx()) {
      this._hover = idx;
      const n = this.nodos[idx];
      /* r91 · anillo HIJO del grupo: coordenadas LOCALES del plano (el
       * grupo ya lleva pos/rotY del patrón WizardMap). */
      const lx = (n.x / this.imgW - 0.5) * this.planoW;
      const ly = (0.5 - n.y / this.imgH) * this.planoW * (this.imgH / this.imgW);
      this.anillo.position.set(lx, ly, 0.012);
      this.anillo.scale.setScalar((n.ts || 1) * 1.22);
      this.anillo.material.color.setHex(0x7ec8ff);
      this.anillo.visible = true;
    } else this.anillo.visible = false;
  }
  /* API de rejugada del contrato */
  replayMap() {
    return { plane: this.plane, nodesPx: this.nodos, imgW: this.imgW, imgH: this.imgH, maxIdx: this.maxIdx() };
  }
  replayHover(idx) { this.hover(idx); }
  replayLaunch(idx) { this.ctrl.rejugar(idx); }
  dispose() {
    /* r91 · el GRUPO entero se va del rig (respaldo + póster + anillo +
     * tapas cuelgan de él). La textura de tapas es ESTÁTICA compartida. */
    const raiz = this.game.rig || this.game.scene;
    try { raiz.remove(this.grupo); } catch (e) { try { this.game.scene.remove(this.grupo); } catch (e2) { /* */ } }
    if (this.back) { if (this.back.geometry) this.back.geometry.dispose(); if (this.back.material) this.back.material.dispose(); this.back = null; }
    if (this.plane) {
      if (this.plane.geometry) this.plane.geometry.dispose();
      if (this.plane.material.map) this.plane.material.map.dispose();
      if (this.plane.material) this.plane.material.dispose();
    }
    this.grupo = null; this.plane = null; this.anillo = null;
    this._tapas = []; this._tapasIdx = -1;
  }
}

/* ------------------------------------------------------------------ */
/* Motor de SUPERPODERES de dos fases (unificado)                      */
/* ------------------------------------------------------------------ */
function _dibujarGlobo(color) {
  const cv = document.createElement('canvas'); cv.width = 128; cv.height = 160;
  const g = cv.getContext('2d');
  g.fillStyle = color;
  g.beginPath(); g.ellipse(64, 62, 46, 56, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = 'rgba(255,255,255,0.35)';
  g.beginPath(); g.ellipse(48, 44, 14, 20, -0.4, 0, Math.PI * 2); g.fill();
  g.strokeStyle = '#64748b'; g.lineWidth = 3;
  g.beginPath(); g.moveTo(64, 118); g.quadraticCurveTo(72, 138, 62, 158); g.stroke();
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const _TINTAS_GLOBO = ['#e02430', '#22d3ee', '#a3e635'];

PLANTILLA_PODERES.confeti = {
  inicio(game, p, ctrl, ctx) { game.confettiBurst = Math.max(game.confettiBurst || 0, p.duration || 8); },
  fin(game) { game.confettiBurst = 0; },
};

PLANTILLA_PODERES.globos = {
  inicio(game, p, ctrl, ctx) {
    const n = 6; const pool = [];
    for (let i = 0; i < n; i++) {
      const tex = _dibujarGlobo(_TINTAS_GLOBO[i % _TINTAS_GLOBO.length]);
      const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true }));
      m.scale.set(0.30, 0.375, 1);
      pool.push({ s: m, vy: rand(0.55, 0.9), t: 0 });
      game.scene.add(m);
    }
    ctx.globos = { pool, popT: 0 };
  },
  paso(dt, game, p, ctrl, ctx) {
    const G = ctx.globos; if (!G) return;
    const cz = DIMS.tableCenterZ;
    G.pool.forEach((o, i) => {
      o.t += dt;
      if (o.s.visible === false) {
        o.t += dt;
        if (o.t > rand(0.8, 1.5)) { o.s.visible = true; o.s.position.set(rand(-1.05, 1.05), rand(0.84, 1.0), rand(cz - 1.5, cz + 0.05)); o.vy = rand(0.55, 0.9); }
        return;
      }
      o.s.position.y += o.vy * dt;
      o.s.position.x += Math.sin(o.t * 2.1 + i) * 0.05 * dt;
      if (o.s.position.y > 1.05 + 0.5 * (o.t % 1)) o.s.position.y = rand(0.84, 1.0);
      const d = o.s.position.distanceTo(game.ballMesh ? game.ballMesh.position : game.ball.pos);
      if (d < 0.185 + DIMS.ballRadius) { o.s.visible = false; o.t = 0; ctrl.fxPop(o.s.position); }
    });
  },
  fin(game, p, ctrl, ctx) {
    const G = ctx && ctx.globos; if (!G) return;
    G.pool.forEach((o) => { game.scene.remove(o.s); o.s.material.map.dispose(); o.s.material.dispose(); });
    ctx.globos = null;
  },
};

PLANTILLA_PODERES.bola = {
  inicio(game, p, ctrl, ctx) {
    const b = game.ball, mesh = game.ballMesh;
    const pr = p.params || {};
    ctx.bola = {
      scale: clamp(pr.scale || 2.0, 1.2, 2.6),
      gravityMul: clamp(pr.gravityMul || 0.55, 0.3, 0.9),
      speedMul: clamp(pr.speedMul || 0.62, 0.4, 1.0),
      color: pr.color != null ? pr.color : 0xe02430,
      emisivo: pr.emisivo != null ? pr.emisivo : 0x8a1016,
    };
    ctx.bola.grav0 = DIMS.gravity;
    ctx.bola.max0 = DIMS.maxBallSpeed;
    ctx.bola.meshScale0 = mesh ? mesh.scale.x : 1;
    ctx.bola.mat0 = mesh && mesh.material ? { color: mesh.material.color.getHex(), emissive: mesh.material.emissive ? mesh.material.emissive.getHex() : 0 } : null;
    DIMS.gravity = ctx.bola.grav0 * ctx.bola.gravityMul;
    DIMS.maxBallSpeed = ctx.bola.max0 * ctx.bola.speedMul;
    if (mesh) {
      mesh.scale.setScalar(ctx.bola.meshScale0 * ctx.bola.scale);
      if (mesh.material) { mesh.material.color.setHex(ctx.bola.color); if (mesh.material.emissive) mesh.material.emissive.setHex(ctx.bola.emisivo); }
    }
  },
  fin(game, p, ctrl, ctx) {
    const B = ctx && ctx.bola; if (!B) return;
    DIMS.gravity = B.grav0; DIMS.maxBallSpeed = B.max0;
    const mesh = game.ballMesh;
    if (mesh) {
      mesh.scale.setScalar(B.meshScale0);
      if (mesh.material && B.mat0) { mesh.material.color.setHex(B.mat0.color); if (mesh.material.emissive) mesh.material.emissive.setHex(B.mat0.emissive); }
    }
    ctx.bola = null;
  },
};

/* ========================================================================
 * r86 · LOS 4 SUPERPODERES REALES DEL ZOMBI (petición del dueño)
 * -----------------------------------------------------------------------
 * Duración 10 s cada uno · anuncio con el cartel SuperPower del dueño +
 * medallón circular abajo-derecha (createPowerSign.iconShow) + congelación
 * momentánea de la partida (congela → game.freezeT, patrón v2.40).
 * Las manos del artista TRAEN el montículo de tierra integrado: la mano
 * sale de su propia tierra (desenrollado de la textura, no hace falta
 * monticulo.png aparte).
 * ====================================================================== */
const TEX_R86 = { cache: {}, pedir(nombre, cb) {
  if (TEX_R86.cache[nombre]) { cb(TEX_R86.cache[nombre]); return; }
  (TEX_R86.pend[nombre] = TEX_R86.pend[nombre] || []).push(cb);
  if (TEX_R86.pend[nombre].length > 1) return;
  try {
    new THREE.TextureLoader().load(A(nombre), (t) => {
      t.colorSpace = THREE.SRGBColorSpace;
      try { t.anisotropy = GAME && GAME.renderer ? GAME.renderer.capabilities.getMaxAnisotropy() : 4; } catch (e) { /* */ }
      TEX_R86.cache[nombre] = t;
      (TEX_R86.pend[nombre] || []).forEach((f) => { try { f(t); } catch (e) { /* */ } });
      delete TEX_R86.pend[nombre];
    }, undefined, () => { delete TEX_R86.pend[nombre]; });
  } catch (e) { delete TEX_R86.pend[nombre]; }
}, pend: {} };

/* -- texturas procedurales de la casa (terrones y humillo verde) -------- */
function _texTerron() {
  if (TEX_R86.cache.__terron) return TEX_R86.cache.__terron;
  const cv = document.createElement('canvas'); cv.width = cv.height = 32;
  const c = cv.getContext('2d');
  c.fillStyle = '#5a4632'; c.beginPath(); c.arc(16, 16, 14, 0, 6.3); c.fill();
  c.fillStyle = '#6e5740'; c.beginPath(); c.arc(13, 13, 8, 0, 6.3); c.fill();
  c.fillStyle = '#3f5233'; c.beginPath(); c.arc(21, 20, 5, 0, 6.3); c.fill();
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  TEX_R86.cache.__terron = t;
  return t;
}
function _texHumo() {
  if (TEX_R86.cache.__humo) return TEX_R86.cache.__humo;
  const cv = document.createElement('canvas'); cv.width = cv.height = 64;
  const c = cv.getContext('2d');
  const g = c.createRadialGradient(32, 32, 2, 32, 32, 30);
  g.addColorStop(0, 'rgba(120,255,80,0.85)');
  g.addColorStop(0.55, 'rgba(70,230,50,0.42)');
  g.addColorStop(1, 'rgba(50,200,40,0)');
  c.fillStyle = g; c.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  TEX_R86.cache.__humo = t;
  return t;
}
/* -- r88 · «CHOFFF» (petición del dueño para la mancha pisada y el
 * estallido de la calabaza podrida): golpe sordo + soplo, síntesis con
 * el motor de audio probado del núcleo (playOsc + playNoise). */
function _chofff(game, x) {
  const pan = clamp((x || 0) / 2.5, -1, 1);
  try { game.audio.playOsc(150, 42, 0.30, 'sine', 0.55, pan); } catch (e) { /* */ }
  try { game.audio.playNoise(0.38, 850, 0.9, 0.42, pan, 'lowpass'); } catch (e) { /* */ }
}

/* -- r88 · VIDA FUERA DEL PODER: el estallido de la calabaza ocurre
 * 0,55 s ANTES del cierre y las ráfagas de humo verde deben seguir en
 * el aire después — trozos y ráfagas viven en este registro GLOBAL con
 * tick desde PlantillaPoderes.update (sala y duelo) y limpieza en
 * parar()/dispose()/_desmonta. Nada sobrevive a la salida. */
const TROZOS_R88 = { lista: [], humo: [] };
function _trozoAl(game, pos, base, podre) {
  const geo = new THREE.TetrahedronGeometry(rand(0.022, 0.05));
  const mat = new THREE.MeshStandardMaterial({ color: (Math.random() < 0.5 ? base : podre).clone(), roughness: 0.85, metalness: 0.0 });
  const m = new THREE.Mesh(geo, mat);
  m.position.copy(pos).add(_v86.set(rand(-0.03, 0.03), rand(-0.02, 0.04), rand(-0.03, 0.03)));
  game.scene.add(m);
  TROZOS_R88.lista.push({
    m, t: 0, vida: rand(0.7, 1.0),
    vx: rand(-1.6, 1.6), vy: rand(1.2, 2.6), vz: rand(-1.6, 1.6),
    va: rand(-11, 11), eje: Math.random() < 0.5 ? 'x' : 'z',
  });
}
function _humoVerdeR88(game, pos, n) {
  for (let i = 0; i < n; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: _texHumo(), transparent: true, opacity: 0.9, depthWrite: false }));
    s.position.set(pos.x + rand(-0.06, 0.06), pos.y + rand(0.0, 0.09), pos.z + rand(-0.06, 0.06));
    s.scale.setScalar(0.08);
    game.scene.add(s);
    TROZOS_R88.humo.push({
      s, t: 0, vida: rand(1.6, 2.4), vy: rand(0.25, 0.6),
      vx: rand(-0.3, 0.3), vz: rand(-0.3, 0.3),
      s0: 0.08, s1: rand(0.42, 0.62), op0: rand(0.78, 0.92),
    });
  }
}
function _pasoTrozosR88(dt, game) {
  const L = TROZOS_R88.lista;
  for (let i = L.length - 1; i >= 0; i--) {
    const t = L[i];
    t.t += dt;
    t.vy -= 7.5 * dt;
    t.m.position.x += t.vx * dt; t.m.position.y += t.vy * dt; t.m.position.z += t.vz * dt;
    t.m.rotation[t.eje] += t.va * dt;
    const k = t.t / t.vida;
    if (k >= 1 || t.m.position.y < 0.02) {
      game.scene.remove(t.m);
      t.m.geometry.dispose(); t.m.material.dispose();
      L.splice(i, 1);
      continue;
    }
    if (k > 0.6) { t.m.material.transparent = true; t.m.material.opacity = Math.max(0, 1 - (k - 0.6) / 0.4); }
  }
  const H = TROZOS_R88.humo;
  for (let i = H.length - 1; i >= 0; i--) {
    const h = H[i];
    h.t += dt;
    h.s.position.y += h.vy * dt;
    h.s.position.x += h.vx * dt; h.s.position.z += h.vz * dt;
    const k = h.t / h.vida;
    h.s.scale.setScalar(h.s0 + k * (h.s1 - h.s0));
    h.s.material.opacity = Math.max(0, h.op0 * (1 - k));
    if (k >= 1) { game.scene.remove(h.s); h.s.material.dispose(); H.splice(i, 1); }
  }
}
function _trozosLimpia(game) {
  for (const t of TROZOS_R88.lista) { try { game.scene.remove(t.m); t.m.geometry.dispose(); t.m.material.dispose(); } catch (e) { /* */ } }
  TROZOS_R88.lista.length = 0;
  for (const h of TROZOS_R88.humo) { try { game.scene.remove(h.s); h.s.material.dispose(); } catch (e) { /* */ } }
  TROZOS_R88.humo.length = 0;
}

const _v86 = new THREE.Vector3();
const _q86 = new THREE.Quaternion();   // r90: marco local de las manchas de gelatina

/* -- CALABAZA PROCEDURAL DE LA CASA (r90 · «o lo solucionamos si se puede
 * o tenemos que buscar otra forma de hacerlo» — informe del dueño tras 4
 * rondas sin ver calabaza.glb) ------------------------------------------
 * POR QUÉ SE RETIRA EL GLB: el modelo de Sketchfab «cargaba» (fetch+parse
 * OK) pero no llegaba a PINTARSE en el casco (nodos Lamp, pivote y centro
 * desplazados, materiales PBR sin las luces del salón) — y como el estato
 * «listo» se marcaba al cargar, el respaldo procedural jamás entraba y la
 * bola quedaba OCULTA: «no carga el modelo y no se puede jugar».
 * LA OTRA FORMA: el mismo pipeline del TROFEO del Hall (LatheGeometry +
 * canvas, probado en el dispositivo) — cuerpo con costillas pintadas,
 * rabo y zarcillo, centrado en el origen. Cero descargas, cero esperas,
 * visible SIEMPRE. */
function _calabazaProcedural() {
  if (TEX_R86.cache.__calProc) return TEX_R86.cache.__calProc;
  /* textura: costillas verticales (gradiente por costilla + brillo lateral) */
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 128;
  const g = cv.getContext('2d');
  const gBase = g.createLinearGradient(0, 0, 0, 128);
  gBase.addColorStop(0, '#c85a08'); gBase.addColorStop(0.42, '#ef8618'); gBase.addColorStop(0.62, '#f59b2a'); gBase.addColorStop(1, '#b34e06');
  g.fillStyle = gBase; g.fillRect(0, 0, 256, 128);
  const COST = 8;                                    // 8 costillas alrededor
  for (let i = 0; i < COST; i++) {
    const x0 = (i / COST) * 256;
    const gr = g.createLinearGradient(x0, 0, x0 + 256 / COST, 0);
    gr.addColorStop(0, 'rgba(90,40,4,0.55)');        // surco oscuro
    gr.addColorStop(0.45, 'rgba(255,170,60,0.30)');  // lomo iluminado
    gr.addColorStop(1, 'rgba(90,40,4,0.55)');
    g.fillStyle = gr;
    g.fillRect(x0, 0, 256 / COST, 128);
  }
  // moteado sutil (piel natural)
  for (let i = 0; i < 90; i++) {
    g.fillStyle = 'rgba(70,30,5,' + (0.05 + Math.random() * 0.08).toFixed(2) + ')';
    g.beginPath(); g.arc(Math.random() * 256, Math.random() * 128, 1 + Math.random() * 2.2, 0, 6.3); g.fill();
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  /* perfil del cuerpo: calabaza achatada con hondillos arriba y abajo */
  const perfil = [
    [0.070, -1.000], [0.200, -0.985], [0.520, -0.880], [0.780, -0.640],
    [0.940, -0.320], [1.000, -0.020], [0.950, 0.300], [0.800, 0.580],
    [0.560, 0.800], [0.300, 0.940], [0.110, 0.995],
  ].map((p) => new THREE.Vector2(p[0] * 0.065, p[1] * 0.052));   // Ø ≈ 0,13 m ≈ 3× la bola
  const matCuerpo = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.62, metalness: 0.0, emissive: 0x1a0d02,
    /* r91 · A PRUEBA DE CASCO: DoubleSide (si Adreno llegara a cullear
     * una cara del lathe, la cara interna la sustituye — el informe del
     * dueño «solo se ve un trocito del rabito») + color base SÓLIDO
     * naranja: si la textura tarda/falla, el cuerpo ES naranja — jamás
     * invisible (el blanco por defecto cantaba menos que nada). */
    side: THREE.DoubleSide, color: 0xe8720c });
  const cuerpo = new THREE.Mesh(new THREE.LatheGeometry(perfil, 28), matCuerpo);
  const matRabo = new THREE.MeshStandardMaterial({ color: 0x4a6b23, roughness: 0.9, metalness: 0.0 });
  const rabo = new THREE.Mesh(new THREE.CylinderGeometry(0.0085, 0.014, 0.05, 8), matRabo);
  rabo.position.y = 0.062; rabo.rotation.z = 0.16; rabo.rotation.x = -0.06;
  const matZar = new THREE.MeshStandardMaterial({ color: 0x55772b, roughness: 0.85, metalness: 0.0 });
  const zar = new THREE.Mesh(new THREE.TorusGeometry(0.016, 0.0028, 6, 18, Math.PI * 1.55), matZar);
  zar.position.set(0.024, 0.058, 0.012); zar.rotation.x = Math.PI / 2.25; zar.rotation.y = 0.5;
  const grp = new THREE.Group();
  grp.add(cuerpo); grp.add(rabo); grp.add(zar);
  /* r91 · frustumCulled OFF en los tres: objeto de 13 cm que se mueve
   * cada frame con la bola — ninguna esfera envolvente obsoleta puede
   * colarlo fuera del frustum en el casco (coste: cero, se dibuja siempre). */
  grp.traverse((o) => { if (o.isMesh) o.frustumCulled = false; });
  TEX_R86.cache.__calProc = grp;
  return grp;
}

/* -- 0 · POOL DE TEXTURAS DE MANO (r87 · anti-trompicones) ---------------
 * texture.clone() crea un RECURSO GPU nuevo: clonar por cada aparición de
 * mano subía 512×885 a la GPU en plena partida (el tirón que notaba el
 * dueño). Pool de 3 clones reciclados (máx. 3 manos vivas): la imagen se
 * re-asingna si el slot trae otra base — UNA subida por slot y sólo cuando
 * cambia de mano. __r86usada marca el slot ocupado. */
function _manoTexLibre(M, baseTex) {
  let t = M.pool.find((x) => x && !x.__r86usada && x.__r86src === baseTex);
  if (!t) t = M.pool.find((x) => x && !x.__r86usada);
  if (!t) {
    if (M.pool.length < 3) { t = baseTex.clone(); t.__r86src = baseTex; M.pool.push(t); }
    else { t = baseTex.clone(); t.__r86extra = true; }   // fuera de pool: muere con el poder
  }
  t.__r86usada = true;
  if (t.__r86src !== baseTex) { t.image = baseTex.image; t.__r86src = baseTex; t.needsUpdate = true; }
  return t;
}
function _manoTexSuelta(M, t) {
  if (!t) return;
  if (t.__r86extra) { try { t.dispose(); } catch (e) { /* */ } M.pool = M.pool.filter((x) => x !== t); }
  else t.__r86usada = false;
}

/* -- 1 · MANO DE ZOMBI (r87 · reescrita según el guion del dueño) --------
 * «en cualquier sitio de la mesa aparece la imagen monticulo.png OJO lo he
 * adjuntado (actualmente no se ve, pero debería aparecer sobre la mesa
 * antes de que aparezca la mano) desde la que sale aleatoriamente una de
 * las tres imágenes de manos zombis… movimiento rápido que se frena un
 * poco en el último momento (como para dar un susto), unos 3 segundos:
 * medio segundo para aparecer/desaparecer y 2 segundos arriba».
 *
 * r90 · SIN MONTÍCULO (informe del dueño: «vamos a retirar la textura
 * monticulo.png de la mesa, puesto que al estar superpuesta con la de
 * mano1/mano2/mano3, esta última se corta y no se visualiza la parte que
 * interseca con monticulo.png»): el montículo plano SE RETIRA — la mano
 * nace DIRECTA de la mesa (su arte ya trae la tierra integrada, recorte
 * MANO_CULTIVO) y el canto de la mesa se guarda con el RADIO DE LA MANO.
 *
 * r90 · COLISIÓN BOLA↔MANO (informe del dueño: «¿qué pasa que la bola no
 * hace nada al atravesar o chocar con las manos? … al chocar por delante
 * o por detrás la bola se para y cae y la mano se destroza — en Clown con
 * Burla era muy similar y funcionaba perfectamente»): se PORTA EL MOTOR
 * DE BURLA (locura, probado en el casco) — (1) CCD por SEGMENTO
 * prev→actual subdividido a ≤3 cm (la bola NO atraviesa la mano por
 * rápida que venga: el test anterior medía un Bloque fino en el frame
 * exacto y se lo tragaba entre frames), (2) CAJA en el marco LOCAL de la
 * mano (su rotación Y hacia la cámara ya no mintiendo al test), (3) BANDA
 * DESDE LA MESA (antes el centro de la banda flotaba a +0,46 m y las
 * bolas de rallye pasaban por DEBAJO sin tocar nada), (4) al chocar la
 * bola SE PARA Y CAE (vel 0,−0.4,0 como Burla) y la mano REVIENTA.
 *
 * CINE EXACTO (sin montículo): la mano DESENROLLA desde la mesa (0,50 s,
 * easeOutCubic + sobresalto 7 %) → 2,00 s de vaivén siniestro → retracto
 * (0,50 s) → fundido (0,25 s). La bola que toca la mano queda PARADA y se
 * cae; la mano sale empujada y revienta en 6 trocitos. */
const MANO_CULTIVO = 1.0;    // r91: ARTE COMPLETO — el informe del dueño («no sale
                             // la parte inferior, la tierra y el brazo saliendo»)
                             // caza el cultivo 0.70 de la r90: la franja inferior
                             // del arte ES la tierra y el brazo (47-62 % de píxeles
                             // visibles medidos) y el dueño la QUIERE en pantalla
const MANO_OFF_Y = 0.0;      // r91: sin recorte — v cubre 0..1 entero
const MANO_GROSOR = 0.055;   // r90: semiespesor del plano mano (por delante Y por detrás)
/* r92 · MANO PEGADA A LA MESA (informe del dueño: «Las manos de los zombis
 * deben salir justa de la mesa de tal forma que su parte inferior toque la
 * mesa y no quede suspendida en el aire»): la base del plano SE ANCLA al
 * tablero en TODAS las fases — fuera el ascenso +0,12 y el vaivén vertical
 * de la r89 (eran los que dejaban la mano COLGANDO sobre la mesa). El
 * «nacer de abajo» sigue leyéndose: el plano DESENROLLA desde la mesa
 * (repeat.y 0→1 con la base fija) y la punta asciende al crecer; el
 * movimiento vivo queda en el vaivén de ROTACIÓN (pivote en la base) y en
 * la respiración de ESCALA (crece desde la base, la punta respira). */
const MANO_Y = 0.005;        // r92: base del plano a 5 mm del tablero (toca la mesa)

PLANTILLA_PODERES.mano = {
  inicio(game, p, ctrl, ctx) {
    /* r90: sin texMonticulo — el montículo SE RETIRA de la mesa */
    const M = { grupo: new THREE.Group(), vivos: [], trocitos: [], t: 0, prox: 0.35,
      tex: [], bolsa: [], pool: [], texTrozo: _texTerron(),
      prev: new THREE.Vector3(), prevOk: false };   // r90: CCD de Burla
    [1, 2, 3].forEach((i) => TEX_R86.pedir('mano' + i + '.webp', (t) => { M.tex.push(t); }));
    game.scene.add(M.grupo);
    ctx.mano = M;                       // r87: ctx ANTES de los callbacks
  },
  /* r89 · BOLSA de manos: las 3 del dueño SALEN SIEMPRE antes de repetir
   * (barajado Fisher-Yates por ciclo) — el dueño «no están saliendo todas». */
  _bolsa(M) {
    if (!M.tex.length) return null;
    if (!M.bolsa.length) {
      const b = M.tex.slice();
      for (let i = b.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [b[i], b[j]] = [b[j], b[i]]; }
      M.bolsa = b;
    }
    return M.bolsa.pop();
  },
  _spawn(game, M) {
    const cz = DIMS.tableCenterZ;
    const HW = (DIMS.tableHalfWidth != null) ? DIMS.tableHalfWidth : 0.7625;
    const HL = (DIMS.tableHalfLength != null) ? DIMS.tableHalfLength : 1.37;
    /* r90 · SIN MONTÍCULO: el radio de guardia es el de la MANO
     * (mitad del ancho 0,34 → 0,17, con margen) + el CANTO RUGOSO de la
     * losa (~7 cm pintados en el borde que NO son tablero jugable). */
    const MON = 0.17 + 0.03;   // r90: radio de la mano (antes, el montículo en pico 0,23·1,18)
    const BORDE = 0.07;        // el canto rugoso de la losa NO es tablero
    /* r89 · RANURAS DE MANO (informe del dueño: «tampoco deben solaparse
     * entre ellos deben estar siempre separados»): 3 posiciones repartidas
     * por la mesa (zigzag) cuya distancia mínima (1,08 m) supera la sepa-
     * ración exigida (0,62 m) AUN con jitter ±10 cm — separación POR
     * CONSTRUCCIÓN. Cada nacimiento toma la primera ranura LIBRE (sin
     * viva a menos de 0,62 m, y sin cortar el canto del tablero) en orden
     * barajado; si no hay ranura libre, la mano no nace (mejor ausente
     * que pisada). */
    const SLOTS = [[-0.30, -0.9], [0.30, 0.0], [-0.30, 0.9]];
    const orden = [0, 1, 2];
    for (let i = orden.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [orden[i], orden[j]] = [orden[j], orden[i]]; }
    let x = null, z = 0;
    for (const si of orden) {
      const cx2 = SLOTS[si][0] + rand(-0.1, 0.1);
      const cz2 = SLOTS[si][1] + rand(-0.1, 0.1);
      if (Math.abs(cx2) + MON + BORDE > HW || Math.abs(cz2) + MON + BORDE > HL) continue;   // canto: ni rozarlo
      let libre = true;
      for (const v of M.vivos) {
        const dx = cx2 - v.mano.position.x;
        const dz = (cz + cz2) - v.mano.position.z;   // r89: z ABSOLUTA en ambos lados (mezclar relativa/absoluta anulaba el chequeo)
        if (dx * dx + dz * dz < 0.62 * 0.62) { libre = false; break; }
      }
      if (libre) { x = cx2; z = cz + cz2; break; }
    }
    if (x == null) return;   // sin hueco separado: no nace
    const b = game.ball ? game.ball.pos : null;
    if (b && Math.abs(b.x - x) < 0.24 && Math.abs(b.z - z) < 0.24) return; // no nacer sobre la bola
    if (!M.tex.length) return;          // r90: sin requisito de montículo
    const baseTex = this._bolsa(M);
    if (!baseTex) return;
    const tex = _manoTexLibre(M, baseTex);
    const W = 0.34, HF = W * (885 / 512);
    // r90 · MANO vertical anclada a la MESA (el montículo plano se RETIRA:
    // el arte de la mano ya trae su tierra integrada y el solape de las
    // dos texturas CORTABA la mano en la línea de visión del dueño)
    const tex2 = tex; tex2.wrapT = THREE.ClampToEdgeWrapping;
    tex2.offset.y = MANO_OFF_Y; tex2.repeat.y = 0.001;   // r91: desenrolla el ARTE ENTERO desde la tierra (v 0 = la tierra)
    const geo = new THREE.PlaneGeometry(W, HF);
    geo.translate(0, HF / 2, 0);
    const mat = new THREE.MeshBasicMaterial({ map: tex2, transparent: true, alphaTest: 0.30, side: THREE.DoubleSide, depthWrite: false });
    const mano = new THREE.Mesh(geo, mat);
    /* r92 · base del plano EN LA MESA (MANO_Y): la parte inferior toca el
     * tablero desde el frame 1 y en TODAS las fases (nada suspendida). */
    mano.position.set(x, DIMS.tableTopY + MANO_Y, z);
    /* r90 · ORDEN DE PINTADO: mano 4 → trocitos 5 (ya sin capa de tierra
     * 3: nada que la corte). Sin depthWrite: el renderOrder decide. */
    mano.renderOrder = 4;
    try {
      const cam = game.camera;
      _v86.setFromMatrixPosition(cam.matrixWorld);
      mano.rotation.y = Math.atan2(_v86.x - x, _v86.z - z);
    } catch (e) { mano.rotation.y = Math.atan2(-x, 0.55 - z); }
    mano.scale.y = 0.001;
    M.grupo.add(mano);
    /* r89 · el dueño («seguimos sin mover la mano de abajo hacia arriba al
     * aparecer»): la mano ASIENDE 12 cm desde su nacimiento en la mesa;
     * v.y0 guarda el nivel de partida para bajar/fundir sobre él.
     * r90: fase inicial DIRECTAMENTE 'subir' (ya no hay pop de montículo). */
    M.vivos.push({ mano, tex: tex2, W, HF, fase: 'subir', t: 0, golpeada: false, vx: 0, vz: 0, va: 0, y0: mano.position.y });
  },
  _revienta(game, M, v, bola) {
    v.fase = 'golpeada'; v.t = 0;
    const dir = Math.atan2(v.mano.position.x - bola.x, v.mano.position.z - bola.z) || rand(0, 6.3);
    v.vx = Math.sin(dir) * rand(0.9, 1.5); v.vz = Math.cos(dir) * rand(0.9, 1.5);
    v.va = rand(-7, 7);
    for (let i = 0; i < 6; i++) {
      const geo = new THREE.PlaneGeometry(rand(0.04, 0.075), rand(0.04, 0.075));
      const mat = new THREE.MeshBasicMaterial({ map: M.texTrozo, transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, depthWrite: false });
      const m = new THREE.Mesh(geo, mat);
      m.renderOrder = 5;   // r88: los trocitos sobre mano y tierra
      m.position.copy(v.mano.position).add(_v86.set(rand(-0.1, 0.1), v.mano.scale.y * v.HF * rand(0.3, 0.9), rand(-0.05, 0.05)));
      M.grupo.add(m);
      M.trocitos.push({ mesh: m, vx: rand(-0.8, 0.8), vy: rand(0.9, 1.8), vz: rand(-0.5, 0.5), va: rand(-9, 9), vida: 0.55, t: 0 });
    }
  },
  paso(dt, game, p, ctrl, ctx) {
    const M = ctx.mano; if (!M) return;
    M.t += dt;
    if (M.t >= M.prox && M.tex.length && M.vivos.length < 3) {   // r90: sin requisito de montículo
      this._spawn(game, M);
      M.prox = M.t + rand(2.0, 2.5);
    }
    const bola = game.ball ? game.ball.pos : null;
    const r = DIMS.ballRadius;
    for (let i = M.vivos.length - 1; i >= 0; i--) {
      const v = M.vivos[i];
      v.t += dt;
      if (v.fase === 'subir') {
        // rápida que se FRENA al final (susto) — guion del dueño: 0,5 s
        const k = Math.min(1, v.t / 0.5);
        const e = 1 - Math.pow(1 - k, 3);
        v.mano.scale.y = Math.max(0.001, e);
        /* r92 · BASE FIJA EN LA MESA: nada de ascenso — la punta sube SOLO
         * porque el plano desenrolla (scale/repeat crecen desde la base). */
        v.mano.position.y = v.y0;
        const sobre = k < 0.24 ? (1 - k / 0.24) * 0.07 : 0;
        v.mano.scale.x = v.mano.scale.z = 1 + sobre;
        v.tex.repeat.y = Math.max(0.001, MANO_CULTIVO * e);   // r91: e→1 = arte completo (tierra + brazo + mano)
        if (k >= 1) { v.fase = 'arriba'; v.t = 0; }
      } else if (v.fase === 'arriba') {
        /* r92 · SIGUE TOCANDO LA MESA: el vaivén vivo es de ROTACIÓN
         * (pivote en la base) y de ESCALA (respira desde la base) — la
         * posición vertical NO se mueve (fuera el bob +0,12±0,012 de la
         * r89 que dejaba la mano suspendida en el aire). */
        v.mano.position.y = v.y0;
        v.mano.rotation.z = Math.sin(v.t * 3.1) * 0.05;           // vaivén siniestro (base fija)
        v.mano.scale.y = 1 + Math.sin(v.t * 4.7) * 0.015;         // respiración desde la base
        if (v.t >= 2.0) { v.fase = 'bajar'; v.t = 0; v.mano.rotation.z = 0; }
      } else if (v.fase === 'bajar') {
        const k = Math.min(1, v.t / 0.5);
        v.mano.scale.y = Math.max(0.001, 1 - k * k);
        v.mano.position.y = v.y0;   // r92: se ENROLLA hacia la mesa (base fija)
        v.tex.repeat.y = Math.max(0.001, MANO_CULTIVO * (1 - k * k));   // r91: se enrolla hasta la tierra
        if (k >= 1) { v.fase = 'fundir'; v.t = 0; }
      } else if (v.fase === 'fundir') {
        const op = Math.max(0, 1 - v.t / 0.25);
        v.mano.material.opacity = op;
        if (v.t >= 0.25) {
          M.grupo.remove(v.mano);
          v.mano.geometry.dispose(); v.mano.material.dispose();
          _manoTexSuelta(M, v.tex);
          M.vivos.splice(i, 1);
          continue;
        }
      } else if (v.fase === 'golpeada') {
        // mano empujada (tumba); trocitos por el aire
        /* r89 · el empujón NO saca la mano del tablero (norma: nada fuera
         * de la mesa, ni siquiera al reventar): se CLAMPEA al canto. */
        const HWg = (DIMS.tableHalfWidth != null) ? DIMS.tableHalfWidth : 0.7625;
        const HZg = (DIMS.tableHalfLength != null) ? DIMS.tableHalfLength : 1.37;
        const czG = DIMS.tableCenterZ;
        v.mano.position.x = clamp(v.mano.position.x + v.vx * dt, -(HWg - 0.18), HWg - 0.18);
        v.mano.position.z = clamp(v.mano.position.z + v.vz * dt, czG - HZg + 0.18, czG + HZg - 0.18);
        v.mano.rotation.z += v.va * dt;
        const op = Math.max(0, 1 - v.t / 0.4);
        v.mano.material.opacity = op;
        if (v.t >= 0.4) {
          M.grupo.remove(v.mano);
          v.mano.geometry.dispose(); v.mano.material.dispose();
          _manoTexSuelta(M, v.tex);
          M.vivos.splice(i, 1);
          continue;
        }
      }
      /* r90 · COLISIÓN BOLA↔MANO — MOTOR DE BURLA portado (probado en el
       * casco con el Clown). CCD por SEGMENTO (la bola NO atraviesa el
       * plano entre frames) + caja en el marco LOCAL de la mano (vale por
       * delante Y por detrás, con su rotación Y real) + banda DESDE LA
       * MESA (la bola de rallye vuela bajo: el test antiguo la perdía). */
      if (bola && !v.golpeada && (v.fase === 'subir' || v.fase === 'arriba') &&
          v.mano.scale.y > 0.3 && M.prevOk && game.rules && game.rules.state === 'rally') {
        const cur = bola;
        const prev = M.prev;
        const segx = cur.x - prev.x, segy = cur.y - prev.y, segz = cur.z - prev.z;
        const len = Math.sqrt(segx * segx + segy * segy + segz * segz);
        const pasos = Math.max(1, Math.ceil(len / 0.03));   // submuestreo ≤3 cm: sin túnel
        const ry = v.mano.rotation.y;
        const cy2 = Math.cos(ry), sy2 = Math.sin(ry);
        const topY = v.mano.position.y + v.mano.scale.y * v.HF + r;
        const semiancho = v.W * 0.5 + r * 0.8;
        const semiesp = MANO_GROSOR + r * 0.8;
        for (let s2 = 1; s2 <= pasos; s2++) {
          const f = s2 / pasos;
          const px = prev.x + segx * f, py = prev.y + segy * f, pz = prev.z + segz * f;
          if (py < DIMS.tableTopY - 0.02 || py > topY) continue;      // banda desde la MESA hasta la punta
          const wx = px - v.mano.position.x, wz = pz - v.mano.position.z;
          const lx = cy2 * wx - sy2 * wz;                             // local = R(−ry)·mundo
          const lz = sy2 * wx + cy2 * wz;
          if (Math.abs(lx) < semiancho && Math.abs(lz) < semiesp) {
            v.golpeada = true;
            /* Burla (probado): la bola SE PARA y cae muerta en el sitio.
             * r90 · BUG RAÍZ CAZADO: «bola» aquí es game.ball.POS (un
             * Vector3) — el código anterior (r87/89) llamaba bola.vel.set
             * sobre el VECTOR DE POSICIÓN: TypeError tragado por el catch
             * del motor → la mano quedaba marcada pero NADA pasaba («la
             * bola no hace nada»). La velocidad vive en game.ball.vel. */
            if (game.ball.vel) game.ball.vel.set(0, -0.4, 0);
            if (game.ball.spin) game.ball.spin.multiplyScalar(0.15);
            try {
              game.audio.paddle(clamp(bola.x / 2.5, -1, 1), 0.4);
              game.audio.playNoise(0.20, 900, 0.55, 0.16, 0);          // crujido seco de la mano
              game.audio.playOsc(220, 60, 0.28, 'square', 0.12, 0);
            } catch (e) { /* */ }
            try { if (game.renderer.xr.isPresenting) game.haptic(game.paddleHand, 0.6, 90); } catch (e) { /* */ }
            try { ctrl.fxPop(v.mano.position); } catch (e) { /* */ }
            this._revienta(game, M, v, bola);
            break;
          }
        }
      }
    }
    /* r90 · memoria del segmento bola (anti-túnel del próximo frame) —
     * patrón exacto de Burla (_burlaPrevV) */
    if (bola) { M.prev.copy(bola); M.prevOk = true; }
    for (let i = M.trocitos.length - 1; i >= 0; i--) {
      const tr = M.trocitos[i];
      tr.t += dt;
      tr.vy -= 5.5 * dt;
      tr.mesh.position.x += tr.vx * dt; tr.mesh.position.y += tr.vy * dt; tr.mesh.position.z += tr.vz * dt;
      tr.mesh.rotation.z += tr.va * dt;
      tr.mesh.material.opacity = Math.max(0, 1 - tr.t / tr.vida);
      if (tr.t >= tr.vida) {
        M.grupo.remove(tr.mesh); tr.mesh.geometry.dispose(); tr.mesh.material.dispose();
        M.trocitos.splice(i, 1);
      }
    }
  },
  fin(game, p, ctrl, ctx) {
    const M = ctx && ctx.mano; if (!M) return;
    M.vivos.forEach((v) => {
      try { v.mano.geometry.dispose(); v.mano.material.dispose(); } catch (e) { /* */ }
      _manoTexSuelta(M, v.tex);
    });
    M.trocitos.forEach((tr) => { tr.mesh.geometry.dispose(); tr.mesh.material.dispose(); });
    M.pool.forEach((t) => { try { t.dispose(); } catch (e) { /* */ } });
    game.scene.remove(M.grupo);
    ctx.mano = null;
  },
};

/* -- 2 · PLAGA DE MOSCAS (r87 · «más trabajadas, aleteo, zumbido, más
 * cantidad y calidad» — informe del dueño) -------------------------------
 * r89 · EL DOBLE de moscas (48): el dueño («colocar el doble de las
 * actuales»). Sigue siendo 1 draw call por sprite y las texturas ya
 * están subidas (pool del TEX_R86) — coste despreciable en el Quest.
 * 48 moscas de 2 FRAMES de aleteo (mosca_a/mosca_b, alternancia ~22 Hz con
 * fase propia), órbitas elípticas con deriva y dardos ocasionales, ZUMBIDO
 * de enjambre en bucle (createBucle + fly_buzz.mp3) y espantado con la
 * pala (proximidad real del mando) — igual que confetti de Clown, pero
 * vivo. */
PLANTILLA_PODERES.moscas = {
  inicio(game, p, ctrl, ctx) {
    const S = { grupo: new THREE.Group(), moscas: [], t: 0, texA: null, texB: null, bucle: null };
    S.grupo.position.set(0, -0.045, -0.44);
    try { game.camera.add(S.grupo); } catch (e) { game.scene.add(S.grupo); }
    ctx.moscas = S;                     // r87: ctx ANTES de los callbacks
    const nace = () => {
      if (!S.texA || !S.texB || S.moscas.length) return;
      for (let i = 0; i < 48; i++) {   // r89: el doble (informe del dueño)
        const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: S.texA, transparent: true, depthWrite: false }));
        const esc = rand(0.026, 0.055);
        s.scale.set(esc, esc * 0.82, 1);
        s.userData.r87 = {
          radio: rand(0.07, 0.26), fase: rand(0, 6.3),
          vel: rand(0.8, 1.9) * (Math.random() < 0.5 ? 1 : -1),
          bob: rand(0.25, 0.7), aleteo: rand(0, 6.3), aleteoV: rand(17, 26),
          dart: rand(1.5, 4.0), dartT: 0, cx: 0, cy: 0, cz: 0,
          muerta: 0, fx: 0, fy: 0,
        };
        S.grupo.add(s);
        S.moscas.push(s);
      }
    };
    TEX_R86.pedir('mosca_a.webp', (t) => { S.texA = t; nace(); });
    TEX_R86.pedir('mosca_b.webp', (t) => { S.texB = t; nace(); });
    // ZUMBIDO del enjambre (bucle del SDK, perfil de audio probado)
    try {
      S.bucle = createBucle(() => game, { url: () => A('fly_buzz.mp3'), vol: () => 0.34, fadeIn: 0.15, stopFade: 0.3 });
      S.bucle.on();
    } catch (e) { S.bucle = null; }
  },
  paso(dt, game, p, ctrl, ctx) {
    const S = ctx.moscas; if (!S) return;
    S.t += dt;
    const pad = game.controllerPaddles ? game.controllerPaddles[(game.paddleHand | 0) || 0] : null;
    for (let i = S.moscas.length - 1; i >= 0; i--) {
      const s = S.moscas[i];
      const u = s.userData.r87;
      if (u.muerta > 0) {
        u.muerta -= dt;
        s.position.x += u.fx * dt; s.position.y += u.fy * dt;
        s.material.opacity = Math.max(0, u.muerta / 0.35);
        if (u.muerta <= 0) { S.grupo.remove(s); s.material.dispose(); S.moscas.splice(i, 1); }
        continue;
      }
      // ALETEO: 2 frames alternando con fase propia (~20 Hz, se ve vivo)
      u.aleteo += dt * u.aleteoV;
      const frame = (Math.floor(u.aleteo) & 1) ? S.texB : S.texA;
      if (s.material.map !== frame) { s.material.map = frame; s.material.needsUpdate = true; }
      // DARDOS: cada 1,5-4 s la mosca re-centra su órbita (enjambre vivo)
      u.dartT += dt;
      if (u.dartT >= u.dart) {
        u.dartT = 0; u.dart = rand(1.5, 4.0);
        u.cx = rand(-0.05, 0.05); u.cy = rand(-0.03, 0.04); u.cz = rand(-0.04, 0.04);
      }
      const a = u.fase + S.t * u.vel;
      s.position.x = u.cx + Math.cos(a) * u.radio;
      s.position.y = u.cy + Math.sin(a * 1.6) * 0.05 + Math.sin(S.t * u.bob + u.fase) * 0.035;
      s.position.z = u.cz + Math.sin(a) * u.radio * 0.55;
      if (pad && pad.pos) {
        s.getWorldPosition(_v86);
        if (_v86.distanceTo(pad.pos) < 0.16) {          // ¡espantada con la pala!
          u.muerta = 0.35;
          const inv = 1 / (Math.hypot(s.position.x, s.position.z) || 1);
          u.fx = s.position.x * inv * rand(1.2, 2.4);
          u.fy = rand(0.4, 1.0);
          ctrl.fxPop(_v86);
          try { game.audio.playOsc(520 + Math.random() * 260, 180, 0.06, 'sawtooth', 0.05, 0); } catch (e) { /* */ }
        }
      }
    }
  },
  fin(game, p, ctrl, ctx) {
    const S = ctx && ctx.moscas; if (!S) return;
    if (S.bucle) { try { S.bucle.off(); } catch (e) { /* */ } S.bucle = null; }
    S.moscas.forEach((s) => s.material.dispose());
    try { game.camera.remove(S.grupo); } catch (e) { /* */ }
    try { game.scene.remove(S.grupo); } catch (e) { /* */ }
    ctx.moscas = null;
  },
};

/* -- 3 · CALABAZA (r90 · cuerpo PROCEDURAL DE LA CASA desde el frame 1) --
 * «La calabaza sigue sin verse, o lo solucionamos si se puede o tenemos
 * que buscar otra forma de hacerlo» (informe del dueño tras V3.6.81).
 * La forma: el cuerpo ES la calabaza procedural de la casa (lathe con
 * costillas + rabo + zarcillo — el pipeline del trofeo del Hall, probado
 * en el casco) y nace EN EL INSTANTE del disparo. El GLB de Sketchfab se
 * retira del runtime: «cargaba» pero nunca se pintaba en el casco, y al
 * marcarse «listo» al cargar bloqueaba el respaldo — bola oculta y
 * «no se puede jugar». Sin GLB no hay espera de cuerpo (el aviso vuelve
 * a su ritmo normal de 2 s) ni swap ni estados intermedios. */

/* -- r88 · cuerpo de calabaza POR INSTANCIA: clona los materiales (la
 * pudrición tiñe SOLO su copia — el caché queda intacto) y guarda el
 * color original de cada uno. Devuelve los registros para paso(). */
const _PODRE_R88 = new THREE.Color(0x3a2b12);
function _preparaCuerpoR88(raiz) {
  const mats = [];
  try {
    raiz.traverse((o) => {
      if (!o.isMesh || !o.material) return;
      /* r91b · EL FALLO QUE ESCONDE EL CUERPO (cazado con THREE r186 delante):
       * esta función convertía material SIEMPRE en ARRAY ([clon]) — y el
       * renderer (projectObject) con material-array SÓLO dibuja los
       * geometry.groups: LatheGeometry (el CUERPO) y TorusGeometry (el
       * zarcillo) NO TIENEN grupos → CERO draw calls → «la calabaza sólo
       * enseña el rabito» (CylinderGeometry SÍ trae grupos: el rabo era lo
       * único vivo — síntoma EXACTO del informe del dueño). FIX: material
       * único vuelve SINGLE; el array sólo si el mesh YA era multi-material. */
      const eraArray = Array.isArray(o.material);
      const origs = eraArray ? o.material : [o.material];
      const clonados = origs.map((mm) => {
        const c = mm.clone();
        mats.push({
          m: c,
          col: c.color ? c.color.clone() : new THREE.Color(0xe8720c),
          emis: (c.emissive && mm.emissive) ? mm.emissive.clone() : null,
          podre: _PODRE_R88,
        });
        return c;
      });
      o.material = eraArray ? clonados : clonados[0];
    });
  } catch (e) { /* */ }
  return mats;
}

PLANTILLA_PODERES.calabaza = {
  inicio(game, p, ctrl, ctx) {
    /* r89 · INFORME DEL DUEÑO («un problema con el peso que para evitar
     * problemas no lo vamos a modificar y queda con el estándar de la
     * bola»): la gravedad ×2.1 de la r86/87 se RETIRA — física de bola
     * ESTÁNDAR; la calabaza ES la bola con otro aspecto.
     * r90 · CUERPO GARANTIZADO DESDE EL FRAME 1: la calabaza procedural
     * de la casa nace EN EL DISPARO — la bola JAMÁS sin cuerpo, sin
     * esperas de GLB, sin fallbackT ni swap.
     * r92 · MARCA ppCalabaza EN LA BOLA: el núcleo (OpponentAI) la lee
     * para ACERCAR el contacto de su pala a la calabaza (Ø 13 cm — con el
     * alcance genérico de 21 cm la pala parecía golpear BESIDE/DESPLEGA-
     * DA: «el rival no la golpea correctamente con su pala parece que
     * tiene un desplazamiento»). La marca viaja en la bola y se limpia
     * en el estallido y en fin() — el resto del rallye queda intacto. */
    const C = { gltf: null, t: 0, listo: true, esProc: true, explotada: false, mats: [], dur: p.duration || 10 };
    ctx.calabaza = C;                   // r87: ANTES del callback (era el bug)
    C.gltf = _calabazaProcedural().clone(true);
    C.mats = _preparaCuerpoR88(C.gltf);
    /* r94 · NACIMIENTO EN EL LUGAR EXACTO DE LA BOLA: antes la calabaza se
     * añadía al origen (0,0,0) y no viajaba hasta el primer paso() — un
     * frame entera en el suelo. Copia INMEDIATA de la posición renderizada. */
    if (game.ballMesh) C.gltf.position.copy(game.ballMesh.position);
    else if (game.ball) C.gltf.position.copy(game.ball.pos);
    game.scene.add(C.gltf);
    if (game.ball) game.ball.ppCalabaza = true;         // r92: contacto de la IA pegado a la calabaza
    if (game.ballMesh) game.ballMesh.visible = false;   // la calabaza ES la bola
  },
  paso(dt, game, p, ctrl, ctx) {
    const C = ctx.calabaza; if (!C) return;
    C.t += dt;
    const b = game.ball; if (!b) return;
    /* r88 · ESTALLIDO FINAL (guion del dueño: «se va oscureciendo
     * (pudriendo) hasta que, cuando está a punto de desaparecer, la
     * calabaza ya podrida explota en trozos y desaparece, con un sonido
     * de CHOFFF»). El estallido va 0,55 s antes del cierre y la bola
     * normal VUELVE en ese instante — nunca calabaza y bola a la vez. */
    if (!C.explotada && C.t >= C.dur - 0.55) {
      C.explotada = true;
      if (b) b.ppCalabaza = false;            // r92: bola normal → contacto de IA normal
      if (C.gltf) C.gltf.visible = false;
      if (game.ballMesh) game.ballMesh.visible = true;
      _chofff(game, b.pos.x);
      for (let i = 0; i < 12; i++) _trozoAl(game, b.pos, new THREE.Color(0xe8720c), new THREE.Color(0x4a3512));
      try { ctrl.fxPop(b.pos); } catch (e) { /* */ }
    }
    if (C.explotada) return;
    /* r94 · INFORME DEL DUEÑO («se ve por un lado la calabaza y por otro la
     * bola… la calabaza debería ocupar el lugar exacto de la bola y esta no
     * verse mientras tengamos la calabaza sin destruir») — DOS garantías
     * duras, cada frame, para TODOS los caminos del núcleo:
     * (1) LA BOLA JAMÁS SE VE mientras la calabaza vive: el núcleo re-enseña
     *     ballMesh en varios sitios (toss del saque c12:4417, HELD del saca-
     *     dor c12:8774, reset de punto c12:1132, tránsitos/restauraciones
     *     c12:6316/10195) y el módulo sólo la ocultaba UNA VEZ en inicio().
     *     Ahora paso() la vuelve a ocultar DESPUÉS de esos caminos y ANTES
     *     del render — ver bola y calabaza a la vez es imposible.
     * (2) EL LUGAR EXACTO: la calabaza copia la posición RENDERIZADA de la
     *     bola (ballMesh.position, que el núcleo sincroniza de ball.pos en
     *     este mismo frame) — bit a bit con donde la bola estaría pintada,
     *     inmune a interpolaciones, HELD o caminos especiales.
     * (3) GUARD r92: si el núcleo recrea el objeto bola entre puntos, la
     *     marca ppCalabaza (contacto de la IA pegado a la calabaza) renace
     *     aquí — nunca caduca a mitad del poder. */
    if (game.ballMesh) game.ballMesh.visible = false;
    if (b) b.ppCalabaza = true;
    if (C.gltf) {
      /* r88 · LA CALABAZA ES LA BOLA: centrada en su centro EXACTO.
       * r92 · GIRO SOBRE SÍ MISMA AL GOLPEARLA (informe del dueño: «La
       * calabaza debería girar sobre si misma al golpearla tal como haría
       * la bola»): el quaternion de la bola (r88) apenas se APRECIABA en
       * un cuerpo de 13 cm (la bola suma spin·dt·0,05 — medio giro por
       * segundo y la superficie de la calabaza apenas se mueve). La cala-
       * bazas lleva SU rotación propia ARRASTRADA POR EL SPIN de la bola
       * a ritmo de cuerpo grande (×3 el factor visual de la bola — misma
       * sensación de rodadura en su tamaño): cada golpe CAMBIA el spin
       * (el remate liftado, el push cortado, el saque) y la calabaza
       * REARANCA su vuelta sobre sí misma en el acto — se la ve girar al
       * golpearla, como haría la bola.
       * r94 · POSICIÓN = bola RENDERIZADA (ver garantía (2) arriba). */
      C.gltf.position.copy(game.ballMesh ? game.ballMesh.position : b.pos);
      const sp = b.spin || null;
      if (sp) {
        C.gltf.rotation.x += sp.x * dt * 0.15;
        C.gltf.rotation.y += sp.y * dt * 0.15;
      }
    }
    /* r88 · PUDRICIÓN: el arte se oscurece linealmente hasta el estallido */
    const k = clamp(C.t / Math.max(0.1, C.dur - 0.55), 0, 1);
    for (const rec of C.mats) {
      if (rec.m.color) rec.m.color.copy(rec.col).lerp(rec.podre, k);
      if (rec.m.emissive && rec.emis) rec.m.emissive.copy(rec.emis).multiplyScalar(1 - k * 0.8);
    }
  },
  fin(game, p, ctrl, ctx) {
    const C = ctx && ctx.calabaza; if (!C) return;
    /* r89: SIN gravedad que restaurar — la física de la bola JAMÁS se toca
     * (peso estándar, decisión del dueño)
     * r92: la marca ppCalabaza se LIMPIA (contacto de la IA de vuelta a la
     * norma genérica de la bola) */
    if (game.ball) game.ball.ppCalabaza = false;
    if (game.ballMesh) game.ballMesh.visible = true;
    if (C.gltf) {
      game.scene.remove(C.gltf);
      /* r88/r90: los MATERIALES son clon por instancia (pudrición) →
       * dispose SIEMPRE; las GEOMETRÍAS son del caché de la casa (clon del
       * template procedural) y NO se tocan — re-subida cero al próximo uso. */
      C.gltf.traverse((o) => {
        if (o.isMesh) {
          if (o.material) { const ms = Array.isArray(o.material) ? o.material : [o.material]; ms.forEach((mm) => { try { mm.dispose(); } catch (e) { /* */ } }); }
        }
      });
    }
    ctx.calabaza = null;
  },
};

/* -- 4 · GELATINA ASQUEROSA (r88 · guion del dueño, reescrita) --------
 * «las manchas se deben repartir siempre por dentro de la mesa y nunca
 * tener alguna parte fuera de ella» (límite por radio CIRCUNSCRITO del
 * cuadrado girado). «Si la bola golpea alguna mancha, sonido de CHOFFF,
 * se convierte en bola verde fosforito y cuando bota en la mesa o en la
 * pala lanza una explosión de humo verde que dificulta mucho la visión.
 * Su peso NO varía: física de la bola normal» — la r87 la pesaba ×3:
 * RETIRADO (la bola se juega igual; sólo cambia el aspecto y el humo). */
PLANTILLA_PODERES.gelatina = {
  inicio(game, p, ctrl, ctx) {
    const G = { manchas: [], humo: [], t: 0, humoT: 0, humoT2: 0.12, humoIdx: 0, contaminada: false, col0: 0, emis0: 0, expT: 0, prevVy: 0 };
    ctx.gelatina = G;                   // r87: ANTES del callback (era el bug)
    TEX_R86.pedir('gelatina.webp', (t) => {
      if (!ctx.gelatina || G.manchas.length) return;
      const cz = DIMS.tableCenterZ;
      const HW = (DIMS.tableHalfWidth != null) ? DIMS.tableHalfWidth : 0.7625;
      const HL = (DIMS.tableHalfLength != null) ? DIMS.tableHalfLength : 1.37;
      /* r89 · CANTO RUGOSO de la losa: el borde pintado de la textura (~7 cm)
       * no es tablero — las manchas no lo pisan ni lo tocan. Verificación
       * por radio CIRCUNSCRITO del cuadrado girado (tam/2·√2) + canto. */
      const BORDE = 0.07;
      /* r89 · COLOCACIÓN EN ZIGZAG (informe del dueño: «algunas salen
       * parcialmente fuera… ni tampoco deben solaparse, debemos asegurar
       * que aparecen separadas entre ellas sin tocarse»): 5 RANURAS a lo
       * largo de la mesa alternando x — la distancia mínima entre ranuras
       * (0,57 m) supera el peor contacto visible de dos manchas grandes
       * (2·0,38·0,42 = 0,32 m) AUN con jitter de ±5 cm: separación POR
       * CONSTRUCCIÓN, no por suerte; y el canto (|x|≤0,25+0,34 < 0,7625;
       * |z|≤0,82+0,34 < 1,37) jamás se pisa. */
      for (let i = 0; i < 5; i++) {
        const tam = rand(0.26, 0.38);
        const geo = new THREE.PlaneGeometry(tam, tam);
        const mat = new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: 0.94, depthWrite: false });
        const m = new THREE.Mesh(geo, mat);
        m.rotation.x = -Math.PI / 2;
        m.rotation.z = rand(0, Math.PI * 2);
        m.userData.tam = tam;                        // r89: zona de impacto REAL
        const rx = -0.2 + (i % 2) * 0.4 + rand(-0.05, 0.05);
        const rz = -0.82 + i * 0.41 + rand(-0.05, 0.05);
        if (Math.abs(rx) + (tam / 2) * 1.4142 + 0.012 + BORDE > HW ||
            Math.abs(rz) + (tam / 2) * 1.4142 + 0.012 + BORDE > HL) continue;   // canto: la mancha NO nace
        // UN POCO POR ENCIMA DE LA MESA (guion del dueño) — escalonado
        m.position.set(rx, DIMS.tableTopY + 0.006 + i * 0.0012, cz + rz);
        game.scene.add(m);
        G.manchas.push(m);
      }
    });
  },
  paso(dt, game, p, ctrl, ctx) {
    const G = ctx.gelatina; if (!G) return;
    G.t += dt;
    G.expT = Math.max(0, G.expT - dt);
    // respiración sutil de las manchas (vivas, pegajosas)
    for (let i = 0; i < G.manchas.length; i++) {
      G.manchas[i].material.opacity = 0.90 + Math.sin(G.t * 2.4 + i * 1.7) * 0.06;
    }
    /* r90 · HUMILLO CONTINUO DESDE LAS MANCHAS (informe del dueño: «mientras
     * dure el efecto desde las texturas esté saliendo el humillo verde
     * fosforito continuamente mientras está el poder activo»): cada mancha
     * echa SU humillo por turnos (~6 efluvios/s repartidos) durante TODA la
     * duración del poder — independientemente de que la bola esté contami-
     * nada. Sprites del mismo pool _texHumo, vida 1,25 s, tope 70 vivos:
     * coste despreciable (≤9 sprites vivos por mancha en el peor caso). */
    G.humoT2 -= dt;
    if (G.humoT2 <= 0 && G.manchas.length && G.humo.length < 70) {
      G.humoT2 = 0.16;
      G.humoIdx = (G.humoIdx + 1) % G.manchas.length;
      const mancha = G.manchas[G.humoIdx];
      const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: _texHumo(), transparent: true, opacity: 0.46, depthWrite: false }));
      s.position.set(mancha.position.x + rand(-0.05, 0.05), mancha.position.y + 0.012, mancha.position.z + rand(-0.05, 0.05));
      s.scale.set(0.07, 0.07, 1);
      game.scene.add(s);
      G.humo.push({ s, vida: 1.25, t: 0, vy: rand(0.10, 0.18), s0: 0.07, s1: 0.20, op0: 0.46 });
    }
    const b = game.ball; const r = DIMS.ballRadius;
    if (!G.contaminada && b && b.pos.y - r <= DIMS.tableTopY + 0.06) {
      for (const m of G.manchas) {
        /* r90 · ZONA DE IMPACTO = LA MANCHA EXACTA (informe del dueño: «da
         * la sensación de que existe un desfase entre la posición de la
         * textura y la zona de colisión»): el test anterior era un CÍRCULO
         * salado (tam·0,42) que ni cubría las esquinas del cuadrado visual
         * ni respetaba su giro. Ahora el punto de la bola se lleva al
         * marco LOCAL de la mancha (quaternion inverso — vale con su
         * rotación Z aleatoria) y se prueba contra el CUADRADO visual
         * entero (tam/2 + holgura de 3/4 de bola): si la bola toca la
         * textura, MANCHA; si no la toca, no. Cero desfase posible. */
        const lim = (m.userData.tam || 0.3) * 0.5 + r * 0.75;
        _q86.copy(m.quaternion).invert();
        _v86.copy(b.pos).sub(m.position).applyQuaternion(_q86);
        if (Math.abs(_v86.x) <= lim && Math.abs(_v86.y) <= lim) {
          G.contaminada = true;
          /* r88 · FÍSICA INTACTA (el dueño: «su peso no varía, tendrá la
           * física de la bola normal») — la r87 la pesaba ×3 y la frenaba:
           * RETIRADO. Sólo cambia el ASPECTO + el humo. */
          const mesh = game.ballMesh;
          if (mesh && mesh.material) {
            G.col0 = mesh.material.color.getHex();
            G.emis0 = mesh.material.emissive ? mesh.material.emissive.getHex() : 0;
            mesh.material.color.setHex(0x39ff14);                  // verde fosforito
            if (mesh.material.emissive) mesh.material.emissive.setHex(0x1f8f0a);
          }
          _chofff(game, b.pos.x);                                  // «CHOFFF»
          ctrl.fxPop(b.pos);
          break;
        }
      }
    }
    if (G.contaminada && b) {
      /* r88 · HUMO VERDE AL BOTAR (el dueño: «cuando bota en la mesa o en
       * la pala lanza una explosión de humo verde que dificulta mucho la
       * visión»): bote en MESA = invierte vy sobre la mesa; bote en PALA =
       * contacto del mando con velocidad. Ráfaga densa y lenta (global:
       * sobrevive al cierre del poder y se disipa sola). */
      const sobreMesa = Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.03 &&
        Math.abs(b.pos.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength + 0.03;
      /* r89 · BOTES MÁS PERCEPTIBLES: el umbral de 0,5 m/s dejaba sin humo
       * los botes suaves (el dueño no veía el efecto «al botar con pala y
       * con mesa») — 0,25 m/s cubre el bote normal de juego. */
      const boteMesa = sobreMesa && G.prevVy < -0.25 && b.vel.y > 0.25;
      let botePala = false;
      const pad = game.controllerPaddles ? game.controllerPaddles[(game.paddleHand | 0) || 0] : null;
      if (pad && pad.pos) {
        const dp = pad.pos.distanceTo(b.pos);
        const vp = pad.velocity ? pad.velocity.length() : 0;
        if (dp < 0.13 + r && vp > 0.4) botePala = true;
      }
      if ((boteMesa || botePala) && G.expT <= 0) {
        G.expT = 0.42;
        _humoVerdeR88(game, b.pos, 22);   // r89: ráfaga más densa (visibilidad)
        try { ctrl.fxPop(b.pos); } catch (e) { /* */ }
      }
      G.prevVy = b.vel.y;
      // humillo verde fosforito que se desvanece (estela ligera)
      G.humoT -= dt;
      if (G.humoT <= 0) {
        G.humoT = 0.075;
        const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: _texHumo(), transparent: true, opacity: 0.62, depthWrite: false }));
        s.position.set(b.pos.x + rand(-0.01, 0.01), b.pos.y + 0.02, b.pos.z + rand(-0.01, 0.01));
        s.scale.set(0.05, 0.05, 1);
        game.scene.add(s);
        G.humo.push({ s, vida: 0.55, t: 0, vy: rand(0.16, 0.24), s0: 0.05, s1: 0.14, op0: 0.62 });
      }
    }
    for (let i = G.humo.length - 1; i >= 0; i--) {
      const h = G.humo[i];
      h.t += dt;
      h.s.position.y += h.vy * dt;
      const k = h.t / h.vida;
      h.s.scale.setScalar(h.s0 + k * (h.s1 - h.s0));
      h.s.material.opacity = Math.max(0, h.op0 * (1 - k));
      if (h.t >= h.vida) { game.scene.remove(h.s); h.s.material.dispose(); G.humo.splice(i, 1); }
    }
  },
  fin(game, p, ctrl, ctx) {
    const G = ctx && ctx.gelatina; if (!G) return;
    /* r88: sin gravedad que restaurar — la física JAMÁS se tocó */
    const mesh = game.ballMesh;
    if (mesh && mesh.material && G.col0) {
      mesh.material.color.setHex(G.col0);
      if (mesh.material.emissive) mesh.material.emissive.setHex(G.emis0);
    }
    G.manchas.forEach((m) => { game.scene.remove(m); m.geometry.dispose(); m.material.dispose(); });
    G.humo.forEach((h) => { game.scene.remove(h.s); h.s.material.dispose(); });
    /* las RÁFAGAS de humo viven en TROZOS_R88 (global): mueren solas o en
     * parar()/dispose() — «cuando el poder cesa desaparece y aparece la
     * bola normal» (la bola ya está restaurada aquí arriba). */
    ctx.gelatina = null;
  },
};
class PlantillaPoderes {
  constructor(ctrl, game, man) {
    this.ctrl = ctrl; this.game = game; this.man = man;
    this.T = Object.assign({
      chance: 0.32, cooldown: 13.0, minRallyHits: 1, warn: 2.0,
      bolsa: 'rotatoria', primerCd: 6, garantiaS: 22, postCdMin: 10, postCdMax: 15,
    }, man.powerTrigger || {});
    this.lista = (man.powers || []).filter((p) => PLANTILLA_PODERES[p.kind]);
    this.bag = []; this.lastKind = null;
    this.cd = this.T.primerCd; this.pendT = 0; this.pend = null;
    this.powerT = 0; this.activo = null; this.ctx = {};
    this.garantiaT = this.T.garantiaS; this.rallyFired = false;
    this.sign = createPowerSign(THREE, () => game, {
      coreo: 'v240', halo: true, arte: 'fit1833',
      url: () => A('superpower.webp'),
      // r87 · INFORME DEL DUEÑO («no aparece el cartel de superpoder»): sin
      // dims el anclaje se saltaba y el cartel nacía en el ORIGEN del rig
      // (a los pies, bajo el frustum). Con dims: sobre la red como los
      // otros 4 campeonatos (locura/orbital pasan lo mismo).
      dims: () => (DIMS ? { netTopY: DIMS.netTopY, tableCenterZ: DIMS.tableCenterZ } : null),
    });
    this.sign.build();
    // r87: precarga de TODOS los assets de superpoderes (manos, moscas 2
    // frames y gelatina) para que el primer disparo ya salga vestido — y
    // sin subidas a GPU a mitad de partida (r90: el montículo SE RETIRA)
    ['mano1.webp', 'mano2.webp', 'mano3.webp', 'mosca_a.webp', 'mosca_b.webp', 'gelatina.webp'].forEach((n) => TEX_R86.pedir(n, () => {}));
    // r87 · PREWARM DE SHADERS (anti-trompicones): los materiales de los
    // poderes nacen a mitad de partida y su 1.ª compilación GLSL da un tirón
    // en el casco. Aquí se compilan UNA VEZ, tras el telón, con dummies que
    // se retiran en el mismo instante (renderer.compile cachea los programas).
    try {
      const warm = [];
      const push = (m) => {
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(0.01, 0.01), m);
        mesh.position.set(0, -50, 0);
        game.scene.add(mesh); warm.push(mesh);
      };
      push(new THREE.MeshBasicMaterial({ transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, depthWrite: false }));
      push(new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false }));
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
      sp.position.set(0, -50, 0);
      game.scene.add(sp); warm.push(sp);
      game.renderer.compile(game.scene, game.camera);
      for (const w of warm) {
        game.scene.remove(w);
        if (w.geometry) w.geometry.dispose();
        if (w.material) w.material.dispose();
      }
    } catch (e) { /* el prewarm nunca rompe */ }
  }
  _elegir() {
    if (this.T.bolsa === 'rotatoria') {
      if (!this.bag.length) { this.bag = this.lista.slice(); for (let i = this.bag.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [this.bag[i], this.bag[j]] = [this.bag[j], this.bag[i]]; } }
      return this.bag.shift();
    }
    const cands = this.lista.filter((p) => p.kind !== this.lastKind);
    return pick(cands.length ? cands : this.lista);
  }
  disparar() {
    if (!this.lista.length || this.pendT > 0 || this.powerT > 0 || this.cd > 0) return;
    const p = this._elegir(); if (!p) return;
    this.lastKind = p.kind; this.pend = p;
    const warn = p.warn != null ? p.warn : this.T.warn;
    /* r90 · CALABAZA SIN ESPERA DE CUERPO: el cuerpo ES el procedural de
     * la casa (LatheGeometry, pipeline del trofeo del Hall) y nace EN EL
     * DISPARO — el aviso vuelve a su ritmo normal (warn) para los CUATRO
     * poderes; se retira la congelación extra de 6 s de la r89 (existía
     * SÓLO para esperar el GLB) y el swap in situ. */
    try { congela(this.game, Math.max(this.sign.T_OUT || 1.9, warn) + 0.1); } catch (e) {}
    this.sign.show(p.icon ? A(String(p.icon).replace(/^assets\//, '')) : A('superpower.webp'));
    if (this.ctrl.rival) this.ctrl.rival._set('crazy', warn + 1.2);
    /* r89/r90 · SONIDO DEL ZOMBI AL LANZAR UN SUPERPODER (zombi_crazy.mp3
     * del dueño) — r90: por el MOTOR PROBADO en el casco (createBucle) */
    if (SFX) SFX.play('crazy', 0.62);
    this.ctrl.haptic(0.6, 200);
    this.pendT = warn;
  }
  _lanzar() {
    if (!this.pend) { this.pendT = 0; return; }   // r86: robustez — nada de disparos fantasma
    const st = this.game.rules.state;
    if (st === 'over' || this.ctrl.pruebaActiva()) { this.cd = 3; this.pend = null; return; }
    const p = this.pend; this.pend = null;
    const impl = PLANTILLA_PODERES[p.kind]; if (!impl) return;
    this.activo = p; this.ctx = { globos: null, bola: null };
    try { impl.inicio(this.game, p, this.ctrl, this.ctx); } catch (e) {}
    this.powerT = p.duration || 8;
    this.cd = Math.max(4, (this.ctrl.curvaVigente() && this.ctrl.curvaVigente().cooldown) || p.cooldown || this.T.cooldown);
    this.rallyFired = true;
  }
  _cerrar() {
    const p = this.activo; if (!p) return;
    const impl = PLANTILLA_PODERES[p.kind];
    try { if (impl && impl.fin) impl.fin(this.game, p, this.ctrl, this.ctx); } catch (e) {}
    this.activo = null; this.powerT = 0;
    this.cd = rand(this.T.postCdMin, this.T.postCdMax);
    this.rallyFired = false;
  }
  update(dt, ctxR) {
    _pasoTrozosR88(dt, this.game);      // r88: trozos de calabaza + ráfagas de humo viven FUERA del poder
    this.sign.update(dt);
    const r = ctxR || this.game.rules || {};
    if (this.activo) {
      const impl = PLANTILLA_PODERES[this.activo.kind];
      try { if (impl && impl.paso) impl.paso(dt, this.game, this.activo, this.ctrl, this.ctx); } catch (e) {}
      this.powerT -= dt;
      if (this.powerT <= 0) this._cerrar();
      return;
    }
    if (this.pendT > 0) {
      this.pendT -= dt; if (this.pendT <= 0) { this._lanzar(); }
      return;
    }
    if (this.cd > 0) { this.cd -= dt; return; }
    if (r.state !== 'rally' || this.ctrl.pruebaActiva()) return;
    if ((r.rallyHits || 0) < this.T.minRallyHits) return;
    const b = this.game.ball;
    if (!b || !(b.vel.z > 0.35)) return;
    if (this.T.bolsa === 'rotatoria' && this.rallyFired) return;
    this.garantiaT -= dt;
    const p0 = this._elegirPico();
    const chance = (p0 && p0.chance != null) ? p0.chance : this.T.chance;
    if (this.garantiaT <= 0 || Math.random() < chance) { this.garantiaT = this.T.garantiaS; this.disparar(); }
    else if (this.garantiaT <= 4) { this.cd = 4; this.garantiaT = this.T.garantiaS; }
  }
  _elegirPico() { return this.lista.length ? (this.bag.length ? this.bag[0] : this.lista[0]) : null; }
  finRally() { this.rallyFired = false; }
  parar() { this.pendT = 0; this.pend = null; if (this.activo) this._cerrar(); this.sign.hide(); _trozosLimpia(this.game); }   // r88: nada vivo al volver a sala/salir
  dispose() { try { this.sign.dispose(); } catch (e) {} if (this.activo) this._cerrar(); _trozosLimpia(this.game); }
}

/* ------------------------------------------------------------------ */
/* Prueba genérica DIANAS (3 modos: objetivos/movimiento/contrarreloj) */
/* ------------------------------------------------------------------ */
const DIANAS_DEF = {
  spawnX: 0.85, spawnYMin: 0.45, spawnYMax: 1.30, spawnZMin: -0.55, spawnZMax: -1.70,
  radio: 0.155, maxVivas: [2, 4], hold: { x: 0.0, z: -0.5, T: 1.5, H: 0.42 },
  recambioMs: 900, deadT: 0.7, tiempoBase: 20, tiempoPorObjetivo: 10, tiempoMax: 90,
};

function _texturaDiana(radioModo) {
  const S = 256; const cv = document.createElement('canvas'); cv.width = S; cv.height = S;
  const g = cv.getContext('2d');
  const anillos = ['#7f1d1d', '#f8fafc', '#dc2626', '#f8fafc', '#b91c1c'];
  const r = S / 2;
  anillos.forEach((c, i) => { g.beginPath(); g.arc(r, r, r * (1 - i * 0.19), 0, Math.PI * 2); g.fillStyle = c; g.fill(); });
  g.lineWidth = 10; g.strokeStyle = '#fbbf24';
  g.beginPath(); g.arc(r, r, r - 5, 0, Math.PI * 2); g.stroke();
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

class DianasPrueba {
  constructor(ctrl, game, stage, cfg) {
    this.ctrl = ctrl; this.game = game; this.stage = stage;
    this.cfg = Object.assign({}, DIANAS_DEF, cfg || {});
    this.rules = stage.rules || {};
    this.modo = this.rules.modo || 'objetivos';
    this.objetivo = Math.max(1, (this.rules.objetivo || 6) + (ctrl.leyendaOn() ? (MAN.camino.leyenda.pruebaExtra || 0) : 0));
    this.golpes = 0; this.perdidas = 0; this.tiempo = Math.min(this.cfg.tiempoMax, this.cfg.tiempoBase + this.objetivo * this.cfg.tiempoPorObjetivo);
    this.fase = 'intro'; this.faseT = 0; this.finT = 0; this.gana = false;
    this.pool = []; this.vivas = [];
    this.bolaEstado = 'hold'; this.holdT = 0; this.flightT = 0; this.prev = new THREE.Vector3();
    this._construir();
  }
  _construir() {
    const tex = _texturaDiana(this.modo === 'contrarreloj');
    this.tex = tex;
    this.hud = null;
    if (MAN.hud && MAN.hud.activo !== false) {
      const cv = document.createElement('canvas'); cv.width = 640; cv.height = 150;
      this.hudCv = cv; this.hudTex = new THREE.CanvasTexture(cv); this.hudTex.colorSpace = THREE.SRGBColorSpace;
      this.hud = new THREE.Mesh(new THREE.PlaneGeometry(1.55, 0.36), new THREE.MeshBasicMaterial({ map: this.hudTex, transparent: true }));
      this.hud.position.set(0, DIMS.tableTopY + 1.18, DIMS.tableCenterZ - 1.55);
      this.game.scene.add(this.hud);
    }
    const nVivas = clamp(this.objetivo, this.cfg.maxVivas[0], this.cfg.maxVivas[1]);
    for (let i = 0; i < nVivas; i++) this.vivas.push(this._nuevaDiana(i));
    const b = this.game.ball;
    b.ignoreNet = true; b.ignoreTable = true; b.ignoreWalls = false;
    this._holdBola();
  }
  _nuevaDiana(i) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: this.tex, transparent: true }));
    const r = this.modo === 'contrarreloj' ? this.cfg.radio * 0.84 : this.cfg.radio;
    s.scale.set(r * 2.6, r * 2.6, 1);
    this._colocar(s);
    this.game.scene.add(s);
    const mv = this.modo === 'objetivos' ? { w: 0.25, a: 0.02 } : this.modo === 'movimiento' ? { w: 0.85, a: 0.22 } : { w: 1.5, a: 0.34 };
    return { s, r, fase: Math.random() * Math.PI * 2, mv, bob: this.modo !== 'objetivos', y0: s.position.y, vida: 0 };
  }
  _colocar(s) {
    s.position.set(rand(-this.cfg.spawnX, this.cfg.spawnX), rand(DIMS.tableTopY + this.cfg.spawnYMin, DIMS.tableTopY + this.cfg.spawnYMax), DIMS.tableCenterZ + rand(this.cfg.spawnZMin, this.cfg.spawnZMax));
  }
  _holdBola() {
    const b = this.game.ball, h = this.cfg.hold;
    b.vel.set(0, 0, 0);
    b.pos.set(h.x, DIMS.tableTopY + h.H, DIMS.tableCenterZ + h.z);
    if (this.game.ballMesh) this.game.ballMesh.position.copy(b.pos);
    this.bolaEstado = 'hold'; this.holdT = 0;
  }
  _lanzarBola(v) {
    const b = this.game.ball;
    const dir = v && v.lengthSq() > 0.2 ? v.clone().normalize() : new THREE.Vector3(rand(-0.2, 0.2), 0.55, -1).normalize();
    b.vel.copy(dir.multiplyScalar(Math.max(2.2, v ? v.length() : 3.0)));
    this.bolaEstado = 'flight'; this.flightT = 0; this.prev.copy(b.pos);
  }
  start() {
    this.fase = 'play';
    const lineas = [tx('prueba_vs', { nombre: this.stage.name, n: 1 }), '🎯 ' + this.objetivo + (this.rules.premio ? ' · ' + this.rules.premio : '')];
    try { this.game.showInstrucciones(this.stage.name, lineas, 7.5, () => {}, MAN.id, { empezar: true }); } catch (e) {}
  }
  laserHit(pos) { this._impactoEn(pos, null); }
  _impactoEn(pos, diana) {
    this.golpes++;
    this.ctrl._puntosAdd(this.rules.puntos || 2);
    this.ctrl.fxPop(pos);
    this.ctrl.haptic(0.7, 120);
    if (diana) { diana.s.visible = false; diana.vida = -1; }
    if (this.golpes >= this.objetivo) this._fin(true);
  }
  _pasoBola(dt) {
    const b = this.game.ball;
    if (this.bolaEstado === 'hold') {
      this.holdT += dt;
      const h = this.cfg.hold;
      const t = this.holdT;
      b.pos.set(h.x, DIMS.tableTopY + h.H + Math.abs(Math.sin(t * Math.PI / h.T)) * h.H * 0.35, DIMS.tableCenterZ + h.z);
      if (this.game.ballMesh) this.game.ballMesh.position.copy(b.pos);
      const palas = this._palas();
      for (const p of palas) {
        if (!p) continue;
        const v = (p.velocity && p.velocity.length ? p.velocity.length() : 0);
        if (p.position.distanceTo(b.pos) < 0.09 + DIMS.ballRadius + 0.03 && v > 0.4) { this._lanzarBola(p.velocity); break; }
      }
      if (this.holdT > 6) this._lanzarBola(null);
    } else {
      this.flightT += dt;
      this.prev.copy(b.pos);
      b.vel.y -= Math.abs(DIMS.gravity) * dt;
      b.pos.addScaledVector(b.vel, dt);
      if (this.game.ballMesh) this.game.ballMesh.position.copy(b.pos);
      for (const d of this.vivas) {
        if (d.vida < 0 || !d.s.visible) continue;
        const rr = d.r + DIMS.ballRadius;
        const seg = new THREE.Vector3().subVectors(b.pos, this.prev);
        const m2 = seg.lengthSq();
        let tHit = -1;
        if (m2 > 1e-9) {
          const t0 = new THREE.Vector3().subVectors(d.s.position, this.prev);
          tHit = clamp(t0.dot(seg) / m2, 0, 1);
        }
        const punto = new THREE.Vector3().lerpVectors(this.prev, b.pos, Math.max(0, tHit));
        if (punto.distanceTo(d.s.position) <= rr) { this._impactoEn(d.s.position, d); b.vel.multiplyScalar(0.25); b.vel.y = Math.abs(b.vel.y) * 0.4 + 0.6; break; }
      }
      if (b.pos.y < 0.05 || b.pos.z > DIMS.tableCenterZ + 1.2 || b.pos.z < DIMS.tableCenterZ - 2.6 || this.flightT > 9) {
        this.perdidas++;
        this._recambio();
      }
    }
  }
  _recambio() {
    this.recambioT = this.cfg.recambioMs / 1000;
    this.bolaEstado = 'wait';
  }
  _palas() {
    const out = [];
    try {
      const pads = this.game.controllerPaddles || [];
      for (const p of pads) if (p && p.position) out.push({ position: p.position, velocity: p.velocity || new THREE.Vector3() });
    } catch (e) {}
    return out;
  }
  step(dt) {
    if (this.fase !== 'play') { this.faseT += dt; return; }
    this.tiempo -= dt;
    if (this.tiempo <= 0) { this._fin(this.golpes >= this.objetivo); return; }
    this.vivas.forEach((d, i) => {
      if (d.vida < 0) { d.vida += dt; if (d.vida > 0.7 && this.golpes + this.vivas.filter((x) => x.vida >= 0).length < this.objetivo + this.vivas.length) { this._colocar(d.s); d.vida = 0; d.s.visible = true; d.y0 = d.s.position.y; } return; }
      d.fase += dt * d.mv.w;
      d.s.position.x += Math.cos(d.fase) * d.mv.a * dt;
      if (d.bob) d.s.position.y = d.y0 + Math.sin(d.fase * 1.3) * 0.035;
    });
    if (this.bolaEstado === 'wait') {
      this.recambioT -= dt;
      if (this.recambioT <= 0) this._holdBola();
    } else this._pasoBola(dt);
    if (this.hud) this._pintaHud();
  }
  _pintaHud() {
    const g = this.hudCv.getContext('2d');
    g.clearRect(0, 0, 640, 150);
    g.fillStyle = 'rgba(10,12,20,0.6)'; g.fillRect(0, 0, 640, 150);
    g.fillStyle = '#fbbf24'; g.font = 'bold 64px sans-serif'; g.textAlign = 'left';
    g.fillText('🎯 ' + this.golpes + '/' + this.objetivo, 24, 96);
    g.fillStyle = '#e2e8f0'; g.font = '52px sans-serif'; g.textAlign = 'right';
    g.fillText('⏱ ' + Math.max(0, Math.ceil(this.tiempo)) + 's', 616, 96);
    this.hudTex.needsUpdate = true;
  }
  _fin(gana) {
    if (this.fase === 'result') return;
    this.fase = 'result'; this.gana = gana; this.faseT = 0;
    const frac = clamp(this.tiempo / Math.max(1, this.cfg.tiempoBase + this.objetivo * this.cfg.tiempoPorObjetivo), 0, 1);
    const stars = gana ? (frac >= 0.25 ? 3 : frac >= 0.08 ? 2 : 1) : 0;
    this.stars = stars;
    telemetria('champ_rank', { champ: MAN.id, prueba: 'dianas', win: gana, score: this.golpes * (this.rules.puntos || 2), stars, golpes: this.golpes, objetivo: this.objetivo, perdidas: this.perdidas, t: Math.round(this.tiempo) });
    this.ctrl._finPrueba(gana, this);
  }
  activa() { return this.fase === 'play'; }
  stop() {
    if (this.hud) { this.game.scene.remove(this.hud); this.hud.geometry.dispose(); this.hud.material.map.dispose(); this.hud.material.dispose(); this.hud = null; }
    this.vivas.forEach((d) => { this.game.scene.remove(d.s); d.s.material.dispose(); });
    this.vivas = [];
    const b = this.game.ball;
    b.ignoreNet = false; b.ignoreTable = false;
  }
  dispose() { this.stop(); if (this.tex) this.tex.dispose(); }
}

PLANTILLA_PRUEBAS.dianas = DianasPrueba;

/* ------------------------------------------------------------------ */
/* Pistola láser opcional (locura/magia/orbital)                       */
/* ------------------------------------------------------------------ */
class PlantillaPistola {
  constructor(ctrl, game, man) {
    this.ctrl = ctrl; this.game = game;
    const g = man.playerGun || {};
    this.activoCfg = !!g.activo;
    this.cadencia = g.cadencia || 0.16; this.alcance = g.alcance || 6.0;
    this.hazColor = g.haz != null ? g.haz : 0x66d9ff;
    this.cd = 0; this.beams = [];
    this._cargarModelo(g.glb || 'assets/pistol.glb');
  }
  _cargarModelo(url) {
    try {
      new GLTFLoader().load(A(String(url).replace(/^assets\//, '')), (gltf) => {
        this.modelo = gltf.scene;
        const esc = (this.man.playerGun.escalado || 0.32);
        this.modelo.scale.setScalar(esc);
        try { (this.game.gunMounts || []).forEach((m) => { m.clear(); m.add(this.modelo.clone(true)); }); } catch (e) {}
      }, undefined, () => {});
    } catch (e) {}
  }
  disparo(mano) {
    if (!this.activoCfg || this.cd > 0 || !this.ctrl.pruebaActiva()) return false;
    this.cd = this.cadencia;
    const origen = new THREE.Vector3(); const dir = new THREE.Vector3(0, 0, -1);
    try {
      const cam = this.game.renderer.xr.getCamera();
      origen.copy(cam.position); cam.getWorldDirection(dir);
    } catch (e) { return false; }
    const hasta = origen.clone().addScaledVector(dir, this.alcance);
    this._haz(origen, hasta);
    this.ctrl.pruebaActual() && this.ctrl.pruebaActual().vivas && this._disparaDianas(origen, dir);
    this.ctrl.haptic(0.25, 60);
    return true;
  }
  _disparaDianas(origen, dir) {
    const pr = this.ctrl.pruebaActual();
    for (const d of pr.vivas) {
      if (d.vida < 0 || !d.s.visible) continue;
      const t0 = new THREE.Vector3().subVectors(d.s.position, origen);
      const tProy = t0.dot(dir);
      if (tProy < 0 || tProy > this.alcance) continue;
      const punto = origen.clone().addScaledVector(dir, tProy);
      if (punto.distanceTo(d.s.position) <= d.r * 1.2) { pr.laserHit(d.s.position); break; }
    }
  }
  _haz(a, b) {
    const geo = new THREE.CylinderGeometry(0.004, 0.004, a.distanceTo(b), 6);
    const mat = new THREE.MeshBasicMaterial({ color: this.hazColor, transparent: true, opacity: 0.9 });
    const m = new THREE.Mesh(geo, mat);
    m.position.lerpVectors(a, b, 0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    this.game.scene.add(m);
    this.beams.push({ m, t: 0.16 });
  }
  update(dt) {
    this.cd -= dt;
    this.beams = this.beams.filter((o) => {
      o.t -= dt; o.m.material.opacity = Math.max(0, o.t / 0.16);
      if (o.t <= 0) { this.game.scene.remove(o.m); o.m.geometry.dispose(); o.m.material.dispose(); return false; }
      return true;
    });
  }
  get armado() { return this.activoCfg; }
}

/* ------------------------------------------------------------------ */
/* CONTROLADOR principal                                               */
/* ------------------------------------------------------------------ */
class PlantillaController {
  constructor(game, man) {
    this.game = game; this.man = man;
    this.camino = Object.assign({ patron: 'duelo_prueba', duelo: { puntos: 11 } }, man.camino || {});
    this.rival = null; this.mapa = null; this.cartel = null; this.poderes = null; this.pistola = null;
    this.prueba = null; this.dueloVivo = false; this.dueloN = 0;
    this._aiMul = 1.0; this._curva = null;
    this._replay = null; this._leyendaOn = false;
    this.streakAi = 0; this._insignia = null;
    this._finalT = 0;                     // r91: hold de la cara final del duelo
    this._losaSaved = null; this._losaTex = null; this._losaFrameMat = null; this._losaFrameCol = 0;
  }
  /* ---- camino / progreso ---- */
  etapas() { return this.man.stages || []; }
  totalEtapas() { return this.etapas().length; }
  indiceReal() { return clamp(parseInt(sGet('stage') || '0', 10) || 0, 0, this.totalEtapas()); }
  etapaActual() { return this.etapas()[Math.min(this.indiceReal(), this.totalEtapas() - 1)] || null; }
  indice() { return Math.min(this.indiceReal() + 1, this.totalEtapas()); }
  isChampion() { return sGet('champ') === '1'; }
  puntos() { return parseInt(sGet('puntos') || '0', 10) || 0; }
  duelwins() { return parseInt(sGet('duelwins') || '0', 10) || 0; }
  leyendaOn() { return this._leyendaOn; }
  pruebaActiva() { return !!(this.prueba && this.prueba.activa()); }
  pruebaActual() { return this.prueba; }
  curvaVigente() { return this._curva; }
  haptic(f, ms) { try { this.game.haptic('right', f, ms); } catch (e) {} }
  _puntosAdd(n) { if (n) sSet('puntos', this.puntos() + n); }

  curvaDuelo(nDuelo, esFinal) {
    const d = this.camino.dificultad || {};
    if (d.modo === 'tabla' && Array.isArray(d.tabla)) {
      const fila = d.tabla[Math.min(nDuelo - 1, d.tabla.length - 1)] || {};
      return { aiMul: fila.aiMul || 1.0, chance: fila.chance, cooldown: fila.cooldown, primer: fila.primer, warn: fila.warn };
    }
    const pers = this.man.rival && this.man.rival.personalidad;
    const extra = pers ? ((pers.agresividad - 3) * 0.03 + (pers.precision - 3) * 0.03) : 0;
    const base = esFinal ? (d.difMul || 1.0) * (d.difFinal || 1.35) : (d.difMul || 1.0) * (1 + (d.paso || 0.15) * (nDuelo - 1));
    return { aiMul: base + extra };
  }
  _nvCfg() {
    const base = this._curva || { aiMul: 1.0 };
    if (!this._leyendaOn) return base;
    const L = (this.camino.leyenda) || {};
    return {
      aiMul: base.aiMul * (L.aiMulMul || 1.15),
      chance: base.chance != null ? Math.min(L.chanceMax || 0.60, base.chance + (L.chanceSuma || 0.06)) : undefined,
      cooldown: base.cooldown != null ? Math.max(L.cooldownMin || 6.0, base.cooldown - (L.cooldownResta || 1.5)) : undefined,
      primer: base.primer != null ? Math.max(L.primerMin || 3.0, base.primer - (L.primerResta || 1.0)) : undefined,
      warn: base.warn,
    };
  }

  /* ---- MESA LOSA (r86 · petición del dueño: la mesa viste la losa de ----
   * piedra del artista, como la mesa de madera del Salvaje Oeste) --------
   * r92 · TEXTURA NUEVA DEL DUEÑO: «Cambiamos la textura de la mesa por la
   * nueva que adjunto» — mesa.webp (2048×1024, cuatro losas de piedra con
   * grietas, musgo y salpicaduras de sangre). El mismo camino de siempre
   * (mesa LOSA sobre ppTableTop, SRGB + anisotropía + marco piedra oscura);
   * losa.jpg se CONSERVA en assets para rollback. */
  _losaOn() {
    const g = this.game;
    if (!g || !g.tableGroup || this._losaSaved) return;
    const top = g.tableGroup.getObjectByName('ppTableTop');
    if (!top || !top.material) return;
    this._losaSaved = {
      mat: top.material,
      map: top.material.map || null,
      col: top.material.color.getHex(),
      rough: top.material.roughness,
      metal: top.material.metalness,
    };
    try {
      const tex = new THREE.TextureLoader().load(A('mesa.webp'));
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
      try { tex.anisotropy = g.renderer.capabilities.getMaxAnisotropy(); } catch (e) { /* */ }
      this._losaTex = tex;
      top.material.map = tex;
      top.material.color.setHex(0xffffff);
      top.material.roughness = 0.92;
      top.material.metalness = 0.0;
      top.material.needsUpdate = true;
    } catch (e) { /* sin losa: mesa clásica */ }
    // marco y patas a piedra oscura (UN material compartido: una sola tinta)
    for (const n of g.tableGroup.children) {
      if ((n.name === 'ppTableApron' || n.name === 'ppTableLeg') &&
          n.material && n.material.color && !this._losaFrameMat) {
        this._losaFrameMat = n.material;
        this._losaFrameCol = n.material.color.getHex();
        break;
      }
    }
    if (this._losaFrameMat) {
      this._losaFrameMat.color.setHex(0x3d4145);
      this._losaFrameMat.needsUpdate = true;
    }
  }
  _losaOff() {
    const s = this._losaSaved;
    if (s && s.mat) {
      s.mat.map = s.map;
      s.mat.color.setHex(s.col);
      s.mat.roughness = s.rough;
      s.mat.metalness = s.metal;
      s.mat.needsUpdate = true;
    }
    if (this._losaFrameMat) {
      this._losaFrameMat.color.setHex(this._losaFrameCol);
      this._losaFrameMat.needsUpdate = true;
    }
    this._losaSaved = null;
    this._losaFrameMat = null;
    if (this._losaTex) { try { this._losaTex.dispose(); } catch (e) { /* */ } this._losaTex = null; }
  }

  /* ---- ciclo sala ---- */
  /* r87 · DESMONTA (nuevo): el arranque repetido (re-entrar al campeonato)
 * deja TODO lo anterior vivo en escena — rival duplicado, mapa viejo,
 * cartel y tabla pendiente. Desmonta en orden inverso y limpia la GPU. */
  _desmonta() {
    if (this.poderes) { try { this.poderes.dispose(); } catch (e) { /* */ } this.poderes = null; }
    if (this.pistola) { try { this.pistola.beams.forEach((o) => { this.game.scene.remove(o.m); }); this.pistola.beams = []; } catch (e) { /* */ } this.pistola = null; }
    if (this.rival) { try { this.rival.dispose(); } catch (e) { /* */ } this.rival = null; }
    if (this.mapa) { try { this.mapa.dispose(); } catch (e) { /* */ } this.mapa = null; }
    if (this.cartel) { try { this.game.scene.remove(this.cartel.mesh); this.cartel.dispose(); } catch (e) { /* */ } this.cartel = null; }
    if (this._insignia) { try { this.game.scene.remove(this._insignia); this._insignia.geometry.dispose(); this._insignia.material.dispose(); } catch (e) { /* */ } this._insignia = null; }
    if (this.prueba) { try { this.prueba.dispose(); } catch (e) { /* */ } this.prueba = null; }
  }
  startChamp() {
    this._desmonta();
    this.rival = new RivalVivo(this.game, this.man);
    this.rival.estadoBase('idle');
    this.cartel = construirCartel(this.game, this.man);
    this.mapa = new MapaPlantilla(this.game, this.man, this);
    this.poderes = new PlantillaPoderes(this, this.game, this.man);
    this.pistola = new PlantillaPistola(this, this.game, this.man);
    this._losaOn();
    if (MUSIC) try { MUSIC.on(); } catch (e) {}
    if (this.game.rules) {
      if (this.game.rules.state === 'champtest' || this.game.rules.state === 'over' || !this.game.rules.state) {}
      this.game.rules.state = STATE_NAME;
      this.game.rules.oppLabel = (this.man.rival && this.man.rival.oppLabel) || 'rival';
    }
    this._variant(null);
  }
  _variant(nombre) {
    try { if (this.game.champRoom && this.game.champRoom.useVariant) this.game.champRoom.useVariant(nombre); } catch (e) {}
  }

  serveTrigger(i) {
    if (this.pruebaActiva()) { if (this.prueba.lanzar) this.prueba.lanzar(); return; }
    if (this.dueloVivo) return;
    const idx = this.indiceReal();
    if (idx >= this.totalEtapas()) { this._rejugarLibre(); return; }
    this._lanzarEtapa(idx, false);
  }
  _lanzarEtapa(idx, esReplay) {
    const st = this.etapas()[idx]; if (!st) return;
    telemetria('stage', { n: idx + 1, id: this.man.id });
    if (st.kind === 'duelo') this._startDuel(idx, esReplay);
    else this._startPrueba(idx, esReplay);
  }
  _startDuel(idx, esReplay) {
    const st = this.etapas()[idx];
    this.dueloN = this.etapas().slice(0, idx + 1).filter((e) => e.kind === 'duelo').length;
    this._curva = this.curvaDuelo(this.dueloN, st.id === 'final' || (st.rules && st.rules.jefe));
    const cfg = this._nvCfg();
    this._aiMul = cfg.aiMul || 1.0;
    try { if (this.game.applyAISkill) this.game.applyAISkill(this._aiMul); } catch (e) {}
    this.dueloVivo = true; this.dueloIdx = idx; this.dueloReplay = !!esReplay;
    this.rival.enDuelo(true);
    this._variant(st.id === 'final' ? 'final' : null);
    this.game.rules.oppLabel = (this.man.rival && this.man.rival.oppLabel) || 'rival';
    this.game.rules.startMatch(this.camino.duelo && this.camino.duelo.modo || 'match');
    if (cfg.primer != null && this.poderes) this.poderes.cd = cfg.primer;
    try { this.game.showInstrucciones(tx('duelo_vs', { n: this.dueloN }), [], 4.0, () => {}, this.man.id, { empezar: true }); } catch (e) {}
  }
  _startPrueba(idx, esReplay) {
    const st = this.etapas()[idx];
    const cls = PLANTILLA_PRUEBAS[st.kind];
    if (!cls) { console.warn('[plantilla] kind de prueba no registrado:', st.kind); this.sala(); return; }
    this.pruebaIdx = idx; this.pruebaReplay = !!esReplay;
    this._variant(null);
    this.prueba = new cls(this, this.game, st, (this.man.pruebas && this.man.pruebas[st.kind]) || {});
    if (this.rival) this.rival.estadoBase('idle');
    this.prueba.start();
  }
  _finPrueba(gana, prueba) {
    if (gana) this._puntosAdd(50);
    this._stageClear(this.pruebaIdx, gana, 'prueba');
    this.prueba = null;
    this.sala();
  }
  onPoint(it) {
    /* r91 · la REACCIÓN al punto la reparte el NÚCLEO por la norma r57
     * (rivalEmocion → cara + sonido). Aquí sólo queda el bookkeeping de
     * la racha — el motor local que pisaba la norma SE RETIRA. */
    if (!this.dueloVivo) return;
    if (it && it.winner === 'rival') this.streakAi++; else if (it && it.winner === 'player') this.streakAi = 0;
  }
  onMatchOver(w) {
    if (!this.dueloVivo) return;
    const won = (w === true || w === 'player');
    const r = this.game.rules || {};
    const score = r.scorePlayer | 0;
    if (won) { sSet('duelwins', this.duelwins() + 1); this._puntosAdd(250); }
    const fila = { w: won, score, stars: won ? 1 : 0, duel: true, pts: this.puntos() };
    try {
      const rank = JSON.parse(sGet('rank') || '[]'); rank.push(fila);
      sSet('rank', JSON.stringify(rank.slice(-10)));
    } catch (e) {}
    telemetria('champ_rank', { champ: this.man.id, prueba: 'duelo', win: won, score, stars: won ? 1 : 0, nv: this.dueloN, duelScore: score });
    if (won) rankingMundial('✔');
    this.rival.final(won);
    /* r89/r91 · SONIDO DEL FINAL (arte del dueño): al VENCERLO suena
     * zombi_defeated.mp3; cuando el zombi GANA, zombi_victory.mp3. Y la
     * CARA final VIVE: _finalT congela el reset de sala() — la r90 la
     * pisaba con idle EL MISMO FRAME (el dueño jamás vio zombi_defeated). */
    if (SFX) SFX.play(won ? 'defeated' : 'victory', 0.7);
    this._finalT = 4.2;
    this.dueloVivo = false;
    if (won) this._stageClear(this.dueloIdx, true, 'duelo');
    this.sala();
  }
  _stageClear(idx, gana, tipo) {
    if (this._replay) {
      if (gana && this.isChampion() && this.camino.leyenda && this.camino.leyenda.activa) {
        sSet('leyenda_' + (idx + 1), '1');
        if (SFX && SFX.tiene('laugh')) SFX.play('pw', 0.5);
        this.haptic(0.8, 200);
        const n = this._sellos();
        if (n >= this.totalEtapas()) this._leyendaFlow();
      }
      sSet('stage', String(this._replay.real));
      this._leyendaOn = false; this._replay = null;
      this._refrescaCartel();
      return;
    }
    if (!gana) return;                       // derrota: la etapa se repite
    const sig = idx + 1;
    sSet('stage', String(sig));
    if (sig >= this.totalEtapas() && !this.isChampion()) this._championFlow();
    this._refrescaCartel();
  }
  _sellos() {
    let n = 0;
    for (let i = 1; i <= this.totalEtapas(); i++) if (sGet('leyenda_' + i) === '1') n++;
    return n;
  }
  _championFlow() {
    sSet('champ', '1');
    const fecha = new Date().toISOString();
    sSet('fecha', fecha);
    this._insigniaShow();
    const C = MAN.coronacion || {};
    const stats = [];
    (C.stats || ['puntos', 'duelos', 'fecha']).forEach((k) => {
      if (k === 'puntos') stats.push(['Puntos', String(this.puntos())]);
      else if (k === 'duelos') stats.push(['Duelos', String(this.duelwins())]);
      else if (k === 'fecha') stats.push(['Fecha', fecha.slice(0, 10)]);
    });
    try {
      if (CORE.showChampConseguido) CORE.showChampConseguido(this.man.id, {
        campeon: true,
        title: tx('coronacion_titulo'),
        msg: tx('coronacion_msg'),
        dur: C.dur || 14,
        stats,
      });
    } catch (e) {}
    telemetria('champion', { id: this.man.id });
    rankingMundial(this.camino.leyenda && this.camino.leyenda.activa ? '★' : '🏆');
    this.rival.final(true);
    this._refrescaCartel();
  }
  _leyendaFlow() {
    sSet('leyenda', '1');
    telemetria('champ_rank', { champ: this.man.id, prueba: 'leyenda', win: true, score: this.puntos(), stars: 3 });
    try {
      if (CORE.showChampConseguido) CORE.showChampConseguido(this.man.id, { campeon: true, title: '★ LEYENDA', msg: tx('leyenda_medalla'), dur: 12 });
    } catch (e) {}
    this.haptic(1.0, 260);
  }
  _insigniaShow() {
    if (this._insignia) return;
    const url = (MAN.coronacion && MAN.coronacion.insignia) || (MAN.trophy && MAN.trophy.arte);
    if (!url) return;
    const tex = new THREE.TextureLoader().load(A(String(url).replace(/^assets\//, '')));
    const m = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.62), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
    m.position.set(-1.9, 1.42, -5.40);   // r87: pared FRONTAL (antes flotaba a mitad de sala)
    this.game.scene.add(m);
    this._insignia = m;
  }
  rejugar(idx) {
    if (idx < 0 || idx > this.mapa.maxIdx() || this.pruebaActiva() || this.dueloVivo) return;
    if (this.isChampion() && this.camino.leyenda && this.camino.leyenda.activa) {
      this._leyendaOn = true;
      this._replay = { real: this.indiceReal() };
    } else {
      this._replay = { real: this.indiceReal() };
    }
    this._lanzarEtapa(idx, true);
  }
  _rejugarLibre() { if (this.mapa) this.mapa.hover(0); }
  sala() {
    if (this.prueba) { try { this.prueba.stop(); } catch (e) {} this.prueba = null; }
    if (this.poderes) this.poderes.parar();
    this.dueloVivo = false;
    if (this.game.rules) {
      this.game.rules.oppLabel = (this.man.rival && this.man.rival.oppLabel) || 'rival';
      this.game.rules.state = STATE_NAME;
    }
    if (this.rival && !(this._finalT > 0)) this.rival.estadoBase('idle');   // r91: la cara final (defeated/victory) NO se pisa al volver a la sala
    this._refrescaCartel();
  }
  _refrescaCartel() {
    /* r88: cartel de bienvenida OCULTO por normativa del dueño (manifest) */
    if (this.man.cartel && this.man.cartel.oculto) { this.cartel = null; return; }
    if (this.cartel) { try { this.game.scene.remove(this.cartel.mesh); } catch (e) {} this.cartel = construirCartel(this.game, this.man); }
  }
  fxPop(pos) {
    try {
      if (this.game.confettiBurst != null) { const c = this.game.confettiBurst; this.game.confettiBurst = c; }
    } catch (e) {}
    this.haptic(0.4, 80);
  }
  leave() {
    if (this.prueba) { try { this.prueba.stop(); } catch (e) {} this.prueba = null; }
    if (this.poderes) this.poderes.parar();
    this._losaOff();
    this._desmonta();       // r87: el mapa/cartel/rival/insignia NO quedan
    this.dueloVivo = false;
    if (MUSIC) try { MUSIC.off(); } catch (e) {}
    try {
      if (this.game.rules) {
        if (this.game.rules.state === STATE_NAME) this.game.rules.startMatch('match');
        this.game.rules.oppLabel = 'cpu';
      }
    } catch (e) {}
    this._variant(null);
  }
  update(dt) {
    if (this._finalT > 0) this._finalT -= dt;   // r91: hold de la cara final del duelo
    if (this.mapa) this.mapa.refresco();   // r87: tapas según progreso
    if (this.rival) {
      const r = this.game.rules || {};
      this.rival.update(dt, { rallyHits: r.rallyHits, scorePlayer: r.scorePlayer, scoreAi: r.scoreAi });
    }
    if (this.poderes) this.poderes.update(dt, this.game.rules);
    if (this.pistola) this.pistola.update(dt);
  }
  aiMul() { return this._aiMul * (this._leyendaOn ? ((this.camino.leyenda && this.camino.leyenda.aiMulMul) || 1.15) : 1.0); }
  reenter() {
    if (this.pruebaActiva()) return;
    if (this.dueloVivo) return;             // el núcleo restaura 'serve'
    if (this.game.rules) this.game.rules.state = STATE_NAME;
  }
  replayMap() { return this.mapa ? this.mapa.replayMap() : null; }
  replayHover(idx) { if (this.mapa) this.mapa.replayHover(idx); }
  replayLaunch(idx) { if (this.mapa) this.mapa.replayLaunch(idx); }
  musicOff() { if (MUSIC) try { MUSIC.off(); } catch (e) {} }
  champIntroPause(on) { if (MUSIC) try { on ? MUSIC.off() : MUSIC.on(); } catch (e) {} }
  testActive() { return this.pruebaActiva(); }
  testStep(dt) { if (this.pruebaActiva()) try { this.prueba.step(dt); } catch (e) {} }
  resetRecords() {
    CLAVES_REGISTRO.forEach(sDel);
    this._refrescaCartel();
  }
  get gunArmed() { return this.pistola ? this.pistola.armado : false; }
  fireGun(i) { return this.pistola ? this.pistola.disparo(i) : false; }
}

/* ------------------------------------------------------------------ */
/* init + export (contrato champ_sdk)                                  */
/* ------------------------------------------------------------------ */
async function init(ctx) {
  GAME = ctx.game;
  STATE_NAME = ctx.stateName || 'champtest';
  CORE = getCore();
  if (!CORE) throw new Error('[plantilla] __PP_CORE no disponible');
  DIMS = CORE.DIMS;
  const res = await fetch(new URL('./manifest.json', MOD_URL));
  MAN = await res.json();
  TXT.es = (MAN.i18n && MAN.i18n.es) || {};
  TXT.en = (MAN.i18n && MAN.i18n.en) || {};
  DECOR = { pieces: (MAN.decor && MAN.decor.pieces) || [] };
  ROOM = {};
  ['floor', 'ceil', 'back', 'front', 'left', 'right'].forEach((k) => { if (MAN.room && MAN.room[k]) ROOM[k] = MAN.room[k]; });
  if (MAN.room && MAN.room.variants) ROOM.variants = MAN.room.variants;
  try {
    const sonidos = {};
    Object.keys((MAN.audio && MAN.audio.sounds) || {}).forEach((k) => {
      sonidos[k] = String(MAN.audio.sounds[k]).replace(/^assets\//, '');
    });
    /* r90 · LOS ONE-SHOTS DEL ZOMBI CAMBIAN DE MOTOR — LA LECCIÓN DEL TREN
     * (Tasks 129→134, cinco versiones): createSfx JAMÁS llegó al hardware
     * de la Quest (play tragado, contexto dormido, buffer tarde) mientras
     * createBucle (galopes + rodadura + Tunel/Llegada desde v3.6.26) sonó
     * SIEMPRE. El dueño: «los sonidos que te pasé no se escuchan crazy/
     * defeated/victory». Cada sonido del zombi (laugh/crazy/victory/
     * defeated) es ahora un createBucle PROPIO (el motor probado) dispa-
     * rado con on() — revival por statechange y espera de buffer DENTRO
     * del motor — y cortado con off() por un reloj que SÓLO corre con
     * suena() honesto (corte antes del wrap de src.loop; desistir en paz
     * a 9 s si el buffer no llega). Duraciones reales del arte sonoro
     * (44100 Hz · 256 kbps CBR — el perfil que el casco decodifica):
     * laugh 2,90 · crazy 2,25 · victory 1,85 · defeated 8,10 s. */
    const DUR_Z = { laugh: 2.90, crazy: 2.25, victory: 1.85, defeated: 8.10 };
    ZONB = {};
    Object.keys(sonidos).forEach((k) => {
      const nb = createBucle(() => GAME, {
        url: () => A(sonidos[k]), vol: () => 0.62,
        fadeIn: 0.06, stopFade: 0.35, ignoraMute: true,   // SFX del rival: suenan SIEMPRE
      });
      ZONB[k] = { b: nb, dur: DUR_Z[k] || 3.0, reloj: -1, espera: 0 };
    });
    SFX = {
      play(n, v, o) {
        const k = (n === 'pw') ? 'laugh' : n;            // 'pw' era el alias legacy de la risa
        const z = ZONB[k]; if (!z) return false;
        z.b.on();                                        // idempotente: revival + espera de buffer
        z.reloj = 0; z.espera = 0;
        return true;
      },
      tiene(n) { const z = ZONB[(n === 'pw') ? 'laugh' : n]; return !!(z && z.b.estado && z.b.estado().cargado); },
      precarga(n) { const z = ZONB[(n === 'pw') ? 'laugh' : n]; if (z) z.b.precarga(); },
    };
    /* r89/r90 · PRECARGA de TODO el arte sonoro del zombi en el arranque —
     * el 1.er disparo encuentra el buffer decodificado. */
    Object.keys(ZONB).forEach((k) => { try { ZONB[k].b.precarga(); } catch (e) { /* */ } });
    const so = MAN.audio || {};
    /* r91 · FORMA CANÓNICA (la de magia/oeste): url y vol COMO FUNCIONES.
     * La r90 los pasó como string/número y el motor los INVOCABA
     * (o.url()/o.vol()) → TypeError silencioso bajo el catch → la BSO
     * nació muerta («No suena la música de fondo en Halloween»). El SDK
     * r91 además tolera valores directos — doble seguro. */
    MUSIC = createMusic(() => GAME, Object.assign({
      url: so.music ? (() => A(String(so.music).replace(/^assets\//, ''))) : null,
      vol: () => (so.musicVolume != null ? so.musicVolume : 0.15),
    }, so.musicOpts || {}));
  } catch (e) { SFX = null; MUSIC = null; }
  CTRL = new PlantillaController(GAME, MAN);
  window.addEventListener('pp-lang', () => { if (CTRL) CTRL._refrescaCartel(); });
  try { window['__PP_' + String(MOD_ID).toUpperCase()] = { ctrl: () => CTRL, man: () => MAN, pods: PLANTILLA_PODERES, mus: () => MUSIC, sfxZ: () => ZONB }; } catch (e) {}
  return Promise.resolve();
}

/* r90 · RELOJ DE CORTE de los one-shots del zombi — el patrón exacto de
 * Tunel/Tren_Llegada (v3.6.26): el reloj SÓLO corre cuando suena() es
 * honesto (instancia viva en el ctx actual); al llegar a dur−0,35 se corta
 * con off() (fundido 0,35 — antes del wrap de src.loop, no hay rebobinado
 * audible) y si el buffer no llegó en 9 s se desiste en paz. Llamado por
 * frame desde update() — coste: 4 booleanos. */
function _zombiSfxTick(dt) {
  if (!ZONB) return;
  for (const k of Object.keys(ZONB)) {
    const z = ZONB[k];
    if (z.reloj < 0) continue;
    if (z.b.suena()) {
      z.reloj += dt;
      if (z.reloj >= Math.max(0.3, z.dur - 0.35)) { try { z.b.off(); } catch (e) { /* */ } z.reloj = -1; }
    } else {
      z.espera += dt;
      if (z.espera > 9) { z.reloj = -1; z.espera = 0; }   // desistir en paz
    }
  }
}

function start() { if (CTRL) CTRL.startChamp(); }
function leave() { if (CTRL) CTRL.leave(); }
function update(dt) { _zombiSfxTick(dt); if (CTRL) CTRL.update(dt); }
function onPoint(it) { if (CTRL) CTRL.onPoint(it); }
// v3.6.49 (r57) · NORMA DE EMOCIONES DEL RIVAL (contrato opcional)
function rivalEmocion(st, info) { if (CTRL && CTRL.rival) CTRL.rival.rivalEmocion(st); }
function onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); }
function aiMul() { return CTRL ? CTRL.aiMul() : 1.0; }
function serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); }
function reenter() { if (CTRL) CTRL.reenter(); }
function replayMap() { return CTRL ? CTRL.replayMap() : null; }
function replayHover(idx) { if (CTRL) CTRL.replayHover(idx); }
function replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); }
function musicOff() {
  if (CTRL) CTRL.musicOff();
  /* r90: al callar la música del campeonato, ningún one-shot del zombi
   * queda sonando huérfano (salida del campeonato / silencio). */
  if (ZONB) for (const k of Object.keys(ZONB)) { try { ZONB[k].b.off(true); } catch (e) { /* */ } ZONB[k].reloj = -1; }
}
function champIntroPause(on) { if (CTRL) CTRL.champIntroPause(on); }
function resetRecords() { if (CTRL) CTRL.resetRecords(); }
function testActive() { return CTRL ? CTRL.testActive() : false; }
function testStep(dt) { if (CTRL) CTRL.testStep(dt); }
function getController() { return CTRL; }
function isChampion() { return CTRL ? CTRL.isChampion() : false; }
function getDecor() { return DECOR; }
function getRoom() { return ROOM; }
function gunArmedGet() { return CTRL ? CTRL.gunArmed : false; }
function fireGun(i) { return CTRL ? CTRL.fireGun(i) : false; }

const MOD_ID = 'halloween';

export default {
  get id() { return MOD_ID; },
  get decor() { return getDecor(); },
  get room() { return getRoom(); },
  get controller() { return getController(); },
  isChampion,
  champIntroPause,
  init,
  start,
  leave,
  resetRecords,
  update,
  onPoint,
  rivalEmocion,
  onMatchOver,
  aiMul,
  serveTrigger,
  reenter,
  replayMap,
  replayHover,
  replayLaunch,
  musicOff,
  testActive,
  testStep,
  get gunArmed() { return gunArmedGet(); },
  fireGun,
};


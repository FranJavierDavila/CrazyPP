// r138 · 13ª pasada — arnés de previsualización OFFSCREEN del menú.
// Ejecuta el drawMenu REAL del juego en node (node-canvas) y vuelva las
// tres panelas del arco de cada página a PNG — QA visual exacta de lo que
// el dueño ve en el visor, sin casco. Uso:
//   node --no-warnings scripts/preview_menu_offscreen.mjs main multi champs
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import url from 'url';

const require = createRequire(import.meta.url);
const { createCanvas, Image, registerFont } = require('canvas');

const AQUI = path.dirname(url.fileURLToPath(import.meta.url));
const RAIZ = path.join(AQUI, '..');
const SALIDA = path.join(AQUI, 'preview_menu');
fs.mkdirSync(SALIDA, { recursive: true });

/* ---------- stubs de navegador ANTES de importar el juego ---------- */
const elStub = () => ({
  style: {}, width: 0, height: 0, addEventListener() {}, removeEventListener() {},
  appendChild() {}, removeChild() {}, setAttribute() {}, getAttribute: () => null,
  classList: { add() {}, remove() {}, toggle() {} }, getContext: () => null,
  textContent: '', innerHTML: '', innerText: '', value: '', checked: false,
  focus() {}, blur() {}, click() {}, querySelector: () => null,
  querySelectorAll: () => [], parentNode: null, children: [], offsetWidth: 0,
});
globalThis.window = globalThis;
try {
  Object.defineProperty(globalThis, 'navigator', {
    value: { userAgent: 'node-preview', language: 'es', vr: {} },
    configurable: true,
  });
} catch (e) { /* node ≥21 trae navigator propio — sirve */ }
globalThis.document = {
  createElement(tag) {
    if (tag === 'canvas') {
      const cv = createCanvas(300, 150);
      cv.style = {}; cv.addEventListener = () => {};
      return cv;
    }
    return elStub();
  },
  getElementById() { return elStub(); },
  addEventListener() {}, removeEventListener() {},
  body: elStub(), documentElement: elStub(),
  visibilityState: 'visible', hidden: false,
  querySelector: () => null, querySelectorAll: () => [],
};
globalThis.Image = Image;
// el pintado comprueba im.complete / naturalWidth (API DOM) — puentear
Object.defineProperty(Image.prototype, 'naturalWidth', {
  get() { return this.width || 0; }, configurable: true,
});
Object.defineProperty(Image.prototype, 'naturalHeight', {
  get() { return this.height || 0; }, configurable: true,
});
const _imgSrc = Object.getOwnPropertyDescriptor(Image.prototype, 'src');
Object.defineProperty(Image.prototype, 'src', {
  set(v) { this._src = v; _imgSrc.set.call(this, v); },
  get() { return this._src; },
  configurable: true,
});
globalThis.requestAnimationFrame = (f) => setTimeout(() => f(performance.now()), 16);
globalThis.cancelAnimationFrame = clearTimeout;
try { globalThis.XRSystem = {}; } catch (e) { /* no-op */ }
globalThis.localStorage = (() => {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => m.set(k, String(v)),
    removeItem: (k) => m.delete(k), clear: () => m.clear() };
})();
/* c12/c00 ejecutan efectos de módulo que cuelgan del window global */
for (const nm of ['addEventListener', 'removeEventListener', 'dispatchEvent']) {
  if (typeof globalThis[nm] !== 'function') globalThis[nm] = () => {};
}
globalThis.matchMedia = globalThis.matchMedia || (() =>
  ({ matches: false, addEventListener() {}, removeEventListener() {},
    addListener() {}, removeListener() {} }));
globalThis.getComputedStyle = globalThis.getComputedStyle || (() =>
  ({ getPropertyValue: () => '' }));
if (!globalThis.AudioContext && !globalThis.webkitAudioContext) {
  globalThis.AudioContext = class {
    constructor() { this.sampleRate = 44100; this.currentTime = 0; this.state = 'suspended'; }
    createGain() { return { gain: { value: 0, setValueAtTime() {}, linearRampToValueAtTime() {},
      exponentialRampToValueAtTime() {}, setTargetAtTime() {}, connect() {} }, connect() {}, disconnect() {} }; }
    createOscillator() { return { type: '', frequency: { value: 0, setValueAtTime() {},
      exponentialRampToValueAtTime() {}, setTargetAtTime() {} }, connect() {}, start() {}, stop() {}, disconnect() {} }; }
    createBuffer() { return { getChannelData: () => new Float32Array(1) }; }
    createBufferSource() { return { buffer: null, gain: null, connect() {}, start() {}, stop() {},
      addEventListener() {}, playbackRate: { value: 1 } }; }
    createBiquadFilter() { return { type: '', frequency: { value: 0 }, Q: { value: 0 }, connect() {} }; }
    createDynamicsCompressor() { return { threshold: { value: 0 }, connect() {} }; }
    resume() { return Promise.resolve(); }
    close() { return Promise.resolve(); }
  };
}

/* fuentes del sistema para el texto (fallback DejaVu si no hay Segoe) */
for (const f of ['DejaVuSans-Bold.ttf', 'DejaVuSans.ttf', 'DejaVuSans-Oblique.ttf']) {
  const p = `/usr/share/fonts/truetype/dejavu/${f}`;
  if (fs.existsSync(p)) {
    try { registerFont(p, { family: 'system-ui', weight: '700' }); } catch (e) { /* ok */ }
    try { registerFont(p, { family: 'system-ui', weight: '800' }); } catch (e) { /* ok */ }
    try { registerFont(p, { family: 'system-ui', weight: '600' }); } catch (e) { /* ok */ }
    try { registerFont(p, { family: 'system-ui', weight: '400' }); } catch (e) { /* ok */ }
  }
}

/* ---------- imports REALES del juego (tras los stubs) ---------- */
/* El grafo fuente tiene nombres importados que c10 declara sin export
 * (el build inline lo tolera; node ESM no). Gancho de carga: completa
 * los exports que faltan con un `export { … }` de las MISMAS declaraciones. */
import { registerHooks } from 'module';
const C10 = path.join(RAIZ, 'src/game/core/c10_menu_saque.js');
const PEDIDOS_C10 = ['CHAMPS_STATE', '_dbQ1', '_dbQ2', '_dbV1', '_rbQ',
  '_rbV1', '_rbV2', '_rbV3', '_rbV4', '_rpSize', '_rpV1',
  'rpDir', 'rpOrigin', 'rpQuat', 'rpRaycaster'];
let _c10Ajustado = false;
registerHooks({
  load(fileUrl, ctx, nextLoad) {
    /* c13 instancia el juego a nivel de módulo (WebGL) — en la previsual-
       ización el constructor no corre: se bloquea SOLO ese new */
    if (fileUrl.endsWith('c13_ui_arranque.js')) {
      const { source } = nextLoad(fileUrl, ctx);
      const src = String(source)
        .replace(/new\s+PingPongGame\s*\(/g, '(null) && new PingPongGame(');
      return { format: 'module', source: src, shortCircuit: true };
    }
    if (!_c10Ajustado && fileUrl.endsWith('c10_menu_saque.js')) {
      _c10Ajustado = true;
      const { source } = nextLoad(fileUrl, ctx);
      const src = String(source);
      const yaExport = new Set();
      for (const m of src.matchAll(/export\s+(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)/g)) {
        yaExport.add(m[1]);
      }
      for (const m of src.matchAll(/export\s*\{([^}]+)\}/g)) {
        for (const nm of m[1].split(',')) {
          const n2 = nm.trim().split(/\s+as\s+/)[0].trim();
          if (n2) yaExport.add(n2);
        }
      }
      const faltan = PEDIDOS_C10.filter((n) => !yaExport.has(n));
      if (faltan.length) {
        console.log(`[preview] completando exports de c10: ${faltan.join(', ')}`);
        return { format: 'module', shortCircuit: true,
          source: src + `\nexport { ${faltan.join(', ')} };\n` };
      }
      return { format: 'module', source: src, shortCircuit: true };
    }
    return nextLoad(fileUrl, ctx);
  },
});

const { PingPongGame } = await import(
  path.join(RAIZ, 'src/game/core/c12_pingponggame.js'));
const { CONFIG_MENUS, CONFIG_SECCIONES } = await import(
  path.join(RAIZ, 'src/game/core/c02_cfg_escena.js'));

/* ---------- fakeThis: estado mínimo + métodos del prototipo REAL ---------- */
const W = CONFIG_MENUS.lienzo.ancho, H = CONFIG_MENUS.lienzo.alto;

function cargarImagen(ruta) {
  const im = new Image();
  try { im.src = ruta; } catch (e) { return im; }
  return im;
}

function construirFakeThis() {
  const f = Object.create(PingPongGame.prototype);
  f.menuCanvas = createCanvas(W, H);
  f.menuPage = 'main';
  f.menuOpen = true;
  f.menuHover = [-1, -1];
  f.menuRects = [];
  f.rules = { state: 'serve' };
  f.social = null;
  f.net = { online: false, status: 'off', role: null };
  f.audio = { online: false, arcMute: false, arcVol: 0.6, micMute: false,
    micVol: 0.8, uiVol: 0.7, voice: true };
  f.renderer = { xr: { isPresenting: false, enabled: false } };
  f.theme = null;
  f.pendingAR = false; f.pstOn = false;
  f._menuMap = null;
  f._menuLados = ['L', 'C', 'R'];
  f._menuConchaPintada = false;
  f._menuDrawPend = false;
  f._menuIconos = {};
  for (const [nombre, ic] of Object.entries(ICONOS.iconos || {})) {
    f._menuIconos[nombre] = cargarImagen(path.join(RAIZ, 'public', ic.src));
  }
  f.menuLogo = cargarImagen(path.join(RAIZ, 'public/assets/externos/logo_menu.jpg'));
  f.padES = cargarImagen(''); f.padEN = cargarImagen('');
  f.champs = null; f._champSel = null;
  f._carreraEstado = () => ({ div: 1,
    done: new Proxy({}, { get: () => false }), crowned: false });
  f._menuSalidaConf = () => ({});
  // peripheral: tooltip y teclado de idioma — fuera del QA visual
  f._menuTipDraw = () => {};
  f._langPaddle = (rects, id, x, y) => {
    const c = f.menuCanvas.getContext('2d');
    c.save();
    c.beginPath(); c.arc(x + 44, y + 34, 30, 0, Math.PI * 2);
    c.fillStyle = 'rgba(16,28,62,0.9)'; c.fill();
    c.strokeStyle = 'rgba(90,190,255,0.8)'; c.lineWidth = 2.5; c.stroke();
    c.fillStyle = '#ffffff'; c.font = '800 24px system-ui';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(id.toUpperCase(), x + 44, y + 36);
    c.restore();
    rects.push({ x: x + 10, y: y + 4, w: 68, h: 60, id: 'lang:' + id });
  };
  // textura: el slice real (lo que _menuTexSube copia a las 3 texturas)
  f._panelasCv = {};
  for (const pa of CONFIG_MENUS.arco.panelas) {
    const cv = createCanvas(pa.w, H);
    f._panelasCv[pa.id] = cv;
  }
  f._menuArco = () => {};
  f._menuTexSube = () => {
    const c0 = f.menuCanvas.getContext('2d');
    for (const pa of CONFIG_MENUS.arco.panelas) {
      const cv = f._panelasCv[pa.id];
      const cc = cv.getContext('2d');
      cc.clearRect(0, 0, pa.w, H);
      cc.drawImage(c0.canvas, pa.x, 0, pa.w, H, 0, 0, pa.w, H);
    }
  };
  return f;
}

/* ICONOS_MENUS importado dinámicamente (necesario para precargar) */
const { ICONOS_MENUS: ICONOS } = await import(
  path.join(RAIZ, 'src/game/core/c02_cfg_escena.js'));
/* re-precarga con el registro real (construirFakeThis usó el hueco ICONOS) */
function recargarIconos(f) {
  f._menuIconos = {};
  for (const [nombre, ic] of Object.entries(ICONOS.iconos)) {
    f._menuIconos[nombre] = cargarImagen(path.join(RAIZ, 'public', ic.src));
  }
}

/* ---------- render de las páginas pedidas ---------- */
const paginas = process.argv.slice(2).length
  ? process.argv.slice(2) : ['main', 'multi', 'champs', 'opts'];
const f = construirFakeThis();
recargarIconos(f);
/* HOVER=N apunta el rect N de cada página antes de pintar (QA de los
 * estados apuntados del rediseño: halos btn/tarjeta/placa) */
if (process.env.HOVER !== undefined) {
  const hN = parseInt(process.env.HOVER, 10);
  f.menuHover = [isNaN(hN) ? 0 : hN, -1];
}

let errores = 0;
for (const pag of paginas) {
  f.menuPage = pag;
  f.menuRects = [];
  try {
    PingPongGame.prototype.drawMenu.call(f);
  } catch (e) {
    errores++;
    console.error(`✗ ${pag}: ${e.message}`);
    console.error((e.stack || '').split('\n').slice(1, 4).join('\n'));
    continue;
  }
  const num = String(paginas.indexOf(pag) + 1).padStart(2, '0');
  const fase = process.env.FASE === 'despues' ? 'despues'
    : (process.env.HOVER !== undefined ? 'hover' : 'antes');
  for (const pa of CONFIG_MENUS.arco.panelas) {
    const cv = f._panelasCv[pa.id];
    fs.writeFileSync(
      path.join(SALIDA, `${fase}_${num}_${pag}_${pa.id.toLowerCase()}.png`),
      cv.toBuffer('image/png'));
  }
  console.log(`✓ ${pag}: ${f.menuRects.length} rects · panelas L/C/R volcadas`);
}
console.log(errores ? `${errores} página(s) con error` : 'todas las páginas OK');

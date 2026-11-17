// Prueba headless v2.117 (oeste) — EL PUEBLO CON EL ARTE REAL:
//  A) CONFIG: túnel por distancia (sin tunnelPre/tunnelDur) · bocas 3,4 m en
//     la ventana · casa sheriff v=0.114 · manifest 36 · VERSION 2.117.0;
//  B) PARADAS: la parada N pide SU PARADAn.png (mapeo off-by-one corregido);
//  C) TÚNEL COSIDO: boca 0±bh/2 · banda abutada borde a borde · boca espejada
//     abutada al final · transiciones pre→in y dur→out POR DISTANCIA;
//  D) ESTRELLA POR REVÓLVER: el disparo la caza (+12 s, se gasta el arma) y
//     los textos ES/EN lo dicen;
//  E) MARCADOR REAL: contador.png del artista (md5) + reloj.png en assets;
//  F) CASA AL SUELO: fachada2/interior2 sustituidos (md5 nuevos);
//  G) SANGRE: regresión (sitio y giro aleatorios en cada disparo).
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';
import * as fs from 'fs';
import * as crypto from 'crypto';

global.window = {
  __PP_CORE: {
    lang: () => 'es',
    DIMS: {
      tableCenterZ: -1.6, tableHalfLength: 1.37, tableHalfWidth: 0.7625,
      tableTopY: 0.76, ballRadius: 0.02, roomHeight: 2.85,
    },
    stepPhysics(_dt, ball) {
      ball.pos.addScaledVector(ball.vel, _dt);
      ball.vel.y -= 9.81 * _dt;
      if (ball.pos.y <= 0.02 && ball.vel.y < 0) {
        ball.pos.y = 0.02;
        ball.vel.y *= -0.45;
      }
    },
  },
  addEventListener: () => {},
};
global.performance = { now: () => Date.now() / 1000 };
const FILLS = [];
const mkCtx = () => new Proxy({}, {
  get: (t, k) => {
    if (k === 'measureText') return () => ({ width: 10 });
    if (k === 'createLinearGradient' || k === 'createRadialGradient') {
      return () => ({ addColorStop: () => {} });
    }
    if (k === 'getImageData') {
      return (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4) });
    }
    if (k === 'fillText') {
      return (txt, x) => { FILLS.push({ t: String(txt), x: x || 0 }); };
    }
    return () => {};
  },
  set: () => true,
});
const mkCanvas = () => {
  const cv = { width: 640, height: 250 };
  cv.getContext = () => mkCtx();
  return cv;
};
global.document = {
  createElementNS: () => ({
    addEventListener() {}, removeEventListener() {},
    set src(v) { setTimeout(() => this.onload && this.onload(), 0); },
    width: 4, height: 4,
  }),
  createElement: () => mkCanvas(),
  addEventListener: () => {},
};
global.Image = class {
  constructor() { this.width = 1024; this.height = 512; }
  set src(v) {
    (global.__IMG_URLS = global.__IMG_URLS || []).push(String(v));
    setTimeout(() => this.onload && this.onload(), 0);
  }
};
global.fetch = () => Promise.reject(new Error('sin red en test'));
global.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };

const modUrl = urlmod.pathToFileURL(
  pathmod.resolve('/home/z/my-project/game/championships/oeste/index.js')).href;
const mod = await import(modUrl);

const rig = new THREE.Group();
const game = {
  rig,
  scene: { background: new THREE.Color(0x0b0e11) },
  camera: { far: 60, updateProjectionMatrix() {} },
  renderer: { xr: { isPresenting: false }, capabilities: { getMaxAnisotropy: () => 4 } },
  audio: { ctx: null },
  ball: { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(), ignoreNet: false },
  ballMesh: new THREE.Mesh(new THREE.SphereGeometry(0.02, 10, 8),
    new THREE.MeshStandardMaterial({ color: 0xf3eee2, roughness: 0.4 })),
  tableGroup: { visible: true },
  scoreboardGroup: { visible: false },
  aiPaddleMesh: { visible: true },
  roomGroup: { visible: true },
  champDecor: { group: { visible: true } },
  champDecorHidden: false,
  rules: { state: '', message: '', oppLabel: '' },
  controllerPaddles: [],
  paddleHand: 1,
  haptic() {},
  events: [],
  mode: 'arcade',
  net: { online: false },
  freezeT: 0,
  resetToss() {}, setupAIServe() {}, ai: { reset() {} },
  applyAISkill() {},
};
let gunRemoved = [];
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: {
    texDot: new THREE.Texture(),
    update() {}, flash() {}, spark() {},
    smoke() {}, smokeGun() {}, beam() {}, laserVisible() {},
  },
  sfx() {},
  musicOn() {},
  _parkMainBall() {}, _findNetParts() { return []; },
  _netParts: [], _revolverModel: null, _revInHand: null,
  _gunRay() { return null; },
  _freeGunApply() {},
  _gunVisible() {}, _endTren() {}, _stageClear() {},
  _gunHandRemove(hand) { gunRemoved.push(hand); },
  _twoGunApply() {}, _twoPaddles() {}, _playWaveJingle() {},
  // v2.118/119: API de la pistola de la estrella (no-op en el banco)
  _starGunApply() {}, _starGunRec: null, _twoGuns: null,
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
  paintCartel() {}, _refreshMap() {},
};
game.rig.add(new THREE.Group());

const Tren = mod.TrenAction;
const TREN = mod.TREN;
const ASEDIO = mod.ASEDIO;
const AsedioAction = mod.AsedioAction;
if (!Tren || !TREN) throw new Error('TrenAction/TREN no exportados');
if (!ASEDIO || !AsedioAction) throw new Error('ASEDIO/AsedioAction no exportados');
const dt = 1 / 60;
let fails = 0;
const ok = (cond, msg) => {
  console.log((cond ? '★ ' : '✗ ') + msg);
  if (!cond) fails++;
};
const md5 = (p) => crypto.createHash('md5')
  .update(fs.readFileSync(p)).digest('hex');
const GA = '/home/z/my-project/game/championships/oeste/assets/';
const BA = '/home/z/my-project/beta1/championships/oeste/assets/';

/* ============ A · CONFIG v2.117 ========================================= */
{
  ok(TREN.tunnelPre === undefined && TREN.tunnelDur === undefined,
    'A1 túnel SIN relojes de fase (por distancia)');
  const TU = TREN.tunel;
  ok(TU.zIn === -12.0, 'A2 la boca nace LEJOS (zIn=' + TU.zIn + ')');
  ok(TU.bh === 3.4 && TU.bocaY === 1.72,
    'A3 bocas 3,4 m centradas en la ventana (bh=' + TU.bh + ' y=' + TU.bocaY + ')');
  ok(TU.len === 26.4 && TU.ojo === 0.4 && TU.ver === 3.0,
    'A4 banda ' + TU.len + ' m · ojo ' + TU.ojo + ' · salida asoma a ' + TU.ver + ' m');
  // la VENTANA (y 1,08-2,55) queda DENTRO de la boca (y 0,02-3,42)
  ok(TU.bocaY - TU.bh / 2 <= 1.08 && TU.bocaY + TU.bh / 2 >= 2.55,
    'A5 la boca CUBRE la ventana completa');
  // casa sheriff: línea verde re-medida sobre el arte nuevo
  const z2 = ASEDIO.casas[1].zonas[0];
  ok(z2.v === 0.114 && z2.u0 === 0.100 && z2.u1 === 0.907 && z2.n === 4,
    'A6 zona sheriff v=0.114 (antes 0.238) u 0.100-0.907 n=4');
  // versiones
  const idx = fs.readFileSync('/home/z/my-project/game/index.html', 'utf8');
  ok(/const VERSION = '2\.1[1-9][0-9]\.0'/.test(idx), 'A7 index.html VERSION (pin flexible)');
  const man = JSON.parse(fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/manifest.json', 'utf8'));
  ok(man.version >= 36, 'A8 manifest versión (pin flexible)');
}

/* ============ B · PARADAS: PARADA N ↔ PARADAn.png ======================== */
{
  const t = new Tren(ctrl);
  t.start();
  const urls = global.__IMG_URLS = [];   // v2.119: _signArt carga vía Image
  try {
    for (const i of [1, 2, 3, 0]) {
      t._paradaTry = {};
      t._paradaTex = {};    // sin caché: cada índice pide SU url
      t._signArt(i);
    }
  } finally { global.__IMG_URLS = null; }
  const num = (u) => (u.match(/PARADA(\d)\.png$/) || [])[1];
  ok(num(urls[0]) === '1' && num(urls[1]) === '2' && num(urls[2]) === '3' &&
     num(urls[3]) === '1',
    'B1 parada 1/2/3 → PARADA1/2/3 y salida → PARADA1 (pedidos: ' +
    urls.map(num).join(',') + ')');
  t.dispose();
}

/* ============ C · TÚNEL COSIDO (se ven las TRES piezas) ================== */
{
  const t = new Tren(ctrl);
  t.start();
  const TU = TREN.tunel;
  const bocas = t.tunelGrp.children.filter((m) => m.userData && m.userData.boca);
  const bandas = t.tunelGrp.children.filter((m) => !(m.userData && m.userData.boca));
  ok(bocas.length === 4 && bandas.length === 2,
    'C1 4 bocas (2 por lado) + 2 bandas');
  ok(bocas.every((m) => m.geometry.parameters.width === TU.bh &&
      m.geometry.parameters.height === TU.bh),
    'C2 las bocas miden ' + TU.bh + ' m (antes 6: sólo se veía roca)');
  ok(bocas.every((m) => Math.abs(m.position.y - TU.bocaY) < 1e-6),
    'C3 las bocas miran a la VENTANA (y=' + TU.bocaY + ')');
  const banda = bandas[0];
  ok(banda.geometry.parameters.width === TU.len &&
     banda.geometry.parameters.height === TU.h,
    'C4 banda de ' + TU.len + '×' + TU.h + ' m');
  // COSIDO: borde a borde, sin hueco ni solape
  const bandaIni = banda.position.z + TU.len / 2;    // borde delante
  const bandaFin = banda.position.z - TU.len / 2;    // borde detrás
  const bocaInFin = -TU.bh / 2;                       // boca de entrada (z local 0)
  const bocaOutIni = -(TU.len + TU.bh) + TU.bh / 2;   // boca de salida
  ok(Math.abs(bandaIni - bocaInFin) < 1e-6,
    'C5 banda COSIDA a la boca de ENTRADA (' + bandaIni.toFixed(3) + ' = ' +
    bocaInFin.toFixed(3) + ')');
  ok(Math.abs(bandaFin - bocaOutIni) < 1e-6,
    'C6 boca de SALIDA COSIDA al final de la banda (' + bandaFin.toFixed(3) +
    ' = ' + bocaOutIni.toFixed(3) + ')');
  // flujo de fases POR DISTANCIA (máquina real)
  t.phase = 'run'; t._depart();
  t.v = TREN.vMax;
  t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre' &&
     Math.abs(t.tunelGrp.position.z - TU.zIn) < 0.05,
    'C7 pre: el grupo nace a ' + TU.zIn + ' m y se VE LLEGAR');
  t._tunelZ = TU.ojo + TU.bh / 2 - 0.1;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'C8 aún pre justo ANTES del umbral');
  t._tunelZ = TU.ojo + TU.bh / 2 + 0.05;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'in', 'C9 in AL PASAR el ojo (borde trasero de la boca)');
  let g2 = 0;
  while (t._tunnelPhase === 'in' && g2++ < 200) { t.step(dt); t.fxStep(dt); }
  ok(t._tunnelPhase === 'dur', 'C10 tras el fundido (1,6 s) llega dur');
  t._tunelZ = TU.len + TU.bh / 2 - TU.ver - 0.1;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'dur', 'C11 aún dur antes de que ASOME la salida');
  t._tunelZ = TU.len + TU.bh / 2 - TU.ver + 0.05;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'out', 'C12 out al ASOMAR la boca de salida');
  const zSal = t.tunelGrp.position.z - (TU.len + TU.bh / 2);
  ok(Math.abs(zSal + TU.ver) < 0.3,
    'C13 la boca de salida asoma a ' + TU.ver + ' m del ojo (z=' +
    zSal.toFixed(2) + ')');
  t._tunnelPhase = 'out'; t._tunnelT2 = TREN.tunnelOut;
  t.fxStep(dt);
  t._tunnelPhase = 'none';
  t.fxStep(dt);
  ok(!t.tunelGrp.visible, 'C14 al salir, el túnel se retira');
  t.dispose();
}

/* ============ D · ESTRELLA DEL SHERIFF POR REVÓLVER ====================== */
{
  const a = new AsedioAction(ctrl);
  let err = '';
  try { a.start(); } catch (e) { err = e.message; }
  if (err && !/tex|load/i.test(err)) console.log('   (start asedio: ' + err + ')');
  ok(Array.isArray(a.edif) && a.edif.length === 3, 'D1 el pueblo tiene 3 edificios');
  a.phase = 'play';
  // contexto REAL: diana viva en una zona verde (la estrella exige diana)
  a._spawnTarget();
  ok(a._zona && a.dianaGrp && a.dianaGrp.visible,
    'D1b diana viva en zona verde (contexto del destape)');
  a._starT = 0.01;
  a._starStep(dt);                       // agenda y SPAWNEA
  ok(a._star && a._star.grp.visible, 'D2 la estrella aparece');
  const sp = a._star.grp.position.clone();
  a.time = 100;
  // DISPARO al centro de la estrella (desde 5 m, eje -Z)
  gunRemoved = [];
  a._shotAt(sp.clone().setZ(sp.z + 5), new THREE.Vector3(0, 0, -1), 0);
  ok(Math.abs(a.time - 112) < 1e-6, 'D3 ¡el disparo CAZA la estrella! +12 s (' +
    a.time.toFixed(0) + ' s)');
  ok(!a._star.grp.visible, 'D4 la estrella se recoge al ser cazada');
  ok(gunRemoved.indexOf(0) >= 0, 'D5 el revólver se GASTA al cazarla');
  // un disparo LEJOS no la caza
  a._starSpawn();
  a.time = 50;
  gunRemoved = [];
  a._shotAt(new THREE.Vector3(50, 50, 50), new THREE.Vector3(0, 0, -1), 1);
  ok(Math.abs(a.time - 50) < 1e-6 && a._star.grp.visible,
    'D6 un disparo fuera NO la caza (tiempo intacto, estrella sigue)');
  ok(gunRemoved.indexOf(1) >= 0, 'D7 …pero el revólver sí se gasta (disparo normal)');
  // textos: bomba O revólver
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/asedio_estrella: '¡ESTRELLA DEL SHERIFF! ¡DALE CON UNA BOMBA O CON EL REVÓLVER!'/.test(src),
    'D8 el aviso ES dice «BOMBA O REVÓLVER»');
  ok(/asedio_estrella: 'SHERIFF STAR! HIT IT WITH A BOMB OR THE REVOLVER!'/.test(src),
    'D9 el aviso EN dice «BOMB OR THE REVOLVER»');
  ok(/Caza la ESTRELLA DEL SHERIFF con una bomba o con el revólver/.test(src),
    'D10 la instrucción del asedio lo explica');
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ E · MARCADOR REAL (contador.png del artista) =============== */
{
  ok(md5(GA + 'contador.png') === '8ece8ff69a0eceea431c5864084b60c0',
    'E1 contador.png de assets = el arte REAL del artista (md5 registrado)');
  ok(md5(GA + 'contador.png') !== md5(BA + 'contador.png'),
    'E2 …DIFERENTE al letrero regenerado de beta1');
  ok(fs.existsSync(GA + 'reloj.png'), 'E3 reloj.png (reloj de arena) en assets');
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/assets\/reloj\.png/.test(src) && /this\.relojImg = rc/.test(src),
    'E4 el HUD carga y TIÑE el reloj de arena');
  ok(/RELOJ de la oleada, junto al cartel/.test(src),
    'E5 el reloj se pinta JUNTO al cartel del marcador');
}

/* ============ F · LA CASA DEL SHERIFF LLEGA AL SUELO ===================== */
{
  ok(md5(GA + 'decor/asedio/fachada2.webp') !==
     md5(BA + 'decor/asedio/fachada2.webp'),
    'F1 fachada2 SUSTITUIDA por el arte nuevo (upload/ ya no existe)');
  ok(md5(GA + 'decor/asedio/interior2.webp') !== md5(BA + 'decor/asedio/interior2.webp'),
    'F2 interior2 SUSTITUIDO por el arte nuevo');
  // el arte nuevo LLEGA AL SUELO: comprobado con PIL en la generación
  // (v_bottom 0.006 ≈ el ras de las casas buenas 0.001-0.008); aquí queda
  // la config que lo apoya:
  ok(ASEDIO.edif.y === -0.10, 'F3 las casas nacen hundidas 10 cm (edif.y)');
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/v: 0\.114, u0: 0\.100, u1: 0\.907, n: 4/.test(src),
    'F4 la línea verde de zonas2.jpg re-medida (v 0.114) en el código');
}

/* ============ G · SANGRE: regresión v2.116 =============================== */
{
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/this\.splat\.position\.set\(\s*\(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G1 el salpicadón del visor CAMBIA DE SITIO en cada disparo');
  ok(/this\.splat\.rotation\.z = \(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G2 el salpicadón CAMBIA DE GIRO en cada disparo');
}

console.log(fails === 0 ? '════ TODO OK v2.117 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

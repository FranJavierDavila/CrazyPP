// Prueba headless v2.118 (oeste) — AJUSTES DEL ARTISTA:
//  A) CONFIG: túnel sin nacer cerca de la estación (bloquea 30 s) · poderes
//     8 s · estacionY (arte al suelo) · manifest 37 · VERSION 2.118.0;
//  B) PARADAS: PARADA N ↔ PARADAn.png + CADA arte a SU altura (posición.y);
//  C) TÚNEL: cosido (regresión) + bocas entrada NORMAL/salida ESPEJADA en
//     las DOS paredes + guard de estación (no nace cerca, se retira al llegar);
//  D) ESTRELLA: disparo de revólver la caza (regresión v2.117);
//  E) PISTOLA DE LA ESTRELLA (clase real ForajidoStand): aparece → pala→
//     revólver en la mano libre; desaparece → pala; los revólveres de diana
//     toman el relevo; _gunLoaded/_gunRayHand la atienden;
//  F) INTEGRACIÓN ASEDIO: _starSpawn monta la pistola y _starHide la retira;
//  G/H) MARCADOR REAL + CASA AL SUELO + SANGRE (regresiones v2.117);
//  I) HUD CLARO: canvas 640×280, HUD a y 2.52, progreso corto, mensajes a 2
//     líneas, cartel de oleada a y 1.38 (no tapa el banderín).
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
    if (k === 'measureText') return (s) => ({ width: String(s).length * 12 });
    if (k === 'createLinearGradient' || k === 'createRadialGradient') {
      return () => ({ addColorStop: () => {} });
    }
    if (k === 'getImageData') {
      return (x, y, w, h) => ({ data: new Uint8ClampedArray(w * h * 4) });
    }
    if (k === 'fillText') {
      return (txt, x, y) => { FILLS.push({ t: String(txt), x: x || 0, y: y || 0 }); };
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
let starCalls = [];
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
  _starGunApply(on) { starCalls.push(on); },
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  paintCartel() {}, _refreshMap() {},
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
};
game.rig.add(new THREE.Group());

const Tren = mod.TrenAction;
const TREN = mod.TREN;
const ASEDIO = mod.ASEDIO;
const AsedioAction = mod.AsedioAction;
const ForajidoStand = mod.ForajidoStand;
if (!Tren || !TREN) throw new Error('TrenAction/TREN no exportados');
if (!ASEDIO || !AsedioAction) throw new Error('ASEDIO/AsedioAction no exportados');
if (!ForajidoStand) throw new Error('ForajidoStand no exportado (pruebas)');
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

/* ============ A · CONFIG v2.118 ========================================= */
{
  const TU = TREN.tunel;
  ok(TU.bloquea === 30.0,
    'A1 bloquea=30 s: NINGÚN túnel cuando la parada está cerca');
  ok(TU.zIn === -12.0 && TU.bh === 3.4 && TU.len === 26.4,
    'A2 regresión túnel v2.117 (zIn -12 · bocas 3,4 · banda 26,4)');
  ok(TREN.poder.vida === 8.0,
    'A3 superpoderes 8 s en escena (antes 5)');
  ok(TREN.estacionY && TREN.estacionY[1] === 1.85 &&
     TREN.estacionY[2] === 1.95 && TREN.estacionY[3] === 1.85,
    'A4 estacionY SUBIDAS v2.119 (1.85 / 1.95 / 1.85)');
  ok(ASEDIO.banner.y === 1.38, 'A5 cartel de oleada a y 1.38 (no tapa el HUD)');
  const idx = fs.readFileSync('/home/z/my-project/game/index.html', 'utf8');
  ok(/const VERSION = '2\.119\.0'/.test(idx), 'A6 index.html VERSION 2.119.0');
  const man = JSON.parse(fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/manifest.json', 'utf8'));
  ok(man.version === 38 && !!man.note_v2119, 'A7 manifest versión 38 + note_v2119');
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/_starGunApply\(on\)/.test(src) && /_starGunRec/.test(src),
    'A8 pistola de la estrella implementada (_starGunApply/_starGunRec)');
  ok(/this\._tunnelT <= 0 && this\.time > TU\.bloquea/.test(src),
    'A9 el guard del túnel consulta el reloj de la parada');
}

/* ============ B · PARADAS: SU arte y SU altura =========================== */
{
  const t = new Tren(ctrl);
  t.start();
  const urls = global.__IMG_URLS = [];
  const yByN = { 1: 1.85, 2: 1.95, 3: 1.85 };   // v2.119: estaciones SUBIDAS
  const tick = () => new Promise((r) => setTimeout(r, 5));
  try {
    for (const i of [1, 2, 3, 0]) {
      t._paradaTry = {};
      t._paradaTex = {};    // sin caché: cada índice pide SU url
      t._signArt(i);        // v2.119: carga vía Image (async) → esperar tick
      await tick();
      const n = (i >= 1 && i <= 3) ? i : 1;
      ok(Math.abs(t.estArt[0].position.y - yByN[n]) < 1e-6,
        'B-y PARADA' + n + ' a y ' + yByN[n] + ' (subida, cuerpo en la ventana)');
    }
  } finally { global.__IMG_URLS = null; }
  const num = (u) => (u.match(/PARADA(\d)\.png$/) || [])[1];
  ok(num(urls[0]) === '1' && num(urls[1]) === '2' && num(urls[2]) === '3' &&
     num(urls[3]) === '1',
    'B1 parada 1/2/3 → PARADA1/2/3 y salida → PARADA1 (pedidos: ' +
    urls.map(num).join(',') + ')');
  t.dispose();
}

/* ============ C · TÚNEL: cosido + bocas + guard de estación ============== */
{
  const t = new Tren(ctrl);
  t.start();
  const TU = TREN.tunel;
  const bocas = t.tunelGrp.children.filter((m) => m.userData && m.userData.boca);
  const bandas = t.tunelGrp.children.filter((m) => !(m.userData && m.userData.boca));
  ok(bocas.length === 4 && bandas.length === 2,
    'C1 4 bocas (2 por lado) + 2 bandas');
  const bocaIn = bocas.filter((m) => Math.abs(m.position.z) < 1e-6);
  const bocaOut = bocas.filter((m) => m.position.z < -1);
  ok(bocaIn.length === 2 &&
     bocaIn[0].scale.x * bocaIn[1].scale.x === -1,
    'C2 v2.119: entrada cosida por u=1 en AMBAS paredes (signos opuestos)');
  ok(bocaOut.length === 2 &&
     bocaOut[0].scale.x * bocaOut[1].scale.x === -1 &&
     bocaOut[0].scale.x === -bocaIn[0].scale.x,
    'C3 v2.119: salida con el signo INVERTIDO respecto a la entrada (izq)');
  const banda = bandas[0];
  const bandaIni = banda.position.z + TU.len / 2;
  const bandaFin = banda.position.z - TU.len / 2;
  ok(Math.abs(bandaIni - (-TU.bh / 2)) < 1e-6,
    'C4 banda COSIDA a la boca de entrada (' + bandaIni.toFixed(3) + ')');
  ok(Math.abs(bandaFin - (-(TU.len + TU.bh) + TU.bh / 2)) < 1e-6,
    'C4b boca de salida COSIDA al final de la banda (' + bandaFin.toFixed(3) + ')');
  // flujo de fases POR DISTANCIA (regresión)
  t.phase = 'run'; t._depart();
  t.v = TREN.vMax;
  t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'C5 pre al arrancar con la parada LEJOS (120 s)');
  t._tunelZ = TU.ojo + TU.bh / 2 + 0.05;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'in', 'C6 in al pasar el ojo');
  let g2 = 0;
  while (t._tunnelPhase === 'in' && g2++ < 200) { t.step(dt); t.fxStep(dt); }
  ok(t._tunnelPhase === 'dur', 'C6b tras el fundido (1,6 s) llega dur');
  t._tunelZ = TU.len + TU.bh / 2 - TU.ver + 0.05;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'out', 'C7 out al asomar la boca de salida');
  t._tunnelPhase = 'none'; t.fxStep(dt);
  ok(!t.tunelGrp.visible, 'C8 al salir, el túnel se retira');
  // v2.118 · GUARD DE ESTACIÓN
  t.time = 25; t._tunnelT = 0.01; t._tunnelPhase = 'none';
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'none',
    'C9 NO nace túnel con la parada cerca (25 s < bloquea 30)');
  t.time = 100; t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'C10 SÍ nace con la parada lejos (100 s)');
  t._tunnelPhase = 'in'; t.tunelGrp.visible = true;
  t.time = 0.05;
  t._llegaEstacion();
  ok(t._tunnelPhase === 'none' && !t.tunelGrp.visible,
    'C11 al LLEGAR la estación, cualquier túnel vivo se retira (nunca solapa)');
  ok(t._tunnelT >= 12, 'C12 el próximo túnel espera ≥12 s tras la llegada');
  t.dispose();
}

/* ============ D · ESTRELLA POR REVÓLVER (regresión v2.117) =============== */
{
  const a = new AsedioAction(ctrl);
  let err = '';
  try { a.start(); } catch (e) { err = e.message; }
  if (err && !/tex|load/i.test(err)) console.log('   (start asedio: ' + err + ')');
  ok(Array.isArray(a.edif) && a.edif.length === 3, 'D1 el pueblo tiene 3 edificios');
  a.phase = 'play';
  a._spawnTarget();
  ok(a._zona && a.dianaGrp && a.dianaGrp.visible,
    'D1b diana viva en zona verde (contexto del destape)');
  a._starT = 0.01;
  a._starStep(dt);
  ok(a._star && a._star.grp.visible, 'D2 la estrella aparece');
  ok(starCalls[starCalls.length - 1] === true,
    'D2b al aparecer, el asedio pide la PISTOLA (pala→revólver)');
  const sp = a._star.grp.position.clone();
  a.time = 100;
  gunRemoved = [];
  a._shotAt(sp.clone().setZ(sp.z + 5), new THREE.Vector3(0, 0, -1), 0);
  ok(Math.abs(a.time - 112) < 1e-6, 'D3 ¡el disparo CAZA la estrella! +12 s');
  ok(!a._star.grp.visible, 'D4 la estrella se recoge al ser cazada');
  ok(gunRemoved.indexOf(0) >= 0, 'D5 el revólver de diana se gasta al cazarla');
  a._starSpawn();
  a.time = 50;
  gunRemoved = [];
  a._shotAt(new THREE.Vector3(50, 50, 50), new THREE.Vector3(0, 0, -1), 1);
  ok(Math.abs(a.time - 50) < 1e-6 && a._star.grp.visible,
    'D6 un disparo fuera NO la caza');
  ok(gunRemoved.indexOf(1) >= 0, 'D7 …pero el revólver sí se gasta (disparo normal)');
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/asedio_estrella: '¡ESTRELLA DEL SHERIFF! ¡DALE CON UNA BOMBA O CON EL REVÓLVER!'/.test(src),
    'D8 aviso ES «BOMBA O REVÓLVER»');
  ok(/asedio_estrella: 'SHERIFF STAR! HIT IT WITH A BOMB OR THE REVOLVER!'/.test(src),
    'D9 aviso EN «BOMB OR THE REVOLVER»');
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ E · PISTOLA DE LA ESTRELLA (clase real) ==================== */
{
  const st = new ForajidoStand(game, {});
  st.game = game;
  st._revolverModel = new THREE.Group();   // clone(true) válido; sin cañón medible
  game.gunMounts = [new THREE.Group(), new THREE.Group()];
  game.paddleMounts = [new THREE.Group(), new THREE.Group()];
  game.paddleHand = 1;
  const pad = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.1, 0.1),
    new THREE.MeshBasicMaterial());
  pad.visible = true;
  game.paddleMounts[0].add(pad);
  st._starGunApply(true);
  ok(st._starGunRec && st._starGunRec.hand === 0,
    'E1 pistola de la estrella en la mano LIBRE (0)');
  ok(!pad.visible, 'E2 la PALA de esa mano se OCULTA');
  ok(st._starGunRec.art && st._starGunRec.mount === game.gunMounts[0],
    'E3 revólver montado en la montura de esa mano');
  ok(st._gunLoaded(0) === true && st._gunLoaded(1) === false,
    'E4 _gunLoaded: la mano armada no golpea con pala');
  st._twoGunApply(true);
  ok(st._starGunRec === null,
    'E5 al DESTAPARSE un forajido, la pistola de la estrella se retira limpia');
  ok(Array.isArray(st._twoGuns) && st._twoGuns.length === 2,
    'E6 los DOS revólveres de diana toman el relevo');
  st._twoGunApply(false);
  ok(pad.visible, 'E7 la pala vuelve al retirar los revólveres de diana');
  st._starGunApply(true);
  ok(st._starGunRec && st._starGunRec.art, 'E8 la estrible vuelve a dar su pistola');
  st._starGunApply(false);
  ok(st._starGunRec === null && pad.visible,
    'E9 al DESAPARECER la estrella vuelve la pala');
  // el rayo por mano atiende a la pistola de la estrella (con cañón medible
  // devolvería WYSIWYG; con el modelo vacío devuelve null sin romper)
  ok(st._gunRayHand(0) === null, 'E10 _gunRayHand sin cañón medible → null (sin crash)');
}

/* ============ F · INTEGRACIÓN ASEDIO: montar/retirar ===================== */
{
  const a = new AsedioAction(ctrl);
  try { a.start(); } catch (e) { /* */ }
  a.phase = 'play';
  a._spawnTarget();
  starCalls = [];
  a._starT = 0.01;
  a._starStep(dt);                       // spawn
  ok(starCalls.indexOf(true) >= 0, 'F1 _starSpawn monta la pistola');
  a._starHide();
  ok(starCalls[starCalls.length - 1] === false,
    'F2 _starHide retira la pistola (vuelve la pala)');
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ G · MARCADOR REAL + CASA + SANGRE (regresión) ============== */
{
  ok(md5(GA + 'contador.png') ===
     '8ece8ff69a0eceea431c5864084b60c0',
    'G1 contador.png = el arte REAL del artista (md5 registrado)');
  ok(md5(GA + 'contador.png') !== md5(BA + 'contador.png'),
    'G2 …diferente al letrero regenerado de beta1');
  ok(fs.existsSync(GA + 'reloj.png'), 'G3 reloj.png en assets');
  ok(md5(GA + 'decor/asedio/fachada2.webp') !== md5(BA + 'decor/asedio/fachada2.webp'),
    'G4 fachada2 sustituida (regresión casa al suelo)');
  const src = fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/this\.splat\.position\.set\(\s*\(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G5 sangre: el salpicadón cambia de sitio (regresión)');
  ok(/this\.splat\.rotation\.z = \(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G6 sangre: el salpicadón cambia de giro (regresión)');
}

/* ============ H · HUD DEL ASEDIO CLARO =================================== */
{
  const a = new AsedioAction(ctrl);
  try { a.start(); } catch (e) { /* */ }
  ok(a._hud && Math.abs(a._hud.group.position.y - 2.52) < 1e-6,
    'H1 HUD subido a y 2.52 (fuera del alcance del cartel)');
  ok(a._hud.cv.height === 280, 'H2 canvas del HUD 640×280 (banderín de 2 líneas)');
  ok(a._prog() === 'OLEADA 1/3',
    'H3 progreso corto «OLEADA 1/3» — sin duplicar la cuenta del marcador');
  // banderín: mensaje LARGO → 2 líneas apiladas
  FILLS.length = 0;
  a._hud.msg = 'ASEDIO AL ESCONDITE · revienta las FACHADAS con las BOMBAS y remata con los REVOLVERES';
  a._hud._dirty = true;
  a._hud._paint();
  const penn = FILLS.filter((f) => f.y > 120);
  ok(penn.length === 2, 'H5 el mensaje largo se ENVUELVE a 2 líneas (' +
    penn.length + ' líneas)');
  if (penn.length === 2) {
    ok(penn[1].y - penn[0].y > 20,
      'H6 líneas apiladas (y ' + penn[0].y + ' → ' + penn[1].y + ')');
  }
  // mensaje corto → 1 línea
  FILLS.length = 0;
  a._hud.msg = '¡OLEADA 1!';
  a._hud._dirty = true;
  a._hud._paint();
  ok(FILLS.filter((f) => f.y > 120).length === 1, 'H7 mensaje corto → 1 línea');
  try { a.dispose(); } catch (e) { /* */ }
}

console.log(fails === 0 ? '════ TODO OK v2.118 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

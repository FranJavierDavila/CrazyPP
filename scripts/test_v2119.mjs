// Prueba headless v2.119 (oeste) — CORRECCIONES + RANKING CON SENTIDO:
//  A) CONFIG: estacionY SUBIDAS (1.85/1.95/1.85) · pies del parallax · config
//     del indio · bloquea 30 (regresión) · poderes 8 (regresión) · VERSION
//     2.119.0 · manifest 38 + note_v2119;
//  B) PARADAS: PARADA N ↔ PARADAn.png a SU altura NUEVA (carga async Image);
//  C) TÚNEL: cosido + BOCAS POR PARED (u=1 siempre hacia la banda: izq
//     entrada normal/salida espejada · der entrada espejada/salida normal)
//     + guard de estación (regresión v2.118);
//  D) ESTRELLA: la pistola de la estrella NO se come los revólveres del
//     destape (el bug del artista) + regresión revólver de diana;
//  E) INDIO CABALGANTE: pool 3, spawn de grupo 1-3, mirilla SIEMPRE, flecha
//     que roba lingote, alcanzado→fade, gates (forajido/túnel/llegada);
//  F) PUNTOS: _puntosAdd real (persistencia + pop), HUD chip, ranking p:puntos;
//  G) REGRESIONES: contador.png, casa, sangre, HUD claro.
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
const STORE = {};
global.localStorage = {
  getItem: (k) => (k in STORE ? STORE[k] : null),
  setItem: (k, v) => { STORE[k] = String(v); },
  removeItem: (k) => { delete STORE[k]; },
};

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
let puntosCalls = [];
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
  // stub REALISTA de revólveres: _twoGunApply monta 2 y retira la pistola
  _twoGuns: null,
  _starGunRec: null,
  _starGunApply(on) {
    starCalls.push(on);
    if (on) this._starGunRec = { hand: 1 - game.paddleHand, art: true };
    else this._starGunRec = null;
  },
  _twoGunApply(on) {
    if (on) {
      this._starGunRec = null;                 // la pistola cede la mano
      this._twoGuns = [{ hand: 0, art: true }, { hand: 1, art: true }];
    } else this._twoGuns = null;
  },
  _gunHandRemove(hand) {
    gunRemoved.push(hand);
    if (this._twoGuns) {
      this._twoGuns = this._twoGuns.filter((r) => r.hand !== (hand | 0));
    }
  },
  _twoPaddles() {}, _playWaveJingle() {},
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  paintCartel() {}, _refreshMap() {},
  // v2.119: API de puntos (grabable)
  puntos: 0,
  _puntosAdd(n) { puntosCalls.push(n | 0); this.puntos = (this.puntos | 0) + (n | 0); },
  _puntosStep() {},
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
const SRC = fs.readFileSync(
  '/home/z/my-project/game/championships/oeste/index.js', 'utf8');
const tick = () => new Promise((r) => setTimeout(r, 8));

/* ============ A · CONFIG v2.119 ========================================= */
{
  const I = TREN.indio;
  ok(!!I && I.total === 6 && I.grupoMax === 3 && I.sepZ === 0.95,
    'A1 config del indio (6 grupos · hasta 3 jinetes · sep 0.95)');
  ok(I.yBase === 1.75 && I.h === 1.70 && I.atkT === 3.2,
    'A2 el indio cabalga en la PARTE MEDIA de la ventana (y 1.75)');
  ok(TREN.estacionY[1] === 1.85 && TREN.estacionY[2] === 1.95 &&
     TREN.estacionY[3] === 1.85,
    'A3 estacionY SUBIDAS (1.85 / 1.95 / 1.85) — fin del «sólo el techo»');
  const P = TREN.spawn.planes;
  ok(P[0].feet === -2.2 && P[1].feet === -0.6 && P[2].feet === 0.35,
    'A4 pies del parallax SUBIDOS (P2 -2.2 · P3 -0.6 · P4 +0.35)');
  ok(TU_bloquea() === 30.0, 'A5 regresión: sin túnel cerca de la estación (30 s)');
  ok(TREN.poder.vida === 8.0, 'A6 regresión: superpoderes 8 s');
  const idx = fs.readFileSync('/home/z/my-project/game/index.html', 'utf8');
  ok(/const VERSION = '2\.119\.0'/.test(idx), 'A7 index.html VERSION 2.119.0');
  const man = JSON.parse(fs.readFileSync(
    '/home/z/my-project/game/championships/oeste/manifest.json', 'utf8'));
  ok(man.version === 38 && !!man.note_v2119, 'A8 manifest versión 38 + note_v2119');
  ok(/indio1\.png/.test(SRC) && /indioalcanzado\.png/.test(SRC),
    'A9 el módulo usa indio1-4.png e indioalcanzado.png');
  ok(fs.existsSync(GA + 'indio1.png') && fs.existsSync(GA + 'indio4.png') &&
     fs.existsSync(GA + 'indioalcanzado.png'), 'A10 assets del indio presentes');
}
function TU_bloquea() { return TREN.tunel.bloquea; }

/* ============ B · PARADAS: SU arte y SU altura NUEVA ===================== */
{
  const t = new Tren(ctrl);
  t.start();
  const urls = global.__IMG_URLS = [];
  const yByN = { 1: 1.85, 2: 1.95, 3: 1.85 };
  try {
    for (const i of [1, 2, 3, 0]) {
      t._paradaTry = {};
      t._paradaTex = {};
      t._signArt(i);          // v2.119: carga vía Image (async)
      await tick();
      const n = (i >= 1 && i <= 3) ? i : 1;
      ok(Math.abs(t.estArt[0].position.y - yByN[n]) < 1e-6,
        'B-y PARADA' + n + ' SUBIDA a y ' + yByN[n]);
      ok(!!t._paradaTex[n] && t._paradaTex[n].isCanvasTexture === true,
        'B-cv PARADA' + n + ' sobre lienzo (huecos cerrados)');
    }
  } finally { global.__IMG_URLS = null; }
  const num = (u) => (u.match(/PARADA(\d)\.png$/) || [])[1];
  ok(num(urls[0]) === '1' && num(urls[1]) === '2' && num(urls[2]) === '3' &&
     num(urls[3]) === '1',
    'B1 mapeo parada N → PARADAn.png (regresión)');
  t.dispose();
}

/* ============ C · TÚNEL: bocas POR PARED + guard ========================= */
{
  const t = new Tren(ctrl);
  t.start();
  const TU = TREN.tunel;
  const bocas = t.tunelGrp.children.filter((m) => m.userData && m.userData.boca);
  const bandas = t.tunelGrp.children.filter((m) => !(m.userData && m.userData.boca));
  ok(bocas.length === 4 && bandas.length === 2, 'C1 4 bocas + 2 bandas');
  const bocaIn = bocas.filter((m) => Math.abs(m.position.z) < 1e-6);
  const bocaOut = bocas.filter((m) => m.position.z < -1);
  const izq = (m) => m.position.x < 0;
  ok(bocaIn.length === 2 && bocaOut.length === 2, 'C1b entrada y salida por pared');
  // v2.119 · COSIDO POR u=1: en la IZQUIERDA u=1 mira a -z (hondo) → entrada
  // normal (+1) y salida espejada (-1); en la DERECHA u=1 mira a +z → INVERTIDO
  const inL = bocaIn.find(izq), inR = bocaIn.find((m) => !izq(m));
  const outL = bocaOut.find(izq), outR = bocaOut.find((m) => !izq(m));
  ok(inL.scale.x === 1 && inR.scale.x === -1,
    'C2 entrada cosida por u=1: IZQ normal (+1) · DER espejada (-1)');
  ok(outL.scale.x === -1 && outR.scale.x === 1,
    'C3 salida cosida por u=1: IZQ espejada (-1) · DER normal (+1)');
  ok(inL.scale.x === -outL.scale.x && inR.scale.x === -outR.scale.x,
    'C3b en cada pared, salida = espejo de entrada (el arco SIEMPRE a la banda)');
  const banda = bandas[0];
  const bandaIni = banda.position.z + TU.len / 2;
  const bandaFin = banda.position.z - TU.len / 2;
  ok(Math.abs(bandaIni - (-TU.bh / 2)) < 1e-6, 'C4 banda cosida a la entrada');
  ok(Math.abs(bandaFin - (-(TU.len + TU.bh) + TU.bh / 2)) < 1e-6,
    'C4b banda cosida a la salida (regresión)');
  t.phase = 'run'; t._depart();
  t.v = TREN.vMax; t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'C5 fases por distancia (regresión)');
  t._tunnelPhase = 'none'; t.fxStep(dt);
  t.time = 25; t._tunnelT = 0.01; t._tunnelPhase = 'none';
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'none', 'C6 sin túnel con la parada cerca (regresión)');
  t.dispose();
}

/* ============ D · ESTRELLA: la pistola NO se come el destape ============== */
{
  const a = new AsedioAction(ctrl);
  try { a.start(); } catch (e) { /* */ }
  a.phase = 'play';
  a._spawnTarget();
  ok(a._zona && a.dianaGrp && a.dianaGrp.visible, 'D1 diana viva (contexto)');
  a._starT = 0.01;
  a._starStep(dt);
  ok(a._star && a._star.grp.visible, 'D2 la estrella aparece');
  ok(ctrl._starGunRec && ctrl._starGunRec.art === true,
    'D2b la estrella dio su pistola (stub realista)');
  // CASO NUEVO: disparar a la estrella CON LA PISTOLA DE LA ESTRELLA
  const sp = a._star.grp.position.clone();
  a.time = 100;
  gunRemoved = [];
  ctrl._twoGuns = null;                       // sin revólveres de diana aún
  a._shotAt(sp.clone().setZ(sp.z + 5), new THREE.Vector3(0, 0, -1), 0);
  ok(Math.abs(a.time - 112) < 1e-6, 'D3 la pistola de la estrella la CAZA (+12 s)');
  ok(ctrl._twoGuns && ctrl._twoGuns.length === 2,
    'D4 el destape monta DOS revólveres frescos');
  ok(gunRemoved.length === 0,
    'D5 ★ el disparo que cazó la estrella NO gasta ninguno (bug v2.118 arreglado)');
  ok(ctrl._starGunRec === null, 'D6 la pistola de la estrella cede la mano limpia');
  // REGRESIÓN: disparar a la estrella con un REVÓLVER DE DIANA sí se gasta
  a._starSpawn();
  ctrl._twoGunApply(true);                    // 2 revólveres montados
  a.time = 50;
  gunRemoved = [];
  const sp2 = a._star.grp.position.clone();
  a._shotAt(sp2.clone().setZ(sp2.z + 5), new THREE.Vector3(0, 0, -1), 1);
  ok(Math.abs(a.time - 62) < 1e-6 && !a._star.grp.visible,
    'D7 el revólver de diana TAMBIÉN la caza (+12 s)');
  ok(gunRemoved.indexOf(1) >= 0,
    'D8 …y ese revólver SÍ se gasta (regresión v2.117)');
  ctrl._twoGunApply(false);
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ E · EL INDIO CABALGANTE ==================================== */
{
  const t = new Tren(ctrl);
  t.start();
  ok(t._indPool && t._indPool.length === 3, 'E1 pool de 3 jinetes');
  ok(t._indNext === 14.0 && t._indCount === 0, 'E2 agenda del indio a 14 s');
  // aparecen SOLO si el forajido NO está
  t.phase = 'run'; t._depart();
  t._fjState = 'ventana';                     // forajido EN pantalla
  t._indNext = 0.01; t._tunnelPhase = 'none';
  for (let i = 0; i < 12; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._inds.length === 0 && t._indCount === 0,
    'E3 NO salen indios mientras el forajido está en la ventana');
  ok(t._indNext >= 0.01 - 1e-6, 'E3b la agenda del indio no corre tampoco');
  // forajido fuera → salen (grupo 1..3)
  t._fjState = 'off'; t._fjNext = 999;
  t._indNext = 0.01;
  for (let i = 0; i < 6; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._inds.length >= 1 && t._inds.length <= 3,
    'E4 grupo de 1-3 indios en pantalla (' + t._inds.length + ')');
  ok(t._indCount === 1, 'E5 cuenta de grupos +1');
  ok(t._indAny === true, 'E6 _indAny activo (pausa al forajido)');
  ok(t._inds.every((r) => r.diana.visible),
    'E7 MIRILLA SIEMPRE encima (visible desde que aparecen)');
  ok(t._inds.every((r) => r.grp.visible), 'E8 los jinetes son visibles');
  const zs = t._inds.map((r) => r.zAtk).sort((x, y) => x - y);
  if (zs.length >= 2) {
    ok(Math.abs((zs[1] - zs[0]) - TREN.indio.sepZ) < 1e-6,
      'E9 grupo «ligeramente separado» (sep ' + (zs[1] - zs[0]).toFixed(2) + ')');
  } else ok(true, 'E9 grupo de 1 (sin separación que medir)');
  ok(t._inds.every((r) => Math.abs(r.grp.position.y - TREN.indio.yBase) < 0.12),
    'E10 cabalgan a la parte media de la ventana');
  // mientras cabalgan los indios, el FORAJIDO no agenda
  const fjNext0 = t._fjNext;
  for (let i = 0; i < 20; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._fjNext === fjNext0,
    'E11 la agenda del FORAJIDO se pausa con indios en pantalla');
  // a la ventana: soltan flecha y ROBAN si hay lingotes
  for (const r of t._inds) { r.state = 'ventana'; r.t = TREN.indio.atkT - 0.01; }
  t.ingots = 2;
  const ingote = {
    mesh: new THREE.Group(), volando: false, robado: false,
    robo: 0, roboT: 0, base: new THREE.Vector3(), spin: 1,
    v: new THREE.Vector3(),
  };
  t.ingotes.push(ingote);
  for (let i = 0; i < 4; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._flechas.length >= 1, 'E12 el indio suelta su FLECHA');
  const t0 = performance.now();
  let guard = 0;
  while (t.ingots === 2 && guard++ < 90) { t.step(dt); t.fxStep(dt); }
  ok(t.ingots === 1,
    'E13 la flecha ROBA un lingote (mismo efecto que el forajido) en ' +
    ((performance.now() - t0) / 1000).toFixed(2) + ' s de banco');
  ok(ingote.robado === true, 'E13b el lingote queda marcado robado');
  // derribarlos: alcanzado → fade → fuera
  puntosCalls = [];
  const rec0 = t._inds[0];
  t._indHerido(rec0);
  ok(rec0.state === 'alcanzado' && !rec0.diana.visible,
    'E14 al darle: indioalcanzado + mirilla fuera');
  ok(puntosCalls.indexOf(150) >= 0, 'E15 indio alcanzado = +150 puntos');
  for (let i = 0; i < 130 && t._inds.length; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._inds.length === 0 && t._indAny === false,
    'E16 tras el fundido, el jinete se desvanece y la agenda reprograma');
  // túnel: fuera los indios
  t._indNext = 0.01;
  for (let i = 0; i < 6; i++) { t.step(dt); t.fxStep(dt); }
  ok(t._inds.length >= 1, 'E16b contexto: grupo vivo');
  t._tunnelPhase = 'in';
  t.step(dt); t.fxStep(dt);
  ok(t._inds.length === 0, 'E17 EN EL TÚNEL no hay indios (como el forajido)');
  t._tunnelPhase = 'none';
  // llegada a la estación: huyen
  t._indNext = 0.01;
  for (let i = 0; i < 6; i++) { t.step(dt); t.fxStep(dt); }
  t._indFleeAll();
  ok(t._inds.every((r) => r.state === 'fuga' || r.state === 'gone'),
    'E18 en la llegada al andén los indios HUYEN');
  t.dispose();
}

/* ============ F · PUNTOS COHERENTES CON EL RANKING ======================== */
{
  const st = new ForajidoStand(game, {});
  st.group = new THREE.Group();   // build() ligero para el pool de pops
  const p0 = st.puntos | 0;
  st._puntosAdd(100, new THREE.Vector3(0, 1, 0));
  ok(st.puntos === p0 + 100, 'F1 _puntosAdd suma y persiste (' + st.puntos + ')');
  ok(STORE['pp_champ_oeste_puntos'] === String(st.puntos),
    'F2 persistencia pp_champ_oeste_puntos');
  ok(st._pops.length === 1 && st._pops[0].viva && st._pops[0].spr.visible,
    'F3 el «+N» dorado flota (pool visible)');
  for (let i = 0; i < 80; i++) st._puntosStep(dt);
  ok(!st._pops[0].viva && !st._pops[0].spr.visible,
    'F4 el pop sube y se desvanece (1.15 s)');
  // HUD: chip de puntos
  const a = new AsedioAction(ctrl);
  try { a.start(); } catch (e) { /* */ }
  FILLS.length = 0;
  a._hud.set(60, 'OLEADA 1/3', '', undefined, undefined, 1230);
  ok(a._hud.pts === 1230, 'F5 HUD recibe los puntos (set 6º parámetro)');
  ok(FILLS.some((f) => f.t === '1230'),
    'F6 el chip de estrella pinta «1230» en el banderín');
  // ranking: publica PUNTOS (dos sitios: campeón + victoria de duelo)
  const subs = SRC.match(/W\.submit\('oeste'[\s\S]{0,120}?p: this\.puntos \| 0/g) || [];
  ok(subs.length === 2,
    'F7 el ranking publica p: PUNTOS en campeón y duelo (' + subs.length + ')');
  ok(/rank\.push\(\{ w, score: g\.rules\.scorePlayer \| 0, stars: w \? 1 : 0, duel: true, pts: this\.puntos \| 0 \}\)/.test(SRC),
    'F8 los registros locales guardan pts');
  // tabla de valores del diseño
  ok(/_puntosAdd\(100/.test(SRC) && /_puntosAdd\(150/.test(SRC) &&
     /_puntosAdd\(200/.test(SRC) && /_puntosAdd\(300/.test(SRC) &&
     /_puntosAdd\(20/.test(SRC) && /_puntosAdd\(25/.test(SRC) &&
     /_puntosAdd\(250/.test(SRC),
    'F9 valores del sistema presentes (20/25/100/150/200/250/300)');
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ G · REGRESIONES v2.117/v2.118 =============================== */
{
  ok(md5(GA + 'contador.png') === '8ece8ff69a0eceea431c5864084b60c0',
    'G1 contador.png = arte real del artista');
  ok(md5(GA + 'decor/asedio/fachada2.webp') !== md5(BA + 'decor/asedio/fachada2.webp'),
    'G2 casa corregida (regresión)');
  ok(/this\.splat\.position\.set\(\s*\(Math\.random\(\) \* 2 - 1\)/.test(SRC),
    'G3 sangre aleatoria (regresión)');
  const a = new AsedioAction(ctrl);
  try { a.start(); } catch (e) { /* */ }
  ok(a._hud && Math.abs(a._hud.group.position.y - 2.52) < 1e-6,
    'G4 HUD a y 2.52 (regresión)');
  ok(a._hud.cv.height === 280, 'G5 canvas HUD 640×280 (regresión)');
  ok(ASEDIO.banner.y === 1.38, 'G6 cartel de oleada a y 1.38 (regresión)');
  try { a.dispose(); } catch (e) { /* */ }
}

console.log(fails === 0 ? '════ TODO OK v2.119 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

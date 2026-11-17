// Prueba headless v2.115 (oeste/tren):
//  A) ESTACIONES DEL ARTISTA: PARADA por índice (0→1, 1→2, 2→3, 3→1) y el
//     arte SUSTITUYE al andén procedural (piezas viejas ocultas);
//  B) PIRÁMIDE SEPARADA 1/4 del tamaño desde el principio (y soportes sanos);
//  C) LAS PELOTAS NACEN CADA SEGUNDO (pool multi-bola, max 6) y mueren fuera;
//  D) SUPERPODERES: medallón en la mesa rival, 3 s visible, cadencia ≥15 s;
//  E) POWERCAJAS: lluvia de 5 con física que SE APILA (y máx 30 con explosiones);
//  F) POWERX3: la bola se convierte en 3 con caminos distintos;
//  G) POWERDINAMITA: bola-bomba oscura que revienta el cajón y su radio;
//  H) TÚNEL: boca+banda viajan con el mundo y la luz de la escena baja al 20 %.
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';

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
global.document = {
  createElementNS: () => ({
    addEventListener() {}, removeEventListener() {},
    set src(v) { setTimeout(() => this.onload && this.onload(), 0); },
    width: 4, height: 4,
  }),
  createElement: () => ({
    width: 0, height: 0, getContext: () => new Proxy({}, {
      get: (t, k) => {
        if (k === 'measureText') return () => ({ width: 10 });
        if (k === 'createLinearGradient' || k === 'createRadialGradient') {
          return () => ({ addColorStop: () => {} });
        }
        return () => {};
      },
      set: () => true,
    }),
  }),
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
let smokes = 0, maderas = 0, booms = 0, flashes = 0;
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: {
    texDot: new THREE.Texture(),
    update() {}, flash() { flashes++; }, spark() {},
    smoke() { smokes++; }, smokeGun() {}, beam() {}, laserVisible() {},
  },
  sfx(n) { if (n === 'madera') maderas++; if (n === 'boom') booms++; },
  musicOn() {},
  _parkMainBall() {}, _findNetParts() { return []; },
  _netParts: [], _revolverModel: null, _revInHand: null,
  _gunRay() { return null; },
  _freeGunApply() {},
  _gunVisible() {}, _endTren() {}, _stageClear() {},
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
  paintCartel() {}, _refreshMap() {},
};
game.rig.add(new THREE.Group());

const Tren = mod.TrenAction;
const TREN = mod.TREN;
if (!Tren) throw new Error('TrenAction no exportado');
if (!TREN) throw new Error('TREN no exportado');
const dt = 1 / 60;
let fails = 0;
const ok = (cond, msg) => {
  console.log((cond ? '★ ' : '✗ ') + msg);
  if (!cond) fails++;
};
const vivos = (t) => t.cubos.filter((r) => !r.muerto).length;

/* ============ A · ESTACIONES DEL ARTISTA (PARADA1..3) =================== */
{
  const t = new Tren(ctrl);
  t.start();
  ok(t.estArt && t.estArt.length === 2, 'A1 hay 2 planos de estación (uno por lado)');
  // v2.117 · mapeo REAL vía _signArt: la parada N pide SU PARADAn.png
  // (0=estación de salida → PARADA1)
  const urls = global.__IMG_URLS = [];   // v2.119: _signArt carga vía Image
  try {
    t._paradaTex = {}; t._paradaTry = {};
    t._signArt(1);
    t._paradaTex = {}; t._paradaTry = {};   // relanza cada índice limpio
    t._signArt(2);
    t._paradaTex = {}; t._paradaTry = {};
    t._signArt(3);
    t._paradaTex = {}; t._paradaTry = {};
    t._signArt(0);
  } finally { global.__IMG_URLS = null; }
  const num = (u) => (u.match(/PARADA(\d)\.png$/) || [])[1];
  ok(num(urls[0]) === '1' && num(urls[1]) === '2' && num(urls[2]) === '3' &&
     num(urls[3]) === '1',
    'A2 parada N ↔ PARADAn.png (pedidos: ' + urls.map(num).join(',') + ')');
  // el arte SUSTITUYE al andén procedural
  const fake = { image: { width: 1024, height: 512 }, dispose() {} };
  t._signApply(fake);
  ok(t.estArt.every((m) => m.visible && m.material.map === fake),
    'A3 el arte queda puesto en los dos lados');
  ok(t._stationParts.every((p) => !p.visible),
    'A4 el andén procedural qued OCULTO (sustituido)');
  ok(Math.abs(t.estArt[0].scale.x - 1) < 0.01 && Math.abs(t.estArt[0].scale.y - 1) < 0.01,
    'A5 proporción 2:1 (1024×512) sin deformar');
  t.dispose();
}

/* ============ B · PIRÁMIDE SEPARADA 1/4 DESDE EL PRINCIPIO ============== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._buildPiramide();
  const C = TREN.cubo;
  const sep = C.size * (C.sep || 1);
  ok(Math.abs(sep - C.size * 1.25) < 1e-9, 'B1 separación = tamaño × 1,25 (hueco 1/4)');
  const xs0 = t.cubos.filter((r) => r.row === 0).map((r) => r.base.x).sort((a, b) => a - b);
  const span = xs0[4] - xs0[0] + C.size;
  ok(span <= C.peanaW + 0.01, 'B2 la base de 5 cabe en el muelle (' + span.toFixed(2) + ' ≤ ' + C.peanaW + ')');
  const r1 = t.cubos.find((r) => r.row === 1);
  const sup = t._soportes(r1);
  ok(sup.length >= 1, 'B3 el cajón de arriba tiene APOYO directo (' + sup.length + ')');
  const r2 = t.cubos.find((r) => r.row === 2);
  ok(t._soportes(r2).length >= 1, 'B4 la fila cima también tiene apoyo');
  t.dispose();
}

/* ============ C · LAS PELOTAS NACEN CADA SEGUNDO ======================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  let nacimientos = 0;
  let prevAlive = 0;
  for (let f = 0; f < 60 * 7; f++) {
    const a = t.extras.filter((e) => e.alive).length;
    if (a > prevAlive) { nacimientos += a - prevAlive; prevAlive = a; }
    t.step(dt); t.fxStep(dt);
    if (t._dead) { /* la principal muere y reaparece: sin Changes */ }
  }
  const alive = t.extras.filter((e) => e.alive).length;
  console.log('   extras nacidos en 7 s:', nacimientos, '· vivos ahora:', alive,
    '(+ principal:', !t._dead, ')');
  ok(nacimientos >= 1 && nacimientos <= 2, 'C1 v2.116: nacen bolas CADA 4 s (1-2 en 7 s: ' + nacimientos + ')');
  ok(alive + (!t._dead ? 1 : 0) <= TREN.bolas.max,
    'C2 el pool respeta el MÁXIMO (' + (alive + (!t._dead ? 1 : 0)) + ' ≤ ' + TREN.bolas.max + ')');
  // las mallas siguen a SUS bolas
  const e0 = t.extras.find((e) => e.alive);
  ok(e0 && e0.mesh.position.distanceTo(e0.ball.pos) < 1e-6, 'C3 cada malla sigue a su bola');
  // una bola extra fuera de límites MUERE sin recambio individual
  const n0 = t.extras.filter((e) => e.alive).length;
  e0.ball.pos.set(0, 0.5, 9.0);
  t.step(dt);
  ok(!e0.alive && t.extras.filter((e) => e.alive).length === n0 - 1,
    'C4 la bola extra que se sale MUERE (sin recambio individual)');
  // las extras comparten colisionador: una extra también GASTA
  const e1 = t.extras.find((e) => e.alive);
  if (e1) {
    const rec = t.cubos.find((r) => !r.muerto && !r.abierto);
    e1.ball.pos.copy(rec.mesh.position);
    t._collide(e1.ball);
    ok(e1.gastada === true, 'C5 una EXTRA también queda gastada tras cajón');
  }
  t.dispose();
}

/* ============ D · SUPERPODERES: CADENCIA Y LUGAR ======================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._podT = 0.01;
  t.step(dt);
  ok(!!t._pod, 'D1 el medallón NACE cuando toca');
  const P = TREN.poder;
  ok(t._pod.z < -1.6 && t._pod.z >= P.zMin - 0.01 && Math.abs(t._pod.x) <= P.x + 0.01,
    'D2 nace en la MESA RIVAL (z=' + t._pod.z.toFixed(2) + ', x=' + t._pod.x.toFixed(2) + ')');
  ok(Math.abs(t._pod.vida - P.vida) < 0.05, 'D3 visible 3 s (vida=' + t._pod.vida.toFixed(2) + ')');
  ok(t._pod.ref.mesh.visible, 'D4 el medallón SE VE');
  // la bola ALTA no lo dispara
  t._pod.x = 0; t._pod.z = -2.2;
  game.ball.pos.set(0, 1.5, -2.2); game.ball.vel.set(0, 0, 0);
  t.step(dt);
  ok(!!t._pod, 'D5 la bola ALTA no dispara el medallón');
  // la bola BAJA sí
  game.ball.pos.set(0, 0.8, -2.2);
  t.step(dt);
  ok(!t._pod, 'D6 la bola BAJA lo dispara (se consume)');
  ok(t._podT >= 15, 'D7 cadencia MÍNIMA 15 s (próximo en ' + t._podT.toFixed(1) + ' s)');
  // fuera de fase run: no hay poderes
  t.phase = 'stop';
  t._podT = 0.01;
  t.step(dt);
  ok(!t._pod, 'D8 fuera de la marcha no nacen poderes');
  t.dispose();
}

/* ============ E · POWERCAJAS: LLUVIA FÍSICA + MÁXIMO 30 ================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  const base = vivos(t);
  t._lluviaCajas();
  ok(vivos(t) === base + 5, 'E1 la lluvia añade 5 cajas (' + vivos(t) + ')');
  ok(t.cubos.some((r) => r.cayendo), 'E2 nacen CAYENDO (física real)');
  // caen y se ASIENTAN (3 s de simulación visual)
  let asentadas = 0;
  for (let f = 0; f < 60 * 3 && asentadas === 0; f++) {
    t.fxStep(dt);
    asentadas = t.cubos.filter((r) => r.cayendo === false && r.i === -1).length;
  }
  for (let f = 0; f < 60 * 3; f++) t.fxStep(dt);
  const lluvia = t.cubos.filter((r) => r.i === -1);
  ok(lluvia.every((r) => !r.cayendo), 'E3 las 5 cajas SE ASIENTAN (nada flota)');
  ok(lluvia.every((r) => r.mesh.position.y > TREN.cubo.peanaH - 0.02),
    'E4 nadie cae bajo el muelle (y ≥ ' + TREN.cubo.peanaH.toFixed(2) + ')');
  const apiladas = lluvia.filter((r) => r.base.y > TREN.cubo.peanaH + 0.3).length;
  console.log('   cajas apiladas ENCIMA de la pirámide:', apiladas, '/ 5');
  ok(apiladas >= 1, 'E5 al menos 1 cae ENCIMA de las existentes');
  // MÁXIMO 30: lluvias repetidas → explosiones para hacer sitio, nunca > 30
  let explotadas0 = t.cubos.filter((r) => r.muerto).length;
  for (let k = 0; k < 5; k++) {
    t._lluviaCajas();
    for (let f = 0; f < 60 * 2; f++) t.fxStep(dt);
  }
  console.log('   cajas vivas tras 6 lluvias:', vivos(t), '· muertas:',
    t.cubos.filter((r) => r.muerto).length - explotadas0, 'explotadas por sitio');
  ok(vivos(t) <= TREN.lluvia.max, 'E6 el MÁXIMO de 30 cajas se respeta (' + vivos(t) + ')');
  ok(t.cubos.filter((r) => r.muerto).length - explotadas0 > 0,
    'E7 algunas cajas EXPLOTARON para hacer sitio');
  t.dispose();
}

/* ============ F · POWERX3: TRES CAMINOS ================================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  game.ball.pos.set(0, 0.8, -2.2);
  game.ball.vel.set(0, 0, 0.5);
  const antes = t.extras.filter((e) => e.alive).length;
  t._tripleBola(game.ball);
  const nacidas = t.extras.filter((e) => e.alive).length - antes;
  const vels = t.extras.slice(-3).map((e) => e.ball.vel.clone());
  console.log('   vels:', vels.map((v) => '(' + v.x.toFixed(2) + ',' + v.y.toFixed(2) + ',' + v.z.toFixed(2) + ')').join(' '));
  const dif = vels.length === 3 &&
    vels[0].distanceTo(vels[1]) > 0.1 && vels[1].distanceTo(vels[2]) > 0.1;
  ok(nacidas >= 2, 'F1 la bola SE CONVIERTE en 3 (nacidas: ' + nacidas + ')');
  ok(t._dead, 'F2 la bola original DESAPARECE');
  ok(dif, 'F3 las 3 toman CAMINOS DIFERENTES');
  ok(vels.every((v) => v.z < -1), 'F4 los 3 caminos van HACIA LAS CAJAS (vz<0)');
  t.dispose();
}

/* ============ G · POWERDINAMITA: BOMBA + EXPLOSIÓN ====================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  game.ball.pos.set(0, 0.8, -2.2);
  t._hazBomba(game.ball);
  ok(t._bomba === true, 'G1 la bola principal se vuelve BOMBA');
  // el fusible cuelga de la malla (mecha + chispa) como en el asedio
  ok(t._fuseMain && t._fuseMain.visible && t._fuseMain.children.length === 2,
    'G2 mecha encendida en la bola (cuerda + chispa)');
  // impacto en un cajón: explota EL Y SU ALREDEDOR
  const rec = t.cubos.find((r) => !r.muerto && !r.abierto);
  game.ball.pos.copy(rec.mesh.position);
  game.ball.vel.set(0, 0.2, 0.2);
  const muertos0 = t.cubos.filter((r) => r.muerto).length;
  const abiertos0 = t.cubos.filter((r) => r.abierto).length;
  t._collide(game.ball);
  const tocados = (t.cubos.filter((r) => r.muerto).length - muertos0) +
    (t.cubos.filter((r) => r.abierto).length - abiertos0);
  console.log('   cajones alcanzados por el BOOM:', tocados);
  ok(tocados >= 3, 'G3 la explosión revienta el cajón Y SU ALREDEDOR (' + tocados + ')');
  ok(booms > 0, 'G4 suena el BOOM');
  ok(t._dead, 'G5 la bomba SE CONSUME con la explosión');
  ok(t._bomba === false, 'G6 la bomba se APAGA al morir la bola');
  t.dispose();
}

/* ============ H · TÚNEL DEL ARTISTA + LUZ AL 20 % ======================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  t.v = TREN.vMax;
  ok(t.tunelGrp && t.tunelOscuro, 'H1 el túnel del artista está construido');
  ok(!t.tunelGrp.visible, 'H2 fuera del túnel el grupo NO se ve');
  // ENTRADA (v2.116: fase PRE a lo lejos, IN al alcanzar la ventana)
  t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'H3 el túnel SE ANUNCIA (fase pre)');
  // v2.117: 'in' llega POR DISTANCIA (el borde trasero de la boca pasa el ojo)
  t._tunelZ = TREN.tunel.ojo + TREN.tunel.bh / 2 + 0.05;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'in', 'H3b al pasar el ojo ENTRA (fase in)');
  ok(t.tunelGrp.visible, 'H4 el grupo del túnel SE VE');
  const z0 = t.tunelGrp.position.z;
  for (let f = 0; f < 30; f++) { t.step(dt); t.fxStep(dt); }
  const z1 = t.tunelGrp.position.z;
  ok(z1 > z0 + 0.5, 'H5 la boca DESFILA con el mundo (Δz=' + (z1 - z0).toFixed(2) + ' m)');
  // boca espejada: en cada lado, ENTRADA y SALIDA tienen espejos opuestos
  const bocas = t.tunelGrp.children.filter((m) => m.userData && m.userData.boca);
  ok(bocas.length === 4, 'H6 boca de entrada y de salida POR LADO (4 planos)');
  // INTERIOR: la luz de toda la escena al 20 %
  t._tunnelPhase = 'dur'; t._tunnelT2 = 1.0;
  t.fxStep(dt);
  ok(Math.abs(t.tunelOscuro.material.opacity - TREN.tunel.oscuro) < 0.02,
    'H7 la luz baja al 20 % (opacity=' + t.tunelOscuro.material.opacity.toFixed(2) + ')');
  ok(t.tunelOscuro.visible, 'H8 la caja de oscuridad ACTIVA dentro del túnel');
  // SALIDA: se recupera
  t._tunnelPhase = 'out'; t._tunnelT2 = TREN.tunnelOut;
  t.fxStep(dt);
  t._tunnelPhase = 'none';
  t.fxStep(dt);
  ok(!t.tunelGrp.visible && !t.tunelOscuro.visible,
    'H9 a la SALIDA el túnel se retira y la luz se RECUPERA');
  ok(Math.abs(t.tunelOscuro.material.opacity) < 0.01, 'H10 oscuridad a cero al salir');
  t.dispose();
}

console.log(fails === 0 ? '════ TODO OK v2.115 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

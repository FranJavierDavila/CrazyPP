// Smoke headless del TrenAction (oeste) — RECONSTRUIDO tras el reset del
// sandbox: recorre el CICLO COMPLETO (3 paradas de 2 min con reloj acelerado
// por golpes entregados) hasta la VICTORIA, con TODOS los sistemas v2.115
// activos (multi-bola, poderes, lluvia, túnel, estaciones del artista).
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
global.Image = class { set src(v) { setTimeout(() => this.onload && this.onload(), 0); } };
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
let errores = 0;
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: {
    texDot: new THREE.Texture(),
    update() {}, flash() {}, spark() {},
    smoke() {}, smokeGun() {}, beam() {}, laserVisible() {},
  },
  sfx() {}, musicOn() {},
  _parkMainBall() {}, _findNetParts() { return []; },
  _netParts: [], _revolverModel: null, _revInHand: null,
  _gunRay() { return null; },
  _freeGunApply() {},
  _gunVisible() {}, _endTren() {}, _stageClear() {},
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  paintCartel() {}, _refreshMap() {},
  // v2.119: API de puntos (no-op en el banco)
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
};
game.rig.add(new THREE.Group());

const Tren = mod.TrenAction;
const TREN = mod.TREN;
const dt = 1 / 60;

const t = new Tren(ctrl);
t.start();
let winVisto = false;
// el autopiloto JUEGA: entrega golpes REALES en la pirámide cada ~0,55 s
// (coloca la bola principal contra un cajón y llama al colisionador, como
// el núcleo haría vía _extra) y de paso ejercita multi-bola, poderes,
// lluvia y túnel con el reloj REAL de parada.
const META = TREN.meta;
let guard = 60 * 60 * 12;          // máx 12 min de juego simulado
let frames = 0;
let lastReport = 0;
try {
  while (!t.done && guard-- > 0) {
    frames++;
    // AUTOPILILO: si hay bola viva y toca golpear, la planta sobre un cajón
    if (t.phase === 'run' && !t._dead && frames % 33 === 0) {
      const libres = t.cubos.filter((r) => !r.muerto && !r.abierto && !r.cayendo);
      if (libres.length) {
        const rec = libres[(Math.random() * libres.length) | 0];
        game.ball.pos.copy(rec.mesh.position);
        game.ball.vel.set(0, 0.2, 0.2);
        t._collide(game.ball);       // entrega REAL del golpe (como el núcleo)
      }
    }
    t.step(dt);
    t.fxStep(dt);
    if (t.phase === 'win') { winVisto = true; break; }
    if (frames - lastReport >= 60 * 60) {
      lastReport = frames;
      console.log('[g' + frames + '] fase=' + t.phase + ' parada=' + t.wave +
        ' lingotes=' + t.ingots + '/' + (META[t.wave - 1] || 3) +
        ' extrasVivos=' + t.extras.filter((e) => e.alive).length +
        ' cubosVivos=' + t.cubos.filter((r) => !r.muerto).length +
        ' pod=' + (t._pod ? t._pod.tipo : '-') +
        (t._tunnelPhase !== 'none' ? ' TUNNEL=' + t._tunnelPhase : ''));
    }
  }
} catch (e) {
  errores++;
  console.error('ERROR en el bucle:', e);
}
const vivos = t.cubos.filter((r) => !r.muerto).length;
console.log('fin → fase: ' + t.phase + ' parada: ' + t.wave +
  ' lingots: ' + t.ingots + ' guard: ' + frames +
  ' cubosVivos: ' + vivos + ' · victoria vista: ' + winVisto);
console.log('errores: ' + errores);
try { t.dispose(); console.log('dispose OK'); } catch (e) { console.log('dispose fallo:', e.message); }
console.log(winVisto && errores === 0 ? '★ VICTORIA COMPLETA OK' : '✗ SMOKE FALLÓ');
process.exit(winVisto && errores === 0 ? 0 : 1);

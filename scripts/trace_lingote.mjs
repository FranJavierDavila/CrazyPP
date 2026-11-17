// Trazado fino: golpea UN cajón con lingote y sigue su ciclo completo.
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
      ball.vel.y -= 6 * _dt;
      if (ball.pos.y < 0.02 && ball.vel.y < 0) ball.vel.y *= -0.4;
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
  set src(v) { setTimeout(() => this.onload && this.onload(), 0); }
};
global.fetch = () => Promise.reject(new Error('sin red'));
global.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };

const modUrl = urlmod.pathToFileURL(pathmod.resolve(
  '/home/z/my-project/game/championships/oeste/index.js')).href;
const mod = await import(modUrl);

const rig = new THREE.Group();
const game = {
  rig, scene: { background: new THREE.Color(0x0b0e11) },
  camera: { far: 60, updateProjectionMatrix() {} },
  renderer: { xr: { isPresenting: false }, capabilities: { getMaxAnisotropy: () => 4 } },
  audio: { ctx: null }, ball: { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(), ignoreNet: false },
  ballMesh: { visible: true }, tableGroup: { visible: true }, scoreboardGroup: { visible: false },
  aiPaddleMesh: { visible: true }, roomGroup: { visible: true },
  champDecor: { group: { visible: true } }, champDecorHidden: false,
  rules: { state: '', message: '' }, controllerPaddles: [], paddleHand: 1,
  haptic() {}, events: [], mode: 'arcade', net: { online: false }, freezeT: 0,
  resetToss() {}, setupAIServe() {}, ai: { reset() {} }, applyAISkill() {},
};
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: { texDot: new THREE.Texture(), update() {}, flash() {}, spark() {}, smoke() {}, smokeGun() {}, beam() {}, laserVisible() {} },
  sfx() {}, musicOn() {}, _parkMainBall() {}, _findNetParts() { return []; },
  _netParts: [], _revolverModel: null, _revInHand: null,
  _gunRay() { return { pos: new THREE.Vector3(2, 1.4, 0), dir: new THREE.Vector3(0, 0, -1) }; },
  _freeGunApply() {}, _gunVisible() {}, _endTren() {}, _stageClear() {},
  setState() {}, _setStateSilent() {}, storageKey() { return 'x'; },
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
  paintCartel() {}, _refreshMap() {},
};

const t = new mod.TrenAction(ctrl);
t.start();
t.phase = 'run';            // saltamos la intro
t._depart();
const dt = 1 / 60;

// busca un cajón con lingote y golpéalo
let rec = null;
for (let f = 0; f < 600; f++) {
  t.step(dt); t.fxStep(dt);
  if (t.phase !== 'run') { t.phase = 'run'; }
  if (!rec) {
    rec = t.cubos.find((r) => r.lingote && !r.muerto && !r.abierto && r.born <= 0);
    if (rec) {
      game.ball.pos.copy(rec.mesh.position);
      game.ball.vel.set(0, 0, 1.5);
      t._collide(game.ball);
      console.log('frame', f, 'GOLPE: lingote=', rec.lingote, 'abierto=', rec.abierto, 'shakeT=', rec.shakeT);
    }
  }
  if (f % 20 === 0) {
    console.log('f' + f, 'shakeT=' + (rec ? rec.shakeT.toFixed(2) : '-'),
      'ingotes=' + t.ingotes.length, 'volando=' + t.ingotes.filter((i) => i.volando).length,
      'contador=' + t.ingots, 'proto=' + !!t._lingoteProto);
  }
  if (t.ingots > 0) { console.log('★ LINGOTE CONTADO en frame', f); break; }
}
console.log('estado final: ingots=', t.ingots, 'pileN=', t._pileN,
  'fase=', t.phase, 'muerto=', rec && rec.muerto);
t.dispose();

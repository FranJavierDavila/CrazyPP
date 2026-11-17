// Sondeo del trigger: por qué el rayo no acierta la diana
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';

global.window = {
  __PP_CORE: {
    lang: () => 'es',
    DIMS: { tableCenterZ: -1.6, tableHalfLength: 1.37, tableHalfWidth: 0.7625,
      tableTopY: 0.76, ballRadius: 0.02, roomHeight: 2.85 },
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
global.Image = class { set src(v) { setTimeout(() => this.onload && this.onload(), 0); } };
global.fetch = () => Promise.reject(new Error('sin red'));
global.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };

const mod = await import(urlmod.pathToFileURL(pathmod.resolve(
  '/home/z/my-project/game/championships/oeste/index.js')).href);

const game = {
  rig: new THREE.Group(), scene: { background: new THREE.Color(0) },
  camera: { far: 60, updateProjectionMatrix() {} },
  renderer: { xr: { isPresenting: false }, capabilities: { getMaxAnisotropy: () => 4 } },
  audio: { ctx: null }, ball: { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3() },
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
  sfx() {}, musicOn() {}, _parkMainBall() {}, _findNetParts() { return [] },
  _netParts: [], _revolverModel: null,
  _revInHand: { mount: null, art: null },
  _gunRay() { return null; },
  _freeGunApply() {}, _gunVisible() {}, _endTren() {}, _stageClear() {},
  setState() {}, _setStateSilent() {}, storageKey() { return 'x' },
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
  paintCartel() {}, _refreshMap() {},
};

const t = new mod.TrenAction(ctrl);
t.start();
t.phase = 'run';
t._depart();
const dt = 1 / 60;
// fuerza un ataque con diana de inmediato
t._fjState = 'ida'; t._fjAtk = true; t._fjCount = 1; t._fjSide = 1;
t.fj.visible = true;
for (let f = 0; f < 130; f++) { t.step(dt); t.fxStep(dt); }
console.log('fjState tras ida:', t._fjState, 'diana visible:', t.fjDiana.visible);

// donde está realmente la diana
t.fj.updateWorldMatrix(true, true);
const wp = t.fjDiana.getWorldPosition(new THREE.Vector3());
console.log('diana world:', wp.x.toFixed(2), wp.y.toFixed(2), wp.z.toFixed(2));
console.log('fj world:', t.fj.position.x.toFixed(2), t.fj.position.y.toFixed(2), t.fj.position.z.toFixed(2));

const pos = new THREE.Vector3(2, 1.5, 0);
const dir = wp.clone().sub(pos).normalize();
ctrl._gunRay = () => ({ pos: pos.clone(), dir: dir.clone() });
const before = t._fjState;
t.trigger(0);
console.log('trigger:', before, '→', t._fjState,
  t._fjState === 'herido' ? '★ ACIERTA' : '✗ FALLA');
t.dispose();

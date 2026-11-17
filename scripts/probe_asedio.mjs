// Sonda: ¿se puede instanciar AsedioAction con el arnés headless de test_v2115?
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';

global.window = { __PP_CORE: { lang: () => 'es', DIMS: { tableCenterZ: -1.6, tableHalfLength: 1.37, tableHalfWidth: 0.7625, tableTopY: 0.76, ballRadius: 0.02, roomHeight: 2.85 }, stepPhysics(_dt, b) { b.pos.addScaledVector(b.vel, _dt); b.vel.y -= 9.81 * _dt; if (b.pos.y <= 0.02 && b.vel.y < 0) { b.pos.y = 0.02; b.vel.y *= -0.45; } } }, addEventListener: () => {} };
global.performance = { now: () => Date.now() / 1000 };
global.document = { createElementNS: () => ({ addEventListener() {}, removeEventListener() {}, set src(v) { setTimeout(() => this.onload && this.onload(), 0); }, width: 4, height: 4 }), createElement: () => ({ width: 0, height: 0, getContext: () => new Proxy({}, { get: (t, k) => { if (k === 'measureText') return () => ({ width: 10 }); if (k === 'createLinearGradient' || k === 'createRadialGradient') return () => ({ addColorStop: () => {} }); return () => {}; }, set: () => true })), addEventListener: () => {} };
global.Image = class { set src(v) { setTimeout(() => this.onload && this.onload(), 0); } };
global.fetch = () => Promise.reject(new Error('sin red'));
global.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };

const mod = await import(urlmod.pathToFileURL(pathmod.resolve('/home/z/my-project/game/championships/oeste/index.js')).href);
const rig = new THREE.Group();
const game = {
  rig, scene: { background: new THREE.Color(0x0b0e11) },
  camera: { far: 60, updateProjectionMatrix() {} },
  renderer: { xr: { isPresenting: false }, capabilities: { getMaxAnisotropy: () => 4 } },
  audio: { ctx: null },
  ball: { pos: new THREE.Vector3(), vel: new THREE.Vector3(), spin: new THREE.Vector3(), ignoreNet: false },
  ballMesh: new THREE.Mesh(new THREE.SphereGeometry(0.02, 10, 8), new THREE.MeshStandardMaterial()),
  tableGroup: { visible: true }, scoreboardGroup: { visible: false }, aiPaddleMesh: { visible: true },
  roomGroup: { visible: true }, champDecor: { group: { visible: true } }, champDecorHidden: false,
  rules: { state: '', message: '', oppLabel: '' }, controllerPaddles: [], paddleHand: 1, haptic() {},
  events: [], mode: 'arcade', net: { online: false }, freezeT: 0,
  resetToss() {}, setupAIServe() {}, ai: { reset() {} }, applyAISkill() {},
};
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: { texDot: new THREE.Texture(), update() {}, flash() {}, spark() {}, smoke() {}, smokeGun() {}, beam() {}, laserVisible() {} },
  sfx() {}, musicOn() {}, _parkMainBall() {}, _findNetParts() { return []; }, _netParts: [],
  _revolverModel: null, _revInHand: null, _gunRay() { return null; }, _freeGunApply() {},
  _gunVisible() {}, _endTren() {}, _stageClear() {}, setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; }, paintCartel() {}, _refreshMap() {},
};
game.rig.add(new THREE.Group());
try {
  const a = new mod.AsedioAction(ctrl);
  console.log('ASEDIO OK · start()…');
  a.start();
  console.log('start OK · phase:', a.phase, '· wave:', a.wave, '· need:', a._waveNeed());
  a.step(1 / 60);
  console.log('step OK');
  try { a.dispose(); } catch (e) { console.log('dispose warn:', e.message); }
} catch (e) {
  console.log('ASEDIO FALLO:', e.message);
}

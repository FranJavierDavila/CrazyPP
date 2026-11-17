// Prueba headless v2.114 (oeste/tren) — RECONSTRUIDA tras el reset del sandbox:
//  A) el VÓRTICE nace MÁS PEGADO A LA RED (a 0,30 m de tableCenterZ hacia
//     el jugador; antes al canto de la mesa, a 1,07 m) y la bola sale de él;
//  B) BOLA GASTADA: tras golpear un CAJÓN la bola rebota ~1,5 s y se RETIRA
//     SOLA, y el vórtice saca OTRA en TREN.respawnT (0,55 s) — cadencia
//     golpe→bola nueva ≈ 2 s (antes la misma bola volvía una y otra vez);
//  C) REGRESIÓN del bote arkanoi: bola nueva sigue saliendo HACIA el
//     jugador, bota al ápice y se asienta en la zona cómoda sin morir.
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';

// --- stubs de entorno (mismo arnés que test_v2113.mjs) -------------------
global.window = {
  __PP_CORE: {
    lang: () => 'es',
    DIMS: {
      tableCenterZ: -1.6, tableHalfLength: 1.37, tableHalfWidth: 0.7625,
      tableTopY: 0.76, ballRadius: 0.02, roomHeight: 2.85,
    },
    // física falsa FIEL: gravedad real + bote de suelo 0.45 (sin mesa)
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
  ballMesh: { visible: true, material: { color: { getHex: () => 0xf3eee2, setHex() {} } } },
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

let smokes = 0, maderas = 0;
const ctrl = {
  game,
  stateName: 'champtest',
  active: true,
  manifest: {},
  dianaTex: null,
  mapa: { visible: true },
  cartel: { visible: true },
  sprite: { visible: true },
  arbustoGroup: null,
  arbustoSombra: null,
  fx: {
    texDot: new THREE.Texture(),
    update() {}, flash() {}, spark() {},
    smoke() { smokes++; }, smokeGun() {}, beam() {},
    laserVisible() {},
  },
  sfx(n) { if (n === 'madera') maderas++; },
  musicOn() {},
  _parkMainBall() {}, _findNetParts() { return []; },
  _netParts: [],
  _revolverModel: null,
  _revInHand: null,
  _gunRay() { return null; },
  _freeGunApply(on) { this._revInHand = on ? { mount: null, art: null } : null; },
  _gunVisible() {}, _endTren() {}, _stageClear() {},
  setState() {}, _setStateSilent() {},
  storageKey() { return 'x'; },
  puntos: 0, _puntosAdd() {}, _puntosStep() {},
  paintCartel() {}, _refreshMap() {},
};
game.rig.add(new THREE.Group());

const Tren = mod.TrenAction;
if (!Tren) throw new Error('TrenAction no exportado');
const dt = 1 / 60;
let fails = 0;
const ok = (cond, msg) => {
  console.log((cond ? '★ ' : '✗ ') + msg);
  if (!cond) fails++;
};

/* ================= A · VÓRTICE PEGADO A LA RED ========================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._depart();
  const pz = t._portalZ;
  const netZ = -1.6;                       // tableCenterZ = la RED
  const dRed = Math.abs(pz - netZ);
  console.log('   portal z=' + pz.toFixed(3), '· red z=' + netZ,
    '· distancia a la red=' + dRed.toFixed(2) + ' m (antes 1,07 m)');
  ok(Math.abs(pz - (netZ + 0.30)) < 1e-6, 'A1 el vórtice nace a 0,30 m de la red (z=' + pz.toFixed(3) + ')');
  ok(dRed < 0.5, 'A2 PEGADO a la red: distancia ' + dRed.toFixed(2) + ' m < 0,50 m');
  ok(Math.abs(t.portalSpin.position.z - pz) < 1e-6, 'A3 el anillo del portal está EN el portal');
  const bz = game.ball.pos.z;
  ok(Math.abs(bz - pz) < 0.05, 'A4 la bola SALE DEL VÓRTICE (z bola=' + bz.toFixed(3) + ' ≈ z portal)');
  t.fxStep(dt);
  ok(t.portalGrp.visible === true && t._portalT > 0,
    'A5 el vórtice SE VE al salir la bola (portalT=' + t._portalT.toFixed(2) + ')');
  t.dispose();
}

/* ============ B · BOLA GASTADA → SALE OTRA CON FRECUENCIA =============== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._depart();
  ok(t.cubos.length > 0, 'B1 hay pirámide con cajones (' + t.cubos.length + ')');
  const rec = t.cubos.find((r) => !r.muerto && !r.abierto);
  game.ball.pos.copy(rec.mesh.position);
  game.ball.vel.set(0, 0.2, 0.2);
  const mz0 = maderas;
  t._collide(game.ball);
  ok(t._gastada === true, 'B2 tras golpear el cajón la bola queda GASTADA');
  ok(t._gastadaT > 1.4 && t._gastadaT <= 1.51, 'B3 con rebote visible de 1,5 s (t=' + t._gastadaT.toFixed(2) + ')');
  ok(maderas > 0, 'B4 el golpe sonó (madera)');
  game.ball.pos.set(0, 1.0, -1.0);
  game.ball.vel.set(0, 2.0, 0.8);
  let fKill = -1;
  for (let f = 0; f < 60 * 6; f++) {
    t.step(dt); t.fxStep(dt);
    if (t._dead) { fKill = f + 1; break; }
  }
  const tKill = fKill * dt;
  console.log('   muerte de la bola gastada a los ' + tKill.toFixed(2) + ' s');
  ok(fKill > 0, 'B5 la bola gastada SE RETIRA SOLA');
  ok(tKill > 1.2 && tKill < 1.9, 'B6 retiro a los ~1,5 s (t=' + tKill.toFixed(2) + ')');
  let fServe = -1;
  for (let f = 0; f < 60 * 3; f++) {
    t.step(dt); t.fxStep(dt);
    if (!t._dead && game.ballMesh.visible) { fServe = f + 1; break; }
  }
  const tServe = fServe * dt;
  ok(fServe > 0, 'B7 el vórtice saca OTRA bola tras morir');
  ok(tServe > 0.35 && tServe < 0.9, 'B8 recambio RÁPIDO 0,55 s (t=' + tServe.toFixed(2) + ' · antes 1,05)');
  ok(Math.abs(game.ball.pos.z - (t._portalZ || -1.3)) < 0.05,
    'B9 la nueva bola sale OTRA VEZ del vórtice junto a la red (z=' + game.ball.pos.z.toFixed(2) + ')');
  ok(t._gastada === false, 'B10 la bola nueva NO está gastada');
  const total = tKill + tServe;
  ok(total < 3.0, 'B11 cadencia golpe→bola nueva ' + total.toFixed(2) + ' s < 3 s');
  t.dispose();
}

/* ============ C · REGRESIÓN: BOTE ARKANOI INTACTO ======================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  const vz0 = game.ball.vel.z;
  ok(vz0 > 0.3, 'C1 la bola sigue saliendo HACIA EL JUGADOR (vz=' + vz0.toFixed(2) + ')');
  let maxZ = -99, killed = false, settled = false, botas = 0;
  let prevVy = 0;
  for (let f = 0; f < 60 * 25; f++) {
    prevVy = game.ball.vel.y;
    t.step(dt); t.fxStep(dt);
    maxZ = Math.max(maxZ, game.ball.pos.z);
    if (t._dead) { killed = true; break; }
    if (prevVy < -0.5 && game.ball.vel.y > 4.5 && game.ball.vel.y < 6.2) botas++;
    if (botas >= 3 && Math.abs(game.ball.pos.z - 1.05) < 0.6) { settled = true; break; }
  }
  ok(!killed, 'C2 la bola fresca NO muere esperando el golpe (25 s)');
  ok(botas >= 3, 'C3 botes recalibrados al ápice (' + botas + ')');
  ok(settled, 'C4 se ASIENTA en la zona cómoda (z=' + game.ball.pos.z.toFixed(2) + ' ≈ 1.05)');
  ok(maxZ < 2.3, 'C5 nunca sobrepasa al jugador (maxZ=' + maxZ.toFixed(2) + ')');
  t.dispose();
}

console.log(fails === 0 ? '════ TODO OK v2.114 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

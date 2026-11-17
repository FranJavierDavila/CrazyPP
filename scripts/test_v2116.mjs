// Prueba headless v2.116 (oeste) — BETA1:
//  A) CONFIG: bolas cada 4 s · poderes 5 s · túnel pre/zIn/dur · perWave 3/5/7;
//  B) NACIMIENTOS: primera EXTRA ~4 s y cadencia 4 s (antes 1 s);
//  C) TÚNEL LEJANO: fase 'pre' — la boca nace a 10 m, se VE LLEGAR con luz
//     normal, cruza la ventana → 'in' (oscuridad) y 'dur' ampliado a 8 s;
//  D) SIN JINETE EN EL TÚNEL: desaparece y su agenda se pausa;
//  E) FÍSICA DE CAJONES: soportes por posición REAL — la pirámide se
//     sostiene, al reventar los apoyos la cima CAE (no flota) y tras una
//     tormenta de lluvias TODA caja viva queda APOYADA (invariante);
//  F) MARCADOR DEL ASEDIO: perWave [3,5,7], _marc() resta bajas y el HUD
//     pinta la placa contador.png (HudOeste real con canvas stub);
//  G) SANGRE: el salpicadón del visor cambia de SITIO y giro en cada disparo.
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
/* canvas 2D de reserva COMPLETO (proxy): soporta ellipse/putImageData… y
 * CAPTURA los fillText (texto + x) para validar LO QUE PINTA y DONDE. */
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
  constructor() { this.width = 380; this.height = 190; }
  set src(v) { setTimeout(() => this.onload && this.onload(), 0); }
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
let booms = 0;
const ctrl = {
  game, stateName: 'champtest', active: true, manifest: {}, dianaTex: null,
  mapa: { visible: true }, cartel: { visible: true }, sprite: { visible: true },
  arbustoGroup: null, arbustoSombra: null,
  fx: {
    texDot: new THREE.Texture(),
    update() {}, flash() {}, spark() {},
    smoke() {}, smokeGun() {}, beam() {}, laserVisible() {},
  },
  sfx(n) { if (n === 'boom') booms++; },
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
const vivos = (t) => t.cubos.filter((r) => !r.muerto).length;

/* ============ A · CONFIG v2.116 ========================================= */
{
  ok(TREN.bolas.cada === 4.0, 'A1 bolas EXTRA cada 4 s (cada=' + TREN.bolas.cada + ')');
  // v2.118: los poderes pasan a 8 s en escena (petición del artista)
  ok(TREN.poder.vida === 8.0, 'A2 superpoderes EN ESCENA 8 s (vida=' + TREN.poder.vida + ')');
  // v2.117: el túnel ya no usa relojes (tunnelPre/tunnelDur fuera)
  ok(TREN.tunnelPre === undefined && TREN.tunnelDur === undefined,
    'A3 túnel SIN relojes de fase (por distancia)');
  ok(TREN.tunel.zIn === -12.0, 'A4 el túnel NACE LEJOS (zIn=' + TREN.tunel.zIn + ' m)');
  ok(TREN.tunel.bh === 3.4 && TREN.tunel.bocaY === 1.72,
    'A5 bocas de 3,4 m centradas en la ventana (bh=' + TREN.tunel.bh +
    ' · bocaY=' + TREN.tunel.bocaY + ')');
  ok(JSON.stringify(ASEDIO.perWave) === '[3,5,7]',
    'A6 forajidos por oleada 3/5/7 (' + JSON.stringify(ASEDIO.perWave) + ')');
}

/* ============ B · NACIMIENTOS CADA 4 SEGUNDOS =========================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  let nacimientos = 0, tPrimer = -1;
  let prevAlive = 0;
  for (let f = 0; f < 60 * 10; f++) {
    const a = t.extras.filter((e) => e.alive).length;
    if (a > prevAlive) {
      nacimientos += a - prevAlive;
      if (tPrimer < 0) tPrimer = f * dt;
      prevAlive = a;
    }
    t.step(dt); t.fxStep(dt);
  }
  console.log('   nacimientos en 10 s:', nacimientos, '· 1º a los',
    tPrimer.toFixed(2), 's');
  ok(tPrimer > 3.0 && tPrimer < 5.2, 'B1 la primera EXTRA nace ~4 s (' +
    tPrimer.toFixed(2) + ' s)');
  ok(nacimientos >= 2 && nacimientos <= 3,
    'B2 cadencia de 4 s (2-3 nacimientos en 10 s: ' + nacimientos + ')');
  t.dispose();
}

/* ============ C · TÚNEL LEJANO (fase pre + bocas apreciables) =========== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  t.v = TREN.vMax;
  t._tunnelT = 0.01;
  t.step(dt); t.fxStep(dt);
  ok(t._tunnelPhase === 'pre', 'C1 el túnel entra en fase PRE (se anuncia)');
  ok(t.tunelGrp.visible, 'C2 el grupo del túnel SE VE desde que se anuncia');
  ok(Math.abs(t.tunelGrp.position.z - TREN.tunel.zIn) < 0.05,
    'C3 la boca NACE A 12 m (z=' + t.tunelGrp.position.z.toFixed(2) + ')');
  ok(!t.tunelOscuro.visible || t.tunelOscuro.material.opacity < 0.01,
    'C4 mientras SE APROXIMA la luz es NORMAL (sin oscuridad)');
  // avanza con el mundo y SE ACERCA
  const z0 = t.tunelGrp.position.z;
  for (let f = 0; f < 60 * 2; f++) { t.step(dt); t.fxStep(dt); }
  const z1 = t.tunelGrp.position.z;
  ok(z1 > z0 + 3.0, 'C5 la boca SE ACERCA desfilando (Δz=' + (z1 - z0).toFixed(2) + ' m)');
  ok(t._tunnelPhase === 'pre', 'C6 sigue en pre a mitad de camino');
  // cruza la ventana → IN (oscuridad): máquina REAL, frame a frame
  // (v2.117: 'in' llega POR DISTANCIA, cuando el borde trasero de la
  // boca pasa el ojo: z = ojo + bh/2)
  t._tunelZ = TREN.tunel.ojo + TREN.tunel.bh / 2 + 0.05;
  let guard = 0;
  while (t._tunnelPhase === 'pre' && guard++ < 120) { t.step(dt); t.fxStep(dt); }
  ok(t._tunnelPhase === 'in', 'C7 al pasar el ojo entra IN (oscuridad)');
  // in real (1,6 s) hasta dur, y DENTRO la luz al 20 %
  guard = 0;
  while (t._tunnelPhase === 'in' && guard++ < 200) { t.step(dt); t.fxStep(dt); }
  ok(t._tunnelPhase === 'dur', 'C8a tras 1,6 s de fundido llega DUR');
  t.fxStep(dt);
  ok(Math.abs(t.tunelOscuro.material.opacity - TREN.tunel.oscuro) < 0.02,
    'C8 dentro: luz al 20 % (opacity=' + t.tunelOscuro.material.opacity.toFixed(2) + ')');
  // dur → OUT POR DISTANCIA: la boca de SALIDA asoma (a TU.ver del ojo)
  t._tunelZ = TREN.tunel.len + TREN.tunel.bh / 2 - TREN.tunel.ver - 0.05;
  guard = 0;
  while (t._tunnelPhase === 'dur' && guard++ < 30) { t.step(dt); t.fxStep(dt); }
  ok(t._tunnelPhase === 'out', 'C9 al asomar la boca de SALIDA pasa a OUT');
  const finBoca = t.tunelGrp.position.z - (TREN.tunel.len + TREN.tunel.bh / 2);
  console.log('   boca de SALIDA al empezar out: z=' + finBoca.toFixed(2) + ' m');
  ok(Math.abs(finBoca + TREN.tunel.ver) < 0.3, 'C10 la boca de SALIDA ASOMA a ' +
    TREN.tunel.ver + ' m del ojo (z=' + finBoca.toFixed(2) + ')');
  t._tunnelPhase = 'out'; t._tunnelT2 = TREN.tunnelOut;
  t.fxStep(dt);
  t._tunnelPhase = 'none';
  t.fxStep(dt);
  ok(!t.tunelGrp.visible && !t.tunelOscuro.visible,
    'C11 al salir el túnel se retira y la luz se RECUPERA');
  t.dispose();
}

/* ============ D · EN EL TÚNEL NO APARECE EL JINETE ====================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run'; t._depart();
  // jinete EN ESCENA
  t._fjSpawn();
  ok(t._fjState !== 'off' && t.fj.visible, 'D1 el jinete aparece fuera del túnel');
  // llega el túnel (fase pre) → el jinete DESAPARECE
  t._tunnelPhase = 'pre';
  t._fjUpdate(dt);
  ok(t._fjState === 'off' && !t.fj.visible, 'D2 con túnel en curso el jinete DESAPARECE');
  // su agenda queda PAUSADA mientras dura el túnel
  t._fjNext = 5.0;
  for (let f = 0; f < 60; f++) t._fjUpdate(dt);
  ok(Math.abs(t._fjNext - 5.0) < 1e-9, 'D3 la agenda del jinete NO avanza en el túnel');
  // al salir el túnel vuelve a programarse (intervalo nuevo) y aparece
  t._tunnelPhase = 'none';
  t._fjNext = 0.01;
  t._fjUpdate(dt);
  ok(t._fjState !== 'off', 'D4 fuera del túnel el jinete VUELVE a salir');
  t.dispose();
}

/* ============ E · FÍSICA DE CAJONES: NADA FLOTA ========================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._buildPiramide();
  // pirámide SANA: toda caja viva APOYADA
  ok(t.cubos.filter((r) => !r.muerto).every((r) => t._apoyado(r)),
    'E1 la pirámide recién hecha está toda APOYADA');
  // reventar los apoyos de la cima → la cima CAE (no flota)
  const cima = t.cubos.find((r) => r.row === 2);
  const y0 = cima.base.y;
  for (const o of t.cubos) {
    if (o.row === 1) { o.muerto = true; o.mesh.visible = false; }
  }
  for (let f = 0; f < 60 * 2; f++) t.fxStep(dt);
  ok(!cima.muerto && cima.base.y < y0 - 0.1,
    'E2 la cima CAE al perder los apoyos (' + y0.toFixed(2) + ' → ' +
    cima.base.y.toFixed(2) + ')');
  ok(t._apoyado(cima), 'E3 la cima queda APOYADA tras caer (fila ' + cima.row + ')');
  t.dispose();
}
{
  // TORMENTA DE LLUVIAS: el invariante «nada flota» tras el caos
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  for (let k = 0; k < 4; k++) {
    t._lluviaCajas();
    for (let f = 0; f < 60 * 2; f++) t.fxStep(dt);
  }
  // reventar un TERcio aleatorio de las cajas asentadas (como bolas/bombas)
  const viv = t.cubos.filter((r) => !r.muerto && !r.cayendo);
  for (let i = 0; i < viv.length / 3; i++) {
    const r = viv[(Math.random() * viv.length) | 0];
    if (!r.muerto) { r.muerto = true; r.mesh.visible = false; }
  }
  for (let f = 0; f < 60 * 3; f++) t.fxStep(dt);
  const restantes = t.cubos.filter((r) => !r.muerto && !r.cayendo);
  const flotando = restantes.filter((r) => !t._apoyado(r));
  console.log('   cajas vivas tras la tormenta:', restantes.length,
    '· flotando:', flotando.length);
  ok(flotando.length === 0,
    'E4 INVARIANTE: tras reventar un tercio, NINGUNA caja flota');
  // y las que quedan caen hasta APOYARSE de verdad (nada en el aire)
  const cimas = restantes.map((r) => r.base.y);
  ok(cimas.every((y) => y > TREN.cubo.peanaH - 0.05),
    'E5 ninguna caja cae bajo el muelle');
  // una caja EN EL AIRE teletransportada cae hasta APOYARSE (regresión)
  const sol = restantes[0];
  const yAir = sol.base.y + 0.9;
  sol.base.y = yAir; sol.mesh.position.y = yAir; sol.cae = false;
  for (let f = 0; f < 60; f++) t.fxStep(dt);
  ok(sol.base.y < yAir - 0.05, 'E6 una caja dejada EN EL AIRE cae (' +
    yAir.toFixed(2) + ' → ' + sol.base.y.toFixed(2) + ')');
  ok(t._apoyado(sol), 'E7 …y queda APOYADA (no flota)');
  t.dispose();
}

/* ============ F · MARCADOR DEL ASEDIO (contador.png) ==================== */
{
  const a = new AsedioAction(ctrl);
  let err = '';
  try { a.start(); } catch (e) { err = e.message; }
  if (err && !/tex|load/i.test(err)) console.log('   (start asedio: ' + err + ')');
  ok(a._waveNeed() === 3, 'F1 oleada 1: matar a 3');
  a.wave = 2; ok(a._waveNeed() === 5, 'F2 oleada 2: matar a 5');
  a.wave = 3; ok(a._waveNeed() === 7, 'F3 oleada 3: matar a 7');
  // _marc() resta las bajas de la oleada
  a.wave = 2; a.killsWave = 2;
  const m = a._marc();
  ok(m.n === 3 && m.m === 5, 'F4 marcador «3 DE 5» tras 2 bajas (' +
    m.n + '/' + m.m + ')');
  a.killsWave = 99;
  ok(a._marc().n === 0, 'F5 el marcador nunca es negativo');
  // el HUD pinta la placa (canvas proxy captura fillText)
  const hud = a._hud;
  ok(!!hud && typeof hud.set === 'function', 'F6 el HUD del asedio existe');
  if (hud) {
    FILLS.length = 0;
    hud._dirty = true;
    hud.set(100, 'OLEADA 2/3 · 2/5', '', undefined, { n: 3, m: 5 });
    // v2.117: la cuenta vive en la zona libre de la carta — «3» grande y
    // «DE 5» debajo; el reloj de la oleada va JUNTO al cartel (x≈274)
    ok(FILLS.some((f) => f.t === '3' && Math.abs(f.x - 134) < 3) &&
       FILLS.some((f) => f.t === 'DE 5' && Math.abs(f.x - 134) < 3),
      'F7 el HUD pinta «3» y «DE 5» en la zona libre de contador.png');
    ok(FILLS.some((f) => f.t === '1:40' && Math.abs(f.x - 274) < 3),
      'F7b el reloj de la oleada se pinta JUNTO al cartel (x=' +
      (FILLS.find((f) => f.t === '1:40') || {}).x + ')');
    ok(!FILLS.some((f) => f.t === '1:40' && Math.abs(f.x - 320) < 3),
      'F7c en el asedio NO hay reloj central duplicado');
    // y al pasar al TREN (placa lingotes) el reloj central vuelve
    FILLS.length = 0;
    hud.set(100, 'PARADA 1/3', '', { n: 0, m: 3 });
    ok(hud.marc === null && FILLS.some((f) => f.t === '1:40' && Math.abs(f.x - 320) < 3),
      'F8 con la placa del tren el reloj central VUELVE');
    FILLS.length = 0;
    hud.set(100, '', '', undefined, null);
    ok(hud.marc === null, 'F9 sin marcador (derrota) la placa se retira');
  }
  try { a.dispose(); } catch (e) { /* */ }
}

/* ============ G · SANGRE: CADA DISPARO, SITIO DISTINTO ================== */
{
  const t = new Tren(ctrl);
  t.start();
  // SangreCara vive en el ctrl del duelo; aquí validamos el PATRÓN del
  // salpicadón por fuente: posición y giro aleatorios en cada trigger.
  const src = await (await import('fs/promises'))
    .readFile('/home/z/my-project/game/championships/oeste/index.js', 'utf8');
  ok(/this\.splat\.position\.set\(\s*\(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G1 el salpicadón del visor CAMBIA DE SITIO en cada disparo');
  ok(/this\.splat\.rotation\.z = \(Math\.random\(\) \* 2 - 1\)/.test(src),
    'G2 el salpicadón CAMBIA DE GIRO en cada disparo');
  ok(/perWave: \[3, 5, 7\]/.test(src) && /contadorUrl: A\('contador\.png'\)/.test(src),
    'G3 marcador cableado: perWave 3/5/7 + contadorUrl en el manifest');
  t.dispose();
}

console.log(fails === 0 ? '════ TODO OK v2.116 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

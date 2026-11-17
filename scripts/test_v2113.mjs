// Prueba headless v2.113 (oeste/tren):
//  A) el vórtice SUELTA LA BOLA HACIA EL JUGADOR y el bote se asienta en la
//     zona cómoda (zComoda) sin morir;
//  B) el ROBO levita 1 m girando EN ROJO y sale por la ventana (sin teñir
//     el proto ni la pila);
//  C) los cajones que aterrizan NO vuelven a caer (adiós humo/madera eternos);
//  D) ¡YIHAA! y zumbido no rompen sin AudioContext;
//  E) el CUERPO del jinete mata aunque la diana no esté sobre el rayo.
import * as THREE from 'three';
import * as urlmod from 'url';
import * as pathmod from 'path';

const __dirname = pathmod.dirname(urlmod.fileURLToPath(import.meta.url));

// --- stubs de entorno (mismo arnés que smoke_tren.mjs) ------------------
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
  ballMesh: { visible: true },
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

let smokes = 0, maderas = 0, yihhas = 0, zumbidos = 0;
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

/* ================= A · BOTE HACIA EL JUGADOR ============================ */
{
  const t = new Tren(ctrl);
  t.start();
  // forzar fase run con la bola recién sacada del vórtice
  t.phase = 'run'; t._depart();
  const vz0 = game.ball.vel.z;
  const z0 = game.ball.pos.z;
  ok(vz0 > 0.3, 'A1 la bola sale del vórtice HACIA EL JUGADOR (vz=' + vz0.toFixed(2) + ' > 0)');
  let maxZ = -99, killed = false, settled = false, botasGestionados = 0;
  let prevVy = 0;
  for (let f = 0; f < 60 * 25; f++) {
    prevVy = game.ball.vel.y;
    t.step(dt); t.fxStep(dt);
    maxZ = Math.max(maxZ, game.ball.pos.z);
    if (t._dead) { killed = true; break; }
    // contar botes recalibrados (vy altísima tras el bote = ápice 1,45)
    if (prevVy < -0.5 && game.ball.vel.y > 4.5 && game.ball.vel.y < 6.2) botasGestionados++;
    if (botasGestionados >= 3 && Math.abs(game.ball.pos.z - 1.05) < 0.6) { settled = true; break; }
  }
  console.log('   bote: z0=' + z0.toFixed(2), 'maxZ=' + maxZ.toFixed(2),
    'z final=' + game.ball.pos.z.toFixed(2), 'y final=' + game.ball.pos.y.toFixed(2),
    'botasGestionados=' + botasGestionados, 'killed=' + killed);
  ok(!killed, 'A2 la bola NO muere mientras espera el golpe (25 s)');
  ok(maxZ < 2.3, 'A3 la bola nunca sobrepasa al jugador (maxZ=' + maxZ.toFixed(2) + ' < 2.3)');
  ok(botasGestionados >= 3, 'A4 hay botes recalibrados al ápice (' + botasGestionados + ')');
  ok(settled, 'A5 la bola se ASIENTA en la zona cómoda (z=' + game.ball.pos.z.toFixed(2) + ' ≈ 1.05)');
  t.dispose();
}

/* ================= C · HUMO ETERNO DE LOS CAJONES ======================= */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  t._buildPiramide();
  // cajón de la fila 1 con sus DOS apoyos de la fila 0
  const rec = t.cubos.find((r) => r.row === 1 && !r.lingote) ||
              t.cubos.find((r) => r.row === 1);
  const soportes = t._soportes(rec);
  ok(soportes.length >= 1, 'C1 el cajón fila-1 tiene apoyo directo (' + soportes.length + ')');
  const sfx0 = maderas, sm0 = smokes;
  for (const s of soportes) t._revientaCubo(s);   // saltan los apoyos
  // correr 6 s: el cajón cae UNA vez y se queda (el bug vieja: humo+madera
  // cada frame → ~360 eventos)
  for (let f = 0; f < 60 * 6; f++) { t.step(dt); t.fxStep(dt); }
  const ev = (maderas - sfx0) + (smokes - sm0);
  console.log('   eventos tras 6 s:', (maderas - sfx0), 'madera +', (smokes - sm0), 'humo');
  // estabilidad: 3 s más SIN eventos nuevos
  const sfx1 = maderas, sm1 = smokes;
  for (let f = 0; f < 60 * 3; f++) { t.step(dt); t.fxStep(dt); }
  const ev2 = (maderas - sfx1) + (smokes - sm1);
  ok(ev >= 2 && ev <= 8, 'C2 la caída genera POCOS eventos (' + ev + ' ≤ 8)');
  ok(ev2 === 0, 'C3 luego del aterrizaje CERO eventos en 3 s (' + ev2 + ') — sin humo eterno');
  // y si un apoyo VIVO revienta después, el cajón vuelve a caer (física honesta)
  const rec2 = t.cubos.find((r) => r.row === 2 && !r.muerto && !r.abierto);
  if (rec2) {
    const sup2 = t._soportes(rec2).filter((s) => !s.muerto);
    const yAntes = rec2.mesh.position.y;
    const sfx2 = maderas, sm2 = smokes;
    for (const s of sup2) t._revientaCubo(s);
    for (let f = 0; f < 60 * 4; f++) { t.step(dt); t.fxStep(dt); }
    const cayo = rec2.mesh.position.y < yAntes - 0.05;
    const ev3 = (maderas - sfx2) + (smokes - sm2);
    ok(cayo && ev3 >= 2 && ev3 <= 8, 'C4 apoyo reventado DESPUÉS → el cajón vuelve a caer UNA vez (Δy=' +
      (rec2.mesh.position.y - yAntes).toFixed(2) + ', ev=' + ev3 + ')');
  }
  t.dispose();
}

/* ================= B · ROBO: LEVITA, ROJO, VENTANA ====================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  // dos lingotes asentados en la pila
  t._lanzaLingote(new THREE.Vector3(-0.2, 0.78, -2.05));
  t._lanzaLingote(new THREE.Vector3(0.0, 0.78, -2.43));
  for (const it of t.ingotes) { it.t = it.T; it.volando = true; }
  t.fxStep(dt);   // aterrizan (contador +2)
  ok(t.ingots === 2, 'B1 pila con 2 lingotes contados (' + t.ingots + ')');
  // color del PROTO antes del robo (control)
  let protoR = 0, protoG = 1;
  t._lingoteProto.traverse((n) => {
    if (n.isMesh && n.material && n.material.color) {
      protoR = Math.max(protoR, n.material.color.r);
      protoG = Math.min(protoG, n.material.color.g);
    }
  });
  ok(t._robaLingote() === true, 'B2 el forajido roba');
  const it = t.ingotes.find((i) => i.robado);
  ok(!!it && it.robo === 0, 'B3 fase de LEVITACIÓN activa (robo=' + (it && it.robo) + ')');
  ok(t.ingots === 1, 'B4 la cuenta baja a 1 (' + t.ingots + ')');
  ok(t._pileN === 1, 'B5 el hueco de la pila queda libre (pileN=' + t._pileN + ')');
  // materiales ROJOS sólo en el robado
  let rMax = 0, gMin = 1;
  it.mesh.traverse((n) => {
    if (n.isMesh && n.material && n.material.color) {
      rMax = Math.max(rMax, n.material.color.r);
      gMin = Math.min(gMin, n.material.color.g);
    }
  });
  ok(rMax > 0.9 && gMin < 0.4, 'B6 el lingote robado está TEÑIDO DE ROJO (r=' + rMax.toFixed(2) + ' g=' + gMin.toFixed(2) + ')');
  let pr2 = 0, pg2 = 1;
  t._lingoteProto.traverse((n) => {
    if (n.isMesh && n.material && n.material.color) {
      pr2 = Math.max(pr2, n.material.color.r);
      pg2 = Math.min(pg2, n.material.color.g);
    }
  });
  ok(!(pr2 > 0.9 && pg2 < 0.4), 'B7 el PROTO sigue DORADO (r=' + pr2.toFixed(2) + ' g=' + pg2.toFixed(2) + ')');
  // levitación: a mitad de fase sube ya; al CAMBIAR de fase está a +1,00 m
  const yBase = it.base.y;
  for (let f = 0; f < 27; f++) t.fxStep(dt);           // 0,45 s ≈ k=0.5
  const yMid = it.mesh.position.y;
  ok(it.robo === 0 && yMid > yBase + 0.4 && yMid < yBase + 1.0,
    'B8 levitando a mitad de fase (+' + (yMid - yBase).toFixed(2) + ' m, aún sin llegar)');
  for (let f = 0; f < 60; f++) {
    t.fxStep(dt);
    if (it.robo === 1) break;                          // medir EN el cambio
  }
  ok(it.robo === 1, 'B9 pasa a fase SALIDA (robo=1)');
  const yTop = it.mesh.position.y;
  ok(yTop - yBase > 0.95 && yTop - yBase < 1.06,
    'B10 levita EXACTAMENTE ~1 m sobre la mesa (+' + (yTop - yBase).toFixed(2) + ' m)');
  ok(Math.abs(it.v.x) > 5, 'B11 sale disparado hacia la ventana (vx=' + it.v.x.toFixed(1) + ')');
  const xAntes = it.mesh.position.x;
  for (let f = 0; f < 60; f++) t.fxStep(dt);
  ok(t.ingotes.every((i) => !i.robado), 'B12 el lingote robado SALIÓ por la ventana y desapareció');
  console.log('   vuelo: x ' + xAntes.toFixed(2) + ' → recorridos ' +
    Math.abs(it.mesh ? it.mesh.position.x - xAntes : 99).toFixed(2) + ' m');
  // el girar no rompe nada con spin alto
  t.dispose();
}

/* ================= D · SONIDOS SIN AUDIOCONTEXT ========================= */
{
  const t = new Tren(ctrl);
  t.start();
  let threw = false;
  try { t._sndYihha(); t._sndZumbido(); } catch (e) { threw = true; console.log(e); }
  ok(!threw, 'D1 ¡YIHAA! y zumbido sin AudioContext no rompen');
  t.dispose();
}

/* ================= E · CUERPO DEL JINETE MATA =========================== */
{
  const t = new Tren(ctrl);
  t.start();
  t.phase = 'run';
  // jinete plantado en la ventana con diana visible pero el rayo apunta al
  // CUERPO (alejado de la diana)
  t._fjState = 'ventana'; t._fjAtk = true;
  t._fjSide = -1;
  t._fjZ = TREN_zAtk(t);
  t._fjSetFrame('dispara');
  t._fjDianaPos();
  t.fjDiana.visible = true;
  t.fj.visible = true;
  t._fjPose(0);
  const wp = t.fjDiana.getWorldPosition(new THREE.Vector3());
  // rayo hacia el centro del PLANO del jinete, lejos de la diana
  const cuerpo = new THREE.Vector3(t.fj.position.x, t.fj.position.y, t.fj.position.z);
  cuerpo.z += t._fjW * 0.3;                       // esquina del cuerpo
  const pos = new THREE.Vector3(1.6, 1.5, 0.5);
  ctrl._gunRay = () => ({ pos, dir: cuerpo.clone().sub(pos).normalize() });
  const dDiana = (() => {
    const toD = wp.clone().sub(pos);
    const tt = Math.max(0, Math.min(9, toD.dot(cuerpo.clone().sub(pos).normalize())));
    return pos.clone().addScaledVector(cuerpo.clone().sub(pos).normalize(), tt).distanceTo(wp);
  })();
  t._gunLast = 0;
  t.trigger(0);
  ok(dDiana > 0.3, 'E1 el rayo cae LEJOS de la diana (d=' + dDiana.toFixed(2) + ' m)');
  ok(t._fjState === 'herido', 'E2 CUERPO del jinete mata → herido (antes: seguía vivo)');
  // y un rayo a la NADA no mata
  const t2 = new Tren(ctrl);
  t2.start(); t2.phase = 'run';
  t2._fjState = 'ventana'; t2._fjAtk = true; t2._fjSide = -1;
  t2._fjZ = TREN_zAtk(t2); t2._fjSetFrame('dispara');
  t2._fjDianaPos(); t2.fjDiana.visible = true; t2.fj.visible = true; t2._fjPose(0);
  ctrl._gunRay = () => ({ pos, dir: new THREE.Vector3(0, 1, 0) });  // al techo
  t2._gunLast = 0;
  t2.trigger(0);
  ok(t2._fjState === 'ventana', 'E3 tiro al TECHO no mata (estado=' + t2._fjState + ')');
  t.dispose(); t2.dispose();
}
function TREN_zAtk(t) { return -1.82; }
// (TREN no se exporta; el valor zAtk de la config vale -1.82)

console.log(fails === 0 ? '════ TODO OK v2.113 ════' : '════ ' + fails + ' FALLOS ════');
process.exit(fails === 0 ? 0 : 1);

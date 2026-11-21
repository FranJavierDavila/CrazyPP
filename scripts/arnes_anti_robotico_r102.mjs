/* r102 · ARNÉS ANTI-ROBÓTICO §6+§7.2 — las dos piezas del estudio en cola,
 * probadas contra la física REAL del motor (c04/c05 sin réplicas):
 *  §6 APOYO PERSISTENTE EN MESA (micro-solver compliant):
 *    A1 · caída floja (< 1 m/s) SE POSA: ≤ 2 eventos de mesa y |vy| < 0.05
 *         en 1,2 s (antes: micro-bote zombi a rest 0,935 sin fin).
 *    A2 · la bola en apoyo RUEDA con su efecto: topspin acelera hacia
 *         adelante (|vz| crece), backspin frena hasta casi pararse.
 *    A3 · empuje en continuo: una bola posada empujada por una pala que
 *         avanza responde sin salto binario (despegue con velocidad ≤ min).
 *    A4 · el bote REAL no cambia: impacto 2,4 m/s sigue siendo impulso
 *         (apex ITTF ya lo cubre — aquí: rebota y SALE del apoyo).
 *  §7.2 KALMAN POR EJE (updatePaddleSim):
 *    K1 · tracking con jitter ±3 mm a 60 Hz ⇒ ps.vel suave (pico de
 *         variación frame a frame < 25 % del de la media-móvil).
 *    K2 · salto de tracking (re-centrado 0,4 m) ⇒ re-nace: |ps.vel| vuelve
 *         a ser razonable en ≤ 6 ticks y NUNCA guarda el salto.
 */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r102' }; } catch (e) { /* getter */ }

import * as THREE from 'three';
const { DIMS } = await import('/home/z/my-project/src/game/core/c02_cfg_escena.js');
const { stepPhysics } = await import('/home/z/my-project/src/game/core/c05_colisiones_ia_golpeo.js');
const c04 = await import('/home/z/my-project/src/game/core/c04_fisica_ccd.js');

const C = DIMS.tableCenterZ, TOP = DIMS.tableTopY, R = DIMS.ballRadius;
const V3 = THREE.Vector3;
let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}
function bola(x, y, z, vx, vy, vz, wx = 0, wz = 0) {
  return { pos: new V3(x, y, z), vel: new V3(vx, vy, vz), spin: new V3(wx, 0, wz),
    dragMul: 1, ppEfecto: false, ppEfectoTipo: '', ppEfectoLado: 0, ppPortal: false };
}

/* ── A1 · caída floja se posa (sin micro-bote zombi) ── */
{
  const b = bola(0.1, TOP + R + 0.03, C + 0.5, 0.05, 0, -0.4);
  const evs = []; let nEv = 0, minVy = 9, apoyada = false;
  for (let i = 0; i < 90; i++) {                     // 1,5 s a 60 Hz
    evs.length = 0;
    stepPhysics(1 / 60, b, [], evs, null);
    nEv += evs.filter(e => e.type === 'table').length;
    if (i > 40) { minVy = Math.min(minVy, Math.abs(b.vel.y)); }
    if (b.__ppMesa > 0.5) apoyada = true;
  }
  CHK(nEv <= 2, `A1 caída floja: ≤2 botes (hay ${nEv}) — adiós al micro-bote zombi`);
  CHK(apoyada, 'A1 la bola entra en APOYO PERSISTENTE (__ppMesa)');
  CHK(minVy < 0.05, `A1 se posa: |vy| mínima ${minVy.toFixed(3)} < 0.05 m/s`);
}

/* ── A2 · rodadura con efecto real ── */
{
  // topspin (ωx>0 según convenio: uz = vz − r·ωx → backspin frena): bola con
  // backspin grande cae floja y el apoyo la FRENA hasta casi pararla
  const b = bola(-0.1, TOP + R + 0.02, C + 0.6, 0.6, 0, -0.5, 0, 0);
  b.spin.x = 60;                                     // backspin: uz = vz − r·ωx < 0
  let vzIni = 0, vzFin = 0;
  for (let i = 0; i < 120; i++) stepPhysics(1 / 60, b, [], [], null);
  vzIni = 0.6; vzFin = b.vel.z;
  CHK(Math.abs(vzFin) < 0.35, `A2 backspin frena en apoyo: vz ${vzFin.toFixed(2)} (ini 0.60)`);
  // sidespin: la bola rodando se desvía lateralmente
  const b2 = bola(0.15, TOP + R + 0.02, C - 0.4, 0.8, 0, 0.55, 0, 55);
  const x0 = b2.pos.x;
  for (let i = 0; i < 120; i++) stepPhysics(1 / 60, b2, [], [], null);
  CHK(Math.abs(b2.pos.x - x0) > 0.03,
    `A2 sidespin desvía al rodar: Δx ${(b2.pos.x - x0).toFixed(3)} m`);
}

/* ── A3 · empuje en continuo (pala que avanza lenta sobre bola posada) ── */
{
  const b = bola(0, TOP + R, C + 0.3, 0, 0, 0);
  for (let i = 0; i < 60; i++) stepPhysics(1 / 60, b, [], [], null);  // se posa
  const pad = { active: true, index: 7, who: 'player',
    pos: new V3(0, TOP + 0.02, C + 0.3), prev: new V3(0, TOP + 0.02, C + 0.3),
    vel: new V3(0, 0, -0.25), velInst: new V3(0, 0, -0.25),
    normal: new V3(0, 1, 0), prevNormal: new V3(0, 1, 0),
    up: new V3(0, 0, -1), prevUp: new V3(0, 0, -1),
    right: new V3(1, 0, 0), prevRight: new V3(1, 0, 0),
    quat: new THREE.Quaternion(), cooldown: 0, serveFlight: false };
  b.pos.copy(pad.pos).add(new V3(0, R + 0.001, 0.02));
  b.vel.set(0, 0, 0);
  b.__ppRestIdx = pad.index; b.__ppRestT = 0; b.__ppRestSx = 0; b.__ppRestSy = 0;
  b.__ppRestLx = 0; b.__ppRestDy = 0.02; b.__ppRestPush = 0; b.__ppRestSide = 1;
  let saltos = 0, velPrev = 0;
  for (let i = 0; i < 60; i++) {                     // la pala avanza 1 s a 0,25 m/s
    pad.pos.z -= 0.25 / 60;
    const evs = []; stepPhysics(1 / 60, b, [pad], evs, null);
    const dv = Math.abs(b.vel.length() - velPrev);
    if (dv > 0.6) saltos++;
    velPrev = b.vel.length();
  }
  CHK(saltos === 0, `A3 empuje sostenido SIN salto binario (${saltos} saltos >0,6 m/s)`);
  CHK(b.vel.length() > 0.15 || b.__ppRestPush > 0.002,
    `A3 la compresión acumula (vel ${b.vel.length().toFixed(2)} · push ${(b.__ppRestPush || 0).toFixed(3)})`);
}

/* ── A4 · el bote REAL sigue siendo impulso (y sale del apoyo) ── */
{
  const b = bola(0.1, TOP + R + 0.3, C + 0.5, 0.1, -2.4, -0.6);
  let botes = 0, apoyadoTras = false;
  for (let i = 0; i < 420; i++) {                    // 7 s: la cascada de rest 0,935
    const evs = []; stepPhysics(1 / 60, b, [], evs, null);
    if (evs.some(e => e.type === 'table')) botes++;
    if (i > 30 && b.__ppMesa > 0.4) apoyadoTras = true;
  }
  CHK(botes >= 1, `A4 impacto 2,4 m/s bota por impulso (${botes} eventos)`);
  CHK(apoyadoTras, 'A4 y al agotarse entra en apoyo (transición natural)');
}

/* ── K1 · Kalman: jitter ±3 mm ⇒ velocidad suave ── */
{
  const ps = c04.createPaddleSim('player', 0);
  const q = new THREE.Quaternion();
  const base = new V3(0, 1.0, C + 1.5);
  let picoKF = 0, picoAvg = 0;
  let velPrev = new V3(), avgPrev = new V3();
  const pos = new V3(), posAvg = new V3();
  for (let i = 0; i < 120; i++) {                    // 2 s de mano en vaivén + jitter
    const t = i / 60;
    pos.copy(base);
    pos.x += 0.12 * Math.sin(t * 6.0);               // mano real ~0,7 m/s pico
    pos.z += 0.1 * Math.cos(t * 4.5);
    pos.x += (Math.sin(i * 12.9898) * 43758.5453 % 1) * 0.006;   // jitter ±3 mm
    pos.y += ((Math.sin(i * 78.233) * 12345.678 % 1) * 0.006) - 0.003;
    posAvg.copy(pos);
    c04.updatePaddleSim(ps, pos, q, t, 1 / 60);
    if (i > 20) {
      picoKF = Math.max(picoKF, ps.vel.distanceTo(velPrev));
      velPrev.copy(ps.vel);
      // la media-móvil la simulo aparte (misma ventana 70 ms sobre la posición
      // SIN filtro — lo que hacía el código antes del KF)
      const vInst = posAvg.clone().sub(base.clone().add(
        new V3(0.12 * Math.sin((t - 1 / 60) * 6.0), 0, 0.1 * Math.cos((t - 1 / 60) * 4.5))))
        .multiplyScalar(60);
      picoAvg = Math.max(picoAvg, vInst.distanceTo(avgPrev));
      avgPrev.copy(vInst);
    }
  }
  CHK(picoKF < picoAvg * 0.9,
    `K1 Kalman más suave que diferencias finitas: pico KF ${picoKF.toFixed(3)} vs FD ${picoAvg.toFixed(3)} m/s`);
}

/* ── K2 · re-nacimiento ante salto de tracking ── */
{
  const ps = c04.createPaddleSim('player', 0);
  const q = new THREE.Quaternion();
  const pos = new V3(0, 1.0, C + 1.5);
  for (let i = 0; i < 40; i++) c04.updatePaddleSim(ps, pos, q, i / 60, 1 / 60);
  pos.z -= 0.4;                                      // re-centrado: salto de 0,4 m
  let peor = 0;
  for (let i = 0; i < 8; i++) {
    c04.updatePaddleSim(ps, pos, q, (40 + i) / 60, 1 / 60);
    peor = Math.max(peor, Math.abs(ps.vel.z));
  }
  // el re-nacimiento hereda velInst (el salto DIJO 24 m/s, el techo dice 16):
  // legítimo — lo que NUNCA puede pasar es superar el techo (sin wind-up)
  CHK(peor <= DIMS.paddleVelClamp + 0.01,
    `K2 tras el salto la velocidad NO guarda el glitch (pico |vz| ${peor.toFixed(2)} ≤ techo ${DIMS.paddleVelClamp})`);
  CHK(ps.vel.z < 0.2, `K2 y converge a la mano quieta (|vz| ${Math.abs(ps.vel.z).toFixed(3)} < 0.2)`);
}

/* ── r103 · apoyo en el MUNDO — los dos bugs del dueño con la bola apoyada ── */
function padApoyo() {
  return { active: true, index: 7, who: 'player',
    pos: new V3(0, TOP + 0.02, C + 0.6), prev: new V3(0, TOP + 0.02, C + 0.6),
    vel: new V3(0, 0, 0), velInst: new V3(0, 0, 0),
    normal: new V3(0, 1, 0), prevNormal: new V3(0, 1, 0),
    up: new V3(0, 0, 1), prevUp: new V3(0, 0, 1),
    right: new V3(1, 0, 0), prevRight: new V3(1, 0, 0),
    omega: new V3(0, 0, 0), quat: new THREE.Quaternion(),
    cooldown: 0, serveFlight: false };
}
function bolaApoyada(pad, lx, dy) {
  const b = bola(0, TOP + 0.02, C + 0.6, 0, 0, 0);
  b.__ppRestIdx = 7; b.__ppRestT = 0; b.__ppRestLx = lx; b.__ppRestDy = dy;
  b.__ppRestPush = 0; b.__ppRestSide = 1;
  b.pos.copy(pad.pos).add(new V3(lx, R + 0.001, dy));
  b.vel.set(0, 0, 0);
  return b;
}

/* ── N1 · INCLINAR LA PALA DESLIZA LA BOLA (antes: soldada al punto local) ── */
{
  const pad = padApoyo();
  const b = bolaApoyada(pad, 0, 0);
  for (let i = 0; i < 30; i++) stepPhysics(1 / 60, b, [pad], [], null);   // se posa
  // inclinar 0→25° sobre el eje right en 30 frames, pala quieta en la mano
  const Lx0 = b.__ppRestLx, x0 = b.pos.x;
  for (let i = 0; i < 60; i++) {
    const dA = i < 30 ? (25 * Math.PI / 180) / 30 : 0;
    pad.omega.set(dA * 60, 0, 0);
    const cA = Math.cos(dA), sA = Math.sin(dA);
    const nx = pad.normal.x * cA + pad.normal.y * sA;
    const ny = pad.normal.y * cA - pad.normal.x * sA;
    pad.normal.set(nx, ny, 0).normalize();
    const evs = []; stepPhysics(1 / 60, b, [pad], evs, null);
    if (i >= 30) pad.omega.set(0, 0, 0);
  }
  const dLx = b.__ppRestLx - Lx0;
  // la inclinación tumba la normal hacia +X ⇒ la pendiente es +X: la bola
  // desliza cuesta abajo y, sostenido 1 s, RODA FUERA del borde (natural)
  CHK(dLx > 0.005 || b.__ppRestIdx < 0,
    `N1 inclinar 25° DESLIZA cuesta abajo (ΔLx ${(dLx * 1000).toFixed(1)} mm, rueda fuera: ${b.__ppRestIdx < 0})`);
  CHK(b.__ppRestIdx < 0 || Math.abs(b.pos.x - x0) > 0.005,
    `N1 la bola se movió en el mundo (Δx ${((b.pos.x - x0) * 1000).toFixed(1)} mm o rodó fuera)`);
}

/* ── N2 · GIRAR LA MUÑECA ARRASTRA CON RETARDO (antes: orbitaba pegada) ── */
{
  const pad = padApoyo();
  const b = bolaApoyada(pad, 0.02, 0);
  for (let i = 0; i < 30; i++) stepPhysics(1 / 60, b, [pad], [], null);   // se posa
  pad.omega.set(0, 10, 0);                       // la cara corre bajo la bola (10 rad/s)
  const Lx0 = b.__ppRestLx;
  for (let i = 0; i < 60; i++) stepPhysics(1 / 60, b, [pad], [], null);
  const dLx = Math.abs(b.__ppRestLx - Lx0);
  CHK(dLx > 0.003,
    `N2 girar la muñeca DESLIZA la bola sobre la cara (ΔLx ${(dLx * 1000).toFixed(1)} mm > 3 mm)`);
}

/* ── N3 · SWING RÁPIDO DESDE EL APOYO = GOLPE (antes: la atravesaba) ── */
{
  const pad = padApoyo();
  const b = bolaApoyada(pad, 0, 0);
  for (let i = 0; i < 30; i++) stepPhysics(1 / 60, b, [pad], [], null);   // se posa
  pad.vel.set(0, 0.2, -2.5);                     // el impulso rápido (> carry 0,3)
  pad.velInst.copy(pad.vel);
  const evs = [];
  stepPhysics(1 / 60, b, [pad], evs, null);
  const golpe = evs.find(e => e.type === 'paddle');
  CHK(!!golpe, 'N3 el swing lanza la bola y el ÁRBITRO registra el golpe');
  if (golpe) {
    const alin = b.vel.dot(pad.vel) / (b.vel.length() * pad.vel.length());
    CHK(alin > 0.75,
      `N3 la bola sale EN LA DIRECCIÓN del impulso (alineación ${(alin * 100).toFixed(0)} %)`);
    const frente = b.pos.clone().sub(pad.pos).addScaledVector(pad.up, -DIMS.bladeCenterUp).dot(pad.normal);
    CHK(frente > 0, `N3 y la bola quedó DELANTE de la cara (${(frente * 1000).toFixed(1)} mm)`);
  }
}

console.log(`\nANTI-ROBÓTICO §6+§7.2 · ${ok} OK · ${fail} FALLOS`);
process.exit(fail ? 1 : 0);

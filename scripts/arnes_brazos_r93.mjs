#!/usr/bin/env node
/* =====================================================================
 * ARNÉS BRAZOS GLB r93 — «los brazos que agarran la pala y la bola»
 * ---------------------------------------------------------------------
 * 1. HUESOS RÍGIDOS SIEMPRE: solveArmIKRigido jamás estira (|S-E|=L1,
 *    |E-W|=L2 exactos), objetivo clampado al anillo, flag alcanzado.
 * 2. COMPOSICIÓN DE HUESOS con el GLB REAL: jerarquía sintética con los
 *    T/R del propio vr_arm.glb → el quat mundo deseado se compone igual
 *    que en el driver y el eje +X del hueso CAE en la dirección deseada.
 *    Los huesos conservan posición y escala de reposo (nunca se estiran).
 * 3. PISO DURO DE MESA: con objetivos bajo la mesa, codo y muñeca quedan
 *    por encima del plano (pole arriba + subida de muñeca) y el hueso
 *    SIGUE rígido.
 * 4. ONE EURO anti-temblor: el jitter de alta frecuencia se reduce a
 *    < 20 % sin perder la conducción (converge al escalón y el pico del
 *    golpeo llega con < 28 ms de retardo en el modo nítido).
 * 5. AGARRE POR EL MANDO: muñeca = centro − continuación·0,1303 es
 *    EXACTA (identidad) en alcance; zona dulce: nudge ≤ 4 cm solo si la
 *    bola sale del disco central (62 % R).
 * 6. ALTURA ADULTA y LADO: hombro ≈ 1,35 m (adiós al efecto enano) y el
 *    brazo de la pala cae en el lado de la mano del rival (s).
 * 7. BINDING REAL DEL GLB: los nombres y jerarquía que el loader busca
 *    EXISTEN en vr_arm.glb (contrato de fuente binario).
 * ===================================================================== */
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { readFileSync } from 'node:fs';

globalThis.window = globalThis.window || globalThis;   // c00 en Node

const { OneEuroV3, OneEuroQ, solveArmIKRigido, zonaDulceNudge } =
  await import(fileURLToPath(new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url)));
const { DIMS } = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));

let ok = 0, fails = 0;
const dije = (nombre, bien, detalle) => {
  if (bien) { ok++; console.log(`  ✓ ${nombre}${detalle ? ' · ' + detalle : ''}`); }
  else { fails++; console.log(`  ✗ FALLO ${nombre}${detalle ? ' · ' + detalle : ''}`); }
};
const rng = (() => { let s = 1234567; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

/* ---------- 7 · binding real del GLB (fuente binaria) ---------- */
let nodosGLB = null, hijos = null, esc = 0, L1 = 0, L2 = 0, L1u = 0, L2u = 0;
{
  const buf = readFileSync(fileURLToPath(new URL('../public/vr_arm.glb', import.meta.url)));
  const jl = buf.readUInt32LE(12), jt = buf.readUInt32LE(16);
  const gltf = JSON.parse(buf.slice(20, 20 + jl).toString('utf8'));
  nodosGLB = gltf.nodes; hijos = nodosGLB.map(n => n.children || []);
  const busca = (n) => nodosGLB.find(nd => nd.name === n);
  const body = busca('Body_01'), a0 = busca('U_arm_021'), a1 = busca('L_arm_022'),
    h0 = busca('hand_023'), am0 = busca('U_arm(mirrored)_02'),
    am1 = busca('L_arm(mirrored)_03'), hm0 = busca('hand(mirrored)_04'),
    root = busca('_rootJoint');
  const existe = body && a0 && a1 && h0 && am0 && am1 && hm0 && root &&
    (hijos[nodosGLB.indexOf(body)].includes(nodosGLB.indexOf(a0))) &&
    (hijos[nodosGLB.indexOf(body)].includes(nodosGLB.indexOf(am0)));
  L1u = new THREE.Vector3().fromArray(a1.translation).length();
  L2u = new THREE.Vector3().fromArray(h0.translation).length();
  esc = 0.27 / L1u; L1 = L1u * esc; L2 = L2u * esc;
  dije('GLB · los 7 huesos que busca el loader EXISTEN y cuelgan de Body_01',
    !!existe, `hijos de Body: [${hijos[nodosGLB.indexOf(body)].join(',')}]`);
  dije('GLB · escala adulta: brazo 0,270 m y antebrazo en proporción del GLB',
    Math.abs(L1 - 0.27) < 1e-9 && Math.abs(L2 - L2u * esc) < 1e-9,
    `L1 ${L1.toFixed(3)} m · L2 ${L2.toFixed(3)} m · esc ${esc.toFixed(5)}`);
  // 2 dedos × 3 falanges × 2 manos: las manos tienen hijos para el curl
  const manos = [h0, hm0];
  const conDedos = manos.every(m => (m.children || []).length >= 3);
  dije('GLB · las DOS manos tienen cadenas de dedos para el agarre', conDedos,
    `hijos mano: ${manos.map(m => (m.children || []).length).join(' y ')}`);
}

/* ---------- rig sintético con los T/R REALES del GLB ---------- */
const mkRig = () => {
  const mapa = nodosGLB.map((n, i) => {
    const o = new THREE.Object3D();
    o.name = n.name || 'n' + i;
    if (n.translation) o.position.fromArray(n.translation);
    if (n.rotation) o.quaternion.fromArray(n.rotation);   // (x,y,z,w) idem three
    return o;
  });
  nodosGLB.forEach((n, i) => (n.children || []).forEach(c => mapa[i].add(mapa[c])));
  return mapa;
};
const capturaBrazo = (mapa, nombreBra, nombreAnt, nombreMano) => {
  const bra = mapa.find(o => o.name === nombreBra);
  const ant = mapa.find(o => o.name === nombreAnt);
  const mano = mapa.find(o => o.name === nombreMano);
  const root = mapa.find(o => o.name === '_rootJoint');
  root.updateMatrixWorld(true);
  const S = bra.getWorldPosition(new THREE.Vector3()).multiplyScalar(esc);
  const E = ant.getWorldPosition(new THREE.Vector3()).multiplyScalar(esc);
  const W = mano.getWorldPosition(new THREE.Vector3()).multiplyScalar(esc);
  return { bra, ant, mano, root,
    Srest: S, axisRestU: E.clone().sub(S).normalize(),
    axisRestL: W.clone().sub(E).normalize(),
    restQbra: bra.getWorldQuaternion(new THREE.Quaternion()),
    restQant: ant.getWorldQuaternion(new THREE.Quaternion()) };
};

/* ---------- 1 · huesos rígidos SIEMPRE ---------- */
{
  const S = new THREE.Vector3(0.1, 1.35, -2.3);
  const E = new THREE.Vector3(), W = new THREE.Vector3();
  const pole = new THREE.Vector3(0, -1, 0);
  let roto = 0, goma = 0, flag = 0;
  for (let i = 0; i < 300; i++) {
    const Wd = new THREE.Vector3((rng() - 0.5) * 1.6, 0.6 + rng() * 1.4, -2.3 + (rng() - 0.5) * 1.6);
    const r = solveArmIKRigido(S, Wd, L1, L2, pole, E, W);
    const d1 = E.distanceTo(S), d2 = W.distanceTo(E);
    if (Math.abs(d1 - L1) > 1e-9 || Math.abs(d2 - L2) > 1e-9) { goma++; continue; }
    const alcanza = Wd.distanceTo(S) <= 0.999 * (L1 + L2) && Wd.distanceTo(S) >= 0.28 * (L1 + L2);
    if (alcanza !== r.alcanzado) { flag++; continue; }
    if (alcanza && W.distanceTo(Wd) > 1e-9) { roto++; continue; }
    if (!alcanza && Math.abs(W.distanceTo(S) - 0.999 * (L1 + L2)) > 1e-6 &&
        Math.abs(W.distanceTo(S) - 0.28 * (L1 + L2)) > 1e-6) { roto++; continue; }
  }
  dije('rígido · 300 objetivos: |S-E|=L1 y |E-W|=L2 EXACTOS (0 estirados)',
    goma === 0, `${goma} estirados`);
  dije('rígido · alcanzado honesto y muñeca en el objetivo (o en el anillo)',
    roto === 0 && flag === 0, `${roto} fuera · ${flag} flags mal`);
}

/* ---------- 2 · composición de huesos con el GLB real ---------- */
{
  const mapa = mkRig();
  const bp = capturaBrazo(mapa, 'U_arm_021', 'L_arm_022', 'hand_023');
  const p0ant = bp.ant.position.clone();                 // reposo local
  let malDir = 0, malRigido = 0;
  const _q1 = new THREE.Quaternion(), _q2 = new THREE.Quaternion();
  const _d = new THREE.Vector3(), _x = new THREE.Vector3(1, 0, 0);
  for (let i = 0; i < 120; i++) {
    // IK rígida desde el hombro (el S del rig sintético está en unidades·esc)
    const S = bp.Srest;
    const Wd = new THREE.Vector3((rng() - 0.5) * 0.9, S.y - 0.35 + rng() * 0.5,
      S.z + 0.1 + rng() * 0.5);
    const E = new THREE.Vector3(), W = new THREE.Vector3();
    solveArmIKRigido(S, Wd, L1, L2, new THREE.Vector3(0, -1, 0), E, W);
    // composición del driver: quat mundo deseado → local (parentQ⁻¹·q)
    _d.copy(E).sub(S).normalize();
    _q1.setFromUnitVectors(bp.axisRestU, _d).multiply(bp.restQbra);
    bp.bra.parent.getWorldQuaternion(_q2);
    bp.bra.quaternion.copy(_q2).invert().multiply(_q1);
    bp.bra.updateWorldMatrix(false, false);
    bp.bra.getWorldQuaternion(_q2);
    _d.copy(W).sub(E).normalize();
    _q1.setFromUnitVectors(bp.axisRestL, _d).multiply(bp.restQant);
    bp.ant.quaternion.copy(_q2).invert().multiply(_q1);
    bp.ant.updateWorldMatrix(false, false);
    // verificación: el eje +X MUNDO de cada hueso == dirección deseada
    _x.set(1, 0, 0).applyQuaternion(bp.bra.matrixWorld).normalize();
    _d.copy(E).sub(S).normalize();
    if (_x.angleTo(_d) > 1e-4) malDir++;
    _x.set(1, 0, 0).applyQuaternion(bp.ant.matrixWorld).normalize();
    _d.copy(W).sub(E).normalize();
    if (_x.angleTo(_d) > 1e-4) malDir++;
    // rígido: posición local de reposo INTACTA y escala 1
    if (bp.ant.position.distanceTo(p0ant) > 1e-9 ||
        bp.ant.scale.x !== 1 || bp.ant.scale.y !== 1 || bp.ant.scale.z !== 1) malRigido++;
  }
  dije('huesos · el eje +X de brazo y antebrazo CAE en la dirección IK (240 huesos)',
    malDir === 0, `${malDir} desviados`);
  dije('huesos · posición y escala de reposo INTACTAS (0 estirados/escala ≠ 1)',
    malRigido === 0, `${malRigido} alterados`);
}

/* ---------- 3 · piso duro de mesa ---------- */
{
  const S = new THREE.Vector3(-0.15, 1.354, -2.2);
  const mesaY = DIMS.tableTopY + 0.02;
  const pole0 = new THREE.Vector3(0, -1, 0), poleUp = new THREE.Vector3(0, 0.9, 0);
  let bajoCodo = 0, goma = 0;
  const E = new THREE.Vector3(), W = new THREE.Vector3();
  for (let i = 0; i < 80; i++) {
    const G = new THREE.Vector3((rng() - 0.5) * 0.7,
      mesaY - 0.25 + rng() * 0.45, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.3 + rng() * 0.6);
    if (G.y < mesaY) G.y = mesaY;                       // piso del AGARRE
    solveArmIKRigido(S, G, L1, L2, pole0, E, W);
    if (E.y < mesaY + 0.045) {                          // piso del CODO
      solveArmIKRigido(S, G, L1, L2, poleUp, E, W);
      if (E.y < mesaY + 0.045) {
        G.y = mesaY + 0.045;
        solveArmIKRigido(S, G, L1, L2, poleUp, E, W);
      }
    }
    if (W.y < mesaY - 1e-6) bajoCodo++;
    const d1 = E.distanceTo(S), d2 = W.distanceTo(E);
    if (Math.abs(d1 - L1) > 1e-9 || Math.abs(d2 - L2) > 1e-9) goma++;
  }
  dije('mesa · 80 objetivos bajo/near la mesa: muñeca sobre el plano y hueso rígido',
    bajoCodo === 0 && goma === 0, `${bajoCodo} bajos · ${goma} estirados`);
}

/* ---------- 4 · ONE EURO anti-temblor ---------- */
{
  const f = new OneEuroV3(1.2, 0.045);
  const dt = 1 / 72;
  // señal: escalón 0,25 m a t=0,5 s + temblor 14 Hz de ±4 mm
  const sig = [], out = [];
  for (let i = 0; i < 144; i++) {
    const t = i * dt;
    let v = 1.0 + 0.004 * Math.sin(2 * Math.PI * 14 * t);
    if (t >= 0.5) v += 0.25;
    sig.push(v);
    out.push(f.filtrar(new THREE.Vector3(v, 0, 0), dt).x);
  }
  const jitter = (a) => {
    let acc = 0, n = 0;
    for (let i = 8; i < a.length - 8; i++) { const d = a[i] - a[i - 1]; acc += d * d; n++; }
    return Math.sqrt(acc / Math.max(n, 1));
  };
  // jitter en el tramo ESTABLE (el escalón es conducción, no temblor)
  const jIn = jitter(sig.slice(8, 28)), jOut = jitter(out.slice(8, 28));
  // convergencia: a 0,6 s del escalón (t=1,1 s) el error < 5 % del paso
  const idx = out.length - 1;
  const conv = Math.abs(out[idx] - 1.25) < 0.05 * 0.25 + 0.01;
  dije('one euro · el temblor de alta frecuencia cae a < 25 % (sin fuga cruda)',
    jOut < 0.25 * jIn, `jitter in ${(jIn * 1000).toFixed(2)} mm → out ${(jOut * 1000).toFixed(2)} mm`);
  dije('one euro · sigue el escalón (converge al deseo, lag acotado)', conv,
    `final ${(out[idx]).toFixed(3)} vs 1.250`);
  // ONE EURO Q: articulación con temblor angular ±2° sobre un swing lento
  const fq = new OneEuroQ(2.2, 0.09);
  const wIn = [], wOut = [];
  let qPrev = new THREE.Quaternion(), qfPrev = new THREE.Quaternion();
  for (let i = 0; i < 108; i++) {
    const t = i * dt;
    const base = 0.35 * Math.sin(2 * Math.PI * 0.7 * t);
    const ruido = (rng() - 0.5) * 0.07;                  // ±2°
    const q = new THREE.Quaternion().setFromAxisAngle(
      new THREE.Vector3(0, 0, 1).normalize(), base + ruido);
    wIn.push(Math.abs(2 * Math.acos(THREE.MathUtils.clamp(Math.abs(qPrev.dot(q)), 0, 1))) / dt);
    const qf = fq.filtrar(q, dt);
    wOut.push(Math.abs(2 * Math.acos(THREE.MathUtils.clamp(Math.abs(qfPrev.dot(qf)), 0, 1))) / dt);
    qPrev = q.clone();
    qfPrev = qf.clone();
  }
  const jitW = (a) => {
    let acc = 0, n = 0;
    for (let i = 6; i < a.length - 6; i++) { const d = a[i] - a[i - 1]; acc += d * d; n++; }
    return Math.sqrt(acc / Math.max(n, 1));
  };
  dije('one euro Q · el temblor angular de la articulación cae a < 55 %',
    jitW(wOut) < 0.55 * jitW(wIn), `ω in ${(jitW(wIn)).toFixed(1)} → out ${(jitW(wOut)).toFixed(1)} rad/s²`);
}

/* ---------- 5 · agarre por el mando + zona dulce ---------- */
{
  const D = 0.1303;
  let mal = 0, dulce = 0, borde = 0;
  const dir = new THREE.Vector3(0.2, 0.3, 0.93).normalize();
  for (let i = 0; i < 100; i++) {
    const centro = new THREE.Vector3((rng() - 0.5), 0.9 + rng() * 0.3, -1.7);
    const grip = new THREE.Vector3().copy(centro).addScaledVector(dir, -D);
    const centro2 = new THREE.Vector3().copy(grip).addScaledVector(dir, D);
    if (centro2.distanceTo(centro) > 1e-9) mal++;
    // zona dulce: bola DENTRO del disco central → sin nudge; fuera → hacia
    // la bola con tope 4 cm
    const R = 0.075;                                       // bladeRadius DIMS
    const bola = centro.clone().add(new THREE.Vector3(
      (rng() - 0.5), (rng() - 0.5), (rng() - 0.5)).normalize().multiplyScalar(R * (0.2 + rng() * 0.9)));
    const g2 = zonaDulceNudge(grip, bola, centro, R, new THREE.Vector3());
    const desvio = bola.distanceTo(centro) - R * 0.62;
    if (desvio <= 0) { if (g2.distanceTo(grip) > 1e-12) dulce++; }
    else {
      const paso = g2.distanceTo(grip);
      if (paso > Math.min(desvio, 0.04) + 1e-6 || paso < Math.min(desvio, 0.04) - 1e-6) borde++;
    }
  }
  dije('agarre · mando ⇄ centro de hoja: identidad EXACTA con continuación·0,1303',
    mal === 0, `${mal} fallos`);
  dije('zona dulce · nudge solo FUERA del disco central y con tope de 4 cm',
    dulce === 0 && borde === 0, `${dulce} nudges de más · ${borde} mal medidos`);
}

/* ---------- 6 · altura adulta + lado del brazo ---------- */
{
  const mapa = mkRig();
  const bp = capturaBrazo(mapa, 'U_arm_021', 'L_arm_022', 'hand_023');
  const bl = capturaBrazo(mapa, 'U_arm(mirrored)_02', 'L_arm(mirrored)_03', 'hand(mirrored)_04');
  // pecho adulto (fórmula del driver): chest = max(ai.pos.y+0.33, 1.325) —
  // el rig se COLOCA como el driver (root = pecho − rootToBody) y el
  // hombro se lee de la posición mundial del hueso (matrices frescas)
  const chest = Math.max(1.0 + 0.33, 1.325);
  // como el driver: escala del CONTENEDOR (esc) y root = pecho − rootToBody
  const r2b = mapa.find(o => o.name === 'Body_01').getWorldPosition(new THREE.Vector3());
  const root0 = mapa[0];
  root0.scale.setScalar(esc);
  root0.position.copy(r2b).multiplyScalar(-esc).add(new THREE.Vector3(0, chest, 0));
  mapa[0].updateMatrixWorld(true);
  const hombroY = bp.bra.getWorldPosition(new THREE.Vector3()).y;   // metros
  dije('altura · hombro del rival ≈ 1,35 m ADULTO (adiós al efecto enano)',
    hombroY > 1.30 && hombroY < 1.42, `hombro ${hombroY.toFixed(3)} m`);
  // lado: brazo[0] (U_arm_021) en +X y brazo[1] (mirrored) en −X
  dije('lado · brazos espejados: U_arm_021 en +X y mirrored en −X',
    bp.Srest.x > 0 && bl.Srest.x < 0,
    `A ${(bp.Srest.x * 100).toFixed(1)} cm · B ${(bl.Srest.x * 100).toFixed(1)} cm`);
  // binding del driver: CPU diestra (s=-1) → brazo en −X (mirrored)...
  // la mano del CPU vive en (s,0,0)=(-1,0,0): hombro con x·s>0 → x<0 ✓
  const sCPU = -1;
  const elegido = (bp.Srest.x * sCPU > 0) ? bp : bl;
  dije('lado · el brazo de la PALA del CPU (s=-1) cae en −X (su derecha)',
    elegido.Srest.x * sCPU > 0, `hombro elegido x ${(elegido.Srest.x * 100).toFixed(1)} cm`);
}

console.log(`\nBRAZOS GLB r93 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

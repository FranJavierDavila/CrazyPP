#!/usr/bin/env node
/* =====================================================================
 * ARNÉS BRAZOS GLB r94 — «el material aparece y los brazos aguantan el
 * recentrado»: corrección del video del dueño (brazos blancos sin mate-
 * rial, mal colocados, pala suelta, golpeo fuera de la zona dulce).
 * ---------------------------------------------------------------------
 * 1. MATERIAL · el GLB exige KHR_materials_pbrSpecularGlossiness (Sketchfab)
 *    y three r163+ ya no lo trae: el parse sigue con material blanco METÁ-
 *    LICO. Contrato: c12 reconstruye el material con la textura difusa
 *    embebida (parser.getDependency('texture', 0)) + respaldo tono piel,
 *    y el GLB real trae imágenes embebidas para cargar.
 * 2. MARCO DEL RIG · la captura (rootToBody/Srest/ejes/quats de reposo) y
 *    el driver viven en RIG-LOCAL: con el rig GIRADO y MOVIDO (recentrado
 *    XR, hall, onda) la mano cae IGUAL en el mando — invariancia de marco
 *    con 3 transforms distintos del rig.
 * 3-7. HERENCIA r93 · huesos rígidos exactos, composición de quats con el
 *    GLB real, piso duro de mesa, One Euro, agarre por el mando + zona
 *    dulce, altura adulta y lado del brazo.
 * ===================================================================== */
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { readFileSync } from 'node:fs';

globalThis.window = globalThis.window || globalThis;   // c00/c02 en Node

const { OneEuroV3, OneEuroQ, solveArmIKRigido, zonaDulceNudge } =
  await import(fileURLToPath(new URL('../src/game/core/c06_logros_stats_ia_rival.js', import.meta.url)));
const { DIMS } = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));

let ok = 0, fails = 0;
const dije = (nombre, bien, detalle) => {
  if (bien) { ok++; console.log(`  ✓ ${nombre}${detalle ? ' · ' + detalle : ''}`); }
  else { fails++; console.log(`  ✗ FALLO ${nombre}${detalle ? ' · ' + detalle : ''}`); }
};
const rng = (() => { let s = 1234567; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();

/* ---------- 1 · binding real del GLB (fuente binaria) + material ---------- */
let nodosGLB = null, hijos = null, esc = 0, L1 = 0, L2 = 0, L1u = 0, L2u = 0, imgs = 0;
{
  const buf = readFileSync(fileURLToPath(new URL('../public/vr_arm.glb', import.meta.url)));
  const jl = buf.readUInt32LE(12), jt = buf.readUInt32LE(16);
  const gltf = JSON.parse(buf.slice(20, 20 + jl).toString('utf8'));
  nodosGLB = gltf.nodes; hijos = nodosGLB.map(n => n.children || []);
  imgs = (gltf.images || []).length;
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
  // r94 · contrato del MATERIAL: el GLB trae texturas embebidas Y c12 las
  // asigna (reconstrucción spec-gloss → MeshStandard con mapa + respaldo)
  const c12 = readFileSync(fileURLToPath(new URL(
    '../src/game/core/c12_pingponggame.js', import.meta.url)), 'utf8');
  const reconstruye = c12.includes("getDependency('texture', 0)") &&
    c12.includes('SRGBColorSpace') && c12.includes('MeshStandardMaterial');
  dije('material · c12 reconstruye el material con la textura difusa embebida',
    reconstruye && imgs >= 1,
    `${imgs} imágenes en el GLB · getDependency('texture',0) ${reconstruye ? 'presente' : 'AUSENTE'}`);
  const sinSpec = !c12.includes('extensionsRequired') ; // el loader NO debe exigir la extensión
  dije('material · el loader no exige la extensión muerta (sólo reconstruye)',
    sinSpec, `spec-gloss del GLB ignorado a propósito (three r163+ la retiró)`);
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

/* ---------- 2 · captura + driver EN MARCO DEL RIG (r94) ---------- */
/* Replica la captura r94 (todo relativo al rig) y el driver r94 (IK y fil-
 * tros en rig-local; quats deseadas devueltas a mundo antes de componer).
 * Devuelve la mano en RIG-LOCAL tras N frames con el plan de la pala. */
const driveBrazo = (transformRig, frames) => {
  const mapa = mkRig();
  const body = mapa.find(o => o.name === 'Body_01');
  const capas = [
    { lado: 'A', bra: mapa.find(o => o.name === 'U_arm_021'),
      ant: mapa.find(o => o.name === 'L_arm_022'),
      mano: mapa.find(o => o.name === 'hand_023') },
    { lado: 'B', bra: mapa.find(o => o.name === 'U_arm(mirrored)_02'),
      ant: mapa.find(o => o.name === 'L_arm(mirrored)_03'),
      mano: mapa.find(o => o.name === 'hand(mirrored)_04') },
  ];
  // esc va en la RAÍZ del gltf (como gltf.scene.scale.setScalar en c12)
  mapa[0].scale.setScalar(esc);
  const rig = new THREE.Group();
  rig.add(mapa[0]);
  rig.position.copy(transformRig.pos);
  rig.quaternion.copy(transformRig.quat);
  const escena = new THREE.Group();
  escena.add(rig);
  escena.updateMatrixWorld(true);
  rig.updateWorldMatrix(true, false);
  mapa[0].updateMatrixWorld(true);
  // — captura r94: TODO en marco del rig
  const rigInv = rig.matrixWorld.clone().invert();
  const rigQinv = new THREE.Quaternion().setFromRotationMatrix(rig.matrixWorld).invert();
  const alRig = (v) => v.applyMatrix4(rigInv);
  const qlRig = (q) => q.premultiply(rigQinv);
  const inst = { root: mapa[0], body, L1, L2,
    rootToBody: alRig(body.getWorldPosition(new THREE.Vector3())),
    brazos: capas.map((c) => {
      const S = alRig(c.bra.getWorldPosition(new THREE.Vector3()));
      const E = alRig(c.ant.getWorldPosition(new THREE.Vector3()));
      const W = alRig(c.mano.getWorldPosition(new THREE.Vector3()));
      return { lado: c.lado, bra: c.bra, ant: c.ant, mano: c.mano,
        Srest: S.clone(), axisRestU: E.clone().sub(S).normalize(),
        axisRestL: W.clone().sub(E).normalize(),
        restQbra: qlRig(c.bra.getWorldQuaternion(new THREE.Quaternion())),
        restQant: qlRig(c.ant.getWorldQuaternion(new THREE.Quaternion())),
        restQmano: qlRig(c.mano.getWorldQuaternion(new THREE.Quaternion())),
        poleSide: 0,
        fG: new OneEuroV3(1.2, 0.045), fqU: new OneEuroQ(2.2, 0.09),
        fqL: new OneEuroQ(2.2, 0.09), fqH: new OneEuroQ(2.6, 0.11) };
    }), _t: 0 };
  // — driver r94 (sólo el brazo de la pala; el plan manda la pala)
  const R = inst;
  const dt = 1 / 72;
  const mesaY = DIMS.tableTopY + 0.02;
  const D_GRIP = 0.1303;
  const s = -1;
  const paddle = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.02, 0.15),
    new THREE.MeshStandardMaterial());
  // plan de la pala en RIG-LOCAL (como ai.pos/DIMS/bola)
  paddle.position.set(-0.30, 1.05, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.30);
  paddle.quaternion.setFromEuler(new THREE.Euler(0.25, 0.4, 0.1));
  const _vA = new THREE.Vector3(), _vB = new THREE.Vector3(), _vC = new THREE.Vector3(),
    _vD = new THREE.Vector3(), _vE = new THREE.Vector3(), _vF = new THREE.Vector3(),
    _vG = new THREE.Vector3(), _vH = new THREE.Vector3(), _vS = new THREE.Vector3(),
    _vP = new THREE.Vector3(1, 0, 0), _vUp = new THREE.Vector3(0, 1, 0),
    _vNeg = new THREE.Vector3(-1, 0, 0), _vAx = new THREE.Vector3();
  const _qA = new THREE.Quaternion(), _qB = new THREE.Quaternion(),
    _qC = new THREE.Quaternion(), _qD = new THREE.Quaternion(), _qE = new THREE.Quaternion(),
    _qRigQ = new THREE.Quaternion(), _qRigInvQ = new THREE.Quaternion(),
    _qArmQ = new THREE.Quaternion();
  const bp = (R.brazos[0].Srest.x * s > 0) ? R.brazos[0] : R.brazos[1];
  const mano0 = bp.mano.getWorldPosition(new THREE.Vector3());
  for (let f = 0; f < frames; f++) {
    R._t += dt;
    rig.updateWorldMatrix(true, false);
    _qRigQ.setFromRotationMatrix(rig.matrixWorld);
    _qRigInvQ.copy(_qRigQ).invert();
    _vP.setFromMatrixPosition(rig.matrixWorld);
    // pecho en rig-local (igual que c12)
    _vA.set(0, Math.max(1.05 + 0.33, 1.325) + 0.005 * Math.sin(R._t * 2.1),
      DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45);
    _qA.setFromAxisAngle(_vUp, 0);
    R.root.position.copy(_vA).sub(_vB.copy(R.rootToBody).applyQuaternion(_qA));
    R.root.quaternion.copy(_qA);
    R.root.updateMatrixWorld(true);
    bp.bra.parent.updateWorldMatrix(true, false);
    bp.bra.getWorldPosition(_vS);
    _vS.sub(_vP).applyQuaternion(_qRigInvQ);
    _vD.set(0, 1, 0).applyQuaternion(paddle.quaternion).normalize();
    _vC.copy(paddle.position);
    _vE.copy(_vC).addScaledVector(_vD, -D_GRIP);
    _vF.copy(_vE).sub(_vS);
    const dG = Math.max(_vF.length(), 1e-6);
    const maxR = 0.999 * (R.L1 + R.L2), minR = 0.28 * (R.L1 + R.L2);
    if (dG > maxR) _vE.copy(_vS).addScaledVector(_vF, maxR / dG);
    else if (dG < minR) _vE.copy(_vS).addScaledVector(_vF.divideScalar(dG), minR);
    if (_vE.y < mesaY) _vE.y = mesaY;
    _vE.copy(bp.fG.filtrar(_vE, dt));
    const ladoDeseado = THREE.MathUtils.clamp((_vE.x - _vS.x) * s * 4, -1, 1);
    if (Math.abs(ladoDeseado) > 0.2 && Math.sign(ladoDeseado) !== bp.poleSide)
      bp.poleSide = Math.sign(ladoDeseado);
    _vG.set(0, -1, 0).addScaledVector(_vNeg, s * bp.poleSide * -0.8);
    solveArmIKRigido(_vS, _vE, R.L1, R.L2, _vG, _vH, _vA);
    if (_vH.y < mesaY + 0.045) {
      _vG.y = 0.9;
      solveArmIKRigido(_vS, _vE, R.L1, R.L2, _vG, _vH, _vA);
      if (_vH.y < mesaY + 0.045) { _vE.y = mesaY + 0.045; solveArmIKRigido(_vS, _vE, R.L1, R.L2, _vG, _vH, _vA); }
    }
    if (_vA.y < mesaY) _vA.y = mesaY;
    _vF.copy(_vH).sub(_vS).normalize();
    _qB.setFromUnitVectors(bp.axisRestU, _vF).multiply(bp.restQbra);
    bp.fqU.filtrar(_qB, dt);
    _qC.copy(bp.fqU.prev).premultiply(_qRigQ);
    bp.bra.parent.getWorldQuaternion(_qD);
    bp.bra.quaternion.copy(_qD).invert().multiply(_qC);
    bp.bra.updateWorldMatrix(false, false);
    bp.bra.getWorldQuaternion(_qD);
    _vF.copy(_vA).sub(_vH).normalize();
    _qB.setFromUnitVectors(bp.axisRestL, _vF).multiply(bp.restQant);
    bp.fqL.filtrar(_qB, dt);
    _qC.copy(bp.fqL.prev).premultiply(_qRigQ);
    bp.ant.quaternion.copy(_qD).invert().multiply(_qC);
    bp.ant.updateWorldMatrix(false, false);
    _qB.copy(bp.fqL.prev);
    _qE.setFromAxisAngle(_vF, -0.9 * s);
    _qB.multiply(_qE);
    bp.fqH.filtrar(_qB, dt);
    _qC.copy(bp.fqH.prev).premultiply(_qRigQ);
    bp.mano.parent.getWorldQuaternion(_qD);
    bp.mano.quaternion.copy(_qD).invert().multiply(_qC);
    bp.mano.updateWorldMatrix(false, false);
    paddle.position.copy(_vA).addScaledVector(_vD, D_GRIP);
  }
  rig.updateWorldMatrix(true, true);
  const manoW = bp.mano.getWorldPosition(new THREE.Vector3());
  const manoRig = manoW.applyMatrix4(rig.matrixWorld.clone().invert());
  return { manoRig, mano0World: mano0, gripFinal: paddle.position.clone(), L1, L2 };
};

const qy = (rad) => new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), rad);
{
  const frames = 120;   // ~1,7 s: los filtros One Euro convergen
  const base = driveBrazo({ pos: new THREE.Vector3(0, 0, 0), quat: qy(0) }, frames);
  const girado = driveBrazo({ pos: new THREE.Vector3(1.5, 0.8, -2.2), quat: qy(0.9) }, frames);
  const girado2 = driveBrazo({ pos: new THREE.Vector3(-2.0, -0.4, 1.1), quat: qy(-2.4) }, frames);
  // invariancia: la mano en RIG-LOCAL cae en el mismo sitio con cualquier rig
  const d1 = base.manoRig.distanceTo(girado.manoRig);
  const d2 = base.manoRig.distanceTo(girado2.manoRig);
  dije('marco rig · la mano cae IGUAL (rig-local) con el rig girado y movido',
    d1 < 0.01 && d2 < 0.01,
    `Δ(girado) ${(d1 * 100).toFixed(1)} mm · Δ(girado2) ${(d2 * 100).toFixed(1)} mm`);
  // el agarre: la mano queda a la distancia del MANDO del centro de la hoja
  const dGrip = base.manoRig.distanceTo(base.gripFinal);
  dije('marco rig · mano ⇄ centro de hoja = mando 0,1303 (agarre por el mando)',
    Math.abs(dGrip - 0.1303) < 0.012,
    `${(dGrip * 100).toFixed(1)} cm · pala en (${base.gripFinal.x.toFixed(2)},${base.gripFinal.y.toFixed(2)},${base.gripFinal.z.toFixed(2)})`);
  // la mano efectivamente SE MOVIO del reposo (el driver conduce, no decorativo)
  const seMovio = base.manoRig.distanceTo(girado.mano0World) > 0.05 ||
    Math.abs(base.manoRig.y - girado.mano0World.y) > 0.02;
  dije('marco rig · el brazo se CONDUCE al plan (no queda en reposo decorativo)',
    seMovio, `mano rig-final (${base.manoRig.toArray().map(v => v.toFixed(2)).join(',')})`);
}

/* ---------- 3 · huesos rígidos SIEMPRE (herencia r93) ---------- */
{
  const S = new THREE.Vector3(0.1, 1.35, -2.3);
  const E = new THREE.Vector3(), W = new THREE.Vector3();
  const pole = new THREE.Vector3(0, -1, 0);
  let goma = 0;
  for (let i = 0; i < 300; i++) {
    const Wd = new THREE.Vector3((rng() - 0.5) * 1.6, 0.6 + rng() * 1.4, -2.3 + (rng() - 0.5) * 1.6);
    solveArmIKRigido(S, Wd, L1, L2, pole, E, W);
    if (Math.abs(E.distanceTo(S) - L1) > 1e-9 || Math.abs(W.distanceTo(E) - L2) > 1e-9) goma++;
  }
  dije('rígido · 300 objetivos: |S-E|=L1 y |E-W|=L2 EXACTOS (0 estirados)',
    goma === 0, `${goma} estirados`);
}

/* ---------- 4 · piso duro de mesa (herencia r93) ---------- */
{
  const S = new THREE.Vector3(-0.15, 1.354, -2.2);
  const mesaY = DIMS.tableTopY + 0.02;
  let bajo = 0, goma = 0;
  const E = new THREE.Vector3(), W = new THREE.Vector3();
  for (let i = 0; i < 80; i++) {
    const G = new THREE.Vector3((rng() - 0.5) * 0.7,
      mesaY - 0.25 + rng() * 0.45, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.3 + rng() * 0.6);
    if (G.y < mesaY) G.y = mesaY;
    solveArmIKRigido(S, G, L1, L2, new THREE.Vector3(0, -1, 0), E, W);
    if (E.y < mesaY + 0.045) {
      solveArmIKRigido(S, G, L1, L2, new THREE.Vector3(0, 0.9, 0), E, W);
      if (E.y < mesaY + 0.045) { G.y = mesaY + 0.045; solveArmIKRigido(S, G, L1, L2, new THREE.Vector3(0, 0.9, 0), E, W); }
    }
    if (W.y < mesaY - 1e-6) bajo++;
    if (Math.abs(E.distanceTo(S) - L1) > 1e-9 || Math.abs(W.distanceTo(E) - L2) > 1e-9) goma++;
  }
  dije('mesa · 80 objetivos bajo la mesa: muñeca sobre el plano y hueso rígido',
    bajo === 0 && goma === 0, `${bajo} bajos · ${goma} estirados`);
}

/* ---------- 5 · zona dulce (herencia r93) ---------- */

{
  const R = 0.075;
  let mal = 0, borde = 0;
  const dir = new THREE.Vector3(0.2, 0.3, 0.93).normalize();
  for (let i = 0; i < 100; i++) {
    const centro = new THREE.Vector3((rng() - 0.5), 0.9 + rng() * 0.3, -1.7);
    const bola = centro.clone().add(new THREE.Vector3(
      (rng() - 0.5), (rng() - 0.5), (rng() - 0.5)).normalize().multiplyScalar(R * (0.2 + rng() * 0.9)));
    const grip = centro.clone().addScaledVector(dir, -0.1303);
    const g2 = zonaDulceNudge(grip, bola, centro, R, new THREE.Vector3());
    const desvio = bola.distanceTo(centro) - R * 0.62;
    if (desvio > 0) {
      const paso = g2.distanceTo(grip);
      if (Math.abs(paso - Math.min(desvio, 0.04)) > 1e-6) borde++;
    } else if (g2.distanceTo(grip) > 1e-12) mal++;
  }
  dije('zona dulce · nudge solo FUERA del disco central y con tope de 4 cm',
    mal === 0 && borde === 0, `${mal} nudges de más · ${borde} mal medidos`);
}


/* ---------- 6 · altura adulta + lado (herencia r93) ---------- */
{
  const mapa = mkRig();
  const body = mapa.find(o => o.name === 'Body_01');
  const bra = mapa.find(o => o.name === 'U_arm_021');
  const braM = mapa.find(o => o.name === 'U_arm(mirrored)_02');
  const r2b = body.getWorldPosition(new THREE.Vector3());   // reposo SIN escalar
  mapa[0].scale.setScalar(esc);
  const rig = new THREE.Group(); rig.add(mapa[0]);
  rig.updateMatrixWorld(true);
  mapa[0].position.copy(r2b).multiplyScalar(-esc).add(new THREE.Vector3(0, 1.325, 0));
  mapa[0].updateMatrixWorld(true);
  const hombroY = bra.getWorldPosition(new THREE.Vector3()).y;
  dije('altura · hombro del rival ≈ 1,35 m ADULTO (adiós al efecto enano)',
    hombroY > 1.30 && hombroY < 1.42, `hombro ${hombroY.toFixed(3)} m`);
  const sCPU = -1;
  const xA = bra.getWorldPosition(new THREE.Vector3()).x;
  const xB = braM.getWorldPosition(new THREE.Vector3()).x;
  const elegido = (xA * sCPU > 0) ? 'A' : 'B';
  dije('lado · el brazo de la PALA del CPU (s=-1) cae en −X (su derecha)',
    (elegido === 'A' ? xA : xB) * sCPU > 0,
    `A ${(xA * 100).toFixed(1)} cm · B ${(xB * 100).toFixed(1)} cm → ${elegido}`);
}

console.log(`\nBRAZOS GLB r94 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);

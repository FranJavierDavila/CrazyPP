// REPRODUCCIÓN r94 del camino de producción REAL: parse GLTFLoader three
// 0.186 + _cargarArmasGLB (verbatim c12) + updateAIArmGlb (verbatim c12)
// con entradas realistas de partida (ai en su home, pala en plan, bola).
// Objetivo: ver dónde caen hombro/codo/muñeca/pala y qué queda suelto.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { readFileSync } from 'node:fs';

globalThis.self = globalThis;   // GLTFLoader en Node
globalThis.window = globalThis; // c06/c02 en Node (igual que el arnés r93)

const { solveArmIKRigido, zonaDulceNudge, OneEuroV3, OneEuroQ } =
  await import('/home/z/my-project/src/game/core/c06_logros_stats_ia_rival.js');
const { DIMS } = await import('/home/z/my-project/src/game/core/c02_cfg_escena.js');

// ---------- 1 · parse real ----------
const buf = readFileSync('/home/z/my-project/tmp_assets/vr_arm_notex.glb');
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
let gltf;
try {
  gltf = await new Promise((res, rej) => new GLTFLoader().parse(ab, '', res, rej));
  console.log('PARSE OK (warn spec-gloss esperado)');
} catch (e) {
  console.log('PARSE FALLÓ:', e.message);
  process.exit(1);
}

// ---------- 2 · _cargarArmasGLB verbatim (c12:19632-19708) ----------
const nom = (b) => gltf.scene.getObjectByName(b);
const body = nom('Body_01');
const capas = [
  { lado: 'A', bra: nom('U_arm_021'), ant: nom('L_arm_022'), mano: nom('hand_023') },
  { lado: 'B', bra: nom('U_arm(mirrored)_02'), ant: nom('L_arm(mirrored)_03'),
    mano: nom('hand(mirrored)_04') },
];
if (!body || !capas[0].bra || !capas[0].ant || !capas[0].mano ||
    !capas[1].bra || !capas[1].ant || !capas[1].mano) {
  console.log('HUESOS NO ENCONTRADOS'); process.exit(1);
}
const L1u = capas[0].ant.position.length();
const L2u = capas[0].mano.position.length();
const esc = 0.27 / L1u;
gltf.scene.scale.setScalar(esc);
const L1 = L1u * esc, L2 = L2u * esc;
console.log(`esc ${esc.toFixed(5)} · L1 ${L1.toFixed(3)} · L2 ${L2.toFixed(3)}`);
const dedos = [];
for (const capa of capas) {
  const dc = [];
  capa.mano.children.forEach((f1) => {
    let ant = f1, curvatura = 0;
    while (ant && ant.children.length && ant.children[0].children !== undefined) {
      const sig = ant.children[0];
      curvatura += 0.5;
      const q = new THREE.Quaternion().setFromAxisAngle(
        new THREE.Vector3(0, 0, -1), Math.min(curvatura, 1.15));
      sig.quaternion.copy(q);
      dc.push(sig);
      ant = sig;
      if (dc.length > 14) break;
    }
  });
  dedos.push(dc);
}
console.log('dedos por mano:', dedos.map(d => d.length).join(' / '));
const root = new THREE.Group();
root.name = 'aiArmGlb';
root.add(gltf.scene);
// NOTA producción: root va dentro de this.rig (grupo sin transform en partida)
const rig = new THREE.Group();
rig.add(root);
root.updateMatrixWorld(true);
const inst = { root, body, L1, L2, listo: true, yaw: 0, esc,
  rootToBody: body.getWorldPosition(new THREE.Vector3()),
  brazos: capas.map((c, i) => {
    const S = c.bra.getWorldPosition(new THREE.Vector3());
    const E = c.ant.getWorldPosition(new THREE.Vector3());
    const W = c.mano.getWorldPosition(new THREE.Vector3());
    console.log(`  capa ${c.lado}: S(${S.x.toFixed(3)},${S.y.toFixed(3)},${S.z.toFixed(3)}) · W(${W.x.toFixed(3)},${W.y.toFixed(3)},${W.z.toFixed(3)})`);
    return { lado: c.lado, bra: c.bra, ant: c.ant, mano: c.mano, dedos: dedos[i],
      Srest: S.clone(), axisRestU: E.clone().sub(S).normalize(),
      axisRestL: W.clone().sub(E).normalize(),
      restQbra: c.bra.getWorldQuaternion(new THREE.Quaternion()),
      restQant: c.ant.getWorldQuaternion(new THREE.Quaternion()),
      restQmano: c.mano.getWorldQuaternion(new THREE.Quaternion()),
      poleSide: 0,
      fG: new OneEuroV3(1.2, 0.045),
      fqU: new OneEuroQ(2.2, 0.09),
      fqL: new OneEuroQ(2.2, 0.09),
      fqH: new OneEuroQ(2.6, 0.11) };
  }),
  _t: 0 };
console.log('rootToBody:', inst.rootToBody.toArray().map(v => v.toFixed(3)).join(','));

// ---------- 3 · updateAIArmGlb verbatim (c12:19718-19866) ----------
// estado de partida realista: ai en home (0,1.05,-1.82), sign -1, pala en
// plan de espera (lado -X, altura 1.0), bola en rally.
const _gA = new THREE.Vector3(); const _gB = new THREE.Vector3();
const _gC = new THREE.Vector3(); const _gD = new THREE.Vector3();
const _gE = new THREE.Vector3(); const _gF = new THREE.Vector3();
const _gG = new THREE.Vector3(); const _gH = new THREE.Vector3();
const _gQa = new THREE.Quaternion(); const _gQb = new THREE.Quaternion();
const _gQc = new THREE.Quaternion(); const _gQd = new THREE.Quaternion();
const _gQe = new THREE.Quaternion(); const _gS = new THREE.Vector3();
const _armA = new THREE.Vector3(); const _armBx = new THREE.Vector3();
const _armQ = new THREE.Quaternion(); const _armX = new THREE.Vector3(1, 0, 0);
const _gUp = new THREE.Vector3(0, 1, 0); const _gNeg = new THREE.Vector3(-1, 0, 0);
const ai = { sign: -1, pos: new THREE.Vector3(0, 1.05, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45),
  chain: null };
const paddleMesh = new THREE.Mesh(
  new THREE.BoxGeometry(0.15, 0.15, 0.02), new THREE.MeshStandardMaterial());
paddleMesh.position.set(-0.55, 1.0, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.30);
paddleMesh.quaternion.setFromEuler(new THREE.Euler(0.3, 0.2, 0.1));
const R = inst;
const dt = 1 / 72;
const mesaY = DIMS.tableTopY + 0.02;
const D_GRIP = 0.1303;
const s = ai.sign;
const ch = ai.chain;
const golpeando = !!(ch && (ch.phase === 'strike' || ch.phase === 'follow'));
const aiToss = null;
const rules = { state: 'rally', server: 'player' };
const calib = false;
const ball = { pos: new THREE.Vector3(0.2, 1.2, 0.5) };

let err = null;
try {
  for (let f = 0; f < 90; f++) {
    R._t += dt;
    _gA.set(ai.pos.x, Math.max(ai.pos.y + 0.33, 1.325) + 0.005 * Math.sin(R._t * 2.1), ai.pos.z);
    _gQa.setFromAxisAngle(_gUp, R.yaw);
    R.root.position.copy(_gA).sub(_gB.copy(R.rootToBody).applyQuaternion(_gQa));
    R.root.quaternion.copy(_gQa);
    R.root.updateMatrixWorld(true);
    const bp = (R.brazos[0].Srest.x * s > 0) ? R.brazos[0] : R.brazos[1];
    const bl = (bp === R.brazos[0]) ? R.brazos[1] : R.brazos[0];
    bp.bra.parent.updateWorldMatrix(true, false);
    bp.bra.parent.getWorldPosition(_gB);
    bp.bra.getWorldPosition(_gS);
    _gD.set(0, 1, 0).applyQuaternion(paddleMesh.quaternion);
    if (_gD.lengthSq() < 1e-8) _gD.set(0, 0, s < 0 ? 1 : -1);
    _gD.normalize();
    _gC.copy(paddleMesh.position);
    _gE.copy(_gC).addScaledVector(_gD, -D_GRIP);
    if (golpeando)
      _gE.copy(zonaDulceNudge(_gE, ball.pos, _gC, DIMS.bladeRadius, _gF));
    _gF.copy(_gE).sub(_gS);
    const dG = Math.max(_gF.length(), 1e-6);
    const maxR = 0.999 * (R.L1 + R.L2), minR = 0.28 * (R.L1 + R.L2);
    if (dG > maxR) _gE.copy(_gS).addScaledVector(_gF, maxR / dG);
    else if (dG < minR) _gE.copy(_gS).addScaledVector(_gF.divideScalar(dG), minR);
    if (_gE.y < mesaY) _gE.y = mesaY;
    bp.fG.fcMin = golpeando ? 6.5 : 1.2;
    _gE.copy(bp.fG.filtrar(_gE, dt));
    const ladoDeseado = THREE.MathUtils.clamp((_gE.x - _gS.x) * s * 4, -1, 1);
    if (Math.abs(ladoDeseado) > 0.2 && Math.sign(ladoDeseado) !== bp.poleSide)
      bp.poleSide = Math.sign(ladoDeseado);
    _gG.set(0, -1, 0).addScaledVector(_gNeg, s * bp.poleSide * -0.8);
    solveArmIKRigido(_gS, _gE, R.L1, R.L2, _gG, _gH, _gA);
    if (_gH.y < mesaY + 0.045) {
      _gG.y = 0.9;
      solveArmIKRigido(_gS, _gE, R.L1, R.L2, _gG, _gH, _gA);
      if (_gH.y < mesaY + 0.045) {
        _gE.y = mesaY + 0.045;
        solveArmIKRigido(_gS, _gE, R.L1, R.L2, _gG, _gH, _gA);
      }
    }
    if (_gA.y < mesaY) _gA.y = mesaY;
    bp.fqU.fcMin = golpeando ? 6.5 : 2.2;
    bp.fqL.fcMin = golpeando ? 6.5 : 2.2;
    bp.fqH.fcMin = golpeando ? 7 : 2.6;
    _gF.copy(_gH).sub(_gS).normalize();
    _gQb.setFromUnitVectors(bp.axisRestU, _gF).multiply(bp.restQbra);
    bp.fqU.filtrar(_gQb, dt);
    _gQc.copy(bp.fqU.prev);
    bp.bra.parent.getWorldQuaternion(_gQd);
    bp.bra.quaternion.copy(_gQd).invert().multiply(_gQc);
    bp.bra.updateWorldMatrix(false, false);
    bp.bra.getWorldQuaternion(_gQd);
    _gF.copy(_gA).sub(_gH).normalize();
    _gQb.setFromUnitVectors(bp.axisRestL, _gF).multiply(bp.restQant);
    bp.fqL.filtrar(_gQb, dt);
    _gQc.copy(bp.fqL.prev);
    bp.ant.quaternion.copy(_gQd).invert().multiply(_gQc);
    bp.ant.updateWorldMatrix(false, false);
    bp.ant.getWorldQuaternion(_gQd);
    _gQb.copy(_gQd);
    _gQe.setFromAxisAngle(_gF, -0.9 * s);
    _gQb.multiply(_gQe);
    bp.fqH.filtrar(_gQb, dt);
    bp.mano.parent.getWorldQuaternion(_gQd);
    bp.mano.quaternion.copy(_gQd).invert().multiply(bp.fqH.prev);
    bp.mano.updateWorldMatrix(false, false);
    paddleMesh.position.copy(_gA).addScaledVector(_gD, D_GRIP);
    _armA.set(0, 1, 0).applyQuaternion(paddleMesh.quaternion);
    const cosA = THREE.MathUtils.clamp(_armA.dot(_gF), -1, 1);
    _armBx.crossVectors(_armA, _gF);
    const sinA = _armBx.length();
    if (sinA > 1e-4 && Math.abs(cosA) < 0.99999) {
      _armQ.setFromAxisAngle(_armBx.divideScalar(sinA), Math.acos(cosA));
      paddleMesh.quaternion.premultiply(_armQ);
    } else if (sinA <= 1e-4 && cosA < 0) {
      _armQ.setFromAxisAngle(_armX, Math.PI);
      paddleMesh.quaternion.premultiply(_armQ);
    }
    // clampPaddlePose NO disponible aquí: ver distancia mano-pala directamente
    if (f % 30 === 0) {
      const W = bp.mano.getWorldPosition(new THREE.Vector3());
      const S = bp.bra.getWorldPosition(new THREE.Vector3());
      const E = bp.ant.getWorldPosition(new THREE.Vector3());
      console.log(`f${f} · hombro(${S.x.toFixed(2)},${S.y.toFixed(2)},${S.z.toFixed(2)}) · codo(${E.x.toFixed(2)},${E.y.toFixed(2)},${E.z.toFixed(2)}) · mano(${W.x.toFixed(2)},${W.y.toFixed(2)},${W.z.toFixed(2)}) · pala(${paddleMesh.position.x.toFixed(2)},${paddleMesh.position.y.toFixed(2)},${paddleMesh.position.z.toFixed(2)}) · mano↔pala ${W.distanceTo(paddleMesh.position).toFixed(3)} m`);
    }
  }
  console.log('DRIVER OK — sin excepciones');
} catch (e) {
  err = e;
  console.log('DRIVER LANZÓ:', e.message, '\n', (e.stack || '').split('\n').slice(0, 4).join('\n'));
}
// resultado final del material (lo que vería el usuario)
const meshInfo = [];
gltf.scene.traverse((o) => {
  if (o.isMesh) meshInfo.push({ mesh: o.name, tipoMat: o.material.type,
    map: !!o.material.map, color: '#' + o.material.color.getHexString(),
    metal: o.material.metalness, rough: o.material.roughness,
    skin: !!o.isSkinnedMesh });
});
console.log('MATERIAL FINAL:', JSON.stringify(meshInfo));

// r99 · MEDICIÓN COMPLETA DEL RIG vr_arm.glb (ingeniería de rigging —
// base factual del plan plan_brazos_r99.md). NO toca src/game/.
//
//   1a. Cada hueso con su matriz de mundo de BIND (escena sin animar).
//   1b. Ambas manos: dirección MUNDO de cada dedo, eje de palma (pulgar →
//       lado medio-anular) y NORMAL PALMAR = −Z local de la mano (medición
//       independiente; across×along sólo se cruza como control).
//   1c. EJE DE FLEXIÓN de cada falange (raíz incluida) en marco padre y
//       marco propio, con signo; VERIFICACIÓN: flexión +0.5 rad mueve la
//       PUNTA (cacheada en marco propio del distal) hacia la palma (dot>0).
//   1d. Agarre: quat de MUÑECA (mano rel. antebrazo, relativa al bind) con
//       hoja ⟂ antebrazo, cara al rival y pulgar hacia la punta; offset del
//       hueso mano respecto al mango (D_GRIP = 0.1303).
//   2.  POSE_A/B/C: calibración por búsqueda en rejilla contra objetivos
//       derivados de las referencias del dueño + simulación del driver r95
//       actual para comparar. Todo a scripts/plan_medidas_rig_r99.json.
import * as THREE from 'three';
globalThis.self = globalThis;   // GLTFLoader → loadImageSource usa self.URL
const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
import { readFileSync, writeFileSync } from 'node:fs';

const RUTA = '/home/z/my-project/public/vr_arm.glb';
const SALIDA = '/home/z/my-project/scripts/plan_medidas_rig_r99.json';
const D_GRIP = 0.1303;                          // mango → centro de hoja (r54)
const V3 = THREE.Vector3, Q4 = THREE.Quaternion;
const f4 = (x) => +(+x).toFixed(4);
const fV = (v) => v.toArray().map(f4);
const fQ = (q) => [f4(q.x), f4(q.y), f4(q.z), f4(q.w)];
const fE = (q, ord = 'XYZ') => {
  const e = new THREE.Euler().setFromQuaternion(q, ord);
  return [f4(e.x), f4(e.y), f4(e.z)];
};
const ejeAngulo = (q) => {
  const ang = 2 * Math.acos(THREE.MathUtils.clamp(Math.abs(q.w), -1, 1));
  const s = Math.sqrt(Math.max(1 - q.w * q.w, 1e-12));
  const sg = q.w < 0 ? -1 : 1;
  return { eje: fV(new V3(sg * q.x / s, sg * q.y / s, sg * q.z / s)), ang: f4(ang) };
};
const JSON_ = { fecha: 'r99', glb: RUTA };

/* — carga: three primero, parser GLB mínimo de respaldo (solo nodos) — */
let escena = null, via = 'three';
try {
  const buf = readFileSync(RUTA);
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  const gltf = await new Promise((res, rej) =>
    new GLTFLoader().parse(ab, '', res, rej));
  escena = gltf.scene;
} catch (e3) {
  via = 'parser-minimo';
  console.warn('GLTFLoader falló (' + e3.message + ') → parser mínimo de nodos');
  const raw = readFileSync(RUTA);
  const dv = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
  if (dv.getUint32(0, true) !== 0x46546c67) throw new Error('GLB inválido');
  const jsonLen = dv.getUint32(12, true);
  const json = JSON.parse(new TextDecoder().decode(
    new Uint8Array(raw.buffer, raw.byteOffset + 20, jsonLen)));
  const montar = (idx, padre) => {
    const n = json.nodes[idx];
    const o = new THREE.Object3D();
    o.name = n.name || ('nodo' + idx);
    if (n.translation) o.position.fromArray(n.translation);
    if (n.rotation) o.quaternion.fromArray(n.rotation);
    if (n.scale) o.scale.fromArray(n.scale);
    if (padre) padre.add(o); else escena = o;
    (n.children || []).forEach((h) => montar(h, o));
    return o;
  };
  (json.scenes[json.scene || 0].nodes).forEach((r) => montar(r, null));
}
escena.updateMatrixWorld(true);
const nom = (b) => escena.getObjectByName(b);
console.log(`# r99 · CARGA OK via=${via}`);

/* — 1a · inventario de huesos: matriz de mundo de BIND — */
const huesos = [];
escena.traverse((o) => {
  if (o.isBone || (o.name && o.children.length && !o.isMesh)) huesos.push(o);
});
console.log(`\n== 1a · ${huesos.length} nodos con nombre (${huesos.filter(h => h.isBone).length} isBone) ==`);
JSON_.huesos = huesos.map((h) => ({
  nombre: h.name, esHueso: !!h.isBone, padre: h.parent ? h.parent.name : null,
  hijos: h.children.length,
  posMundo: fV(h.getWorldPosition(new V3())),
  quatMundo: fQ(h.getWorldQuaternion(new Q4())),
  matrizMundo: h.matrixWorld.elements.map(f4),
}));
for (const h of huesos) {
  const p = h.getWorldPosition(new V3()), q = h.getWorldQuaternion(new Q4());
  console.log(`  ${h.isBone ? 'H' : 'g'} ${h.name.padEnd(26)} padre=${(h.parent?.name || '—').padEnd(22)} pos=[${fV(p)}] q=[${fQ(q)}]`);
}

/* — escala adulta (igual que _cargarArmasGLB): brazo superior = 0.27 m — */
const U_A = nom('U_arm_021'), L_A = nom('L_arm_022'), MANO_A = nom('hand_023');
const L1u = L_A.position.length();
const L2u = MANO_A.position.length();
const esc = 0.27 / L1u;
console.log(`\n== escala ==  L1u=${f4(L1u)}cm L2u=${f4(L2u)}cm esc=${f4(esc)} → L1=${f4(0.27)}m L2=${f4(L2u * esc)}m`);
JSON_.escala = { L1u_cm: f4(L1u), L2u_cm: f4(L2u), esc: f4(esc), L1_m: 0.27, L2_m: f4(L2u * esc) };

/* — dedos: RAÍZ + falanges (3 huesos por dedo) + cache de PUNTAS en bind — */
const PREFIJOS = ['thumb', 'mid', 'index', 'ring', 'pinky'];
const prefijoDe = (n) => { const m = /^(thumb|mid|index|ring|pinky)/.exec(n || ''); return m ? m[1] : null; };
const dedosDe = (mano) => {
  const mapa = new Map();
  mano.traverse((o) => {
    const p = prefijoDe(o.name);
    if (p) { if (!mapa.has(p)) mapa.set(p, []); mapa.get(p).push(o); }
  });
  const dedos = [];
  for (const p of PREFIJOS) {
    const nodos = (mapa.get(p) || []).sort((a, b) => a.name.localeCompare(b.name));
    if (!nodos.length) continue;
    const raiz = nodos.find((n) => prefijoDe(n.parent?.name) !== p) || nodos[0];
    const fal = [raiz]; let ant = raiz;
    while (ant.children.length) { const s = ant.children[0]; fal.push(s); ant = s; }
    dedos.push({ nombre: p, raiz, falanges: fal });
  }
  return dedos;
};
// cache de punta: dirección del último tramo en el MARCO PROPIO del distal,
// capturada EN BIND (así la punta responde a rotar la propia falange)
const tipCache = new Map();
const cachearPuntas = (dedosInfo) => {
  for (const dd of dedosInfo) {
    const fs = dd.falanges, d = fs[fs.length - 1];
    const ant = fs[fs.length - 2] || d.parent;
    const seg = d.getWorldPosition(new V3()).sub(ant.getWorldPosition(new V3()));
    tipCache.set(d.name, {
      lon: seg.length(),
      dLocal: seg.clone().normalize()
        .applyQuaternion(d.getWorldQuaternion(new Q4()).clone().invert()),
    });
  }
};
const posDe = (o) => o.getWorldPosition(new V3());
const puntaDe = (falanges) => {
  const d = falanges[falanges.length - 1];
  const c = tipCache.get(d.name);
  if (!c) cachearPuntas([{ falanges }]);
  const cc = tipCache.get(d.name);
  return posDe(d).add(cc.dLocal.clone().applyQuaternion(d.getWorldQuaternion(new Q4())).multiplyScalar(cc.lon));
};

/* — análisis de un brazo — */
const _m = new THREE.Matrix4();
const analizarBrazo = (etq, U, L, MANO) => {
  const lado = etq[0];
  console.log(`\n================ BRAZO ${etq} · mano=${MANO.name} ================`);
  const out = { lado, mano: MANO.name };
  const qU = L.getWorldQuaternion(new Q4());
  const qM = MANO.getWorldQuaternion(new Q4());
  const relBind = qU.clone().invert().multiply(qM);
  console.log(`  mano rel. ANTEBRAZO (bind): quat=[${fQ(relBind)}] eulerXYZ=${JSON.stringify(fE(relBind))}`);
  out.relBind = { quat: fQ(relBind), eulerXYZ: fE(relBind) };
  const ejesM = ['X', 'Y', 'Z'].map((_, i) =>
    new V3(i === 0 ? 1 : 0, i === 1 ? 1 : 0, i === 2 ? 1 : 0).applyQuaternion(qM));
  console.log(`  ejes mano en mundo: X=[${fV(ejesM[0])}] Y=[${fV(ejesM[1])}] Z=[${fV(ejesM[2])}]`);
  out.ejesManoMundo = { X: fV(ejesM[0]), Y: fV(ejesM[1]), Z: fV(ejesM[2]) };
  const W = posDe(MANO), E = posDe(L);
  const eU = new V3().subVectors(W, E).normalize();
  const eU_local = eU.clone().applyQuaternion(qU.clone().invert());
  console.log(`  antebrazo: dirMundo=[${fV(eU)}] dirMarcoPropio=[${fV(eU_local)}]`);
  out.antebrazo = { dirMundo: fV(eU), dirMarcoPropio: fV(eU_local) };

  const dedos = dedosDe(MANO);
  cachearPuntas(dedos);
  const base = {};
  for (const dd of dedos) base[dd.nombre] = posDe(dd.raiz);
  const T = base.thumb, M = base.mid, R = base.ring, P = base.pinky;
  const across = new V3().subVectors(new V3().addVectors(R, P).multiplyScalar(0.5), T).normalize();
  const along = new V3().subVectors(M, W).normalize();
  const nCand = new V3().crossVectors(across, along).normalize();
  const nPalm = ejesM[2].clone().negate();            // palma = −Z mano (independiente)
  console.log(`  PALMA: across(pulgar→meñique)=[${fV(across)}] along(muñeca→medio)=[${fV(along)}]`);
  console.log(`  normal palmar (−Z mano)=[${fV(nPalm)}] · across×along=[${fV(nCand)}] · dot=${f4(nPalm.dot(nCand))}`);
  out.palma = { across: fV(across), along: fV(along), normal: fV(nPalm), cand: fV(nCand), dotNormalCand: f4(nPalm.dot(nCand)) };

  // — 1c · eje de flexión por falange (RAÍZ incluida), verificación no circular
  const filas = [];
  for (const dd of dedos) {
    const fs = dd.falanges;
    const tipReposo = puntaDe(fs);
    for (let iF = 0; iF < fs.length; iF++) {
      const hueso = fs[iF];
      const qPadre = hueso.parent.getWorldQuaternion(new Q4());
      const hijo = fs[iF + 1] || null;
      const dW = hijo
        ? new V3().subVectors(posDe(hijo), posDe(hueso)).normalize()
        : new V3().subVectors(posDe(hueso), posDe(hueso.parent)).normalize();
      const dP = dW.clone().applyQuaternion(qPadre.clone().invert());
      const nP = nPalm.clone().applyQuaternion(qPadre.clone().invert());
      const ejeP = new V3().crossVectors(dP, nP);
      const degen = ejeP.length() < 1e-6;
      if (!degen) ejeP.normalize();
      const bindQ = hueso.quaternion.clone();
      const ejeHueso = degen ? null : ejeP.clone().applyQuaternion(bindQ.clone().invert());
      let dotVer = null, mov = null;
      if (!degen) {
        hueso.quaternion.copy(new Q4().setFromAxisAngle(ejeP, 0.5)).multiply(bindQ);
        escena.updateMatrixWorld(true);
        const movV = puntaDe(fs).sub(tipReposo);
        mov = f4(movV.length());
        dotVer = f4(movV.dot(nPalm));
        hueso.quaternion.copy(bindQ);
        escena.updateMatrixWorld(true);
      }
      const dotDriver = degen ? null : f4(nP.dot(new V3(0, 1, 0).cross(dP)));
      const angVsDriver = degen ? null : f4(ejeP.angleTo(new V3(0, 1, 0)));
      filas.push({ dedo: dd.nombre, falange: iF, hueso: hueso.name, padre: hueso.parent.name,
        d_padre: fV(dP), eje_padre: degen ? null : fV(ejeP), eje_hueso: ejeHueso ? fV(ejeHueso) : null,
        verif_dot05: dotVer, verif_mov: mov, driver_ejeY_dot: dotDriver, ang_vs_driverY: angVsDriver,
        bind_euler: fE(bindQ), bind_ang: f4(bindQ.angleTo(new Q4())) });
    }
  }
  console.log(`  eje flexión por falange (marco padre · rotación + acerca la punta a la palma):`);
  for (const r of filas)
    console.log(`    ${r.dedo.padEnd(6)} f${r.falange} ${r.hueso.padEnd(16)} ejePadre=[${r.eje_padre}] verifDot(+0.5)=${r.verif_dot05} mov=${r.verif_mov} · driverY dot=${r.driver_ejeY_dot} ang=${r.ang_vs_driverY} · bind ang=${r.bind_ang}`);
  out.normalPalmar = fV(nPalm);
  out.deduccion = filas;

  out.longitudes = dedos.map((dd) => {
    const ps = dd.falanges.map(posDe);
    let lon = 0;
    for (let i = 0; i + 1 < ps.length; i++) lon += ps[i].distanceTo(ps[i + 1]);
    if (ps.length >= 2) lon += ps[ps.length - 2].distanceTo(ps[ps.length - 1]);
    return { dedo: dd.nombre, huesos: dd.falanges.length, lon_cm: f4(lon), lon_m: f4(lon * esc) };
  });
  for (const lo of out.longitudes)
    console.log(`  largo ${lo.dedo}: ${lo.huesos} huesos · ${lo.lon_cm}cm GLB · ${lo.lon_m}m adulto`);

  // — 1d · agarre (hoja ⟂ antebrazo, cara=±X mano, pulgar→punta) —
  const pulgarY = (lado === 'A') ? -1 : 1;
  const bF = T.clone().sub(W).applyQuaternion(qU.clone().invert());
  bF.addScaledVector(eU_local, -bF.dot(eU_local));
  if (bF.lengthSq() < 1e-8) bF.set(0, 0, 1);
  bF.normalize();
  const Xd = eU_local.clone();
  const Yd = bF.clone().multiplyScalar(pulgarY);
  const Zd = new V3().crossVectors(Xd, Yd).normalize();
  const Yd2 = new V3().crossVectors(Zd, Xd).normalize();
  _m.makeBasis(Xd, Yd2, Zd);
  const relDesQ = new Q4().setFromRotationMatrix(_m);
  const deltaQ = relDesQ.clone().multiply(relBind.clone().invert());
  const ea = ejeAngulo(deltaQ);
  console.log(`  AGARRE (pulgarY=${pulgarY}): marco antebrazo X_des=[${fV(Xd)}] b(pulgar⟂)=[${fV(bF)}] Y_des=[${fV(Yd2)}] Z_des=[${fV(Zd)}] palma=−Z`);
  console.log(`    relDes(eulerXYZ)=${JSON.stringify(fE(relDesQ))} · DELTA MUÑECA rel. bind: quat=[${fQ(deltaQ)}] eje=${JSON.stringify(ea.eje)} ángulo=${ea.ang} rad · eulerXYZ=${JSON.stringify(fE(deltaQ))}`);
  out.agarre = { pulgarY, b_marcoAnte: fV(bF), X_des: fV(Xd), Y_des: fV(Yd2), Z_des: fV(Zd),
    relDes: { quat: fQ(relDesQ), eulerXYZ: fE(relDesQ) },
    deltaMuneca: { quat: fQ(deltaQ), eje: ea.eje, ang_rad: ea.ang, eulerXYZ: fE(deltaQ) } };
  // offset del hueso mano respecto al mango: centro de PALMA (con pulgar) y
  // CENTRO DE CREASE (nudillos de los 4 dedos, sin pulgar — la línea real
  // donde el mango cruza la mano en un agarre shakehand)
  const centroPalma = new V3().addVectors(base.index, M).add(R).add(P).add(T).multiplyScalar(0.2);
  const offLocal = centroPalma.clone().sub(W).applyQuaternion(qM.clone().invert());
  const offM = offLocal.clone().multiplyScalar(esc);
  const centroCrease = new V3().addVectors(base.index, M).add(R).add(P).multiplyScalar(0.25);
  const offCrease = centroCrease.clone().sub(W).applyQuaternion(qM.clone().invert());
  console.log(`    centroPalma − muñeca (marco mano): [${fV(offLocal)}]cm GLB · [${fV(offM)}]m adulto`);
  console.log(`    centroCrease (4 nudillos, sin pulgar) − muñeca: [${fV(offCrease)}]cm GLB · [${fV(offCrease.clone().multiplyScalar(esc))}]m adulto`);
  out.offsetMano = { local_cm: fV(offLocal), adulto_m: fV(offM), D_GRIP,
    crease_local_cm: fV(offCrease), crease_adulto_m: fV(offCrease.clone().multiplyScalar(esc)) };
  // tips de bind en marco mano (referencia de manos abiertas)
  const tipsBind = {};
  for (const dd of dedos)
    tipsBind[dd.nombre] = fV(puntaDe(dd.falanges).sub(W).applyQuaternion(qM.clone().invert()));
  console.log(`    tips BIND (marco mano cm)=${JSON.stringify(tipsBind)}`);
  out.tipsBind_mano_cm = tipsBind;
  return { out, W, E, qU, qM, eU_local, relBind, relDesQ, deltaQ, dedos, pulgarY, base, ejesM, nPalm,
    offLocal, offCrease, qMinv: qM.clone().invert() };
};

const braA = analizarBrazo('A (hand_023)', U_A, L_A, MANO_A);
const U_B = nom('U_arm(mirrored)_02'), L_B = nom('L_arm(mirrored)_03'), MANO_B = nom('hand(mirrored)_04');
const braB = analizarBrazo('B (espejado)', U_B, L_B, MANO_B);

const xA = U_A.getWorldPosition(new V3()).x, xB = U_B.getWorldPosition(new V3()).x;
const brazoPalaCPU = xA < 0 ? 'A' : 'B';
console.log(`\n== lado ==  U_arm_021 x=${f4(xA)} · U_arm(mirrored) x=${f4(xB)} → CPU (s=−1) agarra con el brazo de x<0: ${brazoPalaCPU}`);
JSON_.ladoCPU = { xA: f4(xA), xB: f4(xB), brazoPalaCPU, nota:
  'bind: modelo mirando a +z (manos 10 cm al frente del pecho); hand_023 (+x) = mano IZQUIERDA del personaje, hand(mirrored)_04 (−x) = mano DERECHA. pulgarY driver (A=−1, B=+1) confirmado por la medición.' };

/* — hombros: offsets bind respecto a Body_01 — */
const BODY = nom('Body_01');
const pBody = posDe(BODY);
const offHombros = [['A', U_A], ['B', U_B]].map(([k, U]) => {
  const o = U.getWorldPosition(new V3()).sub(pBody);
  return { brazo: k, offset_cm: fV(o), offset_m: fV(o.clone().multiplyScalar(esc)) };
});
console.log(`  Body_01 pos=[${fV(pBody)}] eulerYXZ=${JSON.stringify(fE(BODY.getWorldQuaternion(new Q4()), 'YXZ'))}`);
for (const oh of offHombros)
  console.log(`  hombro ${oh.brazo} − Body_01: [${oh.offset_m}] m adulto`);
JSON_.hombros = { body_pos_cm: fV(pBody), offsets: offHombros };
JSON_.brazos = { A: braA.out, B: braB.out };   // r99 · medición completa por brazo

/* — utilidades de poses — */
const bindQDe = (h) => h.userData.bindQ99 || (h.userData.bindQ99 = h.quaternion.clone());
const ejesMedidos = (bra) => {
  const m = {};
  for (const r of bra.out.deduccion)
    (m[r.dedo] = m[r.dedo] || [])[r.falange] = new V3().fromArray(r.eje_padre);
  return m;
};
const aplicarCurl = (dedosInfo, angulos, ejes) => {
  for (const dd of dedosInfo) {
    const ang = angulos[dd.nombre]; if (!ang) continue;
    dd.falanges.forEach((h, i) => {
      if (ang[i] == null) return;
      const eje = (ejes && ejes[dd.nombre] && ejes[dd.nombre][i]) || new V3(0, 1, 0);
      const bq = bindQDe(h);   // r99 · leer el cache ANTES del copy: copy() corre
      // primero y sin esto el cache capturaría la flexión (q⊗q = rotación doble)
      h.quaternion.copy(new Q4().setFromAxisAngle(eje, ang[i])).multiply(bq);
    });
  }
};
const tipsManoLocal = (bra, dedosInfo) => {
  const t = {};
  for (const dd of dedosInfo)
    t[dd.nombre] = puntaDe(dd.falanges).sub(bra.W).applyQuaternion(bra.qMinv);
  return t;
};
const capturar = (dedosInfo) => {
  const g = {};
  for (const dd of dedosInfo) for (const h of dd.falanges) g[h.name] = h.quaternion.clone();
  return g;
};
const restaurar = (dedosInfo, g) => {
  for (const dd of dedosInfo) for (const h of dd.falanges) h.quaternion.copy(g[h.name]);
  escena.updateMatrixWorld(true);
};
// línea del mango en marco mano: por el CENTRO DE CREASE (x nudillos, sin
// pulgar) ∥ Y — los dedos nacen SOBRE esa línea y envuelven naturalmente
const distALineaMango = (bra, tipLocal) => {
  const dx = tipLocal.x - bra.offCrease.x, dz = tipLocal.z - bra.offCrease.z;
  return Math.hypot(dx, dz);
};

/* — 2a · POSE_A «agarre shakehand» — calibración por rejilla POR BRAZO — */
console.log(`\n== 2a · POSE_A: calibración (objetivos derivados de las referencias) ==`);
const RADIO_MANGO_CM = 0.8;    // tip−línea ≈ radio mango 1.25 + yema 0.55 cm adulto (HIPÓTESIS r mango; aguja de render: contacto dedo-mango)
const REJ_WRAP = [[0.5, 0.7, 0.9, 1.1, 1.3, 1.45], [0.9, 1.2, 1.5, 1.8, 2.0], [0.4, 0.7, 1.0, 1.3, 1.5]];
const REJ_IDX = [[1.2, 1.4, 1.6], [0.1, 0.25, 0.4], [0.1, 0.25, 0.4]];
const REJ_TH = [[0, 0.1, 0.2], [0, 0.15, 0.3, 0.45], [0, 0.1, 0.2, 0.3]];
// objetivos en MARCO MANO (cm GLB); y según el lado del pulgar del brazo
const objetivosDe = (bra) => ({
  index: { punto: new V3(bra.offCrease.x + 0.70, 0.90 * bra.pulgarY, -3.30) }, // borde inferior hoja, cara +X (lado dedos)
  thumb: { distMango: 1.2, pulgarY: bra.pulgarY },             // cara trasera (−X, lado pulgar), junto a la hoja
});
const escanear = (bra, dedo, ejes, rejilla, objetivo) => {
  const dd = bra.dedos.find((d) => d.nombre === dedo);
  const g = capturar([dd]);
  let mejor = null;
  const errDe = (tip, ang, distPip) => {
    if (objetivo.punto) return tip.distanceTo(objetivo.punto);
    // envolver: la yema queda a ≈0.8 cm de la línea del mango (que cruza la
    // crease de los nudillos); el pulgar además cabalga hacia la hoja
    if (dedo === 'thumb') {
      const yl = tip.y * objetivo.pulgarY;
      return Math.abs(distPip.tip - objetivo.distMango)
        + 0.3 * Math.max(0, -0.3 - yl) + 0.3 * Math.max(0, yl - 3.4);
    }
    return Math.abs(distPip.tip - 0.8);
  };
  for (const a of rejilla[0]) for (const b of rejilla[1]) for (const c of rejilla[2]) {
    aplicarCurl([dd], { [dedo]: [a, b, c] }, ejes);
    escena.updateMatrixWorld(true);
    const tip = puntaDe(dd.falanges).sub(bra.W).applyQuaternion(bra.qMinv);
    const pipL = posDe(dd.falanges[1]).sub(bra.W).applyQuaternion(bra.qMinv);
    const distPip = { tip: distALineaMango(bra, tip), pip: distALineaMango(bra, pipL) };
    const err = errDe(tip, [a, b, c], distPip);
    if (!mejor || err < mejor.err) mejor = { ang: [a, b, c], err: f4(err),
      tip: fV(tip), distMango: f4(distPip.tip), distPip: f4(distPip.pip) };
  }
  restaurar([dd], g);
  return mejor;
};
const POSE_A = {};            // { A: {...}, B: {...} } — el runtime elige por brazo.lado
JSON_.poses = JSON_.poses || {};
JSON_.poses.POSE_A_calibracion = { radioMango_cm: RADIO_MANGO_CM, scan: {} };
for (const bra of [braA, braB]) {
  const ejes = ejesMedidos(bra);
  const obj = objetivosDe(bra);
  const scan = {};
  for (const dedo of ['mid', 'ring', 'pinky']) {
    scan[dedo] = escanear(bra, dedo, ejes, REJ_WRAP, { distMango: RADIO_MANGO_CM, pulgarY: bra.pulgarY });
    console.log(`  wrap ${bra.out.lado} ${dedo}: mejor=${JSON.stringify(scan[dedo].ang)} err=${scan[dedo].err} · tip=${JSON.stringify(scan[dedo].tip)} · distMango=${scan[dedo].distMango}cm`);
  }
  scan.index = escanear(bra, 'index', ejes, REJ_IDX, obj.index);
  console.log(`  index ${bra.out.lado}: mejor=${JSON.stringify(scan.index.ang)} err=${scan.index.err} · tip=${JSON.stringify(scan.index.tip)} · distMango=${scan.index.distMango}cm`);
  scan.thumb = escanear(bra, 'thumb', ejes, REJ_TH, obj.thumb);
  console.log(`  thumb ${bra.out.lado}: mejor=${JSON.stringify(scan.thumb.ang)} err=${scan.thumb.err} · tip=${JSON.stringify(scan.thumb.tip)} · distMango=${scan.thumb.distMango}cm`);
  // control: mismo escaneo con el eje del DRIVER (+Y) — cuantifica el error del eje
  const ctrlMid = escanear(bra, 'mid', null, REJ_WRAP, { distMango: RADIO_MANGO_CM, pulgarY: bra.pulgarY });
  const ctrlTh = escanear(bra, 'thumb', null, REJ_TH, obj.thumb);
  console.log(`  [control eje +Y] ${bra.out.lado}: mid err=${ctrlMid.err} (medido ${scan.mid.err}) · thumb err=${ctrlTh.err} (medido ${scan.thumb.err})`);
  POSE_A[bra.out.lado] = { thumb: scan.thumb.ang, index: scan.index.ang,
    mid: scan.mid.ang, ring: scan.ring.ang, pinky: scan.pinky.ang };
  JSON_.poses.POSE_A_calibracion.scan[bra.out.lado] = {
    scan, controlEjeDriver: { mid: ctrlMid, thumb: ctrlTh } };
}
JSON_.poses.POSE_A = { angulos_por_brazo_y_falange_raiz_primero: POSE_A,
  nota: 'orden falanges [MCP raíz, PIP, DIP] · ejes medidos por hueso (deduccion) · el driver elige por brazo.lado' };
console.log(`\n== POSE_A FINAL == A=${JSON.stringify(POSE_A.A)} B=${JSON.stringify(POSE_A.B)}`);
for (const bra of [braA, braB]) {
  const g = capturar(bra.dedos);
  aplicarCurl(bra.dedos, POSE_A[bra.out.lado], ejesMedidos(bra));
  escena.updateMatrixWorld(true);
  const tips = tipsManoLocal(bra, bra.dedos);
  const res = {};
  for (const [k, t] of Object.entries(tips))
    res[k] = { tip_mano_cm: fV(t), distMango_cm: f4(distALineaMango(bra, t)) };
  console.log(`  verif brazo ${bra.out.lado}: ${JSON.stringify(res)}`);
  JSON_.poses['POSE_A_verif_' + bra.out.lado] = res;
  restaurar(bra.dedos, g);
}
// — simulación del DRIVER r95 ACTUAL (f1/f2 con +Y; raíz sin tocar; meñique 0) —
{
  const g = capturar(braA.dedos);
  const driverAng = { thumb: [null, 0.32, 0.54], index: [null, 0.62, 1.34],
    mid: [null, 0.62, 1.34], ring: [null, 0.62, 1.34], pinky: [0, 0, 0] };
  aplicarCurl(braA.dedos, driverAng, null);
  escena.updateMatrixWorld(true);
  const tips = tipsManoLocal(braA, braA.dedos);
  const res = {};
  for (const [k, t] of Object.entries(tips))
    res[k] = { tip_mano_cm: fV(t), distMango_cm: f4(distALineaMango(braA, t)) };
  console.log(`  DRIVER r95 actual (mano A): ${JSON.stringify(res)}`);
  console.log(`    nota: meñique queda EN BIND (el bucle children[0] de _cargarArmasGLB nunca llega a pinky__031)`);
  JSON_.poses.driver_r95_sim = res;
  restaurar(braA.dedos, g);
}
// — stance sintético del brazo de la pala: antebrazo (0,−0.30,0.95), rival +z —
// la quat de mano en stance se COMPONE (qStance ⊗ relDes): el brazo sigue en bind
JSON_.poses.POSE_A_stance = {};
for (const [etq, bra] of [['A', braA], ['B', braB]]) {
  const dLt = new V3(0, -0.30, 0.95).normalize();
  const eUw = new V3().fromArray(bra.out.antebrazo.dirMundo);
  const qStance = new Q4().setFromUnitVectors(eUw, dLt).multiply(bra.qU);
  const qMw = qStance.clone().multiply(bra.relDesQ);       // mano mundo en stance
  const cara = new V3(1, 0, 0).applyQuaternion(qMw);       // cara +X mano (lado dedos/índice)
  const ejeHoja = new V3(0, 1, 0).applyQuaternion(qMw).multiplyScalar(bra.pulgarY);
  const palma = new V3(0, 0, -1).applyQuaternion(qMw);
  console.log(`  stance ${etq}: cara(+X mano)=[${fV(cara)}] ejeHoja=[${fV(ejeHoja)}] palma=[${fV(palma)}]`);
  console.log(`    ángulo cara↔rival(+z)=${f4(cara.angleTo(new V3(0, 0, 1)))} rad · ejeHoja↔+y=${f4(ejeHoja.angleTo(new V3(0, 1, 0)))} rad`);
  JSON_.poses.POSE_A_stance[etq] = { cara: fV(cara), ejeHoja: fV(ejeHoja), palma: fV(palma),
    ang_cara_rival_rad: f4(cara.angleTo(new V3(0, 0, 1))),
    ang_ejeHoja_up_rad: f4(ejeHoja.angleTo(new V3(0, 1, 0))) };
}

/* — 2b · POSE_B «palma de saque» (mano libre) — antebrazo horizontal al centro — */
console.log(`\n== 2b · POSE_B palma arriba (stance: antebrazo (−0.15,−0.05,0.99), codo 90-110°) ==`);
const dLtB = new V3(-0.15, -0.05, 0.99).normalize();
const munecaPalmArriba = (bra, dLt) => {
  const eUw = new V3().fromArray(bra.out.antebrazo.dirMundo);
  const qStance = new Q4().setFromUnitVectors(eUw, dLt).multiply(bra.qU);
  const nUpF = new V3(0, 1, 0).applyQuaternion(qStance.clone().invert()); // "arriba" marco antebrazo
  const Xh = bra.eU_local.clone();
  const Zh = nUpF.clone().negate();                    // palma=−Z ⇒ Z=−arriba (ortogonalizado)
  Zh.addScaledVector(Xh, -Zh.dot(Xh)).normalize();
  const Yh = new V3().crossVectors(Zh, Xh).normalize();
  _m.makeBasis(Xh, Yh, Zh);
  const relDes = new Q4().setFromRotationMatrix(_m);
  return { relDes, delta: relDes.clone().multiply(bra.relBind.clone().invert()), qStance };
};
// cuenco: altura de cada tip sobre el PLANO DE PALMA (z_local del centro de
// palma), en MARCO MANO de bind — exacto sin quats: el curl vive en el marco
// mano y el stance de palma-arriba sólo reorienta la mano entera
const bowlStance = (bra, dedosInfo) => {
  const out = {};
  for (const dd of dedosInfo) {
    const tip = puntaDe(dd.falanges).sub(bra.W).applyQuaternion(bra.qMinv);
    out[dd.nombre] = f4((bra.offLocal.z - tip.z) * esc);
  }
  return { palmaDir: fV(new V3(0, 0, -1).applyQuaternion(bra.qM)), bowl_m: out };
};
// cuenco por dedo: escaneo por dedo con objetivo de altura sobre el plano de
// palma (bola r=2 cm descansa en la palma: dedos en copa suave ≈ 1.2 cm,
// pulgar relajado al lado ≈ 1.8 cm — ref. 3 del dueño)
const REJ_B = [[0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4], [0, 0.08, 0.14, 0.22, 0.3, 0.4],
  [0, 0.1, 0.16, 0.24, 0.34, 0.5]];   // 0 permitido: una falange puede quedar en bind
const OBJ_BOWL_M = 0.012, OBJ_BOWL_THUMB = 0.018;
const braLibre = braA;                     // mano libre de la CPU (personaje: izquierda)
let POSE_B;
{
  const { relDes, delta } = munecaPalmArriba(braLibre, dLtB);
  const ea = ejeAngulo(delta);
  console.log(`  DELTA MUÑECA palma-arriba (marco antebrazo, rel. bind): quat=[${fQ(delta)}] eje=${JSON.stringify(ea.eje)} ángulo=${ea.ang} rad · eulerXYZ=${JSON.stringify(fE(delta))}`);
  JSON_.poses.POSE_B_muneca = { quat: fQ(delta), eje: ea.eje, ang_rad: ea.ang, eulerXYZ: fE(delta),
    stance_antebrazo: fV(dLtB), formula: 'X=antebrazo · palma=+Y mundo (Z=−arriba ort.) · Y=Z×X' };
  const qStB = new Q4().setFromUnitVectors(
    new V3().fromArray(braLibre.out.antebrazo.dirMundo), dLtB).multiply(braLibre.qU);
  const g = capturar(braLibre.dedos);
  POSE_B = {};
  const scanB = {};
  for (const dd of braLibre.dedos) {
    const obj = dd.nombre === 'thumb' ? OBJ_BOWL_THUMB : OBJ_BOWL_M;
    let mejor = null;
    for (const a of REJ_B[0]) for (const b of REJ_B[1]) for (const c of REJ_B[2]) {
      restaurar(braLibre.dedos, g);
      aplicarCurl([dd], { [dd.nombre]: [a, b, c] }, ejesMedidos(braLibre));
      escena.updateMatrixWorld(true);
      const bowl = bowlStance(braLibre, [dd]).bowl_m[dd.nombre];
      const err = Math.abs(bowl - obj);
      if (!mejor || err < mejor.err) mejor = { ang: [a, b, c], err: f4(err), bowl };
    }
    POSE_B[dd.nombre] = mejor.ang;
    scanB[dd.nombre] = mejor;
    console.log(`  ${dd.nombre.padEnd(6)} → ${JSON.stringify(mejor.ang)} · bowl=${f4(mejor.bowl)}m (objetivo ${obj}m)`);
  }
  restaurar(braLibre.dedos, g);
  // verificación COMBINADA de los 5 ganadores
  aplicarCurl(braLibre.dedos, POSE_B, ejesMedidos(braLibre));
  escena.updateMatrixWorld(true);
  const comb = bowlStance(braLibre, braLibre.dedos);
  console.log(`  POSE_B combinada → palmaDir=[${comb.palmaDir}] bowl(m)=${JSON.stringify(comb.bowl_m)}`);
  JSON_.poses.POSE_B = { angulos_falange_raiz_primero: POSE_B, bowl_m: comb.bowl_m,
    palmaDir_stance: comb.palmaDir, objetivos_m: { dedos: OBJ_BOWL_M, thumb: OBJ_BOWL_THUMB }, scanB };
}

/* — 2c · POSE_C «balance rally» (mano libre, muñeca neutra=bind) — */
console.log(`\n== 2c · POSE_C semicurva, muñeca NEUTRA (bind) ==`);
const POSE_C = { thumb: [0.18, 0.12, 0.08], index: [0.35, 0.55, 0.65],
  mid: [0.35, 0.55, 0.65], ring: [0.36, 0.57, 0.67], pinky: [0.38, 0.59, 0.69] };
{
  const g = capturar(braLibre.dedos);
  aplicarCurl(braLibre.dedos, POSE_C, ejesMedidos(braLibre));
  escena.updateMatrixWorld(true);
  const tips = tipsManoLocal(braLibre, braLibre.dedos);
  const res = {};
  for (const [k, t] of Object.entries(tips)) res[k] = fV(t);
  console.log(`  tips(mano local cm)=${JSON.stringify(res)}`);
  JSON_.poses.POSE_C = { angulos_falange_raiz_primero: POSE_C, tips_mano_cm: res,
    muneca: 'neutral = relBind intacta (el driver ya la compone al continuar el antebrazo)' };
  restaurar(braLibre.dedos, g);
}
JSON_.poses.POSE_REST = 'bind sin cambios (todos los ángulos 0) — fuera de juego';

/* — guardar JSON — */
const serializado = JSON.stringify(JSON_, null, 1);
writeFileSync(SALIDA, serializado);
console.log(`\n# r99 · JSON → ${SALIDA} (${serializado.length} bytes)`);


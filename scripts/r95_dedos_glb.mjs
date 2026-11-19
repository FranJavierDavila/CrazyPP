// r95 · ANÁLISIS ANATÓMICO de las manos de vr_arm.glb: cadenas de dedos,
// direcciones de reposo en el MARCO LOCAL de la mano, palma vía pulgar.
// Sirve de base factual para el curl de dedos y el rollo de muñeca.
import * as THREE from 'three';
globalThis.self = globalThis;   // GLTFLoader → loadImageSource usa self.URL
const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
import { readFileSync } from 'node:fs';

const buf = readFileSync('/home/z/my-project/upload/vr_arm.glb');
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
const gltf = await new Promise((res, rej) => new GLTFLoader().parse(ab, '', res, rej));
const nom = (b) => gltf.scene.getObjectByName(b);
gltf.scene.updateMatrixWorld(true);

const capas = [
  { lado: 'A', bra: nom('U_arm_021'), ant: nom('L_arm_022'), mano: nom('hand_023') },
  { lado: 'B', bra: nom('U_arm(mirrored)_02'), ant: nom('L_arm(mirrored)_03'),
    mano: nom('hand(mirrored)_04') },
];

for (const c of capas) {
  const mano = c.mano;
  console.log(`\n=== BRAZO ${c.lado} · mano=${mano.name} · hijos directos: ${mano.children.length}`);
  const manoInv = mano.matrixWorld.clone().invert();
  const aLocal = (v) => v.clone().applyMatrix4(manoInv);   // punto mundo → marco mano
  const dirLocal = (origenHijo, destino) => {              // dir del hueso en marco mano
    const p0 = aLocal(origenHijo.getWorldPosition(new THREE.Vector3()));
    const p1 = aLocal(destino.getWorldPosition(new THREE.Vector3()));
    return p1.sub(p0);
  };
  // 1) recorrido de la cadena de cada hijo (hasta la hoja)
  for (const f1 of mano.children) {
    const nombres = [f1.name];
    let ant = f1;
    const dirs = [];
    while (ant.children.length) {
      const sig = ant.children[0];
      nombres.push(sig.name);
      dirs.push(dirLocal(ant, sig).normalize().toArray().map((v) => +v.toFixed(3)));
      ant = sig;
    }
    const lon = dirLocal(f1, ant).length();
    console.log(`  cadena ${nombres.join(' → ')} · tramos=${dirs.length} · largo≈${lon.toFixed(3)}cm-GLB`);
    console.log(`    dirs en marco mano: ${JSON.stringify(dirs)}`);
  }
  // 2) orientación de la mano en el mundo y respecto al antebrazo
  const mQ = mano.getWorldQuaternion(new THREE.Quaternion());
  const eM = new THREE.Euler().setFromQuaternion(mQ, 'YXZ');
  console.log(`  mano quat mundo: [${[mQ.x,mQ.y,mQ.z,mQ.w].map(v=>+v.toFixed(3)).join(',')}] euler YXZ: [${[eM.x,eM.y,eM.z].map(v=>+v.toFixed(2)).join(',')}]`);
  const antQ = c.ant.getWorldQuaternion(new THREE.Quaternion());
  const relQ = antQ.clone().invert().multiply(mQ);
  const eR = new THREE.Euler().setFromQuaternion(relQ, 'XYZ');
  console.log(`  mano rel. antebrazo euler XYZ: [${[eR.x,eR.y,eR.z].map(v=>+v.toFixed(2)).join(',')}]`);
  // 3) eje del antebrazo y del brazo en el mundo (reposo)
  const S = c.bra.getWorldPosition(new THREE.Vector3());
  const E = c.ant.getWorldPosition(new THREE.Vector3());
  const W = mano.getWorldPosition(new THREE.Vector3());
  const dU = E.clone().sub(S).normalize(), dL = W.clone().sub(E).normalize();
  console.log(`  ejes mundo reposo: brazo [${[dU.x,dU.y,dU.z].map(v=>+v.toFixed(3))}] antebrazo [${[dL.x,dL.y,dL.z].map(v=>+v.toFixed(3))}]`);
  console.log(`  posiciones mundo: S=${S.toArray().map(v=>+v.toFixed(2))} E=${E.toArray().map(v=>+v.toFixed(2))} W=${W.toArray().map(v=>+v.toFixed(2))}`);
  // 4) ejes LOCALES de la mano proyectados al mundo (qué es X/Y/Z de la mano)
  const ax = ['X','Y','Z'].map((k, i) => {
    const v = new THREE.Vector3(i === 0 ? 1 : 0, i === 1 ? 1 : 0, i === 2 ? 1 : 0)
      .applyQuaternion(mQ).normalize();
    return `${k}→[${[v.x,v.y,v.z].map(n=>+n.toFixed(2))}]`;
  });
  console.log(`  ejes locales de la mano en mundo: ${ax.join('  ')}`);
}

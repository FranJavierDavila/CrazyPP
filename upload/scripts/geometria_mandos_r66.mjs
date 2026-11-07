#!/usr/bin/env node
/* r66 · Geometría REAL de los dos mandos GLB (izquierdo Mando.glb · derecho
 * mando_derecho.glb): replica EXACTAMENTE lo que hace buildMando() en c13
 * (Box3.setFromObject → center/size → esc = 0.205/maxdim → position.sub(cen)
 * → scale esc) y donde quedan las ANCLAS del izquierdo, para deducir las del
 * derecho en el MISMO espacio. También vuelca los clusters de la cabeza
 * (stick/botones) para validar a ojo. */
import { readFileSync } from 'node:fs';
globalThis.self = globalThis;          // GLTFLoader lo espera (entorno nodo)
globalThis.URL = globalThis.URL || (await import('node:url')).URL;
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const RUTAS = {
  izq: '/home/z/my-project/upload/Mando.glb',
  der: '/home/z/my-project/upload/mando_derecho.glb',
};

function cargar(ruta) {
  return new Promise((res, rej) => {
    const bin = Uint8Array.from(readFileSync(ruta)).buffer;
    new GLTFLoader().parse(bin, '', (g) => res(g), rej);
  });
}

for (const [tag, ruta] of Object.entries(RUTAS)) {
  const gltf = await cargar(ruta);
  const modelo = gltf.scene;
  modelo.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(modelo);
  const cen = box.getCenter(new THREE.Vector3());
  const tam = box.getSize(new THREE.Vector3());
  const esc = 0.205 / Math.max(tam.x, tam.y, tam.z, 0.01);
  console.log(`\n== ${tag} ==`);
  console.log(' bbox(size):', tam.toArray().map((v) => v.toFixed(5)).join(', '));
  console.log(' center:', cen.toArray().map((v) => v.toFixed(6)).join(', '));
  console.log(' esc:', esc.toFixed(3));

  // vértices del mesh (posición local del mesh, con SU matriz de nodo)
  let mesh = null;
  modelo.traverse((o) => { if (o.isMesh && !mesh) mesh = o; });
  const pos = mesh.geometry.attributes.position;
  console.log(' vértices:', pos.count);
  // a espacio de mandoSpin (padre de modelo): v_local_mesh con matrizMundo
  // del mesh relativa al modelo, luego (v - cen) * esc  [lo que hace c13]
  const mMesh = mesh.matrixWorld.clone();
  const mModel = modelo.matrixWorld.clone();
  const rel = mModel.clone().invert().multiply(mMesh);
  const v = new THREE.Vector3();
  const pts = [];
  for (let i = 0; i < pos.count; i += 7) {          // muestreo 1/7 (rápido)
    v.fromBufferAttribute(pos, i).applyMatrix4(rel);
    pts.push([(v.x - cen.x) * esc, (v.y - cen.y) * esc, (v.z - cen.z) * esc]);
  }
  // ANCLAS del izquierdo (c13) en este mismo espacio para comparar
  if (tag === 'izq') {
    const ANCLAS = {
      gatillo: [-0.0189, -0.021, 0.036],
      stick: [0.0076, 0.0192, 0.0342],
      botones: [-0.004, 0.0162, 0.0219],
      grip: [-0.0157, -0.0079, -0.0102],
    };
    console.log(' --- ANCLAS izq (espacio post-normalización, SIN ×esc):');
    for (const k in ANCLAS) console.log('   ', k, ANCLAS[k].join(', '));
    // ¿a qué vértice real se acerca cada ancla ×1.12/…? distancia mínima
    const dmin = (a) => {
      let m = 1e9, mejor = null;
      for (const p of pts) {
        const d = Math.hypot(p[0] - a[0], p[1] - a[1], p[2] - a[2]);
        if (d < m) { m = d; mejor = p; }
      }
      return [m, mejor];
    };
    for (const k in ANCLAS) {
      const a = ANCLAS[k];
      const [d, p] = dmin(a);
      console.log(`    ${k}: dist a vértice más próximo ${(d * 1000).toFixed(1)} mm → vértice (${p.map((x) => x.toFixed(4)).join(', ')})`);
    }
  }
  // clusters de la cabeza (Y alto) en el espacio post-normalización
  const ys = pts.map((p) => p[1]);
  const yMax = Math.max(...ys), yMin = Math.min(...ys);
  const alto = yMax - yMin;
  const cabeza = pts.filter((p) => p[1] > yMax - 0.22 * alto);
  // rejilla 8 mm
  const BIN = 0.008;
  const g = new Map();
  for (const p of cabeza) {
    const k = `${Math.floor(p[0] / BIN)},${Math.floor(p[2] / BIN)}`;
    if (!g.has(k)) g.set(k, []);
    g.get(k).push(p);
  }
  const cl = [...g.values()].filter((a) => a.length >= 12)
    .map((a) => {
      const c = [0, 1, 2].map((i) => a.reduce((s, p) => s + p[i], 0) / a.length);
      return { n: a.length, c };
    }).sort((a, b) => b.n - a.n).slice(0, 12);
  console.log(' clusters cabeza (n, x, y, z) esp. post-norm:');
  for (const { n, c } of cl) console.log(`   n=${String(n).padStart(4)}  (${c.map((x) => x.toFixed(4)).join(', ')})`);

  // gatillo: cabeza, lado -Z (¿o +Z?) — imprime extremos Z de la cabeza
  const zc = cabeza.map((p) => p[2]);
  console.log(' cabeza Z min/max:', Math.min(...zc).toFixed(4), Math.max(...zc).toFixed(4));
  // grip: mango lateral (Y bajo, X extremo)
  const mango = pts.filter((p) => p[1] < yMin + 0.45 * alto);
  const xs = mango.map((p) => p[0]);
  const xLo = mango.filter((p) => p[0] < Math.min(...xs) + 0.1 * (Math.max(...xs) - Math.min(...xs)));
  const xHi = mango.filter((p) => p[0] > Math.max(...xs) - 0.1 * (Math.max(...xs) - Math.min(...xs)));
  const centro = (a) => [0, 1, 2].map((i) => a.reduce((s, p) => s + p[i], 0) / a.length);
  if (xLo.length) console.log(' mango -X centro:', centro(xLo).map((x) => x.toFixed(4)).join(', '), `n=${xLo.length}`);
  if (xHi.length) console.log(' mango +X centro:', centro(xHi).map((x) => x.toFixed(4)).join(', '), `n=${xHi.length}`);
}
console.log('\nLISTO');

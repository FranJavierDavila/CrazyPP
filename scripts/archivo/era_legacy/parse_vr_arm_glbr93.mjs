#!/usr/bin/env node
/* =====================================================================
 * r93 · PARSEO vr_arm.glb — jerarquía de huesos, skins, longitudes,
 * ibm, pesos y mallas. Todo por consola para diseñar el driver IK.
 * ===================================================================== */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const ruta = fileURLToPath(new URL('../upload/vr_arm.glb', import.meta.url));
const buf = readFileSync(ruta);
console.log(`vr_arm.glb · ${(buf.length / 1024).toFixed(1)} KB`);

// --- cabecera GLB ---
const magic = buf.readUInt32LE(0);
const version = buf.readUInt32LE(4);
if (magic !== 0x46546c67) { console.error('No es un GLB'); process.exit(1); }
console.log(`GLB v${version} · chunks:`);

// --- chunks ---
let off = 12;
const chunks = [];
while (off < buf.length) {
  const len = buf.readUInt32LE(off);
  const type = buf.readUInt32LE(off + 4);
  const tipoStr = String.fromCharCode(type & 0xff, (type >> 8) & 0xff,
    (type >> 16) & 0xff, (type >> 24) & 0xff);
  chunks.push({ tipo: tipoStr, len, off: off + 8 });
  console.log(`  · ${tipoStr} · ${len} B`);
  off += 8 + len;
}

const jsonChunk = chunks.find(c => c.tipo === 'JSON');
const gltf = JSON.parse(buf.slice(jsonChunk.off, jsonChunk.off + jsonChunk.len).toString('utf8'));

console.log(`\n== GLTF ==`);
console.log(`nodos: ${gltf.nodes?.length || 0} · mallas: ${gltf.meshes?.length || 0} · skins: ${gltf.skins?.length || 0} · escenas: ${gltf.scenes?.length || 0}`);
console.log(`extensiones usadas: ${JSON.stringify(gltf.extensionsUsed || [])}`);

// --- nodos ---
const nodos = gltf.nodes || [];
console.log(`\n== NODOS (${nodos.length}) ==`);
nodos.forEach((n, i) => {
  const t = n.translation ? n.translation.map(v => +v.toFixed(4)).join(', ') : '—';
  const r = n.rotation ? n.rotation.map(v => +v.toFixed(3)).join(', ') : '—';
  const s = n.scale ? n.scale.map(v => +v.toFixed(3)).join(', ') : '—';
  console.log(`  [${i}] ${n.name || '(sin nombre)'} · mesh:${n.mesh ?? '—'} skin:${n.skin ?? '—'} · hijos:[${(n.children || []).join(',')}]`);
  console.log(`      T[${t}] R[${r}] S[${s}]`);
});

// --- skins ---
(gltf.skins || []).forEach((sk, i) => {
  console.log(`\n== SKIN ${i}: ${sk.name || '(sin nombre)'} ==`);
  console.log(`  skeleton(root): ${sk.skeleton} · joints: ${sk.joints.length}`);
  console.log(`  joints: ${sk.joints.map(j => `${j}(${nodos[j].name || '?'})`).join(' · ')}`);
  console.log(`  inverseBindMatrices: accessor ${sk.inverseBindMatrices}`);
});

// --- mallas + primitivas + atributos ---
(gltf.meshes || []).forEach((m, i) => {
  console.log(`\n== MALLA ${i}: ${m.name || '(sin nombre)'} ==`);
  (m.primitives || []).forEach((p, j) => {
    const attrs = Object.keys(p.attributes || {}).map(a => `${a}=${p.attributes[a]}`);
    console.log(`  prim ${j}: [${attrs.join(' · ')}] índices:${p.indices ?? '—'} modo:${p.mode ?? 4}`);
    if (p.targets) console.log(`    morph targets: ${p.targets.length}`);
  });
  if (m.weights) console.log(`  weights: ${m.weights.join(', ')}`);
});

// --- accessors de interés (POSITION de nodos con skin, ibm) ---
console.log(`\n== ACCESSORS (los primeros 20) ==`);
(gltf.accessors || []).slice(0, 20).forEach((a, i) => {
  console.log(`  [${i}] ${a.type} · count ${a.count} · min/max ${a.min ? a.min.map(v => +v.toFixed(3)) : ''}`);
});

// --- imágenes/texturas (para el tamaño) ---
console.log(`\n== MEDIA ==`);
console.log(`imágenes: ${(gltf.images || []).length} · texturas: ${(gltf.textures || []).length} · materiales: ${(gltf.materials || []).length}`);
(gltf.images || []).forEach((im, i) => console.log(`  img ${i}: ${im.name || im.uri || '(bin)'} · mime ${im.mimeType || '?'}`));
(gltf.materials || []).forEach((mt, i) => console.log(`  mat ${i}: ${mt.name || '(sin nombre)'} · pbr:${!!mt.pbrMetallicRoughness}`));

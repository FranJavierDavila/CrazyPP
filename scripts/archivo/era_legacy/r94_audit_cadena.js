// Auditoría de la CADENA de huesos de hand_023 en el GLB real:
// ¿alguno usa `matrix` en vez de t/r/s? ¿hay escalas ≠ uniformes?
// ¿el offset del hijo cae sobre el +X local del padre?
const fs = require('fs');
const buf = fs.readFileSync('/home/z/my-project/upload/vr_arm.glb');
const jl = buf.readUInt32LE(12);
const g = JSON.parse(buf.slice(20, 20 + jl).toString('utf8'));
const idx = {};
g.nodes.forEach((n, i) => idx[n.name] = i);
const parent = {};
g.nodes.forEach((n, i) => (n.children || []).forEach(c => parent[c] = i));

const chain = [];
let cur = idx['hand_023'];
while (cur !== undefined) { chain.unshift(cur); cur = parent[cur]; }
console.log('cadena:', chain.map(i => `${i}:${g.nodes[i].name}`).join(' → '));
for (const i of chain) {
  const n = g.nodes[i];
  console.log(`--- ${i}:${n.name}`);
  if (n.matrix) {
    console.log('  MATRIX:', n.matrix.map(v => +v.toFixed(4)).join(', '));
    // extrae T/R/S de la matriz (column-major de glTF)
    const m = n.matrix;
    const T = [m[12], m[13], m[14]];
    const sx = Math.hypot(m[0], m[1], m[2]);
    const sy = Math.hypot(m[4], m[5], m[6]);
    const sz = Math.hypot(m[8], m[9], m[10]);
    console.log('  ⇒ T=', T.map(v=>+v.toFixed(3)), ' S=', [+sx.toFixed(5), +sy.toFixed(5), +sz.toFixed(5)]);
  } else {
    console.log('  t=', (n.translation || []).map(v=>+v.toFixed(3)),
      ' r=', (n.rotation || []).map(v=>+v.toFixed(4)),
      ' s=', n.scale || '(1,1,1)');
  }
}
// el offset del hijo en el espacio LOCAL del padre: ¿es +X?
const armIdx = idx['U_arm_021'], antIdx = idx['L_arm_022'], handIdx = idx['hand_023'];
const par = g.nodes[armIdx];
console.log('\nhijo L_arm en espacio local de U_arm:', g.nodes[antIdx].translation);
console.log('hijo hand en espacio local de L_arm:', g.nodes[handIdx].translation);
// y la rotación de U_arm aplicada al +X local:
const q = par.rotation; // (x,y,z,w)
const v = new THREEVec(); // placeholder

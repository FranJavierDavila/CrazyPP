// Parse vr_arm.glb: JSON chunk → nodes, skins, materials, meshes
const fs = require('fs');
const buf = fs.readFileSync('/home/z/my-project/upload/vr_arm.glb');
const magic = buf.readUInt32LE(0);
const ver = buf.readUInt32LE(4);
const len = buf.readUInt32LE(8);
console.log('magic', magic.toString(16), 'version', ver, 'len', len, 'file', buf.length);
let off = 12;
let json = null, binChunk = null;
while (off < len) {
  const clen = buf.readUInt32LE(off);
  const ctype = buf.toString('ascii', off + 4, off + 8).trim();
  const data = buf.subarray(off + 8, off + 8 + clen);
  if (ctype === 'JSON') json = JSON.parse(data.toString('utf8'));
  else if (ctype === 'BIN') binChunk = data;
  off += 8 + clen;
}
console.log('== asset ==', json.asset);
console.log('== materials ==', JSON.stringify(json.materials || [], null, 1).slice(0, 1200));
console.log('== textures ==', (json.textures || []).length, 'images:', (json.images || []).length);
console.log('== skins ==', (json.skins || []).length);
for (const s of json.skins || []) {
  console.log('  skin joints:', s.joints.length, 'inverseBindMatrices acc', s.inverseBindMatrices);
}
console.log('== nodes ==', json.nodes.length);
const byName = {};
json.nodes.forEach((n, i) => { byName[n.name] = i; });
console.log('node names:', json.nodes.map((n, i) => `${i}:${n.name}${n.mesh !== undefined ? ' [mesh' + n.mesh + ']' : ''}`).join('\n'));
console.log('== meshes ==', (json.meshes || []).map(m => `${m.name} prims=${m.primitives.length} mat=${m.primitives.map(p => p.material).join(',')} pos=${m.primitives[0].attributes.POSITION}`).join('\n'));
console.log('== accessors count ==', (json.accessors || []).length);
console.log('== scenes ==', JSON.stringify(json.scenes));
const minmax = (ai) => {
  const a = json.accessors[ai];
  return { min: a.min, max: a.max, count: a.count, compType: a.componentType, type: a.type };
};
for (const m of json.meshes || []) {
  for (const p of m.primitives) {
    console.log('mesh', m.name, 'POS', minmax(p.attributes.POSITION), 'JOINTS', p.attributes.JOINTS_0 !== undefined ? minmax(p.attributes.JOINTS_0) : null, 'WEIGHTS', p.attributes.WEIGHTS_0 !== undefined ? minmax(p.attributes.WEIGHTS_0) : null);
  }
}
// node translations of key bones
const want = ['Body_01', 'U_arm_021', 'L_arm_022', 'hand_023', 'U_arm(mirrored)_02', 'L_arm(mirrored)_03', 'hand(mirrored)_04'];
for (const w of want) {
  const n = json.nodes[byName[w]];
  if (!n) { console.log('MISSING', w); continue; }
  console.log('node', w, 't=', n.translation, 'r=', n.rotation, 's=', n.scale, 'parent=', json.nodes.findIndex(x => (x.children || []).includes(byName[w])));
}

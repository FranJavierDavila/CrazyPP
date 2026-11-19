// Variante del repro con GLB SIN texturas (para Node): quita images/
// textures/samplers y las referencias de material → parse no decodifica
// imágenes y reproduce EXACTAMENTE el material blanco por defecto.
const fs = require('fs');
const src = fs.readFileSync('/home/z/my-project/upload/vr_arm.glb');
const jl = src.readUInt32LE(12);
const json = JSON.parse(src.slice(20, 20 + jl).toString('utf8'));
const bin = src.subarray(20 + jl + 8, src.readUInt32LE(8));

json.extensionsUsed = [];
json.extensionsRequired = [];
delete json.textures; delete json.images; delete json.samplers;
for (const m of json.materials || []) {
  m.pbrMetallicRoughness = { baseColorFactor: [1, 1, 1, 1], metallicFactor: 1, roughnessFactor: 1 };
  delete m.normalTexture; delete m.occlusionTexture; delete m.extensions;
}
const enc = Buffer.from(JSON.stringify(json), 'utf8');
const pad = (4 - (enc.length % 4)) % 4;
const encPad = Buffer.concat([enc, Buffer.alloc(pad, 0x20)]);
const lenB = Buffer.alloc(4);
lenB.writeUInt32LE(12 + 8 + encPad.length + 8 + bin.length);
const out = Buffer.concat([
  Buffer.from('glTF'), Buffer.from([2, 0, 0, 0]), lenB,
  (() => { const b = Buffer.alloc(4); b.writeUInt32LE(encPad.length); return b; })(),
  Buffer.from('JSON'), encPad,
  (() => { const b = Buffer.alloc(4); b.writeUInt32LE(bin.length); return b; })(),
  Buffer.from('BIN\0'), bin,
]);
fs.writeFileSync('/home/z/my-project/tmp_assets/vr_arm_notex.glb', out);
console.log('escrito tmp_assets/vr_arm_notex.glb', out.length, 'bytes · material SIN texturas (blanco metálico, igual que producción sin soporte spec-gloss)');

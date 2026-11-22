// Prueba definitiva: ¿GLTFLoader de three 0.186 puede parsear vr_arm.glb
// (que exige KHR_materials_pbrSpecularGlossiness en extensionsRequired)?
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { readFileSync } from 'node:fs';

const buf = readFileSync('/home/z/my-project/upload/vr_arm.glb');
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
try {
  const gltf = await new Promise((res, rej) => new GLTFLoader().parse(ab, '', res, rej));
  console.log('PARSE OK — no lanzó excepción');
  const nom = (b) => gltf.scene.getObjectByName(b);
  console.log('Body_01:', !!nom('Body_01'), 'U_arm_021:', !!nom('U_arm_021'),
    'U_arm(mirrored)_02:', !!nom('U_arm(mirrored)_02'));
  const mats = [];
  gltf.scene.traverse((o) => {
    if (o.isMesh) {
      const m = o.material;
      mats.push({ name: o.name, tipo: m && m.type, map: !!(m && m.map),
        color: m && m.color ? '#' + m.color.getHexString() : null,
        metal: m && m.metalness, rough: m && m.roughness,
        skin: o.isSkinnedMesh, verde: o.visible,
        weights: o.geometry && o.geometry.attributes.color ? 'vertex-colors' : null });
    }
  });
  console.log('meshes:', JSON.stringify(mats, null, 1));
} catch (e) {
  console.log('PARSE FALLÓ:', e && e.message ? e.message : e);
}

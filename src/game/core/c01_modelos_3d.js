import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

/* =====================================================================
 *  MODELO DE PALA (GLB del usuario, incrustado en base64)
 *  Ejes del modelo: hoja hacia +Y, mango hacia -Y, cara normal ±Z.
 *  Escala 0.026 m/unidad -> hoja de 16 cm, pala completa de 26 cm.
 * ===================================================================== */


// v2.38 · PISTOLA DE RAYOS (superpoder de ARKANOID, GLB incrustado).
// A escala real (~26 cm), cañón hacia -Z y empuñadura hacia -Y: se monta
// DIRECTO en el espacio grip del mando libre.


export const PALA_SCALE = 0.026;
// punto de agarre (centro del mango) y centro de la hoja en coordenadas del modelo
export const PALA_GRIP_Y = -2.9;
export const PALA_BLADE_Y = 2.1115;

/**
 * Corrige mallas del GLB con winding/normales invertidos (cara interna hacia
 * fuera): calcula el volumen firmado y, si es negativo, invierte el orden de
 * los triángulos y niega las normales. Así la iluminación, las sombras y los
 * contornos de la pala se ven SIEMPRE correctos, sin depender del exportador.
 */
export function fixInvertedMeshes(root) {
  let fixed = 0;
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const bc = new THREE.Vector3();
  root.traverse((o) => {
    if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return;
    const geo = o.geometry;
    const pos = geo.attributes.position;
    const idx = geo.index;
    const triCount = Math.floor((idx ? idx.count : pos.count) / 3);
    if (!triCount) return;

    let vol = 0;
    for (let i = 0; i < triCount; i++) {
      const i0 = idx ? idx.getX(i * 3) : i * 3;
      const i1 = idx ? idx.getX(i * 3 + 1) : i * 3 + 1;
      const i2 = idx ? idx.getX(i * 3 + 2) : i * 3 + 2;
      a.fromBufferAttribute(pos, i0);
      b.fromBufferAttribute(pos, i1);
      c.fromBufferAttribute(pos, i2);
      vol += a.dot(bc.copy(b).cross(c)) / 6;   // volumen firmado
    }
    if (vol > -1e-10) return;                  // bien orientada o abierta: nada

    if (idx) {
      const arr = idx.array;
      for (let i = 0; i < triCount; i++) {
        const s = i * 3;
        const t = arr[s + 1];
        arr[s + 1] = arr[s + 2];
        arr[s + 2] = t;
      }
      idx.needsUpdate = true;
    } else {
      for (const name of Object.keys(geo.attributes)) {
        const attr = geo.attributes[name];
        const v = attr.array;
        const it = attr.itemSize;
        for (let i = 0; i < triCount; i++) {
          const o1 = (i * 3 + 1) * it;
          const o2 = (i * 3 + 2) * it;
          for (let k = 0; k < it; k++) {
            const t = v[o1 + k];
            v[o1 + k] = v[o2 + k];
            v[o2 + k] = t;
          }
        }
        attr.needsUpdate = true;
      }
    }
    const nor = geo.attributes.normal;
    if (nor) {
      for (let i = 0; i < nor.count; i++) {
        nor.setXYZ(i, -nor.getX(i), -nor.getY(i), -nor.getZ(i));
      }
      nor.needsUpdate = true;
    }
    fixed++;
  });
  return fixed;
}

/** v3.0.3 · Endurece el modelo tras la carga (opaco, doble cara, sin brillos
 *  metálicos falsos). Compartido por el GLB externo y el incrustado. */
function hardenPaddle(model) {
  const fixedMeshes = fixInvertedMeshes(model);
  if (fixedMeshes) {
    console.info(`Pala: ${fixedMeshes} malla(s) con winding/normales invertidos corregida(s)`);
  }
  model.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) {
        if (!m) continue;
        // Doble cara: evita caras invertidas del GLB; la pala se ve bien
        // por ambos lados (goma roja / madera) desde cualquier ángulo.
        m.side = THREE.DoubleSide;
        m.shadowSide = THREE.DoubleSide;
        // v2.21 · TRANSPARENCIA FANTASMA: los exportadores suelen marcar
        // BLEND aunque la textura sea RGB sin canal alfa y el alfa base
        // sea 1. GLTFLoader entonces fija transparent=true Y
        // depthWrite=false (three#17706): la pala se dibuja en el pase
        // transparente sin escribir profundidad y, con doble cara, se
        // ven las caras internas (efecto radiografía / "invertida").
        // Si no hay transparencia real, devolvemos el material al pase
        // opaco con depthWrite=true. Es el arreglo definitivo del
        // "efecto invertido" reportado desde la v1.
        if (m.transparent && m.opacity >= 1 && !m.alphaTest) {
          m.transparent = false;
          m.depthWrite = true;
        }
        m.needsUpdate = true;
        if (m.isMeshStandardMaterial) {
          m.metalness = Math.min(m.metalness ?? 0, 0.35);
          m.roughness = Math.max(m.roughness ?? 0.75, 0.45);
          m.envMapIntensity = 0.9;
        }
      }
    }
  });
  return model;
}

/** v3.0.3 · Carga el GLB de la pala desde assets/pala/pala.glb — la pala
 *  no vive dentro del código: sustituir ese archivo cambia la pala de todo
 *  el juego sin tocar nada (pedido del dueño para crecer por assets).
 *  C2 (r129 · ola 3): ya NO hay copia base64 en el HTML — si el GLB falta,
 *  resuelve null y makePaddleVisual dibuja la pala procedural. */
export function loadPaddleModel() {
  return new Promise((resolve) => {
    const loader = new GLTFLoader();
    fetch('assets/pala/pala.glb')
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((buf) => new Promise((res, rej) => loader.parse(buf, '', (g) => res(g), rej)))
      .then((gltf) => {
        console.info('Pala: modelo EXTERNO assets/pala/pala.glb cargado');
        resolve(hardenPaddle(gltf.scene));
      })
      .catch(() => {
        console.warn('Pala: GLB externo no disponible — pala procedural');
        resolve(null);
      });
  });
}

/**
 * Instancia de la pala.
 *  mode='grip'  -> el punto de agarre queda en el origen (para el mando)
 *  mode='center'-> el centro de la hoja queda en el origen (para la IA)
 */
export function makePaddleVisual(model, mode) {
  const g = new THREE.Group();
  if (model) {
    const inst = model.clone(true);
    inst.scale.setScalar(PALA_SCALE);
    inst.position.y = mode === 'grip'
      ? -PALA_GRIP_Y * PALA_SCALE
      : -PALA_BLADE_Y * PALA_SCALE;
    g.add(inst);
  } else {
    // fallback: pala procedural si el GLB no cargara
    const R = 0.0795;
    const blade = new THREE.Mesh(
      new THREE.CylinderGeometry(R, R, 0.014, 32),
      [
        new THREE.MeshStandardMaterial({ color: 0xb98a5a, roughness: 0.7, side: THREE.DoubleSide }),
        new THREE.MeshStandardMaterial({ color: 0xc0392b, roughness: 0.95, side: THREE.DoubleSide }),
        new THREE.MeshStandardMaterial({ color: 0x17181a, roughness: 0.95, side: THREE.DoubleSide }),
      ],
    );
    blade.rotation.x = Math.PI / 2;
    blade.position.y = mode === 'grip' ? 0.14 : 0;
    blade.castShadow = true;
    g.add(blade);
    const handle = new THREE.Mesh(
      new THREE.BoxGeometry(0.03, 0.02, 0.1),
      new THREE.MeshStandardMaterial({ color: 0x8a6540, roughness: 0.8 }),
    );
    handle.position.set(0, mode === 'grip' ? 0.02 : -0.12, -0.055);
    g.add(handle);
  }
  return g;
}

/* =====================================================================
 *  v2.38 · PISTOLA DE RAYOS (superpoder ARKANOID)
 *  Carga el GLB incrustado y devuelve un grupo listo para el mando libre:
 *  cañón hacia -Z, empuñadura hacia -Y, origen en el punto de agarre.
 *  Sin GLB (o si falla): pistola procedural low-poly de respaldo.
 * ===================================================================== */
/* v2.38 · PISTOLA DE RAYOS (superpoder ARKANOID)
 * v2.45 · pistol.glb del JUGADOR: análisis de la geometría real del GLB —
 * el cañón YA apunta a -Z del mundo glTF (PCA de la corrediza: desvío 1,4°)
 * y la empuñadura cae hacia -Y, así que el pitch de montaje es 0 (el 60° de
 * v2.44 la ponía "apuntando al cielo"). El modelo se escala a tamaño real
 * (×0,05 → 18,8 cm de largo) y se RECENTRA dejando el PUÑO en el origen del
 * grip: la mano agarra la empuñadura como en una pistola de verdad. */
const GUN_MOUNT_PITCH = 0;
const GUN_SCALE = 0.05;
const GUN_GRIP = { x: 1.5504, y: -0.9415, z: 1.4313 };   // ancla del puño (coords modelo)
const GUN_MUZZLE = new THREE.Vector3(0.0003, 0.092, -0.163); // boca del cañón (m, en montura)

export function loadGunModel() {
  return new Promise((resolve) => {
    // C2 (r129): el GLB vive en assets/externos/gun.glb (antes base64).
    // Sin GLB o si falla: null → pistola procedural de makeGunVisual.
    const loader = new GLTFLoader();
    fetch('assets/externos/gun.glb')
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((buf) => {
        loader.parse(buf, '', (gltf) => {
        const model = gltf.scene;
        fixInvertedMeshes(model);
        model.traverse((o) => {
          if (!o.isMesh) return;
          o.castShadow = true;
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          for (const m of mats) {
            if (!m) continue;
            m.side = THREE.FrontSide;
            if (m.transparent && m.opacity >= 1 && !m.alphaTest) {
              m.transparent = false;
              m.depthWrite = true;
            }
            m.needsUpdate = true;
            if (m.isMeshStandardMaterial) {
              m.envMapIntensity = 0.9;
              // respeta el emissive de las piezas energéticas del GLB
              if (!m.emissive) m.emissive = new THREE.Color(0x000000);
            }
          }
        });
          resolve(model);
        }, () => resolve(null));
      })
      .catch(() => resolve(null));
  });
}

export function makeGunVisual(model) {
  const g = new THREE.Group();
  if (model) {
    const inner = model.clone(true);
    // v2.45 · ENCAJE EN LA MANO: escala real y el PUÑO de la empuñadura en
    // el origen del grip (cañón nativo hacia -Z, pitch 0 — ver constante).
    inner.scale.setScalar(GUN_SCALE);
    inner.position.set(
      -GUN_GRIP.x * GUN_SCALE,
      -GUN_GRIP.y * GUN_SCALE + 0.012,
      -GUN_GRIP.z * GUN_SCALE);
    inner.rotation.x = GUN_MOUNT_PITCH;
    g.add(inner);
  } else {
    // respaldo procedural: pistola de rayos low-poly (mismo encaje)
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(0.044, 0.058, 0.175),
      new THREE.MeshStandardMaterial({ color: 0x2b2f36, roughness: 0.38, metalness: 0.85 }));
    body.position.set(0, 0.052, -0.03);
    const barrel = new THREE.Mesh(
      new THREE.CylinderGeometry(0.0135, 0.0135, 0.07, 16),
      new THREE.MeshStandardMaterial({ color: 0x1f2227, roughness: 0.45, metalness: 0.85 }));
    barrel.rotation.x = Math.PI / 2;
    barrel.position.set(0, 0.056, -0.135);
    const tip = new THREE.Mesh(
      new THREE.CylinderGeometry(0.017, 0.017, 0.015, 16),
      new THREE.MeshStandardMaterial({
        color: 0xff9a3c, emissive: 0xff7a1a, emissiveIntensity: 1.4, roughness: 0.3,
      }));
    tip.rotation.x = Math.PI / 2;
    tip.position.set(0, 0.056, -0.173);
    const grip = new THREE.Mesh(
      new THREE.BoxGeometry(0.034, 0.118, 0.049),
      new THREE.MeshStandardMaterial({ color: 0x1a1c21, roughness: 0.92, metalness: 0.15 }));
    grip.position.set(0, -0.03, 0.037);
    grip.rotation.x = 0.34;
    g.add(body, barrel, tip, grip);
  }
  return g;
}

/* =====================================================================
 *  CONSTANTES (unidades SI · mesa reglamentaria ITTF)
 * ===================================================================== */

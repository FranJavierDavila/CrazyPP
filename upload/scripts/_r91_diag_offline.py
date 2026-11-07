#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91_diag_offline.py — diagnóstico r91 parte 1 (offline):
1) winding/normales del LatheGeometry de la calabaza procedural (perfil EXACTO
   del módulo) — ¿las caras miran hacia FUERA o hacia DENTRO?
2) contenido de la franja inferior de mano1/2/3.webp — ¿qué amputa el cultivo
   MANO_CULTIVO 0.70/offset 0.30?
3) perfiles de audio de los mp3 del zombi y de la BSO (ffprobe).
"""
import subprocess, json, os, sys

RAIZ = '/home/z/my-project'
HL = os.path.join(RAIZ, 'public', 'championships', 'halloween')

print('=== 1) LATHE DE LA CALABAZA (three.js real) ===')
MJS = r"""
const THREE = require('/home/z/my-project/node_modules/three/build/three.cjs');
// perfil EXACTO de _calabazaProcedural (index.js r90)
const perfil = [
  [0.000,-1.000],[0.200,-0.985],[0.520,-0.880],[0.780,-0.640],
  [0.940,-0.320],[1.000,-0.020],[0.950,0.300],[0.800,0.580],
  [0.560,0.800],[0.300,0.940],[0.110,0.995],
].map(p => new THREE.Vector2(p[0]*0.065, p[1]*0.052));
const geo = new THREE.LatheGeometry(perfil, 28);
const pos = geo.attributes.position, idx = geo.index, nor = geo.attributes.normal;
// para cada triangulo: ¿su normal geométrica apunta hacia fuera (mismo
// hemisferio que el centroide) o hacia dentro?
let out = 0, inn = 0;
for (let i = 0; i < idx.count; i += 3) {
  const a = new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i));
  const b = new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i+1));
  const c = new THREE.Vector3().fromBufferAttribute(pos, idx.getX(i+2));
  const nrm = new THREE.Vector3().subVectors(c, b).cross(new THREE.Vector3().subVectors(a, b));
  const cen = new THREE.Vector3().copy(a).add(b).add(c).multiplyScalar(1/3);
  // radial del centroide (x,z) — la dirección «hacia fuera» del cuerpo
  const rad = new THREE.Vector3(cen.x, 0, cen.z);
  if (rad.lengthSq() < 1e-9) continue;
  if (nrm.dot(rad) > 0) out++; else inn++;
}
console.log(JSON.stringify({triangulos: (idx.count/3)|0, normalesFuera: out, normalesDentro: inn}));
"""
r = subprocess.run(['node', '-e', MJS], capture_output=True, text=True, timeout=60)
print(r.stdout.strip() or r.stderr.strip()[:600])

print()
print('=== 2) FRANJA INFERIOR DE LAS MANOS (lo que corta MANO_CULTIVO 0.70) ===')
try:
    from PIL import Image
    import numpy as np
    for n in ('mano1.webp', 'mano2.webp', 'mano3.webp'):
        im = Image.open(os.path.join(HL, 'assets', n)).convert('RGBA')
        a = np.array(im)
        h, w = a.shape[:2]
        # cultivo: offset.y=0.30, repeat.y=0.70 → se muestra la franja SUPERIOR
        # (v de 0.30 a 1.00). En píxeles con flipY: la franja inferior del ARTE
        # (últimas filas) es la amputada.
        corte = int(h * 0.30)
        abajo = a[h-corte:, :, 3]
        # % de píxeles VISIBLES (alpha>128) en la franja amputada
        pct = (abajo > 128).mean() * 100
        # color medio de lo visible
        vis = a[h-corte:, :, :3][abajo > 128]
        medio = vis.mean(axis=0).astype(int) if len(vis) else None
        print(f'{n}: {w}x{h} · franja amputada={corte}px · visible en ella: {pct:.1f}% · RGB medio {medio}')
except Exception as e:
    print('PIL fallo:', e)

print()
print('=== 3) PERFILES DE AUDIO (lo que decodifica el casco: 44100 CBR) ===')
for f in ('midnight_volley.mp3', 'risas.mp3', 'zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3', 'bso.wav', 'fly_buzz.mp3'):
    p = os.path.join(HL, 'assets', f)
    if not os.path.exists(p):
        print(f'{f}: AUSENTE'); continue
    try:
        out = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json',
                              '-show_streams', p], capture_output=True, text=True, timeout=30).stdout
        s = json.loads(out)['streams'][0]
        print(f"{f}: {s.get('sample_rate')} Hz · {s.get('bit_rate')} bps · {s.get('codec_name')} · {float(s.get('duration',0)):.2f}s")
    except Exception as e:
        print(f'{f}: ffprobe fallo {e}')
print('DIAG OFFLINE OK')

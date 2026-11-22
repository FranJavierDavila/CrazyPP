#!/usr/bin/env python3
"""Inspecciona el GLB de la pala embebido en game.html (V3.0.2):
nombres de nodos/mallas, materiales y cotas nativas por primitiva."""
import base64
import json
import re
import struct
import sys

SRC = '/home/z/my-project/public/game.html'
OUT_DIR = '/home/z/my-project/scripts/tmp_pala'

src = open(SRC, encoding='utf-8').read()
m = re.search(r"const PALA_GLB_B64 = '([^']+)'", src)
if not m:
    print('NO PALA_GLB_B64'); sys.exit(1)
raw = base64.b64decode(m.group(1))
print('GLB bytes:', len(raw))

magic, ver, length = struct.unpack('<III', raw[:12])
assert magic == 0x46546C67, 'not glTF'
off = 12
json_len, json_type = struct.unpack('<II', raw[off:off + 8])
gltf = json.loads(raw[off + 8:off + 8 + json_len])
bin_off = off + 8 + json_len
bin_len, bin_type = struct.unpack('<II', raw[bin_off:bin_off + 8])
print('JSON len:', json_len, '· BIN len:', bin_len)

print('\n=== meshes ===')
for i, mesh in enumerate(gltf.get('meshes', [])):
    print(f"mesh[{i}] name={mesh.get('name')!r}")
    for j, prim in enumerate(mesh.get('primitives', [])):
        mat = prim.get('material')
        matname = gltf['materials'][mat].get('name') if mat is not None and 'materials' in gltf else None
        print(f"  prim[{j}] material={mat} ({matname!r}) attrs={list(prim['attributes'].keys())}")

print('\n=== materials ===')
for i, mat in enumerate(gltf.get('materials', [])):
    pbr = mat.get('pbrMetallicRoughness', {})
    print(f"material[{i}] name={mat.get('name')!r} baseColorFactor={pbr.get('baseColorFactor')} "
          f"metallic={pbr.get('metallicFactor')} rough={pbr.get('roughnessFactor')} "
          f"baseColorTexture={pbr.get('baseColorTexture')} emissive={mat.get('emissiveFactor')}")

print('\n=== nodes ===')
def walk(idx, depth):
    n = gltf['nodes'][idx]
    print('  ' * depth + f"node[{idx}] name={n.get('name')!r} mesh={n.get('mesh')} "
          f"trans={n.get('translation')} scale={n.get('scale')} rot={n.get('rotation')}")
    for ch in n.get('children', []):
        walk(ch, depth + 1)
for s in gltf.get('scenes', []):
    for root in s.get('nodes', []):
        walk(root, 0)

def acc_bounds(ai):
    a = gltf['accessors'][ai]
    return a.get('min'), a.get('max'), a.get('count')

print('\n=== cotas por primitiva (POSIX, unidades nativas) ===')
for i, mesh in enumerate(gltf.get('meshes', [])):
    for j, prim in enumerate(mesh.get('primitives', [])):
        mn, mx, cnt = acc_bounds(prim['attributes']['POSITION'])
        print(f"mesh[{i}].prim[{j}] count={cnt} min={[round(v,4) for v in mn]} max={[round(v,4) for v in mx]}")

# extraer el GLB para el nuevo loader externo
import os
os.makedirs(OUT_DIR, exist_ok=True)
out = os.path.join(OUT_DIR, 'pala_base.glb')
open(out, 'wb').write(raw)
print('\nGLB extraído a', out, f'({len(raw)} B)')

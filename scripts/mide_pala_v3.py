#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae el GLB de la pala de game.html y mide su geometría en coords de montura.

Montura (makePaddleVisual mode='grip'):
  mount = (x,y,z)_escena * PALA_SCALE + (0, -PALA_GRIP_Y*PALA_SCALE, 0)
i.e. mount_y = y*0.026 + 0.0754  (PALA_GRIP_Y=-2.9, PALA_SCALE=0.026)
"""
import base64, json, re, struct, sys
import numpy as np

SRC = '/home/z/my-project/public/game.html'
OUT = '/home/z/my-project/scripts/tmp_pala/pala.glb'

s = open(SRC, encoding='utf-8').read()
m = re.search(r"const PALA_GLB_B64 = '([A-Za-z0-9+/=]+)'", s)
assert m, 'b64 no encontrado'
glb = base64.b64decode(m.group(1))
import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(glb)
print(f'GLB extraído: {len(glb)} bytes -> {OUT}')

# --- parse GLB ---
magic, ver, total = struct.unpack('<III', glb[:12])
assert magic == 0x46546C67
clen, ctype = struct.unpack('<II', glb[12:20])
j = json.loads(glb[20:20 + clen])
bin_off = 20 + clen
blen, btype = struct.unpack('<II', glb[bin_off:bin_off + 8])
assert btype == 0x004E4942
BIN = glb[bin_off + 8: bin_off + 8 + blen]

CT = {5120: 'i1', 5121: 'u1', 5122: 'i2', 5123: 'u2', 5125: 'u4', 5126: 'f4'}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def read_acc(idx):
    a = j['accessors'][idx]
    bv = j['bufferViews'][a['bufferView']]
    n = NC[a['type']]
    dt = np.dtype(CT[a['componentType']])
    dt = dt.newbyteorder('<')
    stride = bv.get('byteStride') or (n * dt.itemsize)
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    cnt = a['count']
    out = np.zeros((cnt, n), dtype=np.float64)
    for i in range(cnt):
        out[i] = np.frombuffer(BIN, dtype=dt, count=n, offset=off + i * stride)
    return out

def node_matrix(node):
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=np.float64).reshape(4, 4).T
    M = np.eye(4)
    t = node.get('translation', [0, 0, 0])
    r = node.get('rotation', [0, 0, 0, 1])  # xyzw
    s = node.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
    M[:3, :3] = R @ np.diag(s)
    M[:3, 3] = t
    return M

def walk(node_idx, parent, collect):
    node = j['nodes'][node_idx]
    M = parent @ node_matrix(node)
    if 'mesh' in node:
        collect.append((node.get('name', f'mesh{node["mesh"]}'), M, node['mesh']))
    for c in node.get('children', []):
        walk(c, M, collect)

scene = j['scenes'][j.get('scene', 0)]
items = []
for root in scene['nodes']:
    walk(root, np.eye(4), items)

print(f'\nEscena: {len(items)} nodos con malla\n')
SCALE = 0.026
GY = -2.9
allpts = []
for name, M, mi in items:
    mesh = j['meshes'][mi]
    pts = []
    for prim in mesh['primitives']:
        pa = prim['attributes']['POSITION']
        p = read_acc(pa)
        w = np.hstack([p, np.ones((len(p), 1))]) @ M.T
        pts.append(w[:, :3])
    P = np.vstack(pts)
    mn, mx = P.min(0), P.max(0)
    print(f'· {name}: n={len(P):6d}  escena y[{mn[1]:8.3f},{mx[1]:8.3f}] x[{mn[0]:7.3f},{mx[0]:7.3f}] z[{mn[2]:7.3f},{mx[2]:7.3f}]')
    print(f'   montura y[{mn[1]*SCALE - GY*SCALE:8.4f},{mx[1]*SCALE - GY*SCALE:8.4f}] '
          f'x[{mn[0]*SCALE:7.4f},{mx[0]*SCALE:7.4f}] z[{mn[2]*SCALE:7.4f},{mx[2]*SCALE:7.4f}]  (m)')
    allpts.append(P)

A = np.vstack(allpts)
mn, mx = A.min(0), A.max(0)
print(f'\nTOTAL escena: y[{mn[1]:.3f},{mx[1]:.3f}]  -> montura y[{mn[1]*SCALE-GY*SCALE:.4f},{mx[1]*SCALE-GY*SCALE:.4f}]')
print(f'BLADE_Y montura (const juego) = {(2.1115-GY)*SCALE:.4f}')
print(f'bladeCenterUp colisionador    = 0.1400')

# handle: puntos por debajo del borde inferior de la hoja
# hoja = la malla más grande; tomamos puntos con montura_y < 0.02 (bajo el agarre estimado)
mys = A[:, 1] * SCALE - GY * SCALE
low = A[mys < 0.02]
if len(low):
    lmn, lmx = low.min(0), low.max(0)
    cy = (lmn[1] + lmx[1]) / 2 * SCALE - GY * SCALE
    print(f'\nMANGO (montura y<0.02): y[{lmn[1]*SCALE-GY*SCALE:.4f},{lmx[1]*SCALE-GY*SCALE:.4f}] '
          f'x[{lmn[0]*SCALE:.4f},{lmx[0]*SCALE:.4f}] z[{lmn[2]*SCALE:.4f},{lmx[2]*SCALE:.4f}] centro_y={cy:.4f}')
    xs = low[:, 0] * SCALE; zs = low[:, 2] * SCALE
    print(f'   centro xz del mango: ({(xs.min()+xs.max())/2:.4f}, {(zs.min()+zs.max())/2:.4f})  radio_xz≈{(xs.max()-xs.min())/2:.4f}×{(zs.max()-zs.min())/2:.4f}')

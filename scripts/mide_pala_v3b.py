#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análisis fino: centro del mango por franjas + caras de la hoja (montura)."""
import base64, json, re, struct
import numpy as np

SRC = '/home/z/my-project/public/game.html'
s = open(SRC, encoding='utf-8').read()
m = re.search(r"const PALA_GLB_B64 = '([A-Za-z0-9+/=]+)'", s)
glb = base64.b64decode(m.group(1))
clen, _ = struct.unpack('<II', glb[12:20])
j = json.loads(glb[20:20 + clen])
bin_off = 20 + clen
blen, _ = struct.unpack('<II', glb[bin_off:bin_off + 8])
BIN = glb[bin_off + 8: bin_off + 8 + blen]
CT = {5120: 'i1', 5121: 'u1', 5122: 'i2', 5123: 'u2', 5125: 'u4', 5126: 'f4'}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def read_acc(idx):
    a = j['accessors'][idx]
    bv = j['bufferViews'][a['bufferView']]
    n = NC[a['type']]
    dt = np.dtype(CT[a['componentType']]).newbyteorder('<')
    stride = bv.get('byteStride') or (n * dt.itemsize)
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    out = np.zeros((a['count'], n))
    for i in range(a['count']):
        out[i] = np.frombuffer(BIN, dtype=dt, count=n, offset=off + i * stride)
    return out

def node_matrix(node):
    if 'matrix' in node:
        return np.array(node['matrix']).reshape(4, 4).T
    M = np.eye(4)
    t = node.get('translation', [0, 0, 0]); r = node.get('rotation', [0, 0, 0, 1]); sc = node.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    M[:3, :3] = R @ np.diag(sc); M[:3, 3] = t
    return M

def walk(i, P, col):
    n = j['nodes'][i]; M = P @ node_matrix(n)
    if 'mesh' in n: col.append((M, n['mesh']))
    for c in n.get('children', []): walk(c, M, col)

col = []
for r in j['scenes'][j.get('scene', 0)]['nodes']: walk(r, np.eye(4), col)

S = 0.026; GY = -2.9
mounts = []
for M, mi in col:
    for prim in j['meshes'][mi]['primitives']:
        p = read_acc(prim['attributes']['POSITION'])
        w = np.hstack([p, np.ones((len(p), 1))]) @ M.T
        mounts.append(w[:, :3] * np.array([S, S, S]) + np.array([0, -GY * S, 0]))

print('=== MANGO: centro por franjas de Y (montura, m) — mallas gruesa y placa ===')
H = np.vstack([mounts[k] for k in (2, 4)])
for lo in np.arange(-0.05, 0.08, 0.01):
    sel = H[(H[:, 1] >= lo) & (H[:, 1] < lo + 0.01)]
    if len(sel) < 4: continue
    cx = (sel[:, 0].min() + sel[:, 0].max()) / 2
    cz = (sel[:, 2].min() + sel[:, 2].max()) / 2
    print(f'y[{lo:+.2f},{lo+0.01:+.2f}] n={len(sel):4d}  x[{sel[:,0].min():+.4f},{sel[:,0].max():+.4f}] c={cx:+.4f}   z[{sel[:,2].min():+.4f},{sel[:,2].max():+.4f}] c={cz:+.4f}')

print('\n=== HOJA: extents por malla (montura) ===')
for k in (0, 1, 3):
    B = mounts[k]
    print(f'malla{k}: y[{B[:,1].min():.4f},{B[:,1].max():.4f}] x[{B[:,0].min():+.4f},{B[:,0].max():+.4f}] z[{B[:,2].min():+.4f},{B[:,2].max():+.4f}]')

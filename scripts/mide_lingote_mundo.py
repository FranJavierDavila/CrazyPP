#!/usr/bin/env python3
"""Replica EXACTO del Box3.setFromObject() del módulo: recorre la jerarquía
de nodos del GLB aplicando TRS (T*R*S) y computa el bbox en espacio-mundo
del root — lo que realmente ve el juego tras la normalización a 0,17."""
import json
import math
import struct

p = '/home/z/my-project/public/championships/oeste/assets/lowpoly_gold_bar.glb'
data = open(p, 'rb').read()
clen, ctype = struct.unpack_from('<II', data, 12)
js = json.loads(data[20:20 + clen])

# bbox LOCAL de cada mesh (min/max de sus POSITION accessors)
def acc_bbox(ai):
    acc = js['accessors'][ai]
    return acc['min'], acc['max']

def quat_mat(q):
    x, y, z, w = q
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]

def node_mat(n):
    if 'matrix' in n:
        m = n['matrix']  # column-major
        return [[m[0], m[4], m[8], m[12]],
                [m[1], m[5], m[9], m[13]],
                [m[2], m[6], m[10], m[14]],
                [m[3], m[7], m[11], m[15]]]
    t = n.get('translation', [0, 0, 0])
    r = quat_mat(n.get('rotation', [0, 0, 0, 1]))
    s = n.get('scale', [1, 1, 1])
    m3 = [[r[i][j] * s[j] for j in range(3)] + [t[i]] for i in range(3)]
    return m3 + [[0, 0, 0, 1]]

def mul(a, b):  # a*b (4x4, columnas como filas de listas)
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]

def xform(m, p):
    return [sum(m[i][k] * p[k] for k in range(3)) + m[i][3] for i in range(3)]

gmin, gmax = [1e9] * 3, [-1e9] * 3
def walk(ni, pm):
    global gmin, gmax
    n = js['nodes'][ni]
    m = mul(pm, node_mat(n))
    if 'mesh' in n:
        for prim in js['meshes'][n['mesh']]['primitives']:
            if 'POSITION' in prim.get('attributes', {}):
                mn, mx = acc_bbox(prim['attributes']['POSITION'])
                for x in (mn[0], mx[0]):
                    for y in (mn[1], mx[1]):
                        for z in (mn[2], mx[2]):
                            w = xform(m, [x, y, z])
                            for i in range(3):
                                gmin[i] = min(gmin[i], w[i])
                                gmax[i] = max(gmax[i], w[i])
    for c in n.get('children', []):
        walk(c, m)

ID = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
for s in js['scenes'][js.get('scene', 0)]['nodes']:
    walk(s, ID)

ext = [gmax[i] - gmin[i] for i in range(3)]
mx = max(ext)
sc = 0.17 / mx
print('bbox MUNDO (como lo ve three):', ['%.4f' % e for e in ext])
print('normalizado a 0,17          :', ['%.4f' % (e * sc) for e in ext])
print('→ largo %.3f · alto %.3f · fondo %.3f' % (ext[0] * sc, ext[1] * sc, ext[2] * sc))
print('capa real (alto+1,5mm)      : %.4f' % (ext[1] * sc + 0.0015))
print('hueco columnas sepX 0.19    : %.4f' % (0.19 - ext[0] * sc))
print('hueco filas     sepZ 0.095  : %.4f' % (0.095 - ext[2] * sc))

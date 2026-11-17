#!/usr/bin/env python3
"""V3.0.3 · Genera la pala PRO CARBON como GLB externo (assets/pala/pala_pro.glb).

La piel «Pro Carbon» del PRO TRAINING sustituye el MODELO 3D de la pala por
este archivo. Se construye en las MISMAS convenciones nativas que el GLB
incrustado de la pala clásica (medido con scripts/mide_pala_v3.py):

  · punto de agarre   y = -2.9
  · centro de hoja    y = +2.1115   (PALA_BLADE_Y)
  · hoja              elipse rx 2.92 / ry 3.05, grosor z ±0.19
  · mango             y -0.85 .. -4.85, anatómico (ensanchamiento en el flap)

UV: cara superior → goma ROJA con pips (cuadrante sup-izq de la textura),
cara inferior → goma NEGRA con pips (cuadrante sup-der), canto + mango →
fibra de carbono (mitad inferior). Todo en UNA imagen PNG de 1024².

Salida: GLB binario (JSON chunk + BIN chunk + image/png embebida).
"""
import json
import math
import struct
import zlib

OUT = '/home/z/my-project/public/assets/pala/pala_pro.glb'

# ---------------------------------------------------------------- textura --
S = 1024
px = bytearray(S * S * 3)


def put(x, y, r, g, b):
    if 0 <= x < S and 0 <= y < S:
        i = (y * S + x) * 3
        px[i] = r; px[i + 1] = g; px[i + 2] = b


def fill_rect(x0, y0, w, h, c):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put(x, y, *c)


def fill_circle(cx, cy, rad, c):
    for y in range(int(cy - rad), int(cy + rad) + 1):
        for x in range(int(cx - rad), int(cx + rad) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad:
                put(x, y, *c)


def pips(cx, cy, rad, base, hi, lo, emboss=False):
    """Goma con pips en relieve (cuadrícula hexagonal con gradiente)."""
    fill_circle(cx, cy, rad, base)
    step, r = 24, 8
    row = 0
    y = cy - rad + step
    while y < cy + rad:
        x0 = cx - rad + step + (step // 2 if row % 2 else 0)
        x = x0
        while x < cx + rad:
            d = math.hypot(x - cx, y - cy)
            if d < rad - r - 2:
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        dd = math.hypot(dx, dy)
                        if dd <= r:
                            if emboss:      # pips grabados (oro): anillo
                                t = dd / r
                                c = lo if t > 0.72 else (hi if t < 0.2 else base)
                            else:           # pips en relieve con luz arriba-izq
                                t = max(0.0, min(1.0, (dd / r) * 1.15 + (dx + dy) / (r * 4.5)))
                                if t < 0.35:
                                    c = hi
                                elif t < 0.85:
                                    c = base
                                else:
                                    c = lo
                            put(x + dx, y + dy, *c)
            x += step
        y += step
        row += 1


def carbon(y0, y1):
    """Sarga 2×2 de fibra de carbono."""
    t = 32
    for y in range(y0, y1):
        for x in range(0, S):
            horiz = ((x // t) + (y // t)) % 2 == 0
            fy = (y % t) / t
            fx = (x % t) / t
            v = fx if horiz else fy
            if v < 0.15:
                c = (58, 64, 78)
            elif v < 0.5:
                c = (36, 40, 50)
            elif v < 0.62:
                c = (24, 27, 34)
            else:
                c = (44, 49, 60)
            if (x % t in (8, 9) and horiz) or (y % t in (8, 9) and not horiz):
                c = (min(255, c[0] + 26), min(255, c[1] + 28), min(255, c[2] + 34))
            put(x, y, *c)


fill_rect(0, 0, S, S, (30, 32, 38))                    # espacio UV sin usar
pips(256, 256, 244, (176, 34, 34), (216, 74, 74), (110, 16, 16))          # goma roja
pips(768, 256, 244, (23, 24, 26), (58, 63, 71), (0, 0, 0))                # goma negra
carbon(512, S)                                          # canto + mango

# PNG (RGB8, sin filtros)
raw = b''.join(b'\x00' + bytes(px[y * S * 3:(y + 1) * S * 3]) for y in range(S))


def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data +
            struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))


png = (b'\x89PNG\r\n\x1a\n' +
       chunk(b'IHDR', struct.pack('>IIBBBBB', S, S, 8, 2, 0, 0, 0)) +
       chunk(b'IDAT', zlib.compress(raw, 9)) +
       chunk(b'IEND', b''))
print('PNG textura:', len(png), 'B')

# ---------------------------------------------------------------- geometría --
CX, CY, RX, RY, HZ = 0.0, 2.1115, 2.92, 3.05, 0.19
SEG = 64

pos, nor, uv, idx = [], [], [], []

# --- cara superior (z +HZ, normal +Z, UV goma roja)
top0 = len(pos)
pos.append((0.0, CY, HZ)); nor.append((0.0, 0.0, 1.0)); uv.append((0.25, 0.25))
for k in range(SEG + 1):
    a = 2 * math.pi * k / SEG
    x, y = RX * math.cos(a), CY + RY * math.sin(a)
    pos.append((x, y, HZ)); nor.append((0.0, 0.0, 1.0))
    uv.append((0.25 + math.cos(a) * 0.225, 0.25 + math.sin(a) * 0.225))
for k in range(1, SEG + 1):
    idx += [top0, top0 + k, top0 + k + 1]          # CCW visto desde +Z

# --- cara inferior (z -HZ, normal -Z, UV goma negra)
bot0 = len(pos)
pos.append((0.0, CY, -HZ)); nor.append((0.0, 0.0, -1.0)); uv.append((0.75, 0.25))
for k in range(SEG + 1):
    a = 2 * math.pi * k / SEG
    x, y = RX * math.cos(a), CY + RY * math.sin(a)
    pos.append((x, y, -HZ)); nor.append((0.0, 0.0, -1.0))
    uv.append((0.75 + math.cos(a) * 0.225, 0.25 + math.sin(a) * 0.225))
for k in range(1, SEG + 1):
    idx += [bot0, bot0 + k + 1, bot0 + k]          # CW visto desde +Z = CCW desde -Z

# --- canto (banda entre los dos bordes, UV carbono)
rim0 = len(pos)
for k in range(SEG + 1):
    a = 2 * math.pi * k / SEG
    nx, ny = math.cos(a) / RX, math.sin(a) / RY
    nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
    x, y = RX * math.cos(a), CY + RY * math.sin(a)
    pos.append((x, y, HZ));  nor.append((nx, ny, 0.0)); uv.append((k / SEG, 0.535))
for k in range(SEG + 1):
    a = 2 * math.pi * k / SEG
    nx, ny = math.cos(a) / RX, math.sin(a) / RY
    nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
    x, y = RX * math.cos(a), CY + RY * math.sin(a)
    pos.append((x, y, -HZ)); nor.append((nx, ny, 0.0)); uv.append((k / SEG, 0.60))
for k in range(SEG):
    a0, b0, a1, b1 = rim0 + k, rim0 + k + 1, rim0 + SEG + 1 + k, rim0 + SEG + 1 + k + 1
    idx += [a0, a1, b0, b0, a1, b1]   # CCW visto desde fuera (glTF front-face)

blade_count = len(pos)
print('vértices hoja+canto:', blade_count, '· índices:', len(idx))

# --- mango anatómico (secciones redondeadas a lo largo de Y, UV carbono)
stations = [   # (y, semiancho x, semigrueso z)
    (-0.86, 1.34, 0.36),
    (-2.00, 1.16, 0.33),
    (-3.20, 1.30, 0.34),
    (-4.05, 1.62, 0.36),
    (-4.85, 1.48, 0.33),
]
SEC = 16
h0 = len(pos)
for si, (sy, sw, sd) in enumerate(stations):
    for k in range(SEC):
        a = 2 * math.pi * k / SEC
        c, s = math.cos(a), math.sin(a)
        # rectángulo redondeado (superelipse suave p=0.72)
        x = sw * math.copysign(abs(c) ** 0.72, c)
        z = sd * math.copysign(abs(s) ** 0.72, s)
        nx = math.copysign(abs(c) ** 0.45, c)
        nz = math.copysign(abs(s) ** 0.45, s)
        nl = math.hypot(nx, nz) or 1.0
        v = 0.66 + (si / (len(stations) - 1)) * 0.30
        pos.append((x, sy, z)); nor.append((nx / nl, 0.0, nz / nl))
        uv.append((k / SEC, v))
NS = len(stations)
for si in range(NS - 1):
    for k in range(SEC):
        k2 = (k + 1) % SEC
        a0 = h0 + si * SEC + k
        b0 = h0 + si * SEC + k2
        a1 = h0 + (si + 1) * SEC + k
        b1 = h0 + (si + 1) * SEC + k2
        idx += [a0, b0, a1, b0, b1, a1]   # CCW visto desde fuera (glTF front-face)
print('vértices totales:', len(pos), '· índices totales:', len(idx))

carbon_idx_start = blade_count * 4  # (no usado; los índices se parten por conteo)

# ------------------------------------------------------------- empaquetado --
idx_blade = idx[: (SEG * 3) * 2 + SEG * 6]          # 2 abanicos + banda del canto
idx_carbon = idx[len(idx_blade):]
print('índices hoja:', len(idx_blade), '· índices carbono:', len(idx_carbon))

pos_b = b''.join(struct.pack('<fff', *p) for p in pos)
nor_b = b''.join(struct.pack('<fff', *n) for n in nor)
uv_b = b''.join(struct.pack('<ff', *t) for t in uv)
ib_b = b''.join(struct.pack('<H', i) for i in idx_blade)
ic_b = b''.join(struct.pack('<H', i) for i in idx_carbon)

buffers = [pos_b, nor_b, uv_b, ib_b, ic_b, png]
views = []
off = 0
for b in buffers:
    pad = (4 - off % 4) % 4
    off += pad
    views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(b)})
    off += len(b)
while off % 4:
    off += 1  # el BIN se rellena a 4

blob = b''
for i, b in enumerate(buffers):
    blob += b'\x00' * ((4 - len(blob) % 4) % 4)
    assert len(blob) == views[i]['byteOffset'], (i, len(blob), views[i])
    blob += b
while len(blob) % 4:
    blob += b'\x00'

img_view = len(views) - 1
gl = {
    'asset': {'version': '2.0', 'generator': 'crazypp-pro-paddle V3.0.3'},
    'scene': 0,
    'scenes': [{'nodes': [0]}],
    'nodes': [
        {'name': 'PalaPro', 'children': [1, 2]},
        {'name': 'goma', 'mesh': 0},
        {'name': 'carbono', 'mesh': 1},
    ],
    'meshes': [
        {'name': 'goma', 'primitives': [{
            'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2},
            'indices': 3, 'material': 0}]},
        {'name': 'carbono', 'primitives': [{
            'attributes': {'POSITION': 0, 'NORMAL': 1, 'TEXCOORD_0': 2},
            'indices': 4, 'material': 1}]},
    ],
    'materials': [
        {'name': 'rubber_pro', 'pbrMetallicRoughness': {
            'baseColorTexture': {'index': 0}, 'metallicFactor': 0.05, 'roughnessFactor': 0.85}},
        {'name': 'carbon_pro', 'pbrMetallicRoughness': {
            'baseColorTexture': {'index': 0}, 'metallicFactor': 0.30, 'roughnessFactor': 0.55}},
    ],
    'textures': [{'sampler': 0, 'source': 0}],
    'images': [{'bufferView': img_view, 'mimeType': 'image/png'}],
    'samplers': [{'wrapS': 10497, 'wrapT': 10497, 'magFilter': 9729, 'minFilter': 9987}],
    'accessors': [
        {'bufferView': 0, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3',
         'min': [min(p[i] for p in pos) for i in range(3)],
         'max': [max(p[i] for p in pos) for i in range(3)]},
        {'bufferView': 1, 'componentType': 5126, 'count': len(nor), 'type': 'VEC3'},
        {'bufferView': 2, 'componentType': 5126, 'count': len(uv), 'type': 'VEC2'},
        {'bufferView': 3, 'componentType': 5123, 'count': len(idx_blade), 'type': 'SCALAR'},
        {'bufferView': 4, 'componentType': 5123, 'count': len(idx_carbon), 'type': 'SCALAR'},
    ],
    'bufferViews': views,
    'buffers': [{'byteLength': len(blob)}],
}
json_b = json.dumps(gl, separators=(',', ':')).encode()
json_b += b' ' * ((4 - len(json_b) % 4) % 4)

glb = (struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(json_b) + 8 + len(blob)) +
       struct.pack('<II', len(json_b), 0x4E4F534A) + json_b +
       struct.pack('<II', len(blob), 0x004E4942) + blob)

import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(glb)
print('GLB escrito:', OUT, len(glb), 'B')

# ------------------------------------------------------------- verificación --
raw2 = open(OUT, 'rb').read()
magic, ver, ln = struct.unpack('<III', raw2[:12])
assert magic == 0x46546C67 and ln == len(raw2), 'cabecera GLB inválida'
jl, jt = struct.unpack('<II', raw2[12:20])
g2 = json.loads(raw2[20:20 + jl])
n_idx = sum(a['count'] for a in g2['accessors'] if a['type'] == 'SCALAR')
n_vtx = g2['accessors'][0]['count']
print(f'PARSE OK · meshes={len(g2["meshes"])} · vértices={n_vtx} · índices={n_idx} '
      f'· max_idx={max(idx)} (< {n_vtx} ✓)')
assert max(idx) < n_vtx, 'índice fuera de rango'

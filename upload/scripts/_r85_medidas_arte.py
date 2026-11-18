#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r85 · mediciones del arte del dueño para el Campeonato de Halloween:
   1) overlay de nodos estimados sobre Mapa.png (verificación visual)
   2) hueco interior del cartel zombi_normas.png (rect para NORMAS_SKIN)
   3) alfa de las esquinas de las 12 poses (regla de oro)
   4) pesos del arte provisional del valle (bso)"""
from PIL import Image, ImageDraw
import zipfile, io, os

RAIZ = '/home/z/my-project'

# --- 1) OVERLAY DE NODOS --------------------------------------------------
MAPA = os.path.join(RAIZ, 'upload', 'Mapa.png')
im = Image.open(MAPA).convert('RGB')
W, H = im.size
NODOS = [
    (1, 148, 390, 118),
    (2, 355, 592, 108),
    (3, 875, 202, 112),
    (4, 890, 556, 102),
    (5, 1265, 332, 118),
]
ov = im.copy()
d = ImageDraw.Draw(ov)
for n, x, y, r in NODOS:
    d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 0, 96), width=6)
    d.text((x - 10, y - 22), str(n), fill=(255, 0, 96))
ov.save('/tmp/nodos_overlay.png')
print('overlay /tmp/nodos_overlay.png', ov.size)

# --- 2) HUECO DEL CARTEL ---------------------------------------------------
CAR = os.path.join(RAIZ, 'upload', 'zombi_normas.png')
c = Image.open(CAR).convert('L')
cw, ch = c.size
px = c.load()
# mapa de brillo 16x8: el hueco central es oscuro
BX, BY = 16, 8
grid = []
for gy in range(BY):
    fila = ''
    for gx in range(BX):
        x0, x1 = int(gx * cw / BX), int((gx + 1) * cw / BX)
        y0, y1 = int(gy * ch / BY), int((gy + 1) * ch / BY)
        s = n = 0
        for yy in range(y0, y1, 4):
            for xx in range(x0, x1, 4):
                s += px[xx, yy]; n += 1
        v = s // max(1, n)
        fila += '#' if v < 60 else ('+' if v < 110 else ('.' if v < 170 else ' '))
    grid.append(fila)
print('brillo zombi_normas 16x8 (# oscuro):')
for f in grid:
    print('  ' + f)

# --- 3) ESQUEMAS ALFA DE LAS POSES ----------------------------------------
z = zipfile.ZipFile(os.path.join(RAIZ, 'upload', 'zombi.zip'))
print('esquinas alfa (rgba):')
for n in sorted(z.namelist()):
    img = Image.open(io.BytesIO(z.read(n))).convert('RGBA')
    w, h = img.size
    esq = [img.getpixel(p)[3] for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    print(f'  {n}: esquinas={esq}')

# --- 4) PESOS PROVISIONALES ------------------------------------------------
v = os.path.join(RAIZ, 'public', 'championships', 'valle_neon', 'assets')
for f in ['bso.wav', 'sala_floor.jpg', 'sala_back.jpg', 'decor1.png', 'decor2.png']:
    p = os.path.join(v, f)
    print(f'valle/{f}: {os.path.getsize(p) if os.path.exists(p) else "NO"} B')
r = os.path.join(RAIZ, 'upload', 'Risas.mp3')
print('upload/Risas.mp3:', os.path.getsize(r), 'B')

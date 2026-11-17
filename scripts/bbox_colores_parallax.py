#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BBox opaco por pieza (para escalar por CONTENIDO) + colores del llano p1."""
import os, json
from PIL import Image

D = '/home/z/my-project/game/championships/oeste/assets/parallax'

print('=== BBOX DE PIEZAS (fracciones del canvas) ===')
for f in sorted(os.listdir(D)):
    if not f.endswith('.png') or f.startswith('p1'):
        continue
    im = Image.open(os.path.join(D, f)).convert('RGBA')
    w, h = im.size
    a = im.getchannel('A').resize((128, 128))
    px = a.load()
    xs, ys = [], []
    for y in range(128):
        for x in range(128):
            if px[x, y] > 100:
                xs.append(x); ys.append(y)
    if not xs:
        print(f'{f}: VACIO'); continue
    bbL, bbR = min(xs) / 128, max(xs) / 128
    bbT, bbB = min(ys) / 128, max(ys) / 128
    print(f"{f}: bbW={bbR-bbL:.2f} bbH={bbB-bbT:.2f} top={bbT:.2f} bot={bbB:.2f} aspecto_cont={(bbR-bbL)/max(0.01,(bbB-bbT)):.2f}")

print()
print('=== COLORES DEL LLANO p1 (media RGB por franja, bajo el horizonte) ===')
for f in ['p1_paisajedesierto1.png', 'p1_paisajedesierto2.png']:
    im = Image.open(os.path.join(D, f)).convert('RGBA')
    w, h = im.size
    px = im.load()
    def franja(y0f, y1f):
        r = g = b = n = 0
        for y in range(int(h * y0f), int(h * y1f), 4):
            for x in range(0, w, 8):
                pr, pg, pb, pa = px[x, y]
                if pa > 200:
                    r += pr; g += pg; b += pb; n += 1
        return (r // n, g // n, b // n) if n else None
    print(f'{f}:')
    print(f'  horizonte-montanas(0.50-0.62): {franja(0.50, 0.62)}')
    print(f'  llano-superior   (0.66-0.75): {franja(0.66, 0.75)}')
    print(f'  llano-medio      (0.78-0.88): {franja(0.78, 0.88)}')
    print(f'  llano-inferior   (0.90-1.00): {franja(0.90, 1.00)}')
    # color del cielo justo encima de las montanas mas altas (bruma superior)
    print(f'  bruma-sobre-montanas (0.36-0.43): {franja(0.36, 0.43)}')

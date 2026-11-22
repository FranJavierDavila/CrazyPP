#!/usr/bin/env python3
"""V2.137 — Medición de nodos del MAPA WIZARD nuevo (upload/Mapa.png 1380×752).
Detecta los anillos dorados por color, calcula centros/radios y pinta una
rejilla de verificación con las detecciones para comprobarlas a ojo."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SRC = '/home/z/my-project/upload/Mapa.png'
OUT = '/home/z/my-project/scripts/wizard_mapa_grid.png'

img = Image.open(SRC).convert('RGB')
W, H = img.size
a = np.asarray(img).astype(np.int16)
R, G, B = a[..., 0], a[..., 1], a[..., 2]

# --- máscara de ORO (anillo dorado: R alto, G medio, B bajo) ---
gold = (R > 150) & (G > 90) & (G < 215) & (B < 120) & (R > G + 25) & (G > B + 20)
lab, n = ndimage.label(gold)
print(f'componentes dorados: {n}')
objs = ndimage.find_objects(lab)
sizes = ndimage.sum(gold, lab, range(1, n + 1))

cands = []
for i, sl in enumerate(objs):
    sz = sizes[i]
    if sz < 4000:          # los anillos son gruesos: miles de px
        continue
    ys, xs = np.where(lab[sl] == i + 1)
    ys = ys + sl[0].start; xs = xs + sl[1].start
    h = ys.max() - ys.min() + 1
    w = xs.max() - xs.min() + 1
    # anillo ≈ componente con hueco: bbox cuadrado-ish y tamaño grande
    cx = float(xs.mean()); cy = float(ys.mean())
    cands.append(dict(cx=cx, cy=cy, w=w, h=h, sz=int(sz),
                      x0=int(xs.min()), x1=int(xs.max()),
                      y0=int(ys.min()), y1=int(ys.max())))

cands.sort(key=lambda c: -c['sz'])
print('\nTop componentes (cx, cy, w×h, px):')
for c in cands[:12]:
    print(f"  ({c['cx']:7.1f},{c['cy']:7.1f})  {c['w']}×{c['h']}  {c['sz']}")

# --- rejilla de verificación ---
g = img.copy()
d = ImageDraw.Draw(g)
for x in range(0, W, 50):
    col = (255, 0, 255) if x % 100 == 0 else (120, 60, 120)
    d.line([(x, 0), (x, H)], fill=col, width=2 if x % 100 == 0 else 1)
    if x % 100 == 0:
        d.text((x + 3, 3), str(x), fill=(255, 255, 0))
for y in range(0, H, 50):
    col = (255, 0, 255) if y % 100 == 0 else (120, 60, 120)
    d.line([(0, y), (W, y)], fill=col, width=2 if y % 100 == 0 else 1)
    if y % 100 == 0:
        d.text((3, y + 3), str(y), fill=(255, 255, 0))
g.save(OUT)
print(f'\nrejilla → {OUT}  ({W}×{H})')

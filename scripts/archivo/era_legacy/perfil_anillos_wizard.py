#!/usr/bin/env python3
"""V2.137 — perfiles radiales del anillo dorado por nodo + crop del nodo 5."""
import cv2
import numpy as np
from PIL import Image

SRC = '/home/z/my-project/upload/Mapa.png'
img = cv2.imread(SRC)
b, g, r = img[..., 0].astype(np.int16), img[..., 1].astype(np.int16), img[..., 2].astype(np.int16)
# BGR → oro: R alto, G medio, B bajo
gold = (r > 150) & (g > 90) & (g < 215) & (b < 120) & (r > g + 25) & (g > b + 20)

NODOS = {1: (229, 255), 2: (453, 514), 3: (699, 256), 4: (963, 511)}
for k, (cx, cy) in NODOS.items():
    hits = []
    for ang in np.linspace(0, 2 * np.pi, 720, endpoint=False):
        dx, dy = np.cos(ang), np.sin(ang)
        rr = np.arange(60, 180)
        xs = np.clip((cx + rr * dx).astype(int), 0, 1379)
        ys = np.clip((cy + rr * dy).astype(int), 0, 751)
        m = gold[ys, xs]
        if m.any():
            idx = np.where(m)[0]
            # tramo continuo más largo
            splits = np.split(idx, np.where(np.diff(idx) > 3)[0] + 1)
            seg = max(splits, key=len)
            if len(seg) >= 4:
                hits.append(rr[seg[0]] + rr[seg[-1]])  # media de interior/exterior
    if hits:
        h = np.array(hits)
        print(f'nodo {k}: centro=({cx},{cy})  banda media r = {h.mean():.1f}  '
              f'(p10={np.percentile(h,10):.0f} p90={np.percentile(h,90):.0f}, n={len(h)})')
    else:
        print(f'nodo {k}: sin banda')

# recorte del nodo 5 con rejilla fina de 25 px
im = Image.open(SRC).convert('RGB')
crop = im.crop((1050, 0, 1380, 330)).resize((660, 660), Image.LANCZOS)
d = ImageDraw__ = None
from PIL import ImageDraw
d = ImageDraw.Draw(crop)
# rejilla: cada 25 px originales = 50 px escalados; etiquetas = coords originales
for ox in range(1050, 1381, 25):
    sx = (ox - 1050) * 2
    d.line([(sx, 0), (sx, 660)], fill=(255, 0, 255) if ox % 50 == 0 else (130, 70, 130), width=2 if ox % 50 == 0 else 1)
    if ox % 50 == 0:
        d.text((sx + 2, 2), str(ox), fill=(255, 255, 0))
for oy in range(0, 331, 25):
    sy = oy * 2
    d.line([(0, sy), (660, sy)], fill=(255, 0, 255) if oy % 50 == 0 else (130, 70, 130), width=2 if oy % 50 == 0 else 1)
    if oy % 50 == 0:
        d.text((2, sy + 2), str(oy), fill=(255, 255, 0))
crop.save('/home/z/my-project/scripts/nodo5_crop.png')
print('crop nodo 5 → scripts/nodo5_crop.png')

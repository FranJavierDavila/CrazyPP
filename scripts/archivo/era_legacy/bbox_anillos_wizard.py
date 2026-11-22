#!/usr/bin/env python3
"""V2.137 — bbox dorado por ventanas por nodo (excluye espiral numerada)."""
import numpy as np
from PIL import Image

img = np.asarray(Image.open('/home/z/my-project/upload/Mapa.png').convert('RGB')).astype(np.int16)
R, G, B = img[..., 0], img[..., 1], img[..., 2]
gold = (R > 150) & (G > 90) & (G < 215) & (B < 120) & (R > G + 25) & (G > B + 20)

# ventanas (x0,y0,x1,y1) que contienen SOLO el anillo de cada nodo
VENT = {1: (95, 130, 360, 410), 2: (330, 370, 645, 690), 3: (565, 120, 845, 400),
        4: (840, 365, 1130, 690)}
for k, (x0, y0, x1, y1) in VENT.items():
    m = gold[y0:y1, x0:x1]
    ys, xs = np.where(m)
    X0, X1 = xs.min() + x0, xs.max() + x0
    Y0, Y1 = ys.min() + y0, ys.max() + y0
    cx = (X0 + X1) / 2; cy = (Y0 + Y1) / 2
    rx = (X1 - X0) / 2; ry = (Y1 - Y0) / 2
    print(f'nodo {k}: bbox x[{X0}..{X1}] y[{Y0}..{Y1}] → centro ({cx:.0f},{cy:.0f}) '
          f'r=({rx:.0f},{ry:.0f})')

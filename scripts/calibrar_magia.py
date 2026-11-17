#!/usr/bin/env python3
"""V2.137 — calibración: bandas del mapa VIEJO del mago + círculo de tapa.webp."""
import numpy as np
from PIL import Image

VIEJO = '/home/z/my-project/public/championships/magia/assets/mapa.webp'
img = Image.open(VIEJO).convert('RGB')
a = np.asarray(img).astype(np.int16)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
gold = (R > 150) & (G > 90) & (G < 215) & (B < 120) & (R > G + 25) & (G > B + 20)

OLD = {1: (235, 265, 120), 2: (438, 503, 145), 3: (690, 262, 120),
       4: (934, 503, 145), 5: (1216, 178, 120)}
H, W = gold.shape
for k, (cx, cy, rmod) in OLD.items():
    hits = []
    for ang in np.linspace(0, 2 * np.pi, 720, endpoint=False):
        dx, dy = np.cos(ang), np.sin(ang)
        rr = np.arange(60, 190)
        xs = np.clip((cx + rr * dx).astype(int), 0, W - 1)
        ys = np.clip((cy + rr * dy).astype(int), 0, H - 1)
        m = gold[ys, xs]
        if m.any():
            idx = np.where(m)[0]
            splits = np.split(idx, np.where(np.diff(idx) > 3)[0] + 1)
            seg = max(splits, key=len)
            if len(seg) >= 4:
                hits.append((rr[seg[0]] + rr[seg[-1]]) / 2)
    h = np.array(hits)
    print(f'nodo {k} (r={rmod}): banda media = {h.mean():.1f}  → r/107.5 escala '
          f'= {rmod/107.5:.3f} · banda/escala = {h.mean()/(rmod/107.5):.1f}')

# círculo dibujado dentro de tapa.webp (fracción del canvas que ocupa el medallón)
t = np.asarray(Image.open('/home/z/my-project/public/championships/magia/assets/tapa.webp').convert('RGBA'))
alpha = t[..., 3] > 128
ys, xs = np.where(alpha)
tw, th = t.shape[1], t.shape[0]
print(f'\ntapa.webp {tw}×{th}: opaco x[{xs.min()}..{xs.max()}] y[{ys.min()}..{ys.max()}]'
      f'  → diám. ≈ {xs.max()-xs.min()+1}×{ys.max()-ys.min()+1} '
      f'({(xs.max()-xs.min()+1)/tw:.2f} ancho, {(ys.max()-ys.min()+1)/th:.2f} alto)')

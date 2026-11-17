#!/usr/bin/env python3
"""Measure content bboxes of sheriff house art (old vs new) + green zone line."""
from PIL import Image
import numpy as np

def bbox_alpha(path):
    im = Image.open(path).convert('RGBA')
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 16)
    if len(ys) == 0:
        return None
    H, W = a.shape
    return dict(w=W, h=H, x0=int(xs.min()), x1=int(xs.max()),
                y0=int(ys.min()), y1=int(ys.max()),
                v_bottom=round(1 - ys.max() / H, 4),
                v_top=round(1 - ys.min() / H, 4))

def green_line(path):
    im = Image.open(path).convert('RGB')
    a = np.array(im).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mask = (g > 150) & (r < 130) & (b < 130) & (g - r > 60) & (g - b > 60)
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    H, W = mask.shape
    return dict(x0=int(xs.min()), x1=int(xs.max()),
                y0=int(ys.min()), y1=int(ys.max()),
                v_center=round(1 - (ys.min() + ys.max()) / 2 / H, 4),
                u0=round(xs.min() / W, 4), u1=round(xs.max() / W, 4),
                npix=int(len(ys)))

G = '/home/z/my-project/game/championships/oeste/assets/decor/asedio/'
U = '/home/z/my-project/upload/'
for name, p in [
    ('OLD interior2 (game)', G + 'interior2.webp'),
    ('NEW Interior2 (upload)', U + 'Interior2.png'),
    ('OLD fachada2 (game)', G + 'fachada2.webp'),
    ('NEW Fachada2 (upload)', U + 'Fachada2.png'),
    ('REF fachada1 (good)', G + 'fachada1.webp'),
    ('REF interior1 (good)', G + 'interior1.webp'),
    ('REF fachada5 (good)', G + 'fachada5.webp'),
]:
    print(name, bbox_alpha(p))
print('zonas2.jpg green line:', green_line(U + 'zonas2.jpg'))

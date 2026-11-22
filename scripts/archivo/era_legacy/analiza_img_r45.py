#!/usr/bin/env python3
"""r45 · análisis de candado.png y palas.png (contornos para la constelación)."""
import sys
from PIL import Image
import numpy as np

def info(p):
    im = Image.open(p)
    print(f"== {p} == modo={im.mode} size={im.size}")
    a = np.array(im)
    print("shape:", a.shape, "dtype:", a.dtype)
    if a.shape[2] == 4:
        al = a[:, :, 3]
        print(f"alpha: min={al.min()} max={al.max()} opacos(>128)={int((al > 128).sum())} ({(al > 128).mean() * 100:.1f}%)")
        ys, xs = np.where(al > 128)
        if len(xs):
            print(f"bbox opacos: x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
        # silueta en ASCII (32 columnas)
        m = (al > 128)
    else:
        g = a[:, :, :3].mean(axis=2) if a.ndim == 3 else a
        m = g < 128
        ys, xs = np.where(m)
        if len(xs):
            print(f"bbox oscuros: x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}] px={len(xs)}")
    # ascii preview
    H, W = m.shape
    rows, cols = 26, 48
    art = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            y0, y1 = int(r * H / rows), int((r + 1) * H / rows)
            x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
            frac = m[y0:y1, x0:x1].mean()
            line += "#" if frac > 0.55 else ("+" if frac > 0.2 else ("." if frac > 0.04 else " "))
        art.append(line)
    print("\n".join(art))
    # colores del área opaca
    if a.shape[2] == 4:
        op = a[:, :, 3] > 128
        if op.any():
            rgb = a[:, :, :3][op]
            print("color medio opacos:", rgb.mean(axis=0).round(1), "único?:", len(np.unique(rgb.reshape(-1, 3), axis=0)) <= 4)

info(sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/upload/candado.png")

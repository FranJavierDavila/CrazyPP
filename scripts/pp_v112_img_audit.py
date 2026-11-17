#!/usr/bin/env python3
"""Auditoría de canal alfa: parallax del vagón (p1-p4) + galope1-3."""
from PIL import Image
import os, glob

PAR = '/home/z/my-project/game/championships/oeste/assets/parallax'
UP = '/home/z/my-project/upload'

def audit(path):
    im = Image.open(path)
    name = os.path.basename(path)
    mode = im.mode
    has_alpha = 'A' in im.getbands()
    w, h = im.size
    info = f"{name:34s} {w:5d}x{h:<5d} mode={mode:6s} alpha={'SÍ' if has_alpha else 'NO'}"
    if has_alpha:
        a = im.getchannel('A')
        lo, hi = a.getextrema()
        # proporción de píxeles totalmente transparentes
        hist = a.histogram()
        total = w * h
        t0 = hist[0] / total * 100
        t255 = hist[255] / total * 100
        info += f" aRange=({lo},{hi}) a=0:{t0:.1f}% a=255:{t255:.1f}%"
        # color medio de las zonas transparentes (¿negro?)
        if t0 > 0.5:
            rgb = im.convert('RGBA')
            px = rgb.getdata()
            import random
            idxs = [i for i in range(0, total, max(1, total // 20000)) if px[i][3] < 10]
            if idxs:
                rs = sum(px[i][0] for i in idxs) / len(idxs)
                gs = sum(px[i][1] for i in idxs) / len(idxs)
                bs = sum(px[i][2] for i in idxs) / len(idxs)
                info += f" | RGB medio zona transparente=({rs:.0f},{gs:.0f},{bs:.0f})"
    else:
        # ¿esquinas negras? muestreo de las 4 esquinas
        rgb = im.convert('RGB')
        cs = [rgb.getpixel((0,0)), rgb.getpixel((w-1,0)), rgb.getpixel((0,h-1)), rgb.getpixel((w-1,h-1))]
        info += f" esquinas={cs}"
    return info

print("== PARALLAX (assets del juego) ==")
for f in sorted(glob.glob(PAR + '/*.png')) + sorted(glob.glob(PAR + '/*.jpg')):
    print(audit(f))

print("\n== GALOPE (upload/) ==")
for f in sorted(glob.glob(UP + '/galope*.png')):
    print(audit(f))

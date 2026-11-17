#!/usr/bin/env python3
"""Audita el canal alfa de los PNG del juego (parallax + galope + cubos + HUD).
Un «manchón negro» = PNG sin alfa (fondo negro opaco) o alfa todo 255."""
import os, sys
from PIL import Image

BASES = [
    '/home/z/my-project/game/championships/oeste/assets/parallax',
    '/home/z/my-project/game/championships/oeste/assets/galope',
    '/home/z/my-project/game/championships/oeste/assets/cubos',
    '/home/z/my-project/game/championships/oeste/assets',
]

def audit(path):
    try:
        im = Image.open(path)
    except Exception as e:
        return 'ERROR ' + str(e)
    mode = im.mode
    has_alpha = mode in ('RGBA', 'LA', 'PA') or 'transparency' in im.info
    info = f"{os.path.basename(path):38s} {mode:5s} {im.size[0]}x{im.size[1]}"
    if not has_alpha:
        return info + '  << SIN CANAL ALFA'
    im2 = im.convert('RGBA')
    a = im2.getchannel('A')
    hist = a.histogram()
    n = im2.size[0] * im2.size[1]
    transparent = sum(hist[:16]) / n
    semi = sum(hist[16:240]) / n
    opaque = sum(hist[240:]) / n
    mn, mx = a.getextrema()
    flag = ''
    if mn == 255:
        flag = '  << ALFA=255 EN TODO (sin transparencia real)'
    elif transparent < 0.01 and semi < 0.01:
        flag = '  << casi todo opaco'
    return info + f"  transp={transparent:.2f} semi={semi:.2f} opaco={opaque:.2f} min={mn}" + flag

for base in BASES:
    if not os.path.isdir(base):
        continue
    print('== ' + base)
    for f in sorted(os.listdir(base)):
        if f.lower().endswith('.png'):
            print('  ' + audit(os.path.join(base, f)))
for f in ['ligotes.png']:
    p = '/home/z/my-project/game/championships/oeste/assets/' + f
    if os.path.exists(p):
        print('== sueltos')
        print('  ' + audit(p))

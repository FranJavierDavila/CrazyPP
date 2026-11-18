#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""laminas_r74.py — láminas de contacto de las 8 capturas r74."""
from PIL import Image, ImageDraw
import pathlib

CAP = pathlib.Path('/home/z/my-project/download/r74_capturas')
PAGS = ['main', 'hallpick', 'multi', 'elegirVis', 'dueloask', 'trainarea',
        'salabola', 'salaroom']

W = 760
GRUPO = 4
for gi in range(0, len(PAGS), GRUPO):
    grupo = PAGS[gi:gi + GRUPO]
    imgs = []
    for p in grupo:
        im = Image.open(CAP / (p + '.png')).convert('RGB')
        h = round(im.height * W / im.width)
        imgs.append((p, im.resize((W, h), Image.LANCZOS), h))
    H = max(h for _, _, h in imgs) + 44
    lamina = Image.new('RGB', (W * len(imgs) + 8 * (len(imgs) + 1), H + 8),
                       (10, 13, 22))
    d = ImageDraw.Draw(lamina)
    x = 8
    for p, im, _h in imgs:
        d.text((x + 6, 8), p, fill=(232, 180, 90))
        lamina.paste(im, (x, 36))
        x += W + 8
    out = CAP / ('lamina' + str(gi // GRUPO + 1) + '_r74.png')
    lamina.save(out)
    print(out.name, lamina.size)

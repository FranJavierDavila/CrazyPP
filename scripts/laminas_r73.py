#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""laminas_r73.py — láminas de contacto de las 10 capturas del nivel 3
maquetado (r73). 5 por lámina, 2 láminas, títulos de página incluidos."""
from PIL import Image, ImageDraw
import pathlib

CAP = pathlib.Path('/home/z/my-project/download/r73_capturas')
PAGS = ['opts', 'optsSala', 'multi', 'rankini', 'champs',
        'train', 'carrera', 'carreradiv', 'rankme', 'champuno']

W = 760   # ancho de cada captura en la lámina
GRUPO = 5
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
    out = CAP / ('lamina' + str(gi // GRUPO + 1) + '_nivel3.png')
    lamina.save(out)
    print(out.name, lamina.size)

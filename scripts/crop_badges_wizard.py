#!/usr/bin/env python3
"""V2.137 — crops con rejilla de 25 px de las espirales numeradas (nodos 2-5)."""
from PIL import Image, ImageDraw

SRC = '/home/z/my-project/upload/Mapa.png'
im = Image.open(SRC).convert('RGB')

ZONAS = {
    'n2': (350, 280, 640, 700),    # espiral 2 + anillo orbe 1
    'n3': (580, 20, 870, 420),     # espiral 3 + anillo wizard 2
    'n4': (860, 270, 1150, 700),   # espiral 4 + anillo orbe 2
}
for name, (x0, y0, x1, y1) in ZONAS.items():
    w, h = x1 - x0, y1 - y0
    crop = im.crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(crop)
    for gx in range(x0 - x0 % 25, x1, 25):
        sx = gx - x0
        mayor = gx % 100 == 0
        d.line([(sx, 0), (sx, h)], fill=(255, 0, 255) if mayor else (130, 70, 130),
               width=2 if mayor else 1)
        if mayor:
            d.text((sx + 2, 2), str(gx), fill=(255, 255, 0))
    for gy in range(y0 - y0 % 25, y1, 25):
        sy = gy - y0
        mayor = gy % 100 == 0
        d.line([(0, sy), (w, sy)], fill=(255, 0, 255) if mayor else (130, 70, 130),
               width=2 if mayor else 1)
        if mayor:
            d.text((2, sy + 2), str(gy), fill=(255, 255, 0))
    crop = crop.resize((w * 2, h * 2), Image.LANCZOS)
    crop.save(f'/home/z/my-project/scripts/badge_{name}.png')
    print(f'badge_{name}.png  zona {x0,y0,x1,y1}')

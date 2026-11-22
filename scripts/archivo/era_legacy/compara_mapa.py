#!/usr/bin/env python3
"""Compara el mapa.webp actual con el mapa.png nuevo subido,
dibujando los NODOS (198,341)(516,456)(863,313)(1173,462)(1536,269) r=95
sobre ambos para verificar si el anillo/tapas siguen alineados."""
from PIL import Image, ImageDraw

NODOS = [(198, 341), (516, 456), (863, 313), (1173, 462), (1536, 269)]
R = 95

viejo = Image.open('/home/z/my-project/public/championships/oeste/assets/mapa.webp').convert('RGB')
nuevo = Image.open('/home/z/my-project/upload/mapa.png').convert('RGB')

def marca(im):
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(NODOS, 1):
        d.ellipse([x - R, y - R, x + R, y + R], outline=(255, 0, 0), width=6)
        d.text((x - 10, y - 14), str(i), fill=(255, 255, 0))
    return im

a, b = marca(viejo.copy()), marca(nuevo.copy())
lienzo = Image.new('RGB', (1699, 926 * 2 + 20), (20, 20, 20))
lienzo.paste(a, (0, 0))
lienzo.paste(b, (0, 946))
lienzo.save('/home/z/my-project/scripts/_mapa_compara.png')
print('guardado _mapa_compara.png  (ARRIBA=viejo mapa.webp, ABAJO=nuevo mapa.png)')

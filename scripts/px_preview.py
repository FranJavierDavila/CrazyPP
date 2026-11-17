#!/usr/bin/env python3
"""Compone el panorama P1 cosido + muestras de planos sobre cielo azul
para REPRODUCIR lo que se ve por la ventana y localizar el manchón negro."""
from PIL import Image
import os

P = '/home/z/my-project/game/championships/oeste/assets/parallax'
SKY = (110, 167, 214)  # azul cielo del _texSky

def over_sky(img, w, h):
    bg = Image.new('RGBA', (w, h), SKY + (255,))
    if img.size != (w, h):
        img = img.resize((w, h))
    bg.alpha_composite(img)
    return bg

# 1) Pano P1 cosido (como _buildPano): 2 imágenes 2172x524 pegadas
a = Image.open(os.path.join(P, 'p1_paisajedesierto1.png')).convert('RGBA')
b = Image.open(os.path.join(P, 'p1_paisajedesierto2.png')).convert('RGBA')
cv = Image.new('RGBA', (a.width + b.width, a.height), (0, 0, 0, 0))
cv.paste(a, (0, 0)); cv.paste(b, (a.width, 0))
pano = over_sky(cv, 4344, 524)
pano.save('/tmp/pxcheck/pano_sky.png')
# detalle de la COSTURA (zona central)
pano.crop((2000, 0, 2400, 524)).save('/tmp/pxcheck/pano_seam.png')

# 2) muestras p2/p3/p4 sobre cielo
for f in ['p2_rancho1.png', 'p2_estructura3.png', 'p3_arbusto1.png', 'p4_cactus1.png']:
    im = Image.open(os.path.join(P, f)).convert('RGBA')
    over_sky(im, 512, 512).save('/tmp/pxcheck/muestra_' + f)
print('ok')

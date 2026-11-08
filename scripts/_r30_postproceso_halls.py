#!/usr/bin/env python3
"""ronda 30 (v3.6.126) · POSTPROCESO DE LOS 18 PLANOS IA → assets/hall/.
Recorta al tamaño EXACTO de la spec (frente/fondo 1849×864 · laterales
2395×864 · suelo/techo 1296×1678) con realce suave (enfoque + saturación)
y escribe los JPG finales en public/assets/hall/<id>/. Idempotente."""
import os
from PIL import Image, ImageEnhance, ImageFilter

RAIZ = '/home/z/my-project/upload'   # r30: el repo VIVO (el snapshot raíz es intocable)
GEN = os.path.join(RAIZ, 'scripts', '_r30_assets', 'gen')
DEST = os.path.join(RAIZ, 'public', 'assets', 'hall')

SPEC = {  # plano → (ancho, alto) EXACTOS de la spec v3.6.28
    'frente': (1849, 864), 'fondo': (1849, 864),
    'izquierda': (2395, 864), 'derecha': (2395, 864),
    'suelo': (1296, 1678), 'techo': (1296, 1678),
}
SALAS = ['neon', 'observatorio', 'dojo']


def cubrir(im, an, al):
    """Escala a cubrir (LANCZOS) y recorta centrado al tamaño exacto."""
    f = max(an / im.width, al / im.height)
    nw, nh = round(im.width * f), round(im.height * f)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - an) // 2
    y = (nh - al) // 2
    return im.crop((x, y, x + an, y + al))


def realce(im):
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Contrast(im).enhance(1.02)
    return im


tot = 0
for sala in SALAS:
    acum = 0
    for plano, (an, al) in SPEC.items():
        src = os.path.join(GEN, f'{sala}_{plano}.png')
        dst_dir = os.path.join(DEST, sala)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, f'{plano}.jpg')
        im = Image.open(src).convert('RGB')
        im = cubrir(im, an, al)
        im = realce(im)
        assert im.size == (an, al), f'{sala}/{plano}: {im.size} != {(an, al)}'
        im.save(dst, 'JPEG', quality=86, optimize=True, progressive=True)
        kb = os.path.getsize(dst) // 1024
        acum += kb
        print(f'{sala}/{plano}.jpg  {an}x{al}  {kb} KB')
    print(f'  → {sala}: {acum} KB totales\n')
    tot += acum
print(f'TOTAL 3 salones: {tot // 1024} MB')

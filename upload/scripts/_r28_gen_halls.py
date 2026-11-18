#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r28 (v3.6.124, FASE 126) — REGENERADOR DE LOS 3 HALL.
Rediseño a nivel Locura/Wizard por petición del dueño («muy cutres…
la diferencia es abismal»). Mismo contrato de fichas y proporciones
EXACTAS del museo/cabaña/r26b (c08_hall_hud.js):
  frente.jpg / fondo.jpg      1849×864  → plano 6,10×2,85
  izquierda.jpg / derecha.jpg 2395×864  → plano 7,90×2,85
  suelo.jpg / techo.jpg       1296×1678 → plano 6,10×7,90
Salida: public/assets/hall/<id>/*.jpg (JPEG q84, arte 100 % procedural).
"""
import sys
from pathlib import Path
from PIL import Image

RAIZ = Path('/home/z/my-project/upload')
sys.path.insert(0, str(RAIZ / 'scripts'))

import _r28_halls_neon as NEON
import _r28_halls_orbital as ORB
import _r28_halls_dojo as DOJO

PLANOS = {
    'frente': (1849, 864), 'fondo': (1849, 864),
    'izquierda': (2395, 864), 'derecha': (2395, 864),
    'suelo': (1296, 1678), 'techo': (1296, 1678),
}


def salva(img, dest, tam):
    assert img.size == tam, f'{dest}: {img.size} != {tam}'
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'JPEG', quality=84, optimize=True)


def main():
    base = RAIZ / 'public' / 'assets' / 'hall'
    total = 0

    def haz(salon, funcs):
        nonlocal total
        for pieza, fn in funcs.items():
            im = fn()
            w, h = PLANOS[pieza]
            if im.size != (w, h):
                im = im.resize((w, h), Image.LANCZOS)
            p = base / salon / f'{pieza}.jpg'
            salva(im, p, (w, h))
            kb = p.stat().st_size / 1024
            total += p.stat().st_size
            print(f'  {salon}/{pieza}.jpg  {w}x{h}  {kb:.0f} KB')

    print('NEON ARCADE')
    haz('neon', {
        'frente': NEON.frente, 'fondo': NEON.fondo,
        'izquierda': lambda: NEON.lateral(3, False),
        'derecha': lambda: NEON.lateral(8, True),
        'suelo': NEON.suelo, 'techo': NEON.techo,
    })
    print('OBSERVATORIO ESTELAR')
    haz('observatorio', {
        'frente': ORB.frente, 'fondo': ORB.fondo,
        'izquierda': lambda: ORB.lateral(60),
        'derecha': lambda: ORB.lateral(90),
        'suelo': ORB.suelo, 'techo': ORB.techo,
    })
    print('DOJO ZEN')
    haz('dojo', {
        'frente': DOJO.frente, 'fondo': DOJO.fondo,
        'izquierda': lambda: DOJO.lateral(70, True),
        'derecha': lambda: DOJO.lateral(80, False),
        'suelo': DOJO.suelo, 'techo': DOJO.techo,
    })
    print(f'\nTOTAL: {total / 1024:.0f} KB en 18 imágenes')


if __name__ == '__main__':
    main()

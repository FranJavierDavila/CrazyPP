#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r26b (v3.6.122, FASE 124) — INSERTA los 9 literales de
assets (3 PNG + 6 voces) de los superpoderes nuevos en c12_pingponggame.js,
justo antes del registro PODERES_PALA (mismo patrón que patch_r25.py).

Idempotente: si ya están los marcadores, no hace nada.
"""
from base64 import b64encode
from pathlib import Path

C12 = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
A = Path('/home/z/my-project/upload/scripts/_r26b_assets')
MARCADOR = '/* == r26b: ASSETS INSERTADOS =='


def datauri(p, mime):
    return f'data:{mime};base64,' + b64encode(p.read_bytes()).decode('ascii')


def main():
    src = C12.read_text(encoding='utf-8')
    if MARCADOR in src:
        print('ya insertados: nada que hacer')
        return
    ancla = 'const PODERES_PALA = ['
    ix = src.index(ancla)
    bloque = []
    bloque.append(MARCADOR)
    bloque.append('/* =====================================================================')
    bloque.append(' *  r26b (v3.6.122) · ARTE DE LOS 3 SUPERPODERES NUEVOS — insignias')
    bloque.append(' *  circulares 256×256 (256 colores) y voces espeak-ng → MP3 (48 kHz')
    bloque.append(' *  mono 64 kbps), TODO embebido como data-URI: cero red, offline en')
    bloque.append(' *  el Quest (mismo patrón data-URI de las 7 entradas anteriores).')
    bloque.append(' *  ===================================================================== */')
    for pid in ('fenix', 'crono', 'hielo'):
        png = datauri(A / f'icon_{pid}.png', 'image/png')
        bloque.append(f"const PNG_PODER_{pid.upper()} = '{png}';")
        voz_es = datauri(A / f'voz_{pid}_es.mp3', 'audio/mpeg')
        voz_en = datauri(A / f'voz_{pid}_en.mp3', 'audio/mpeg')
        bloque.append(f"const VOZ_PODER_{pid.upper()} = '{voz_es}';")
        bloque.append(f"const VOZ_PODER_{pid.upper()}_EN = '{voz_en}';")
    bloque.append('')
    out = src[:ix] + '\n'.join(bloque) + '\n' + src[ix:]
    C12.write_text(out, encoding='utf-8')
    print(f'insertados 9 literales antes de «{ancla}» (+{len("\n".join(bloque))} B)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r33 (v3.6.129) · INSERTA los assets de los 4 poderes nuevos en c12:
sustituye los marcadores __R33_*__ por los data-URI reales (PNG 256×256
cuantizado a 256 colores + voces Piper MP3 48 kHz mono 64 kbps).
Idempotente: si no hay marcadores, no toca nada."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
A = RAIZ / 'scripts' / '_r33_assets'

PARES = {
    '__R33_PNG_PRISMA__': ('icon_prisma.png', 'image/png'),
    '__R33_VOZ_PRISMA__': ('voz_prisma_es.mp3', 'audio/mpeg'),
    '__R33_VOZ_PRISMA_EN__': ('voz_prisma_en.mp3', 'audio/mpeg'),
    '__R33_PNG_ONDA__': ('icon_onda.png', 'image/png'),
    '__R33_VOZ_ONDA__': ('voz_onda_es.mp3', 'audio/mpeg'),
    '__R33_VOZ_ONDA_EN__': ('voz_onda_en.mp3', 'audio/mpeg'),
    '__R33_PNG_SALVA__': ('icon_salva.png', 'image/png'),
    '__R33_VOZ_SALVA__': ('voz_salva_es.mp3', 'audio/mpeg'),
    '__R33_VOZ_SALVA_EN__': ('voz_salva_en.mp3', 'audio/mpeg'),
    '__R33_PNG_ANCLA__': ('icon_ancla.png', 'image/png'),
    '__R33_VOZ_ANCLA__': ('voz_ancla_es.mp3', 'audio/mpeg'),
    '__R33_VOZ_ANCLA_EN__': ('voz_ancla_en.mp3', 'audio/mpeg'),
}


def datauri(fich, mime):
    b = (A / fich).read_bytes()
    return f'data:{mime};base64,' + base64.b64encode(b).decode('ascii')


def main():
    src = C12.read_text(encoding='utf-8')
    total = 0
    for marcador, (fich, mime) in PARES.items():
        n = src.count(marcador)
        if n == 0:
            print(f'· {marcador}: ya sustituido (0 apariciones)')
            continue
        if n != 1:
            print(f'!! {marcador}: {n} apariciones (se esperaba 1) — ABORT')
            return 1
        src = src.replace(marcador, datauri(fich, mime))
        total += 1
        print(f'✓ {marcador} ← {fich}')
    C12.write_text(src, encoding='utf-8')
    print(f'insertados: {total}/12 · c12 queda en {C12.stat().st_size:,} B')
    return 0


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
"""RONDA 35 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r30/r31/r32/r34 a 3.6.131-SDK6 (FASE 133 — Prisma visible).

Patrón de la casa (sella_r31/r32/r33): los tests de rondas anteriores
llevan sus sellos de versión/tamaño/golden DUROS; cada bump los deja
viejos. Este script los re-ancla IN SITU a los valores VIGENTES:
  · versión    : 3.6.130-SDK6 → 3.6.131-SDK6 (y variantes V/v/hub)
  · fase       : 132 → 133
  · faseNombre : «Correcciones a los superpoderes de pala» →
                 «Prisma visible — bola arcoíris»
  · tamaño     : 11.375.288 → 11.378.159 B
  · golden     : e00e508a… → c9c65ff5…
Uso: python3 scripts/sella_r35_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = 'e00e508ab0616dec7c9cb8c694ae66227ea70eea83fe9dc16c2d0af06dd82d7f'
GOLDEN_NUEVO = 'c9c65ff52117556fc225f590c96189fef6c77ac5e262d11f833aecdf0d8ff81a'

TOKENS = [
    ('3.6.130-SDK6', '3.6.131-SDK6'),
    ('V3.6.130-SDK6', 'V3.6.131-SDK6'),
    ('v3.6.130-SDK6', 'v3.6.131-SDK6'),
    ('v36130-sdk6', 'v36131-sdk6'),
    ('v36130', 'v36131'),
    ('3.6.130', '3.6.131'),
    ('vjson.fase === 132', 'vjson.fase === 133'),
    ('FASE 132', 'FASE 133'),
    ('fase 132', 'fase 133'),
    ("vjson.faseNombre === 'Correcciones a los superpoderes de pala'",
     "vjson.faseNombre === 'Prisma visible — bola arcoíris'"),
    ('11375288', '11378159'),
    ('11.375.288', '11.378.159'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('e00e508a', 'c9c65ff5'),
]

TESTS = [
    'scripts/test_r30_fenix_salones_v36126.mjs',
    'scripts/test_r31_higiene_v36127.mjs',
    'scripts/test_r32_salones_v36128.mjs',
    'scripts/test_r34_fixes_v36130.mjs',
]


def main():
    for rel in TESTS:
        p = RAIZ / rel
        txt = p.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            print(f'  re-anclado: {rel}')
        else:
            print(f'  sin cambios: {rel}')
    print('sella_r35_viva: listo. Re-ejecutar los 4 tests de regresión.')


if __name__ == '__main__':
    main()

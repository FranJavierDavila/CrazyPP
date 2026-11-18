# -*- coding: utf-8 -*-
"""RONDA 36 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r30-r35 a 3.6.132-SDK6 (FASE 134 — revisión del multijugador).

Patrón de la casa (sella_r31/r32/r33/r35): versión, tamaño, golden y
faseNombre de los tests de rondas anteriores se re-anclan IN SITU a los
valores VIGENTES tras el bump.
Uso: python3 scripts/sella_r36_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = 'c9c65ff52117556fc225f590c96189fef6c77ac5e262d11f833aecdf0d8ff81a'
GOLDEN_NUEVO = '49d01478b0cbbc0218df31b0099671098cf991dc1d87b3e9f8643e127b2ecb5d'

TOKENS = [
    ('3.6.131-SDK6', '3.6.132-SDK6'),
    ('V3.6.131-SDK6', 'V3.6.132-SDK6'),
    ('v3.6.131-SDK6', 'v3.6.132-SDK6'),
    ('v36131-sdk6', 'v36132-sdk6'),
    ('v36131', 'v36132'),
    ('3.6.131', '3.6.132'),
    ('vjson.fase === 133', 'vjson.fase === 134'),
    ('FASE 133', 'FASE 134'),
    ('fase 133', 'fase 134'),
    ("vjson.faseNombre === 'Prisma visible — bola arcoíris'",
     "vjson.faseNombre === 'Revisión del multijugador — 3 bugs de red'"),
    ('11378159', '11380008'),
    ('11.378.159', '11.380.008'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('c9c65ff5', '49d01478'),
]

TESTS = [
    'scripts/test_r30_fenix_salones_v36126.mjs',
    'scripts/test_r31_higiene_v36127.mjs',
    'scripts/test_r32_salones_v36128.mjs',
    'scripts/test_r34_fixes_v36130.mjs',
    'scripts/test_r35_prisma_v36131.mjs',
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
    print('sella_r36_viva: listo. Re-ejecutar los 5 tests de regresión.')


if __name__ == '__main__':
    main()

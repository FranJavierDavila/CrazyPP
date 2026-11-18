# -*- coding: utf-8 -*-
"""RONDA 38 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r24-r37 a 3.6.134-SDK6 (FASE 136 — el salón de la partida:
Rascacielos + partidas en el hall del anfitrión, IA y multijugador).

Patrón de la casa (sella_r31…r37): versión, tamaño, golden y faseNombre de
los tests de rondas anteriores se re-anclan IN SITU a los valores VIGENTES
tras el bump. Nota r38: test_r24 afirmaba «HALL_VARIANTES.length === 5»
(re-anclada r26b) — el catálogo ahora tiene SEIS variantes (rascacielos),
y su etiqueta lo documenta.

Uso: python3 scripts/sella_r38_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '726f262ca69f9781c7fd7f3bd509651cb71884e4790164e9595ab03f98695b0f'
GOLDEN_NUEVO = '951940900bdefb5d27498257e5adf01a3188e25f449945f6fa678da98a0e786f'

TOKENS = [
    ('3.6.133-SDK6', '3.6.134-SDK6'),
    ('V3.6.133-SDK6', 'V3.6.134-SDK6'),
    ('v3.6.133-SDK6', 'v3.6.134-SDK6'),
    ('v36133-sdk6', 'v36134-sdk6'),
    ('v36133', 'v36134'),
    ('3.6.133', '3.6.134'),
    ('vjson.fase === 135', 'vjson.fase === 136'),
    ('FASE 135', 'FASE 136'),
    ('fase 135', 'fase 136'),
    ("vjson.faseNombre === 'Revisión del multijugador II — reconexión ICE real'",
     "vjson.faseNombre === 'El salón de la partida — Rascacielos'"),
    ('11384002', '11395884'),
    ('11.384.002', '11.395.884'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('726f262c', '95194090'),
    # r38 · el catálogo de salones crece a SEIS (rascacielos): el test de la
    # r24 contaba CINCO (re-anclado ya en r26b) — número y etiqueta nuevos.
    ("chk(Array.isArray(HALL_VARIANTES) && HALL_VARIANTES.length === 5, '5 variantes (re-anclada r26b: museo + cabaña + neón + orbital + dojo)');",
     "chk(Array.isArray(HALL_VARIANTES) && HALL_VARIANTES.length === 6, '6 variantes (re-anclada r38: museo + cabaña + neón + orbital + dojo + rascacielos)');"),
    # r37b · aguja que cita el CÓDIGO FUENTE cambiado por la r37 (el sella
    # anterior lo dejó con sello r37 — conservarlo tal cual: el source no cambia).
]

TESTS = [
    'scripts/test_r24_spin_cabana_v36119.mjs',
    'scripts/test_r26b_sorpresa_v36122.mjs',
    'scripts/test_r27_foro3d_v36123.mjs',
    'scripts/test_r30_fenix_salones_v36126.mjs',
    'scripts/test_r31_higiene_v36127.mjs',
    'scripts/test_r32_salones_v36128.mjs',
    'scripts/test_r33_poderes_v36129.mjs',
    'scripts/test_r34_fixes_v36130.mjs',
    'scripts/test_r35_prisma_v36131.mjs',
    'scripts/test_r36_red_v36132.mjs',
    'scripts/test_r37_red_v36133.mjs',
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
            print(f'· re-anclado {rel}')
        else:
            print(f'  (sin cambios) {rel}')


if __name__ == '__main__':
    main()

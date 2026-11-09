# -*- coding: utf-8 -*-
"""RONDA 40 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r24-r39 a 3.6.136-SDK6 (FASE 138 — el Arcano a la vista:
búho un 25 % más pequeño, botones del hall pulsables sin menú, el
escenario arcano DELANTE del anfitrión, cielo azul liso sin imagen,
suelo infinito de losetas que mutan y la melodía propia arcano.mp3).

Patrón de la casa (sella_r31…r39): versión, tamaño, golden y faseNombre
de los tests de rondas anteriores se re-anclan IN SITU a los valores
VIGENTES tras el bump. Además, la ÚNICA aguja de la r39 que describe la
bóveda CON Vía Láctea se re-ancla al cielo LISO de la r40 (petición del
dueño: «el fondo completamente azul oscuro sin imagen»).

Uso: python3 scripts/sella_r40_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '70049f9c258c575cd50f836cc5e44686615e53e62b12d3ef1b3419268b60f5b4'
GOLDEN_NUEVO = '3e54690b9abd48818ec97ff3fc87262988fde2c0cacb74e7a201aafbaf2ff997'

TOKENS = [
    ('3.6.135-SDK6', '3.6.136-SDK6'),
    ('V3.6.135-SDK6', 'V3.6.136-SDK6'),
    ('v3.6.135-SDK6', 'v3.6.136-SDK6'),
    ('v36135-sdk6', 'v36136-sdk6'),
    ('v36135', 'v36136'),
    ('3.6.135', '3.6.136'),
    ('vjson.fase === 137', 'vjson.fase === 138'),
    ('FASE 137', 'FASE 138'),
    ('fase 137', 'fase 138'),
    ("vjson.faseNombre === 'El apartado arcano — superpoderes'",
     "vjson.faseNombre === 'El Arcano a la vista — revisión del dueño'"),
    ('11453242', '11461098'),
    ('11.453.242', '11.461.098'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('70049f9c', '3e54690b'),
    # r40 · la bóveda del Arcano pierde la VÍA LÁCTEA (petición del dueño:
    # «el fondo completamente azul oscuro sin imagen»): la aguja de la r39
    # se re-ancla al cielo liso y al suelo infinito nuevo.
    ("""chk(c08.includes('VÍA LÁCTEA: banda diagonal de nubes estelares'),
  'VÍA LÁCTEA: banda diagonal de nubes estelares');""",
     """chk(c08.includes("bg.addColorStop(1, '#0a1a36')"),
  're-anclada r40: cielo azul oscuro LISO (sin Vía Láctea ni estrellas)');"""),
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
    'scripts/test_r38_rascacielos_v36134.mjs',
    'scripts/test_r39_arcano_v36135.mjs',
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
            print('· re-anclado', rel)
        else:
            print('· sin cambios', rel)
    print('OK sella_r40_viva')


if __name__ == '__main__':
    main()

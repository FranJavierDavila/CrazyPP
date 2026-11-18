# -*- coding: utf-8 -*-
"""RONDA 39 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r24-r38 a 3.6.135-SDK6 (FASE 137 — el apartado arcano: búho del
hall, espacio infinito, galería de superpoderes, desbloqueo por campeonato
ganado y Duelos Locos con los desbloqueados).

Patrón de la casa (sella_r31…r38): versión, tamaño, golden y faseNombre de
los tests de rondas anteriores se re-anclan IN SITU a los valores VIGENTES
tras el bump.

Uso: python3 scripts/sella_r39_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '951940900bdefb5d27498257e5adf01a3188e25f449945f6fa678da98a0e786f'
GOLDEN_NUEVO = '70049f9c258c575cd50f836cc5e44686615e53e62b12d3ef1b3419268b60f5b4'

TOKENS = [
    ('3.6.134-SDK6', '3.6.135-SDK6'),
    ('V3.6.134-SDK6', 'V3.6.135-SDK6'),
    ('v3.6.134-SDK6', 'v3.6.135-SDK6'),
    ('v36134-sdk6', 'v36135-sdk6'),
    ('v36134', 'v36135'),
    ('3.6.134', '3.6.135'),
    ('vjson.fase === 136', 'vjson.fase === 137'),
    ('FASE 136', 'FASE 137'),
    ('fase 136', 'fase 137'),
    ("vjson.faseNombre === 'El salón de la partida — Rascacielos'",
     "vjson.faseNombre === 'El apartado arcano — superpoderes'"),
    ('11395884', '11453242'),
    ('11.395.884', '11.453.242'),
    ('11453168', '11453242'),
    ('11.453.168', '11.453.242'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('670d114beabbbf046d0806c3c1b2ce0440a8382594ee88d5445912932a3182f9', GOLDEN_NUEVO),
    ('95194090', '70049f9c'),
    ('670d114b', '70049f9c'),
    # r39 · el ESPACIO ARCANO se añade a la escena junto al hall (el 12.º
    # scene.add legítimo): la cuenta de r34 se re-ancla.
    ("""chk(cuenta(c12, 'this.scene.add(') === 11,
  `scene.add sólo los 11 legítimos (rig/hall/menú/ondas portal/flechas/visor/servido): ${cuenta(c12, 'this.scene.add(')}`);""",
     """chk(cuenta(c12, 'this.scene.add(') === 12,
  `scene.add sólo los 12 legítimos (re-anclada r39: +el espacio arcano): ${cuenta(c12, 'this.scene.add(')}`);"""),
    # r39 · el guard del portal estrena la EXCEPCIÓN DUELOS LOCOS (el
    # invitado portaliza SU golpe): la aguja de r26b cita el literal viejo.
    ("""chk(c12.includes('!(this.net.online && this.net.role === \\'guest\\')) {'), 'el invitado online no enciende (no simula)');""",
     """chk(c12.includes("this.rules.mode !== 'duelos'"), 're-anclada r39: el invitado no enciende fuera de duelos (allí portaliza SU golpe)');"""),
    # r39 · las ventanas de campeonato se tickan también POR DUELOS LOCOS
    # (los desbloqueados viven SUS ventanas): agujas del patrón red/elec.
    ("""chk(c12.includes('if (on && this._fenixT > 0) {') && c12.includes('if (on && this._cronoT > 0) {') &&
    c12.includes('if (on && this._oscuridadT > 0) {'), 'ventanas propias en el tick (patrón red/elec)');""",
     """chk(c12.includes("(on || this._dlVentana('fenix')) && this._fenixT > 0") && c12.includes("(on || this._dlVentana('crono')) && this._cronoT > 0") &&
    c12.includes("(on || this._dlVentana('oscuridad')) && this._oscuridadT > 0"), 're-anclada r39: ventanas propias en el tick (campeonato + duelos)');"""),
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

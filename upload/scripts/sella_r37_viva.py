# -*- coding: utf-8 -*-
"""RONDA 37 (línea viva) · RE-ANCLADO de los sellos de los tests de
regresión r30-r36 a 3.6.133-SDK6 (FASE 135 — revisión del multijugador II:
reconexión ICE real).

Patrón de la casa (sella_r31/r32/r33/r35/r36): versión, tamaño, golden y
faseNombre de los tests de rondas anteriores se re-anclan IN SITU a los
valores VIGENTES tras el bump. Nota r37: el watchdog de silencio es ahora
DINÁMICO (pausa 60 s · reinicio de ICE en vuelo 25 s · normal 12 s) — la
aguja literal de la r36 (`const SILENCIO = this._pausedRemote ? 60000 :
12000;`) se sustituye por la expresión vigente, que conserva el 60 s de la
pausa anunciada (el contenido del FIX B sigue siendo cierto).
Uso: python3 scripts/sella_r37_viva.py
"""
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')

GOLDEN_VIEJO = '49d01478b0cbbc0218df31b0099671098cf991dc1d87b3e9f8643e127b2ecb5d'
GOLDEN_NUEVO = '726f262ca69f9781c7fd7f3bd509651cb71884e4790164e9595ab03f98695b0f'

SILENCIO_VIEJO = 'const SILENCIO = this._pausedRemote ? 60000 : 12000;'
SILENCIO_NUEVO = 'const SILENCIO = this._pausedRemote ? 60000 : (reinicioVivo ? 25000 : 12000);'

TOKENS = [
    ('3.6.132-SDK6', '3.6.133-SDK6'),
    ('V3.6.132-SDK6', 'V3.6.133-SDK6'),
    ('v3.6.132-SDK6', 'v3.6.133-SDK6'),
    ('v36132-sdk6', 'v36133-sdk6'),
    ('v36132', 'v36133'),
    ('3.6.132', '3.6.133'),
    ('vjson.fase === 134', 'vjson.fase === 135'),
    ('FASE 134', 'FASE 135'),
    ('fase 134', 'fase 135'),
    ("vjson.faseNombre === 'Revisión del multijugador — 3 bugs de red'",
     "vjson.faseNombre === 'Revisión del multijugador II — reconexión ICE real'"),
    ('11380008', '11384002'),
    ('11.380.008', '11.384.002'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('49d01478', '726f262c'),
    # 1.ª pasada de este sella dejó el hash CORTO (16) — r30/r31/r32 comparan
    # con === : hash COMPLETO en los literales (las etiquetas conservan el corto)
    ("'726f262ca69f9781'", "'" + GOLDEN_NUEVO + "'"),
    (SILENCIO_VIEJO, SILENCIO_NUEVO),
    # r37b · agujas que citan el CÓDIGO FUENTE cambiado por la r37:
    ("const span = PPNET.wrapDiff(ring[n - 1], ring[0]);",
     "const span = NetLink._seqDiff(ring[n - 1], ring[0]);   // r37: u16-safe"),
    # …y el comentario del source de la r36 (v3.6.132) que la pasada de
    # versión de arriba cambió DENTRO de la aguja del test (el source
    # conserva su sello r36 — la aguja debe citarlo tal cual):
    ("// r36 (v3.6.133): pérdida de la VENTANA",
     "// r36 (v3.6.132): pérdida de la VENTANA"),
]

TESTS = [
    'scripts/test_r30_fenix_salones_v36126.mjs',
    'scripts/test_r31_higiene_v36127.mjs',
    'scripts/test_r32_salones_v36128.mjs',
    'scripts/test_r34_fixes_v36130.mjs',
    'scripts/test_r35_prisma_v36131.mjs',
    'scripts/test_r36_red_v36132.mjs',
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

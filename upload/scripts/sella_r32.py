#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 32 · RE-ANCLADO de los sellos de los tests de regresión a 3.6.128.

Los tests de las rondas 27-31 llevan sus secciones de SELLOS clavadas a la
versión de SU ronda (lección r30/r31: cada bump necesita el re-anclado o la
regresión compara contra la versión vieja). Este sellador actualiza IN SITU:
  · 3.6.127-SDK6 → 3.6.128-SDK6 (y menciones v3.6.127 → v3.6.128)
  · FASE 129 → FASE 130 · faseNombre → SALONES DEL DUEÑO (solo r30)
  · tamaño 11.166.858 → 11.185.934 (y su forma con puntos)
  · golden 6badce1b… → 780de58f… (64 hex)
  · hub v36127-sdk6 → v36128-sdk6
  · etiquetas «re-anclada r31» → «re-anclada r32»

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente, cuenta
como «ya anclado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

GOLDEN_VIEJO = '6badce1bc5cd56bbec7c818b38cca7ba1278fbbe61510bbad18d96978011f456'
GOLDEN_NUEVO = '780de58f35842de6e621269b184b3799af525ebea63a4f1c4a9da1972a4c90d4'

REGS = [
    ('3.6.127-SDK6', '3.6.128-SDK6'),
    ('v3.6.127', 'v3.6.128'),
    ('FASE 129', 'FASE 130'),
    ('fase === 129', 'fase === 130'),
    ('fase 129', 'fase 130'),
    ('11.166.858', '11.185.934'),
    ('11166858', '11185934'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('6badce1b…', '780de58f…'),
    ('6badce1b', '780de58f'),
    ('v36127-sdk6', 'v36128-sdk6'),
    ('re-anclada r31', 're-anclada r32'),
    ('Fase 129', 'Fase 130'),
]

FASENOMBRE = [('HIGIENE TEXTUAL FÉNIX', 'SALONES DEL DUEÑO')]

# (test, regs extra) — r30 pina el faseNombre de SU ronda; r27/r28/r29/r31 no
PLAN = [
    ('test_r31_higiene_v36127.mjs', []),
    ('test_r30_fenix_salones_v36126.mjs', FASENOMBRE),
    ('test_r29_sup_poderes_v36125.mjs', FASENOMBRE),
    ('test_r28_bola_salones_v36124.mjs', FASENOMBRE),
    ('test_r27_foro3d_v36123.mjs', FASENOMBRE),
]

fallos = 0
for nombre, regs_extra in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    total = 0
    ya = 0
    for viejo, nuevo in REGS + regs_extra:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            total += n
        elif nuevo in txt:
            ya += 1   # ya anclado en una pasada anterior
        else:
            # aguja ×0 y sello nuevo ausente: puede ser legítimo (el test no
            # menciona ese literal) — se informa, no aborta
            print(f'  · {nombre}: literal ausente ({viejo[:40]}…) — ok si no aplica')
    p.write_text(txt, encoding='utf-8')
    print(f'  ✓ {nombre}: {total} agujas · {ya} ya ancladas')
    if total == 0 and ya == 0:
        fallos += 1
        print(f'  ✗ {nombre}: NADA anclado — revisar a mano')

if fallos:
    print(f'\nRE-ANCLADO con {fallos} test(s) sospechoso(s)')
    sys.exit(1)
print('\nRE-ANCLADO COMPLETO · tests 27-31 miran a 3.6.128-SDK6 (FASE 130)')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 33 · RE-ANCLADO de los sellos de los tests de regresión a 3.6.129.

Patrón de la casa (sella_r31/r32): los tests de las rondas 27-32 llevan sus
secciones de SELLOS clavadas a la versión de SU ronda. Este sellador actualiza
IN SITU a la ronda 33 (v3.6.129-SDK6 · FASE 131 · Lote Aprobado):
  · 3.6.128-SDK6 → 3.6.129-SDK6 (y menciones v3.6.128 → v3.6.129)
  · FASE 130 → FASE 131 · fase === 130 → 131 · faseNombre → LOTE APROBADO
  · tamaño 11.185.934 → 11.365.004 (y su forma con puntos)
  · golden 780de58f… → 9213fc59… (64 hex)
  · hub v36128-sdk6 → v36129-sdk6
  · etiquetas «re-anclada r32» → «re-anclada r33»

Idempotente (lección r13): si la aguja da ×0 pero el sello NUEVO ya está
presente, cuenta como «ya anclado»."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

GOLDEN_VIEJO = '780de58f35842de6e621269b184b3799af525ebea63a4f1c4a9da1972a4c90d4'
GOLDEN_NUEVO = '9213fc5966ac243314fbc8a1c9804509f6ccea6136c337738f6430624c0eae5a'

REGS = [
    ('3.6.128-SDK6', '3.6.129-SDK6'),
    ('v3.6.128', 'v3.6.129'),
    ('FASE 130', 'FASE 131'),
    ('fase === 130', 'fase === 131'),
    ('fase 130', 'fase 131'),
    ('11.185.934', '11.365.004'),
    ('11185934', '11365004'),
    (GOLDEN_VIEJO, GOLDEN_NUEVO),
    ('780de58f…', '9213fc59…'),
    ('780de58f', '9213fc59'),
    ('v36128-sdk6', 'v36129-sdk6'),
    ('re-anclada r32', 're-anclada r33'),
    ('Fase 130', 'Fase 131'),
]

FASENOMBRE = [('SALONES DEL DUEÑO', 'LOTE APROBADO')]

PLAN = [
    ('test_r32_salones_v36128.mjs', []),
    ('test_r31_higiene_v36127.mjs', []),
    ('test_r30_fenix_salones_v36126.mjs', []),
    ('test_r29_sup_poderes_v36125.mjs', []),
    ('test_r28_bola_salones_v36124.mjs', []),
    ('test_r27_foro3d_v36123.mjs', []),
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
            ya += 1
        else:
            print(f'  · {nombre}: literal ausente ({viejo[:40]}…) — ok si no aplica')
    p.write_text(txt, encoding='utf-8')
    print(f'  ✓ {nombre}: {total} agujas · {ya} ya ancladas')
    if total == 0 and ya == 0:
        fallos += 1
        print(f'  ✗ {nombre}: NADA anclado — revisar a mano')

if fallos:
    print(f'\nRE-ANCLADO con {fallos} test(s) sospechoso(s)')
    sys.exit(1)
print('\nRE-ANCLADO COMPLETO · tests 27-32 miran a 3.6.129-SDK6 (FASE 131)')

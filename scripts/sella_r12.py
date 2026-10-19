#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 12 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.9-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los ZIPs
en las capas que los llevan clavados (lección de las rondas 10-11: cada bump
necesita su sellado o el QA TOTAL compara contra la versión vieja).

Capas y sellos:
  E · qa_sup1_v365.py    — versión 3.6.8-SDK6 → 3.6.9-SDK6 (3)
  F · qa_imp2_v351.py    — versión (2)
  G · qa_escudo_v350.py  — versión (3)
  H · qa_descargas_v365.py — versión + nombres de ZIP + tamaños esperados
  I · smoke_sdk5.py      — versión (2)

Idempotente por contador: si un reemplazo da 0, FALLA (sello perdido)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.8-SDK6', '3.6.9-SDK6'), ('v368-sdk6', 'v369-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v369 (construidos esta ronda)
    ('125220738', '125220903'),   # COMPLETO
    ('11456111', '11456276'),     # ligera
    ('125207352', '125207516'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES),
    ('qa_imp2_v351.py', VERSIONES),
    ('qa_escudo_v350.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
]

fallos = 0
for nombre, regs in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    total = 0
    for viejo, nuevo in regs:
        n = txt.count(viejo)
        if n == 0:
            print(f'FALLO: {nombre}: sello {viejo!r} ×0 (¿ya sellado o perdido?)')
            fallos += 1
            continue
        txt = txt.replace(viejo, nuevo)
        total += n
    p.write_text(txt, encoding='utf-8')
    print(f'· {nombre}: {total} sellos actualizados')

if fallos:
    sys.exit(f'{fallos} sellos sin casar — revisar')
print('· sellado en cascada a 3.6.9-SDK6 COMPLETO')

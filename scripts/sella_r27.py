#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 26b · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.20-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los ZIPs
en las capas que los llevan clavados (lección de las rondas 10-25: cada bump
necesita su sellado o el QA TOTAL compara contra la versión vieja).

Capas y sellos (configuración REAL heredada de las rondas 13-26):
  E · qa_sup1_v365.py    — versión (1)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños esperados
  I · smoke_sdk5.py      — versión (1)
  (el tag de hub v3619-sdk6 → v3620-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.19-SDK6', '3.6.20-SDK6'), ('v3619-sdk6', 'v3620-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3620 (construidos esta ronda)
    ('125257077', '125257463'),   # COMPLETO
    ('11458725', '11459111'),     # ligera
    ('125243691', '125244077'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
]

fallos = 0
for nombre, regs in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    total = 0
    ya = 0
    for viejo, nuevo in regs:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            total += n
        elif nuevo in txt:
            ya += 1          # ya sellado por una pasada anterior: OK
        else:
            print(f'FALLO: {nombre}: sello {viejo!r} ×0 y {nuevo!r} ausente')
            fallos += 1
    p.write_text(txt, encoding='utf-8')
    print(f'· {nombre}: {total} sellos actualizados · {ya} ya sellados')

if fallos:
    sys.exit(f'{fallos} sellos sin casar — revisar')
print('· sellado en cascada a 3.6.20-SDK6 COMPLETO')

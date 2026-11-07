#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 41 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.33-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-40:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
ronda — sus pines se conservan tal cual. LA LOCURA sube a v25 (MEGA
PALA 2.0 «NÚCLEO DE ENERGÍA»): sus pines se ajustan aquí.

Capas y sellos (configuración REAL heredada de las rondas 13-40):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian por el módulo locura v25)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3632-sdk6 → v3633-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.32-SDK6', '3.6.33-SDK6'), ('v3632-sdk6', 'v3633-sdk6')]
MANIFEST_LOCURA = [  # E/H: pin del manifest de locura (v24 → v25, MEGA PALA 2.0)
    # (patrones POR FICHERO: qa_sup1 clava 'v240', qa_descargas clava 'v3.6.4-SDK4')
    ("('locura', 24, 'v240')", "('locura', 25, 'v240')"),
    ("('locura', 24, 'v3.6.4-SDK4')", "('locura', 25, 'v3.6.4-SDK4')"),
]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3633 (construidos esta ronda)
    ('130789233', '130794903'),   # COMPLETO
    ('15755311', '15756274'),     # ligera
    ('130775847', '130781517'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_sup1_v365.py', MANIFEST_LOCURA[:1]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS + MANIFEST_LOCURA[1:]),
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
            ya += 1
        else:
            print(f'✗ {nombre}: ni «{viejo}» ni «{nuevo}»')
            fallos += 1
    p.write_text(txt, encoding='utf-8')
    print(f'· {nombre}: {total} sustitución(es) · {ya} ya sellada(s)')

print('OK · sella_r41' if not fallos else f'FALLOS: {fallos}')
sys.exit(1 if fallos else 0)

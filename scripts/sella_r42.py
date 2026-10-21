#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 42 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.34-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-41:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
ronda — sus pines se conservan tal cual. LA LOCURA sube a v26 (mega
al núcleo, MEGA PALA NORMATIVA): sus pines se ajustan aquí.

Capas y sellos (configuración REAL heredada de las rondas 13-41):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian por el módulo locura v26)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3633-sdk6 → v3634-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.33-SDK6', '3.6.34-SDK6'), ('v3633-sdk6', 'v3634-sdk6')]
MANIFEST_LOCURA = [  # E/H: pin del manifest de locura (v25 → v26, mega al núcleo)
    # (patrones POR FICHERO: qa_sup1 clava 'v240', qa_descargas clava 'v3.6.4-SDK4')
    ("('locura', 25, 'v240')", "('locura', 26, 'v240')"),
    ("('locura', 25, 'v3.6.4-SDK4')", "('locura', 26, 'v3.6.4-SDK4')"),
]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3634 (construidos esta ronda)
    ('130794903', '130796328'),   # COMPLETO
    ('15756274', '15762598'),     # ligera
    ('130781517', '130782942'),   # CLOUDFLARE
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
for nombre, susts in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    for viejo, nuevo in susts:
        n = txt.count(viejo)
        if n == 0 and nuevo in txt:
            print(f'  = {nombre}: {viejo} → ya sellado')
            continue
        if n == 0:
            print(f'  ✗ {nombre}: aguja no encontrada: {viejo}')
            fallos += 1
            continue
        txt = txt.replace(viejo, nuevo)
        print(f'  ✓ {nombre}: {viejo} → {nuevo} (×{n})')
    p.write_text(txt, encoding='utf-8')

print(f'SELLADO R42: {"OK" if fallos == 0 else f"{fallos} FALLOS"}')
sys.exit(1 if fallos else 0)

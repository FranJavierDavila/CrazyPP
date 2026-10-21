#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 43 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.35-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-42:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y los manifests del oeste (v56) y de la locura
(v26) NO cambian esta ronda (la mecánica vive en el núcleo) — sus pines
se conservan tal cual.

Capas y sellos (configuración REAL heredada de las rondas 13-42):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             crecen por los assets embebidos del
                             superpoder: PNG del dueño + voz TTS)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3634-sdk6 → v3635-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.34-SDK6', '3.6.35-SDK6'), ('v3634-sdk6', 'v3635-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3635 (construidos esta ronda)
    ('130796328', '130853386'),   # COMPLETO
    ('15762598', '15819293'),     # ligera
    ('130782942', '130840000'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
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

print(f'SELLADO R43: {"OK" if fallos == 0 else f"{fallos} FALLOS"}')
sys.exit(1 if fallos else 0)

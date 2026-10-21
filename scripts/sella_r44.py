#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 44 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.36-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-43:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y los manifests del oeste (v56) y de la locura
(v26) NO cambian esta ronda (la mecánica vive en el núcleo) — sus pines
se conservan tal cual.

Capas y sellos (configuración REAL heredada de las rondas 13-43):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             crecen por los assets embebidos del
                             superpoder: 2 iconos + 4 voces nativas)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3635-sdk6 → v3636-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.35-SDK6', '3.6.36-SDK6'), ('v3635-sdk6', 'v3636-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3636 (construidos esta ronda)
    ('130853386', '130921194'),   # COMPLETO
    ('15819293', '15886827'),     # ligera
    ('130840000', '130907808'),   # CLOUDFLARE
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

print('SELLA_R44:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

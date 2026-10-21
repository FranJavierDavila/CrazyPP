#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 40 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.32-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-39:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
ronda — sus pines se conservan tal cual. LA LOCURA sube a v24 (MEGA
PALA visual): si alguna capa clavara su manifest, se ajusta aquí.

Capas y sellos (configuración REAL heredada de las rondas 13-39):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian por el módulo locura v24)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  (el tag de hub v3631-sdk6 → v3632-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.31-SDK6', '3.6.32-SDK6'), ('v3631-sdk6', 'v3632-sdk6')]
MANIFEST_LOCURA = [  # E/H: pin del manifest de locura (v23 → v24, MEGA PALA visual)
    ("('locura', 23, 'v3.6.4-SDK4')", "('locura', 24, 'v3.6.4-SDK4')"),
    ("('locura', 23, 'v240')", "('locura', 24, 'v240')"),
]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3632 (construidos esta ronda)
    ('130786087', '130789233'),   # COMPLETO
    ('15754823', '15755311'),     # ligera
    ('130772701', '130775847'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_sup1_v365.py', MANIFEST_LOCURA),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS + MANIFEST_LOCURA),
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
    p.write_text(txt, encoding='utf-8')
    estado = 'YA' if (total == 0 and ya) else 'OK'
    print(f'  · {nombre}: {total} agujas ({ya} ya selladas) {estado}')
    if total == 0 and ya == 0:
        print(f'    FALLO: ni aguja ni sello nuevo en {nombre}')
        fallos += 1

print('SELLA_R40', 'OK' if fallos == 0 else f'CON {fallos} FALLOS')
sys.exit(1 if fallos else 0)

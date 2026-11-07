#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 33 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.26-SDK6.

Actualiza IN SITU los sellos de versión, los tamaños esperados de los ZIPs
y el PIN del SDK (v1.5.4 · createBucle.precarga, con TODO el v1.5.3:
play booleano + sinPend + huérfana muerta + busyAt) en las capas que los
llevan clavados (lección de las rondas 10-31: cada bump necesita su
sellado o el QA TOTAL compara contra la versión vieja).

Capas y sellos (configuración REAL heredada de las rondas 13-31):
  E · qa_sup1_v365.py    — versión + SDK v1.5.4 (literal y runtime) + oeste v56
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños + SDK v1.5.4 + oeste v56
  I · smoke_sdk5.py      — versión + sdkVer v1.5.4
  (el tag de hub v3625-sdk6 → v3626-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.25-SDK6', '3.6.26-SDK6'), ('v3625-sdk6', 'v3626-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3626 (construidos esta ronda)
    ('126303860', '126491012'),   # COMPLETO
    ('11459651', '11459748'),     # ligera
    ('126290473', '126477625'),   # CLOUDFLARE
]
SDK_PIN = [("const SDK_VERSION = '1.5.3'", "const SDK_VERSION = '1.5.4'")]
# pins del SDK vivo en las capas E/I (qa_sup1 usa el literal y el runtime;
# smoke_sdk5 exige r['sdkVer']; qa_version compara con VERSION.json — esa
# se alimenta del bump --sdk 1.5.4, no de este sellado)
SDK_EI = [
    ("const SDK_VERSION = '1.5.3'", "const SDK_VERSION = '1.5.4'"),
    ("\"window.__PP_SDK || ''\") == '1.5.3'", "\"window.__PP_SDK || ''\") == '1.5.4'"),
    ("window.__PP_SDK = 1.5.3", "window.__PP_SDK = 1.5.4"),
    ("r['sdkVer'] == '1.5.3'", "r['sdkVer'] == '1.5.4'"),
]
# manifest de oeste v55 → v56 en los adopcioneros de E/H
OESTE_V56 = [("('oeste', 55,", "('oeste', 56,")]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1] + SDK_EI[:3] + OESTE_V56),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1] + SDK_EI[3:]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS + SDK_PIN + OESTE_V56),
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

sys.exit(1 if fallos else 0)

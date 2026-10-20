#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 31 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I) a 3.6.25-SDK6.

Actualiza IN SITU los sellos de versión, los tamaños esperados de los ZIPs
y el PIN del SDK (v1.5.3 · play booleano + sinPend + huérfana muerta +
busyAt) en las capas que los llevan clavados (lección de las rondas
10-30: cada bump necesita su sellado o el QA TOTAL compara contra la
versión vieja).

Capas y sellos (configuración REAL heredada de las rondas 13-30):
  E · qa_sup1_v365.py    — versión + SDK v1.5.3 (literal y runtime) + oeste v55
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños + SDK v1.5.3 + oeste v55
  I · smoke_sdk5.py      — versión + sdkVer v1.5.3
  (el tag de hub v3624-sdk6 → v3625-sdk6 SOLO vive en la capa H)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.24-SDK6', '3.6.25-SDK6'), ('v3624-sdk6', 'v3625-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3625 (construidos esta ronda)
    ('126301679', '126303860'),   # COMPLETO
    ('11459657', '11459651'),     # ligera
    ('126288292', '126290473'),   # CLOUDFLARE
]
SDK_PIN = [("const SDK_VERSION = '1.5.2'", "const SDK_VERSION = '1.5.3'")]
# pins del SDK vivo en las capas E/I (qa_sup1 usa el literal y el runtime;
# smoke_sdk5 exige r['sdkVer']; qa_version compara con VERSION.json — esa
# se alimenta del bump --sdk 1.5.3, no de este sellado)
SDK_EI = [
    ("const SDK_VERSION = '1.5.2'", "const SDK_VERSION = '1.5.3'"),
    ("\"window.__PP_SDK || ''\") == '1.5.2'", "\"window.__PP_SDK || ''\") == '1.5.3'"),
    ("window.__PP_SDK = 1.5.2", "window.__PP_SDK = 1.5.3"),
    ("r['sdkVer'] == '1.5.2'", "r['sdkVer'] == '1.5.3'"),
]
# manifest de oeste v54 → v55 en los adopcioneros de E/H
OESTE_V55 = [("('oeste', 54,", "('oeste', 55,")]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1] + SDK_EI[:3] + OESTE_V55),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1] + SDK_EI[3:]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS + SDK_PIN + OESTE_V55),
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

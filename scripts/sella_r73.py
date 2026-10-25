#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 73 · SELLADO EN CASCADA de las capas QA a 3.6.65-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-72).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

LECCIÓN DE LA RONDA 68 APLICADA: smoke_sdk5.py ENTRA en el plan (su pin
de versión se quedó viejo en el bump anterior y el smoke cayó).

Tamaños byte-exactos de los ZIPs v3665 (ronda 73):
  COMPLETO   133.121.845 · ligera 18.066.633 · CLOUDFLARE 133.108.458

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.64-SDK6', '3.6.65-SDK6'), ('v3664-sdk6', 'v3665-sdk6')]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3665 (ronda 73, notas FASE 67 limpias)
    ('133116865', '133121845'),   # COMPLETO
    ('18061653', '18066633'),     # ligera
    ('133103478', '133108458'),   # CLOUDFLARE
    ('133122412', '133121845'),   # COMPLETO (pasada intermedia del ensamblador)
    ('18067200', '18066633'),     # ligera (pasada intermedia)
    ('133109025', '133108458'),   # CLOUDFLARE (pasada intermedia)
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('qa_poderes_iman_v3637.py', VERSIONES[:1]),
    ('qa_poderes_v3638.py', VERSIONES[:1]),
    ('qa_poderes_reset_v3639.py', VERSIONES[:1]),
    ('qa_poderes_activo_v3640.py', VERSIONES[:1]),
    ('qa_bomba_v3644.py', VERSIONES[:1]),
    ('qa_electrico_v3645.py', VERSIONES[:1]),
    ('qa_superpoderes_v3643.py', VERSIONES[:1]),
    ('qa_portal_v3642.py', VERSIONES[:1]),
    ('qa_r71_v3663.py', VERSIONES[:1]),
    ('qa_r72_v3664.py', VERSIONES[:1]),
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

fallos = 0
for nombre, reemplazos in PLAN:
    f = SCR / nombre
    if not f.exists():
        print(f'  ? {nombre}: no existe (se omite)')
        continue
    txt = f.read_text(encoding='utf-8')
    for viejo, nuevo in reemplazos:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  · {nombre}: {n}× {viejo} → {nuevo}')
        elif nuevo in txt:
            print(f'  = {nombre}: {nuevo} ya sellado')
        else:
            print(f'  ✗ {nombre}: ni {viejo} ni {nuevo} presentes')
            fallos += 1
    # tamaños de ZIPs (sólo qa_descargas los lleva)
    for viejo, nuevo in TAMANOS:
        if viejo in txt:
            txt = txt.replace(viejo, nuevo)
            print(f'    · tamaño {viejo} → {nuevo}')
    f.write_text(txt, encoding='utf-8')

print(f'\nSELLO r73 {"COMPLETO" if not fallos else "CON FALLOS: " + str(fallos)}')
sys.exit(1 if fallos else 0)

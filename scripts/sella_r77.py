#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 77 · SELLADO EN CASCADA de las capas QA a 3.6.69-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-76).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Tamaños byte-exactos de los ZIPs v3669 (ronda 77, notas FASE 71):
  COMPLETO   133.310.032 · ligera 18.254.820 · CLOUDFLARE 133.296.513
  (SOLO-RELAY 6.221, sin cambios)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.68-SDK6', '3.6.69-SDK6'), ('v3668-sdk6', 'v3669-sdk6')]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3669 (ronda 77)
    ('133309729', '133310032'),   # COMPLETO
    ('18254517', '18254820'),     # ligera
    ('133296210', '133296513'),   # CLOUDFLARE
    # SOLO-RELAY 6.221 sin cambios esta ronda
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
    ('qa_r73_v3665.py', VERSIONES[:1]),
    ('qa_r74_v3666.py', VERSIONES[:1]),   # r76 ya la dejó en 3.6.68
    ('qa_r75_v3667.py', VERSIONES[:1]),
    ('qa_r76_v3668.py', VERSIONES[:1]),   # nacida en 3.6.68: sube a 3.6.69
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
    antes = txt                 # ANTES de cualquier reemplazo (lección r76)
    for viejo, nuevo in reemplazos:
        n = txt.count(viejo)
        if n == 0:
            if nuevo in txt:
                print(f'  · {nombre}: ya sellado a {nuevo}')
            else:
                print(f'  ✗ {nombre}: aguja {viejo} ×0 y sello {nuevo} ausente')
                fallos += 1
            continue
        txt = txt.replace(viejo, nuevo)
        print(f'  ✓ {nombre}: {viejo} → {nuevo} (×{n})')
    # tamaños de ZIP (sólo capas que llevan los byte-exactos)
    for viejo, nuevo in TAMANOS:
        if txt.count(viejo):
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: tamaño {viejo} → {nuevo}')
    if txt != antes:
        f.write_text(txt, encoding='utf-8')

sys.exit(1 if fallos else 0)

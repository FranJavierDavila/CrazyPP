#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 75 · SELLADO EN CASCADA de las capas QA a 3.6.67-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-73).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Tamaños byte-exactos de los ZIPs v3667 (ronda 75, notas FASE 69):
  COMPLETO   133.304.497 · ligera 18.249.285 · CLOUDFLARE 133.291.110

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.66-SDK6', '3.6.67-SDK6'), ('v3666-sdk6', 'v3667-sdk6')]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3667 (ronda 75)
    ('133303948', '133304497'),   # COMPLETO
    ('18248736', '18249285'),     # ligera
    ('133290561', '133291110'),   # CLOUDFLARE
    ('133303948', '133304497'),   # COMPLETO (v3666, heredado por las capas)
    ('18248736', '18249285'),     # ligera (v3666, heredado)
    ('133290561', '133291110'),   # CLOUDFLARE (v3666, heredado)
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
        if n == 0:
            if nuevo in txt:
                print(f'  = {nombre}: {nuevo} ya presente (idempotente)')
            else:
                print(f'  ? {nombre}: aguja {viejo} ×0 (sin sello en esta capa)')
            continue
        txt = txt.replace(viejo, nuevo)
        print(f'  ✓ {nombre}: {viejo} → {nuevo} (×{n})')
    # tamaños de ZIP (solo capas que llevan los byte-exactos)
    cambiado = False
    for viejo, nuevo in TAMANOS:
        if txt.count(viejo):
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: tamaño {viejo} → {nuevo}')
            cambiado = True
    if cambiado or txt != open(f, encoding='utf-8').read():
        f.write_text(txt, encoding='utf-8')

# el hub /descargas lleva el pin del COMPLETO + CLOUDFLARE por mención
hub = RAIZ / 'src' / 'app' / 'descargas' / 'page.tsx'
if hub.exists():
    t = hub.read_text(encoding='utf-8')
    n = 0
    for viejo, nuevo in TAMANOS:
        if t.count(viejo):
            t = t.replace(viejo, nuevo)
            print(f'  ✓ hub: tamaño {viejo} → {nuevo}')
            n += 1
    if n:
        hub.write_text(t, encoding='utf-8')

if fallos:
    sys.exit(1)
print('SELLA r75 OK')

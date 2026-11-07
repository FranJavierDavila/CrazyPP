#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 54 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I + AF/AG/AH/AI/AK/AL/AM/AN/AO) a 3.6.46-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-54:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y los manifests del oeste (v56) y de la locura
(v26) NO cambian esta ronda (la mecánica vive en el núcleo).

Capas y sellos (configuración REAL heredada de las rondas 13-53):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian: spin real + gancho + pala metálica;
                             SOLO intacto)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  AF · qa_poderes_iman_v3637.py   — sello de versión servida (re-anclada
                                    al GANCHO, r54)
  AG · qa_poderes_v3638.py        — sello de versión servida (arsenal
                                    sin canto del imán, r54)
  AH · qa_poderes_reset_v3639.py  — sello de versión servida
  AI · qa_poderes_activo_v3640.py — sello de versión servida
  AK · qa_portal_v3642.py         — sello de versión servida
  AL · qa_superpoderes_v3643.py   — sello de versión servida (re-anclada:
                                    pala metálica + precaliente 13, r54)
  AM · qa_bomba_v3644.py          — sello de versión servida (re-anclada:
                                    negativas de campo/estela, r54)
  AN · qa_electrico_v3645.py      — sello de versión servida
  AO · qa_spin_pala_v3646.py      — NUEVA r54 (spin real + gancho + pala
                                    metálica + clamp del mango)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.45-SDK6', '3.6.46-SDK6'), ('v3645-sdk6', 'v3646-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3646 (ronda 54)
    ('131178409', '131179177'),   # COMPLETO
    ('16129241', '16129721'),     # ligera
    ('131165022', '131165790'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('smoke_sdk5.py', VERSIONES[:1]),
    ('qa_poderes_iman_v3637.py', VERSIONES[:1]),
    ('qa_poderes_v3638.py', VERSIONES[:1]),
    ('qa_poderes_reset_v3639.py', VERSIONES[:1]),
    ('qa_poderes_activo_v3640.py', VERSIONES[:1]),
    ('qa_portal_v3642.py', VERSIONES[:1]),
    ('qa_superpoderes_v3643.py', VERSIONES[:1]),
    ('qa_bomba_v3644.py', VERSIONES[:1]),
    ('qa_electrico_v3645.py', VERSIONES[:1]),
    ('qa_spin_pala_v3646.py', VERSIONES[:1]),
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
]

fallos = 0
for nombre, susts in PLAN:
    p = SCR / nombre
    if not p.exists():
        print(f'  ✗ {nombre}: FALTA el fichero')
        fallos += 1
        continue
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

print('SELLA_R54:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

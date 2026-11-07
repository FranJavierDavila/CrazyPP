#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 53 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I + AF/AG/AH/AI/AK/AL/AM/AN) a 3.6.45-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-53:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y los manifests del oeste (v56) y de la locura
(v26) NO cambian esta ronda (la mecánica vive en el núcleo y en el
módulo de la locura).

Capas y sellos (configuración REAL heredada de las rondas 13-52):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian: eléctrico + cadencia de la bomba;
                             SOLO intacto)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  AF · qa_poderes_iman_v3637.py   — sello de versión servida
  AG · qa_poderes_v3638.py        — sello de versión servida
  AH · qa_poderes_reset_v3639.py  — sello de versión servida
  AI · qa_poderes_activo_v3640.py — sello de versión servida
  AK · qa_portal_v3642.py         — sello de versión servida
  AL · qa_superpoderes_v3643.py   — sello de versión servida
  AM · qa_bomba_v3644.py          — sello de versión servida (cadencia
                                    re-anclada a los intervalos de 15 s)
  AN · qa_electrico_v3645.py      — sello de versión servida (nueva r53)

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.44-SDK6', '3.6.45-SDK6'), ('v3644-sdk6', 'v3645-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3645 (ronda 53)
    ('131171885', '131178409'),   # COMPLETO
    ('16128412', '16129241'),     # ligera
    ('131158498', '131165022'),   # CLOUDFLARE
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
    ('qa_descargas_v365.py', VERSIONES + TAMANOS),
]

fallos = 0
for nombre, susts in PLAN:
    p = SCR / nombre
    txt = p.read_text(encoding='utf-8')
    for viejo, nuevo in susts:
        if nuevo.startswith('PENDIENTE_'):
            print(f'  ⚠ {nombre}: tamaño {viejo} → {nuevo} (RELLENAR TRAS BUILD)')
            continue
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

print('SELLA_R53:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 78 · SELLADO EN CASCADA de las capas QA a 3.6.70-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-77).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Además (r78): los FIXTURES de la capa BJ (qa_r75) que pintan la caja
PODERES de la pizarra de modos se actualizan al texto nuevo «SOLO
CAMPEONATOS» — la capa mide lo que REALMENTE se sirve (los nuevos textos
son más cortos: el encaje solo puede mejorar).

Tamaños byte-exactos de los ZIPs v3670 (ronda 78, notas FASE 72):
  se rellenan tras build_zip (se dejan los marcadores del v3669 y esta
  ronda NO lleva TAMANOS hasta conocer los bytes nuevos).

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.69-SDK6', '3.6.70-SDK6'), ('v3669-sdk6', 'v3670-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3670 (ronda 78, notas FASE 72)
    ('133310032', '133382859'),   # COMPLETO
    ('18254820', '18327647'),     # ligera
    ('133296513', '133369341'),   # CLOUDFLARE
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
    ('qa_r74_v3666.py', VERSIONES[:1]),
    ('qa_r75_v3667.py', VERSIONES[:1]),
    ('qa_r76_v3668.py', VERSIONES[:1]),
    ('qa_r77_v3669.py', VERSIONES[:1]),   # nacida en 3.6.69: sube a 3.6.70
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

# r78 · la caja PODERES de la pizarra de modos: los fixtures de BJ miden
# ahora el texto que REALMENTE se sirve (más corto ⇒ encaje garantizado).
PODERES = [
    ('qa_r75_v3667.py',
     'PODERES: Mega Pala · Efecto · Imán · Portal · Clon — gatillo con la bola viva.',
     'PODERES · SOLO CAMPEONATOS: 20 toques seguidos cargan · gatillo lanza · 10 s',
     'POWERS: Mega Paddle · Spin · Magnet · Portal · Clone — trigger with a live ball.',
     'POWERS · CHAMPIONSHIPS ONLY: 20 straight hits charge · trigger fires · 10 s'),
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

for nombre, es_viejo, es_nuevo, en_viejo, en_nuevo in PODERES:
    f = SCR / nombre
    if not f.exists():
        print(f'  ? {nombre}: no existe (fixtures omitidos)')
        continue
    txt = f.read_text(encoding='utf-8')
    a = txt.count(es_viejo) + txt.count(en_viejo)
    if a == 0 and es_nuevo in txt and en_nuevo in txt:
        print(f'  · {nombre}: fixtures PODERES ya actualizados')
        continue
    txt = txt.replace(es_viejo, es_nuevo).replace(en_viejo, en_nuevo)
    f.write_text(txt, encoding='utf-8')
    print(f'  ✓ {nombre}: fixtures PODERES → «SOLO CAMPEONATOS» (ES+EN)')

sys.exit(1 if fallos else 0)

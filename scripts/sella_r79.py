#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 79 · SELLADO EN CASCADA de las capas QA a 3.6.71-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-78).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Tamaños byte-exactos de los ZIPs v3671 (ronda 79, notas FASE 73):
  COMPLETO 133.409.105 · ligera 18.353.893 · CLOUDFLARE 133.395.587
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.70-SDK6', '3.6.71-SDK6'), ('v3670-sdk6', 'v3671-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3671 (ronda 79, notas FASE 73)
    ('133382859', '133409182'),   # COMPLETO
    ('18327647', '18353970'),     # ligera
    ('133369341', '133395664'),   # CLOUDFLARE
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
    ('qa_r77_v3669.py', VERSIONES[:1]),
    ('qa_r78_v3670.py', VERSIONES[:1]),   # nacida en 3.6.70: sube a 3.6.71
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]


def sella_fichero(nombre, pares):
    p = SCR / nombre
    if not p.exists():
        print(f'  ✗ FALLO: {nombre} no existe')
        return 1
    txt = p.read_text(encoding='utf-8')
    cambios = 0
    for viejo, nuevo in pares:
        n = txt.count(viejo)
        if n == 0:
            if nuevo in txt:
                continue                     # ya sellado antes (idempotente)
            print(f'  ✗ FALLO: {nombre} — aguja {viejo!r} ×0 y sin sello nuevo')
            return 1
        txt = txt.replace(viejo, nuevo)
        cambios += n
    p.write_text(txt, encoding='utf-8')
    print(f'  ✓ {nombre}: {cambios} sello(s)')
    return 0


def main():
    fallos = 0
    print('— RONDA 79 · sellos de versión 3.6.70-SDK6 → 3.6.71-SDK6 —')
    for nombre, pares in PLAN:
        fallos += sella_fichero(nombre, pares)
    print('— tamaños byte-exactos de los ZIPs v3671 —')
    for nombre, _ in PLAN:
        if 'descargas' not in nombre:
            continue
        fallos += sella_fichero(nombre, TAMANOS)
    if fallos:
        print(f'\nSELLADO CON {fallos} FALLOS')
        sys.exit(1)
    print('\nSELLADO COMPLETO (r79 · V3.6.71-SDK6)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 81 · SELLADO EN CASCADA de las capas QA a 3.6.73-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-80).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Tamaños byte-exactos de los ZIPs v3673 (ronda 81, notas FASE 75):
  COMPLETO 133.424.463 · ligera 18.369.251 · CLOUDFLARE 133.410.944
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.72-SDK6', '3.6.73-SDK6'), ('v3672-sdk6', 'v3673-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3673 (ronda 81, notas FASE 75)
    ('133414563', '133424463'),   # COMPLETO
    ('18359351', '18369251'),     # ligera
    ('133401044', '133410944'),   # CLOUDFLARE
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
    ('qa_r78_v3670.py', VERSIONES[:1]),
    ('qa_r79_v3671.py', VERSIONES[:1]),
    ('qa_r80_v3672.py', VERSIONES[:1]),
    ('qa_r81_v3673.py', VERSIONES[:1]),   # nacida en 3.6.72: sube a 3.6.73
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
    print('— RONDA 81 · sellos de versión 3.6.72-SDK6 → 3.6.73-SDK6 —')
    for nombre, pares in PLAN:
        fallos += sella_fichero(nombre, pares)
    print('— tamaños byte-exactos de los ZIPs v3673 —')
    for nombre, _ in PLAN:
        if 'descargas' not in nombre:
            continue
        fallos += sella_fichero(nombre, TAMANOS)
    if fallos:
        print(f'\nSELLADO CON {fallos} FALLOS')
        sys.exit(1)
    print('\nSELLADO COMPLETO (r81 · V3.6.73-SDK6)')


if __name__ == '__main__':
    main()

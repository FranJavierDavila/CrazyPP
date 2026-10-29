#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 89 · SELLADO EN CASCADA de las capas QA a 3.6.81-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados. El SDK (1.5.4) NO cambia esta
ronda; hay UN cambio de núcleo (c12: bola aparcada en la sala de
campeonato) y el resto vive en el módulo halloween + su manifest.

Tamaños byte-exactos de los ZIPs v3680 (ronda 88, build_zip real):
  COMPLETO 139.947.727 · ligera 18.397.397 · CLOUDFLARE 139.933.936
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (lección de la ronda 13)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.80-SDK6', '3.6.81-SDK6'), ('v3680-sdk6', 'v3681-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3681 (ronda 89, build_zip real)
    ('139947727', '140314414'),   # COMPLETO (r88 → r89)
    ('18397397', '18396894'),     # ligera
    ('139933936', '140300623'),   # CLOUDFLARE
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
    ('qa_r81_v3673.py', VERSIONES[:1]),
    ('qa_r82_v3674.py', VERSIONES[:1]),
    ('qa_r83_v3675.py', VERSIONES[:1]),
    ('qa_r84_v3676.py', VERSIONES[:1]),
    ('qa_r85_v3677.py', VERSIONES[:1]),
    ('qa_r86_v3678.py', VERSIONES[:1]),
    ('qa_r87_v3679.py', VERSIONES[:1]),
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]


def sella_fichero(nombre, pares):
    p = SCR / nombre
    if not p.exists():
        return f'  · {nombre}: NO EXISTE (omitido)'
    txt = p.read_text(encoding='utf-8')
    cambios = 0
    for viejo, nuevo in pares:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            cambios += n
    if cambios:
        p.write_text(txt, encoding='utf-8')
        return f'  · {nombre}: {cambios} reemplazo(s)'
    if any(nuevo in txt for _, nuevo in pares):
        return f'  · {nombre}: ya sellado a la versión nueva'
    return f'  · {nombre}: sin sellos (nada que rodar)'


def main():
    print('— RONDA 88 · sellado de capas QA a 3.6.81-SDK6 —')
    for nombre, pares in PLAN:
        print(sella_fichero(nombre, pares))
    print('— tamaños byte-exactos de los ZIPs —')
    for nombre, pares in PLAN:
        pares_t = list(pares) + TAMANOS
        print(sella_fichero(nombre, pares_t))
    return 0


if __name__ == '__main__':
    sys.exit(main())

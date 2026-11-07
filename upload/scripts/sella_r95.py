#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 95 · SELLADO EN CASCADA de las capas QA a 3.6.87-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados. El SDK (1.5.4) NO cambia esta
ronda; el cambio vive en el NÚCLEO (c00 i18n · c02 MESA · c03 canales de
volumen · c06 estilo/mStats · c07 relayoutMesa · c08 chip stats · c12
menú/estilo/stats) y en los módulos (halloween/plantilla/estacion sin
cartel en duelos · oeste/magia canal música) — +25.396 B en game.html.

Tamaños byte-exactos de los ZIPs v3687 (ronda 95, build_zip real):
  COMPLETO 146.612.044 · ligera 18.408.768 · CLOUDFLARE 146.598.253
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (lección de la ronda 13)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.86-SDK6', '3.6.87-SDK6'), ('v3686-sdk6', 'v3687-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3687 (ronda 95, build_zip real)
    ('146599827', '146612044'),   # COMPLETO (r94 → r95)
    ('18397305', '18408768'),     # ligera
    ('146586035', '146598253'),   # CLOUDFLARE
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
    ('qa_r91_v3683.py', VERSIONES[:1]),
    ('qa_r92_v3684.py', VERSIONES[:1]),
    ('qa_r93_v3685.py', VERSIONES[:1]),
    ('qa_r94_v3686.py', VERSIONES[:1]),
    ('qa_r95_v3687.py', VERSIONES[:1]),
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
    print('— RONDA 95 · sellado de capas QA a 3.6.87-SDK6 —')
    for nombre, pares in PLAN:
        print(sella_fichero(nombre, pares))
    print('— tamaños byte-exactos de los ZIPs —')
    for nombre, pares in PLAN:
        pares_t = list(pares) + TAMANOS
        print(sella_fichero(nombre, pares_t))
    return 0


if __name__ == '__main__':
    sys.exit(main())

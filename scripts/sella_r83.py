#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 83 · SELLADO EN CASCADA de las capas QA a 3.6.75-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-82).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda (oeste v56,
magia v33, locura v27, orbital v17, valle_neon v5).

Tamaños byte-exactos de los ZIPs v3675 (ronda 83, notas FASE 77):
  COMPLETO 133.442.692 · ligera 18.387.480 · CLOUDFLARE 133.429.174
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.74-SDK6', '3.6.75-SDK6'), ('v3674-sdk6', 'v3675-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3675 (ronda 83, notas FASE 77)
    ('133430392', '134713641'),   # COMPLETO (real del build_zip)
    ('18375180', '18611505'),     # ligera (real del build_zip)
    ('133416873', '134700123'),   # CLOUDFLARE (real del build_zip)
    ('133442692', '134713641'),   # COMPLETO (estimación del borrador → real)
    ('18387480', '18611505'),     # ligera (estimación del borrador → real)
    ('133429174', '134700123'),   # CLOUDFLARE (estimación del borrador → real)
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
    ('qa_r81_v3673.py', VERSIONES[:1]),
    ('qa_r82_v3674.py', VERSIONES[:1]),   # nacida en 3.6.74: sube a 3.6.75
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
        return f'  · {nombre}: {cambios} sello(s) rodado(s)'
    # idempotencia: ¿el sello NUEVO ya está?
    if any(nuevo in txt for _, nuevo in pares):
        return f'  · {nombre}: ya sellado a la versión nueva'
    return f'  · {nombre}: sin sellos de versión (nada que rodar)'


def main():
    print('— RONDA 83 · sellado de capas QA a 3.6.75-SDK6 —')
    fallos = 0
    for nombre, pares in PLAN:
        print(sella_fichero(nombre, pares))
    print('— tamaños byte-exactos de los ZIPs —')
    for nombre, pares in PLAN:
        pares_t = list(pares) + TAMANOS
        print(sella_fichero(nombre, pares_t))
    print('LISTO (los tamaños van dentro de cada par: viejo→nuevo ya aplicado)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

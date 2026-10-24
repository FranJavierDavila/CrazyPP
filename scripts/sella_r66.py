#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 66 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I + AF…AO) a 3.6.58-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-65).
El SDK (1.5.4) y los manifests del oeste (v56), locura (v27), magia (v33)
y valle_neon (v5) NO cambian esta ronda.

Las capas AT-BA (r59-r66) no llevan sello de versión.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.57-SDK6', '3.6.58-SDK6'), ('v3657-sdk6', 'v3658-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3658 (ronda 66)
    ('132378999', '133096287'),   # COMPLETO
    ('17324643', '18041931'),     # ligera
    ('132365613', '133082901'),   # CLOUDFLARE
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


def sella(archivo, pares):
    p = SCR / archivo
    if not p.exists():
        return f'✗ {archivo}: NO EXISTE'
    txt = p.read_text(encoding='utf-8')
    total = 0
    for viejo, nuevo in pares:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            total += n
        elif nuevo in txt:
            pass  # ya sellado antes
        else:
            return f'✗ {archivo}: ni {viejo} ni {nuevo} (aguja perdida)'
    p.write_text(txt, encoding='utf-8')
    return f'✓ {archivo}: {total} sellos actualizados'


if __name__ == '__main__':
    fallos = 0
    for archivo, pares in PLAN:
        r = sella(archivo, pares)
        print(r)
        if r.startswith('✗'):
            fallos += 1
    print('SELLADO', 'CON FALLOS' if fallos else 'COMPLETO')
    sys.exit(1 if fallos else 0)

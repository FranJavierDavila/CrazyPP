#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 65 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I + AF…AO) a 3.6.57-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-64).
El SDK (1.5.4) y los manifests del oeste (v56), locura (v27), magia (v33)
y valle_neon (v5) NO cambian esta ronda.

Las capas AQ-AY (r59-r64) y la nueva AZ r65 (qa_r65_v3657) no llevan
sello de versión.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.56-SDK6', '3.6.57-SDK6'), ('v3656-sdk6', 'v3657-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3657 (ronda 65)
    ('131396208', '132378999'),   # COMPLETO
    ('16341852', '17324643'),     # ligera
    ('131382821', '132365613'),   # CLOUDFLARE
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
    cambio = []
    for viejo, nuevo in pares:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            cambio.append(f'{viejo}→{nuevo} ×{n}')
        elif nuevo in txt:
            cambio.append(f'{nuevo} ya sellado')
        else:
            return f'✗ {archivo}: ni {viejo} ni {nuevo} presentes'
    p.write_text(txt, encoding='utf-8')
    return f'✓ {archivo}: ' + ' · '.join(cambio)


def main():
    fallos = 0
    for archivo, pares in PLAN:
        res = sella(archivo, pares)
        print(res)
        if res.startswith('✗'):
            fallos += 1
    if fallos:
        sys.exit(f'SELLADO CON {fallos} FALLOS')
    print('SELLA_R65 COMPLETO')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 57 · SELLADO EN CASCADA de las capas QA (E/F/G/H/I + AF/AG/AH/AI/AK/AL/AM/AN/AO) a 3.6.49-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-57:
cada bump necesita su sellado o el QA TOTAL compara contra la versión
vieja). El SDK (1.5.4) y los manifests del oeste (v56) y de la locura
(v26) NO cambian esta ronda (la mecánica vive en el núcleo).
Las capas AP (qa_efecto_rally_v3647, r55), AQ (qa_poderes_10s20_v3648,
r56) y AR (qa_norma_rival_v3649, r57) no llevan sello de versión.

Capas y sellos (configuración REAL heredada de las rondas 13-57):
  E · qa_sup1_v365.py    — versión (+ SDK v1.5.4 y oeste v56 intactos)
  F · qa_imp2_v351.py    — versión (1)
  G · qa_escudo_v350.py  — versión (1)
  H · qa_descargas_v365.py — versión + tag de hub + tamaños (los ZIPs
                             cambian: la guía r57 crece un pelín el
                             núcleo; SOLO intacto)
  I · smoke_sdk5.py      — versión (+ sdkVer 1.5.4 intacto)
  AF · qa_poderes_iman_v3637.py   — sello de versión servida (REESCRITA r57)
  AG · qa_poderes_v3638.py        — sello de versión servida
  AH · qa_poderes_reset_v3639.py  — sello de versión servida
  AI · qa_poderes_activo_v3640.py — sello de versión servida
  AK · qa_portal_v3642.py         — sello de versión servida
  AL · qa_superpoderes_v3643.py   — sello de versión servida
  AM · qa_bomba_v3644.py          — sello de versión servida
  AN · qa_electrico_v3645.py      — sello de versión servida
  AO · qa_spin_pala_v3646.py      — sello de versión servida

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.48-SDK6', '3.6.49-SDK6'), ('v3648-sdk6', 'v3649-sdk6')]
TAMANOS = [  # H: tamaños byte-exactos de los ZIPs v3649 (ronda 57)
    ('131178477', '131172235'),   # COMPLETO
    ('16128890', '16119850'),     # ligera
    ('131165090', '131158848'),   # CLOUDFLARE
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
        sys.exit(1)
    print('SELLA_R57 COMPLETO')


if __name__ == '__main__':
    main()

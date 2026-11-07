#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 84 · SELLADO EN CASCADA de las capas QA a 3.6.76-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-83).
El SDK (1.5.4) y TODOS los manifests NO cambian esta ronda.

Además, dos agujas que la r84 OBSOLETA POR DISEÑO:
  · qa_superpoderes_v3643: la cuenta sonora 3·2·1 de los poderes gana un
    sexto _poderTickBlip(2) — el aviso de expiración de los poderes de
    DUELOS LOCOS comparte la misma primitiva (5→6 en la aguja (2)).
  · qa_r79_v3671 (BN): la tarjeta DUELOS LOCOS deja el patrón de bloqueo
    r79 (velo+candado+chip) — las agujas del candado pasan a verificar la
    tarjeta DESBLOQUEADA y el runtime deja de exigir _modeCardDuelos
    (método retirado: la tarjeta vive en _modeCard como sus hermanas).

Tamaños byte-exactos de los ZIPs v3676 (ronda 84, notas FASE 78):
  COMPLETO 133.443.218 · ligera 18.388.006 · CLOUDFLARE 133.429.699
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.75-SDK6', '3.6.76-SDK6'), ('v3675-sdk6', 'v3676-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3676 (ronda 84, build_zip real)
    ('134713641', '133443218'),   # COMPLETO
    ('18611505', '18388006'),     # ligera
    ('134700123', '133429699'),   # CLOUDFLARE
]

# capas que SOLO llevan sellos de versión (3.6.75 → 3.6.76)
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
    ('qa_r83_v3675.py', VERSIONES[:1]),   # nacida en 3.6.75: sube a 3.6.76
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

# agujas que la r84 obsoleta por diseño: reemplazos EXACTOS (viejo → nuevo)
AGUJAS = [
    ('qa_superpoderes_v3643.py', [
        ("game.count('this._poderTickBlip(2)') == 5 and",
         "game.count('this._poderTickBlip(2)') == 6 and"),
        ('los CINCO poderes comparten la cuenta 3·2·1 (15 llamadas)',
         'los CINCO poderes + el aviso DUELOS comparten la cuenta 3·2·1 (16 llamadas)'),
    ]),
    ('qa_r79_v3671.py', [
        ("(\"tarjeta DUELOS LOCOS (patrón candado)\", \"_modeCardDuelos\"),",
         "(\"tarjeta DUELOS LOCOS desbloqueada (r84)\", \"this._modeCard(rects, 'mjduel', 40, 326\"),"),
        ("(\"candado ENCIMA del nombre en Duelos\", \"candado(c, x + 134\", 1),",
         "(\"candado fuera de la tarjeta Duelos (r84)\", \"candado(c, x + 134\", 0),"),
        ("(\"_modeCardDuelos (def + llamada)\", \"_modeCardDuelos\", 2),",
         "(\"mjduel vía _modeCard con las hermanas (r84)\", \"rects, 'mjduel', 40, 326\", 1),"),
        ("      chk(typeof G.drawMenuMulti === 'function' && typeof G._modeCardDuelos === 'function'",
         "      chk(typeof G.drawMenuMulti === 'function' && typeof G.onNetMatchStart === 'function'"),
        ("      && typeof G.onNetMatchStart === 'function' && typeof G.onNetV2Ready === 'function',",
         "      && typeof G.onNetV2Ready === 'function' && typeof G._dlTrigger === 'function',"),
    ]),
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
    print('— RONDA 84 · sellado de capas QA a 3.6.76-SDK6 —')
    fallos = 0
    for nombre, pares in PLAN:
        print(sella_fichero(nombre, pares))
    print('— agujas obsoletas por diseño (r84) —')
    for nombre, pares in AGUJAS:
        print(sella_fichero(nombre, pares))
    print('— tamaños byte-exactos de los ZIPs —')
    for nombre, pares in PLAN:
        pares_t = list(pares) + TAMANOS
        print(sella_fichero(nombre, pares_t))
    print('LISTO (los tamaños van dentro de cada par: viejo→nuevo ya aplicado)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

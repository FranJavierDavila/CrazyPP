#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 85 · SELLADO EN CASCADA de las capas QA a 3.6.77-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados. El SDK (1.5.4) NO cambia esta
ronda. Además, la r85 RETIRA el Valle Neón (petición del dueño) y su
hueco lo ocupa HALLOWEEN — las capas que listaban campeonatos o el
candado LOCKED se re-anclan:

  · qa_r72_v3664 (BG): el candado era ['estacion_orbital','valle_neon']
    → ahora ['estacion_orbital'] (halloween nace LIBRE, juega el primer día).
  · qa_r74_v3666 (BI): orden esperado de campeonatos → halloween.
  · qa_manifiestos (C): MODOS + arte del rival del standee → halloween.
  · qa_norma_rival_v3649 (AR): URL del módulo del valle → halloween.
  · qa_r60_v3652 (AU): lista de ids de salas → halloween.
  · qa_sup1_v365 / smoke_sdk5 / qa_descargas_v366 (H): listas + sellos.
  · qa_champion_listo (L, producción): ESTADO champion → pp_champ_halloween_*.

Tamaños byte-exactos de los ZIPs v3677 (ronda 85, notas FASE 79):
  COMPLETO 135.631.128 · ligera 18.389.092 · CLOUDFLARE 135.617.337
  · SOLO-RELAY 6.221 sin cambio.

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (lección de la ronda 13)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.76-SDK6', '3.6.77-SDK6'), ('v3676-sdk6', 'v3677-sdk6')]

TAMANOS = [  # tamaños byte-exactos de los ZIPs v3677 (ronda 85, build_zip real)
    ('133443218', '135631094'),   # COMPLETO
    ('18388006', '18389058'),     # ligera
    ('133429699', '135617303'),   # CLOUDFLARE
]

# capas que SOLO llevan sellos de versión (3.6.76 → 3.6.77)
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
    ('qa_r84_v3676.py', VERSIONES[:1]),   # nacida en 3.6.76: sube a 3.6.77
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

# agujas que la r85 obsoleta por diseño: reemplazos EXACTOS (viejo → nuevo)
AGUJAS = [
    ('qa_r72_v3664.py', [
        ("static LOCKED = ['estacion_orbital', 'valle_neon'];",
         "static LOCKED = ['estacion_orbital'];"),
        ("  · CANDADOS: LOCKED = ['estacion_orbital','valle_neon'] en ChampLoader,",
         "  · CANDADOS: LOCKED = ['estacion_orbital'] en ChampLoader (r85: valle fuera),"),
        ('chk(datos.get("valle_neon") is True, "list(): valle_neon locked=true")',
         'chk(datos.get("halloween") is False, "list(): halloween libre (r85)")'),
    ]),
    ('qa_r74_v3666.py', [
        ('esperado_orden = ["locura", "magia", "oeste", "estacion_orbital", "valle_neon"]',
         'esperado_orden = ["locura", "magia", "oeste", "estacion_orbital", "halloween"]'),
    ]),
    ('qa_manifiestos.py', [
        ("MODOS = ('oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon')",
         "MODOS = ('oeste', 'magia', 'locura', 'estacion_orbital', 'halloween')  # r85"),
        ("'valle_neon': ('rival_kraken.png', '.png'),",
         "'halloween': ('present.webp', '.webp'),"),
    ]),
    ('qa_norma_rival_v3649.py', [
        ("'valle_neon': 'http://localhost:3000/championships/valle_neon/index.js',",
         "'halloween': 'http://localhost:3000/championships/halloween/index.js',"),
    ]),
    ('qa_r60_v3652.py', [
        ("const ids = ['oeste', 'locura', 'magia', 'valle_neon', 'estacion_orbital'];",
         "const ids = ['oeste', 'locura', 'magia', 'halloween', 'estacion_orbital'];  // r85"),
    ]),
    ('qa_sup1_v365.py', [
        ("('valle_neon', 5, 'v3.6.3-SDK3')", "('halloween', 1, 'r85')"),
        ("('valle_neon', 5, 'precarga', 'rival_kraken.png')", "('halloween', 1, 'precarga', 'present.webp')"),
        ("for (const m of ['oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon'])",
         "for (const m of ['oeste', 'magia', 'locura', 'estacion_orbital', 'halloween'])"),
    ]),
    ('smoke_sdk5.py', [
        ("for (const m of ['estacion_orbital', 'oeste', 'magia', 'locura', 'valle_neon'])",
         "for (const m of ['estacion_orbital', 'oeste', 'magia', 'locura', 'halloween'])"),
    ]),
    ('qa_descargas_v366.py', [
        ("('valle_neon', 5, 'v3.6.5-SDK5')", "('halloween', 1, 'r85')"),
        ('\'valle_neon\': ("import { createCartel, createMusic, createRival, getCore } from \'../sdk/champ_sdk.js\'",',
         '\'halloween\': ("createSfx, createMusic, createPowerSign, createRival, createCartel",'),
    ]),
    ('qa_champion_listo.py', [
        ("'pp_champ_valle_neon_champ': '1',", "'pp_champ_halloween_champ': '1',"),
        ("'pp_champ_valle_neon_stage': '4',", "'pp_champ_halloween_stage': '5',"),
        ("IDS = ['oeste', 'locura', 'magia', 'estacion_orbital', 'valle_neon']",
         "IDS = ['oeste', 'locura', 'magia', 'estacion_orbital', 'halloween']"),
        ("valle_neon       pp_champ_valle_neon_champ      (872 ↔ championFlag entries)",
         "halloween        pp_champ_halloween_champ     (r85 · plantilla)"),
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
    print('— RONDA 85 · sellado de capas QA a 3.6.77-SDK6 —')
    for nombre, pares in PLAN:
        print(sella_fichero(nombre, pares))
    print('— agujas obsoletas por diseño (r85 · valle_neon → halloween) —')
    for nombre, pares in AGUJAS:
        print(sella_fichero(nombre, pares))
    print('— tamaños byte-exactos de los ZIPs —')
    for nombre, pares in PLAN:
        pares_t = list(pares) + TAMANOS
        print(sella_fichero(nombre, pares_t))
    return 0


if __name__ == '__main__':
    sys.exit(main())

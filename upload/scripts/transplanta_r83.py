#!/usr/bin/env python3
"""transplanta_r83 — lleva los hunks r83 de public/game.html (QA verde,
sha 2f687b6c…) a los módulos src/game/core/ (que están en V3.6.74, golden
d7edefe3…). El build (bump_version → build_game) regenerará game.html
byte-exacto desde los módulos.

  · Los hunks de SELLO DE VERSIÓN (const VERSION en c00, badge en 03_body)
    se OMITEN: los aplica bump_version.py (camino legítimo).
  · Cada módulo guarda copia .pre_r83 antes de escribir.
"""
import difflib
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
MARK_INI = b'DEPS-FASE2-INICIO'
MARK_FIN = b'DEPS-FASE2-FIN'
RE_EXPORT = re.compile(rb'^export (?=(?:async function\b|function\b|class\b|const\b|let\b|var\b))')

# sellos que NO transplanta (los hace bump_version)
SELLOS = (b"const VERSION = '3.6.75-SDK6'", b'>V3.6.75-SDK6</span>')


def pieza_pura(datos):
    lineas = datos.split(b'\n')
    fuera, saltando = [], False
    for l in lineas:
        if MARK_INI in l:
            saltando = True
            continue
        if MARK_FIN in l:
            saltando = False
            continue
        if not saltando:
            fuera.append(RE_EXPORT.sub(b'', l))
    return b'\n'.join(fuera)


ORDER = ['00_head.html', '01_vendor.html', '02_importmap.html', '03_body.html',
         '04_boot.html', '05_module_open.html',
         'core/c00_pre_three.js', 'core/c01_modelos_3d.js', 'core/c02_cfg_escena.js',
         'core/c03_audio_voz.js', 'core/c04_fisica_ccd.js', 'core/c05_colisiones_ia_golpeo.js',
         'core/c06_logros_stats_ia_rival.js', 'core/c07_escena_sala.js', 'core/c08_hall_hud.js',
         'core/c09_red_netlink.js', 'core/c09b_red_nucleo.js', 'core/c10_menu_saque.js',
         'core/c11_champloader.js', 'core/c12_pingponggame.js', 'core/c13_ui_arranque.js',
         '06_module_close.html', '07_tail.html']

# 1 · rangos de cada pieza en el ensamblado de referencia (EN LÍNEAS)
# OJO: cada pieza que acaba en \n aporta una línea fantasma al hacer split,
# pero el JOIN con la pieza siguiente la consume (frontera) — sólo la ÚLTIMA
# pieza conserva su fantasma en el fichero completo.
ranges = []
off = 0
for idx, n in enumerate(ORDER):
    d = (SRC / n).read_bytes()
    d = pieza_pura(d) if n.startswith('core/') else d
    nl = len(d.split(b'\n'))
    ultima = (idx == len(ORDER) - 1)
    if d.endswith(b'\n') and not ultima:
        nl -= 1                       # fantasma consumido en la frontera
    ranges.append((n, off, off + nl))
    off += nl

ref = (RAIZ / '/tmp/ref_v3674.html'.lstrip('/')).read_bytes() if False else Path('/tmp/ref_v3674.html').read_bytes()
cur = (RAIZ / 'public/game.html').read_bytes()
ref_lines = ref.split(b'\n')
cur_lines = cur.split(b'\n')
sm = difflib.SequenceMatcher(None, ref_lines, cur_lines, autojunk=False)
opcodes = sm.get_opcodes()


def line_off(lines, upto):
    return sum(len(l) + 1 for l in lines[:upto])


# 2 · procesar cada pieza con hunks
objetivos = ['03_body.html', 'core/c00_pre_three.js', 'core/c08_hall_hud.js',
             'core/c12_pingponggame.js', 'core/c13_ui_arranque.js']
resumen = []
for pieza in objetivos:
    path = SRC / pieza
    mod_lines = path.read_bytes().split(b'\n')
    L1 = next(a for n, a, b in ranges if n == pieza)
    L2 = next(b for n, a, b in ranges if n == pieza)
    total_asm = L2 - L1

    # mapa línea ensamblada → línea de módulo (pieza_pura inversa)
    map_inv = [-1] * total_asm
    saltando = False
    k = 0
    for idx, line in enumerate(mod_lines):
        if MARK_INI in line:
            saltando = True
            continue
        if MARK_FIN in line:
            saltando = False
            continue
        if saltando:
            continue
        if k < total_asm:
            map_inv[k] = idx
        k += 1
    if k < total_asm:
        sys.exit(f'FALLO: {pieza} emite {k} líneas ensambladas < {total_asm} '
                 f'(la diferencia por encima se asume fantasma de frontera)')
    if any(m < 0 for m in map_inv):
        sys.exit(f'FALLO: {pieza} tiene líneas ensambladas sin módulo')

    # hunks de esta pieza (en espacio ensamblado), omitiendo sellos
    hunks = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            continue
        if not (L1 <= i1 < L2):
            continue
        nuevo = b'\n'.join(cur_lines[j1:j2])
        if any(s in nuevo for s in SELLOS):
            print(f'  · {pieza}: hunk de SELLO omitido (lo aplica bump_version)')
            continue
        hunks.append((tag, i1 - L1, i2 - L1, j1, j2))
    if not hunks:
        continue

    nuevo_mod = []
    m = 0
    saltadas = 0
    for tag, a1, a2, j1, j2 in hunks:
        mi1 = map_inv[a1]
        nuevo_mod.extend(mod_lines[m:mi1])
        m = mi1
        if tag in ('replace', 'delete'):
            # líneas de módulo que emiten [a1, a2)
            mi2 = map_inv[a2] if a2 < total_asm else len(mod_lines)
            saltadas += mi2 - m
            m = mi2
        if tag in ('replace', 'insert'):
            nuevo_mod.extend(cur_lines[j1:j2])
    nuevo_mod.extend(mod_lines[m:])

    bak = path.with_suffix(path.suffix + '.pre_r83')
    shutil.copy2(path, bak)
    path.write_bytes(b'\n'.join(nuevo_mod))
    add = sum(1 for t, _, _, j1, j2 in hunks if t in ('insert', 'replace') for _ in range(j2 - j1))
    resumen.append(f'{pieza}: {len(hunks)} hunks · +{add} · -{saltadas} (copia {bak.name})')

print('— TRANSPLANTE r83 —')
for r in resumen:
    print('  ✓', r)
print('LISTO. Siguiente: bump_version.py 3.6.75-SDK6 --fase 77 …')

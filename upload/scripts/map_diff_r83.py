#!/usr/bin/env python3
"""map_diff_r83 — atribuye el diff game.html(actual) vs ensamblado V3.6.74
a las piezas src/game/ y genera parches por módulo."""
import difflib
import re
from pathlib import Path

SRC = Path('/home/z/my-project/src/game')
MARK_INI = b'DEPS-FASE2-INICIO'; MARK_FIN = b'DEPS-FASE2-FIN'
RE_EXPORT = re.compile(rb'^export (?=(?:async function\b|function\b|class\b|const\b|let\b|var\b))')

def pieza_pura(datos):
    lineas = datos.split(b'\n'); fuera, saltando = [], False
    for l in lineas:
        if MARK_INI in l: saltando = True; continue
        if MARK_FIN in l: saltando = False; continue
        if not saltando: fuera.append(RE_EXPORT.sub(b'', l))
    return b'\n'.join(fuera)

ORDER = ['00_head.html', '01_vendor.html', '02_importmap.html', '03_body.html',
         '04_boot.html', '05_module_open.html',
         'core/c00_pre_three.js', 'core/c01_modelos_3d.js', 'core/c02_cfg_escena.js',
         'core/c03_audio_voz.js', 'core/c04_fisica_ccd.js', 'core/c05_colisiones_ia_golpeo.js',
         'core/c06_logros_stats_ia_rival.js', 'core/c07_escena_sala.js', 'core/c08_hall_hud.js',
         'core/c09_red_netlink.js', 'core/c09b_red_nucleo.js', 'core/c10_menu_saque.js',
         'core/c11_champloader.js', 'core/c12_pingponggame.js', 'core/c13_ui_arranque.js',
         '06_module_close.html', '07_tail.html']

# rangos de cada pieza en el ensamblado
ranges = []
off = 0
for n in ORDER:
    d = (SRC / n).read_bytes()
    d = pieza_pura(d) if n.startswith('core/') else d
    ranges.append((n, off, off + len(d)))
    off += len(d)

ref = Path('/tmp/ref_v3674.html').read_bytes()
cur = Path('/home/z/my-project/public/game.html').read_bytes()

ref_lines = ref.split(b'\n')
cur_lines = cur.split(b'\n')
sm = difflib.SequenceMatcher(None, ref_lines, cur_lines, autojunk=False)

# acumular rangos de líneas modificadas por pieza
from collections import defaultdict
hunks = defaultdict(list)   # módulo → lista de (tag, i1,i2, j1,j2, resumen)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    # ubicar por la línea de inicio del hunk (byte offset aproximado)
    byte_off = sum(len(l) + 1 for l in ref_lines[:i1])
    pieza = next((n for n, a, b in ranges if a <= byte_off < b), '?')
    ref_frag = b' '.join(ref_lines[i1:min(i1+2, i2)])[:90]
    cur_frag = b' '.join(cur_lines[j1:min(j1+2, j2)])[:90]
    hunks[pieza].append((tag, i2 - i1, j2 - j1, ref_frag.decode('utf-8', 'replace'),
                         cur_frag.decode('utf-8', 'replace')))

total_add = total_del = 0
for pieza in sorted(hunks):
    hs = hunks[pieza]
    a = sum(h[2] for h in hs); d = sum(h[1] for h in hs)
    total_add += a; total_del += d
    print(f'\n### {pieza} · {len(hs)} hunks (+{a} / -{d} líneas)')
    for tag, nd, na, rf, cf in hs[:60]:
        print(f'  [{tag:8}] -{nd:+4}/+{na:+4}  ref: {rf[:70]}')
        if tag in ('replace', 'insert'):
            print(f'  {" ":18} nuevo: {cf[:70]}')
print(f'\nTOTAL hunks: {sum(len(v) for v in hunks.values())} (+{total_add}/-{total_del} líneas)')

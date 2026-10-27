#!/usr/bin/env python3
"""transplanta_r83_v2 — versión corregida del transplante:
  · Rangos SIEMPRE desde los módulos ORIGINALES (pre_r83 = V3.6.74).
  · El insert de frontera c12/c13 (createPalaAxes) va al FINAL de c12
    (la declaración de función se eleva: orden equivalente en runtime).
  · Los sellos de versión se omiten (bump_version.py los aplica).
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

# origen de cada pieza: los hunks se buscan contra el estado PRE-transplante
def origen(nombre):
    p = SRC / nombre
    bak = p.with_suffix(p.suffix + '.pre_r83')
    return bak if bak.exists() else p


# 1 · rangos EN LÍNEAS desde los ORIGINALES
ranges = []
off = 0
for idx, n in enumerate(ORDER):
    d = origen(n).read_bytes()
    d = pieza_pura(d) if n.startswith('core/') else d
    nl = len(d.split(b'\n'))
    ultima = (idx == len(ORDER) - 1)
    if d.endswith(b'\n') and not ultima:
        nl -= 1
    ranges.append((n, off, off + nl))
    off += nl

ref_lines = Path('/tmp/ref_v3674.html').read_bytes().split(b'\n')
cur_lines = (RAIZ / 'public/game.html').read_bytes().split(b'\n')
sm = difflib.SequenceMatcher(None, ref_lines, cur_lines, autojunk=False)

objetivos = ['03_body.html', 'core/c00_pre_three.js', 'core/c08_hall_hud.js',
             'core/c12_pingponggame.js', 'core/c13_ui_arranque.js']
bloque_c13_frontera = None
resumen = []

for pieza in objetivos:
    path = SRC / pieza
    mod_lines = origen(pieza).read_bytes().split(b'\n')
    L1 = next(a for n, a, b in ranges if n == pieza)
    L2 = next(b for n, a, b in ranges if n == pieza)
    total_asm = L2 - L1

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
        sys.exit(f'FALLO: {pieza} emite {k} < {total_asm}')
    if any(v < 0 for v in map_inv):
        sys.exit(f'FALLO: {pieza} sin mapa completo')

    nuevo = []
    m = 0
    saltadas = 0
    nh = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal' or not (L1 <= i1 < L2):
            continue
        a1, a2 = i1 - L1, i2 - L1
        txt = b'\n'.join(cur_lines[j1:j2])
        if any(s in txt for s in SELLOS):
            print(f'  · {pieza}: sello omitido (bump_version lo aplica)')
            continue
        # el insert de FRONTERA al inicio de c13 (createPalaAxes) → final de c12
        if pieza.endswith('c13_ui_arranque.js') and tag == 'insert' and a1 == 0:
            bloque_c13_frontera = cur_lines[j1:j2]
            print(f'  · c13: insert de frontera ({len(bloque_c13_frontera)} líneas) '
                  f'reservado para el FINAL de c12')
            continue
        mi1 = map_inv[a1]
        nuevo.extend(mod_lines[m:mi1])
        m = mi1
        if tag in ('replace', 'delete'):
            mi2 = map_inv[a2] if a2 < total_asm else len(mod_lines)
            saltadas += mi2 - m
            m = mi2
        if tag in ('replace', 'insert'):
            nuevo.extend(cur_lines[j1:j2])
            nh += 1
    nuevo.extend(mod_lines[m:])
    path.write_bytes(b'\n'.join(nuevo))
    resumen.append(f'{pieza}: {nh} hunks aplicados · -{saltadas} líneas')

for r in resumen:
    print('  ✓', r)

if bloque_c13_frontera:
    p12 = SRC / 'core/c12_pingponggame.js'
    t12 = p12.read_bytes()
    if not t12.endswith(b'\n'):
        t12 += b'\n'
    p12.write_bytes(t12 + b'\n'.join(bloque_c13_frontera) + b'\n')
    print(f'  ✓ c12: + createPalaAxes ({len(bloque_c13_frontera)} líneas) al final')

print('LISTO.')

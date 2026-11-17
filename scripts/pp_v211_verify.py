#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2.111 · VERIFICACIÓN estática de Crazy Ping Pong.

Comprueba: banner de versión, existencia de los nuevos assets, sintaxis JS
del módulo oeste (node --check) y de TODOS los <script> inline del núcleo
(extraídos a .mjs), y los cambios clave del menú (OPCIONES único) y del
parallax (p1_horizonte + arena + sandTexs + override de música).
"""
import io
import os
import re
import subprocess
import sys

ROOT = '/home/z/my-project/game'
CORE = os.path.join(ROOT, 'index.html')
MOD = os.path.join(ROOT, 'championships', 'oeste', 'index.js')
PX = os.path.join(ROOT, 'championships', 'oeste', 'assets', 'parallax')

ok = True


def check(name, cond, extra=''):
    global ok
    tag = 'OK ' if cond else 'FAIL'
    if not cond:
        ok = False
    print(f'[{tag}] {name}' + (f' · {extra}' if extra else ''))


def main():
    core = io.open(CORE, encoding='utf-8').read()
    mod = io.open(MOD, encoding='utf-8').read()

    # ---- assets nuevos ----
    check('asset p1_horizonte.png', os.path.isfile(os.path.join(PX, 'p1_horizonte.png')))
    check('asset arena.jpg', os.path.isfile(os.path.join(PX, 'arena.jpg')))
    check('asset vagon.mp3',
          os.path.isfile(os.path.join(ROOT, 'championships', 'oeste', 'assets', 'vagon.mp3')))
    import struct

    def png_size(path):
        with open(path, 'rb') as f:
            f.seek(16)
            w, h = struct.unpack('>II', f.read(8))
        return w, h

    w, h = png_size(os.path.join(PX, 'p1_horizonte.png'))
    check('p1_horizonte 4344x524', (w, h) == (4344, 524), f'{w}x{h}')

    # ---- banner ----
    check('banner build v2.111', 'build v2.111' in core[:400])

    # ---- módulo oeste: parallax v2.111 ----
    check('P1 usa p1_horizonte.png', "A('parallax/p1_horizonte.png')" in mod)
    check('suelo usa arena.jpg', "A('parallax/arena.jpg')" in mod)
    check('sandTexs existe', 'this.sandTexs' in mod)
    check('scroll de arena en fxStep', 'st.offset.y' in mod)
    check('groundY definido', 'groundY: -0.15' in mod)
    check('cy P1 recalibrado (24.2)', 'cy: 24.2' in mod)
    check('sin lienzo procedural P1', '_layerCanvas' not in mod)
    check('sin _buildPano runtime', '_buildPano' not in mod)
    check('piezas p2 apoyadas en arena', 'feet: -0.45, jitF: 0.45' in mod)
    check('piezas p3 apoyadas en arena', 'feet: -0.30, jitF: 0.30' in mod)
    check('piezas p4 apoyadas en arena', 'feet: -0.18, jitF: 0.18' in mod)
    check('sin planos procedurales de terreno (k=1..3)',
          'this._layerCanvases' not in mod)

    # ---- música del vagón ----
    check("override con vagon.mp3", "musicSetOverride(OE_A('vagon.mp3'))" in mod)
    check('clear override en dispose', 'musicClearOverride()' in mod)
    check('preload durante el cartel', '_musicPreload(OE_A' in mod)
    check('caché por URL', '_musicBufs' in mod)
    check('musicOff limpia override', 'this._musicOvrUrl = null' in mod)

    # ---- menú: OPCIONES único ----
    check("hub: tarjeta page:opts", "this._modeCard(rects, 'page:opts', X0, y + 18, 912, 132" in core)
    check('hub: sin dock de ajustes rápidos',
          "label(T('dock_label')" not in core)
    check('hub: sin botón themecyc', "btn('themecyc'" not in core)
    check('hub: sin botones diff sueltos',
          core.count("btn('diff:easy'") == 1)          # sólo en OPCIONES
    check('hub: sin botones pname sueltos',
          core.count("btn('pname'") == 1)              # sólo en OPCIONES
    check('i18n es page_opts OPCIONES', "page_opts: 'OPCIONES ›'" in core)
    check('i18n es opts_title OPCIONES', "opts_title: 'OPCIONES'" in core)
    check('i18n en opts_title OPTIONS', "opts_title: 'OPTIONS'" in core)
    check('icono engranaje opts', 'opts(c, x, y) {' in core)
    check('dificultad en página OPCIONES',
          core.count("btn('diff:medium'") == 1)

    # ---- sintaxis: módulo ----
    r = subprocess.run(['node', '--check', MOD], capture_output=True, text=True)
    check('node --check módulo oeste', r.returncode == 0, r.stderr.strip()[:200])

    # ---- sintaxis: scripts inline del núcleo (sólo JS; importmap=JSON) ----
    blocks = re.findall(r'<script([^>]*)>(.*?)</script>', core, re.S | re.I)
    scripts = []
    for attrs, sc in blocks:
        t = re.search(r'type="([^"]+)"', attrs or '', re.I)
        ty = (t.group(1) if t else 'text/javascript').lower()
        if 'json' in ty or 'importmap' in ty:
            continue
        scripts.append(sc)
    check('scripts inline encontrados', len(scripts) >= 1, f'{len(scripts)} bloques JS')
    tmp = '/home/z/my-project/scripts/_core_inline'
    os.makedirs(tmp, exist_ok=True)
    all_ok = True
    for i, sc in enumerate(scripts):
        if not sc.strip():
            continue
        f = os.path.join(tmp, f'core_{i}.mjs')
        io.open(f, 'w', encoding='utf-8').write(sc)
        r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if r.returncode != 0:
            all_ok = False
            print('   fallo bloque', i, r.stderr[:300])
    check('node --check scripts inline del núcleo', all_ok)

    print('\nRESULTADO:', 'TODO OK' if ok else 'HAY FALLOS')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

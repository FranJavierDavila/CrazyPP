#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_trazo_palas_r47.py — r47 · REGENERA ARCANO_PALAS_TRAZO desde la NUEVA
palas.png del dueño (logo CRAZY PING PONG: texto macizo + pala + bola).

La r45 extraía el ESQUELETO de trazos finos (silueta lineal); el arte nuevo
es ARTE MACIZO (letras rellenas), así que el trazado a bolígrafo sigue el
CONTORNO (marching squares sobre el canal alfa suavizado, skimage) — el
efecto de escritura se mantiene igual: polilíneas normalizadas x −0.5..0.5,
y abajo→arriba positivo, consumidas por montaConstelacion() en c08.

Salida: reemplaza la línea `const ARCANO_PALAS_TRAZO = [...];` de
src/game/core/c08_hall_hud.js (misma convención r45, contorno en vez de
esqueleto). Sin tocar nada más.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from skimage import measure

RAIZ = Path('/home/z/my-project')
IMG = RAIZ / 'upload' / 'palas.png'
C08 = RAIZ / 'src' / 'game' / 'core' / 'c08_hall_hud.js'

EPS = 1.6          # Douglas-Peucker (px) — suaviza sin perder letra
MIN_PERIM = 26.0   # contornos más cortos se descartan (ruido del alfa)
MAX_PTS = 240      # techo de puntos por polilínea (decimado uniforme)
DEC = 4            # decimales por coordenada


def dp_simplifica(pts, eps):
    """Douglas-Peucker iterativo (pts: ndarray (N,2))."""
    n = len(pts)
    if n < 3:
        return pts
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[-1] = True
    pila = [(0, n - 1)]
    while pila:
        i0, i1 = pila.pop()
        if i1 <= i0 + 1:
            continue
        seg = pts[i1] - pts[i0]
        L = np.hypot(*seg) or 1e-9
        sub = pts[i0 + 1:i1]
        d = np.abs(np.cross(seg, sub - pts[i0])) / L
        imax = int(np.argmax(d))
        if d[imax] > eps:
            j = i0 + 1 + imax
            keep[j] = True
            pila.append((i0, j))
            pila.append((j, i1))
    return pts[keep]


def main():
    im = Image.open(IMG).convert('RGBA')
    W, H = im.size
    al = np.asarray(im, dtype=np.float64)[:, :, 3] / 255.0
    m = gaussian_filter(al, 1.1)                 # bordes estables
    conts = measure.find_contours(m, 0.5)        # (row, col) — cerrados
    trazos = []
    for c in conts:
        per = float(np.hypot(*np.diff(c, axis=0).T).sum())
        if per < MIN_PERIM:
            continue
        c2 = c[:-1] if len(c) > 1 and np.allclose(c[0], c[-1]) else c
        pts = dp_simplifica(c2, EPS)
        if len(pts) < 4:
            continue
        if len(pts) > MAX_PTS:                   # decimado uniforme
            idx = np.linspace(0, len(pts) - 1, MAX_PTS).round().astype(int)
            idx = np.unique(idx)
            pts = pts[idx]
        # (row, col) px → normalizado del dueño: x −0.5..0.5 · y abajo→arriba
        norm = np.stack([(pts[:, 1] / W) - 0.5, 0.5 - (pts[:, 0] / H)], axis=1)
        trazos.append((per, norm))
    trazos.sort(key=lambda t: -t[0])             # el trazo mayor abre la escena
    print(f'polilíneas: {len(trazos)} · puntos: {sum(len(t[1]) for t in trazos)}')
    if not (8 <= len(trazos) <= 140):
        sys.exit(f'FATAL: {len(trazos)} polilíneas — fuera de rango sano')
    # — serialización compacta, MISMO formato r45 —
    partes = []
    for _, norm in trazos:
        p = '[' + ','.join('[%.*f,%.*f]' % (DEC, x, DEC, y) for x, y in norm) + ']'
        partes.append(p)
    linea = 'const ARCANO_PALAS_TRAZO = [' + ','.join(partes) + '];'
    src = C08.read_text(encoding='utf-8')
    nuevo, n = re.subn(r'const ARCANO_PALAS_TRAZO = \[.*?\];', linea, src,
                       count=1, flags=re.S)
    if n != 1:
        sys.exit('FATAL: no encontré la línea ARCANO_PALAS_TRAZO en c08')
    C08.write_text(nuevo, encoding='utf-8')
    print(f'OK -> {C08.name} ({len(linea)//1024} KB de trazo)')


if __name__ == '__main__':
    main()

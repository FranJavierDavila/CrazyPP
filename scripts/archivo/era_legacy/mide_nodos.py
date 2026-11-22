#!/usr/bin/env python3
"""Mide el CENTRO de cada medallón dorado en el mapa.png nuevo:
pixels «oro» (R alto, G medio, B bajo) por fila/columna dentro de una
ventana ±130 px; el ancho de fila descarta la estrella (más estrecha)."""
import numpy as np
from PIL import Image

im = np.asarray(Image.open('/home/z/my-project/upload/mapa.png').convert('RGB')).astype(int)
NODOS = [((198, 341), 'viejo'), ((516, 456), 'viejo'), ((863, 313), 'viejo'),
         ((1173, 462), 'viejo'), ((1536, 269), 'viejo')]

for (x0, y0), _ in NODOS:
    w = im[y0 - 150:y0 + 150, x0 - 150:x0 + 150]
    R, G, B = w[:, :, 0], w[:, :, 1], w[:, :, 2]
    oro = (R > 190) & (G > 130) & (G < 215) & (B < 130) & (R - B > 90)
    filas = oro.sum(axis=1)
    cols = oro.sum(axis=0)
    if filas.max() == 0:
        print(f'nodo ({x0},{y0}): sin oro'); continue
    # filas del MEDALLÓN: >=55% del máximo (la estrella aporta menos)
    fs = np.where(filas >= 0.55 * filas.max())[0]
    cs = np.where(cols >= 0.45 * cols.max())[0]
    cy = int((fs.min() + fs.max()) / 2) - 150 + y0
    cx = int((cs.min() + cs.max()) / 2) - 150 + x0
    dy, dx = cy - y0, cx - x0
    print(f'nodo ({x0:4d},{y0:3d})  medallón medido ({cx:4d},{cy:3d})  Δx={dx:+3d} Δy={dy:+3d}')

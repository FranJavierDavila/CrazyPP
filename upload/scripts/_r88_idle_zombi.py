#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r88 · Nueva pose IDLE del zombi (informe del dueño: «sustituye la
posición idle de zombi por la que te adjunto, la que tienes tiene un
error»). Fuente: upload/zombi_idle.png (512x1024 RGBA, alfa del dueño).
Pipeline idéntico al de las 12 poses (r85): limpiado quirúrgico del
perímetro superior/lateral (8 px, pies intactos) → webp q90 method 6.
Salida: public/championships/halloween/assets/idle.webp"""
from PIL import Image
import os, shutil

RAIZ = '/home/z/my-project'
SRC = os.path.join(RAIZ, 'upload', 'zombi_idle.png')
OUT = os.path.join(RAIZ, 'public', 'championships', 'halloween', 'assets', 'idle.webp')
BAK = os.path.join(RAIZ, 'scripts', '_r88_idle_anterior.webp')

img = Image.open(SRC).convert('RGBA')
w, h = img.size
px = img.load()
# diagnóstico: ¿el arte toca los bordes laterales? (igual que r85)
toca_izq = any(px[0, y][3] > 30 for y in range(100, h - 100, 25))
toca_der = any(px[w - 1, y][3] > 30 for y in range(100, h - 100, 25))
M = 8
for y in range(h):
    if y >= h - 2:
        continue                          # pies al borde inferior: intactos
    for x in list(range(M)) + list(range(w - M, w)):
        if y < M or (x < M and toca_izq) or (x >= w - M and toca_der):
            p = list(px[x, y]); p[3] = 0; px[x, y] = tuple(p)
    for x in range(M, w - M):
        if y < M:
            p = list(px[x, y]); p[3] = 0; px[x, y] = tuple(p)

if os.path.exists(OUT):
    shutil.copy2(OUT, BAK)
img.save(OUT, 'WEBP', quality=90, method=6)
print('idle.webp nuevo: %d B (antes: %s B, respaldo en scripts/_r88_idle_anterior.webp)' % (
    os.path.getsize(OUT), os.path.getsize(BAK) if os.path.exists(BAK) else 'n/a'))
print('toca_izq=%s toca_der=%s' % (toca_izq, toca_der))
print('OK r88 idle')

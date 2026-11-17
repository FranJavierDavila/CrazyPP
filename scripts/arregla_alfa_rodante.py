"""V2.125 · Repara el canal alfa de rodante.png (Oeste, TORMENTA DE ARENA). v2

v1 ya quitó tablero y fondo; quedaban (a) halo blanco perimetral y
(b) bolsas blancas ENCERRADAS entre ramas. Esta pasada añade:
  · Des-contaminación de borde: en la banda de 6 px junto al fondo, el alfa
    se atenúa según la distancia de color al blanco del estudio (sin tocar
    ramas marrones/oscuras).
  · Bolsas encerradas: componentes conexas de píxeles blancos-acromáticos
    NO conectadas al borde, pequeñas (≤2600 px) y de color uniforme ≈ fondo
    → alfa 0 con pluma (son estudio visto entre ramas).
"""
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

SRC = '/home/z/my-project/public/championships/oeste/assets/rodante.png'
BKUP = '/home/z/my-project/scripts/respaldos/rodante.orig.png'
CHK = '/tmp/rodante_compos.png'

import shutil

shutil.copyfile(BKUP, SRC)  # siempre desde el ORIGINAL del artista

im = Image.open(SRC).convert('RGBA')
arr = np.array(im).astype(np.float64)
h, w = arr.shape[:2]
r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
mx = np.maximum(np.maximum(r, g), b)
mn = np.minimum(np.minimum(r, g), b)
sat = mx - mn
lum = (r + g + b) / 3.0

# 1. fondo conectado al borde
bgish = ((sat < 22) & (lum > 150)) | (a < 25)
mask = np.zeros((h, w), dtype=bool)
dq = deque()
for x in range(w):
    for y in (0, h - 1):
        if bgish[y, x]:
            mask[y, x] = True
            dq.append((y, x))
for y in range(h):
    for x in (0, w - 1):
        if bgish[y, x]:
            mask[y, x] = True
            dq.append((y, x))
while dq:
    y, x = dq.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and bgish[ny, nx]:
            mask[ny, nx] = True
            dq.append((ny, nx))

# 1b. HISTÉRESIS: crecimiento laxo desde el fondo estricto — come el suelo
# en sombra (grises lum 106-150) y el tablero negro (lum<45) conectado,
# sin saltar a las ramas (sat<26).
laxo = (sat < 26) & ((lum > 106) | (lum < 45))
visto = mask.copy()
dq = deque()
for y, x in zip(*np.where(mask)):
    dq.append((y, x))
while dq:
    y, x = dq.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if (0 <= ny < h and 0 <= nx < w and not visto[ny, nx]
                and laxo[ny, nx]):
            visto[ny, nx] = True
            mask[ny, nx] = True
            dq.append((ny, nx))
mask = visto

# 2. distancia BFS al fondo (capas de 1 px)
dist = np.full((h, w), 9999, dtype=np.int32)
dq = deque()
for y, x in zip(*np.where(mask)):
    dist[y, x] = 0
    dq.append((y, x))
while dq:
    y, x = dq.popleft()
    d0 = dist[y, x]
    if d0 >= 8:
        continue
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and dist[ny, nx] > d0 + 1:
            dist[ny, nx] = d0 + 1
            dq.append((ny, nx))

# 3. des-contaminación de borde: banda 1..6 px, blanco → alfa ↓
dcol = np.maximum(np.maximum(np.abs(r - 226), np.abs(g - 226)), np.abs(b - 226))
banda = (dist >= 1) & (dist <= 6) & (~mask)
factor = np.clip((dcol - 16.0) / 46.0, 0.0, 1.0)
a = np.where(banda, a * factor, a)

# 4. bolsas blancas ENCERRADAS (estudio visto entre ramas)
blanco = (sat < 20) & (lum > 192) & (a > 200) & (~mask)
etiq = np.zeros((h, w), dtype=np.int32)
nxt = 0
quitar = np.zeros((h, w), dtype=bool)
for y0, x0 in zip(*np.where(blanco)):
    if etiq[y0, x0]:
        continue
    nxt += 1
    comp = [(y0, x0)]
    etiq[y0, x0] = nxt
    dq.append((y0, x0))
    toca_borde = False
    while dq:
        y, x = dq.popleft()
        if y in (0, h - 1) or x in (0, w - 1):
            toca_borde = True
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and blanco[ny, nx] and not etiq[ny, nx]:
                etiq[ny, nx] = nxt
                comp.append((ny, nx))
                dq.append((ny, nx))
    if not toca_borde and len(comp) <= 2600:
        ys = [p[0] for p in comp]
        xs = [p[1] for p in comp]
        med = [np.median(arr[ys, xs, c]) for c in range(3)]
        if max(abs(med[0] - 226), abs(med[1] - 226), abs(med[2] - 226)) < 26:
            for yy, xx in comp:
                quitar[yy, xx] = True
print('píxeles de bolsas encerradas eliminadas:', int(quitar.sum()))
a = np.where(quitar, 0.0, a)

# 5. re-clasifica fondo con el nuevo alfa y calcula alfa suave
bg2 = mask | quitar | (a < 25)
fg8 = np.where(bg2, 0, 255).astype(np.uint8)
fgI = Image.fromarray(fg8).filter(ImageFilter.GaussianBlur(0.9))
m = np.array(fgI).astype(np.float64) / 255.0
m = np.maximum(m, np.where((a >= 250) & (~bg2), 1.0, 0.0))

# 6. un-blending del velo blanco donde el alfa es parcial
BG = 226.0
eps = 1e-4
for c in range(3):
    ch = arr[..., c]
    ch[:] = np.where(m > 0.02, (ch - BG * (1.0 - m)) / np.maximum(m, eps), ch)
arr[..., 0:3] = np.clip(arr[..., 0:3], 0, 255)
arr[..., 3] = np.clip(m * 255.0, 0, 255)

out = Image.fromarray(arr.astype(np.uint8))
out.save(SRC, optimize=True)

arr2 = np.array(out)
ring = [arr2[0, 0], arr2[0, w - 1], arr2[h - 1, 0], arr2[h - 1, w - 1],
        arr2[0, w // 2], arr2[h - 1, w // 2], arr2[h // 2, 0], arr2[h // 2, w - 1]]
print('alfa anillo exterior:', [int(p[3]) for p in ring])
opacos = int((arr2[..., 3] > 250).sum())
print(f'opacos: {opacos} ({100 * opacos / (h * w):.1f}%)')

fondo = Image.new('RGBA', out.size, (255, 0, 255, 255))
fondo.alpha_composite(out)
fondo.convert('RGB').save(CHK)
print('composición en', CHK)

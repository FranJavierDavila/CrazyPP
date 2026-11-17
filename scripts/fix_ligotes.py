#!/usr/bin/env python3
"""ligotes.png: vuelve transparentes las esquinas blancas (fuera del marco
redondeado) para que la placa del HUD no muestre un cuadrado blanco."""
from PIL import Image
from collections import deque

P = '/home/z/my-project/game/championships/oeste/assets/ligotes.png'
im = Image.open(P).convert('RGBA')
w, h = im.size
px = im.load()

def near_white(p):
    r, g, b, a = p
    return a == 0 or (r > 235 and g > 235 and b > 235)

seen = [[False] * w for _ in range(h)]
q = deque()
for x in range(w):
    for y in (0, h - 1):
        if near_white(px[x, y]) and not seen[y][x]:
            q.append((x, y)); seen[y][x] = True
for y in range(h):
    for x in (0, w - 1):
        if near_white(px[x, y]) and not seen[y][x]:
            q.append((x, y)); seen[y][x] = True
n = 0
while q:
    x, y = q.popleft()
    px[x, y] = (255, 255, 255, 0)
    n += 1
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and near_white(px[nx, ny]):
            seen[ny][nx] = True
            q.append((nx, ny))
im.save(P)
print('esquinas transparentadas:', n, 'px de', w * h)

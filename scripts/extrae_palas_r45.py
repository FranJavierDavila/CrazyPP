#!/usr/bin/env python3
"""r45 v2 · polilíneas de palas.png — une fragmentos del esqueleto por
proximidad de extremos y simplifica con curva viva (eps pequeño).
Salida: scripts/constelacion_palas.json + preview scripts/constelacion_preview.png
"""
import json
import numpy as np
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
from scipy import ndimage

SRC = '/home/z/my-project/upload/palas.png'
OUT = '/home/z/my-project/scripts/constelacion_palas.json'
PRE = '/home/z/my-project/scripts/constelacion_preview.png'

im = np.array(Image.open(SRC))
al = im[:, :, 3] > 90
# cierra micro-gaps del anti-aliasing (dilatación 4-vecina CORRECTA)
al2 = al.copy()
al2[1:, :] |= al[:-1, :]
al2[:-1, :] |= al[1:, :]
al2[:, 1:] |= al[:, :-1]
al2[:, :-1] |= al[:, 1:]
al = al2
sk = skeletonize(al)
ys, xs = np.where(sk)
pts = set(zip(ys.tolist(), xs.tolist()))
# diagnóstico: componentes conexos del esqueleto
lab, ncomp = ndimage.label(sk, structure=np.ones((3, 3)))
print('componentes esqueleto:', ncomp)

vecinos8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def vecinos(p):
    y, x = p
    return [(y + dy, x + dx) for dy, dx in vecinos8 if (y + dy, x + dx) in pts]

grado = {p: len(vecinos(p)) for p in pts}
extremos = [p for p, g in grado.items() if g == 1]

visitadas = set()

def trazar(inicio):
    cam = [inicio]
    cur = inicio
    while True:
        vs = [q for q in vecinos(cur) if (cur, q) not in visitadas]
        if not vs:
            break
        if len(vs) > 1 and len(cam) >= 2:
            dy0, dx0 = cur[0] - cam[-2][0], cur[1] - cam[-2][1]
            vs.sort(key=lambda q: -((q[0] - cur[0]) * dy0 + (q[1] - cur[1]) * dx0))
        nxt = vs[0]
        visitadas.add((cur, nxt)); visitadas.add((nxt, cur))
        cam.append(nxt)
        cur = nxt
        if grado[cur] != 2:
            break
    return cam if len(cam) >= 6 else None

caminos = []
for e in extremos:
    if any((e, q) in visitadas for q in vecinos(e)):
        continue
    c = trazar(e)
    if c:
        caminos.append(c)
for p in [p for p, g in grado.items() if g == 2]:
    if any((p, q) in visitadas for q in vecinos(p)):
        continue
    c = trazar(p)
    if c and len(c) >= 12:
        # cierra el anillo SOLO si el fin cayó junto al inicio (un recorrido
        # que terminó lejos NO se cierra: el salto pintaría una cuerda falsa)
        if (c[0][0] - c[-1][0]) ** 2 + (c[0][1] - c[-1][1]) ** 2 <= 9:
            c.append(c[0])
        caminos.append(c)

# —— 2.ª pasada: tramos nudo→nudo que quedaron sin visitar ——
for p in sorted(pts):
    if any((p, q) not in visitadas for q in vecinos(p)):
        c = trazar(p)
        if c and len(c) >= 4:
            caminos.append(c)

# —— unión de fragmentos por extremos próximos (dos pasadas) ——
def extremos_de(c):
    return c[0], c[-1]

def une(caminos, radio=9.0, pasadas=6):
    for _ in range(pasadas):
        n = len(caminos)
        usados = [False] * n
        out = []
        for i in range(n):
            if usados[i]:
                continue
            cur = list(caminos[i])
            usados[i] = True
            cambio = True
            while cambio:
                cambio = False
                for j in range(n):
                    if usados[j]:
                        continue
                    a, b = caminos[j][0], caminos[j][-1]
                    for (pe, extremo_i) in ((cur[-1], 'fin'), (cur[0], 'ini')):
                        for pj, lado in ((a, 'ini'), (b, 'fin')):
                            if (pe[0] - pj[0]) ** 2 + (pe[1] - pj[1]) ** 2 <= radio * radio:
                                seg = list(caminos[j])
                                if lado == 'fin':
                                    seg.reverse()
                                if extremo_i == 'fin':
                                    cur = cur + seg
                                else:
                                    cur = seg + cur
                                usados[j] = True
                                cambio = True
                                break
                        if cambio:
                            break
            out.append(cur)
        caminos = out
        if len(caminos) == n:
            break
    return caminos

caminos = une(caminos)
print('caminos unidos:', len(caminos), '· largos:', sorted(len(c) for c in caminos))

def dp(puntos, eps):
    if len(puntos) < 3:
        return puntos
    p0 = np.array(puntos[0], float)
    p1 = np.array(puntos[-1], float)
    d = p1 - p0
    L = float(np.hypot(d[0], d[1]))
    if L < 2.0:
        # tramo casi cerrado (o degenerado): parte por el punto MÁS LEJANO
        # de p0 — el corte clásico de DP muere con cuerda ~0 (dist=0/L).
        seg = np.array(puntos[1:-1], float)
        if not len(seg):
            return puntos
        dd = np.hypot(seg[:, 0] - p0[0], seg[:, 1] - p0[1])
        i = int(np.argmax(dd))
        a = dp(puntos[:i + 2], eps)
        b = dp(puntos[i + 1:], eps)
        return a[:-1] + b
    seg = np.array(puntos[1:-1], float)
    if not len(seg):
        return puntos
    sx, sy = seg[:, 0] - p0[0], seg[:, 1] - p0[1]
    dist = np.abs(d[0] * sy - d[1] * sx) / L
    i = int(np.argmax(dist))
    if dist[i] > eps:
        a = dp(puntos[:i + 2], eps)
        b = dp(puntos[i + 1:], eps)
        return a[:-1] + b
    return [puntos[0], puntos[-1]]

EPS = 0.8
polis = []
for c in caminos:
    abierto = [(float(x), float(y)) for (y, x) in c]
    cerrado = len(abierto) >= 3 and abierto[0] == abierto[-1]
    if cerrado:
        abierto = abierto[:-1]           # DP clásico sobre el anillo abierto
    s = dp(abierto, EPS)
    if cerrado and len(s) >= 3:
        s.append(s[0])                   # re-cierra el anillo
    if len(s) >= 2:
        polis.append(s)

todas = [p for s in polis for p in s]
x0 = min(p[0] for p in todas); x1 = max(p[0] for p in todas)
y0 = min(p[1] for p in todas); y1 = max(p[1] for p in todas)
span = max(x1 - x0, y1 - y0)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
salida = []
for s in polis:
    plano = [(round((x - cx) / span, 4), round(-(y - cy) / span, 4)) for (x, y) in s]
    if len(plano) >= 2:
        salida.append(plano)

total_pts = sum(len(s) for s in salida)
js = json.dumps(salida, separators=(',', ':'))
print('polilíneas:', len(salida), '· puntos:', total_pts, '· bytes json:', len(js))
with open(OUT, 'w') as f:
    f.write(js)

# —— preview: dibuja las polilíneas sobre el original atenuado ——
img = Image.open(SRC).convert('RGBA')
img.putalpha(40)
dr = ImageDraw.Draw(img)
for s in salida:
    pix = [((x * span + cx), (-y * span + cy)) for (x, y) in s]
    dr.line(pix, fill=(0, 170, 255, 255), width=4)
img.save(PRE)
print('preview:', PRE)

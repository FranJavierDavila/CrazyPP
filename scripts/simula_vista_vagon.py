#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VERIFICACIÓN VISUAL del parallax v2.111 — replica las fórmulas del código
de championships/oeste/index.js y compone la vista por la ventana:
- P1: p1_*.png cosidas sobre quad 530x64 en cy=10.2 (horizonte del arte a 1.55 m)
- P2/P3/P4: suelo degradado naciendo en born=(cy+h/2)/h, + piezas con escala
  por bbox (hf) y pies en y=0 (feet) — como _pxApply.
Cámara pinhole lateral: ojo (0,1.6,0) mirando a +x; sx = f*z/x, sy = f*(1.6-y)/x.
"""
import os, json
from PIL import Image, ImageDraw

D = '/home/z/my-project/game/championships/oeste/assets/parallax'
W, H = 1600, 800
F = 700.0
EYE = 1.6

img = Image.new('RGB', (W, H), (110, 160, 205))   # cielo base
dr = ImageDraw.Draw(img)

def proj(z, y, x):
    """proyecta punto del mundo (x=dist lateral, y=altura, z=a lo largo del tren)"""
    sx = W / 2 + F * z / x
    sy = H / 2 + F * (EYE - y) / x
    return sx, sy

def bb_of(im):
    a = im.getchannel('A').resize((96, 96))
    px = a.load()
    xs, ys = [], []
    for yy in range(96):
        for xx in range(96):
            if px[xx, yy] > 100:
                xs.append(xx); ys.append(yy)
    if not ys:
        return 0, 1, 0, 1
    return min(xs) / 96, max(xs) / 96, min(ys) / 96, max(ys) / 96

LAYERS = [  # dist, w, h, cy  (TREN.layers)
    (140, 530, 64, 10.2), (70, 130, 30, 3.4), (28, 60, 12, 2.3), (9, 24, 4.2, 1.84),
]
COLT = {1: (167, 135, 152), 2: (174, 126, 132), 3: (176, 122, 94)}
COLB = {1: (174, 126, 132), 2: (176, 122, 94), 3: (169, 110, 64)}

# ---------- suelos P2/P3/P4 (quads con degradado + nacimiento en born) -----
for k in (1, 2, 3):
    dist, w, h, cy = LAYERS[k]
    born = min(0.96, (cy + h / 2) / h)
    zA, zB = -w / 2, w / 2
    yTop = cy + h / 2
    yBot = cy - h / 2
    NB = 60
    for i in range(NB):
        t0, t1 = i / NB, (i + 1) / NB
        # t=0 en born (y=yTop), t=1 en yBot
        ya = yTop + (yBot - yTop) * t0
        yb = yTop + (yBot - yTop) * t1
        tt = (t0 + t1) / 2
        # alfa de nacimiento suave
        a = 0.0 if tt < born else min(1.0, 3.0 * (tt - born)) if tt < born + 0.07 else 1.0
        if a <= 0.01:
            continue
        col = tuple(int(COLT[k][j] + (COLB[k][j] - COLT[k][j]) * ((tt - born) / max(1e-6, 1 - born))) for j in range(3))
        col = tuple(int(c0 * a + img.getpixel((W // 2, 20))[j] * (1 - a)) for j, c0 in enumerate(col))
        p1 = proj(zA, ya, dist); p2 = proj(zB, ya, dist)
        p3 = proj(zB, yb, dist); p4 = proj(zA, yb, dist)
        dr.polygon([p1, p2, p3, p4], fill=col)

# ---------- P1: horizonte cosido del artista -------------------------------
pano1 = Image.open(os.path.join(D, 'p1_paisajedesierto1.png')).convert('RGBA')
pano2 = Image.open(os.path.join(D, 'p1_paisajedesierto2.png')).convert('RGBA')
w0, h0 = pano1.size
cv = Image.new('RGBA', (w0 * 2, h0))
cv.paste(pano1, (0, 0)); cv.paste(pano2, (w0, 0))
dist, w, h, cy = LAYERS[0]
yTop, yBot = cy + h / 2, cy - h / 2
zA, zB = -w / 2, w / 2
zr = 12  # trocear el quad en columnas para mapear la textura
for i in range(zr):
    t0, t1 = i / zr, (i + 1) / zr
    za, zb = zA + (zB - zA) * t0, zA + (zB - zA) * t1
    u0, u1 = t0, t1
    strip = cv.crop((int(u0 * cv.width), 0, int(u1 * cv.width), cv.height)).resize((64, 256))
    pa, pb = proj(za, yTop, dist), proj(zb, yTop, dist)
    pc, pd = proj(zb, yBot, dist), proj(zb, yBot, dist)
    # quad completo con textura aproximada: trocear también en Y
    yr = 40
    for j in range(yr):
        v0, v1 = j / yr, (j + 1) / yr
        ya2 = yTop + (yBot - yTop) * v0
        yb2 = yTop + (yBot - yTop) * v1
        sv = strip.crop((0, int(v0 * 256), 64, int(v1 * 256) + 1)).resize((1, 1))
        r, g, b, a = sv.getpixel((0, 0))
        if a < 10:
            continue
        col = (r, g, b)
        q1 = proj(za, ya2, dist); q2 = proj(zb, ya2, dist)
        q3 = proj(zb, yb2, dist); q4 = proj(za, yb2, dist)
        dr.polygon([q1, q2, q3, q4], fill=col)

# ---------- piezas del artista (hf + bbox, pies en y=0) ---------------------
CFG = {
 'p2': {'dist': 70, 'hf': {'p2_rancho1.png': 11, 'p2_estructura1.png': 14, 'p2_roca1.png': 6.5, 'p2_poste1.png': 12.5}},
 'p3': {'dist': 28, 'hf': {'p3_arbusto1.png': 3.2, 'p3_arbusto5.png': 3.2, 'p3_poste1.png': 7.5}},
 'p4': {'dist': 9,  'hf': {'p4_cactus1.png': 3.0, 'p4_caseta.png': 2.6, 'p4_valla.png': 1.3, 'p4_roca1.png': 1.7}},
}
ZSPOT = {  # posiciones z de muestra en la banda visible
 'p2': [-60, -20, 20], 'p3': [-20, -5, 10], 'p4': [-6, 0, 6],
}
for key, cfg in CFG.items():
    for f, z in zip(cfg['hf'].keys(), ZSPOT[key]):
        im = Image.open(os.path.join(D, f)).convert('RGBA')
        iw, ih = im.size
        x0, x1, y0, y1 = bb_of(im)
        bbH = max(0.15, y1 - y0)
        hf = cfg['hf'][f]
        mesh_h = hf / bbH
        mesh_w = mesh_h * (iw / ih)
        feet = 0.0
        y_bot_mesh = feet - (1 - y1) * mesh_h
        y_top_mesh = y_bot_mesh + mesh_h
        # escala del sprite: alto en px = F*mesh_h/dist
        px_h = F * mesh_h / cfg['dist']
        px_w = px_h * (iw / ih)
        sp = im.resize((max(1, int(px_w)), max(1, int(px_h))))
        sx, sy = proj(z, y_top_mesh, cfg['dist'])
        img.paste(sp, (int(sx - px_w / 2), int(sy)), sp)

img.save('/home/z/my-project/scripts/vista_vagon_sim.png')
print('Vista simulada guardada: scripts/vista_vagon_sim.png')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2.128 · Insignia del campeonato ESTACIÓN ORBITAL (512×512 RGBA).

Estilo cartoon circular como las insignias de locura/magia/oeste:
anillo metálico con remaches, disco de espacio profundo con estrellas,
pala de ping-pong con bola en órbita elíptica + planeta anillado.
Dibujo a 2048 px y rebajado a 512 (antialias de alta calidad).
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

S = 2048                       # lienzo de trabajo
CX = CY = S // 2
R_RING_O = int(S * 0.485)      # radio exterior del anillo
R_RING_I = int(S * 0.405)      # radio interior del anillo
R_DISC = R_RING_I

random.seed(42)

img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)


def circle(xy, r, fill=None, outline=None, width=1):
    d.ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r],
              fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- anillo ---
# cuerpo metálico del anillo (acero azulado con sombra inferior)
circle((CX, CY), R_RING_O, fill='#8f9bb3')
# bisel superior (luz)
d.arc([CX - R_RING_O, CY - R_RING_O, CX + R_RING_O, CY + R_RING_O],
      200, 340, fill='#d7deea', width=int(S * 0.030))
# borde exterior oscuro (contorno cartoon)
circle((CX, CY), R_RING_O, outline='#14181f', width=int(S * 0.014))
# hueco interior
circle((CX, CY), R_RING_I, fill='#14181f')
circle((CX, CY), R_RING_I - int(S * 0.006), fill='#101623')

# remaches del anillo (12, alternando luz/sombra)
for i in range(12):
    a = math.radians(i * 30 + 15)
    rm = (R_RING_O + R_RING_I) / 2
    x = CX + rm * math.cos(a)
    y = CY + rm * math.sin(a)
    rr = int(S * 0.016)
    circle((x, y), rr + int(S * 0.005), fill='#2a3140')
    circle((x, y), rr, fill='#cfd6e4')

# ------------------------------------------------------- disco de espacio ---
# degradado simulado: círculos concéntricos de azul profundo a azul céntrico
steps = 46
for i in range(steps, 0, -1):
    k = i / steps
    col = (
        int(0x0c + (0x27 - 0x0c) * (1 - k)),
        int(0x12 + (0x3a - 0x12) * (1 - k)),
        int(0x20 + (0x5c - 0x20) * (1 - k)),
    )
    circle((CX, CY), int(R_DISC * (i / steps)), fill=col + (255,))
circle((CX, CY), R_DISC - int(S * 0.008), outline='#0a0e16', width=int(S * 0.012))

# estrellas (puntos + destellos de 4 puntas)
star_pts = []
for _ in range(90):
    a = random.uniform(0, math.tau)
    rr = math.sqrt(random.uniform(0, 1)) * (R_DISC - S * 0.05)
    x, y = CX + rr * math.cos(a), CY + rr * math.sin(a)
    mag = random.choice([2, 3, 4, 5])
    col = random.choice(['#ffffff', '#dfe8ff', '#ffe9b8'])
    star_pts.append((x, y, mag, col))
for x, y, m, col in star_pts:
    circle((x, y), m, fill=col)


def sparkle(x, y, r, col='#ffffff'):
    d.line([x - r, y, x + r, y], fill=col, width=max(2, int(r * 0.22)))
    d.line([x, y - r, x, y + r], fill=col, width=max(2, int(r * 0.22)))


for _ in range(6):
    a = random.uniform(0, math.tau)
    rr = math.sqrt(random.uniform(0.15, 0.9)) * (R_DISC - S * 0.07)
    sparkle(CX + rr * math.cos(a), CY + rr * math.sin(a), random.uniform(16, 30),
            random.choice(['#ffffff', '#ffe9b8']))

# ------------------------------------------------------ planeta anillado ---
# mini saturno arriba a la derecha del disco
px, py, pr = CX + int(R_DISC * 0.46), CY - int(R_DISC * 0.50), int(R_DISC * 0.155)
circle((px, py), pr + int(S * 0.008), fill='#14181f')
circle((px, py), pr, fill='#e8a24b')
# banda del planeta
d.arc([px - pr, py - pr, px + pr, py + pr], 20, 160, fill='#c77f2e', width=int(pr * 0.22))
# brillo
d.arc([px - pr, py - pr, px + pr, py + pr], 200, 330, fill='#ffd9a0', width=int(pr * 0.16))
# anillo del planeta (elipse detrás/delante)
ring_w = int(pr * 0.16)
ring_box = [px - int(pr * 1.9), py - int(pr * 0.62), px + int(pr * 1.9), py + int(pr * 0.62)]
d.arc(ring_box, 185, 355, fill='#cfd6e4', width=ring_w)          # parte delantera
d.arc(ring_box, 5, 175, fill='#8f9bb3', width=ring_w)            # parte trasera

# ------------------------------------------------------- órbita + satélite ---
# elipse orbital alrededor del centro (pala+bola)
orb_box = [CX - int(R_DISC * 0.78), CY - int(R_DISC * 0.34),
           CX + int(R_DISC * 0.78), CY + int(R_DISC * 0.34)]
orb_w = int(S * 0.010)
d.arc(orb_box, 0, 360, fill='#7f8ea8', width=orb_w)

# ---------------------------------------------------------------- la pala ---
# pala roja inclinada con mango de madera (cartoon, contorno negro)
pa = math.radians(-38)                      # inclinación
pcx, pcy = CX - int(S * 0.035), CY + int(S * 0.02)
pw, ph = int(S * 0.135), int(S * 0.175)     # semiejes de la goma
hl, hw = int(S * 0.16), int(S * 0.045)      # largo/ancho del mango


def rot(x, y, ang, ox, oy):
    dx, dy = x - ox, y - oy
    return (ox + dx * math.cos(ang) - dy * math.sin(ang),
            oy + dx * math.sin(ang) + dy * math.cos(ang))


# capa del contorno (grosor extra) + cuerpo
for w_extra, col in [(int(S * 0.012), '#14181f'), (0, '#d23a2a')]:
    pts = []
    for i in range(72):
        a = math.radians(i * 5)
        pts.append(rot(pcx + pw * math.cos(a), pcy + ph * math.sin(a), pa, pcx, pcy))
    d.polygon(pts, fill=col)
# mango (rectángulo rotado) — primero contorno, luego madera
mx0, my0 = pcx + hw, pcy + ph * 0.55
rect_pts = [(mx0 - hw, my0), (mx0 + hw, my0),
            (mx0 + hw, my0 + hl), (mx0 - hw, my0 + hl)]
for w_extra, col in [(int(S * 0.012), '#14181f'), (0, '#c98a4b')]:
    d.polygon([rot(x, y, pa, pcx, pcy) for x, y in rect_pts], fill=col)
# goma interior (línea de la pala)
inner = []
for i in range(72):
    a = math.radians(i * 5)
    inner.append(rot(pcx + (pw - S * 0.018) * math.cos(a),
                     pcy + (ph - S * 0.018) * math.sin(a), pa, pcx, pcy))
d.polygon(inner, fill='#e8564a')

# ---------------------------------------------------------------- la bola ---
# bola blanca con estela de órbita (arco azul eléctrico)
bx, by = CX + int(R_DISC * 0.36), CY - int(R_DISC * 0.20)
# estela: arco grueso detrás de la bola sobre la elipse orbital
d.arc(orb_box, 305, 350, fill='#40c4ff', width=int(S * 0.020))
circle((bx, by), int(S * 0.050) + int(S * 0.008), fill='#14181f')
circle((bx, by), int(S * 0.050), fill='#ffffff')
circle((bx - S * 0.014, by - S * 0.014), int(S * 0.013), fill='#f0f4ff')

# ----------------------------------------------------------- satélite AX-9 ---
# pequeño satélite sobre la órbita (cuerpo + paneles solares)
sx, sy = CX - int(R_DISC * 0.62), CY + int(R_DISC * 0.26)
bw, bh = int(S * 0.036), int(S * 0.030)
d.rectangle([sx - bw, sy - bh, sx + bw, sy + bh], fill='#cfd6e4', outline='#14181f', width=int(S * 0.007))
for sgn in (-1, 1):
    pan_x0 = sx + sgn * (bw + int(S * 0.008))
    pan_x1 = sx + sgn * (bw + int(S * 0.062))
    d.rectangle([min(pan_x0, pan_x1), sy - int(bh * 0.7),
                 max(pan_x0, pan_x1), sy + int(bh * 0.7)],
                fill='#2e6db4', outline='#14181f', width=int(S * 0.006))
# antena
d.line([sx, sy - bh, sx, sy - bh - int(S * 0.028)], fill='#cfd6e4', width=int(S * 0.008))
circle((sx, sy - bh - int(S * 0.034)), int(S * 0.010), fill='#ffd257', outline='#14181f', width=int(S * 0.004))

# ------------------------------------------------------------ brillo global ---
img = img.filter(ImageFilter.SMOOTH)
final = img.resize((512, 512), Image.LANCZOS)

out = '/home/z/my-project/public/championships/estacion_orbital/assets/insignia.png'
final.save(out, 'PNG')
print('insignia guardada:', out, final.size, final.mode)

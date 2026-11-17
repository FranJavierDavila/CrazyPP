#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2.116 · Genera contador.png — letrero de madera del MARCADOR de forajidos
de la etapa 2 (ASEDIO del pueblo). Se pinta en la esquina superior izquierda
del HUD (HudOeste) y encima se dibuja el número que FALTA por matar.
380x190 px (relación 2:1 = la del hueco 190x95 del HUD)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, os

W, H = 380, 190
random.seed(7)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ---- tabla de madera horizontal con vetas ----
base = (94, 60, 32)
d.rounded_rectangle([2, 2, W - 3, H - 3], radius=16, fill=base + (255,))
# tablones horizontales (3 bandas con tono ligeramente distinto)
ys = [0, 62, 124, H]
for i in range(3):
    y0, y1 = ys[i] + (2 if i else 4), ys[i + 1] - 2
    tone = random.randint(-10, 10)
    col = (94 + tone, 60 + tone, 32 + tone, 255)
    d.rectangle([6, y0, W - 7, y1], fill=col)
    # veta: líneas horizontales onduladas semitransparentes
    for _ in range(14):
        yy = random.randint(y0 + 3, y1 - 3)
        x0 = random.randint(4, W // 3)
        ln = random.randint(40, 160)
        a = random.randint(18, 42)
        d.line([x0, yy, min(W - 6, x0 + ln), yy], fill=(60, 38, 18, a), width=2)
# nudos de madera
for _ in range(4):
    kx, ky = random.randint(30, W - 30), random.randint(24, H - 24)
    kr = random.randint(5, 9)
    d.ellipse([kx - kr, ky - kr // 2, kx + kr, ky + kr // 2],
              outline=(52, 32, 14, 120), width=2)

# ---- marco con clavos ----
d.rounded_rectangle([2, 2, W - 3, H - 3], radius=16,
                    outline=(40, 24, 10, 255), width=5)
d.rounded_rectangle([9, 9, W - 10, H - 10], radius=12,
                    outline=(160, 118, 62, 200), width=2)
for nx in (24, W - 24):
    for ny in (22, H - 22):
        d.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=(58, 58, 62, 255))
        d.ellipse([nx - 4, ny - 4, nx + 1, ny + 1], fill=(210, 210, 218, 255))

# ---- texto FORAJIDOS (crema con sombra) ----
fb = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', 46)
ft = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', 30)
txt = 'FORAJIDOS'
bb = d.textbbox((0, 0), txt, font=fb)
tw = bb[2] - bb[0]
tx, ty = (W - tw) // 2, 18
d.text((tx + 3, ty + 3), txt, font=fb, fill=(30, 16, 6, 200))
d.text((tx, ty), txt, font=fb, fill=(242, 226, 190, 255))
# línea de adorno
d.line([W // 2 - 70, 82, W // 2 + 70, 82], fill=(196, 150, 84, 220), width=3)
d.ellipse([W // 2 - 4, 78, W // 2 + 4, 86], fill=(196, 150, 84, 230))

# ---- hueco del número (placa recortada) ----
d.rounded_rectangle([W // 2 - 78, 96, W // 2 + 78, H - 18], radius=12,
                    fill=(52, 32, 14, 200), outline=(196, 150, 84, 220), width=3)
d.text((W // 2 - 64, 118), '0 DE 0', font=ft, fill=(0, 0, 0, 0))

out = '/home/z/my-project/game/championships/oeste/assets/contador.png'
img.save(out, 'PNG')
print('OK', out, os.path.getsize(out), 'bytes')

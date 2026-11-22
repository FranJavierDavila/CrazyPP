#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera powerburla.png (512x512 RGBA): medallón circular del superpoder
BURLA del Clown, sustituye a powergiro.png (Mareo).
Estilo de la familia: anillo metálico + interior con arte. Aquí el anillo
es ARCOÍRIS (el rayo de la Burla) con bordes dorados, y el interior lleva
la cara burlesca del clown recortada de burla1.png."""
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import math, colorsys

SRC = '/home/z/my-project/public/championships/locura/assets/burla1.png'
OUT = '/home/z/my-project/public/championships/locura/assets/powerburla.png'
S = 512
CX = CY = S / 2

img = Image.new('RGBA', (S, S), (0, 0, 0, 0))

# --- 1) interior: cara del clown (mitad superior de burla1, cuadrada) ------
src = Image.open(SRC).convert('RGB')
face = src.crop((0, 0, 512, 512)).resize((S, S), Image.LANCZOS)

R_IN = 196          # radio del interior (cara)
R_BAND = 44         # grosor del anillo arcoíris
R_OUT = 252         # radio exterior dorado

# máscara circular del interior
mask_in = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask_in).ellipse(
    (CX - R_IN, CY - R_IN, CX + R_IN, CY + R_IN), fill=255)
img.paste(face, (0, 0), mask_in)

# --- 2) anillo arcoíris (barrido de tono por ángulo) ------------------------
band = Image.new('RGBA', (S, S), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
STEPS = 360
for i in range(STEPS):
    a0 = 2 * math.pi * i / STEPS
    a1 = 2 * math.pi * (i + 1) / STEPS + 0.012
    r, g, b = colorsys.hsv_to_rgb(i / STEPS, 0.78, 0.96)
    col = (int(r * 255), int(g * 255), int(b * 255), 255)
    bd.pieslice((CX - R_IN - R_BAND, CY - R_IN - R_BAND,
                 CX + R_IN + R_BAND, CY + R_IN + R_BAND),
                math.degrees(a0), math.degrees(a1), fill=col)
# agujero central al anillo
hole = Image.new('L', (S, S), 0)
ImageDraw.Draw(hole).ellipse(
    (CX - R_IN + 2, CY - R_IN + 2, CX + R_IN - 2, CY + R_IN - 2), fill=255)
band.putalpha(Image.composite(Image.new('L', (S, S), 0), band.getchannel('A'), hole))
img.alpha_composite(band)

# --- 3) bordes dorados (exterior + separadores) -----------------------------
gold = (212, 175, 55, 255)
gold_hi = (255, 224, 130, 255)
dd = ImageDraw.Draw(img)
dd.arc((CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT), 0, 360,
       fill=gold, width=10)
dd.arc((CX - R_IN - R_BAND - 4, CY - R_IN - R_BAND - 4,
        CX + R_IN + R_BAND + 4, CY + R_IN + R_BAND + 4), 0, 360,
       fill=gold, width=6)
dd.arc((CX - R_IN - 2, CY - R_IN - 2, CX + R_IN + 2, CY + R_IN + 2), 0, 360,
       fill=gold_hi, width=4)

# --- 4) brillo especular superior (mismo acabado de medallón) ---------------
shine = Image.new('RGBA', (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(shine)
sd.ellipse((CX - R_IN, CY - R_IN - 6, CX + R_IN, CY + R_IN - 120),
           fill=(255, 255, 255, 52))
shine = shine.filter(ImageFilter.GaussianBlur(26))
img.alpha_composite(shine)

# recorte final al círculo exterior (alpha 0 fuera)
final_mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(final_mask).ellipse(
    (CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT), fill=255)
a = Image.composite(img.getchannel('A'), Image.new('L', (S, S), 0), final_mask)
img.putalpha(a)

img.save(OUT)
print('OK ->', OUT, img.size, img.mode)

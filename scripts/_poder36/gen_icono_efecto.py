#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.36 · Icono PROVISIONAL del poder SÚPER EFECTO (SuperPala_Efecto.png
del dueño NO llegó al sandbox — el dueño lo re-adjuntará y se sustituye en
un minuto con el mismo cuantizador). Misma familia visual que
SuperPala_Crece.png: insignia circular azul marino + anillo blanco + palas
rojas; aquí una BOLA con flechas de GIRO (cian) = el efecto/spin."""
from PIL import Image, ImageDraw
import math

S = 512  # dibujo grande → downscale a 256 (suavidad)
im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

CX = CY = S // 2
R = S // 2 - 4

# ---- fondo circular azul marino (degradado radial simulado) ----
for i in range(R, 0, -1):
    t = i / R
    rr = int(14 + 26 * (1 - t))
    gg = int(42 + 58 * (1 - t))
    bb = int(92 + 122 * (1 - t))
    d.ellipse([CX - i, CY - i, CX + i, CY + i], fill=(rr, gg, bb, 255))

# ---- anillo blanco doble (firma de la familia) ----
d.ellipse([CX - R + 14, CY - R + 14, CX + R - 14, CY + R - 14],
          outline=(255, 255, 255, 255), width=16)
d.ellipse([CX - R + 44, CY - R + 44, CX + R - 44, CY + R - 44],
          outline=(255, 255, 255, 130), width=5)

# ---- palas rojas en diagonal (silueta, como Crece) ----
def pala(cx, cy, ang, esc, alpha=255):
    pal = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pal)
    # hoja (elipse roja con borde blanco y sombra interna)
    rw, rh = 88 * esc, 118 * esc
    pd.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
               fill=(226, 62, 54, alpha), outline=(255, 255, 255, alpha), width=max(3, int(7 * esc)))
    pd.ellipse([cx - rw * .62, cy - rh * .72, cx + rw * .62, cy + rh * .72],
               outline=(180, 34, 30, alpha), width=max(2, int(5 * esc)))
    # mango de madera
    mw, mh = 30 * esc, 96 * esc
    pd.rounded_rectangle([cx - mw, cy + rh * .55, cx + mw, cy + rh * .55 + mh],
                         radius=int(12 * esc), fill=(196, 148, 92, alpha),
                         outline=(120, 84, 46, alpha), width=max(2, int(4 * esc)))
    return pal.rotate(ang, center=(cx, cy), resample=Image.BICUBIC)

im.alpha_composite(pala(CX - 66, CY + 40, -22, 0.86))
im.alpha_composite(pala(CX + 42, CY + 74, 14, 0.68, alpha=215))

# ---- BOLA blanca protagonista (es el EFECTO: la bola gira) ----
bx, by, br = CX + 52, CY - 92, 66
d.ellipse([bx - br, by - br, bx + br, by + br], fill=(250, 250, 250, 255),
          outline=(210, 214, 224, 255), width=4)
d.ellipse([bx - br + 12, by - br + 12, bx + br - 26, by + br - 30],
          outline=(226, 230, 238, 255), width=5)   # brillo

# ---- flechas de GIRO alrededor de la bola (cian + blanco) ----
def flecha_giro(cx, cy, r, a0, a1, col, wdt):
    steps = 46
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
           for i in range(steps + 1)]
    d.line(pts, fill=col, width=wdt, joint='curve')
    # punta en el extremo (tangente)
    ax, ay = pts[-1]
    tx, ty = pts[-4]
    ang = math.atan2(ay - ty, ax - tx)
    L = wdt * 3.1
    p1 = (ax + L * math.cos(ang - 0.45), ay + L * math.sin(ang - 0.45))
    p2 = (ax + L * math.cos(ang + 0.45), ay + L * math.sin(ang + 0.45))
    d.polygon([pts[-1], p1, p2], fill=col)

flecha_giro(bx, by, br + 34, 200, 340, (99, 200, 240, 255), 13)   # cian arriba→derecha
flecha_giro(bx, by, br + 60, 30, 150, (255, 255, 255, 235), 10)   # blanca derecha→abajo
flecha_giro(bx, by, br + 34, 60, 160, (99, 200, 240, 200), 9)     # cian interior

# ---- destellos ----
for (x, y, r) in [(CX - 150, CY - 140, 11), (CX + 168, CY + 66, 8), (CX - 118, CY + 158, 7)]:
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 246, 216, 255))

im = im.resize((256, 256), Image.LANCZOS)
im.save('/home/z/my-project/scripts/_poder36/icono_efecto.png')

# cuantización a 64 colores (misma regla del icono del dueño: peso mínimo)
q = im.convert('RGB').quantize(colors=64, method=Image.MEDIANCUT).convert('RGBA')
# restaurar canal alfa circular (fuera del círculo, transparente)
mask = Image.new('L', (256, 256), 0)
md = ImageDraw.Draw(mask)
md.ellipse([2, 2, 254, 254], fill=255)
q.putalpha(mask)
q.save('/home/z/my-project/scripts/_poder36/icono_efecto_64.png', optimize=True)
import os
print('icono_efecto.png   :', os.path.getsize('/home/z/my-project/scripts/_poder36/icono_efecto.png'), 'B')
print('icono_efecto_64.png:', os.path.getsize('/home/z/my-project/scripts/_poder36/icono_efecto_64.png'), 'B')
print('ICONO_OK')

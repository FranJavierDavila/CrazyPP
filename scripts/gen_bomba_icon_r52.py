#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ronda 52 · bomba.webp — icono del LADRILLO BOMBA del ARKANOID 2 (etapa 4
del campeonato de La Locura), al estilo del reloj.webp del tiempo extra:
cartela blanca 512x512 con silueta negra — aquí, una BOMBA clasica
(esfera + collar + cuello + mecha encendida con chispa de 4 puntas)."""
from PIL import Image, ImageDraw
import math

S = 512
im = Image.new('RGBA', (S, S), (255, 255, 255, 255))
d = ImageDraw.Draw(im)

NEGRO = (12, 12, 15, 255)

cx, cy = 256, 316          # centro de la esfera
R = 148                    # radio de la bomba

# --- esfera ---
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=NEGRO)

# --- cuello/collar: trapezoide corto sobre la esfera ---
nx1, nx2 = cx - 46, cx + 46
ny_top, ny_bot = cy - R - 34, cy - R + 26
d.polygon([(nx1, ny_bot), (nx2, ny_bot), (nx2 - 14, ny_top), (nx1 + 14, ny_top)],
          fill=NEGRO)

# --- mecha curva (arco de curvas Bezier aproximadas con lineas gruesas) ---
mec_pts = []
for i in range(31):
    t = i / 30.0
    # curva en S desde el cuello hacia arriba-derecha
    x = (nx2 - 22) + t * 74
    y = (ny_top - 6) - math.sin(t * math.pi * 0.9) * 62 - t * 26
    mec_pts.append((x, y))
for w, seg in ((22, 5), (16, 10), (11, 20)):
    for i in range(0, len(mec_pts) - seg, seg):
        d.line([mec_pts[i], mec_pts[i + seg]], fill=NEGRO, width=w)
d.line([mec_pts[-seg], mec_pts[-1]], fill=NEGRO, width=11)

# --- chispa de 4 puntas en la punta de la mecha ---
sx, sy = mec_pts[-1]
pr_out, pr_in = 46, 13
for k in range(4):
    a = -math.pi / 2 + k * math.pi / 2
    a2 = a + math.pi / 4
    p1 = (sx + math.cos(a) * pr_out, sy + math.sin(a) * pr_out)
    p2 = (sx + math.cos(a2) * pr_in, sy + math.sin(a2) * pr_in)
    a3 = a + math.pi / 2
    p3 = (sx + math.cos(a3) * pr_out, sy + math.sin(a3) * pr_out)
    d.polygon([p1, p2, p3], fill=NEGRO)

# --- brillo de la esfera (recorte eliptico blanco arriba-izquierda) ---
bx, by = cx - 58, cy - 64
d.ellipse([bx - 34, by - 20, bx + 34, by + 20], fill=(255, 255, 255, 255))
# pequeño segundo brillo
d.ellipse([bx + 58, by + 22, bx + 92, by + 44], fill=(255, 255, 255, 255))

# --- base sombra suave bajo la bomba (mismo lenguaje del reloj: la silueta apoya) ---
d.ellipse([cx - 110, 448, cx + 110, 476], fill=NEGRO)

# alfa por luminancia: el blanco puro pasa a transparente SOLO fuera de la
# cartela — NO: el reloj.webp es cartela blanca OPACA sobre el ladrillo
# negro (mismo look). Mantenemos blanco opaco y guardamos webp.
im = im.convert('RGB')
im.save('/home/z/my-project/public/championships/locura/assets/bomba.webp',
        'WEBP', quality=92, method=6)
print('bomba.webp creado:', im.size)

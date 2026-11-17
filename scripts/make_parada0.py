#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2.134 · PARADA0.png — arte de la estación de SALIDA «BRAVOS» (nuevo, para
que la salida NO repita la imagen de la parada 1).

Pasos:
  1. Recorta el fondo claro del render IA (scripts/_parada0_raw.png) por
     inundación desde los BORDES (los blancos interiores se quedan).
  2. Encaja el contenido en un lienzo 1024×512 RGBA (como PARADA1-3),
     apoyado en el borde inferior.
  3. Pinta el nombre «BRAVOS» como letrero de estación (coordenadas
     calibradas a mano sobre el resultado del paso 2).
"""
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAW = '/home/z/my-project/scripts/_parada0_raw.png'
OUT = '/home/z/my-project/public/championships/oeste/assets/PARADA0.png'
W, H = 1024, 512
TOL = 26          # tolerancia del fondo claro desde las esquinas


def cutout(im):
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    # color de fondo = las DOS esquinas SUPERIORES (el borde inferior lleva
    # la vía/grava — contenido legítimo, NO fondo; y no debe contaminar la
    # mediana como en la 1.ª versión)
    bg = tuple((px[0, 0][i] + px[w - 1, 0][i]) // 2 for i in range(3))

    def is_bg(p):
        return (abs(p[0] - bg[0]) <= TOL and abs(p[1] - bg[1]) <= TOL and
                abs(p[2] - bg[2]) <= TOL)

    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(px[x, y]) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(px[x, y]) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                if is_bg(px[nx, ny]):
                    seen[ny * w + nx] = 1
                    q.append((nx, ny))
    # borde suave: 1 px de feathering en el alfa
    a = im.split()[3].filter(ImageFilter.MinFilter(3))
    im.putalpha(a)
    # BOLSAS DE CIELO ENCAJADAS (huecos entre grúa/torre/postes que NO tocan
    # el borde: la inundación no llega). Sólo componentes de color EXACTO de
    # fondo y neutras (r-b<=8 — la madera clara es cálida, r-b≈15, y se queda).
    px2 = im.load()
    seen2 = bytearray(w * h)
    for y0 in range(h):
        for x0 in range(w):
            p = px2[x0, y0]
            if seen2[y0 * w + x0] or p[3] == 0:
                continue
            if not (abs(p[0] - bg[0]) <= 14 and abs(p[1] - bg[1]) <= 14 and
                    abs(p[2] - bg[2]) <= 14 and p[0] - p[2] <= 8):
                continue
            stack = [(x0, y0)]
            seen2[y0 * w + x0] = 1
            comp = []
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if (0 <= nx < w and 0 <= ny < h and
                            not seen2[ny * w + nx]):
                        q = px2[nx, ny]
                        if (q[3] > 0 and abs(q[0] - bg[0]) <= 14 and
                                abs(q[1] - bg[1]) <= 14 and
                                abs(q[2] - bg[2]) <= 14 and
                                q[0] - q[2] <= 8):
                            seen2[ny * w + nx] = 1
                            stack.append((nx, ny))
            if len(comp) >= 60:                    # bolsita de cielo real
                for cx, cy in comp:
                    px2[cx, cy] = (0, 0, 0, 0)
    return im


def fit(im):
    bbox = im.getbbox()
    im = im.crop(bbox)
    w, h = im.size
    s = min((W - 24) / w, (H - 6) / h)
    nw, nh = int(w * s), int(h * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cv.paste(im, ((W - nw) // 2, H - nh), im)
    return cv


def plaque(cv, text='BRAVOS', cx=560, cy=205, tw=252, th=42):
    """Letrero de madera colgado en el hastial (coordenadas del lienzo
    1024×512 — calibradas mirando el resultado del ajuste)."""
    d = ImageDraw.Draw(cv)
    # tabla de madera
    wood = (146, 108, 64)
    wood_hi = (176, 136, 88)
    d.rounded_rectangle([cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2],
                        radius=6, fill=wood, outline=(58, 38, 20), width=3)
    # veta: dos líneas horizontales suaves
    for yy in (cy - th // 4, cy + th // 4):
        d.line([cx - tw // 2 + 8, yy, cx + tw // 2 - 8, yy],
               fill=wood_hi, width=2)
    # tornillos
    for sx in (cx - tw // 2 + 10, cx + tw // 2 - 10):
        d.ellipse([sx - 2, cy - 2, sx + 2, cy + 2], fill=(58, 38, 20))
    # texto
    size = 30
    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', size)
    except Exception:
        font = ImageFont.load_default()
    bb = d.textbbox((0, 0), text, font=font)
    d.text((cx - (bb[2] - bb[0]) // 2 - bb[0],
            cy - (bb[3] - bb[1]) // 2 - bb[1]),
           text, font=font, fill=(252, 240, 214),
           stroke_width=1, stroke_fill=(46, 30, 16))
    return cv


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('all', 'cut'):
        im = cutout(Image.open(RAW))
        cv = fit(im)
        cv.save('/home/z/my-project/scripts/_parada0_fit.png')
        print('fit → scripts/_parada0_fit.png', cv.size)
    if mode in ('all', 'text'):
        cv = Image.open('/home/z/my-project/scripts/_parada0_fit.png')
        plaque(cv)
        cv.save(OUT)
        print('PARADA0 →', OUT)


if __name__ == '__main__':
    main()

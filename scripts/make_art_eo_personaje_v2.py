#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTACIÓN ORBITAL — ANDROIDE AX-9 V2 (v2.130)
5 estados 512×1024 RGBA: rival · idle · duelo · derrotado · triunfante
Mejoras v2: sombreado por DEGRADADOS con máscaras (luz arriba-izquierda),
luz de borde, más piezas (antenas, codos, ventilas, cables, nacelles),
expresiones claras por estado y anillo antigrav con glow.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = '/home/z/my-project/public/championships/estacion_orbital/assets'
os.makedirs(OUT, exist_ok=True)

TINTA = (16, 20, 34)
CUERPO_A = (250, 253, 255)     # luz
CUERPO_B = (214, 224, 240)     # sombra
PANELC = (150, 162, 186)
CIAN = (79, 216, 255)
CIAN_LO = (30, 118, 152)
AMBAR = (255, 176, 76)
ROJO = (255, 92, 84)
VERDE = (105, 240, 174)
GRIS = (120, 132, 154)
NEGRO = (10, 14, 26)

W, H = 512, 1024


def _grad(sz, c0, c1, diag=True):
    """Degradado lineal diagonal c0→c1."""
    w, h = sz
    g = Image.new('RGB', (w, h))
    gd = ImageDraw.Draw(g)
    for y in range(h):
        for_k = y / max(1, h - 1)
        col = tuple(int(c0[i] + (c1[i] - c0[i]) * for_k) for i in range(3))
        gd.line([(0, y), (w, y)], fill=col)
    if diag:
        som = Image.new('L', (w, h), 0)
        sd = ImageDraw.Draw(som)
        for i in range(w):
            sd.line([(i, 0), (i, h)], fill=int(70 * (1 - i / w)))
        oscura = Image.new('RGB', (w, h), TINTA)
        g = Image.composite(oscura, g, som.point(lambda a: a // 3))
    return g


def parte(base, shape_fn, bbox, c0=CUERPO_A, c1=CUERPO_B, outline=TINTA, ow=7):
    """Pinta una pieza con degradado recortado por shape_fn(mask_draw) + borde."""
    x0, y0, x1, y1 = [int(v) for v in bbox]
    pad = ow + 6
    mw, mh = x1 - x0 + pad * 2, y1 - y0 + pad * 2
    mask = Image.new('L', (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    shape_fn(md, pad, mw, mh)
    grad = _grad((mw, mh), c0, c1)
    base.paste(grad, (x0 - pad, y0 - pad), mask)
    if outline:
        edge = Image.new('L', (mw, mh), 0)
        ed = ImageDraw.Draw(edge)
        ed.rectangle([0, 0, mw - 1, mh - 1], fill=255)
        edge = Image.composite(Image.new('L', (mw, mh), 0), edge,
                               mask.filter(ImageFilter.MaxFilter(3)))
        borde = Image.new('RGBA', (mw, mh), outline + (255,))
        e2 = mask.filter(ImageFilter.MaxFilter(ow * 2 + 1))
        e2.paste(0, mask)
        base.paste(borde, (x0 - pad, y0 - pad),
                   Image.composite(e2, Image.new('L', (mw, mh), 0),
                                   Image.new('L', (mw, mh), 255)))
    return mask


def pieza(base, shape_fn, bbox, c0, c1, ow=7, outline=TINTA):
    """Pieza con máscara + degradado + contorno (implementación única)."""
    x0, y0, x1, y1 = [int(v) for v in bbox]
    pad = ow + 8
    mw, mh = x1 - x0 + pad * 2, y1 - y0 + pad * 2
    mask = Image.new('L', (mw, mh), 0)
    shape_fn(ImageDraw.Draw(mask), pad, mw, mh)
    grad = _grad((mw, mh), c0, c1)
    base.paste(grad, (x0 - pad, y0 - pad), mask)
    if outline:
        outer = mask.filter(ImageFilter.MaxFilter(ow * 2 + 1))
        ring = ImageChops_subtract(outer, mask)
        base.paste(Image.new('RGBA', (mw, mh), outline + (255,)),
                   (x0 - pad, y0 - pad), ring)
    return mask


def ImageChops_subtract(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)


def glow(base, cx, cy, r, col, a=120, blur=18):
    m = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(m)


def linea(d, p0, p1, w, fill, outline=None):
    w = int(w)
    if outline:
        d.line([p0, p1], fill=outline, width=w + 8)
        for p in (p0, p1):
            d.ellipse([p[0] - (w + 8) / 2, p[1] - (w + 8) / 2,
                       p[0] + (w + 8) / 2, p[1] + (w + 8) / 2], fill=outline)
    d.line([p0, p1], fill=fill, width=w)
    for p in (p0, p1):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)


def garra(base, cx, cy, ang, scale=1.0, abierta=True):
    d = ImageDraw.Draw(base)
    L = 52 * scale
    sep = 0.62 if abierta else 0.34
    for s in (-1, 1):
        a = ang + s * sep
        x1 = cx + L * math.cos(a)
        y1 = cy + L * math.sin(a)
        linea(d, (cx, cy), (x1, y1), 15 * scale, GRIS, TINTA)
        x2 = x1 + 20 * scale * math.cos(a + s * 0.55)
        y2 = y1 + 20 * scale * math.sin(a + s * 0.55)
        linea(d, (x1, y1), (x2, y2), 11 * scale, (96, 106, 128), TINTA)
    d.ellipse([cx - 13 * scale, cy - 13 * scale, cx + 13 * scale, cy + 13 * scale],
              fill=PANELC, outline=TINTA, width=4)


def ojo(d, cx, cy, estado):
    if estado == 'derrotado':
        for s in (-1, 1):
            linea(d, (cx + s * 16 - 12, cy - 12), (cx + s * 16 + 12, cy + 12), 8, CIAN)
            linea(d, (cx + s * 16 + 12, cy - 12), (cx + s * 16 - 12, cy + 12), 8, CIAN)
    elif estado == 'triunfante':
        d.polygon([(cx, cy - 16), (cx + 5, cy - 5), (cx + 17, cy - 3),
                   (cx + 8, cy + 5), (cx + 10, cy + 17), (cx, cy + 10),
                   (cx - 10, cy + 17), (cx - 8, cy + 5), (cx - 17, cy - 3),
                   (cx - 5, cy - 5)], fill=AMBAR)
    else:
        w, h = (26, 20) if estado == 'duelo' else (30, 26)
        d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=NEGRO)
        d.ellipse([cx - w + 5, cy - h + 5, cx + w - 5, cy + h - 5], fill=CIAN)
        d.ellipse([cx - w + 9, cy - h + 7, cx - w + 21, cy - h + 16],
                  fill=(220, 250, 255))
        if estado == 'duelo':
            # ceño
            d.line([cx - w - 8, cy - h - 12, cx - 4, cy - h + 2], fill=TINTA, width=9)
            d.line([cx + w + 8, cy - h - 12, cx + 4, cy - h + 2], fill=TINTA, width=9)


def pecho(base, estado):
    """Pantalla del pecho con gráfica según estado."""
    d = ImageDraw.Draw(base)
    x0, y0, x1, y1 = 176, 470, 336, 590
    d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y1 + 8], radius=22,
                        fill=PANELC, outline=TINTA, width=7)
    d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=NEGRO,
                        outline=(40, 52, 76), width=4)
    cx = (x0 + x1) / 2
    if estado == 'duelo':
        pts = [(x0 + 12 + i * 7, 530 + math.sin(i * 0.9) * 34 * (1 if i % 2 else -0.4))
               for i in range(19)]
        d.line(pts, fill=ROJO, width=6)
        d.ellipse([cx - 16, 500, cx + 16, 532], outline=AMBAR, width=6)
    elif estado == 'derrotado':
        d.line([x0 + 14, 512, cx - 30, 512], fill=CIAN_LO, width=6)
        d.line([cx - 30, 512, cx - 10, 566], fill=CIAN_LO, width=6)
        d.line([cx - 10, 566, cx + 40, 566], fill=CIAN_LO, width=6)
        d.line([cx + 40, 566, cx + 60, 540], fill=CIAN_LO, width=6)
    elif estado == 'triunfante':
        d.polygon([(cx, 506), (cx + 10, 528), (cx + 34, 531), (cx + 16, 546),
                   (cx + 22, 570), (cx, 557), (cx - 22, 570), (cx - 16, 546),
                   (cx - 34, 531), (cx - 10, 528)], fill=AMBAR)
    else:
        pts = [(x0 + 12 + i * 7, 530 + math.sin(i * 0.55) * 22) for i in range(19)]
        d.line(pts, fill=CIAN, width=6)


def draw_ax9(estado):
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    CX = 256
    hover = estado == 'duelo'
    dy = -6 if hover else 0

    # ---- anillo antigrav (debajo, con glow) ----
    ry = 836 + dy
    glow(base, CX, ry, 128, CIAN, 90, blur=34)
    d = ImageDraw.Draw(base)
    def ring_shape(md, pad, mw, mh):
        md.ellipse([pad, pad + 26, mw - pad, mh - pad + 26], fill=255)
    pieza(base, ring_shape, (CX - 150, ry - 40, CX + 150, ry + 40),
          (196, 206, 224), (108, 120, 144), ow=8)
    d = ImageDraw.Draw(base)
    d.ellipse([CX - 106, ry - 20, CX + 106, ry + 20], outline=CIAN_LO, width=8)
    # nacelles
    for sx in (-1, 1):
        nx = CX + sx * 128
        def nac(md, pad, mw, mh):
            md.rounded_rectangle([pad, pad, mw - pad, mh - pad], radius=30, fill=255)
        pieza(base, nac, (nx - 34, ry - 52, nx + 34, ry + 34),
              CUERPO_A, CUERPO_B, ow=7)
        if hover:
            d.polygon([(nx, ry + 36), (nx - 16, ry + 36), (nx, ry + 84),
                       (nx + 16, ry + 36)], fill=CIAN)

    # ---- brazos + garras (detrás del torso) ----
    yh = 500 + dy
    if estado == 'triunfante':
        lados = [(-1, -2.35, True), (1, -0.80, True)]     # al aire
    elif estado == 'derrotado':
        lados = [(-1, 2.35, False), (1, 2.35, False)]     # caídos
    elif estado == 'duelo':
        lados = [(-1, -0.5, True), (1, -0.5, True)]       # al frente
    else:
        lados = [(-1, 1.85, False), (1, 1.30, False)]     # relajados
    for s, ang, abierto in lados:
        ex = CX + s * 128
        codox = CX + s * 172
        codoy = yh - 12 + (28 if ang > 0 else -30)
        linea(ImageDraw.Draw(base), (ex, yh), (codox, codoy), 30, CUERPO_B, TINTA)
        gx = codox + s * 26
        gy = codoy + (66 if ang > 1.5 else (-6 if ang < 0 else 60))
        linea(ImageDraw.Draw(base), (codox, codoy), (gx, gy), 24, (222, 230, 244), TINTA)
        garra(base, gx + s * 8, gy + (18 if ang > 1.5 else -8), ang + s * 0.2,
              1.0 if estado != 'derrotado' else 0.86, abierto)
        # chispas de duelo
        if estado == 'duelo':
            rsx = gx + s * 30
            d = ImageDraw.Draw(base)
            for k in range(5):
                a = math.pi * 2 * k / 5
                d.line([rsx, gy - 10, rsx + math.cos(a) * 20, gy - 10 + math.sin(a) * 20],
                       fill=AMBAR, width=5)

    # ---- torso ----
    def torso_shape(md, pad, mw, mh):
        md.rounded_rectangle([pad, pad, mw - pad, mh - pad], radius=64, fill=255)
    pieza(base, torso_shape, (CX - 122, 428 + dy, CX + 122, 668 + dy),
          CUERPO_A, CUERPO_B, ow=9)
    pecho(base, estado)
    d = ImageDraw.Draw(base)
    # ventilas laterales
    for sy in range(3):
        yy = 618 + dy + sy * 16
        d.rounded_rectangle([CX - 104, yy, CX - 66, yy + 9], radius=4, fill=(96, 106, 128))
        d.rounded_rectangle([CX + 66, yy, CX + 104, yy + 9], radius=4, fill=(96, 106, 128))
    # cinturón de luces
    d.rounded_rectangle([CX - 96, 648 + dy, CX + 96, 664 + dy], radius=8,
                        fill=NEGRO, outline=TINTA, width=4)
    for i, lx in enumerate(range(CX - 78, CX + 84, 26)):
        col = [VERDE, CIAN, AMBAR][(i + (1 if estado == 'duelo' else 0)) % 3]
        d.ellipse([lx - 6, 649 + dy, lx + 6, 663 + dy],
                  fill=col if estado != 'derrotado' else (70, 80, 96))

    # ---- cuello ----
    d.rounded_rectangle([CX - 34, 388 + dy, CX + 34, 442 + dy], radius=14,
                        fill=(96, 106, 128), outline=TINTA, width=6)

    # ---- cabeza ----
    hx0, hy0, hx1, hy1 = CX - 138, 196 + dy, CX + 138, 404 + dy
    def cabeza_shape(md, pad, mw, mh):
        md.rounded_rectangle([pad, pad, mw - pad, mh - pad], radius=74, fill=255)
    pieza(base, cabeza_shape, (hx0, hy0, hx1, hy1), CUERPO_A, CUERPO_B, ow=9)
    d = ImageDraw.Draw(base)
    # antena central + laterales
    d.line([CX, hy0, CX, hy0 - 44], fill=(96, 106, 128), width=10)
    d.ellipse([CX - 13, hy0 - 72, CX + 13, hy0 - 46],
              fill=ROJO if estado != 'derrotado' else (110, 70, 70),
              outline=TINTA, width=5)
    for s in (-1, 1):
        d.line([CX + s * 118, hy0 + 26, CX + s * 150, hy0 + 2],
               fill=(96, 106, 128), width=9)
        d.ellipse([CX + s * 150 - 10, hy0 - 10, CX + s * 150 + 10, hy0 + 14],
                  fill=PANELC, outline=TINTA, width=4)
    # visor
    vx0, vy0, vx1, vy1 = CX - 108, 268 + dy, CX + 108, 356 + dy
    d.rounded_rectangle([vx0 - 10, vy0 - 10, vx1 + 10, vy1 + 10], radius=40,
                        fill=PANELC, outline=TINTA, width=7)
    d.rounded_rectangle([vx0, vy0, vx1, vy1], radius=32, fill=NEGRO,
                        outline=(40, 52, 76), width=4)
    ey = (vy0 + vy1) / 2 - 6
    ojo(d, CX - 44, ey, estado)
    ojo(d, CX + 44, ey, estado)
    # boca / rejilla
    mb = vy1 + 24
    d.rounded_rectangle([CX - 52, mb, CX + 52, mb + 18], radius=8,
                        fill=(96, 106, 128), outline=TINTA, width=4)
    for gx in range(int(CX) - 40, int(CX) + 44, 13):
        d.line([gx, mb + 3, gx, mb + 15], fill=TINTA, width=4)
    if estado == 'derrotado':
        # humo del visor
        glow(base, CX - 60, vy0 - 10, 26, (150, 150, 160), 90, blur=22)
        glow(base, CX + 70, vy0 - 24, 20, (150, 150, 160), 70, blur=20)
    if estado == 'triunfante':
        glow(base, CX, hy0 - 60, 44, AMBAR, 80, blur=26)

    # luz de borde (rim light derecha)
    rim = Image.new('RGBA', base.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rounded_rectangle([hx1 - 26, hy0 + 30, hx1, hy1 - 26], radius=30,
                         fill=(190, 230, 255, 70))
    rd.rounded_rectangle([CX + 96, 448 + dy, CX + 122, 648 + dy], radius=30,
                         fill=(190, 230, 255, 60))
    rim = rim.filter(ImageFilter.GaussianBlur(7))
    base.alpha_composite(rim)
    return base


if __name__ == '__main__':
    for est in ('rival', 'idle', 'duelo', 'derrotado', 'triunfante'):
        img = draw_ax9(est)
        img.save(f'{OUT}/{est}.webp', quality=92, method=4)
        print('OK', est, img.size)

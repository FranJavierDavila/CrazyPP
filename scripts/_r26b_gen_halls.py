#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r26b (v3.6.122, FASE 124) — ARTE DE LOS 3 HALL NUEVOS.

Mismas fichas y PROPORCIONES EXACTAS de los planos que el museo y la
cabaña (c08_hall_hud.js):
  frente.jpg / fondo.jpg    1849×864  → plano 6,10×2,85
  izquierda.jpg / derecha.jpg 2395×864 → plano 7,90×2,85
  suelo.jpg / techo.jpg     1296×1678 → plano 6,10×7,90

  · NEÓN ARCADE  (synthwave: rejillas de neón, recreativas, letrero glow)
  · ESTACIÓN ORBITAL (paneles metálicos, ojos de buey, Tierra al ventanal)
  · DOJO ZEN     (shoji luminoso, tokonoma con ensō, tatami, ramas de cerezo)

Salida: public/assets/hall/<id>/*.jpg  (JPEG q82, arte 100% procedural).
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path
import math, random

RAIZ = Path('/home/z/my-project/upload/public/assets/hall')
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

random.seed(20261108)


def grad_v(w, h, arriba, abajo):
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(arriba[k] + (abajo[k] - arriba[k]) * t) for k in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def ruido(img, sigma=16, alfa=14):
    """Grano fino para que nada parezca plástico."""
    n = Image.effect_noise(img.size, sigma).convert('L')
    g = Image.merge('RGB', (n, n, n))
    return Image.blend(img, g, alfa / 255.0)


def vineta(img, fuerza=90):
    w, h = img.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-w * 0.25, -h * 0.25, w * 1.25, h * 1.25], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12))
    osc = Image.new('RGB', (w, h), (4, 4, 8))
    return Image.composite(img, Image.blend(img, osc, fuerza / 255.0), m)


def texto_glow(img, txt, xy, size, color, blur=14, angulado=0):
    f = ImageFont.truetype(FONT_B, size)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.text(xy, txt, font=f, fill=color + (255,), anchor='mm')
    if angulado:
        capa = capa.rotate(angulado, resample=Image.BICUBIC, center=xy)
    halo = capa.filter(ImageFilter.GaussianBlur(blur))
    img.paste(halo, (0, 0), halo)
    img.paste(capa, (0, 0), capa)
    return img


def glow_elipse(img, caja, color, blur):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.ellipse(caja, fill=color + (150,))
    halo = capa.filter(ImageFilter.GaussianBlur(blur))
    img.paste(halo, (0, 0), halo)
    return img


def grid_persp(d, w, h, horizonte, color_v, color_h, paso=110, hasta=None):
    """Rejilla sintwave: verticales convergen al punto de fuga central."""
    fuga = (w // 2, horizonte)
    for x in range(-w, 2 * w, paso):
        d.line([fuga, (x, h)], fill=color_v, width=3)
    y = horizonte + paso * 0.35
    n = 0
    while y < h:
        d.line([0, y, w, y], fill=color_h, width=2 + (n % 2))
        n += 1
        y += paso * (0.35 + 0.12 * n)


def estrella_pto(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def panelse(img, base_a, base_b, filas=5, cols=8, led=None):
    """Pared de paneles metálicos con bisel, remaches y tira LED opcional."""
    w, h = img.size
    img = grad_v(w, h, base_a, base_b)
    d = ImageDraw.Draw(img)
    pw, ph = w / cols, h / filas
    for j in range(filas):
        for i in range(cols):
            x0, y0 = i * pw, j * ph
            d.rectangle([x0, y0, x0 + pw, y0 + ph], outline=(20, 24, 30), width=4)
            d.line([x0 + 3, y0 + 3, x0 + pw - 3, y0 + 3], fill=(78, 90, 104), width=2)
            d.line([x0 + 3, y0 + 3, x0 + 3, y0 + ph - 3], fill=(64, 74, 88), width=2)
            d.line([x0 + 3, y0 + ph - 3, x0 + pw - 3, y0 + ph - 3], fill=(16, 19, 24), width=3)
            for rx, ry in ((8, 8), (pw - 8, 8), (8, ph - 8), (pw - 8, ph - 8)):
                d.ellipse([x0 + rx - 3, y0 + ry - 3, x0 + rx + 3, y0 + ry + 3],
                          fill=(110, 122, 136))
    if led:
        y = h * 0.075
        for x0, x1 in ((0, w * 0.31), (w * 0.36, w * 0.64), (w * 0.69, w)):
            d.rectangle([x0, y, x1, y + 7], fill=led)
            glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.rectangle([x0, y - 10, x1, y + 17], fill=led + (70,))
            hg = glow.filter(ImageFilter.GaussianBlur(9))
            img.paste(hg, (0, 0), hg)
    return img


def ojo_buey(img, cx, cy, r, interior):
    """Ventana circular con marco de pernos y contenido estrellado."""
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26],
              fill=(120, 134, 150), outline=(52, 60, 72), width=6)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=interior)
    dd = ImageDraw.Draw(img)
    for k in range(42):
        sx = cx - r + random.random() * 2 * r
        sy = cy - r + random.random() * 2 * r
        if (sx - cx) ** 2 + (sy - cy) ** 2 < (r - 6) ** 2:
            rr = random.choice((1, 1, 2, 2, 3))
            estrella_pto(dd, sx, sy, rr, (255, 255, 255))
    for a in range(8):
        ang = a * math.pi / 4
        px, py = cx + (r + 26) * math.cos(ang), cy + (r + 26) * math.sin(ang)
        dd.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(70, 80, 94))
    return img


def tierra(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30],
               fill=(110, 180, 255, 90))
    hg = glow.filter(ImageFilter.GaussianBlur(26))
    img.paste(hg, (0, 0), hg)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(43, 107, 191))
    # continentes orgánicos (blobs de círculos)
    random.seed(77)
    for _ in range(26):
        ax = cx + (random.random() * 2 - 1) * r * 0.78
        ay = cy + (random.random() * 2 - 1) * r * 0.78
        if (ax - cx) ** 2 + (ay - cy) ** 2 < (r * 0.82) ** 2:
            rr = r * (0.10 + random.random() * 0.16)
            d.ellipse([ax - rr, ay - rr * 0.7, ax + rr, ay + rr * 0.7],
                      fill=(63, 143, 95))
    # nubes
    for _ in range(18):
        ax = cx + (random.random() * 2 - 1) * r * 0.85
        ay = cy + (random.random() * 2 - 1) * r * 0.85
        if (ax - cx) ** 2 + (ay - cy) ** 2 < (r * 0.9) ** 2:
            rr = r * (0.06 + random.random() * 0.10)
            d.ellipse([ax - rr * 1.6, ay - rr * 0.5, ax + rr * 1.6, ay + rr * 0.5],
                      fill=(226, 238, 248))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(150, 200, 255), width=5)
    return img


def ensyo(img, cx, cy, r, color, wmax=26):
    """Círculo ensō a pincel: arco con grosor variable y hueco final."""
    d = ImageDraw.Draw(img)
    pas = 90
    for k in range(pas):
        t = k / pas
        ang0 = math.radians(-100 + t * 320)
        ang1 = ang0 + math.radians(320 / pas) + 0.02
        w = int(wmax * (1.25 - t) + 4)
        d.arc([cx - r, cy - r, cx + r, cy + r],
              math.degrees(ang0), math.degrees(ang1), fill=color, width=w)
    return img


# ═══════════════════════ NEÓN ARCADE ═══════════════════════
ROS = (255, 47, 150)
CIA = (41, 216, 255)
VIO = (138, 43, 226)
AMBAR = (255, 196, 80)


def neon_frente():
    w, h = 1849, 864
    img = grad_v(w, h, (16, 12, 40), (5, 5, 13))
    d = ImageDraw.Draw(img)
    grid_persp(d, w, h, int(h * 0.62), (ROS + (140,))[:3], (CIA + (90,))[:3], 130)
    # horizonte ardiente
    img = glow_elipse(img, (w * 0.2, h * 0.5, w * 0.8, h * 0.75), ROS, 60)
    d = ImageDraw.Draw(img)
    # fila de recreativas
    nrec, gap = 6, 40
    rw = (w - (nrec + 1) * gap) // nrec
    for k in range(nrec):
        x0 = gap + k * (rw + gap)
        y1 = int(h * 0.96)
        y0 = int(h * 0.42)
        d.rectangle([x0, y0, x0 + rw, y1], fill=(10, 9, 24), outline=(60, 50, 110), width=4)
        # marquesina superior de colores
        col = (ROS, CIA, AMBAR, VIO, (126, 255, 160), (255, 120, 220))[k % 6]
        d.rectangle([x0 + 12, y0 + 14, x0 + rw - 12, y0 + 62],
                    fill=(24, 20, 46), outline=col, width=3)
        # pantalla encendida
        d.rectangle([x0 + 18, y0 + 84, x0 + rw - 18, y0 + 240],
                    fill=(6, 10, 22), outline=(46, 44, 84), width=3)
        for j in range(5):
            sx = x0 + 30 + random.random() * (rw - 70)
            sy = y0 + 100 + random.random() * 120
            d.rectangle([sx, sy, sx + 26, sy + 8], fill=col)
        # panel de mandos + ranura
        d.rectangle([x0 + 14, y0 + 260, x0 + rw - 14, y0 + 330],
                    fill=(18, 16, 36), outline=(46, 44, 84), width=3)
        d.ellipse([x0 + rw * 0.3 - 16, y0 + 280 - 16, x0 + rw * 0.3 + 16, y0 + 280 + 16],
                  fill=col)
        d.ellipse([x0 + rw * 0.62 - 13, y0 + 284 - 13, x0 + rw * 0.62 + 13, y0 + 284 + 13],
                  fill=(90, 90, 110))
        d.rectangle([x0 + rw * 0.42 - 5, y0 + 346, x0 + rw * 0.42 + 5, y0 + 374],
                    fill=(200, 190, 120))
    # letrero glow
    img = texto_glow(img, 'CRAZY ARCADE', (w // 2, 92), 108, ROS, blur=22)
    d = ImageDraw.Draw(img)
    d.line([w * 0.22, 168, w * 0.78, 168], fill=CIA, width=6)
    # estrellas del techo
    for _ in range(70):
        estrella_pto(d, random.random() * w, random.random() * h * 0.3,
                     random.choice((1, 1, 2)), (200, 220, 255))
    return ruido(vineta(img), 14, 10)


def neon_fondo():
    w, h = 1849, 864
    img = grad_v(w, h, (12, 8, 32), (5, 5, 13))
    d = ImageDraw.Draw(img)
    grid_persp(d, w, h, int(h * 0.58), (CIA + (150,))[:3], (ROS + (90,))[:3], 120)
    img = glow_elipse(img, (w * 0.3, h * 0.42, w * 0.7, h * 0.74), VIO, 70)
    d = ImageDraw.Draw(img)
    # portal circular neón + triángulo interior
    cx, cy, r = w // 2, int(h * 0.55), 210
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ROS, width=10)
    d.ellipse([cx - r + 34, cy - r + 34, cx + r - 34, cy + r - 34], outline=CIA, width=5)
    tri = [(cx, cy - r * 0.52), (cx - r * 0.46, cy + r * 0.30), (cx + r * 0.46, cy + r * 0.30)]
    d.polygon(tri, outline=(255, 220, 90), width=6)
    # anillos flotantes
    for (ax, ay, ar, col) in ((w * 0.16, h * 0.35, 60, CIA), (w * 0.84, h * 0.30, 46, ROS),
                              (w * 0.10, h * 0.68, 34, AMBAR), (w * 0.90, h * 0.66, 40, VIO)):
        d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], outline=col, width=5)
    # bola de ping-pong neón al centro del portal
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(255, 250, 240))
    for _ in range(60):
        estrella_pto(d, random.random() * w, random.random() * h * 0.4,
                     random.choice((1, 1, 2)), (190, 210, 255))
    return ruido(vineta(img), 14, 10)


def neon_lateral(letra):
    w, h = 2395, 864
    img = grad_v(w, h, (13, 9, 34), (5, 5, 13))
    d = ImageDraw.Draw(img)
    grid_persp(d, w, h, int(h * 0.5), (ROS + (130,))[:3], (CIA + (100,))[:3], 140)
    img = glow_elipse(img, (w * 0.15, h * 0.2, w * 0.85, h * 0.8), VIO, 80)
    d = ImageDraw.Draw(img)
    # formas flotantes distintas por pared
    if letra == 'i':
        formas = [('hex', w * 0.22, h * 0.42, 120, CIA), ('anillo', w * 0.5, h * 0.35, 90, ROS),
                  ('tri', w * 0.78, h * 0.5, 110, AMBAR), ('anillo', w * 0.36, h * 0.68, 60, VIO)]
    else:
        formas = [('tri', w * 0.18, h * 0.45, 120, ROS), ('anillo', w * 0.46, h * 0.3, 84, CIA),
                  ('hex', w * 0.74, h * 0.42, 110, VIO), ('anillo', w * 0.6, h * 0.7, 58, AMBAR)]
    for f, fx, fy, fr, col in formas:
        if f == 'anillo':
            d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], outline=col, width=7)
        elif f == 'tri':
            d.polygon([(fx, fy - fr), (fx - fr, fy + fr * 0.8), (fx + fr, fy + fr * 0.8)],
                      outline=col, width=7)
        else:
            pts = [(fx + fr * math.cos(math.radians(60 * k - 30)),
                    fy + fr * math.sin(math.radians(60 * k - 30))) for k in range(6)]
            d.polygon(pts, outline=col, width=7)
    # tira de CRTs con barras de color
    y0 = int(h * 0.80)
    for k in range(5):
        x0 = 90 + k * ((w - 180) // 5)
        cw = (w - 180) // 5 - 30
        d.rectangle([x0, y0, x0 + cw, y0 + 120], fill=(8, 7, 18), outline=(60, 50, 110), width=4)
        for j, col in enumerate((ROS, AMBAR, CIA, (126, 255, 160), VIO)):
            d.rectangle([x0 + 10 + j * (cw - 20) // 5, y0 + 40,
                         x0 + 10 + (j + 1) * (cw - 20) // 5, y0 + 92], fill=col)
    for _ in range(80):
        estrella_pto(d, random.random() * w, random.random() * h * 0.32,
                     random.choice((1, 1, 2)), (190, 210, 255))
    return ruido(vineta(img), 14, 10)


def neon_suelo():
    w, h = 1296, 1678
    img = grad_v(w, h, (24, 8, 34), (5, 5, 12))
    d = ImageDraw.Draw(img)
    # rejilla que converge hacia el CENTRO superior (el punto lejano del suelo)
    fuga = (w // 2, int(h * 0.12))
    for x in range(-w, 2 * w, 120):
        d.line([fuga, (x, h)], fill=(ROS), width=3)
    y = int(h * 0.14)
    n = 0
    while y < h:
        d.line([0, y, w, y], fill=CIA, width=2 + (n % 2))
        n += 1
        y += int(46 * (1 + n * 0.16))
    # emblema central: doble anillo + bola + letrero
    cx, cy = w // 2, int(h * 0.52)
    img = glow_elipse(img, (cx - 250, cy - 250, cx + 250, cy + 250), VIO, 50)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 235, cy - 235, cx + 235, cy + 235], outline=ROS, width=9)
    d.ellipse([cx - 175, cy - 175, cx + 175, cy + 175], outline=CIA, width=5)
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(255, 250, 240))
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], outline=AMBAR, width=5)
    img = texto_glow(img, 'CRAZY PP', (cx, cy + 330), 96, CIA, blur=18)
    return ruido(vineta(img, 70), 16, 12)


def neon_techo():
    w, h = 1296, 1678
    img = grad_v(w, h, (7, 6, 16), (14, 10, 30))
    d = ImageDraw.Draw(img)
    # vigas de celosía en X + luces pequeñas
    paso = h // 8
    for j in range(8):
        y = j * paso + paso // 2
        d.line([0, y, w, y], fill=(40, 34, 66), width=10)
        for k in range(9):
            x0, x1 = k * (w // 8), (k + 1) * (w // 8)
            d.line([x0, y - 26, x1, y + 26], fill=(34, 28, 56), width=6)
            d.line([x0, y + 26, x1, y - 26], fill=(34, 28, 56), width=6)
            if k % 2 == 0:
                d.ellipse([x0 + 8, y - 8, x0 + 24, y + 8], fill=AMBAR)
    # resplandor central (la sala arde abajo)
    img = glow_elipse(img, (w * 0.25, h * 0.7, w * 0.75, h * 1.05), ROS, 80)
    return ruido(vineta(img, 60), 14, 8)


# ═══════════════════════ ESTACIÓN ORBITAL ═══════════════════════
PN_A = (58, 66, 78)
PN_B = (30, 35, 43)
LED = (53, 200, 255)


def orb_frente():
    w, h = 1849, 864
    img = panelse(Image.new('RGB', (w, h)), PN_A, PN_B, 5, 8, led=LED)
    d = ImageDraw.Draw(img)
    # gran ventanal de 3 arcos con la TIERRA al centro
    marco = (92, 104, 120)
    cx, cy, rw, rh = w // 2, int(h * 0.52), 300, int(h * 0.40)
    for dx in (-rw * 1.52, 0, rw * 1.52):
        x0, x1 = cx + dx - rw, cx + dx + rw
        y0, y1 = cy - rh, cy + int(rh * 0.62)
        d.rounded_rectangle([x0, y0, x1, y1], radius=90, fill=(6, 8, 16),
                            outline=marco, width=16)
    tierra(img, cx, cy - 40, 170)
    # estrellas en los paneles laterales del ventanal
    dd = ImageDraw.Draw(img)
    for dx in (-rw * 1.52, rw * 1.52):
        for _ in range(40):
            sx = cx + dx + random.random() * 2 * rw - rw
            sy = cy - rh + random.random() * (rh * 1.6)
            if abs(sx - (cx + dx)) < rw - 20 and cy - rh + 20 < sy < cy + rh * 0.6 - 20:
                estrella_pto(dd, sx, sy, random.choice((1, 1, 2)), (255, 255, 255))
    # marco de pernos del ventanal
    for px in (cx - rw * 1.52, cx, cx + rw * 1.52):
        for py in (cy - rh, cy + int(rh * 0.62)):
            d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(150, 162, 176))
    # placa de misión
    d.rounded_rectangle([cx - 210, h - 86, cx + 210, h - 30], radius=8,
                        fill=(40, 46, 56), outline=(90, 100, 114), width=3)
    for k in range(6):
        d.line([cx - 180, h - 74 + k * 8, cx + 180, h - 74 + k * 8],
               fill=(120, 132, 146), width=2)
    return ruido(vineta(img, 60), 12, 8)


def orb_lateral(letra, w=2395):
    h = 864
    img = panelse(Image.new('RGB', (w, h)), PN_A, PN_B, 5, 11, led=LED)
    x1, x2 = w * 0.30, w * 0.70
    ojo_buey(img, int(x1), int(h * 0.46), 128, (5, 7, 14))
    ojo_buey(img, int(x2), int(h * 0.46), 128, (5, 7, 14))
    # la Tierra asoma por el ojo de buey derecho/izquierdo
    dd = ImageDraw.Draw(img)
    clip = Image.new('L', img.size, 0)
    cd = ImageDraw.Draw(clip)
    cx, cy, r = int(x2 if letra == 'd' else x1), int(h * 0.46), 128
    cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    t = Image.new('RGB', img.size, (0, 0, 0))
    tierra(t, cx + int(r * 0.5), cy + int(r * 0.34), 90)
    img.paste(t, (0, 0), clip)
    d = ImageDraw.Draw(img)
    # escotilla con rueda central
    hx = int(w * 0.5)
    hy = int(h * 0.48)
    d.ellipse([hx - 150, hy - 150, hx + 150, hy + 150], fill=(38, 44, 54),
              outline=(120, 132, 148), width=14)
    d.ellipse([hx - 118, hy - 118, hx + 118, hy + 118], outline=(70, 80, 94), width=6)
    for a in range(3):
        ang = a * math.pi / 1.5
        d.line([hx, hy, hx + 112 * math.cos(ang), hy + 112 * math.sin(ang)],
               fill=(140, 152, 168), width=12)
    d.ellipse([hx - 26, hy - 26, hx + 26, hy + 26], fill=(160, 172, 188))
    # tuberías a lo alto
    for py, col in ((int(h * 0.10), (96, 106, 120)), (int(h * 0.16), (72, 82, 96))):
        d.line([0, py, w, py], fill=col, width=16)
        for k in range(12):
            x = k * (w // 12) + 40
            d.rectangle([x, py - 12, x + 18, py + 12], fill=(52, 60, 72))
    # placas de etiquetas
    for k in range(4):
        x0 = 120 + k * (w // 4)
        d.rounded_rectangle([x0, h - 96, x0 + 220, h - 44], radius=6,
                            fill=(44, 50, 60), outline=(88, 98, 112), width=3)
        d.line([x0 + 16, h - 80, x0 + 204, h - 80], fill=(120, 132, 146), width=3)
        d.line([x0 + 16, h - 62, x0 + 150, h - 62], fill=(96, 106, 120), width=3)
    return ruido(vineta(img, 60), 12, 8)


def orb_suelo():
    w, h = 1296, 1678
    img = grad_v(w, h, (44, 51, 62), (22, 26, 32))
    d = ImageDraw.Draw(img)
    # cubierta metálica: retícula de placas + brillo diagonal
    pw, ph = w // 6, h // 10
    for j in range(10):
        for i in range(6):
            x0, y0 = i * pw, j * ph
            d.rectangle([x0 + 4, y0 + 4, x0 + pw - 4, y0 + ph - 4],
                        outline=(24, 28, 34), width=4)
            d.line([x0 + 6, y0 + 6, x0 + pw - 6, y0 + 6], fill=(84, 96, 110), width=2)
    for k in range(-4, 14):
        x = k * (w // 5)
        d.line([x, 0, x + w * 0.5, h], fill=(70, 82, 96), width=1)
    # emblema orbital: 3 anillos giratorios + bola blanca
    cx, cy = w // 2, int(h * 0.52)
    img = glow_elipse(img, (cx - 260, cy - 260, cx + 260, cy + 260), LED, 46)
    d = ImageDraw.Draw(img)
    for rot, rr in ((18, 235), (64, 185), (110, 135)):
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(capa)
        cd.ellipse([cx - rr, cy - rr // 2, cx + rr, cy + rr // 2],
                   outline=LED + (255,), width=8)
        capa = capa.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
        img.paste(capa, (0, 0), capa)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 54, cy - 54, cx + 54, cy + 54], fill=(255, 252, 244),
              outline=(150, 200, 255), width=6)
    img = texto_glow(img, 'ESTACION 7', (cx, cy + 320), 78, (120, 180, 230), blur=14)
    return ruido(vineta(img, 70), 14, 9)


def orb_techo():
    w, h = 1296, 1678
    img = grad_v(w, h, (30, 35, 43), (44, 51, 62))
    d = ImageDraw.Draw(img)
    # dos barras de luz larga con halo + conductos
    for cx in (int(w * 0.3), int(w * 0.7)):
        d.rounded_rectangle([cx - 26, h * 0.06, cx + 26, h * 0.94], radius=20,
                            fill=(235, 246, 255))
        glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.rounded_rectangle([cx - 60, h * 0.04, cx + 60, h * 0.96], radius=30,
                             fill=(160, 220, 255, 80))
        hg = glow.filter(ImageFilter.GaussianBlur(30))
        img.paste(hg, (0, 0), hg)
    d = ImageDraw.Draw(img)
    for px in (w * 0.12, w * 0.88):
        d.line([px, h * 0.05, px, h * 0.95], fill=(70, 80, 94), width=14)
        for k in range(9):
            y = h * 0.08 + k * (h * 0.1)
            d.rectangle([px - 10, y, px + 10, y + 22], fill=(48, 56, 68))
    return ruido(vineta(img, 55), 12, 8)


# ═══════════════════════ DOJO ZEN ═══════════════════════
MAD = (138, 90, 52)
MAD_O = (109, 68, 38)
PAPEL_A = (244, 233, 210)
PAPEL_B = (224, 205, 172)
TAT_A = (154, 168, 106)
TAT_B = (138, 152, 92)


def shoji(img, cols=5, filas=4, luz=True):
    """Retícula de shoji: celosía de madera sobre papel translúcido."""
    w, h = img.size
    base = grad_v(w, h, PAPEL_A if luz else PAPEL_B, PAPEL_B if luz else (206, 186, 152))
    base = ruido(base, 10, 6)
    img.paste(base, (0, 0))
    d = ImageDraw.Draw(img)
    pw, ph = w / cols, h / filas
    for j in range(filas + 1):
        d.line([0, j * ph, w, j * ph], fill=MAD, width=10)
    for i in range(cols + 1):
        d.line([i * pw, 0, i * pw, h], fill=MAD, width=12)
    # travesaños interiores finos
    for j in range(filas):
        for i in range(cols):
            x0, y0 = i * pw, j * ph
            d.line([x0, y0 + ph / 2, x0 + pw, y0 + ph / 2], fill=MAD_O, width=4)
    # pilar madera a cada lado
    d.rectangle([0, 0, int(w * 0.045), h], fill=MAD, outline=MAD_O, width=3)
    d.rectangle([int(w * 0.955), 0, w, h], fill=MAD, outline=MAD_O, width=3)
    # zócalo
    d.rectangle([0, h - 26, w, h], fill=(70, 44, 26))
    return img


def dojo_frente():
    w, h = 1849, 864
    img = Image.new('RGB', (w, h))
    img = shoji(img, 6, 4)
    d = ImageDraw.Draw(img)
    # TOKONOMA: alcoba central de madera oscura con pergamino
    ax0, ax1 = int(w * 0.36), int(w * 0.64)
    ay0, ay1 = int(h * 0.10), int(h * 0.88)
    d.rectangle([ax0, ay0, ax1, ay1], fill=(36, 26, 18), outline=MAD, width=16)
    d.rectangle([ax0 + 14, ay0 + 14, ax1 - 14, ay1 - 14], fill=(24, 17, 12))
    # pergamino colgante
    px0 = (ax0 + ax1) // 2
    d.rectangle([px0 - 120, ay0 + 40, px0 + 120, ay1 - 120],
                fill=(240, 232, 214), outline=(150, 130, 100), width=6)
    ensyo(img, px0, (ay0 + ay1) // 2 - 40, 92, (40, 40, 46), 22)
    d = ImageDraw.Draw(img)
    # varilla y cordel
    d.line([px0 - 140, ay0 + 34, px0 + 140, ay0 + 34], fill=(90, 60, 36), width=10)
    # ramas de cerezo cruzando la parte alta
    br = [(int(w * 0.05), int(h * 0.16)), (int(w * 0.2), int(h * 0.24)),
          (int(w * 0.38), int(h * 0.15)), (int(w * 0.6), int(h * 0.2)),
          (int(w * 0.8), int(h * 0.12)), (int(w * 0.97), int(h * 0.2))]
    d.line(br, fill=(96, 62, 40), width=12)
    for k in range(len(br) - 1):
        x0, y0 = br[k]
        d.line([x0, y0, x0 + 40, y0 + 46], fill=(96, 62, 40), width=7)
    for _ in range(46):
        bx = random.uniform(w * 0.04, w * 0.96)
        by = random.uniform(h * 0.06, h * 0.32)
        r = random.uniform(9, 20)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(245, 184, 200))
        d.ellipse([bx - r * 0.3, by - r * 0.3, bx + r * 0.3, by + r * 0.3],
                  fill=(255, 240, 246))
    # farolillos cálidos a los lados de la alcoba
    for fx in (int(w * 0.30), int(w * 0.70)):
        fy = int(h * 0.40)
        d.line([fx, h * 0.18, fx, fy - 70], fill=(80, 54, 32), width=6)
        d.ellipse([fx - 54, fy - 70, fx + 54, fy + 70], fill=(255, 208, 130),
                  outline=(120, 80, 44), width=6)
        d.line([fx - 54, fy, fx + 54, fy], fill=(120, 80, 44), width=4)
    return ruido(vineta(img, 70), 10, 7)


def dojo_lateral(letra, w=2395):
    h = 864
    img = Image.new('RGB', (w, h))
    img = shoji(img, 7, 4)
    d = ImageDraw.Draw(img)
    # bambú vertical con nudos entre paneles
    for k in range(6):
        bx = int(w * (0.14 + k * 0.145))
        for seg in range(4):
            y0 = seg * (h // 4) + 14
            y1 = (seg + 1) * (h // 4) - 6
            d.line([bx, y0, bx, y1], fill=(106, 148, 84), width=9)
            d.line([bx - 5, y1, bx + 5, y1], fill=(78, 110, 62), width=8)
    # cuadro colgante con ensō pequeño
    qx = int(w * (0.36 if letra == 'i' else 0.64))
    d.rectangle([qx - 110, int(h * 0.24), qx + 110, int(h * 0.60)],
                fill=(28, 22, 16), outline=MAD, width=10)
    d.rectangle([qx - 96, int(h * 0.26), qx + 96, int(h * 0.58)],
                fill=(238, 230, 212))
    ensyo(img, qx, int(h * 0.42), 62, (44, 44, 50), 15)
    return ruido(vineta(img, 70), 10, 7)


def dojo_suelo():
    w, h = 1296, 1678
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    # tatami: bandas horizontales alternas con juntas oscuras + trama
    nb = 9
    bh = h // nb
    for j in range(nb):
        y0 = j * bh
        col = TAT_A if j % 2 == 0 else TAT_B
        d.rectangle([0, y0, w, y0 + bh], fill=col)
        d.line([0, y0, w, y0], fill=(86, 98, 58), width=6)
        for k in range(0, w, 9):
            d.line([k, y0 + 6, k, y0 + bh - 6], fill=(0, 0, 0, 0) or
                   (col[0] - 12, col[1] - 12, col[2] - 10), width=1)
    # borde de tela de los tatamis
    d.rectangle([0, 0, w, 26], fill=(70, 54, 40))
    d.rectangle([0, h - 26, w, h], fill=(70, 54, 40))
    # ensō central de tinta + bola
    cx, cy = w // 2, h // 2
    ensyo(img, cx, cy, 300, (36, 38, 44), 30)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=(255, 250, 238),
              outline=(198, 188, 168), width=6)
    d.arc([cx - 74, cy - 74, cx + 74, cy + 74], 110, 250, fill=(206, 196, 176), width=8)
    img = texto_glow(img, 'DOJO', (cx, cy + 470), 84, (70, 52, 36), blur=10)
    return ruido(vineta(img, 60), 12, 8)


def dojo_techo():
    w, h = 1296, 1678
    img = grad_v(w, h, (44, 32, 22), (58, 42, 28))
    d = ImageDraw.Draw(img)
    # vigas gruesas cruzadas + paneles de papel entre ellas
    nb = 8
    bh = h // nb
    for j in range(nb):
        d.rectangle([0, j * bh, w, j * bh + 34], fill=(50, 36, 24),
                    outline=(30, 22, 15), width=3)
        d.line([0, j * bh + 4, w, j * bh + 4], fill=(96, 72, 48), width=4)
    for k in range(1, 4):
        x = k * (w // 4)
        d.rectangle([x - 17, 0, x + 17, h], fill=(46, 33, 22))
    # paneles de papel (glow cálido) entre vigas
    for j in range(nb):
        for k in range(4):
            x0 = k * (w // 4) + 22
            y0 = j * bh + 38
            d.rectangle([x0, y0, x0 + w // 4 - 44, y0 + bh - 42], fill=(226, 206, 172))
    # farol central
    cx, cy = w // 2, int(h * 0.5)
    d.line([cx, 0, cx, cy - 90], fill=(60, 44, 30), width=8)
    d.ellipse([cx - 110, cy - 90, cx + 110, cy + 90], fill=(255, 214, 150),
              outline=(140, 96, 52), width=8)
    d.line([cx - 110, cy, cx + 110, cy], fill=(140, 96, 52), width=6)
    return ruido(vineta(img, 55), 12, 8)


SALIDA = {
    'neon': {'frente': neon_frente, 'fondo': neon_fondo,
             'izquierda': lambda: neon_lateral('i'), 'derecha': lambda: neon_lateral('d'),
             'suelo': neon_suelo, 'techo': neon_techo},
    'orbital': {'frente': orb_frente, 'fondo': lambda: orb_lateral('f', 1849),
                'izquierda': lambda: orb_lateral('i'), 'derecha': lambda: orb_lateral('d'),
                'suelo': orb_suelo, 'techo': orb_techo},
    'dojo': {'frente': dojo_frente, 'fondo': lambda: dojo_lateral('f', 1849),
             'izquierda': lambda: dojo_lateral('i'), 'derecha': lambda: dojo_lateral('d'),
             'suelo': dojo_suelo, 'techo': dojo_techo},
}

total = 0
for hall, fichas in SALIDA.items():
    carp = RAIZ / hall
    carp.mkdir(parents=True, exist_ok=True)
    for ficha, gen in fichas.items():
        p = carp / (ficha + '.jpg')
        gen().save(p, quality=82, optimize=True)
        kb = p.stat().st_size / 1024
        total += kb
        print(f'  ✓ hall/{hall}/{ficha}.jpg {kb:.0f} KB')
print(f'total: {total / 1024:.2f} MB')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTACIÓN ORBITAL — ARTE DE PERSONAJE, TROQUELES, ICONOS Y PRUEBAS
  · rival.webp + idle/duelo/derrotado/triunfante.webp  (512×1024, ALFA)
    ANDROIDE AX-9: robot flotante retro, visor de un ojo, anillo antigrav.
  · decor/troquel1-3.png  (512×640, ALFA): cohete · rover · satélite
  · powerestrellas/powermeteoritos/powertractor/powercero.png (512×512
    RGBA): medallones de superpoder (familia powerburla: anillo + oro)
  · asteroide.png · caja.png · dron.png (256×256, ALFA): dianas de pruebas
Estilo cartoon: rellenos planos + contorno oscuro, como el resto del juego.
"""
import math
import os
import random
from PIL import Image, ImageDraw

OUT = '/home/z/my-project/public/championships/estacion_orbital/assets'
os.makedirs(OUT + '/decor', exist_ok=True)

# ------------------------------------------------------------------ paleta
TINTA = (14, 18, 30, 255)
CUERPO = (234, 240, 250, 255)
CUERPO_HI = (250, 253, 255, 255)
CUERPO_LO = (188, 199, 220, 255)
JUNTA = (52, 60, 80, 255)
JUNTA_LO = (34, 40, 56, 255)
VISCERA = (79, 216, 255, 255)       # cian visor / núcleo
VISCERA_LO = (26, 108, 140, 255)
AMBAR = (255, 163, 71, 255)
AMBAR_LO = (196, 108, 34, 255)
ROJO = (255, 92, 84, 255)
GRIS = (128, 140, 160, 255)
ESPACIO = (10, 14, 26, 255)


def linea_gorda(d, p0, p1, w, fill, outline=None):
    """Cápsula: línea gruesa con tapas redondas (contorno opcional)."""
    w = int(round(w))
    if outline:
        d.line([p0, p1], fill=outline, width=w + 8)
        for p in (p0, p1):
            d.ellipse([p[0] - (w + 8) / 2, p[1] - (w + 8) / 2,
                       p[0] + (w + 8) / 2, p[1] + (w + 8) / 2], fill=outline)
    d.line([p0, p1], fill=fill, width=w)
    for p in (p0, p1):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2],
                  fill=fill)


def disco(d, cx, cy, r, fill, outline=None, ow=6):
    if outline:
        d.ellipse([cx - r - ow / 2, cy - r - ow / 2,
                   cx + r + ow / 2, cy + r + ow / 2], fill=outline)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def pildora(d, x0, y0, x1, y1, fill, outline=None, ow=6):
    if outline:
        d.rounded_rectangle([x0 - ow / 2, y0 - ow / 2, x1 + ow / 2, y1 + ow / 2],
                            radius=(y1 - y0) / 2 + ow / 2, fill=outline)
    d.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) / 2, fill=fill)


def _i(v):
    return int(round(v))


# ==================================================================== AX-9
def garra(d, cx, cy, ang, scale=1.0):
    """Pinza de dos dedos orientada por ang (rad)."""
    L = 46 * scale
    a1 = ang - 0.55
    a2 = ang + 0.55
    for a in (a1, a2):
        x1 = cx + L * math.cos(a)
        y1 = cy + L * math.sin(a)
        linea_gorda(d, (cx, cy), (x1, y1), 14 * scale, GRIS, TINTA)
        # punta
        x2 = x1 + 16 * scale * math.cos(a + 0.6)
        y2 = y1 + 16 * scale * math.sin(a + 0.6)
        linea_gorda(d, (x1, y1), (x2, y2), 10 * scale, JUNTA, TINTA)
    disco(d, cx, cy, 15 * scale, JUNTA, TINTA)


def brazo(d, sx, sy, hx, hy, w=30):
    """Brazo segmentado: hombro→codo→muñeca."""
    mx = (sx + hx) / 2 + 18          # codo desplazado
    my = (sy + hy) / 2 + 10
    linea_gorda(d, (sx, sy), (mx, my), w, CUERPO, TINTA)
    linea_gorda(d, (mx, my), (hx, hy), w - 4, CUERPO, TINTA)
    disco(d, mx, my, w * 0.42, JUNTA, TINTA, 5)


def visor(d, modo, ex, ey, ew, eh):
    """Visor de un ojo: banda oscura + ojo expresivo."""
    d.rounded_rectangle([ex - ew, ey - eh, ex + ew, ey + eh], radius=eh * 0.8,
                        fill=JUNTA_LO, outline=TINTA, width=6)
    if modo == 'off':
        # apagado: brillo muerto + chispa
        d.ellipse([ex - 26, ey - 14, ex + 26, ey + 14], fill=(70, 78, 96))
        d.line([ex - 18, ey - 12, ex + 18, ey + 12], fill=GRIS, width=7)
        d.line([ex - 18, ey + 12, ex + 18, ey - 12], fill=GRIS, width=7)
        return
    if modo == 'narrow':
        d.polygon([(ex - 52, ey + 26), (ex + 52, ey + 26),
                   (ex + 30, ey - 22), (ex - 30, ey - 8)], fill=VISCERA)
        d.polygon([(ex - 40, ey + 22), (ex + 40, ey + 22),
                   (ex + 24, ey - 12), (ex - 24, ey - 2)],
                  fill=(200, 245, 255))
        d.ellipse([ex + 12, ey - 2, ex + 34, ey + 20], fill=CUERPO_HI)
    elif modo == 'happy':
        d.arc([ex - 46, ey - 26, ex + 46, ey + 34], 200, 340,
              fill=VISCERA, width=16)
    elif modo == 'sad':
        d.arc([ex - 46, ey - 30, ex + 46, ey + 30], 20, 160,
              fill=VISCERA, width=14)
    else:   # round
        disco(d, ex, ey, 34, VISCERA)
        disco(d, ex + 9, ey - 9, 12, (210, 248, 255))


def chispas(d, pts, seed=3):
    rnd = random.Random(seed)
    for (x, y) in pts:
        for _ in range(5):
            a = rnd.uniform(0, 2 * math.pi)
            L = rnd.uniform(14, 42)
            x1, y1 = x + L * math.cos(a), y + L * math.sin(a)
            d.line([x, y, x1, y1], fill=(255, 236, 140, 255), width=4)
            d.ellipse([x1 - 4, y1 - 4, x1 + 4, y1 + 4],
                      fill=(255, 250, 200, 255))


def humo(d, pts, seed=5):
    rnd = random.Random(seed)
    for (x, y) in pts:
        for k in range(4):
            r = rnd.uniform(16, 34)
            dx = rnd.uniform(-28, 28)
            dy = -k * 30 + rnd.uniform(-8, 8)
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                      fill=(120, 126, 140, 150))


def estrellitas(d, pts):
    for (x, y) in pts:
        for i in range(4):
            a = math.pi / 2 * i + 0.4
            d.line([x - 16 * math.cos(a), y - 16 * math.sin(a),
                    x + 16 * math.cos(a), y + 16 * math.sin(a)],
                   fill=(255, 224, 130, 255), width=5)
        disco(d, x, y, 7, (255, 244, 200))


def draw_ax9(estado='idle'):
    """ANDROIDE AX-9 — 512×1024 RGBA. Flota sobre su anillo antigrav."""
    im = Image.new('RGBA', (512, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    modo_brazos = 'down'
    ojo = 'round'
    cx = 256

    # ---- ANILLO ANTIGRAV + cono de empuje (bajo el torso) -----------------
    # (detrás: lo primero)
    d.ellipse([cx - 118, 882, cx + 118, 962], fill=VISCERA_LO, outline=TINTA, width=6)
    d.ellipse([cx - 84, 898, cx + 84, 946], fill=(120, 230, 255, 255))
    d.polygon([(cx - 70, 812), (cx + 70, 812), (cx + 96, 892), (cx - 96, 892)],
              fill=(56, 150, 190, 110))

    # ---- PIERNAS cortas (pistones) ----------------------------------------
    for sx in (cx - 62, cx + 62):
        linea_gorda(d, (sx, 780), (sx, 892), 34, JUNTA, TINTA)
        disco(d, sx, 892, 24, GRIS, TINTA, 5)

    # ---- BRAZOS según pose ------------------------------------------------
    if estado in ('rival', 'idle'):
        modo_brazos = 'down'
        brazo(d, 128, 505, 96, 700)
        brazo(d, 384, 505, 416, 700)
        garra(d, 96, 726, math.pi / 2)
        garra(d, 416, 726, math.pi / 2)
        ojo = 'round'
    elif estado == 'duelo':
        modo_brazos = 'fight'
        brazo(d, 128, 505, 58, 620)
        brazo(d, 384, 505, 454, 620)
        garra(d, 52, 640, -1.9, 1.15)
        garra(d, 460, 640, -1.24, 1.15)
        ojo = 'narrow'
    elif estado == 'derrotado':
        brazo(d, 128, 505, 118, 730)
        brazo(d, 384, 505, 394, 730)
        garra(d, 118, 752, math.pi / 2 + 0.3)
        garra(d, 394, 752, math.pi / 2 - 0.3)
        ojo = 'off'
    else:   # triunfante
        brazo(d, 128, 505, 74, 380)
        brazo(d, 384, 505, 438, 380)
        garra(d, 62, 352, -0.9, 1.1)
        garra(d, 450, 352, -2.24, 1.1)
        ojo = 'happy'

    # ---- TORSO (delante de los brazos: cápsula blanca) --------------------
    d.rounded_rectangle([126, 428, 386, 812], radius=96, fill=CUERPO,
                        outline=TINTA, width=8)
    d.rounded_rectangle([150, 448, 362, 700], radius=80, fill=CUERPO_HI)
    # panel pectoral ámbar
    d.rounded_rectangle([186, 640, 326, 700], radius=22, fill=AMBAR,
                        outline=TINTA, width=5)
    d.line([200, 668, 312, 668], fill=AMBAR_LO, width=6)
    # NÚCLEO cian
    disco(d, cx, 560, 62, JUNTA_LO, TINTA, 7)
    disco(d, cx, 560, 48, VISCERA)
    disco(d, cx - 12, 548, 14, (215, 250, 255))
    # remaches laterales
    for (rx, ry) in ((150, 480), (362, 480), (150, 760), (362, 760)):
        disco(d, rx, ry, 8, GRIS)

    # ---- HOMBROS ----------------------------------------------------------
    disco(d, 126, 470, 44, JUNTA, TINTA, 7)
    disco(d, 386, 470, 44, JUNTA, TINTA, 7)
    disco(d, 126, 470, 20, GRIS)
    disco(d, 386, 470, 20, GRIS)
    # los brazos salen DETRÁS del torso en pose down… redibujar hombros ok

    # ---- CUELLO + CABEZA --------------------------------------------------
    d.rounded_rectangle([cx - 26, 384, cx + 26, 436], radius=14, fill=JUNTA,
                        outline=TINTA, width=6)
    tilt = 0
    if estado == 'derrotado':
        tilt = 26            # cabeza caída
    # cabeza: caja redondeada
    hx0, hy0, hx1, hy1 = 146, 178 + tilt, 366, 396 + tilt
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=64, fill=CUERPO,
                        outline=TINTA, width=8)
    d.rounded_rectangle([hx0 + 18, hy0 + 16, hx1 - 18, hy0 + 88], radius=40,
                        fill=CUERPO_HI)
    # orejas-bulón
    for exx in (hx0 - 2, hx1 + 2):
        disco(d, exx, (hy0 + hy1) / 2, 20, AMBAR, TINTA, 6)
    # antena
    linea_gorda(d, (cx, hy0 + 6), (cx, hy0 - 44), 10, GRIS, TINTA)
    disco(d, cx, hy0 - 58, 18, ROJO if estado != 'derrotado' else GRIS,
          TINTA, 5)
    # VISOR
    visor(d, ojo, cx, (hy0 + hy1) / 2 + 8, 96, 46)

    # ---- EXTRAS por estado -------------------------------------------------
    if estado == 'derrotado':
        chispas(d, [(150, 600), (370, 690), (cx, 430)])
        humo(d, [(cx - 60, 780), (cx + 80, 800)])
    elif estado == 'triunfante':
        estrellitas(d, [(70, 250), (440, 230), (cx, 120)])
    elif estado == 'duelo':
        chispas(d, [(52, 640), (460, 640)])

    # sombra flotante
    d.ellipse([cx - 96, 956, cx + 96, 992], fill=(0, 0, 0, 60))
    return im


for est in ('rival', 'idle', 'duelo', 'derrotado', 'triunfante'):
    im = draw_ax9(est)
    im.save(f'{OUT}/{est}.webp', 'WEBP', lossless=True)
    print(est, os.path.getsize(f'{OUT}/{est}.webp'))


# ============================================================== TROQUELES
def troquel_cohete():
    im = Image.new('RGBA', (512, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = 256
    # cuerpo
    d.polygon([(cx - 88, 300), (cx + 88, 300), (cx + 66, 560), (cx - 66, 560)],
              fill=CUERPO, outline=TINTA)
    # morro
    d.polygon([(cx - 88, 300), (cx + 88, 300), (cx, 96)], fill=ROJO,
              outline=TINTA)
    # aletas
    d.polygon([(cx - 88, 380), (cx - 168, 560), (cx - 88, 560)], fill=AMBAR,
              outline=TINTA)
    d.polygon([(cx + 88, 380), (cx + 168, 560), (cx + 88, 560)], fill=AMBAR,
              outline=TINTA)
    # ventana
    disco(d, cx, 330, 52, JUNTA_LO, TINTA, 8)
    disco(d, cx, 330, 36, VISCERA)
    disco(d, cx - 10, 320, 10, (220, 250, 255))
    # llama
    d.polygon([(cx - 44, 560), (cx + 44, 560), (cx, 640)], fill=(255, 170, 60),
              outline=TINTA)
    d.polygon([(cx - 22, 560), (cx + 22, 560), (cx, 610)],
              fill=(255, 236, 140))
    # estrellas de fondo
    for (sx, sy) in ((60, 80), (440, 60), (90, 240), (430, 210)):
        disco(d, sx, sy, 5, (255, 240, 190))
    im.save(OUT + '/decor/troquel1.png')


def troquel_rover():
    im = Image.new('RGBA', (512, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # chasis
    d.rounded_rectangle([70, 330, 442, 470], radius=40, fill=CUERPO,
                        outline=TINTA, width=8)
    d.rounded_rectangle([100, 356, 250, 444], radius=18, fill=AMBAR,
                        outline=TINTA, width=5)
    d.rounded_rectangle([268, 356, 412, 444], radius=18, fill=VISCERA_LO,
                        outline=TINTA, width=5)
    # cabina
    d.rounded_rectangle([150, 230, 330, 330], radius=44, fill=CUERPO_HI,
                        outline=TINTA, width=8)
    d.rounded_rectangle([178, 254, 302, 316], radius=24, fill=JUNTA_LO)
    d.ellipse([196, 268, 232, 302], fill=VISCERA)
    # antena parabólica
    linea_gorda(d, (390, 330), (390, 240), 12, GRIS, TINTA)
    d.pieslice([330, 160, 450, 280], 180, 360, fill=AMBAR, outline=TINTA)
    # ruedas (6)
    for wx in (110, 256, 402):
        disco(d, wx, 500, 62, JUNTA_LO, TINTA, 8)
        disco(d, wx, 500, 26, GRIS)
        for k in range(6):
            a = math.pi * k / 3
            d.line([wx - 40 * math.cos(a), 500 - 40 * math.sin(a),
                    wx + 40 * math.cos(a), 500 + 40 * math.sin(a)],
                   fill=(70, 80, 100), width=6)
    # suelo lunar sugerido
    d.ellipse([40, 560, 472, 610], fill=(150, 148, 160, 120))
    im.save(OUT + '/decor/troquel2.png')


def troquel_satelite():
    im = Image.new('RGBA', (512, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 256, 320
    # paneles solares
    for sgn in (-1, 1):
        x0 = cx + sgn * 90
        x1 = cx + sgn * 240
        d.rounded_rectangle([min(x0, x1), cy - 70, max(x0, x1), cy + 70],
                            radius=12, fill=(40, 70, 150), outline=TINTA,
                            width=8)
        for k in range(4):
            yy = cy - 70 + (140 / 4) * k
            d.line([min(x0, x1), yy, max(x0, x1), yy],
                   fill=(90, 130, 220), width=4)
        d.line([x0, cy - 70, x0, cy + 70], fill=JUNTA, width=8)
    # cuerpo
    disco(d, cx, cy, 92, CUERPO, TINTA, 8)
    disco(d, cx, cy, 60, CUERPO_HI)
    disco(d, cx - 16, cy - 18, 16, VISCERA)
    # antenas
    linea_gorda(d, (cx, cy - 92), (cx, cy - 190), 10, GRIS, TINTA)
    disco(d, cx, cy - 204, 16, ROJO, TINTA, 4)
    for a in (0.6, 2.5, -0.6):
        linea_gorda(d, (cx + 80 * math.cos(a), cy + 80 * math.sin(a)),
                    (cx + 170 * math.cos(a), cy + 170 * math.sin(a)),
                    8, GRIS, TINTA)
        disco(d, cx + 176 * math.cos(a), cy + 176 * math.sin(a), 9, AMBAR)
    # estrellas
    for (sx, sy) in ((80, 90), (440, 120), (60, 520), (450, 540)):
        disco(d, sx, sy, 5, (255, 240, 190))
    im.save(OUT + '/decor/troquel3.png')


troquel_cohete()
troquel_rover()
troquel_satelite()
print('troqueles OK')


# ============================================================== ICONOS (medallón)
def medallon(nombre, interior_fn):
    """Medallón 512×512: interior espacio + anillo acero + bordes oro."""
    S = 512
    CX = CY = S / 2
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    R_IN, R_BAND, R_OUT = 196, 40, 252
    # interior
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    interior_fn(ImageDraw.Draw(lay), CX, CY, R_IN)
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse((CX - R_IN, CY - R_IN, CX + R_IN, CY + R_IN),
                                 fill=255)
    img.paste(lay, (0, 0), mask)
    # anillo acero con tornes
    band = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.pieslice((CX - R_IN - R_BAND, CY - R_IN - R_BAND,
                 CX + R_IN + R_BAND, CY + R_IN + R_BAND), 0, 360,
                fill=(74, 92, 122, 255))
    bd.pieslice((CX - R_IN - R_BAND + 8, CY - R_IN - R_BAND + 8,
                 CX + R_IN + R_BAND - 8, CY + R_IN + R_BAND - 8), 0, 360,
                fill=(120, 142, 174, 255))
    hole = Image.new('L', (S, S), 0)
    ImageDraw.Draw(hole).ellipse((CX - R_IN + 2, CY - R_IN + 2,
                                  CX + R_IN - 2, CY + R_IN - 2), fill=255)
    band.putalpha(Image.composite(Image.new('L', (S, S), 0),
                                  band.getchannel('A'), hole))
    img.alpha_composite(band)
    # remaches del anillo
    dd = ImageDraw.Draw(img)
    for i in range(8):
        a = 2 * math.pi * i / 8 + math.pi / 8
        rr = R_IN + R_BAND / 2
        dd.ellipse([CX + rr * math.cos(a) - 9, CY + rr * math.sin(a) - 9,
                    CX + rr * math.cos(a) + 9, CY + rr * math.sin(a) + 9],
                   fill=(60, 74, 100, 255))
    # bordes dorados
    gold = (212, 175, 55, 255)
    dd.arc((CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT), 0, 360,
           fill=gold, width=10)
    dd.arc((CX - R_IN - R_BAND - 4, CY - R_IN - R_BAND - 4,
            CX + R_IN + R_BAND + 4, CY + R_IN + R_BAND + 4), 0, 360,
           fill=gold, width=6)
    dd.arc((CX - R_IN - 2, CY - R_IN - 2, CX + R_IN + 2, CY + R_IN + 2),
           0, 360, fill=gold, width=4)
    img.save(OUT + '/' + nombre)
    print(nombre, os.path.getsize(OUT + '/' + nombre))


def fondo_espacio(d, cx, cy, R):
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=ESPACIO)
    rnd = random.Random(9)
    for _ in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        rr = R * math.sqrt(rnd.random()) * 0.94
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r = rnd.choice([2, 2, 3, 4])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 228, 244, 255))


def art_estrellas(d, cx, cy, R):
    fondo_espacio(d, cx, cy, R)
    # cometa: estrella con cola
    sx, sy = cx - R * 0.30, cy - R * 0.16
    for k in range(7):
        t = k / 7
        rr = 64 * (1 - t * 0.75)
        px = sx - (0.72 * R) * t
        py = sy + (0.34 * R) * t
        col = (255, int(236 - 90 * t), int(150 - 80 * t), 200 - int(160 * t))
        d.ellipse([px - rr, py - rr * 0.62, px + rr, py + rr * 0.62], fill=col)
    # estrella de 5 puntas
    pts = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        rr = 58 if i % 2 == 0 else 24
        pts.append((sx + rr * math.cos(a), sy + rr * math.sin(a)))
    d.polygon(pts, fill=(255, 224, 130, 255), outline=(150, 110, 30, 255))
    d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(255, 250, 220, 255))
    # estrellitas
    for (x, y) in ((cx - 90, cy - 120), (cx + 110, cy - 80), (cx + 60, cy + 120)):
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(240, 246, 255, 255))


def art_meteoritos(d, cx, cy, R):
    fondo_espacio(d, cx, cy, R)
    mx, my = cx + R * 0.18, cy + R * 0.10
    # cola de fuego
    for k in range(8):
        t = k / 8
        rr = (78 - 40 * t)
        px = mx - (0.85 * R) * t
        py = my + (0.5 * R) * t
        col = (255, int(180 - 120 * t), int(90 - 60 * t), 210 - int(170 * t))
        d.ellipse([px - rr, py - rr * 0.7, px + rr, py + rr * 0.7], fill=col)
    # roca
    rnd = random.Random(4)
    pts = []
    for i in range(9):
        a = 2 * math.pi * i / 9
        rr = 92 * rnd.uniform(0.78, 1.05)
        pts.append((mx + rr * math.cos(a), my + rr * math.sin(a)))
    d.polygon(pts, fill=(150, 132, 116, 255), outline=(58, 46, 40, 255))
    d.polygon([(px, py) for (px, py) in pts[:5]], fill=(172, 152, 134, 255))
    # cráteres
    for (ox, oy, cr) in ((-30, -20, 18), (26, 18, 13), (10, -38, 9)):
        d.ellipse([mx + ox - cr, my + oy - cr, mx + ox + cr, my + oy + cr],
                  fill=(112, 96, 84, 255))
    # destello de impacto
    d.line([mx + 60, my - 60, mx + 110, my - 110], fill=(255, 240, 170, 255),
           width=8)
    d.line([mx + 84, my - 30, mx + 132, my - 52], fill=(255, 240, 170, 255),
           width=6)


def art_tractor(d, cx, cy, R):
    fondo_espacio(d, cx, cy, R)
    # OVNI arriba
    ux, uy = cx - 10, cy - R * 0.52
    d.ellipse([ux - 60, uy - 42, ux + 60, uy + 42], fill=(160, 170, 190, 255),
              outline=(30, 36, 52, 255))
    d.ellipse([ux - 34, uy - 62, ux + 34, uy - 6], fill=(140, 240, 190, 255),
              outline=(30, 36, 52, 255))
    for i in range(5):
        lx = ux - 44 + i * 22
        d.ellipse([lx - 6, uy + 22, lx + 6, uy + 34],
                  fill=(255, 224, 130, 255))
    # haz tractor (cono) hacia una bola
    d.polygon([(ux - 40, uy + 30), (ux + 40, uy + 30),
               (cx + 90, cy + 110), (cx - 90, cy + 110)],
              fill=(120, 240, 190, 90))
    for k in range(3):
        yy = uy + 60 + k * 52
        ww = 52 + k * 26
        d.line([cx - ww, yy, cx + ww, yy], fill=(150, 245, 205, 110), width=8)
    # bola atrapada
    bx, by = cx, cy + 96
    d.ellipse([bx - 44, by - 44, bx + 44, by + 44], fill=(255, 250, 244, 255),
              outline=(30, 36, 52, 255))
    d.arc([bx - 44, by - 44, bx + 44, by + 44], 200, 320,
          fill=(255, 170, 90, 255), width=8)


def art_cero(d, cx, cy, R):
    fondo_espacio(d, cx, cy, R)
    # bola flotante con anillo orbital
    bx, by = cx, cy - R * 0.10
    # halo de ingravidez
    for rr, al in ((120, 60), (150, 34)):
        d.ellipse([bx - rr, by - rr, bx + rr, by + rr],
                  fill=(120, 220, 255, al))
    d.ellipse([bx - 78, by - 78, bx + 78, by + 78], fill=(255, 250, 244, 255),
              outline=(30, 36, 52, 255))
    d.arc([bx - 78, by - 78, bx + 78, by + 78], 200, 320,
          fill=(255, 170, 90, 255), width=10)
    # anillo orbital elíptico
    d.arc([bx - 140, by - 56, bx + 140, by + 56], 0, 180,
          fill=(140, 245, 255, 255), width=12)
    d.arc([bx - 140, by - 56, bx + 140, by + 56], 180, 360,
          fill=(70, 160, 190, 255), width=12)
    # satélite chiquito en el anillo
    sxx, syy = bx + 140, by
    d.rounded_rectangle([sxx - 18, syy - 12, sxx + 18, syy + 12], radius=6,
                        fill=(170, 180, 200, 255), outline=(30, 36, 52, 255))
    # motitas flotando
    for (x, y) in ((cx - 120, cy + 100), (cx + 120, cy - 110)):
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(210, 240, 255, 220))


medallon('powerestrellas.png', art_estrellas)
medallon('powermeteoritos.png', art_meteoritos)
medallon('powertractor.png', art_tractor)
medallon('powercero.png', art_cero)


# ============================================================== DIANAS DE PRUEBAS
def asteroide(nombre, base, semilla):
    im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(semilla)
    cx = cy = 128
    pts = []
    for i in range(11):
        a = 2 * math.pi * i / 11
        rr = 108 * rnd.uniform(0.72, 1.0)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=base, outline=(40, 32, 28, 255))
    # cara iluminada
    d.polygon(pts[:6], fill=tuple(min(255, c + 26) for c in base[:3]) + (255,))
    # cráteres
    for _ in range(6):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, 70)
        ox, oy = cx + rr * math.cos(a), cy + rr * math.sin(a)
        cr = rnd.uniform(8, 20)
        d.ellipse([ox - cr, oy - cr, ox + cr, oy + cr],
                  fill=tuple(max(0, c - 40) for c in base[:3]) + (255,))
        d.arc([ox - cr, oy - cr, ox + cr, oy + cr], 200, 340,
              fill=(210, 190, 170, 160), width=4)
    im.save(OUT + '/' + nombre)
    print(nombre, os.path.getsize(OUT + '/' + nombre))


asteroide('asteroide.png', (150, 132, 116, 255), 11)
asteroide('asteroide2.png', (116, 122, 140, 255), 23)


def caja():
    im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([24, 34, 232, 226], radius=18, fill=(96, 110, 138, 255),
                        outline=(26, 32, 46, 255), width=8)
    d.rounded_rectangle([40, 48, 216, 212], radius=10,
                        fill=(70, 82, 108, 255))
    # franjas de peligro arriba
    x = 40
    while x < 216:
        d.polygon([(x, 48), (x + 16, 48), (x + 4, 78), (x - 12, 78)],
                  fill=(255, 179, 71, 255))
        x += 32
    # emblema cian
    d.ellipse([96, 100, 160, 164], fill=(26, 108, 140, 255),
              outline=(18, 24, 36, 255), width=4)
    d.ellipse([112, 116, 144, 148], fill=(120, 230, 255, 255))
    # tornillos
    for (x, y) in ((50, 196), (206, 196)):
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(140, 154, 178, 255))
    im.save(OUT + '/caja.png')
    print('caja.png', os.path.getsize(OUT + '/caja.png'))


caja()


def dron():
    im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = 128, 132
    # brazos con hélices
    for sgn in (-1, 1):
        linea_gorda(d, (cx, cy - 10), (cx + sgn * 84, cy - 44), 14,
                    (70, 82, 108, 255), (26, 32, 46, 255))
        d.ellipse([cx + sgn * 84 - 34, cy - 78, cx + sgn * 84 + 34, cy - 10],
                  fill=(110, 126, 154, 255), outline=(26, 32, 46, 255))
    # cuerpo
    disco(d, cx, cy + 14, 56, (160, 172, 194, 255), (26, 32, 46, 255), 7)
    disco(d, cx, cy + 8, 30, (18, 24, 38, 255))
    disco(d, cx, cy + 8, 20, (120, 230, 255, 255))
    disco(d, cx + 6, cy + 2, 7, (230, 252, 255, 255))
    # luz inferior
    d.ellipse([cx - 10, cy + 52, cx + 10, cy + 72], fill=(255, 92, 84, 255))
    im.save(OUT + '/dron.png')
    print('dron.png', os.path.getsize(OUT + '/dron.png'))


dron()
print('ARTE EO OK')

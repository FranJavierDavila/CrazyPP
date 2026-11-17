#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTACIÓN ORBITAL — ARTE V2 DE LA SALA (v2.130, «plantilla final» pulida)
Mejoras sobre v3:
  · texturas con ASPECTO REAL de los planos (núcleo estira la imagen):
      suelo/techo 6,10×7,90 → 1024×1328 · frontales 6,10×2,85 → 1536×718
      laterales 7,90×2,85 → 1536×554
  · MUCHO más detalle: oclusión ambiental, dobles biseles, remaches,
    tubos con brillos, consolas con gráficas, ventanales con nebulosa
    multicapa, franjas de aviso, señética, manchas y desgaste
  · zona CALMA reservada en la pared IZQUIERDA justo donde cuelga el
    MAPA del campeonato (u 0,305..0,517 · v 0,365..0,687) con marco
    remachado — el póster se monta encima (convención de la casa)
Estilo cartoon espacial coherente: acero azul profundo + cian #4fd8ff
+ ámbar #ffb347.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = '/home/z/my-project/public/championships/estacion_orbital/assets'
os.makedirs(OUT, exist_ok=True)
random.seed(47)

# ------------------------------------------------------------- tipografía
_FDIR = '/usr/share/fonts/truetype/dejavu'
_FCACHE = {}

def F(sz, bold=True):
    """Fuente DejaVu (tildes/ñ correctos) con caché."""
    key = (sz, bold)
    if key not in _FCACHE:
        _FCACHE[key] = ImageFont.truetype(
            (_FDIR + '/DejaVuSans-Bold.ttf') if bold else (_FDIR + '/DejaVuSans.ttf'),
            sz)
    return _FCACHE[key]

# ---------------------------------------------------------------- paleta
ESPACIO = (7, 10, 20)
AZUL_HONDO = (12, 19, 33)
PANEL = (30, 42, 66)
PANEL_2 = (37, 51, 79)
PANEL_HI = (58, 76, 110)
STEEL = (76, 94, 124)
STEEL_LO = (42, 55, 82)
STEEL_HI = (120, 140, 172)
CIAN = (79, 216, 255)
CIAN_LO = (38, 120, 155)
CIAN_DARK = (16, 52, 74)
AMBAR = (255, 179, 71)
AMBAR_DARK = (168, 104, 28)
BLANCO = (232, 238, 250)
ROJO = (255, 96, 88)
VERDE = (105, 240, 174)
VIOLETA = (150, 96, 220)
PLANETA = (72, 140, 208)
PLANETA_LO = (38, 84, 146)
PLANETA_HI = (120, 190, 240)


# ------------------------------------------------------------- utilidades
def lienzo(w, h):
    img = Image.new('RGB', (w, h), AZUL_HONDO)
    return img, ImageDraw.Draw(img)


def capa(w, h):
    """Capa RGBA independiente (para glows que se pegan con alpha_composite)."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def pegar(base, capa_img, blur=0):
    if blur:
        capa_img = capa_img.filter(ImageFilter.GaussianBlur(blur))
    base.paste(capa_img, (0, 0), capa_img)


def ruido(img, cantidad=9, alfa=14):
    """Grano sutil determinista para que el acero no quede plano."""
    w, h = img.size
    px = img.load()
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y][:3]
            n = random.randint(-cantidad, cantidad)
            px[x, y] = (max(0, min(255, r + n)),
                        max(0, min(255, g + n)),
                        max(0, min(255, b + n)))
    return img


def vineta(img, fuerza=110, inset=0.18):
    """Oclusión ambiental en bordes (vignette) — da profundidad de sala."""
    w, h = img.size
    m, dc = capa(w, h)
    steps = 26
    for i in range(steps):
        k = i / steps
        a = int(fuerza * (k ** 1.6))
        dc.rectangle([int(w * inset * k), int(h * inset * k),
                      w - int(w * inset * k) - 1, h - int(h * inset * k) - 1],
                     outline=(4, 6, 12, a))
    pegar(img, m, blur=8)


def panel(d, x0, y0, x1, y1, fill=PANEL, edge=PANEL_HI, lo=STEEL_LO, rw=3):
    """Panel metálico con bisel doble."""
    d.rectangle([x0, y0, x1, y1], fill=fill)
    d.line([x0, y0, x1, y0], fill=edge, width=rw)
    d.line([x0, y0, x0, y1], fill=edge, width=rw)
    d.line([x0, y1, x1, y1], fill=lo, width=rw + 1)
    d.line([x1, y0, x1, y1], fill=lo, width=rw + 1)


def remaches(d, pts, r=5):
    for (x, y) in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=STEEL)
        d.ellipse([x - r + 1, y - r + 1, x + r - 1, y - 1], fill=STEEL_HI)
        d.ellipse([x - r + 2, y - r + 2, x + r, y + r], fill=STEEL_LO)


def franja_aviso(d, x0, y0, x1, y1, vertical=False, paso=34):
    """Franja rayada ámbar/negro de aviso industrial."""
    d.rectangle([x0, y0, x1, y1], fill=(28, 30, 36))
    if vertical:
        n = int((y1 - y0) / paso) + 1
        for i in range(-1, n + 1):
            yy = y0 + i * paso
            d.polygon([(x0, min(yy + paso, y1)), (x1, max(yy - paso + paso, y0)),
                       (x1, min(yy, y1)), (x0, min(yy + paso // 1, y1))], fill=AMBAR)
            # (polígono simple en diagonal)
        for i in range(-1, n + 2):
            yy = y0 + i * paso * 2
            d.polygon([(x0, yy), (x1, yy - (x1 - x0)), (x1, yy - (x1 - x0) + paso // 2),
                       (x0, yy + paso // 2)], fill=AMBAR)
    else:
        n = int((x1 - x0) / paso) + 2
        for i in range(-1, n):
            xx = x0 + i * paso * 2
            d.polygon([(xx, y1), (xx + paso, y1), (xx + paso + (y1 - y0), y0),
                       (xx + (y1 - y0), y0)], fill=AMBAR)


def tuberia_h(d, y, x0, x1, r=13, col=STEEL, hi=STEEL_HI, lo=STEEL_LO):
    d.rectangle([x0, y - r, x1, y + r], fill=col)
    d.line([x0, y - r, x1, y - r], fill=hi, width=3)
    d.line([x0, y + r - 2, x1, y + r - 2], fill=lo, width=4)
    for x in range(x0 + 40, x1, 210):
        d.rectangle([x - 8, y - r - 5, x + 8, y + r + 5], fill=(52, 64, 92))
        d.rectangle([x - 8, y - r - 5, x + 8, y - r - 2], fill=STEEL_HI)


def estrella(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def destello4(d, x, y, r, col, a):
    """Destello de 4 puntas."""
    d.polygon([(x - r * 3, y), (x, y - r), (x + r * 3, y), (x, y + r)], fill=col)
    d.polygon([(x, y - r * 3), (x + r, y), (x, y + r * 3), (x - r, y)], fill=col)


def campo_estrellas(img, d, n=170, semilla=7):
    rs = random.Random(semilla)
    for i in range(n):
        x = rs.uniform(0, img.width)
        y = rs.uniform(0, img.height)
        r = 1 if rs.random() < 0.8 else 2
        col = (159, 216, 255) if rs.random() < 0.25 else (235, 242, 255)
        estrella(d, x, y, r, col)
        if rs.random() < 0.06:
            destello4(d, x, y, 2, (210, 235, 255), 0)


def nebulosa(img, cx, cy, rx, ry, semilla=3):
    """Nebulosa multicapa suave (para ventanales)."""
    rs = random.Random(semilla)
    m, dm = capa(img.width, img.height)
    cols = [(120, 70, 190, 46), (60, 130, 210, 52), (40, 170, 190, 38),
            (190, 90, 150, 30)]
    for i in range(46):
        cc = cols[i % len(cols)]
        ang = rs.uniform(0, math.tau)
        rad = rs.uniform(0, 1)
        x = cx + math.cos(ang) * rx * rad
        y = cy + math.sin(ang) * ry * rad * 0.62
        r = rs.uniform(28, 105) * (1.15 - rad * 0.5)
        dm.ellipse([x - r, y - r, x + r, y + r], fill=cc)
    pegar(img, m, blur=34)


def planeta_anillado(img, cx, cy, R, ang=-0.30):
    """Planeta con anillo (recorte elíptico por capas, look cartoon)."""
    w, h = img.size
    m, dm = capa(w, h)
    # sombra proyectada del planeta sobre el anillo trasero
    dm.ellipse([cx - R, cy - R, cx + R, cy + R], fill=PLANETA)
    # bandas de nubes
    for i, cc in enumerate([PLANETA_HI, (92, 160, 224), PLANETA_LO,
                            (56, 104, 168), PLANETA_HI, PLANETA_LO]):
        yy = cy - R + (i + 0.5) * (2 * R / 6)
        grosor = R / 7.5
        dm.ellipse([cx - R + 3, yy - grosor, cx + R - 3, yy + grosor], fill=cc)
    # terminador día/noche
    som, ds = capa(w, h)
    ds.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(6, 9, 18, 150))
    ds.ellipse([cx - R * 0.85, cy - R * 0.92, cx + R * 0.35, cy + R * 0.75],
               fill=(0, 0, 0, 0))
    pegar(img, som.filter(ImageFilter.GaussianBlur(10)))
    del som, ds
    # anillo (mitad trasera → planeta → mitad delantera)
    an, dn = capa(w, h)
    for rr, aa in [(1.62, 210), (1.44, 150), (1.82, 120)]:
        dn.ellipse([cx - R * rr, cy - R * rr * 0.30, cx + R * rr, cy + R * rr * 0.30],
                   outline=(216, 196, 160, aa), width=max(3, int(R * 0.05)))
    an = an.rotate(0)
    pegar(img, an)
    del an, dn
    pegar(img, m)          # el planeta encima del anillo trasero
    del m, dm
    m2, d2 = capa(w, h)
    for rr, aa in [(1.62, 235), (1.44, 170), (1.82, 140)]:
        bbox = [cx - R * rr, cy - R * rr * 0.30, cx + R * rr, cy + R * rr * 0.30]
        d2.ellipse(bbox, outline=(226, 208, 172, aa), width=max(3, int(R * 0.05)))
    # tapa la mitad SUPERIOR del anillo (queda detrás del planeta):
    d2.rectangle([0, 0, w, cy], fill=(0, 0, 0, 0))
    # recorte: sólo la parte que pasa POR DELANTE (semieje inferior)
    mascara = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mascara)
    md.ellipse([cx - R * 1.05, cy - R * 1.02, cx + R * 1.05, cy + R * 1.05], fill=255)
    md.rectangle([0, 0, w, cy], fill=0)
    m2.putalpha(Image.composite(m2.split()[3], Image.new('L', (w, h), 0), mascara))
    pegar(img, m2)
    del m2, d2


def glow_circulo(img, cx, cy, r, col, a=90, blur=16):
    m, dm = capa(img.width, img.height)
    dm.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    pegar(img, m, blur=blur)


def pantalla_consola(d, x0, y0, x1, y1, grafica=CIAN, semilla=1):
    """Monitor con gráficas (barras/ondas) — vida de sala."""
    rs = random.Random(semilla)
    d.rectangle([x0, y0, x1, y1], fill=(10, 16, 28))
    d.rectangle([x0, y0, x1, y1], outline=STEEL_LO, width=3)
    mx0, my0, mx1, my1 = x0 + 6, y0 + 6, x1 - 6, y1 - 6
    # onda
    pts = []
    for i in range(0, mx1 - mx0, 6):
        yy = (my0 + my1) / 2 + math.sin(i * 0.11 + semilla) * (my1 - my0) * 0.28
        pts.append((mx0 + i, yy))
    d.line(pts, fill=grafica, width=3)
    # barras
    n = max(3, (mx1 - mx0) // 22)
    for i in range(n):
        bh = rs.uniform(0.2, 0.9) * (my1 - my0) * 0.8
        bx = mx0 + 4 + i * ((mx1 - mx0 - 8) / n)
        d.rectangle([bx, my1 - bh, bx + 10, my1], fill=AMBAR if rs.random() < 0.2 else CIAN_DARK)


def tubo_luz(img, x0, y, x1, col=CIAN, grosor=8, halo=26):
    m, dm = capa(img.width, img.height)
    dm.rectangle([x0, y - grosor // 2, x1, y + grosor // 2], fill=col + (235,))
    pegar(img, m)
    g, dg = capa(img.width, img.height)
    dg.rectangle([x0, y - grosor, x1, y + grosor], fill=col + (110,))
    pegar(img, g, blur=halo)
    del m, g


# =====================================================================
#  SUELO  (1024×1328 = 6,10 × 7,90 m · u=0 en x −3,05 … u=1 en x +3,05)
# =====================================================================
def gen_suelo():
    W, H = 1024, 1328
    img, d = lienzo(W, H)
    # base con gradiente longitudinal (más luz bajo las lámparas del techo)
    for y in range(H):
        k = y / H
        base = (int(16 + 10 * math.sin(k * math.pi)), int(24 + 12 * math.sin(k * math.pi)),
                int(40 + 14 * math.sin(k * math.pi)))
        d.line([0, y, W, y], fill=base)
    # losa grande: placas 4×5 con junta cian luminosa
    cols, rows = 4, 5
    pw, ph = W // cols, H // rows
    for cx in range(cols):
        for cy in range(rows):
            x0, y0 = cx * pw, cy * ph
            tono = PANEL if (cx + cy) % 2 == 0 else PANEL_2
            panel(d, x0 + 6, y0 + 6, x0 + pw - 6, y0 + ph - 6, fill=tono)
            remaches(d, [(x0 + 20, y0 + 20), (x0 + pw - 20, y0 + 20),
                         (x0 + 20, y0 + ph - 20), (x0 + pw - 20, y0 + ph - 20),
                         (x0 + pw // 2, y0 + 18), (x0 + pw // 2, y0 + ph - 18)])
            # textura antideslizante: rombos tenues
            rs = random.Random(cx * 31 + cy * 7)
            for i in range(26):
                bx = rs.uniform(x0 + 40, x0 + pw - 40)
                by = rs.uniform(y0 + 40, y0 + ph - 40)
                s = 7
                d.polygon([(bx, by - s), (bx + s, by), (bx, by + s), (bx - s, by)],
                          outline=(48, 62, 92))
    # juntas luminosas cian
    g, dg = capa(W, H)
    for cx in range(1, cols):
        dg.line([cx * pw, 0, cx * pw, H], fill=CIAN + (70,), width=4)
    for cy in range(1, rows):
        dg.line([0, cy * ph, W, cy * ph], fill=CIAN + (70,), width=4)
    pegar(img, g, blur=6)
    del g
    # calle de guía hacia la mesa (líneas discontinuas ámbar) — u centrada
    for sx in (-1, 1):
        x = W // 2 + sx * 150
        for y in range(60, H - 60, 110):
            d.rectangle([x - 7, y, x + 7, y + 56], fill=AMBAR_DARK)
    # escotilla de acceso (abajo, lado jugador) + franja de aviso
    franja_aviso(d, W - 250, H - 96, W - 20, H - 22)
    d.ellipse([60, H - 180, 190, H - 50], outline=STEEL_HI, width=8)
    d.ellipse([84, H - 156, 166, H - 74], outline=CIAN_LO, width=5)
    remaches(d, [(125, H - 190), (125, H - 40), (52, H - 115), (198, H - 115)])
    # desgaste: roces y manchas
    rs = random.Random(99)
    for i in range(24):
        x, y = rs.uniform(30, W - 30), rs.uniform(30, H - 30)
        r = rs.uniform(8, 30)
        d.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4],
                  outline=(26, 34, 52), width=2)
    ruido(img, 8)
    vineta(img, 95)
    img.save(f'{OUT}/sala_floor.jpg', quality=90)


# =====================================================================
#  TECHO  (1024×1328)
# =====================================================================
def gen_techo():
    W, H = 1024, 1328
    img, d = lienzo(W, H)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(9 + 8 * k), int(14 + 9 * k), int(26 + 11 * k)))
    # vigas longitudinales
    for x in (120, 512, 904):
        d.rectangle([x - 26, 0, x + 26, H], fill=(24, 33, 52))
        d.line([x - 26, 0, x - 26, H], fill=PANEL_HI, width=3)
        d.line([x + 26, 0, x + 26, H], fill=STEEL_LO, width=4)
        remaches(d, [(x, yy) for yy in range(40, H, 150)], r=6)
    # tuberías con brillo
    tuberia_h(d, 190, 40, W - 40, r=15)
    tuberia_h(d, 250, 40, W - 40, r=9, col=(58, 74, 104))
    tuberia_h(d, H - 170, 40, W - 40, r=12)
    # anillo de LEDs central + 2 paneles de luz (los del núcleo van en x±1,4 →
    # en textura: u = (x+3,05)/6,10 → x_px = u*W → ±1,4 → 277 y 747)
    for px in (277, 747):
        d.rounded_rectangle([px - 120, 470, px + 120, 860], radius=26, fill=(228, 242, 255))
        d.rounded_rectangle([px - 120, 470, px + 120, 860], radius=26, outline=STEEL_HI, width=6)
        glow_circulo(img, px, 665, 210, (180, 225, 255), 60, blur=60)
        remaches(d, [(px - 108, 486), (px + 108, 486), (px - 108, 844), (px + 108, 844)])
    m, dm = capa(W, H)
    dm.ellipse([W // 2 - 210, H // 2 - 210, W // 2 + 210, H // 2 + 210],
               outline=CIAN + (150,), width=10)
    dm.ellipse([W // 2 - 260, H // 2 - 260, W // 2 + 260, H // 2 + 260],
               outline=CIAN_DARK + (110,), width=6)
    pegar(img, m, blur=2)
    del m
    # rejillas de ventilación
    for gy in (H - 420, H - 350):
        d.rectangle([380, gy, 644, gy + 44], fill=(18, 26, 42))
        for lx in range(390, 636, 18):
            d.line([lx, gy + 6, lx, gy + 38], fill=STEEL_LO, width=5)
    ruido(img, 7)
    vineta(img, 105)
    img.save(f'{OUT}/sala_ceil.jpg', quality=90)


# =====================================================================
#  PARED FRONTAL (donde está el rival)  1536×718 = 6,10 × 2,85 m
#  u=0 en x −3,05 … u=1 en x +3,05 (v=0 abajo)
# =====================================================================
def gen_frontal():
    W, H = 1536, 718
    img, d = lienzo(W, H)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(13 + 6 * k), int(21 + 8 * k), int(37 + 11 * k)))
    # VENTANAL GRANDE al espacio (centro-derecha, el rival Flota a la derecha)
    vx0, vy0, vx1, vy1 = 560, 90, 1450, 470
    space = Image.new('RGB', (vx1 - vx0, vy1 - vy0), ESPACIO)
    sd = ImageDraw.Draw(space)
    campo_estrellas(space, sd, n=190, semilla=5)
    nebulosa(space, 340, 190, 300, 150, semilla=3)
    nebulosa(space, 700, 300, 240, 120, semilla=9)
    planeta_anillado(space, 620, 210, 120)
    img.paste(space, (vx0 + 10, vy0 + 10))
    # marco del ventanal
    d.rectangle([vx0, vy0, vx1, vy1], outline=STEEL_HI, width=14)
    d.rectangle([vx0 + 14, vy0 + 14, vx1 - 14, vy1 - 14], outline=STEEL_LO, width=6)
    # montante central
    d.rectangle([(vx0 + vx1) // 2 - 12, vy0, (vx0 + vx1) // 2 + 12, vy1], fill=(30, 40, 62))
    remaches(d, [(vx0 + 8, vy0 + 8), (vx1 - 8, vy0 + 8), (vx0 + 8, vy1 - 8),
                 (vx1 - 8, vy1 - 8), ((vx0 + vx1) // 2, vy0 + 8),
                 ((vx0 + vx1) // 2, vy1 - 8)], r=7)
    # brillo del cristal
    g, dg = capa(W, H)
    dg.polygon([(vx0 + 60, vy1 - 40), (vx0 + 260, vy0 + 30), (vx0 + 330, vy0 + 30),
                (vx0 + 130, vy1 - 40)], fill=(190, 230, 255, 26))
    pegar(img, g, blur=6)
    del g
    # ESCLUSA (izquierda): puerta circular con rueda de válvula
    ax, ay, ar = 250, 400, 175
    d.ellipse([ax - ar - 26, ay - ar - 26, ax + ar + 26, ay + ar + 26], fill=(24, 34, 54))
    d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(16, 24, 40), outline=STEEL_HI, width=10)
    d.ellipse([ax - ar + 26, ay - ar + 26, ax + ar - 26, ay + ar - 26],
              outline=CIAN_LO, width=6)
    # rueda de válvula
    d.ellipse([ax - 62, ay - 62, ax + 62, ay + 62], outline=AMBAR, width=12)
    for a in range(0, 360, 60):
        x2 = ax + math.cos(math.radians(a)) * 58
        y2 = ay + math.sin(math.radians(a)) * 58
        d.line([ax, ay, x2, y2], fill=AMBAR_DARK, width=9)
    d.ellipse([ax - 16, ay - 16, ax + 16, ay + 16], fill=AMBAR)
    remaches(d, [(ax - ar - 18, ay - ar - 18), (ax + ar + 18, ay - ar - 18),
                 (ax - ar - 18, ay + ar + 18), (ax + ar + 18, ay + ar + 18)], r=7)
    # franja de aviso bajo la escotilla
    franja_aviso(d, 60, 640, 470, 690)
    # CONSOLAS bajo el ventanal
    d.rectangle([560, 500, 1450, 640], fill=PANEL)
    d.rectangle([560, 500, 1450, 640], outline=STEEL_LO, width=5)
    pantalla_consola(d, 590, 522, 760, 616, CIAN, 2)
    pantalla_consola(d, 785, 522, 955, 616, VERDE, 5)
    pantalla_consola(d, 980, 522, 1150, 616, AMBAR, 8)
    pantalla_consola(d, 1175, 522, 1345, 616, CIAN, 11)
    for lx in range(1370, 1440, 22):
        d.ellipse([lx, 545, lx + 12, 557], fill=VERDE if lx % 44 else ROJO)
        d.ellipse([lx, 575, lx + 12, 587], fill=CIAN_LO)
    remaches(d, [(575, 510), (1435, 510), (575, 630), (1435, 630)])
    # v2.130b: la señalética pintada se RETIRA — ese hueco lo ocupa el
    # cartel de etapa del módulo (ETAPA X/5), mejor no duplicar textos.
    # tubería superior + cables
    tuberia_h(d, 46, 30, W - 30, r=13)
    for cy in (66, 84):
        pts = [(i * 40, cy + math.sin(i * 0.6) * 6) for i in range(0, 39)]
        d.line(pts, fill=(48, 60, 88), width=4)
    # franja ámbar a media altura (guía visual)
    d.rectangle([0, 686, W, 700], fill=AMBAR_DARK)
    ruido(img, 8)
    vineta(img, 95)
    img.save(f'{OUT}/sala_front.jpg', quality=90)


# =====================================================================
#  PARED TRASERA (detrás del jugador)  1536×718
#  NOTA: rotY=π → u=0 en x +3,05 (espejado respecto a la frontal)
# =====================================================================
def gen_trasera():
    W, H = 1536, 718
    img, d = lienzo(W, H)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(12 + 5 * k), int(19 + 7 * k), int(34 + 10 * k)))
    # CÁPSULAS DE SUEÑO (fila de 3, la central abierta con luz)
    for i, cx in enumerate((300, 730, 1160)):
        cy = 300
        abierto = (i == 1)
        d.rounded_rectangle([cx - 175, cy - 150, cx + 175, cy + 150], radius=60,
                            fill=PANEL, outline=STEEL_HI, width=8)
        d.rounded_rectangle([cx - 145, cy - 118, cx + 145, cy + 118], radius=44,
                            fill=(14, 22, 38))
        if abierto:
            glow_circulo(img, cx, cy, 120, (120, 220, 255), 70, blur=40)
            d.rounded_rectangle([cx - 120, cy - 95, cx + 120, cy + 95], radius=36,
                                fill=(26, 48, 78), outline=CIAN, width=5)
        else:
            d.rounded_rectangle([cx - 120, cy - 95, cx + 120, cy + 95], radius=36,
                                fill=(18, 30, 50), outline=CIAN_LO, width=5)
            d.ellipse([cx - 30, cy - 26, cx + 30, cy + 26], outline=CIAN_DARK, width=6)
        remaches(d, [(cx - 160, cy - 135), (cx + 160, cy - 135),
                     (cx - 160, cy + 135), (cx + 160, cy + 135)], r=6)
        d.rectangle([cx - 60, cy + 158, cx + 60, cy + 172], fill=STEEL_LO)
    # panel de estado de las cápsulas
    pantalla_consola(d, 520, 500, 950, 640, VERDE, 4)
    d.text((735, 560), 'HIBERNACIÓN', font=F(26), fill=(200, 230, 250), anchor='mm')
    d.text((735, 602), 'CÁPSULAS 1–3 · NOMINAL', font=F(18, False),
           fill=(120, 180, 160), anchor='mm')
    # ESTANTERÍA de suministros (derecha en espejo = x −)
    ex0, ey0, ex1, ey1 = 60, 150, 250, 640
    d.rectangle([ex0, ey0, ex1, ey1], fill=(22, 31, 50), outline=STEEL_LO, width=5)
    for sy in range(ey0 + 40, ey1, 120):
        d.line([ex0 + 6, sy, ex1 - 6, sy], fill=STEEL_HI, width=6)
        for bx in range(ex0 + 18, ex1 - 30, 62):
            bw = 44
            d.rectangle([bx, sy - 62, bx + bw, sy - 4], fill=PANEL_2,
                        outline=STEEL_LO, width=3)
            d.line([bx + 8, sy - 33, bx + bw - 8, sy - 33], fill=AMBAR_DARK, width=5)
    # MÁQUINA EXPENDEDORA (izquierda en espejo = x +)
    mx = 1370
    d.rounded_rectangle([mx - 95, 180, mx + 95, 640], radius=18, fill=PANEL,
                        outline=STEEL_HI, width=7)
    d.rectangle([mx - 70, 210, mx + 70, 420], fill=(12, 20, 36), outline=CIAN_DARK, width=4)
    for ry in range(230, 410, 46):
        for rx in (mx - 52, mx + 6):
            col = [VERDE, AMBAR, CIAN, ROJO][(ry // 46 + (1 if rx > mx else 0)) % 4]
            d.rounded_rectangle([rx, ry, rx + 46, ry + 34], radius=8, fill=(24, 36, 58))
            d.ellipse([rx + 14, ry + 8, rx + 30, ry + 24], fill=col)
    d.rectangle([mx - 70, 450, mx + 70, 560], fill=(8, 14, 26), outline=CIAN_LO, width=4)
    d.text((mx, 505), 'RACIONES', font=F(20), fill=CIAN, anchor='mm')
    d.rectangle([mx - 70, 580, mx + 70, 620], fill=(16, 24, 40))
    franja_aviso(d, 300, 668, 1230, 700)
    # tubería superior
    tuberia_h(d, 40, 30, W - 30, r=12)
    ruido(img, 8)
    vineta(img, 95)
    img.save(f'{OUT}/sala_back.jpg', quality=90)


# =====================================================================
#  PARED IZQUIERDA  1536×554 = 7,90 × 2,85 m
#  u=0 en z +2,35 (jugador) … u=1 en z −5,55 (rival)
#  ZONA CALMA del MAPA: u 0,305..0,517 · v 0,365..0,687
#    → px x 469..794 · y 176..353 (v=0 abajo ⇒ y = H·(1−v))
# =====================================================================
def gen_izquierda():
    W, H = 1536, 554
    img, d = lienzo(W, H)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(12 + 5 * k), int(20 + 7 * k), int(35 + 10 * k)))
    # PANELES base (deja la zona del mapa lisa)
    for (x0, x1) in ((20, 440), (440, 820), (820, 1180), (1180, 1516)):
        panel(d, x0, 24, x1, H - 24, fill=PANEL if (x0 // 380) % 2 == 0 else PANEL_2)
    remaches(d, [(x, 40) for x in range(50, 1500, 120)] +
                 [(x, H - 40) for x in range(50, 1500, 120)])
    # marco remachado RESERVADO para el mapa del campeonato
    mx0, my0, mx1, my1 = 455, 168, 808, 362
    d.rectangle([mx0 - 14, my0 - 14, mx1 + 14, my1 + 14], fill=(22, 32, 52))
    d.rectangle([mx0 - 14, my0 - 14, mx1 + 14, my1 + 14], outline=STEEL_HI, width=7)
    remaches(d, [(mx0 - 6, my0 - 6), (mx1 + 6, my0 - 6),
                 (mx0 - 6, my1 + 6), (mx1 + 6, my1 + 6)], r=6)
    d.rectangle([mx0, my0, mx1, my1], fill=(10, 16, 28), outline=CIAN_DARK, width=4)
    d.text(((mx0 + mx1) // 2, my1 + 34), 'RUTA DE MISIÓN', font=F(20),
           fill=CIAN_LO, anchor='mm')
    # VENTANAL al espacio (hacia el lado del rival, u alto)
    vx0, vy0, vx1, vy1 = 1010, 80, 1500, 380
    space = Image.new('RGB', (vx1 - vx0, vy1 - vy0), ESPACIO)
    sd = ImageDraw.Draw(space)
    campo_estrellas(space, sd, n=150, semilla=11)
    nebulosa(space, 300, 160, 260, 130, semilla=12)
    planeta_anillado(space, 340, 200, 88)
    img.paste(space, (vx0 + 8, vy0 + 8))
    d.rectangle([vx0, vy0, vx1, vy1], outline=STEEL_HI, width=12)
    d.rectangle([(vx0 + vx1) // 2 - 9, vy0, (vx0 + vx1) // 2 + 9, vy1], fill=(30, 40, 62))
    remaches(d, [(vx0 + 6, vy0 + 6), (vx1 - 6, vy0 + 6), (vx0 + 6, vy1 - 6),
                 (vx1 - 6, vy1 - 6)], r=6)
    # CINTURÓN DE HERRAMIENTAS + extintor (bajo el ventanal)
    d.rectangle([1010, 430, 1500, 520], fill=PANEL_2, outline=STEEL_LO, width=4)
    for hx in range(1040, 1480, 90):
        d.rectangle([hx, 448, hx + 56, 504], fill=(24, 36, 58), outline=STEEL_LO, width=3)
        d.line([hx + 10, 476, hx + 46, 476], fill=AMBAR_DARK, width=6)
    # extintor
    ex = 940
    d.rounded_rectangle([ex - 26, 380, ex + 26, 500], radius=18, fill=ROJO)
    d.rectangle([ex - 8, 360, ex + 8, 384], fill=STEEL_LO)
    d.ellipse([ex - 14, 348, ex + 14, 366], outline=STEEL_HI, width=5)
    franja_aviso(d, 40, 500, 380, 540)
    # tubería superior
    tuberia_h(d, 34, 24, W - 24, r=10)
    ruido(img, 7)
    vineta(img, 85)
    img.save(f'{OUT}/sala_left.jpg', quality=90)


# =====================================================================
#  PARED DERECHA  1536×554   (u=0 en z −5,55 … u=1 en z +2,35)
# =====================================================================
def gen_derecha():
    W, H = 1536, 554
    img, d = lienzo(W, H)
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(12 + 5 * k), int(20 + 7 * k), int(35 + 10 * k)))
    for (x0, x1) in ((20, 420), (420, 830), (830, 1180), (1180, 1516)):
        panel(d, x0, 24, x1, H - 24, fill=PANEL if (x0 // 390) % 2 else PANEL_2)
    remaches(d, [(x, 40) for x in range(50, 1500, 120)] +
                 [(x, H - 40) for x in range(50, 1500, 120)])
    # BRAZO ROBÓTICO montado en el carril superior
    bx, by = 300, 120
    d.rectangle([60, 150, 760, 176], fill=(24, 34, 54), outline=STEEL_LO, width=4)
    d.line([bx, by, bx + 170, by - 60], fill=STEEL, width=22)
    d.line([bx + 170, by - 60, bx + 330, by + 10], fill=STEEL, width=16)
    d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=STEEL_HI, outline=STEEL_LO, width=4)
    d.ellipse([bx + 158, by - 72, bx + 182, by - 48], fill=AMBAR)
    d.ellipse([bx + 322, by - 2, bx + 346, by + 22], fill=AMBAR)
    # pinza
    d.polygon([(bx + 330, by + 10), (bx + 366, by - 6), (bx + 360, by + 16)], fill=STEEL_HI)
    d.polygon([(bx + 330, by + 10), (bx + 362, by + 34), (bx + 340, by + 38)], fill=STEEL_HI)
    glow_circulo(img, bx + 170, by - 60, 26, AMBAR, 60, blur=14)
    # CONSOLA DE CONTROL grande (centro)
    d.rounded_rectangle([880, 120, 1380, 470], radius=20, fill=PANEL,
                        outline=STEEL_HI, width=8)
    pantalla_consola(d, 905, 145, 1355, 300, CIAN, 6)
    for i, lx in enumerate(range(920, 1340, 70)):
        col = [VERDE, CIAN, AMBAR, ROJO][i % 4]
        d.ellipse([lx, 330, lx + 22, 352], fill=col if i % 3 else (40, 60, 90))
        d.ellipse([lx, 372, lx + 22, 394], fill=CIAN_DARK if i % 2 else CIAN_LO)
    d.rectangle([905, 415, 1355, 445], fill=(14, 22, 38), outline=STEEL_LO, width=3)
    for kx in range(915, 1345, 34):
        d.rectangle([kx, 420, kx + 22, 440], fill=PANEL_2)
    remaches(d, [(895, 135), (1365, 135), (895, 455), (1365, 455)], r=6)
    # PERCHERO con cascos de traje (izquierda baja)
    for hx in (120, 210):
        d.line([hx, 250, hx, 430], fill=STEEL_LO, width=10)
        d.ellipse([hx - 34, 250, hx + 34, 318], fill=(168, 178, 196),
                  outline=STEEL_LO, width=5)
        d.rectangle([hx - 22, 300, hx + 22, 318], fill=(120, 132, 156))
        d.ellipse([hx - 16, 268, hx - 4, 284], fill=(30, 200, 255))
        d.ellipse([hx + 4, 268, hx + 16, 284], fill=(30, 200, 255))
    # CAJAS apiladas
    for (bx0, by0) in ((430, 430), (510, 430), (470, 350)):
        d.rectangle([bx0, by0, bx0 + 72, by0 + 84], fill=PANEL_2, outline=STEEL_LO, width=4)
        d.line([bx0 + 10, by0 + 42, bx0 + 62, by0 + 42], fill=AMBAR_DARK, width=7)
    franja_aviso(d, 900, 500, 1500, 538)
    tuberia_h(d, 34, 24, W - 24, r=10)
    ruido(img, 7)
    vineta(img, 85)
    img.save(f'{OUT}/sala_right.jpg', quality=90)


# =====================================================================
#  MAPA DEL CAMPEONATO (1380×752, convenio WizardMap) + TAPA (290×300)
#  Nodos (px del arte) — DEVEMOS usar EXACTAMENTE éstos en el módulo:
#    0 DUELO 1      (215, 300) r 112
#    1 CINTURÓN     (452, 520) r 134
#    2 DUELO 2      (700, 268) r 112
#    3 TORMENTA     (948, 520) r 134
#    4 DUELO FINAL  (1196, 268) r 112
#  + trofeo/insignia en (1330, 470)
# =====================================================================
NODES = [(210, 260, 100), (455, 500, 120), (700, 260, 100),
         (945, 500, 120), (1190, 260, 100)]
TROFEO = (1278, 472)


def gen_mapa():
    W, H = 1380, 752
    img = Image.new('RGB', (W, H), (10, 16, 30))
    d = ImageDraw.Draw(img)
    # fondo espacial
    for y in range(H):
        k = y / H
        d.line([0, y, W, y], fill=(int(10 + 6 * k), int(16 + 8 * k), int(30 + 12 * k)))
    sd = ImageDraw.Draw(img)
    campo_estrellas(img, sd, n=120, semilla=21)
    nebulosa(img, 690, 400, 430, 190, semilla=6)
    # marco de acero
    d.rectangle([10, 10, W - 10, H - 10], outline=STEEL, width=12)
    d.rectangle([26, 26, W - 26, H - 26], outline=CIAN_DARK, width=4)
    remaches(d, [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30),
                 (W // 2, 30), (W // 2, H - 30)], r=7)
    # banda de título
    d.rounded_rectangle([40, 42, W - 40, 130], radius=22, fill=(18, 50, 74))
    d.rounded_rectangle([40, 42, W - 40, 130], radius=22, outline=CIAN, width=5)
    d.text((W // 2, 74), 'ESTACIÓN ORBITAL', font=F(40), fill=(127, 232, 255),
           anchor='mm')
    d.text((W // 2, 110), 'CAMINO DEL CAMPEÓN · 5 ETAPAS', font=F(20, False),
           fill=BLANCO, anchor='mm')

    # ruta punteada con curvas suaves (detrás de los nodos)
    path = [NODES[0][:2], NODES[1][:2], NODES[2][:2], NODES[3][:2], NODES[4][:2],
            TROFEO]
    for a, b in zip(path, path[1:]):
        ax, ay = a
        bx, by = b
        cxx, cyy = (ax + bx) / 2, min(ay, by) - 46
        pts = []
        for i in range(0, 41):
            t = i / 40
            x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * cxx + t ** 2 * bx
            y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * cyy + t ** 2 * by
            pts.append((x, y))
        for i in range(0, len(pts) - 3, 4):
            d.line([pts[i], pts[i + 2]], fill=AMBAR_DARK, width=9)
            d.line([pts[i], pts[i + 2]], fill=(255, 214, 120), width=4)

    # nodos
    labels = ['DUELO 1', 'CINTURÓN', 'DUELO 2', 'TORMENTA', 'DUELO FINAL']
    subs = ['AX-9 · Nv.1', 'PRUEBA · 10 DIANAS', 'AX-9 · Nv.2',
            'PRUEBA · 14 DIANAS', 'JEFE · x1.42']
    for i, (nx, ny, nr) in enumerate(NODES):
        prueba = (i % 2 == 1)
        d.ellipse([nx - nr - 12, ny - nr - 12, nx + nr + 12, ny + nr + 12],
                  fill=(18, 50, 74), outline=CIAN, width=6)
        if prueba:
            # asteroide con cráteres + retícula de diana
            d.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(58, 50, 44),
                      outline=(122, 102, 82), width=7)
            rs = random.Random(i * 17)
            for k in range(10):
                ang = rs.uniform(0, math.tau)
                rr = rs.uniform(0, 0.62)
                ex = nx + math.cos(ang) * nr * rr
                ey = ny + math.sin(ang) * nr * rr
                er = rs.uniform(7, 16) * (1 - rr * 0.4)
                d.ellipse([ex - er, ey - er, ex + er, ey + er],
                          fill=(74, 63, 54), outline=(40, 34, 29), width=3)
            # retícula cian
            for rr in (0.42, 0.72):
                d.ellipse([nx - nr * rr, ny - nr * rr, nx + nr * rr, ny + nr * rr],
                          outline=CIAN, width=5)
            d.line([nx - nr * 0.86, ny, nx - nr * 0.30, ny], fill=CIAN, width=5)
            d.line([nx + nr * 0.30, ny, nx + nr * 0.86, ny], fill=CIAN, width=5)
            d.line([nx, ny - nr * 0.86, nx, ny - nr * 0.30], fill=CIAN, width=5)
            d.line([nx, ny + nr * 0.30, nx, ny + nr * 0.86], fill=CIAN, width=5)
        else:
            # cara del AX-9: cabeza con visor, ojos cian y antena
            hw, hh = nr * 0.58, nr * 0.46
            hy = ny - nr * 0.06
            # antena
            d.line([nx, hy - hh, nx, hy - hh - 26], fill=STEEL_HI, width=7)
            d.ellipse([nx - 9, hy - hh - 42, nx + 9, hy - hh - 24], fill=ROJO,
                      outline=(20, 26, 40), width=3)
            d.rounded_rectangle([nx - hw, hy - hh, nx + hw, hy + hh], radius=26,
                                fill=(206, 214, 228), outline=(20, 26, 40), width=7)
            # visor
            d.rounded_rectangle([nx - hw + 14, hy - hh * 0.52, nx + hw - 14,
                                 hy + hh * 0.28], radius=20, fill=(12, 18, 32),
                                outline=STEEL_LO, width=4)
            ey = hy - hh * 0.12
            for ex in (nx - hw * 0.42, nx + hw * 0.42):
                d.ellipse([ex - 13, ey - 9, ex + 13, ey + 9], fill=CIAN)
            # boca: rejilla
            my0 = hy + hh * 0.5
            d.rectangle([nx - 34, my0, nx + 34, my0 + 12], fill=(60, 70, 90),
                        outline=(20, 26, 40), width=3)
            for gx in range(nx - 26, nx + 30, 13):
                d.line([gx, my0 + 2, gx, my0 + 10], fill=(20, 26, 40), width=3)
            # cuello
            d.rectangle([nx - 24, hy + hh, nx + 24, hy + hh + 14], fill=STEEL_LO)
        # insignia de número (esquina sup-izq del nodo)
        bx, by = nx - nr * 0.82, ny - nr * 0.82
        d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=AMBAR,
                  outline=(40, 26, 6), width=4)
        d.text((bx, by - 2), str(i + 1), font=F(28), fill=(50, 32, 4), anchor='mm')
        d.text((nx, ny + nr + 34), labels[i], font=F(27), fill=BLANCO, anchor='mm')
        d.text((nx, ny + nr + 64), subs[i], font=F(19, False), fill=CIAN_LO,
               anchor='mm')

    # trofeo final: insignia CONSEGUIDO
    tx0, ty0 = TROFEO
    d.ellipse([tx0 - 66, ty0 - 66, tx0 + 66, ty0 + 66], fill=(44, 36, 14),
              outline=AMBAR, width=8)
    d.ellipse([tx0 - 42, ty0 - 42, tx0 + 42, ty0 + 42], fill=AMBAR)
    d.polygon([(tx0 - 14, ty0 - 22), (tx0 + 18, ty0 - 22), (tx0 + 8, ty0 + 6),
               (tx0 + 18, ty0 + 6), (tx0, ty0 + 30), (tx0 - 18, ty0 + 6),
               (tx0 - 8, ty0 + 6)], fill=(122, 84, 10))
    d.text((tx0, ty0 + 86), '¡CONSEGUIDO!', font=F(22), fill=AMBAR, anchor='mm')
    img.save(f'{OUT}/mapa.png')


def gen_tapa():
    W = H = 300
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, W - 10, H - 10], fill=(30, 42, 66, 255),
              outline=STEEL_HI + (255,), width=10)
    d.ellipse([36, 36, W - 36, H - 36], fill=(18, 28, 46, 255),
              outline=CIAN_DARK + (255,), width=5)
    remaches(d, [(150, 34), (150, 266), (34, 150), (266, 150)], r=7)
    d.text((150, 150), '?', fill=CIAN + (255,), anchor='mm')
    img.save(f'{OUT}/tapa.png')


# =====================================================================
#  TROQUELES V2 (512×640, RGBA): cohete / rover / satélite con sombreado
# =====================================================================
def outline_shape(d, pts, fill, width=6, col=(20, 26, 40)):
    d.polygon(pts, fill=fill, outline=col, width=width)


def gen_troqueles():
    # ---- cohete (troquel1, h 1,2 m) ----
    W, H = 512, 640
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # aletas
    outline_shape(d, [(150, 420), (86, 580), (176, 560)], ROJO)
    outline_shape(d, [(362, 420), (426, 580), (336, 560)], ROJO)
    # cuerpo con gradiente por bandas
    for i in range(240):
        t = i / 240
        col = (int(210 - 60 * t), int(216 - 60 * t), int(228 - 50 * t))
        d.line([166 + int(4 * t), 150 + i, 346 - int(4 * t), 150 + i], fill=col)
    d.polygon([(166, 390), (346, 390), (346, 150), (166, 150)], fill=None)
    # morro
    d.polygon([(166, 152), (346, 152), (256, 34)], fill=(226, 96, 84),
              outline=(20, 26, 40))
    # ventana
    d.ellipse([206, 210, 306, 310], fill=(14, 30, 52), outline=(20, 26, 40), width=8)
    d.ellipse([224, 228, 282, 286], fill=(90, 180, 240))
    d.ellipse([234, 238, 262, 262], fill=(200, 240, 255))
    # franjas
    d.rectangle([166, 360, 346, 396], fill=ROJO, outline=(20, 26, 40))
    d.rectangle([166, 120, 346, 152], fill=ROJO, outline=(20, 26, 40))
    # llama
    d.polygon([(216, 585), (296, 585), (256, 634)], fill=AMBAR)
    d.polygon([(232, 585), (280, 585), (256, 616)], fill=(255, 236, 150))
    d.line([166, 390, 346, 390], fill=(20, 26, 40), width=6)
    img.save(f'{OUT}/decor/troquel1.png')

    # ---- rover (troquel2, h 0,8 m) ----
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    outline_shape(d, [(120, 300), (392, 300), (420, 420), (92, 420)], (200, 206, 220))
    outline_shape(d, [(180, 230), (332, 230), (352, 302), (160, 302)], (214, 220, 232))
    d.rectangle([196, 250, 316, 286], fill=(30, 52, 84), outline=(20, 26, 40), width=5)
    d.ellipse([246, 190, 286, 230], fill=(120, 130, 150), outline=(20, 26, 40), width=4)
    d.line([266, 190, 266, 150], fill=(20, 26, 40), width=6)
    d.ellipse([258, 138, 274, 154], fill=ROJO, outline=(20, 26, 40), width=3)
    # ruedas con llanta
    for wx in (140, 256, 372):
        d.ellipse([wx - 52, 390, wx + 52, 494], fill=(52, 56, 66),
                  outline=(20, 26, 40), width=8)
        d.ellipse([wx - 24, 418, wx + 24, 466], fill=(120, 126, 140),
                  outline=(20, 26, 40), width=5)
    # panel solar
    d.rectangle([96, 312, 200, 352], fill=(40, 80, 170), outline=(20, 26, 40), width=5)
    for gx in range(112, 196, 22):
        d.line([gx, 312, gx, 352], fill=(24, 50, 110), width=4)
    d.rectangle([312, 312, 416, 352], fill=(40, 80, 170), outline=(20, 26, 40), width=5)
    for gx in range(328, 412, 22):
        d.line([gx, 312, gx, 352], fill=(24, 50, 110), width=4)
    img.save(f'{OUT}/decor/troquel2.png')

    # ---- satélite (troquel3, h 1,0 m) ----
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # paneles solares
    for px in (28, 356):
        d.rectangle([px, 270, px + 128, 370], fill=(40, 80, 170),
                    outline=(20, 26, 40), width=7)
        for gx in range(px + 16, px + 128, 24):
            d.line([gx, 270, gx, 370], fill=(24, 50, 110), width=5)
    d.line([156, 320, 196, 320], fill=(20, 26, 40), width=8)
    d.line([316, 320, 356, 320], fill=(20, 26, 40), width=8)
    # cuerpo
    outline_shape(d, [(196, 220), (316, 220), (316, 420), (196, 420)], (206, 212, 226))
    d.rectangle([196, 268, 316, 300], fill=ROJO, outline=(20, 26, 40), width=4)
    d.ellipse([228, 330, 284, 386], fill=(14, 30, 52), outline=(20, 26, 40), width=6)
    d.ellipse([240, 342, 272, 374], fill=(90, 200, 240))
    # antena parabólica arriba
    d.polygon([(256, 220), (216, 150), (296, 150)], fill=(214, 220, 232),
              outline=(20, 26, 40))
    d.ellipse([236, 120, 276, 160], fill=(180, 188, 204), outline=(20, 26, 40), width=5)
    d.line([256, 96, 256, 122], fill=(20, 26, 40), width=6)
    d.ellipse([250, 82, 262, 94], fill=CIAN, outline=(20, 26, 40), width=3)
    # antena inferior
    d.line([256, 420, 256, 470], fill=(20, 26, 40), width=6)
    d.ellipse([244, 470, 268, 494], fill=AMBAR, outline=(20, 26, 40), width=4)
    img.save(f'{OUT}/decor/troquel3.png')


if __name__ == '__main__':
    gen_suelo()
    gen_techo()
    gen_frontal()
    gen_trasera()
    gen_izquierda()
    gen_derecha()
    gen_mapa()
    gen_tapa()
    gen_troqueles()
    # validación
    from PIL import Image as I
    esperado = {
        'sala_floor.jpg': (1024, 1328), 'sala_ceil.jpg': (1024, 1328),
        'sala_front.jpg': (1536, 718), 'sala_back.jpg': (1536, 718),
        'sala_left.jpg': (1536, 554), 'sala_right.jpg': (1536, 554),
        'mapa.png': (1380, 752), 'tapa.png': (300, 300),
        'decor/troquel1.png': (512, 640), 'decor/troquel2.png': (512, 640),
        'decor/troquel3.png': (512, 640),
    }
    ok = True
    for f, (w, h) in esperado.items():
        p = os.path.join(OUT, f)
        try:
            im = I.open(p)
            good = im.size == (w, h)
            print(f"{'OK ' if good else 'MAL'} {f} {im.size} (esperado {(w, h)})")
            ok = ok and good
        except Exception as e:
            print(f"FALTA {f}: {e}")
            ok = False
    print('VALIDACION', 'OK' if ok else 'CON ERRORES')

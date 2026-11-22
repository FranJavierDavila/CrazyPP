#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTACIÓN ORBITAL — ARTE DE LA SALA (6 paredes, 1024×1024 JPG)
Estilo cartoon espacial coherente con el juego:
  · estructura de acero azul profundo + paneles remachados
  · luces cian (#4fd8ff) + franjas de aviso ámbar
  · ventanal al espacio con planeta anillado
Medidas reales de los planos (nota v2.85 de magia):
  · suelo/techo 6,10 × 7,90 m  · trasera/frontal 6,10 × 2,85 m
  · laterales 7,90 × 2,85 m
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

OUT = '/home/z/my-project/public/championships/estacion_orbital/assets'
os.makedirs(OUT, exist_ok=True)
S = 1024
random.seed(47)

# ---------------------------------------------------------------- paleta
ESPACIO = (8, 11, 22)
AZUL_HONDO = (13, 21, 36)
PANEL = (30, 42, 66)
PANEL_2 = (38, 52, 80)
PANEL_HI = (52, 70, 104)
STEEL = (74, 92, 122)
STEEL_LO = (44, 58, 86)
CIAN = (79, 216, 255)
CIAN_LO = (38, 120, 155)
CIAN_DARK = (16, 52, 74)
AMBAR = (255, 179, 71)
AMBAR_DARK = (170, 106, 30)
BLANCO = (232, 238, 250)
ROJO = (255, 96, 88)
VERDE = (105, 240, 174)
PLANETA = (72, 140, 208)
PLANETA_LO = (40, 88, 148)


def base_panel(d, x0, y0, x1, y1, fill=PANEL, edge=PANEL_HI):
    """Panel metálico con bisel: relleno + cara superior clara + sombra baja."""
    d.rectangle([x0, y0, x1, y1], fill=fill)
    d.line([x0, y0, x1, y0], fill=edge, width=3)
    d.line([x0, y0, x0, y1], fill=edge, width=3)
    d.line([x0, y1, x1, y1], fill=STEEL_LO, width=4)
    d.line([x1, y0, x1, y1], fill=STEEL_LO, width=4)


def rivets(d, pts, r=5, col=STEEL, hi=(140, 160, 190)):
    for (x, y) in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        d.ellipse([x - r + 1, y - r + 1, x + r - 1, y - 1], fill=hi)


def estrella(d, x, y, r, col, hi=None):
    if hi:
        d.ellipse([x - r * 2.2, y - r * 2.2, x + r * 2.2, y + r * 2.2],
                  fill=(col[0], col[1], col[2], 60))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def campo_estrellas(d, box, n=170, seed=1):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for i in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        r = rnd.choice([1, 1, 1, 2, 2, 3])
        b = rnd.randint(120, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(b, b, min(255, b + 12)))


def franja_aviso(d, x0, y, x1, h=26, paso=46):
    """Franja diagonal de aviso ámbar/negro."""
    d.rectangle([x0, y, x1, y + h], fill=(16, 16, 20))
    x = x0 - paso
    while x < x1 + paso:
        d.polygon([(x, y + h), (x + paso / 2, y), (x + paso, y),
                   (x + paso / 2, y + h)], fill=AMBAR)
        x += paso
    d.line([x0, y, x1, y], fill=AMBAR_DARK, width=2)
    d.line([x0, y + h, x1, y + h], fill=AMBAR_DARK, width=2)


def pantalla(d, x0, y0, x1, y1, seed=2, tono=CIAN):
    """Consola: marco + gráficas y barras luminosas."""
    base_panel(d, x0, y0, x1, y1, fill=(10, 16, 26), edge=STEEL)
    m = 10
    d.rectangle([x0 + m, y0 + m, x1 - m, y1 - m], fill=CIAN_DARK)
    rnd = random.Random(seed)
    # gráfica de línea
    pts = []
    n = 9
    for i in range(n + 1):
        px = x0 + m + 8 + (x1 - x0 - 2 * m - 16) * i / n
        py = y0 + m + 14 + (y1 - y0) * 0.34 * rnd.random()
        pts.append((px, py))
    d.line(pts, fill=tono, width=5)
    # barras
    bx = x0 + m + 10
    while bx < x1 - m - 22:
        bh = (y1 - y0) * 0.30 * rnd.random() + 8
        col = VERDE if rnd.random() < 0.25 else tono
        d.rectangle([bx, y1 - m - 10 - bh, bx + 12, y1 - m - 10], fill=col)
        bx += 22
    # línea de barrido
    d.line([x0 + m, y1 - m - 10, x1 - m, y1 - m - 10], fill=STEEL_LO, width=2)


def tuberia_h(d, y, x0, x1, w=18):
    d.rectangle([x0, y - w // 2, x1, y + w // 2], fill=STEEL)
    d.line([x0, y - w // 2, x1, y - w // 2], fill=(120, 140, 170), width=4)
    for x in range(x0 + 30, x1 - 20, 150):
        d.rectangle([x, y - w // 2 - 5, x + 14, y + w // 2 + 5], fill=STEEL_LO)
        d.rectangle([x + 3, y - w // 2 - 2, x + 11, y + w // 2 + 2],
                    fill=(100, 118, 148))


def luz_empotrada(d, cx, cy, w, h, col=CIAN):
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=min(w, h) / 3, fill=col)
    d.rounded_rectangle([cx - w / 2 + 4, cy - h / 2 + 4, cx + w / 2 - 4,
                         cy + h / 2 - 4], radius=max(2, min(w, h) / 4),
                        fill=(min(255, col[0] + 60), min(255, col[1] + 30),
                              min(255, col[2] + 40)))


# ================================================================ SUELO
def suelo():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    # losas grandes en perspectiva suave (bandas horizontales)
    paso = 128
    for j, y in enumerate(range(0, S, paso)):
        base_panel(d, 0, y, S, min(S, y + paso - 4),
                   fill=PANEL if j % 2 == 0 else PANEL_2, edge=PANEL_HI)
        rivets(d, [(x, y + 14) for x in range(26, S, 96)])
        rivets(d, [(x, min(S - 12, y + paso - 18)) for x in range(26, S, 96)])
    # junta central + tiras de luz corriendo en profundidad
    d.rectangle([0, S // 2 - 8, S, S // 2 + 8], fill=STEEL_LO)
    for yy in (S // 2 - 84, S // 2 + 76):
        d.rectangle([0, yy - 6, S, yy + 6], fill=CIAN_DARK)
        d.rectangle([0, yy - 3, S, yy + 3], fill=CIAN)
    # círculo holográfico central (bajo la mesa)
    for rr, col in ((230, CIAN_DARK), (188, (24, 84, 112)), (150, CIAN_LO)):
        d.ellipse([S / 2 - rr, S / 2 - rr * 0.62, S / 2 + rr, S / 2 + rr * 0.62],
                  outline=col, width=8)
    d.ellipse([S / 2 - 96, S / 2 - 60, S / 2 + 96, S / 2 + 60],
              outline=CIAN, width=6)
    # marcas de aviso en las esquinas
    franja_aviso(d, 0, 24, 210, h=20, paso=38)
    franja_aviso(d, S - 210, 24, S, h=20, paso=38)
    im.save(OUT + '/sala_floor.jpg', quality=90)


# ================================================================ TECHO
def techo():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    # panelado central + vigas
    for j, y in enumerate(range(0, S, 170)):
        base_panel(d, 0, y, S, min(S, y + 162), fill=PANEL, edge=PANEL_HI)
    tuberia_h(d, 60, 0, S, w=22)
    tuberia_h(d, S - 70, 0, S, w=26)
    # Pozo de luz central: anillo de LEDs
    d.ellipse([S / 2 - 300, S / 2 - 190, S / 2 + 300, S / 2 + 190],
              fill=STEEL_LO)
    d.ellipse([S / 2 - 250, S / 2 - 158, S / 2 + 250, S / 2 + 158],
              fill=CIAN_DARK)
    d.ellipse([S / 2 - 200, S / 2 - 126, S / 2 + 200, S / 2 + 126],
              fill=(28, 96, 128))
    n = 16
    for i in range(n):
        a = 2 * math.pi * i / n
        x = S / 2 + 224 * math.cos(a)
        y = S / 2 + 142 * math.sin(a)
        luz_empotrada(d, x, y, 34, 22, CIAN)
    # rejillas de ventilación
    for cx in (150, S - 150):
        base_panel(d, cx - 90, S - 250, cx + 90, S - 90, fill=PANEL_2)
        for k in range(6):
            d.rectangle([cx - 70, S - 234 + k * 22, cx + 70,
                         S - 224 + k * 22], fill=(18, 26, 42))
    im.save(OUT + '/sala_ceil.jpg', quality=90)


# ================================================================ VENTANA AL ESPACIO
def _capa_ventana(rx, ry, seed, planeta):
    """Contenido del ventanal en capa RGBA recortada a la elipse."""
    lay = Image.new('RGBA', (2 * rx, 2 * ry), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse([0, 0, 2 * rx, 2 * ry], fill=ESPACIO + (255,))
    campo_estrellas(ld, (0, 0, 2 * rx, 2 * ry), n=130, seed=seed)
    if planeta:
        px, py, pr = rx * 1.30, ry * 1.16, rx * 0.52
        ld.ellipse([px - pr, py - pr, px + pr, py + pr], fill=PLANETA)
        ld.ellipse([px - pr, py - pr, px + pr * 0.2, py + pr * 0.2],
                   fill=(min(255, PLANETA[0] + 44), min(255, PLANETA[1] + 46),
                         min(255, PLANETA[2] + 40), 255))
        for rr, wdt in ((pr * 1.55, 12), (pr * 1.85, 7)):
            ld.arc([px - rr, py - rr * 0.30, px + rr, py + rr * 0.30],
                   190, 350, fill=(216, 196, 160, 255), width=wdt)
        ld.ellipse([px - pr * 1.9, py + pr * 0.55, px - pr * 1.55,
                    py + pr * 0.9], fill=(180, 184, 196, 255))
    # máscara elíptica: TODO lo que salga del óvalo se recorta
    m = Image.new('L', (2 * rx, 2 * ry), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * rx, 2 * ry], fill=255)
    lay.putalpha(m)
    return lay


def ventanal(d, cx, cy, rx, ry, seed=7, planeta=True):
    """Gran ventana circular con marco remachado y vista al espacio."""
    d.ellipse([cx - rx - 26, cy - ry - 26, cx + rx + 26, cy + ry + 26],
              fill=STEEL_LO)
    # espacio + planeta en capa propia (recorte limpio al óvalo)
    lay = _capa_ventana(int(rx), int(ry), seed, planeta)
    im_d = d._image
    im_d.paste(lay, (int(cx - rx), int(cy - ry)), lay)
    # cruces del marco (estilo esclusa)
    wdt = 22
    d.rectangle([cx - wdt / 2, cy - ry, cx + wdt / 2, cy + ry], fill=STEEL)
    d.rectangle([cx - rx, cy - wdt / 2, cx + rx, cy + wdt / 2], fill=STEEL)
    d.line([cx - wdt / 2, cy - ry, cx - wdt / 2, cy + ry],
           fill=(120, 140, 170), width=4)
    d.line([cx - rx, cy - wdt / 2, cx + rx, cy - wdt / 2],
           fill=(120, 140, 170), width=4)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=STEEL, width=10)
    # remaches del marco
    riv = []
    n = 14
    for i in range(n):
        a = 2 * math.pi * i / n
        riv.append((cx + (rx + 13) * math.cos(a),
                    cy + (ry + 13) * math.sin(a)))
    rivets(d, riv, r=6)
    # reflejo cristal
    d.arc([cx - rx + 40, cy - ry + 30, cx + rx - 30, cy + ry - 60],
          200, 250, fill=(150, 210, 255), width=14)


# ================================================================ PARED TRASERA
def back():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    base_panel(d, 0, 0, S, S, fill=PANEL, edge=PANEL_HI)
    # ventanales: 3 en fila (el rival queda delante del central)
    ventanal(d, S // 2, 330, 250, 210, seed=7, planeta=True)
    ventanal(d, 190, 300, 140, 150, seed=11, planeta=False)
    ventanal(d, S - 190, 300, 140, 150, seed=13, planeta=False)
    # consolas bajo los ventanales
    pantalla(d, 60, 560, 350, 760, seed=21)
    pantalla(d, S - 350, 560, S - 60, 760, seed=22)
    base_panel(d, 380, 590, S - 380, 780, fill=PANEL_2)
    # teclado central
    for k in range(8):
        luz_empotrada(d, 420 + k * 26, 700, 18, 18,
                      CIAN if k % 3 else VERDE)
    d.rounded_rectangle([398, 620, 626, 668], radius=8, fill=CIAN_DARK)
    d.rounded_rectangle([404, 626, 620, 662], radius=6,
                        fill=(20, 100, 130))
    # franja de aviso y tuberías
    franja_aviso(d, 0, 830, S, h=30)
    tuberia_h(d, 900, 0, S, w=20)
    d.rectangle([0, 960, S, S], fill=STEEL_LO)
    im.save(OUT + '/sala_back.jpg', quality=90)


# ================================================================ PARED FRONTAL (jugador)
def front():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    base_panel(d, 0, 0, S, S, fill=PANEL, edge=PANEL_HI)
    # ESCLUSA central: puerta redonda con marco + franjas de aviso
    cx, cy, R = S // 2, 420, 250
    d.ellipse([cx - R - 34, cy - R - 34, cx + R + 34, cy + R + 34],
              fill=STEEL_LO)
    riv = [(cx + (R + 17) * math.cos(2 * math.pi * i / 16),
            cy + (R + 17) * math.sin(2 * math.pi * i / 16))
           for i in range(16)]
    rivets(d, riv, r=7)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=PANEL_2,
              outline=STEEL, width=10)
    d.ellipse([cx - R + 46, cy - R + 46, cx + R - 46, cy + R - 46],
              fill=PANEL, outline=STEEL_LO, width=6)
    # rueda de válvula
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=AMBAR, width=16)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=AMBAR)
    for i in range(3):
        a = 2 * math.pi * i / 3
        d.line([cx + 20 * math.cos(a), cy + 20 * math.sin(a),
                cx + 56 * math.cos(a), cy + 56 * math.sin(a)],
               fill=AMBAR, width=14)
    # paneles laterales con pantallas y racks
    pantalla(d, 40, 140, 300, 430, seed=31)
    pantalla(d, S - 300, 140, S - 40, 430, seed=32)
    # racks de contenedores
    for x0 in (60, S - 260):
        for j in range(3):
            base_panel(d, x0, 500 + j * 110, x0 + 200, 590 + j * 110,
                       fill=PANEL_2)
            luz_empotrada(d, x0 + 100, 545 + j * 110, 60, 14,
                          VERDE if j == 1 else CIAN_LO)
    franja_aviso(d, 0, 860, S, h=30)
    tuberia_h(d, 940, 0, S, w=22)
    im.save(OUT + '/sala_front.jpg', quality=90)


# ================================================================ PARED IZQUIERDA
def left():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    base_panel(d, 0, 0, S, S, fill=PANEL, edge=PANEL_HI)
    # bahía de cápsulas de sueño (3 cápsulas verticales)
    for k in range(3):
        cx = 170 + k * 240
        base_panel(d, cx - 92, 120, cx + 92, 700, fill=PANEL_2)
        # cristal de la cápsula
        d.rounded_rectangle([cx - 66, 160, cx + 66, 640], radius=52,
                            fill=CIAN_DARK, outline=STEEL, width=8)
        d.rounded_rectangle([cx - 52, 180, cx + 52, 620], radius=44,
                            fill=(20, 90, 120))
        # silueta del ocupante (bulto suave)
        d.ellipse([cx - 40, 260, cx + 40, 420], fill=(30, 110, 140))
        d.rectangle([cx - 30, 400, cx + 30, 560], fill=(30, 110, 140))
        luz_empotrada(d, cx, 740, 90, 18, CIAN)
    pantalla(d, 500, 780, 850, 950, seed=41)
    franja_aviso(d, 0, 20, S, h=26)
    im.save(OUT + '/sala_left.jpg', quality=90)


# ================================================================ PARED DERECHA
def right():
    im = Image.new('RGB', (S, S), AZUL_HONDO)
    d = ImageDraw.Draw(im)
    base_panel(d, 0, 0, S, S, fill=PANEL, edge=PANEL_HI)
    # gran ventanal oblicuo al espacio
    ventanal(d, 560, 340, 300, 220, seed=17, planeta=True)
    # brazo robótico de mantenimiento a la izquierda
    base_panel(d, 60, 240, 200, 560, fill=PANEL_2)
    d.line([130, 540, 130, 380], fill=STEEL, width=26)
    d.line([130, 380, 210, 300], fill=STEEL, width=22)
    d.ellipse([112, 520, 148, 556], fill=STEEL_LO)
    d.ellipse([192, 282, 228, 318], fill=AMBAR)
    luz_empotrada(d, 130, 220, 70, 16, CIAN)
    # estantería de herramientas + extintor
    base_panel(d, 780, 560, 980, 940, fill=PANEL_2)
    for j in range(3):
        y = 610 + j * 110
        d.rectangle([790, y + 60, 970, y + 68], fill=STEEL)
        if j == 0:
            d.rectangle([810, y, 840, y + 60], fill=ROJO)
            d.rectangle([818, y - 14, 832, y], fill=STEEL_LO)
        elif j == 1:
            for t in range(3):
                d.rectangle([820 + t * 34, y + 8, 846 + t * 34, y + 60],
                            fill=CIAN_LO)
        else:
            d.ellipse([830, y + 6, 900, y + 62], fill=AMBAR)
    pantalla(d, 300, 800, 700, 960, seed=43)
    franja_aviso(d, 0, 20, S, h=26)
    im.save(OUT + '/sala_right.jpg', quality=90)


if __name__ == '__main__':
    suelo()
    techo()
    back()
    front()
    left()
    right()
    for f in ('sala_floor.jpg', 'sala_ceil.jpg', 'sala_back.jpg',
              'sala_front.jpg', 'sala_left.jpg', 'sala_right.jpg'):
        p = OUT + '/' + f
        print(f, os.path.getsize(p))
    print('SALA OK')

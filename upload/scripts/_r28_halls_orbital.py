#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r28 — OBSERVATORIO ESTELAR (estación orbital de lujo).
Paneles metálicos con remaches y conductos, OJO DE BUEY con la TIERRA
real (continentes, nubes, terminador, atmósfera), consolas con pantallas
de datos orbitales, esclusa con rayas de peligro, suelo de placas con
guías de luz y emblema ESTACION 7."""
from PIL import Image, ImageDraw, ImageFilter
import math, random
from _r28_hall_lib import (grad_multi, grano, vineta, ao_esquinas, contacto_suelo,
                           sombra_techo, texto_neon, tubo_neon, foco_glow, caja_3t,
                           sombra_prop, remaches, campo_estrellas, tierra,
                           _aclara, _oscurece)

ACERO = (52, 60, 74)
ACERO_O = (30, 36, 48)
CIAN = (80, 200, 255)
AMBAR = (255, 176, 64)
ROJO_A = (255, 90, 70)


def _panel(img, caja, seed, leds=True, tint=None):
    """Panel de nave: chapa con gradiente, juntas, remaches, rejillas de
    ventilación y tiras LED opcionales."""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = caja
    base = tint or ACERO
    caja_3t(d, caja, base)
    # juntas internas (sub-paneles)
    nx, ny = rnd.randint(2, 3), rnd.randint(2, 3)
    for i in range(1, nx):
        x = x0 + (x1 - x0) * i // nx
        d.line([x, y0, x, y1], fill=_oscurece(base, .35), width=3)
    for j in range(1, ny):
        y = y0 + (y1 - y0) * j // ny
        d.line([x0, y, x1, y], fill=_oscurece(base, .35), width=3)
    remaches(d, caja, 74)
    # rejillas de ventilación en un sub-panel
    vx = x0 + (x1 - x0) // 2 - 40
    vy = y0 + (y1 - y0) // 2 - 30
    for k in range(6):
        d.rectangle([vx, vy + k * 10, vx + 80, vy + k * 10 + 5], fill=_oscurece(base, .5))
    if leds:
        for k in range(5):
            lx = x0 + 18 + k * 22
            col = [CIAN, AMBAR, (90, 230, 140)][k % 3] if rnd.random() < .8 else ROJO_A
            d.rectangle([lx, y1 - 22, lx + 12, y1 - 12], fill=col)
            img = foco_glow(img, (lx + 6, y1 - 17), 10, col, fuerza=110)
            d = ImageDraw.Draw(img)
    return img


def _tuberia(img, pts, grosor=16, col=(90, 100, 118)):
    """Conducto con sombreado cilíndrico + brida."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = pts
    vertical = abs(x1 - x0) < abs(y1 - y0)
    if vertical:
        for k in range(grosor):
            t = k / grosor
            f = math.sin(t * math.pi)
            c = int(col[0] * (0.45 + f * 0.75)), int(col[1] * (0.45 + f * 0.75)), int(col[2] * (0.45 + f * 0.75))
            d.line([x0 + k, y0, x0 + k, y1], fill=c)
        for by in (y0 + 14, y1 - 14):
            d.rectangle([x0 - 3, by, x0 + grosor + 3, by + 8], fill=_aclara(col, .12))
    else:
        for k in range(grosor):
            t = k / grosor
            f = math.sin(t * math.pi)
            c = int(col[0] * (0.45 + f * 0.75)), int(col[1] * (0.45 + f * 0.75)), int(col[2] * (0.45 + f * 0.75))
            d.line([x0, y0 + k, x1, y0 + k], fill=c)
        for bx in (x0 + 14, x1 - 14):
            d.rectangle([bx, y0 - 3, bx + 8, y0 + grosor + 3], fill=_aclara(col, .12))
    return img


def _capa_glow_anillo(img, centro, radio, grosor, col, fuerza=140):
    """Glow en ANILLO (para marcos y ventanas: ilumina sin lavar el centro)."""
    from PIL import ImageChops
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    cx, cy = centro
    d.ellipse([cx - radio, cy - radio, cx + radio, cy + radio], outline=col + (255,), width=grosor)
    out = img.convert('RGBA')
    for b, f in [(radio * 0.55, int(fuerza * 0.6)), (radio * 0.16, fuerza)]:
        c = capa.filter(ImageFilter.GaussianBlur(b))
        a = c.getchannel('A').point(lambda v: int(v * f / 255))
        c.putalpha(a)
        out = ImageChops.add(out, c)
    return out.convert('RGB')


def _consola(img, caja, seed):
    """Consola: pantalla con órbita + teclas + LEDs."""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = caja
    caja_3t(d, caja, (38, 44, 58), luz_izq=False)
    # pantalla con TRAYECTORIA ORBITAL
    sx0, sy0, sx1, sy1 = x0 + 14, y0 + 12, x1 - 14, y0 + (y1 - y0) * 52 // 100
    d.rectangle([sx0, sy0, sx1, sy1], fill=(5, 14, 20))
    pw, ph = sx1 - sx0, sy1 - sy0
    # planeta + elipses de órbita
    ccx, ccy = pw // 2, ph // 2
    for rr in range(24, max(pw, ph), 26):
        d.ellipse([ccx - rr, ccy - rr * 0.42, ccx + rr, ccy + rr * 0.42],
                  outline=(40, 130, 150), width=1)
    d.ellipse([ccx - 9, ccy - 9, ccx + 9, ccy + 9], fill=CIAN)
    sat = (ccx + int(math.cos(rnd.random() * 6) * 90), ccy + int(math.sin(rnd.random() * 6) * 38))
    d.ellipse([sat[0] - 4, sat[1] - 4, sat[0] + 4, sat[1] + 4], fill=AMBAR)
    # teclas
    d = ImageDraw.Draw(img)
    for r_ in range(2):
        for c_ in range(8):
            kx = x0 + 18 + c_ * ((x1 - x0 - 36) // 8)
            ky = sy1 + 10 + r_ * 16
            col = (70, 80, 100) if (c_ + r_) % 3 else AMBAR
            d.rectangle([kx, ky, kx + 14, ky + 10], fill=col)
    return img


def frente():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (10, 14, 22)), (0.5, (22, 30, 44)), (1, (12, 16, 26))])
    # bahía de observación CENTRAL: ventana octogonal con la TIERRA
    cx = w // 2
    cy = int(h * .40)
    r = 235
    # marco octogonal metálico
    d = ImageDraw.Draw(img)
    pts = []
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        pts.append((cx + math.cos(a) * (r + 46), cy + math.sin(a) * (r + 46)))
    d.polygon(pts, fill=ACERO_O)
    pts2 = [(cx + math.cos(a := math.pi / 8 + k * math.pi / 4) * (r + 8),
             cy + math.sin(a) * (r + 8)) for k in range(8)]
    d.polygon(pts2, fill=(14, 20, 30))
    # interior: campo de estrellas + Tierra (r28: glow SÓLO detrás del marco,
    # nunca encima del disco — antes lavaba la Tierra hasta dejar un blob cian)
    win = Image.new('RGB', (r * 2, r * 2), (4, 6, 14))
    win = campo_estrellas(win, 130, seed=21, grandes=7)
    win = tierra(win, r, r, int(r * 0.78), seed=5, luz_deg=205)
    m = Image.new('L', win.size, 0)
    md = ImageDraw.Draw(m)
    md.ellipse([0, 0, r * 2, r * 2], fill=255)
    img.paste(win, (cx - r, cy - r), m)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CIAN, width=3)
    # remaches del marco
    for k in range(16):
        a = math.pi / 8 + k * math.pi / 4 * 0.5
        bx, by = cx + math.cos(a) * (r + 26), cy + math.sin(a) * (r + 26)
        d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=_aclara(ACERO, .3))
    # halo EXTERIOR del marco (anillo, no disco lleno)
    d2 = ImageDraw.Draw(img)
    d2.ellipse([cx - int(r * 1.16), cy - int(r * 1.16), cx + int(r * 1.16), cy + int(r * 1.16)],
               outline=(40, 90, 150), width=14)
    img = _capa_glow_anillo(img, (cx, cy), int(r * 1.16), 26, (40, 90, 150), fuerza=70)
    # consolas bajo la ventana
    img = contacto_suelo(img, 0.09, 115)
    img = _consola(img, (int(w * .06), int(h * .66), int(w * .27), h - 8), 31)
    img = _consola(img, (int(w * .73), int(h * .66), int(w * .94), h - 8), 32)
    d = ImageDraw.Draw(img)
    # panel central bajo la ventana con rayas de peligro
    px0, px1 = cx - 190, cx + 190
    d.rectangle([px0, int(h * .70), px1, h - 8], fill=(40, 46, 58), outline=(18, 22, 30))
    for k in range(-8, 26):
        x = px0 + k * 34
        d.polygon([(x, h - 8), (x + 16, h - 8), (x + 34, int(h * .70)), (x + 18, int(h * .70))],
                  fill=AMBAR if k % 2 else (26, 26, 30))
    img = texto_neon(img, 'ESTACION 7', (cx, int(h * .79)), 40, CIAN)
    # paneles laterales que enmarcan
    img = _panel(img, (0, int(h * .06), int(w * .045), h), 41, leds=False)
    img = _panel(img, (int(w * .955), int(h * .06), w, h), 42, leds=False)
    img = sombra_techo(img, 0.07, 85)
    img = ao_esquinas(img, 64)
    img = grano(img, 12, 8)
    img = vineta(img, 54)
    return img


def fondo():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (9, 12, 20)), (0.5, (20, 27, 40)), (1, (11, 14, 24))])
    cx = w // 2
    # ESCLUSA: puerta circular pesada
    r = 190
    cy = int(h * .48)
    img = sombra_prop(img, (cx - r - 30, cy - r - 20, cx + r + 30, h), alfa=90, blur=24, dy=10)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 46, cy - r - 46, cx + r + 46, cy + r + 46], fill=ACERO_O)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(36, 42, 56))
    # rayas de peligro alrededor del aro
    for k in range(36):
        a0 = k * math.pi / 18
        a1 = a0 + math.pi / 36
        p0 = (cx + math.cos(a0) * (r + 40), cy + math.sin(a0) * (r + 40))
        p1 = (cx + math.cos(a1) * (r + 40), cy + math.sin(a1) * (r + 40))
        p2 = (cx + math.cos(a1) * (r + 12), cy + math.sin(a1) * (r + 12))
        p3 = (cx + math.cos(a0) * (r + 12), cy + math.sin(a0) * (r + 12))
        d.polygon([p0, p1, p2, p3], fill=AMBAR if k % 2 else (30, 30, 34))
    # rueda de apertura (volante)
    d.ellipse([cx - 64, cy - 64, cx + 64, cy + 64], outline=_aclara(ACERO, .18), width=14)
    for k in range(3):
        a = k * math.pi / 3
        d.line([cx - math.cos(a) * 56, cy - math.sin(a) * 56, cx + math.cos(a) * 56,
                cy + math.sin(a) * 56], fill=_aclara(ACERO, .22), width=12)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=_aclara(ACERO, .3))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=_oscurece(ACERO, .4), width=6)
    # luces de estado de la esclusa
    for k, col in enumerate([ROJO_A, AMBAR, (90, 230, 140)]):
        ly = cy - 60 + k * 60
        d.ellipse([cx + r + 76 - 10, ly - 10, cx + r + 76 + 10, ly + 10], fill=col)
        img = foco_glow(img, (cx + r + 76, ly), 17, col, fuerza=150)
    d = ImageDraw.Draw(img)
    # paneles con tuberías a los lados
    img = _panel(img, (int(w * .04), int(h * .10), int(w * .26), h - 6), 51)
    img = _panel(img, (int(w * .74), int(h * .10), int(w * .96), h - 6), 52)
    img = _tuberia(img, (int(w * .07), int(h * .30), int(w * .07), h - 20), 20)
    img = _tuberia(img, (int(w * .075), int(h * .22), int(w * .24), int(h * .22)), 14, (110, 90, 80))
    img = _tuberia(img, (int(w * .93), int(h * .34), int(w * .93), h - 20), 20)
    img = _tuberia(img, (int(w * .76), int(h * .26), int(w * .925), int(h * .26)), 14, (80, 110, 96))
    d = ImageDraw.Draw(img)
    img = texto_neon(img, 'AIRLOCK 02', (cx, int(h * .82)), 38, CIAN)
    img = contacto_suelo(img, 0.09, 115)
    img = sombra_techo(img, 0.06, 85)
    img = ao_esquinas(img, 62)
    img = grano(img, 12, 8)
    img = vineta(img, 54)
    return img


def lateral(seed):
    w, h = 2395, 864
    img = grad_multi(w, h, [(0, (8, 11, 18)), (0.5, (19, 26, 38)), (1, (10, 13, 22))])
    # zócalo de paneles grandes
    n = 6
    pw = w // n
    for i in range(n):
        img = _panel(img, (i * pw + 6, int(h * .055), (i + 1) * pw - 6, h - int(h * .07)), seed * 10 + i,
                     leds=(i % 2 == 0))
    # ojos de buey con estrellas (2)
    for k, fx in enumerate([0.30, 0.70]):
        cx = int(w * fx)
        cy = int(h * .40)
        r = 118
        img = campo_estrellas(img, 40, seed=seed + k, zona=(cx - r, cy - r, cx + r, cy + r))
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22], fill=ACERO_O)
        win = Image.new('RGB', (r * 2, r * 2), (3, 5, 12))
        win = campo_estrellas(win, 60, seed=seed + 5 + k, grandes=3)
        m = Image.new('L', win.size, 0)
        ImageDraw.Draw(m).ellipse([0, 0, r * 2, r * 2], fill=255)
        img.paste(win, (cx - r, cy - r), m)
        d = ImageDraw.Draw(img)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=_aclara(ACERO, .2), width=8)
        for b in range(8):
            a = b * math.pi / 4
            bx, by = cx + math.cos(a) * (r + 11), cy + math.sin(a) * (r + 11)
            d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=_aclara(ACERO, .35))
        img = _capa_glow_anillo(img, (cx, cy), r + 16, 12, (60, 120, 170), fuerza=90)
    # tuberías cruzadas + esquema de la estación
    img = _tuberia(img, (int(w * .05), int(h * .78), int(w * .95), int(h * .78)), 18)
    img = _tuberia(img, (int(w * .16), int(h * .12), int(w * .16), int(h * .72)), 16, (100, 86, 76))
    d = ImageDraw.Draw(img)
    # póster esquemático (planos de la estación)
    sx0, sy0, sx1, sy1 = int(w * .40), int(h * .56), int(w * .52), int(h * .90)
    d.rectangle([sx0, sy0, sx1, sy1], fill=(226, 228, 232), outline=(140, 144, 152), width=4)
    sd = ImageDraw.Draw(img)
    for k in range(4):
        sd.rectangle([sx0 + 12, sy0 + 12 + k * 26, sx1 - 12, sy0 + 30 + k * 26],
                     outline=(70, 80, 96), width=2)
    sd.ellipse([sx0 + 26, sy0 + 20, sx1 - 26, sy1 - 14], outline=(90, 100, 120), width=3)
    img = contacto_suelo(img, 0.08, 110)
    img = sombra_techo(img, 0.06, 82)
    img = ao_esquinas(img, 60)
    img = grano(img, 12, 8)
    img = vineta(img, 52)
    return img


def suelo():
    w, h = 1296, 1678
    img = grad_multi(w, h, [(0, (16, 20, 30)), (0.5, (26, 32, 44)), (1, (15, 19, 28))], horizontal=True)
    d = ImageDraw.Draw(img)
    # placas de cubierta con ranura antideslizante
    pw, ph = 216, 240
    for yy in range(0, h, ph):
        for xx in range(0, w, pw):
            d.rectangle([xx + 3, yy + 3, xx + pw - 3, yy + ph - 3],
                        fill=(30 + (xx // pw + yy // ph) % 2 * 6, 38 + (xx // pw + yy // ph) % 2 * 6, 52),
                        outline=(14, 18, 26), width=3)
            for gy in range(yy + 18, yy + ph - 10, 14):
                d.line([xx + 12, gy, xx + pw - 12, gy], fill=(24, 30, 42), width=2)
    # guías de luz hacia el centro
    cx, cy = w // 2, h // 2
    for s in (-1, 1):
        img = tubo_neon(img, [(cx + s * 90, 0), (cx + s * 90, h)], (70, 170, 220), grosor=3, halo=14)
    # emblema ESTACION 7 con anillo
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 210, cy - 120, cx + 210, cy + 120], outline=(120, 150, 170), width=8)
    d.ellipse([cx - 180, cy - 96, cx + 180, cy + 96], outline=(90, 110, 130), width=3)
    img = texto_neon(img, 'ESTACION 7', (cx, cy), 60, CIAN)
    img = grano(img, 12, 8)
    img = vineta(img, 58)
    return img


def techo():
    w, h = 1296, 1678
    img = grad_multi(w, h, [(0, (10, 13, 20)), (0.5, (18, 23, 34)), (1, (9, 12, 19))], horizontal=True)
    d = ImageDraw.Draw(img)
    # costillas estructurales + paneles de luz fríos
    for i in range(7):
        y = int(h * (0.07 + i * 0.145))
        d.rectangle([0, y - 10, w, y + 10], fill=(26, 32, 44))
        d.rectangle([0, y - 10, w, y - 4], fill=(40, 50, 66))
    for i in range(6):
        y = int(h * (0.12 + i * 0.16))
        px0, px1 = int(w * .30), int(w * .70)
        # panel de luz con ESTRUCTURA: marco, difusor con nervios y glow SUAVE
        d.rectangle([px0 - 10, y - 32, px1 + 10, y + 32], fill=(46, 56, 72))
        d.rectangle([px0, y - 22, px1, y + 22], fill=(196, 212, 224))
        for k in range(1, 6):
            x = px0 + (px1 - px0) * k // 6
            d.line([x, y - 22, x, y + 22], fill=(160, 176, 190), width=2)
        img = _capa_glow_anillo(img, ((px0 + px1) // 2, y), 46, 20, (120, 160, 190), fuerza=60)
    d = ImageDraw.Draw(img)
    # conducto central
    img = _tuberia(img, (int(w * .5) - 13, 0, int(w * .5) - 13, h), 26, (70, 80, 96))
    img = grano(img, 12, 8)
    img = vineta(img, 56)
    return img

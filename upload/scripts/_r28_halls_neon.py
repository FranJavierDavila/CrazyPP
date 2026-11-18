#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r28 — SALÓN NEÓN ARCADE (synthwave de lujo).
6 caras 1849×864 / 2395×864 / 1296×1678. Materiales: rejillas de neón,
recreativas DETALLADAS (marquesina, pantalla con partida viva, botones),
murales de horizonte, suelo espejo con emblema."""
from PIL import Image, ImageDraw, ImageFilter
import math, random
from _r28_hall_lib import (grad_multi, grano, vineta, ao_esquinas, contacto_suelo,
                           sombra_techo, texto_neon, tubo_neon, foco_glow, caja_3t,
                           sombra_prop, remaches, campo_estrellas, _aclara, _oscurece)

MAGENTA = (255, 60, 170)
CIAN = (60, 220, 255)
VIOLETA = (150, 80, 255)
AMAR = (255, 200, 60)
AZUL_N = (10, 8, 26)


def _recreativa(img, x, y, w, h, seed, col_neon):
    """Cabinet de recreativa DETALLADO: cuerpo, marquesina encendida,
    pantalla con PARTIDA de ping-pong, panel de mandos, monedero, pies."""
    rnd = random.Random(seed)
    img = sombra_prop(img, (x + 6, y + h - 4, x + w + 14, y + h + 8), alfa=130, blur=10)
    d = ImageDraw.Draw(img)
    cuerpo = (30, 26, 54)
    # sombra lateral + cuerpo
    caja_3t(d, (x, y, x + w, y + h), cuerpo)
    # marquesina inclinada (trapecio) encendida
    my = y + int(h * 0.02)
    mh = int(h * 0.11)
    d.polygon([(x - int(w * .04), my + mh), (x + w + int(w * .04), my + mh),
               (x + w - int(w * .06), my), (x + int(w * .06), my)],
              fill=_oscurece(col_neon, 0.55))
    img = texto_neon(img, 'PP', (x + w // 2, my + mh // 2), int(mh * 0.8), col_neon)
    d = ImageDraw.Draw(img)
    # bisel de pantalla
    sx0, sy0, sx1, sy1 = x + int(w * .10), y + mh + int(h * .05), x + int(w * .90), y + int(h * .62)
    d.rectangle([sx0 - 6, sy0 - 6, sx1 + 6, sy1 + 6], fill=(16, 14, 30))
    # PANTALLA con partida viva: mesa verde-azul, red, palas, bola con estela
    pant = Image.new('RGB', (sx1 - sx0, sy1 - sy0), (6, 10, 22))
    pd = ImageDraw.Draw(pant)
    pw, ph = pant.size
    # mesa
    mt = (14, 60, 50) if rnd.random() < .5 else (18, 40, 80)
    pd.polygon([(pw * .18, ph * .30), (pw * .82, ph * .30), (pw * .95, ph * .78),
                (pw * .05, ph * .78)], fill=mt)
    pd.line([(pw * .05, ph * .78), (pw * .95, ph * .78)], fill=_aclara(mt, .3), width=2)
    # red
    pd.line([(pw * .5, ph * .40), (pw * .5, ph * .70)], fill=(220, 230, 240), width=2)
    # palas
    pd.ellipse([pw * .24 - 7, ph * .52 - 10, pw * .24 + 7, ph * .52 + 10], fill=(240, 70, 70))
    pd.ellipse([pw * .74 - 7, ph * .50 - 10, pw * .74 + 7, ph * .50 + 10], fill=(70, 140, 250))
    # bola + estela
    bx, by = pw * .58, ph * .44
    for k in range(4):
        pd.ellipse([bx - 3 - k * 8, by - 3 + k * 3, bx + 3 - k * 8, by + 3 + k * 3],
                   fill=(255, 255, 255, 40))
    pd.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 255, 255))
    pant = grano(pant, 12, 8)
    # scanlines CRT
    sc = ImageDraw.Draw(pant)
    for yy in range(0, ph, 3):
        sc.line([0, yy, pw, yy], fill=(0, 0, 0), width=1)
    img.paste(pant, (sx0, sy0))
    d = ImageDraw.Draw(img)
    # r28b · SIN halo sobre la pantalla: el CRT ya brilla por sí mismo
    # (el foco_glow anterior lo saturaba hasta tapar la partida)
    # panel de mandos: joysticks + botones
    py0 = sy1 + 8
    d.rectangle([x + int(w * .08), py0, x + int(w * .92), py0 + int(h * .10)],
                fill=(24, 20, 44), outline=(70, 60, 110))
    for jx in (x + int(w * .22), x + int(w * .78)):
        d.ellipse([jx - 10, py0 + 8, jx + 10, py0 + 28], fill=(200, 205, 220))
        d.line([jx, py0 + 18, jx, py0 - 2], fill=(90, 90, 110), width=3)
    for k, bc in enumerate([MAGENTA, CIAN, AMAR]):
        bx2 = x + int(w * .40) + k * int(w * .08)
        d.ellipse([bx2 - 6, py0 + 12, bx2 + 6, py0 + 24], fill=bc, outline=(10, 10, 16))
    # monedero + arte lateral
    d.rectangle([x + w // 2 - 8, y + int(h * .80), x + w // 2 + 8, y + int(h * .90)],
                fill=(12, 12, 20), outline=(90, 90, 130))
    for sy2 in range(y + int(h * .68), y + int(h * .80), 8):
        d.line([x + 6, sy2, x + int(w * .09), sy2], fill=col_neon, width=2)
        d.line([x + w - 6, sy2, x + w - int(w * .09), sy2], fill=CIAN, width=2)
    # pies
    d.rectangle([x + 4, y + h, x + int(w * .16), y + h + 10], fill=(14, 12, 26))
    d.rectangle([x + int(w * .84), y + h, x + w - 4, y + h + 10], fill=(14, 12, 26))
    return img


def frente():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (8, 6, 20)), (0.45, (16, 10, 38)), (0.8, (26, 12, 48)), (1, (10, 6, 22))])
    # murales geométricos de fondo
    d = ImageDraw.Draw(img)
    rnd = random.Random(11)
    for _ in range(26):
        x = rnd.uniform(0, w); y = rnd.uniform(40, h * .5)
        r = rnd.uniform(20, 90)
        col = rnd.choice([MAGENTA, CIAN, VIOLETA])
        if rnd.random() < .5:
            d.polygon([(x, y - r), (x + r * .9, y + r * .7), (x - r * .9, y + r * .7)],
                      outline=_oscurece(col, .35), width=2)
        else:
            d.polygon([(x, y - r * .6), (x + r * .6, y), (x, y + r * .6), (x - r * .6, y)],
                      outline=_oscurece(col, .35), width=2)
    img = campo_estrellas(img, 90, seed=3, zona=(0, 0, w, int(h * .45)))
    # letrero maestro doble línea
    img = texto_neon(img, 'CRAZY ARCADE', (w // 2, int(h * .185)), 118, MAGENTA)
    d = ImageDraw.Draw(img)
    # marco del letrero
    for col, off in [(CIAN, 96), (MAGENTA, 108)]:
        d.rounded_rectangle([w * .13, h * .075 + off, w * .87, h * .30 + off],
                            radius=26, outline=col, width=4)
    # fila de 4 recreativas sobre zócalo
    img = contacto_suelo(img, 0.11, 130)
    zw = int(w * .92)
    x0 = (w - zw) // 2
    cw, gap = int(zw * .185), int(zw * .067)
    for i in range(4):
        col = [CIAN, MAGENTA, VIOLETA, AMAR][i]
        img = _recreativa(img, x0 + i * (cw + gap), int(h * .36), cw, int(h * .52), 40 + i, col)
    d = ImageDraw.Draw(img)
    # zócalo con tira de luz
    d.rectangle([0, h - 26, w, h], fill=(20, 12, 34))
    img = tubo_neon(img, [(0, h - 30), (w, h - 30)], CIAN, grosor=4, halo=18)
    img = ao_esquinas(img, 70)
    img = grano(img, 12, 9)
    img = vineta(img, 58)
    return img


def fondo():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (9, 7, 22)), (0.5, (18, 11, 40)), (1, (12, 7, 26))])
    img = campo_estrellas(img, 70, seed=9, zona=(0, 0, w, int(h * .5)))
    # PUERTA: portal triangular synthwave (la puerta del salón)
    cx = w // 2
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 150, int(h * .30), cx + 150, h], fill=(6, 5, 14))
    img = tubo_neon(img, [(cx - 150, h), (cx - 150, int(h * .30)), (cx + 150, int(h * .30)), (cx + 150, h)],
                    MAGENTA, grosor=6, halo=26)
    # horizonte dentro del portal
    d = ImageDraw.Draw(img)
    hor = int(h * .72)
    for i in range(10):
        t = i / 10
        d.line([cx - 150, hor + i * 9, cx + 150, hor + i * 9], fill=_oscurece(CIAN, .3 + t * .5), width=2)
    img = foco_glow(img, (cx, hor), 190, VIOLETA, fuerza=110)
    img = texto_neon(img, 'INSERT COIN', (int(w * .80), int(h * .16)), 44, AMAR)
    # máquinas flanqueando la puerta
    img = contacto_suelo(img, 0.11, 130)
    img = _recreativa(img, int(w * .045), int(h * .40), int(w * .145), int(h * .50), 61, CIAN)
    img = _recreativa(img, int(w * .815), int(h * .40), int(w * .145), int(h * .50), 62, MAGENTA)
    # máquina de snacks entre medias
    d = ImageDraw.Draw(img)
    vx = cx - 70
    caja_3t(d, (vx, int(h * .47), vx + 140, h - 10), (36, 30, 60))
    d = ImageDraw.Draw(img)
    rr2 = random.Random(77)
    for fila in range(3):
        for c_ in range(3):
            colp = (rr2.randint(70, 220), rr2.randint(50, 200), rr2.randint(80, 230))
            d.rectangle([vx + 14 + c_ * 40, int(h * .50) + fila * 44, vx + 44 + c_ * 40,
                         int(h * .50) + fila * 44 + 30], fill=colp)
    d.rectangle([vx + 30, h - 74, vx + 110, h - 20], fill=(10, 10, 16))  # expendedor
    img = ao_esquinas(img, 70)
    img = grano(img, 12, 9)
    img = vineta(img, 58)
    return img


def rnd_(s):
    r = random.Random(s + 99)
    return (r.randint(60, 220), r.randint(40, 200), r.randint(80, 230))


def lateral(seed, espejo):
    w, h = 2395, 864
    img = grad_multi(w, h, [(0, (7, 5, 18)), (0.55, (20, 10, 44)), (0.86, (36, 14, 58)), (1, (14, 8, 30))])
    img = campo_estrellas(img, 130, seed=seed, zona=(0, 0, w, int(h * .55)), grandes=8)
    # SOL synthwave con franjas (r28: ecuación del círculo CORRECTA — antes
    # la x salía desplazada y el sol no aparecía) + horizonte de rejilla
    cx = w // 2
    hor = int(h * .60)
    r_sol = 215
    cy_sol = hor - 46
    # r28b · glow del sol SÓLO en anillo tras él (el disco lleno anterior
    # inundaba el mural entero de rosa)
    from _r28_halls_orbital import _capa_glow_anillo
    img = _capa_glow_anillo(img, (cx, cy_sol), int(r_sol * 1.06), 40, MAGENTA, fuerza=52)
    d = ImageDraw.Draw(img)
    # SOL synthwave CLÁSICO (r28c): disco completo con gradiente amarillo→
    # magenta→violeta y 3 CORTES horizontales que crecen hacia abajo,
    # compuesto como capa RGBA (antes las bandas escalonadas hacían zigurat)
    sol = Image.new('RGBA', (r_sol * 2, r_sol * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sol)
    for y in range(r_sol * 2):
        t = y / (r_sol * 2 - 1)
        if t < 0.45:
            f = t / 0.45
            col = (255, int(224 - f * 150), int(90 + f * 60))
        else:
            f = (t - 0.45) / 0.55
            col = (int(255 - f * 60), int(74 - f * 30), int(150 + f * 90))
        dx = int(math.sqrt(max(0, r_sol * r_sol - (y - r_sol) ** 2)))
        if dx > 0:
            sd.line([r_sol - dx, y, r_sol + dx, y], fill=col + (255,))
    # cortes horizontales (r28c: sólo cortan la parte VISIBLE del disco —
    # el horizonte recorta el disco en la fila 0.606 — y crecen hacia abajo)
    for c0, c1 in [(0.26, 0.33), (0.40, 0.49), (0.53, 0.60)]:
        sd.rectangle([0, int(r_sol * 2 * c0), r_sol * 2, int(r_sol * 2 * c1)],
                     fill=(0, 0, 0, 0))
    m_sol = Image.new('L', sol.size, 0)
    ImageDraw.Draw(m_sol).ellipse([0, 0, r_sol * 2, r_sol * 2], fill=255)
    # el sol se sienta SOBRE el horizonte: todo lo que baja de él, fuera
    dclip = ImageDraw.Draw(m_sol)
    dclip.rectangle([0, r_sol + 46, r_sol * 2, r_sol * 2], fill=0)
    img.paste(sol, (cx - r_sol, cy_sol - r_sol), m_sol)
    d = ImageDraw.Draw(img)
    picos = [(0, hor), (int(w * .08), hor - 90), (int(w * .16), hor), (int(w * .26), hor - 150),
             (int(w * .36), hor), (cx, hor - 40), (int(w * .64), hor), (int(w * .74), hor - 170),
             (int(w * .84), hor), (int(w * .92), hor - 80), (w, hor)]
    d.line(picos, fill=_aclara(VIOLETA, .1), width=3)
    # rejilla del suelo: rayos al punto de fuga + horizontales DENSOS cerca
    # del horizonte (espaciado geométrico, el clásico synthwave)
    for px_ in range(0, w + 1, 130):
        d.line([px_, hor, int(cx + (px_ - cx) * 3.2), h], fill=_oscurece(MAGENTA, .45), width=2)
    gy = hor + 6
    paso = 4.0
    while gy < h:
        d.line([0, int(gy), w, int(gy)], fill=_oscurece(CIAN, .2), width=2)
        paso *= 1.24
        gy += paso
    # ARCOS de neón repetidos (el ritmo del salón)
    n_arcs = 5
    for i in range(n_arcs):
        ax = int(w * (0.09 + 0.2 * i))
        img = tubo_neon(img, [(ax - 120, h), (ax - 120, int(h * .16)), (ax + 120, int(h * .16)), (ax + 120, h)],
                        CIAN if i % 2 == 0 else MAGENTA, grosor=4, halo=20)
    d = ImageDraw.Draw(img)
    img = contacto_suelo(img, 0.10, 125)
    img = sombra_techo(img, 0.07, 95)
    img = ao_esquinas(img, 66)
    img = grano(img, 12, 9)
    img = vineta(img, 55)
    return img


def suelo():
    w, h = 1296, 1678
    img = grad_multi(w, h, [(0, (10, 7, 24)), (0.5, (16, 10, 36)), (1, (24, 13, 46))], horizontal=True)
    cx, cy = w // 2, h // 2
    # rejilla de baile en perspectiva (desde el centro)
    d = ImageDraw.Draw(img)
    paso = 56
    for i in range(-12, 13):
        x = cx + i * paso
        f = 1 + abs(i) * 0.02
        d.line([x, 0, int(cx + i * paso * 2.4), h], fill=_oscurece(MAGENTA, .35), width=2)
    for yy in range(0, h, paso):
        alfa = 1 - abs(yy - cy) / (h / 2)
        d.line([0, yy, w, yy], fill=_oscurece(CIAN, .2 + (1 - alfa) * .55), width=2)
    # brillo de reflejo central
    img = foco_glow(img, (cx, cy), 330, VIOLETA, fuerza=55)
    # emblema central con anillos
    img = texto_neon(img, 'CRAZY PP', (cx, cy), 92, CIAN)
    d = ImageDraw.Draw(img)
    for rr, col in [(180, MAGENTA), (210, _oscurece(MAGENTA, .3))]:
        d.ellipse([cx - rr, cy - 62, cx + rr, cy + 62], outline=col, width=4)
    img = grano(img, 12, 9)
    img = vineta(img, 62)
    return img


def techo():
    w, h = 1296, 1678
    img = grad_multi(w, h, [(0, (6, 5, 14)), (0.5, (11, 8, 24)), (1, (7, 5, 16))], horizontal=True)
    d = ImageDraw.Draw(img)
    # vigas + tiras de luz de neón (tubos de la discoteca)
    for i in range(6):
        y = int(h * (0.09 + i * 0.16))
        d.rectangle([60, y - 8, w - 60, y + 8], fill=(18, 14, 34))
        col = [MAGENTA, CIAN][i % 2]
        img = tubo_neon(img, [(90, y), (w - 90, y)], col, grosor=4, halo=20)
    d = ImageDraw.Draw(img)
    # paneles estrellados tenues
    img = campo_estrellas(img, 60, seed=17, zona=(0, 0, w, h))
    img = grano(img, 12, 8)
    img = vineta(img, 60)
    return img

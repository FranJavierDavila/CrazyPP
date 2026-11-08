#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r28 — DOJO ZEN (casa japonesa de lujo).
Madera noble con veta, shoji con PAISAJE tras el papel (Fuji al atardecer),
tokonoma con pergamino ensō e ikebana, farolillos andón, tatami con trama
real y borde de tela, techo de vigas con paneles washi."""
from PIL import Image, ImageDraw, ImageFilter
import math, random
from _r28_hall_lib import (grad_multi, grano, vineta, ao_esquinas, contacto_suelo,
                           sombra_techo, foco_glow, caja_3t, sombra_prop, _aclara, _oscurece)

MADERA = (94, 62, 38)
MADERA_O = (62, 40, 24)
MADERA_C = (128, 88, 52)
WASHI = (238, 228, 204)
SUMI = (34, 30, 28)
VERMELL = (178, 58, 44)
SAKURA = (244, 182, 196)


def _veta_madera(d, caja, tono, semilla, horizontal=True):
    """Veta de madera: líneas onduladas de tono variable."""
    rnd = random.Random(semilla)
    x0, y0, x1, y1 = caja
    n = 26 if horizontal else 26
    for k in range(n):
        f = k / n
        c = int(tono[0] * (0.82 + rnd.random() * 0.4)), int(tono[1] * (0.82 + rnd.random() * 0.4)), int(tono[2] * (0.82 + rnd.random() * 0.4))
        if horizontal:
            y = y0 + (y1 - y0) * f
            pts = [(x0 + (x1 - x0) * i / 12, y + math.sin(i * 0.9 + f * 9) * 2.2) for i in range(13)]
            d.line(pts, fill=c, width=2)
        else:
            x = x0 + (x1 - x0) * f
            pts = [(x + math.sin(i * 0.9 + f * 9) * 2.2, y0 + (y1 - y0) * i / 12) for i in range(13)]
            d.line(pts, fill=c, width=2)


def _shoji(img, caja, semilla, paisaje=False, atardecer=False):
    """Panel shoji: marco de madera + retícula kumiko + papel washi con
    luz cálida DETRÁS y silueta de paisaje opcional."""
    rnd = random.Random(semilla)
    x0, y0, x1, y1 = caja
    d = ImageDraw.Draw(img)
    # papel con gradiente de luz (más claro arriba-centro)
    base_top = (252, 244, 220) if not atardecer else (255, 214, 168)
    base_bot = (228, 214, 182) if not atardecer else (238, 160, 120)
    papel = grad_multi(x1 - x0, y1 - y0, [(0, base_top), (0.6, base_bot), (1, _oscurece(base_bot, .12))])
    if paisaje:
        # siluetas tras el papel: Fuji + colinas + niebla
        pd = ImageDraw.Draw(papel, 'RGBA')
        pw, ph = papel.size
        fx = pw * 0.5
        fh = ph * 0.34
        fy = ph * 0.62
        pd.polygon([(fx - fh * 1.35, fy), (fx - fh * 0.30, fy - fh), (fx + fh * 0.10, fy - fh * 0.86),
                    (fx + fh * 0.30, fy - fh * 0.98), (fx + fh * 1.35, fy)], fill=(120, 96, 110, 150))
        pd.ellipse([fx - fh * 0.5, fy - fh - 6, fx + fh * 0.5, fy - fh + 14], fill=(245, 240, 238, 190))
        pd.ellipse([-pw * .1, fy - ph * .1, pw * .45, fy + ph * .2], fill=(130, 104, 118, 90))
        pd.ellipse([pw * .55, fy - ph * .06, pw * 1.1, fy + ph * .22], fill=(130, 104, 118, 90))
    img.paste(papel, (x0, y0))
    d = ImageDraw.Draw(img)
    # retícula kumiko
    nx, ny = max(3, (x1 - x0) // 110), max(4, (y1 - y0) // 96)
    for i in range(1, nx):
        x = x0 + (x1 - x0) * i // nx
        d.rectangle([x - 3, y0, x + 3, y1], fill=MADERA)
    for j in range(1, ny):
        y = y0 + (y1 - y0) * j // ny
        d.rectangle([x0, y - 3, x1, y + 3], fill=MADERA)
    # marco grueso + travesaño
    d.rectangle(caja, outline=MADERA_O, width=10)
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=_aclara(MADERA, .18), width=3)
    return img


def _andón(img, x, y, s, semilla):
    """Farolillo andón: caja de papel con luz cálida + techo de madera."""
    img = sombra_prop(img, (x - 30 * s, y + 96 * s, x + 30 * s, y + 110 * s), alfa=100, blur=10)
    d = ImageDraw.Draw(img)
    # resplandor en la pared
    img = foco_glow(img, (x, y + 40 * s), 90 * s, (255, 190, 110), fuerza=110)
    d = ImageDraw.Draw(img)
    caja_3t(d, (x - 26 * s, y, x + 26 * s, y + 92 * s), (252, 236, 200), luz_izq=False)
    d = ImageDraw.Draw(img)
    # listones verticales del papel
    for k in range(1, 5):
        lx = x - 26 * s + k * 52 * s / 5
        d.line([lx, y, lx, y + 92 * s], fill=_oscurece((226, 206, 168), .08), width=2)
    # techo y base de madera
    d.rectangle([x - 34 * s, y - 10 * s, x + 34 * s, y], fill=MADERA_O)
    d.rectangle([x - 30 * s, y + 92 * s, x + 30 * s, y + 100 * s], fill=MADERA_O)
    # kanji decorativo (式 = estilo/forma; trazos simples)
    d.line([x - 9 * s, y + 30 * s, x + 9 * s, y + 30 * s], fill=SUMI, width=3)
    d.line([x, y + 22 * s, x, y + 62 * s], fill=SUMI, width=3)
    d.line([x - 12 * s, y + 62 * s, x + 12 * s, y + 62 * s], fill=SUMI, width=3)
    return img


def _cerezo(img, ax, ay, semilla, s=1.0, hacia_der=True):
    """Rama de cerezo: madera oscura + racimos de flores sakura."""
    rnd = random.Random(semilla)
    d = ImageDraw.Draw(img)
    pts = [(ax, ay)]
    x, y = ax, ay
    dirx = 1 if hacia_der else -1
    for k in range(6):
        x += dirx * rnd.uniform(30, 70) * s
        y += rnd.uniform(-14, 30) * s
        pts.append((x, y))
    d.line(pts, fill=(72, 48, 40), width=int(10 * s))
    # sub-ramas
    for k in range(1, 5):
        bx, by = pts[k]
        d.line([(bx, by), (bx + dirx * rnd.uniform(20, 46) * s, by - rnd.uniform(20, 50) * s)],
               fill=(72, 48, 40), width=int(5 * s))
    # flores
    for k in range(46):
        fx = ax + dirx * rnd.uniform(10, 260) * s
        fy = ay + rnd.uniform(-70, 46) * s
        r = rnd.uniform(7, 15) * s
        for p in range(5):
            a = p * 2 * math.pi / 5 + rnd.random()
            px, py = fx + math.cos(a) * r * .6, fy + math.sin(a) * r * .6
            d.ellipse([px - r * .38, py - r * .38, px + r * .38, py + r * .38], fill=SAKURA)
        d.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=(255, 224, 230))
    return img


def _ensyo(d, cx, cy, r, color=SUMI, wmax=13, abre=0.16):
    """Ensō: trazo de pincel circular con apertura y grosor variable."""
    pasos = 90
    for k in range(pasos):
        t0 = k / pasos
        a0 = -math.pi / 2 + t0 * (2 * math.pi * (1 - abre))
        w = wmax * (1 - t0 * 0.82) * (0.7 + 0.3 * math.sin(t0 * 9))
        x0 = cx + math.cos(a0) * r
        y0 = cy + math.sin(a0) * r
        d.ellipse([x0 - w, y0 - w, x0 + w, y0 + w], fill=color)


def frente():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (70, 48, 30)), (0.42, (92, 62, 38)), (0.8, (104, 72, 44)), (1, (58, 38, 24))])
    # pared de madera con listones verticales
    d = ImageDraw.Draw(img)
    for x in range(0, w, 92):
        d.line([x, 0, x, h], fill=_oscurece(MADERA, .22), width=3)
        _veta_madera(d, (x + 4, 0, x + 88, h), _oscurece(MADERA, .06), x)
    # TOKONOMA: alcoba central con pergamino e ikebana
    tx0, tx1 = int(w * .315), int(w * .685)
    ty0, ty1 = int(h * .06), int(h * .88)
    d.rectangle([tx0 - 26, ty0 - 20, tx1 + 26, ty1], fill=_oscurece(MADERA_O, .18))
    d.rectangle([tx0, ty0, tx1, ty1], fill=(52, 34, 22))
    # interior de la alcoba: fondo oscuro con gradiente
    alc = grad_multi(tx1 - tx0, ty1 - ty0, [(0, (30, 20, 14)), (1, (46, 30, 20))])
    img.paste(alc, (tx0, ty0))
    d = ImageDraw.Draw(img)
    # pergamino colgado (kakejiku) con ensō
    px0, py0 = (tx0 + tx1) // 2 - 120, ty0 + 26
    pw, ph = 240, 420
    d.rectangle([px0 - 10, py0 - 10, px0 + pw + 10, py0 + ph + 10], fill=_aclara(MADERA_O, .05))
    d.rectangle([px0, py0, px0 + pw, py0 + ph], fill=(236, 226, 196))
    d.rectangle([px0, py0, px0 + 26, py0 + ph], fill=(168, 148, 118))
    d.rectangle([px0 + pw - 26, py0, px0 + pw, py0 + ph], fill=(168, 148, 118))
    # ensō dentro
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    _ensyo(cd, px0 + pw // 2, py0 + ph // 2 - 20, 88)
    # firma vertical al lado
    for k in range(3):
        cd.line([px0 + pw - 52, py0 + 300 + k * 30, px0 + pw - 52, py0 + 316 + k * 30], fill=SUMI + (255,), width=4)
    capa = capa.filter(ImageFilter.GaussianBlur(0.7))
    img = Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')
    d = ImageDraw.Draw(img)
    # ikebana: jarrón + rama
    jx = tx0 + 90
    d.polygon([(jx - 34, ty1 - 96), (jx + 34, ty1 - 96), (jx + 24, ty1 - 10), (jx - 24, ty1 - 10)],
              fill=(30, 26, 26))
    img = _cerezo(img, jx, ty1 - 96, 5, s=0.62, hacia_der=True)
    d = ImageDraw.Draw(img)
    # base de la alcoba
    d.rectangle([tx0 - 26, ty1, tx1 + 26, h], fill=MADERA_C)
    # shoji a los lados de la alcoba
    img = _shoji(img, (int(w * .02), int(h * .12), tx0 - 40, int(h * .92)), 21)
    img = _shoji(img, (tx1 + 40, int(h * .12), int(w * .98), int(h * .92)), 22)
    # columnas de madera enmarcando todo
    for cx2 in (int(w * .012), int(w * .988)):
        d = ImageDraw.Draw(img)
        caja_3t(d, (cx2 - 16, 0, cx2 + 16, h), MADERA_O, luz_izq=(cx2 < w / 2))
        d = ImageDraw.Draw(img)
    img = contacto_suelo(img, 0.09, 120)
    img = sombra_techo(img, 0.07, 96)
    img = ao_esquinas(img, 58)
    img = grano(img, 11, 8)
    img = vineta(img, 50)
    return img


def fondo():
    w, h = 1849, 864
    img = grad_multi(w, h, [(0, (64, 44, 28)), (0.5, (86, 58, 36)), (1, (54, 36, 22))])
    d = ImageDraw.Draw(img)
    for x in range(0, w, 92):
        d.line([x, 0, x, h], fill=_oscurece(MADERA, .22), width=3)
        _veta_madera(d, (x + 4, 0, x + 88, h), _oscurece(MADERA, .06), x + 7)
    # PARED SHOJI GRANDE con atardecer cálido tras el papel + ranma superior
    img = _shoji(img, (int(w * .06), int(h * .30), int(w * .94), int(h * .90)), 33, paisaje=True, atardecer=True)
    d = ImageDraw.Draw(img)
    # ranma (transom) calado encima
    ry0, ry1 = int(h * .12), int(h * .26)
    d.rectangle([int(w * .06), ry0, int(w * .94), ry1], fill=MADERA_O)
    for k in range(14):
        x = int(w * .06) + k * int(w * .88 / 14)
        d.line([(x + int(w * .88 / 28), ry1 - 6), (x + int(w * .88 / 14), ry0 + 8),
                (x + int(w * .88 / 14) + int(w * .88 / 28), ry1 - 6)], fill=MADERA_C, width=6)
    # puerta corredera enmarcada en el centro del shoji
    cx = w // 2
    d.rectangle([cx - 120, int(h * .30), cx + 120, int(h * .90)], outline=MADERA_O, width=14)
    d.rectangle([cx - 8, int(h * .30), cx + 8, int(h * .90)], fill=MADERA_O)
    # tirador vermell
    d.ellipse([cx + 40, int(h * .58), cx + 64, int(h * .58) + 24], fill=VERMELL)
    # columnas
    for cx2 in (int(w * .012), int(w * .988)):
        caja_3t(d, (cx2 - 16, 0, cx2 + 16, h), MADERA_O, luz_izq=(cx2 < w / 2))
    img = contacto_suelo(img, 0.09, 120)
    img = sombra_techo(img, 0.07, 96)
    img = ao_esquinas(img, 58)
    img = grano(img, 11, 8)
    img = vineta(img, 50)
    return img


def lateral(semilla, fuji=True):
    w, h = 2395, 864
    img = grad_multi(w, h, [(0, (66, 46, 28)), (0.5, (90, 60, 36)), (1, (56, 38, 24))])
    d = ImageDraw.Draw(img)
    for x in range(0, w, 92):
        d.line([x, 0, x, h], fill=_oscurece(MADERA, .22), width=3)
        _veta_madera(d, (x + 4, 0, x + 88, h), _oscurece(MADERA, .06), x + semilla)
    # 4 paneles shoji con paisaje + pilares entre ellos
    n = 4
    m = int(w * .05)
    pw = (w - m * (n + 1)) // n
    for i in range(n):
        x0 = m + i * (pw + m)
        img = _shoji(img, (x0, int(h * .16), x0 + pw, int(h * .90)), semilla * 10 + i,
                     paisaje=(i % 2 == 0), atardecer=(i % 3 == 1))
    # pilares estructurales
    for i in range(n + 1):
        x = m // 2 + i * (pw + m)
        d = ImageDraw.Draw(img)
        caja_3t(d, (x - 20, 0, x + 20, h), MADERA_O, luz_izq=(i % 2 == 0))
    # andón entre paneles + rama de cerezo que asoma
    img = _andón(img, int(w * .055) + 40, int(h * .30), 1.15, 9)
    img = _cerezo(img, 0, int(h * .18), semilla, s=1.25, hacia_der=True)
    d = ImageDraw.Draw(img)
    # estantería baja con bonsái
    bx = int(w * .78)
    d.rectangle([bx, int(h * .74), bx + 240, int(h * .77)], fill=MADERA_O)
    d.rectangle([bx + 6, int(h * .77), bx + 234, h], fill=_oscurece(MADERA, .3))
    # maceta + bonsái
    d.polygon([(bx + 96, int(h * .66)), (bx + 144, int(h * .66)), (bx + 136, int(h * .74)),
               (bx + 104, int(h * .74))], fill=(60, 40, 34))
    rndb = random.Random(semilla + 3)
    for k in range(9):
        a = rndb.uniform(-math.pi, 0)
        L = rndb.uniform(20, 54)
        x0, y0 = bx + 120, int(h * .66)
        d.line([(x0, y0), (x0 + math.cos(a) * L, y0 + math.sin(a) * L)], fill=(58, 40, 28), width=4)
        px, py = x0 + math.cos(a) * L, y0 + math.sin(a) * L
        d.ellipse([px - 16, py - 12, px + 16, py + 8], fill=(64, 96, 52))
        d.ellipse([px - 9, py - 7, px + 9, py + 5], fill=(84, 118, 66))
    img = contacto_suelo(img, 0.09, 120)
    img = sombra_techo(img, 0.07, 96)
    img = ao_esquinas(img, 58)
    img = grano(img, 11, 8)
    img = vineta(img, 50)
    return img


def suelo():
    w, h = 1296, 1678
    # tatami: trama de paja + bordes de tela oscuros + ensō central
    img = Image.new('RGB', (w, h), (188, 158, 108))
    d = ImageDraw.Draw(img)
    rnd = random.Random(41)
    # media caja de trama (cada tatami 1296×~839: 2 filas)
    th = h // 2
    for fila in range(2):
        y0 = fila * th
        tono = [(196, 166, 114), (182, 152, 102)][fila]
        d.rectangle([4, y0 + 4, w - 4, y0 + th - 4], fill=tono)
        # trama diagonal fina
        for yy in range(y0 + 8, y0 + th - 8, 5):
            desv = math.sin(yy * 0.05) * 3
            d.line([(6 + desv, yy), (w - 6 + desv, yy)], fill=_oscurece(tono, rnd.uniform(0.04, 0.12)), width=2)
        # borde de tela (heri) del tatami
        d.rectangle([4, y0 + th - 26, w - 4, y0 + th - 4], fill=(46, 56, 88) if fila == 0 else (88, 52, 52))
        d.rectangle([4, y0, w - 4, y0 + 22], fill=(46, 56, 88) if fila == 0 else (88, 52, 52))
    # junta central
    d.line([0, th, w, th], fill=(120, 100, 70), width=6)
    # ensō central gigante (el sello del dojo)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(capa)
    _ensyo(cd, w // 2, h // 2, 300, color=(30, 28, 30, 216), wmax=34, abre=0.14)
    capa = capa.filter(ImageFilter.GaussianBlur(1.6))
    img = Image.alpha_composite(img.convert('RGBA'), capa).convert('RGB')
    # desgaste sutil + AO
    img = grano(img, 13, 12)
    img = ao_esquinas(img, 72)
    img = vineta(img, 56)
    return img


def techo():
    w, h = 1296, 1678
    img = grad_multi(w, h, [(0, (52, 36, 22)), (0.5, (76, 52, 32)), (1, (48, 32, 20))], horizontal=True)
    d = ImageDraw.Draw(img)
    _veta_madera(d, (0, 0, w, h), (70, 48, 30), 12)
    # vigas transversales de madera noble
    for i in range(8):
        y = int(h * (0.06 + i * 0.125))
        d.rectangle([0, y - 14, w, y + 14], fill=MADERA_O)
        d.rectangle([0, y - 14, w, y - 6], fill=_aclara(MADERA_O, .22))
        d.rectangle([0, y + 6, w, y + 14], fill=_oscurece(MADERA_O, .3))
    # paneles washi empotrados (luz suave CON ESTRUCTURA — r28: antes el
    # glow los quemaba hasta dejar blobs blancos)
    for i in range(4):
        y = int(h * (0.16 + i * 0.25))
        wx0, wx1 = int(w * .32), int(w * .68)
        d.rectangle([wx0 - 8, y - 52, wx1 + 8, y + 52], fill=MADERA_O)
        washi = grad_multi(wx1 - wx0, 104, [(0, (222, 208, 178)), (1, (198, 180, 148))])
        img.paste(washi, (wx0, y - 52))
        d = ImageDraw.Draw(img)
        # retícula fina del panel
        for k in range(1, 4):
            x = wx0 + (wx1 - wx0) * k // 4
            d.line([x, y - 52, x, y + 52], fill=_oscurece(MADERA, .1), width=2)
        # halo suave alrededor del panel (anillo, no disco)
        from _r28_halls_orbital import _capa_glow_anillo
        img = _capa_glow_anillo(img, ((wx0 + wx1) // 2, y), 64, 26, (255, 214, 160), fuerza=44)
    d = ImageDraw.Draw(img)
    img = grano(img, 11, 8)
    img = vineta(img, 54)
    return img

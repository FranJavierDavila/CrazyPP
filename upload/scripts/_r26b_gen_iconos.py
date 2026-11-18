#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r26b (v3.6.122, FASE 124) — ARTE FINAL de los 3
superpoderes nuevos: insignias CIRCULARES 256×256 (patrón del catálogo),
dibujadas a 2048 y reducidas con Lanczos (antialias real), cuantizadas a
256 colores y optimizadas (mismo tratamiento que los PNG del dueño).

  · SÚPER FÉNIX  — fénix de llamas alzando la bola, oro/naranja sobre noche.
  · SÚPER CRONO  — esfera de reloj con arcos de tiempo y bola con estela.
  · SÚPER HIELO  — cristal de seis puntas, bola en pedestal de hielo.

Salida: scripts/_r26b_assets/icon_fenix.png / icon_crono.png / icon_hielo.png
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math

SAL = Path('/home/z/my-project/upload/scripts/_r26b_assets')
SAL.mkdir(parents=True, exist_ok=True)
S = 2048          # lienzo de trabajo (baja a 256 → AA de 8×)
C = S // 2


def lienzo():
    return Image.new('RGBA', (S, S), (0, 0, 0, 0))


def disco_fondo(img, dentro, fuera, centro=None, radio=None):
    """Disco con degradado radial (máscara L + colores por anillo)."""
    centro = centro or (C, C)
    radio = radio or int(S * 0.485)
    grad = Image.new('L', (S, S), 0)
    dg = ImageDraw.Draw(grad)
    tapa = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    td = ImageDraw.Draw(tapa)
    for r in range(radio, 0, -2):
        t = r / radio
        v = int(255 * (1 - t))
        dg.ellipse([centro[0] - r, centro[1] - r, centro[0] + r, centro[1] + r], fill=v)
        col = (int(fuera[0] + (dentro[0] - fuera[0]) * (1 - t)),
               int(fuera[1] + (dentro[1] - fuera[1]) * (1 - t)),
               int(fuera[2] + (dentro[2] - fuera[2]) * (1 - t)), 255)
        td.ellipse([centro[0] - r, centro[1] - r, centro[0] + r, centro[1] + r], fill=col)
    grad = grad.filter(ImageFilter.GaussianBlur(6))
    tapa.putalpha(grad)
    img.alpha_composite(tapa)
    return img


def anillos(img, color_ext, color_int, grosor_ext=44, grosor_int=12):
    d = ImageDraw.Draw(img)
    r = int(S * 0.462)
    d.ellipse([C - r, C - r, C + r, C + r], outline=color_ext, width=grosor_ext)
    r2 = int(S * 0.412)
    d.ellipse([C - r2, C - r2, C + r2, C + r2], outline=color_int, width=grosor_int)
    return img


def estrella(d, x, y, r, col):
    """Destello de 4 puntas (brillo premium)."""
    d.line([x - r, y, x + r, y], fill=col, width=max(2, r // 5))
    d.line([x, y - r, x, y + r], fill=col, width=max(2, r // 5))
    d.line([x - r // 2, y - r // 2, x + r // 2, y + r // 2], fill=col, width=max(2, r // 8))
    d.line([x - r // 2, y + r // 2, x + r // 2, y - r // 2], fill=col, width=max(2, r // 8))
    d.ellipse([x - r // 3, y - r // 3, x + r // 3, y + r // 3], fill=col)


def bola_pp(d, x, y, r, halo=None):
    """La bola de ping-pong con corona SÓLIDA escalonada (ImageDraw no
    compone: los alfa parciales oscurecen — lección r26b)."""
    for rr, cc in ((int(r * 2.0), (96, 74, 40, 255)),
                   (int(r * 1.66), (128, 98, 52, 255)),
                   (int(r * 1.38), (168, 128, 66, 255)),
                   (int(r * 1.16), (214, 164, 88, 255))):
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=cc)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 238, 255),
              outline=(210, 200, 180, 255), width=max(3, r // 12))
    d.arc([x - r, y - r, x + r, y + r], 110, 250, fill=(198, 188, 168, 255),
          width=max(2, r // 10))


def llama(d, punta, base_w, alto, curva, col_a, col_b, capas=4):
    """Lengua de llama curvada por capas (de fuera a dentro)."""
    x0, y0 = punta
    for i in range(capas, 0, -1):
        f = i / capas
        w = base_w * f
        h = alto * (0.6 + 0.4 * f)
        col = tuple(int(col_a[k] + (col_b[k] - col_a[k]) * (1 - f)) for k in range(3)) + (255,)
        pts = []
        n = 22
        for j in range(n + 1):
            t = j / n
            px = x0 + curva * t * t - w * math.sin(t * math.pi)
            py = y0 + h * t
            pts.append((px, py))
        for j in range(n, -1, -1):
            t = j / n
            px = x0 + curva * t * t + w * math.sin(t * math.pi)
            py = y0 + h * t
            pts.append((px, py))
        d.polygon(pts, fill=col)


# ── 1 · SÚPER FÉNIX ────────────────────────────────────────────────────
def fenix():
    img = lienzo()
    disco_fondo(img, (24, 40, 78), (6, 10, 22))
    d = ImageDraw.Draw(img)
    # resplandor nocturno tras el ave
    glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([C - 520, C - 620, C + 520, C + 420], fill=(255, 120, 30, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    # cola: tres lenguas descendentes
    for dx, cur, alt in ((-150, -260, 420), (0, -80, 520), (150, 240, 420)):
        llama(d, (C + dx - 60, C + 120), 74, alt, cur, (255, 122, 26), (255, 214, 120))
    # alas: arcos de llamas a los lados
    for lado in (-1, 1):
        for k in range(4):
            off = k * 95
            llama(d, (C + lado * (180 + off), C - 260 + k * 60),
                  52 - k * 8, 330 - k * 40, lado * (90 - k * 16),
                  (255, 92, 20), (255, 196, 96))
    # cuerpo: llama central ascendente
    llama(d, (C - 40, C - 560), 120, 640, 30, (255, 70, 12), (255, 240, 190))
    llama(d, (C + 40, C - 420), 96, 500, -24, (255, 110, 30), (255, 224, 150))
    # cresta
    for dx in (-120, 0, 120):
        llama(d, (C + dx - 30, C - 620), 40, 150, dx // 3, (255, 190, 60), (255, 250, 220))
    # LA BOLA: caliente, centro del poder (corona dorada sólida escalonada)
    for rr, cc in ((300, (150, 100, 46, 255)), (250, (178, 120, 54, 255)),
                   (205, (206, 144, 66, 255)), (168, (236, 176, 88, 255))):
        d.ellipse([C + 40 - rr, C + 40 - rr, C + 40 + rr, C + 40 + rr], fill=cc)
    d.ellipse([C + 40 - 132, C + 40 - 132, C + 40 + 132, C + 40 + 132],
              fill=(255, 250, 238, 255), outline=(255, 214, 140, 255), width=14)
    d.arc([C + 40 - 106, C + 40 - 106, C + 40 + 106, C + 40 + 106], 110, 250,
          fill=(214, 186, 138, 255), width=9)
    d = ImageDraw.Draw(img)
    # chispas doradas
    for (sx, sy, sr) in ((C - 560, C - 160, 26), (C + 570, C - 220, 30),
                         (C - 420, C + 400, 20), (C + 460, C + 430, 24),
                         (C - 120, C - 700, 22), (C + 190, C - 660, 18)):
        estrella(d, sx, sy, sr, (255, 226, 150, 255))
    anillos(img, (232, 180, 90, 255), (255, 214, 140, 255))
    return img


# ── 2 · SÚPER CRONO ────────────────────────────────────────────────────
def crono():
    img = lienzo()
    disco_fondo(img, (36, 30, 88), (11, 8, 32))
    d = ImageDraw.Draw(img)
    # arcos de tiempo (cian) — barrido horario, dash grueso
    for r, a0, a1, w in ((int(S * 0.395), -60, 150, 26),
                         (int(S * 0.345), 120, 300, 20),
                         (int(S * 0.30), -160, -10, 14)):
        d.arc([C - r, C - r, C + r, C + r], a0, a1, fill=(125, 227, 255, 220), width=w)
        # cabeza luminosa del arco
        ang = math.radians(a1)
        hx, hy = C + r * math.cos(ang), C + r * math.sin(ang)
        d.ellipse([hx - 22, hy - 22, hx + 22, hy + 22], fill=(190, 244, 255, 255))
    # esfera del reloj
    rf = int(S * 0.262)
    d.ellipse([C - rf, C - rf, C + rf, C + rf], fill=(16, 13, 46, 235),
              outline=(201, 204, 212, 255), width=22)
    # 12 marcas (oras cardinales en oro)
    for h in range(12):
        ang = math.radians(h * 30 - 90)
        x1 = C + (rf - 46) * math.cos(ang)
        y1 = C + (rf - 46) * math.sin(ang)
        x2 = C + (rf - 14) * math.cos(ang)
        y2 = C + (rf - 14) * math.sin(ang)
        col = (255, 210, 87, 255) if h % 3 == 0 else (150, 158, 176, 255)
        wdt = 16 if h % 3 == 0 else 9
        d.line([x1, y1, x2, y2], fill=col, width=wdt)
    # agujas a las 10:10 (plata) + contrapeso
    for ang_deg, largo, w, col in ((-145, rf - 96, 20, (222, 228, 240, 255)),
                                   (-45, rf - 60, 15, (222, 228, 240, 255))):
        ang = math.radians(ang_deg)
        d.line([C, C, C + largo * math.cos(ang), C + largo * math.sin(ang)],
               fill=col, width=w)
    d.ellipse([C - 26, C - 26, C + 26, C + 26], fill=(255, 210, 87, 255),
              outline=(120, 90, 30, 255), width=6)
    # LA BOLA cruzando con estela de tiempo (solid: reemplazo seguro)
    for k, cc in enumerate(((32, 88, 116, 255), (44, 116, 150, 255),
                            (60, 150, 190, 255), (94, 200, 236, 255))):
        tx, ty = C + 330 - k * 74, C + 250 - k * 62
        d.ellipse([tx - 34 + k * 8, ty - 16, tx + 34 + k * 8, ty + 16], fill=cc)
    bola_pp(d, C + 380, C + 290, 96)
    d = ImageDraw.Draw(img)
    # estrellas + arena dorada del tiempo
    for (sx, sy, sr) in ((C - 540, C + 190, 24), (C + 520, C - 260, 28),
                         (C - 300, C - 520, 20), (C + 300, C + 540, 22)):
        estrella(d, sx, sy, sr, (190, 240, 255, 255))
    anillos(img, (201, 204, 212, 255), (125, 227, 255, 255))
    return img


# ── 3 · SÚPER HIELO ────────────────────────────────────────────────────
def hielo():
    img = lienzo()
    disco_fondo(img, (22, 62, 108), (7, 20, 38))
    d = ImageDraw.Draw(img)
    # aurora polar de fondo
    aur = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aur)
    ad.ellipse([C - 640, C - 520, C + 640, C + 200], fill=(90, 200, 255, 70))
    aur = aur.filter(ImageFilter.GaussianBlur(130))
    img.alpha_composite(aur)
    d = ImageDraw.Draw(img)
    # cristal de 6 puntas con ramificaciones
    r_main = int(S * 0.335)
    for h in range(6):
        ang = math.radians(h * 60 - 90)
        ca, sa = math.cos(ang), math.sin(ang)
        x2, y2 = C + r_main * ca, C + r_main * sa
        d.line([C, C, x2, y2], fill=(214, 240, 255, 255), width=34)
        d.line([C, C, x2, y2], fill=(255, 255, 255, 255), width=14)
        # ramas laterales a 38 % y 68 % del brazo
        for f, lr in ((0.38, 0.30), (0.68, 0.22)):
            bx, by = C + r_main * f * ca, C + r_main * f * sa
            for sgn in (-1, 1):
                a2 = ang + sgn * math.radians(38)
                d.line([bx, by, bx + r_main * lr * math.cos(a2),
                        by + r_main * lr * math.sin(a2)],
                       fill=(168, 220, 250, 255), width=20)
        # punta brillante
        d.ellipse([x2 - 26, y2 - 26, x2 + 26, y2 + 26], fill=(240, 252, 255, 255))
    # hexágono central helado + LA BOLA sobre pedestal
    rh = int(S * 0.135)
    d.polygon([(C + rh * math.cos(math.radians(-90 + 60 * i)),
                C + rh * math.sin(math.radians(-90 + 60 * i))) for i in range(6)],
              fill=(9, 30, 56, 255), outline=(168, 220, 250, 255), width=16)
    # pedestal de hielo bajo la bola
    d.polygon([(C - 110, C + 208), (C + 110, C + 208), (C + 66, C + 320),
               (C - 66, C + 320)], fill=(150, 205, 240, 255),
              outline=(220, 244, 255, 255), width=8)
    d.line([C - 84, C + 238, C + 84, C + 238], fill=(226, 246, 255, 255), width=10)
    bola_pp(d, C, C + 40, 120)
    d = ImageDraw.Draw(img)
    # copos y escarcha
    for (sx, sy, sr) in ((C - 520, C - 300, 30), (C + 530, C - 180, 34),
                         (C - 380, C + 460, 24), (C + 420, C + 470, 26),
                         (C - 160, C - 620, 22), (C + 240, C - 600, 20)):
        for h in range(6):
            ang = math.radians(h * 60)
            d.line([sx - sr * math.cos(ang), sy - sr * math.sin(ang),
                    sx + sr * math.cos(ang), sy + sr * math.sin(ang)],
                   fill=(226, 246, 255, 255), width=max(3, sr // 5))
    anillos(img, (191, 224, 245, 255), (140, 200, 240, 255))
    return img


def exportar(img, nombre):
    """Reducción 2048→256 + cuantización 256 colores (tratamiento del dueño)."""
    small = img.resize((256, 256), Image.LANCZOS)
    fondo = Image.new('RGB', small.size, (12, 16, 28))
    fondo.paste(small, (0, 0), small)
    p = fondo.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    p.save(SAL / nombre, optimize=True)
    kb = (SAL / nombre).stat().st_size / 1024
    print(f'  ✓ {nombre}: {kb:.1f} KB')


print('— insignias r26b (256×256, 256 colores)…')
exportar(fenix(), 'icon_fenix.png')
exportar(crono(), 'icon_crono.png')
exportar(hielo(), 'icon_hielo.png')
print('listo.')

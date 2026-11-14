#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mockup_vestibulo.py — Mockups pixelados del rediseño «VESTÍBULO» (FASE 161).
Estilo calcado de la referencia del dueño (Menú de ping-pong futurista sin
texto.png): chasis azul metálico con brillo cian, botones caramelo glossy con
medallón circular de icono blanco, héroe verde a toda fila, cabecera con
pala+bola y banderas ES/EN.
Salida (3 PNG en download/):
  1. mockup1_vestibulo_arco.png     — vista VR completa (3 paneles + dock)
  2. mockup2_panel_jugar_closeup.png— primer plano del panel central
  3. mockup3_pantalla_campeonatos.png— pantalla de sección con pestañas
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
OUT = '/home/z/my-project/download/'

NAVY_D = (6, 13, 31, 255)        # chasis profundo
NAVY = (13, 27, 61, 255)         # chasis
CYAN = (53, 196, 255, 255)       # brillo de bordes
TXT_SUB = (205, 226, 255, 255)

# (nombre, color claro, color oscuro, aro oscuro, glow)
C_HERO = ((74, 240, 94), (24, 158, 44), (8, 60, 22), (88, 255, 110))
C_MAG = ((255, 74, 214), (198, 8, 152), (74, 4, 58), (255, 96, 222))
C_AMB = ((255, 186, 42), (226, 124, 0), (84, 44, 0), (255, 200, 70))
C_BLU = ((58, 172, 255), (12, 96, 214), (4, 40, 88), (80, 190, 255))
C_FIR = ((255, 96, 38), (208, 44, 0), (78, 12, 0), (255, 130, 70))
C_VIO = ((186, 88, 255), (122, 31, 208), (46, 6, 78), (200, 120, 255))
C_TRP = ((255, 202, 30), (216, 140, 0), (80, 48, 0), (255, 215, 80))
C_TEA = ((30, 216, 204), (10, 136, 146), (0, 56, 62), (70, 235, 220))
C_STL = ((150, 168, 194), (88, 104, 132), (30, 40, 56), (170, 190, 215))
C_WID = ((26, 190, 178), (13, 122, 138), (0, 48, 56), (255, 190, 30))


def fnt(sz):
    return ImageFont.truetype(FONT_B, sz)


def vgrad(w, h, top, bot):
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    a = np.array(top, float)[None, None, :3]
    b = np.array(bot, float)[None, None, :3]
    arr = (a + (b - a) * t).astype(np.uint8)
    arr = np.repeat(arr, w, axis=1)
    alpha = np.full((h, w, 1), 255, np.uint8)
    return Image.fromarray(np.concatenate([arr, alpha], axis=2), 'RGBA')


def rrect_mask(w, h, r):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return m


def candy_button(im, xy, wh, colors, radius=46, ring=10, glow_a=110):
    """Botón caramelo: glow exterior + aro oscuro + gradiente + brillo glass."""
    x, y = xy
    w, h = wh
    hi, lo, ring_c, glow_c = colors
    base = im
    # glow exterior
    gl = Image.new('RGBA', base.size, (0, 0, 0, 0))
    gm = rrect_mask(w, h, radius)
    gl.paste(Image.new('RGBA', (w, h), glow_c[:3] + (glow_a,)), (x, y), gm)
    gl = gl.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(gl)
    # cuerpo
    body = vgrad(w, h, hi, lo)
    body.putalpha(rrect_mask(w, h, radius))
    base.alpha_composite(body, (x, y))
    d = ImageDraw.Draw(base)
    # aro oscuro
    d.rounded_rectangle([x, y, x + w, y + h], radius,
                        outline=ring_c[:3] + (255,), width=ring)
    # línea de luz inferior-derecha (borde interno claro)
    d.rounded_rectangle([x + ring, y + ring, x + w - ring, y + h - ring],
                        radius - ring // 2,
                        outline=(255, 255, 255, 60), width=2)
    # sheen de cristal (mitad superior)
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([ring * 2, ring * 2, w - ring * 2,
                          int(h * 0.52)], radius - ring, fill=(255, 255, 255, 52))
    ds.ellipse([int(w * 0.06), -int(h * 0.18), int(w * 0.94),
                int(h * 0.42)], fill=(255, 255, 255, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.putalpha(sh.split()[3].point(lambda v: int(v * 0.9)))
    m2 = rrect_mask(w, h, radius)
    sh.putalpha(Image.composite(sh.split()[3], Image.new('L', (w, h), 0), m2))
    base.alpha_composite(sh, (x, y))
    # destello diagonal
    st = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dst = ImageDraw.Draw(st)
    dst.polygon([(int(w * 0.52), ring * 2), (int(w * 0.70), ring * 2),
                 (int(w * 0.40), h), (int(w * 0.28), h)],
                fill=(255, 255, 255, 26))
    st.putalpha(Image.composite(st.split()[3], Image.new('L', (w, h), 0), m2))
    base.alpha_composite(st, (x, y))


def medallion(im, cx, cy, r, glyph):
    """Medallón circular oscuro con icono blanco (como la referencia)."""
    d = ImageDraw.Draw(im)
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - r, cy - r, cx + r, cy + r],
                                 fill=(255, 255, 255, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(glow)
    # aro exterior claro + disco oscuro con gradiente radial simulado
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 16, 34, 255),
              outline=(235, 242, 255, 255), width=5)
    inner = Image.new('RGBA', (2 * r, 2 * r), (0, 0, 0, 0))
    di = ImageDraw.Draw(inner)
    di.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=(40, 58, 96, 255))
    di.ellipse([int(r * 0.3), int(r * 0.3), int(2 * r - r * 0.1),
                int(2 * r - r * 0.1)], fill=(22, 34, 62, 255))
    mm = Image.new('L', (2 * r, 2 * r), 0)
    ImageDraw.Draw(mm).ellipse([2, 2, 2 * r - 3, 2 * r - 3], fill=255)
    im.paste(inner, (cx - r, cy - r), mm)
    W = (255, 255, 255, 255)
    lw = max(4, r // 5)
    # — glifos vectoriales —
    if glyph == 'play':
        s = r * 0.52
        d.polygon([(cx - s * 0.7, cy - s), (cx - s * 0.7, cy + s),
                   (cx + s * 1.05, cy)], fill=W)
    elif glyph == 'ladder':
        x0, x1, hgt = cx - r * 0.42, cx + r * 0.42, r * 0.72
        d.line([x0, cy - hgt, x0, cy + hgt], fill=W, width=lw)
        d.line([x1, cy - hgt, x1, cy + hgt], fill=W, width=lw)
        for i in range(4):
            yy = cy - hgt + (2 * hgt) * i / 3
            d.line([x0, yy, x1, yy], fill=W, width=lw)
    elif glyph == 'cap':
        w2, h2 = r * 0.95, r * 0.52
        d.polygon([(cx, cy - h2), (cx + w2, cy - h2 * 0.25), (cx, cy + h2 * 0.4),
                   (cx - w2, cy - h2 * 0.25)], fill=W)
        d.arc([cx - w2 * 0.5, cy - h2 * 0.1, cx + w2 * 0.5, cy + h2 * 1.3],
              20, 160, fill=W, width=lw)
        d.line([cx + w2 * 0.78, cy - h2 * 0.28, cx + w2 * 0.78, cy + r * 0.45],
               fill=W, width=max(3, lw // 2))
        d.ellipse([cx + w2 * 0.78 - 6, cy + r * 0.45, cx + w2 * 0.78 + 6,
                   cy + r * 0.45 + 12], fill=W)
    elif glyph == 'target':
        rr_ = r * 0.62
        d.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], outline=W, width=lw)
        rr2 = r * 0.3
        d.ellipse([cx - rr2, cy - rr2, cx + rr2, cy + rr2], outline=W, width=lw)
        for a, b in [((cx - r * 0.85, cy), (cx - rr_, cy)),
                     ((cx + rr_, cy), (cx + r * 0.85, cy)),
                     ((cx, cy - r * 0.85), (cx, cy - rr_)),
                     ((cx, cy + rr_), (cx, cy + r * 0.85))]:
            d.line([a, b], fill=W, width=max(3, lw - 1))
    elif glyph == 'flame':
        s = r * 0.78
        d.polygon([(cx, cy - s), (cx + s * 0.55, cy + s * 0.15),
                   (cx + s * 0.34, cy + s * 0.62), (cx, cy + s * 0.78),
                   (cx - s * 0.34, cy + s * 0.62),
                   (cx - s * 0.55, cy + s * 0.15)], fill=W)
        d.ellipse([cx - s * 0.26, cy + s * 0.18, cx + s * 0.26,
                   cy + s * 0.66], fill=(255, 150, 40, 255))
    elif glyph == 'swords':
        s = r * 0.72
        for dx in (-1, 1):
            d.line([cx - dx * s * 0.62, cy - s * 0.62, cx + dx * s * 0.62,
                    cy + s * 0.62], fill=W, width=lw)
            d.line([cx + dx * s * 0.62 - dx * 12, cy + s * 0.62 - 12,
                    cx + dx * s * 0.62 + dx * 12, cy + s * 0.62 + 12],
                   fill=W, width=max(3, lw - 1))
            d.line([cx - dx * s * 0.30, cy + s * 0.12, cx - dx * s * 0.05,
                    cy + s * 0.37], fill=W, width=max(3, lw - 1))
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=W)
    elif glyph == 'trophy':
        w2 = r * 0.6
        d.rounded_rectangle([cx - w2, cy - r * 0.72, cx + w2, cy + r * 0.1],
                            r // 4, fill=W)
        d.arc([cx - w2 - r * 0.4, cy - r * 0.7, cx - w2 + r * 0.25,
               cy + r * 0.05], 90, 300, fill=W, width=max(3, lw - 1))
        d.arc([cx + w2 - r * 0.25, cy - r * 0.7, cx + w2 + r * 0.4,
               cy + r * 0.05], 240, 90, fill=W, width=max(3, lw - 1))
        d.line([cx, cy + r * 0.1, cx, cy + r * 0.42], fill=W, width=lw)
        d.rounded_rectangle([cx - r * 0.5, cy + r * 0.42, cx + r * 0.5,
                             cy + r * 0.58], 8, fill=W)
    elif glyph == 'globe':
        rr_ = r * 0.68
        d.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], outline=W, width=lw)
        d.ellipse([cx - rr_ * 0.42, cy - rr_, cx + rr_ * 0.42, cy + rr_],
                  outline=W, width=max(3, lw - 2))
        d.line([cx - rr_, cy, cx + rr_, cy], fill=W, width=max(3, lw - 2))
        d.arc([cx - rr_, cy - rr_ * 1.5, cx + rr_, cy - rr_ * 0.1], 25, 155,
              fill=W, width=max(3, lw - 2))
        d.arc([cx - rr_, cy + rr_ * 0.1, cx + rr_, cy + rr_ * 1.5], 205, 335,
              fill=W, width=max(3, lw - 2))
    elif glyph == 'gear':
        rr_ = r * 0.52
        for i in range(8):
            ang = i * np.pi / 4
            x0 = cx + np.cos(ang) * rr_ * 0.85
            y0 = cy + np.sin(ang) * rr_ * 0.85
            x1 = cx + np.cos(ang) * rr_ * 1.28
            y1 = cy + np.sin(ang) * rr_ * 1.28
            d.line([x0, y0, x1, y1], fill=W, width=int(lw * 1.5))
        d.ellipse([cx - rr_, cy - rr_, cx + rr_, cy + rr_], fill=W)
        hole = r * 0.22
        d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole],
                  fill=(22, 34, 62, 255))
    elif glyph == 'house':
        s = r * 0.85
        d.polygon([(cx, cy - s * 0.85), (cx + s, cy + s * 0.05),
                   (cx - s, cy + s * 0.05)], fill=W)
        d.rectangle([cx - s * 0.62, cy + s * 0.05, cx + s * 0.62,
                     cy + s * 0.8], fill=W)
        d.rectangle([cx - s * 0.16, cy + s * 0.28, cx + s * 0.16,
                     cy + s * 0.8], fill=(22, 34, 62, 255))
    elif glyph == 'star':
        s = r * 0.8
        pts = []
        for i in range(10):
            ang = -np.pi / 2 + i * np.pi / 5
            rad = s if i % 2 == 0 else s * 0.45
            pts.append((cx + np.cos(ang) * rad, cy + np.sin(ang) * rad))
        d.polygon(pts, fill=W)
    elif glyph == 'flag_es':
        d.ellipse([cx - r, cy - r * 0.68, cx + r, cy + r * 0.68],
                  fill=(196, 8, 24, 255))
        d.rectangle([cx - r, cy - r * 0.34, cx + r, cy + r * 0.34],
                    fill=(255, 196, 0, 255))
        d.ellipse([cx - r * 0.3, cy - r * 0.18, cx + r * 0.3, cy + r * 0.18],
                  outline=(150, 40, 40, 255), width=3)
    elif glyph == 'flag_uk':
        d.ellipse([cx - r, cy - r * 0.68, cx + r, cy + r * 0.68],
                  fill=(10, 42, 110, 255))
        d.rectangle([cx - r, cy - r * 0.12, cx + r, cy + r * 0.12],
                    fill=(230, 230, 230, 255))
        d.rectangle([cx - r * 0.16, cy - r * 0.68, cx + r * 0.16,
                     cy + r * 0.68], fill=(230, 230, 230, 255))
        d.rectangle([cx - r, cy - r * 0.06, cx + r, cy + r * 0.06],
                    fill=(200, 16, 30, 255))
        d.rectangle([cx - r * 0.08, cy - r * 0.68, cx + r * 0.08,
                     cy + r * 0.68], fill=(200, 16, 30, 255))
    elif glyph == 'tv':
        d.rounded_rectangle([cx - r * 0.75, cy - r * 0.5, cx + r * 0.75,
                             cy + r * 0.5], 10, outline=W, width=lw)
        d.line([cx - r * 0.3, cy - r * 0.5, cx - r * 0.6, cy - r * 0.85],
               fill=W, width=max(3, lw - 1))
        d.line([cx + r * 0.3, cy - r * 0.5, cx + r * 0.6, cy - r * 0.85],
               fill=W, width=max(3, lw - 1))
    elif glyph == 'door':
        d.rounded_rectangle([cx - r * 0.5, cy - r * 0.8, cx + r * 0.5,
                             cy + r * 0.8], 12, outline=W, width=lw)
        d.ellipse([cx + r * 0.12, cy - 6, cx + r * 0.3, cy + 12], fill=W)
    elif glyph == 'back':
        s = r * 0.7
        d.line([cx + s * 0.5, cy - s, cx - s * 0.5, cy], fill=W, width=lw * 2)
        d.line([cx - s * 0.5, cy, cx + s * 0.5, cy + s], fill=W, width=lw * 2)
    return


def panel(im, xy, wh, title, radius=44):
    """Panel de cristal oscuro con borde cian y title-bar."""
    x, y = xy
    w, h = wh
    gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle([x, y, x + w, y + h], radius,
                                         fill=(40, 130, 255, 60))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))
    body = vgrad(w, h, (16, 28, 62, 242), (8, 14, 36, 246))
    body.putalpha(rrect_mask(w, h, radius))
    im.alpha_composite(body, (x, y))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + w, y + h], radius,
                        outline=(90, 190, 255, 200), width=4)
    d.rounded_rectangle([x + 6, y + 6, x + w - 6, y + h - 6], radius - 6,
                        outline=(255, 255, 255, 36), width=2)
    d.line([x + 18, y + 14, x + w * 0.42, y + 14], fill=(120, 215, 255, 150),
           width=3)
    d.line([x + w - 18, y + h - 14, x + w * 0.6, y + h - 14],
           fill=(120, 215, 255, 110), width=3)
    if title:
        d.text((x + 30, y + 18), title, font=fnt(44),
               fill=(255, 255, 255, 255))
        d.line([x + 30, y + 78, x + w - 30, y + 78],
               fill=(255, 255, 255, 40), width=2)


def fit_text(d, xy, text, size, maxw, fill, anchor='lm'):
    """Escribe el texto reduciendo la fuente hasta caber en maxw."""
    s = size
    while s > 16 and d.textlength(text, font=fnt(s)) > maxw:
        s -= 2
    d.text(xy, text, font=fnt(s), fill=fill, anchor=anchor)


def mode_card(im, xy, wh, colors, glyph, title, sub, r=40):
    x, y = xy
    w, h = wh
    candy_button(im, xy, wh, colors, radius=r)
    d = ImageDraw.Draw(im)
    mr = 52 if w >= 560 else 44
    if h < 110:
        mr = max(26, (h - 16) // 2)
    mx = x + 64 + (20 if w >= 560 else 0)
    medallion(im, mx, y + h // 2, mr, glyph)
    tx = mx + mr + 26
    tsize = 46 if w >= 900 else (44 if w >= 560 else 36)
    ssize = 28 if w >= 560 else 24
    maxw = x + w - tx - 26
    fit_text(d, (tx, y + (h * 0.32 if sub else h * 0.5)), title, tsize, maxw,
             (255, 255, 255, 255))
    if sub:
        fit_text(d, (tx, y + h * 0.66), sub, ssize, maxw, TXT_SUB)


def dock_button(im, cx, cy, r, colors, glyph):
    candy_button(im, (cx - r, cy - r), (2 * r, 2 * r), colors, radius=r,
                 ring=7, glow_a=80)
    medallion(im, cx, cy, int(r * 0.62), glyph)


def header(im, x, y, w, h):
    """Cabecera estilo referencia: banda azul glossy + pala/bola + banderas."""
    candy_button(im, (x, y), (w, h), ((44, 130, 255), (8, 60, 190),
                                      (2, 26, 80), (90, 190, 255)), radius=40)
    d = ImageDraw.Draw(im)
    # remolino
    for i in range(3):
        d.arc([x + 40 + i * 24, y + 18 + i * 10, x + 430 - i * 10,
               y + h + 40 - i * 22], 200, 340, fill=(150, 220, 255, 90 - i * 25),
              width=8)
    # pala roja + bola blanca (dentro de la banda)
    d.rounded_rectangle([x + 196, y + h - 26, x + 224, y + h - 4], 8,
                        fill=(180, 120, 60, 255))
    d.ellipse([x + 148, y + 22, x + 252, y + h - 22], fill=(220, 30, 30, 255),
              outline=(140, 10, 10, 255), width=5)
    d.ellipse([x + 168, y + 36, x + 228, y + h - 38],
              outline=(255, 140, 140, 160), width=4)
    d.ellipse([x + 262, y + 40, x + 310, y + 88], fill=(250, 250, 255, 255),
              outline=(160, 180, 220, 255), width=4)
    # banderas
    medallion(im, x + w - 150, y + h // 2, 52, 'flag_es')
    medallion(im, x + w - 60, y + h // 2, 52, 'flag_uk')


def chassis(im, xy, wh, radius=56):
    x, y = xy
    w, h = wh
    body = vgrad(w, h, (26, 44, 96, 255), (8, 16, 40, 255))
    body.putalpha(rrect_mask(w, h, radius))
    im.alpha_composite(body, (x, y))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + w, y + h], radius,
                        outline=(30, 80, 180, 255), width=8)
    d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h - 10], radius - 8,
                        outline=(70, 170, 255, 120), width=3)
    d.rounded_rectangle([x + 26, y + 26, x + w - 26, y + h - 26], radius - 16,
                        outline=(0, 0, 0, 160), width=6)


def save(im, name):
    im.convert('RGB').save(OUT + name, 'PNG', optimize=True)
    print(name, im.size)


# ————————— MOCKUP 1 · VESTÍBULO COMPLETO (vista VR) —————————
im = Image.new('RGBA', (2560, 1440), (5, 8, 18, 255))
d = ImageDraw.Draw(im)
for i in range(70):   # fondo: pista tenue
    d.ellipse([1200 - 900 + i * 26, 1180 + (i % 3) * 6,
               1360 - 900 + i * 26, 1200 + (i % 3) * 6],
              fill=(20, 40, 70, 40))
chassis(im, (60, 40), (2440, 1300))

header(im, 880, 70, 800, 130)

# — panel central JUGAR —
panel(im, (860, 230, ), (840, 950), 'JUGAR')
candy_button(im, (890, 340), (780, 190), C_HERO, radius=48)
medallion(im, 990, 435, 72, 'play')
d = ImageDraw.Draw(im)
d.text((1090, 404), 'PARTIDO', font=fnt(80), fill=(255, 255, 255, 255))
d.text((1090, 486), 'vs CPU · Fácil', font=fnt(36), fill=(230, 255, 230, 255))
mode_card(im, (890, 560), (780, 230), C_MAG, 'ladder', 'CARRERA',
          'División 2 · 3/5 rivales')
mode_card(im, (890, 820), (380, 230), C_BLU, 'target', 'ENTRENAR', None)
mode_card(im, (1290, 820), (380, 230), C_FIR, 'flame', 'SUPERVIVENCIA',
          'Racha: 12')
mode_card(im, (890, 1080), (780, 70), ((60, 74, 98), (36, 46, 66),
                                       (10, 16, 30), (150, 170, 200)),
          'house', 'EL VESTÍBULO', None, r=34)

# — panel izquierdo COMPITE —
panel(im, (140, 230), (660, 950), 'COMPITE')
mode_card(im, (175, 340), (590, 240), C_VIO, 'swords', 'MULTIJUGADOR',
          'Online P2P · 2 conectados')
mode_card(im, (175, 620), (590, 240), C_TRP, 'trophy', 'CAMPEONATOS',
          'Locura · Magia · Oeste')
mode_card(im, (175, 900), (590, 240), C_TEA, 'globe', 'RANKING MUNDIAL',
          'Top 10 mundial')

# — panel derecho TU CASA —
panel(im, (1760, 230), (660, 950), 'TU CASA')
mode_card(im, (1795, 340), (590, 240), ((232, 162, 42), (140, 106, 20),
                                        (60, 42, 4), (255, 200, 70)),
          'door', 'SALA ARCANA', 'Poderes · pieles · logros')
mode_card(im, (1795, 620), (590, 240), C_AMB, 'cap', 'ACADEMIA',
          'Aprende en 5 lecciones')
mode_card(im, (1795, 900), (590, 240), C_STL, 'gear', 'AJUSTES',
          'Juego · Audio · Pala')

# — dock inferior —
dy = 1245
dock = Image.new('RGBA', (1900, 170), (0, 0, 0, 0))
dock.putalpha(rrect_mask(1900, 170, 60))
body = vgrad(1900, 170, (20, 34, 74, 235), (10, 18, 44, 240))
body.putalpha(Image.composite(body.split()[3],
                              Image.new('L', (1900, 170), 0),
                              rrect_mask(1900, 170, 60)))
im.alpha_composite(body, (330, dy - 30))
ImageDraw.Draw(im).rounded_rectangle([330, dy - 30, 2230, dy + 140], 60,
                                     outline=(90, 190, 255, 160), width=4)
labels = [('gear', 'Ajustes', C_STL), ('tv', 'TV en vivo', C_BLU),
          ('star', 'Intro', C_AMB), ('door', 'Instalar', C_TEA),
          ('trophy', 'Apoyar', C_TRP), ('back', 'Salir', ((90, 100, 120),
                                                          (50, 58, 76),
                                                          (12, 18, 30),
                                                          (150, 160, 180)))]
for i, (g, lab, col) in enumerate(labels):
    cx = 430 + i * 300
    dock_button(im, cx, dy + 40, 52, col, g)
    d.text((cx, dy + 118), lab, font=fnt(26), fill=TXT_SUB, anchor='mm')
save(im, 'mockup1_vestibulo_arco.png')

# ————————— MOCKUP 2 · PANEL CENTRAL EN PRIMER PLANO —————————
im2 = Image.new('RGBA', (1280, 1810), (5, 8, 18, 255))
chassis(im2, (24, 24), (1232, 1766))
header(im2, 64, 64, 1152, 140)
panel(im2, (64, 250), (1152, 1470), 'JUGAR')
candy_button(im2, (104, 370), (1072, 240), C_HERO, radius=54)
medallion(im2, 240, 490, 92, 'play')
d = ImageDraw.Draw(im2)
d.text((400, 432), 'PARTIDO', font=fnt(104), fill=(255, 255, 255, 255))
d.text((400, 576), 'vs CPU · Fácil', font=fnt(46), fill=(230, 255, 230, 255))
mode_card(im2, (104, 650), (1072, 300), C_MAG, 'ladder', 'CARRERA',
          'División 2 · 3/5 rivales vencidos', r=46)
medallion(im2, 1120, 800, 46, 'star')
mode_card(im2, (104, 990), (516, 300), C_BLU, 'target', 'ENTRENAR',
          'PRO TRAINING', r=46)
mode_card(im2, (660, 990), (516, 300), C_FIR, 'flame', 'SUPERVIVENCIA',
          'Racha: 12', r=46)
mode_card(im2, (104, 1330), (1072, 130), ((60, 74, 98), (36, 46, 66),
                                          (10, 16, 30), (150, 170, 200)),
          'house', 'EL VESTÍBULO · tu habitación', None, r=36)
d.text((104, 1520), 'El vestíbulo guarda tus colecciones: Sala Arcana,',
       font=fnt(34), fill=TXT_SUB)
d.text((104, 1570), 'pieles, logros y medallas.', font=fnt(34), fill=TXT_SUB)
save(im2, 'mockup2_panel_jugar_closeup.png')

# ————————— MOCKUP 3 · PANTALLA DE SECCIÓN (CAMPEONATOS) —————————
im3 = Image.new('RGBA', (1280, 1810), (5, 8, 18, 255))
chassis(im3, (24, 24), (1232, 1766))
# cabecera de sección con Volver
candy_button(im3, (64, 64), (1152, 170), ((30, 110, 235), (10, 55, 150),
                                          (2, 26, 80), (90, 190, 255)),
             radius=44)
medallion(im3, 190, 149, 58, 'back')
d = ImageDraw.Draw(im3)
d.text((300, 118), 'CAMPEONATOS', font=fnt(74), fill=(255, 255, 255, 255))
d.text((300, 202), '3 coronas · Locura 2/3', font=fnt(34), fill=TXT_SUB)
# pestañas
tabs = [('MIS TORNEOS', True), ('INSCRIBIR', False), ('CORONACIÓN', False)]
for i, (t, act) in enumerate(tabs):
    tx = 64 + i * 392
    if act:
        candy_button(im3, (tx, 270), (368, 96), ((255, 186, 42),
                                                 (226, 124, 0), (84, 44, 0),
                                                 (255, 200, 70)), radius=36)
        ImageDraw.Draw(im3).text((tx + 184, 318), t, font=fnt(40),
                                 fill=(24, 14, 0, 255), anchor='mm')
    else:
        body = vgrad(368, 96, (28, 44, 84, 255), (16, 28, 58, 255))
        body.putalpha(rrect_mask(368, 96, 36))
        im3.alpha_composite(body, (tx, 270))
        ImageDraw.Draw(im3).rounded_rectangle([tx, 270, tx + 368, 366], 36,
                                              outline=(120, 170, 230, 130),
                                              width=3)
        ImageDraw.Draw(im3).text((tx + 184, 318), t, font=fnt(40),
                                 fill=TXT_SUB, anchor='mm')
# tarjetas de torneos
panel(im3, (64, 410), (1152, 1310), None)
torneos = [('LA LOCURA', 'Semifinal 2/3 · racha ×4', C_MAG, 'swords',
            'EN CURSO'),
           ('LA MAGIA', 'Completado · ✦ Corona', C_VIO, 'star', 'CORONADO'),
           ('EL OESTE', 'Bloqueado · gana La Magia', C_STL, 'trophy',
            'BLOQUEADO')]
yy = 470
for nom, sub, col, g, badge in torneos:
    mode_card(im3, (104, yy), (1072, 330), col, g, nom, sub, r=46)
    byc = yy + 62
    bw = 130
    bx2 = 104 + 1072 - 36
    ImageDraw.Draw(im3).rounded_rectangle([bx2 - 2 * bw, byc - 34, bx2,
                                           byc + 34], 34,
                                          fill=(0, 0, 0, 150),
                                          outline=(255, 255, 255, 90), width=3)
    ImageDraw.Draw(im3).text((bx2 - bw, byc), badge, font=fnt(32),
                             fill=(255, 255, 255, 255), anchor='mm')
    yy += 400
candy_button(im3, (104, 1600), (1072, 110), C_HERO, radius=40)
ImageDraw.Draw(im3).text((640, 1655), 'SEGUIR JUGANDO', font=fnt(52),
                         fill=(255, 255, 255, 255), anchor='mm')
save(im3, 'mockup3_pantalla_campeonatos.png')
print('LISTO')

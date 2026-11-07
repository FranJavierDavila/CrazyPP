#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r85 · Construye el ARTE del Campeonato de Halloween (staging scripts/_r85_arte/)
   Fuentes: upload/zombi.zip (12 poses del dueño), upload/Mapa.png (mapa del dueño),
   upload/zombi_normas.png (cartel de normas del dueño), upload/Risas.mp3 (provisional),
   valle_neon bso.wav (provisional). Salas de cementerio PROCEDIMENTALES (provisionales:
   el dueño pasa el escenario real en la siguiente tanda)."""
from PIL import Image, ImageDraw, ImageFilter
import zipfile, io, os, shutil, random

RAIZ = '/home/z/my-project'
UP = os.path.join(RAIZ, 'upload')
OUT = os.path.join(RAIZ, 'scripts', '_r85_arte')
os.makedirs(OUT, exist_ok=True)

def log(m): print('· ' + m)

# ---------------------------------------------------------------- POSES ----
z = zipfile.ZipFile(os.path.join(UP, 'zombi.zip'))
ESTADOS = ['present', 'idle', 'focused', 'surprised', 'panic', 'laughing',
           'crazy', 'angry', 'picando', 'loosing', 'defeated', 'victory']
MAPA_FICHERO = {'zombi.png': 'present'}
for e in ESTADOS[1:]:
    MAPA_FICHERO['zombi_%s.png' % e] = e
for fichero, estado in MAPA_FICHERO.items():
    img = Image.open(io.BytesIO(z.read(fichero))).convert('RGBA')
    w, h = img.size
    # diagnóstico: ¿el arte toca los bordes laterales/superiores?
    px = img.load()
    toca_izq = any(px[0, y][3] > 30 for y in range(100, h - 100, 25))
    toca_der = any(px[w - 1, y][3] > 30 for y in range(100, h - 100, 25))
    # limpiado quirúrgico del perímetro superior/lateral (8 px) — NUNCA el fondo
    M = 8
    for y in range(h):
        if y >= h - 2:
            continue                      # pies al borde inferior: intactos
        for x in list(range(M)) + list(range(w - M, w)):
            if y < M or (x < M and toca_izq) or (x >= w - M and toca_der):
                p = list(px[x, y]); p[3] = 0; px[x, y] = tuple(p)
        for x in range(M, w - M):
            if y < M:
                p = list(px[x, y]); p[3] = 0; px[x, y] = tuple(p)
    img.save(os.path.join(OUT, estado + '.webp'), 'WEBP', quality=90, method=6)
    log(f'{estado}.webp  {os.path.getsize(os.path.join(OUT, estado + ".webp"))} B  (toca_izq={toca_izq} toca_der={toca_der})')

# base del standee (igual que present — convención rival.webp)
shutil.copy2(os.path.join(OUT, 'present.webp'), os.path.join(OUT, 'rival.webp'))
log('rival.webp (copia del present)')

# ---------------------------------------------------------------- MAPA -----
im = Image.open(os.path.join(UP, 'Mapa.png')).convert('RGB')
im.save(os.path.join(OUT, 'mapa.webp'), 'WEBP', quality=88, method=6)
log('mapa.webp %d B' % os.path.getsize(os.path.join(OUT, 'mapa.webp')))

# --------------------------------------------------------- CARTEL NORMAS ---
shutil.copy2(os.path.join(UP, 'zombi_normas.png'), os.path.join(OUT, 'normas_halloween.png'))
log('normas_halloween.png (arte del dueño tal cual)')

# -------------------------------------------------- SALAS PROCEDIMENTALES ---
# paleta cementerio nocturno
CIELO_1 = (18, 28, 26); CIELO_2 = (44, 64, 54)
NIEBLA = (118, 148, 132); TIERRA_1 = (52, 46, 34); TIERRA_2 = (34, 30, 22)
PIEDRA = (74, 82, 74); PIEDRA_2 = (52, 58, 52); LUNA = (222, 230, 214)
FANT = (140, 240, 170)
def rnd(seed):
    s = [seed]
    def f():
        s[0] = (s[0] * 16807) % 2147483647
        return s[0] / 2147483647
    return f

def cielo(cv, d, seed, estrellas=True, luna=(0.78, 0.16)):
    W, H = cv.size
    r = rnd(seed)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(CIELO_1[i] + (CIELO_2[i] - CIELO_1[i]) * t) for i in range(3)))
    if estrellas:
        for _ in range(90):
            x, y = r() * W, r() * H * 0.55
            rad = 1.1 if r() < 0.85 else 2.2
            d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(198, 214, 198))
    mx, my = luna[0] * W, luna[1] * H
    d.ellipse([mx - 54, my - 54, mx + 54, my + 54], fill=LUNA)
    d.ellipse([mx - 20 - 54, my - 8 - 54, mx - 20 + 54, my - 8 + 54], fill=CIELO_2)

def tumba(d, x, ybase, w, h, col=PIEDRA, cruz=False):
    d.rounded_rectangle([x - w / 2, ybase - h, x + w / 2, ybase], 8, fill=col, outline=tuple(max(0, c - 22) for c in col), width=3)
    if cruz:
        d.rectangle([x - 4, ybase - h - 26, x + 4, ybase - h + 4], fill=col)
        d.rectangle([x - 16, ybase - h - 14, x + 16, ybase - h - 6], fill=col)
    else:
        d.rounded_rectangle([x - w / 4, ybase - h * 0.72, x + w / 4, ybase - h * 0.5], 4, fill=tuple(max(0, c - 14) for c in col))

def arbol_seco(d, x, ybase, h, col=(16, 22, 18)):
    d.line([(x, ybase), (x, ybase - h)], fill=col, width=10)
    for dx, dy, wd in [(-70, -h * 0.45, 6), (60, -h * 0.6, 6), (-40, -h * 0.75, 5), (90, -h * 0.35, 5), (-95, -h * 0.25, 5)]:
        d.line([(x, ybase - h * 0.55), (x + dx, ybase - h * 0.55 + dy * 0.8)], fill=col, width=wd)
        d.line([(x + dx, ybase - h * 0.55 + dy * 0.8), (x + dx * 1.4, ybase - h * 0.55 + dy * 1.2)], fill=col, width=max(3, wd - 2))

def fantasma(d, x, y, s, a):
    d.ellipse([x - s, y - s, x + s, y + s * 0.9], fill=FANT + (a,))
    d.polygon([(x - s, y), (x + s, y), (x, y + s * 1.5)], fill=FANT + (a,))
    d.ellipse([x - s * 0.34, y - s * 0.3, x - s * 0.1, y - s * 0.05], fill=(20, 34, 26))
    d.ellipse([x + s * 0.1, y - s * 0.3, x + s * 0.34, y - s * 0.05], fill=(20, 34, 26))

def niebla_baja(cv, d, seed, fuerza=70):
    W, H = cv.size
    r = rnd(seed)
    capa = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(capa)
    for _ in range(26):
        x, y = r() * W, H * (0.55 + r() * 0.4)
        rx, ry = W * (0.12 + r() * 0.2), H * (0.035 + r() * 0.05)
        dd.ellipse([x - rx, y - ry, x + rx, y + ry], fill=NIEBLA + (int(fuerza * (0.4 + r() * 0.6)),))
    capa = capa.filter(ImageFilter.GaussianBlur(14))
    cv.paste(capa, (0, 0), capa)

def planos_fondo(W, H, seed, con_mausoleo=False, con_luna=True):
    cv = Image.new('RGB', (W, H), CIELO_1)
    d = ImageDraw.Draw(cv, 'RGBA')
    cielo(cv, d, seed, luna=(0.78, 0.16) if con_luna else (1.5, -1))
    r = rnd(seed + 1)
    hor = int(H * 0.62)
    # TIERRA primero (franja firme) con hierba oscura en el borde
    d.rectangle([0, hor, W, H], fill=TIERRA_1)
    for _ in range(int(W / 22)):
        x = r() * W
        d.line([(x, hor + 2), (x + 5, hor + 16 + r() * 14)], fill=(44, 78, 48), width=3)
    for _ in range(int(W / 30)):
        x = r() * W
        d.line([(x, hor + 40), (x + 8, H)], fill=TIERRA_2, width=4)
    # árboles DETRÁS de las tumbas, plantados en la línea del horizonte
    for _ in range(5):
        arbol_seco(d, r() * W, hor + 6, 130 + r() * 90)
    # mausoleo (sin árboles encima: se dibuja después de los árboles)
    if con_mausoleo:
        mx = W * 0.24
        d.rectangle([mx - 130, hor - 230, mx + 130, hor + 10], fill=PIEDRA_2, outline=(30, 36, 30), width=4)
        d.polygon([(mx - 150, hor - 230), (mx, hor - 320), (mx + 150, hor - 230)], fill=PIEDRA_2, outline=(30, 36, 30))
        d.rounded_rectangle([mx - 34, hor - 130, mx + 34, hor + 10], 40, fill=(12, 16, 14))
    # tumbas FIRMES en la tierra (nunca sobre el horizonte)
    for _ in range(13):
        x = r() * W
        if con_mausoleo and abs(x - W * 0.24) < 190:
            continue
        ybase = hor + 70 + r() * (H - hor - 100)
        tumba(d, x, ybase, 60 + r() * 46, 90 + r() * 70, PIEDRA_2 if r() < 0.5 else PIEDRA, cruz=r() < 0.35)
    for _ in range(4):
        fantasma(d, r() * W, hor * (0.35 + r() * 0.4), 14 + r() * 12, 90)
    niebla_baja(cv, d, seed + 2)
    return cv

# trasera y frontal 1849x864; laterales 2395x864 (medidas canónicas)
planos_fondo(1849, 864, 11, con_mausoleo=True).save(os.path.join(OUT, 'sala_back.jpg'), 'JPEG', quality=82)
planos_fondo(1849, 864, 23, con_luna=False).save(os.path.join(OUT, 'sala_front.jpg'), 'JPEG', quality=82)
planos_fondo(2395, 864, 37).save(os.path.join(OUT, 'sala_left.jpg'), 'JPEG', quality=82)
planos_fondo(2395, 864, 53).save(os.path.join(OUT, 'sala_right.jpg'), 'JPEG', quality=82)
log('salas back/front/left/right.jpg')

# suelo: losas de piedra con hierba
cv = Image.new('RGB', (1296, 1678), TIERRA_1)
d = ImageDraw.Draw(cv, 'RGBA')
r = rnd(71)
for gy in range(0, 1678, 96):
    off = (gy // 96 % 2) * 48
    for gx in range(-48, 1296 + 96, 96):
        x0, y0 = gx + off, gy
        ton = 58 + int(r() * 26)
        col = (ton, ton + 6, ton - 2)
        d.rounded_rectangle([x0 + 3, y0 + 3, x0 + 93, y0 + 93], 12, fill=col, outline=(28, 30, 26), width=3)
        for _ in range(3):
            hx, hy = x0 + 8 + r() * 78, y0 + 8 + r() * 78
            d.line([(hx, hy), (hx + 4, hy - 9)], fill=(44, 78, 48), width=2)
            d.line([(hx + 3, hy), (hx + 9, hy - 7)], fill=(38, 66, 42), width=2)
niebla_baja(cv, d, 79, fuerza=36)
cv.save(os.path.join(OUT, 'sala_floor.jpg'), 'JPEG', quality=82)
log('sala_floor.jpg')

# techo: cielo abierto nocturno con nubes y murciélagos
cv = Image.new('RGB', (1296, 1678), CIELO_1)
d = ImageDraw.Draw(cv, 'RGBA')
cielo(cv, d, 91, luna=(0.3, 0.22))
r = rnd(97)
for _ in range(9):
    x, y = r() * 1296, r() * 1678
    for _ in range(4):
        cx, cy = x + (r() - 0.5) * 260, y + (r() - 0.5) * 180
        d.ellipse([cx - 130, cy - 34, cx + 130, cy + 34], fill=(30, 42, 38, 120))
for _ in range(10):
    x, y = r() * 1296, r() * 1678
    s = 10 + r() * 8
    d.polygon([(x - s, y), (x, y - s * 0.5), (x + s, y)], fill=(10, 14, 12))
    d.polygon([(x - s, y + 2), (x, y + s * 0.55), (x + s, y + 2)], fill=(10, 14, 12))
cv = cv.filter(ImageFilter.GaussianBlur(1.2))
cv.save(os.path.join(OUT, 'sala_ceil.jpg'), 'JPEG', quality=82)
log('sala_ceil.jpg')

# ------------------------------------------------- ICONOS DE SUPERPODER ----
def icono(fichero, pintar):
    cv = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(cv)
    d.ellipse([14, 14, 242, 242], fill=(26, 40, 30, 235), outline=(154, 230, 120, 255), width=8)
    pintar(d)
    cv.save(os.path.join(OUT, fichero), 'PNG')
    log(fichero)

def p_niebla(d):
    r = rnd(5)
    for _ in range(7):
        x, y = 58 + r() * 140, 90 + r() * 80
        rx, ry = 40 + r() * 34, 18 + r() * 14
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(126, 226, 148, 165))
    d.ellipse([100, 96, 156, 152], fill=(16, 30, 20, 220))
    d.ellipse([112, 112, 128, 128], fill=(150, 250, 170))
    d.ellipse([132, 112, 148, 128], fill=(150, 250, 170))
    d.rectangle([112, 134, 148, 140], fill=(150, 250, 170))
icono('power_0.png', p_niebla)

def p_orbe(d):
    for rad, col in [(76, (60, 120, 90, 200)), (58, (120, 220, 150, 220)), (34, (210, 255, 220, 235))]:
        d.ellipse([128 - rad, 128 - rad, 128 + rad, 128 + rad], fill=col)
    d.ellipse([96, 88, 132, 124], fill=(240, 255, 240, 255))
    for a in range(8):
        import math
        x1 = 128 + math.cos(a * math.pi / 4) * 92
        y1 = 128 + math.sin(a * math.pi / 4) * 92
        x2 = 128 + math.cos(a * math.pi / 4) * 108
        y2 = 128 + math.sin(a * math.pi / 4) * 108
        d.line([(x1, y1), (x2, y2)], fill=(150, 250, 170, 220), width=6)
icono('power_1.png', p_orbe)

# ------------------------------------------------------- INSIGNIA/TROFEO ---
cv = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
d = ImageDraw.Draw(cv)
d.ellipse([16, 16, 496, 496], fill=(24, 34, 28, 240), outline=(212, 175, 55, 255), width=12)
d.ellipse([40, 40, 472, 472], outline=(150, 120, 40, 255), width=4)
d.polygon([(186, 128), (326, 128), (316, 262), (196, 262)], fill=(196, 158, 60, 255), outline=(120, 92, 30, 255))
d.line([(326, 148), (382, 156), (368, 214), (318, 228)], fill=(196, 158, 60, 255), width=18)
d.line([(186, 148), (130, 156), (144, 214), (194, 228)], fill=(196, 158, 60, 255), width=18)
d.rectangle([234, 262, 278, 316], fill=(196, 158, 60, 255))
d.rounded_rectangle([186, 316, 326, 352], 10, fill=(212, 175, 55, 255))
d.ellipse([220, 168, 292, 240], fill=(34, 46, 36, 255))
d.ellipse([232, 180, 252, 200], fill=(180, 240, 170, 255))
d.ellipse([260, 180, 280, 200], fill=(180, 240, 170, 255))
d.rectangle([238, 222, 274, 230], fill=(180, 240, 170, 255))
for i, (x, y) in enumerate([(200, 400), (256, 392), (312, 400)]):
    d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(150, 250, 170, 255))
cv.save(os.path.join(OUT, 'insignia.png'), 'PNG')
log('insignia.png')

# ------------------------------------------------------------- PROVISIONAL -
shutil.copy2(os.path.join(RAIZ, 'public', 'championships', 'valle_neon', 'assets', 'bso.wav'),
             os.path.join(OUT, 'bso.wav'))
shutil.copy2(os.path.join(UP, 'Risas.mp3'), os.path.join(OUT, 'risas.mp3'))
log('bso.wav (provisional del valle) + risas.mp3 (provisional)')

LEEME = """MATERIALES DE «Campeonato de Halloween» — qué es del dueño y qué es provisional
================================================================================
DEL DUEÑO (r85):
  present.webp + idle/focused/surprised/panic/laughing/crazy/angry/picando/
    loosing/defeated/victory.webp + rival.webp   12 poses del zombi (upload/zombi.zip)
  mapa.webp                                      póster del camino (upload/Mapa.png 1380x752)
  normas_halloween.png                           cartel de las NORMAS de las etapas 2 y 4
                                                 (upload/zombi_normas.png 1024x512)

PROVISIONAL (FUNCIONAL — sustituir en tandas siguientes):
  sala_floor/ceil/back/front/left/right.jpg      cementerio procedimental — el dueño
                                                 pasará el escenario real para mapear
                                                 los 6 planos de la estancia
  bso.wav                                        música provisional (del valle)
  risas.mp3                                      risa provisional
  power_0.png / power_1.png                      iconos procedimentales
  insignia.png                                   insignia procedimental

PENDIENTE DE LA SIGUIENTE TANDA (dicho por el dueño):
  · escenario (los 6 planos de la estancia) → sustituye las sala_*.jpg
  · los 4 troqueles → manifest.decor.pieces (assets/decor1.png ...)
  · mecánicas de las etapas 2 y 4 (hoy: dianas provisionales)

REGLAS DE ORO (heredadas del proyecto):
  · PNG/WebP con transparencia = recorte exacto al alfa, sin borde añadido.
  · Los sprites del rival son PLANOS (billboard suave), arte 512x1024.
  · No renames: el nombre ES el contrato.
"""
open(os.path.join(OUT, 'LEEME-ASSETS.txt'), 'w', encoding='utf-8').write(LEEME)
log('LEEME-ASSETS.txt')
print('OK staging scripts/_r85_arte/')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r33 (v3.6.129) · ICONOS de los 4 superpoderes nuevos — insignias
circulares 256×256 en la SINTONÍA EXACTA de la familia SuperPala del
dueño (SuperPala_*.png): doble anillo azul marino + anillo azul + filete
blanco, interior azul con remolino sutil y escena cartoon central con
contorno grueso, brillo de cristal y bola de ping pong protagonista.

Salida: scripts/_r33_assets/icon_{prisma,onda,salva,ancla}.png
(256×256, cuantizadas a 256 colores FASTOCTREE — patrón r25/r29)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

S = 1024          # lienzo de trabajo (supermuestreo ×4)
OUT = Path('/home/z/my-project/upload/scripts/_r33_assets')
OUT.mkdir(parents=True, exist_ok=True)

# — paleta de la casa (leída de las insignias del dueño) —
AZUL_MARINO = (16, 42, 84)      # anillo exterior
AZUL_ANILLO = (38, 92, 160)     # anillo medio
AZUL_CLARO = (86, 148, 214)     # interior base
AZUL_INTERIOR = (52, 112, 186)  # interior profundo
BLANCO = (255, 255, 255)
CONTORNO = (15, 32, 58)         # contorno cartoon


def lienzo():
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def anillos(d):
    """El marco de la casa: marino → azul → blanco → borde marino."""
    cx = cy = S / 2
    d.ellipse([18, 18, S - 18, S - 18], fill=AZUL_MARINO)
    d.ellipse([44, 44, S - 44, S - 44], fill=AZUL_ANILLO)
    d.ellipse([74, 74, S - 74, S - 74], fill=BLANCO)
    d.ellipse([92, 92, S - 92, S - 92], fill=AZUL_INTERIOR)
    # brillo especular del anillo marino (arco superior izquierdo)
    d.arc([30, 30, S - 30, S - 30], 150, 240, fill=(90, 140, 205), width=14)
    d.arc([56, 56, S - 56, S - 56], 150, 235, fill=(150, 195, 240), width=10)
    # filete inferior del anillo azul (sombra suave)
    d.arc([52, 52, S - 52, S - 52], 30, 140, fill=(24, 66, 120), width=12)
    return cx, cy


def interior(d, cx, cy):
    """Fondo azul del interior con gradiente radial + remolino (Imán)."""
    # gradiente radial manual por anillos concéntricos (centro claro)
    pasos = 26
    for i in range(pasos, 0, -1):
        t = i / pasos
        r = 420 * t
        col = (
            int(AZUL_INTERIOR[0] + (AZUL_CLARO[0] - AZUL_INTERIOR[0]) * (1 - t) * 0.75),
            int(AZUL_INTERIOR[1] + (AZUL_CLARO[1] - AZUL_INTERIOR[1]) * (1 - t) * 0.75),
            int(AZUL_INTERIOR[2] + (AZUL_CLARO[2] - AZUL_INTERIOR[2]) * (1 - t) * 0.75),
        )
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # remolino: arcos concéntricos desplazados (textura del Imán)
    for k in range(7):
        r = 130 + k * 44
        caja = [cx - r, cy - r, cx + r, cy + r]
        w = 10 if k % 2 == 0 else 6
        col = (108, 168, 228) if k % 2 == 0 else (40, 92, 158)
        d.arc(caja, 20 + k * 24, 150 + k * 24, fill=col, width=w)
        d.arc(caja, 200 + k * 24, 330 + k * 24, fill=col, width=w)


def bola(d, x, y, r, contorno=True):
    """La bola de ping pong de la casa: blanca, sombreada y brillante."""
    if contorno:
        d.ellipse([x - r - 14, y - r - 14, x + r + 14, y + r + 14], fill=CONTORNO)
    d.ellipse([x - r, y - r, x + r, y + r], fill=BLANCO)
    # sombreado inferior (gris azulado)
    d.ellipse([x - r, y - r + r * 0.45, x + r, y + r + r * 0.5],
              fill=(214, 224, 238))
    d.ellipse([x - r, y - r, x + r, y + r - r * 0.28], fill=BLANCO)
    # brillo especular
    d.ellipse([x - r * 0.52, y - r * 0.66, x - r * 0.05, y - r * 0.28],
              fill=(255, 255, 255))


def contorno_shape(d, pts, fill, width=16, outline=CONTORNO):
    """Polígono cartoon: relleno + contorno grueso (línea cerrada)."""
    d.polygon(pts, fill=fill, outline=outline, width=width)


def brillos(d, cx, cy, n=4, semilla=7):
    """Crucecitas de destello (estrella de 4 puntas) repartidas."""
    for i in range(n):
        ang = (i * 2.399 + semilla) % 6.2832
        rr = 250 + (i * 97) % 190
        x = cx + int(280 * __import__('math').cos(ang) * 0.4 + rr * 0.4 *
                     __import__('math').cos(ang + 1.7))
        y = cy + int(rr * 0.42 * __import__('math').sin(ang + 0.6) -
                     120 * __import__('math').cos(ang))
        x = max(170, min(S - 170, x))
        y = max(170, min(S - 170, y))
        L = 34 + (i * 13) % 22
        w = 10
        d.line([x - L, y, x + L, y], fill=(255, 255, 255), width=w)
        d.line([x, y - L, x, y + L], fill=(255, 255, 255), width=w)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(255, 255, 255))


# ———————————————————————————————————————————————— PRISMA —
def icono_prisma():
    im, d = lienzo()
    cx, cy = anillos(d)
    interior(d, cx, cy)
    # haz blanco de entrada (desde la bola al prisma)
    d.polygon([(300, 470), (560, 512), (560, 556), (300, 530)], fill=BLANCO)
    # el prisma triangular de cristal (centro)
    tri = [(cx + 10, 330), (cx + 195, 690), (cx - 175, 690)]
    # halo del prisma
    d.polygon([(cx + 10, 318), (cx + 207, 702), (cx - 187, 702)],
              fill=(24, 62, 112))
    d.polygon(tri, fill=(168, 214, 255))
    # faceta de luz interior
    d.polygon([(cx + 10, 356), (cx + 148, 664), (cx - 118, 664)],
              fill=(212, 238, 255))
    d.line([tri[0], tri[1]], fill=CONTORNO, width=18)
    d.line([tri[1], tri[2]], fill=CONTORNO, width=18)
    d.line([tri[2], tri[0]], fill=CONTORNO, width=18)
    # abanico de 5 colores arcoíris saliendo a la derecha
    colores = [(237, 48, 62), (255, 166, 32), (60, 182, 92),
               (38, 150, 236), (150, 66, 214)]
    origen = (cx + 78, 560)
    for i, col in enumerate(colores):
        y0 = 500 + i * 62
        pts = [(origen[0], origen[1] - 12), (origen[0], origen[1] + 12),
               (S - 168, y0 + 34), (S - 168, y0 - 6)]
        d.polygon(pts, fill=col)
        # contorno suave superior/inferior del haz
    # la bola blanca entrando (izquierda)
    bola(d, 288, 500, 92)
    # chispas del fenómeno
    brillos(d, cx, cy, n=3, semilla=2.1)
    return im


# ———————————————————————————————————————————— ONDA DE CHOQUE —
def _pala_rotada(cx_blade, cy_blade, ang=-38, escala=1.0):
    """Pala roja de la casa dibujada en lienzo propio y pegada girada."""
    P = 520
    p = Image.new('RGBA', (P, P), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p)
    # hoja (óvalo ping pong, más alta que ancha)
    pd.ellipse([70, 40, 450, 420], fill=CONTORNO)
    pd.ellipse([88, 58, 432, 402], fill=(212, 62, 52))
    pd.ellipse([118, 86, 372, 344], fill=(238, 96, 78))
    pd.ellipse([150, 116, 296, 246], fill=(246, 138, 112))
    # mango hacia abajo
    pd.rectangle([222, 404, 298, 512], fill=CONTORNO)
    pd.rectangle([236, 404, 284, 500], fill=(184, 132, 76))
    pd.rectangle([250, 404, 272, 488], fill=(214, 168, 108))
    p = p.rotate(ang, resample=Image.BICUBIC, expand=True)
    return p, (cx_blade, cy_blade)


def icono_onda():
    import math
    im, d = lienzo()
    cx, cy = anillos(d)
    interior(d, cx, cy)
    ix, iy = 640, 540          # punto de IMPACTO
    # ONDAS: 3 anillos completos concéntricos (detrás de todo)
    for i, r in enumerate((170, 275, 385)):
        caja = [ix - r, iy - r, ix + r, iy + r]
        w = 26 - i * 6
        col = (255, 255, 255) if i == 0 else (206, 232, 255)
        d.arc(caja, 0, 360, fill=(36, 82, 138), width=w + 10)
        d.arc(caja, 0, 360, fill=col, width=w)
    # la pala girada llegando desde abajo-izquierda
    p, (px, py) = _pala_rotada(0, 0, ang=-34)
    # pega con contorno: sombra dura leve
    sombra = Image.new('RGBA', p.size, (0, 0, 0, 0))
    alfa = p.split()[3].point(lambda a: 120 if a > 40 else 0)
    negro = Image.new('RGBA', p.size, (15, 32, 58, 255))
    sombra = Image.composite(negro, sombra, alfa)
    im.paste(sombra, (150, 250), sombra)
    im.paste(p, (140, 238), p)
    # ESTRELLA de impacto grande (dos capas)
    star = []
    for k in range(16):
        r = 128 if k % 2 == 0 else 52
        a = k * math.pi / 8 - math.pi / 2
        star.append((ix + r * math.cos(a), iy + r * math.sin(a)))
    contorno_shape(d, star, (255, 214, 92), width=16)
    star2 = []
    for k in range(16):
        r = 84 if k % 2 == 0 else 32
        a = k * math.pi / 8 - math.pi / 2
        star2.append((ix + r * math.cos(a), iy + r * math.sin(a)))
    d.polygon(star2, fill=(255, 246, 200))
    # la bola recién golpeada arriba-derecha de la estrella
    bola(d, 800, 420, 78)
    # líneas de velocidad
    for k, (x0, y) in enumerate(((806, 560), (838, 640))):
        d.line([x0, y, x0 + 120 - k * 30, y], fill=(224, 242, 255), width=16)
    return im


# ————————————————————————————————————————————— SALVAVIDAS —
def icono_salva():
    im, d = lienzo()
    cx, cy = anillos(d)
    interior(d, cx, cy)
    import math
    # ESTELA DE WARP: arco punteado brillante desde abajo-izquierda
    pts = []
    for t in range(0, 41):
        u = t / 40
        x = (1 - u) ** 2 * 320 + 2 * (1 - u) * u * 460 + u * u * (cx - 6)
        y = (1 - u) ** 2 * 880 + 2 * (1 - u) * u * 610 + u * u * (cy + 40)
        pts.append((x, y))
    for i in range(0, len(pts) - 2, 2):
        d.line([pts[i], pts[i + 1]], fill=CONTORNO, width=30)
        d.line([pts[i], pts[i + 1]], fill=(255, 244, 190), width=18)
    # MINI-PALA real al inicio de la estela (blade + mango visibles)
    p, _ = _pala_rotada(0, 0, ang=-26)
    p = p.resize((330, 330), Image.LANCZOS)
    im.paste(p, (150, 700), p)
    # ARO SALVAVIDAS: secciones rojas y blancas alternas
    R, r0 = 252, 152
    cx2, cy2 = cx + 30, cy - 20
    for k in range(8):
        a0 = k * math.pi / 4
        a1 = a0 + math.pi / 4
        col = (212, 52, 46) if k % 2 == 0 else BLANCO
        d.pieslice([cx2 - R, cy2 - R, cx2 + R, cy2 + R],
                   math.degrees(a0), math.degrees(a1), fill=col)
    d.ellipse([cx2 - r0, cy2 - r0, cx2 + r0, cy2 + r0], fill=AZUL_INTERIOR)
    for i in range(14, 0, -1):
        t = i / 14
        r = r0 * t
        col = (int(52 + 34 * (1 - t)), int(112 + 36 * (1 - t)),
               int(186 + 28 * (1 - t)))
        d.ellipse([cx2 - r, cy2 - r, cx2 + r, cy2 + r], fill=col)
    d.ellipse([cx2 - R, cy2 - R, cx2 + R, cy2 + R], outline=CONTORNO, width=22)
    d.ellipse([cx2 - r0, cy2 - r0, cx2 + r0, cy2 + r0], outline=CONTORNO,
              width=18)
    # cuerdas del aro (4 nudos)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        x = cx2 + int((R - 14) * math.cos(a))
        y = cy2 + int((R - 14) * math.sin(a))
        d.ellipse([x - 28, y - 28, x + 28, y + 28], fill=CONTORNO)
        d.ellipse([x - 17, y - 17, x + 17, y + 17], fill=(255, 214, 92))
    # LA BOLA SALVADA dentro del aro
    bola(d, cx2, cy2, 88)
    brillos(d, cx, cy, n=2, semilla=4.2)
    return im


# —————————————————————————————————————————————————— ANCLA —
def icono_ancla():
    im, d = lienzo()
    cx, cy = anillos(d)
    interior(d, cx, cy)
    import math
    ax = cx
    # — ANCLA clásica y audaz (silueta dorada con contorno grueso) —
    # argolla (grande, arriba)
    d.ellipse([ax - 84, 396, ax + 84, 564], outline=CONTORNO, width=40)
    d.ellipse([ax - 66, 414, ax + 66, 546], outline=(255, 208, 84), width=24)
    # caña
    d.rounded_rectangle([ax - 26, 540, ax + 26, 810], radius=22, fill=CONTORNO)
    d.rounded_rectangle([ax - 14, 552, ax + 14, 798], radius=12,
                        fill=(255, 208, 84))
    # travesaño
    d.rounded_rectangle([ax - 190, 590, ax + 190, 648], radius=24,
                        fill=CONTORNO)
    d.rounded_rectangle([ax - 176, 602, ax + 176, 636], radius=15,
                        fill=(255, 224, 128))
    # brazos en U (arco inferior) + uñas
    d.arc([ax - 268, 218, ax + 268, 754], 28, 152, fill=CONTORNO, width=48)
    d.arc([ax - 254, 230, ax + 254, 742], 31, 149, fill=(255, 208, 84),
          width=30)
    for sx in (-1, 1):
        tipx = ax + sx * 238
        tipy = 640
        contorno_shape(d, [(tipx - 34 * sx, tipy - 10),
                           (tipx + 26 * sx, tipy - 86),
                           (tipx + 6 * sx, tipy + 30)],
                       (255, 208, 84), width=16)
    # peana de anclaje con pernos
    d.rounded_rectangle([ax - 252, 812, ax + 252, 892], radius=26,
                        fill=CONTORNO)
    d.rounded_rectangle([ax - 238, 826, ax + 238, 878], radius=20,
                        fill=(70, 128, 196))
    for px in (-150, 0, 150):
        d.ellipse([ax + px - 20, 838, ax + px + 20, 868], fill=CONTORNO)
        d.ellipse([ax + px - 11, 847, ax + px + 11, 859],
                  fill=(255, 214, 92))
    # LA BOLA protegida, apoyada sobre la argolla
    bola(d, ax, 296, 66)
    # eslabón corto que une bola y argolla
    d.ellipse([ax - 24, 376, ax + 24, 424], fill=CONTORNO)
    d.ellipse([ax - 13, 387, ax + 13, 413], fill=(255, 214, 92))
    brillos(d, cx, cy, n=2, semilla=1.3)
    return im


def terminar(im, nombre):
    im = im.resize((256, 256), Image.LANCZOS)
    q = im.quantize(colors=256, method=Image.FASTOCTREE,
                    dither=Image.FLOYDSTEINBERG)
    dst = OUT / f'icon_{nombre}.png'
    q.save(dst, optimize=True)
    print(f'{dst.name}: {dst.stat().st_size:,} B')


if __name__ == '__main__':
    terminar(icono_prisma(), 'prisma')
    terminar(icono_onda(), 'onda')
    terminar(icono_salva(), 'salva')
    terminar(icono_ancla(), 'ancla')

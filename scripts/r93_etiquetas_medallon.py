#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r93 · Etiquetas de superpoder del Halloween → medallón circular tenebroso.

Toma los 4 artes fotorealistas (1024×1024) generados para el dueño y los
convierte en las etiquetas del juego: recorte circular, anillo de hierro
viejo con filo ember (paleta calabaza 0xe8720c apagada), borde suave y
salida RGBA webp 512×512 (nítido en el plano de 0,30 m del cartel y ligero).

Los nombres de salida SON los del manifest (assets/power_*.webp): cero
cambios de código — el cartel los muestra por powers[].icon como siempre.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE = '/home/z/my-project'
RAW = os.path.join(BASE, 'scripts', 'staging-r93')
OUT = os.path.join(BASE, 'public', 'championships', 'halloween', 'assets')

# (fichero bruto, destino, nombre del poder)
MAPA = [
    ('mano_raw.png',     'power_mano.webp',     'MANO'),
    ('moscas_raw.png',   'power_moscas.webp',   'MOSCAS'),
    ('calabaza_raw.png', 'power_calabaza.webp', 'CALABAZA'),
    ('gelatina_raw.png', 'power_gelatina.webp', 'GELATINA'),
]

S = 1024              # lienzo de trabajo
R_IMG = 448           # radio del arte (dentro del anillo)
R_EXT = 500           # radio exterior del anillo
ANILLO = R_EXT - R_IMG  # grosor del anillo (52 px)
FIL_MIN, FIL_MAX = 3, 5  # filo ember: anillos concéntricos finos


def a_gris(x):
    return int(x) & 0xFF


def medallon(ruta_raw, ruta_out, nombre):
    im = Image.open(ruta_raw).convert('RGB').resize((S, S), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.06)      # un pelín más de drama
    im = ImageEnhance.Color(im).enhance(1.08)

    # máscara circular del arte (borde suave 3 px)
    marte = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(marte)
    d.ellipse((S // 2 - R_IMG, S // 2 - R_IMG,
               S // 2 + R_IMG, S // 2 + R_IMG), fill=255)
    marte = marte.filter(ImageFilter.GaussianBlur(2.2))

    # anillo de hierro viejo: base oscura con bisel (claro arriba-izq, sombra abajo-der)
    anillo = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    da = ImageDraw.Draw(anillo)
    cx = S // 2
    da.ellipse((cx - R_EXT, cx - R_EXT, cx + R_EXT, cx + R_EXT),
               fill=(24, 22, 21, 255))                       # hierro casi negro
    da.ellipse((cx - R_IMG, cx - R_IMG, cx + R_IMG, cx + R_IMG),
               fill=(0, 0, 0, 0))                            # hueco del arte
    # bisel: arco claro (luz de luna) arriba-izquierda y sombra abajo-derecha
    bisel = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    db = ImageDraw.Draw(bisel)
    db.arc((cx - R_EXT + 5, cx - R_EXT + 5, cx + R_EXT - 5, cx + R_EXT - 5),
           start=140, end=320, fill=(96, 92, 88, 255), width=9)
    db.arc((cx - R_EXT + 5, cx - R_EXT + 5, cx + R_EXT - 5, cx + R_EXT - 5),
           start=-40, end=140, fill=(8, 7, 7, 255), width=9)
    bisel = bisel.filter(ImageFilter.GaussianBlur(2.0))
    anillo = Image.alpha_composite(anillo, bisel)

    # filo ember (acentos apagados de calabaza): 3 anillos finos justo dentro
    filo = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    df = ImageDraw.Draw(filo)
    for i, w in enumerate([FIL_MAX, FIL_MIN, FIL_MIN]):
        r = R_IMG + 8 + i * 11
        df.ellipse((cx - r, cx - r, cx + r, cx + r),
                   outline=(168, 72, 12, 210 - i * 55), width=w)
    filo = filo.filter(ImageFilter.GaussianBlur(0.8))
    anillo = Image.alpha_composite(anillo, filo)

    # composición: arte recortado + anillo por encima
    lienzo = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    lienzo.paste(im, (0, 0), marte)
    lienzo = Image.alpha_composite(lienzo, anillo)

    # veta siniestra global: viñeta radial suave que oscurece los bordes del arte
    vin = Image.new('L', (S, S), 0)
    dv = ImageDraw.Draw(vin)
    dv.ellipse((cx - R_IMG, cx - R_IMG, cx + R_IMG, cx + R_IMG), fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(140))
    negro = Image.new('RGBA', (S, S), (5, 4, 8, 255))
    oscuro = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    oscuro.paste(negro, (0, 0), vin.point(lambda v: int((255 - v) * 0.55)))
    arte_zona = Image.new('L', (S, S), 0)
    da2 = ImageDraw.Draw(arte_zona)
    da2.ellipse((cx - R_IMG + 6, cx - R_IMG + 6, cx + R_IMG - 6, cx + R_IMG - 6), fill=255)
    arte_zona = arte_zona.filter(ImageFilter.GaussianBlur(2.0))
    oscuro.putalpha(Image.composite(oscuro.getchannel('A'), Image.new('L', (S, S), 0), arte_zona))
    lienzo = Image.alpha_composite(lienzo, oscuro)

    # salida 512×512 webp RGBA
    final = lienzo.resize((512, 512), Image.LANCZOS)
    final.save(ruta_out, 'WEBP', quality=86, method=6, exact=False)
    kb = os.path.getsize(ruta_out) / 1024
    print(f'  ✓ {nombre:9s} → {os.path.basename(ruta_out)} ({kb:.0f} KB, 512×512 RGBA)')


if __name__ == '__main__':
    print('r93 · medallones tenebrosos de superpoder')
    for raw, out, nom in MAPA:
        medallon(os.path.join(RAW, raw), os.path.join(OUT, out), nom)
    print('listo')

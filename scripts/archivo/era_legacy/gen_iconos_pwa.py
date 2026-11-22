#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_iconos_pwa.py — ICONOS PWA de CRAZY PING PONG (r109 · hito M3).

Genera, con PIL y a partir de la IDENTIDAD DE LA CASA (el emblema del Hall:
palas cruzadas + bola en oro sobre fondo azul profundo, r35 FASE 29),
tres iconos en public/:

  logo-192.png            · icono estándar 192×192
  logo-512.png            · icono estándar 512×512
  logo-maskable-512.png   · variante MASKABLE (todo el contenido dentro del
                            80 % central: el navegador puede recortar círculo)

Dibujo (vector con PIL, sin assets externos):
  · fondo radial azul noche (#0b2050 → #050810) como la portada
  · anillo dorado (#ffd257 / #c9932f latón del Hall)
  · dos palas cruzadas en X: goma ROJA (45°) y goma NEGRA (−45°) — las dos
    caras del juego desde Task 1 — con mango de madera
  · bola blanca con sombra en el centro del cruce (la estrella de la casa)
Idempotente: siempre regenera los 3 PNG.
"""
from math import sin, cos, radians
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path('/home/z/my-project/upload')
PUB = RAIZ / 'public'

FONDO_IN = (11, 32, 80)      # #0b2050 (portada)
FONDO_OUT = (5, 8, 16)       # #050810
ORO = (255, 210, 87)         # #ffd257 (badge)
ORO_OSC = (201, 147, 47)     # #c9932f (latón del Hall)
ROJO = (196, 40, 47)         # goma roja
NEGRO = (30, 32, 38)         # goma negra
MADERA = (146, 102, 60)      # mango
BLANCO = (238, 242, 246)     # bola


def fondo_radial(S):
    img = Image.new('RGB', (S, S), FONDO_OUT)
    dr = ImageDraw.Draw(img)
    pasos = 90
    for i in range(pasos, -1, -1):
        t = i / pasos
        r = int(S * 0.75 * t) + 1
        col = tuple(int(FONDO_OUT[k] + (FONDO_IN[k] - FONDO_OUT[k]) * (1 - t)) for k in range(3))
        dr.ellipse([S // 2 - r, S // 2 - r, S // 2 + r, S // 2 + r], fill=col)
    return img


def pala(S, ang, cara, escala=1.0):
    """Una pala rotada `ang` grados: hoja elíptica + mango. Capa RGBA."""
    L = S * 2
    lay = Image.new('RGBA', (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = cy = L // 2
    # proporciones (en función de S): hoja rx≈0.16S ry≈0.20S, mango 0.30S
    rx = 0.16 * S * escala
    ry = 0.20 * S * escala
    ml = 0.34 * S * escala       # largo del mango
    mw = 0.055 * S * escala      # ancho del mango
    # hoja centrada desplazada hacia arriba, mango hacia abajo (pala vertical)
    leaf_cy = cy - 0.10 * S * escala
    hnd_cy = leaf_cy + ry + ml / 2
    # mango (redondeado)
    d.rounded_rectangle([cx - mw, hnd_cy - ml / 2, cx + mw, hnd_cy + ml / 2],
                        radius=mw, fill=MADERA)
    # hoja: goma (elipse) + borde
    for delta, col in ((int(0.012 * S * escala), (0, 0, 0, 160)), (0, cara)):
        d.ellipse([cx - rx + delta, leaf_cy - ry + delta,
                   cx + rx + delta, leaf_cy + ry + delta], fill=col)
    # brillo de la goma (arco superior)
    d.ellipse([cx - rx * 0.62, leaf_cy - ry * 0.66,
               cx + rx * 0.10, leaf_cy - ry * 0.05], fill=tuple(min(255, int(c * 1.25)) for c in cara))
    lay = lay.rotate(ang, resample=Image.BICUBIC, center=(cx, cy))
    m = (L - S) // 2
    return lay.crop((m, m, m + S, m + S))


def emblema(S, margen_seguridad=1.0):
    """Icono completo a S px. margen_seguridad<1 encoge el arte (maskable)."""
    img = fondo_radial(S)
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    # anillo dorado
    d = ImageDraw.Draw(lay)
    r = 0.46 * S * margen_seguridad
    w = max(3, int(0.024 * S))
    for dw, col in ((w, ORO_OSC), (max(2, w // 2), ORO)):
        d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=col, width=dw)
    esc = margen_seguridad * 0.92
    lay = Image.alpha_composite(lay, pala(S, 38, ROJO, esc).convert('RGBA'))
    lay = Image.alpha_composite(lay, pala(S, -38, NEGRO, esc).convert('RGBA'))
    img = Image.alpha_composite(img.convert('RGBA'), lay)
    # bola blanca en el centro con sombra
    d = ImageDraw.Draw(img)
    br = 0.085 * S * margen_seguridad
    d.ellipse([S / 2 - br * 1.15 + 0.012 * S, S / 2 - br * 1.15 + 0.014 * S,
               S / 2 + br * 1.15 + 0.012 * S, S / 2 + br * 1.15 + 0.014 * S],
              fill=(0, 0, 0, 110))
    d.ellipse([S / 2 - br, S / 2 - br, S / 2 + br, S / 2 + br], fill=BLANCO)
    d.ellipse([S / 2 - br * 0.55, S / 2 - br * 0.6,
               S / 2 + br * 0.05, S / 2 - br * 0.05], fill=(255, 255, 255))
    return img


def main():
    outs = []
    i512 = emblema(512)
    i512.save(PUB / 'logo-512.png', optimize=True)
    outs.append(('logo-512.png', 512))
    i192 = i512.resize((192, 192), Image.LANCZOS)
    i192.save(PUB / 'logo-192.png', optimize=True)
    outs.append(('logo-192.png', 192))
    im512 = emblema(512, margen_seguridad=0.74)   # maskable: 80 % central
    im512.save(PUB / 'logo-maskable-512.png', optimize=True)
    outs.append(('logo-maskable-512.png', 512))
    for n, s in outs:
        p = PUB / n
        print(f'  ✓ {n}: {s}×{s} · {p.stat().st_size:,} B')
    print('ICONOS PWA GENERADOS')


if __name__ == '__main__':
    main()

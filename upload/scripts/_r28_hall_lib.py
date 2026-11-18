#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r28 (v3.6.124, FASE 126) — LIBRERÍA DE ARTE PARA LOS
3 HALL REDISEÑADOS. Nivel de detalle del bar: los decorados de La Locura
y Wizard (geometría en capas, iluminación y materiales), aquí en PIL:
  · gradientes MULTI-PARADA (4-6 tonos, nunca 2)
  · OCLUSIÓN AMBIENTAL (esquinas, contacto suelo-pared, sombra de techo)
  · GLOW ADITIVO de verdad (núcleo + halo medio + halo amplio)
  · props con SOMBREADO DE 3 TONOS + brillos especulares
  · grano de película + viñeta suave (nada de plástico)
Salida: usada por _r28_gen_halls.py (18 imágenes, 3 salones × 6 caras).
"""
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import math, random

FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


# ---------------------------------------------------------------- gradientes
def grad_multi(w, h, stops, horizontal=False):
    """Gradiente multi-parada. stops = [(t, (r,g,b)), ...] con t en 0..1."""
    stops = sorted(stops, key=lambda s: s[0])
    img = Image.new('RGB', (w, h))
    px = img.load()
    n = (w if horizontal else h)
    for i in range(n):
        t = i / max(1, n - 1)
        # buscar tramo
        k = 0
        while k < len(stops) - 2 and t > stops[k + 1][0]:
            k += 1
        t0, c0 = stops[k]
        t1, c1 = stops[min(k + 1, len(stops) - 1)]
        f = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
        c = tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
        if horizontal:
            for y in range(h):
                px[i, y] = c
        else:
            for x in range(w):
                px[x, i] = c
    return img


def grad_radial(w, h, centro, radio, c_in, c_out):
    """Radial suave (para glows de suelo, halos de lámpara)."""
    img = Image.new('RGB', (w, h))
    px = img.load()
    cx, cy = centro
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / max(1.0, radio)
            f = min(1.0, max(0.0, d))
            f = f * f * (3 - 2 * f)  # smoothstep
            px[x, y] = tuple(int(c_in[k] + (c_out[k] - c_in[k]) * f) for k in range(3))
    return img


# ---------------------------------------------------------------- acabados
def grano(img, sigma=14, alfa=10):
    n = Image.effect_noise(img.size, sigma).convert('L')
    g = Image.merge('RGB', (n, n, n))
    return Image.blend(img, g, alfa / 255.0)


def vineta(img, fuerza=70):
    w, h = img.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-w * 0.28, -h * 0.28, w * 1.28, h * 1.28], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(w, h) * 0.11))
    osc = Image.new('RGB', (w, h), (3, 3, 6))
    return Image.composite(img, Image.blend(img, osc, fuerza / 255.0), m)


def ao_esquinas(img, fuerza=88, radio=0.16):
    """Oclusión ambiental en las 4 esquinas (multi-blob suave)."""
    w, h = img.size
    capa = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(capa)
    r = int(min(w, h) * radio)
    for (cx, cy) in [(0, 0), (w, 0), (0, h), (w, h)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fuerza)
    capa = capa.filter(ImageFilter.GaussianBlur(r * 0.55))
    osc = Image.new('RGB', img.size, (2, 2, 5))
    return Image.composite(Image.blend(img, osc, 0.55), img, capa)


def contacto_suelo(img, altura=0.10, fuerza=120):
    """Sombra de contacto pared-suelo (banda oscura difuminada abajo)."""
    w, h = img.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    hh = int(h * altura)
    d.rectangle([0, h - hh, w, h], fill=fuerza)
    m = m.filter(ImageFilter.GaussianBlur(hh * 0.45))
    osc = Image.new('RGB', (w, h), (4, 4, 7))
    return Image.composite(Image.blend(img, osc, 0.65), img, m)


def sombra_techo(img, altura=0.08, fuerza=90):
    w, h = img.size
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    hh = int(h * altura)
    d.rectangle([0, 0, w, hh], fill=fuerza)
    m = m.filter(ImageFilter.GaussianBlur(hh * 0.5))
    osc = Image.new('RGB', (w, h), (3, 3, 6))
    return Image.composite(Image.blend(img, osc, 0.6), img, m)


# ---------------------------------------------------------------- glow
def _capa(img):
    return Image.new('RGBA', img.size, (0, 0, 0, 0))


def glow_compuesto(img, dibujo_fn, color, blurs=(26, 9, 0), fuerza=(90, 150, 255)):
    """Glow aditivo de 3 pasadas: dibujo_fn(d) pinta la FORMA en blanco o
    color sobre una capa; se devuelve img con núcleo + halos sumados."""
    base = _capa(img)
    dibujo_fn(ImageDraw.Draw(base), color)
    out = img.convert('RGBA')
    for b, f in zip(blurs, fuerza):
        c = base.filter(ImageFilter.GaussianBlur(b)) if b else base
        if f < 255:
            a = c.getchannel('A').point(lambda v: int(v * f / 255))
            c.putalpha(a)
        out = ImageChops.add(out, c)
    return out.convert('RGB')


def texto_neon(img, txt, xy, size, color, blur_core=2, anchor='mm'):
    """Letrero de neón: halo amplio + medio + tubería nítida."""
    def dib(d, col):
        f = ImageFont.truetype(FONT_B, size)
        d.text(xy, txt, font=f, fill=col + (255,), anchor=anchor)
    return glow_compuesto(img, dib, color, blurs=(size * 0.45, size * 0.10, blur_core),
                          fuerza=(70, 140, 255))


def tubo_neon(img, puntos, color, grosor=5, halo=22, cerrado=False):
    """Tubería de neón con glow (polilínea)."""
    def dib(d, col):
        w = grosor + 2
        d.line(puntos + ([puntos[0]] if cerrado else []), fill=col + (255,), width=w * 3, joint='curve')
        if cerrado and len(puntos) >= 3:
            d.polygon(puntos, outline=col + (255,), width=w * 3)
    img = glow_compuesto(img, dib, color, blurs=(halo, halo * 0.35, 0), fuerza=(80, 150, 255))
    # núcleo claro encima (tubo encendido)
    d = ImageDraw.Draw(img)
    d.line(puntos + ([puntos[0]] if cerrado else []), fill=_aclara(color, 0.55) + (255,),
           width=grosor, joint='curve')
    return img


def _aclara(col, f):
    return tuple(int(c + (255 - c) * f) for c in col)


def _oscurece(col, f):
    return tuple(int(c * (1 - f)) for c in col)


def foco_glow(img, xy, radio, color, fuerza=170):
    """Halo circular suave (lámpara, señal)."""
    def dib(d, col):
        d.ellipse([xy[0] - radio, xy[1] - radio, xy[0] + radio, xy[1] + radio], fill=col + (255,))
    return glow_compuesto(img, dib, color, blurs=(radio * 0.9, radio * 0.3, radio * 0.08),
                          fuerza=(int(fuerza * 0.5), fuerza, 235))


# ---------------------------------------------------------------- props 3-tonos
def caja_3t(d, caja, base, luz_izq=True, borde=None, radio=0):
    """Rectángulo con sombreado de 3 tonos (base, sombra, luz) + arista."""
    x0, y0, x1, y1 = caja
    sombra = _oscurece(base, 0.42)
    luz = _aclara(base, 0.30)
    d.rectangle(caja, fill=base)
    # franja de luz (izq o der) y de sombra
    fw = max(2, int((x1 - x0) * 0.10))
    if luz_izq:
        d.rectangle([x0, y0, x0 + fw, y1], fill=luz)
        d.rectangle([x1 - fw, y0, x1, y1], fill=sombra)
    else:
        d.rectangle([x1 - fw, y0, x1, y1], fill=luz)
        d.rectangle([x0, y0, x0 + fw, y1], fill=sombra)
    d.rectangle(caja, outline=borde or _oscurece(base, 0.6), width=max(1, radio))


def sombra_prop(img, caja, alfa=110, blur=12, dy=6):
    """Sombra elíptica suave bajo un prop."""
    capa = _capa(img)
    d = ImageDraw.Draw(capa)
    x0, y0, x1, y1 = caja
    d.ellipse([x0, y1 - dy, x1, y1 + dy * 2], fill=(0, 0, 0, alfa))
    capa = capa.filter(ImageFilter.GaussianBlur(blur))
    out = img.convert('RGBA')
    out = Image.alpha_composite(out, capa)
    return out.convert('RGB')


def remaches(d, caja, paso, col=None, r=3):
    x0, y0, x1, y1 = caja
    col = col or (168, 176, 188)
    xs = list(range(x0 + paso // 2, x1, paso))
    for x in xs:
        for y in (y0 + 10, y1 - 10):
            d.ellipse([x - r, y - r, x + r, y + r], fill=_aclara(col, 0.3))
            d.ellipse([x - r + 1, y - r + 1, x + r, y + r], fill=col)


# ---------------------------------------------------------------- estrellas
def campo_estrellas(img, n, seed=7, zona=None, grandes=6):
    rnd = random.Random(seed)
    w, h = img.size
    x0, y0, x1, y1 = zona or (0, 0, w, h)
    capa = _capa(img)
    d = ImageDraw.Draw(capa)
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        r = rnd.choice([0.6, 0.8, 1.0, 1.2, 1.6])
        brillo = rnd.randint(120, 255)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(brillo, brillo, min(255, brillo + 14), 235))
    # pocas estrellas grandes con cruz de difracción
    for _ in range(grandes):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        r = rnd.uniform(1.8, 2.8)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
        L = rnd.uniform(6, 13)
        d.line([x - L, y, x + L, y], fill=(210, 225, 255, 160), width=1)
        d.line([x, y - L, x, y + L], fill=(210, 225, 255, 160), width=1)
    capa = capa.filter(ImageFilter.GaussianBlur(0.4))
    out = Image.alpha_composite(img.convert('RGBA'), capa)
    return out.convert('RGB')


# ---------------------------------------------------------------- tierra
def tierra(img, cx, cy, r, seed=5, luz_deg=215):
    """La Tierra REAL: océano con gradiente, continentes (blobs), nubes,
    terminador con sombra y ATMÓSFERA con halo azul."""
    rnd = random.Random(seed)
    # 1 · halo de atmósfera (detrás)
    img = foco_glow(img, (cx, cy), r * 1.22, (90, 160, 255), fuerza=120)
    # 2 · disco con océano
    disc = Image.new('RGB', (r * 2 + 4, r * 2 + 4), (0, 0, 0))
    dd = ImageDraw.Draw(disc)
    for i in range(r * 2):
        t = i / max(1, r * 2 - 1)
        c = (int(12 + 40 * math.sin(t * math.pi)),
             int(60 + 90 * math.sin(t * math.pi * 0.9) + 30 * math.sin(t * 6)),
             int(120 + 110 * math.sin(t * math.pi)))
        dd.line([0, i, r * 2 + 3, i], fill=(max(0, c[0]), max(0, min(255, c[1])), max(0, min(255, c[2]))))
    # continentes: blobs verdes-ocre con borde costero
    for _ in range(9):
        bx = rnd.uniform(r * 0.25, r * 1.75)
        by = rnd.uniform(r * 0.3, r * 1.7)
        br = rnd.uniform(r * 0.16, r * 0.42)
        col = rnd.choice([(52, 110, 58), (74, 122, 60), (96, 128, 64), (60, 100, 52)])
        for _k in range(7):
            ox, oy = bx + rnd.uniform(-br * .5, br * .5), by + rnd.uniform(-br * .5, br * .5)
            rr = br * rnd.uniform(0.45, 0.95)
            dd.ellipse([ox - rr, oy - rr, ox + rr, oy + rr], fill=col)
    # nubes: arcos blancos suaves
    nube = Image.new('RGBA', disc.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(nube)
    for _ in range(14):
        bx = rnd.uniform(0, r * 2)
        by = rnd.uniform(0, r * 2)
        L = rnd.uniform(r * 0.2, r * 0.7)
        nd.arc([bx - L, by - L * 0.4, bx + L, by + L * 0.4], rnd.randint(0, 360),
               rnd.randint(80, 220), fill=(255, 255, 255, rnd.randint(70, 130)), width=rnd.randint(3, 7))
    nube = nube.filter(ImageFilter.GaussianBlur(3))
    disc = Image.alpha_composite(disc.convert('RGBA'), nube).convert('RGB')
    # máscara circular + terminador (sombra del lado opuesto a la luz)
    m = Image.new('L', disc.size, 0)
    md = ImageDraw.Draw(m)
    md.ellipse([2, 2, r * 2 + 2, r * 2 + 2], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(disc, (int(cx - r), int(cy - r)), m)
    # terminador: media luna oscura según luz_deg
    som = Image.new('L', img.size, 0)
    sd = ImageDraw.Draw(som)
    ang = math.radians(luz_deg)
    sx, sy = cx - math.cos(ang) * r * 0.55, cy - math.sin(ang) * r * 0.55
    sd.ellipse([sx - r * 1.15, sy - r * 1.15, sx + r * 1.15, sy + r * 1.15], fill=170)
    som = som.filter(ImageFilter.GaussianBlur(r * 0.35))
    # recortar sombra al disco
    discmask = Image.new('L', img.size, 0)
    dmd = ImageDraw.Draw(discmask)
    dmd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    som = ImageChops.multiply(som, discmask)
    osc = Image.new('RGB', img.size, (2, 4, 10))
    img = Image.composite(Image.blend(img, osc, 0.75), img, som)
    # 3 · borde atmosférico nítido
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 190, 255), width=2)
    return img

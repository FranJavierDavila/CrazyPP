#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2.134 · MÁS VEGETACIÓN en la panorámica exterior del parallax (etapa 4,
«Asalto al Tren» del Salva je Oeste) — petición del dueño: «yo metería algo
más de vegetación en la imagen del exterior del parallax, la veo un poco
escasa de elementos».

Qué hace:
  1. Respalda los originales a scripts/backup_p1_v2133/ (una sola vez).
  2. Compone ARBUSTOS/CACTUS/ROCAS del propio artista (sprites RGBA de
     assets/parallax p3_/p4_/p2_ + decor/) sobre el SUELO DE ARENA de las
     DOS panorámicas p1_paisajedesierto1/2.png (2172×524).
  3. Escala por perspectiva (pies más abajo = más cerca = más grande),
     racimos naturales + solitarios, volteo aleatorio y BRUMA cálida de
     distancia (mezcla hacia el tono de la arena lejana).
  4. NO toca la franja inferior de 64 px (rows 460..524): _buildPano del
     módulo estira las últimas 60 filas para bajar el desierto (EXT=190)
     y todo lo que caiga ahí se DEFORMARÍA.

Es idempotente en práctica (siempre respalda primero; si ya hay respaldo,
no lo pisa) y se puede re-ejecutar sobre los RESPALDOS para recalibrar.
"""
import os
import random
import shutil
from PIL import Image

BASE = '/home/z/my-project/public/championships/oeste/assets/parallax'
DECOR = '/home/z/my-project/public/championships/oeste/assets/decor'
BAK = '/home/z/my-project/scripts/backup_p1_v2133'
PANOS = ['p1_paisajedesierto1.png', 'p1_paisajedesierto2.png']

# sprites del artista con alfa (pequeños/medianos, ideales para lejos)
SPRITES = (
    ['p3_arbusto%d.png' % i for i in range(1, 10)] +
    ['p4_cactus1.png', 'p4_cactus2.png'] +
    ['p2_roca2.png', 'p2_roca3.png', 'p2_roca5.png'] +
    [os.path.join(DECOR, 'arbusto.png'), os.path.join(DECOR, 'cactus.png')]
)

# banda de suelo seguro: pies entre y=404 (lejos) y y=456 (cerca);
# la franja 460..524 queda VIRGEN (zona estirada por _buildPano).
Y_FAR, Y_NEAR = 404, 456
H_FAR, H_NEAR = 9.0, 30.0          # altura de sprite en px (lejos → cerca)
EDGE = 14                          # margen con las costuras laterales
HAZE = (208, 186, 152)             # bruma cálida del desierto lejano

random.seed(20261014)


def load_sprites():
    out = []
    for f in SPRITES:
        p = f if os.path.isabs(f) else os.path.join(BASE, f)
        im = Image.open(p).convert('RGBA')
        # recorta al contenido (bbox alfa) para componer sin aire alrededor
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
        out.append(im)
    return out


def foot_free(pix, x, y, w):
    """El pie debe caer sobre arena OPACA (no cielo/siluetas huecas)."""
    if x < EDGE or x > w - EDGE:
        return False
    if y < Y_FAR - 6 or y > Y_NEAR:
        return False
    for dy in (-3, 0):
        r, g, b, a = pix[x, y + dy]
        if a < 200:
            return False
    return True


def paste(im, pix_dst, spr, x, y_foot):
    w, h = im.size
    # perspectiva: pies más abajo (más cerca) → sprite más grande
    t = (y_foot - Y_FAR) / float(Y_NEAR - Y_FAR)
    scale = (H_FAR + (H_NEAR - H_FAR) * t) / float(spr.height)
    scale *= random.uniform(0.78, 1.30)
    nw = max(3, int(spr.width * scale))
    nh = max(3, int(spr.height * scale))
    if nw >= w - 2:
        return False
    s = spr.resize((nw, nh), Image.LANCZOS)
    if random.random() < 0.5:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    # bruma de distancia: lejos (t pequeño) → más mezcla con la bruma
    k = max(0.10, 0.46 * (1.0 - t))
    px = s.load()
    for yy in range(nh):
        for xx in range(nw):
            r, g, b, a = px[xx, yy]
            if a == 0:
                continue
            r2 = int(r + (HAZE[0] - r) * k)
            g2 = int(g + (HAZE[1] - g) * k)
            b2 = int(b + (HAZE[2] - b) * k)
            a2 = int(a * (0.90 + 0.10 * t))     # lejanos apenas más tenues
            px[xx, yy] = (r2, g2, b2, a2)
    im.paste(s, (x - nw // 2, y_foot - nh), s)
    return True


def enrich(path, sprites):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    pix = im.load()
    total = 0
    # RACIMOS: 10 grupos con 5-9 pies cada uno (spread gaussiano)
    for _ in range(10):
        cx = random.randint(EDGE + 30, w - EDGE - 30)
        cy = random.randint(Y_FAR + 8, Y_NEAR - 8)
        for _ in range(random.randint(5, 9)):
            for _try in range(8):
                x = int(cx + random.gauss(0, 34))
                y = int(cy + random.gauss(0, 7))
                if foot_free(pix, x, y, w):
                    if paste(im, pix, random.choice(sprites), x, y):
                        total += 1
                    break
    # SOLITARIOS: 18 arbustos/cactus repartidos
    for _ in range(18):
        for _try in range(10):
            x = random.randint(EDGE, w - EDGE)
            y = random.randint(Y_FAR, Y_NEAR)
            if foot_free(pix, x, y, w):
                if paste(im, pix, random.choice(sprites), x, y):
                    total += 1
                break
    im.save(path)
    return total


def main():
    os.makedirs(BAK, exist_ok=True)
    sprites = load_sprites()
    print('sprites del artista: %d' % len(sprites))
    for f in PANOS:
        src = os.path.join(BASE, f)
        bak = os.path.join(BAK, f)
        if not os.path.exists(bak):
            shutil.copy2(src, bak)          # respaldo SOLO la 1.ª vez
            print('respaldo: %s' % bak)
        else:
            shutil.copy2(bak, src)          # re-ejecución: parte del original
            print('re-ejecutando desde respaldo: %s' % f)
        n = enrich(src, sprites)
        print('%s → +%d vegetales' % (f, n))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2.111 · ASSETS DEL VAGÓN (Crazy Ping Pong — etapa ASALTO AL TREN).

1) Pre-cose las DOS panorámicas p1_paisajedesierto1/2.png en UNA única
   tira continua `p1_horizonte.png` (4344×524, RGBA con cielo transparente).
   En la costura del BUCLE (borde derecho de la 2ª -> borde izquierdo de la
   1ª) aplica un FUNDIDO de 200 px para que el horizonte no salte al
   repetirse la textura (medición: sin fundido la costura da dif=45).
2) Genera la TEXTURA DE ARENA sin costuras `arena.jpg` (1024×1024) para el
   suelo real del desierto: ruido FFT periódico + grano + ondulaciones +
   piedritas, color calibrado con el suelo pintado de la panorámica
   (RGB 165,112,65).
3) Copia la música de la escena `vagon.mp3` a los assets del campeonato.
"""
import os
import shutil
import numpy as np
from PIL import Image, ImageDraw

BASE = '/home/z/my-project/game/championships/oeste/assets'
PXDIR = os.path.join(BASE, 'parallax')
RNG = np.random.default_rng(21111)


def stitch_pano():
    p1 = Image.open(os.path.join(PXDIR, 'p1_paisajedesierto1.png')).convert('RGBA')
    p2 = Image.open(os.path.join(PXDIR, 'p1_paisajedesierto2.png')).convert('RGBA')
    w, h = p1.size
    a1 = np.array(p1, dtype=np.float32)
    a2 = np.array(p2, dtype=np.float32)
    B = 200  # ancho del fundido del bucle
    ramp = np.linspace(0.0, 1.0, B, dtype=np.float32)[None, :, None]
    tail = a2[:, -B:, :]
    head = a1[:, :B, :]
    a2[:, -B:, :] = tail * (1.0 - ramp) + head * ramp
    canvas = np.concatenate([a1, a2], axis=1).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(canvas, 'RGBA')
    out.save(os.path.join(PXDIR, 'p1_horizonte.png'), optimize=True)
    print('p1_horizonte.png', out.size)


def _periodic_noise(h, w, beta=1.25, seed_shift=0):
    """Ruido suave PERFECTAMENTE periódico vía FFT (espectro 1/f^beta)."""
    white = np.random.default_rng(9001 + seed_shift).standard_normal((h, w))
    spec = np.fft.rfft2(white)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fy * fy + fx * fx) + 1e-6
    mask = 1.0 / np.power(f, beta)
    mask[0, 0] = 0.0
    n = np.fft.irfft2(spec * mask, s=(h, w))
    n -= n.mean()
    mx = np.abs(n).max() + 1e-6
    return n / mx


def make_sand():
    S = 1024
    base = np.array([168.0, 116.0, 70.0])
    img = np.zeros((S, S, 3), dtype=np.float32)
    for c in range(3):
        img[:, :, c] = base[c]

    # 1) ondulación amplia del terreno (±11) — dos escalas periódicas
    und = (_periodic_noise(S, S, 1.15, 1) * 8.0 +
           _periodic_noise(S, S, 2.1, 2) * 4.0)
    img += und[:, :, None]

    # 2) ondulaciones de viento (crestas suaves ±4), periódicas en ambos ejes
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rip = np.sin(2 * np.pi * (3 * xx / S) +
                 1.6 * np.sin(2 * np.pi * 2 * yy / S) +
                 2.4 * np.sin(2 * np.pi * 1 * yy / S))
    img += (rip * 3.5)[:, :, None]

    # 3) grano fino por píxel (±7) — aleatorio plano: ya es periódico al tile
    grain = RNG.uniform(-7, 7, (S, S, 1)).astype(np.float32)
    img += grain

    # 4) piedritas y motas con wrap (dibujo desplazado en 9 posiciones)
    cv = Image.fromarray(img.clip(0, 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(cv)
    for _ in range(300):
        x, y = int(RNG.integers(0, S)), int(RNG.integers(0, S))
        r = float(RNG.uniform(0.7, 2.6))
        dark = RNG.random() < 0.62
        g = int(RNG.uniform(14, 30))
        col = (int(base[0] - g), int(base[1] - g), int(base[2] - g * 0.8)) \
            if dark else (int(base[0] + g * 0.7), int(base[1] + g * 0.6),
                          int(base[2] + g * 0.4))
        for dx in (-S, 0, S):
            for dy in (-S, 0, S):
                d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                          fill=col)
    # ramitas secas finas
    for _ in range(90):
        x, y = int(RNG.integers(0, S)), int(RNG.integers(0, S))
        ln = float(RNG.uniform(4, 11))
        ang = float(RNG.uniform(0, np.pi))
        x2, y2 = x + ln * np.cos(ang), y + ln * np.sin(ang)
        col = (int(base[0] - 34), int(base[1] - 30), int(base[2] - 22))
        for dx in (-S, 0, S):
            for dy in (-S, 0, S):
                d.line([x + dx, y + dy, x2 + dx, y2 + dy],
                       fill=col, width=1)

    # 5) verificación de costuras (wrap) y guardado
    arr = np.array(cv, dtype=np.float32)
    dv = np.abs(arr[:, 0, :] - arr[:, -1, :]).mean()
    dh = np.abs(arr[0, :, :] - arr[-1, :, :]).mean()
    print(f'arena bordes: vert={dv:.1f} horiz={dh:.1f} (<=30 OK)')
    cv.save(os.path.join(PXDIR, 'arena.jpg'), quality=90)
    # vista previa 2x2 para inspección visual
    prev = Image.new('RGB', (S * 2, S * 2))
    for i in range(2):
        for j in range(2):
            prev.paste(cv, (i * S, j * S))
    prev.resize((768, 768)).save('/home/z/my-project/scripts/arena_preview.png')
    print('arena.jpg OK')


def copy_music():
    src = '/home/z/my-project/upload/vagon.mp3'
    dst = os.path.join(BASE, 'vagon.mp3')
    shutil.copyfile(src, dst)
    print('vagon.mp3 ->', dst, os.path.getsize(dst), 'bytes')


if __name__ == '__main__':
    stitch_pano()
    make_sand()
    copy_music()
    print('ASSETS v2.111 LISTOS')

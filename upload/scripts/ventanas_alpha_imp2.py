#!/usr/bin/env python3
"""v3.5.1 · Recorta el CRISTAL de los ventanales laterales del Reactor de
impulso (izquierda.png / derecha.png) para que sea transparente de verdad.
Informe del dueño: «las ventanas tienen transparencia y se debe respetar
para ver el exterior» (espacio negro + partículas de velocidad lumínica).

Método: el cristal (espacio azul oscuro + Tierra azul) es la MANCHA AZUL
más grande dentro de la banda central de la pared; sus agujeros (nubes,
sol) se cierran con fill_holes. El marco metálico (gris, sin dominancia
azul) queda fuera; una erosión + borde suave evitan morder la moldura."""
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = '/home/z/my-project/public/championships/estacion_orbital/assets/reactor_impulso'

def cristal(nombre):
    img_path = f'{BASE}/{nombre}.png'
    im = Image.open(img_path).convert('RGBA')
    a = np.array(im)
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    bluish = (b > r + 18) & (b > 60)
    banda = np.zeros_like(bluish)
    banda[130:640, 520:1640] = True       # el ventanal vive en esta banda
    m = bluish & banda
    lbl, n = ndimage.label(m)
    sizes = ndimage.sum(m, lbl, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    mancha = ndimage.binary_fill_holes(lbl == big)
    # v2: sellar fugas por las juntas de sombra — el cristal es una banda
    # ANCHA; cualquier px por ENCIMA de la primera fila ancha (> 400 px) es
    # fuga (bolsa de sombra sobre el marco) y vuelve a ser opaco
    anchos = mancha.sum(axis=1)
    filas_anchas = np.where(anchos > 400)[0]
    if len(filas_anchas):
        mancha[:filas_anchas[0] + 1, :] = False
    ys, xs = np.where(mancha)
    print(f'{nombre}: cristal {int(mancha.sum())} px · bbox x {xs.min()}..{xs.max()} · y {ys.min()}..{ys.max()}')
    # erosionar 2 px para no morder la moldura + borde suave de 2 px
    nucleo = ndimage.binary_erosion(mancha, iterations=2)
    suave = ndimage.gaussian_filter(nucleo.astype(float), sigma=1.1)
    alpha = a[:, :, 3].astype(float)
    alpha = np.minimum(alpha, 255.0 * (1.0 - np.clip(suave * 1.5, 0, 1)))
    a[:, :, 3] = alpha.astype(np.uint8)
    out = Image.fromarray(a)
    out.save(img_path)
    prev = Image.new('RGBA', im.size, (255, 0, 200, 255))
    prev.alpha_composite(out)
    prev.convert('RGB').save(f'{BASE}/{nombre}_preview.jpg', quality=88)
    print('  guardado:', img_path)

cristal('izquierda')
cristal('derecha')

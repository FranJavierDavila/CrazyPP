#!/usr/bin/env python3
# Hojas de contacto r72: 30 capturas → 3 láminas (2 columnas × 5 filas)
from PIL import Image
import os

CAP = '/home/z/my-project/download/r72_capturas'
SAL = '/home/z/my-project/download/r72_capturas'

ORDEN1 = ['main', 'rankini', 'rank', 'rankme', 'champs',
          'champuno', 'champhist', 'train', 'trainarea', 'trainext']
ORDEN2 = ['carrera', 'carreradiv', 'opts', 'optsJuego', 'optsSala',
          'optsSonido', 'optsVisual', 'optsPerfil', 'optsRendi', 'optsPala']
ORDEN3 = ['optsSalaRoom', 'optsSalaMesa', 'optsSalaBola', 'optsSalaHall',
          'multi', 'join', 'name', 'gripname', 'hallask', 'salirask']

CW, CH = 620, 350   # celda
COLS, FILAS = 2, 5

def lamina(orden, nombre):
    lam = Image.new('RGB', (CW * COLS, CH * FILAS + 20 * FILAS), (12, 14, 22))
    for i, pg in enumerate(orden):
        p = os.path.join(CAP, pg + '.png')
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert('RGB')
        im.thumbnail((CW, CH))
        x = (i % COLS) * CW
        y = (i // COLS) * (CH + 20)
        lam.paste(im, (x + (CW - im.width) // 2, y + 18))
        from PIL import ImageDraw
        d = ImageDraw.Draw(lam)
        d.text((x + 8, y + 2), pg, fill=(255, 210, 87))
    lam.save(os.path.join(SAL, nombre), quality=80)
    print(nombre, lam.size)

lamina(ORDEN1, 'lamina1_ranking_train.png')
lamina(ORDEN2, 'lamina2_ajustes.png')
lamina(ORDEN3, 'lamina3_sala_teclados.png')

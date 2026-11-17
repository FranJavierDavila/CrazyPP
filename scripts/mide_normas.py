#!/usr/bin/env python3
"""Mide el rectángulo interior útil de los 3 carteles de normas (1024x512)."""
from PIL import Image

UP = '/home/z/my-project/upload/'
FILES = {
    'locura': 'clown_normas.png',
    'magia': 'Wizard_normas.png',
    'oeste': 'forajido_normas.png',
}

for tema, fn in FILES.items():
    im = Image.open(UP + fn).convert('RGBA')
    W, H = im.size
    px = im.load()
    cx, cy = W // 2, H // 2

    def lum(p):
        return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]

    # recorrido desde el centro hacia cada borde: el interior es oscuro y
    # opaco; el marco es dorado/bronce (luminancia alta) o transparente
    def walk(dx, dy, thr=105):
        x, y = cx, cy
        while 0 <= x < W and 0 <= y < H:
            p = px[x, y]
            if p[3] < 200 or lum(p) > thr:
                return x, y
            x += dx; y += dy
        return x - dx, y - dy

    lx, _ = walk(-1, 0)
    rx, _ = walk(1, 0)
    _, ty = walk(0, -1)
    _, by = walk(0, 1)
    print(f'{tema:8s} {fn}: interior x [{lx}..{rx}] y [{ty}..{by}]  '
          f'= {rx-lx+1}x{by-ty+1}px  (centro luminancia {lum(px[cx,cy]):.0f})')

    # muestras de luminancia en la línea de centro para verificar el salto
    row = [f'{lx}:{lum(px[lx,cy]):.0f}', f'{lx-6}:{lum(px[lx-6,cy]):.0f}',
           f'{rx}:{lum(px[rx,cy]):.0f}', f'{rx+6}:{lum(px[rx+6,cy]):.0f}']
    print('   bordes horizontales (x:lum):', ' '.join(row))

    # luminancia media del interior (para el scrim)
    tot = 0; n = 0
    for yy in range(ty + 10, by - 10, 12):
        for xx in range(lx + 10, rx - 10, 12):
            tot += lum(px[xx, yy]); n += 1
    print(f'   luminancia media interior: {tot/n:.1f}   '
          f'alpha esquinas: {px[3,3][3]}')

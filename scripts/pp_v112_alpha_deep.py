#!/usr/bin/env python3
"""Medición fina de alfa PARCIAL (0<a<128 y 128<=a<255) + composiciones para inspección visual."""
from PIL import Image
import os, glob

PAR = '/home/z/my-project/game/championships/oeste/assets/parallax'
OUT = '/home/z/my-project/download/inspect'
os.makedirs(OUT, exist_ok=True)

def checker(size=16):
    """Fondo de cuadros magenta/gris para visualizar transparencia."""
    from PIL import ImageDraw
    cv = Image.new('RGB', (4096, 4096), (200, 200, 200))
    d = ImageDraw.Draw(cv)
    for y in range(0, 4096, size):
        for x in range(0, 4096, size):
            if (x // size + y // size) % 2 == 0:
                d.rectangle([x, y, x + size - 1, y + size - 1], fill=(160, 60, 160))
    return cv

def partial(path):
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    total = w * h
    a = list(im.getchannel('A').getdata())
    zero = sum(1 for v in a if v < 8)
    lo = sum(1 for v in a if 8 <= v < 128)
    hi = sum(1 for v in a if 128 <= v < 250)
    op = sum(1 for v in a if v >= 250)
    # RGB medio de la banda parcial baja (8..128): ¿oscura?
    px = list(im.getdata())
    idxs = [i for i, v in enumerate(a) if 8 <= v < 128]
    if idxs:
        step = max(1, len(idxs) // 5000)
        sel = idxs[::step]
        r = sum(px[i][0] for i in sel) / len(sel)
        g = sum(px[i][1] for i in sel) / len(sel)
        b = sum(px[i][2] for i in sel) / len(sel)
        rgb = f"({r:.0f},{g:.0f},{b:.0f})"
    else:
        rgb = "-"
    n = os.path.basename(path)
    return f"{n:32s} a<8:{zero*100/total:5.1f}%  8<=a<128:{lo*100/total:5.1f}% RGB={rgb:15s} 128<=a<250:{hi*100/total:5.1f}%  a>=250:{op*100/total:5.1f}%"

print("== PANO P1 ==")
for f in ['p1_horizonte.png', 'p1_paisajedesierto1.png', 'p1_paisajedesierto2.png']:
    print(partial(os.path.join(PAR, f)))
print("\n== MUESTRA PIEZAS p2/p3/p4 ==")
for f in ['p2_estructura1.png', 'p2_roca1.png', 'p2_rancho1.png', 'p3_arbusto1.png', 'p3_poste1.png',
          'p4_cactus1.png', 'p4_caseta.png', 'p4_roca1.png', 'p4_senal.png', 'p4_valla.png']:
    print(partial(os.path.join(PAR, f)))
print("\n== GALOPE ==")
for f in sorted(glob.glob('/home/z/my-project/upload/galope*.png')):
    print(partial(f))

# Composiciones para inspección visual (el pano completo reducido + galopes)
ck = checker()
pano = Image.open(os.path.join(PAR, 'p1_horizonte.png')).convert('RGBA')
pano = pano.resize((2172, 262))
ck.crop((0, 0, 2172, 262)).paste(pano, (0, 0), pano)
ck.crop((0, 0, 2172, 262)).save(os.path.join(OUT, 'p1_horizonte_alfa.png'))

for f in sorted(glob.glob('/home/z/my-project/upload/galope*.png')):
    im = Image.open(f).convert('RGBA').resize((384, 384))
    base = checker(24).crop((0, 0, 384, 384))
    base.paste(im, (0, 0), im)
    base.save(os.path.join(OUT, os.path.basename(f)))

# Sprite sheet 3 frames (galope1|2|3) — también lo dejamos listo para el juego
frames = [Image.open(f'/home/z/my-project/upload/galope{i}.png').convert('RGBA') for i in (1, 2, 3)]
sheet = Image.new('RGBA', (512 * 3, 512), (0, 0, 0, 0))
for i, fr in enumerate(frames):
    sheet.paste(fr, (i * 512, 0), fr)
sheet.save(os.path.join(OUT, 'galope_sprite_preview.png'))
sheet.save(PAR + '/galope_forajido.png')  # ya colocado en assets del juego
print("\nSprite sheet 1536x512 ->", PAR + '/galope_forajido.png')
print("Inspecciones en", OUT)

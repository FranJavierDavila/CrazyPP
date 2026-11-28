#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161 · paquete de arte de la CARTELA MAIN (tema UI_Default):
1 · copia los 14 PNG del dueño (upload/Main.zip → public/assets/ui/UI_Default/Main/)
2 · genera fondo.png (1472×1400 = rodaja de la panela C): tonos azulados,
    gradiente de transparencia hacia los bordes y esquinas curvas al MISMO
    radio físico de la panela (0,036 m ≈ 42 px), con resplandores tras el
    logo y las palas. El hall se adivina detrás (alfa variable)."""
import os, shutil
from PIL import Image, ImageDraw, ImageFilter

ORIGEN = '/home/z/my-project/upload/_extraido_main/Main'
DEST = '/home/z/my-project/public/assets/ui/UI_Default/Main'
W, H = 1472, 1400          # rodaja C del lienzo panorámico 3696×1400
RADIO = 42                 # = radioEsquinaM 0,036 m · altoM 1,20 · w 1472

os.makedirs(DEST, exist_ok=True)
n = 0
for f in sorted(os.listdir(ORIGEN)):
    if f.lower().endswith('.png'):
        shutil.copy2(os.path.join(ORIGEN, f), os.path.join(DEST, f))
        n += 1
print(f'✓ {n} PNG del dueño copiados a {DEST}')

# ── fondo.png ────────────────────────────────────────────────────────────
base = Image.new('RGBA', (W, H), (0, 0, 0, 0))

# gradiente vertical azul profundo (tonos del mock: navy → azul medio)
grad = Image.new('RGBA', (1, H))
for y in range(H):
    t = y / (H - 1)
    if t < 0.45:                       # arriba: navy → azul medio
        u = t / 0.45
        r = int(10 + (18 - 10) * u); g = int(22 + (41 - 22) * u); b = int(48 + (92 - 48) * u)
    else:                              # abajo: azul medio → azul noche
        u = (t - 0.45) / 0.55
        r = int(18 + (7 - 18) * u); g = int(41 + (16 - 41) * u); b = int(92 + (36 - 92) * u)
    grad.putpixel((0, y), (r, g, b, 255))
grad = grad.resize((W, H))
base.alpha_composite(grad)

# resplandores radiales (cian tras el logo · azul tras las palas)
def resplandor(img, cx, cy, rad, color, alfa):
    capa = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color + (alfa,))
    capa = capa.filter(ImageFilter.GaussianBlur(rad * 0.45))
    img.alpha_composite(capa)

resplandor(base, 736, 330, 520, (53, 196, 255), 62)    # tras el logo
resplandor(base, 480, 1060, 500, (30, 95, 255), 48)    # tras las palas
resplandor(base, 1180, 900, 420, (53, 196, 255), 26)   # aire tras los botones

# viñeta suave (esquinas algo más oscuras)
vin = Image.new('L', (W, H), 0)
dv = ImageDraw.Draw(vin)
dv.rectangle((120, 120, W - 120, H - 120), fill=255)
vin = vin.filter(ImageFilter.GaussianBlur(160))
oscuro = Image.new('RGBA', (W, H), (2, 6, 16, 110))
vin_inv = vin.point(lambda p: 255 - p)
base = Image.composite(base, Image.alpha_composite(base, oscuro), vin)

# máscara: esquinas curvas (radio físico) + gradiente de transparencia:
# alfa ~0.95 en el centro → ~0.78 en los bordes → 0 fuera de la curva
masc = Image.new('L', (W, H), 0)
dm = ImageDraw.Draw(masc)
dm.rounded_rectangle((0, 0, W - 1, H - 1), RADIO, fill=255)

dist = Image.new('L', (W, H), 0)
dd = ImageDraw.Draw(dist)
for margen in (300, 200, 120, 60, 24):
    dd.rounded_rectangle((margen, margen, W - 1 - margen, H - 1 - margen),
                         max(RADIO - margen // 3, 8), fill=255)
dist = dist.point(lambda p: 255 - p)          # 255 en el borde, 0 al centro
dist = dist.filter(ImageFilter.GaussianBlur(70))
alfa_centro, alfa_borde = 242, 196
mapa_alfa = dist.point(lambda p: alfa_centro - (alfa_centro - alfa_borde) * p // 255)
masc = Image.composite(mapa_alfa, Image.new('L', (W, H), 0), masc.point(lambda p: p))
r, g, b, a = base.split()
base = Image.merge('RGBA', (r, g, b, Image.composite(a, Image.new('L', (W, H), 0),
                    masc.point(lambda p: min(p, alfa_centro)))))

# borde luminoso fino (inset 8 px, cian pálido)
bor = Image.new('RGBA', (W, H), (0, 0, 0, 0))
db = ImageDraw.Draw(bor)
db.rounded_rectangle((8, 8, W - 9, H - 9), RADIO - 8,
                     outline=(150, 205, 255, 130), width=3)
halo = bor.filter(ImageFilter.GaussianBlur(6))
base = Image.alpha_composite(base, halo)
base = Image.alpha_composite(base, bor)

base.save(os.path.join(DEST, 'fondo.png'), optimize=True)
kb = os.path.getsize(os.path.join(DEST, 'fondo.png')) / 1024
print(f'✓ fondo.png {W}×{H} · {kb:.0f} KB · radio {RADIO}px · alfa {alfa_centro}→{alfa_borde}')

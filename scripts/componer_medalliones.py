#!/usr/bin/env python3
# r137 · 12ª pasada — compone los glifos del kit sobre el medallión del menú.
# Los PNG actuales del juego traen su propio disco (estilo medallón brillante);
# los glifos del kit son desnudos. El sustituto mantiene el plato (disco navy
# con borde y brillo superior, paleta del kit = paleta del juego) y estrena
# glifo AAA centrado. Salida: staging png_final/ 256×256 RGBA.
import os
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(BASE, 'iconos_plantilla', 'png')
FIN_DIR = os.path.join(BASE, 'iconos_plantilla', 'png_final')
os.makedirs(FIN_DIR, exist_ok=True)

FONDO_C = (13, 28, 56)      # centro del disco (bg-card del kit #0A1730)
FONDO_B = (24, 47, 92)      # borde superior (más claro, brillo)
RIM = (35, 69, 122)         # rim del kit (--border-ui #23457A)
RIM_HI = (72, 118, 190)     # rim con luz


def medallion(radio_px=124):
    """disco navy con rim y brillo superior — replica del estilo actual."""
    S = 4  # supermuestreo
    D = radio_px * 2 * S
    cx = cy = D // 2
    r = D // 2 - 2 * S
    # gradiente vertical REAL: una fila por línea (sin elipses solapadas —
    # la primera versión producía bandas horizontales visibles)
    grad = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(D):
        t = min(max((y - (cy - r)) / (2 * r), 0.0), 1.0)
        c = tuple(int(FONDO_B[k] + (FONDO_C[k] - FONDO_B[k]) * t) for k in range(3))
        gd.line((0, y, D, y), fill=c + (255,))
    mascara = Image.new('L', (D, D), 0)
    ImageDraw.Draw(mascara).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    im = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    im.paste(grad, (0, 0), mascara)
    d = ImageDraw.Draw(im)
    # rim exterior
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RIM + (255,), width=4 * S)
    d.ellipse((cx - r + 2 * S, cy - r + 2 * S, cx + r - 2 * S, cy + r - 2 * S),
              outline=RIM_HI + (110,), width=2 * S)
    # brillo superior (arco elíptico suave)
    brillo = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    db = ImageDraw.Draw(brillo)
    db.ellipse((cx - int(r * 0.78), cy - int(r * 0.92),
                cx + int(r * 0.78), cy - int(r * 0.10)), fill=(255, 255, 255, 26))
    brillo = brillo.filter(ImageFilter.GaussianBlur(6 * S))
    im.alpha_composite(Image.composite(brillo, Image.new('RGBA', (D, D), (0, 0, 0, 0)), mascara))
    return im.resize((radio_px * 2, radio_px * 2), Image.LANCZOS)


COMPUESTOS = {
    'entrenar': 'entrenar',
    'multijugador': 'multijugador',
    'campeonatos': 'campeonatos',
    'ranking': 'ranking',
    'vestibulo': 'vestibulo',
    'ajustes': 'ajustes',
    'sala': 'sala',
    'audio': 'audio',
    'usuario': 'usuario',
    'partido': 'candidato_partido_jugar',
}

plato = medallion(124)
LIENZO = 256
for destino, fuente in COMPUESTOS.items():
    ruta = os.path.join(PNG_DIR, f'icono_{fuente}.png')
    glifo = Image.open(ruta).convert('RGBA')
    G = 158  # el glifo ocupa ~62% del disco (los actuales ~60-65%)
    glifo = glifo.resize((G, G), Image.LANCZOS)
    final = Image.new('RGBA', (LIENZO, LIENZO), (0, 0, 0, 0))
    final.alpha_composite(plato, ((LIENZO - plato.width) // 2, (LIENZO - plato.height) // 2))
    final.alpha_composite(glifo, (LIENZO // 2 - G // 2, LIENZO // 2 - G // 2))
    salida = os.path.join(FIN_DIR, f'icono_{destino}.png')
    final.save(salida)
    print(f'  ✓ icono_{destino}.png  ← {fuente}')

# hoja de contactos final para verificación visual
from PIL import ImageFont
claves = sorted(COMPUESTOS.keys())
CEL, W = 200, 130
hoja = Image.new('RGB', (len(claves) * CEL, CEL + 30), (10, 23, 48))
d = ImageDraw.Draw(hoja)
try:
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except Exception:
    fnt = ImageFont.load_default()
for i, c in enumerate(claves):
    im = Image.open(os.path.join(FIN_DIR, f'icono_{c}.png')).resize((W, W))
    hoja.paste(im, (i * CEL + 35, 20), im)
    d.text((i * CEL + 35 + W // 2 - 40, CEL - 6), c, fill=(248, 250, 252), font=fnt)
hoja.save(os.path.join(FIN_DIR, 'hoja_final.png'))
print('hoja final lista')

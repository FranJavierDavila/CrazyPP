#!/usr/bin/env python3
# r137 · 12ª pasada — extrae los iconos volumétricos (sección F) del UI Kit
# AAA adjunto y los renderiza a PNG 256×256 (resolución de ICONOS_MENUS).
# Los SVG quedan en scripts/iconos_plantilla/svg/ y los PNG en png/
# (staging: la copia a public/assets/externos/ es un paso aparte, revisado).
import re, os
import cairosvg

BASE = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(BASE, '..', 'upload', 'gemini-code-1794944450526.html')
SVG_DIR = os.path.join(BASE, 'iconos_plantilla', 'svg')
PNG_DIR = os.path.join(BASE, 'iconos_plantilla', 'png')
os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

s = open(PLANTILLA, encoding='utf-8').read()
bloques = []
for m in re.finditer(r'<svg\b[^>]*>.*?</svg>', s, re.S):
    antes = s[:m.start()]
    h3 = re.findall(r'<h3[^>]*>([^<]{2,60})</h3>', antes)
    titulo = h3[-1].strip() if h3 else '?'
    bloques.append((titulo, m.group(0)))

# mapeo plantilla → claves de ICONOS_MENUS (c02:931): sólo equivalencias claras
MAPEO = {
    'ico_entrenar': 'entrenar',
    'ico_multijugador': 'multijugador',
    'ico_campeonatos': 'campeonatos',
    'ico_escalera': 'ranking',
    'ico_hall': 'vestibulo',
    'ico_ajustes': 'ajustes',
    'ico_sala_escena': 'sala',
    'ico_sonido': 'audio',
    'ico_perfiles': 'usuario',
    'ico_jugar': 'candidato_partido_jugar',
    'ico_vr_pala': 'candidato_partido_pala',
}

extraidos = {}
for titulo, clave in MAPEO.items():
    # el ancla REAL es el comentario <!-- ico_x --> que precede a su tarjeta
    # (el h3 va DESPUÉS del svg en el DOM y la asociación por h3 desplazaba
    # los iconos — detectado en la hoja de contactos de la primera pasada)
    ancla = s.find(f'<!-- {titulo} -->')
    assert ancla >= 0, f'comentario {titulo} no encontrado'
    m = re.search(r'<svg\b[^>]*>.*?</svg>', s[ancla:], re.S)
    assert m, f'svg tras {titulo} no encontrado'
    svg = m.group(0)
    # los iconos del kit son 128×128; asegurar tamaño de salida 256
    svg2 = svg.replace('width="128" height="128"', '')
    ruta_svg = os.path.join(SVG_DIR, f'{clave}.svg')
    open(ruta_svg, 'w', encoding='utf-8').write(svg2)
    ruta_png = os.path.join(PNG_DIR, f'icono_{clave}.png')
    cairosvg.svg2png(bytestring=svg2.encode('utf-8'), write_to=ruta_png,
                     output_width=256, output_height=256)
    extraidos[clave] = ruta_png
    print(f'  ✓ {titulo:20s} → icono_{clave}.png')
# hoja de contactos (una imagen para verificación visual)
from PIL import Image
claves = sorted(extraidos.keys())
n = len(claves)
cols, filas = 6, (n + 5) // 6
CEL = 180
hoja = Image.new('RGBA', (cols * CEL, filas * CEL), (10, 23, 48, 255))
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(hoja)
try:
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception:
    fnt = ImageFont.load_default()
for i, clave in enumerate(claves):
    x, y = (i % cols) * CEL, (i // cols) * CEL
    im = Image.open(extraidos[clave]).convert('RGBA')
    hoja.alpha_composite(im.resize((140, 140)), (x + 20, y + 8))
    d.text((x + 12, y + 152), clave[:24], fill=(248, 250, 252, 255), font=fnt)
ruta_hoja = os.path.join(PNG_DIR, 'hoja_contactos.png')
hoja.convert('RGB').save(ruta_hoja, quality=90)
print('hoja de contactos:', ruta_hoja)

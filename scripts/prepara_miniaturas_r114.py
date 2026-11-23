#!/usr/bin/env python3
"""prepara_miniaturas_r114.py — extrae el hero base64 y genera miniaturas
PNG de las piezas de arte clave para embeberlas en el documento docx.
Salida: download/_thumbs_r114/*.png + scripts/_thumbs_dims.json"""
import base64
import json
import re
from pathlib import Path
from PIL import Image

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src/game'
OUT = RAIZ / 'download/_thumbs_r114'
OUT.mkdir(parents=True, exist_ok=True)
MAXW = 420  # ancho máximo de miniatura


def mini(p_origen, nombre, crop=None):
    im = Image.open(p_origen)
    im.load()
    if crop:  # recorte fraccional (l, t, r, b) para mostrar solo una zona
        im = im.crop((int(crop[0] * im.width), int(crop[1] * im.height),
                      int(crop[2] * im.width), int(crop[3] * im.height)))
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)),
                       Image.LANCZOS)
    destino = OUT / f'{nombre}.png'
    im.save(destino)
    return {'f': destino.name, 'w': im.width, 'h': im.height}


# 1. hero = primera data:image/jpeg de 03_body.html (línea 16-17)
cuerpo = (SRC / '03_body.html').read_text(encoding='utf-8', errors='replace')
m = re.search(r'data:image/jpeg;base64,([A-Za-z0-9+/=]+)', cuerpo)
hero = Image.open(__import__('io').BytesIO(
    base64.b64decode(m.group(1) + '=' * (-len(m.group(1)) % 4))))
hero_path = OUT / '_hero_orig.jpg'
hero.save(hero_path, 'JPEG')

dims = {
    'hero': mini(hero_path, 'thumb_hero'),
    'arcano': mini(RAIZ / 'public/assets/hall/arcano.png', 'thumb_arcano'),
    'candado': mini(RAIZ / 'public/assets/hall/candado.png', 'thumb_candado'),
    'palas': mini(RAIZ / 'public/assets/hall/palas.png', 'thumb_palas'),
    'museo_frente': mini(RAIZ / 'public/assets/hall/frente.jpg',
                         'thumb_museo_frente'),
    'museo_suelo': mini(RAIZ / 'public/assets/hall/suelo.jpg',
                        'thumb_museo_suelo'),
    'museo_techo': mini(RAIZ / 'public/assets/hall/techo.jpg',
                        'thumb_museo_techo'),
    'neon_frente': mini(RAIZ / 'public/assets/hall/neon/frente.jpg',
                        'thumb_neon_frente'),
    'dojo_frente': mini(RAIZ / 'public/assets/hall/dojo/frente.jpg',
                        'thumb_dojo_frente'),
    'poster_win': None,  # se extrae del base64 de c08 abajo
}
hero_path.unlink()

# 2. poster de victoria (primer WebP de c08:2657)
c08 = (SRC / 'core/c08_hall_hud.js').read_text(encoding='utf-8',
                                               errors='replace')
m2 = re.search(r'data:image/webp;base64,([A-Za-z0-9+/=]+)', c08)
if m2:
    pw = Image.open(__import__('io').BytesIO(
        base64.b64decode(m2.group(1) + '=' * (-len(m2.group(1)) % 4))))
    p2 = OUT / '_poster_orig.webp'
    pw.save(p2, 'WEBP')
    dims['poster_win'] = mini(p2, 'thumb_poster_win')
    p2.unlink()

(RAIZ / 'scripts/_thumbs_dims.json').write_text(
    json.dumps(dims, ensure_ascii=False, indent=1), encoding='utf-8')
for k, d in dims.items():
    print(f"  {k:14s} {json.dumps(d)}")
print(f"✓ {len([d for d in dims.values() if d])} miniaturas en {OUT}")

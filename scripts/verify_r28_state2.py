#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificación 2: dimensiones JPEG de salones + localización catálogo poderes + voces."""
import os, re, json, struct

ROOT = '/home/z/my-project/upload'
out = {}

def jpeg_size(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:2] != b'\xff\xd8':
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i+1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack('>HH', data[i+5:i+9])
            return (w, h)
        elif marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
        else:
            seglen = struct.unpack('>H', data[i+2:i+4])[0]
            i += 2 + seglen
    return None

HALL_SIZES = {
    'frente.jpg': (1849, 864), 'fondo.jpg': (1849, 864),
    'izquierda.jpg': (2395, 864), 'derecha.jpg': (2395, 864),
    'suelo.jpg': (1296, 1678), 'techo.jpg': (1296, 1678),
}
halls = {}
for h in sorted(os.listdir(os.path.join(ROOT, 'public/assets/hall'))):
    hd = os.path.join(ROOT, 'public/assets/hall', h)
    if not os.path.isdir(hd):
        continue
    res = {}
    ok = 0
    for fn, (ew, eh) in HALL_SIZES.items():
        fp = os.path.join(hd, fn)
        if os.path.exists(fp):
            sz = jpeg_size(fp)
            good = sz == (ew, eh)
            ok += good
            res[fn] = f"{'OK' if good else 'BAD'} {sz[0]}x{sz[1]}" if sz else 'BAD?'
        else:
            res[fn] = 'MISSING'
    res['SCORE'] = f'{ok}/6'
    halls[h] = res
out['halls'] = halls

# catálogo de poderes: dónde vive "Oscuridad"
hits = {}
srcdir = os.path.join(ROOT, 'src/game/core')
for fn in sorted(os.listdir(srcdir)):
    if not fn.endswith('.js'):
        continue
    txt = open(os.path.join(srcdir, fn), encoding='utf-8', errors='replace').read()
    n = txt.count('Oscuridad')
    hielo = txt.count('Hielo')
    if n or hielo:
        hits[fn] = {'Oscuridad': n, 'Hielo': hielo}
out['src_Oscuridad_Hielo'] = hits

# voces de poderes: buscar rutas de voz en c12
c12 = open(os.path.join(srcdir, 'c12_pingponggame.js'), encoding='utf-8', errors='replace').read()
voces = sorted(set(re.findall(r'voces?/[^"\'\s\)]+', c12)))[:14]
out['voces_refs'] = voces
# strings de anuncio de poder
anuncios = sorted(set(re.findall(r'¡[Ss]úper[^!]{0,30}!', c12)))[:14]
out['anuncios'] = anuncios
# context FENIX_MUL / FENIX_CAP (¿comentario de retirada?)
for m in re.finditer(r'FENIX_(MUL|CAP)', c12):
    s = max(0, m.start() - 120)
    out.setdefault('fenix_ctx', []).append(c12[s:m.end() + 80].replace('\n', ' ')[:220])

print(json.dumps(out, ensure_ascii=False, indent=1))

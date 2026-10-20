#!/usr/bin/env python3
"""Mide las proporciones del lingote (lowpoly_gold_bar.glb) leyendo los
min/max de los accessors POSITION del chunk JSON del GLB — sin three.js."""
import json
import struct
import sys

p = '/home/z/my-project/public/championships/oeste/assets/lowpoly_gold_bar.glb'
try:
    data = open(p, 'rb').read()
except FileNotFoundError:
    # buscar en otra ruta de assets
    sys.exit('no encontrado: ' + p)

magic, ver, length = struct.unpack_from('<III', data, 0)
assert magic == 0x46546C67, 'no es GLB'
off = 12
clen, ctype = struct.unpack_from('<II', data, off)
js = json.loads(data[off + 8:off + 8 + clen])

mins, maxs = [1e9] * 3, [-1e9] * 3
for acc in js.get('accessors', []):
    if acc.get('type') == 'VEC3' and 'min' in acc and 'max' in acc:
        # solo atributos POSITION (con componentType FLOAT típico 5126)
        for i in range(3):
            mins[i] = min(mins[i], acc['min'][i])
            maxs[i] = max(maxs[i], acc['max'][i])
ext = [maxs[i] - mins[i] for i in range(3)]
mx = max(ext)
s = 0.17 / mx
print('bbox cruda   :', ['%.4f' % e for e in ext])
print('escalada     :', ['%.4f' % (e * s) for e in ext])
print('proporciones : 1 : %.3f : %.3f' % (ext[1] / mx, ext[2] / mx))
print('sepX 0.19 vs largo %.4f → hueco %.4f' % (ext[0] * s, 0.19 - ext[0] * s))
print('sepZ 0.095 vs fondo %.4f → hueco %.4f' % (ext[2] * s, 0.095 - ext[2] * s))

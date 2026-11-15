#!/usr/bin/env python3
# r72 · RE-ESPACIADO de drawMenuOptsCat (v2, regex acotada al segmento).
# Filas de btn: altura +6 (y, W, H, …). Pasos verticales: y += n → n+8.
# Ids y conducta intactos; _modeCard (CH_CARD) y barras quedan igual.
import re
import sys

PATH = '/home/z/my-project/upload/public/game.html'
s = open(PATH, encoding='utf-8').read()
orig_len = len(s)

i = s.find('drawMenuOptsCat(rects, cat) {')
if i < 0:
    print('FALLO: no encuentro drawMenuOptsCat'); sys.exit(1)
fin = i + 26270
seg = s[i:fin]
seg0 = seg

# — alturas de fila btn(id, X, y, W, H, …): H +6 —
def bump_h(m):
    h = int(m.group(2))
    return m.group(1) + str(min(h + 6, 92)) + m.group(3)

seg, n_h = re.subn(r'(, y, \d{2,3}, )(\d{2,3})(,)', bump_h, seg)
# — pasos verticales: y += n → n+8 —
def bump_y(m):
    return 'y += ' + str(int(m.group(1)) + 8) + ';'

seg, n_y = re.subn(r'y \+= (\d+);', bump_y, seg)
print(f'alturas tocadas: {n_h} · pasos tocados: {n_y}')
print('delta segmento:', len(seg) - len(seg0), 'B')
if n_h < 20 or n_y < 20:
    print('FALLO: demasiados pocos reemplazos — aborto sin escribir')
    sys.exit(1)

s = s[:i] + seg + s[fin:]
open(PATH, 'w', encoding='utf-8').write(s)
print(f'TAMAÑO: {orig_len} → {len(s)} B (delta {len(s)-orig_len:+d})')

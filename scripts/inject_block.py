#!/usr/bin/env python3
"""Injerta el bloque v2.111 en championships/oeste/index.js sustituyendo
el sistema antiguo de oleadas (líneas con anclas exactas)."""
import io, sys

P = '/home/z/my-project/game/championships/oeste/index.js'
BLOCK = io.open('/home/z/my-project/scripts/block_v2111.js', encoding='utf-8').read()

with io.open(P, encoding='utf-8') as f:
    lines = f.readlines()

# localiza anclas
i0 = i1 = -1
for i, ln in enumerate(lines):
    if 'oleadas (construcción) -----------------------' in ln:
        i0 = i
    if i0 >= 0 and ln.rstrip() == '  }' and i > i0 + 10 and 'waveTotal' in lines[i - 2] + lines[i - 1] + lines[i - 3]:
        i1 = i
        break
if i0 < 0 or i1 < 0:
    sys.exit('ANCLAS NO ENCONTRADAS i0=%d i1=%d' % (i0, i1))
print('bloque antiguo: líneas %d..%d (%d líneas)' % (i0 + 1, i1 + 1, i1 - i0 + 1))
# sanity: el bloque debe contener _mkSafe y _buildWave
seg = ''.join(lines[i0:i1 + 1])
assert '_mkSafe' in seg and '_buildWave' in seg, 'segmento inesperado'

new = lines[:i0] + [BLOCK] + lines[i1 + 1:]
with io.open(P, 'w', encoding='utf-8', newline='') as f:
    f.writelines(new)
print('injerto OK — nuevo total de líneas:', sum(1 for _ in new))

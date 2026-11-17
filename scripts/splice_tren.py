#!/usr/bin/env python3
"""v2.109: empotra la nueva TrenAction (vagón interior) en championships/oeste/index.js.
Sustituye el bloque [comentario v2.94 ETAPA 4 + clase TrenAction] por scripts/tren_v2109.js."""
import io, sys

MOD = '/home/z/my-project/crazypp/championships/oeste/index.js'
NEW = '/home/z/my-project/scripts/tren_v2109.js'

with io.open(MOD, encoding='utf-8') as f:
    lines = f.readlines()
with io.open(NEW, encoding='utf-8') as f:
    new_block = f.read()

# localizar el COMENTARIO de cabecera del bloque antiguo
i_start = None
for i, ln in enumerate(lines):
    if 'v2.94 · ETAPA 4' in ln and 'ASALTO AL TREN' in ln:
        i_start = i - 1          # la línea /* ====... inmediatamente anterior
        break
assert i_start is not None and lines[i_start].startswith('/* ==='), 'no se halla el inicio del bloque'

# localizar el COMENTARIO del HUD (fin del bloque: línea anterior al cierre de clase)
i_hud = None
for i in range(i_start, len(lines)):
    if 'HUD de las PRUEBAS' in lines[i]:
        i_hud = i - 1            # la línea /* ====... del HUD
        break
assert i_hud is not None, 'no se halla el HUD'
# el cierre de la clase son las líneas vacías/} antes del comentario del HUD
i_end = i_hud
while lines[i_end - 1].strip() == '':
    i_end -= 1
assert lines[i_end - 1].rstrip() == '}', 'el bloque no termina en }'
i_end = i_end - 1              # exclusivo: hasta la línea } inclusive -> slice[:i_end]

old_len = i_end - i_start
lines[i_start:i_end] = [new_block]
with io.open(MOD, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('OK: sustituidas %d líneas por %d (bloque nuevo %d chars)' % (old_len, new_block.count('\n') + 1, len(new_block)))

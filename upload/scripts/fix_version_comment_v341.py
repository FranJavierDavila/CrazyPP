#!/usr/bin/env python3
"""Reordena los comentarios de la línea VERSION en game.html (v3.4.1-RIV1):
comentario v3.4.1 → const → comentario histórico v3.4.0 en línea propia."""
p = '/home/z/my-project/public/game.html'
lines = open(p, encoding='utf-8').read().split('\n')
i = 1863  # línea 1864 (0-index) — const VERSION
ln = lines[i]
assert ln.lstrip().startswith("const VERSION = '3.4.1-RIV1';"), ln[:60]

sep341 = '   // v3.4.1-RIV1'
sep340 = '   // v3.4.0-IMP1 · REACTOR'
j341 = ln.index(sep341)
j340 = ln.index(sep340)
c341 = ln[j341 + 3:j340].rstrip()   # comentario nuevo (sin el histórico)
c340 = ln[j340 + 3:].rstrip()       # comentario histórico íntegro

lines[i] = '  ' + c341
lines.insert(i + 1, "  const VERSION = '3.4.1-RIV1';")
lines.insert(i + 2, '  ' + c340)
open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('OK — comentarios reordenados')

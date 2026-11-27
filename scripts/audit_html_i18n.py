#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verifica TODAS las data-i18n* de public/game.html contra I18N_STRINGS."""
import re, io

src = io.open('/home/z/my-project/src/game/core/c00_pre_three.js', encoding='utf-8').read()
lines = src.split('\n')
es_start = next(i for i, l in enumerate(lines) if l.strip() == 'es: {')
en_start = next(i for i, l in enumerate(lines) if l.strip() == 'en: {')
en_end = next(i for i in range(en_start, len(lines)) if lines[i].startswith('  },'))

def block_keys(start, end):
    return set(m.group(1) for i in range(start, end)
               for m in [re.match(r"^    ([A-Za-z0-9_]+):", lines[i])] if m)

ES = block_keys(es_start, en_start)
EN = block_keys(en_start, en_end)

html = io.open('/home/z/my-project/public/game.html', encoding='utf-8').read()
missing = []
for m in re.finditer(r'data-i18n(?:-html|-ph|-title)?="([^"]+)"', html):
    k = m.group(1)
    ln = html[:m.start()].count('\n') + 1
    if k not in ES: missing.append((ln, k, 'es'))
    if k not in EN: missing.append((ln, k, 'en'))
print("data-i18n en game.html:", len(re.findall(r'data-i18n', html)))
if missing:
    for x in missing: print("  FALTA", x)
else:
    print("  todas las data-i18n de game.html existen en es y en")

# ¿#status tiene data-i18n?
m = re.search(r'<div id="status"[^>]*>', html)
print("tag #status:", m.group(0) if m else "NO")

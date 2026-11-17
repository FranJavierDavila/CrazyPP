#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deduplicación: deja SOLO la PRIMERA declaración de cada constante del
clon (el script anterior movió el bloque pero no borró el original)."""
import re
from pathlib import Path

C12 = Path('/home/z/my-project/src/game/core/c12_pingponggame.js')
txt = C12.read_text(encoding='utf-8')

pats = [
    re.compile(r"^const PNG_PODER_CLON = 'data:image/png;base64,[^']*';$\n?", re.M),
    re.compile(r"^const VOZ_PODER_CLON = 'data:audio/mpeg;base64,[^']*';$\n?", re.M),
    re.compile(r"^const VOZ_PODER_CLON_EN = 'data:audio/mpeg;base64,[^']*';$\n?", re.M),
]
for pat in pats:
    ms = list(pat.finditer(txt))
    print(pat.pattern[:26], '→', len(ms), 'apariciones')
    # conserva la primera, borra el resto (con su salto de línea)
    for m in reversed(ms[1:]):
        txt = txt[:m.start()] + txt[m.end():]

C12.write_text(txt, encoding='utf-8')
print('DEDUP_OK')

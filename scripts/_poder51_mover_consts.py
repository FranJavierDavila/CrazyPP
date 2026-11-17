#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mueve PNG_PODER_CLON/VOZ_PODER_CLON(_EN) por ENCIMA del registro
PODERES_PALA (el array evalúa las voces en la inicialización del módulo:
declararlas después = TDZ crash «Cannot access before initialization»)."""
from pathlib import Path

C12 = Path('/home/z/my-project/src/game/core/c12_pingponggame.js')
txt = C12.read_text(encoding='utf-8')

BLOQUE = """const PNG_PODER_CLON = 'data:image/png;base64,PLACEHOLDER_CLON_PNG';
const VOZ_PODER_CLON = 'data:audio/mpeg;base64,PLACEHOLDER_CLON_ES';
const VOZ_PODER_CLON_EN = 'data:audio/mpeg;base64,PLACEHOLDER_CLON_EN';
"""

# 1) localizar las tres declaraciones reales (data URIs gigantes)
import re
pat_png = re.compile(r"^const PNG_PODER_CLON = 'data:image/png;base64,[^']*';$", re.M)
pat_voz = re.compile(r"^const VOZ_PODER_CLON = 'data:audio/mpeg;base64,[^']*';$", re.M)
pat_zen = re.compile(r"^const VOZ_PODER_CLON_EN = 'data:audio/mpeg;base64,[^']*';$", re.M)
m1, m2, m3 = pat_png.search(txt), pat_voz.search(txt), pat_zen.search(txt)
assert m1 and m2 and m3, 'no se hallaron las tres declaraciones'
trozo = m1.group(0) + '\n' + m2.group(0) + '\n' + m3.group(0)

# 2) quitarlas de donde están (y el blank line sobrante)
txt = txt.replace(trozo + '\n\n', '', 1)

# 3) insertarlas justo ANTES de «/** Registro de poderes»
ancla = '/** Registro de poderes (v3.6.36\u2192v3.6.50)'
assert ancla in txt
txt = txt.replace(ancla, trozo + '\n' + ancla, 1)

C12.write_text(txt, encoding='utf-8')
print('MOVIDO_OK — orden: assets → registro (TDZ resuelto)')

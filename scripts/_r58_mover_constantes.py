#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r58 · MUEVE el bloque de constantes del SÚPER CLONACIÓN (CLON_* +
VOZ_SEL_* + VOZ_PODER_CLON + PNG_PODER_CLON) a ANTES del registro
PODERES_PALA — el registro evalúa VOZ_PODER_CLON/PNG_PODER_CLON en carga
y con las constantes DEBAJO reventaba con TDZ («Cannot access
'VOZ_PODER_CLON' before initialization»). Idempotente."""
import sys
from pathlib import Path

C12 = Path('/home/z/my-project/src/game/core/c12_pingponggame.js')
txt = C12.read_text(encoding='utf-8')

INI = "// v3.6.50 (r58) · SÚPER CLONACIÓN (5.º poder; spec completa del dueño):"
FIN = "const PNG_PODER_CLON = "
REG = "const PODERES_PALA = ["

i0 = txt.find(INI)
if i0 < 0:
    print('el bloque CLON no está: nada que hacer')
    sys.exit(0)
j0 = txt.find(FIN, i0)
if j0 < 0:
    print('FALLO: fin del bloque no encontrado')
    sys.exit(1)
j1 = txt.find("';", j0)
if j1 < 0:
    print('FALLO: cierre del PNG no encontrado')
    sys.exit(1)
j1 += 2
bloque = txt[i0:j1]
if bloque.find(REG) >= 0:
    print('FALLO inesperado: el registro está dentro del bloque')
    sys.exit(1)
sin_bloque = txt[:i0] + txt[j1:]
i_reg = sin_bloque.find(REG)
if i_reg < 0:
    print('FALLO: PODERES_PALA no encontrado')
    sys.exit(1)
nuevo = sin_bloque[:i_reg] + bloque + "\n" + sin_bloque[i_reg:]
C12.write_text(nuevo, encoding='utf-8')
print(f'bloque movido: {len(bloque):,} B por delante del registro PODERES_PALA')

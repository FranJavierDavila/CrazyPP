#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.36 · SUPERPODER DE PALA — MATRIZ + SÚPER EFECTO: inserta los assets
EMBEBIDOS (data-URI) en src/game/core/c12_pingponggame.js:
  · SUSTITUYE la voz MEGA vieja (tongtong — «horrible, no es nativa
    castellana»,petición del dueño) por la NUEVA voz NATIVA
    (Piper es_ES-davefx-medium, LA MISMA de la megafonía del juego).
  · RELLENA los placeholders del poder EFECTO:
      __PODER_PNG_EFECTO__      ← scripts/_poder36/icono_efecto_64.png
      __PODER_VOZ_MEGA_EN__     ← scripts/_poder36/voz_mega_en.mp3
      __PODER_VOZ_EFECTO_ES__   ← scripts/_poder36/voz_efecto_es.mp3
      __PODER_VOZ_EFECTO_EN__   ← scripts/_poder36/voz_efecto_en.mp3
Idempotente: lo ya hecho no se rehace (verifica data-URI/placeholder)."""
import base64
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_poder36'

def uri(fich, mime):
    return mime + base64.b64encode(Path(fich).read_bytes()).decode('ascii')

txt = C12.read_text(encoding='utf-8')
fallos = 0

# 1) VOZ MEGA ES: sustitución del data-URI viejo por la voz nativa davefx
nuevo_mega = uri(P / 'voz_mega_es.mp3', 'data:audio/mpeg;base64,')
pat = re.compile(r"const VOZ_PODER_MEGA = 'data:audio/mpeg;base64,[^']*';")
if pat.search(txt):
    txt = pat.sub("const VOZ_PODER_MEGA = '" + nuevo_mega + "';", txt, count=1)
    print('  ✓ VOZ MEGA ES SUSTITUIDA → voz nativa davefx '
          f'({(P / "voz_mega_es.mp3").stat().st_size:,} B)')
elif nuevo_mega[:64] in txt:
    print('  = VOZ MEGA ES ya es la nativa')
else:
    print('  ✗ VOZ MEGA ES: ni la vieja ni la nueva presentes')
    fallos += 1

# 2) placeholders del poder EFECTO (+ voz EN del mega)
for ph, fich, mime in [
    ('__PODER_PNG_EFECTO__', 'icono_efecto_64.png', 'data:image/png;base64,'),
    ('__PODER_VOZ_MEGA_EN__', 'voz_mega_en.mp3', 'data:audio/mpeg;base64,'),
    ('__PODER_VOZ_EFECTO_ES__', 'voz_efecto_es.mp3', 'data:audio/mpeg;base64,'),
    ('__PODER_VOZ_EFECTO_EN__', 'voz_efecto_en.mp3', 'data:audio/mpeg;base64,'),
]:
    if ph in txt:
        u = uri(P / fich, mime)
        txt = txt.replace(ph, u, 1)
        print(f'  ✓ {ph} ← {fich} ({(P / fich).stat().st_size:,} B)')
    elif ("'" + uri(P / fich, mime) + "'") in txt:
        # comparación EXACTA del URI completo (los prefijos base64 de los
        # PNG/MP3 son idénticos entre ficheros: iVBORw0KGgo… / SUQzBAAA…)
        print(f'  = {ph} ya insertado')
    else:
        print(f'  ✗ {ph}: ni placeholder ni asset')
        fallos += 1

if not fallos:
    C12.write_text(txt, encoding='utf-8')
quedan = [ph for ph in ('__PODER_PNG_EFECTO__', '__PODER_VOZ_MEGA_EN__',
                        '__PODER_VOZ_EFECTO_ES__', '__PODER_VOZ_EFECTO_EN__')
          if ph in txt]
if quedan:
    print('  ✗ placeholders sin resolver:', quedan)
    fallos += 1
print('ASSETS PODER v3.6.36:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

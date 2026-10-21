#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.37 · FASE 39 — SÚPER IMÁN: inserta los assets EMBEBIDOS (data-URI)
en src/game/core/c12_pingponggame.js:
    __PODER_PNG_IMAN__      ← scripts/_poder37/icono_iman_64.png
                              (SuperPala_Iman.png del dueño, 64 colores)
    __PODER_VOZ_IMAN_ES__   ← scripts/_poder37/voz_iman_es.mp3 (davefx)
    __PODER_VOZ_IMAN_EN__   ← scripts/_poder37/voz_iman_en.mp3 (lessac)
Idempotente: lo ya hecho no se rehace (comparación EXACTA del URI completo
— lección ronda 44: los prefijos base64 dan falsos positivos)."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_poder37'

def uri(fich, mime):
    return mime + base64.b64encode(Path(fich).read_bytes()).decode('ascii')

txt = C12.read_text(encoding='utf-8')
fallos = 0
for ph, fich, mime in [
    ('__PODER_PNG_IMAN__', 'icono_iman_64.png', 'data:image/png;base64,'),
    ('__PODER_VOZ_IMAN_ES__', 'voz_iman_es.mp3', 'data:audio/mpeg;base64,'),
    ('__PODER_VOZ_IMAN_EN__', 'voz_iman_en.mp3', 'data:audio/mpeg;base64,'),
]:
    if ph in txt:
        txt = txt.replace(ph, uri(P / fich, mime), 1)
        print(f'  ✓ {ph} ← {fich} ({(P / fich).stat().st_size:,} B)')
    elif ("'" + uri(P / fich, mime) + "'") in txt:
        print(f'  = {ph} ya insertado')
    else:
        print(f'  ✗ {ph}: ni placeholder ni asset')
        fallos += 1

if not fallos:
    C12.write_text(txt, encoding='utf-8')
quedan = [ph for ph in ('__PODER_PNG_IMAN__', '__PODER_VOZ_IMAN_ES__',
                        '__PODER_VOZ_IMAN_EN__') if ph in txt]
if quedan:
    print('  ✗ placeholders sin resolver:', quedan)
    fallos += 1
print('ASSETS IMÁN v3.6.37:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

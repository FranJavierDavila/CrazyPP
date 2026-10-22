#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.41 · FASE 43 — SÚPER PORTAL: inserta los assets EMBEBIDOS (data-URI)
en src/game/core/c12_pingponggame.js:
    __PODER_PNG_PORTAL__      ← scripts/_poder43/icono_portal_64.png
                              (SuperPala_Portal.png del dueño, 64 colores)
    __PODER_VOZ_PORTAL_ES__   ← scripts/_poder43/voz_portal_es.mp3 (TTS)
    __PODER_VOZ_PORTAL_EN__   ← scripts/_poder43/voz_portal_en.mp3 (TTS)
Idempotente: lo ya hecho no se rehace (comparación EXACTA del URI completo
— lección ronda 44: los prefijos base64 dan falsos positivos)."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_poder43'

def uri(fich, mime):
    return mime + base64.b64encode(Path(fich).read_bytes()).decode('ascii')

txt = C12.read_text(encoding='utf-8')
fallos = 0
for ph, fich, mime in [
    ('__PODER_PNG_PORTAL__', 'icono_portal_64.png', 'data:image/png;base64,'),
    ('__PODER_VOZ_PORTAL_ES__', 'voz_portal_es.mp3', 'data:audio/mpeg;base64,'),
    ('__PODER_VOZ_PORTAL_EN__', 'voz_portal_en.mp3', 'data:audio/mpeg;base64,'),
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
quedan = [ph for ph in ('__PODER_PNG_PORTAL__', '__PODER_VOZ_PORTAL_ES__',
                        '__PODER_VOZ_PORTAL_EN__') if ph in txt]
if quedan:
    print('  ✗ placeholders sin resolver:', quedan)
    fallos += 1
print('ASSETS PORTAL v3.6.41:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.50 · FASE 52 — SÚPER CLONACIÓN + VOCES RÁPIDAS DE SELECCIÓN: inserta
los assets EMBEBIDOS (data-URI) en src/game/core/c12_pingponggame.js:
  · __PODER_PNG_CLON__        ← scripts/_poder51/icono_clon_64.png
                                (SuperPala_Clon.png del dueño a 64 px)
  · __PODER_VOZ_CLON_ES__     ← scripts/_poder51/voz_clon_es.mp3
  · __PODER_VOZ_CLON_EN__     ← scripts/_poder51/voz_clon_en.mp3
  · __PODER_SEL_*_ES/EN__ ×12 ← scripts/_poder51/sel_*.mp3
                                (voces RÁPIDAS del joystick: «Súper pala»,
                                «Imán», «Súper efecto», «Portal», «Clonación»
                                y «Sin poder» — traducidas al inglés)
Idempotente: lo ya hecho no se rehace (comparación EXACTA del URI)."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_poder51'

def uri(fich, mime):
    return mime + base64.b64encode(Path(fich).read_bytes()).decode('ascii')

txt = C12.read_text(encoding='utf-8')
fallos = 0

ASSETS = [
    ('__PODER_PNG_CLON__', 'icono_clon_64.png', 'data:image/png;base64,'),
    ('__PODER_VOZ_CLON_ES__', 'voz_clon_es.mp3', 'data:audio/mpeg;base64,'),
    ('__PODER_VOZ_CLON_EN__', 'voz_clon_en.mp3', 'data:audio/mpeg;base64,'),
]
for k in ('mega', 'efecto', 'iman', 'portal', 'clon', 'sinpoder'):
    ASSETS.append((f'__PODER_SEL_{k.upper()}_ES__', f'sel_{k}_es.mp3', 'data:audio/mpeg;base64,'))
    ASSETS.append((f'__PODER_SEL_{k.upper()}_EN__', f'sel_{k}_en.mp3', 'data:audio/mpeg;base64,'))

for ph, fich, mime in ASSETS:
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

if fallos:
    print(f'FALLOS: {fallos}')
    sys.exit(1)

C12.write_text(txt, encoding='utf-8')
print('INSERTADOS_OK')

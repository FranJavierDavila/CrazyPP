#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.35 · SUPERPODER DE PALA — inserta los assets EMBEBIDOS (data-URI)
en src/game/core/c12_pingponggame.js, sustituyendo los placeholders:
  __PODER_PNG_DATA_URI__  ← scripts/_poder35/icono_mega_64.png  (icono del dueño)
  __PODER_VOZ_DATA_URI__  ← scripts/_poder35/voz_mega_final.mp3 (voz animosa)
Idempotente: si los placeholders ya no están, no toca nada (verifica que
los data-URI reales SÍ están)."""
import base64
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
PNG = RAIZ / 'scripts' / '_poder35' / 'icono_mega_64.png'
VOZ = RAIZ / 'scripts' / '_poder35' / 'voz_mega_final.mp3'

txt = C12.read_text(encoding='utf-8')
fallos = 0

if '__PODER_PNG_DATA_URI__' in txt:
    b64 = base64.b64encode(PNG.read_bytes()).decode('ascii')
    txt = txt.replace('__PODER_PNG_DATA_URI__',
                      'data:image/png;base64,' + b64)
    print(f'  ✓ PNG del dueño insertado ({PNG.stat().st_size:,} B → '
          f'{len(b64):,} B base64)')
elif 'data:image/png;base64,' in txt:
    print('  = PNG ya insertado')
else:
    print('  ✗ ni placeholder ni PNG insertado')
    fallos += 1

if '__PODER_VOZ_DATA_URI__' in txt:
    b64 = base64.b64encode(VOZ.read_bytes()).decode('ascii')
    txt = txt.replace('__PODER_VOZ_DATA_URI__',
                      'data:audio/mpeg;base64,' + b64)
    print(f'  ✓ voz TTS insertada ({VOZ.stat().st_size:,} B → '
          f'{len(b64):,} B base64)')
elif 'data:audio/mpeg;base64,' in txt:
    print('  = voz ya insertada')
else:
    print('  ✗ ni placeholder ni voz insertada')
    fallos += 1

if not fallos:
    C12.write_text(txt, encoding='utf-8')
print('ASSETS PODER v3.6.35:', 'OK' if not fallos else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)

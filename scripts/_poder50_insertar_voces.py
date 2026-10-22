#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.42 · FASE 44 — re-embibe las voces del portal (Piper nativo):
    VOZ_PODER_PORTAL    ← scripts/_poder50/voz_portal_es.mp3 (davefx, ES)
    VOZ_PODER_PORTAL_EN ← scripts/_poder50/voz_portal_en.mp3 (lessac, EN)
Sustitución EXACTA del literal completo (idempotente)."""
import base64
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_poder50'

txt = C12.read_text(encoding='utf-8')
fallos = 0
for nombre, fich in [('VOZ_PODER_PORTAL_EN', 'voz_portal_en.mp3'),
                     ('VOZ_PODER_PORTAL', 'voz_portal_es.mp3')]:
    uri = 'data:audio/mpeg;base64,' + base64.b64encode((P / fich).read_bytes()).decode('ascii')
    pat = "const " + nombre + r" = '[^']+';"
    n = len(re.findall(pat, txt))
    if n == 1:
        txt = re.sub(pat, "const " + nombre + " = '" + uri + "';", txt, count=1)
        print(f'  ✓ {nombre} ← {fich} ({(P / fich).stat().st_size:,} B)')
    elif ("'" + uri + "'") in txt:
        print(f'  = {nombre} ya insertado')
    else:
        print(f'  ✗ {nombre}: patrón no único/encontrado ({n})')
        fallos += 1

if not fallos:
    C12.write_text(txt, encoding='utf-8')
print('VOCES PORTAL r50:', 'OK' if not fallos else 'FALLOS')
sys.exit(1 if fallos else 0)

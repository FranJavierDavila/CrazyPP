#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36187.py — r95 · clona el kit release-v36186 → release-v36187.
Tokens: v36186→v36187 · V3.6.186→V3.6.187 · staging · la nota de r94
(FASE 187) se conserva: solo cambian sellos de versión y nombres de ZIP
para que el service worker del casco REINSTALE y borre la caché vieja."""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36186'
DESTINO = RAIZ / 'scripts' / 'release-v36187'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales de versión
t = t.replace('release-v36186', 'release-v36187')
t = t.replace('staging-v36186', 'staging-v36187')
t = t.replace('v36186-sdk6', 'v36187-sdk6')
t = t.replace('V3.6.186-SDK6', 'V3.6.187-SDK6')
t = t.replace('3.6.186-SDK6', '3.6.187-SDK6')

# 2. guardas y conteos del propio kit (patrón v36186)
t = t.replace('grep -c "3.6.186"', 'grep -c "3.6.187"')
t = t.replace('menciones 3.6.186', 'menciones 3.6.187')
t = t.replace('el hub empaquetado no es el v36186',
              'el hub empaquetado no es el v36187')
bz.write_text(t, encoding='utf-8')

# 3. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if f.exists():
        x = f.read_text(encoding='utf-8')
        x = (x.replace('release-v36186', 'release-v36187')
              .replace('v36186-sdk6', 'v36187-sdk6')
              .replace('V3.6.186-SDK6', 'V3.6.187-SDK6')
              .replace('3.6.186-SDK6', '3.6.187-SDK6'))
        f.write_text(x, encoding='utf-8')

# 4. verificación: cero tokens viejos en el kit clonado
viejos = 0
for f in DESTINO.rglob('*'):
    if f.is_file() and f.suffix in ('.py', '.txt', '.md', '.json', '.mjs'):
        viejos += f.read_text(encoding='utf-8', errors='ignore').count('v36186')
print(f'kit release-v36187 creado desde release-v36186')
print(f'tokens v36186 restantes en el kit: {viejos}')
assert viejos == 0, 'quedan tokens v36186 en el kit'

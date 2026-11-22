#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36186.py — r94 · clona el kit release-v36185 → release-v36186.
Tokens: v36185→v36186 · V3.6.185→V3.6.186 · staging · lección del bloqueo
del dueño heredada (el párrafo HOTFIX DE PRODUCCIÓN ya vive en build_zip.py
desde r91b y se hereda con el clon) · la nota FASE 187 se conserva: solo
cambian sellos de versión y nombres de ZIP para que el service worker del
casco REINSTALE y borre la caché vieja."""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36185'
DESTINO = RAIZ / 'scripts' / 'release-v36186'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales de versión
t = t.replace('release-v36185', 'release-v36186')
t = t.replace('staging-v36185', 'staging-v36186')
t = t.replace('v36185-sdk6', 'v36186-sdk6')
t = t.replace('V3.6.185-SDK6', 'V3.6.186-SDK6')
t = t.replace('3.6.185-SDK6', '3.6.186-SDK6')

# 2. guardas y conteos del propio kit (lección del patrón v36182)
t = t.replace('grep -c "3.6.185"', 'grep -c "3.6.186"')
t = t.replace('menciones 3.6.185', 'menciones 3.6.186')
t = t.replace('el hub empaquetado no es el v36185',
              'el hub empaquetado no es el v36186')
bz.write_text(t, encoding='utf-8')

# 3. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if f.exists():
        c = f.read_text(encoding='utf-8')
        c = c.replace('release-v36185', 'release-v36186')
        c = c.replace('staging-v36185', 'staging-v36186')
        c = c.replace('v36185-sdk6', 'v36186-sdk6')
        c = c.replace('V3.6.185-SDK6', 'V3.6.186-SDK6')
        c = c.replace('3.6.185-SDK6', '3.6.186-SDK6')
        f.write_text(c, encoding='utf-8')

# 4. server.mjs y mock_host.mjs: tokens si los llevan
for nombre in ('server.mjs', 'mock_host.mjs'):
    f = DESTINO / nombre
    if f.exists():
        c = f.read_text(encoding='utf-8')
        c = c.replace('v36185-sdk6', 'v36186-sdk6')
        c = c.replace('3.6.185-SDK6', '3.6.186-SDK6')
        f.write_text(c, encoding='utf-8')

print('kit release-v36186 creado desde release-v36185')
restantes = sum(p.read_text(encoding='utf-8').count('36185')
                for p in DESTINO.rglob('*') if p.suffix in ('.py', '.js', '.mjs', '.json', '.txt', '.md'))
print('tokens v36185 restantes en el kit:', restantes)

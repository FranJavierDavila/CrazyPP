#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36184.py — hotfix r91b · clona el kit release-v36182 → release-v36184.
Tokens: v36182→v36183 · V3.6.182→V3.6.183 · staging · lección del bloqueo del
dueño heredada (el párrafo HOTFIX DE PRODUCCIÓN ya vive en build_zip.py desde
r91b y se hereda con el clon) · la nota FASE 187 se conserva (el hotfix es QA
de esa fase, no una fase nueva): solo cambian sellos de versión y nombres de
ZIP para que el service worker del casco REINSTALE y borre la caché vieja."""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36182'
DESTINO = RAIZ / 'scripts' / 'release-v36184'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales de versión
t = t.replace('release-v36182', 'release-v36184')
t = t.replace('staging-v36182', 'staging-v36184')
t = t.replace('v36182-sdk6', 'v36184-sdk6')
t = t.replace('V3.6.182-SDK6', 'V3.6.184-SDK6')
t = t.replace('3.6.182-SDK6', '3.6.184-SDK6')

# 2. guardas y conteos del propio kit (lección del patrón v36182)
t = t.replace('grep -c "3.6.182"', 'grep -c "3.6.183"')
t = t.replace('menciones 3.6.182', 'menciones 3.6.183')
t = t.replace('el hub empaquetado no es el v36182',
              'el hub empaquetado no es el v36183')
bz.write_text(t, encoding='utf-8')

# 3. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36182-sdk6', 'v36184-sdk6')
          .replace('release-v36182', 'release-v36184')
          .replace('staging-v36182', 'staging-v36184')
          .replace('V3.6.182-SDK6', 'V3.6.184-SDK6')
          .replace('3.6.182-SDK6', '3.6.184-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36184 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36183 restante={s.count("v36182-sdk6")} · '
          f'v36184={s.count("v36184-sdk6")} · V3.6.183={s.count("V3.6.182-SDK6")}')

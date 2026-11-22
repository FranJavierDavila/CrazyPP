#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36173.py — r82 · clona el kit release-v36172 → release-v36173.
Tokens: v36172→v36173 · V3.6.172→V3.6.173 · staging · veto añade v36172 ·
nota FASE 178 «MENUS SIN ALIASING» (el aliasing reportado por el dueño).
Orden CRÍTICO: (1) global v36172→v36173, (2) INSERTAR el veto v36172 antes
de v36171 (si se inserta antes, el global lo convertiría en v36173).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36172'
DESTINO = RAIZ / 'scripts' / 'release-v36173'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales (después los dirs ya apuntan a v36173)
t = t.replace('release-v36172', 'release-v36173')
t = t.replace('staging-v36172', 'staging-v36173')
t = t.replace('v36172-sdk6', 'v36173-sdk6')
t = t.replace('V3.6.172-SDK6', 'V3.6.173-SDK6')
t = t.replace('3.6.172-SDK6', '3.6.173-SDK6')

# 2. veto: la v36172 entra en la lista de vetados (sigue la cadena)
viejo_veto = "'v36171-sdk6' in hub"
nuevo_veto = "'v36172-sdk6' in hub or 'v36171-sdk6' in hub"
if t.count(viejo_veto) != 1:
    sys.exit(f'ABORTA: esperaba 1 veto v36171, hay {t.count(viejo_veto)}')
t = t.replace(viejo_veto, nuevo_veto, 1)

# 3. nota de la ficha: FASE 178 cabecera + F177 queda como base histórica
viejo_nota = (
    "'Rama    : main · SDK6 (FASE 177 — MENÚS EN ESCENA: el dueño pidió que al\\n'\n"
    "    'pulsar B el menú salga FIJO, sin seguimiento de la vista, con las\\n'\n"
    "    'animaciones y efectos de la competencia — el ancla fija ya vivía desde\\n'\n"
    "    'la FASE 175 «SIEMPRE ANCLADO» y esta fase le da VIDA al arco:\\n'"
)
nuevo_nota = (
    "'Rama    : main · SDK6 (FASE 178 — MENUS SIN ALIASING: el FX de la FASE 177\\n'\n"
    "    'escalaba las panelas del arco SIN mipmaps (r105) y el texto del menú\\n'\n"
    "    'CRAWLEABA (aliasing reportado por el dueño en la V3.6.172): ahora las\\n'\n"
    "    'tres texturas llevan generateMipmaps=true + LinearMipmapLinearFilter +\\n'\n"
    "    'anisotropy 4; la magnificación sigue Lineal y el coste es despreciable.\\n'\n"
    "    'La FASE 177 «MENÚS EN ESCENA» (el dueño pidió que al pulsar B el menú\\n'\n"
    "    'salga FIJO, sin seguimiento de la vista, con las animaciones y efectos\\n'\n"
    "    'de la competencia — el ancla fija ya vivía desde la FASE 175 «SIEMPRE\\n'\n"
    "    'ANCLADO») le da VIDA al arco:\\n'"
)
if t.count(viejo_nota) != 1:
    sys.exit('ABORTA: bloque de notas FASE 177 no encontrado tal cual')
t = t.replace(viejo_nota, nuevo_nota, 1)
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36172-sdk6', 'v36173-sdk6')
          .replace('release-v36172', 'release-v36173')
          .replace('V3.6.172-SDK6', 'V3.6.173-SDK6')
          .replace('3.6.172-SDK6', '3.6.173-SDK6')
          .replace('release-v36172', 'release-v36173')
          .replace('staging-v36172', 'staging-v36173'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36173 creado')
print('  · build_zip.py: VER/ guards/ veto/ notas → V3.6.173-SDK6')
print('  · veto nuevo: v36172-sdk6 (cadena intacta)')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36172 restante={s.count("v36172-sdk6")} · '
          f'v36173={s.count("v36173-sdk6")} · V3.6.172={s.count("V3.6.172-SDK6")}')

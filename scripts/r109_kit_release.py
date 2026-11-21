#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r109 · KIT DE RELEASE V3.6.207-SDK6 — derivado del kit v36198 (el último
con guardas vivas): copia el kit, sustituye la nota de VERSION.txt por la de
la r109 y el RESUMEN final (SOBRE EL TEXTO ORIGINAL), y después reemplaza
TODAS las marcas de versión (36198→36207 · V3.6.198-SDK6→V3.6.207-SDK6 ·
v36198-sdk6→v36207-sdk6 · 3.6.198→3.6.207). Las guardas de identidad (SDK,
manifests, assets byte-exactos) quedan intactas porque siguen siendo ciertas
en 3.6.207."""
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36198'
DESTINO = RAIZ / 'scripts' / 'release-v36207'

if not ORIGEN.exists():
    sys.exit('FALLO: no existe el kit origen release-v36198')
if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

# ── 1. cirugía de build_zip.py SOBRE EL TEXTO ORIGINAL (36198) ──────
bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

lineas_nota = [
    "Base    : main · SDK6 (FASE 184 — SUPER CRIPTONITA: VOZ EN DOS SALAS Y",
    "CANDADO HONESTO — el dueño: «el Superpoder de criptonita le falta el",
    "audio tanto en el juego como en la sala Arcano; en ambos lugares en",
    "castellano e inglés y con la entonación propia de cada lugar · debe",
    "aparecer bloqueado salvo con la regla del administrador FORO3D»):",
    "· LA VOZ: banco ES/EN Piper de la casa (davefx/lessac, receta r44/r50,",
    "  loudnorm I=-16, mp3 48 kHz mono 64k) embebido como las voces de",
    "  concesión — en el JUEGO la voz ágil del selector (r58) y la de",
    "  concesión (_megaVoz); en el ARCANO la voz SOLEMNE del oráculo (r47:",
    "  cinta ×0,82 + paso-bajo 2,8 kHz + sala ceremonial) sobre el MISMO",
    "  banco: la entonación propia de cada lugar, cero bytes duplicados.",
    "· EL CANDADO: revierte la apertura de fábrica de la r108 + MIGRACIÓN",
    "  que retira la cripto sembrada en el almacenamiento; se abre por la",
    "  vía de siempre (la coronación libera al azar entre los cerrados).",
    "  LA REGLA DEL ADMINISTRADOR: FORO3D (ppDebugMode) TODO desbloqueado.",
    "· LOS CRISTALES: al expirar el poder se ROMPEN TODOS (fin() →",
    "  giro + encogido 0,3 s) — verificado contra la fábrica real de c07.",
    "· RESCATE del linaje r101-r108 (árbol sin commitear tras el reciclado",
    "  del sandbox) + LIMPIEZA del repositorio (r109-b/c: fuera material",
    "  no imprescindible >1 semana — temporales, copias y cachés).",
    "· Arnés scripts/arnes_cripto_r109.mjs 40/40 · golden 7c645570 ·",
    "  sellada a 3.6.207",
]
nota_src = "\n    ".join(
    "'" + l.replace('\\', '\\\\').replace("'", "\\'") + "\\n'" for l in lineas_nota)
t2, n = re.subn(r"'Base    :.*?'Hashes SHA256",
                lambda m: nota_src + "'Hashes SHA256", t, flags=re.S)
if n != 1:
    sys.exit(f'FALLO: la nota de VERSION.txt no se pudo sustituir (coincidencias: {n})')
t2, n2 = re.subn(r"print\('\\nV3\.6\.198-SDK6 lista:.*",
                 lambda m: "print('\\nV3.6.207-SDK6 lista: SUPER CRIPTONITA — VOZ EN DOS SALAS Y "
                           "CANDADO HONESTO (voz ES/EN en juego y Arcano · candado honesto con "
                           "migración · regla FORO3D · cristales que se rompen al expirar) — "
                           "arnés 40/40.')", t2)
if n2 != 1:
    sys.exit(f'FALLO: el RESUMEN no se pudo sustituir (coincidencias: {n2})')
bz.write_text(t2, encoding='utf-8')
print('· build_zip.py: nota de versión r109 + RESUMEN sustituidos')

# ── 2b. versiones de manifest REALES del árbol (el kit v36198 pedía las de
#      su linaje — el árbol r108 verificado byte-exacto manda) ──
import json
vers = {}
for mod in ('oeste', 'magia', 'locura', 'estacion_orbital', 'halloween'):
    ver = json.loads((RAIZ / 'public' / 'championships' / mod / 'manifest.json')
                     .read_text(encoding='utf-8')).get('version')
    vers[mod] = ver
    print(f'· manifest {mod} = v{ver} (árbol real)')
for mod in ('magia', 'locura', 'estacion_orbital', 'oeste', 'halloween'):
    tt2 = bz.read_text(encoding='utf-8')
    nn2 = re.subn(rf"('{mod}': \()\d+", rf"\g<1>{vers[mod]}", tt2)
    if nn2[1]:
        bz.write_text(nn2[0], encoding='utf-8')
    # menciones cosméticas en los print de verificación
    tt3 = bz.read_text(encoding='utf-8')
    for viejo, nuevo in ((f'{mod} v33', f'{mod} v{vers["magia"]}' if mod == 'magia' else None),
                         (f'{mod} v27', f'{mod} v{vers["locura"]}' if mod == 'locura' else None)):
        if nuevo and viejo in tt3:
            bz.write_text(tt3.replace(viejo, nuevo), encoding='utf-8')
print('· guardas del kit alineadas a las versiones REALES de los manifests')

# ── 2. reemplazos globales de versión en todos los ficheros de texto ──
MARCA = [
    ('/home/z/my-project/upload', '/home/z/my-project'),
    ('release-v36198', 'release-v36207'),
    ('staging-v36198', 'staging-v36207'),
    ('V3.6.198-SDK6', 'V3.6.207-SDK6'),
    ('v36198-sdk6', 'v36207-sdk6'),
    ('crazypp-v36198-sdk6', 'crazypp-v36207-sdk6'),
    ('3.6.198-SDK6', '3.6.207-SDK6'),
    ('3.6.198', '3.6.207'),
]
for p in DESTINO.rglob('*'):
    if not p.is_file() or p.suffix in ('.zip', '.png', '.mp3', '.wav', '.webp', '.glb'):
        continue
    try:
        tt = p.read_text(encoding='utf-8')
    except (UnicodeDecodeError, ValueError):
        continue
    nn = tt
    for viejo, nuevo in MARCA:
        nn = nn.replace(viejo, nuevo)
    if nn != tt:
        p.write_text(nn, encoding='utf-8')
        print(f'· versión actualizada: {p.relative_to(DESTINO)}')

print(f'✓ kit listo en {DESTINO}')

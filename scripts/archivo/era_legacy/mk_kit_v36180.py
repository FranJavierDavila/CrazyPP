#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36180.py — r89 · clona el kit release-v36179 → release-v36180.
Tokens: v36179→v36180 · V3.6.179→V3.6.180 · staging · guard del hub heredado ·
nota FASE 185 «MANO LIBRE SIN JÚPITER + MANGO NATURAL» (exención del clamp de
mesa para la mano libre + bola apoyada en el tablero + eje de hoja a ~20-30°).
Lecciones heredadas: (1) guard del hub con versión NUEVA, (2) cabecera de nota
SIN comilla final — la ÚLTIMA línea de nueva_cabecera termina en el \\n LITERAL
y sin salto real, para que la cola compartida « «MENÚS EN ESCENA»… continúe en
la misma línea física.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36179'
DESTINO = RAIZ / 'scripts' / 'release-v36180'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36179', 'release-v36180')
t = t.replace('staging-v36179', 'staging-v36180')
t = t.replace('v36179-sdk6', 'v36180-sdk6')
t = t.replace('V3.6.179-SDK6', 'V3.6.180-SDK6')
t = t.replace('3.6.179-SDK6', '3.6.180-SDK6')

# 2. nota de la ficha: FASE 184 → FASE 185 (marker-based, respeta el pie)
i = t.find('FASE 184 — IA NATURAL')
if i < 0:
    sys.exit('ABORTA: nota FASE 184 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'P0 REV2 + §7.5) intacta —\\n'   # \n LITERAL (lección r84)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 185 — MANO LIBRE SIN JÚPITER + MANGO\\n'\n"
    "    'NATURAL: tercer informe del dueño sobre la V3.6.179, dos causas\\n'\n"
    "    'nuevas con dieta exacta · «la pelota sólo me la deja bajar hasta ~10\\n'\n"
    "    'cm sobre la mesa y si sigo bajando el mando me la coloca debajo» —\\n'\n"
    "    'CAZADO en el tick de mandos: clampPaddlePose MUTA grip.position para\\n'\n"
    "    'sacar la HOJA del tablero y se aplicaba a LOS DOS mandos, incluida\\n'\n"
    "    'la MANO LIBRE: la bola en mano (mano + BALL_HAND_LIFT 0,08) heredaba\\n'\n"
    "    'el techo artificial (mano clavada en topR ⇒ bola a topR+0,10 — la\\n'\n"
    "    '«zona prohibida» de ~10 cm) y al hundir el mando el empuje de mínima\\n'\n"
    "    'penetración salía por la cara más cercana (ABAJO): bola bajo la mesa\\n'\n"
    "    '· FIX: la mano libre va EXENTA del clamp (no lleva pala que proteger)\\n'\n"
    "    'y la bola APOYA sobre el tablero (centro en topR mientras entra en la\\n'\n"
    "    'losa sobre la huella — tocar la mesa como antes; hundido el mando por\\n'\n"
    "    'debajo del canto, la bola vuelve a seguirlo) en offline Y online ·\\n'\n"
    "    '«la pala del rival está vertical, con el mango apuntando hacia la\\n'\n"
    "    'mesa; por lo general se sostiene con el mango casi horizontal» — el\\n'\n"
    "    'EJE de la hoja (mango→punta) baja de la vertical (~18°) a ~20-30°\\n'\n"
    "    'sobre la mesa en ESPERA (0,35·up + 0,93·fwd), en el GOLPEO (0,5−0,15e\\n'\n"
    "    '·up + 0,8+fwd·0,8: se EXTIENDE en el follow-through conservando la\\n'\n"
    "    'firma fwd/side de cada golpe) y en la PREPARACIÓN del saque (0,4·up +\\n'\n"
    "    '0,9·fwd) — la cara (vdir + cierre por efecto) intacta · QA TODO\\n'\n"
    "    'VERDE: goldens c04 12/12 · c05 17/17 · arnés P0 r86 21/21 · arnés\\n'\n"
    "    'r87-89 26/26 · test_red_nucleo 60/60 · rallies I1-I5 con hash\\n'\n"
    "    'IDÉNTICO al de r88 (44377527 — la física del núcleo no se toca) · La\\n'\n"
    "    'FASE 184 (IA NATURAL + SAQUE LIBRE) intacta —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 3. guard del hub DESACTUALIZADO (lección r86 #1, heredada)
t = t.replace('grep -c "3.6.179"', 'grep -c "3.6.180"')
t = t.replace('menciones 3.6.179', 'menciones 3.6.180')
t = t.replace('el hub empaquetado no es el v36179',
              'el hub empaquetado no es el v36180')
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36179-sdk6', 'v36180-sdk6')
          .replace('release-v36179', 'release-v36180')
          .replace('staging-v36179', 'staging-v36180')
          .replace('V3.6.179-SDK6', 'V3.6.180-SDK6')
          .replace('3.6.179-SDK6', '3.6.180-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36180 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36179 restante={s.count("v36179-sdk6")} · '
          f'v36180={s.count("v36180-sdk6")} · V3.6.179={s.count("V3.6.179-SDK6")}')

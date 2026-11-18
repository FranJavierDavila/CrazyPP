#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36179.py — r88 · clona el kit release-v36178 → release-v36179.
Tokens: v36178→v36179 · V3.6.178→V3.6.179 · staging · veto hereda la cadena ·
nota FASE 184 «IA NATURAL + SAQUE LIBRE» (revert del arco/goal de r87 + carga
previa y roll por efecto en el swing + reanclaje solo bajo el plano + gracia
de mano stale). Lecciones r86 HEREDADAS: (1) guard del hub con versión NUEVA
y (2) cabecera de nota SIN comilla final (línea física compartida).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36178'
DESTINO = RAIZ / 'scripts' / 'release-v36179'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36178', 'release-v36179')
t = t.replace('staging-v36178', 'staging-v36179')
t = t.replace('v36178-sdk6', 'v36179-sdk6')
t = t.replace('V3.6.178-SDK6', 'V3.6.179-SDK6')
t = t.replace('3.6.178-SDK6', '3.6.179-SDK6')

# 2. nota de la ficha: FASE 183 → FASE 184 (marker-based, respeta el pie)
i = t.find('FASE 183 — P0 REV2')
if i < 0:
    sys.exit('ABORTA: nota FASE 183 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'contacto y saque P0) intacta —\\n'   # \n LITERAL (lección r84)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 184 — IA NATURAL + SAQUE LIBRE: el segundo\\n'\n"
    "    'informe del dueño tras la V3.6.178 trae dos regresiones/correcciones\\n'\n"
    "    'con causa exacta · «el rival realiza movimientos curvos muy raros y\\n'\n"
    "    'falla muchos golpes»: el ARCO tangente y el OBJETIVO suavizado (90\\n'\n"
    "    'ms) de r87 AÑADÍAN camino y retraso a la llegada — la pala llegaba\\n'\n"
    "    'tarde al punto de contacto y los barridos fallaban; el steering\\n'\n"
    "    'vuelve a ser DIRECTO (revert, el de r86 que sabía llegar) y un\\n'\n"
    "    'jugador real se COLOCA donde va a recibir: trayecto corto y decidido\\n'\n"
    "    '· la naturalidad que pedía el dueño vive ahora EN EL GOLPE: CARGA\\n'\n"
    "    'PREVIA (la hoja arranca DETRÁS del contacto y barre A TRAVÉS de él —\\n'\n"
    "    'carga → contacto → follow-through: el acompañamiento pedido) + ROLL\\n'\n"
    "    'DE MUÑECA LIGADO AL EFECTO REAL del tiro (lift > 0 topspin: la hoja\\n'\n"
    "    'barre por ENCIMA, pronación · lift < 0 cortada: por DEBAJO,\\n'\n"
    "    'supinación — ya no es azar) + el SUELO sobre la mesa se conserva\\n'\n"
    "    '(jamás bajo topR+3 cm) · RESULTADO EN EL ARNÉS DE RALLIES: 380\\n'\n"
    "    'golpes totales y rallyes de hasta 38 (r87: 35 y máx 5) — la IA vuelve\\n'\n"
    "    'a jugar al ping-pong · «es imposible colocar la bola pegada a la\\n'\n"
    "    'mesa, no me la permite bajar»: dos causas de r87 cazadas — (1) el\\n'\n"
    "    'reanclaje al soltar disparaba con margen de 2 cm AUNQUE la bola\\n'\n"
    "    'estuviera ENCIMA del tablero: ahora SOLO procede con la bola DEBAJO\\n'\n"
    "    'del plano (el caso roto de r86: bola oculta sin saque posible);\n'\n"
    "    'colocar/soltar pegada a la mesa es LIBRE y las reglas cantan la\\n'\n"
    "    'ilegalidad con su causa (hint_behind al golpear delante de la línea /\\n'\n"
    "    'rescate honesto si el toss muere sobre la mesa) — jamás un\\n'\n"
    "    'teletransporte silencioso, y (2) un parpadeo de tracking de la mano\\n'\n"
    "    'bajada (>400 ms de frescura) saltaba la bola al PECHO (respaldo r65):\n'\n"
    "    'GRACIA de mano stale — la bola se CONGELA en la última pose válida\\n'\n"
    "    '600 ms (offline Y online) antes de recurrir al respaldo · QA TODO\\n'\n"
    "    'VERDE: goldens c04 12/12 · c05 17/17 · arnés P0 r86 21/21 · arnés\\n'\n"
    "    'r87-88 23/23 · test_red_nucleo 60/60 · rallies 40/40 I1-I5 (canario\\n'\n"
    "    'renovado por diseño 44377527) · La FASE 183 (P0 REV2 + §7.5) intacta —\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 3. guard del hub DESACTUALIZADO (lección r86 #1, heredada)
t = t.replace('grep -c "3.6.178"', 'grep -c "3.6.179"')
t = t.replace('menciones 3.6.178', 'menciones 3.6.179')
t = t.replace('el hub empaquetado no es el v36178',
              'el hub empaquetado no es el v36179')
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36178-sdk6', 'v36179-sdk6')
          .replace('release-v36178', 'release-v36179')
          .replace('staging-v36178', 'staging-v36179')
          .replace('V3.6.178-SDK6', 'V3.6.179-SDK6')
          .replace('3.6.178-SDK6', '3.6.179-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36179 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36178 restante={s.count("v36178-sdk6")} · '
          f'v36179={s.count("v36179-sdk6")} · V3.6.178={s.count("V3.6.178-SDK6")}')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36182.py — r91 · clona el kit release-v36181 → release-v36182.
Tokens: v36181→v36182 · V3.6.181→V3.6.182 · staging · guard del hub heredado ·
nota FASE 187 «CADENA CINEMÁTICA DEL RIVAL» (hombro→codo→muñeca→pala con IK,
quíntico mínimo-jerk, fases reacción→carga→golpeo→acompañamiento→recuperación
sincronizadas a la llegada de la bola, brazo visible, variabilidad funcional,
unificación física verificada) · lecciones heredadas: guard del hub con
versión NUEVA, marcador de cola de nota «SAQUE LIBRE) intacta —\\n»."""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36181'
DESTINO = RAIZ / 'scripts' / 'release-v36182'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36181', 'release-v36182')
t = t.replace('staging-v36181', 'staging-v36182')
t = t.replace('v36181-sdk6', 'v36182-sdk6')
t = t.replace('V3.6.181-SDK6', 'V3.6.182-SDK6')
t = t.replace('3.6.181-SDK6', '3.6.182-SDK6')

# 2. nota de la ficha: FASE 186 → FASE 187 (marker-based, respeta el pie)
i = t.find('FASE 186 — POSE ITTF')
if i < 0:
    sys.exit('ABORTA: nota FASE 186 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'MANGO NATURAL) intacta —\\n'   # \n LITERAL (lección r88)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 187 — CADENA CINEMÁTICA DEL RIVAL:\\n'\n"
    "    'quinto informe del dueño con investigación aplicada («no es creíble…\\n'\n"
    "    'se posiciona de manera previsible y da un empujoncito» + video de\\n'\n"
    "    'técnica con Gatien + 6 fuentes biomecánicas: Bańkosz & Winiarski\\n'\n"
    "    '2025 J Sports Sci Med 24:311 · Bańkosz 2018 PMC5950751 · Malagoli\\n'\n"
    "    'Lanzoni 2021 Appl Sci 11:5178 · Wong 2020 Appl Sci 10:5203 · Flash &\\n'\n"
    "    'Hogan 1985) — la pala del rival DEJA DE TELETRANSPORTARSE: es el\\n'\n"
    "    'extremo de un PLAN DE GOLPE HUMANO (c06 OpponentAI) con fases\\n'\n"
    "    'reacción (12-30 % del vuelo) → carga (backswing, altura mínima de\\n'\n"
    "    'pala AQUÍ — medido en 550 Hz) → golpeo (pico de velocidad\\n'\n"
    "    'SINCRONIZADO a la llegada de la bola, tBall de predictStrike) →\\n'\n"
    "    'acompañamiento (la pala sigue subiendo tras el contacto) →\\n'\n"
    "    'recuperación viva sobre el cuerpo · trayectorias de MÍNIMO JERK\\n'\n"
    "    '(quíntico de Hermite con velocidades de extremo, Flash & Hogan) ·\\n'\n"
    "    're-anclaje por EMPALME con continuidad de velocidad (submovimientos,\\n'\n"
    "    'modelo neurocientífico real) anclado a la refinación de la\\n'\n"
    "    'predicción y al IMPACTO REAL (cadenaContacto al punto del barrido\\n'\n"
    "    'con el pico alineado a la salida — el empujón invisible se vuelve\\n'\n"
    "    'golpe visible) · variabilidad funcional ±12 % (el rival nunca repite\\n'\n"
    "    'pose idéntica — Bańkosz 2025) · BRAZO VISIBLE: hombro→brazo→\\n'\n"
    "    'antebrazo→muñeca en cápsulas carbón articuladas por IK analítica de\\n'\n"
    "    '2 huesos con polo anatómico (el codo cae en drive y sube en revés,\\n'\n"
    "    'rango humano 25-145°), siempre desde la posición REAL de la pala\\n'\n"
    "    '(cadena, saque o espera) y oculto online · la FÍSICA del golpe\\n'\n"
    "    '(solver, árbitro, efectos) INTACTA: goldens c04/c05 12/12+17/17 sin\\n'\n"
    "    're-baseline · UNIFICACIÓN DE FÍSICA verificada por test: mismo\\n'\n"
    "    'estado ⇒ misma trayectoria (determinismo del motor compartido) y 0\\n'\n"
    "    'overrides de constantes físicas fuera de c02 — entrenamiento y\\n'\n"
    "    'partida ya compartían stepPhysics/DIMS (la percepción de diferencia\\n'\n"
    "    'era el patrón de alimentación, no la física) · QA TODO VERDE:\\n'\n"
    "    'arnés CADENA r91 10/10 (quíntico exacto, IK anatómica, fases ==\\n'\n"
    "    'tBall, continuidad 0,0000 m/s, variabilidad, impacto sincronizado,\\n'\n"
    "    'física única) · P0 r86 21/21 · r87-91 33/33 (6 agujas nuevas) · red\\n'\n"
    "    '60/60 · ITTF §12.1 8/8 · rallies 200 rallies 0 violaciones (hash\\n'\n"
    "    'canario nuevo 8f3eba54: el jitter de la cadena consume el PRNG\\n'\n"
    "    'sembrado — desplazamiento documentado, sin cambio de conducta) · 2\\n'\n"
    "    'bugs cazados por el propio arnés: aliasing p0↔cur (el quíntico\\n'\n"
    "    'corrompía su origen → guard NaN) y tiempo global vs local de\\n'\n"
    "    'segmento (agotaba el plan en cascada) · La FASE 186 (POSE ITTF +\\n'\n"
    "    '§12.1 DEL ESTUDIO) intacta —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 3. guard del hub DESACTUALIZADO (lección r86 #1, heredada)
t = t.replace('grep -c "3.6.181"', 'grep -c "3.6.182"')
t = t.replace('menciones 3.6.181', 'menciones 3.6.182')
t = t.replace('el hub empaquetado no es el v36181',
              'el hub empaquetado no es el v36182')
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36181-sdk6', 'v36182-sdk6')
          .replace('release-v36181', 'release-v36182')
          .replace('staging-v36181', 'staging-v36182')
          .replace('V3.6.181-SDK6', 'V3.6.182-SDK6')
          .replace('3.6.181-SDK6', '3.6.182-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36182 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36181 restante={s.count("v36181-sdk6")} · '
          f'v36182={s.count("v36182-sdk6")} · V3.6.181={s.count("V3.6.181-SDK6")}')

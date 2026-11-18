#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36178.py — r87 · clona el kit release-v36177 → release-v36178.
Tokens: v36177→v36178 · V3.6.177→V3.6.178 · staging · veto hereda la cadena ·
nota FASE 183 «P0 REV2 + §7.5» (los cuatro defectos del dueño: bola en mano
LIBRE + reanclaje solo al soltar · inmunidad del toss SOLO subiendo · glitch
de tracking §7.5-lite con cuarentena 100 ms · conducción natural del rival:
goal suavizado + arco + suelo sobre mesa). Lecciones r86 HEREDADAS: (1) el
guard del hub cuenta la versión NUEVA (el bump reescribe el hub entero) y
(2) la cabecera de la nota TERMINA SIN COMILLA (línea física compartida).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36177'
DESTINO = RAIZ / 'scripts' / 'release-v36178'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales (la cadena de veto se desplaza sola: v36177 pasa a veto)
t = t.replace('release-v36177', 'release-v36178')
t = t.replace('staging-v36177', 'staging-v36178')
t = t.replace('v36177-sdk6', 'v36178-sdk6')
t = t.replace('V3.6.177-SDK6', 'V3.6.178-SDK6')
t = t.replace('3.6.177-SDK6', '3.6.178-SDK6')

# 2. nota de la ficha: FASE 182 → FASE 183 (marker-based, respeta el pie)
i = t.find('FASE 182 — FÍSICA P0')
if i < 0:
    sys.exit('ABORTA: nota FASE 182 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'jugando + tienda) intacta —\\n'   # \n LITERAL (lección r84)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 183 — P0 REV2 + §7.5: la sesión del dueño\\n'\n"
    "    'en el visor tras la V3.6.177 trae CUATRO defectos nuevos con causa\\n'\n"
    "    'exacta y correctivo quirúrgico · «si tienes la bola en la mano para\\n'\n"
    "    'sacar y la desplazas sobre la mesa automáticamente te la desplaza\\n'\n"
    "    'fuera, lo que es incorrecto»: el reanclaje del P0-1 CORRÍA CADA\\n'\n"
    "    'FRAME con la bola en mano — la bola en mano vuelve a ser LIBRE\\n'\n"
    "    '(cinemática pura que sigue al mando donde esté) y el reanclaje vive\\n'\n"
    "    'SOLO en tossFromHand ANTES de sellar el toss (la legalidad manda al\\n'\n"
    "    'soltar, nunca mientras se pasea) · «si dejamos caer la bola en el\\n'\n"
    "    'saque con la pala quieta la atraviesa»: la INMUNIDAD del toss\\n'\n"
    "    '(v3.0.6-SRV1) vivía TODO el vuelo mientras (tossMaxY−tossReleaseY)\\n'\n"
    "    '< tossMinRise — un lanzamiento flojo jamás alcanzaba el rise mínimo\\n'\n"
    "    'y la pala quedaba INVISIBLE toda la caída; ahora la inmunidad exige\\n'\n"
    "    'bola SUBIENDO (vel.y > 0) y en cuanto el vuelo cae, la pala vuelve a\\n'\n"
    "    'estar ahí (bote o apoyo — el rise mínimo sigue decidiendo la\\n'\n"
    "    'LEGALIDAD en hint_toss_high) · «en algunos golpes puntuales la\\n'\n"
    "    'pelota adquiere una fuerza anormal, con un pequeño gesto sale\\n'\n"
    "    'disparada»: el estudio técnico §7.5 entra en la casa — un salto de\\n'\n"
    "    'tracking con velocidad implícita > 30 m/s (paddleGlitchSpeed, por\\n'\n"
    "    'VELOCIDAD y no por metros: un smash real de 16 m/s a dt de frame\\n'\n"
    "    'cubre 1,33 m y JAMÁS es glitch) LIMPIA vel/velInst/omega y la\\n'\n"
    "    'ventana de velocidad y mete la pala en CUARENTENA 100 ms\\n'\n"
    "    '(paddleGlitchT) que bloquea el barrido en collidePaddleSweep — sin\\n'\n"
    "    'impulsos por teletransporte · «la pala del rival se teletransporta,\\n'\n"
    "    'va en línea recta, nunca atraviesa la mesa y procura el punto dulce\\n'\n"
    "    'con curvas suaves»: CONDUCCIÓN NATURAL del rival (c06) en tres\\n'\n"
    "    'piezas cero-alloc — OBJETIVO SUAVIZADO (goal persigue con constante\\n'\n"
    "    '90 ms: la re-predicción deja de sacudir la dirección), ARCO DE\\n'\n"
    "    'APROXIMACIÓN (tangente al lado del golpe con peso senoidal que\\n'\n"
    "    'nace, culmina y muere en el contacto) y SUELO SOBRE LA MESA\\n'\n"
    "    '(huella ⇒ jamás bajo topR+3 cm) · VALIDACIÓN TODO VERDE: goldens\\n'\n"
    "    'c04 12/12 · c05 17/17 · arnés P0 r86 21/21 · test_red_nucleo 60/60 ·\\n'\n"
    "    'arnés rallies 40/40 con I1-I5 intactas (canario de conducta\\n'\n"
    "    'RENOVADO por diseño) · arnés P0 r87 NUEVO 20/20 (bola en mano libre\\n'\n"
    "    '· inmunidad con caída visible · glitch 62 m/s cazado y smash 12 m/s\\n'\n"
    "    'respetado · suelo IA) · La FASE 182 (contacto y saque P0) intacta —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 3. guard del hub DESACTUALIZADO (lección r86 #1, heredada): el bump
#    reescribe el hub entero → el guard cuenta la versión NUEVA (3.6.178).
t = t.replace('grep -c "3.6.177"', 'grep -c "3.6.178"')
t = t.replace('menciones 3.6.177', 'menciones 3.6.178')
t = t.replace('el hub empaquetado no es el v36177',
              'el hub empaquetado no es el v36178')
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36177-sdk6', 'v36178-sdk6')
          .replace('release-v36177', 'release-v36178')
          .replace('staging-v36177', 'staging-v36178')
          .replace('V3.6.177-SDK6', 'V3.6.178-SDK6')
          .replace('3.6.177-SDK6', '3.6.178-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36178 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36177 restante={s.count("v36177-sdk6")} · '
          f'v36178={s.count("v36178-sdk6")} · V3.6.177={s.count("V3.6.177-SDK6")}')

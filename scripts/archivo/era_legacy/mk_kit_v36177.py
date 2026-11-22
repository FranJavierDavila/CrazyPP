#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36177.py — r86 · clona el kit release-v36176 → release-v36177.
Tokens: v36176→v36177 · V3.6.176→V3.6.177 · staging · veto hereda la cadena ·
nota FASE 182 «FÍSICA P0: CONTACTO Y SAQUE» (los tres defectos del dueño con
causa exacta y correctivo: secuestro del scoop → captura solo con pala quieta
+ despegue analógico por empuje sostenido; fondo de mesa a expulsión lateral →
mínima penetración en 3 ejes; saque bajo la mesa → reanclaje + altura absoluta
+ rescate honesto). Orden CRÍTICO: (1) tokens globales, (2) nota de la ficha.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36176'
DESTINO = RAIZ / 'scripts' / 'release-v36177'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales (la cadena de veto se desplaza sola: v36176 pasa a veto)
t = t.replace('release-v36176', 'release-v36177')
t = t.replace('staging-v36176', 'staging-v36177')
t = t.replace('v36176-sdk6', 'v36177-sdk6')
t = t.replace('V3.6.176-SDK6', 'V3.6.177-SDK6')
t = t.replace('3.6.176-SDK6', '3.6.177-SDK6')

# 2. nota de la ficha: FASE 181 → FASE 182 (marker-based, respeta el pie)
i = t.find('FASE 181 — SALIDAS Y MONEDAS')
if i < 0:
    sys.exit('ABORTA: nota FASE 181 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'imagen plena) intactas —\\n'   # \n LITERAL en el fuente (lección r84)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 182 — FÍSICA P0: CONTACTO Y SAQUE: los tres\\n'\n"
    "    'defectos que el dueño reportó tras la V3.6.176 tienen causa exacta\\n'\n"
    "    'encontrada por el análisis profundo (c04/c05/c12 línea a línea,\\n'\n"
    "    'cruzado con el estudio técnico de simulación del dueño) y\\n'\n"
    "    'correctivo aplicado · «la bola queda falsamente parada, no\\n'\n"
    "    'desliza, no obedece a los sutiles movimientos y no se puede\\n'\n"
    "    'empujar desde parada»: la captura de reposo r101 era un ANCLAJE\\n'\n"
    "    'BINARIO que secuestraba el scoop — ahora exige PALA QUIETA\\n'\n"
    "    '(restPadSpeed², el mismo umbral del cooldown) y llega el\\n'\n"
    "    'DESPEGUE ANALÓGICO: empujar la pala contra la bola apoyada\\n'\n"
    "    'acumula compresión con fuga exponencial y al superar 10 mm la\\n'\n"
    "    'suelta con un golpe suave proporcional CONTABLE para el árbitro\\n'\n"
    "    '(+ carry 0,5→0,30 y μS estático 0,35→0,18: la bola rueda desde\\n'\n"
    "    '~10°, antes 19,3°) · «golpear por debajo de la altura de la\\n'\n"
    "    'mesa falla»: la banda del fondo de la mesa ahora resuelve por\\n'\n"
    "    'MÍNIMA PENETRACIÓN EN 3 EJES (x/z/arriba/abajo) — la bola bajo\\n'\n"
    "    'el tablero sale por la cara más cercana en vez de ser expulsada\\n'\n"
    "    'de lado · «soltar la bola con la pala bajo la mesa no funciona\\n'\n"
    "    'y desaparece»: reanclaje del punto de saque (la bola en mano\\n'\n"
    "    'JAMÁS nace dentro de la huella: se empuja fuera a línea de fondo\\n'\n"
    "    '+0,10 con aviso en pantalla ES/EN), altura ABSOLUTA del\\n'\n"
    "    'lanzamiento asistido (garantiza topR+0,10 con física pura) y\\n'\n"
    "    'rescate HONESTO (punto de rescate visible tras la línea de fondo\\n'\n"
    "    '+ bola muerta en suelo o mesa propia ⇒ aviso inmediato en vez de\\n'\n"
    "    'esperar 8 s) · LECCIÓN de namespace: restPadSpeed vive en\\n'\n"
    "    'SERVE_TUNE, no DIMS (el arnés P0 nuevo lo cazó antes del visor)\\n'\n"
    "    '· VALIDACIÓN TODO VERDE: arnés P0 test_fisica_p0_r86.mjs 21/21\\n'\n"
    "    '· golden c04 12/12 SIN desviaciones (física quirúrgica) · golden\\n'\n"
    "    'c05 17/17 con escenario nuevo stepPhysics.pushDespegue ·\\n'\n"
    "    'test_red_nucleo 60/60 · La FASE 181 (salidas y monedas: monedas\\n'\n"
    "    'jugando + tienda) intacta —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]

# 4. guard de hub DESACTUALIZADO (lección r86): contaba menciones de la
#    versión ANTERIOR en page.tsx (el hub antaño acumulaba historial), pero
#    el bump actual reescribe el hub entero → contar la versión NUEVA.
t = t.replace('grep -c "3.6.176"', 'grep -c "3.6.177"')
t = t.replace('menciones 3.6.176', 'menciones 3.6.177')
t = t.replace('el hub empaquetado no es el v36175',
              'el hub empaquetado no es el v36177')
bz.write_text(t, encoding='utf-8')

# 3. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36176-sdk6', 'v36177-sdk6')
          .replace('release-v36176', 'release-v36177')
          .replace('staging-v36176', 'staging-v36177')
          .replace('V3.6.176-SDK6', 'V3.6.177-SDK6')
          .replace('3.6.176-SDK6', '3.6.177-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36177 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36176 restante={s.count("v36176-sdk6")} · '
          f'v36177={s.count("v36177-sdk6")} · V3.6.176={s.count("V3.6.176-SDK6")}')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36174.py — r83 · clona el kit release-v36173 → release-v36174.
Tokens: v36173→v36174 · V3.6.173→V3.6.174 · staging · veto añade v36173 ·
nota FASE 179 «MENUS NITIDOS» (borrosidad + deslizador + barrido de luz).
Orden CRÍTICO: (1) global v36173→v36174, (2) INSERTAR el veto v36173.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36173'
DESTINO = RAIZ / 'scripts' / 'release-v36174'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36173', 'release-v36174')
t = t.replace('staging-v36173', 'staging-v36174')
t = t.replace('v36173-sdk6', 'v36174-sdk6')
t = t.replace('V3.6.173-SDK6', 'V3.6.174-SDK6')
t = t.replace('3.6.173-SDK6', '3.6.174-SDK6')

# 2. veto: la v36173 entra en la cadena
viejo_veto = "'v36172-sdk6' in hub"
nuevo_veto = "'v36173-sdk6' in hub or 'v36172-sdk6' in hub"
if t.count(viejo_veto) != 1:
    sys.exit(f'ABORTA: esperaba 1 veto v36172, hay {t.count(viejo_veto)}')
t = t.replace(viejo_veto, nuevo_veto, 1)

# 3. nota de la ficha: FASE 178 → FASE 179 (marker-based, respeta el pie F177)
i = t.find('FASE 178 — MENUS SIN ALIASING')
if i < 0:
    sys.exit('ABORTA: nota FASE 178 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = "el coste es despreciable.\\n'\n    '"
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 179 — MENUS NITIDOS: el informe del dueño\\n'\n"
    "    'tras la V3.6.173 marcó el camino: «los menús se leen muy mal, están\\n'\n"
    "    'muy borrosos» (los mips del r82 suavizaban el texto: vuelta al r105,\\n'\n"
    "    'bilinear nítido) + «el deslizador de campeonatos está mal maquetado\\n'\n"
    "    'y no permite deslizarlo con el mando» (el arrastre de la música de\\n'\n"
    "    'campeonatos movía el volumen de FX; la etiqueta pisaba el botón −;\\n'\n"
    "    'banda a su hueco limpio) + «barrido de luz estilo la competencia»\\n'\n"
    "    '(banda aditiva cruzando el arco, C→lados, 850 ms cada 7 s, GPU pura).\\n'\n"
    "    'El FX ya no ESCALA panelas (posición+opacidad, pulso por color):\\n'\n"
    "    'cero re-muestreo de textura. La FASE 177 «MENÚS EN ESCENA» le da\\n'\n"
    "    'VIDA al arco; la FASE 178 probó mips contra el crawleo y el dueño la\\n'\n"
    "    'revocó por borrosa — conservación r55-r178 íntegra:\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]
bz.write_text(t, encoding='utf-8')

# 4. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36173-sdk6', 'v36174-sdk6')
          .replace('release-v36173', 'release-v36174')
          .replace('staging-v36173', 'staging-v36174')
          .replace('V3.6.173-SDK6', 'V3.6.174-SDK6')
          .replace('3.6.173-SDK6', '3.6.174-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36174 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36173 restante={s.count("v36173-sdk6")} · '
          f'v36174={s.count("v36174-sdk6")} · V3.6.173={s.count("V3.6.173-SDK6")}')

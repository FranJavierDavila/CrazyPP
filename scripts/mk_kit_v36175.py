#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36175.py — r84 · clona el kit release-v36174 → release-v36175.
Tokens: v36174→v36175 · V3.6.174→V3.6.175 · staging · veto añade v36174 ·
nota FASE 180 «ENTRENAMIENTO AL DIA» (imagen plena + subpáginas migradas +
arco a 1,00 m). Orden CRÍTICO: (1) tokens globales, (2) INSERTAR el veto.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36174'
DESTINO = RAIZ / 'scripts' / 'release-v36175'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales
t = t.replace('release-v36174', 'release-v36175')
t = t.replace('staging-v36174', 'staging-v36175')
t = t.replace('v36174-sdk6', 'v36175-sdk6')
t = t.replace('V3.6.174-SDK6', 'V3.6.175-SDK6')
t = t.replace('3.6.174-SDK6', '3.6.175-SDK6')

# 2. veto: la v36174 entra en la cadena (la v36174 kit chequea v36173|v36172)
viejo_veto = "'v36173-sdk6' in hub"
nuevo_veto = "'v36174-sdk6' in hub or 'v36173-sdk6' in hub"
if t.count(viejo_veto) != 1:
    sys.exit(f'ABORTA: esperaba 1 veto v36173, hay {t.count(viejo_veto)}')
t = t.replace(viejo_veto, nuevo_veto, 1)

# 3. nota de la ficha: FASE 179 → FASE 180 (marker-based, respeta el pie)
i = t.find('FASE 179 — MENUS NITIDOS')
if i < 0:
    sys.exit('ABORTA: nota FASE 179 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = "íntegra:\\nLa FASE 177"
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 180 — ENTRENAMIENTO AL DIA: el informe\\n'\n"
    "    'del dueño tras la V3.6.174: «se sigue leyendo mal» (el GOBERNADOR\\n'\n"
    "    'degradaba IMAGEN con el menú abierto — ahora el menú RESTAURA el\\n'\n"
    "    'perfil del tier al instante y _stepDown no toca fovea/escala mientras\\n'\n"
    "    'se lee · y el arco se acerca a 1,00 m: +15 % angular del texto) +\\n'\n"
    "    '«los subapartados de entrenamiento están con una maquetación\\n'\n"
    "    'antigua» (la deuda r80 «hasta su migración» pagada: trainarea y\\n'\n"
    "    'trainext NATIVAS al interior C del arco — fuera placa, transform LEG\\n'\n"
    "    'y sus coordenadas de 1024). La FASE 177/179 (vida del arco +\\n'\n"
    "    'nitidez) intacta — conservación\\n"
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
    s = (s.replace('v36174-sdk6', 'v36175-sdk6')
          .replace('release-v36174', 'release-v36175')
          .replace('staging-v36174', 'staging-v36175')
          .replace('V3.6.174-SDK6', 'V3.6.175-SDK6')
          .replace('3.6.174-SDK6', '3.6.175-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36175 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36174 restante={s.count("v36174-sdk6")} · '
          f'v36175={s.count("v36175-sdk6")} · V3.6.174={s.count("V3.6.174-SDK6")}')

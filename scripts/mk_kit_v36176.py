#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mk_kit_v36176.py — r85 · clona el kit release-v36175 → release-v36176.
Tokens: v36175→v36176 · V3.6.175→V3.6.176 · staging · veto hereda la cadena ·
nota FASE 181 «SALIDAS Y MONEDAS» (el atrapamiento del ajuste de pala: SÍ/NO
muerto → vivo; la ventana de información que se arrastraba y el menú
incerrable → estancos; y la ECONOMÍA CRAZY: monedas jugando + TIENDA de
bolas/mesas). Orden CRÍTICO: (1) tokens globales, (2) nota de la ficha.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36175'
DESTINO = RAIZ / 'scripts' / 'release-v36176'

if DESTINO.exists():
    shutil.rmtree(DESTINO)
shutil.copytree(ORIGEN, DESTINO)

bz = DESTINO / 'build_zip.py'
t = bz.read_text(encoding='utf-8')

# 1. tokens globales (la cadena de veto se desplaza sola: v36175 pasa a veto)
t = t.replace('release-v36175', 'release-v36176')
t = t.replace('staging-v36175', 'staging-v36176')
t = t.replace('v36175-sdk6', 'v36176-sdk6')
t = t.replace('V3.6.175-SDK6', 'V3.6.176-SDK6')
t = t.replace('3.6.175-SDK6', '3.6.176-SDK6')

# 2. nota de la ficha: FASE 180 → FASE 181 (marker-based, respeta el pie)
i = t.find('FASE 180 — ENTRENAMIENTO AL DIA')
if i < 0:
    sys.exit('ABORTA: nota FASE 180 no encontrada')
a = t.rfind("'Rama", 0, i)
fin_marcador = 'nitidez) intacta — conservación\\n'   # \n LITERAL en el fuente (lección r84)
j = t.find(fin_marcador, i)
if a < 0 or j < 0:
    sys.exit('ABORTA: span de la nota no acotado')
nueva_cabecera = (
    "'Rama    : main · SDK6 (FASE 181 — SALIDAS Y MONEDAS: el informe\\n'\n"
    "    'del dueño tras la V3.6.175: «en la configuración de la posición de\\n'\n"
    "    'la pala no se puede salir» y «el botón B abre un panel que no hace\\n'\n"
    "    'nada, es puramente cosmético» — FIX RAÍZ: la autorización SÍ/NO era\\n'\n"
    "    'CÓDIGO MUERTO (case \\'pala:si\\' jamás casaba en el switch del\\n'\n"
    "    'prefijo ns del despacho de menuClick) → case \\'pala\\' despacha por\\n'\n"
    "    'arg: SÍ recoge el ajuste con la salida limpia al Hall · NO cierra el\\n'\n"
    "    'menú y el ajuste sigue vivo) + «la ventana de información de ajuste\\n'\n"
    "    'y colocación de la pala se arrastra hacia otros menús y no\\n'\n"
    "    'desaparece; a partir de ahí ya no es posible cerrar el menú»\\n'\n"
    "    '(palaRecoger OCULTA calibPanel · exitCalib resetea pregunta y ancla\\n'\n"
    "    '(la re-entrada nace FRONTAL exacta) · toggleMenu ya no incerra el\\n'\n"
    "    'menú durante el ajuste (guard calib && !calibPala) · el bloque B 0.6\\n'\n"
    "    'incluye calibPala · la ventana se aparta mientras el menú manda y\\n'\n"
    "    'VUELVE al cerrarlo) + «NO existen bloqueos de bolas ni de mesas,\\n'\n"
    "    'cosa que debería configurarse con la economía del juego» —\\n'\n"
    "    'ECONOMÍA CRAZY: monedas que se ganan JUGANDO (+25 victoria · +8\\n'\n"
    "    'derrota en recordMatch · viven en ppxr_stats_v1 con migración\\n'\n"
    "    'tolerante) y TIENDA CRAZY (coste en las 2 mesas de gala y 12 bolas ·\\n'\n"
    "    'rejilla con candado+precio y moneda dorada · modal de compra con\\n'\n"
    "    'COMPRAR/Cancelar · pp_compras persiste · comprado = seleccionado ·\\n'\n"
    "    'el hito por logros sigue siendo la vía GRATIS) · i18n ES/EN · Las\\n'\n"
    "    'FASES 177/179/180 (vida del arco, nitidez, imagen plena) intactas —\\n"
)
t = t[:a] + nueva_cabecera + t[j + len(fin_marcador):]
bz.write_text(t, encoding='utf-8')

# 3. LEEMEs y package.json: solo tokens de versión
for nombre in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt', 'package.json',
               'LEEME-live-service.md'):
    f = DESTINO / nombre
    if not f.exists():
        continue
    s = f.read_text(encoding='utf-8')
    s = (s.replace('v36175-sdk6', 'v36176-sdk6')
          .replace('release-v36175', 'release-v36176')
          .replace('staging-v36175', 'staging-v36176')
          .replace('V3.6.175-SDK6', 'V3.6.176-SDK6')
          .replace('3.6.175-SDK6', '3.6.176-SDK6'))
    f.write_text(s, encoding='utf-8')

print('✓ kit release-v36176 creado')
for f in ('build_zip.py', 'LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DESTINO / f).read_text(encoding='utf-8')
    print(f'  · {f}: v36175 restante={s.count("v36175-sdk6")} · '
          f'v36176={s.count("v36176-sdk6")} · V3.6.175={s.count("V3.6.175-SDK6")}')

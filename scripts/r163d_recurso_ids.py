#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163d · las claves del recurso eran los NOMBRES DEL ARTE (btn_maquina…)
pero los ids de acción del despachador son start/traingo/survgo/
escalera:soon/tut:go — el mapa recurso.imgs[id] jamás casaba y la
selección del fade no se movía del defecto (visto en el probe r163).
FIX: claves = ids de acción; defecto = 'start' («Jugar contra la máquina»
seleccionado por defecto, con jugar.png en pantalla al abrir)."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'

with open(F_C02, 'r', encoding='utf-8') as fh:
    s = fh.read()

VIEJO = """            defecto: 'btn_maquina',
            imgs: {
              btn_maquina: 'Jugar/jugar.png',
              btn_entrenamiento: 'Jugar/entrenamiento.png',
              btn_supervivencia: 'Jugar/supervivencia.png',
              btn_escalera: 'Jugar/escalera.png',
              btn_tutorial: 'Jugar/tutorial.png',
            },"""
NUEVO = """            // claves = ids de acción del despachador (el hover resuelve
            // rects[hi].id y mira AQUÍ): start=máquina · traingo=
            // entrenamiento · survgo=supervivencia · escalera:soon ·
            // tut:go=tutorial
            defecto: 'start',
            imgs: {
              start: 'Jugar/jugar.png',
              traingo: 'Jugar/entrenamiento.png',
              survgo: 'Jugar/supervivencia.png',
              'escalera:soon': 'Jugar/escalera.png',
              'tut:go': 'Jugar/tutorial.png',
            },"""

if s.count(VIEJO) != 1:
    print(f'✗ {s.count(VIEJO)} coincidencias del bloque recurso')
    sys.exit(1)
with open(F_C02, 'w', encoding='utf-8') as fh:
    fh.write(s.replace(VIEJO, NUEVO))
print('✓ recurso.imgs por ids de acción (defecto start)')

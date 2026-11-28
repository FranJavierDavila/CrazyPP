#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163b · dos remates del r163 (descubiertos por el probe):
1 · LAS CLAVES i18n VIVIAN EN EL FICHERO EQUIVOCADO: el diccionario T()
    vive en src/game/core/c00_pre_three.js (game.html se ENSAMBLA desde
    las piezas en cada build — mis claves en game.html se las llevó el
    rebuild). FIX: claves jug_maquina / jug_entrena / jug_escalera /
    escalera_soon en los DOS diccionarios de c00 (es línea 383, en 1570).
2 · EL CONGELADO r161f NO SE RESETEABA AL ABRIR: se decidía en el primer
    drawMenu (a veces con el menú aún cerrado y sin arte) y quedaba
    pegado — el vestíbulo legado salía SIEMPRE al arrancar (informe del
    dueño). FIX: menuFxInicia('in') — el nacimiento en escena de TODAS
    las aperturas (1157/6769/6819/10964/19595) — resetea _uiModoVals:
    «se decide al abrir» queda literal, y el swap del arranque de
    _uiArteLlego sigue protegiendo los rects bajo la mano."""
import sys

F_C00 = '/home/z/my-project/src/game/core/c00_pre_three.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

B = {}
for f in (F_C00, F_C12):
    with open(f, 'r', encoding='utf-8') as fh:
        B[f] = fh.read()

P = [
    (F_C00, """    jugar_sub: 'Partido · Carrera · Entrenamiento · Supervivencia · Tutorial',""",
     """    jugar_sub: 'Partido · Carrera · Entrenamiento · Supervivencia · Tutorial',
    // r163 · cartela JUGAR (el diccionario vive AQUÍ, no en game.html:
    // el build ensambla el shell desde estas piezas en cada pasada)
    jug_maquina: 'JUGAR CONTRA LA MÁQUINA',
    jug_entrena: 'ENTRENAMIENTO',
    jug_escalera: 'ESCALERA DE CAMPEONATO',
    escalera_soon: 'ESCALERA DE CAMPEONATO · cartela propia en camino',""", 1),
    (F_C00, """    jugar_sub: 'Match · Career · Training · Survival · Tutorial',""",
     """    jugar_sub: 'Match · Career · Training · Survival · Tutorial',
    // r163 · JUGAR board
    jug_maquina: 'PLAY AGAINST THE MACHINE',
    jug_entrena: 'TRAINING',
    jug_escalera: 'CHAMPIONSHIP LADDER',
    escalera_soon: 'CHAMPIONSHIP LADDER · its own board is on the way',""", 1),
    (F_C12, """    if (dir === 'in') {
      this.menuGroup.visible = true;
      this._menuFxOut = 0;""",
     """    if (dir === 'in') {
      // r163b · «SE DECIDE AL ABRIR» hecho literal: cada apertura re-decide
      // cartela ⇄ legado (el congelado de r161f no se reseteaba nunca y el
      // vestíbulo antiguo salía SIEMPRE al arrancar — informe del dueño).
      // El hover nace vacío en la apertura: el swap jamás muda rects bajo
      // la mano; dentro de la sesión sigue congelado (r161f intacto).
      this._uiModoVals = {};
      this.menuGroup.visible = true;
      this._menuFxOut = 0;""", 1),
]

mal = []
for i, (f, old, new, nn) in enumerate(P):
    cc = B[f].count(old)
    if cc != nn:
        mal.append((i, f.split('/')[-1], old[:60], cc, nn))
        continue
    B[f] = B[f].replace(old, new)
if mal:
    for i, nom, o, cc, nn in mal:
        print(f'✗ parche {i} [{nom}] «{o}…»: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")
print('✓ r163b: dict en c00 + congelado se decide al abrir')

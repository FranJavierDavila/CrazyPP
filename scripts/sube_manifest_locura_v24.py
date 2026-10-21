#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 40 · manifest de LA LOCURA v23 → v24 (v3.6.32).

El dueño pide (tras V3.6.31): «Si la MEGA PALA sí existe debería dar
feedback visual de alguna forma, aumentando el tamaño de la raqueta y
poniendo una alerta visual como de energía o algún efecto que indique
que la pala del jugador tiene ese poder».

Cambio de MÓDULO (locura, módulo v24): la MEGA PALA (playerPower de este
manifest: kind mega_pala · reachMul 1.38 · duration 8 s) era INVISIBLE —
sólo tocaba la física (radio de detección ×1,38) y el jugador no sabía
por qué la bola llegaba más lejos. Ahora:

  · la PALA CRECE a ×1,30 (se escala la MONTURA visual de la pala; la
    física sigue mandada por hitAssistRadius — cero cambios de juego)
  · AURA dorada (sprite aditivo, billboard: mira siempre a la cámara)
    + DOBLE anillo de energía girando en el plano de la hoja
  · power-up sonoro (arpegio arcade) + háptica al ACTIVARSE
  · aviso ÚNICO en los <2 s finales: parpadeo rápido + sfx descendente
    (el poder se agota)
  · la energía cuelga de las DOS monturas de pala (viaja sola si el
    jugador cambia de mano) y leave() la recoge con dispose completo
  · REGRESIÓN corregida de paso: el radio de detección quedaba inflado
    si un startMatch ponía _megaT a 0 directamente (auto-revancha dentro
    de la ventana de 8 s) — ahora el else del update restaura SIEMPRE.

QA: capa AA nueva (qa_mega_pala_v3632, en vivo): ~20 checks — agujas del
módulo servido + mecánica real en headless (launch de locura, power
forzado, escala de la montura, energía viva/apagada, restauración en
leave y monturas a escala 1).
"""
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project')
P = RAIZ / 'public/championships/locura/manifest.json'
VJ = RAIZ / 'src/game/VERSION.json'

# 1 · manifest: versión + nota de historial
m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 24:
    print('manifest locura ya en v24 — nada que hacer')
else:
    assert m['version'] == 23, f'versión inesperada: {m["version"]}'
    m['version'] = 24
    m.setdefault('notes', []).append(
        '2026-10-21 v3.6.32-SDK6 · FASE 34 · MEGA PALA CON FEEDBACK VISUAL '
        '(informe del dueño: «si la MEGA PALA sí existe debería dar feedback '
        'visual… aumentando el tamaño de la raqueta y poniendo una alerta '
        'visual como de energía»): el poder (kind mega_pala · reachMul 1.38 '
        '· 8 s) era invisible — sólo tocaba la física. Ahora la pala CRECE a '
        '×1,30 (montura visual, la física no cambia), se envuelve en AURA '
        'dorada + doble anillo girando en el plano de la hoja, suena un '
        'arpegio arcade con háptica al activarse y PARPADEA en los <2 s '
        'finales (aviso único de agotamiento). La energía cuelga de las dos '
        'monturas (viaja sola al cambiar de mano) y leave() la recoge con '
        'dispose. Regresión corregida: el radio de detección quedaba '
        'inflado si un startMatch ponía _megaT=0 directo. QA: capa AA '
        '(qa_mega_pala_v3632) con mecánica real en headless.')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
    print('manifest locura → v24 con nota FASE 34')

# 2 · VERSION.json: sincroniza manifests.locura (fuente de verdad de qa_version)
v = json.loads(VJ.read_text(encoding='utf-8'))
if v.get('manifests', {}).get('locura') == 24:
    print('VERSION.json ya apunta a locura v24')
else:
    v['manifests']['locura'] = 24
    VJ.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n',
                  encoding='utf-8')
    print('VERSION.json: manifests.locura → 24')

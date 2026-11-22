#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36164.py — FASE 167 · r73 · generador del release.
Re-sella scripts/release-v36163/build_zip.py → scripts/release-v36164/:
  · tokens de versión (v36163→v36164 · 3.6.163→3.6.164) + veto explícito
    de la v36163 al girar el candado del hub.
  · notas del release: FASE 166 → FASE 167 (EL NIVEL 3, PLACA A PLACA).
  · línea final del resumen con el contenido real de r73."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36163/build_zip.py'
DESTINO = RAIZ / 'release-v36164/build_zip.py'

t = ORIGEN.read_text(encoding='utf-8')

# 1 · tokens de versión (el candado del hub se actualiza solo: al girar
#     las etiquetas, la v36163 pasa a la lista de vetadas automáticamente)
for a, b in [('v36163-sdk6', 'v36164-sdk6'),
             ('V3.6.163-SDK6', 'V3.6.164-SDK6'),
             ('3.6.163-SDK6', '3.6.164-SDK6'),
             ('v36163', 'v36164'),
             ('3.6.163', '3.6.164')]:
    t = t.replace(a, b)

# 1b · el candado veta también la v36163 (por si el guard no la heredó)
t = t.replace("'v36164-sdk6' not in hub",
              "'v36164-sdk6' not in hub or 'v36163-sdk6' in hub")

# 2 · notas FASE 166 → FASE 167
m = re.search(r"'Rama    : main · SDK6 \(FASE 166[^\0]*?'  3\.6\.164\\n'", t)
if not m:
    sys.exit('ABORTA: bloque de notas FASE 166 no hallado')
L = []


def ln(s):
    L.append("    '" + s + "\\n'")


ln('Rama    : main · SDK6 (FASE 167 — EL NIVEL 3, PLACA A PLACA: el dueño')
ln('pidió «continua» tras ver r72 desplegada; quedaban las TARJETAS del')
ln('nivel 3 pintadas a caramelo saturado (r72 maquetó el botón compartido')
ln('y Ajustes/Ranking; el informe r72 mostraba champs, train, multi,')
ln('rankini, carrera y sala con degradados vivos).')
ln('  · LA PLACA DE MUSEO (_vestPlaca73): base oscura + overlay blanco')
ln('    sutil + MARCO DE LATÓN rgba(232,180,90,0.32) — el mismo lenguaje')
ln('    que el botón compartido r72. Visten así LAS 6 REJILLAS (AJUSTES 7,')
ln('    MULTIJUGADOR 3, RANKING 2, CAMPEONATOS, ENTRENAR 7, CARRERA 5),')
ln('    las FILAS DE RIVALES de la división y las tarjetas de _modeCard')
ln('    (SALA: Room/Mesa/Bola/Hall).')
ln('  · EL COLOR SOBREVIVE COMO ARO: _vestMedallion admite aro teñido')
ln('    (_aroTinte, hex→rgba 0,62) — cada categoría conserva su hue en el')
ln('    anillo del medallón (wayfinding sin caramelo); vencido verde y')
ln('    pendiente acero en las filas de rivales; sin tinte (Vestíbulo,')
ln('    prompts) queda el blanco de siempre.')
ln('  · INTACTO lo aprobado: el VESTÍBULO (referencia caramelo del dueño)')
ln('    y su concha, los prompts de confirmación, el botón ATRÁS flotante')
ln('    y los HÉROES de acción (▶ JUGAR, JUGAR verde de champuno,')
ln('    CHALLENGE de la división).')
ln('  · QA: qa_vestibulo_r73 22/0 (contadores candy/placa por página —')
ln('    el candy residual es SOLO el ATRÁS; aros teñidos verificados;')
ln('    héroes intactos; 26 páginas en lados y bounds; kofi fuera r72;')
ln('    _rankiniFresh r72) · arnes_r73 6/0 (30 páginas sanas · rankini')
ln('    1 GET · 0 errores) · láminas de contacto revisadas a ojo.')
ln('  · Ensamblado 12.183.852 B (golden edeaab80).')
ln('  SE CONSERVA TODO: r55-r72 íntegro (anclaje r69/r71, aspecto exacto')
ln('    r70, ola data-driven, blindaje del saque r65, BOLA LOCA, Hall')
ln('    FASE 29, multijugador, ELO, taller UGC, PWA, PRO TRAINING,')
ln('    halloween, guarda _rankiniFresh).')
ln('  · sellada a')
ln('  3.6.164')
NOTAS = '\n'.join(L) + '\n'
t = t[:m.start()] + NOTAS + t[m.end():]

# 3 · línea final del resumen
m = re.search(r"print\('\\nV3\.6\.164-SDK6 lista:[^']*'\)", t)
if not m:
    sys.exit('ABORTA: línea final no hallada')
t = t[:m.start()] + ("print('\\nV3.6.164-SDK6 lista: EL NIVEL 3, PLACA A PLACA — las tarjetas de "
  "TODAS las rejillas del nivel 3 (Ajustes, Multijugador, Ranking, Campeonatos, "
  "Entrenar, Carrera), las filas de rivales y las tarjetas de Sala visten la "
  "PLACA DE MUSEO (base oscura + overlay sutil + marco de latón) con el color "
  "de categoría sobreviviendo como ARO del medallón; el Vestíbulo, los prompts "
  "y los héroes de acción conservan su caramelo — verificado con "
  "qa_vestibulo_r73 22/0 y arnes_r73 6/0 (30 páginas, rankini 1 GET); "
  "conservación r55-r72 íntegra.')") + t[m.end():]

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(t, encoding='utf-8')
ast.parse(t)
print(f'gen_release_v36164 OK → {DESTINO} (notas FASE 167 · línea final r73)')

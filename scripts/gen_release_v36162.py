#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36162.py — FASE 165 · r71 · generador del release.
Re-sella scripts/release-v36161/build_zip.py → scripts/release-v36162/:
  · tokens de versión (v36161→v36162 · 3.6.161→3.6.162) — el candado del
    hub hereda v36161 como versión vetada automáticamente.
  · notas del release: FASE 164 → FASE 165 (EL MENÚ NACE ANCLADO).
  · línea final del resumen con el contenido real de r71."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36161/build_zip.py'
DESTINO = RAIZ / 'release-v36162/build_zip.py'

t = ORIGEN.read_text(encoding='utf-8')

# 1 · tokens de versión (el candado del hub se actualiza solo: al girar
#     las etiquetas, la v36161 pasa a la lista de vetadas automáticamente)
for a, b in [('v36161-sdk6', 'v36162-sdk6'),
             ('V3.6.161-SDK6', 'V3.6.162-SDK6'),
             ('3.6.161-SDK6', '3.6.162-SDK6'),
             ('v36161', 'v36162'),
             ('3.6.161', '3.6.162')]:
    t = t.replace(a, b)

# 1b · el candado del hub veta también la v36161 (por si el guard r68 no
#     la heredó al rotar)
t = t.replace("'v36160-sdk6' in hub",
              "'v36160-sdk6' in hub or 'v36161-sdk6' in hub")

# 2 · notas FASE 164 → FASE 165: bloque CONCATENACIÓN de literales con
#     comilla simple y \n embebido, sangría 4, SIN comas — cierre real:
#     «'  3.6.162\n'» (ya girado por los tokens)
m = re.search(r"'Rama    : main · SDK6 \(FASE 164[^\0]*?'  3\.6\.162\\n'", t)
if not m:
    sys.exit('ABORTA: bloque de notas FASE 164 no hallado')
L = []


def ln(s):
    L.append("    '" + s + "\\n'")


ln('Rama    : main · SDK6 (FASE 165 — EL MENÚ NACE ANCLADO: informe del')
ln('dueño tras V3.6.161 en el casco: «primero el menú no aparece anclado')
ln('como dijimos, y además bloquea el juego haciendo imposible jugar»).')
ln('  · CAUSA RAÍZ (cazada con arnés XR + sondas three.js): el ARRANQUE')
ln('    XR (onSessionStart) abría el menú (bloque M4) con anchorMenu()')
ln('    SIN forzar → con la chincheta puesta retornaba SIN anclar ni')
ln('    firmar la estancia → enterHall movía el rig ~17 m DESPUÉS → el')
ln('    heal r114 veía un viaje y SOLTABA la chincheta en el frame 1 →')
ln('    el menú nacía SIGUIENDO la cara: nunca fijo («no aparece')
ln('    anclado»), siempre delante de la vista y comiéndose los')
ln('    gatillos («bloquea el juego, imposible jugar»).')
ln('  · FIX: anchorMenu(true) en el bloque M4 del arranque, re-ancla')
ln('    forzado JUSTO DESPUÉS de enterHall (nace en el HALL delante de')
ln('    la mirada, FIJO, con la firma de estancia al día — el heal')
ln('    calla) y anchorMenu(true) en la apertura del menú de Entrenar')
ln('    con B. Las demás aperturas ya nacían forzadas (toggleMenu,')
ln('    openHallAsk). El heal r114 se conserva intacto (viajes reales).')
ln('  · ARNÉS NUEVO: xr_boot_r71.py — simula el arranque XR real y mide')
ln('    pin/distancia/estancia por frames: ANTES pin=False desde el')
ln('    frame 1 (menú following), DESPUÉS pin=True constante y grupo')
ln('    QUIETO (0,000 m de deriva). xr_flujo_r71.py: nace en el HUB,')
ln('    NO sigue la mirada al girar 90° con chincheta, y el rayo real')
ln('    (uv→rect) halla PLAY. xr_sim_r71.py 27/0 + qa_vestibulo_r70')
ln('    58/0 sobre el build corregido.')
ln('  · 0 cambios de diseño: panelas, concha, rejillas, lados, anclaje')
ln('    r69 y todo r55-r70 íntegro. Ensamblado 12.180.164 B (golden')
ln('    698a6d76).')
ln('  SE CONSERVA TODO: r55-r70 íntegro (arco tangente a 1,15 m, ancla')
ln('    congela/sigue, ola data-driven, blindaje del saque r65, BOLA LOCA')
ln('    + regla solo-1 r160, Hall FASE 29, multijugador, ELO, taller UGC,')
ln('    PWA, PRO TRAINING, halloween).')
ln('  · sellada a')
ln('  3.6.162')
NOTAS = '\n'.join(L) + '\n'
t = t[:m.start()] + NOTAS + t[m.end():]

# 3 · línea final del resumen
m = re.search(r"print\('\\nV3\.6\.162-SDK6 lista:[^']*'\)", t)
if not m:
    sys.exit('ABORTA: línea final no hallada')
t = t[:m.start()] + ("print('\\nV3.6.162-SDK6 lista: EL MENÚ NACE ANCLADO — el arranque XR "
  "ancla FORZADO y re-firma tras enterHall (fin del menú siguiendo la cara: nace "
  "delante de la mirada, FIJO salvo chincheta manual), la apertura B-entrenar "
  "también nace anclada, el heal r114 intacto para viajes reales — verificado con "
  "el arnés xr_boot (pin True constante, 0,000 m de deriva), xr_flujo y xr_sim "
  "27/0 + qa_vestibulo 58/0; conservación r55-r70 íntegra.')") + t[m.end():]

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(t, encoding='utf-8')
ast.parse(t)
print(f'gen_release_v36162 OK → {DESTINO} (notas FASE 165 · línea final r71)')

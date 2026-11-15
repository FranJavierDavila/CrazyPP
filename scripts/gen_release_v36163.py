#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36163.py — FASE 166 · r72 · generador del release.
Re-sella scripts/release-v36162/build_zip.py → scripts/release-v36163/:
  · tokens de versión (v36162→v36163 · 3.6.162→3.6.163) — el candado del
    hub hereda v36162 como versión vetada automáticamente.
  · notas del release: FASE 165 → FASE 166 (EL NIVEL 3 MAQUETADO).
  · línea final del resumen con el contenido real de r72."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36162/build_zip.py'
DESTINO = RAIZ / 'release-v36163/build_zip.py'

t = ORIGEN.read_text(encoding='utf-8')

# 1 · tokens de versión (el candado del hub se actualiza solo: al girar
#     las etiquetas, la v36162 pasa a la lista de vetadas automáticamente)
for a, b in [('v36162-sdk6', 'v36163-sdk6'),
             ('V3.6.162-SDK6', 'V3.6.163-SDK6'),
             ('3.6.162-SDK6', '3.6.163-SDK6'),
             ('v36162', 'v36163'),
             ('3.6.162', '3.6.163')]:
    t = t.replace(a, b)

# 1b · el candado del hub veta también la v36162 (por si el guard r68 no
#     la heredó al rotar)
t = t.replace("'v36160-sdk6' in hub",
              "'v36160-sdk6' in hub or 'v36161-sdk6' in hub")

# 2 · notas FASE 165 → FASE 166: bloque CONCATENACIÓN de literales con
#     comilla simple y \n embebido, sangría 4, SIN comas — cierre real:
#     «'  3.6.163\n'» (ya girado por los tokens)
m = re.search(r"'Rama    : main · SDK6 \(FASE 165[^\0]*?'  3\.6\.163\\n'", t)
if not m:
    sys.exit('ABORTA: bloque de notas FASE 165 no hallado')
L = []


def ln(s):
    L.append("    '" + s + "\\n'")


ln('Rama    : main · SDK6 (FASE 166 — EL NIVEL 3 MAQUETADO: informe del')
ln('dueño tras V3.6.162 en el casco: «todos los menús de tercer nivel')
ln('siguen en el formato antiguo sin maquetar; en Ajustes debe')
ln('desaparecer el botón de Apoyar proyecto; el juego acaba de volver a')
ln('bloquearse al pulsar sobre Ranking Mundial — si continuamos con el')
ln('bloque prefiero volver al diseño anterior».')
ln('  · CONGELAMIENTO DE RANKING MUNDIAL CAZADO Y CORREGIDO: el landing')
ln('    r70 (drawMenuRankIni) disparaba WORLDRANK.load(true) DENTRO del')
ln('    dibujo y su .then() redibujaba LA MISMA página, que volvía a')
ln('    disparar el load(true) — ciclo GET+redibujo SIN FIN que')
ln('    saturaba el navegador de la Quest (juego congelado al pulsar).')
ln('    FIX: guarda _rankiniFresh — UNA sola revalidación por aterrizaje,')
ln('    re-armada al ENTRAR en la página (page:/wrl:open); fuera el')
ln('    load(true) muerto de wrl:open. El refresh manual y el resto de')
ln('    call-sites (one-shot por clic) quedan intactos.')
ln('  · ARNÉS NUEVO (la vacuna): arnes_r72.py — SOAK anti-bucle que abre')
ln('    LAS 30 páginas del menú, bombea 700 ms por página y cuenta')
ln('    peticiones al almacén + salud de macrotareas + rects: rankini')
ln('    gasta 1 GET en toda la visita (antes: tormenta sin fin), 0')
ln('    errores de página, 30/30 páginas sanas.')
ln('  · FUERA «Apoyar el proyecto (Ko-fi)» de AJUSTES (petición del')
ln('    dueño): la tarjeta se retira de la rejilla; el canal kofi de la')
ln('    portada web (dock/footlink) no se toca.')
ln('  · NIVEL 3 MAQUETADO con el lenguaje nuevo: el pintor compartido')
ln('    btn viste degradado sutil + MARCO DE LATÓN en reposo y radio 16')
ln('    (optCat, teclados, asks, sala, estados de multi y páginas c13 se')
ln('    maquetan de una pieza); las 6 categorías de AJUSTES re-espaciadas')
ln('    (filas +6 px, pasos +8 px — 40 alturas y 70 pasos); RANKING con')
ln('    cabeceras en oro y MI RANKING con ELO en oro y tarjetas con')
ln('    marco de latón (placa de museo). Ids y conducta intactos.')
ln('  · QA: qa_vestibulo_r72 58/0 (regresión completa del apartado +')
ln('    kofi fuera verificado) · arnes_r72 6/0 (30 páginas · sin bucles')
ln('    · sin tormentas). Ensamblado 12.181.736 B (golden 53266b4b).')
ln('  SE CONSERVA TODO: r55-r71 íntegro (anclaje r69/r71, aspecto exacto')
ln('    r70, ola data-driven, blindaje del saque r65, BOLA LOCA, Hall')
ln('    FASE 29, multijugador, ELO, taller UGC, PWA, PRO TRAINING,')
ln('    halloween).')
ln('  · sellada a')
ln('  3.6.163')
NOTAS = '\n'.join(L) + '\n'
t = t[:m.start()] + NOTAS + t[m.end():]

# 3 · línea final del resumen
m = re.search(r"print\('\\nV3\.6\.163-SDK6 lista:[^']*'\)", t)
if not m:
    sys.exit('ABORTA: línea final no hallada')
t = t[:m.start()] + ("print('\\nV3.6.163-SDK6 lista: EL NIVEL 3 MAQUETADO — el congelamiento de "
  "Ranking Mundial cazado (bucle load(true).then(drawMenu) en drawMenuRankIni) y "
  "corregido con la guarda _rankiniFresh (una revalidación por aterrizaje), Ko-fi "
  "fuera de Ajustes, y el nivel 3 vistiendo el lenguaje nuevo: btn compartido en "
  "latón+degradado, 6 categorías de AJUSTES re-espaciadas, RANKING/MI RANKING en "
  "oro de museo — verificado con arnes_r72 (30 páginas, sin bucles, rankini 1 GET) "
  "y qa_vestibulo_r72 58/0; conservación r55-r71 íntegra.')") + t[m.end():]

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(t, encoding='utf-8')
ast.parse(t)
print(f'gen_release_v36163 OK → {DESTINO} (notas FASE 166 · línea final r72)')

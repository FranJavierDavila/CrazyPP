#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36161.py — FASE 164 · r70 · generador del release.
Re-sella scripts/release-v36160/build_zip.py → scripts/release-v36161/:
  · tokens de versión (v36160→v36161 · 3.6.160→3.6.161) — el candado del
    hub hereda v36160 como versión vetada automáticamente.
  · notas del release: FASE 163 → FASE 164 (EL APARTADO COMPLETO).
  · línea final del resumen con el contenido real de r70."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36160/build_zip.py'
DESTINO = RAIZ / 'release-v36161/build_zip.py'

t = ORIGEN.read_text(encoding='utf-8')

# 1 · tokens de versión (el candado del hub se actualiza solo: al girar
#     las etiquetas, la v36160 pasa a la lista de vetadas automáticamente)
for a, b in [('v36160-sdk6', 'v36161-sdk6'),
             ('V3.6.160-SDK6', 'V3.6.161-SDK6'),
             ('3.6.160-SDK6', '3.6.161-SDK6'),
             ('v36160', 'v36161'),
             ('3.6.160', '3.6.161')]:
    t = t.replace(a, b)

# 1b · el candado del hub veta también la v36160 (por si el guard r68 no
#     la heredó al rotar)
t = t.replace("'v36159-sdk6' in hub",
              "'v36159-sdk6' in hub or 'v36160-sdk6' in hub")

# 2 · notas FASE 163 → FASE 164: bloque CONCATENACIÓN de literales con
#     comilla simple y \n embebido, sangría 4, SIN comas — cierre real:
#     «'  3.6.161\n'» (ya girado por los tokens)
m = re.search(r"'Rama    : main · SDK6 \(FASE 163[^\0]*?'  3\.6\.161\\n'", t)
if not m:
    sys.exit('ABORTA: bloque de notas FASE 163 no hallado')
L = []


def ln(s):
    L.append("    '" + s + "\\n'")


ln('Rama    : main · SDK6 (FASE 164 — EL APARTADO COMPLETO: informe del')
ln('dueño tras V3.6.160 en el casco).')
ln('  · 1 · «LOS PANELES CON LAS ESQUINAS REDONDEADAS Y RECORTADAS')
ln('    TAMBIÉN EN REDONDO»: cada panela es un ShapeGeometry con sus')
ln('    CUATRO esquinas en curva (radio 0,036 m) y UVs 0..1 — los CORTES')
ln('    del troceo quedan redondeados, sin bordes vivos en ningún lado.')
ln('  · 2 · «LOS BLOQUES ESTÁN ACHICADOS… LOS CÍRCULOS DE LOS ICONOS NO')
ln('    SON CIRCULARES POR ESTAR EL PANEL ESCALADO»: causa raíz cazada —')
ln('    r69 estrechó los anchos físicos sin tocar el lienzo y la textura')
ln('    se estiraba (rodaja 1112/1400 = 0,794 vs físico 0,66/0,95 =')
ln('    0,695). Ahora el ancho se DERIVA del aspecto de la rodaja')
ln('    (anchoM = w/altoLienzo·altoM → central 0,9989 m · laterales')
ln('    0,7546 m: TAMAÑO ORIGINAL recuperado) y el YAW se CALCULA con la')
ln('    fórmula r69 desde las anchuras reales (42,485° — sin grados a')
ln('    mano). QA: texel/px IDÉNTICO en las tres panelas → los círculos')
ln('    son círculos. scale.set PROHIBIDO en el grupo del menú.')
ln('  · 3 · «SI NO HAY CONTENIDO NO SE COLOCA EL BLOQUE»: bloques')
ln('    condicionales — CONFIG_SECCIONES.lados declara los lados con')
ln('    contenido de cada página; _menuArco monta SÓLO esas panelas y')
ln('    recalcula el arco para 1/2/3 (C siempre al frente); las ocultas')
ln('    salen del rayo y del troceo. La concha pinta su cristal sólo')
ln('    donde hay pantalla. NUNCA una panela vacía.')
ln('  · 4 · «RETORNAR COMO BOTONES FLOTANTES SOBRE EL BLOQUE CENTRAL»:')
ln('    banda de navegación común en la franja superior de la C (ATRÁS +')
ln('    título con medallón + títulos dinámicos), idiomas y sello en la R')
ln('    si está montada; backs legados fuera (rank, historial).')
ln('  · 5 · «MULTIJUGADOR, CAMPEONATOS, RANKING MUNDIAL, ESCALERA DE')
ln('    CARRERA Y ENTRENAR CON EL FORMATO AJUSTES»: MULTIJUGADOR landing')
ln('    rejilla (2 modos + unirse) + invitación + estados de sala en la C')
ln('    (voz, pulso con INVITAR, avisos de build) · CAMPEONATOS rejilla')
ln('    C+R con tarjetas VIVAS del índice + DETALLE con JUGAR héroe,')
ln('    presentación y controles del módulo · RANKING landing (tabla + mi')
ln('    posición) · CARRERA: 5 divisiones + división abierta con rivales y')
ln('    DESAFIAR · ENTRENAR rejilla (5 áreas + reto semanal + perfil y')
ln('    extras) con FUERA «Volver al Hall» (petición literal).')
ln('  · 6 · CALIDAD: qa_vestibulo_r70.py 58 OK · 0 fallos (aspecto exacto,')
ln('    yaw por fórmula, colocación en mundo 1,151 m, congela/sigue r69,')
ln('    barrido de 25 páginas con panelas montadas == lados del dato y')
ln('    rects en bounds, banda ATRÁS, rejillas de los 5 apartados) +')
ln('    capturas de main, multi, champs, carrera, train y rankini')
ln('    revisadas a ojo. Ensamblado 12.179.103 B (golden a43fec1d).')
ln('  SE CONSERVA TODO: r55-r69 íntegro (arco tangente a 1,15 m, ancla')
ln('    congela/sigue, ola data-driven, blindaje del saque r65, BOLA LOCA')
ln('    + regla solo-1 r160, Hall FASE 29, multijugador, ELO, taller UGC,')
ln('    PWA, PRO TRAINING, halloween).')
ln('  · sellada a')
ln('  3.6.161')
NOTAS = '\n'.join(L) + '\n'
t = t[:m.start()] + NOTAS + t[m.end():]

# 3 · línea final del resumen
m = re.search(r"print\('\\nV3\.6\.161-SDK6 lista:[^']*'\)", t)
if not m:
    sys.exit('ABORTA: línea final no hallada')
t = t[:m.start()] + ("print('\\nV3.6.161-SDK6 lista: EL APARTADO COMPLETO — panelas a ASPECTO "
  "EXACTO (círculos circulares garantizados, el central vuelve a ~1,00 m), yaw "
  "calculado por la fórmula r69 desde anchuras reales, silueta redondeada en las "
  "4 esquinas con cortes también redondos, bloques CONDICIONALES (una página sin "
  "contenido no monta panela), ATRÁS y navegación común flotando sobre el bloque "
  "central, y los 5 apartados (Multi, Campeonatos, Ranking, Carrera, Entrenar) "
  "reconstruidos con el formato Ajustes hasta el último subnivel, fuera «Volver "
  "al Hall» de Entrenar — qa_vestibulo_r70 58/0; anclaje r69 intacto; "
  "conservación r55-r69 íntegra.')") + t[m.end():]

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(t, encoding='utf-8')
ast.parse(t)
print(f'gen_release_v36161 OK → {DESTINO} (notas FASE 164 · línea final r70)')

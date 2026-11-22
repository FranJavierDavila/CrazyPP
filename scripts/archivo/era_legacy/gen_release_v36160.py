#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36160.py — FASE 163 · r69 · generador del release.
Re-sella scripts/release-v36159/build_zip.py → scripts/release-v36160/:
  · tokens de versión (v36159→v36160 · 3.6.159→3.6.160) — el candado del
    hub hereda v36159 como versión vetada automáticamente.
  · notas del release: FASE 162 → FASE 163 (CORRECCIÓN DEL ARCO).
  · línea final del resumen con el contenido real de r69."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36159/build_zip.py'
DESTINO = RAIZ / 'release-v36160/build_zip.py'

t = ORIGEN.read_text(encoding='utf-8')

# 1 · tokens de versión (el candado del hub se actualiza solo: al girar
#     las etiquetas, la v36159 pasa a la lista de vetadas)
for a, b in [('v36159-sdk6', 'v36160-sdk6'),
             ('V3.6.159-SDK6', 'V3.6.160-SDK6'),
             ('3.6.159-SDK6', '3.6.160-SDK6'),
             ('v36159', 'v36160'),
             ('3.6.159', '3.6.160')]:
    t = t.replace(a, b)

# 1b · el candado del hub veta también la v36159
t = t.replace("'v36158-sdk6' in hub",
              "'v36158-sdk6' in hub or 'v36159-sdk6' in hub")

# 2 · notas FASE 162 → FASE 163: el bloque es una CONCATENACIÓN de
#     literales con comilla simple y \n embebido, sangría 4, SIN comas —
#     cierre real: «'  3.6.160\n'» (ya girado por los tokens)
m = re.search(r"'Rama    : main · SDK6 \(FASE 162[^\0]*?'  3\.6\.160\\n'", t)
if not m:
    sys.exit('ABORTA: bloque de notas FASE 162 no hallado')
L = []


def ln(s):
    L.append("    '" + s + "\\n'")


ln('Rama    : main · SDK6 (FASE 163 — CORRECCIÓN DEL ARCO: informe del')
ln('dueño tras V3.6.159 en el casco).')
ln('  · 1 · «LOS TRES BLOQUES NO SE PUEDEN PISAR O SUPERPONER, DEBEN IR')
ln('    UNOS SEGUIDOS A LOS OTROS»: panelas TANGENTES y consecutivas —')
ln('    las TRES a la MISMA distancia 1,15 m (equidistancia real, r68')
ln('    puso los lados a 1,25), cada una perpendicular a su radio; yaw =')
ln('    γC + γL + 0,8° con γ = atan(w/2/d) → bordes paralelos con ranura')
ln('    uniforme de ~1,7 cm, sin solape angular NI físico. Tamaños:')
ln('    centro 0,88 m · lados 0,66 m (lienzo virtual intacto: +14 % de')
ln('    texel/m — MÁS nitidez). Verificado por fórmulas en la QA.')
ln('  · 2 · «ESTÁS COLOCANDO MAL EL MENÚ»: r68 puso el origen del grupo')
ln('    EN la cabeza y lookAt hacia delante — el arco nacía a la ESPALDA.')
ln('    Restaurada la convención r67 (grupo DELANTE de la cara mirando A')
ln('    la cara) y el arco se centra en la cabeza con las posiciones')
ln('    locales (z = D_REF − cos(yaw)·dist). La QA mide la colocación en')
ln('    MUNDO: panela central a 1,135 m de proyección sobre la vista.')
ln('  · 3 · SEMÁNTICA DEL ANCLA (petición literal): al ABRIR el menú nace')
ln('    SIEMPRE justo delante de la mirada y queda FIJO (anclado); sin')
ln('    chincheta SIGUE a la cabeza SIEMPRE, de frente a donde miramos')
ln('    (comportamiento anterior); el botón chincheta CONGELA donde está')
ln('    y ahí lo recuerda; el heal r114 sigue curando viajes de escena.')
ln('    anchorMenu(forzar): las aperturas y el heal obligan; el botón,')
ln('    no. La chincheta vuelve a ser clicable (z +6 mm — r68 la dejó')
ln('    detrás del plano y no se podía pulsar).')
ln('  · 4 · DISEÑO LIMPIO HASTA EL ÚLTIMO SUBNIVEL: fuera los títulos del')
ln('    legado que duplicaban la concha (multi, join, name, gripname,')
ln('    rank, rankme, carrera, opts, optsCat y champs) — la concha manda')
ln('    en TODAS las páginas; TOOLTIPS espacio-conscientes (abrazadera al')
ln('    lienzo de SU espacio: 1024 legado / 3696 virtual — antes se')
ln('    desbordaban en el arco) y nunca bajo la cabecera.')
ln('  · 5 · CALIDAD: qa_vestibulo_r69.py 33 OK · 0 fallos — arco sin')
ln('    solape por fórmulas (ranura angular 0,85°), colocación en mundo,')
ln('    semántica del ancla (congela/sigue) y BARRIDO de 22 páginas con')
ln('    los rects dentro del lienzo virtual; capturas de main, AJUSTES >')
ln('    Sala y teclado de nombre revisadas a ojo. Ensamblado 12.163.159 B')
ln('    (golden 255fb05d).')
ln('  SE CONSERVA TODO: r55-r68 íntegro (ola data-driven, blindaje del')
ln('    saque r65, BOLA LOCA + regla solo-1 r160, Hall FASE 29,')
ln('    multijugador, ELO, taller UGC, PWA, PRO TRAINING, halloween).')
ln('  · sellada a')
ln('  3.6.160')
NOTAS = '\n'.join(L) + '\n'
t = t[:m.start()] + NOTAS + t[m.end():]

# 3 · línea final del resumen
m = re.search(r"print\('\\nV3\.6\.160-SDK6 lista:[^']*'\)", t)
if not m:
    sys.exit('ABORTA: línea final no hallada')
t = t[:m.start()] + ("print('\\nV3.6.160-SDK6 lista: CORRECCIÓN DEL ARCO — los tres bloques "
  "SEGUIDOS sin pisarse (tangentes al arco, los tres a 1,15 m, ranura de 1,7 cm), "
  "el menú nace DELANTE de la mirada y fijo (fin del arco a la espalda), sin "
  "chincheta SIGUE siempre de frente, el botón chincheta congela donde está y lo "
  "recuerda, chincheta vuelve a ser clicable, tooltips abrazados a su lienzo y "
  "nunca bajo la cabecera, y 9 títulos duplicados del legado fuera — la concha "
  "manda en todos los subniveles; qa_vestibulo_r69 33/0 con barrido de 22 páginas; "
  "conservación r55-r68 íntegra.')") + t[m.end():]

DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(t, encoding='utf-8')
ast.parse(t)
print(f'gen_release_v36160 OK → {DESTINO} (notas FASE 163 · línea final r69)')

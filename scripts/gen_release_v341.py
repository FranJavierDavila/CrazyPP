#!/usr/bin/env python3
"""Genera scripts/release-v341/ a partir de release-v340/:
· copia los ficheros neutros del relay tal cual
· adapta LEEME/CHULETA (sustitución de versión + nota del fix)
· construye build_zip.py con identidad V3.4.1-RIV1 (incluye el check de la
  NUEVA posición del ASTRO y la retirada del check antiguo)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v340')
DST = Path('/home/z/my-project/scripts/release-v341')

if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

# 1) ficheros neutros del relay (idénticos)
for f in ('server.mjs', 'package.json', 'mock_host.mjs', 'LEEME-live-service.md'):
    shutil.copy2(SRC / f, DST / f)
print('· relay neutro copiado (4 ficheros)')

# 2) LEEME-DESPLIEGUE.txt / CHULETA-DIRECTO.txt: versión + fix
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (SRC / name).read_text(encoding='utf-8')
    s = s.replace('3.4.0-IMP1', '3.4.1-RIV1').replace('v340-imp1', 'v341-riv1')
    s = s.replace('V3.4.0-IMP1', 'V3.4.1-RIV1')
    ancla = 'CRAZY PING PONG · V3.4.1-RIV1'
    i = s.index(ancla)
    fin_linea = s.index('\n', i)
    extra = ('\nFIX DE ESTA VERSIÓN: el ASTRO (rival de la Estación Orbital) está\n'
             'recolocado en la convención de duelos de la casa — junto a la esquina\n'
             'lejana derecha de la mesa, en espacio abierto (x 1,26 · z −3,82), la\n'
             'misma profundidad que CLOWN y WIZARD — y ya no se lee dentro de la\n'
             'pared frontal de la sala.')
    s = s[:fin_linea] + extra + s[fin_linea:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py: adaptación dirigida
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v340', 'release-v341').replace('staging-v340', 'staging-v341')
s = s.replace('3.4.0-IMP1', '3.4.1-RIV1')
s = s.replace('V3.4.0-IMP1', 'V3.4.1-RIV1')
s = s.replace('v340-imp1', 'v341-riv1')
# identidad: checks del hub (v341-riv1 presente, sin v340-imp1)
s = s.replace(
    "if 'v341-riv1' not in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:",
    "if 'v341-riv1' not in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:")
# manifest ahora v10
s = s.replace(
    "if man.get('version') != 9 or man['rival']['name'] != 'ASTRO':",
    "if man.get('version') != 10 or man['rival']['name'] != 'ASTRO':")
s = s.replace(
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.4.1 (ASTRO, manifest v9)')",
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.4.1 (ASTRO, manifest v10)')")
# módulo: posición NUEVA del ASTRO (1,26 · −3,82) y NO la antigua (1,62 · −4,5)
s = s.replace(
    "           'RIV_H = 2.15', 'position.set(1.62, RIV_H / 2',",
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 2.22',")
if "position.set(1.62, RIV_H / 2" in s:
    sys.exit_old = None
s = s.replace(
    "    if tk not in eo:\n        sys.exit(f'FALLO: el módulo orbital no contiene {tk!r}')",
    "    if tk not in eo:\n        sys.exit(f'FALLO: el módulo orbital no contiene {tk!r}')\n"
    "if 'position.set(1.62, RIV_H / 2' in eo:\n"
    "    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en la posición v3.2.1 (x 1,62 · z −4,5)')")
# VERSION.txt: novedades de ESTA versión
s = s.replace(
    "    'Base    : V3.1.2-CCD1 (precisión de contacto por CCD SDF) + V3.2.x-ORB + V3.3.0-NUC1\\n'\n"
    "    'Rama    : main · IMP1 (Reactor de impulso en la etapa 4)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.3.0-NUC1) — mecánica del dueño:\\n'",
    "    'Base    : V3.4.0-IMP1 (Reactor de impulso) + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
    "    'Rama    : main · RIV1 (ASTRO recolocado en la sala del orbital)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.4.0-IMP1):\\n'\n"
    "    '  · FIX DE COLOCACIÓN DEL ASTRO (informe del dueño: «el rival sigue\\n'\n"
    "    '    apareciendo dentro de la pared»): el spot v3.2.1 (x 1,62 · z −4,5)\\n'\n"
    "    '    dejaba al rival a sólo 1,05 m de la pared frontal y desde el punto\\n'\n"
    "    '    de vista del jugador se fundía con el arte de la pared. AHORA usa\\n'\n"
    "    '    la convención EXACTA de los rivales bien colocados de la casa\\n'\n"
    "    '    (REGLA FIJA de duelos, locura/magia v2.71): x = borde derecho de\\n'\n"
    "    '    la mesa + 0,50 = 1,26 · z = −3,82 — la misma profundidad del\\n'\n"
    "    '    CLOWN y del WIZARD: en espacio abierto, visible sin problemas,\\n'\n"
    "    '    cuerpo entero de 2,15 m con los pies en el suelo.\\n'")
# menciones del hub empaquetado: ahora 3.4.1
s = s.replace(
    "out = run(f'unzip -p \"{zip_c}\" extras-nextjs/descargas/page.tsx | grep -c \"3.4.0\" || true')\n"
    "n340 = int(out.strip() or '0')\n"
    "print(f'  page.tsx dentro del COMPLETO: {n340} menciones 3.4.0')\n"
    "if n340 < 4:",
    "out = run(f'unzip -p \"{zip_c}\" extras-nextjs/descargas/page.tsx | grep -c \"3.4.1\" || true')\n"
    "n341 = int(out.strip() or '0')\n"
    "print(f'  page.tsx dentro del COMPLETO: {n341} menciones 3.4.1')\n"
    "if n341 < 4:")
s = s.replace(
    "    sys.exit('FALLO: el hub empaquetado no es el v340 (¿se editó después de construir?)')",
    "    sys.exit('FALLO: el hub empaquetado no es el v341 (¿se editó después de construir?)')")
# nota cloudflare
s = s.replace(
    "'etapa 4 — cubos cuánticos, pistola láser, dianas y perturbaciones —,\\n'\n"
    "    'el REACTOR DE ENERGÍA INESTABLE en la etapa 2, la ESTACIÓN ORBITAL\\n'\n"
    "    'afinada, la CCD SDF de contacto, el saque VR realista y el hall del\\n'",
    "'el ASTRO de la Estación Orbital RECOLOCADO (convención de duelos, ya\\n'\n"
    "    'no se lee dentro de la pared), la etapa 4 — REACTOR DE IMPULSO: cubos\\n'\n"
    "    'cuánticos, pistola láser, dianas y perturbaciones —, el REACTOR DE\\n'\n"
    "    'ENERGÍA INESTABLE en la etapa 2, la CCD SDF de contacto, el saque VR\\n'\n"
    "    'realista y el hall del\\n'")
# cierre
s = s.replace(
    "print('\\nV3.4.1-RIV1 lista: Reactor de impulso en la etapa 4 (cubos cuánticos, pistola láser, dianas y perturbaciones).')",
    "print('\\nV3.4.1-RIV1 lista: ASTRO recolocado (convención de duelos) + Reactor de impulso en la etapa 4.')")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# verificación rápida de los anclajes clave
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.4.1-RIV1'" in t),
    ("position.set(1.26, RIV_H / 2" in t),
    ("(D.tableCenterZ || -1.6) - 2.22" in t),
    ("position.set(1.62, RIV_H / 2' in eo" in t),
    ("man.get('version') != 10" in t),
    ("'v341-riv1' not in hub or 'v340-imp1' in hub" in t),
    ('crazypp-v341-riv1-COMPLETO.zip' in t),
    ('Novedades de esta versión (frente a V3.4.0-IMP1)' in t),
    ('REGLA FIJA de duelos, locura/magia v2.71' in t),
    ("grep -c \"3.4.1\"" in t),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print('· anclajes de identidad: OK (10/10)')

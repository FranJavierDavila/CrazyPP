#!/usr/bin/env python3
"""Genera scripts/release-v360/ a partir de release-v351/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.0-SUP1 (superpoderes redefinidos + voz del ASTRO + ajustes
del reactor: diana 2 s y pelota que siempre vuelve a la base)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v351')
DST = Path('/home/z/my-project/scripts/release-v360')

if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

# 1) relay neutro
for f in ('server.mjs', 'package.json', 'mock_host.mjs', 'LEEME-live-service.md'):
    shutil.copy2(SRC / f, DST / f)
print('· relay neutro copiado (4 ficheros)')

# 2) LEEME/CHULETA
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (SRC / name).read_text(encoding='utf-8')
    s = s.replace('3.5.1-IMP2', '3.6.0-SUP1').replace('v351-imp2', 'v360-sup1')
    s = s.replace('V3.5.1-IMP2', 'V3.6.0-SUP1')
    ancla = 'CRAZY PING PONG · V3.6.0-SUP1'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: SUPERPODERES REDEFINIDOS por el dueño\n'
             '+ LA VOZ DEL ASTRO. El aviso «Super Power!!» congela la partida\n'
             'de verdad (como en La Locura de siempre); los METEORITOS son ahora\n'
             'pequeñas ROCAS EN 3D con vetas de óxido, calor de entrada y\n'
             'tumbling; el RAYO TRACTOR sale de un mini DRON y ATRAPA la bola\n'
             'flotando dentro del rayo hasta que desaparece y la deja caer en\n'
             'vertical; la GRAVEDAD CERO atrae la bola y la hace rebotar ENTRE\n'
             'las partículas blancas hasta que desaparecen; el ASTRO estrena los\n'
             'audios risa_astro.mp3 (pose de risas) y enfado_astro.mp3 (pierde\n'
             'un punto). En el REACTOR DE IMPULSO la diana permanece visible 2 s\n'
             'y la pelota SIEMPRE vuelve a botar sobre la base flotante.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v351', 'release-v360').replace('staging-v351', 'staging-v360')
s = s.replace('V3.5.1-IMP2', 'V3.6.0-SUP1').replace('3.5.1-IMP2', '3.6.0-SUP1')
s = s.replace('v351-imp2', 'v360-sup1')
# identidad: hub (v360 presente, sin v351 ni anteriores)
s = s.replace(
    "if 'v360-sup1' not in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:",
    "if 'v360-sup1' not in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:")
s = s.replace(
    "if man.get('version') != 12 or man['rival']['name'] != 'ASTRO':",
    "if man.get('version') != 13 or man['rival']['name'] != 'ASTRO':")
s = s.replace(
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.4.0 (ASTRO, manifest v9)')",
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.6.0 (ASTRO, manifest v13)')")
# módulo: tokens SUP1 (meteoritos 3D, dron del tractor, trampa, gravedad cero,
# audios, diana 2 s, reposo, freeze)
s = s.replace(
    "           'alphaTest: ventanal ? 0.35 : 0', 'warpSpeed',\n"
    "           \"imp.phase === 'play' || imp.phase === 'intro'\",",
    "           'alphaTest: ventanal ? 0.35 : 0', 'warpSpeed',\n"
    "           \"imp.phase === 'play' || imp.phase === 'intro'\",\n"
    "           'function _geoMeteorito', '_rocasGeo = [_geoMeteorito(0)',\n"
    "           'vertexColors: true, flatShading: true', 'emissive: 0xff6a22',\n"
    "           'dronTractor', '_tractorTrap', 'caída vertical pura',\n"
    "           'const ATT = 7.5', 'this._sfx(\\'risa_astro.mp3\\')',\n"
    "           'this._sfx(\\'enfado_astro.mp3\\')', 'dianaVis: 2.0',\n"
    "           'this._restT > 0.6', 'this.game.freezeT = Math.max',")
# assets: los dos mp3 del dueño entran en la lista de presencia
s = s.replace(
    "           'pistol.glb', 'mapa.png', 'superpower.png', 'angry.webp'):",
    "           'pistol.glb', 'mapa.png', 'superpower.png', 'angry.webp',\n"
    "           'risa_astro.mp3', 'enfado_astro.mp3'):")
# byte-exactos de los mp3
s = s.replace(
    "if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:\n"
    "    sys.exit('FALLO: diana_quantica.png no es byte-exacta (409.356 B)')",
    "if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:\n"
    "    sys.exit('FALLO: diana_quantica.png no es byte-exacta (409.356 B)')\n"
    "if (PUB / 'championships/estacion_orbital/assets/risa_astro.mp3').stat().st_size != 81408:\n"
    "    sys.exit('FALLO: risa_astro.mp3 no es byte-exacto (81.408 B)')\n"
    "if (PUB / 'championships/estacion_orbital/assets/enfado_astro.mp3').stat().st_size != 37616:\n"
    "    sys.exit('FALLO: enfado_astro.mp3 no es byte-exacto (37.616 B)')")
s = s.replace("print('· Identidad verificada: game.html V3.6.0-SUP1 + hub v360-sup1 + impulso afinado en la etapa 2')",
              "print('· Identidad verificada: game.html V3.6.0-SUP1 + hub v360-sup1 + superpoderes redefinidos + voz del ASTRO')")
# VERSION.txt: base y rama
s = s.replace(
    "    'Base    : V3.4.1-RIV1 + V3.4.0-IMP1 + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
    "    'Rama    : main · ESC1 (Escudo de pala · Defensa del casco)\\n\\n'",
    "    'Base    : V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
    "    'Rama    : main · SUP1 (Superpoderes redefinidos + voz del ASTRO)\\n\\n'")
# VERSION.txt: novedades de la SUP1 (bloque completo)
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.5.1-IMP2):\\n'\n"
    "    '  · SUPERPODERES REDEFINIDOS por el dueño + LA VOZ DEL ASTRO.\\n'\n"
    "    '  · AVISO CON LA PARTIDA CONGELADA: cuando el cartel «Super\\n'\n"
    "    '    Power!!» anuncia un poder, el juego se congela de verdad (IA,\\n'\n"
    "    '    física, saque y árbitro) hasta que el aviso desaparece — como\\n'\n"
    "    '    en La Locura de siempre.\\n'\n"
    "    '  · METEORITOS EN 3D: fuera las imágenes recortadas — ahora caen\\n'\n"
    "    '    pequeñas ROCAS procedurales (basalto con vetas de óxido,\\n'\n"
    "    '    calor de entrada y tumbling) que se posan sobre tu campo y\\n'\n"
    "    '    estallan al bloquear la bola.\\n'\n"
    "    '  · RAYO TRACTOR con DRON: un mini dron flota ENCIMA del haz y el\\n'\n"
    "    '    rayo sale de su emisor. Si la bola cruza el rayo (o es\\n'\n"
    "    '    interceptada) queda ATRAPADA flotando dentro del rayo y SOLO\\n'\n"
    "    '    cuando el rayo desaparece cae VERTICALMENTE.\\n'\n"
    "    '  · GRAVEDAD CERO real: las partículas blancas ATRAEN la bola y\\n'\n"
    "    '    la hacen rebotar ENTRE ELLAS de manera aleatoria hasta que\\n'\n"
    "    '    desaparecen y la dejan caer.\\n'\n"
    "    '  · AUDIOS DEL ASTRO (mp3 del dueño): risa_astro.mp3 cuando se\\n'\n"
    "    '    burla con la pose de risas (punto perdido y derrotas de las\\n'\n"
    "    '    pruebas) y enfado_astro.mp3 cuando pierde un punto.\\n'\n"
    "    '  · REACTOR DE IMPULSO: la diana cuántica permanece visible 2 s\\n'\n"
    "    '    (antes 1 s: casi imposible de disparar) y la pelota SIEMPRE\\n'\n"
    "    '    vuelve a botar sobre la base flotante (si queda reposa, se\\n'\n"
    "    '    recupera sola; adiós la pelota perdida tras el primer golpeo).\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR DE\\n'\n"
    "    '    ENERGÍA INESTABLE, la CCD SDF de contacto (CCD1), el saque VR\\n'\n"
    "    '    realista (SRV2), la gracia del saque, el bote honesto, el hall\\n'\n"
    "    '    del anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'\n"
    "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
# hashes: los mp3 entran en la ficha
s = s.replace(
    "    'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb'),",
    "    'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb'),\n"
    "    'championships/estacion_orbital/assets/risa_astro.mp3':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/risa_astro.mp3'),\n"
    "    'championships/estacion_orbital/assets/enfado_astro.mp3':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/enfado_astro.mp3'),")
# menciones del hub empaquetado
s = s.replace('grep -c "3.5.1"', 'grep -c "3.6.0"')
s = s.replace("n351 = int(out.strip() or '0')", "n360 = int(out.strip() or '0')")
s = s.replace("print(f'  page.tsx dentro del COMPLETO: {n351} menciones 3.5.1')",
              "print(f'  page.tsx dentro del COMPLETO: {n360} menciones 3.6.0')")
s = s.replace("if n351 < 4:", "if n360 < 4:")
s = s.replace("sys.exit('FALLO: el hub empaquetado no es el v351 (¿se editó después de construir?)')",
              "sys.exit('FALLO: el hub empaquetado no es el v360 (¿se editó después de construir?)')")
# nota cloudflare: párrafo Contenido reescrito para SUP1
old = ("    'Contenido: index.html (el juego con el REACTOR DE IMPULSO en la\\n'\n"
       "    'el ESCUDO DE PALA en la etapa 4 (orbes de plasma, drones piratas,\\n'\n"
       "    'Centinela y nave abordadora), el REACTOR DE IMPULSO AFINADO en la\\n'\n"
       "    'etapa 2 (golpeo CCD real de la pala, pistola láser en la mano, dianas\\n'\n"
       "    'con desintegración, cubos a la mitad con la estética del decorado,\\n'\n"
       "    'ventanas con velocidad lumínica tras el cristal, atractor sin solapes,\\n'\n"
       "    'pantalla legible y núcleo detallado), el ASTRO a distancia fija de la\\n'\n"
       "    'mesa, la CCD SDF de contacto, el saque VR realista y el hall del\\n'\n"
       "    'anfitrión), tv.html (CRAZY TV), assets/, championships/ (5\\n'")
new = ("    'Contenido: index.html (el juego con los SUPERPODERES REDEFINIDOS:\\n'\n"
       "    'aviso con la partida congelada, METEORITOS en 3D, RAYO TRACTOR con\\n'\n"
       "    'dron que atrapa la bola hasta soltarla en caída vertical, GRAVEDAD\\n'\n"
       "    'CERO que hace rebotar la bola entre partículas y la voz del ASTRO\\n'\n"
       "    '(risa_astro.mp3 / enfado_astro.mp3), el ESCUDO DE PALA en la etapa\\n'\n"
       "    '4, el REACTOR DE IMPULSO en la etapa 2 con dianas visibles 2 s y\\n'\n"
       "    'la pelota que siempre vuelve a la base, la CCD SDF de contacto, el\\n'\n"
       "    'saque VR realista y el hall del anfitrión), tv.html (CRAZY TV),\\n'\n"
       "    'assets/, championships/ (5\\n'")
if s.count(old) == 1:
    s = s.replace(old, new)
    print('· nota Cloudflare adaptada')
# cierre
s = s.replace("print('\\nV3.6.0-SUP1 lista: REACTOR DE IMPULSO afinado (8 correcciones del dueño) + ASTRO a distancia fija de la mesa.')",
              "print('\\nV3.6.0-SUP1 lista: SUPERPODERES REDEFINIDOS (freeze, meteoritos 3D, tractor con dron, gravedad cero) + voz del ASTRO + diana 2 s.')")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.0-SUP1'" in t),
    ("'v360-sup1' not in hub or 'v351-imp2' in hub" in t),
    ("man.get('version') != 13" in t),
    ("'function _geoMeteorito'" in t),
    ("'dronTractor', '_tractorTrap', 'caída vertical pura'" in t),
    ("'const ATT = 7.5'" in t),
    ("'this._sfx(\\'risa_astro.mp3\\')'" in t),
    ("'dianaVis: 2.0'" in t),
    ("'this._restT > 0.6'" in t),
    ("'this.game.freezeT = Math.max'" in t),
    ("'risa_astro.mp3', 'enfado_astro.mp3'):" in t),
    ('risa_astro.mp3 no es byte-exacto (81.408 B)' in t),
    ('Novedades de esta versión (frente a V3.5.1-IMP2)' in t),
    ('grep -c "3.6.0"' in t),
    ('crazypp-v360-sup1-COMPLETO.zip' in t),
    ('menciones 3.6.0' in t),
    ('SUPERPODERES REDEFINIDOS (freeze, meteoritos 3D' in t),
    ('Rama    : main · SUP1' in t),
    ('staging-v351' not in t),
    # las únicas menciones permitidas de la versión ANTERIOR: la línea Base y
    # el encabezado del bloque de novedades (frente a V3.5.1-IMP2)
    (t.count('3.5.1-IMP2') == 2),
    ("t.count('v351-imp2') == 1 and 'v351-imp2' in hub" in t or t.count('v351-imp2') == 1),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print('· anclajes de identidad: OK (21/21)')

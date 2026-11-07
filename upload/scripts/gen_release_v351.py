#!/usr/bin/env python3
"""Genera scripts/release-v351/ a partir de release-v350/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.5.1-IMP2 (ajuste fino del Reactor de impulso + ASTRO etapa 1
a distancia fija de la mesa)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v350')
DST = Path('/home/z/my-project/scripts/release-v351')

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
    s = s.replace('3.5.0-ESC1', '3.5.1-IMP2').replace('v350-esc1', 'v351-imp2')
    s = s.replace('V3.5.0-ESC1', 'V3.5.1-IMP2')
    ancla = 'CRAZY PING PONG · V3.5.1-IMP2'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: AJUSTE FINO del «REACTOR DE IMPULSO»\n'
             'por el informe del dueño en casco: el golpeo de la pala es ahora\n'
             'REAL (el mismo barrido CCD esfera-pala del juego, no un bumper en\n'
             'el agarre), la PISTOLA LÁSER ya aparece en la mano libre, las\n'
             'DIANAS aparecen y desaparecen con un efecto de DESINTEGRACIÓN,\n'
             'los CUBOS CUÁNTICOS son la mitad de pequeños y están elaborados\n'
             'con la estética del decorado, el efecto de VELOCIDAD LUMÍNICA se\n'
             've a través del cristal de los ventanales con el espacio negro\n'
             'pasando a toda velocidad (la nave avanza), el ATRACTOR agrupa los\n'
             'cubos casi unidos sin penetrarse, los textos de la PANTALLA viven\n'
             'dentro del panel sin cortarse y el NÚCLEO es un modelo detallado.\n'
             'El ASTRO de la etapa 1 se coloca a distancia fija de la mesa,\n'
             'totalmente visible.')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v350', 'release-v351').replace('staging-v350', 'staging-v351')
s = s.replace('3.5.0-ESC1', '3.5.1-IMP2').replace('V3.5.0-ESC1', 'V3.5.1-IMP2')
s = s.replace('v350-esc1', 'v351-imp2')
# identidad: hub (v351 presente, sin v350 ni anteriores)
s = s.replace(
    "if 'v351-imp2' not in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:",
    "if 'v351-imp2' not in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:")
s = s.replace(
    "if man.get('version') != 11 or man['rival']['name'] != 'ASTRO':",
    "if man.get('version') != 12 or man['rival']['name'] != 'ASTRO':")
s = s.replace(
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.1 (ASTRO, manifest v11)')",
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.1 (ASTRO, manifest v12)')")
s = s.replace(
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.0 (ASTRO, manifest v11)')",
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.1 (ASTRO, manifest v12)')")
s = s.replace("print('· Identidad verificada: game.html V3.5.1-IMP2 + hub v351-imp2 + impulso en la etapa 4')",
              "print('· Identidad verificada: game.html V3.5.1-IMP2 + hub v351-imp2 + impulso afinado en la etapa 2')")
# módulo: ASTRO v3.5.1 (z −3,30) sustituye al v3.4.1 (z −3,82) + tokens IMP2
s = s.replace(
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 2.22',",
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 1.70',\n"
    "           'cubeS: 0.16, cubeHitR: 0.14', 'ballT: 0.80, ballH: 0.34',\n"
    "           'atrSep: 0.19', 'static HUECOS', '_atractorSepara',\n"
    "           'dianaMat', 'ShaderMaterial', 'uDissolve',\n"
    "           'alphaTest: ventanal ? 0.35 : 0', 'warpSpeed',\n"
    "           \"imp.phase === 'play' || imp.phase === 'intro'\",")
# el ASTRO ya NO está en z −3,82
s = s.replace(
    "if 'position.set(1.62, RIV_H / 2' in eo:\n"
    "    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en la posición v3.2.1 (x 1,62 · z −4,5)')",
    "if 'position.set(1.62, RIV_H / 2' in eo:\n"
    "    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en la posición v3.2.1 (x 1,62 · z −4,5)')\n"
    "if '(D.tableCenterZ || -1.6) - 2.22' in eo:\n"
    "    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en el spot v3.4.1 (z −3,82)')")
# VERSION.txt: novedades de la IMP2 (bloque completo)
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.5.0-ESC1):\\n'\n"
    "    '  · AJUSTE FINO del REACTOR DE IMPULSO por el informe del dueño en\\n'\n"
    "    '    casco (8 correcciones) + el ASTRO de la etapa 1 a distancia\\n'\n"
    "    '    fija de la mesa.\\n'\n"
    "    '  · GOLPEO DE PALA REAL en el reactor: el contacto usa el MISMO\\n'\n"
    "    '    barrido CCD esfera-pala del núcleo que el Escudo de pala y el\\n'\n"
    "    '    rally (antes era un bumper en el AGARRE del mando, casi\\n'\n"
    "    '    imposible de acertar). Se golpea con la HOJA y con la física de\\n'\n"
    "    '    siempre: rebote, efecto y velocidad de la mano.\\n'\n"
    "    '  · Bote-en-espera más vivo sobre la base flotante (0,80 s) y\\n'\n"
    "    '    salida con propósito: 3..9 m/s tras cada golpeo.\\n'\n"
    "    '  · PISTOLA LÁSER (pistol.glb) VISIBLE en la mano libre durante\\n'\n"
    "    '    todo el reactor — antes nunca se montaba en esta prueba (el\\n'\n"
    "    '    montaje sólo corría en el muro arkanoid); ahora se arma desde la\\n'\n"
    "    '    intro y se guarda al salir.\\n'\n"
    "    '  · DIANAS CUÁNTICAS con DESINTEGRACIÓN: shader de disolución con\\n'\n"
    "    '    borde de energía al aparecer (materialización inversa) y al\\n'\n"
    "    '    desaparecer (con restos); el láser la desintegra aún más rápido.\\n'\n"
    "    '  · CUBOS CUÁNTICOS a la MITAD de tamaño (0,16 m) y elaborados con\\n'\n"
    "    '    la estética del decorado: marco de paneles de la sala, nodos\\n'\n"
    "    '    ámbar en las esquinas, carcasa oscura y núcleo interior azul\\n'\n"
    "    '    (estable) / rojo (inestable).\\n'\n"
    "    '  · VELOCIDAD LUMÍNICA DE VERDAD: el cristal de los ventanales\\n'\n"
    "    '    laterales es transparente (recorte alpha en el arte) y las\\n'\n"
    "    '    partículas corren FUERA de la sala de DELANTE hacia ATRÁS a\\n'\n"
    "    '    13-26 m/s sobre el fondo negro del espacio: la nave avanza.\\n'\n"
    "    '  · ATRACTOR sin trampas: cada cubo converge a SU hueco del racimo\\n'\n"
    "    '    (centro + 6 caras) y una separación por pares los mantiene casi\\n'\n"
    "    '    unidos pero JAMÁS penetrándose (separación mínima 0,19 m).\\n'\n"
    "    '  · PANTALLA del techo legible: TODO el texto vive DENTRO de la\\n'\n"
    "    '    pantalla del arte (antes flotaba fuera del panel y las columnas\\n'\n"
    "    '    se solapaban).\\n'\n"
    "    '  · NÚCLEO detallado: columna de plasma con vidrio contrarrotante,\\n'\n"
    "    '    blindaje con costillas y marcas ámbar, domo con antena, peana\\n'\n"
    "    '    con aro y anillos de contención azul/rojo.\\n'\n"
    "    '  · ASTRO (etapa 1) a distancia fija de la mesa (z −3,30):\\n'\n"
    "    '    totalmente visible, fuera de la transición pintada de la pared\\n'\n"
    "    '    frontal; el dron vigía no molesta durante el reactor.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR DE\\n'\n"
    "    '    ENERGÍA INESTABLE, la CCD SDF de contacto (CCD1), el saque VR\\n'\n"
    "    '    realista (SRV2), la gracia del saque, el bote honesto, el hall\\n'\n"
    "    '    del anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'\n"
    "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
# menciones del hub empaquetado
s = s.replace('grep -c "3.5.0"', 'grep -c "3.5.1"')
s = s.replace("n350 = int(out.strip() or '0')", "n351 = int(out.strip() or '0')")
s = s.replace("print(f'  page.tsx dentro del COMPLETO: {n350} menciones 3.5.0')",
              "print(f'  page.tsx dentro del COMPLETO: {n351} menciones 3.5.1')")
s = s.replace("if n350 < 4:", "if n351 < 4:")
s = s.replace("sys.exit('FALLO: el hub empaquetado no es el v350 (¿se editó después de construir?)')",
              "sys.exit('FALLO: el hub empaquetado no es el v351 (¿se editó después de construir?)')")
# nota cloudflare: IMP2
old = "'la etapa 4 NUEVA — ESCUDO DE PALA · DEFENSA DEL CASCO (orbos de\\n'\n    'plasma, drones piratas, Centinela y nave abordadora) con arte propio —,\\n'\n    'el REACTOR DE IMPULSO en la etapa 2 (cubos cuánticos, pistola láser y\\n'\n    'dianas), el ASTRO RECOLOCADO (convención de duelos), la CCD SDF de\\n'\n    'contacto, el saque VR realista y el hall del\\n'"
new = "'el ESCUDO DE PALA en la etapa 4 (orbes de plasma, drones piratas,\\n'\n    'Centinela y nave abordadora), el REACTOR DE IMPULSO AFINADO en la\\n'\n    'etapa 2 (golpeo CCD real de la pala, pistola láser en la mano, dianas\\n'\n    'con desintegración, cubos a la mitad con la estética del decorado,\\n'\n    'ventanas con velocidad lumínica tras el cristal, atractor sin solapes,\\n'\n    'pantalla legible y núcleo detallado), el ASTRO a distancia fija de la\\n'\n    'mesa, la CCD SDF de contacto, el saque VR realista y el hall del\\n'"
if s.count(old) == 1:
    s = s.replace(old, new)
    print('· nota Cloudflare adaptada')
# cierre
s = s.replace("print('\\nV3.5.1-IMP2 lista: ESCUDO DE PALA en la etapa 4 + REACTOR DE IMPULSO en la etapa 2 (orden del dueño).')",
              "print('\\nV3.5.1-IMP2 lista: REACTOR DE IMPULSO afinado (8 correcciones del dueño) + ASTRO a distancia fija de la mesa.')")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.5.1-IMP2'" in t),
    ("class EscudoCasco" in t),
    ("'cubeS: 0.16, cubeHitR: 0.14'" in t),
    ("'(D.tableCenterZ || -1.6) - 1.70'" in t),
    ("man.get('version') != 12" in t),
    ("'v351-imp2' not in hub or 'v350-esc1' in hub" in t),
    ('crazypp-v351-imp2-COMPLETO.zip' in t),
    ('Novedades de esta versión (frente a V3.5.0-ESC1)' in t),
    ('grep -c "3.5.1"' in t),
    ('_atractorSepara' in t),
    ("(D.tableCenterZ || -1.6) - 2.22" not in t.split('sys.exit')[0].split('STAGE.mkdir')[0]),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print('· anclajes de identidad: OK (11/11)')

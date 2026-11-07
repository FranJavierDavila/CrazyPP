#!/usr/bin/env python3
"""Genera scripts/release-v350/ a partir de release-v341/ (mismo patrón que
gen_release_v341): relay neutro + LEEME/CHULETA con versión nueva + build_zip
con la identidad dura de la V3.5.0-ESC1 (escudo en etapa 4, impulso en etapa 2,
artefactos y checks del EscudoCasco)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v341')
DST = Path('/home/z/my-project/scripts/release-v350')

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
    s = s.replace('3.4.1-RIV1', '3.5.0-ESC1').replace('v341-riv1', 'v350-esc1')
    s = s.replace('V3.4.1-RIV1', 'V3.5.0-ESC1')
    ancla = 'CRAZY PING PONG · V3.5.0-ESC1'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: la etapa 4 estrena el «ESCUDO DE PALA ·\n'
             'DEFENSA DEL CASCO» con arte propio (escudo_pala/): la pala es un\n'
             'escudo manual que devuelve los orbes de plasma (estándar, pesado,\n'
             'inestable y rotor) de los drones piratas; el golpe limpio carga la\n'
             'SOBRECARGA hasta el orbe perforante; 3 fases (drones, Centinela de\n'
             'rally y nave abordadora de 3 cañones) con INTEGRIDAD DEL CASCO y\n'
             'Barrera de Casco trasera. El REACTOR DE IMPULSO sube a la etapa 2\n'
             '(orden del dueño) y el reactor v3.3.0 sale del camino. Además: el\n'
             'Hall ya no arrastra elementos al volver de un campeonato y el botón\n'
             'A/X cambia la pala de mano también en el entrenamiento (zurdos).')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v341', 'release-v350').replace('staging-v341', 'staging-v350')
s = s.replace('3.4.1-RIV1', '3.5.0-ESC1').replace('V3.4.1-RIV1', 'V3.5.0-ESC1')
s = s.replace('v341-riv1', 'v350-esc1')
# identidad: hub (v350 presente, sin v341 ni anteriores)
s = s.replace(
    "if 'v350-esc1' not in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:",
    "if 'v350-esc1' not in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:")
s = s.replace(
    "if man.get('version') != 10 or man['rival']['name'] != 'ASTRO':",
    "if man.get('version') != 11 or man['rival']['name'] != 'ASTRO':")
s = s.replace(
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.0 (ASTRO, manifest v10)')",
    "sys.exit('FALLO: el manifest de estacion_orbital no es el v3.5.0 (ASTRO, manifest v11)')")
# módulo: checks del camino nuevo + EscudoCasco + el ASTRO recolocado de v3.4.1 se conserva
s = s.replace(
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 2.22',",
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 2.22',\n"
    "           'class EscudoCasco', 'const ESC_CFG', \"id: 'escudo'\",\n"
    "           '_empezarEscudo', '_arrancarEscudo', 'escudo_pala/',\n"
    "           'window.__PP_PADDLE_SWEEP', 'BARRERA DE CASCO', 'champDecorHidden',")
# VERSION.txt: novedades de la ESC1
old_base = ("    'Base    : V3.4.0-IMP1 (Reactor de impulso) + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
            "    'Rama    : main · RIV1 (ASTRO recolocado en la sala del orbital)\\n\\n'\n"
            "    'Novedades de esta versión (frente a V3.4.0-IMP1):\\n'")
new_base = ("    'Base    : V3.4.1-RIV1 + V3.4.0-IMP1 + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
            "    'Rama    : main · ESC1 (Escudo de pala · Defensa del casco)\\n\\n'\n"
            "    'Novedades de esta versión (frente a V3.4.1-RIV1):\\n'\n"
            "    '  · ETAPA 4 NUEVA · ESCUDO DE PALA · DEFENSA DEL CASCO (mecánica\\n'\n"
            "    '    reactiva del dueño, arte propio v3.5.0 en escudo_pala/): la pala\\n'\n"
            "    '    es un ESCUDO MANUAL — devuelve los ORBES DE PLASMA (estándar 9-13\\n'\n"
            "    '    m/s, pesado de restitución baja, inestable con fusible 2,5 s y\\n'\n"
            "    '    rotor con curva) con la FÍSICA DE SIEMPRE y el MISMO barrido CCD\\n'\n"
            "    '    esfera-pala del juego (sin corrección de dirección).\\n'\n"
            "    '  · GOLPE LIMPIO (zona dulce 3,5 cm + ≥4 m/s) = destello, sonido y\\n'\n"
            "    '    +20 % de SOBRECARGA; al 100 % el siguiente golpe firme (≥3 m/s)\\n'\n"
            "    '    lanza un ORBE PERFORANTE que atraviesa y destruye núcleos.\\n'\n"
            "    '    Golpe sucio (canto/mango): devuelve sin bonificaciones.\\n'\n"
            "    '  · 3 FASES: 1) 3 drones artilleros · 2) 4 drones + el CENTINELA\\n'\n"
            "    '    (duelo de rally: su escudo devuelve el orbe con +10 %; a 5\\n'\n"
            "    '    devoluciones su núcleo queda expuesto 3 s) · 3) la NAVE\\n'\n"
            "    '    ABORDADORA: 3 cañones (3 HP, el golpe limpio cuenta 2), uno\\n'\n"
            "    '    activo cada 8 s con patrones propios, los cerrados son inmunes.\\n'\n"
            "    '    Interludios de 5 s: +30 de integridad y mensaje de NOVA.\\n'\n"
            "    '  · INTEGRIDAD DEL CASCO 100: la BARRERA DE CASCO trasera recibe\\n'\n"
            "    '    los proyectiles no devueltos (onda en el punto exacto); los\\n'\n"
            "    '    orbes JAMÁS colisionan con el jugador (zona segura de cabeza).\\n'\n"
            "    '    Alerta crítica ≤30 (luces rojas + alarma). Sin límite de tiempo:\\n'\n"
            "    '    presión creciente tras 90 s (cadencia −8 % cada 15 s, mín. 50 %).\\n'\n"
            "    '    PANTALLA del techo con fase, integridad, enemigos, Sobrecarga y\\n'\n"
            "    '    rally; NOVA narra la acción. Derrota: astro_laughing y regreso.\\n'\n"
            "    '  · REORDEN del dueño: el REACTOR DE IMPULSO pasa a la ETAPA 2 (el\\n'\n"
            "    '    reactor v3.3.0 sale del camino, clase conservada); el ASTRO sigue\\n'\n"
            "    '    en su convención de duelos (v3.4.1) y las salas propias ya no\\n'\n"
            "    '    arrastran recortes decorativos.\\n'\n"
            "    '  · FIX HALL: al volver de un campeonato el hall nace en saque\\n'\n"
            "    '    limpio — la bola ya no rueda sobre la mesa invisible.\\n'\n"
            "    '  · FIX ENTRENAMIENTO: A/X cambia la pala de mano también en el PRO\\n'\n"
            "    '    TRAINING (jugadores zurdos); el ajuste de pala sigue igual.\\n'")
assert s.count(old_base) == 1, 'base VERSION.txt'
s = s.replace(old_base, new_base)
# menciones del hub empaquetado
s = s.replace('grep -c "3.4.1"', 'grep -c "3.5.0"')
s = s.replace("n341 = int(out.strip() or '0')", "n350 = int(out.strip() or '0')")
s = s.replace("print(f'  page.tsx dentro del COMPLETO: {n341} menciones 3.4.1')",
              "print(f'  page.tsx dentro del COMPLETO: {n350} menciones 3.5.0')")
s = s.replace("if n341 < 4:", "if n350 < 4:")
s = s.replace("sys.exit('FALLO: el hub empaquetado no es el v341 (¿se editó después de construir?)')",
              "sys.exit('FALLO: el hub empaquetado no es el v350 (¿se editó después de construir?)')")
# nota cloudflare: añade el escudo
old = "'el ASTRO de la Estación Orbital RECOLOCADO (convención de duelos, ya\\n'\n    'no se lee dentro de la pared), la etapa 4 — REACTOR DE IMPULSO: cubos\\n'\n    'cuánticos, pistola láser, dianas y perturbaciones —, el REACTOR DE\\n'\n    'ENERGÍA INESTABLE en la etapa 2, la CCD SDF de contacto, el saque VR\\n'\n    'realista y el hall del\\n'"
new = "'la etapa 4 NUEVA — ESCUDO DE PALA · DEFENSA DEL CASCO (orbos de\\n'\n    'plasma, drones piratas, Centinela y nave abordadora) con arte propio —,\\n'\n    'el REACTOR DE IMPULSO en la etapa 2 (cubos cuánticos, pistola láser y\\n'\n    'dianas), el ASTRO RECOLOCADO (convención de duelos), la CCD SDF de\\n'\n    'contacto, el saque VR realista y el hall del\\n'"
if s.count(old) == 1:
    s = s.replace(old, new)
    print('· nota Cloudflare adaptada')
# cierre
s = s.replace("print('\\nV3.5.0-ESC1 lista: ASTRO recolocado (convención de duelos) + Reactor de impulso en la etapa 4.')",
              "print('\\nV3.5.0-ESC1 lista: ESCUDO DE PALA en la etapa 4 + REACTOR DE IMPULSO en la etapa 2 (orden del dueño).')")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.5.0-ESC1'" in t),
    ("class EscudoCasco" in t),
    ("id: 'escudo'" in t),
    ("'position.set(1.26, RIV_H / 2'" in t),
    ("man.get('version') != 11" in t),
    ("'v350-esc1' not in hub or 'v341-riv1' in hub" in t),
    ('crazypp-v350-esc1-COMPLETO.zip' in t),
    ('Novedades de esta versión (frente a V3.4.1-RIV1)' in t),
    ('grep -c "3.5.0"' in t),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print('· anclajes de identidad: OK (9/9)')

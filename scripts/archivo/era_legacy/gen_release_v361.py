#!/usr/bin/env python3
"""Genera scripts/release-v361/ a partir de release-v360/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.1-SDK1 (FASE 3 de la modularización P0: SDK de campeonatos
champ_sdk.js v1.0.0 + orbital adoptante con conducta idéntica)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v360')
DST = Path('/home/z/my-project/scripts/release-v361')

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
    s = s.replace('3.6.0-SUP1', '3.6.1-SDK1').replace('v360-sup1', 'v361-sdk1')
    ancla = 'CRAZY PING PONG · V3.6.1-SDK1'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: el SDK DE CAMPEONATOS (champ_sdk.js\n'
             'v1.0.0) — la FASE 3 de la modularización P0: el kernel que los 5\n'
             'campeonatos reimplementaban (motor SFX con la lección v2.125 «forma\n'
             'promesa», el congelado del aviso de superpoder patrón La Locura\n'
             'v2.40 y el puente al núcleo) vive ahora en UNA sola fuente. La\n'
             'Estación Orbital estrena la adopción con conducta idéntica y cero\n'
             'cambios de gameplay.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v360', 'release-v361').replace('staging-v360', 'staging-v361')
s = s.replace('3.6.0-SUP1', '3.6.1-SDK1').replace('v360-sup1', 'v361-sdk1')
# (tras el reemplazo anterior ya no quedan «3.6.0-SUP1»; los «3.6.0» sueltos:)
s = s.replace('3.6.0', '3.6.1').replace('n360', 'n361')
# identidad: hub (v361 presente, sin v360 ni anteriores)
s = s.replace(
    "if 'v361-sdk1' not in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:",
    "if 'v361-sdk1' not in hub or 'v360-sup1' in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:")
s = s.replace("no es el v3.6.1 (ASTRO, manifest v13)", "no es el v3.6.1 (ASTRO, manifest v14)")
s = s.replace("if man.get('version') != 13 or", "if man.get('version') != 14 or")
# módulo: el freeze del aviso vive ahora en el SDK (tokens SDK)
s = s.replace(
    "           'this._restT > 0.6', 'this.game.freezeT = Math.max',",
    "           'this._restT > 0.6', \"congela(this.game, (def.warn || 2.0) + 0.15)\",\n"
    "           \"from '../sdk/champ_sdk.js'\", 'createSfx(import.meta.url',\n"
    "           '__sdkSfx',")
# identidad del SDK de campeonatos (fichero nuevo)
s = s.replace(
    "if 'position.set(1.62, RIV_H / 2' in eo:",
    "sdkf = PUB / 'championships/sdk/champ_sdk.js'\n"
    "if not sdkf.exists():\n"
    "    sys.exit('FALLO: falta championships/sdk/champ_sdk.js (SDK de campeonatos)')\n"
    "sdk = sdkf.read_text(encoding='utf-8')\n"
    "for tk in (\"const SDK_VERSION = '1.0.0'\", 'export function createSfx',\n"
    "           'export function congela', 'export function descongela',\n"
    "           'export function getCore', 'export function assetURL',\n"
    "           'forma promesa (v2.125)', 'window.__PP_SDK = SDK_VERSION'):\n"
    "    if tk not in sdk:\n"
    "        sys.exit(f'FALLO: champ_sdk.js no contiene {tk!r}')\n"
    "if 'position.set(1.62, RIV_H / 2' in eo:")
# hashes de VERSION.txt: el SDK entra en la ficha
s = s.replace(
    "    'championships/estacion_orbital/assets/enfado_astro.mp3':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/enfado_astro.mp3'),",
    "    'championships/estacion_orbital/assets/enfado_astro.mp3':\n"
    "        sha256(STAGE / 'championships/estacion_orbital/assets/enfado_astro.mp3'),\n"
    "    'championships/sdk/champ_sdk.js':\n"
    "        sha256(STAGE / 'championships/sdk/champ_sdk.js'),")
# VERSION.txt: base y rama
s = s.replace(
    "    'Base    : V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
    "    'Rama    : main · SUP1 (Superpoderes redefinidos + voz del ASTRO)\\n\\n'",
    "    'Base    : V3.6.0-SUP1 + V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\\n'\n"
    "    'Rama    : main · SDK1 (SDK de campeonatos — kernel compartido de los 5)\\n\\n'")
# VERSION.txt: novedades de la SDK1 (bloque completo)
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.6.0-SUP1):\\n'\n"
    "    '  · SDK DE CAMPEONATOS (FASE 3 de la modularización P0): nace\\n'\n"
    "    '    championships/sdk/champ_sdk.js v1.0.0 — el kernel que los 5\\n'\n"
    "    '    campeonatos reimplementaban vive ahora en UNA sola fuente:\\n'\n"
    "    '    motor de SFX canónico (fetch + decodeAudioData en forma\\n'\n"
    "    '    promesa — la lección v2.125 que llegó a estar copiada 7 veces\\n'\n"
    "    '    en el Oeste y 2 en Magia —, cache por nombre, respeta el\\n'\n"
    "    '    silencio del arcade), congela()/descongela() del aviso de\\n'\n"
    "    '    superpoder (patrón de La Locura v2.40) y el puente al núcleo.\\n'\n"
    "    '    Un bug del kernel se arregla UNA vez y sirven los 5.\\n'\n"
    "    '  · ESTACIÓN ORBITAL adopta el SDK: su motor _sfx (voz del\\n'\n"
    "    '    ASTRO) y el congelado del aviso delegan en champ_sdk con\\n'\n"
    "    '    conducta idéntica; manifest v14.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta, los\\n'\n"
    "    '    4 superpoderes redefinidos de SUP1, el reactor, el escudo y\\n'\n"
    "    '    los duelos se comportan exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
# identidad imprimida y cierre
s = s.replace("+ hub v361-sdk1 + superpoderes redefinidos + voz del ASTRO')",
              "+ hub v361-sdk1 + SDK de campeonatos (orbital adoptante)')")
s = s.replace(
    "V3.6.1-SDK1 lista: SUPERPODERES REDEFINIDOS (freeze, meteoritos 3D, tractor con dron, gravedad cero) + voz del ASTRO + diana 2 s.",
    "V3.6.1-SDK1 lista: SDK DE CAMPEONATOS (kernel único de los 5) + superpoderes redefinidos + voz del ASTRO + diana 2 s.")
# nota cloudflare: contenido con el SDK + championships incluye sdk/
s = s.replace(
    "    'Contenido: index.html (el juego con los SUPERPODERES REDEFINIDOS:\\n'",
    "    'Contenido: index.html (el juego con el SDK DE CAMPEONATOS de la\\n'\n"
    "    'FASE 3 — kernel único de los 5 campeonatos — y los SUPERPODERES\\n'\n"
    "    'REDEFINIDOS:\\n'")
s = s.replace(
    "    'assets/, championships/ (5\\n'\n"
    "    'campeonatos), vendor/, LEEME-DESPLIEGUE.txt y VERSION.txt.\\n\\n'",
    "    'assets/, championships/ (5 campeonatos + el SDK compartido\\n'\n"
    "    'sdk/champ_sdk.js), vendor/, LEEME-DESPLIEGUE.txt y VERSION.txt.\\n\\n'")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# 4) anclajes de identidad del build_zip generado
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.1-SDK1'" in t),
    ("'V3.6.1-SDK1'" in t),
    ("if 'v361-sdk1' not in hub or 'v360-sup1' in hub" in t),
    ("man.get('version') != 14" in t),
    ("no es el v3.6.1 (ASTRO, manifest v14)" in t),
    ("'function _geoMeteorito'" in t),
    ("'dronTractor', '_tractorTrap', 'caída vertical pura'" in t),
    ("'this._sfx(\\'risa_astro.mp3\\')'" in t),
    ("'dianaVis: 2.0'" in t),
    ("'this._restT > 0.6'" in t),
    ("\"congela(this.game, (def.warn || 2.0) + 0.15)\"" in t),
    ("\"from '../sdk/champ_sdk.js'\"" in t),
    ("'createSfx(import.meta.url'" in t),
    ("'__sdkSfx'" in t),
    ("championships/sdk/champ_sdk.js" in t),
    ("window.__PP_SDK = SDK_VERSION" in t),
    ('Novedades de esta versión (frente a V3.6.0-SUP1)' in t),
    ('Rama    : main · SDK1' in t),
    ('grep -c "3.6.1"' in t),
    ('menciones 3.6.1' in t),
    ('crazypp-v361-sdk1-COMPLETO.zip' in t),
    ('crazypp-v361-sdk1-CLOUDFLARE.zip' in t),
    ('crazypp-v361-sdk1-ligera.zip' in t),
    ('SDK DE CAMPEONATOS (kernel único de los 5)' in t),
    ('el SDK compartido' in t),
    ('staging-v360' not in t),
    ('release-v360' not in t),
    # las únicas menciones permitidas de la versión ANTERIOR: la línea Base,
    # el encabezado «frente a» y el hub prohibido (1)
    (t.count('3.6.0-SUP1') == 2),
    (t.count('v360-sup1') == 1),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print(f'· anclajes de identidad: OK ({len(checks)}/{len(checks)})')

# 5) LEEME/CHULETA anclados
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DST / name).read_text(encoding='utf-8')
    assert 'V3.6.1-SDK1' in s and 'champ_sdk' in s, name
    assert 'v360-sup1' not in s, name
print('· LEEME/CHULETA anclados: OK')

print('\nrelease-v361/ listo: python3 scripts/release-v361/build_zip.py')

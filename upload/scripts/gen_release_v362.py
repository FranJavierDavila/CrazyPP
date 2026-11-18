#!/usr/bin/env python3
"""Genera scripts/release-v362/ a partir de release-v361/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.2-SDK2 (FASE 4 de la modularización P0: el SDK de campeonatos
champ_sdk.js v1.1.0 adoptado por oeste/magia/locura/valle_neon)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v361')
DST = Path('/home/z/my-project/scripts/release-v362')

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
    s = s.replace('3.6.1-SDK1', '3.6.2-SDK2').replace('v361-sdk1', 'v362-sdk2')
    ancla = 'CRAZY PING PONG · V3.6.2-SDK2'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: la FASE 4 de la modularización — el\n'
             'SDK DE CAMPEONATOS (champ_sdk.js v1.1.0) ya lo usan LOS 5\n'
             'campeonatos: Oeste (4 motores SFX + 3 congelados), Magia (risa\n'
             'del mago + congelado), La Locura (el patrón v2.40 que nació ahí)\n'
             'y Valle Neón (puente), con conducta idéntica y cero cambios de\n'
             'gameplay.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v361', 'release-v362').replace('staging-v361', 'staging-v362')
s = s.replace('3.6.1-SDK1', '3.6.2-SDK2').replace('v361-sdk1', 'v362-sdk2')
# (tras el reemplazo anterior ya no quedan «3.6.1-SDK1»; los «3.6.1» sueltos:)
s = s.replace('3.6.1', '3.6.2').replace('n361', 'n362')
# identidad: hub (v362 presente, sin v361 ni anteriores)
s = s.replace(
    "if 'v362-sdk2' not in hub or 'v360-sup1' in hub or",
    "if 'v362-sdk2' not in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or")
# identidad del SDK v1.1.0: versión + precarga + opts.pan
s = s.replace(
    "for tk in (\"const SDK_VERSION = '1.0.0'\"",
    "for tk in (\"const SDK_VERSION = '1.1.0'\"")
s = s.replace(
    "           'forma promesa (v2.125)', 'window.__PP_SDK = SDK_VERSION'):",
    "           'forma promesa (v2.125)', 'function precarga',\n"
    "           'opts && opts.pan', 'window.__PP_SDK = SDK_VERSION'):")
# NUEVO — adopción SDK2: los 4 campeonatos (manifest + tokens + sin freeze duplicado)
BLOQUE = '''# — FASE 4 (SDK2): los 4 campeonatos adoptantes ——————————————
ADOPCION = {
    'oeste': (49, ("import { createSfx, congela, getCore } from '../sdk/champ_sdk.js'",
                   '__sfxSDK', "precarga('risas_forajido.mp3')",
                   "eng.play('risas.mp3', vol || 0.8, { pan: 0.4 })",
                   'congela(g, DUELO_P.drawT + DUELO_P.window + 0.35)',
                   'congela(g, 0.10)',
                   'congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1)',
                   'const __CORE = getCore() || {}')),
    'magia': (29, ("import { createSfx, congela, getCore } from '../sdk/champ_sdk.js'",
                   '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                   'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                   'const __CORE = getCore() || {}')),
    'locura': (21, ("import { congela, getCore } from '../sdk/champ_sdk.js'",
                    'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                    'const __CORE = getCore() || {}')),
    'valle_neon': (2, ("import { getCore } from '../sdk/champ_sdk.js'",
                       'const CORE = getCore();')),
}
for mod, (vman, tokens) in ADOPCION.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (adopción SDK2)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
    if 'freezeT = Math.max' in srcm:
        sys.exit(f'FALLO: {mod} conserva un freeze duplicado (debe vivir en el SDK)')
print('· Adopción SDK2 verificada: oeste v49 · magia v29 · locura v21 · valle_neon v2')
'''
s = s.replace(
    "if 'position.set(1.62, RIV_H / 2' in eo:",
    BLOQUE + "if 'position.set(1.62, RIV_H / 2' in eo:")
# hashes de VERSION.txt: los 4 index.js adoptantes entran en la ficha
s = s.replace(
    "    'championships/sdk/champ_sdk.js':\n"
    "        sha256(STAGE / 'championships/sdk/champ_sdk.js'),",
    "    'championships/sdk/champ_sdk.js':\n"
    "        sha256(STAGE / 'championships/sdk/champ_sdk.js'),\n"
    "    'championships/oeste/index.js':\n"
    "        sha256(STAGE / 'championships/oeste/index.js'),\n"
    "    'championships/magia/index.js':\n"
    "        sha256(STAGE / 'championships/magia/index.js'),\n"
    "    'championships/locura/index.js':\n"
    "        sha256(STAGE / 'championships/locura/index.js'),\n"
    "    'championships/valle_neon/index.js':\n"
    "        sha256(STAGE / 'championships/valle_neon/index.js'),")
# VERSION.txt: base y rama
s = s.replace(
    "    'Base    : V3.6.0-SUP1 + ",
    "    'Base    : V3.6.1-SDK1 + V3.6.0-SUP1 + ")
s = s.replace(
    "'Rama    : main · SDK1 (SDK de campeonatos — kernel compartido de los 5)\\n\\n'",
    "'Rama    : main · SDK2 (FASE 4 — el SDK adoptado por los 5 campeonatos)\\n\\n'")
# VERSION.txt: novedades de la SDK2 (bloque completo)
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.6.1-SDK1):\\n'\n"
    "    '  · FASE 4 de la modularización P0: el SDK DE CAMPEONATOS\\n'\n"
    "    '    (champ_sdk.js v1.1.0) ya lo usan LOS 5 campeonatos. La\\n'\n"
    "    '    Estación Orbital estrenó la adopción en SDK1; ahora se suman:\\n'\n"
    "    '    · OESTE (manifest v49): sus 4 motores SFX one-shot (risa del\\n'\n"
    "    '      forajido, risa del pueblo, jingle de oleada y risas del robo\\n'\n"
    "    '      del vagón) y sus 3 congelados (duelo de revólver ×2 y aviso\\n'\n"
    "    '      de superpoder) delegan en el SDK; volúmenes, anti-spam de\\n'\n"
    "    '      3,2 s y paneo 0,4 intactos. La BSO del saloon y la música\\n'\n"
    "    '      del vagón conservan su motor propio (fundido, resurrección\\n'\n"
    "    '      de contexto y sincronía con el núcleo).\\n'\n"
    "    '    · MAGIA (v29): la risa del mago y el congelado del aviso.\\n'\n"
    "    '    · LA LOCURA (v21): el congelado del aviso — el patrón v2.40\\n'\n"
    "    '      que NACIÓ en este módulo — y el puente al núcleo.\\n'\n"
    "    '    · VALLE NEÓN (v2): el puente al núcleo.\\n'\n"
    "    '  · SDK v1.1.0: precarga() (calentar la cache sin sonar) y\\n'\n"
    "    '    opts.pan (paneo estéreo opcional). Un bug del kernel se\\n'\n"
    "    '    arregla UNA vez y sirven los 5 campeonatos.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta, los\\n'\n"
    "    '    superpoderes, el reactor, el escudo y los duelos se comportan\\n'\n"
    "    '    exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
# identidad imprimida y cierre
s = s.replace('+ hub v362-sdk2 + SDK de campeonatos (orbital adoptante)\')',
              '+ hub v362-sdk2 + SDK de campeonatos (adopción en los 4)\')')
s = s.replace(
    'V3.6.2-SDK2 lista: SDK DE CAMPEONATOS (kernel único de los 5) + superpoderes redefinidos + voz del ASTRO + diana 2 s.',
    'V3.6.2-SDK2 lista: SDK en LOS 5 CAMPEONATOS (FASE 4) + superpoderes redefinidos + voz del ASTRO + diana 2 s.')
# nota cloudflare: contenido con la FASE 4
s = s.replace(
    "'FASE 3 — kernel único de los 5 campeonatos — y los SUPERPODERES\\n'",
    "'FASE 4 — adoptado por los 5 campeonatos — y los SUPERPODERES\\n'")
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# 4) anclajes de identidad del build_zip generado
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.2-SDK2'" in t),
    ("'V3.6.2-SDK2'" in t),
    ("if 'v362-sdk2' not in hub or 'v361-sdk1' in hub" in t),
    ("man.get('version') != 14" in t),
    ("no es el v3.6.2 (ASTRO, manifest v14)" in t),
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
    ("const SDK_VERSION = '1.1.0'" in t),
    ("'function precarga'" in t),
    ("'opts && opts.pan'" in t),
    ('Adopción SDK2 verificada' in t),
    ("no es v{vman} (adopción SDK2)" in t),
    ("'freezeT = Math.max' in srcm" in t),
    ("window.__PP_SDK = SDK_VERSION" in t),
    ('Novedades de esta versión (frente a V3.6.1-SDK1)' in t),
    ('Rama    : main · SDK2' in t),
    ('grep -c "3.6.2"' in t),
    ('menciones 3.6.2' in t),
    ('crazypp-v362-sdk2-COMPLETO.zip' in t),
    ('crazypp-v362-sdk2-CLOUDFLARE.zip' in t),
    ('crazypp-v362-sdk2-ligera.zip' in t),
    ('SDK en LOS 5 CAMPEONATOS (FASE 4)' in t),
    ('el SDK compartido' in t),
    ('championships/oeste/index.js' in t),
    ('championships/valle_neon/index.js' in t),
    ('staging-v361' not in t),
    ('release-v361' not in t),
    # las únicas menciones permitidas de la versión ANTERIOR: la línea Base,
    # el encabezado «frente a» y el hub prohibido (1)
    (t.count('3.6.1-SDK1') == 2),
    (t.count('v361-sdk1') == 1),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print(f'· anclajes de identidad: OK ({len(checks)}/{len(checks)})')

# 5) LEEME/CHULETA anclados
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DST / name).read_text(encoding='utf-8')
    assert 'V3.6.2-SDK2' in s and 'champ_sdk' in s, name
    assert 'v361-sdk1' not in s, name
print('· LEEME/CHULETA anclados: OK')

print('\nrelease-v362/ listo: python3 scripts/release-v362/build_zip.py')

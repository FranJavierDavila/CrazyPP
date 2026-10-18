#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera scripts/release-v363/ a partir de release-v362/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.3-SDK3 (FASE 5 de la modularización P0: createMusic — el
SDK champ_sdk.js v1.2.0 unifica la MÚSICA en bucle de oeste/magia/valle_neon).
Cada reemplazo se cuenta y se aserta: si el origen cambia, el derivador FALLA."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v362')
DST = Path('/home/z/my-project/scripts/release-v363')

def reemplazar(s, viejo, nuevo, esperado, etiqueta):
    n = s.count(viejo)
    assert n == esperado, f'{etiqueta}: {viejo!r} aparece {n} veces (esperado {esperado})'
    return s.replace(viejo, nuevo)

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
    s = s.replace('3.6.2-SDK2', '3.6.3-SDK3').replace('v362-sdk2', 'v363-sdk3')
    ancla = 'CRAZY PING PONG · V3.6.3-SDK3'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: la FASE 5 de la modularización —\n'
             'createMusic (champ_sdk.js v1.2.0): los TRES motores de MÚSICA\n'
             'en bucle que seguían duplicados (BSO del saloon v2.78+v2.124,\n'
             'música del vagón v2.111 y la WAV de Valle Neón) convergen en\n'
             'UNA sola máquina de estados en el SDK, con conducta idéntica\n'
             '(fundidos, sincronía con el ajuste global, UNA MELODÍA,\n'
             'resurrección de contexto v2.124) y cero cambios de gameplay.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v362', 'release-v363').replace('staging-v362', 'staging-v363')
s = s.replace('3.6.2-SDK2', '3.6.3-SDK3').replace('v362-sdk2', 'v363-sdk3')
# (tras el reemplazo anterior ya no quedan «3.6.2-SDK2»; los «3.6.2» sueltos:)
s = s.replace('3.6.2', '3.6.3').replace('n362', 'n363')
# identidad: hub (v363 presente, sin v362 ni anteriores)
s = reemplazar(
    s,
    "if 'v363-sdk3' not in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or",
    "if 'v363-sdk3' not in hub or 'v362-sdk2' in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or",
    1, 'identidad hub')
# identidad del SDK v1.2.0: versión + createMusic + gate UNA MELODÍA
s = reemplazar(s, 'for tk in ("const SDK_VERSION = \'1.1.0\'", \'export function createSfx\',',
               'for tk in ("const SDK_VERSION = \'1.2.0\'", \'export function createSfx\',',
               1, 'SDK versión')
s = reemplazar(
    s,
    "           'forma promesa (v2.125)', 'function precarga',\n"
    "           'opts && opts.pan', 'window.__PP_SDK = SDK_VERSION'):",
    "           'forma promesa (v2.125)', 'function precarga',\n"
    "           'opts && opts.pan', 'export function createMusic',\n"
    "           'o.gateStart !== false && arcPlaying()', 'window.__PP_SDK = SDK_VERSION'):",
    1, 'tokens SDK 1.2.0')
# FASE 4 (bloque heredado): los imports y manifests actuales de los 4 adoptantes
s = reemplazar(s, '"import { createSfx, congela, getCore } from \'../sdk/champ_sdk.js\'"',
               '"import { createSfx, createMusic, congela, getCore } from \'../sdk/champ_sdk.js\'"',
               2, 'imports FASE 4 (oeste+magia)')
s = reemplazar(s, '"import { getCore } from \'../sdk/champ_sdk.js\'"',
               '"import { createMusic, getCore } from \'../sdk/champ_sdk.js\'"',
               1, 'import FASE 4 (valle)')
s = reemplazar(s, "'oeste': (49,", "'oeste': (50,", 1, 'manifest oeste')
s = reemplazar(s, "'magia': (29,", "'magia': (30,", 1, 'manifest magia')
s = reemplazar(s, "'valle_neon': (2,", "'valle_neon': (3,", 1, 'manifest valle')
s = reemplazar(s, "(adopción SDK2)')", "(adopción SDK2/SDK3)')", 1, 'etiqueta FASE 4')
s = reemplazar(s, "print('· Adopción SDK2 verificada: oeste v49 · magia v29 · locura v21 · valle_neon v2')",
               "print('· Adopción SDK2/SDK3 verificada: oeste v50 · magia v30 · locura v21 · valle_neon v3')",
               1, 'print FASE 4')
# NUEVO — FASE 5 (SDK3): los 3 campeonatos que migran su MÚSICA
BLOQUE = '''# — FASE 5 (SDK3): la MÚSICA en bucle vive en el SDK ——————————
MUSICA = {
    'oeste': (50, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   "puede: () => this._stageMode !== 'tren'",
                   'get _musSDKv()', "syncMode: 'direct'",
                   'excluso: () => this.ctrl._musSDK.sonando()',
                   '_musicStart() { this._musSDKv.on(); }',
                   '_musicStop() { this._musSDKv.off(); }')),
    'magia': (30, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   '_syncMusicGain() {', 'this._musSDK.sync();')),
    'valle_neon': (3, ('get _musSDK()', 'fadeIn: 1.2', 'ancla: false',
                       "syncMode: 'none'", 'gateOn: true', 'stopFade: 0.4')),
}
for mod, (vman, tokens) in MUSICA.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (música SDK3)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
    if 'decodeAudioData(' in srcm:
        sys.exit(f'FALLO: {mod} conserva decodeAudioData propio (debe vivir en el SDK)')
print('· Música SDK3 verificada: oeste v50 (BSO+vagón) · magia v30 (BSO) · valle_neon v3 (WAV)')
'''
s = reemplazar(s, "if 'position.set(1.62, RIV_H / 2' in eo:",
               BLOQUE + "if 'position.set(1.62, RIV_H / 2' in eo:", 1, 'bloque FASE 5')
# VERSION.txt: base y rama
s = reemplazar(s, "    'Base    : V3.6.1-SDK1 + ",
               "    'Base    : V3.6.2-SDK2 + V3.6.1-SDK1 + ", 1, 'base VERSION.txt')
s = reemplazar(s, "'Rama    : main · SDK2 (FASE 4 — el SDK adoptado por los 5 campeonatos)\\n\\n'",
               "'Rama    : main · SDK3 (FASE 5 — createMusic unifica la música)\\n\\n'", 1, 'rama VERSION.txt')
# VERSION.txt: novedades de la SDK3 (bloque completo)
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.6.2-SDK2):\\n'\n"
    "    '  · FASE 5 de la modularización P0: createMusic (champ_sdk.js\\n'\n"
    "    '    v1.2.0) unifica la MÚSICA en bucle de los campeonatos. Los\\n'\n"
    "    '    tres motores que seguían duplicados convergen en UNA sola\\n'\n"
    "    '    máquina de estados del SDK, con variantes por opciones:\\n'\n"
    "    '    · OESTE (manifest v50): la BSO del saloon (motor v2.78 +\\n'\n"
    "    '      v2.124 — fundido 0,8 s, sincronía en vivo con el ajuste\\n'\n"
    "    '      global con rampa 0,15 s, UNA MELODÍA con arcPlaying,\\n'\n"
    "    '      resurrección de contexto) y la música del vagón (v2.111 —\\n'\n"
    "    '      sin fundido, sync directo, sin resurrección) delegan en el\\n'\n"
    "    '      SDK; la exclusividad BSO↔vagón (antes, la ranura _mus\\n'\n"
    "    '      compartida) se reproduce con opts.excluso.\\n'\n"
    "    '    · MAGIA (v30): la BSO del Wizard, knobs canónicos.\\n'\n"
    "    '    · VALLE NEÓN (v3): la música WAV con sus variantes propias —\\n'\n"
    "    '      volumen fijo del manifest, fundido de entrada 1,2 s sin\\n'\n"
    "    '      ancla, gate UNA MELODÍA también en musicOn, sin sync y\\n'\n"
    "    '      parada con fundido de 0,4 s (stop a 500 ms).\\n'\n"
    "    '  · El fix v2.125 (decodeAudioData en forma promesa) vive UNA\\n'\n"
    "    '    vez en el SDK también para la música: ninguna de las 5\\n'\n"
    "    '    módulos conserva ya decodeAudioData propio.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual;\\n'\n"
    "    '    la conducta de cada motor de música se conserva al detalle.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
# identidad imprimida y cierre
s = reemplazar(s, '+ hub v363-sdk3 + SDK de campeonatos (adopción en los 4)\')',
               '+ hub v363-sdk3 + SDK de campeonatos (música unificada)\')', 1, 'print identidad')
s = reemplazar(s,
               'V3.6.3-SDK3 lista: SDK en LOS 5 CAMPEONATOS (FASE 4) + superpoderes redefinidos + voz del ASTRO + diana 2 s.',
               'V3.6.3-SDK3 lista: MÚSICA UNIFICADA en createMusic (FASE 5) + SDK en los 5 + superpoderes redefinidos + voz del ASTRO.',
               1, 'print cierre')
# nota cloudflare: contenido con la FASE 5
s = reemplazar(s, "'FASE 4 — adoptado por los 5 campeonatos — y los SUPERPODERES\\n'",
               "'FASE 5 — la música unificada en createMusic — y los SUPERPODERES\\n'", 1, 'nota cloudflare')
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# 4) anclajes de identidad del build_zip generado
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.3-SDK3'" in t),
    ("'V3.6.3-SDK3'" in t),
    ("if 'v363-sdk3' not in hub or 'v362-sdk2' in hub" in t),
    ("man.get('version') != 14" in t),
    ("no es el v3.6.3 (ASTRO, manifest v14)" in t),
    ("'function _geoMeteorito'" in t),
    ("'dronTractor', '_tractorTrap', 'caída vertical pura'" in t),
    ("'this._sfx(\\'risa_astro.mp3\\')'" in t),
    ("'dianaVis: 2.0'" in t),
    ("'this._restT > 0.6'" in t),
    ("\"congela(this.game, (def.warn || 2.0) + 0.15)\"" in t),
    ("\"from '../sdk/champ_sdk.js'\"" in t),
    ("'createSfx(import.meta.url'" in t),
    ("'__sfxSDK'" in t),
    ("championships/sdk/champ_sdk.js" in t),
    ("const SDK_VERSION = '1.2.0'" in t),
    ("'function precarga'" in t),
    ("'opts && opts.pan'" in t),
    ("'export function createMusic'" in t),
    ("'o.gateStart !== false && arcPlaying()'" in t),
    ('Adopción SDK2/SDK3 verificada' in t),
    ("no es v{vman} (adopción SDK2/SDK3)" in t),
    ("'freezeT = Math.max' in srcm" in t),
    ('Música SDK3 verificada' in t),
    ("'decodeAudioData(' in srcm" in t),
    ("no es v{vman} (música SDK3)" in t),
    ("'excluso: () => this.ctrl._musSDK.sonando()'" in t),
    ("'_musicStart() { this._musSDKv.on(); }'" in t),
    ("'stopFade: 0.4'" in t),
    ('window.__PP_SDK = SDK_VERSION' in t),
    ('Novedades de esta versión (frente a V3.6.2-SDK2)' in t),
    ('Rama    : main · SDK3' in t),
    ('grep -c "3.6.3"' in t),
    ('menciones 3.6.3' in t),
    ('crazypp-v363-sdk3-COMPLETO.zip' in t),
    ('crazypp-v363-sdk3-CLOUDFLARE.zip' in t),
    ('crazypp-v363-sdk3-ligera.zip' in t),
    ('MÚSICA UNIFICADA en createMusic (FASE 5)' in t),
    ('el SDK compartido' in t),
    ('championships/oeste/index.js' in t),
    ('championships/valle_neon/index.js' in t),
    ('staging-v362' not in t),
    ('release-v362' not in t),
    # las únicas menciones permitidas de la versión ANTERIOR: la línea Base,
    # el hub prohibido y el «frente a» (2 de 3.6.2-SDK2)
    (t.count('3.6.2-SDK2') == 2),
    (t.count('v362-sdk2') == 1),
    (t.count('3.6.1-SDK1') == 1),
    ('1.1.0' not in t),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print(f'· anclajes de identidad: OK ({len(checks)}/{len(checks)})')

# 5) LEEME/CHULETA anclados
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DST / name).read_text(encoding='utf-8')
    assert 'V3.6.3-SDK3' in s and 'createMusic' in s, name
    assert 'v362-sdk2' not in s, name
print('· LEEME/CHULETA anclados: OK')

print('\nrelease-v363/ listo: python3 scripts/release-v363/build_zip.py')

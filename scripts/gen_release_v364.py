#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera scripts/release-v364/ a partir de release-v363/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.4-SDK4 (FASE 6: createPowerSign — el cartel de SUPERPODER de
los 4 campeonatos con duelos unificado en champ_sdk.js v1.3.0)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v363')
DST = Path('/home/z/my-project/scripts/release-v364')

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
    s = s.replace('3.6.3-SDK3', '3.6.4-SDK4').replace('v363-sdk3', 'v364-sdk4')
    ancla = 'CRAZY PING PONG · V3.6.4-SDK4'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: la FASE 6 de la modularización —\n'
             'createPowerSign (champ_sdk.js v1.3.0): el tablón «¡Super Power!!»\n'
             'de los 4 campeonatos con duelos (Oeste, Magia, La Locura y Estación\n'
             'Orbital) vive en UNA sola fábrica del SDK, con sus DOS coreografías\n'
             'exactas («clasica» v2.120 y «v240» con el halo que respira) y cero\n'
             'cambios de gameplay.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v363', 'release-v364').replace('staging-v363', 'staging-v364')
s = s.replace('3.6.3-SDK3', '3.6.4-SDK4').replace('v363-sdk3', 'v364-sdk4')
s = s.replace('3.6.3', '3.6.4').replace('n363', 'n364')
s = reemplazar(
    s,
    "if 'v364-sdk4' not in hub or 'v362-sdk2' in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or",
    "if 'v364-sdk4' not in hub or 'v363-sdk3' in hub or 'v362-sdk2' in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or",
    1, 'identidad hub')
s = reemplazar(s, 'for tk in ("const SDK_VERSION = \'1.2.0\'", \'export function createSfx\',',
               'for tk in ("const SDK_VERSION = \'1.3.0\'", \'export function createSfx\',',
               1, 'SDK versión')
s = reemplazar(
    s,
    "           'opts && opts.pan', 'export function createMusic',\n"
    "           'o.gateStart !== false && arcPlaying()', 'window.__PP_SDK = SDK_VERSION'):",
    "           'opts && opts.pan', 'export function createMusic',\n"
    "           'o.gateStart !== false && arcPlaying()', 'export function createPowerSign',\n"
    "           'V240 = o.coreo', 'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22',\n"
    "           'window.__PP_SDK = SDK_VERSION'):",
    1, 'tokens SDK 1.3.0')
# orbital: manifest ahora v15
s = reemplazar(s, "if man.get('version') != 14 or man['rival']['name'] != 'ASTRO':",
               "if man.get('version') != 15 or man['rival']['name'] != 'ASTRO':", 1, 'manifest orbital')
s = reemplazar(s, "(ASTRO, manifest v14)", "(ASTRO, manifest v15)", 1, 'etiqueta orbital v15')
# FASE 5 música: manifests actuales de los 3 migrados
s = reemplazar(s, "'oeste': (50, ('get _musSDK()'", "'oeste': (51, ('get _musSDK()'", 1, 'FASE5 oeste v51')
s = reemplazar(s, "'magia': (30, ('get _musSDK()'", "'magia': (31, ('get _musSDK()'", 1, 'FASE5 magia v31')
s = reemplazar(s, "print('· Música SDK3 verificada: oeste v50 (BSO+vagón) · magia v30 (BSO) · valle_neon v3 (WAV)')",
               "print('· Música SDK3/SDK4 verificada: oeste v51 (BSO+vagón) · magia v31 (BSO) · valle_neon v3 (WAV)')",
               1, 'print FASE 5')
# FASE 4 adopción: manifests actuales
s = reemplazar(s, '"import { createSfx, createMusic, congela, getCore } from \'../sdk/champ_sdk.js\'"',
               '"import { createSfx, createMusic, createPowerSign, congela, getCore } from \'../sdk/champ_sdk.js\'"',
               2, 'imports FASE 4 (oeste+magia)')
s = reemplazar(s, '"import { congela, getCore } from \'../sdk/champ_sdk.js\'"',
               '"import { createPowerSign, congela, getCore } from \'../sdk/champ_sdk.js\'"',
               1, 'import FASE 4 (locura)')
s = reemplazar(s, "'oeste': (50,", "'oeste': (51,", 1, 'FASE4 oeste v51')
s = reemplazar(s, "'magia': (30,", "'magia': (31,", 1, 'FASE4 magia v31')
s = reemplazar(s, "'locura': (21,", "'locura': (22,", 1, 'FASE4 locura v22')
s = reemplazar(s, "(adopción SDK2/SDK3)')", "(adopción SDK2/SDK3/SDK4)')", 1, 'etiqueta FASE 4')
s = reemplazar(s, "print('· Adopción SDK2/SDK3 verificada: oeste v50 · magia v30 · locura v21 · valle_neon v3')",
               "print('· Adopción SDK2/SDK3/SDK4 verificada: oeste v51 · magia v31 · locura v22 · valle_neon v3')",
               1, 'print FASE 4')
# NUEVO — FASE 6 (SDK4): el cartel de SUPERPODER en el SDK
BLOQUE = '''# — FASE 6 (SDK4): el CARTEL DE SUPERPODER vive en el SDK ——————
POWERSIGN = {
    'oeste': (51, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'plano'",
                   'pintar: (aplicar) => this._pintarRespaldo(aplicar)',
                   'oesteCanvas(1024, 560)')),
    'magia': (31, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'canvas1024'",
                   'fallbackURL: () => paintPowerBanner()')),
    'locura': (22, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                    "arte: 'fit1833'")),
    'estacion_orbital': (15, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                              'onTex: (tex) => { try { this.ctrl._ownTex.add(tex); }')),
}
for mod, (vman, tokens) in POWERSIGN.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (PowerSign SDK4)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
print('· PowerSign SDK4 verificada: oeste v51 · magia v31 · locura v22 · orbital v15 (tablón en el SDK)')
'''
s = reemplazar(s, "if 'position.set(1.62, RIV_H / 2' in eo:",
               BLOQUE + "if 'position.set(1.62, RIV_H / 2' in eo:", 1, 'bloque FASE 6')
# VERSION.txt: base, rama y novedades
s = reemplazar(s, "    'Base    : V3.6.2-SDK2 + ", "    'Base    : V3.6.3-SDK3 + V3.6.2-SDK2 + ", 1, 'base VERSION.txt')
s = reemplazar(s, "'Rama    : main · SDK3 (FASE 5 — createMusic unifica la música)\\n\\n'",
               "'Rama    : main · SDK4 (FASE 6 — createPowerSign unifica el cartel de superpoder)\\n\\n'", 1, 'rama VERSION.txt')
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.6.3-SDK3):\\n'\n"
    "    '  · FASE 6 de la modularización P0: createPowerSign (champ_sdk.js\\n'\n"
    "    '    v1.3.0) unifica el CARTEL DE SUPERPODER. Los 4 campeonatos con\\n'\n"
    "    '    duelos delegan en UNA fábrica del SDK con dos coreografías\\n'\n"
    "    '    exactas:\\n'\n"
    "    '    · OESTE (v51) y MAGIA (v31): la «clasica» v2.120 — entrada por\\n'\n"
    "    '      la izquierda (1,4 m, rot 0,22), vaivén y salida 1,5·e² con\\n'\n"
    "    '      rot −0,24; el Oeste conserva su respaldo pintado (tablón\\n'\n"
    "    '      quemado con estrella del sheriff) y Magia su arte por canvas\\n'\n"
    "    '      1024 con respaldo a paintPowerBanner.\\n'\n"
    "    '    · LA LOCURA (v22) y la ESTACIÓN ORBITAL (v15): la «v240» —\\n'\n"
    "    '      entrada con escala 0,92→1, vaivén y HALO DE CONTORNO que\\n'\n"
    "    '      respira; el orbital conserva el registro de texturas propias\\n'\n"
    "    '      (_ownTex) y el dispose de la regla Quest pasa a los cuatro.\\n'\n"
    "    '  · El anclado a la red (v2.88) y el icono circular del poder\\n'\n"
    "    '    anunciado (v2.120) son COMUNES: un bug del tablón se arregla\\n'\n"
    "    '    UNA vez y sirven los 4.\\n'\n"
    "    '  · La FASE 5 (createMusic) sigue intacta: ningún módulo conserva\\n'\n"
    "    '    decodeAudioData propio y la música suena exactamente igual.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
s = reemplazar(s, '+ hub v364-sdk4 + SDK de campeonatos (música unificada)\')',
               '+ hub v364-sdk4 + SDK de campeonatos (tablón y música en el SDK)\')', 1, 'print identidad')
s = reemplazar(s,
               'V3.6.4-SDK4 lista: MÚSICA UNIFICADA en createMusic (FASE 5) + SDK en los 5 + superpoderes redefinidos + voz del ASTRO.',
               'V3.6.4-SDK4 lista: TABLÓN DE SUPERPODER en createPowerSign (FASE 6) + música unificada + SDK en los 5.',
               1, 'print cierre')
s = reemplazar(s, "'FASE 5 — la música unificada en createMusic — y los SUPERPODERES\\n'",
               "'FASE 6 — el tablón de superpoder unificado — y los SUPERPODERES\\n'", 1, 'nota cloudflare')
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# 4) anclajes de identidad del build_zip generado
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.4-SDK4'" in t),
    ("'V3.6.4-SDK4'" in t),
    ("if 'v364-sdk4' not in hub or 'v363-sdk3' in hub" in t),
    ("man.get('version') != 15" in t),
    ("(ASTRO, manifest v15)" in t),
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
    ("const SDK_VERSION = '1.3.0'" in t),
    ("'function precarga'" in t),
    ("'opts && opts.pan'" in t),
    ("'export function createMusic'" in t),
    ("'export function createPowerSign'" in t),
    ("'V240 = o.coreo'" in t),
    ("'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22'" in t),
    ('Adopción SDK2/SDK3/SDK4 verificada' in t),
    ('Música SDK3/SDK4 verificada' in t),
    ('PowerSign SDK4 verificada' in t),
    ('(PowerSign SDK4)' in t),
    ("'oesteCanvas(1024, 560)'" in t),
    ("'fallbackURL: () => paintPowerBanner()'" in t),
    ("'onTex: (tex) => { try { this.ctrl._ownTex.add(tex); }'" in t),
    ('window.__PP_SDK = SDK_VERSION' in t),
    ('Novedades de esta versión (frente a V3.6.3-SDK3)' in t),
    ('Rama    : main · SDK4' in t),
    ('grep -c "3.6.4"' in t),
    ('menciones 3.6.4' in t),
    ('crazypp-v364-sdk4-COMPLETO.zip' in t),
    ('crazypp-v364-sdk4-CLOUDFLARE.zip' in t),
    ('crazypp-v364-sdk4-ligera.zip' in t),
    ('TABLÓN DE SUPERPODER en createPowerSign (FASE 6)' in t),
    ('el SDK compartido' in t),
    ('championships/estacion_orbital/index.js' in t),
    ('staging-v363' not in t),
    ('release-v363' not in t),
    (t.count('3.6.3-SDK3') == 2),
    (t.count('v363-sdk3') == 1),
    (t.count('3.6.2-SDK2') == 1),
    (t.count("'1.2.0'") == 0),
    (t.count("'1.1.0'") == 0),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print(f'· anclajes de identidad: OK ({len(checks)}/{len(checks)})')

# 5) LEEME/CHULETA anclados
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DST / name).read_text(encoding='utf-8')
    assert 'V3.6.4-SDK4' in s and 'createPowerSign' in s, name
    assert 'v363-sdk3' not in s, name
print('· LEEME/CHULETA anclados: OK')

print('\nrelease-v364/ listo: python3 scripts/release-v364/build_zip.py')

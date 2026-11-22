#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera scripts/release-v365/ a partir de release-v364/ (mismo patrón):
relay neutro + LEEME/CHULETA con versión nueva + build_zip con la identidad
dura de la V3.6.5-SDK5 (FASE 7 · CIERRE DEL SDK v1.x: createRival + createCartel
en champ_sdk.js v1.4.0, música del orbital al SDK — 0 decodeAudioData en los 5)."""
import shutil
from pathlib import Path

SRC = Path('/home/z/my-project/scripts/release-v364')
DST = Path('/home/z/my-project/scripts/release-v365')

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
    s = s.replace('3.6.4-SDK4', '3.6.5-SDK5').replace('v364-sdk4', 'v365-sdk5')
    ancla = 'CRAZY PING PONG · V3.6.5-SDK5'
    i = s.index(ancla)
    fin = s.index('\n', i)
    extra = ('\nNOVEDADES DE ESTA VERSIÓN: la FASE 7 CIERRA el SDK v1.x —\n'
             'createRival (el STANDEE del rival: ASTRO «perezoso» y ZETA-7\n'
             '«precarga», con FIX de arte real .png en Valle) y createCartel\n'
             '(los tableros de etapa) viven en champ_sdk.js v1.4.0, y la\n'
             'música del orbital (el ÚLTIMO decodeAudioData propio) pasa a\n'
             'createMusic: CERO decodeAudioData en los 5 campeonatos.\n')
    s = s[:fin] + extra + s[fin:]
    (DST / name).write_text(s, encoding='utf-8')
    print(f'· {name} adaptado')

# 3) build_zip.py
s = (SRC / 'build_zip.py').read_text(encoding='utf-8')
s = s.replace('release-v364', 'release-v365').replace('staging-v364', 'staging-v365')
s = s.replace('3.6.4-SDK4', '3.6.5-SDK5').replace('v364-sdk4', 'v365-sdk5')
s = reemplazar(s, '3.6.4', '3.6.5', 3, 'restos 3.6.4 (v3.6.4 + grep + print)')
# hub: la cadena de identidad crece (v364-sdk4 pasa al lado de los vetados)
s = reemplazar(
    s,
    "if 'v365-sdk5' not in hub or 'v363-sdk3' in hub or",
    "if 'v365-sdk5' not in hub or 'v364-sdk4' in hub or 'v363-sdk3' in hub or",
    1, 'identidad hub')
# SDK 1.4.0: versión + tokens nuevos
s = reemplazar(s, "for tk in (\"const SDK_VERSION = '1.3.0'\", 'export function createSfx',",
               "for tk in (\"const SDK_VERSION = '1.4.0'\", 'export function createSfx',",
               1, 'SDK versión for-loop')
s = reemplazar(
    s,
    "           'o.gateStart !== false && arcPlaying()', 'export function createPowerSign',\n"
    "           'V240 = o.coreo', 'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22',\n"
    "           'window.__PP_SDK = SDK_VERSION'):",
    "           'o.gateStart !== false && arcPlaying()', 'export function createPowerSign',\n"
    "           'V240 = o.coreo', 'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22',\n"
    "           'export function createRival', \"o.modo === 'precarga'\",\n"
    "           'export function createCartel',\n"
    "           'window.__PP_SDK = SDK_VERSION'):",
    1, 'tokens SDK 1.4.0')
# orbital: manifest ahora v16
s = reemplazar(s, "if man.get('version') != 15 or man['rival']['name'] != 'ASTRO':",
               "if man.get('version') != 16 or man['rival']['name'] != 'ASTRO':", 1, 'manifest orbital')
s = reemplazar(s, "(ASTRO, manifest v15)", "(ASTRO, manifest v16)", 1, 'etiqueta orbital v16')
# orbital: el standee ya no usa RIV_H/position.set — ahora delega en createRival
s = reemplazar(
    s,
    "           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',\n"
    "           '(D.tableCenterZ || -1.6) - 1.70',",
    "           'this._rivalSDK = createRival(THREE, () => this.game, {',\n"
    "           'pos: [1.26, 2.15 / 2, (D.tableCenterZ || -1.6) - 1.70],',\n"
    "           '(D.tableCenterZ || -1.6) - 1.70',",
    1, 'tokens standee orbital')
# FASE 4: valle import nuevo + manifest v4
s = reemplazar(
    s,
    "    'valle_neon': (3, (\"import { createMusic, getCore } from '../sdk/champ_sdk.js'\",",
    "    'valle_neon': (4, (\"import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js'\",",
    1, 'ADOPCION valle')
s = reemplazar(s, "'valle_neon': (3,", "'valle_neon': (4,", 1, 'MUSICA valle v4')
# FASE 5: el orbital se suma a la música del SDK (v16)
s = reemplazar(
    s,
    "                       \"syncMode: 'none'\", 'gateOn: true', 'stopFade: 0.4')),\n"
    "}\n"
    "for mod, (vman, tokens) in MUSICA.items():",
    "                       \"syncMode: 'none'\", 'gateOn: true', 'stopFade: 0.4')),\n"
    "    'estacion_orbital': (16, ('get _musSDK()', 'gateOn: true,',\n"
    "                             'vol: () => this._musicEffVol()',\n"
    "                             'musicOn() { this._musSDK.on(); }')),\n"
    "}\n"
    "for mod, (vman, tokens) in MUSICA.items():",
    1, 'MUSICA orbital v16')
# FASE 6: orbital sube a v16 (el mismo módulo migró todo a la vez)
s = reemplazar(s, "'estacion_orbital': (15, ('createPowerSign(THREE',",
               "'estacion_orbital': (16, ('createPowerSign(THREE',", 1, 'POWERSIGN orbital v16')
s = reemplazar(s, 'orbital v15 (tablón en el SDK)', 'orbital v16 (tablón en el SDK)', 1, 'print POWERSIGN')
s = reemplazar(s, 'PowerSign SDK4 verificada', 'PowerSign SDK5 verificada', 1, 'print POWERSIGN etiqueta')
s = reemplazar(s, "(PowerSign SDK4)')", "(PowerSign SDK5)')", 1, 'etiqueta FALLO POWERSIGN')
# NUEVO — FASE 7 (SDK5): STANDEE + TABLERO en el SDK y CERO decodeAudioData
BLOQUE = '''# — FASE 7 (SDK5): STANDEE + TABLERO en el SDK; CERO decodeAudioData —
RIVAL_CARTEL = {
    'estacion_orbital': (16, ('createRival(THREE', "modo: 'perezoso'",
                              "base: 'rival.webp'", 'createCartel(THREE',
                              'this._cartelSDK.pinta((c, W, H) => {',
                              'this._rivalSDK.rivalEstado(estado);')),
    'valle_neon': (4, ('createRival(THREE', "modo: 'precarga'",
                       "base: 'rival_kraken.png'", "ext: 'png'",
                       'createCartel(THREE', 'this._cartelSDK.pinta(',
                       'this._rivalSDK.rivalEstado(st);')),
}
for mod, (vman, tokens) in RIVAL_CARTEL.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (Rival/Cartel SDK5)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
for mod in ('oeste', 'magia', 'locura', 'estacion_orbital', 'valle_neon'):
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    if 'decodeAudioData(' in srcm:
        sys.exit(f'FALLO: {mod} conserva decodeAudioData propio (FASE 7: cero en los 5)')
print('· Rival/Cartel SDK5 verificada: orbital v16 (perezoso) · valle v4 (precarga) — 0 decodeAudioData en los 5')
'''
s = reemplazar(s, "if 'position.set(1.62, RIV_H / 2' in eo:",
               BLOQUE + "if 'position.set(1.62, RIV_H / 2' in eo:", 1, 'bloque FASE 7')
# prints de los bloques heredados
s = reemplazar(s, "print('· Adopción SDK2/SDK3/SDK4 verificada: oeste v51 · magia v31 · locura v22 · valle_neon v3')",
               "print('· Adopción SDK2/SDK3/SDK4/SDK5 verificada: oeste v51 · magia v31 · locura v22 · valle_neon v4')",
               1, 'print FASE 4')
s = reemplazar(s, "print('· Música SDK3/SDK4 verificada: oeste v51 (BSO+vagón) · magia v31 (BSO) · valle_neon v3 (WAV)')",
               "print('· Música SDK3/4/5 verificada: oeste v51 (BSO+vagón) · magia v31 (BSO) · valle_neon v4 (WAV) · orbital v16 (bso.wav)')",
               1, 'print FASE 5')
# VERSION.txt: base, rama y novedades
s = reemplazar(s, "    'Base    : V3.6.3-SDK3 + ", "    'Base    : V3.6.4-SDK4 + V3.6.3-SDK3 + ", 1, 'base VERSION.txt')
s = reemplazar(s, "'Rama    : main · SDK4 (FASE 6 — createPowerSign unifica el cartel de superpoder)\\n\\n'",
               "'Rama    : main · SDK5 (FASE 7 — CIERRE DEL SDK v1.x: rival, tablero y música orbital)\\n\\n'", 1, 'rama VERSION.txt')
i0 = s.index("    'Novedades de esta versión (frente a")
i1 = s.index("    'Hashes SHA256 (verificación de integridad):")
nuevo = (
    "    'Novedades de esta versión (frente a V3.6.4-SDK4):\\n'\n"
    "    '  · FASE 7 de la modularización P0 — CIERRE DEL SDK v1.x\\n'\n"
    "    '    (champ_sdk.js v1.4.0). Tres convergencias más:\\n'\n"
    "    '    · createRival: el STANDEE del rival vive en el SDK con DOS\\n'\n"
    "    '      motores exactos — el «perezoso» del ASTRO orbital (UNA\\n'\n"
    "    '      textura viva + guard anti-recarga v3.2.1) y el «precarga»\\n'\n"
    "    '      de ZETA-7 (Valle Neón: swap de mapas + escala por aspecto).\\n'\n"
    "    '    · createCartel: la fontanería del tablero de etapa (canvas →\\n'\n"
    "    '      textura → plano → needsUpdate) vive en el SDK; el ARTE sigue\\n'\n"
    "    '      siendo de cada módulo (_pintaCartel pinta en el lienzo).\\n'\n"
    "    '    · La MÚSICA del orbital (su ÚLTIMO decodeAudioData propio, la\\n'\n"
    "    '      bso.wav del «arsenal») pasa a createMusic con los knobs\\n'\n"
    "    '      canónicos de la BSO: CERO decodeAudioData en los 5 módulos.\\n'\n"
    "    '  · FIX que la migración destapa: el standee de Valle Neón pedía\\n'\n"
    "    '    «rival.webp / <estado>.webp» que NUNCA existieron (los assets\\n'\n"
    "    '    reales son .png) — llevaba pintada la silueta gris de reserva\\n'\n"
    "    '    desde su v1. Ahora carga el arte ZETA-7 real (rival_kraken.png\\n'\n"
    "    '    + estados .png).\\n'\n"
    "    '  · Las FASES 4-6 siguen intactas: SFX/congelados/puente (SDK2),\\n'\n"
    "    '    música (SDK3) y tablón de superpoder (SDK4) en sus fuentes\\n'\n"
    "    '    únicas. Un bug del kernel se arregla UNA vez y sirven los 5.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n")
s = s[:i0] + nuevo + s[i1:]
s = reemplazar(s, '+ hub v365-sdk5 + SDK de campeonatos (tablón y música en el SDK)\')',
               '+ hub v365-sdk5 + SDK de campeonatos (rival, tablón, tablero y música en el SDK)\')', 1, 'print identidad')
s = reemplazar(s,
               'V3.6.5-SDK5 lista: TABLÓN DE SUPERPODER en createPowerSign (FASE 6) + música unificada + SDK en los 5.',
               'V3.6.5-SDK5 lista: CIERRE DEL SDK v1.x — createRival + createCartel + música orbital (FASE 7) + tablón + música.',
               1, 'print cierre')
s = reemplazar(s, "'FASE 6 — el tablón de superpoder unificado — y los SUPERPODERES\\n'",
               "'FASE 7 — el SDK v1.x cerrado: rival, tablero, música — y los SUPERPODERES\\n'", 1, 'nota cloudflare')
# verificación de extras: el hub empaquetado ya dice 3.6.5 (los 3 restos
# '3.6.4' — v3.6.4 del manifest, grep -c y print de menciones — los llevó el
# reemplazo global de arriba); solo queda renombrar n364
s = reemplazar(s, 'n364', 'n365', 3, 'n364 → n365')
(DST / 'build_zip.py').write_text(s, encoding='utf-8')
print('· build_zip.py adaptado')

# 4) anclajes de identidad del build_zip generado
t = (DST / 'build_zip.py').read_text(encoding='utf-8')
checks = [
    ("const VERSION = '3.6.5-SDK5'" in t),
    ("'V3.6.5-SDK5'" in t),
    ("if 'v365-sdk5' not in hub or 'v364-sdk4' in hub" in t),
    ("man.get('version') != 16" in t),
    ("(ASTRO, manifest v16)" in t),
    ("'RIV_H = 2.15'" not in t),
    ("'position.set(1.26, RIV_H / 2'" not in t),
    ("'this._rivalSDK = createRival(THREE, () => this.game, {'" in t),
    ("'pos: [1.26, 2.15 / 2, (D.tableCenterZ || -1.6) - 1.70],'" in t),
    ("'(D.tableCenterZ || -1.6) - 1.70'" in t),
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
    ("const SDK_VERSION = '1.4.0'" in t),
    ("'function precarga'" in t),
    ("'opts && opts.pan'" in t),
    ("'export function createMusic'" in t),
    ("'export function createPowerSign'" in t),
    ("'V240 = o.coreo'" in t),
    ("'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22'" in t),
    ("'export function createRival'" in t),
    ("\"o.modo === 'precarga'\"" in t),
    ("'export function createCartel'" in t),
    ("import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js'" in t),
    ("'estacion_orbital': (16, ('get _musSDK()'" in t),
    ("'valle_neon': (4, ('get _musSDK()'" in t),
    ("'estacion_orbital': (16, ('createPowerSign(THREE'" in t),
    ('RIVAL_CARTEL' in t),
    ("\"modo: 'perezoso'\"" in t),
    ("base: 'rival_kraken.png'" in t),
    ('cero en los 5' in t),
    ('Adopción SDK2/SDK3/SDK4/SDK5 verificada' in t),
    ('Música SDK3/4/5 verificada' in t),
    ('PowerSign SDK5 verificada' in t),
    ('Rival/Cartel SDK5 verificada' in t),
    ('(PowerSign SDK5)' in t),
    ("'oesteCanvas(1024, 560)'" in t),
    ("'fallbackURL: () => paintPowerBanner()'" in t),
    ("'onTex: (tex) => { try { this.ctrl._ownTex.add(tex); }'" in t),
    ('window.__PP_SDK = SDK_VERSION' in t),
    ('Novedades de esta versión (frente a V3.6.4-SDK4)' in t),
    ('Rama    : main · SDK5' in t),
    ('CIERRE DEL SDK v1.x' in t),
    ('silueta gris de reserva' in t),
    ('grep -c "3.6.5"' in t),
    ('menciones 3.6.5' in t),
    ('crazypp-v365-sdk5-COMPLETO.zip' in t),
    ('crazypp-v365-sdk5-CLOUDFLARE.zip' in t),
    ('crazypp-v365-sdk5-ligera.zip' in t),
    ('CIERRE DEL SDK v1.x — createRival + createCartel' in t),
    ('el SDK compartido' in t),
    ('championships/estacion_orbital/index.js' in t),
    ('staging-v364' not in t),
    ('release-v364' not in t),
    (t.count('3.6.4-SDK4') == 2),
    (t.count('v364-sdk4') == 1),
    (t.count('3.6.3-SDK3') == 1),
    (t.count("'1.3.0'") == 0),
    (t.count("'1.2.0'") == 0),
    (t.count("'1.1.0'") == 0),
]
assert all(checks), [i for i, c in enumerate(checks) if not c]
print(f'· anclajes de identidad: OK ({len(checks)}/{len(checks)})')

# 5) LEEME/CHULETA anclados
for name in ('LEEME-DESPLIEGUE.txt', 'CHULETA-DIRECTO.txt'):
    s = (DST / name).read_text(encoding='utf-8')
    assert 'V3.6.5-SDK5' in s and 'createRival' in s, name
    assert 'v364-sdk4' not in s, name
print('· LEEME/CHULETA anclados: OK')

print('\nrelease-v365/ listo: python3 scripts/release-v365/build_zip.py')

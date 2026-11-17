#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA del HUB /descargas · V3.6.102-SDK6 (r110 · hito M4 onboarding).

Re-anclaje honesto de la capa H (era qa_descargas_v367.py, anclada a la
r95/v3.6.87): el hub se verifica ESTÁTICO sobre src/app/descargas/page.tsx
(patrón qa_r109_v3699), los 4 ZIPs byte-exactos en disco, el CONTENIDO de
los ZIPs (juego 3.6.100 · PWA · SDK 1.6.0 · 5 campeonatos con manifests
vigentes · ligera sin championships) y una pasada EN VIVO ligera sirviendo
public/ en un puerto propio (juego + SDK + manifest PWA + orbital).

Uso: python3 scripts/qa_descargas_v36100.py
"""
import json
import os
import re
import sys
import zipfile
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8848
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


ZIPS = {
    'crazypp-v36102-sdk6-COMPLETO.zip': 152938081,
    'crazypp-v36102-sdk6-ligera.zip': 18776063,
    'crazypp-v36102-sdk6-CLOUDFLARE.zip': 152923915,
    'crazypp-live-service-SOLO.zip': 6221,
}

ADOPTANTES = (('oeste', 56), ('magia', 33), ('locura', 27), ('halloween', 3))
ORBITAL = ('estacion_orbital', 17)
CAMINO_ORB = ['duelo1', 'impulso', 'duelo2', 'escudo', 'final']

# ------------------------------------------------------------- estático ----
print('== HUB /descargas (page.tsx, patrón r109) ==')
hub = open(os.path.join(RAIZ, 'src/app/descargas/page.tsx'), encoding='utf-8').read()
chk(hub.count('v36102-sdk6') >= 3, f'enlaces v36102-sdk6 ({hub.count("v36102-sdk6")})')
chk(hub.count('3.6.102-SDK6') >= 5, f'menciones 3.6.102-SDK6 ({hub.count("3.6.102-SDK6")})')
chk('📲 Instalar en el casco (PWA' in hub, 'hub: guía PWA presente (r109 intacta)')
chk('crazypp-live-service-SOLO' in hub, 'hub: nombra el SOLO (live-service)')
for viejo in ('v3699-sdk6', '3.6.99-SDK6', 'v3687-sdk6'):
    chk(viejo not in hub, f'sin residuos de {viejo}')

# ------------------------------------------------------------- ZIPs --------
print('== ZIPs byte-exactos en disco (public/descargas) ==')
for n, esperado in ZIPS.items():
    p = os.path.join(PUB, 'descargas', n)
    t = os.path.getsize(p) if os.path.exists(p) else -1
    chk(t == esperado, f'{n} = {t:,} B (esperado {esperado:,})')

print('== CONTENIDO del COMPLETO ==')
zc = zipfile.ZipFile(os.path.join(PUB, 'descargas', 'crazypp-v36102-sdk6-COMPLETO.zip'))
nom = zc.namelist()
gh = zc.read('index.html').decode('utf-8', 'ignore')
chk("const VERSION = '3.6.102-SDK6'" in gh, 'COMPLETO: index.html = 3.6.102-SDK6 (VERSION)')
chk('>V3.6.102-SDK6</span>' in gh, 'COMPLETO: badge estático V3.6.102-SDK6')
chk('__PP_PADDLE_SWEEP' in gh, 'COMPLETO: puente CCD del núcleo')
chk("T('m4_hint'" in gh or 'm4_hint' in gh, 'COMPLETO: i18n m4_hint del onboarding viaja (r110)')
swz = zc.read('sw.js').decode('utf-8', 'ignore')
chk("const CACHE = 'crazypp-v3.6.102-SDK6'" in swz, 'COMPLETO: sw.js CACHE = crazypp-v3.6.102-SDK6 (4.º sello)')
for f in ('manifest.webmanifest', 'logo-192.png', 'logo-512.png', 'logo-maskable-512.png'):
    chk(f in nom, f'COMPLETO: PWA lleva {f}')
sdkz = zc.read('championships/sdk/champ_sdk.js').decode('utf-8')
chk("const SDK_VERSION = '1.6.0'" in sdkz, 'COMPLETO: SDK = 1.6.0')
for exp in ('export function createSfx', 'export function createBucle',
            'export function createMusic', 'export function createPowerSign',
            'export function createRival', 'export function createCartel',
            'function precarga'):
    chk(exp in sdkz, f'COMPLETO: SDK export {exp.split()[-1]}')
for mod, vman in ADOPTANTES + (ORBITAL,):
    dentro = f'championships/{mod}/index.js' in nom
    chk(dentro, f'COMPLETO: championships/{mod}/index.js')
    if dentro:
        srcm = zc.read(f'championships/{mod}/index.js').decode('utf-8', 'ignore')
        chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod} (ZIP): importa el SDK')
        chk('decodeAudioData(' not in srcm, f'{mod} (ZIP): 0 decodeAudioData propio')
    manz = json.loads(zc.read(f'championships/{mod}/manifest.json').decode('utf-8'))
    chk(manz.get('version') == vman, f'{mod} (ZIP): manifest v{vman}')
maneo = json.loads(zc.read('championships/estacion_orbital/manifest.json').decode('utf-8'))
chk([st['id'] for st in maneo['stages']] == CAMINO_ORB,
    'orbital (ZIP): camino duelo1·impulso·duelo2·escudo·final')

print('== CONTENIDO del CLOUDFLARE y de la ligera ==')
zf = zipfile.ZipFile(os.path.join(PUB, 'descargas', 'crazypp-v36102-sdk6-CLOUDFLARE.zip'))
nomf = zf.namelist()
chk('championships/sdk/champ_sdk.js' in nomf, 'CLOUDFLARE: incluye el SDK')
chk('manifest.webmanifest' in nomf and 'sw.js' in nomf, 'CLOUDFLARE: PWA a bordo')
chk("const VERSION = '3.6.102-SDK6'" in zf.read('index.html').decode('utf-8', 'ignore'),
    'CLOUDFLARE: index.html = 3.6.102-SDK6')
zl = zipfile.ZipFile(os.path.join(PUB, 'descargas', 'crazypp-v36102-sdk6-ligera.zip'))
con_champ = [n for n in zl.namelist() if n.startswith('championships/')
             and n != 'championships/' and 'PON-AQUI' not in n]
chk(not con_champ, f'ligera sin campeonatos (solo el marcador) {con_champ[:2]}')

# ------------------------------------------------------------- en vivo ----
print('== EN VIVO ligero (servidor propio) ==')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=PUB, **kw)

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

try:
    from urllib.request import urlopen
    ghl = urlopen(f'http://127.0.0.1:{PORT}/game.html', timeout=20).read().decode('utf-8', 'ignore')
    chk("const VERSION = '3.6.102-SDK6'" in ghl, 'vivo: game.html = 3.6.102-SDK6')
    sdkl = urlopen(f'http://127.0.0.1:{PORT}/championships/sdk/champ_sdk.js', timeout=20).read().decode('utf-8')
    chk("const SDK_VERSION = '1.6.0'" in sdkl, 'vivo: champ_sdk.js = 1.6.0')
    swl = urlopen(f'http://127.0.0.1:{PORT}/sw.js', timeout=20).read().decode('utf-8')
    chk("const CACHE = 'crazypp-v3.6.102-SDK6'" in swl, 'vivo: sw.js con el 4.º sello')
    man = json.loads(urlopen(f'http://127.0.0.1:{PORT}/manifest.webmanifest', timeout=20).read())
    chk(man.get('display') == 'fullscreen' and man.get('start_url', '').endswith('game.html'),
        'vivo: manifest PWA fullscreen + start_url game.html')
    manl = json.loads(urlopen(f'http://127.0.0.1:{PORT}/championships/estacion_orbital/manifest.json', timeout=20).read())
    chk(manl.get('version') == 17, 'vivo: orbital manifest v17')
    chk([st['id'] for st in manl['stages']] == CAMINO_ORB, 'vivo: orbital camino íntegro')
finally:
    srv.shutdown()

print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
sys.exit(1 if fails else 0)

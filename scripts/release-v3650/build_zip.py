#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.6.50-SDK6.
Construye cuatro ZIP listos para subir:
  · crazypp-v3650-sdk6-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                     campeonatos, ~110 MB)
  · crazypp-v3650-sdk6-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v3650-sdk6-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
                                     aceptado por la subida directa de
                                     Cloudflare Pages sin wrangler)
  · crazypp-live-service-SOLO.zip    (solo el relay, 6 KB, para GitHub → Railway)
Salida: /home/z/my-project/download/ y copia en /home/z/my-project/public/descargas/
"""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path('/home/z/my-project')
PUB = RAIZ / 'public'
SRC = RAIZ / 'scripts' / 'release-v369'
STAGE = RAIZ / 'scripts' / 'staging-v369'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.6.50-SDK6'
FECHA = date.today().isoformat()

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def run(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-3000:]); print(r.stderr[-3000:])
        sys.exit(f'FALLO: {cmd}')
    return r.stdout

# ── 0. Verificación dura de identidad de la versión ──────────────
game_src = (PUB / 'game.html').read_text(encoding='utf-8')
if "const VERSION = '3.6.50-SDK6'" not in game_src:
    sys.exit('FALLO: public/game.html no es la V3.6.50-SDK6 (VERSION distinta)')
if 'V3.6.50-SDK6' not in game_src:
    sys.exit('FALLO: el badge estático no es V3.6.50-SDK6')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
if 'v3650-sdk6' not in hub or 'v369-sdk5' in hub or 'v364-sdk4' in hub or 'v363-sdk3' in hub or 'v362-sdk2' in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:
    sys.exit('FALLO: el hub /descargas no apunta a los paquetes v3650-sdk6')
man = json.loads((PUB / 'championships/estacion_orbital/manifest.json').read_text(encoding='utf-8'))
if man.get('version') != 16 or man['rival']['name'] != 'ASTRO':
    sys.exit('FALLO: el manifest de estacion_orbital no es el v3.6.5 (ASTRO, manifest v16)')
if man['stages'][1]['id'] != 'impulso' or man['stages'][3]['id'] != 'escudo':
    sys.exit('FALLO: el camino del manifest no es impulso/escudo (orden v3.5.0)')
eo = (PUB / 'championships/estacion_orbital/index.js').read_text(encoding='utf-8')
for tk in ('class ReactorImpulso', 'const IMP_CFG', "id: 'impulso'",
           '_empezarImpulso', '_arrancarImpulso', '_oleadaArranca',
           '_dianaHit', '_pertAplica', '_cadenaDestruye',
           'nucleo_gravedad_lp.glb', 'class ReactorInestable',
           'class EOArkanoid', 'class PwSignEO',
           "if (et.id === 'impulso') { this._empezarImpulso(et); return; }",
           "if (et.id === 'escudo') { this._empezarEscudo(et); return; }",
           "if (this.escudo) this.escudo.stop();",
           'this._rivalSDK = createRival(THREE, () => this.game, {',
           'pos: [1.26, 2.15 / 2, (D.tableCenterZ || -1.6) - 1.70],',
           '(D.tableCenterZ || -1.6) - 1.70',
           'cubeS: 0.16, cubeHitR: 0.14', 'ballT: 0.80, ballH: 0.34',
           'atrSep: 0.19', 'static HUECOS', '_atractorSepara',
           'dianaMat', 'ShaderMaterial', 'uDissolve',
           'alphaTest: ventanal ? 0.35 : 0', 'warpSpeed',
           "imp.phase === 'play' || imp.phase === 'intro'",
           'function _geoMeteorito', '_rocasGeo = [_geoMeteorito(0)',
           'vertexColors: true, flatShading: true', 'emissive: 0xff6a22',
           'dronTractor', '_tractorTrap', 'caída vertical pura',
           'const ATT = 7.5', 'this._sfx(\'risa_astro.mp3\')',
           'this._sfx(\'enfado_astro.mp3\')', 'dianaVis: 2.0',
           'this._restT > 0.6', "congela(this.game, (def.warn || 2.0) + 0.15)",
           "from '../sdk/champ_sdk.js'", 'createSfx(import.meta.url',
           '__sdkSfx',
           'class EscudoCasco', 'const ESC_CFG', "id: 'escudo'",
           '_empezarEscudo', '_arrancarEscudo', 'escudo_pala/',
           'window.__PP_PADDLE_SWEEP', 'BARRERA DE CASCO', 'champDecorHidden',
           'x: 1197, y: 335, r: 115', 'TAPA_W = 240 / 1376',
           "get gunArmed() { return !!(CTRL && CTRL.gunArmed); }"):
    if tk not in eo:
        sys.exit(f'FALLO: el módulo orbital no contiene {tk!r}')
sdkf = PUB / 'championships/sdk/champ_sdk.js'
if not sdkf.exists():
    sys.exit('FALLO: falta championships/sdk/champ_sdk.js (SDK de campeonatos)')
sdk = sdkf.read_text(encoding='utf-8')
for tk in ("const SDK_VERSION = '1.5.4'", 'export function createBucle', 'export function createSfx',
           'export function congela', 'export function descongela',
           'export function getCore', 'export function assetURL',
           'forma promesa (v2.125)', 'function precarga',
           'opts && opts.pan', 'export function createMusic',
           'o.gateStart !== false && arcPlaying()', 'export function createPowerSign',
           'V240 = o.coreo', 'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22',
           'export function createRival', "o.modo === 'precarga'",
           'export function createCartel',
           'window.__PP_SDK = SDK_VERSION'):
    if tk not in sdk:
        sys.exit(f'FALLO: champ_sdk.js no contiene {tk!r}')
# — FASE 4 (SDK2): los 4 campeonatos adoptantes ——————————————
ADOPCION = {
    'oeste': (56, ("import { createSfx, createMusic, createBucle, createPowerSign, congela, getCore, assetURL } from '../sdk/champ_sdk.js'",
                   '__sfxSDK', "precarga('risas_forajido.mp3')",
                   "eng.play('risas.mp3', vol || 0.8, { pan: 0.4 })",
                   'congela(g, DUELO_P.drawT + DUELO_P.window + 0.35)',
                   'congela(g, 0.10)',
                   'congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1)',
                   'const __CORE = getCore() || {}')),
    'magia': (32, ("import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                   '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                   'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                   'const __CORE = getCore() || {}')),
    'locura': (27, ("import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                    'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                    'const __CORE = getCore() || {}')),
    'valle_neon': (4, ("import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js'",
                       'const CORE = getCore();')),
}
for mod, (vman, tokens) in ADOPCION.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (adopción SDK2/SDK3/SDK4)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
    if 'freezeT = Math.max' in srcm:
        sys.exit(f'FALLO: {mod} conserva un freeze duplicado (debe vivir en el SDK)')
print('· Adopción SDK2/SDK3/SDK4/SDK5 verificada: oeste v56 · magia v32 · locura v27 · valle_neon v4')
# — FASE 5 (SDK3): la MÚSICA en bucle vive en el SDK ——————————
MUSICA = {
    'oeste': (56, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   "puede: () => this._stageMode !== 'tren'",
                   'get _musSDKv()', "syncMode: 'direct'",
                   'excluso: () => this.ctrl._musSDK.sonando()',
                   '_musicStart() { this._musSDKv.on(); }',
                   '_musicStop() { this._musSDKv.off(); }')),
    'magia': (32, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   '_syncMusicGain() {', 'this._musSDK.sync();')),
    'valle_neon': (4, ('get _musSDK()', 'fadeIn: 1.2', 'ancla: false',
                       "syncMode: 'none'", 'gateOn: true', 'stopFade: 0.4')),
    'estacion_orbital': (16, ('get _musSDK()', 'gateOn: true,',
                             'vol: () => this._musicEffVol()',
                             'musicOn() { this._musSDK.on(); }')),
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
print('· Música SDK3/4/5 verificada: oeste v56 (BSO+vagón) · magia v32 (BSO) · valle_neon v4 (WAV) · orbital v16 (bso.wav)')
# — FASE 6 (SDK4): el CARTEL DE SUPERPODER vive en el SDK ——————
POWERSIGN = {
    'oeste': (56, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'plano'",
                   'pintar: (aplicar) => this._pintarRespaldo(aplicar)',
                   'oesteCanvas(1024, 560)')),
    'magia': (32, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'canvas1024'",
                   'fallbackURL: () => paintPowerBanner()')),
    'locura': (27, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                    "arte: 'fit1833'")),
    'estacion_orbital': (16, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                              'onTex: (tex) => { try { this.ctrl._ownTex.add(tex); }')),
}
for mod, (vman, tokens) in POWERSIGN.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (PowerSign SDK5)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
print('· PowerSign SDK5 verificada: oeste v56 · magia v32 · locura v27 · orbital v16 (tablón en el SDK)')
# — FASE 7 (SDK5): STANDEE + TABLERO en el SDK; CERO decodeAudioData —
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
if 'position.set(1.62, RIV_H / 2' in eo:
    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en la posición v3.2.1 (x 1,62 · z −4,5)')
if '(D.tableCenterZ || -1.6) - 2.22' in eo:
    sys.exit('FALLO: el módulo orbital aún coloca al ASTRO en el spot v3.4.1 (z −3,82)')
if "{ kind: 'prueba', id: 'muro2'" in eo or "id: 'muro1'" in eo:
    sys.exit("FALLO: el módulo aún enruta etapas como muros (muro1/muro2)")
for at in ('reactor_impulso/frente.jpg', 'reactor_impulso/fondo.jpg',
           'reactor_impulso/techo.jpg', 'reactor_impulso/suelo.jpg',
           'reactor_impulso/izquierda.png', 'reactor_impulso/derecha.png',
           'reactor_impulso/diana_quantica.png', 'reactor_impulso/base.png',
           'reactor_impulso/pantallainfo.png', 'nucleo_gravedad_lp.glb',
           'pistol.glb', 'mapa.png', 'superpower.png', 'angry.webp',
           'risa_astro.mp3', 'enfado_astro.mp3'):
    p = PUB / 'championships/estacion_orbital/assets' / at
    if not p.exists() or p.stat().st_size < 1000:
        sys.exit(f'FALLO: falta el asset orbital {at}')
if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:
    sys.exit('FALLO: diana_quantica.png no es byte-exacta (409.356 B)')
if (PUB / 'championships/estacion_orbital/assets/risa_astro.mp3').stat().st_size != 81408:
    sys.exit('FALLO: risa_astro.mp3 no es byte-exacto (81.408 B)')
if (PUB / 'championships/estacion_orbital/assets/enfado_astro.mp3').stat().st_size != 37616:
    sys.exit('FALLO: enfado_astro.mp3 no es byte-exacto (37.616 B)')
print('· Identidad verificada: game.html V3.6.50-SDK6 + hub v3650-sdk6 + SDK de campeonatos (rival, tablón, tablero y música en el SDK)')

# ── 1. Staging limpio ─────────────────────────────────────────────
if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True)

print('· Copiando web del juego (index/tv/assets/vendor)...')
shutil.copy2(PUB / 'game.html', STAGE / 'index.html')
shutil.copy2(PUB / 'tv.html', STAGE / 'tv.html')
shutil.copytree(PUB / 'assets', STAGE / 'assets')
shutil.copytree(PUB / 'championships', STAGE / 'championships')
(STAGE / 'vendor').mkdir()
shutil.copy2(PUB / 'vendor' / 'socket.io.min.js', STAGE / 'vendor' / 'socket.io.min.js')

intro = STAGE / 'assets' / 'intro.mp4'
if intro.stat().st_size != 5779719:
    sys.exit(f'FALLO: assets/intro.mp4 pesa {intro.stat().st_size} B (esperado 5.779.719 B)')
print(f'  intro oficial OK: {intro.stat().st_size} B, sha256={sha256(intro)[:16]}…')

print('· Copiando live-service portable...')
LS = STAGE / 'live-service'
(LS / 'tools').mkdir(parents=True)
shutil.copy2(SRC / 'server.mjs', LS / 'server.mjs')
shutil.copy2(SRC / 'package.json', LS / 'package.json')
shutil.copy2(SRC / 'LEEME-live-service.md', LS / 'LEEME.md')
shutil.copy2(SRC / 'mock_host.mjs', LS / 'tools' / 'mock_host.mjs')

print('· Copiando extras-nextjs (descargas + banner TV + proxy API)...')
EX = STAGE / 'extras-nextjs'
(EX / 'descargas').mkdir(parents=True)
(EX / 'api' / 'channels').mkdir(parents=True)
shutil.copy2(RAIZ / 'src/app/descargas/page.tsx', EX / 'descargas' / 'page.tsx')
shutil.copy2(RAIZ / 'src/app/descargas/TvLiveBanner.tsx', EX / 'descargas' / 'TvLiveBanner.tsx')
shutil.copy2(RAIZ / 'src/app/api/channels/route.ts', EX / 'api' / 'channels' / 'route.ts')
(EX / 'LEEME.txt').write_text(
    'EXTRAS NEXT.JS (opcionales, del entorno de pruebas del proyecto)\n'
    '================================================================\n\n'
    'Estos ficheros NO hacen falta para Netlify. Pertenecen a la app Next.js\n'
    'del entorno de desarrollo:\n\n'
    '  descargas/page.tsx        Centro de descargas (/descargas) con tarjetas.\n'
    '  descargas/TvLiveBanner.tsx  Banner "CRAZY TV" con punto rojo pulsante\n'
    '                            cuando hay canales en directo (poll /api/channels).\n'
    '  api/channels/route.ts     Proxy de respaldo hacia el relay :3004\n'
    '                            (cubre accesos que no pasan por el gateway).\n\n'
    'Si algún día montas la web con Next.js, copialos a src/app/ respetando\n'
    'las rutas y funcionarán tal cual.\n', encoding='utf-8')

print('· Copiando LEEME principal...')
shutil.copy2(SRC / 'LEEME-DESPLIEGUE.txt', STAGE / 'LEEME-DESPLIEGUE.txt')
shutil.copy2(SRC / 'CHULETA-DIRECTO.txt', STAGE / 'CHULETA-DIRECTO.txt')

# ── 2. VERSION.txt con hashes reales ─────────────────────────────
print('· Generando VERSION.txt...')
ficheros = {
    'index.html': sha256(STAGE / 'index.html'),
    'tv.html': sha256(STAGE / 'tv.html'),
    'assets/intro.mp4': sha256(intro),
    'live-service/server.mjs': sha256(LS / 'server.mjs'),
    'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png':
        sha256(STAGE / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png'),
    'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb':
        sha256(STAGE / 'championships/estacion_orbital/assets/nucleo_gravedad_lp.glb'),
    'championships/estacion_orbital/assets/risa_astro.mp3':
        sha256(STAGE / 'championships/estacion_orbital/assets/risa_astro.mp3'),
    'championships/estacion_orbital/assets/enfado_astro.mp3':
        sha256(STAGE / 'championships/estacion_orbital/assets/enfado_astro.mp3'),
    'championships/sdk/champ_sdk.js':
        sha256(STAGE / 'championships/sdk/champ_sdk.js'),
    'championships/oeste/index.js':
        sha256(STAGE / 'championships/oeste/index.js'),
    'championships/magia/index.js':
        sha256(STAGE / 'championships/magia/index.js'),
    'championships/locura/index.js':
        sha256(STAGE / 'championships/locura/index.js'),
    'championships/valle_neon/index.js':
        sha256(STAGE / 'championships/valle_neon/index.js'),
    'vendor/socket.io.min.js': sha256(STAGE / 'vendor' / 'socket.io.min.js'),
}
(STAGE / 'VERSION.txt').write_text(
    'CRAZY PING PONG · FICHA DE VERSIÓN\n'
    '==================================\n'
    f'Versión : {VER}\n'
    f'Fecha   : {FECHA}\n'
    'Base    : V3.6.4-SDK4 + V3.6.3-SDK3 + V3.6.2-SDK2 + V3.6.1-SDK1 + V3.6.0-SUP1 + V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\n'
    'Rama    : main · SDK6 (FASE 52 — EL CLON DOBLE Y LA VOZ QUE\n'
    'GUÍA — petición del dueño tras V3.6.50)\n\n'
    'Novedades de esta versión (frente a V3.6.49-SDK6):\n'
    '  · SÚPER CLONACIÓN (5.º poder de pala; spec literal del dueño):\n'
    '    «dura 10 segundos y crea 2 palas virtuales a una distancia de\n'
    '    50 centímetros». Material GHOST («medio transparente azulado»,\n'
    '    opacidad 0,42 con brillo propio). La pala clon de la DERECHA\n'
    '    atiende a bolas por la derecha y la IZQUIERDA por la izquierda,\n'
    '    SIEMPRE que el jugador no las devuelva (prioridad absoluta: el\n'
    '    clon calla donde la pala llega). Tasa de éxito del 90 % real —\n'
    '    UNA sola tirada por vuelo, sin re-tiradas encubiertas. La\n'
    '    devolución es un golpe de JUGADOR legal (árbitro, contador y\n'
    '    emociones del rival intactos) con el SOLVER DE LA CASA hacia la\n'
    '    mesa rival y cero spin (bote seguro). La ventana vive SUS 10 s\n'
    '    (reloj único; la caza NO gasta cargas; refresh honesto).\n\n'
    '  · LOS CLONES LIMPIAN LA VISIÓN: «estas palas Clon tratarán de\n'
    '    eliminar cualquier poder de molestia de visión como confeti o\n'
    '    el superpoder de Globos del Clown» — los globos del Clown son\n'
    '    CAZABLES por hook (clonBlancos, contrato PLANTILLA-GUIA §4.2;\n'
    '    locura módulo v27: el kill usa el pop propio del módulo) y el\n'
    '    confeti lo BARRE el núcleo (createConfetti.kill: las partículas\n'
    '    cazadas no renacen hasta que la ráfaga termina). Con blancos los\n'
    '    clones VUELAN a ellos; sin blancos patrullan la banda del\n'
    '    confeti; y si el aire está limpio vuelven a la guardia de ±50 cm.\n\n'
    '  · VOZ DEL SELECTOR (petición del dueño): «cuando tenemos cargado\n'
    '    algún poder y movemos el joystick para seleccionarlo que la voz\n'
    '    diga el que nos aparece seleccionado… si no tenemos nada voz\n'
    '    dirá Sin poder… dice de forma rápida solo el nombre». Voces\n'
    '    NATIVAS Piper embebidas (davefx/lessac), NOMBRES CORTOS:\n'
    '    Super Pala · Super Efecto · Imán · Portal · Clonación · Sin\n'
    '    poder — y en inglés Super Paddle · Super Effect · Magnet ·\n'
    '    Portal · Cloning · No power. Funciona con la mano vacía, con un\n'
    '    solo poder (nombra sin ciclar) y al ciclar la matriz ⟷.\n\n'
    '  · HALL: TROFEO RETIRADO (petición del dueño: «eliminar del\n'
    '    escenario Hall la copa central y el haz de luz que cae sobre\n'
    '    ella para dejar ese espacio libre») — fuera la copa torneada,\n'
    '    sus asas y bola, la peana, el haz volumétrico, el anillo del\n'
    '    techo, la placa plateado/oro y su foco: el CENTRO queda LIBRE\n'
    '    sobre el emblema del suelo. Sigue vivo el vaivén de las 7 bolas\n'
    '    doradas. Y SUELO NUEVO del Hall con la imagen del dueño\n'
    '    (suelo.jpg versión r58, byte-exacto).\n\n'
    '  · CONCESIÓN del clon por la MISMA puerta de siempre (cada 20\n'
    '    toques = +1 carga, tope ×3), icono del DUEÑO (etiqueta\n'
    '    SuperPala_Clon) con anillo de tiempo azul fantasma, voz nativa\n'
    '    «¡Súper clonación de pala!» / «Super clone booster!», sonido y\n'
    '    háptica propios. VERIFICACIÓN: capa AS nueva (qa_clon_voz_v3650,\n'
    '    69 checks: agujas + mecánica real headless — ventana de 10 s,\n'
    '    guardia ±50 cm, devolución legal del 90 %, el 10 % que falla,\n'
    '    prioridad del jugador, voz del selector con 0 y 1 poderes) ·\n'
    '    capa W re-anclada al hall sin trofeo (43 checks) · AF/AQ/AR\n'
    '    re-ancladas (5 poderes + suelo nuevo) · golden de física\n'
    '    INTACTO (el clon vive fuera del paso físico).\n\n'
    '  · Conserva TODO: la norma de 20 toques, las ventanas de 10 s del\n'
    '    efecto y del imán, la guía de tiro con el solver de la casa, el\n'
    '    spin real por barrido con su firma SÓLO en la mesa del rival, la\n'
    '    PALA METÁLICA −80 %, el portal EXPLÍCITO, la norma de emociones\n'
    '    del rival en los 6 campeonatos, la bomba por intervalos y el\n'
    '    ladrillo eléctrico con su cadena, la matriz con ciclo ⟷, el\n'
    '    passthrough EN CALIENTE, el SALÓN DEL ARTISTA, la SALA DEL\n'
    '    PARTIDO, PRO CIRCUITO, el ESCUDO DE PALA, el REACTOR DE IMPULSO,\n'
    '    la CCD SDF, el saque VR realista, CRAZY TV en directo y los 5\n'
    '    campeonatos.\n\n'


    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:64s} {v}\n' for k, v in ficheros.items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v3650-sdk6-COMPLETO.zip'
if zip_c.exists():
    zip_c.unlink()
print('· Comprimiendo paquete COMPLETO (campeonatos incluidos, ~110 MB)...')
run(f'cd "{STAGE}" && zip -r -q -X "{zip_c}" .')

# ── 4. ZIP ligera (sin campeonatos) ──────────────────────────────
champ_bak = STAGE / 'championships'
tmp_champ = RAIZ / 'scripts' / 'staging-champs-bak'
if tmp_champ.exists():
    shutil.rmtree(tmp_champ)
shutil.move(str(champ_bak), str(tmp_champ))
champ_bak.mkdir()
(champ_bak / 'PON-AQUI-LOS-CAMPEONATOS.txt').write_text(
    'Esta carpeta va vacía en el paquete ligero.\n'
    'El juego funciona igual (Partido, Entrenamiento, Supervivencia y P2P);\n'
    'solo faltarán los campeonatos extra. Copia aquí la carpeta championships/\n'
    'del paquete COMPLETO para tenerlos.\n', encoding='utf-8')
zip_l = DL / 'crazypp-v3650-sdk6-ligera.zip'
if zip_l.exists():
    zip_l.unlink()
print('· Comprimiendo paquete LIGERA (sin campeonatos, ~11 MB)...')
run(f'cd "{STAGE}" && zip -r -q -X "{zip_l}" .')
shutil.rmtree(champ_bak)
shutil.move(str(tmp_champ), str(champ_bak))   # staging queda íntegro otra vez

# ── 4b. ZIP Cloudflare (estático puro, sin TS ni package.json) ───
CF_STAGE = RAIZ / 'scripts' / 'staging-cloudflare'
if CF_STAGE.exists():
    shutil.rmtree(CF_STAGE)
shutil.copytree(STAGE, CF_STAGE)
shutil.rmtree(CF_STAGE / 'extras-nextjs', ignore_errors=True)
shutil.rmtree(CF_STAGE / 'live-service', ignore_errors=True)
(CF_STAGE / 'NOTA-CLOUDFLARE.txt').write_text(
    'CRAZY PING PONG · V3.6.50-SDK6 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el SDK DE CAMPEONATOS de la\n'
    'FASE 7 — el SDK v1.x cerrado: rival, tablero, música — y los SUPERPODERES\n'
    'REDEFINIDOS:\n'
    'aviso con la partida congelada, METEORITOS en 3D, RAYO TRACTOR con\n'
    'dron que atrapa la bola hasta soltarla en caída vertical, GRAVEDAD\n'
    'CERO que hace rebotar la bola entre partículas y la voz del ASTRO\n'
    '(risa_astro.mp3 / enfado_astro.mp3), el ESCUDO DE PALA en la etapa\n'
    '4, el REACTOR DE IMPULSO en la etapa 2 con dianas visibles 2 s y\n'
    'la pelota que siempre vuelve a la base, la CCD SDF de contacto, el\n'
    'saque VR realista y el hall del anfitrión), tv.html (CRAZY TV),\n'
    'assets/, championships/ (5 campeonatos + el SDK compartido\n'
    'sdk/champ_sdk.js), vendor/, LEEME-DESPLIEGUE.txt y VERSION.txt.\n\n'
    '¿Y el relay (live-service)?\n'
    '  Cloudflare Pages solo acepta ficheros estáticos en subida directa\n'
    '  y rechaza paquetes con TypeScript o package.json. El relay NO va\n'
    '  aquí: descárgalo del paquete COMPLETO (carpeta live-service/) o\n'
    '  del mini-zip live-service-SOLO, y súbelo a Railway/Render con\n'
    '  «npm install && npm start».\n'
    '  La guía LEEME-DESPLIEGUE.txt de este mismo paquete lo explica.\n\n'
    'Sin relay todo sigue funcionando como siempre (Partido,\n'
    'Entrenamiento, Supervivencia y P2P); solo la TV en vivo requiere\n'
    'ese relay encendido y el parámetro ?relay=http://IP:3004.\n',
    encoding='utf-8')
zip_cf = DL / 'crazypp-v3650-sdk6-CLOUDFLARE.zip'
if zip_cf.exists():
    zip_cf.unlink()
print('· Comprimiendo paquete CLOUDFLARE (estático puro, ~110 MB)...')
run(f'cd "{CF_STAGE}" && zip -r -q -X "{zip_cf}" .')
resid = run(
    f'cd "{CF_STAGE}" && find . \\( -name "*.ts" -o -name "*.tsx" '
    f'-o -name "package.json" -o -name "tsconfig*" \\) -print')
if resid.strip():
    sys.exit(f'FALLO: el paquete Cloudflare contiene ficheros prohibidos:\n{resid}')
print('  Chequeo anti-TypeScript/package.json: limpio')

# ── 5. Verificación de integridad ────────────────────────────────
for z in (zip_c, zip_l, zip_cf):
    out = run(f'unzip -t "{z}" | tail -1')
    print(f'  {z.name}: {out.strip()}')

# ── 5b. Mini-zip SOLO-RELAY (6 KB) para GitHub/Railway ───────────
zip_sr = DL / 'crazypp-live-service-SOLO.zip'
if zip_sr.exists():
    zip_sr.unlink()
print('· Comprimiendo mini-zip SOLO-RELAY (live-service, ~6 KB)...')
run(f'cd "{STAGE}" && zip -r -q -X "{zip_sr}" live-service')
out = run(f'unzip -t "{zip_sr}" | tail -1')
print(f'  {zip_sr.name}: {out.strip()}')

# ── 6. Verificación de extras del paquete COMPLETO ───────────────
out = run(f'unzip -p "{zip_c}" extras-nextjs/descargas/page.tsx | grep -c "3.6.50" || true')
n3636 = int(out.strip() or '0')
print(f'  page.tsx dentro del COMPLETO: {n3636} menciones 3.6.50')
if n3636 < 4:
    sys.exit('FALLO: el hub empaquetado no es el v360 (¿se editó después de construir?)')
out2 = run(f'unzip -l "{zip_c}" | grep -c reactor_impulso || true')
if int(out2.strip() or '0') < 9:
    sys.exit('FALLO: las 9 imágenes del REACTOR DE IMPULSO no van dentro del COMPLETO')
print('  reactor_impulso/ (9 imágenes) dentro del COMPLETO: OK')
out3 = run(f'unzip -l "{zip_c}" | grep -c nucleo_gravedad || true')
if int(out3.strip() or '0') < 1:
    sys.exit('FALLO: el núcleo GLB de la etapa 2 no va dentro del paquete COMPLETO')
print('  nucleo_gravedad_lp.glb dentro del COMPLETO: OK')

# ── 7. Copia al centro de descargas de la preview ────────────────
DESC.mkdir(exist_ok=True)
for z in (zip_c, zip_l, zip_cf, zip_sr):
    shutil.copy2(z, DESC / z.name)
print('· Copiados a public/descargas/ (descargables desde la preview).')

print('\nRESUMEN')
for z in (zip_c, zip_l, zip_cf, zip_sr):
    print(f'  {z.name:42s} {z.stat().st_size:>13,} B')
print('\nV3.6.50-SDK6 lista: TELEMETRÍA reparada (array directo + routing por host, FASE 8) sobre el SDK v1.x cerrado (FASE 7).')

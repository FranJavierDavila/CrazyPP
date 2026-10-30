#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.6.88-SDK6.
Construye cuatro ZIP listos para subir:
  · crazypp-v3688-sdk6-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                     campeonatos, ~110 MB)
  · crazypp-v3688-sdk6-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v3688-sdk6-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
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
SRC = RAIZ / 'scripts' / 'release-v3688'
STAGE = RAIZ / 'scripts' / 'staging-v3688'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.6.88-SDK6'
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
if "const VERSION = '3.6.88-SDK6'" not in game_src:
    sys.exit('FALLO: public/game.html no es la V3.6.88-SDK6 (VERSION distinta)')
if 'V3.6.88-SDK6' not in game_src:
    sys.exit('FALLO: el badge estático no es V3.6.88-SDK6')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
if 'v3688-sdk6' not in hub or 'v3667-sdk6' in hub or 'v364-sdk4' in hub or 'v363-sdk3' in hub or 'v362-sdk2' in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:
    sys.exit('FALLO: el hub /descargas no apunta a los paquetes v3688-sdk6')
man = json.loads((PUB / 'championships/estacion_orbital/manifest.json').read_text(encoding='utf-8'))
if man.get('version') != 17 or man['rival']['name'] != 'ASTRO':
    sys.exit('FALLO: el manifest de estacion_orbital no es el v17 (ASTRO EN EL RIG, manifest v17)')
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
    'magia': (33, ("import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                   '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
                   'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                   'const __CORE = getCore() || {}')),
    'locura': (27, ("import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
                    'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
                    'const __CORE = getCore() || {}')),
    'halloween': (3, ('createSfx, createMusic, createPowerSign, createRival, createCartel',
                      "const MOD_ID = 'halloween'",
                      'PLANTILLA_PODERES.gelatina')),
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
print('· Adopción SDK2/SDK3/SDK4/SDK5 verificada: oeste v56 · magia v33 · locura v27 · halloween v2 (plantilla r86 + 4 superpoderes)')
# — FASE 5 (SDK3): la MÚSICA en bucle vive en el SDK ——————————
MUSICA = {
    'oeste': (56, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   "puede: () => this._stageMode !== 'tren'",
                   'get _musSDKv()', "syncMode: 'direct'",
                   'excluso: () => this.ctrl._musSDK.sonando()',
                   '_musicStart() { this._musSDKv.on(); }',
                   '_musicStop() { this._musSDKv.off(); }')),
    'magia': (33, ('get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
                   'vol: () => this._musicEffVol()',
                   '_syncMusicGain() {', 'this._musSDK.sync();')),
    'halloween': (3, ('createMusic(() => GAME', 'so.musicOpts || {}')),
    'estacion_orbital': (17, ('get _musSDK()', 'gateOn: true,',
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
print('· Música SDK3/4/5 verificada: oeste v56 (BSO+vagón) · magia v33 (BSO) · halloween v3 (midnight_volley) · orbital v16 (bso.wav)')
# — FASE 6 (SDK4): el CARTEL DE SUPERPODER vive en el SDK ——————
POWERSIGN = {
    'oeste': (56, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'plano'",
                   'pintar: (aplicar) => this._pintarRespaldo(aplicar)',
                   'oesteCanvas(1024, 560)')),
    'magia': (33, ('createPowerSign(THREE', "coreo: 'clasica'", "arte: 'canvas1024'",
                   'fallbackURL: () => paintPowerBanner()')),
    'locura': (27, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
                    "arte: 'fit1833'")),
    'estacion_orbital': (17, ('createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
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
print('· PowerSign SDK5 verificada: oeste v56 · magia v33 · locura v27 · orbital v16 (tablón en el SDK)')
# — FASE 7 (SDK5): STANDEE + TABLERO en el SDK; CERO decodeAudioData —
RIVAL_CARTEL = {
    'estacion_orbital': (17, ('createRival(THREE', "modo: 'perezoso'",
                              "base: 'rival.webp'", 'createCartel(THREE',
                              'this._cartelSDK.pinta((c, W, H) => {',
                              'this._rivalSDK.rivalEstado(estado);')),
    'halloween': (3, ('createRival(THREE', "modo: this.rv.modo || 'precarga'",
                       "base: this.rv.base || 'rival.webp'", 'createCartel(THREE',
                       'cartel.pinta(', 'this.r.rivalEstado(')),
}
for mod, (vman, tokens) in RIVAL_CARTEL.items():
    m = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    if m.get('version') != vman:
        sys.exit(f'FALLO: manifest de {mod} no es v{vman} (Rival/Cartel SDK5)')
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    for tk in tokens:
        if tk not in srcm:
            sys.exit(f'FALLO: {mod}/index.js no contiene {tk!r}')
for mod in ('oeste', 'magia', 'locura', 'estacion_orbital', 'halloween'):
    srcm = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    if 'decodeAudioData(' in srcm:
        sys.exit(f'FALLO: {mod} conserva decodeAudioData propio (FASE 7: cero en los 5)')
print('· Rival/Cartel SDK5 verificada: orbital v16 (perezoso) · halloween v3 (precarga) — 0 decodeAudioData en los 5')
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
print('· Identidad verificada: game.html V3.6.88-SDK6 + hub v3688-sdk6 + SDK de campeonatos (rival, tablón, tablero y música en el SDK)')

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
    'championships/halloween/index.js':
        sha256(STAGE / 'championships/halloween/index.js'),
    'vendor/socket.io.min.js': sha256(STAGE / 'vendor' / 'socket.io.min.js'),
}
(STAGE / 'VERSION.txt').write_text(
    'CRAZY PING PONG · FICHA DE VERSIÓN\n'
    '==================================\n'
    f'Versión : {VER}\n'
    f'Fecha   : {FECHA}\n'
    'Base    : V3.6.4-SDK4 + V3.6.3-SDK3 + V3.6.2-SDK2 + V3.6.1-SDK1 + V3.6.0-SUP1 + V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\n'
    'Rama    : main · SDK6 (FASE 90 — SALA Y ESCENA EN VIVO (r96). Seis\n'
    'frentes del dueño en una ronda: la sala de partidos se ve al\n'
    'ajustarla, SALA y MESA con sus botones propios, la altura de mesa\n'
    'pasa a DESLIZADOR continuo, TODO el menú gana tooltips, los\n'
    'sonidos dejan de solaparse, las pieles de mesa quedan FUERA de los\n'
    'campeonatos y una auditoría de fluidez tunde el foveado agresivo.\n'
    '\n'
    'Novedades de esta versión (frente a V3.6.87-SDK6):\n'
    '\n'
    '  · SALA Y ESCENA EN VIVO: al entrar en Ajustes › Sala y Escena el\n'
    '    entorno deja el HALL y salta a la SALA DE PARTIDOS (sala + mesa\n'
    '    + marcador; el rig retrocede 1,15 m para que el panel no tape\n'
    '    la mesa). Todo cambio se ve AL MOMENTO en la mesa real. Al\n'
    '    salir de la categoría o cerrar el menú, vuelta EXACTA al Hall.\n'
    '\n'
    '  · SALA y MESA como SUBMENÚS-BOTÓN: dos tarjetas con la estética\n'
    '    del menú (color + icono propio de mesa) que abren SU página —\n'
    '    SALA (los cuatro temas + passthrough) y MESA (altura + aspecto).\n'
    '\n'
    '  · ALTURA POR DESLIZADOR: adiós a los tres presets — un raíl\n'
    '    continuo ajusta el tablero entre Baja (70 cm) y Alta (84 cm),\n'
    '    fijando la altura AL PUNTO apuntado, con botones − / + de paso\n'
    '    fino (1 cm) y lectura viva en cm y zona. DIMS.tableTopY muta y\n'
    '    física, IA, saque y escena la leen en vivo; la red conserva sus\n'
    '    15,25 cm reglamentarios y las patas se re-escalan honestas.\n'
    '\n'
    '  · TOOLTIPS (norma general del dueño): al APUNTAR cualquier opción\n'
    '    de los menús aparece una caja con una breve indicación de qué\n'
    '    hace ese ajuste, en el idioma escogido (ES/EN, ~55 claves\n'
    '    nuevas). Sin apuntar no pinta nada: cero ruido, cero coste.\n'
    '\n'
    '  · SONIDOS SIN SOLAPES: cada volumen (música / efectos) tiene SU\n'
    '    fila de etiqueta y SU fila de controles — nada pisa nada — y las\n'
    '    barras son CLICABLES: tocar un punto fija el volumen al punto.\n'
    '\n'
    '  · PIELES DE MESA SÓLO PARTIDAS Y ENTRENAMIENTO (petición literal:\n'
    '    «los ajustes de pieles de las mesas no deben afectar a los\n'
    '    campeonatos, sólo a las partidas y entrenamiento»). En\n'
    '    campeonato activo la mesa está en su AZUL NATIVO: el tinte del\n'
    '    dueño ya no tiñe la mesa de La Locura ni la de nadie. Al salir\n'
    '    del campeonato, la piel elegida vuelve sola.\n'
    '\n'
    '  · AUDITORÍA DE FLUIDEZ (el dueño: «deformación en medio de la\n'
    '    pantalla» en una partida de resistencia): sospechoso confirmado\n'
    '    — el FOVEADO FIJO (FFR) agresivo del autocalibrador llegaba a\n'
    '    0,8 y dibuja los anillos de compresión dentro de la vista. \n'
    '    AHORA: NITIDEZ (FFR) en AJUSTES › RENDIMIENTO con 4 niveles\n'
    '    (Máxima 0 · Alta 0,25 · Normal 0,5 · Rinde 0,75) que CAPAN el\n'
    '    gobernador, techo honesto 0,65 sin tope manual y Quest 3 naciendo\n'
    '    a 0,35. El gobernador sigue garantizando 60 FPS, pero ya nunca\n'
    '    deforma la imagen en plena vista.\n'
    '\n'
    '  · QA r96 NUEVA (90 checks: deslizador con DIMS/red/patas/paso\n'
    '    fino/clamps, pieles con regla de campeonato simulada, vista de\n'
    '    sala Hall↔cancha con vuelta exacta, raíl y barras que obedecen\n'
    '    al punto apuntado por mano, tooltips con tinta nueva, FFR con\n'
    '    topes y persistencia, 14 páginas del menú repintadas sin\n'
    '    pageerrors) + cascada re-anclada a 3.6.88.\n'
    '\n'
    '\n'
    '\n'
    '\n'
    '\n'
    '\n'
    '\n'






    '  · EL DEFECTO QUE IMPEDÍA JUGAR (cazado por la auditoría): en el\n'
    '    transporte binario, los golpes de rallye NUNCA se anunciaban — la\n'
    '    marca _localHit sólo vivía en la rama antigua v1: sin HIT kind 0,\n'
    '    la FSM de bola no volvía a «own», no había BALL_HANDOFF de vuelta\n'
    '    y el rival recibía un fantasma injugable («veo las palas pero no\n'
    '    puedo jugar la bola»). El duelo de r81 no lo cazó porque llamaba\n'
    '    sendHit() a mano. Ahora todo golpe propio con el rallye vivo se\n'
    '    anuncia solo (y SOLO con el rallye vivo: la bola muerta de un\n'
    '    punto ya no puede resucitarse a sí misma — punto fantasma cazado\n'
    '    en vivo por la batería).\n\n'
    '  · TRES DEFECTOS MÁS DE PRECISIÓN: (1) el JitterBuf guardaba las\n'
    '    muestras POR REFERENCIA al buffer reutilizado del decodificador:\n'
    '    toda la historia era la última pose (aliasing) — el validador\n'
    '    juzgaba el golpe con la pose del ÚLTIMO paquete (el follow-through\n'
    '    de un smash recorre 25-60 cm) y el avatar rival iba a tirones;\n'
    '    ahora cada muestra se CLONA y se sella por el instante de CAPTURA\n'
    '    del emisor (no por la llegada); (2) el eco NTP del reloj compartido\n'
    '    estaba MUERTO (los campos echoTime/echoDelay nunca se escribían):\n'
    '    el offset quedaba congelado en el ancla gruesa y el validador\n'
    '    podía rechazar por «tHit en el futuro» — el eco vive y el reloj se\n'
    '    refina en vivo (tolerancia de futuro 120 ms); (3) el LANZAMIENTO\n'
    '    del saque (kind 2) exigía correlativo shot+1 que no lleva: se\n'
    '    rechazaba SIEMPRE y el receptor quedaba con la bola HELD\n'
    '    congelada — el correlativo lo porta el golpe, no el lanzamiento.\n\n'
    '  · TÚNEL PEERJS DE EMERGENCIA: si el ICE del transporte propio no\n'
    '    abre en 11 s PERO la sala vive, el canal fast viaja ENCAPSULADO por\n'
    '    la DataConnection PeerJS — la FSM v2 entera corre idéntica sobre el\n'
    '    tubo fiable. Adiós a la degradación silenciosa al v1 cosmético\n'
    '    («veo palas moverse pero poco más»). HELLO tolerante a BUILD: dos\n'
    '    cascos con cachés desiguales ya NO rompen el enlace (aviso + voz\n'
    '    pidiendo recargar game.html?v=v3674 en ambos); el partido v1\n'
    '    silencioso está BLOQUEADO con mensaje claro.\n\n'
    '  · REFERENCIAS EXACTAS VISIBLES: la bola HELD del rival se VE EN SU\n'
    '    MANO LIBRE (pose de red espejada) — el saque se lee desde el primer\n'
    '    frame; la montura del avatar usa la MANO FÍSICA del rival (bit 8,\n'
    '    no el hueco del mando); el enlace se CANTA por voz («Enlace directo\n'
    '    establecido» / «Enlace por túnel»); window.__PP_NET.netInfo() y la\n'
    '    telemetría net_match exponen vía, RTT, reloj, pérdida, retraso del\n'
    '    jitter buffer y las CAUSAS de cada rechazo (diagnóstico a\n'
    '    distancia de un partido real fallido); RESYNC hereda las banderas\n'
    '    del árbitro (lastHitter/validBounce).\n\n'



    '  · Conserva TODO lo anterior (r75: los modos todo encaja;\n'
    '    r74: B en el Pro Training, menú sobre el cartel EMPEZAR, glow\n'
    '    que sigue la mano, devoluciones sin atascos, modos con calma\n'
    '    y sin bola sonora, orden Clow→Wizard→Forajido, telón común y\n'
    '    zona muerta del suelo; r73: menú al cielo del render,\n'
    '    candados bien colocados, índice resiliente y telón de teatro;\n'
    '    r72: panel sin solapes y telón con espera honesta; r71: saque\n'
    '    reglamentario del profesor y AJUSTES por subcategorías;\n'
    '    r69-r67: una sola raqueta, golpes honestos, academia en tus\n'
    '    manos; r66-r65: sobre la mesa, onboarding hablado; r61:\n'
    '    estela de poderes, rival adaptativo y repetición; 5 poderes,\n'
    '    voz del selector, expresiones, passthrough en caliente,\n'
    '    SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).\n\n'









    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:64s} {v}\n' for k, v in ficheros.items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v3688-sdk6-COMPLETO.zip'
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
zip_l = DL / 'crazypp-v3688-sdk6-ligera.zip'
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
    'CRAZY PING PONG · V3.6.88-SDK6 · PAQUETE CLOUDFLARE\n'
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
zip_cf = DL / 'crazypp-v3688-sdk6-CLOUDFLARE.zip'
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
out = run(f'unzip -p "{zip_c}" extras-nextjs/descargas/page.tsx | grep -c "3.6.88" || true')
n3688 = int(out.strip() or '0')
print(f'  page.tsx dentro del COMPLETO: {n3688} menciones 3.6.88')
if n3688 < 4:
    sys.exit('FALLO: el hub empaquetado no es el v3684 (¿se editó después de construir?)')
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
print('\nV3.6.88-SDK6 lista: TELEMETRÍA reparada (array directo + routing por host, FASE 8) sobre el SDK v1.x cerrado (FASE 7).')

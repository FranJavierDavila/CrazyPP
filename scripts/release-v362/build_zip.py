#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.6.2-SDK2.
Construye cuatro ZIP listos para subir:
  · crazypp-v362-sdk2-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                     campeonatos, ~110 MB)
  · crazypp-v362-sdk2-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v362-sdk2-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
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
SRC = RAIZ / 'scripts' / 'release-v362'
STAGE = RAIZ / 'scripts' / 'staging-v362'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.6.2-SDK2'
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
if "const VERSION = '3.6.2-SDK2'" not in game_src:
    sys.exit('FALLO: public/game.html no es la V3.6.2-SDK2 (VERSION distinta)')
if 'V3.6.2-SDK2' not in game_src:
    sys.exit('FALLO: el badge estático no es V3.6.2-SDK2')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
if 'v362-sdk2' not in hub or 'v361-sdk1' in hub or 'v360-sup1' in hub or 'v351-imp2' in hub or 'v350-esc1' in hub or 'v341-riv1' in hub or 'v340-imp1' in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:
    sys.exit('FALLO: el hub /descargas no apunta a los paquetes v362-sdk2')
man = json.loads((PUB / 'championships/estacion_orbital/manifest.json').read_text(encoding='utf-8'))
if man.get('version') != 14 or man['rival']['name'] != 'ASTRO':
    sys.exit('FALLO: el manifest de estacion_orbital no es el v3.6.2 (ASTRO, manifest v14)')
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
           'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',
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
for tk in ("const SDK_VERSION = '1.1.0'", 'export function createSfx',
           'export function congela', 'export function descongela',
           'export function getCore', 'export function assetURL',
           'forma promesa (v2.125)', 'function precarga',
           'opts && opts.pan', 'window.__PP_SDK = SDK_VERSION'):
    if tk not in sdk:
        sys.exit(f'FALLO: champ_sdk.js no contiene {tk!r}')
# — FASE 4 (SDK2): los 4 campeonatos adoptantes ——————————————
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
print('· Identidad verificada: game.html V3.6.2-SDK2 + hub v362-sdk2 + SDK de campeonatos (adopción en los 4)')

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
    'Base    : V3.6.1-SDK1 + V3.6.0-SUP1 + V3.5.1-IMP2 + V3.5.0-ESC1 + V3.4.x + V3.3.0-NUC1 + V3.2.x-ORB + V3.1.2-CCD1\n'
    'Rama    : main · SDK2 (FASE 4 — el SDK adoptado por los 5 campeonatos)\n\n'
    'Novedades de esta versión (frente a V3.6.1-SDK1):\n'
    '  · FASE 4 de la modularización P0: el SDK DE CAMPEONATOS\n'
    '    (champ_sdk.js v1.1.0) ya lo usan LOS 5 campeonatos. La\n'
    '    Estación Orbital estrenó la adopción en SDK1; ahora se suman:\n'
    '    · OESTE (manifest v49): sus 4 motores SFX one-shot (risa del\n'
    '      forajido, risa del pueblo, jingle de oleada y risas del robo\n'
    '      del vagón) y sus 3 congelados (duelo de revólver ×2 y aviso\n'
    '      de superpoder) delegan en el SDK; volúmenes, anti-spam de\n'
    '      3,2 s y paneo 0,4 intactos. La BSO del saloon y la música\n'
    '      del vagón conservan su motor propio (fundido, resurrección\n'
    '      de contexto y sincronía con el núcleo).\n'
    '    · MAGIA (v29): la risa del mago y el congelado del aviso.\n'
    '    · LA LOCURA (v21): el congelado del aviso — el patrón v2.40\n'
    '      que NACIÓ en este módulo — y el puente al núcleo.\n'
    '    · VALLE NEÓN (v2): el puente al núcleo.\n'
    '  · SDK v1.1.0: precarga() (calentar la cache sin sonar) y\n'
    '    opts.pan (paneo estéreo opcional). Un bug del kernel se\n'
    '    arregla UNA vez y sirven los 5 campeonatos.\n'
    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta, los\n'
    '    superpoderes, el reactor, el escudo y los duelos se comportan\n'
    '    exactamente igual.\n'
    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\n'
    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\n'
    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\n'
    '    oficial, física viva, palas con carácter, CRAZY TV en\n'
    '    directo y los 5 campeonatos.\n\n'
    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:64s} {v}\n' for k, v in ficheros.items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v362-sdk2-COMPLETO.zip'
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
zip_l = DL / 'crazypp-v362-sdk2-ligera.zip'
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
    'CRAZY PING PONG · V3.6.2-SDK2 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el SDK DE CAMPEONATOS de la\n'
    'FASE 4 — adoptado por los 5 campeonatos — y los SUPERPODERES\n'
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
zip_cf = DL / 'crazypp-v362-sdk2-CLOUDFLARE.zip'
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
out = run(f'unzip -p "{zip_c}" extras-nextjs/descargas/page.tsx | grep -c "3.6.2" || true')
n362 = int(out.strip() or '0')
print(f'  page.tsx dentro del COMPLETO: {n362} menciones 3.6.2')
if n362 < 4:
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
print('\nV3.6.2-SDK2 lista: SDK en LOS 5 CAMPEONATOS (FASE 4) + superpoderes redefinidos + voz del ASTRO + diana 2 s.')

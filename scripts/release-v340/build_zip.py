#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.4.0-IMP1.
Construye cuatro ZIP listos para subir:
  · crazypp-v340-imp1-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                     campeonatos, ~110 MB)
  · crazypp-v340-imp1-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v340-imp1-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
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
SRC = RAIZ / 'scripts' / 'release-v340'
STAGE = RAIZ / 'scripts' / 'staging-v340'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.4.0-IMP1'
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
if "const VERSION = '3.4.0-IMP1'" not in game_src:
    sys.exit('FALLO: public/game.html no es la V3.4.0-IMP1 (VERSION distinta)')
if 'V3.4.0-IMP1' not in game_src:
    sys.exit('FALLO: el badge estático no es V3.4.0-IMP1')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
if 'v340-imp1' not in hub or 'v330-nuc1' in hub or 'v321-orb2' in hub:
    sys.exit('FALLO: el hub /descargas no apunta a los paquetes v340-imp1')
man = json.loads((PUB / 'championships/estacion_orbital/manifest.json').read_text(encoding='utf-8'))
if man.get('version') != 9 or man['rival']['name'] != 'ASTRO':
    sys.exit('FALLO: el manifest de estacion_orbital no es el v3.4.0 (ASTRO, manifest v9)')
if man['stages'][3]['id'] != 'impulso' or man['stages'][1]['id'] != 'reactor':
    sys.exit('FALLO: el camino del manifest no es reactor/impulso')
eo = (PUB / 'championships/estacion_orbital/index.js').read_text(encoding='utf-8')
for tk in ('class ReactorImpulso', 'const IMP_CFG', "id: 'impulso'",
           '_empezarImpulso', '_arrancarImpulso', '_oleadaArranca',
           '_dianaHit', '_pertAplica', '_cadenaDestruye',
           'nucleo_gravedad_lp.glb', 'class ReactorInestable',
           "id: 'reactor'", 'class EOArkanoid', 'class PwSignEO',
           'RIV_H = 2.15', 'position.set(1.62, RIV_H / 2',
           'x: 1197, y: 335, r: 115', 'TAPA_W = 240 / 1376',
           "get gunArmed() { return !!(CTRL && CTRL.gunArmed); }"):
    if tk not in eo:
        sys.exit(f'FALLO: el módulo orbital no contiene {tk!r}')
if "{ kind: 'prueba', id: 'muro2'" in eo or "id: 'muro1'" in eo:
    sys.exit("FALLO: el módulo aún enruta etapas como muros (muro1/muro2)")
for at in ('reactor_impulso/frente.jpg', 'reactor_impulso/fondo.jpg',
           'reactor_impulso/techo.jpg', 'reactor_impulso/suelo.jpg',
           'reactor_impulso/izquierda.png', 'reactor_impulso/derecha.png',
           'reactor_impulso/diana_quantica.png', 'reactor_impulso/base.png',
           'reactor_impulso/pantallainfo.png', 'nucleo_gravedad_lp.glb',
           'pistol.glb', 'mapa.png', 'superpower.png', 'angry.webp'):
    p = PUB / 'championships/estacion_orbital/assets' / at
    if not p.exists() or p.stat().st_size < 1000:
        sys.exit(f'FALLO: falta el asset orbital {at}')
if (PUB / 'championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png').stat().st_size != 409356:
    sys.exit('FALLO: diana_quantica.png no es byte-exacta (409.356 B)')
print('· Identidad verificada: game.html V3.4.0-IMP1 + hub v340-imp1 + impulso en la etapa 4')

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
    'vendor/socket.io.min.js': sha256(STAGE / 'vendor' / 'socket.io.min.js'),
}
(STAGE / 'VERSION.txt').write_text(
    'CRAZY PING PONG · FICHA DE VERSIÓN\n'
    '==================================\n'
    f'Versión : {VER}\n'
    f'Fecha   : {FECHA}\n'
    'Base    : V3.1.2-CCD1 (precisión de contacto por CCD SDF) + V3.2.x-ORB + V3.3.0-NUC1\n'
    'Rama    : main · IMP1 (Reactor de impulso en la etapa 4)\n\n'
    'Novedades de esta versión (frente a V3.3.0-NUC1) — mecánica del dueño:\n'
    '  · ETAPA 4 NUEVA · REACTOR DE IMPULSO: fuera el ARKANOID II. La prueba\n'
    '    tiene SALA PROPIA con las 6 imágenes del dueño (sin mesa: la BASE\n'
    '    FLOTANTE con base.png repone la pelota) y ventanas laterales con\n'
    '    efecto de VIAJE A VELOCIDAD LUMÍNICA (el mismo en ambas paredes).\n'
    '  · EL NÚCLEO alterna ESTABLE (azul, rotación uniforme) e INESTABLE\n'
    '    (rojo pulsante, rotación caótica, ALARMA sonora) y EXPULSA CUBOS\n'
    '    CUÁNTICOS en 3 OLEADAS de 3, 5 y 7 con 2 minutos independientes\n'
    '    por oleada. Sin rival durante la partida.\n'
    '  · LA PALA conserva su mecánica: la pelota se golpea de verdad\n'
    '    (colisión por barrido del segmento, la velocidad de tu pala manda)\n'
    '    y cada cubo destruido se fragmenta en cubitos (sólo visuales).\n'
    '  · PISTOLA LÁSER (pistol.glb) en la mano libre: acierta las DIANAS\n'
    '    cuánticas (diana_quantica.png, 1 s visibles / 1 s de espera, cada\n'
    '    vez en otra posición) y desata PERTURBACIONES: GRAVEDAD 0 (deriva\n'
    '    flotante), ATRACTOR (los agrupa: UN golpe los destruye TODOS en\n'
    '    cadena) y SUPERGRAVEDAD (caen a ras de suelo comprimidos). También\n'
    '    hay cambio automático cada 30 s (independiente de las dianas).\n'
    '  · PANTALLA suspendida del techo (pantallainfo.png) con oleada,\n'
    '    tiempo, cubos restantes, estado del reactor y perturbación activa.\n'
    '  · DERROTA (tiempo a cero con cubos vivos): el ASTRO aparece riéndose\n'
    '    (astro_laughing.png) frente al jugador y vuelves a la sala.\n'
    '  · FIX del gatillo: el export del módulo ahora expone gunArmed/fireGun\n'
    '    (el núcleo los lee del módulo; antes no llegaban).\n'
    '  · Conserva TODO: el REACTOR DE ENERGÍA INESTABLE en la etapa 2\n'
    '    (núcleo de gravedad + esferas de plasma + compuertas), CCD SDF de\n'
    '    contacto (CCD1), saque VR realista (SRV2), gracia del saque + bote\n'
    '    honesto + prompt B (FEEL1), hall del anfitrión, ESTACIÓN ORBITAL\n'
    '    afinada (ORB2), PRO CIRCUITO, intro oficial, física viva, palas con\n'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.\n\n'
    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:64s} {v}\n' for k, v in ficheros.items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v340-imp1-COMPLETO.zip'
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
zip_l = DL / 'crazypp-v340-imp1-ligera.zip'
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
    'CRAZY PING PONG · V3.4.0-IMP1 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el REACTOR DE IMPULSO en la\n'
    'etapa 4 — cubos cuánticos, pistola láser, dianas y perturbaciones —,\n'
    'el REACTOR DE ENERGÍA INESTABLE en la etapa 2, la ESTACIÓN ORBITAL\n'
    'afinada, la CCD SDF de contacto, el saque VR realista y el hall del\n'
    'anfitrión), tv.html (CRAZY TV), assets/, championships/ (5\n'
    'campeonatos), vendor/, LEEME-DESPLIEGUE.txt y VERSION.txt.\n\n'
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
zip_cf = DL / 'crazypp-v340-imp1-CLOUDFLARE.zip'
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
out = run(f'unzip -p "{zip_c}" extras-nextjs/descargas/page.tsx | grep -c "3.4.0" || true')
n340 = int(out.strip() or '0')
print(f'  page.tsx dentro del COMPLETO: {n340} menciones 3.4.0')
if n340 < 4:
    sys.exit('FALLO: el hub empaquetado no es el v340 (¿se editó después de construir?)')
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
print('\nV3.4.0-IMP1 lista: Reactor de impulso en la etapa 4 (cubos cuánticos, pistola láser, dianas y perturbaciones).')

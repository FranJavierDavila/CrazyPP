#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.2.0-ORB1.
Construye cuatro ZIP listos para subir:
  · crazypp-v320-orb1-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                     campeonatos, ~110 MB)
  · crazypp-v320-orb1-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v320-orb1-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
                                     aceptado por la subida directa de
                                     Cloudflare Pages sin wrangler)
  · crazypp-live-service-SOLO.zip    (solo el relay, 12 KB, para GitHub → Railway)
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
SRC = RAIZ / 'scripts' / 'release-v320'
STAGE = RAIZ / 'scripts' / 'staging-v320'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.2.0-ORB1'
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
if "const VERSION = '3.2.0-ORB1'" not in game_src:
    sys.exit('FALLO: public/game.html no es la V3.2.0-ORB1 (VERSION distinta)')
if 'V3.2.0-ORB1' not in game_src:
    sys.exit('FALLO: el badge estático no es V3.2.0-ORB1')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
if 'v320-orb1' not in hub or 'v310-srv2' in hub:
    sys.exit('FALLO: el hub /descargas no apunta a los paquetes v320-orb1')
man = json.loads((PUB / 'championships/estacion_orbital/manifest.json').read_text(encoding='utf-8'))
if man.get('version') != 6 or man['rival']['name'] != 'ASTRO':
    sys.exit('FALLO: el manifest de estacion_orbital no es el v3.2.0 (ASTRO)')
eo = (PUB / 'championships/estacion_orbital/index.js').read_text(encoding='utf-8')
for tk in ('class EOArkanoid', 'superpower.png', "_A('superpower.png')"):
    if tk not in eo:
        sys.exit(f'FALLO: el módulo orbital no contiene {tk!r}')
for at in ('sala_left.jpg', 'sala_ceil.jpg', 'mapa.png', 'normas_astro.png',
           'superpower.png', 'pistol.glb', 'angry.webp', 'crazy.webp',
           'decor/escena_cohete.png'):
    p = PUB / 'championships/estacion_orbital/assets' / at
    if not p.exists() or p.stat().st_size < 1000:
        sys.exit(f'FALLO: falta el asset orbital {at}')
print('· Identidad verificada: game.html V3.2.0-ORB1 + hub v320-orb1 + módulo orbital vestido')

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

# El intro de ESTA versión es el montaje oficial (faststart). Verificación
# dura: tamaño y sha256 deben ser los del montaje oficial verificado.
intro = STAGE / 'assets' / 'intro.mp4'
if intro.stat().st_size != 5779719:
    sys.exit(f'FALLO: assets/intro.mp4 pesa {intro.stat().st_size} B (esperado 5.779.719 B — ¿se pisó con el provisional?)')
if sha256(intro)[:8] != sha256(RAIZ / 'upload' / 'intro.mp4')[:8]:
    print('  nota: intro remuxado (distinto del original subido, esperado)')
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
    'vendor/socket.io.min.js': sha256(STAGE / 'vendor' / 'socket.io.min.js'),
}
(STAGE / 'VERSION.txt').write_text(
    'CRAZY PING PONG · FICHA DE VERSIÓN\n'
    '==================================\n'
    f'Versión : {VER}\n'
    f'Fecha   : {FECHA}\n'
    'Base    : V3.1.2-CCD1 (precisión de contacto por CCD SDF)\n'
    'Rama    : main · ORB1 (decorado real de Estación Orbital + muros arkanoid)\n\n'
    'Novedades de esta versión (frente a V3.1.2-CCD1) — el arte del dueño:\n'
    '  · DECORADO REAL DE LA ESTACIÓN: los 6 planos de la sala (literas,\n'
    '    ventanal con la Tierra, esclusa, suelo y techo con luminarias)\n'
    '    visten el arte del propietario (patrón vagón del Salvaje Oeste).\n'
    '  · EL RIVAL ES EL ASTRO: 12 poses del artista con la convención del\n'
    '    clown (assets/<estado>.webp) — en duelo focused, con superpoder\n'
    '    crazy, al caer defeated; fuera el robot placeholder.\n'
    '  · MUROS ORBITALES (etapas 2 y 4): el mapa nuevo del dueño dibuja las\n'
    '    pruebas como muros de ladrillos (misma iconografía que el clown) y\n'
    '    el camino las juega como el ARKANOID de La Locura: variante 1\n'
    '    clásica (30 ladrillos, 2 min, 5 vidas) y variante 2 (54 ladrillos\n'
    '    rojos/azules + PISTOLA LÁSER pistol.glb con raycast, ladrillo negro\n'
    '    +1 min, abanico anti-atasco). Cartel de normas con la plantilla del\n'
    '    artista (normas_astro.png) vía NORMAS_SKIN.\n'
    '  · MAPA NUEVO en la pared izquierda (1376×768, nodos re-medidos).\n'
    '  · CARTEL DE SUPERPODER con la etiqueta de la casa (superpower.png,\n'
    '    el mismo sello «Super Power!!» de los otros campeonatos) + miniatura\n'
    '    del poder (medallón) + nombre y fase.\n'
    '  · RECORTABLES reales del dueño por el suelo (cohete, astro, lander y\n'
    '    telescopio; fuera los troqueles placeholder).\n'
    '  · Conserva TODO: CCD SDF de contacto (CCD1), saque VR realista\n'
    '    (SRV2), gracia del saque + bote honesto + prompt B (FEEL1), hall\n'
    '    del anfitrión, PRO CIRCUITO, intro oficial, física viva, palas con\n'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.\n\n'
    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:28s} {v}\n' for k, v in ficheros.items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v320-orb1-COMPLETO.zip'
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
zip_l = DL / 'crazypp-v320-orb1-ligera.zip'
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
    'CRAZY PING PONG · V3.2.0-ORB1 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el DECORADO REAL de la ESTACIÓN\n'
    'ORBITAL y los MUROS ORBITALES, CCD SDF de contacto, saque VR realista,\n'
    'hall del anfitrión e intro oficial), tv.html (CRAZY TV), assets/,\n'
    'championships/ (5 campeonatos), vendor/, LEEME-DESPLIEGUE.txt y\n'
    'VERSION.txt.\n\n'
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
zip_cf = DL / 'crazypp-v320-orb1-CLOUDFLARE.zip'
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

# ── 5b. Mini-zip SOLO-RELAY (12 KB) para GitHub/Railway ──────────
zip_sr = DL / 'crazypp-live-service-SOLO.zip'
if zip_sr.exists():
    zip_sr.unlink()
print('· Comprimiendo mini-zip SOLO-RELAY (live-service, ~12 KB)...')
run(f'cd "{STAGE}" && zip -r -q -X "{zip_sr}" live-service')
out = run(f'unzip -t "{zip_sr}" | tail -1')
print(f'  {zip_sr.name}: {out.strip()}')

# ── 6. Verificación de extras del paquete COMPLETO ───────────────
out = run(f'unzip -p "{zip_c}" extras-nextjs/descargas/page.tsx | grep -c "3.2.0" || true')
n320 = int(out.strip() or '0')
print(f'  page.tsx dentro del COMPLETO: {n320} menciones 3.2.0')
if n320 < 4:
    sys.exit('FALLO: el hub empaquetado no es el v320 (¿se editó después de construir?)')

# ── 7. Copia al centro de descargas de la preview ────────────────
DESC.mkdir(exist_ok=True)
for z in (zip_c, zip_l, zip_cf, zip_sr):
    shutil.copy2(z, DESC / z.name)
print('· Copiados a public/descargas/ (descargables desde la preview).')

print('\nRESUMEN')
for z in (zip_c, zip_l, zip_cf, zip_sr):
    print(f'  {z.name:42s} {z.stat().st_size:>13,} B')
print('\nV3.2.0-ORB1 lista: decorado real de Estación Orbital + muros arkanoid sobre la CCD SDF.')

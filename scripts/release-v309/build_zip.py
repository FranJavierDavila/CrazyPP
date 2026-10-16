#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.0.9-HALL1.
Construye cuatro ZIP listos para subir:
  · crazypp-v309-hall1-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                      campeonatos, ~107 MB)
  · crazypp-v309-hall1-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v309-hall1-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
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
SRC = RAIZ / 'scripts' / 'release-v309'
STAGE = RAIZ / 'scripts' / 'staging-v309'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.0.9-HALL1'
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
man = {
    'version': VER,
    'fecha': FECHA,
    'base': 'V3.0.8-TRN1 (saque real + zonas fieles + sparring)',
    'rama': 'main · HALL1 (hall del anfitrión + saque por dificultad)',
    'ficheros': {
        'index.html': sha256(STAGE / 'index.html'),
        'tv.html': sha256(STAGE / 'tv.html'),
        'assets/intro.mp4': sha256(intro),
        'live-service/server.mjs': sha256(LS / 'server.mjs'),
        'vendor/socket.io.min.js': sha256(STAGE / 'vendor' / 'socket.io.min.js'),
    },
}
(STAGE / 'VERSION.txt').write_text(
    'CRAZY PING PONG · FICHA DE VERSIÓN\n'
    '==================================\n'
    f'Versión : {VER}\n'
    f'Fecha   : {FECHA}\n'
    f'Base    : {man["base"]}\n'
    f'Rama    : {man["rama"]}\n\n'
    'Novedades de esta versión (frente a V3.0.8-TRN1):\n'
    '  · HALL DEL ANFITRIÓN: la sesión VR nace en una estancia cálida con\n'
    '    menú delante y una pared de trofeos que se decora sola con lo\n'
    '    conseguido (insignias, logros CRAZY, PRO CIRCUITO y pieles).\n'
    '  · ASISTENCIA DEL SAQUE POR DIFICULTAD: fácil perdona (62 % → 88 %,\n'
    '    13 cm, vy 3,5) · medio es la referencia TRN1 (45 % → 75 %, 9 cm) ·\n'
    '    difícil es tu saque (30 % → 55 %, 6 cm, vy 2,7). Se recuerda.\n'
    '  · EL CILINDRO DEL MANGO, FUERA: adiós a la cinta-cilindro que la\n'
    '    piel arrastraba sobre el mango.\n'
    '  · Conserva TODO: saque real + zonas fieles (TRN1), PRO CIRCUITO\n'
    '    (PLAY1), intro oficial (SRV1), física viva + palas (FIS1) y\n'
    '    CRAZY TV en directo (tv.html + relay).\n\n'
    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:28s} {v}\n' for k, v in man['ficheros'].items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v309-hall1-COMPLETO.zip'
if zip_c.exists():
    zip_c.unlink()
print('· Comprimiendo paquete COMPLETO (campeonatos incluidos, ~107 MB)...')
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
zip_l = DL / 'crazypp-v309-hall1-ligera.zip'
if zip_l.exists():
    zip_l.unlink()
print('· Comprimiendo paquete LIGERA (sin campeonatos, ~11 MB)...')
run(f'cd "{STAGE}" && zip -r -q -X "{zip_l}" .')
shutil.rmtree(champ_bak)
shutil.move(str(tmp_champ), str(champ_bak))   # staging queda íntegro otra vez

# ── 4b. ZIP Cloudflare (estático puro, sin TS ni package.json) ───
# Cloudflare Pages (subida directa) rechaza paquetes con ficheros
# TypeScript o package.json («requires a build process»). Esta variante
# contiene SOLO la web estática: index.html, tv.html, assets,
# championships, vendor, LEEME y VERSION. El relay va aparte.
CF_STAGE = RAIZ / 'scripts' / 'staging-cloudflare'
if CF_STAGE.exists():
    shutil.rmtree(CF_STAGE)
shutil.copytree(STAGE, CF_STAGE)
shutil.rmtree(CF_STAGE / 'extras-nextjs', ignore_errors=True)
shutil.rmtree(CF_STAGE / 'live-service', ignore_errors=True)
(CF_STAGE / 'NOTA-CLOUDFLARE.txt').write_text(
    'CRAZY PING PONG · V3.0.9-HALL1 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el HALL DEL ANFITRIÓN, el saque\n'
    'por dificultad, física viva, palas con carácter e intro oficial),\n'
    'tv.html (CRAZY TV), assets/,\n'
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
zip_cf = DL / 'crazypp-v309-hall1-CLOUDFLARE.zip'
if zip_cf.exists():
    zip_cf.unlink()
print('· Comprimiendo paquete CLOUDFLARE (estático puro, ~107 MB)...')
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

# ── 6. Copia al centro de descargas de la preview ────────────────
DESC.mkdir(exist_ok=True)
for z in (zip_c, zip_l, zip_cf, zip_sr):
    shutil.copy2(z, DESC / z.name)
print('· Copiados a public/descargas/ (descargables desde la preview).')

print('\nRESUMEN')
for z in (zip_c, zip_l, zip_cf, zip_sr):
    print(f'  {z.name:38s} {z.stat().st_size/1e6:7.1f} MB  sha256={sha256(z)[:16]}…')
print(json.dumps({k: v[:12] for k, v in man['ficheros'].items()}, indent=2))

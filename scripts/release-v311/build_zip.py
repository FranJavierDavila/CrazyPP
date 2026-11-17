#!/usr/bin/env python3
"""
CRAZY PING PONG · Ensamblador del paquete de despliegue V3.1.1-FEEL1.
Construye cuatro ZIP listos para subir:
  · crazypp-v311-feel1-COMPLETO.zip   (juego + intro oficial + TV + relay +
                                      campeonatos, ~107 MB)
  · crazypp-v311-feel1-ligera.zip     (lo mismo SIN campeonatos, ~11 MB)
  · crazypp-v311-feel1-CLOUDFLARE.zip (estático puro: SIN TS/package.json;
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
SRC = RAIZ / 'scripts' / 'release-v311'
STAGE = RAIZ / 'scripts' / 'staging-v311'
DL = RAIZ / 'download'
DESC = PUB / 'descargas'

VER = 'V3.1.1-FEEL1'
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

# v3.1.1: el index.html empaquetado debe ser la FEEL1 (anti empaquetar viejo)
idx = (STAGE / 'index.html').read_text(encoding='utf-8', errors='replace')
if "const VERSION = '3.1.1-FEEL1'" not in idx:
    sys.exit('FALLO: index.html no es la V3.1.1-FEEL1 (¿se copió un game.html viejo?)')
print('  index.html = V3.1.1-FEEL1 verificado dentro del staging')

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
    'base': 'V3.1.0-SRV2 (saque VR realista con asistencia limitada + hall hub)',
    'rama': 'main · FEEL1 (gracia del saque + rebote real + prompt B)',
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
    'Novedades de esta versión (frente a V3.1.0-SRV2) — los 3 ajustes\n'
    'de game-feel pedidos tras probar la SRV2 en el casco:\n'
    '  · GRACIA DEL SAQUE: la detección bola-pala sigue viva unos ms más\n'
    '    cuando la bola llega muy justa al borde de la hoja (SOLO en el\n'
    '    vuelo del saque). Lo que se ve que conecta, conecta.\n'
    '  · REBOTE REAL SOBRE PALA QUIETA: sin fuerza de rebote mínima — los\n'
    '    botes decaen hasta pararse; con swing real el suelo de salida\n'
    '    (2,3 m/s) queda intacto y el resto del juego no cambia.\n'
    '  · BOTÓN B = PROMPT «MENÚ PRINCIPAL ¿SI/No?» en cualquier estancia\n'
    '    que no sea el Hall: NO sigue en la escena, SI sale al HALL con el\n'
    '    menú principal en pantalla. En el Hall, B abre/cierra el menú.\n'
    '  · Conserva TODO: saque VR realista + hall hub (SRV2), saque real +\n'
    '    zonas fieles (TRN1), PRO CIRCUITO (PLAY1), intro oficial (SRV1),\n'
    '    física viva + palas (FIS1) y CRAZY TV en directo.\n\n'
    'Hashes SHA256 (verificación de integridad):\n' +
    ''.join(f'  {k:28s} {v}\n' for k, v in man['ficheros'].items()),
    encoding='utf-8')

# ── 3. ZIP completo ──────────────────────────────────────────────
DL.mkdir(exist_ok=True)
zip_c = DL / 'crazypp-v311-feel1-COMPLETO.zip'
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
zip_l = DL / 'crazypp-v311-feel1-ligera.zip'
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
    'CRAZY PING PONG · V3.1.1-FEEL1 · PAQUETE CLOUDFLARE\n'
    '==================================================\n\n'
    'Este paquete es la web ESTÁTICA pura, preparada para la subida\n'
    'directa de Cloudflare Pages (arrastrar y soltar), sin wrangler.\n\n'
    'Contenido: index.html (el juego con el GAME-FEEL V3.1.1 — gracia del\n'
    'saque, rebote real sobre pala quieta y prompt B al Menú Principal —,\n'
    'el HALL DEL ANFITRIÓN, el saque VR realista, física viva, palas con\n'
    'carácter e intro oficial), tv.html (CRAZY TV), assets/,\n'
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
zip_cf = DL / 'crazypp-v311-feel1-CLOUDFLARE.zip'
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

# ── 7. Retirada de ZIPs de versiones anteriores (hub limpio) ─────
for viejo in list(DESC.glob('crazypp-v30*.zip')) + list(DESC.glob('crazypp-v31*-srv2*.zip')):
    viejo.unlink()
    print(f'  retirado del hub: {viejo.name}')
for viejo in list(DL.glob('crazypp-v30*.zip')) + list(DL.glob('crazypp-v31*-srv2*.zip')):
    viejo.unlink()
    print(f'  retirado de download/: {viejo.name}')

print('\nRESUMEN')
for z in (zip_c, zip_l, zip_cf, zip_sr):
    print(f'  {z.name:38s} {z.stat().st_size/1e6:7.1f} MB  sha256={sha256(z)[:16]}…')
print(json.dumps({k: v[:12] for k, v in man['ficheros'].items()}, indent=2))

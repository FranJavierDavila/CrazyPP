#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.140 — línea sellada completa:
  1) zip oficial crazypp-v2140.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.140.txt
  3) docs a V2.140 (guía con párrafo nuevo + manual: HTML + PDF vía print_docs)
  4) editor a V2.140 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.140) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.139)
  8) page.tsx de /descargas a V2.140
  9) game/ espejo sincronizado
 10) verificación de serving vivo (servidor dev: public/ se sirve de disco
     por petición — sin reinicio)
"""
import hashlib
import os
import shutil
import subprocess
import time

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.140'
VX = 'V2.140'
VN = '2140'
PREV = '2.139'
VPREV = 'V2.139'
PN = '2139'
STAGE = f'{BASE}/scripts/stage_v{V}'

def sh(cmd, **kw):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-1500:])
        print(r.stderr[-1500:])
        raise SystemExit(f'FALLO: {cmd}')
    return r.stdout

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

# ---------------------------------------------------------------- 1) ZIP
print('== 1) ZIP oficial ==')
sh(f'rm -rf {STAGE} && mkdir -p {STAGE}')
sh(f'cp {PUB}/game.html {STAGE}/index.html')
sh(f'mkdir -p {STAGE}/assets && cp {PUB}/championships/estacion_orbital/assets/intro.mp4 {STAGE}/assets/intro.mp4 2>/dev/null || true')
sh(f'cp -r {PUB}/championships {STAGE}/championships')
sh(f'cd {STAGE} && rm -f {DL}/crazypp-v{VN}.zip && zip -X -9 -r -q {DL}/crazypp-v{VN}.zip index.html assets championships')
nfiles = sh(f'unzip -l {DL}/crazypp-v{VN}.zip | tail -1').strip()
sh(f'unzip -t {DL}/crazypp-v{VN}.zip > /dev/null && echo OK')
zv = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -o \"VERSION = '[^']*'\" | head -1" % (DL, VN)).strip()
zmega = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'mega_salida_dg:'" % (DL, VN)).strip()
zmegak = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c \"cargamento de oro a buen recaudo\"" % (DL, VN)).strip()
zmegae = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c \"the gold shipment is safe and sound\"" % (DL, VN)).strip()
zskin = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'NORMAS_SKIN'" % (DL, VN)).strip()
zv28 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv47 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv20 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zzona = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'zonaZ: -1.6' || true" % (DL, VN)).strip()
zpila = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'layer \\* hL' || true" % (DL, VN)).strip()
zsuelo = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c \"room/vagon/suelo.jpg\" || true" % (DL, VN)).strip()
zmega_mod = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c \"tren_mega_salida\" || true" % (DL, VN)).strip()
zbandaY = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'bandaY' || true" % (DL, VN)).strip()
ztx = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'tx: 453' || true" % (DL, VN)).strip()
ztx137 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'tx: 456' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv, '· mega_salida_dg:', zmega, '· plan oro es:', zmegak,
      '· plan oro en:', zmegae, '· NORMAS_SKIN:', zskin,
      '· manifest magia:', zv28, '· oeste:', zv47, '· locura:', zv20,
      '· zonaZ:', zzona, '· pila:', zpila, '· suelo.jpg:', zsuelo,
      '· tren_mega:', zmega_mod, '· bandaY:', zbandaY, '· tx453:', ztx, '· tx456:', ztx137)
assert zv == "VERSION = '2.140.0'", 'VERSION del zip incorrecta'
assert int(zmega) == 2, 'el átomo mega_salida_dg no está en los DOS bancos'
assert int(zmegak) >= 1 and int(zmegae) >= 1, 'planes VOICE_FULL del oro ausentes'
assert int(zskin) >= 3, 'carteles ausentes'
assert zv28 == '28', 'manifest magia no es v28'
assert zv47 == '47', 'manifest oeste no es v47'
assert zv20 == '20', 'manifest locura no es v20'
assert int(zzona) >= 1, 'fix zonaZ ausente'
assert int(zpila) >= 1, 'pila en el suelo ausente'
assert int(zsuelo) >= 1, 'suelo.jpg ausente'
assert int(zmega_mod) >= 2, 'megafonía del módulo ausente'
assert int(zbandaY) >= 2 and int(ztx) >= 1 and int(ztx137) >= 1, 'regresión histórica'
import zipfile
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    for nombre, ruta in (('mapa.webp (locura)', 'championships/locura/assets/mapa.webp'),
                         ('suelo.jpg (vagón)', 'championships/oeste/assets/room/vagon/suelo.jpg'),
                         ('recompensa.png', 'championships/oeste/assets/recompensa.png'),
                         ('forajido_robo.png', 'championships/oeste/assets/forajido_robo.png'),
                         ('risas_forajido.mp3', 'championships/oeste/assets/risas_forajido.mp3')):
        _h = hashlib.sha256(z.read(ruta)).hexdigest()
        assert _h == sha(f'{PUB}/{ruta}'), f'{nombre} del zip alterado'
print('    5 assets del zip = disco (sha256 OK)')

# ---------------------------------------------------------------- 2) RELEASE
print('== 2) RELEASE ==')
nloc = sh(f'find {STAGE}/championships/locura -type f | wc -l').strip()
nmag = sh(f'find {STAGE}/championships/magia -type f | wc -l').strip()
noes = sh(f'find {STAGE}/championships/oeste -type f | wc -l').strip()
neo = sh(f'find {STAGE}/championships/estacion_orbital -type f | wc -l').strip()
zsize = os.path.getsize(f'{DL}/crazypp-v{VN}.zip')
usize = int(sh(f'unzip -l {DL}/crazypp-v{VN}.zip | tail -1').split()[0].replace('.', ''))
nfiles_n = int(nfiles.split()[0])
rel = f"""================================================================
 CRAZY PING PONG — RELEASE OFICIAL {VX}
 Meta Quest 3 · WebXR · 2026-10-14
================================================================

IDENTIDAD
  Versión visible : {VX}
  VERSION interna : '{V}.0' (index.html)
  Módulo locura   : manifest version 20 (módulo v20)
  Módulo magia    : manifest version 28 (módulo v28)
  Módulo oeste    : manifest version 47 (módulo v47)
  Módulo EO       : manifest version 5 (plantilla final · módulo v3.2)
  Paquete         : crazypp-v{VN}.zip
  Tamaño zip      : {zsize:,} bytes ({zsize / 1048576:.1f} MB)
  Sin comprimir   : {usize:,} bytes · {nfiles_n} ficheros (+ entradas de directorio)

CONTENIDO DEL PAQUETE
  index.html                          núcleo del juego (única build, {VX})
  assets/intro.mp4                    vídeo de intro (Estación Orbital)
  championships/championships.json    catálogo (descubrimiento dinámico)
  championships/championship.schema.json  contrato de campeonatos
  championships/locura/        ({nloc} f.)  módulo del Campeonato de la Locura (v20)
  championships/magia/         ({nmag} f.)  módulo del Taller del Mago (v28)
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v47)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  El dueño pide correcciones en la etapa 4 del Salvaje Oeste (el vagón)
  y una megafonía de estación con voz pregrabada.

  1) BOTES FANTASMA ELIMINADOS — «si la pelota bota en el campo enemigo
     cerca de la red viene devuelta al jugador como si rebotase contra
     algo invisible»: el bote arkanoi de la etapa tenía su frontera en
     z = -2,2 y dejaba 60 cm de MESA RIVAL dentro de la zona del
     jugador. Ahora la frontera es la RED (z = -1,6): el bote gestionado
     sólo vive en el campo del jugador y en campo enemigo la bola SIGUE
     SU TRAYECTORIA física (si muere botando, la recoge el vórtice).
  2) LINGOTES APILADOS EN EL SUELO — «mejor que se apilen a ambos lados
     del suelo visibles por la cámara… deben estar unos perfectamente
     encima de otros»: dos pilas SIMÉTRICAS en el suelo del vagón junto
     a la red (x ±1,10…±1,38 · z -1,00…-0,82), el lingote alterna
     izquierda/derecha y llena capas de 6 (2 columnas × 3 filas); al
     completar un plano se apila ENCIMA con la altura REAL del lingote
     (medida del prototipo GLB + 1,5 mm) y yaw 0 al aterrizar: pilas
     limpias y perfectamente alineadas — ya no sobre la mesa rival.
  3) SUELO DEL VAGÓN — la TARIMA del dueño (suelo.jpg 1296×1678, mapeo
     1:1 al plano 6,10×7,90; tablas transversales a la marcha): fuera la
     arena procedural de la v2.111.
  4) MEGAFONÍA DE ESTACIÓN — voz pregrabada del banco (misma receta
     Piper es_ES-davefx / en_US-lessac → OGG Opus 28k) por la vía
     announce → speakPlan (WebAudio VR-SAFE, con el chime del megáfono
     y ducking del ambiente): SALIDAS «Pasajeros al tren, partimos
     hacia…» [destino]; a los 30 s del final del trayecto «En menos de
     25 segundos llegaremos a…» [estación]; ARRIBO CON EL ORO «¡
     Cargamento de oro a buen recaudo!» + panel recompensa.png (pop
     elástico, se ve toda la parada); ARRIBO SIN ORO panel
     forajido_robo.png + LAS RISAS DEL FORAJIDO (risas_forajido.mp3,
     precargadas al entrar al vagón). 14 átomos nuevos (7 es + 7 en)
     con los NOMBRES de las estaciones (BRAVOS · DRY GULCH · PERDIDO)
     verificados por ASR; frases i18n es/en (tren_mega_*) y 14 entradas
     VOICE_FULL con la normalización exacta.

QA {VX} (scripts/qa_v{VN}.py — 71/71 VERDE):
  game.html servido = disco · VERSION '{V}.0' · 6 assets servidos = disco
  (index.js, manifest v47, suelo.jpg, recompensa.png, forajido_robo.png,
  risas_forajido.mp3) · 14 átomos mega_* en los dos bancos con base64 =
  OGG de disco byte a byte · OGG opus/mono sanos (1,99-3,68 s) · las 14
  normalizaciones de las frases del módulo → claves VOICE_FULL exactas ·
  RUNTIME del tren: bote en campo ENEMIGO no secuestrado (vel.z -0,46
  intacta) y bote en campo JUGADOR normalizado (vel.z +0,95 · ápice) ·
  pila: lados alternos, capas y = plano × altura exacta, 6 huecos por
  pila, 18 lingotes asentados en 2 capas PERFECTAMENTE alineados
  (fotos cenitales) · suelo del vagón vistiendo suelo.jpg (1296 px) ·
  megafonía: salidas/llegada a los 30 s/oro con spy de announce ·
  voicePlan 7/7 en es y en · paneles robo/recompensa con pop ·
  risas_forajido.mp3 decodifica (2,86 s) · 0 pageerrors en los 4
  campeonatos.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '{V}.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)
  Etapa 4 del Salvaje Oeste     → botes limpios, oro en el suelo,
                                  tarima nueva y estaciones con voz

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
ancla = '<p class="body-text">La <strong>V2.139</strong> añade la <strong>bienvenida'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> pule la etapa 4 del Salvaje Oeste '
           '(«ASALTO AL TREN»): desaparecen los <strong>botes fantasma</strong> junto a la red '
           '(el bote gestionado sólo actúa en tu campo), los <strong>lingotes se apilan en el '
           'suelo</strong> del vagón a ambos lados de la mesa en capas perfectamente alineadas, '
           'el suelo viste la <strong>tarima de madera</strong> del artista y las estaciones '
           'suenan por <strong>megafonía</strong>: salidas, llegadas a los 30 segundos y el '
           'veredicto del oro con recompensa o las risas del forajido.</p>')
if f'La <strong>{VX}</strong> pule la etapa 4' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla del párrafo V2.139 no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    print('    párrafo V2.140 insertado en la guía')
s = s.replace(VPREV, VX)
s = s.replace(f'La <strong>{VX}</strong> añade la <strong>bienvenida',
              f'La <strong>{VPREV}</strong> añade la <strong>bienvenida', 1)
open(gp, 'w', encoding='utf-8').write(s)
print('    metas de la guía a', VX, '· refs', VX, ':', s.count(VX))
p = f'{DL}/manual-editor-campeonatos.html'
t = open(p, encoding='utf-8').read()
t = t.replace(VPREV, VX)
open(p, 'w', encoding='utf-8').write(t)
print('    refs actualizadas en manual', t.count(VX))
sh(f'python3 {BASE}/scripts/print_docs_v{VN}.py')

# ---------------------------------------------------------------- 4) EDITOR
print('== 4) EDITOR ==')
bp = f'{BASE}/scripts/editor_src/body.html'
s = open(bp, encoding='utf-8').read()
s = s.replace(VPREV, VX)
open(bp, 'w', encoding='utf-8').write(s)
sh(f'python3 {BASE}/scripts/build_editor.py')
sh(f'cd {DL}/editor-campeonatos && rm -f ../editor-campeonatos.zip && zip -X -9 -q -r ../editor-campeonatos.zip index.html')
print('    editor reconstruido a', VX)

# ---------------------------------------------------------------- 5) README (ANTES del SHA)
print('== 5) README ==')
rp = f'{DL}/README.md'
s = open(rp, encoding='utf-8').read()
nov = f"""## Novedades {VX} — El vagón a punto: botes limpios, oro en el suelo y megafonía

* Etapa 4 del Salvaje Oeste: los botes fantasma cerca de la red
  desaparecen (el bote gestionado sólo actúa en tu campo).
* Los lingotes se apilan en el SUELO del vagón, a ambos lados de la
  mesa, en capas perfectamente alineadas (nada de pilas sobre la mesa).
* El suelo del vagón viste la tarima de madera del artista (suelo.jpg).
* Megafonía de estación: «Pasajeros al tren, partimos hacia…», la
  llegada a los 30 segundos, el «¡Cargamento de oro a buen recaudo!»
  con recompensa.png o las risas del forajido con forajido_robo.png.

"""
if f'## Novedades {VX}' not in s:
    s = s.replace(f'## Novedades {VPREV} — Bienvenida hablada al entrar en VR',
                  nov + f'## Novedades {VPREV} — Bienvenida hablada al entrar en VR', 1)
    print('    bloque Novedades V2.140 insertado')
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
s = s.replace(f'## Novedades {VX} — Bienvenida hablada al entrar en VR',
              f'## Novedades {VPREV} — Bienvenida hablada al entrar en VR', 1)
open(rp, 'w', encoding='utf-8').write(s)
print('    README actualizado · refs', VX, ':', s.count(VX))

# ---------------------------------------------------------------- 6) SHA (README ya editado)
print('== 6) SHA256SUMS ==')
archivos = [
    f'crazypp-v{VN}.zip', f'RELEASE-{VX}.txt', 'README.md',
    'editor-campeonatos.zip', 'guia-campeonatos-crazy-pingpong.html',
    'guia-campeonatos-crazy-pingpong.pdf', 'manual-editor-campeonatos.html',
    'manual-editor-campeonatos.pdf',
]
lineas = []
for a in archivos:
    lineas.append(f'{sha(f"{DL}/{a}")}  {a}')
open(f'{DL}/SHA256SUMS.txt', 'w').write('\n'.join(lineas) + '\n')
r = sh(f'cd {DL} && sha256sum -c SHA256SUMS.txt 2>&1 | grep -c OK')
print('    sha256sum -c:', r.strip(), '/ 8 OK')

# ---------------------------------------------------------------- 7) DESCARGAS
print('== 7) public/descargas ==')
sh(f'rm -f {DES}/crazypp-v{PN}.zip {DES}/RELEASE-{VPREV}.txt')
for a in archivos:
    shutil.copy2(f'{DL}/{a}', f'{DES}/{a}')
shutil.copy2(f'{DL}/SHA256SUMS.txt', f'{DES}/SHA256SUMS.txt')
sobras = sh(f'ls {DES} | grep -c "{PREV}" || true').strip()
print('    refs', PREV, 'en descargas:', sobras)
assert sobras == '0', 'quedan ficheros de la versión anterior en descargas'

# ---------------------------------------------------------------- 8) page.tsx
print('== 8) page.tsx ==')
pp = f'{BASE}/src/app/descargas/page.tsx'
s = open(pp, encoding='utf-8').read()
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
open(pp, 'w', encoding='utf-8').write(s)
print('    refs', VX, 'en page.tsx:', s.count(VX))

# ---------------------------------------------------------------- 9) game/ espejo
print('== 9) game/ espejo ==')
sh(f'cp {PUB}/game.html {BASE}/game/index.html')
sh(f'cp -r {PUB}/championships/. {BASE}/game/championships/')
gm = sh(f"grep -o \"VERSION = '[^']*'\" {BASE}/game/index.html | head -1").strip()
print('   ', gm)

# ------------------------------------------------- 10) SERVING VIVO (dev server)
print('== 10) verificación de serving vivo ==')
import urllib.request
gv = urllib.request.urlopen('http://localhost:3000/game.html').read()
assert f"VERSION = '{V}.0'".encode() in gv, 'game.html servido no es 2.140.0'
assert gv.count(b'mega_salida_dg:') == 2, 'átomos mega ausentes en lo servido'
print(f"    game.html servido: {V}.0 OK · mega_salida_dg x2 OK")
for f_ in (f'descargas/crazypp-v{VN}.zip', f'descargas/RELEASE-{VX}.txt', 'descargas/SHA256SUMS.txt'):
    c = subprocess.run(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost:3000/{f_}',
                       shell=True, capture_output=True, text=True).stdout.strip()
    print(f'    {f_}: {c}')
    assert c == '200', f'{f_} no servido'
mz = urllib.request.urlopen('http://localhost:3000/championships/oeste/assets/room/vagon/suelo.jpg').read()
assert hashlib.sha256(mz).hexdigest() == sha(f'{PUB}/championships/oeste/assets/room/vagon/suelo.jpg'), \
    'suelo.jpg servido ≠ disco'
print('    oeste/assets/room/vagon/suelo.jpg servido = disco (sha256 OK)')
oj = urllib.request.urlopen('http://localhost:3000/championships/oeste/index.js').read()
assert b'zonaZ: -1.6' in oj and b'tren_mega_salida' in oj, 'index.js de oeste servido está VIEJO'
print('    index.js oeste servido: zonaZ + megafonía OK')

print('PIPELINE OK')

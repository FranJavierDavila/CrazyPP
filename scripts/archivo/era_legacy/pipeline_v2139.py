#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.139 — línea sellada completa:
  1) zip oficial crazypp-v2139.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.139.txt
  3) docs a V2.139 (guía con párrafo nuevo + manual: HTML + PDF vía print_docs)
  4) editor a V2.139 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.139) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.138)
  8) page.tsx de /descargas a V2.139
  9) game/ espejo sincronizado
 10) verificación de serving vivo (servidor dev: public/ se sirve de disco
     por petición — sin reinicio; lección de entorno, el standalone de
     producción no está activo en este runtime «next dev»)
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
V = '2.139'
VX = 'V2.139'
VN = '2139'
PREV = '2.138'
VPREV = 'V2.138'
PN = '2138'
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
zbien = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'bienvenida_modo:'" % (DL, VN)).strip()
zwm = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'welcome_menu'" % (DL, VN)).strip()
zfull = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c \"bienvenido a crazy ping pong escoge una modalidad de juego\"" % (DL, VN)).strip()
zskin = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'NORMAS_SKIN'" % (DL, VN)).strip()
zv28 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv46 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv20 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zbandaY = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'bandaY' || true" % (DL, VN)).strip()
ztrav = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'traverse((m)' || true" % (DL, VN)).strip()
ztx = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'tx: 453' || true" % (DL, VN)).strip()
ztx137 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'tx: 456' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv, '· bienvenida_modo:', zbien, '· welcome_menu:', zwm,
      '· VOICE_FULL es:', zfull, '· NORMAS_SKIN:', zskin,
      '· manifest magia:', zv28, '· oeste:', zv46, '· locura:', zv20,
      '· bandaY:', zbandaY, '· traverse:', ztrav, '· tx453:', ztx, '· tx456:', ztx137)
assert zv == "VERSION = '2.139.0'", 'VERSION del zip incorrecta'
assert int(zbien) == 2, 'los 2 átomos bienvenida_modo no están en el banco'
assert int(zwm) >= 4, 'welcome_menu ausente'
assert int(zfull) == 1, 'VOICE_FULL de la bienvenida ausente'
assert int(zskin) >= 3, 'carteles ausentes'
assert zv28 == '28', 'manifest magia no es v28'
assert zv46 == '46', 'manifest oeste no es v46'
assert zv20 == '20', 'manifest locura no es v20'
assert int(zbandaY) >= 2 and int(ztrav) >= 1, 'regresión del oeste'
assert int(ztx) >= 1 and int(ztx137) >= 1, 'regresión de tapas'
import zipfile
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    _h = hashlib.sha256(z.read('championships/locura/assets/mapa.webp')).hexdigest()
assert _h == sha(f'{PUB}/championships/locura/assets/mapa.webp'), 'mapa.webp del zip alterado'

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
  Módulo oeste    : manifest version 46 (módulo v46)
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
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v46)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  El dueño pide: «que al iniciar el juego en VR nos abriese con el
  siguiente mensaje de voz para la bienvenida (en castellano o inglés
  según el idioma)».

  1) BIENVENIDA HABLADA — al ENTRAR EN VR el megáfono dice «Bienvenido
     a Crazy Ping Pong, escoge una modalidad de juego» (EN: «Welcome
     to Crazy Ping Pong, choose a game mode») justo cuando el MENÚ
     PRINCIPAL abre y recibe al jugador (los 1,4 s de siempre, con su
     chime de torneo). El anuncio del modo elegido sigue sonando al
     escogerla o cambiarla.
  2) DOS ÁTOMOS NUEVOS en el banco de voz (bienvenida_modo es/en) con
     la receta Piper de siempre: es_ES-davefx-medium y en_US-lessac-
     medium → OGG Opus 28k mono (~14/10 KB). La marca se sintetiza en
     castellano con grafía fonética «Kreisi Ping Pong»: el modelo
     es-ES leyendo «Crazy» salía «cricket» (verificado por ASR sobre
     los dos candidatos; el modelo en-US la lee bien literal).
  3) RUTA 100 % VR-SAFE — la voz viaja por VOICE_FULL → speakPlan
     (WebAudio, la misma vía del megáfono, audible dentro de la sesión
     inmersiva donde speechSynthesis NO funciona) y el respaldo
     speechSynthesis de escritorio queda intacto. i18n: clave nueva
     welcome_menu en las dos mesas.

QA {VX} (scripts/qa_v{VN}.py — 23/23 VERDE):
  game.html servido = disco · VERSION '{V}.0' · welcome_menu EXACTO en
  las dos mesas · la normalización _normVoice del texto T() coincide
  con la clave VOICE_FULL en es y en · átomo bienvenida_modo en
  VOICE_B64 y VOICE_B64_EN con base64 = OGG de disco byte a byte ·
  OGG opus/mono de 3,68 s y 3,14 s · call site de onSessionStart
  cambiado (el condicional antiguo, fuera) · decodeAudioData REAL del
  navegador sobre los bytes SERVIDOS (es 3,67 s · en 3,14 s · mono) ·
  0 pageerrors en 2D y en los 4 campeonatos.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '{V}.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)
  Entrar en VR                  → chime + «Bienvenido a Crazy Ping Pong,
                                  escoge una modalidad de juego»

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
ancla = '<p class="body-text">La <strong>V2.138</strong> ajusta el <strong>túnel del tren'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> añade la <strong>bienvenida '
           'hablada</strong>: al entrar en VR, la voz del marcador dice «Bienvenido a Crazy '
           'Ping Pong, escoge una modalidad de juego» (o «Welcome to Crazy Ping Pong, choose '
           'a game mode» según el idioma) justo cuando se abre el menú principal — dos clips '
           'nuevos del banco de voz Piper, audibles dentro de la sesión inmersiva.</p>')
if f'La <strong>{VX}</strong> añade la <strong>bienvenida' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla del párrafo V2.138 no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    print('    párrafo V2.139 insertado en la guía')
s = s.replace(VPREV, VX)
s = s.replace(f'La <strong>{VX}</strong> ajusta el <strong>túnel del tren',
              f'La <strong>{VPREV}</strong> ajusta el <strong>túnel del tren', 1)
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
nov = f"""## Novedades {VX} — Bienvenida hablada al entrar en VR

* Al iniciar el juego en VR suena la voz del megáfono: «Bienvenido a
  Crazy Ping Pong, escoge una modalidad de juego» — y en inglés,
  «Welcome to Crazy Ping Pong, choose a game mode»— justo cuando se
  abre el menú principal.
* Dos clips nuevos en el banco de voz (castellano e inglés) generados
  con la misma voz Piper del marcador, audibles dentro de la sesión
  inmersiva.

"""
if f'## Novedades {VX}' not in s:  # idempotente (re-ejecuciones del pipeline)
    s = s.replace(f'## Novedades {VPREV} — El túnel a escala',
                  nov + f'## Novedades {VPREV} — El túnel a escala', 1)
    print('    bloque Novedades V2.139 insertado')
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
s = s.replace(f'## Novedades {VX} — El túnel a escala',
              f'## Novedades {VPREV} — El túnel a escala', 1)
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
shutil.copy2(f'{DL}/SHA256SUMS.txt', f'{DES}/SHA256SUMS.txt')  # (v2139: estaba served VIEJO desde V2.133)
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
assert f"VERSION = '{V}.0'".encode() in gv, 'game.html servido no es 2.139.0'
assert gv.count(b'bienvenida_modo:') == 2, 'átomos de bienvenida ausentes en lo servido'
print(f"    game.html servido: {V}.0 OK · bienvenida_modo x2 OK")
for f_ in (f'descargas/crazypp-v{VN}.zip', f'descargas/RELEASE-{VX}.txt', 'descargas/SHA256SUMS.txt'):
    c = subprocess.run(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost:3000/{f_}',
                       shell=True, capture_output=True, text=True).stdout.strip()
    print(f'    {f_}: {c}')
    assert c == '200', f'{f_} no servido'
mz = urllib.request.urlopen('http://localhost:3000/championships/locura/assets/mapa.webp').read()
assert hashlib.sha256(mz).hexdigest() == sha(f'{PUB}/championships/locura/assets/mapa.webp'), \
    'mapa.webp servido ≠ disco'
print('    locura/assets/mapa.webp servido = disco (sha256 OK)')
ij = urllib.request.urlopen('http://localhost:3000/championships/locura/index.js').read()
assert b'tx: 453' in ij, 'index.js de locura servido está VIEJO'
oj = urllib.request.urlopen('http://localhost:3000/championships/oeste/index.js').read()
assert b'bandaY' in oj, 'index.js de oeste servido está VIEJO'
print('    index.js locura/oeste servidos: OK')

print('PIPELINE OK')

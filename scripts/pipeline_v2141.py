#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.141 — línea sellada completa:
  1) zip oficial crazypp-v2141.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.141.txt
  3) docs a V2.141 (guía con párrafo nuevo + manual: HTML + PDF vía print_docs)
  4) editor a V2.141 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.141) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.140)
  8) page.tsx de /descargas a V2.141
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
V = '2.141'
VX = 'V2.141'
VN = '2141'
PREV = '2.140'
VPREV = 'V2.140'
PN = '2140'
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
zgd = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'mega_salida_gd:'" % (DL, VN)).strip()
zsc = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'mega_salida_sc:'" % (DL, VN)).strip()
zplan = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'partimos hacia gold dust'" % (DL, VN)).strip()
zplane = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'departing towards gold dust'" % (DL, VN)).strip()
zskin = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'NORMAS_SKIN'" % (DL, VN)).strip()
zv28 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv48 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv20 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zcajon = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'cajonOro: {' || true" % (DL, VN)).strip()
znames = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c \"'GOLD DUST', 'SILVER CREEK'\" || true" % (DL, VN)).strip()
zzona = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'zonaZ: -1.6' || true" % (DL, VN)).strip()
zsuelo = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c \"room/vagon/suelo.jpg\" || true" % (DL, VN)).strip()
zmega_mod = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c \"tren_mega_salida\" || true" % (DL, VN)).strip()
zbandaY = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'bandaY' || true" % (DL, VN)).strip()
ztx = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'tx: 453' || true" % (DL, VN)).strip()
ztx137 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'tx: 456' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv, '· mega_salida_gd:', zgd, '· mega_salida_sc:', zsc,
      '· plan oro-gd es:', zplan, '· en:', zplane, '· NORMAS_SKIN:', zskin,
      '· manifest magia:', zv28, '· oeste:', zv48, '· locura:', zv20,
      '· cajonOro:', zcajon, '· nombres:', znames, '· zonaZ:', zzona,
      '· suelo.jpg:', zsuelo, '· tren_mega:', zmega_mod,
      '· bandaY:', zbandaY, '· tx453:', ztx, '· tx456:', ztx137)
assert zv == "VERSION = '2.141.0'", 'VERSION del zip incorrecta'
assert int(zgd) == 2 and int(zsc) == 2, 'átomos gd/sc ausentes en los DOS bancos'
assert int(zplan) >= 1 and int(zplane) >= 1, 'planes VOICE_FULL de GOLD DUST ausentes'
assert int(zskin) >= 3, 'carteles ausentes'
assert zv28 == '28', 'manifest magia no es v28'
assert zv48 == '48', 'manifest oeste no es v48'
assert zv20 == '20', 'manifest locura no es v20'
assert int(zcajon) >= 1, 'config cajonOro ausente'
assert int(znames) == 1, 'stationNames nuevos ausentes'
assert int(zzona) >= 1, 'regresión zonaZ'
assert int(zsuelo) >= 1, 'regresión suelo.jpg'
assert int(zmega_mod) >= 2, 'regresión megafonía del módulo'
assert int(zbandaY) >= 2 and int(ztx) >= 1 and int(ztx137) >= 1, 'regresión histórica'
import zipfile
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    for nombre, ruta in (
            ('mapa.webp (locura)', 'championships/locura/assets/mapa.webp'),
            ('suelo.jpg (vagón) = upload', 'championships/oeste/assets/room/vagon/suelo.jpg'),
            ('PARADA1.png = upload', 'championships/oeste/assets/PARADA1.png'),
            ('recompensa.png', 'championships/oeste/assets/recompensa.png'),
            ('forajido_robo.png', 'championships/oeste/assets/forajido_robo.png'),
            ('risas_forajido.mp3', 'championships/oeste/assets/risas_forajido.mp3')):
        _h = hashlib.sha256(z.read(ruta)).hexdigest()
        assert _h == sha(f'{PUB}/{ruta}'), f'{nombre} del zip alterado'
print('    6 assets del zip = disco (sha256 OK)')

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
  Módulo oeste    : manifest version 48 (módulo v48)
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
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v48)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  Ajustes del dueño sobre la etapa 4 del Salvaje Oeste (el vagón):
  el oro descansa sobre dos grandes cajones y las paradas tienen el
  nombre y el arte de sus carteles.

  1) LOS CAJONES DEL ORO — «los lingotes van a caer a ambos lados de
     la mesa pero cerca del centro de las ventanas, en el suelo, sobre
     dos grandes cajones de madera (podemos usar alguno de los que ya
     colocamos para destruir, los que no tienen el dibujo del
     candado)»: DOS cajones limpios del artista (cubo1/cubo2)
     ACHATADOS (el doble de anchos: huella 0,72 m · la mitad de altos:
     0,18 m) sobre el suelo del vagón, uno a cada lado de la mesa y
     cerca del CENTRO DE LAS VENTANAS laterales (z -1,38 izq · -1,59
     der, medidos sobre el arte; x ±1,35). En su cara superior se
     apilan los lingotes: rejilla 3×3 por cajón con capas EXACTAS
     (altura real del GLB + 1,5 mm — unos perfectamente encima de
     otros) y una PEQUEÑA VARIACIÓN de colocación (±7 mm · ±3 mm ·
     ±1,7°) para que no parezca tan perfecta — sin solaparse ni
     meterse unos dentro de otros: cada robo LIBERA su hueco y el
     siguiente lingote lo reutiliza.
  2) PARADAS CON NOMBRE Y ARTE PROPIO — «primera parada nombre Bravos,
     imagen parada1.png, segunda parada nombre GOLD DUST, imagen
     parada2.png, tercera parada nombre Silver Creek, imagen
     parada3.png. Estos son los nombres que deberá decir la voz en las
     llegadas y las salidas»: stationNames = BRAVOS (depósito de
     salida) · BRAVOS · GOLD DUST · SILVER CREEK, y PARADA1.png se
     actualiza con el arte nuevo del dueño (1024×512).
  3) MEGAFONÍA AMPLIADA — 4 átomos nuevos por idioma
     (mega_salida/llega_gd·sc, misma receta Piper es_ES-davefx /
     en_US-lessac → OGG Opus 28k, ES literal elegido por ASR,
     consistente con «Dry Gulch» de la v2.140) con sus 8 entradas
     VOICE_FULL; BRAVOS ya sonaba desde la v2.140. La normalización de
     los textos del módulo sigue coincidiendo EXACTA.
  4) SUELO DEL VAGÓN — room/vagon/suelo.jpg se actualiza con la TARIMA
     nueva del dueño (1296×1678, mismo mapeo 1:1 al plano 6,10×7,90).
  5) NORMAS Y AVISOS AL DÍA — la explicación de la etapa y el aviso de
     lingote reflejan el nuevo depósito («LINGOTE AL CAJÓN», «INGOT ON
     THE CRATE»).

QA {VX} (scripts/qa_v{VN}.py — 78/78 VERDE):
  game.html servido = disco · VERSION '{V}.0' · suelo.jpg y PARADA1.png
  servidas = upload del dueño (sha256) · manifest v48 · marcadores del
  módulo (cajonOro 0,72×0,18×0,36 · x 1,35 · z -1,38/-1,59 · pila por
  cajón · robo libera hueco · normas «GRANDES CAJONES») · 22 átomos
  mega_* (11 es + 11 en) con base64 = OGG de disco byte a byte y opus/
  mono sanos · las 14 normalizaciones (BRAVOS · GOLD DUST · SILVER
  CREEK × salida/llegada × es/en + oro) → claves VOICE_FULL exactas ·
  RUNTIME: 2 cajones 0,72×0,18×0,36 en (±1,35 · z -1,38/-1,59) con
  cubo1/cubo2, fuera de la mesa · 20 lingotes → 10+10: 9 huecos
  DISTINTOS por cajón, dos capas exactas (y=h / y=h+hL), jitter ≤
  ±7mm/±3mm/±1,7°, robo reutiliza SU hueco · suelo del vagón con la
  tarima nueva (1296 px) · megafonía: «partimos hacia BRAVOS» (parada
  1), «partimos hacia GOLD DUST» (parada 2), llegada a los 30 s y oro
  con panel · voicePlan 7/7 en es y en · PARADA1.png nueva (1024 px) ·
  fotos cenitales de los DOS cajones con sus pilas · 0 pageerrors en
  los 4 campeonatos.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '{V}.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)
  Etapa 4 del Salvaje Oeste     → oro sobre los dos grandes cajones
                                  junto a las ventanas · paradas
                                  Bravos / Gold Dust / Silver Creek
                                  con voz en llegadas y salidas

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
ancla = '<p class="body-text">La <strong>V2.140</strong> pule la etapa 4'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> ajusta la etapa 4 del Salvaje Oeste: '
           'los <strong>lingotes se apilan sobre dos grandes cajones de madera</strong> '
           '(achatados, sin candado) junto al centro de las ventanas del vagón, en capas '
           'exactas con una pequeña variación natural; las <strong>paradas lucen nombre y '
           'arte propios</strong> — Bravos, Gold Dust y Silver Creek — y la megafonía los '
           'dice en llegadas y salidas; el suelo del vagón estrena la tarima del artista.</p>')
if f'La <strong>{VX}</strong> ajusta la etapa 4' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla del párrafo V2.140 no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    print('    párrafo V2.141 insertado en la guía')
s = s.replace(VPREV, VX)
s = s.replace(f'La <strong>{VX}</strong> pule la etapa 4',
              f'La <strong>{VPREV}</strong> pule la etapa 4', 1)
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
nov = f"""## Novedades {VX} — Los cajones del oro y las paradas con nombre

* Los lingotes se apilan sobre DOS GRANDES CAJONES de madera
  (achatados, los limpios sin candado) junto al centro de las ventanas
  del vagón, uno a cada lado de la mesa.
* Capas exactas unos sobre otros, con una pequeña variación de
  colocación para que no parezca tan perfecta — y si el forajido roba
  uno, su hueco queda libre y se reutiliza.
* Paradas con nombre y arte propios: Bravos (parada1.png nueva), Gold
  Dust y Silver Creek — la megafonía los dice en llegadas y salidas.
* El suelo del vagón estrena la tarima del artista (suelo.jpg).

"""
if f'## Novedades {VX}' not in s:
    s = s.replace(f'## Novedades {VPREV} — El vagón a punto',
                  nov + f'## Novedades {VPREV} — El vagón a punto', 1)
    print('    bloque Novedades V2.141 insertado')
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
s = s.replace(f'## Novedades {VX} — El vagón a punto',
              f'## Novedades {VPREV} — El vagón a punto', 1)
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
assert f"VERSION = '{V}.0'".encode() in gv, 'game.html servido no es 2.141.0'
assert gv.count(b'mega_salida_gd:') == 2, 'átomos gd ausentes en lo servido'
print(f"    game.html servido: {V}.0 OK · mega_salida_gd x2 OK")
for f_ in (f'descargas/crazypp-v{VN}.zip', f'descargas/RELEASE-{VX}.txt', 'descargas/SHA256SUMS.txt'):
    c = subprocess.run(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost:3000/{f_}',
                       shell=True, capture_output=True, text=True).stdout.strip()
    print(f'    {f_}: {c}')
    assert c == '200', f'{f_} no servido'
for ruta in ('championships/oeste/assets/room/vagon/suelo.jpg',
             'championships/oeste/assets/PARADA1.png'):
    mz = urllib.request.urlopen(f'http://localhost:3000/{ruta}').read()
    assert hashlib.sha256(mz).hexdigest() == sha(f'{PUB}/{ruta}'), f'{ruta} servido ≠ disco'
    print(f'    {ruta} servido = disco (sha256 OK)')
oj = urllib.request.urlopen('http://localhost:3000/championships/oeste/index.js').read()
assert b'cajonOro: {' in oj and b"'GOLD DUST', 'SILVER CREEK'" in oj, \
    'index.js de oeste servido está VIEJO'
print('    index.js oeste servido: cajonOro + nombres nuevos OK')

print('PIPELINE OK')

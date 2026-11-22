#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.136 — línea sellada completa:
  1) zip oficial crazypp-v2136.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.136.txt
  3) docs a V2.136 (guía + manual: HTML + PDF vía print_docs)
  4) editor a V2.136 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.136) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.135)
  8) page.tsx de /descargas a V2.136
  9) game/ espejo sincronizado
"""
import hashlib
import os
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.136'
VX = 'V2.136'
VN = '2136'
PREV = '2.135'
VPREV = 'V2.135'
PN = '2135'
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
zv = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -o \"VERSION = '[^']*'\" | head -1" % (DL, VN))
zskin = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'NORMAS_SKIN'" % (DL, VN)).strip()
zn1 = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'normas_clown.png'" % (DL, VN)).strip()
zn2 = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'normas_wizard.png'" % (DL, VN)).strip()
zn3 = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'normas_forajido.png'" % (DL, VN)).strip()
zv45 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zmapa = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'oeste/assets/mapa.webp'" % (DL, VN)).strip()
zincl = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'incl:' || true" % (DL, VN)).strip()
ztrav = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'traverse((m)' || true" % (DL, VN)).strip()
zbh = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'bh: 1.2' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· NORMAS_SKIN:', zskin,
      '· normas_clown/wizard/forajido:', zn1, zn2, zn3,
      '· oeste manifest:', zv45, '· mapa.webp:', zmapa,
      '· incl: (0 esperado):', zincl, '· traverse:', ztrav, '· bh 1.2:', zbh)
assert zv.strip() == "VERSION = '2.136.0'", 'VERSION del zip incorrecta'
assert int(zskin) >= 3 and zn1 == '1' and zn2 == '1' and zn3 == '1', 'carteles ausentes'
assert zv45 == '45', 'manifest oeste no es v45'
assert zmapa == '1', 'mapa.webp no está en el zip'
assert int(zincl) == 0, 'la inclinación v2.134 sigue en el módulo'
assert int(ztrav) >= 1 and int(zbh) >= 1, 'marcadores del fix ausentes'
import zipfile, io as _io
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    _h = hashlib.sha256(z.read('championships/oeste/assets/mapa.webp')).hexdigest()
assert _h == sha(f'{PUB}/championships/oeste/assets/mapa.webp'), \
    'el mapa.webp del zip NO es el arte nuevo'

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
  Módulo locura   : manifest version 19 (módulo v19)
  Módulo magia    : manifest version 27
  Módulo oeste    : manifest version 45 (módulo v45)
  Módulo EO       : manifest version 5 (plantilla final · módulo v3.2)
  Paquete         : crazypp-v{VN}.zip
  Tamaño zip      : {zsize:,} bytes ({zsize / 1048576:.1f} MB)
  Sin comprimir   : {usize:,} bytes · {nfiles_n} ficheros (+ entradas de directorio)

CONTENIDO DEL PAQUETE
  index.html                          núcleo del juego (única build, {VX})
  assets/intro.mp4                    vídeo de intro (Estación Orbital)
  championships/championships.json    catálogo (descubrimiento dinámico)
  championships/championship.schema.json  contrato de campeonatos
  championships/locura/        ({nloc} f.)  módulo del Campeonato de la Locura (v19)
  championships/magia/         ({nmag} f.)  módulo del Taller del Mago (v27)
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v45)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  El dueño, tras probar el túnel con profundidad de la V2.134: «se han
  estropeado las imágenes de entrada y de salida que teníamos colocadas y
  espejadas; va a ser mejor dejarlas como antes, solo que sean más pequeñas
  para que parezca que están más lejos». Y reenvía el mapa de etapas
  (mapa.png) del Salvaje Oeste para reemplazarlo. Así queda:

  1) TÚNEL COMO ANTES — CAUSA RAÍZ: las bocas (tunelboca.png) habían pasado
     a vivir DENTRO de los subgrupos inclinados de la V2.134 y el reparto
     de la textura recorría sólo los hijos directos del grupo del túnel:
     ya no encontraba las bocas, que quedaban SIN arte (planos invisibles)
     y además TORCIDAS por la rotación de ±13,7°. FIX: las tres piezas
     (boca·banda·boca) vuelven a ser hijas directas y COPLANARES a x=3,55
     —sin rotación—, con el espejado de siempre (entrada normal, salida
     espejada en la pared izquierda) y el reparto de textura ahora usa
     traverse() — la textura llega aunque las bocas vuelvan a agruparse.
  2) BOCAS MÁS PEQUEÑAS, PORTAL LEJANO — las bocas bajan de 3,4 a 1,2 m,
     centradas en la ventana (y 1,8): caben ENTERAS en el hueco (que mide
     1,08-2,55 de alto) y se leen como un portal de túnel A LO LEJOS, tal
     y como pidió el dueño. La secuencia boca→banda→boca sigue cosida sin
     hueco (todo se deriva del tamaño de boca) y las fases por distancia
     quedan intactas.
  3) MAPA DE ETAPAS NUEVO — el mapa.png reenviado por el dueño (1699×926;
     el nodo 2 muestra el armero SAGEBRUSH y el nodo 4 el TREN con el oro)
     reemplaza al anterior. Los medallones del arte nuevo son más grandes
     (230-265 px) y los nodos 1/3/5 bajan 26/36/24 px: los cinco nodos
     quedan RE-MEDIDOS sobre el arte, la tapa de madera crece de 240×248 a
     284×292 para cubrirlos entera y el anillo dorado del nodo actual pasa
     de r 95 a r 110 para abrazar el borde dorado.

QA {VX} (ruta natural + verificación visual):
  el mapa.webp SERVIDO es byte a byte el mapa nuevo del dueño · textura de
  la sala a 1699 px · 4 tapas exactamente en los nodos re-medidos · tapa
  284×292 y anillo a escala 110/120 · túnel SIN subgrupos (6 mellas hijas
  directas), piezas coplanares a x=±3,55, bocas de 1,2 m a y=1,8 con la
  textura tunelboca APLICADA (512 px) y espejado v2.119 intacto · fotos 3D
  del mapa de la sala y de los dos portales (entrada normal y salida
  espejada) · smoke de los 4 campeonatos sin errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.136.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
for doc in ('guia-campeonatos-crazy-pingpong.html', 'manual-editor-campeonatos.html'):
    p = f'{DL}/{doc}'
    s = open(p, encoding='utf-8').read()
    s = s.replace(VPREV, VX)
    open(p, 'w', encoding='utf-8').write(s)
    print('    refs actualizadas en', doc, s.count(VX))
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
ancla = f'<p class="body-text">La <strong>{VX}</strong>'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> devuelve el <strong>túnel del tren '
           'a como estaba</strong>: la profundidad estrenada en la entrega anterior había dejado '
           'las <strong>bocas de entrada y salida sin su dibujo</strong> (vivían dentro de los '
           'subgrupos inclinados y el reparto de la textura ya no las encontraba) y además '
           'torcidas. Las tres piezas vuelven a ser <strong>coplanares y espejadas como siempre</strong> '
           'y las bocas se dibujan <strong>más pequeñas —1,2 m— para que parezca que están más '
           'lejos</strong>, cabiendo enteras en la ventana. El mismo pase reemplaza el '
           '<strong>mapa de etapas</strong> por el arte nuevo del dueño (nodos re-medidos, tapas '
           'agrandadas y anillo dorado al borde de los medallones).</p>')
if 'devuelve el <strong>túnel del tren' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla de la guía no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.136 insertado en la guía')
sh(f'python3 {BASE}/scripts/print_docs_v2126.py')

# ---------------------------------------------------------------- 4) EDITOR
print('== 4) EDITOR ==')
bp = f'{BASE}/scripts/editor_src/body.html'
s = open(bp, encoding='utf-8').read()
s = s.replace(VPREV, VX)
open(bp, 'w', encoding='utf-8').write(s)
sh(f'python3 {BASE}/scripts/build_editor.py')
sh(f'cd {DL}/editor-campeonatos && rm -f ../editor-campeonatos.zip && zip -X -9 -q -r ../editor-campeonatos.zip index.html')
print('    editor reconstruido a', VX)

# ---------------------------------------------------------------- 5) README (ANTES del SHA: lección V2.133)
print('== 5) README ==')
rp = f'{DL}/README.md'
s = open(rp, encoding='utf-8').read()
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
nov = f"""## Novedades {VX} — El túnel del Salvaje Oeste, como antes (y más lejano)

* **Bocas del túnel restauradas**: la profundidad de la entrega anterior
  había dejado las imágenes de entrada y salida sin dibujo y torcidas.
  Vuelven a estar colocadas y espejadas como siempre, y el reparto de la
  textura ya no puede perderlas (traverse).
* **Portal lejano**: las bocas se dibujan más pequeñas (1,2 m) y caben
  enteras en la ventana — parecen estar más lejos, tal y como se pidió.
* **Mapa de etapas nuevo**: el arte reenviado por el dueño (nodo 2
  SAGEBRUSH, nodo 4 TREN+ORO) con nodos re-medidos, tapas agrandadas y
  anillo dorado al borde de los medallones.

"""
s = s.replace('## Novedades V2.136 — Los carteles de las normas, con el arte del artista',
              nov + '## Novedades V2.136 — Los carteles de las normas, con el arte del artista', 1)
open(rp, 'w', encoding='utf-8').write(s)
print('    README actualizado')

# ---------------------------------------------------------------- 6) SHA (REHASH: README ya editado)
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
sobras = sh(f'ls {DES} | grep -c "{PREV}" || true').strip()
print('    refs', PREV, 'en descargas:', sobras)

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

print('PIPELINE OK')

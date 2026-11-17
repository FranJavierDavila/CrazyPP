#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.137 — línea sellada completa:
  1) zip oficial crazypp-v2137.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.137.txt
  3) docs a V2.137 (guía + manual: HTML + PDF vía print_docs) — con CORRECCIÓN
     de las etiquetas históricas que los replaces globales anteriores habían
     re-etiquetado todo a «V2.136» (carteles=V2.135, Clown=V2.133, etapa 4
     Oeste=V2.134, AX-9=V2.132, cableado EO=V2.131, intros=V2.130, plantilla=V2.129)
  4) editor a V2.137 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.137 + headers históricos corregidos)
     — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.136)
  8) page.tsx de /descargas a V2.137
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
V = '2.137'
VX = 'V2.137'
VN = '2137'
PREV = '2.136'
VPREV = 'V2.136'
PN = '2136'
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
zv28 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv45 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv19 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zmapa = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'magia/assets/mapa.webp'" % (DL, VN)).strip()
ztx = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'tx: 456' || true" % (DL, VN)).strip()
zv2137 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'v2.137' || true" % (DL, VN)).strip()
ztrav = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'traverse((m)' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· NORMAS_SKIN:', zskin,
      '· normas 3:', zn1, zn2, zn3,
      '· manifest magia:', zv28, '· oeste:', zv45, '· locura:', zv19,
      '· mapa.webp magia:', zmapa, '· tx: 456:', ztx, '· v2.137:', zv2137,
      '· oeste traverse:', ztrav)
assert zv.strip() == "VERSION = '2.137.0'", 'VERSION del zip incorrecta'
assert int(zskin) >= 3 and zn1 == '1' and zn2 == '1' and zn3 == '1', 'carteles ausentes'
assert zv28 == '28', 'manifest magia no es v28'
assert zv45 == '45' and zv19 == '19', 'manifests de oeste/locura cambiados'
assert zmapa == '1', 'mapa.webp de magia no está en el zip'
assert int(ztx) >= 1 and int(zv2137) >= 1, 'marcadores v2.137 ausentes en magia'
assert int(ztrav) >= 1, 'regresión: traverse del oeste ausente'
import zipfile
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    _h = hashlib.sha256(z.read('championships/magia/assets/mapa.webp')).hexdigest()
assert _h == sha(f'{PUB}/championships/magia/assets/mapa.webp'), \
    'el mapa.webp del zip NO es el arte nuevo del wizard'

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
  Módulo magia    : manifest version 28 (módulo v28)
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
  championships/magia/         ({nmag} f.)  módulo del Taller del Mago (v28)
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v45)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  El dueño reenvía el mapa de etapas del Taller del Mago (el Mapa.png del
  wizard, 1380×752 — el MISMO lienzo del arte anterior) para reemplazarlo:

  1) MAPA NUEVO — el arte estrena nodos NUMERADOS con espiral azul (1/3/5
     magos, 2/4 orbes; el 5 dentro de la burbuja, sin anillo dorado) y los
     centros se mueven algo. El mapa.webp se reemplaza y los cinco nodos
     quedan RE-MEDIDOS sobre el arte nuevo (Hough + bbox dorado + perfil
     radial): 229,258 · 456,508 · 701,253 · 966,506 · 1232,162.
  2) ANILLO AL BORDE — el radio del anillo dorado del nodo actual se
     deriva de la banda del arte (r = 120 × banda/107,5): 126/131/122/
     132/126; el anillo abraza el borde dorado de cada medallón.
  3) TAPAS A MEDIDA — las tapas «?» estrenan centro y escala PROPIOS por
     nodo (tx/ty/ts): cubren el anillo Y la espiral numerada ENTERAS (un
     dígito cortado por el medallón se lee roto). La mecánica de tapas y
     anillo no cambia; cero cambios de gameplay.

QA {VX} (ruta natural + verificación visual):
  el mapa.webp SERVIDO es byte a byte el arte nuevo · 1380×752 · nodesPx
  re-medidos en el módulo vivo · 4 tapas centradas en tx/ty con escala ts
  exacta y visibles en la etapa 1 · anillo del nodo 1 a escala 126/120 ·
  cobertura de tapas simulada sobre el arte (anillo exterior + dígito
  DENTRO del medallón en los 4 nodos) · fotos 3D reales del mapa (completo
  y primeros planos de los nodos 2 y 5) · smoke de los 4 campeonatos sin
  errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.137.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
# --- guía: corrección de etiquetas históricas (defecto heredado de los
#     replaces globales: todo decía «La V2.136») ---
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
HIST = [
    ('La <strong>V2.136</strong> viste los <strong>carteles de las normas</strong>',
     'La <strong>V2.135</strong> viste los <strong>carteles de las normas</strong>'),
    ('La <strong>V2.136</strong> hace <strong>visible la bola doble del Clown</strong>',
     'La <strong>V2.133</strong> hace <strong>visible la bola doble del Clown</strong>'),
    ('La <strong>V2.136</strong> pule la etapa 4 del Salvaje Oeste',
     'La <strong>V2.134</strong> pule la etapa 4 del Salvaje Oeste'),
    ('La <strong>V2.136</strong> hace que en <strong>Estación Orbital</strong> los superpoderes',
     'La <strong>V2.132</strong> hace que en <strong>Estación Orbital</strong> los superpoderes'),
    ('La <strong>V2.136</strong> arregla el cableado del campeonato plantilla',
     'La <strong>V2.131</strong> arregla el cableado del campeonato plantilla'),
    ('La <strong>V2.136</strong> pule la experiencia de entrada',
     'La <strong>V2.130</strong> pule la experiencia de entrada'),
    ('Desde la <strong>V2.136</strong> esa plantilla es una demostración completa',
     'Desde la <strong>V2.129</strong> esa plantilla es una demostración completa'),
]
for a, b in HIST:
    if a in s:
        s = s.replace(a, b, 1)
print('    etiquetas históricas corregidas (idempotente)')
# --- párrafo nuevo V2.137 delante del párrafo del túnel (V2.136) ---
ancla = '<p class="body-text">La <strong>V2.136</strong> devuelve el <strong>túnel del tren'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> estrena el <strong>mapa de etapas '
           'nuevo del Taller del Mago</strong>: el arte del dueño llega con los nodos '
           '<strong>numerados con espirales azules</strong> (los magos en 1/3/5, los orbes en '
           '2/4 y el jefe final dentro de su burbuja) y con los centros algo movidos. Los '
           'cinco nodos quedan <strong>re-medidos sobre el arte</strong>, el anillo dorado '
           '<strong>abraza el borde</strong> de cada medallón y las tapas «?» se dibujan a '
           'medida —centro y escala propios— para cubrir el anillo <strong>y el número '
           'enteros</strong>: nada de dígitos cortados.</p>')
if '<strong>V2.137</strong> estrena el <strong>mapa de etapas' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla del túnel no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    print('    párrafo V2.137 insertado en la guía')
# --- metas a V2.137 (title, cover, span, footer) + restaurar el párrafo
#     histórico del túnel a V2.136 tras el replace global ---
s = s.replace(VPREV, VX)
s = s.replace(f'La <strong>{VX}</strong> devuelve el <strong>túnel del tren',
              'La <strong>V2.136</strong> devuelve el <strong>túnel del tren', 1)
open(gp, 'w', encoding='utf-8').write(s)
print('    metas de la guía a', VX, '· refs', VX, ':', s.count(VX))
# --- manual: solo metas, replace global seguro (la guía YA está tratada) ---
p = f'{DL}/manual-editor-campeonatos.html'
t = open(p, encoding='utf-8').read()
t = t.replace(VPREV, VX)
open(p, 'w', encoding='utf-8').write(t)
print('    refs actualizadas en manual', t.count(VX))
sh(f'python3 {BASE}/scripts/print_docs_v2137.py')

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
# headers históricos mal etiquetados por replaces globales anteriores
s = s.replace('## Novedades V2.136 — Los carteles de las normas, con el arte del artista',
              '## Novedades V2.135 — Los carteles de las normas, con el arte del artista', 1)
s = s.replace('## Novedades V2.136 — ESTACIÓN ORBITAL «PLANTILLA FINAL»',
              '## Novedades V2.129 — ESTACIÓN ORBITAL «PLANTILLA FINAL»', 1)
s = s.replace('## Novedades V2.136 — la entrada de los campeonatos, pulida',
              '## Novedades V2.130 — la entrada de los campeonatos, pulida', 1)
print('    headers históricos del README corregidos (3)')
nov = f"""## Novedades {VX} — El Taller del Mago estrena mapa

* **Mapa de etapas nuevo**: el arte del dueño (mismo lienzo) llega con los
  nodos numerados con espirales azules —magos en 1/3/5, orbes en 2/4 y el
  jefe final en su burbuja—.
* **Nodos re-medidos**: los cinco centros se midieron sobre el arte nuevo
  y el anillo dorado del nodo actual abraza el borde de cada medallón.
* **Tapas a medida**: cada «?» cubre el anillo y el número enteros
  (centro y escala propios por nodo) — nada de dígitos cortados.

"""
s = s.replace('## Novedades V2.136 — El túnel del Salvaje Oeste, como antes (y más lejano)',
              nov + '## Novedades V2.136 — El túnel del Salvaje Oeste, como antes (y más lejano)', 1)
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
# el header del túnel ES histórico V2.136: lo restauro tras el replace global
s = s.replace(f'## Novedades {VX} — El túnel del Salvaje Oeste, como antes (y más lejano)',
              '## Novedades V2.136 — El túnel del Salvaje Oeste, como antes (y más lejano)', 1)
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

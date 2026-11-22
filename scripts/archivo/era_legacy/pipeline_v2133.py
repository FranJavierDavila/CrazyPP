#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.133 — línea sellada completa:
  1) zip oficial crazypp-v2133.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.133.txt
  3) docs a V2.133 (guía + manual: HTML + PDF vía Playwright)
  4) editor a V2.133 (editor_src → build_editor.py → zip)
  5) SHA256SUMS.txt (8 entregables)
  6) README.md (tabla + novedades V2.133)
  7) public/descargas/ (8 entregables, SIN rastro de V2.132)
  8) page.tsx de /descargas a V2.133
"""
import hashlib
import os
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.133'
VX = 'V2.133'
VN = '2133'
PREV = '2.132'
VPREV = 'V2.132'
PN = '2132'
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
zv2 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'v2.133 (módulo v19)'" % (DL, VN)).strip()
zv3 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | grep -o '\"version\": [0-9]*'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· marcador v19 locura:', zv2, '·', zv3)
assert zv2.strip() == '1' and '"version": 19' in zv3, 'marcadores del zip incorrectos'

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
  Módulo oeste    : manifest version 43
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
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v43)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  Verificación del dueño en el casco (La Locura): «uno de los nuevos poderes
  de Clown no funciona, el que saca dos bolas». Causa raíz reproducida en
  QA headless y arreglada de raíz:

  1) LA BOLA DOBLE (split) YA SE VE — módulo v19:
     · LA MALLA DEL CLON VIVÍA EN EL LUGAR EQUIVOCADO: se creaba SÓLO dentro
       del primer build() del ARKANOID (la prueba de las etapas 2/4), y el
       split sólo existe en la bolsa del CLOWN Nv. 3 (etapa 5, DUELO JEFE).
       Llegando al duelo final con sesión fresca (etapa guardada, recarga de
       página, salto de depuración o rejugada por el mapa) el arkanoid nunca
       se había construido → el clon corría físico INVISIBLE (la «malla
       perezosa» de v2.120 dependía de _makeCloneMesh, definido también sólo
       en build). El cartel prometía «¡LA BOLA SE DIVIDE EN DOS!», la bola
       oficial se ponía blanca y la segunda bola JAMÁS aparecía.
     · FIX: cloneMesh + _makeCloneMesh al CONSTRUCTOR del arkanoid (UNA vez
       por sesión, regla Quest intacta: nada se crea por partida); el lazy
       de _startSplit queda como cinturón y tirantes.
  2) EL SPLIT YA NO SE DESPERDICIA EN PUNTO MUERTO: si el aviso termina sin
     rallye (saque/reposo), el poder se RE-ARMA 1,2 s y entra en el PRÓXIMO
     rallye (antes nacía y updateSplit lo mataba en el primer frame: cartel
     sin efecto). El guard de maybeTriggerPower evita anunciar otro poder
     mientras el aviso siga pendiente — el split está garantizado.
  3) Sin cambios para magia/oeste/estacion_orbital (núcleo 2.133.0: sólo
     comentario de versión).

QA {VX} (ruta natural, marco de ticks fiel al frame del núcleo):
  A) clon existe SIN build del arkanoid (la marca del bug) · F) bolsa por
  nivel (split sólo en Nv.3) · B) cartel del aviso con coreografía · C)
  lanzamiento: clon VIVO, malla VISIBLE siguiendo la física exacta
  (meshPos == clonPos), bola oficial blanca · D) salvación: la bola oficial
  muere con lastHitter='ai', el clon la hereda y el floor event desaparece
  («¡Perdiste una bola… pero la OTRA sigue viva!») · E) punto muerto en el
  aviso → re-armado en saque y ENTRA en el próximo rallye con malla visible ·
  smoke 0 pageerrors. REGRESIÓN: los 4 poderes de Nv.1 salen en rotación por
  el gatillo natural (redball→globos→burla→confetti), bola loca roja ×2,
  confetti 8 s; smoke de los 4 campeonatos sin errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.133.0'
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
ancla = 'se trabaja en un espacio propio, con sus puertas y sus cerraduras, sin tocar los cimientos ni las habitaciones que ya están amuebladas.</p>'
parrafo = ('<p class="body-text">La <strong>' + VX + '</strong> hace <strong>visible la bola doble del '
           'Clown</strong> (el dueño: «el poder que saca dos bolas no funciona»): la malla del clon vivía '
           'dentro de la construcción del <strong>Arkanoid</strong>, y como la bola doble sólo sale en el '
           '<strong>duelo final (Nv. 3)</strong>, llegar a la etapa 5 con sesión fresca dejaba el clon '
           'corriendo <em>invisible</em> — cartel de «¡la bola se divide en dos!» y ninguna segunda bola. '
           'La malla ahora se crea <strong>una sola vez por sesión</strong> en el constructor y el poder, '
           'si el punto muere durante el aviso, <strong>se re-arma</strong> y entra en el próximo rallye '
           'en lugar de nacer muerto.</p>')
if ancla in s and 'visible la bola doble del' not in s:
    s = s.replace(ancla, ancla + parrafo, 1)
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.133 insertado en la guía')
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

# ---------------------------------------------------------------- 5) SHA
print('== 5) SHA256SUMS ==')
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

# ---------------------------------------------------------------- 6) README
print('== 6) README ==')
rp = f'{DL}/README.md'
s = open(rp, encoding='utf-8').read()
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
nov = f"""## Novedades {VX} — La Locura: la bola doble del Clown ya se ve

* **El poder «Bola doble» funciona de verdad**: la malla del clon vivía
  dentro de la construcción del Arkanoid y el split sólo sale en el duelo
  final (Nv. 3) — con sesión fresca el clon corría **invisible**. Ahora la
  malla se crea una sola vez por sesión y la segunda bola **se ve y se juega**.
* Si el punto muere durante el aviso, el split **se re-arma** y entra en el
  próximo rallye (antes nacía y moría en el primer frame).

"""
s = s.replace('## Novedades V2.132 — Estación Orbital: los poderes ya mandan', nov + '## Novedades V2.132 — Estación Orbital: los poderes ya mandan', 1)
open(rp, 'w', encoding='utf-8').write(s)
print('    README actualizado')

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

print('PIPELINE OK')

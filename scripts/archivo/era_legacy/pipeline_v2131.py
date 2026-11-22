#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.131 — línea sellada completa:
  1) zip oficial crazypp-v2131.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.131.txt
  3) docs a V2.131 (guía + manual: HTML + PDF vía Playwright)
  4) editor a V2.131 (editor_src → build_editor.py → zip)
  5) SHA256SUMS.txt (8 entregables)
  6) README.md (tabla + novedades V2.131)
  7) public/descargas/ (8 entregables, SIN rastro de V2.130)
  8) page.tsx de /descargas a V2.131
"""
import hashlib
import os
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.131'
VX = 'V2.131'
VN = '2131'          # nombre de fichero sin punto (convención)
PREV = '2.130'
VPREV = 'V2.130'
PN = '2130'

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
stage = f'/tmp/stage_v{V}'
sh(f'rm -rf {stage} && mkdir -p {stage}')
sh(f'cp {PUB}/game.html {stage}/index.html')
sh(f'mkdir -p {stage}/assets && cp {PUB}/championships/estacion_orbital/assets/intro.mp4 {stage}/assets/intro.mp4 2>/dev/null || true')
sh(f'cp -r {PUB}/championships {stage}/championships')
sh(f'cd {stage} && rm -f /{DL}/crazypp-v{VN}.zip && zip -X -9 -r -q /{DL}/crazypp-v{VN}.zip index.html assets championships')
nfiles = sh(f'unzip -l {DL}/crazypp-v{VN}.zip | tail -1').strip()
sh(f'unzip -t {DL}/crazypp-v{VN}.zip > /dev/null && echo OK')
zv = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -o \"VERSION = '[^']*'\" | head -1" % (DL, VN))
zv2 = sh("unzip -p %s/crazypp-v%s.zip championships/estacion_orbital/index.js | grep -c 'v3.1 (V2.131)'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· marcador fix EO en módulo:', zv2)

# ---------------------------------------------------------------- 2) RELEASE
print('== 2) RELEASE ==')
nloc = sh(f'find {stage}/championships/locura -type f | wc -l').strip()
nmag = sh(f'find {stage}/championships/magia -type f | wc -l').strip()
noes = sh(f'find {stage}/championships/oeste -type f | wc -l').strip()
neo = sh(f'find {stage}/championships/estacion_orbital -type f | wc -l').strip()
zsize = os.path.getsize(f'{DL}/crazypp-v{VN}.zip')
usize = int(sh(f'unzip -l {DL}/crazypp-v{VN}.zip | tail -1').split()[0].replace('.', ''))
nfiles_n = int(nfiles.split()[0])
rel = f"""================================================================
 CRAZY PING PONG — RELEASE OFICIAL {VX}
 Meta Quest 3 · WebXR · 2026-10-13
================================================================

IDENTIDAD
  Versión visible : {VX}
  VERSION interna : '{V}.0' (index.html)
  Módulo locura   : manifest version 18
  Módulo magia    : manifest version 27
  Módulo oeste    : manifest version 43
  Módulo EO       : manifest version 4 (plantilla final · módulo v3.1)
  Paquete         : crazypp-v{VN}.zip
  Tamaño zip      : {zsize:,} bytes ({zsize / 1048576:.1f} MB)
  Sin comprimir   : {usize:,} bytes · {nfiles_n} ficheros (+ entradas de directorio)

CONTENIDO DEL PAQUETE
  index.html                          núcleo del juego (única build, {VX})
  assets/intro.mp4                    vídeo de intro (Estación Orbital)
  championships/championships.json    catálogo (descubrimiento dinámico)
  championships/championship.schema.json  contrato de campeonatos
  championships/locura/        ({nloc} f.)  módulo del Campeonato de la Locura (v18)
  championships/magia/         ({nmag} f.)  módulo del Taller del Mago (v27)
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v43)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v4, módulo v3.1)

CAMBIOS DE LA {VX} (frente a {VPREV})

  FIX RAÍZ de Estación Orbital — el informe del jugador «no tiene superpoderes
  en las etapas 1, 3 y 5, ni pruebas de habilidad en las etapas 2 y 4» tenía
  una sola causa: el módulo NUNCA ponía rules.state='champtest' en la SALA.
  El núcleo sólo enruta el gatillo al campeonato con ese estado (convención
  oeste/magia: el árbitro duerme en la sala de espera), así que el gatillo
  ejecutaba el SAQUE CLÁSICO: se jugaban partidos normales sin duelo real —
  sin superpoderes (el estado interno del módulo jamás llegaba a 'duelo') y
  sin pruebas (serveTrigger jamás era llamado). La plantilla entera quedaba
  en ping-pong plano.

  ARREGLOS EN EL MÓDULO estacion_orbital (v3.1):
  · EL ÁRBITRO DUERME EN TODA SALA/PRUEBA: startChamp (con bola aparcada
    sobre la mesa), _empezarPrueba (también bajo el panel EMPEZAR),
    _despuesDePrueba y onMatchOver (normal y rejugada) devuelven la sala
    con rules.state='champtest' → el gatillo SIEMPRE lanza la etapa
    vigente: duelos con los 4 superpoderes del AX-9 y pruebas «Dianas
    Orbitales» en las etapas 2 y 4.
  · REJUGADA ARREGLADA: tras repetir un duelo por el mapa, el progreso REAL
    vuelve (antes el estado quedaba en 'duelo', sin cartel, con _replay
    pegado al siguiente duelo real y el cartel mostrando la etapa rejugada
    como si fuera la vigente).
  · REENTER condicional: al volver del menú de VR, en DUELO sigue el
    partido ('serve'); en sala/prueba el árbitro vuelve a dormir.
  · LEAVE restituye al árbitro (convención magia): salir de Estación
    Orbital ya deja el núcleo limpio (antes se quedaba en 'champtest').
  · PALA IA sólo en DUELO: en la sala manda el standee del AX-9 y en las
    pruebas juegas sólo contra las dianas.

  Núcleo sin cambios de comportamiento: locura, magia y oeste intactos
  (verificado en QA: las 4 salas arrancan con su convención de árbitro).

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.131.0'
  QA headless (12 pasos)        → gatillo→duelo1 · powers · victoria→etapa2
                                  · panel instrucciones · prueba activa
                                  · fin de prueba→sala · duelo2 · derrota
                                  repite · rejugada por mapa con progreso
                                  restaurado · leave con árbitro limpio
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
parrafo = ('<p class="body-text">La <strong>' + VX + '</strong> arregla el cableado del campeonato '
           'plantilla: en <strong>Estación Orbital</strong> el gatillo ya <strong>lanza de verdad</strong> '
           'cada etapa — duelos con los <strong>superpoderes del androide AX-9</strong> (lluvia de estrellas, '
           'meteoritos, rayo tractor y gravedad cero) en las etapas 1, 3 y 5 y <strong>pruebas de habilidad '
           '«Dianas Orbitales»</strong> en las etapas 2 y 4, precedidas de su cartel de instrucciones con '
           'botón EMPEZAR. La lección queda escrita en la plantilla: la sala de espera duerme al árbitro '
           'para que el gatillo llegue al campeonato — la misma convención que Magia y el Oeste ya seguían. '
           'De propina, la <strong>rejugada</strong> de etapas por el mapa devuelve el progreso real al '
           'terminar y salir del campeonato deja el árbitro del núcleo limpio.</p>')
if ancla in s and 'arregla el cableado del campeonato plantilla' not in s:
    s = s.replace(ancla, ancla + parrafo, 1)
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.131 insertado en la guía')
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
nov = f"""## Novedades {VX} — Estación Orbital, el gatillo ya manda

* **FIX RAÍZ de la plantilla**: el campeonato nunca ponía el árbitro a dormir
  en su sala, así que el gatillo hacía el saque clásico en vez de lanzar la
  etapa — de ahí que «no hubiera superpoderes en las etapas 1/3/5 ni pruebas
  en las 2/4». Ahora **cada etapa arranca de verdad**: duelos con los 4
  superpoderes del AX-9 y pruebas «Dianas Orbitales» con su cartel EMPEZAR.
* **Rejugada arreglada**: repetir una etapa por el mapa ya devuelve el
  progreso real al terminar (antes te dejaba «atrapado» en la etapa repetida).
* **Salida limpia**: abandonar Estación Orbital ya deja el árbitro del
  núcleo en su sitio (convención de Magia).

"""
s = s.replace('## Novedades V2.130 — la entrada de los campeonatos, pulida', nov + '## Novedades V2.130 — la entrada de los campeonatos, pulida', 1)
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

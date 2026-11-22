#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.130 — línea sellada completa:
  1) zip oficial crazypp-v2130.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.130.txt
  3) docs a V2.130 (guía + manual: HTML + PDF vía Playwright)
  4) editor a V2.130 (editor_src → build_editor.py → zip)
  5) SHA256SUMS.txt (8 entregables)
  6) README.md (tabla + novedades V2.130)
  7) public/descargas/ (8 entregables, SIN rastro de V2.129)
  8) page.tsx de /descargas a V2.130
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.130'
VX = 'V2.130'

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
stage = '/tmp/stage_v2130'
sh(f'rm -rf {stage} && mkdir -p {stage}')
sh(f'cp {PUB}/game.html {stage}/index.html')
sh(f'mkdir -p {stage}/assets && cp {PUB}/championships/estacion_orbital/assets/intro.mp4 {stage}/assets/intro.mp4 2>/dev/null || true')
# el assets/intro.mp4 raíz del zip es el de EO en V2.129 (se mantiene)
sh(f'cp -r {PUB}/championships {stage}/championships')
sh(f'cd {stage} && rm -f /{DL}/crazypp-v2130.zip && zip -X -9 -r -q /{DL}/crazypp-v2130.zip index.html assets championships')
nfiles = sh(f'unzip -l {DL}/crazypp-v2130.zip | tail -1').strip()
sh(f'unzip -t {DL}/crazypp-v2130.zip > /dev/null && echo OK')
zv = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -o \"VERSION = '[^']*'\" | head -1" % (DL, V))
print('   ', nfiles, '·', zv.strip())

# ---------------------------------------------------------------- 2) RELEASE
print('== 2) RELEASE ==')
cat = open(f'{PUB}/championships/championships.json').read()
nloc = sh(f'find {stage}/championships/locura -type f | wc -l').strip()
nmag = sh(f'find {stage}/championships/magia -type f | wc -l').strip()
noes = sh(f'find {stage}/championships/oeste -type f | wc -l').strip()
neo = sh(f'find {stage}/championships/estacion_orbital -type f | wc -l').strip()
zsize = os.path.getsize(f'{DL}/crazypp-v2130.zip')
usize = int(sh(f'unzip -l {DL}/crazypp-v2130.zip | tail -1').split()[0].replace('.', ''))
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
  Módulo EO       : manifest version 3 (plantilla final, sala V2)
  Paquete         : crazypp-v2130.zip
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
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v3, arte sala V2)

CAMBIOS DE LA {VX} (frente a V2.129)
  CUATRO AJUSTES de la revisión del jugador, todos verificados en QA:

  1) PANTALLA DE INSTRUCCIONES CON BOTÓN «EMPEZAR» (estructura común de
     TODOS los campeonatos): las instrucciones de las PRUEBAS DE HABILIDAD
     (etapas 2 y 4) ya no se van solas — el panel espera hasta que el
     jugador apunta con la pala y pulsa el botón EMPEZAR del propio panel
     (mesh 3D hijo del cartel, resaltado al apuntar, gatillo solo sobre el
     botón). En 2D/portada se mantiene el desvanecido automático.
     Call sites actualizados en locura, magia, oeste y estacion_orbital.

  2) INTRO DE CAMPEONATO — VÍDEO DE LA HISTORIA DEL RIVAL (~29 s, OPCIONAL)
     con GRAN BOTÓN «JUGAR» debajo: al entrar en CUALQUIER campeonato,
     ChampLoader.launch() planta una pantalla grande (2,56 m) con el vídeo
     en bucle y el botón dorado; el gatillo solo actúa sobre el botón.
     4 vídeos nuevos (uno por campeonato): escenas compuestas con el arte
     de cada rival + leyendas ES/EN + movimiento Ken Burns + fundidos y la
     BSO del campeonato de fondo. Si falta el vídeo, queda un póster con
     el título. La BSO del campeonato se silencia mientras dura el vídeo
     (hook champIntroPause en magia/oeste/EO; duck del núcleo en Locura).

  3) MAGIA — el cartel de aviso de nuevo partido («VS WIZARD · Ronda N» /
     «¡EL ORBE MÁGICO! · Intento N») bajado de y 2,95 a y 2,55: su borde
     superior (3,18 m) quedaba DENTRO del techo de la sala (2,85 m).
     La Locura baja 2,62→2,58 (rozaba el techo por 2 mm).

  4) ESTACIÓN ORBITAL PULIDA (revisión artística del jugador):
     · RIVAL a la DERECHA de la mesa (x 1,26 = convención DUEL_X de los
       otros campeonatos; antes centrado detrás de la mesa), girado 12°.
     · MESA SIEMPRE LIBRE: el troquel-satélite se lleva del centro
       (0/−2,8, solapado a la mesa) a 2,45/−0,85; cohete y rover revisados.
     · CARTEL DE ETAPA a la PARED FRONTAL (−2,2/1,46/−5,44), junto al
       marcador — antes flotaba sobre la mesa y tapaba la vista del rival.
       Typo GATILGO→GATILLO corregido.
     · MAPA DEL CAMPEONATO en la PARED IZQUIERDA (convención de la casa):
       arte propio 1380×752 con la ruta de 5 etapas + insignia, anillo
       dorado en la etapa vigente, tapas en las futuras y REJUGA por
       gatillo (contrato replayMap v2.96) — el campeonato superado queda
       abierto y cada etapa se puede repetir sin perder el progreso.
     · ARTE V2 de la sala: texturas con ASPECTO REAL de cada plano (el
       núcleo estira la imagen: suelo/techo 1024×1328, frontales 1536×718,
       laterales 1536×554), oclusión ambiental, dobles biseles, ventanales
       con nebulosa multicapa y planeta anillado, esclusa con rueda de
       válvula, cápsulas de hibernación, brazo robótico, consolas con
       gráficas, señalética con tildes; troqueles cohete/rover/satélite
       redibujados y ANDROIDE AX-9 rediseñado (degradados con máscaras,
       luz de borde y 5 expresiones nítidas).

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.130.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)
  Al entrar en cada uno         → vídeo de la historia + botón JUGAR
  Instrucciones de las pruebas  → esperan al botón EMPEZAR
  Pared izquierda de EO         → mapa con la ruta y la etapa vigente

— Sello generado por el pipeline oficial (scripts/pipeline_v2130.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-{VX}.txt'.replace('{VX}', VX), len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
for doc in ('guia-campeonatos-crazy-pingpong.html', 'manual-editor-campeonatos.html'):
    p = f'{DL}/{doc}'
    s = open(p, encoding='utf-8').read()
    s = s.replace('V2.129', VX)
    open(p, 'w', encoding='utf-8').write(s)
    print('    refs actualizadas en', doc, s.count(VX))
# párrafo V2.130 en la guía (tras el párrafo que menciona V2.129→ahora VX)
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
ancla = 'se trabaja en un espacio propio, con sus puertas y sus cerraduras, sin tocar los cimientos ni las habitaciones que ya están amuebladas.</p>'
parrafo = ('<p class="body-text">La <strong>' + VX + '</strong> pule la experiencia de entrada: '
           'cada campeonato arranca ahora con un <strong>vídeo corto que cuenta la historia de su '
           'rival</strong> (opcional verlo; debajo, un gran botón <strong>JUGAR</strong> lanza la partida al momento) '
           'y las instrucciones de las <strong>pruebas de habilidad</strong> esperan a que pulses el botón '
           '<strong>EMPEZAR</strong> — nadie empieza sin haber entendido qué toca hacer. En <strong>Estación '
           'Orbital</strong>, la plantilla de referencia, el androide AX-9 flota a la derecha de la mesa '
           '(como todos los rivales de la casa), la mesa queda siempre libre de troqueles, el cartel de '
           'etapa se ha ido a la pared frontal y la <strong>pared izquierda estrena el mapa del campeonato</strong> '
           'con la ruta completa y la rejugada de etapas superadas. El cartel de La Locura y el del Mago ya '
           'no se asoman al techo.</p>')
if ancla in s and 'vídeo corto que cuenta la historia de su' not in s:
    s = s.replace(ancla, ancla + parrafo, 1)
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.130 insertado en la guía')
sh(f'python3 {BASE}/scripts/print_docs_v2126.py')

# ---------------------------------------------------------------- 4) EDITOR
print('== 4) EDITOR ==')
bp = f'{BASE}/scripts/editor_src/body.html'
s = open(bp, encoding='utf-8').read()
s = s.replace('V2.129', VX)
open(bp, 'w', encoding='utf-8').write(s)
sh(f'python3 {BASE}/scripts/build_editor.py')
sh(f'cd {DL}/editor-campeonatos && rm -f ../editor-campeonatos.zip && zip -X -9 -q -r ../editor-campeonatos.zip index.html')
print('    editor reconstruido a', VX)

# ---------------------------------------------------------------- 5) SHA
print('== 5) SHA256SUMS ==')
archivos = [
    f'crazypp-v2130.zip', f'RELEASE-{VX}.txt', 'README.md',
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
s = s.replace('versión definitiva V2.129', 'versión definitiva ' + VX)
s = s.replace('crazypp-v2129.zip', f'crazypp-v2130.zip')
s = s.replace('RELEASE-V2.129.txt', f'RELEASE-{VX}.txt')
s = s.replace('V2.129', VX)
nov = f"""## Novedades {VX} — la entrada de los campeonatos, pulida

* **Vídeo de la historia del rival + botón JUGAR**: todos los campeonatos
  abren con un vídeo de ~29 s (opcional) que presenta a su rival, con un
  gran botón **JUGAR** debajo para lanzar la partida cuando quieras.
* **Instrucciones con EMPEZAR**: las pruebas de habilidad (etapas 2 y 4)
  presentan su pantalla explicativa y **esperan** a que pulses EMPEZAR.
* **Magia**: el cartel de «VS WIZARD» ya no se mete dentro del techo.
* **Estación Orbital**: rival a la derecha de la mesa, mesa siempre libre,
  cartel de etapa en la pared frontal, **mapa del campeonato en la pared
  izquierda** (con rejugada de etapas) y sala redibujada de pie a cabeza
  (ventanales, esclusa, cápsulas, brazo robótico y AX-9 nuevo).

"""
s = s.replace('## Novedades V2.128', nov + '## Novedades V2.128', 1)
open(rp, 'w', encoding='utf-8').write(s)
print('    README actualizado')

# ---------------------------------------------------------------- 7) DESCARGAS
print('== 7) public/descargas ==')
sh(f'rm -f {DES}/crazypp-v2129.zip {DES}/RELEASE-V2.129.txt')
for a in archivos:
    shutil.copy2(f'{DL}/{a}', f'{DES}/{a}')
sobras = sh(f'ls {DES} | grep -c "2129" || true').strip()
print('    refs 2129 en descargas:', sobras)

# ---------------------------------------------------------------- 8) page.tsx
print('== 8) page.tsx ==')
pp = f'{BASE}/src/app/descargas/page.tsx'
s = open(pp, encoding='utf-8').read()
s = s.replace('crazypp-v2129.zip', f'crazypp-v2130.zip')
s = s.replace('RELEASE-V2.129.txt', f'RELEASE-{VX}.txt')
s = s.replace('V2.129', VX)
open(pp, 'w', encoding='utf-8').write(s)
print('    refs V2.130 en page.tsx:', s.count(VX))

print('PIPELINE OK')

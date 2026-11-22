#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.134 — línea sellada completa:
  1) zip oficial crazypp-v2134.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.134.txt
  3) docs a V2.134 (guía + manual: HTML + PDF vía print_docs)
  4) editor a V2.134 (editor_src → build_editor.py → zip)
  5) SHA256SUMS.txt (8 entregables, REHASH del README tras editarlo)
  6) README.md (tabla + novedades V2.134)
  7) public/descargas/ (8 entregables, SIN rastro de V2.133)
  8) page.tsx de /descargas a V2.134
"""
import hashlib
import os
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.134'
VX = 'V2.134'
VN = '2134'
PREV = '2.133'
VPREV = 'V2.133'
PN = '2133'
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
zv2 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'v2.134 (módulo v44)'" % (DL, VN)).strip()
zv3 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | grep -o '\"version\": [0-9]*'" % (DL, VN)).strip()
zv4 = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'PARADA0.png'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· marcador v44 oeste:', zv2, '·', zv3, '· PARADA0 en zip:', zv4)
assert zv2.strip() == '1' and '"version": 44' in zv3 and zv4.strip() == '1', 'marcadores del zip incorrectos'

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
  Módulo oeste    : manifest version 44 (módulo v44)
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
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v44)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  Verificación del dueño en el casco (Salvaje Oeste, etapa 4 «Asalto al
  Tren») — 5 observaciones, todas atendidas:

  1) PARADAS SIN REPETIR — la estación de SALIDA (BRAVOS) lucía PARADA1.png,
     la MISMA imagen que la parada 1. La salida estrena SU arte (PARADA0.png,
     depósito de madera con placa BRAVOS: recorte por inundación + bolsas de
     cielo limpiadas + encaje 1024×512) y las 4 estaciones del trayecto
     lucen imágenes distintas.
  2) MÁS VEGETACIÓN EN LA PANORÁMICA EXTERIOR — 184 arbustos/cactus/rocas
     del propio artista compuestos sobre el suelo de arena de las DOS
     panorámicas p1_*, con perspectiva (pies más abajo = más grandes),
     racimos naturales, volteo aleatorio y bruma cálida de distancia. La
     franja inferior queda virgen (el módulo estira las últimas filas para
     bajar el desierto y lo que cayera ahí se deformaría).
  3) TÚNEL CON PROFUNDIDAD — las 3 piezas (boca · banda · boca) vivían
     COPLANARES a 0,5 m de la ventana («muy pegado»). Ahora cada pared del
     túnel se INCLINA hacia fuera (rotación Y ∓13,7°) y arranca más lejos
     (x 3,55→3,75): la boca queda junto a la ventana y el interior SE PIERDE
     A LO LEJOS — se ve DENTRO del túnel, no un decorado pegado. La costura
     boca→banda→boca y las fases por distancia quedan intactas.
  4) LA PARED DEL FONDO REBOTA — la bola que sobrevuela la pirámide ya no
     muere contra el frontal del vagón: REBOTA (restitución 0,72, chispazo
     de polvo y golpe seco de madera) y puede golpear las cajas DESDE ATRÁS.
     Lo mismo las bolas EXTRA del vórtice.
  5) SUPERPODERES DE VERDAD SOBRE LA MESA —
     · X3: las 3 bolas salen con TIRO BALÍSTICO a cajas apiladas REALES
       (izquierda · centro · derecha, escalonadas en ola) y el impacto queda
       asegurado: son «bolas de plomo» (cortan el aire — el drag normal se
       comía el 30 % de la velocidad y caían cortas) y el poder fuerza el
       tope de bolas simultáneas.
     · DINAMITA: CADENA DE EXPLOSIONES — la bola-bomba ya no muere en la
       primera detonación: ESTALLA SIEMPRE que toca caja, rebota y sale
       CAZANDO la caja viva más cercana (tiro balístico) hasta agotar TODAS
       las cajas activas en el momento del poder, con brote final. Vigilante
       anti-atasco: si la bola encadenada se queda sin camino 3,2 s, se
       re-apunta sola.

QA {VX} (ruta natural — gatillo real de la sala + FRAME NATURAL del núcleo):
  A) la SALIDA pide PARADA0.png (y NO PARADA1) con textura cargada · B) túnel:
  2 subgrupos rotados ±0,24 rad y piezas a x=3,75 · C) pared del fondo: la
  bola llega a z=-5,5 con velocidad -3,5 y SALE VIVA con vel.z positiva ·
  D) X3: 3 bolas nuevas con tiro balístico (4,5/3,8/3,8 m/s) y 3 impactos en
  la pirámide · E) dinamita: serie con la foto de las 10 cajas activas →
  primera explosión (6 cajas, bola viva re-apuntada) → la cadena corre sola
  hasta resolver TODAS → brote final · smoke de los 4 campeonatos sin
  errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.134.0'
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
ancla = 'en lugar de nacer muerto.</p>'
parrafo = ('<p class="body-text">La <strong>' + VX + '</strong> pule la etapa 4 del Salvaje Oeste '
           '(«Asalto al Tren») con cinco ajustes pedidos desde el casco: la <strong>estación de '
           'salida</strong> ya no repite la imagen de la parada 1 (estrena su propio arte, «BRAVOS»); '
           'la <strong>panorámica exterior</strong> gana vegetación (arbustos y cactus del propio '
           'artista con bruma de distancia); el <strong>túnel</strong> se ve por fin con profundidad '
           '(el interior se pierde a lo lejos en vez de ir pegado a la ventana); la <strong>pared del '
           'fondo rebota</strong> — la bola vuelve y puede golpear las cajas desde atrás —; y los '
           '<strong>superpoderes de la mesa</strong> hacen lo que prometen: el X3 lanza tres bolas con '
           'tiro balístico asegurado contra las cajas apiladas y la dinamita encadena explosiones '
           'hasta acabar con todas las cajas activas de ese momento.</p>')
if ancla in s and 'pule la etapa 4 del Salvaje Oeste' not in s:
    s = s.replace(ancla, ancla + parrafo, 1)
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.134 insertado en la guía')
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
nov = f"""## Novedades {VX} — Salvaje Oeste: el tren a punto

* **Paradas sin repetir**: la estación de salida (BRAVOS) estrena su propia
  imagen — las 4 estaciones del trayecto son distintas.
* **Más vegetación** en la panorámica exterior del desierto (arbustos y
  cactus del propio artista, con bruma de distancia).
* **Túnel con profundidad**: el interior se pierde a lo lejos en vez de ir
  pegado a la ventana.
* **La pared del fondo rebota**: la bola vuelve hacia la pirámide y puede
  golpear las cajas desde atrás.
* **Superpoderes de verdad**: el X3 lanza 3 bolas con tiro balístico
  asegurado a las cajas apiladas y la dinamita encadena explosiones hasta
  acabar con todas las cajas activas de ese momento.

"""
s = s.replace('## Novedades V2.133 — La Locura: la bola doble del Clown ya se ve',
              nov + '## Novedades V2.133 — La Locura: la bola doble del Clown ya se ve', 1)
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

print('PIPELINE OK')

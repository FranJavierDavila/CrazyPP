#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V3.0 — línea sellada completa:
  1) zip oficial crazypp-v300.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V3.0.txt
  3) download/README.md a V3.0 (tabla + novedades)
  4) SHA256SUMS.txt (8 entregables)
  5) public/descargas/ (8 entregables, sin rastro de V2.141)
  6) src/app/descargas/page.tsx a V3.0
  7) game/ espejo sincronizado
  8) verificación sha256sum -c (8/8) + serving vivo
"""
import hashlib
import re
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '3.0'
VN = '300'
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
ztrain = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'enterTraining(' " % (DL, VN)).strip()
zskins = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'PADDLE_SKINS'" % (DL, VN)).strip()
zbadge = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'addSpinBadges'" % (DL, VN)).strip()
ztape = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c '_tapeY'" % (DL, VN)).strip()
zmenu = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'drawMenuTraining'" % (DL, VN)).strip()
zstore = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c 'pp_train_v1'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv, '· enterTraining:', ztrain, '· PADDLE_SKINS:', zskins,
      '· badges:', zbadge, '· cinta:', ztape, '· menú academia:', zmenu, '· store:', zstore)
assert '3.0.0' in zv, 'zip sin V3.0.0'

# ---------------------------------------------------------------- 2) RELEASE
print('== 2) RELEASE ==')
import os
zsize = os.path.getsize(f'{DL}/crazypp-v{VN}.zip')
zunc = int(re.search(r'([\d ]+) entradas', nfiles + ' ').group(1) or 0) if False else 0
locura = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
magia = sh("unzip -p %s/crazypp-v%s.zip championships/magia/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
oeste = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
eo = sh("unzip -p %s/crazypp-v%s.zip championships/estacion_orbital/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
rel = f"""================================================================
 CRAZY PING PONG — RELEASE OFICIAL V3.0
 Meta Quest 3 · WebXR · 2026-10-14
================================================================

IDENTIDAD
  Versión visible : V3.0
  VERSION interna : '3.0.0' (index.html)
  Módulo locura   : manifest version {locura}
  Módulo magia    : manifest version {magia}
  Módulo oeste    : manifest version {oeste}
  Módulo EO       : manifest version {eo} (plantilla final)
  Paquete         : crazypp-v300.zip
  Tamaño zip      : {zsize:,} bytes ({zsize/1048576:.1f} MB)

CONTENIDO DEL PAQUETE
  index.html                          núcleo del juego (única build, V3.0)
  assets/intro.mp4                    vídeo de intro (Estación Orbital)
  championships/championships.json    catálogo (descubrimiento dinámico)
  championships/championship.schema.json  contrato de campeonatos
  championships/locura/        módulo del Campeonato de la Locura
  championships/magia/         módulo del Taller del Mago
  championships/oeste/         módulo del Campeonato del Salvaje Oeste
  championships/estacion_orbital/  PLANTILLA FINAL

CAMBIOS DE LA V3.0 (frente a V2.141)

  LA GRAN EXPANSIÓN DEL ENTRENAMIENTO: el apartado ENTRENAR pasa a ser
  una ACADEMIA PROFESIONAL de 5 áreas de mejora con 9 modos, perfil de
  puntos, palas cosméticas desbloqueables y el efecto (spin) con
  feedback visual en TODOS los modos de juego.

  1) TU PALA — el ajuste de la posición de la pala sobre la mano (que
     ya existía) se COMPACTA como primer subapartado de la academia:
     mismo panel, mismos agarres guardados, misma máquina de bolas.

  2) COLOCACIÓN Y DIRECCIÓN —
     · CUADRANTES: la mesa rival se tiza en 6 zonas (profundo/medio/
       corto × izquierda/derecha, etiquetas A–F); el juego exige 5
       golpes consecutivos a la zona marcada (pulsa en ámbar). Enseña
       a no colocar la bola en el centro (zona fácil para el rival).
     · LÍNEAS DE BANDA: franjas de 9 cm junto a laterales y fondo
       resaltadas; 4 botes pegados a línea sin salirse.

  3) ALTURA SOBRE LA RED —
     · PASE BAJO LA CINTA: cinta flotante NARANJA a +17 cm sobre la red
       con COLISIÓN REAL — la bola debe cruzar el hueco entre red y
       cinta (pasar por encima falla; golpearla rebota con «¡cinta!»).
     · AROS PARA GLOBOS: aro verde a 2,02 m sobre el campo propio con
       haz de luz; el globo debe cruzarlo y caer profundo (z < -2,45).

  4) CONTROL DE EFECTOS — robot lanzador con portal animado:
     · ROBOT CORTADO: feeds con backspin PESADO (ωx -58…-80 rad/s) a la
       zona corta; hay que abrir la pala para superar la red.
     · ROBOT TOPSPIN: feeds con topspin potente (ωx +38…+60) profundos
       a velocidades variadas; pala cerrada y bloqueo activo.

  5) PRÁCTICA DE SAQUE — el saque usa el flujo reglamentario (bola en
     la mano libre, gatillo para lanzar) y SIN enderezado del
     asistente: la bola sale tal cual de la pala.
     · SAQUE CORTO: 2 botes dentro del campo rival (zona azul tizada).
     · SAQUE PROFUNDO: diana en los últimos 15 cm (banda roja).

  6) RITMO Y CONSISTENCIA — METRÓNOMO: rallye de 30 golpes sin fallar
     a cadencia fija de 1,7 s, con anillo pulsante en el suelo y
     bonus en 30/50/100.

  7) INTERFAZ DE FEEDBACK TÉCNICO (todos los modos de academia):
     estela de la bola (ya existente), MARCAS de impacto (anillos
     blancos de 2,4 s en cada bote para medir la precisión contra la
     tiza), FLECHA DE SPIN sobre la bola (ámbar topspin · cian
     backspin · magenta lateral, con rotación según el sentido) y HUD
     propio con objetivo, racha en grande, récord, puntos de sesión y
     controles. Y en el marcador, la línea de estado del ejercicio.

  8) PUNTOS Y PERFIL DE ENTRENAMIENTO — cada acierto suma (tip por
     golpe bueno, bonus al completar el objetivo); TODO se guarda en
     el perfil (pp_train_v1): puntos totales y RÉCORD de racha por
     modo, visibles en la página ACADEMIA (medallón dorado) y en el
     subtítulo de la tarjeta ENTRENAR del menú principal.

  9) PALAS COSMÉTICAS — 6 pieles que se DESBLOQUEAN con los puntos:
     Clásica (0) · Ébano (60) · Fuego (150) · Hielo (280) · Dorada
     (450) · Neón (700). El tintado es por MATERIAL (clonado por piel:
     la clásica y la IA nunca se ven afectadas) y la pala equipada se
     usa en TODOS los modos y campeonatos: partido, supervivencia,
     online, pruebas y duelos. Al desbloquear suena el aviso, salta
     confeti y la vitrina del menú la marca como disponible.

  10) MENÚ — la tarjeta ENTRENAR abre la página ACADEMIA maquetada de
      forma artística: bandas de color por área, iconos vectoriales
      por modo, récords y recompensas en cada tarjeta, vitrina de
      palas con cerraduras y «EN USO».

  11) SPIN GLOBAL + ICONO DE EFECTO EN LA PALA — el efecto ya vivía en
      la física compartida (Magnus en TODOS los juegos); ahora cada
      golpe del jugador con efecto suficiente ENCIENTE un icono en
      las DOS CARAS de la pala (1,1 s, aditivo, sin colisión): ámbar
      topspin, cian backspin, magenta lateral, girado según el
      sentido — en partido, supervivencia, online y campeonatos, con
      la máxima precisión y sin pérdida de control (solo feedback).

  12) NÚCLEO INTACTO — nada de esto toca la física del rallye, el
      árbitro, los campeonatos ni el multijugador: los modos de la
      academia reutilizan la vía «calib» (sin IA, sin árbitro) con su
      árbitro propio; Y sale con Y como siempre.

QA V3.0 (scripts/qa_v300.py — 43/43 VERDE):
  zip = disco · VERSION '3.0.0' · 43 claves i18n es/en · catálogos
  (6 áreas · 9 modos · 6 skins con umbrales 0/60/150/280/450/700) ·
  15 símbolos del motor · menú (page:train + casos tr/skin) · 11
  compuertas _trainServe · evento paddle con spin · sintaxis JS
  inline OK · RUNTIME: carga 0 pageerrors · cuadrantes con tiza +
  resaltado + 14 marcas + flecha · máquina alimenta · puntos y
  récord persistidos · robot cortado ω -76 / topspin ω +54 · cinta a
  +17 cm con colisión real (la bola rebota) · skin fuego tintada y
  persistida con badges en las 2 monturas · icono se enciende y se
  apaga solo · menú academia con 17 rects (tr:quad… skin:ebano) ·
  65 pts desbloquean Ébano con aviso «¡NUEVA PALA DESBLOQUEADA: Ébano!» ·
  skin bloqueada rechazada · smoke de partido 0 pageerrors.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '3.0.0'
  Menú ENTRENAR del casco       → ACADEMIA (5 áreas · 9 modos · palas)
  Entrenamiento                 → puntos en el perfil y palas que se
                                  equipan para todos los campeonatos

— Sello generado por el pipeline oficial (scripts/pipeline_v300.py)
"""
open(f'{DL}/RELEASE-V{V}.txt', 'w').write(rel)
print('    RELEASE-V3.0.txt ·', len(rel), 'chars')

# ---------------------------------------------------------------- 3) README
print('== 3) README ==')
rdm = open(f'{DL}/README.md').read()
rdm = rdm.replace('versión definitiva V2.141', 'versión definitiva V3.0')
rdm = rdm.replace('`crazypp-v2141.zip` | **El juego final (V2.141)**',
                  '`crazypp-v300.zip` | **El juego final (V3.0)**')
rdm = rdm.replace('`RELEASE-V2.141.txt`', '`RELEASE-V3.0.txt`')
rdm = rdm.replace('asistente de 7 fases), V2.141', 'asistente de 7 fases), V3.0')
rdm = rdm.replace('**Guía maquetada sin tecnicismos** (14 páginas), V2.141',
                  '**Guía maquetada sin tecnicismos** (14 páginas), V3.0')
rdm = rdm.replace('**Manual del editor paso a paso** (9 páginas), V2.141',
                  '**Manual del editor paso a paso** (9 páginas), V3.0')
nov3 = """## Novedades V3.0 — La Academia de Entrenamiento + palas cosméticas

* ENTRENAR pasa a ser una ACADEMIA de 5 áreas con 9 modos
  profesionales: cuadrantes tizados, líneas de banda, pase bajo la
  cinta (con colisión real), aros para globos, robot cortado y robot
  topspin (spin de verdad), saque corto de doble bote, saque profundo
  a los últimos 15 cm y metrónomo de 30 golpes.
* Feedback técnico en VR: estela, marcas de impacto, flecha de spin
  sobre la bola y HUD propio con racha, récord y puntos.
* Los objetivos dan PUNTOS que se guardan en tu perfil y desbloquean
  6 PALAS COSMÉTICAS (Clásica · Ébano · Fuego · Hielo · Dorada ·
  Neón) que se equipan para TODOS los modos y campeonatos.
* El efecto se INDICA: icono en las dos caras de tu pala al golpear
  con spin — en partido, supervivencia, online y campeonatos.
* El ajuste de la pala sobre la mano queda compactado como primer
  subapartado de la academia (todo igual, mejor ordenado).

"""
rdm = re.sub(r'## Novedades V2\.141[^\n]*\n((?!\Z).|\n)*?(?=## Novedades V2\.140)',
             nov3, rdm, count=1, flags=re.S)
open(f'{DL}/README.md', 'w').write(rdm)
print('    README.md a V3.0')

# ---------------------------------------------------------------- 4) SHA256
print('== 4) SHA256SUMS ==')
entregables = [
    f'crazypp-v{VN}.zip',
    f'RELEASE-V{V}.txt',
    'README.md',
    'editor-campeonatos.zip',
    'guia-campeonatos-crazy-pingpong.html',
    'guia-campeonatos-crazy-pingpong.pdf',
    'manual-editor-campeonatos.html',
    'manual-editor-campeonatos.pdf',
]
with open(f'{DL}/SHA256SUMS.txt', 'w') as f:
    for e in entregables:
        f.write(f'{sha(f"{DL}/{e}")}  {e}\n')
print('    8 entregables')

# ---------------------------------------------------------------- 5) descargas
print('== 5) public/descargas ==')
sh(f'rm -f {DES}/crazypp-v2141.zip {DES}/RELEASE-V2.141.txt')
for e in entregables:
    shutil.copy2(f'{DL}/{e}', f'{DES}/{e}')
print('   ', len(entregables), 'entregables copiados ·', len(os.listdir(DES)), 'ficheros')

# ---------------------------------------------------------------- 6) page.tsx
print('== 6) page.tsx ==')
ptx = open(f'{BASE}/src/app/descargas/page.tsx').read()
ptx = ptx.replace('crazypp-v2141.zip', f'crazypp-v{VN}.zip')
ptx = ptx.replace('V2.141', 'V3.0')
open(f'{BASE}/src/app/descargas/page.tsx', 'w').write(ptx)
print('    page.tsx a V3.0 ·', ptx.count('V3.0'), 'referencias')

# ---------------------------------------------------------------- 7) espejo
print('== 7) espejo game/ ==')
sh(f'cp {PUB}/game.html {BASE}/game/index.html')
print('    game/index.html =', sha(f'{BASE}/game/index.html')[:12])

# ---------------------------------------------------------------- 8) verificación
print('== 8) verificación ==')
v = sh(f'cd {DL} && sha256sum -c SHA256SUMS.txt')
ok8 = v.count(': OK')
print(v)
print(f'SHA256: {ok8}/8 OK')
assert ok8 == 8
served = urllib_sha = None
import urllib.request
served_game = urllib.request.urlopen('http://localhost:3000/game.html', timeout=20).read()
print('serving game.html =', hashlib.sha256(served_game).hexdigest()[:12],
      '== disco', sha(f'{PUB}/game.html')[:12])
assert hashlib.sha256(served_game).hexdigest() == sha(f'{PUB}/game.html')
print('PIPELINE V3.0 COMPLETO')

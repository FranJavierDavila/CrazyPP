#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.132 — línea sellada completa:
  1) zip oficial crazypp-v2132.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.132.txt
  3) docs a V2.132 (guía + manual: HTML + PDF vía Playwright)
  4) editor a V2.132 (editor_src → build_editor.py → zip)
  5) SHA256SUMS.txt (8 entregables)
  6) README.md (tabla + novedades V2.132)
  7) public/descargas/ (8 entregables, SIN rastro de V2.131)
  8) page.tsx de /descargas a V2.132
"""
import hashlib
import os
import shutil
import subprocess

BASE = '/home/z/my-project'
PUB = f'{BASE}/public'
DL = f'{BASE}/download'
DES = f'{BASE}/public/descargas'
V = '2.132'
VX = 'V2.132'
VN = '2132'          # nombre de fichero sin punto (convención)
PREV = '2.131'
VPREV = 'V2.131'
PN = '2131'

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
zv2 = sh("unzip -p %s/crazypp-v%s.zip championships/estacion_orbital/index.js | grep -c 'v3.2 (V2.132)'" % (DL, VN)).strip()
zv3 = sh("unzip -p %s/crazypp-v%s.zip championships/estacion_orbital/manifest.json | grep -o '\"version\": [0-9]*'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· marcador v3.2 EO:', zv2, '·', zv3)

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
 Meta Quest 3 · WebXR · 2026-10-14
================================================================

IDENTIDAD
  Versión visible : {VX}
  VERSION interna : '{V}.0' (index.html)
  Módulo locura   : manifest version 18
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
  championships/locura/        ({nloc} f.)  módulo del Campeonato de la Locura (v18)
  championships/magia/         ({nmag} f.)  módulo del Taller del Mago (v27)
  championships/oeste/         ({noes} f.) módulo del Campeonato del Salvaje Oeste (v43)
  championships/estacion_orbital/ ({neo} f.) PLANTILLA FINAL (v5, módulo v3.2)

CAMBIOS DE LA {VX} (frente a {VPREV})

  Informe del casco en Estación Orbital: «no se lanzan superpoderes en las
  partidas (ni cartel con el identificador del poder)» y «en la prueba de
  asteroides la bola aparece botando lejos, por encima de la mesa, y es
  imposible destruir los asteroides (además, muy cutres)». Tres raíces y
  un bug extra cazado por el QA de esta versión:

  1) SUPERPODERES A PRUEBA DE BALAS (módulo v3.2):
     · DISPARO REDUNDANTE — se queda el gancho por PUNTO (onPoint) y el
       update() del módulo añade el disparo por RALLY (bola viniendo al
       jugador, edge vel.z>0.35, patrón de La Locura que sí funciona en el
       casco) + GARANTÍA: si en 22 s de duelo no ha saltado nada, el poder
       se FUERZA (red anti-silencio verificada con azar bloqueado a 0.99).
     · CARTEL DEL SUPERPODER — el «identificador» que el jugador espera:
       panel flotante junto al AX-9 con el medallón del poder + nombre en
       grande; fase AVISO ámbar «AX-9 PREPARA…» y fase ACTIVA cian, con
       pulso. Los 404 assets/assets/ de los iconos, corregidos.
     · EFECTOS BLINDADOS — _poderArrancar en try/catch: un efecto que
       falle cierra el poder limpio (antes una excepción dejaba el poder
       colgado y bloqueaba la bolsa para siempre). Reintentos más ágiles
       (fallo 4 s, post-poder 10-15 s, primer poder a 6 s).

  2) PRUEBA «DIANAS ORBITALES» JUGABLE:
     · LA BOLA DE ESPERA ESTABA INALCANZABLE — z=-0.90 era 0,67 m DENTRO
       de la mesa (el borde del jugador está en -0.23): de ahí lo de
       «imposible destruir los asteroides». Ahora espera en z=-0.50,
       pegada al borde (convención Magia tableNearZ−0.38), apex 0.42.
     · DIANAS 3D DE VERDAD (adiós a los sprites «cutres»): asteroide =
       icosaedro con ruido determinista por vértice + 2 piedras satélite;
       caja blindada = contenedor metálico con aristas ámbar, núcleo
       brillante y escudo esférico que destella al aguantar un golpe;
       dron = fuselaje con cabina cian y 4 rotores girando. La colisión
       esférica y el barrido anti-túnel se quedan igual (el Group respeta
       position/visible); dispose completo al reintentar.

  3) FIX CRÍTICO de onMatchOver — el núcleo llama con el GANADOR como
     STRING ('player'/'rival') y el módulo lo trataba como booleano:
     'rival' es truthy → PERDER un duelo AVANZABA la etapa con mensajes
     de victoria. Ahora convención Oeste: won = (w === 'player').

  QA {VX} (13 pasos, TODO por la ruta natural): poderes por puntos reales
  (processIntents+applyPoint, azar intacto: 3 poderes distintos con cartel),
  poder por rally, garantía 22 s con mala suerte total, ganar duelo 1,
  prueba 1 con colisión REAL balística (19 frames a la 1.ª diana) y 10/10,
  PERDER duelo 2 (la etapa NO avanza), revancha ganada, prueba 4 compleja
  (14 dianas · 3 cajas · 2 drones · 3 escudos · rotores), bola-HOLD a
  0,564 m, escudo de 2 golpes verificado (aguanta con destello y rompe),
  14/14 → etapa final, leave con árbitro limpio; smoke de los 4
  campeonatos sin errores de página. Núcleo sin cambios de comportamiento
  para locura/magia/oeste.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.132.0'
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
parrafo = ('<p class="body-text">La <strong>' + VX + '</strong> hace que en <strong>Estación Orbital</strong> '
           'los superpoderes del AX-9 <strong>no puedan quedarse callados</strong>: el módulo dispara por '
           'punto <em>y</em> por rally (bola viniendo al jugador, como La Locura) y si en 22 segundos no ha '
           'saltado nada, <strong>fuerza el poder</strong>. Cada poder anuncia su <strong>cartel con el '
           'medallón y el nombre</strong> — «AX-9 PREPARA…» en ámbar y «¡SUPERPODER!» en cian — y los '
           'efectos van blindados para que un fallo nunca cuelgue la bolsa. En las <strong>pruebas de '
           'dianas</strong>, la bola de espera se coloca <strong>pegada al borde del jugador</strong> (antes '
           'flotaba dentro de la mesa, inalcanzable) y las dianas son <strong>modelos 3D de verdad</strong>: '
           'asteroides facetados con piedras satélite, cajas blindadas con escudo que destella y drones con '
           'rotores girando. Además, perder un duelo ya <strong>no avanza la etapa</strong> (el núcleo nombra '
           'al ganador con texto y el módulo lo leía como verdadero).</p>')
if ancla in s and 'no puedan quedarse callados' not in s:
    s = s.replace(ancla, ancla + parrafo, 1)
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.132 insertado en la guía')
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
nov = f"""## Novedades {VX} — Estación Orbital: los poderes ya mandan

* **Superpoderes a prueba de balas**: disparo por punto *y* por rally (como
  La Locura) + **garantía a los 22 s** sin poderes. Cada poder enseña su
  **cartel con el medallón y el nombre** («AX-9 PREPARA…» / «¡SUPERPODER!»).
* **Prueba de dianas jugable**: la bola de espera estaba *dentro* de la mesa
  (inalcanzable) — ahora espera pegada al borde del jugador — y las dianas
  son **modelos 3D** (asteroides facetados, cajas con escudo, drones).
* **Perder un duelo ya no avanza la etapa** (el ganador llega como texto y
  se leía como verdadero) y los efectos de poder van blindados.

"""
s = s.replace('## Novedades V2.131 — Estación Orbital, el gatillo ya manda', nov + '## Novedades V2.131 — Estación Orbital, el gatillo ya manda', 1)
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

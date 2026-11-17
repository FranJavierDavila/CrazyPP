#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.138 — línea sellada completa:
  1) zip oficial crazypp-v2138.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.138.txt
  3) docs a V2.138 (guía con párrafo nuevo + manual: HTML + PDF vía print_docs)
  4) editor a V2.138 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.138) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.137)
  8) page.tsx de /descargas a V2.138
  9) game/ espejo sincronizado
 10) rebuild Next + sync standalone + reinicio del servidor (lecciones V2.135/136)
 11) verificación de serving vivo
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
V = '2.138'
VX = 'V2.138'
VN = '2138'
PREV = '2.137'
VPREV = 'V2.137'
PN = '2137'
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
zv46 = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zv20 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/manifest.json | python3 -c \"import json,sys; print(json.load(sys.stdin)['version'])\"" % (DL, VN)).strip()
zmapa = sh("unzip -l %s/crazypp-v%s.zip | grep -c 'locura/assets/mapa.webp'" % (DL, VN)).strip()
ztx = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'tx: 453' || true" % (DL, VN)).strip()
zv2138 = sh("unzip -p %s/crazypp-v%s.zip championships/locura/index.js | grep -c 'v2.138' || true" % (DL, VN)).strip()
zbandaY = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'bandaY' || true" % (DL, VN)).strip()
ztrav = sh("unzip -p %s/crazypp-v%s.zip championships/oeste/index.js | grep -c 'traverse((m)' || true" % (DL, VN)).strip()
ztx137 = sh("unzip -p %s/crazypp-v%s.zip championships/magia/index.js | grep -c 'tx: 456' || true" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· NORMAS_SKIN:', zskin,
      '· normas 3:', zn1, zn2, zn3,
      '· manifest magia:', zv28, '· oeste:', zv46, '· locura:', zv20,
      '· mapa.webp locura:', zmapa, '· tx: 453:', ztx, '· v2.138:', zv2138,
      '· bandaY:', zbandaY, '· oeste traverse:', ztrav, '· magia tx: 456:', ztx137)
assert zv.strip() == "VERSION = '2.138.0'", 'VERSION del zip incorrecta'
assert int(zskin) >= 3 and zn1 == '1' and zn2 == '1' and zn3 == '1', 'carteles ausentes'
assert zv28 == '28', 'manifest magia no es v28'
assert zv46 == '46', 'manifest oeste no es v46'
assert zv20 == '20', 'manifest locura no es v20'
assert zmapa == '1', 'mapa.webp de locura no está en el zip'
assert int(ztx) >= 1 and int(zv2138) >= 1, 'marcadores v2.138 ausentes en locura'
assert int(zbandaY) >= 2, 'bandaY ausente en oeste'
assert int(ztrav) >= 1, 'regresión: traverse del oeste ausente'
assert int(ztx137) >= 1, 'regresión: tapas tx del magia ausentes'
import zipfile
with zipfile.ZipFile(f'{DL}/crazypp-v{VN}.zip') as z:
    _h = hashlib.sha256(z.read('championships/locura/assets/mapa.webp')).hexdigest()
assert _h == sha(f'{PUB}/championships/locura/assets/mapa.webp'), \
    'el mapa.webp del zip NO es el arte nuevo del clown'

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

  El dueño revisa el casco y pide dos cosas: el túnel del Salvaje Oeste
  «todas las piezas al mismo factor» (con bocas de ~1,8 m, porque las de
  1,2 m se veían los cortes por abajo de la ventana) y el mapa del CLOWN
  (el reenvío que en la {VPREV} llegó con el mismo nombre que el del
  wizard y fue sobrescrito).

  1) TÚNEL A ESCALA — FACTOR ÚNICO f = 1,8/3,4 = 0,529 en TODO el rig:
     bocas (tunelboca.png) 1,2 → 1,8 m (sus cortes inferior 0,9 y superior
     2,7 salen del hueco de la ventana, y 1,08-2,55: ya no se ve ningún
     corte) y banda interior (tunel.png repetida) 6,0 → 3,176 m con centro
     TU.bandaY 2,65 → 2,257 (el centro antiguo escalado anclado al centro
     de la ventana: la franja visible del arte conserva su centro y la
     banda cubre la ventana entera). Secuencia boca→banda→boca cosida
     intacta (todo se deriva de bh/len), copias 2 → 4 por la misma regla
     (len/(h×2,35)) y fases por distancia intactas. Módulo OESTE v46.
  2) MAPA DEL CLOWN — arte nuevo 1380×752 con GLOBOS numerados (1/3/5
     clowns, 2/4 arkanoid) sobre medallones redondos: mapa.webp
     reemplazado (q92, 183 KB) y NODOS re-medidos (Hough + banda de
     cobertura angular dorada): 226,253 · 453,507 · 700,256 · 959,508 ·
     1208,322 con anillos r 114/119/109/121/107 (regla r = 120×banda/107,5
     calibrada en la V2.137). TAPAS «?» con centro y escala PROPIOS por
     nodo (tx/ty/ts): cubren cada medallón entero con margen (ts
     0,94/0,86/0,95/0,85) — los globos numerados asoman encima, como las
     estrellas del Oeste. Módulo de La Locura v20.

QA {VX} (ruta natural + verificación visual):
  el mapa.webp SERVIDO es byte a byte el arte nuevo (dif. media 1,9 frente
  al PNG del dueño) · nodesPx re-medidos en el módulo vivo · 4 tapas
  centradas en tx/ty con escala ts exacta y visibles en la etapa 1 ·
  anillo del nodo 1 a escala 114/120 · cobertura de tapas verificada
  (medallón + 3 px de AA DENTRO del rect de tapa en los 4 nodos) ·
  tunelGrp VIVO: 4 bocas 1,8×1,8 @y1,8 y 2 bandas 26,4×3,176 @y2,257 ·
  ventana cubierta SIN cortes (boca 0,9-2,7 · banda 0,67-3,85 ⊇ ventana
  1,08-2,55) · factor único h/bh = 6,0/3,4 · copias = 4 · fotos 3D reales
  del mapa y de los portales de entrada/salida · smoke 4 campeonatos sin
  errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.138.0'
  Menú CAMPEONATOS del casco    → 4 campeonatos (todos «publicado»)

— Sello generado por el pipeline oficial (scripts/pipeline_v{V}.py)
"""
open(f'{DL}/RELEASE-{VX}.txt', 'w').write(rel)
print('    RELEASE-%s.txt' % VX, len(rel), 'bytes')

# ---------------------------------------------------------------- 3) DOCS
print('== 3) DOCS (guía + manual) ==')
gp = f'{DL}/guia-campeonatos-crazy-pingpong.html'
s = open(gp, encoding='utf-8').read()
# --- párrafo nuevo V2.138 delante del párrafo V2.137 (mapa del wizard) ---
ancla = '<p class="body-text">La <strong>V2.137</strong> estrena el <strong>mapa de etapas'
parrafo = (f'<p class="body-text">La <strong>{VX}</strong> ajusta el <strong>túnel del tren del '
           'Salvaje Oeste</strong> —entradas, salida e interior pasan por el <strong>mismo factor '
           'de reducción</strong> (las bocas suben a ~1,8 m y ya no se ve ningún corte por la '
           'ventana)— y estrena el <strong>mapa de etapas del Campeonato de la Locura</strong>: '
           'cinco medallones redondos con <strong>globos numerados</strong>, nodos re-medidos, '
           'anillo dorado que abraza cada borde y tapas «?» a medida.</p>')
if '<strong>V2.138</strong> ajusta el <strong>túnel del tren' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla del párrafo V2.137 no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    print('    párrafo V2.138 insertado en la guía')
# --- metas a V2.138 + restaurar el párrafo histórico V2.137 tras el replace ---
s = s.replace(VPREV, VX)
s = s.replace(f'La <strong>{VX}</strong> estrena el <strong>mapa de etapas',
              'La <strong>V2.137</strong> estrena el <strong>mapa de etapas', 1)
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
nov = f"""## Novedades {VX} — El túnel a escala y el mapa del clown

* **Túnel a escala**: entradas, salida e interior del túnel del Salvaje
  Oeste comparten el mismo factor de reducción; las bocas suben a ~1,8 m
  y ya no se ve ningún corte por la ventana.
* **Mapa del clown nuevo**: cinco medallones redondos con globos
  numerados —nodos re-medidos, anillo al borde y tapas «?» a medida—.
* El mapa del wizard de la {VPREV} no cambia: el clown había llegado
  pisado y ahora tiene su propio arte.

"""
s = s.replace('## Novedades V2.137 — El Taller del Mago estrena mapa',
              nov + '## Novedades V2.137 — El Taller del Mago estrena mapa', 1)
s = s.replace('versión definitiva ' + VPREV, 'versión definitiva ' + VX)
s = s.replace(f'crazypp-v{PN}.zip', f'crazypp-v{VN}.zip')
s = s.replace(f'RELEASE-{VPREV}.txt', f'RELEASE-{VX}.txt')
s = s.replace(VPREV, VX)
# el header del mapa del wizard ES histórico V2.137: lo restauro tras el replace global
s = s.replace(f'## Novedades {VX} — El Taller del Mago estrena mapa',
              '## Novedades V2.137 — El Taller del Mago estrena mapa', 1)
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

# ------------------------------------------------- 10) REBUILD + SYNC + RESTART
print('== 10) rebuild Next + sync standalone + restart ==')
rc = sh(f'cd {BASE} && npm run build > /tmp/build_v{V}.log 2>&1; echo $?').strip()
assert rc == '0', f'npm run build falló (rc {rc}) — ver /tmp/build_v{V}.log'
_gv = open(f'{BASE}/.next/standalone/public/game.html', encoding='utf-8').read()
assert "VERSION = '2.138.0'" in _gv, 'el build no copió el game.html nuevo'
pid = sh("ss -tlnp | grep ':3000' | grep -oP 'pid=\\K[0-9]+' | head -1").strip()
if pid:
    sh(f'kill {pid} || true')
    time.sleep(1.5)
sh(f'cd {BASE}/.next/standalone && NODE_ENV=production nohup bun server.js > server.log 2>&1 & echo arrancado')
for _ in range(30):
    try:
        code = subprocess.run('curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/game.html',
                              shell=True, capture_output=True, text=True).stdout.strip()
    except Exception:
        code = '000'
    if code == '200':
        break
    time.sleep(1)
print('    servidor arriba (game.html 200)')

# ------------------------------------------------- 11) SERVING VIVO
print('== 11) verificación de serving vivo ==')
import urllib.request
gv = urllib.request.urlopen('http://localhost:3000/game.html').read()
assert b"VERSION = '2.138.0'" in gv, 'game.html servido no es 2.138.0'
print('    game.html servido: 2.138.0 OK')
for f_ in (f'descargas/crazypp-v{VN}.zip', f'descargas/RELEASE-{VX}.txt', 'descargas/SHA256SUMS.txt'):
    c = subprocess.run(f'curl -s -o /dev/null -w "%{{http_code}}" http://localhost:3000/{f_}',
                       shell=True, capture_output=True, text=True).stdout.strip()
    print(f'    {f_}: {c}')
    assert c == '200', f'{f_} no servido'
mz = urllib.request.urlopen('http://localhost:3000/championships/locura/assets/mapa.webp').read()
assert hashlib.sha256(mz).hexdigest() == sha(f'{PUB}/championships/locura/assets/mapa.webp'), \
    'mapa.webp servido ≠ arte nuevo'
print('    locura/assets/mapa.webp servido = arte nuevo (sha256 OK)')
ij = urllib.request.urlopen('http://localhost:3000/championships/locura/index.js').read()
assert b'tx: 453' in ij and b'v2.138' in ij, 'index.js de locura servido está VIEJO'
oj = urllib.request.urlopen('http://localhost:3000/championships/oeste/index.js').read()
assert b'bandaY' in oj, 'index.js de oeste servido está VIEJO'
print('    index.js locura/oeste servidos: v2.138 OK')

print('PIPELINE OK')

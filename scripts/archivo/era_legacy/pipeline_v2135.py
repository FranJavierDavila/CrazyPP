#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE OFICIAL V2.135 — línea sellada completa:
  1) zip oficial crazypp-v2135.zip (index.html + assets/intro.mp4 + championships/)
  2) RELEASE-V2.135.txt
  3) docs a V2.135 (guía + manual: HTML + PDF vía print_docs)
  4) editor a V2.135 (editor_src → build_editor.py → zip)
  5) README.md (tabla + novedades V2.135) — ANTES del SHA (lección V2.133)
  6) SHA256SUMS.txt (8 entregables)
  7) public/descargas/ (8 entregables, SIN rastro de V2.134)
  8) page.tsx de /descargas a V2.135
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
V = '2.135'
VX = 'V2.135'
VN = '2135'
PREV = '2.134'
VPREV = 'V2.134'
PN = '2134'
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
zarte = sh("unzip -p %s/crazypp-v%s.zip index.html | grep -c '_instrArte'" % (DL, VN)).strip()
print('   ', nfiles, '·', zv.strip(), '· NORMAS_SKIN:', zskin, '· _instrArte:', zarte,
      '· normas_clown/wizard/forajido en zip:', zn1, zn2, zn3)
assert zv.strip() == "VERSION = '2.135.0'", 'VERSION del zip incorrecta'
assert int(zskin) >= 3 and int(zarte) >= 2, 'marcadores del núcleo ausentes'
assert zn1 == '1' and zn2 == '1' and zn3 == '1', 'faltan los 3 carteles en el zip'

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

  El dueño manda 3 marcos nuevos del artista para «usar de carteles cuando
  se explican las normas de juego de las diferentes etapas» y pide «que los
  textos estén bien colocados, que entren en el espacio interior de los
  carteles y que se lean perfectamente». Así queda:

  1) PIEL DE ARTE POR CAMPEONATO — el cartel de instrucciones de las etapas
     (showInstrucciones) viste el arte real del artista: La Locura el marco
     de circo con el CLOWN asomando (normas_clown.png), Magia el marco
     arcano con el WIZARD (normas_wizard.png) y el Salvaje Oeste el marco
     de bronce con el FORAJIDO (normas_forajido.png). Estación Orbital
     conserva su panel espacial dibujado. Las 3 imágenes precargan al
     arrancar; si alguna no llegara, caja de seguridad a la piel dibujada
     de siempre.
  2) SIN DEFORMAR EL ARTE — el cartel pasa a lienzo 1280×640, la proporción
     2:1 nativa de los marcos, en un panel de 3,8×1,9 m (antes el arte se
     habría estirado un 28 % en vertical).
  3) TODO EL TEXTO DENTRO DEL HUECO — el rectángulo interior de cada cartel
     está MEDIDO sobre el arte (con margen de seguridad: el personaje asoma
     por el centro superior y las manos agarran el marco) y título, filete
     y cuerpo se maquetan dentro: título oro/crema con contorno y sombra,
     filete dorado con rombo, y cuerpo envuelto con measureText (NUNCA se
     corta) en 1 columna si cabe cómodo o 2 columnas equilibradas con
     separador central cuando el texto es largo (las normas del ASEDIO, las
     más largas, entran de sobra).
  4) LEGIBILIDAD PERFECTA — velo oscuro suave sobre el hueco + sombra de
     texto: crema y oro sobre la pizarra / el pergamino oscuro / la piedra,
     sin tapar el arte. Fuente nunca por debajo de 19 px del lienzo
     (~5,6 cm físicos en el cartel).
  5) BOTÓN EMPEZAR en su sitio — el botón cuelga PINZADO al marco bajo del
     cartel (fuera del hueco: las normas lo ocupan entero), con el mismo
     raycast y resaltado al apuntar de siempre.

QA {VX} (ruta natural, textos REALES de los módulos):
  pieles activas por campeonato (skin=locura/magia/oeste) · diff por píxel
  contra el arte escalado: TODOS los píxeles de texto dentro del hueco
  (0 fuera) en los 3 carteles · fuente 21-22,5 px · piel «estacion» sin
  cambios · botón EMPEZAR pintado con re-pintado al apuntar y raycast
  seguro sin mandos · smoke de los 4 campeonatos sin errores de página.

VERIFICACIÓN
  sha256sum -c SHA256SUMS.txt   → 8/8 OK
  grep "VERSION = " index.html  → '2.135.0'
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
ancla = '<p class="body-text">La <strong>V2.135</strong>'
parrafo = ('<p class="body-text">La <strong>V2.135</strong> viste los <strong>carteles de las normas</strong> '
           'con el <strong>arte del artista</strong>: tres marcos nuevos —el de <strong>circo con el Clown '
           'asomando</strong> para La Locura, el <strong>arcano con el Wizard</strong> para el Taller del Mago y '
           'el de <strong>bronce con el Forajido</strong> para el Salvaje Oeste— que enmarcan ahora las '
           'instrucciones de cada etapa. El cartel respeta la proporción nativa del dibujo (nada se estira), '
           'el <strong>título y las normas viven dentro del hueco del cartel</strong> —título en oro con '
           'contorno, cuerpo en crema con sombra, en una o dos columnas equilibradas según el largo del '
           'texto— y un velo oscuro suave garantiza que <strong>todo se lea perfecto</strong>; el botón '
           '<strong>EMPEZAR</strong> cuelga del marco inferior, fuera del hueco. Estación Orbital conserva '
           'su panel espacial de siempre.</p>')
if 'viste los <strong>carteles de las normas</strong>' not in s:
    pos = s.find(ancla)
    assert pos > 0, 'ancla de la guía no encontrada'
    s = s[:pos] + parrafo + s[pos:]
    open(gp, 'w', encoding='utf-8').write(s)
    print('    párrafo V2.135 insertado en la guía')
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
nov = f"""## Novedades {VX} — Los carteles de las normas, con el arte del artista

* **3 marcos nuevos** enmarcan las instrucciones de las etapas: el de circo
  con el Clown (La Locura), el arcano con el Wizard (Magia) y el de bronce
  con el Forajido (Salvaje Oeste).
* **Todo el texto dentro del hueco del cartel**: título en oro con contorno
  y cuerpo en crema con sombra, en una o dos columnas equilibradas — nunca
  se corta ni sale del marco (verificado píxel a píxel).
* **El arte no se deforma**: el cartel adopta la proporción nativa 2:1 de
  los marcos.
* **Legibilidad perfecta**: velo oscuro suave + sombra de texto sobre el
  hueco; el botón EMPEZAR cuelga del marco inferior, fuera del hueco.

"""
s = s.replace('## Novedades V2.135 — ESTACIÓN ORBITAL «PLANTILLA FINAL»',
              nov + '## Novedades V2.135 — ESTACIÓN ORBITAL «PLANTILLA FINAL»', 1)
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

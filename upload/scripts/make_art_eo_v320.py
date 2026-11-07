#!/usr/bin/env python3
"""V3.2.0-ORB1 · Convierte el arte del dueño al paquete del campeonato
ESTACIÓN ORBITAL (public/championships/estacion_orbital/assets).

  · SALA (6 planos, convención del núcleo createChampRoom):
      _ext/paredes/izquierda.png → sala_left.jpg   (2395×864 → 1920)
      _ext/paredes/derecha.png   → sala_right.jpg  (2395×864 → 1920)
      _ext/paredes/fondo.png     → sala_back.jpg   (1849×864 → 1600)
      _ext/paredes/frente.png    → sala_front.jpg  (1849×864 → 1600)
      _ext/paredes/suelo.png     → sala_floor.jpg  (1296×1678 nativo)
      upload/techo.png           → sala_ceil.jpg   (1296×1678 nativo, el
      reenvío fresco del dueño — pisa el de _ext/paredes con mismo tamaño)
  · RIVAL (poses 512×1024 RGBA → webp q88, convención clown
    «assets/<estado>.webp» + alias de los 4 estados históricos):
      astro.png        → rival.webp + idle.webp
      astro_focused    → focused.webp + duelo.webp (pose de duelo)
      astro_victory    → victory.webp + triunfante.webp
      astro_defeated   → defeated.webp + derrotado.webp
      astro_idle/surprised/panic/laughing/loosing/picando/crazy → <estado>.webp
      upload/astro_angry.png → angry.webp (el reenvío del dueño, idéntico
      al «techo.png» que venía dentro de astro.zip — md5 802a3324…)
  · CARTEL SUPER POWER!! (la misma etiqueta de los otros campeonatos):
      locura/assets/superpoder.webp → superpower.png
  · MAPA de la pared izquierda: upload/mapa.png → mapa.png (1376×768)
  · NORMAS (plantilla del artista para los carteles v2.135):
      upload/astro_normas.png → normas_astro.png (1024×512, hueco 152..872 × 152..432)
  · RECORTABLES del suelo (sustituyen a los troqueles placeholder):
      _ext/recortables/escena_*.png → decor/escena_*.png  (fuera troquel1-3)
  · PISTOLA LÁSER del ARKANOID 2 (mismo modelo que magia/locura):
      locura/assets/pistol.glb → pistol.glb
"""
from PIL import Image
import os
import shutil

RAIZ = '/home/z/my-project'
UP = os.path.join(RAIZ, 'upload')
EXT = os.path.join(UP, '_ext')
DST = os.path.join(RAIZ, 'public', 'championships', 'estacion_orbital', 'assets')
LOC = os.path.join(RAIZ, 'public', 'championships', 'locura', 'assets')


def jpg(src, dst, maxw=None, q=85):
    im = Image.open(src).convert('RGB')
    if maxw and im.size[0] > maxw:
        h = round(im.size[1] * maxw / im.size[0])
        im = im.resize((maxw, h), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=q, optimize=True, progressive=True)
    return im.size


def webp(src, dst, q=88):
    im = Image.open(src).convert('RGBA')
    im.save(dst, 'WEBP', quality=q, method=6)
    return im.size


def copia(src, dst):
    shutil.copy2(src, dst)


hechos = []
for src, dst, maxw in [
    (f'{EXT}/paredes/izquierda.png', f'{DST}/sala_left.jpg', 1920),
    (f'{EXT}/paredes/derecha.png', f'{DST}/sala_right.jpg', 1920),
    (f'{EXT}/paredes/fondo.png', f'{DST}/sala_back.jpg', 1600),
    (f'{EXT}/paredes/frente.png', f'{DST}/sala_front.jpg', 1600),
    (f'{EXT}/paredes/suelo.png', f'{DST}/sala_floor.jpg', None),
    (f'{UP}/techo.png', f'{DST}/sala_ceil.jpg', None),
]:
    s = jpg(src, dst, maxw)
    hechos.append((os.path.basename(dst), s, os.path.getsize(dst)))

POSES = [
    ('astro.png', ['rival.webp', 'idle.webp']),
    ('astro_focused.png', ['focused.webp', 'duelo.webp']),
    ('astro_victory.png', ['victory.webp', 'triunfante.webp']),
    ('astro_defeated.png', ['defeated.webp', 'derrotado.webp']),
    ('astro_idle.png', ['idle.webp']),
    ('astro_surprised.png', ['surprised.webp']),
    ('astro_panic.png', ['panic.webp']),
    ('astro_laughing.png', ['laughing.webp']),
    ('astro_loosing.png', ['loosing.webp']),
    ('astro_picando.png', ['picando.webp']),
    ('astro_crazy.png', ['crazy.webp']),
]
for nombre, destinos in POSES:
    for d in destinos:
        s = webp(f'{EXT}/astro/{nombre}', f'{DST}/{d}')
        hechos.append((d, s, os.path.getsize(f'{DST}/{d}')))
s = webp(f'{UP}/astro_angry.png', f'{DST}/angry.webp')
hechos.append(('angry.webp', s, os.path.getsize(f'{DST}/angry.webp')))

copia(f'{LOC}/superpoder.webp', f'{DST}/superpower.png')
copia(f'{UP}/mapa.png', f'{DST}/mapa.png')
copia(f'{UP}/astro_normas.png', f'{DST}/normas_astro.png')
copia(f'{LOC}/pistol.glb', f'{DST}/pistol.glb')
for e in ['escena_astro', 'escena_cohete', 'escena_lander', 'escena_telescopio']:
    copia(f'{EXT}/recortables/{e}.png', f'{DST}/decor/{e}.png')
for t in ['troquel1.png', 'troquel2.png', 'troquel3.png']:
    p = f'{DST}/decor/{t}'
    if os.path.exists(p):
        os.remove(p)

print('Origen superpoder (locura):', os.path.getsize(f'{LOC}/superpoder.webp'), 'B')
print(f"{'fichero':24s} {'tamaño':>10s} {'dimensión'}")
for n, dim, b in hechos:
    print(f'{n:24s} {b:>10,} {dim[0]}x{dim[1]}')
tot = sum(os.path.getsize(os.path.join(r, f))
          for r, _, fs in os.walk(DST) for f in fs)
print('TOTAL carpeta assets:', f'{tot:,}', 'B')

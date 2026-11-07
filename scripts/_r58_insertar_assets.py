#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.50 · FASE 52 (r58) — inserta los assets EMBEBIDOS del SÚPER
CLONACIÓN y de la VOZ DEL SELECTOR en src/game/core/c12_pingponggame.js:

  VOCES DEL SELECTOR (nombres cortos ES/EN + «Sin poder»):
    VOZ_SEL_MEGA / _EN      ← scripts/_r58/sel_mega_{es,en}.mp3
    VOZ_SEL_EFECTO / _EN    ← scripts/_r58/sel_efecto_{es,en}.mp3
    VOZ_SEL_IMAN / _EN      ← scripts/_r58/sel_iman_{es,en}.mp3
    VOZ_SEL_PORTAL / _EN    ← scripts/_r58/sel_portal_{es,en}.mp3
    VOZ_SEL_CLON / _EN      ← scripts/_r58/sel_clon_{es,en}.mp3
    VOZ_SEL_NADA / _EN      ← scripts/_r58/sel_nada_{es,en}.mp3
  CONCESIÓN + ETIQUETA del SÚPER CLONACIÓN:
    VOZ_PODER_CLON / _EN    ← scripts/_r58/voz_clon_{es,en}.mp3
    PNG_PODER_CLON          ← upload/SuperPala_Clon.png (etiqueta del dueño)

Y el SUELO NUEVO del HALL (petición del dueño, r58):
    upload/suelo.jpg (390.326 B) → public/assets/hall/suelo.jpg

Idempotente: los placeholders se rellenan UNA vez; lo ya hecho no se rehace."""
import base64
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src' / 'game' / 'core' / 'c12_pingponggame.js'
P = RAIZ / 'scripts' / '_r58'

PARES = [
    # (CONSTANTE, PLACEHOLDER en c12, fichero, mime)
    ('VOZ_SEL_MEGA', 'SEL_VOZ_MEGA', 'sel_mega_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_MEGA_EN', 'SEL_VOZ_MEGA_EN', 'sel_mega_en.mp3', 'audio/mpeg'),
    ('VOZ_SEL_EFECTO', 'SEL_VOZ_EFECTO', 'sel_efecto_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_EFECTO_EN', 'SEL_VOZ_EFECTO_EN', 'sel_efecto_en.mp3', 'audio/mpeg'),
    ('VOZ_SEL_IMAN', 'SEL_VOZ_IMAN', 'sel_iman_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_IMAN_EN', 'SEL_VOZ_IMAN_EN', 'sel_iman_en.mp3', 'audio/mpeg'),
    ('VOZ_SEL_PORTAL', 'SEL_VOZ_PORTAL', 'sel_portal_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_PORTAL_EN', 'SEL_VOZ_PORTAL_EN', 'sel_portal_en.mp3', 'audio/mpeg'),
    ('VOZ_SEL_CLON', 'SEL_VOZ_CLON', 'sel_clon_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_CLON_EN', 'SEL_VOZ_CLON_EN', 'sel_clon_en.mp3', 'audio/mpeg'),
    ('VOZ_SEL_NADA', 'SEL_VOZ_NADA', 'sel_nada_es.mp3', 'audio/mpeg'),
    ('VOZ_SEL_NADA_EN', 'SEL_VOZ_NADA_EN', 'sel_nada_en.mp3', 'audio/mpeg'),
    ('VOZ_PODER_CLON', 'PODER_VOZ_CLON', 'voz_clon_es.mp3', 'audio/mpeg'),
    ('VOZ_PODER_CLON_EN', 'PODER_VOZ_CLON_EN', 'voz_clon_en.mp3', 'audio/mpeg'),
    ('PNG_PODER_CLON', 'PODER_PNG_CLON', RAIZ / 'upload' / 'SuperPala_Clon.png', 'image/png'),
]

txt = C12.read_text(encoding='utf-8')
fallos = 0
for nombre, ph, fich, mime in PARES:
    src = P / fich if not isinstance(fich, Path) else fich
    uri = 'data:' + mime + ';base64,' + base64.b64encode(src.read_bytes()).decode('ascii')
    pat = "const " + nombre + " = '__" + ph + "__';"
    if pat in txt:
        txt = txt.replace(pat, "const " + nombre + " = '" + uri + "';", 1)
        print(f'  ✓ {nombre} ← {Path(fich).name} ({src.stat().st_size:,} B)')
    elif ("'" + uri + "'") in txt:
        print(f'  = {nombre} ya insertado')
    else:
        print(f'  ✗ {nombre}: placeholder no encontrado ({pat[:48]}…)')
        fallos += 1

if fallos:
    print('VOCES/ASSETS r58: FALLOS', fallos)
    sys.exit(1)
C12.write_text(txt, encoding='utf-8')
print('— SUELO del HALL ← upload/suelo.jpg (nueva versión del dueño)…')
dst = RAIZ / 'public' / 'assets' / 'hall' / 'suelo.jpg'
shutil.copyfile(RAIZ / 'upload' / 'suelo.jpg', dst)
print(f'  ✓ suelo.jpg ({dst.stat().st_size:,} B)')
print('ASSETS r58: OK')

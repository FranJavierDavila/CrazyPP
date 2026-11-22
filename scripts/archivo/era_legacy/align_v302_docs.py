#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alinea el Taller (editor) y la guía con la V3.0.2 y actualiza las filas del README."""
import shutil, subprocess, pathlib

# ---------- 1 · EDITOR: del zip servido → V3.0.2 → re-zip ----------
work = pathlib.Path('/tmp/edwork')
shutil.rmtree(work, ignore_errors=True)
work.mkdir(parents=True)
subprocess.run(['unzip', '-o', '-q', '/home/z/my-project/public/descargas/editor-campeonatos.zip', '-d', str(work)], check=True)
idx = work / 'index.html'
txt = idx.read_text(encoding='utf-8')

callout_old = ('✨ <b>Novedad V3.0 «PRO TRAINING»:</b> el juego estrena un centro de entrenamiento '
               'con 5 áreas profesionales y pieles de pala. Las cajas que genera este Taller siguen '
               'siendo válidas tal cual — el entrenamiento nuevo vive en su propio módulo y no toca a los campeonatos.')
callout_new = ('✨ <b>Novedad V3.0.2 «PRO TRAINING»:</b> el juego estrena un centro de entrenamiento '
               'con 5 áreas profesionales y pieles de pala — ya pulido con los fixes de las pruebas en el casco '
               '(metrónomo, pase bajo y zonas bien visibles). Las cajas que genera este Taller siguen '
               'siendo válidas tal cual — el entrenamiento nuevo vive en su propio módulo y no toca a los campeonatos.')
assert txt.count(callout_old) == 1, 'callout del hero no encontrado'
txt = txt.replace(callout_old, callout_new)

n = txt.count('V3.0')
assert n == 9, f'esperaba 9 menciones V3.0, hay {n}'
txt = txt.replace('V3.0', 'V3.0.2')
idx.write_text(txt, encoding='utf-8')
print('editor: 9 menciones → V3.0.2 + callout al día')

# re-zip servido + sincroniza el build interno que quedó viejo
subprocess.run(['zip', '-q', '-j', '/home/z/my-project/public/descargas/editor-campeonatos.zip', str(idx)], check=True)
shutil.copy(idx, '/home/z/my-project/download/editor-campeonatos/index.html')
print('editor: zip re-sellado y build interno sincronizado')

# ---------- 2 · GUÍA HTML: etiquetas a V3.0.2 + nota de fixes ----------
g = pathlib.Path('/home/z/my-project/public/descargas/guia-campeonatos-crazy-pingpong.html')
gt = g.read_text(encoding='utf-8')
g_edits = [
    ('<title>CRAZY PING PONG · Guía sin tecnicismos · V3.0</title>',
     '<title>CRAZY PING PONG · Guía sin tecnicismos · V3.0.2</title>'),
    ('<div class="cover-tag">Guía sin tecnicismos&nbsp;· V3.0</div>',
     '<div class="cover-tag">Guía sin tecnicismos&nbsp;· V3.0.2</div>'),
    ('<span>Meta Quest 3&nbsp;· V3.0</span>',
     '<span>Meta Quest 3&nbsp;· V3.0.2</span>'),
    ('<div class="c-t">&#10024; Novedad en el juego &mdash; la V3.0 &laquo;PRO TRAINING&raquo;</div>',
     '<div class="c-t">&#10024; Novedad en el juego &mdash; el PRO TRAINING de la V3.0.2</div>'),
    ('La versión actual del juego, la <strong>V3.0</strong>, estrena un <strong>centro de entrenamiento</strong>',
     'La versión actual del juego, la <strong>V3.0.2</strong>, estrena un <strong>centro de entrenamiento</strong> '
     '&mdash; ya pulido con dos rondas de pruebas en el casco: V3.0.1 arregló el desfase de las marcas con la bola '
     'y V3.0.2 el metrónomo, el pase bajo y la visibilidad de las zonas.'),
    ('<div class="e-id">Crazy Ping Pong&nbsp;· Guía sin tecnicismos&nbsp;· V3.0</div>',
     '<div class="e-id">Crazy Ping Pong&nbsp;· Guía sin tecnicismos&nbsp;· V3.0.2</div>'),
]
for old, new in g_edits:
    assert gt.count(old) == 1, f'ancla guía no única: {old[:60]!r}'
    gt = gt.replace(old, new)
g.write_text(gt, encoding='utf-8')
print('guía HTML: 6 etiquetas → V3.0.2 + nota de fixes')

# ---------- 3 · README ×2: filas del Taller, guía y RELEASE ----------
for p in ['/home/z/my-project/download/README.md', '/home/z/my-project/public/descargas/README.md']:
    rt = pathlib.Path(p).read_text(encoding='utf-8')
    r_edits = [
        ('| `RELEASE-V3.0.txt` | **Notas oficiales de la V3.0.1** selladas: contenido, qué añade, ADDENDUM V3.0.1 con los 3 fixes del casco, verificación e historial de tamaños |',
         '| `RELEASE-V3.0.txt` | **Notas oficiales de la V3.0.2** selladas: contenido, qué añade, ADDENDUM 1 (fixes del casco) + ADDENDUM 2 (metrónomo, pase bajo, jueces y zonas), verificación a 240 Hz e historial de tamaños |'),
        ('| `editor-campeonatos.zip` | **El Taller**: editor de campeonatos (asistente de 7 fases), actualizado a V3.0 |',
         '| `editor-campeonatos.zip` | **El Taller**: editor de campeonatos (asistente de 7 fases), alineado con la V3.0.2 |'),
        ('| `guia-campeonatos-crazy-pingpong.pdf` | **Guía maquetada sin tecnicismos** (14 páginas, V3.0) |',
         '| `guia-campeonatos-crazy-pingpong.pdf` | **Guía maquetada sin tecnicismos** (14 páginas, V3.0.2) |'),
        ('| `guia-campeonatos-crazy-pingpong.html` | La misma guía en HTML autónomo (V3.0) |',
         '| `guia-campeonatos-crazy-pingpong.html` | La misma guía en HTML autónomo (V3.0.2) |'),
    ]
    for old, new in r_edits:
        assert rt.count(old) == 1, f'ancla README no única en {p}: {old[:60]!r}'
        rt = rt.replace(old, new)
    pathlib.Path(p).write_text(rt, encoding='utf-8')
    print('README al día:', p)

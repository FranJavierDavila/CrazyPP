#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_editor_ugc.py — ensambla EL TALLER UGC (r85).
   scripts/editor_ugc_src/{plantilla.html, estilo.css, cuerpo.html, app.js}
   → public/ugc/index.html (standalone, sin dependencias).
   Sanity: llaves balanceadas en app.js + placeholder del CSS + tamaño final."""
import os, sys, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, 'scripts', 'editor_ugc_src')
DEST = os.path.join(RAIZ, 'public', 'ugc', 'index.html')

plantilla = open(os.path.join(SRC, 'plantilla.html'), encoding='utf-8').read()
css = open(os.path.join(SRC, 'estilo.css'), encoding='utf-8').read()
cuerpo = open(os.path.join(SRC, 'cuerpo.html'), encoding='utf-8').read()
app = open(os.path.join(SRC, 'app.js'), encoding='utf-8').read()

# sanity 1: llaves balanceadas (fuera de cadenas es heurística, pero sirve de guardia)
for nombre, texto in [('estilo.css', css), ('app.js', app)]:
    if texto.count('{') != texto.count('}'):
        print('FALLO: llaves desbalanceadas en %s ({ %d vs } %d)' % (nombre, texto.count('{'), texto.count('}')))
        sys.exit(1)
    if texto.count('(') != texto.count(')'):
        print('FALLO: paréntesis desbalanceados en %s' % nombre)
        sys.exit(1)
# sanity 2: sin secretos
for patron in ('github_pat_', 'cfut_', 'CLAVE', 'password'):
    if patron in app or patron in cuerpo:
        print('FALLO: posible secreto (%s) en las fuentes del editor' % patron)
        sys.exit(1)

html = plantilla.replace('/* __CSS__ */', css).replace('<!-- __CUERPO__ -->', cuerpo).replace('/* __APP__ */', app)
resto = re.findall(r'__(?:CSS|CUERPO|APP)__', html)
if resto:
    print('FALLO: placeholders sin sustituir:', resto)
    sys.exit(1)
os.makedirs(os.path.dirname(DEST), exist_ok=True)
open(DEST, 'w', encoding='utf-8').write(html)
print('OK EL TALLER UGC → %s (%d B)' % (os.path.relpath(DEST, RAIZ), len(html.encode("utf-8"))))

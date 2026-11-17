#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actualiza el hash del re-sellado final (build con sello en pantalla) en
RELEASE (2 copias), README y page.tsx. Anclas con assert de unicidad."""

NEW = 'dd86d7344118f2f2ac61d7988607750096c07c7a361c160bb23e2a3ed06f74e1'
OLD = '208f9b2631dffd41c2cd72ad20798f723d76cbf00703358f4381a35b92bd20d1'

RELEASES = [
    '/home/z/my-project/download/RELEASE-V3.0.txt',
    '/home/z/my-project/public/descargas/RELEASE-V3.0.txt',
]

# RELEASE: hash de cabecera + hash del addendum (se re-sella tras añadir el sello en pantalla)
REL_EDITS = [
    ("   - SHA256: " + OLD, "   - SHA256: " + NEW),
    ("NUEVO HASH DEL ZIP: " + OLD,
     "RE-SELLO FINAL (build con sello de versión en pantalla): " + NEW +
     "\n(208f9b26… fue el primer re-sello de la V3.0.1; el definitivo añade el\n"
     "sello «V3.0.1» visible en la portada 2D y en el menú VR)"),
]

READMES = ['/home/z/my-project/download/README.md', '/home/z/my-project/public/descargas/README.md']
READ_EDITS = [("Hash SHA256 de la build V3.0.1 (208f9b26…)", "Hash SHA256 de la build V3.0.1 (dd86d734…)")]

PAGE = '/home/z/my-project/src/app/descargas/page.tsx'
PAGE_EDITS = [
    ("SHA256 208f9b26…", "SHA256 dd86d734…"),
    ("Hash SHA256 de la build V3.0.1 (208f9b26…)", "Hash SHA256 de la build V3.0.1 (dd86d734…)"),
]

def apply(path, edits):
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    for old, new in edits:
        assert txt.count(old) == 1, f'ancla no única ({txt.count(old)}) en {path}: {old[:60]}'
        txt = txt.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(txt)
    print('OK', path)

for p in RELEASES:
    apply(p, REL_EDITS)
for p in READMES:
    apply(p, READ_EDITS)
apply(PAGE, PAGE_EDITS)

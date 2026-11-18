#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Elimina la entrada duplicada del TOC: add_toc_placeholders escribe la
primera entrada como hipervínculo con PAGEREF vacío Y además la inyecta
plana; nos quedamos con la plana (lleva número de página visible).
Uso: python3 patch_toc_dupe.py <file.docx>
"""
import re, sys, zipfile, shutil, tempfile, os

SRC = sys.argv[1]
tmp = tempfile.mkdtemp()
with zipfile.ZipFile(SRC) as z:
    z.extractall(tmp)

doc_path = os.path.join(tmp, "word", "document.xml")
doc = open(doc_path, encoding="utf-8").read()

# campo TOC: begin → instrText 'TOC' → separate → [párrafo hyperlink duplicado]
m = re.search(r'PAGEREF _Toc1', doc)
if not m:
    print("sin PAGEREF _Toc1: nada que hacer")
    sys.exit(0)

# párrafo completo que contiene ese PAGEREF y el anchor _Toc1
p_start = doc.rfind("<w:p>", 0, m.start())
p_start2 = doc.rfind("<w:p ", 0, m.start())
p_start = max(p_start, p_start2)
p_end = doc.find("</w:p>", m.end()) + len("</w:p>")
frag = doc[p_start:p_end]
if 'w:anchor="_Toc1"' not in frag or 'PAGEREF _Toc1' not in frag:
    print("estructura inesperada: no se toca")
    sys.exit(0)

doc = doc[:p_start] + doc[p_end:]
open(doc_path, "w", encoding="utf-8").write(doc)
print("eliminada entrada duplicada _Toc1 (hipervínculo con PAGEREF vacío)")

out = SRC + ".tmp"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(tmp):
        for fn in files:
            full = os.path.join(root, fn)
            z.write(full, os.path.relpath(full, tmp))
shutil.move(out, SRC)
shutil.rmtree(tmp)
print("OK", SRC)

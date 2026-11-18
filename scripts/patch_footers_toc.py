#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parche post-generación del informe docx (compatibilidad WPS/Word):
 1) elimina <w:pgNumType/> vacíos de document.xml (confunden a WPS)
 2) parchea el instrText de cada pie: sección 2 (índice) → PAGE \\* ROMAN,
    sección 3 (cuerpo) → PAGE \\* arabic  (WPS ignora pgNumType fmt)
Uso: python3 patch_footers_toc.py <file.docx>
"""
import re, sys, zipfile, shutil, tempfile, os

SRC = sys.argv[1]
tmp = tempfile.mkdtemp()
with zipfile.ZipFile(SRC) as z:
    z.extractall(tmp)

doc_path = os.path.join(tmp, "word", "document.xml")
with open(doc_path, encoding="utf-8") as f:
    doc = f.read()

# 1) pgNumType vacíos fuera
doc = doc.replace("<w:pgNumType/>", "")

# 2) mapear footerReference -> archivo, en orden de secciones
rels_path = os.path.join(tmp, "word", "_rels", "document.xml.rels")
with open(rels_path, encoding="utf-8") as f:
    rels = f.read()
rel_map = dict(re.findall(r'<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels))

sect_prs = re.findall(r"<w:sectPr[ >].*?</w:sectPr>", doc, re.S)
print("secciones:", len(sect_prs))
refs = []  # (orden_seccion, archivo_footer)
for i, sp in enumerate(sect_prs):
    m = re.search(r'<w:footerReference w:type="default" r:id="([^"]+)"', sp)
    refs.append((i, rel_map.get(m.group(1), "") if m else ""))
print("footers por sección:", refs)

def patch_footer(fname, fmt):
    path = os.path.join(tmp, "word", os.path.basename(fname))
    with open(path, encoding="utf-8") as f:
        xml = f.read()
    xml2 = re.sub(r"(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)",
                  r"\1 PAGE \\* " + fmt + r" \\* MERGEFORMAT \2", xml)
    xml2 = re.sub(r'(<w:fldSimple w:instr=")\s*PAGE\s*(")',
                  r"\1 PAGE \\* " + fmt + r" \\* MERGEFORMAT \2", xml2)
    if xml2 != xml:
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml2)
        print("parcheado", os.path.basename(fname), "->", fmt)

# sección 1 = portada (sin pie) · sección 2 = índice (ROMAN) · sección 3 = cuerpo (arabic)
for idx, fname in refs:
    if not fname:
        continue
    if idx == 1:
        patch_footer(fname, "ROMAN")
    elif idx == 2:
        patch_footer(fname, "arabic")

with open(doc_path, "w", encoding="utf-8") as f:
    f.write(doc)

out = SRC + ".tmp"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(tmp):
        for fn in files:
            full = os.path.join(root, fn)
            z.write(full, os.path.relpath(full, tmp))
shutil.move(out, SRC)
shutil.rmtree(tmp)
print("OK parche", SRC)

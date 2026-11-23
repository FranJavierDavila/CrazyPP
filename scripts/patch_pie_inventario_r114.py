#!/usr/bin/env python3
"""patch_pie_r113.py — post-proceso WPS del docx (toc.md § Footer Field Instruction):
  · mapea cada sectPr de document.xml a su footer via rels
  · sección 2 (Índice, romanos): PAGE → PAGE \\* ROMAN \\* MERGEFORMAT
  · sección 3 (cuerpo, arábigos): PAGE → PAGE \\* arabic \\* MERGEFORMAT
  · elimina <w:pgNumType/> vacío de la portada
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

DOCX = Path('/home/z/my-project/download/Inventario_arte_menu_CrazyPP_r114.docx')
TMP = Path('/tmp/patch_pie_r113')

if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir()
with zipfile.ZipFile(DOCX) as z:
    z.extractall(TMP)

doc = (TMP / 'word/document.xml').read_text(encoding='utf-8')
doc = doc.replace('<w:pgNumType/>', '')

# sectPr en orden: 1=portada, 2=índice (ROMAN), 3=cuerpo (arabic)
sect_footers = re.findall(r'<w:footerReference w:type="default" r:id="(rId\d+)"/>', doc)
rels = (TMP / 'word/_rels/document.xml.rels').read_text(encoding='utf-8')
rid_a_target = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"', rels))
formatos = ['ROMAN', 'arabic']   # por orden de aparición: índice, cuerpo
vistos = 0
for rid in sect_footers:
    target = rid_a_target.get(rid)
    if not target or vistos >= 2:
        continue
    f = TMP / 'word' / target
    xml = f.read_text(encoding='utf-8')
    fmt = formatos[vistos]
    xml2, n = re.subn(r'(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)',
                      rf'\1 PAGE \\* {fmt} \\* MERGEFORMAT \2', xml)
    if n:
        f.write_text(xml2, encoding='utf-8')
        print(f'  · {target}: {n} campo(s) PAGE → \\* {fmt}')
    vistos += 1

(TMP / 'word/document.xml').write_text(doc, encoding='utf-8')

salida = DOCX.with_suffix('.tmp.docx')
with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(TMP.rglob('*')):
        if f.is_file():
            z.write(f, f.relative_to(TMP).as_posix())
shutil.move(salida, DOCX)
print('✓ pie de página parcheado y pgNumType vacío eliminado')

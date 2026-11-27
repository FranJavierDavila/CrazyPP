#!/usr/bin/env python3
"""fix_toc_dup_r114.py — elimina la entrada cacheada duplicada del campo TOC.
add_toc_placeholders inyecta 26 entradas; el campo TOC conservaba además la
entrada cacheada del primer título (hipervínculo con PAGEREF _Toc1), por lo
que «1 · Resumen ejecutivo» aparecía dos veces. Word regenera el resultado
del campo al actualizar, así que retirar la cache es seguro."""
import re
import shutil
import zipfile
from pathlib import Path

DOCX = Path('/home/z/my-project/download/Propuesta_modo_espectador_CrazyPP_r115.docx')
TMP = Path('/tmp/fix_toc_r114')

if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir()
with zipfile.ZipFile(DOCX) as z:
    z.extractall(TMP)

doc = (TMP / 'word/document.xml').read_text(encoding='utf-8')
# primera entrada cacheada dentro del resultado del campo TOC (antes de 'end')
m = re.search(r'<w:hyperlink [^>]*w:anchor="_Toc1">.*?</w:hyperlink>', doc, re.S)
if m:
    doc = doc[:m.start()] + doc[m.end():]
    print('✓ entrada cacheada duplicada eliminada del campo TOC')
else:
    print('· no se encontró entrada cacheada (nada que corregir)')

# compactar el espaciado de las 26 entradas inyectadas para que el índice
# quepa en una sola página (antes/después 120/60 → 40/20)
doc, n_esp = re.subn(r'<w:spacing w:before="120" w:after="60"/>',
                     '<w:spacing w:before="40" w:after="20"/>', doc)
print(f'✓ {n_esp} entradas del índice compactadas')

(TMP / 'word/document.xml').write_text(doc, encoding='utf-8')
salida = DOCX.with_suffix('.tmp.docx')
with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(TMP.rglob('*')):
        if f.is_file():
            z.write(f, f.relative_to(TMP).as_posix())
shutil.move(salida, DOCX)
print('✓ docx reconstruido')

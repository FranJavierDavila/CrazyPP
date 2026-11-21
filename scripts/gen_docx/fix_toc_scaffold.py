#!/usr/bin/env python3
"""fix_toc_scaffold.py — elimina la entrada-fantasma del scaffold del TOC.

docx-js TableOfContents genera el campo así:
  begin + instrText(TOC) + separate + [hyperlink "1. <primer H1>" + PAGEREF sin
  resultado]   ← párrafo scaffold: se ve como línea con texto y SIN página
y add_toc_placeholders inserta las 12 entradas reales DESPUÉS → la primera
sección del índice aparece dos veces.

Arreglo: borra el párrafo scaffold y re-inyecta los tres runs (begin,
instrText, separate) al PRINCIPIO del primer placeholder, de modo que el
campo abra sobre la entrada con página y el refresco de Word siga
funcionando (los placeholders quedan dentro del resultado del campo).

Uso: python3 fix_toc_scaffold.py <docx>
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path


def arregla(ruta: str) -> None:
    p = Path(ruta)
    tmp = p.with_suffix(".tmp.docx")
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8")
        nombres = z.namelist()

    # 1 · localiza el párrafo scaffold: pStyle TOC1 + fldChar begin + instrText TOC
    #     + separate + hyperlink _Toc1 (primer anchor de la skill)
    patron = re.compile(
        r'<w:p><w:pPr><w:pStyle w:val="TOC1"/>.*?'
        r'<w:fldChar w:fldCharType="begin"[^/]*/>.*?'
        r'<w:instrText[^>]*>TOC[^<]*</w:instrText>.*?'
        r'<w:fldChar w:fldCharType="separate"/></w:r>'
        r'<w:hyperlink[^>]*>.*?</w:hyperlink></w:p>',
        re.S,
    )
    m = patron.search(xml)
    if not m:
        print("scaffold no encontrado — nada que hacer")
        return
    scaffold = m.group(0)

    # 2 · extrae los tres runs estructurales del campo (begin, instrText, separate)
    runs = re.findall(r'<w:r>(?:(?!</w:r>).)*?(?:fldChar|instrText)(?:(?!</w:r>).)*?</w:r>', scaffold, re.S)
    opens = [r for r in runs if 'fldCharType="begin"' in r or "<w:instrText" in r or 'fldCharType="separate"' in r]
    if len(opens) < 3:
        sys.exit(f"✗ esperaba 3 runs estructurales, encontré {len(opens)}")
    apertura = "".join(opens[:3])

    # 3 · borra el párrafo scaffold
    xml2 = xml.replace(scaffold, "", 1)

    # 4 · inyecta la apertura al inicio del primer placeholder (el siguiente
    #     <w:p> con pStyle TOC1 tras el borrado)
    j = xml2.find('<w:pStyle w:val="TOC1"/>', m.start())
    if j < 0:
        sys.exit("✗ no encontré el primer placeholder TOC1")
    # el <w:p> que lo contiene: retrocede hasta '<w:p>' más cercano
    ini = xml2.rfind("<w:p>", 0, j)
    punto = ini + len("<w:p>")
    xml2 = xml2[:punto] + apertura + xml2[punto:]

    # 5 · reescribe el zip
    with zipfile.ZipFile(p) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in nombres:
            datos = zin.read(n)
            if n == "word/document.xml":
                datos = xml2.encode("utf-8")
            zout.writestr(n, datos)
    shutil.move(tmp, p)
    print(f"OK · scaffold eliminado y campo re-anclado en {p.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("uso: python3 fix_toc_scaffold.py <docx>")
    arregla(sys.argv[1])

#!/usr/bin/env python3
"""Instalador final de fuentes para el pipeline de impresión de Chromium:
1. Toma los subsets latin/latin-ext de fonts.css (Baloo 2, Nunito Sans).
2. Congela las fuentes VARIABLES (fvar) a instancias estáticas en el peso CSS.
3. Normaliza name/OS2/macStyle (familia limpia, peso real, bits correctos).
4. Instala en ~/.local/share/fonts + fc-cache."""
import os, re, glob
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SRC = "/home/z/my-project/scripts/manual_editor_src"
OUT = os.path.expanduser("~/.local/share/fonts/crazypp_manual")
for f in glob.glob(OUT + "/*.ttf"):
    os.remove(f)

css = open(f"{SRC}/fonts.css", encoding="utf-8").read()
faces = re.findall(r"@font-face\s*\{[^}]*\}", css)

def subfamilia(weight, style):
    if style == "italic": return "Italic"
    return {400: "Regular", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}[weight]

FAMS = {"Baloo 2": "Baloo2", "Nunito Sans": "NunitoSans"}
keep = variables = estaticas = 0
for i, f in enumerate(faces):
    fam = re.search(r"font-family:\s*'([^']+)'", f).group(1)
    weight = int(re.search(r"font-weight:\s*(\d+)", f).group(1))
    st = re.search(r"font-style:\s*(\w+)", f)
    style = st.group(1) if st else "normal"
    ur = re.search(r"unicode-range:\s*([^;]+);", f).group(1)
    if not (ur.startswith("U+0000-00FF") or ur.startswith("U+0100-02BA")):
        continue  # solo latin y latin-ext (español)

    woff = f"{SRC}/fonts/font_{i:02d}.woff2"
    t = TTFont(woff)
    t.flavor = None

    # congelar ejes variables al peso del CSS (wght) y defaults en el resto
    if "fvar" in t:
        ejes = {a.axisTag: (weight if a.axisTag == "wght" else a.defaultValue) for a in t["fvar"].axes}
        instantiateVariableFont(t, ejes, inplace=True)
        assert "fvar" not in t, "fvar sigue presente"
        variables += 1
    else:
        estaticas += 1

    sub = subfamilia(weight, style)
    bold = weight >= 700 and style != "italic"
    ital = style == "italic"
    os2 = t["OS/2"]; os2.usWeightClass = weight
    os2.fsSelection = (os2.fsSelection & ~97) | (1 if ital else (32 if bold else 64))
    t["head"].macStyle = (t["head"].macStyle & ~3) | (1 if bold else 0) | (2 if ital else 0)
    name = t["name"]
    for nid, val in ((1, fam), (2, sub), (4, f"{fam} {sub}"), (6, f"{FAMS[fam]}-{sub}")):
        name.setName(val, nid, 3, 1, 0x409)
    name.removeNames(nameID=16); name.removeNames(nameID=17)

    t.save(f"{OUT}/{FAMS[fam]}-{sub}-{i:02d}.ttf")
    keep += 1

print(f"Instalados {keep} TTF estáticos ({variables} congelados desde variable, {estaticas} ya estáticos)")

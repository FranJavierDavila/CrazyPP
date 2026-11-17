#!/usr/bin/env python3
"""Normaliza los TTF de subsets de Google para fontconfig:
- familia -> 'Baloo 2' / 'Nunito Sans'
- usWeightClass real (600/700/800 / 400/600/700/900) + bits Bold de head/OS2
- subfamily por peso y estilo (Regular/SemiBold/Bold/ExtraBold/Black/Italic)
Después: fc-cache y el pipeline de impresión de Chromium las resuelve por sistema."""
import os, re
from fontTools.ttLib import TTFont

SRC = "/home/z/my-project/scripts/manual_editor_src"
FDIR = os.path.join(SRC, "fonts")
OUT = os.path.expanduser("~/.local/share/fonts/crazypp_manual")
os.makedirs(OUT, exist_ok=True)

css = open(os.path.join(SRC, "fonts.css"), encoding="utf-8").read()
faces = re.findall(r"@font-face\s*\{[^}]*\}", css)

def subfamilia(weight, style):
    if style == "italic":
        return "Italic"
    return {400: "Regular", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}[weight]

familias = {"Baloo 2": "Baloo2", "Nunito Sans": "NunitoSans"}
n = 0
for i, f in enumerate(faces):
    fam = re.search(r"font-family:\s*'([^']+)'", f).group(1)
    weight = int(re.search(r"font-weight:\s*(\d+)", f).group(1))
    style = (re.search(r"font-style:\s*(\w+)", f) or re.search(r"font-style:\s*(\w+)", f)).group(1) if "font-style" in f else "normal"
    st = re.search(r"font-style:\s*(\w+)", f)
    style = st.group(1) if st else "normal"
    woff = os.path.join(FDIR, f"font_{i:02d}.woff2")
    if not os.path.exists(woff):
        continue
    t = TTFont(woff)
    t.flavor = None
    sub = subfamilia(weight, style)
    bold = weight >= 700 and style != "italic"
    ital = style == "italic"

    # OS/2: peso real + bits de selección
    os2 = t["OS/2"]
    os2.usWeightClass = weight
    fs = os2.fsSelection
    fs &= ~0b1100001  # limpia ITALIC(0), BOLD(5), REGULAR(6) = 97
    if ital: fs |= 0b1
    elif bold: fs |= 0b100000
    else: fs |= 0b1000000
    os2.fsSelection = fs
    try:
        os2.fsType = 0
    except Exception:
        pass

    # head.macStyle
    head = t["head"]
    head.macStyle = (head.macStyle & ~0b11) | (0b1 if bold else 0) | (0b10 if ital else 0)

    # name table
    name = t["name"]
    familia = familias[fam]
    setName = lambda nid, val: name.setName(val, nid, 3, 1, 0x409)
    setName(1, fam)                # familia
    setName(2, sub)                # subfamilia
    setName(4, f"{fam} {sub}")     # nombre completo
    setName(6, f"{familia}-{sub}")  # PostScript
    # elimina IDs 16/17 tipográficos (evita 'Nunito Sans 12pt ExtraLight')
    name.removeNames(nameID=16)
    name.removeNames(nameID=17)

    destino = os.path.join(OUT, f"{familia}-{sub}-{i:02d}.ttf")
    t.save(destino)
    n += 1
print(f"Normalizados e instalados {n} TTF en {OUT}")

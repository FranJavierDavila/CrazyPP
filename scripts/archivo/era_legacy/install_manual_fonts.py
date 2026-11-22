#!/usr/bin/env python3
"""Descomprime los subsets woff2 a TTF y los instala como fuentes de sistema.
Así el pipeline de impresión de Chromium (que en este entorno no incrusta webfonts)
resuelve 'Baloo 2' y 'Nunito Sans' vía fontconfig y las incrusta en el PDF."""
import os, re, sys
from fontTools.ttLib import TTFont

SRC = "/home/z/my-project/scripts/manual_editor_src"
FDIR = os.path.join(SRC, "fonts")
OUT = os.path.expanduser("~/.local/share/fonts/crazypp_manual")
os.makedirs(OUT, exist_ok=True)

# mapa de subset -> sufijo descriptivo a partir del unicode-range de fonts.css
css = open(os.path.join(SRC, "fonts.css"), encoding="utf-8").read()
faces = re.findall(r"@font-face\s*\{[^}]*\}", css)
print("faces:", len(faces))

instalados = []
for i in range(len(os.listdir(FDIR))):
    woff = os.path.join(FDIR, f"font_{i:02d}.woff2")
    if not os.path.exists(woff):
        continue
    f = TTFont(woff)
    f.flavor = None  # descomprime a TTF
    fam = f["name"].getDebugName(1) or "?"
    sub = f["name"].getDebugName(2) or "?"
    nombre = f"font_{i:02d}_{fam.replace(' ','')}-{sub.replace(' ','')}.ttf"
    destino = os.path.join(OUT, nombre)
    f.save(destino)
    instalados.append((nombre, fam, sub))

print(f"Guardados {len(instalados)} TTF en {OUT}")
for n, fam, sub in instalados[:8]:
    print("  ", n, "|", fam, "|", sub)
print("   …")

#!/usr/bin/env python3
"""Extrae los bloques @font-face (fuentes data-URI) de la guía V2.124
para reutilizarlos en el manual del editor con la misma tipografía."""
import re, os, json

SRC = "/home/z/my-project/download/guia-campeonatos-crazy-pingpong.html"
OUT_DIR = "/home/z/my-project/scripts/manual_editor_src"
os.makedirs(OUT_DIR, exist_ok=True)

html = open(SRC, "r", encoding="utf-8").read()

faces = re.findall(r"@font-face\s*\{[^}]*\}", html)
print("Bloques @font-face encontrados:", len(faces))

info = []
css_out = []
for f in faces:
    fam = re.search(r"font-family:\s*'([^']+)'", f)
    weight = re.search(r"font-weight:\s*(\d+)", f)
    style = re.search(r"font-style:\s*(\w+)", f)
    # tamaño del data URI
    uris = re.findall(r"data:font/(\w+);base64,([A-Za-z0-9+/=]+)", f)
    size_kb = sum(len(u[1]) for u in uris) * 3 // 4 // 1024
    fam_name = fam.group(1) if fam else "?"
    w = weight.group(1) if weight else "?"
    st = style.group(1) if style else "normal"
    print(f"  - {fam_name} {w} {st} -> {size_kb} KB ({len(uris)} archivos)")
    info.append({"family": fam_name, "weight": w, "style": st, "kb": size_kb})
    # normalizar la URL relativa fonts/ -> vacía (por si acaso quedara alguna)
    f2 = f.replace("url(fonts/", "url(data:font/woff2;base64,")
    css_out.append(f2)

open(os.path.join(OUT_DIR, "fonts.css"), "w", encoding="utf-8").write("\n".join(css_out))
json.dump(info, open(os.path.join(OUT_DIR, "fonts_info.json"), "w"), indent=1)
print("Guardado:", os.path.join(OUT_DIR, "fonts.css"))

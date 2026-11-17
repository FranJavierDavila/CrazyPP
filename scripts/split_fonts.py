#!/usr/bin/env python3
"""Divide fonts.css (data-URI) en archivos .woff2 reales + fonts_ext.css con url() externa.
Motivo: html2pdf-next.js espera 'networkidle' — los data-URI no cuentan como peticiones,
los .woff2 externos sí → las fuentes están garantizadas antes del page.pdf()."""
import re, os, base64

SRC = "/home/z/my-project/scripts/manual_editor_src"
FDIR = os.path.join(SRC, "fonts")
os.makedirs(FDIR, exist_ok=True)

css = open(os.path.join(SRC, "fonts.css"), encoding="utf-8").read()
faces = re.findall(r"@font-face\s*\{[^}]*\}", css)
print("Bloques:", len(faces))

out = []
for i, f in enumerate(faces):
    m = re.search(r"url\(data:font/(\w+);base64,([A-Za-z0-9+/=]+)\)", f)
    if not m:
        print("  sin data-URI, se copia tal cual:", i); out.append(f); continue
    fmt, b64 = m.groups()
    ext = "woff2" if fmt == "woff2" else ("woff" if fmt == "woff" else "ttf")
    nombre = f"font_{i:02d}.{ext}"
    open(os.path.join(FDIR, nombre), "wb").write(base64.b64decode(b64))
    fam = re.search(r"font-family:\s*'([^']+)'", f).group(1)
    w = re.search(r"font-weight:\s*(\d+)", f)
    print(f"  {nombre} <- {fam} w{w.group(1) if w else '?'} ({len(b64)*3//4//1024} KB)")
    f2 = f.replace(m.group(0), f"url('fonts/{nombre}') format('{fmt}')")
    out.append(f2)

open(os.path.join(SRC, "fonts_ext.css"), "w", encoding="utf-8").write("\n".join(out))
print("OK -> fonts_ext.css +", len([f for f in os.listdir(FDIR)]), "archivos en fonts/")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_editor.py — Ensambla el Editor de Campeonatos de Crazy Ping Pong (V2.124)
a partir de las piezas de scripts/editor_src/ en un único index.html autónomo.

Piezas:
  head.html   → doctype, <head> con fuentes y placeholder @@STYLE@@, apertura <body> + cabecera
  style.css   → hoja de estilos
  body.html   → pantallas (home, nuevo, editor), modales y cajones
  app1.js     → datos, almacenamiento, plantillas, navegación
  app2.js     → formularios de las 7 fases
  app3.js     → revisión automática, estados, exportación (ZIP), diario, arranque

Salida: download/editor-campeonatos/index.html
"""
import pathlib, re, sys

SRC = pathlib.Path(__file__).parent / "editor_src"
OUT = pathlib.Path("/home/z/my-project/download/editor-campeonatos/index.html")

def read(name: str) -> str:
    p = SRC / name
    if not p.exists():
        sys.exit(f"Falta la pieza {p}")
    return p.read_text(encoding="utf-8")

head  = read("head.html")
style = read("style.css")
body  = read("body.html")
app1  = read("app1.js")
app2  = read("app2.js")
app3  = read("app3.js")

html = (head
        .replace("@@STYLE@@", style)
        .replace("@@BODY@@", body)
        .replace("@@APP1@@", app1)
        .replace("@@APP2@@", app2)
        .replace("@@APP3@@", app3))

# comprobaciones básicas de marcadores sin sustituir
for token in ("@@STYLE@@", "@@BODY@@", "@@APP1@@", "@@APP2@@", "@@APP3@@"):
    if token in html:
        sys.exit(f"Token sin sustituir: {token}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")

# sanity: balance de llaves en los JS concatenados (aproximado, sin strings)
for label, js in (("app1", app1), ("app2", app2), ("app3", app3)):
    stripped = re.sub(r"//[^\n]*", "", js)
    o, c = stripped.count("{"), stripped.count("}")
    print(f"{label}: llaves {o}/{c} {'OK' if o == c else '⚠️ REVISAR'}")

print(f"OK → {OUT} ({OUT.stat().st_size:,} bytes)")

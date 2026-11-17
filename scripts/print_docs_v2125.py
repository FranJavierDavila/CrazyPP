#!/usr/bin/env python3
"""Reimprime los PDFs oficiales (manual del editor + guía) tras la actualización a V2.125.

Lecciones del pipeline original (ver worklog Task 39):
 - El Chromium de este entorno NO incrusta webfonts (@font-face) en page.pdf():
   hay que imprimir desde variantes SIN @font-face para que fontconfig resuelva
   las TTF instaladas en ~/.local/share/fonts/crazypp_manual (Baloo 2 + Nunito Sans).
 - Ambos documentos usan @page { size: 720px 1020px; margin: 0; } → se imprime con
   prefer_css_page_size y márgenes 0, fondo activo.
 - El HTML entregable de la guía lleva fuentes data-URI (autohospedadas); para
   imprimir se usa una copia temporal sin @font-face (el resto es idéntico).
"""
import re, os, sys
from playwright.sync_api import sync_playwright

BASE = "/home/z/my-project"
MANUAL_HTML = os.path.join(BASE, "scripts/manual_editor_src/render3.html")
MANUAL_PDF = os.path.join(BASE, "download/manual-editor-campeonatos.pdf")
GUIA_HTML = os.path.join(BASE, "download/guia-campeonatos-crazy-pingpong.html")
GUIA_PRINT = os.path.join(BASE, "scripts/guia_v2125_print.html")
GUIA_PDF = os.path.join(BASE, "download/guia-campeonatos-crazy-pingpong.pdf")

# Variante de impresión de la guía: quitar bloques @font-face (fuentes ya en el sistema)
guia = open(GUIA_HTML, encoding="utf-8").read()
guia_sin_ff = re.sub(r"@font-face\s*{[^}]*}", "", guia)
open(GUIA_PRINT, "w", encoding="utf-8").write(guia_sin_ff)
print(f"guía variante de impresión: {len(guia_sin_ff)/1024:.0f} KB (sin @font-face)")

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 720, "height": 1020})
    for src, dst, nombre in [(MANUAL_HTML, MANUAL_PDF, "manual"),
                             (GUIA_PRINT, GUIA_PDF, "guía")]:
        page.goto(f"file://{src}", wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.pdf(path=dst, print_background=True,
                 prefer_css_page_size=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        print(f"{nombre}: {os.path.getsize(dst):,} B -> {dst}")
    browser.close()
print("PDFs regenerados")

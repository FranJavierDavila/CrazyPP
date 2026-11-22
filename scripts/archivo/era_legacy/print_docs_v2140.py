#!/usr/bin/env python3
"""Reimprime los PDFs a la V2.140 (guía + manual del editor) con Playwright.
Receta heredada de print_docs_v2138.py — CAMBIO de entorno: los @font-face
de la guía son data: URIs (woff2 incrustadas, offline), así que se CONSERVAN
para imprimir con la tipografía diseñada (Nunito Sans/Baloo 2); recortarlas
obliga al fallback DejaVu (más ancho) y desordena la paginación (20 págs)."""
import re, sys, os, subprocess
from playwright.sync_api import sync_playwright

JOBS = [
    ('/home/z/my-project/download/guia-campeonatos-crazy-pingpong.html',
     '/home/z/my-project/download/guia-campeonatos-crazy-pingpong.pdf', 16),
]
MAN_HTML = '/home/z/my-project/download/manual-editor-campeonatos.html'
MAN_PDF = '/home/z/my-project/download/manual-editor-campeonatos.pdf'
if os.path.exists(MAN_HTML):
    JOBS.append((MAN_HTML, MAN_PDF, None))

def sin_webfonts(html: str) -> str:
    return html  # fuentes data: URI: se conservan (ver cabecera)

ok = True
with sync_playwright() as p:
    browser = p.chromium.launch()
    for src, dst, esperadas in JOBS:
        html = open(src, encoding='utf-8').read()
        variante = '/tmp/print_' + os.path.basename(src)
        open(variante, 'w', encoding='utf-8').write(sin_webfonts(html))
        page = browser.new_page()
        page.goto('file://' + variante, wait_until='networkidle')
        page.emulate_media(media='print')
        page.pdf(path=dst, prefer_css_page_size=True,
                 margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'},
                 print_background=True)
        page.close()
        info = subprocess.run(['pdfinfo', dst], capture_output=True, text=True).stdout
        m = re.search(r'Pages:\s+(\d+)', info)
        npag = int(m.group(1)) if m else -1
        peso = os.path.getsize(dst)
        estado = 'OK' if (esperadas is None or npag == esperadas) else '¡PÁGINAS!'
        if esperadas is not None and npag != esperadas:
            ok = False
        print(f'{os.path.basename(dst)}: {npag} págs · {peso/1048576:.2f} MB · {estado}')
    browser.close()
sys.exit(0 if ok else 1)

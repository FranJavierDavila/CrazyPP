#!/usr/bin/env python3
"""Reimprime los PDFs de la V2.126 (guía + manual del editor) con Playwright.
Receta heredada de print_docs_v2125.py:
  - variante SIN @font-face (Chromium no incrusta webfonts; usar fuentes del
    sistema Baloo 2 + Nunito Sans en ~/.local/share/fonts/crazypp_manual)
  - prefer_css_page_size, márgenes 0, print_background
QA con poppler (pypdf falla con estos descriptores)."""
import re, sys, os, subprocess
from playwright.sync_api import sync_playwright

JOBS = [
    # (html origen, pdf destino, página esperada)
    ('/home/z/my-project/download/guia-campeonatos-crazy-pingpong.html',
     '/home/z/my-project/download/guia-campeonatos-crazy-pingpong.pdf', 16),
]
# el manual se añade a JOBS si existe
MAN_HTML = '/home/z/my-project/download/manual-editor-campeonatos.html'
MAN_PDF = '/home/z/my-project/download/manual-editor-campeonatos.pdf'
if os.path.exists(MAN_HTML):
    JOBS.append((MAN_HTML, MAN_PDF, None))

def sin_webfonts(html: str) -> str:
    """Quita TODOS los bloques @font-face para que manden las fuentes del sistema."""
    return re.sub(r'@font-face\s*\{[^}]*\}', '/* webfont quitado para imprimir */', html, flags=re.S)

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
        estado = 'OK' if (esperadas is None or npag == esperadas) else '¡PÁGINAS!rase'
        if esperadas is not None and npag != esperadas:
            ok = False
        print(f'{os.path.basename(dst)}: {npag} págs · {peso:,} B · esperadas {esperadas} · {estado}')
    browser.close()
sys.exit(0 if ok else 1)

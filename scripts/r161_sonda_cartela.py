#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161 · verificación de la CARTELA MAIN: precarga del arte, apertura del
menú, montaje de la panela única, rects de los 6 botones y CAPTURA visual."""
import os, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3015
CAPTURA = '/tmp/render/r161_cartela.png'


def serve():
    import http.server
    os.chdir(PUBLIC)
    handler = http.server.SimpleHTTPRequestHandler

    class H(handler):
        def log_message(self, *a):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    os.makedirs('/tmp/render', exist_ok=True)
    from playwright.sync_api import sync_playwright
    errs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg.wait_for_timeout(3500)
        pg.mouse.click(30, 30)
        st = pg.evaluate('''() => { const g = window.__game;
            g._uiPrecarga();
            return { cv: Object.keys(g._uiCv).length,
                     falla: Object.keys(g._uiFalla).length }; }''')
        pg.wait_for_timeout(4500)
        st2 = pg.evaluate('''() => { const g = window.__game;
            return { cv: Object.keys(g._uiCv).length,
                     falla: Object.keys(g._uiFalla).length,
                     lista: g._uiCartelaLista('Main') }; }''')
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(1800)   # fundido de entrada + FX
        fin = pg.evaluate('''() => { const g = window.__game;
            return { menuOpen: !!g.menuOpen, page: g.menuPage,
                     lados: g._menuLados, panelas: g._menuPanelas.length,
                     lista: g._uiCartelaLista('Main'),
                     ids: (g.menuRects || []).map(r => r.id),
                     nRects: (g.menuRects || []).length }; }''')
        pg.screenshot(path=CAPTURA)
        b.close()
    print('precarga inicial :', json.dumps(st))
    print('precarga 4,5 s   :', json.dumps(st2))
    print('menú abierto     :', json.dumps(fin))
    print('pageerrors       :', errs[:4] or 'ninguno')
    print('captura          :', CAPTURA, os.path.getsize(CAPTURA), 'bytes')


if __name__ == '__main__':
    main()

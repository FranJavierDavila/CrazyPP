#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161e · verificación final de la cartela: rótulos autoajustados (es),
estado _on dorado con hover forzado sobre JUGAR y click real en el rect de
MULTIJUGADOR → navega a la página multi (despachador intacto)."""
import os, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3016


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
    from playwright.sync_api import sync_playwright
    errs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg.wait_for_timeout(3200)
        pg.evaluate("() => localStorage.setItem('pp_lang', 'es')")
        pg.evaluate('() => window.__game._uiPrecarga()')
        pg.wait_for_timeout(4000)
        # 1 · cartela en castellano
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(1600)
        r1 = pg.evaluate('''() => { const g = window.__game;
            return { page: g.menuPage, panelas: g._menuPanelas.length,
                     ids: (g.menuRects || []).map(r => r.id) }; }''')
        print('cartela es:', json.dumps(r1))
        # 2 · hover forzado sobre JUGAR → estado _on dorado
        pg.evaluate('''() => { const g = window.__game;
            const i = g.menuRects.findIndex(r => r.id === 'page:jugar');
            g.menuHover = [i]; g.drawMenu(); }''')
        pg.wait_for_timeout(400)
        pg.screenshot(path='/tmp/render/r161_hover.png')
        # 3 · click real en el rect de MULTIJUGADOR (mismo camino que el
        # ray: menuClick recibe el ÍNDICE del rect, como onSelectStart)
        r3 = pg.evaluate('''() => { const g = window.__game;
            const i = g.menuRects.findIndex((x) => x.id === 'tab:multi');
            if (i < 0) return { fallo: 'sin rect' };
            g.menuClick(i, 0);
            return { click: i, page: g.menuPage }; }''')
        print('click multi:', json.dumps(r3))
        pg.wait_for_timeout(1200)
        r4 = pg.evaluate('''() => { const g = window.__game;
            return { page: g.menuPage, panelas: g._menuPanelas.length,
                     lados: g._menuLados }; }''')
        print('página multi:', json.dumps(r4))
        # 4 · volver a main por el CAMINO REAL (botón ATRÁS de la concha:
        # rect 'page:main' → menuClick por índice) → la cartela vuelve
        r5 = pg.evaluate('''() => { const g = window.__game;
            const i = g.menuRects.findIndex((x) => x.id === 'page:main');
            if (i < 0) return { fallo: 'sin ATRÁS', ids:
              (g.menuRects || []).map((r) => r.id).slice(0, 6) };
            g.menuClick(i, 0);
            return { click: i, page: g.menuPage }; }''')
        print('click ATRÁS:', json.dumps(r5))
        pg.wait_for_timeout(1300)
        r6 = pg.evaluate('''() => { const g = window.__game;
            return { page: g.menuPage, panelas: g._menuPanelas.length,
                     cartela: g._uiCartelaLista('Main'),
                     ids: (g.menuRects || []).map((r) => r.id) }; }''')
        print('vuelta a main:', json.dumps(r6))
        b.close()
    from PIL import Image
    Image.open('/tmp/render/r161_hover.png').crop(
        (455, 175, 910, 615)).resize((614, 594), Image.LANCZOS).save(
        '/tmp/render/r161_hover_zoom.png')
    print('zoom hover guardado')
    print('pageerrors:', errs[:3] or 'ninguno')


if __name__ == '__main__':
    main()

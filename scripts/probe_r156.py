#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SONDA r156 · diagnóstico paso a paso del estado del menú/perfil."""
import os, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3009


def serve():
    import http.server
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(PUBLIC)

    class H(handler):
        def log_message(self, *a):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    from playwright.sync_api import sync_playwright

    def dump(page, tag):
        s = page.evaluate('''() => {
            const g = window.__game;
            return { page: g.menuPage, tab: g._peTab || null,
                arm: g._compraArm || null,
                pf: g._perfil,
                rects: (g.menuRects || []).length,
                ids: (g.menuRects || []).filter((r) => /pavatar|pguardar|petab/.test(r.id)).slice(0, 6).map((r) => r.id),
                mon: g.stats.data.monedas,
                ls: localStorage.getItem('pp_perfil_v1') };
        }''')
        print(f'[{tag}] {s}')

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--use-gl=swiftshader'])
        ctx = browser.new_context(viewport={'width': 1280, 'height': 720},
                                  service_workers='block')
        page = ctx.new_page()
        perr = []
        page.on('pageerror', lambda e: perr.append('PE: ' + str(e)[:120]))
        page.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load', timeout=30_000)
        page.wait_for_timeout(8_000)

        page.evaluate('''() => { const g = window.__game;
            g.menuOpen = true; g.menuPage = 'main'; g.menuSec = 'match'; g.drawMenu(); }''')
        s = page.evaluate('''() => { const g = window.__game;
            return { n: (g.menuRects || []).length,
                ids: (g.menuRects || []).map((r) => r.id).slice(0, 18),
                sec: g.menuSec, pg: g.menuPage,
                nuevo: document.documentElement.innerHTML.indexOf('page:jugar') >= 0 }; }''')
        print('hub tras nav (SW bloqueado):', s)
        idx = page.evaluate('''() => {
            const g = window.__game;
            const i = (g.menuRects || []).findIndex((r) => r && r.id === 'page:perfil');
            g.menuClick(i, null);
            return i;
        }''')
        print('click page:perfil idx=', idx)
        for i in range(10):
            mp = page.evaluate('() => window.__game.menuPage + "/" + (window.__game.menuOpen ? "open" : "closed")')
            print(f'  t+{i * 150}ms menuPage={mp}')
            page.wait_for_timeout(150)
        for e in perr:
            print(e)
        browser.close()


if __name__ == '__main__':
    main()

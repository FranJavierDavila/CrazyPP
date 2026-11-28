#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r159 · sonda de arranque: carga el juego en headless, lista errores de
consola/pageerror y comprueba si window.__game llega a existir."""
import os, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3011


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
    errores = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on('console', lambda m: errores.append(
            f"[{m.type}] {m.text[:220]}") if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: errores.append(f"[pageerror] {str(e)[:220]}"))
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg.wait_for_timeout(4000)
        hay = pg.evaluate("() => ({game: !!window.__game,"
                          " menuOpen: !!(window.__game && window.__game.menuOpen)})")
        b.close()
    print(f"window.__game: {hay}")
    if errores:
        print(f"--- {len(errores)} mensajes de consola/errores ---")
        for e in errores[:15]:
            print(e)
    else:
        print("(sin errores de consola)")


if __name__ == '__main__':
    main()

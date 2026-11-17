#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chequeo global r105 · captura páginas del menú NO cubiertas por qa_r104:
join, name, gripname, rank, trainarea, hallask, tutask, optsRendi.
Sólo captura (sin checks): el análisis visual es posterior."""
import base64, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PORT = 8849
OUT = os.path.join(RAIZ, 'scripts', '_checkglobal_shots')
os.makedirs(OUT, exist_ok=True)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.join(RAIZ, 'public'), **kw)
    def log_message(self, *a):
        pass

srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

PAGINAS = ['join', 'name', 'gripname', 'rank', 'trainarea',
           'hallask', 'tutask', 'optsRendi']

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader',
                                 '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2500)
    ok = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      try { g.toggleMenu(); } catch (e) { return 'toggle: ' + e.message; }
      return g.menuOpen ? 'abierto' : 'no abre';
    }""")
    print('menú:', ok)
    for p in PAGINAS:
        d = pg.evaluate("""(pagina) => {
          const g = window.__PP_GAME;
          try { g.menuPage = pagina; g.drawMenu(); }
          catch (e) { return { err: '' + (e && e.message) }; }
          return { img: g.menuCanvas.toDataURL('image/png') };
        }""", p)
        if 'err' in (d or {}):
            print(f'  ✗ {p}: {d["err"]}')
            continue
        png = base64.b64decode(d['img'].split(',', 1)[1])
        ruta = os.path.join(OUT, 'pg_%s.png' % p)
        open(ruta, 'wb').write(png)
        print(f'  ✓ {p}: {len(png)//1024} KB')
    print('pageerrors:', len(errs), errs[:3])
    b.close()
srv.shutdown()
print('listo')

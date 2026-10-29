#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_flujo_r93.py — qué pasa tras el clic de portada (champIntro, estado, música)."""
import os, functools, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8818

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    pg.mouse.click(640, 600)          # sobre vrbtn/playEs (460,581 + 360×90)
    print('clic portada hecho')
    for t in range(5):
        pg.wait_for_timeout(2500)
        st = pg.evaluate("""() => {
          const H = window.__PP_HALLOWEEN;
          if (!H) return { H: false };
          const g = H.ctrl().game;
          const m = H.mus() ? H.mus().estado() : null;
          return { H: true, est: m,
                   ci: !!g.champIntro, ciVis: g.champIntro ? g.champIntro.group.visible : null,
                   estado: g.rules ? g.rules.state : null,
                   inHall: !!g.inHall, calib: !!g.calib,
                   xr: !!(g.renderer && g.renderer.xr && g.renderer.xr.isPresenting) };
        }""")
        print('t=%ds' % ((t + 1) * 2.5), json.dumps(st))
    # clic de nuevo (¿segundo clic sobre el botón 3D del champ intro proyectado?)
    pg.mouse.click(640, 400)
    print('segundo clic (640,400)')
    pg.wait_for_timeout(3000)
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const m = H.mus() ? H.mus().estado() : null;
      return { est: m, ci: !!g.champIntro, ciVis: g.champIntro ? g.champIntro.group.visible : null,
               estado: g.rules ? g.rules.state : null };
    }""")
    print('tras 2º clic:', json.dumps(st))
    b.close()
srv.shutdown()

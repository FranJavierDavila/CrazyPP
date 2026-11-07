#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_bso_r93.py — por qué estado().sonando es false con buffer cargado."""
import os, functools, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8815

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('console', lambda m: print('  [console]', m.text[:160]) if ('music' in m.text.lower() or 'bso' in m.text.lower()) else None)
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
        print('clic JUGAR EN VR ok')
    except Exception as e:
        pg.mouse.click(640, 600)
        print('clic fallback', e)
    for t in range(6):
        pg.wait_for_timeout(2000)
        st = pg.evaluate("""() => {
          const H = window.__PP_HALLOWEEN; if (!H) return { H: false };
          const m = H.mus() ? H.mus().estado() : null;
          const g = H.ctrl() ? H.ctrl().game : null;
          return { H: true, est: m,
                   ctx: g && g.audio && g.audio.ctx ? g.audio.ctx.state : null,
                   hidden: document.hidden,
                   vis: document.visibilityState };
        }""")
        print('t=%ds' % ((t + 1) * 2), json.dumps(st))
    b.close()
srv.shutdown()

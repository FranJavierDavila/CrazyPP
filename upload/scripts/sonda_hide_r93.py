#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_hide_r93.py — hideChampIntro(true) → ¿on() de la BSO?"""
import os, functools, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PUB = '/home/z/my-project/public'
PORT = 8819
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    r = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      if (!g.champIntro) return 'no champIntro';
      g.hideChampIntro(true);          // el efecto EXACTO del botón JUGAR (c12:4241)
      return 'hideChampIntro(true) ok';
    }""")
    print('ciHide:', r)
    for t in range(3):
        pg.wait_for_timeout(2000)
        st = pg.evaluate("""() => {
          const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
          const m = H.mus() ? H.mus().estado() : null;
          return { est: m, estado: g.rules ? g.rules.state : null };
        }""")
        print('t=%ds' % ((t + 1) * 2), json.dumps(st))
    b.close()
srv.shutdown()

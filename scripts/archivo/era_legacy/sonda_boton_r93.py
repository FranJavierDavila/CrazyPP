#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_boton_r93.py — estado del botón JUGAR EN VR en el arranque."""
import os, functools, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8816

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    for t in (1000, 2500, 4000):
        pg.wait_for_timeout(t if t == 1000 else t - (1500 if t == 2500 else 2500))
        info = pg.evaluate("""() => {
          const cand = [...document.querySelectorAll('button, a, div, span')]
            .filter(el => el.textContent && el.textContent.trim().toUpperCase().indexOf('JUGAR EN VR') >= 0
                          && el.children.length === 0);
          return cand.map(el => {
            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            const ov = el.closest('[id]');
            return { tag: el.tagName, txt: el.textContent.trim().slice(0, 30),
                     x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
                     display: cs.display, vis: cs.visibility, op: cs.opacity,
                     env: ov ? ov.id : null, envDisp: ov ? getComputedStyle(ov).display : null,
                     puntero: cs.pointerEvents };
          });
        }""")
        print('t≈%dms' % t, json.dumps(info, ensure_ascii=False))
    # intento de clic DOM directo
    ok = pg.evaluate("""() => {
      const el = [...document.querySelectorAll('button, a, div, span')]
        .find(el => el.textContent && el.textContent.trim().toUpperCase() === 'JUGAR EN VR' && el.children.length === 0);
      if (!el) return 'no está';
      el.click();
      return 'click() disparado sobre ' + el.tagName;
    }""")
    print('DOM:', ok)
    pg.wait_for_timeout(6000)
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN;
      const m = H && H.mus() ? H.mus().estado() : null;
      return { H: !!H, est: m };
    }""")
    print('tras clic DOM:', json.dumps(st))
    b.close()
srv.shutdown()

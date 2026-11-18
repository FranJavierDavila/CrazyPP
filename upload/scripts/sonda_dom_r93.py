#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_dom_r93.py — quién hay en pantalla al arrancar y dónde está JUGAR."""
import os, functools, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8817

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3500)
    st = pg.evaluate("""() => {
      const out = { overlays: [], jugars: [] };
      for (const id of ['introov', 'menu', 'portada', 'hud', 'status', 'vrbtn', 'playEs', 'playEn']) {
        const el = document.getElementById(id);
        if (!el) continue;
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        out.overlays.push({ id, display: cs.display, vis: cs.visibility, op: cs.opacity,
                            x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) });
      }
      const walk = (el) => {
        for (const n of el.childNodes) {
          if (n.nodeType === 3 && n.textContent && n.textContent.toUpperCase().indexOf('JUGAR') >= 0) {
            const p = n.parentElement;
            const r = p.getBoundingClientRect();
            out.jugars.push({ tag: p.tagName, id: p.id, cls: String(p.className).slice(0, 40),
                              txt: n.textContent.trim().slice(0, 40),
                              x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width) });
          }
          if (n.nodeType === 1) walk(n);
        }
      };
      walk(document.body);
      return out;
    }""")
    print(json.dumps(st, ensure_ascii=False, indent=1))
    b.close()
srv.shutdown()

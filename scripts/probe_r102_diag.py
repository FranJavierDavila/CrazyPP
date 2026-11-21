#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_r102_diag.py — dónde está la bola durante el rallye guiado."""
import functools, json, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8842

ARRANCA = r"""
(() => {
  const g = window.__PP_GAME;
  if (!g) return { err: 'sin juego' };
  const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || g.DIMS;
  if (!D) return { err: 'sin DIMS', keys: Object.keys(g).slice(0, 20) };
  const C = D.tableCenterZ, HL = D.tableHalfLength;
  g.rules.beginServeRally('player');
  g.ball.pos.set(0, 1.05, C + HL - 0.10);
  g.ball.vel.set(0, 1.15, -3.5);
  g.ball.spin.set(0, 0, 0);
  return { ok: 1, C, HL, top: D.tableTopY, net: D.netTopY || null,
    estado: g.rules.state, servidor: g.rules.server,
    menu: !!g.menuOpen, hall: !!g.inHall, tut: !!g.tutV1,
    calib: !!g.calib, vr: !!g.vrBound };
})()
"""

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.on('pageerror', lambda e: print('  PAGEERROR:', str(e)[:200]))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(1500)
    st = pg.evaluate(ARRANCA)
    print('arranque:', json.dumps(st))
    for i in range(14):
        pg.wait_for_timeout(1000)
        s = pg.evaluate("""() => {
          const g = window.__PP_GAME; if (!g) return { err: 1 };
          const b = g.ball, r = g.rules, ai = g.ai;
          return { t: performance.now() | 0, st: r.state,
            p: [ +b.pos.x.toFixed(2), +b.pos.y.toFixed(2), +b.pos.z.toFixed(2) ],
            v: [ +b.vel.x.toFixed(2), +b.vel.y.toFixed(2), +b.vel.z.toFixed(2) ],
            fz: r.lastHitter, vb: r.validBounce, mBO: r.mustBounceOpp,
            ch: ai.chain ? ai.chain.phase : '-', msg: r.message };
        }""")
        print(json.dumps(s))
    b.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r89_probe_gelatina.py — diagnóstico del aire por pareja de manchas."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8797
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(13000)
    out = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes;
      const p = motor.lista.find(q => q.kind === 'gelatina');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      for (let s = 0; s < 6; s++) motor.update(0.1, motor.game.rules);
      const G = motor.ctx.gelatina; if (!G) return { err: 'sin ctx' };
      const D = window.__PP_CORE.DIMS;
      const ms = G.manchas.map(m => ({ x: m.position.x, z: m.position.z - D.tableCenterZ, tam: m.userData.tam }));
      const pares = [];
      for (let i = 0; i < ms.length; i++) for (let j = i + 1; j < ms.length; j++) {
        const a = ms[i], bb = ms[j];
        const d = Math.hypot(a.x - bb.x, a.z - bb.z);
        pares.push({ i, j, d: +d.toFixed(3), aire: +(d - (a.tam + bb.tam) * 0.42).toFixed(3) });
      }
      return { ms: ms.map(m => ({ x: +m.x.toFixed(3), z: +m.z.toFixed(3), tam: +m.tam.toFixed(3) })), pares };
    }""")
    print(json.dumps(out, indent=1))
    b.close()
srv.shutdown()

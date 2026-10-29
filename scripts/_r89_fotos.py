#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r89_fotos.py — capturas de la sala r89 (patrón _r88_fotos.py)."""
import os, functools, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8793

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
        print('· clic JUGAR EN VR')
    except Exception:
        pg.mouse.click(640, 600)
        print('· clic centro')
    pg.wait_for_timeout(20000)
    # Sala desde la posición del jugador (derecha de la mesa, mirando al rival)
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(1.35, 1.55, 0.35);
      g.camera.lookAt(-0.2, 1.35, -2.6);
    }""")
    pg.wait_for_timeout(900)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_sala_jugador.png'))
    # Mapa de cerca (como el dueño lo vería girando la cabeza a la izquierda)
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.9, 1.5, -0.4);
      g.camera.lookAt(-3.03, 1.5, -1.9);
    }""")
    pg.wait_for_timeout(900)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_mapa_pared.png'))
    print('· capturas listas')
    b.close()
srv.shutdown()
print('FOTOS OK')

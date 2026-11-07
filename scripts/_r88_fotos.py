#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura VISUAL r88: sala de Halloween (sin cartel, con mapa en la pared
izquierda y zombi a la derecha de la mesa) + primer plano del mapa."""
import os, functools, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8767
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=6000)
        print('· clic JUGAR EN VR (texto)')
    except Exception as e:
        print('· fallback:', e)
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(14000)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_sala.png'))
    print('· sala capturada')
    # primer plano del mapa (pared izquierda) girando la cámara del juego
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.4, 1.45, -1.6);
      g.camera.lookAt(-3.03, 1.45, -1.9);
    }""")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_mapa_cerca.png'))
    print('· mapa capturado')
    # zombi (derecha de la mesa, anclado a ella)
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.3, 1.5, 0.2);
      g.camera.lookAt(1.45, 1.15, -3.3);
    }""")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_zombi_cerca.png'))
    print('· zombi capturado')
    b.close()
srv.shutdown()
print('OK capturas r88')

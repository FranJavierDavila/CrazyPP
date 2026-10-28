#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_halloween_foto_r85.py — fotografía de la sala de Halloween en modo espectador:
   JUGAR EN VR (2D) → el juego arranca ?champ=halloween → captura de la sala del
   cementerio con el rival ZOMBI, el cartel de bienvenida y el mapa del dueño."""
import os, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading, functools
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8742
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
        print('· clic JUGAR EN VR')
    except Exception:
        try:
            pg.mouse.click(640, 600)
            print('· clic centro (JUGAR EN VR)')
        except Exception as e:
            print('· clic directo falló:', e)
    pg.wait_for_timeout(12000)      # espectador: carga cancha + campeonato + sala
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r85_halloween_sala.png'))
    pg.wait_for_timeout(3000)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r85_halloween_sala2.png'))
    print('pageerrors:', len(errs), errs[:2])
    b.close()
srv.shutdown()
print('OK capturas sala')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Foto del CANVAS del menú (página ACADEMIA) + foto 3D del modo cuadrantes."""
import base64
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    pg = br.new_page(viewport={'width': 1280, 'height': 800})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/game.html', wait_until='domcontentloaded')
    pg.wait_for_function('() => !!window.__PP_GAME', timeout=60000)
    pg.wait_for_timeout(2000)

    # página ACADEMIA del menú VR (canvas interno 1024×1536)
    pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.toggleMenu(); g.menuPage = 'train'; g.drawMenu(); })()""")
    b64 = pg.evaluate("""(() => { const g = window.__PP_GAME;
      return g.menuCanvas.toDataURL('image/png'); })()""")
    open('/home/z/my-project/scripts/_qa_v300_academia.png', 'wb').write(
        base64.b64decode(b64.split(',', 1)[1]))

    # foto 3D de la portada con el modo cuadrantes montado (tiza visible)
    pg.evaluate("window.__PP_GAME.closeMenu()")
    pg.evaluate("window.__PP_GAME.enterTraining('quad')")
    pg.wait_for_timeout(1500)
    pg.screenshot(path='/home/z/my-project/scripts/_qa_v300_quad3d.png')

    # también el hub con la tarjeta nueva de ENTRENAR
    pg.evaluate("window.__PP_GAME.exitTraining()")
    pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.toggleMenu(); g.menuPage = 'main'; g.drawMenu(); })()""")
    b64 = pg.evaluate("window.__PP_GAME.menuCanvas.toDataURL('image/png')")
    open('/home/z/my-project/scripts/_qa_v300_hub.png', 'wb').write(
        base64.b64decode(b64.split(',', 1)[1]))
    print('fotos listas · pageerrors:', len(errs), errs[:2])
    br.close()

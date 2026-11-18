#!/usr/bin/env python3
"""_r92_diag_mesa.py — diagnóstico: ¿quién viste la mesa y con qué?"""
import os, functools, threading
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
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    for texto in ('ESPAÑOL', 'ENGLISH'):
        try:
            pg.get_by_text(texto, exact=True).click(timeout=1200); break
        except Exception:
            pass
    try:
        pg.get_by_text('JUGAR EN VR', exact=True).click(timeout=3000)
    except Exception:
        pg.mouse.click(640, 620)
    pg.wait_for_timeout(9000)
    out = pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      const top = g.tableGroup.getObjectByName('ppTableTop');
      const src = top.material.map && top.material.map.image && top.material.map.image.src || null;
      const H = window.__PP_HALLOWEEN;
      return {
        estado: g.rules.state,
        mapSrc: src ? src.slice(-40) : null,
        color: '#' + top.material.color.getHexString(),
        losaSaved: !!H.ctrl()._losaSaved,
        // ¿cuántos meshes TOP hay?
        tops: (() => { let n = 0; g.scene.traverse(o => { if (o.name === 'ppTableTop') n++; }); return n; })(),
        // el material es COMPARTIDO con otra mesa (demo/TV)?
        mats: (() => { const arr = []; g.scene.traverse(o => { if (o.isMesh && o.material === top.material) arr.push(o.name || o.type); }); return arr.slice(0, 6); })(),
      };
    }""")
    print(out)
    b.close()
srv.shutdown()

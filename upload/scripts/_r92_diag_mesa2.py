#!/usr/bin/env python3
"""_r92_diag_mesa2.py — primer plano cenital de la mesa + sin luces cálidas ambiguas."""
import os, functools, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8819
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
    pg.evaluate("""() => {
      for (const el of document.body.children) {
        if (el.tagName === 'CANVAS') continue;
        try { el.style.display = 'none'; } catch (e) {}
      }
    }""")
    pg.wait_for_timeout(300)
    D = pg.evaluate("() => window.__PP_CORE.DIMS")
    cz = D['tableCenterZ']
    # cenital cercana: boca abajo sobre la mesa
    pg.evaluate(f"() => {{ const g = window.__PP_HALLOWEEN.ctrl().game; g.camera.position.set(0.4, 2.05, {cz} + 0.25); g.camera.lookAt(0.0, {D['tableTopY']}, {cz} - 0.15); }}")
    pg.wait_for_timeout(1000)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r92_vis_mesa_cenital.png'))
    b.close()
srv.shutdown()
print('ok')

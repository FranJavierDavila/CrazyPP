#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91i_mano_close.py — primer plano de la mano: la tierra y el brazo del
arte INTEGRAL deben verse bajo la mano."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8803
OUT = os.path.join(RAIZ, 'scripts')

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    for texto in ('ESPAÑOL', 'ENGLISH'):
        try:
            pg.get_by_text(texto, exact=True).click(timeout=1200); break
        except Exception: pass
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=6000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(8000)
    try:
        pg.evaluate("() => { const g = window.__PP_HALLOWEEN.ctrl().game; g.hideChampIntro(true); }")
    except Exception: pass
    pg.wait_for_timeout(2000)

    res = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods; const ctrl = H.ctrl(); const ctxP = {};
      pods.mano.inicio(g, { duration: 20 }, ctrl, ctxP);
      const M = ctxP.mano;
      return new Promise((res) => {
        const t0 = Date.now();
        const espera = () => {
          if (M.tex.length < 1 && Date.now() - t0 < 8000) return setTimeout(espera, 200);
          try { pods.mano._spawn(g, M); } catch (e) { res({ err: String(e) }); return; }
          const v = M.vivos[0];
          if (v) { for (let i = 0; i < 26; i++) pods.mano.paso(0.05, g, { duration: 20 }, ctrl, ctxP); }
          if (!v) { res({ err: 'sin mano' }); return; }
          // forzar la fase 'arriba' con el arte completo
          v.fase = 'arriba'; v.tex.repeat.y = 1.0; v.tex.offset.y = 0.0;
          res({ pos: [+v.mano.position.x.toFixed(2), +v.mano.position.z.toFixed(2)], rep: v.tex.repeat.y, off: v.tex.offset.y });
        };
        espera();
      });
    }""")
    print('mano:', json.dumps(res))
    pg.wait_for_timeout(400)
    # cámara baja mirando a la mano (primer plano)
    if 'pos' in res:
        x, z = res['pos']
        pg.evaluate(f"""() => {{
          const g = window.__PP_HALLOWEEN.ctrl().game;
          g.camera.position.set({x + 0.35}, 1.02, {z + 0.42});
          g.camera.lookAt({x}, 0.98, {z});
        }}""")
        pg.wait_for_timeout(600)
        pg.screenshot(path=os.path.join(OUT, '_r91i_mano_close.png'))
        # y un plano más frontal
        pg.evaluate(f"""() => {{
          const g = window.__PP_HALLOWEEN.ctrl().game;
          g.camera.position.set({x}, 1.06, {z + 0.55});
          g.camera.lookAt({x}, 1.0, {z});
        }}""")
        pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(OUT, '_r91i_mano_frontal.png'))
    b.close()

srv.shutdown()
print('MANO CLOSE OK')

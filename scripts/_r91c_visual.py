#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91c_visual.py — capturas de verificación visual r91c:
   mapa en pared, calabaza, mano completa, rival defeated, sala."""
import os, time, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8796
OUT = os.path.join(RAIZ, 'scripts')

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

CAP = """((nom, cx, cy, cz, tx, ty, tz) => {
  const g = window.__PP_HALLOWEEN.ctrl().game;
  g.camera.position.set(cx, cy, cz);
  g.camera.lookAt(tx, ty, tz);
  return nom;
})"""

def cam(pg, nom, cx, cy, cz, tx, ty, tz):
    return pg.evaluate(f"{CAP}({nom!r}, {cx}, {cy}, {cz}, {tx}, {ty}, {tz})")

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
        except Exception: pass
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=6000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(10000)
    try:
        pg.mouse.click(640, 360)
    except Exception: pass
    pg.wait_for_timeout(4000)

    # ocultar DOM (HUD) para ver la escena 3D limpia
    pg.evaluate("""() => {
      const v = document.getElementById('root') || document.body;
      for (const el of document.body.children) {
        if (el.tagName === 'CANVAS') continue;
        try { el.style.display = 'none'; } catch (e) {}
      }
    }""")
    pg.wait_for_timeout(400)

    # 1) sala desde el jugador
    cam(pg, 'sala', 0.0, 1.55, 0.75, -1.2, 1.35, -1.9)
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(OUT, '_r91c_sala.png'))

    # 2) mapa de cerca
    cam(pg, 'mapa', -0.5, 1.50, -0.75, -2.98, 1.45, -0.9)
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(OUT, '_r91c_mapa.png'))

    # 3) calabaza: spawn + captura (con protecciones)
    cala = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods; const ctrl = H.ctrl();
      const ctxP = {};
      try {
        const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
        if (!g.ball) g.ball = new V3();
        if (!g.ball.pos) g.ball = { pos: new V3(), vel: new V3(), spin: new V3() };
        g.ball.pos.set(0.15, 0.95, -0.6);
        pods.calabaza.inicio(g, { duration: 10 }, ctrl, ctxP);
        for (let i = 0; i < 3; i++) pods.calabaza.paso(0.033, g, { duration: 10 }, ctrl, ctxP);
        const C = ctxP.calabaza;
        if (!C) return { err: 'sin ctx.calabaza' };
        return { enEscena: !!C.gltf.parent, pos: [+C.gltf.position.x.toFixed(2), +C.gltf.position.y.toFixed(2)] };
      } catch (e) { return { err: String(e) }; }
    }""")
    print('calabaza:', json.dumps(cala))
    cam(pg, 'cala', 0.45, 1.25, -0.25, 0.15, 0.93, -0.6)
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, '_r91c_calabaza.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      try { H.pods.calabaza.fin(g, { duration: 10 }, H.ctrl(), H.__ctxP || {}); } catch (e) {}
    }""")

    # 4) mano: spawn completo + captura
    mano = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods; const ctrl = H.ctrl();
      const ctxP = {};
      try {
        pods.mano.inicio(g, { duration: 10 }, ctrl, ctxP);
        const M = ctxP.mano;
        if (!M) return { err: 'sin ctx.mano' };
        return new Promise((res) => {
          const t0 = Date.now();
          const espera = () => {
            if (M.tex.length < 1 && Date.now() - t0 < 8000) return setTimeout(espera, 200);
            try { pods.mano._spawn(g, M); } catch (e) { res({ err: String(e) }); return; }
            const v = M.vivos[0];
            if (v) { for (let i = 0; i < 30; i++) pods.mano.paso(0.05, g, { duration: 10 }, ctrl, ctxP); }
            res({ tex: M.tex.length, vivos: M.vivos.length,
                  rep: v ? [+v.tex.repeat.y.toFixed(3), +v.tex.offset.y.toFixed(3)] : null, fase: v ? v.fase : null });
          };
          espera();
        });
      } catch (e) { return { err: String(e) }; }
    }""")
    print('mano:', json.dumps(mano))
    cam(pg, 'mano', 0.55, 1.45, -0.20, 0.30, 0.95, -0.95)
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, '_r91c_mano.png'))

    # 5) rival defeated + captura
    pg.evaluate("""() => {
      const C = window.__PP_HALLOWEEN.ctrl(); C.rival.rivalEmocion('defeated');
    }""")
    pg.wait_for_timeout(500)
    cam(pg, 'rival', -0.2, 1.5, 0.3, 1.45, 1.1, -3.3)
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, '_r91c_rival_defeated.png'))

    print('pageerrors:', errs[:5])
    b.close()

srv.shutdown()
print('VISUAL r91c OK')

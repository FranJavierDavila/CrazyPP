#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r92_visual.py — capturas de verificación visual r92:
   1) mesa con la textura NUEVA (mesa.webp — losas de piedra con sangre),
   2) mano zombi ANCLADA (base tocando la mesa),
   3) calabaza GIRANDO en la mesa (dos muestras de rotación)."""
import os, time, functools, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8815
OUT = os.path.join(RAIZ, 'scripts')

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

    ok = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return false;
      const g = H.ctrl().game;
      if (g.rules.state === 'portada' || !H.ctrl().rival) { try { H.ctrl().startChamp(); } catch (e) {} }
      return !!H.ctrl().rival;
    }""")
    print('escena viva:', ok)
    pg.wait_for_timeout(2500)

    # ocultar DOM (portada 2D + HUD) y CERRAR LA INTRO (la ruta de cámara de
    # la intro secuestra la cámara cada frame — hideChampIntro(true) es el
    # efecto EXACTO del botón JUGAR, patrón r91)
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      try { g.hideChampIntro(true); } catch (e) {}
      for (const el of document.body.children) {
        if (el.tagName === 'CANVAS') continue;
        try { el.style.display = 'none'; } catch (e) {}
      }
    }""")
    pg.wait_for_timeout(1500)

    CAP = """((cx, cy, cz, tx, ty, tz) => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(cx, cy, cz);
      g.camera.lookAt(tx, ty, tz);
      return true;
    })"""
    D = pg.evaluate("() => window.__PP_CORE.DIMS")
    cz = D['tableCenterZ']

    # 1) MESA NUEVA — vista elevada del jugador hacia la mesa
    pg.evaluate(f"{CAP}(0, 1.62, {cz} + 1.55, 0, 0.72, {cz} - 0.4)")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=os.path.join(OUT, '_r92_vis_mesa.png'))

    # 2) MANO ANCLADA — lanzar el poder y capturar en fase 'arriba'
    pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const ctxP = {};
      H.pods.mano.inicio(g, { duration: 20 }, ctrl, ctxP);
      window.__r92mano = { ctxP, impl: H.pods.mano };
      const M = ctxP.mano;
      for (let i = 0; i < 100 && M.tex.length < 3; i++) await new Promise(r => setTimeout(r, 100));
      const D = window.__PP_CORE.DIMS;
      g.ball.pos.set(0, 1.0, D.tableCenterZ + 1.15);
      for (let i = 0; i < 8; i++) { H.pods.mano._spawn(g, M); if (M.vivos.length) break; }
    }""")
    for _ in range(16):
        pg.evaluate("""() => { const r = window.__r92mano; r.impl.paso(0.1, r.ctxP.mano ? { } : null); }""") if False else None
        pg.evaluate("""() => { const r = window.__r92mano; const g = window.__PP_HALLOWEEN.ctrl().game;
                               r.impl.paso(0.1, g, { duration: 20 }, window.__PP_HALLOWEEN.ctrl(), r.ctxP); }""")
        pg.wait_for_timeout(60)
    fase = pg.evaluate("""() => { const r = window.__r92mano; const v = r.ctxP.mano.vivos[0];
                                  return v ? { f: v.fase, y: +v.mano.position.y.toFixed(3) } : null; }""")
    print('mano fase:', fase)
    pg.evaluate(f"{CAP}(0, 1.35, {cz} + 0.85, 0, 0.92, {cz} - 0.1)")
    pg.wait_for_timeout(900)
    pg.screenshot(path=os.path.join(OUT, '_r92_vis_mano.png'))

    # 3) CALABAZA con spin — dos capturas separadas 0,5 s (se ve girada)
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const ctxP = {};
      H.pods.calabaza.inicio(g, { duration: 30 }, ctrl, ctxP);
      window.__r92cal = { ctxP, impl: H.pods.calabaza };
      g.ball.pos.set(0.0, window.__PP_CORE.DIMS.tableTopY + 0.08, window.__PP_CORE.DIMS.tableCenterZ - 0.2);
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(9, 4, 0);
    }""")
    for i in range(10):
        pg.evaluate("""() => { const r = window.__r92cal; const g = window.__PP_HALLOWEEN.ctrl().game;
                               r.impl.paso(0.05, g, { duration: 30 }, window.__PP_HALLOWEEN.ctrl(), r.ctxP); }""")
        pg.wait_for_timeout(50)
    pg.evaluate(f"{CAP}(0, 1.30, {cz} + 0.75, 0, 0.85, {cz} - 0.2)")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, '_r92_vis_calabaza_a.png'))
    for i in range(10):
        pg.evaluate("""() => { const r = window.__r92cal; const g = window.__PP_HALLOWEEN.ctrl().game;
                               r.impl.paso(0.05, g, { duration: 30 }, window.__PP_HALLOWEEN.ctrl(), r.ctxP); }""")
        pg.wait_for_timeout(50)
    pg.screenshot(path=os.path.join(OUT, '_r92_vis_calabaza_b.png'))
    rot = pg.evaluate("""() => { const r = window.__r92cal;
      return { x: +r.ctxP.calabaza.gltf.rotation.x.toFixed(2), y: +r.ctxP.calabaza.gltf.rotation.y.toFixed(2) }; }""")
    print('calabaza rotación acumulada:', rot)
    pg.evaluate("""() => { try { const r = window.__r92cal; const g = window.__PP_HALLOWEEN.ctrl().game;
      r.impl.fin(g, { duration: 30 }, window.__PP_HALLOWEEN.ctrl(), r.ctxP); } catch (e) {}
      try { const m = window.__r92mano; const g = window.__PP_HALLOWEEN.ctrl().game;
      m.impl.fin(g, { duration: 20 }, window.__PP_HALLOWEEN.ctrl(), m.ctxP); } catch (e) {} }""")
    print('pageerrors:', len(errs))
    for e in errs[:5]:
        print('  !', e[:160])
    b.close()
srv.shutdown()
print('capturas: _r92_vis_mesa.png · _r92_vis_mano.png · _r92_vis_calabaza_a/b.png')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91f_cadena.py — prueba de la CADENA COMPLETA de emociones del núcleo:
game.rivalEmocion() → champs.rivalEmocion() → módulo → cara + sonido."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8799

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

CADENA = """() => {
  const H = window.__PP_HALLOWEEN; const g = H.ctrl().game; const C = H.ctrl();
  const cara = () => { try { const mm = C.rival.r.mat; return mm && mm.map && mm.map.image ? mm.map.image.src.split('/').pop() : null; } catch (e) { return 'ERR'; } };
  const out = { champsActive: !!(g.champs && g.champs.active), activeId: g.champs ? g.champs.activeId : null,
                state: g.rules.state, cara0: cara() };
  // LA CADENA REAL DEL NÚCLEO (lo que corre en un punto del partido)
  g.rivalEmocion('laughing', 2.0, 'victory'); out.cara1Laughing = cara();
  g.rivalEmocion('angry', 2.0);               out.cara2Angry = cara();
  g.rivalEmocion('defeated', 0);              out.cara3Defeated = cara();
  g.rivalEmocion('idle', 0);                  out.cara4Idle = cara();
  // estado de la norma en el núcleo
  out._rivalEmo = g._rivalEmo; out._rivalEmoT = g._rivalEmoT;
  // hook del módulo visto por el champloader
  out.modTieneHook = !!(g.champs.mod && g.champs.mod.rivalEmocion);
  return out;
}"""

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
    pg.wait_for_timeout(3000)

    d = pg.evaluate(CADENA)
    print(json.dumps(d, indent=1, ensure_ascii=False))
    SALIDA = d
    print('pageerrors:', errs[:5])
    b.close()

srv.shutdown()
print('CADENA OK')

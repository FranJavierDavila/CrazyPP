#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91g_musica.py — verificación de la BSO y de los sonidos del zombi
EN EL MOTOR REAL del módulo (vía __PP_HALLOWEEN.mus()/sfxZ())."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8801

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

MUS = """() => {
  const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
  const out = { ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null, arcPlaying: !!(g.audio && g.audio.arcPlaying) };
  try { const m = H.mus(); out.music = m ? m.estado() : 'null'; } catch (e) { out.music = 'err:' + e; }
  try { const z = H.sfxZ(); out.zonb = z ? Object.keys(z).map((k) => ({ k, cargado: z[k].b.estado ? z[k].b.estado().cargado : '?' })) : 'null'; } catch (e) { out.zonb = 'err:' + e; }
  return out;
}"""

DISPARO = """() => {
  const H = window.__PP_HALLOWEEN; const C = H.ctrl();
  const out = {};
  // disparar los 4 sonidos por la vía REAL (rivalEmocion / power)
  C.rival.rivalEmocion('laughing');   // → laugh
  out.laugh = true;
  return out;
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required',
                                 '--autoplay-policy=no-user-gesture-required'])
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
    pg.wait_for_timeout(8000)

    e0 = pg.evaluate(MUS)
    print('== TRAS ENTRADA (intro viva) =='); print(json.dumps(e0, indent=1))

    # pulsar JUGAR de la intro (el flujo real que reanuda la BSO)
    try:
        pg.mouse.click(640, 360)
    except Exception: pass
    pg.wait_for_timeout(9000)
    e1 = pg.evaluate(MUS)
    print('== TRAS JUGAR (BSO debe sonar) =='); print(json.dumps(e1, indent=1))

    # disparo del laugh por la vía real
    pg.evaluate(DISPARO)
    pg.wait_for_timeout(700)
    e2 = pg.evaluate(MUS)
    print('== TRAS RIVAL_EMOCION(laughing) =='); print(json.dumps(e2.get('zonb'), indent=1))

    print('pageerrors:', errs[:5])
    b.close()

srv.shutdown()
print('MÚSICA OK')

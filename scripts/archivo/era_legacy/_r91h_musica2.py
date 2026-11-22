#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91h_musica2.py — BSO en el flujo REAL: entrada → intro → hideChampIntro(true)
(el efecto EXACTO del botón JUGAR) → seguimiento 20 s → duelo → seguimiento."""
import os, functools, json, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8802

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

MUS = """() => {
  const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
  const out = { ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null,
                arcPlaying: !!(g.audio && g.audio.arcPlaying),
                musicPlaying: !!(g.audio && g.audio.musicPlaying),
                state: g.rules.state };
  try { const m = H.mus(); out.music = m ? m.estado() : 'null'; } catch (e) { out.music = 'err:' + e; }
  return out;
}"""

S = {}
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
    pg.wait_for_timeout(9000)

    S['entrada'] = pg.evaluate(MUS)
    print('== ENTRADA =='); print(json.dumps(S['entrada']))

    # el efecto EXACTO del botón JUGAR de la intro
    pg.evaluate("""() => { const g = window.__PP_HALLOWEEN.ctrl().game; g.hideChampIntro(true); }""")
    for i in range(5):
        pg.wait_for_timeout(2000)
        e = pg.evaluate(MUS)
        S['trasJugar_%d' % i] = e
        print('trasJugar +%ds:' % ((i + 1) * 2), json.dumps(e['music']), 'arc:', e['arcPlaying'], 'ctx:', e['ctx'])

    # lanzar el DUELO 1 (serveTrigger) y seguir 8 s
    pg.evaluate("""() => { window.__PP_HALLOWEEN.ctrl().serveTrigger(0); }""")
    for i in range(4):
        pg.wait_for_timeout(2000)
        e = pg.evaluate(MUS)
        S['duelo_%d' % i] = e
        print('duelo +%ds:' % ((i + 1) * 2), json.dumps(e['music']), 'arc:', e['arcPlaying'], 'state:', e['state'])

    print('pageerrors:', errs[:5])
    b.close()

srv.shutdown()
with open(os.path.join(RAIZ, 'scripts', '_r91h_salida.json'), 'w') as f:
    json.dump(S, f, indent=1, ensure_ascii=False)
print('MÚSICA2 OK')

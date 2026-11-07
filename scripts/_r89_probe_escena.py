#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r89_probe_escena.py — sonda de la ronda 89.
1) Enumera los planos con texturas del módulo halloween en la escena VIVA
   (detecta duplicados: dos estados del zombi coplanares, dos mapas...).
2) Muestrea durante 40 s buscando el momento del solape del rival.
3) Capturas desde la posición del jugador (mapa en pared izquierda)."""
import os, sys, time, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8791

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

ENUM = """() => {
  const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
  const g = H.ctrl().game;
  const out = { vive: true, planos: [], sprites: [] };
  g.scene.traverse((o) => {
    let src = null;
    try {
      const m = o.material;
      const map = Array.isArray(m) ? m[0] && m[0].map : m && m.map;
      if (map && map.image && map.image.src) src = map.image.src;
    } catch (e) {}
    if (!src) return;
    const i = src.indexOf('/championships/halloween/');
    if (i < 0) return;
    const nom = src.slice(i + '/championships/halloween/'.length);
    const esSprite = !!o.isSprite;
    const p = o.getWorldPosition(new (Object.getPrototypeOf(o.position).constructor)());
    out[esSprite ? 'sprites' : 'planos'].push({
      tex: nom, pos: [+p.x.toFixed(2), +p.y.toFixed(2), +p.z.toFixed(2)],
      rotY: o.parent === g.scene ? +(+o.rotation.y.toFixed(3)) : null,
      esc: [+o.scale.x.toFixed(2), +o.scale.y.toFixed(2)],
      visible: o.visible && (!o.parent || o.parent.visible !== false),
    });
  });
  const r = H.ctrl().rival;
  out.estadoRival = r ? r.estado : null;
  out.prewarm = r ? r.prewarmI : -99;
  return out;
}"""

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
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)

    # 1) enumeración inicial
    e0 = pg.evaluate(ENUM)
    print('== ENUM t=0 =='); print(json.dumps(e0, indent=1, ensure_ascii=False))

    # 2) muestreo 40 s: ¿algún momento con DOS planos de estados del zombi?
    print('== MUESTREO 40 s ==')
    for k in range(20):
        e = pg.evaluate(ENUM)
        estados = [p['tex'] for p in e['planos'] if any(n in p['tex'] for n in
                   ['present', 'idle', 'focused', 'surprised', 'panic', 'laughing',
                    'crazy', 'angry', 'picando', 'loosing', 'defeated', 'victory', 'rival'])]
        mapas = [p for p in e['planos'] if 'mapa' in p['tex']]
        print('t=%02d rival=%s prewarm=%s planosEstado=%s mapas=%d' %
              (k * 2, e.get('estadoRival'), e.get('prewarm'), estados, len(mapas)))
        if len(estados) > 1:
            print('   ¡¡DOS PLANOS DE ESTADO!!', json.dumps([p for p in e['planos'] if p['tex'] in estados], indent=1))
        pg.wait_for_timeout(2000)

    # 3) capturas desde la posición del jugador
    pg.camera_set = None
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(1.35, 1.55, 0.35);
      g.camera.lookAt(0.0, 1.25, -2.4);
    }""")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_vista_jugador.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(0.2, 1.55, 0.6);
      g.camera.lookAt(-3.03, 1.45, -1.9);
    }""")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_mapa_jugador.png'))
    print('capturas escritas')

    if errs:
        print('ERRORES DE PÁGINA:', errs[:6])
    b.close()
srv.shutdown()
print('SONDA OK')

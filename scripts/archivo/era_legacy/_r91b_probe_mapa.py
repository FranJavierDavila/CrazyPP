#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91b_probe_mapa.py — sonda mínima r91b: estado REAL del plano del mapa
en escena viva + red (¿404?) + página. Corta y rápida (mapa primero)."""
import os, time, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8795

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# log de red: todas las peticiones a championships/halloween/assets/
NETLOG = """() => {
  const out = performance.getEntriesByType('resource')
    .filter((e) => e.name.indexOf('/championships/halloween/assets/') >= 0)
    .map((e) => ({ url: e.name.split('/championships/halloween/assets/')[1],
                   ms: Math.round(e.duration), size: e.transferSize }));
  return out;
}"""

ENUM = """() => {
  const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
  const g = H.ctrl().game; const C = H.ctrl();
  const out = { vive: true, mapa: null, rigHijos: 0 };
  // mapa: buscar el plano con textura mapa.webp en TODO el grafo
  const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
  g.scene.traverse((o) => {
    let src = null;
    try { const m = o.material; const map = m && m.map; if (map && map.image && map.image.src) src = map.image.src; } catch (e) {}
    if (!src || src.indexOf('mapa.webp') < 0) return;
    const p = o.getWorldPosition(new V3());
    const pad = []; let q = o.parent; while (q) { pad.push(q.type + (q === g.rig ? ':RIG' : '')); q = q.parent; }
    out.mapa = { pos: [+p.x.toFixed(3), +p.y.toFixed(3), +p.z.toFixed(3)],
                 visible: o.visible, opacity: o.material.opacity, transparent: o.material.transparent,
                 depthWrite: o.material.depthWrite, colorSpace: String(o.material.map.colorSpace),
                 texTam: [o.material.map.image.width, o.material.map.image.height],
                 padres: pad.join('>'), renderOrder: o.renderOrder,
                 tapas: o.children ? o.children.length : 0 };
  });
  if (C.mapa && C.mapa.grupo) {
    out.grupo = { enRig: C.mapa.grupo.parent === g.rig, pos: C.mapa.grupo.position.toArray().map((v) => +v.toFixed(3)),
                  hijos: C.mapa.grupo.children.length };
  }
  out.rigHijos = g.rig.children.length;
  out.modoMapa = C.mapa ? C.mapa.modo : null;
  return out;
}"""

SALIDA = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    fails = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('requestfailed', lambda r: fails.append(r.url.split('/')[-1] + ' :: ' + str(r.failure)))
    pg.on('response', lambda r: fails.append(str(r.status) + ' ' + r.url.split('/')[-1]) if r.status >= 400 else None)
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
    pg.wait_for_timeout(6000)

    e = pg.evaluate(ENUM)
    SALIDA['enum'] = e
    print('== MAPA =='); print(json.dumps(e, indent=1, ensure_ascii=False))
    SALIDA['red'] = pg.evaluate(NETLOG)
    print('== RED assets =='); print(json.dumps(SALIDA['red'], indent=1))
    SALIDA['fallos'] = fails[:10]
    print('fallos/red 4xx:', fails[:10])
    SALIDA['pageerrors'] = errs[:6]
    print('pageerrors:', errs[:6])
    b.close()

srv.shutdown()
with open(os.path.join(RAIZ, 'scripts', '_r91b_salida.json'), 'w') as f:
    json.dump(SALIDA, f, indent=1, ensure_ascii=False)
print('SONDA r91b OK')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91d_calabaza.py — diagnóstico profundo del CUERPO de la calabaza:
geometría válida, boundingSphere, materiales, world matrix, raycast."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8797

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

DIAG = """() => {
  const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
  const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
  if (!g.ball || !g.ball.pos) g.ball = { pos: new V3(), vel: new V3(), spin: new V3() };
  g.ball.pos.set(0.15, 0.95, -0.6);
  const pods = H.pods, ctrl = H.ctrl(); const ctxP = {};
  pods.calabaza.inicio(g, { duration: 10 }, ctrl, ctxP);
  pods.calabaza.paso(0.033, g, { duration: 10 }, ctrl, ctxP);
  const C = ctxP.calabaza;
  const out = {};
  out.hijos = C.gltf.children.map((c) => ({
    tipo: c.type, nombre: c.geometry && c.geometry.type, vis: c.visible,
    culled: c.frustumCulled, posLocal: [+c.position.x.toFixed(4), +c.position.y.toFixed(4), +c.position.z.toFixed(4)],
    escala: [+c.scale.x.toFixed(3), +c.scale.y.toFixed(3), +c.scale.z.toFixed(3)],
  }));
  // cuerpo = children[0]
  const cuerpo = C.gltf.children[0];
  const geo = cuerpo.geometry;
  out.geo = {
    tipo: geo.type, attrs: Object.keys(geo.attributes),
    nVerts: geo.attributes.position ? geo.attributes.position.count : 0,
    bs: geo.boundingSphere ? { r: +geo.boundingSphere.radius.toFixed(4), c: geo.boundingSphere.center.toArray().map((v) => +v.toFixed(4)) } : null,
  };
  // primeros 3 y últimos 3 vértices + validez
  const p = geo.attributes.position;
  let nan = 0, minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i);
    if (Number.isNaN(x) || Number.isNaN(y)) nan++;
    if (x < minX) minX = x; if (x > maxX) maxX = x;
    if (y < minY) minY = y; if (y > maxY) maxY = y;
  }
  out.geo.nan = nan; out.geo.rangoX = [+minX.toFixed(4), +maxX.toFixed(4)]; out.geo.rangoY = [+minY.toFixed(4), +maxY.toFixed(4)];
  const m = cuerpo.material;
  out.mat = { tipo: m.type, side: m.side, color: '#' + m.color.getHexString(), map: !!m.map,
              transparent: m.transparent, opacity: m.opacity, visible: m.visible,
              depthTest: m.depthTest, depthWrite: m.depthWrite, alphaTest: m.alphaTest,
              emissive: m.emissive ? '#' + m.emissive.getHexString() : null };
  // world matrix del cuerpo
  cuerpo.updateWorldMatrix(true, false);
  const wp = cuerpo.getWorldPosition(new V3());
  out.worldPos = [+wp.x.toFixed(3), +wp.y.toFixed(3), +wp.z.toFixed(3)];
  const ws = cuerpo.getWorldScale(new V3());
  out.worldScale = [+ws.x.toFixed(3), +ws.y.toFixed(3), +ws.z.toFixed(3)];
  // el grupo entero: escala
  const gs = C.gltf.getWorldScale(new V3());
  out.grupoEscala = [+gs.x.toFixed(3), +gs.y.toFixed(3), +gs.z.toFixed(3)];
  // raycast desde la cámara hacia el cuerpo
  const rc = new (cuerpo.raycast.constructor.prototype.constructor.name === 'Raycaster' ? Object : Object)();
  // (raycast directo con THREE del módulo)
  out.padres = (() => { const pad = []; let q = C.gltf.parent; while (q) { pad.push(q.type); q = q.parent; } return pad.join('>'); })();
  // ¿qué luz hay? (MeshStandardMaterial necesita luces)
  out.luces = [];
  g.scene.traverse((o) => { if (o.isLight) out.luces.push({ tipo: o.type, vis: o.visible, int: +o.intensity.toFixed(2) }); });
  return out;
}"""

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
    pg.wait_for_timeout(10000)
    try:
        pg.mouse.click(640, 360)
    except Exception: pass
    pg.wait_for_timeout(3000)

    d = pg.evaluate(DIAG)
    print(json.dumps(d, indent=1, ensure_ascii=False))
    b.close()

srv.shutdown()
print('DIAG calabaza OK')

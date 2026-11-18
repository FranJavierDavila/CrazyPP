#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_normal2_r71.py — autopsia definitiva de la panela C.

1 · normal del primer triángulo del ShapeGeometry (¿+Z hacia el jugador?).
2 · rayo posado sobre el rect 'start' → updateMenu → hover (FrontSide).
3 · material.side = DoubleSide → updateMenu → hover (¿revive?).
"""
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3676', '--bind', '127.0.0.1',
     '--directory', '/home/z/my-project/upload/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader',
                                     '--enable-unsafe-swiftshader'])
        page = b.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('http://127.0.0.1:3676/game.html', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        page.wait_for_timeout(1000)
        out = page.evaluate("""() => {
          const G = window.__PP_GAME;
          Object.defineProperty(G.renderer.xr, 'isPresenting',
            { value: true, configurable: true });
          G.connected = [true, true];
          if (!G.menuOpen) G.toggleMenu();
          G.anchorMenu(true);
          const pa = G.menuMesh;
          const g = pa.geometry;
          const pos = g.attributes.position;
          const idx = g.index;
          const P = (i) => ({ x: pos.getX(i), y: pos.getY(i), z: pos.getZ(i) });
          const A = P(idx.getX(0)), B = P(idx.getX(1)), C = P(idx.getX(2));
          const sub = (p, q) => ({x: p.x - q.x, y: p.y - q.y, z: p.z - q.z});
          const crs = (u, v) => ({x: u.y*v.z - u.z*v.y,
                                  y: u.z*v.x - u.x*v.z,
                                  z: u.x*v.y - u.y*v.x});
          const n = crs(sub(B, A), sub(C, A));
          // ¿dónde está el jugador respecto a la panela? dot(normal, jugador-centro)
          const V3 = G.menuGroup.position.constructor;
          const ojos = new V3();
          G.camera.getWorldPosition(ojos);
          const cw = new V3();
          pa.getWorldPosition(cw);
          const aOjos = ojos.clone().sub(cw).normalize();
          const dotOjos = +(n.x*aOjos.x + n.y*aOjos.y + n.z*aOjos.z).toFixed(3);
          // rayo al centro del rect 'start'
          const r = G.menuRects.find((x) => x.id === 'start');
          const p = pa.userData.panela;
          const u = ((r.x + r.w / 2) - p.x) / p.w;
          const v = 1 - (r.y + r.h / 2) / 1400;
          if (!G.rays[0]) {
            const ray = new G.rig.constructor();
            G.rig.add(ray);
            G.rays[0] = ray;
          }
          const ray = G.rays[0];
          const mundo = G.menuGroup.localToWorld(new V3(
            (u - 0.5) * p.anchoM, (v - 0.5) * p.altoM, 0.004));
          ray.position.set(-0.25, 1.30, 0.55);
          ray.lookAt(mundo);
          ray.rotateY(Math.PI);
          ray.updateMatrixWorld(true);
          const hoverDe = () => {
            G.menuHover = [-1, -1];
            try { G.updateMenu(0.016); } catch (e) { return 'ERR:' + e; }
            return G.menuHover[0];
          };
          const hFront = hoverDe();
          const old = pa.material.side;
          pa.material.side = 2;                     // DoubleSide
          const hDouble = hoverDe();
          pa.material.side = old;
          return {
            normal: {x: +n.x.toFixed(3), y: +n.y.toFixed(3), z: +n.z.toFixed(3)},
            dotNormalVsOjos: dotOjos,     // <0: la cara ve A OTRA PARTE
            side: old,                    // 0 Front, 1 Back, 2 Double
            hoverFront: hFront,
            hoverDouble: hDouble,
            panelaId: p.id, u: +u.toFixed(3), v: +v.toFixed(3),
          };
        }""")
        print(out)
        b.close()
finally:
    server.terminate()

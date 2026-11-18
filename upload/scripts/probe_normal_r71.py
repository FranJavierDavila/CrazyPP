#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_normal_r71.py — autopsia de la panela C: normal del ShapeGeometry,
material.side y raycast desde los ojos del jugador (Front vs Double)."""
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3675', '--bind', '127.0.0.1',
     '--directory', '/home/z/my-project/upload/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader',
                                     '--enable-unsafe-swiftshader'])
        page = b.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('http://127.0.0.1:3675/game.html', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        page.wait_for_timeout(1000)
        out = page.evaluate("""() => {
          const G = window.__PP_GAME;
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
          const V3 = G.menuGroup.position.constructor;
          const origen = new V3();
          G.camera.getWorldPosition(origen);
          const cw = new V3();
          pa.getWorldPosition(cw);
          const dir = cw.clone().sub(origen).normalize();
          const RC = G.muRaycaster ? G.muRaycaster.constructor
                                   : (G._menuRayC || null);
          let rc;
          if (RC) rc = new RC();
          else {
            // el juego no expone la clase: usa el raycaster de muRaycaster
            rc = null;
          }
          if (!rc) {
            // intenta con el raycaster global del juego si existe
            const cands = Object.getOwnPropertyNames(G)
              .filter((k) => /ray/i.test(k));
            return { sinRaycaster: cands };
          }
          rc.set(origen, dir);
          const hitsF = rc.intersectObjects(G._menuPanelas, false);
          const old = pa.material.side;
          pa.material.side = 2;                  // DoubleSide
          rc.set(origen, dir);
          const hitsD = rc.intersectObjects(G._menuPanelas, false);
          pa.material.side = old;
          return {
            normal: {x: +n.x.toFixed(3), y: +n.y.toFixed(3), z: +n.z.toFixed(3)},
            side: old,                           // 0 Front, 1 Back, 2 Double
            hitsFront: hitsF.length,
            hitsDouble: hitsD.length,
            camPos: [+origen.x.toFixed(2), +origen.y.toFixed(2), +origen.z.toFixed(2)],
            panelaPos: [+cw.x.toFixed(2), +cw.y.toFixed(2), +cw.z.toFixed(2)],
            grupoMira: +(G.menuGroup.getWorldPosition(new V3()).z.toFixed(2)),
          };
        }""")
        print(out)
        b.close()
finally:
    server.terminate()

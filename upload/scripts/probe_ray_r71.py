#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_ray_r71.py — autopsia del RAYCAST con THREE real (import dinámico).

El menú se renderiza (captura) pero el rayo del juego no intersecta las
panelas ShapeGeometry. Este sondeo compara, para el MISMO rayo:
  · boundingSphere del geometry
  · matrixWorld de la panela (¿estancada?)
  · Raycaster THREE FrontSide vs DoubleSide
  · intersección ANALÍTICA local (plano z=0, rect w×h)
"""
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3681', '--bind', '127.0.0.1',
     '--directory', '/home/z/my-project/upload/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader',
                                     '--enable-unsafe-swiftshader'])
        page = b.new_page(viewport={'width': 960, 'height': 600})
        page.goto('http://127.0.0.1:3681/game.html', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        page.wait_for_timeout(1200)
        out = page.evaluate("""async () => {
          const THREE = await import('three');
          const G = window.__PP_GAME;
          if (!G.menuOpen) G.toggleMenu();
          G.anchorMenu(true);
          const pa = G.menuMesh;
          const g = pa.geometry;
          g.computeBoundingSphere();
          const bs = g.boundingSphere;
          const V3 = G.menuGroup.position.constructor;
          const ojos = new V3();
          G.camera.getWorldPosition(ojos);
          const cw = new V3();
          pa.getWorldPosition(cw);
          // matrixWorld ¿fresca? — compara con lo que debería (position)
          const mw = pa.matrixWorld.elements;
          const mwPos = { x: +mw[12].toFixed(2), y: +mw[13].toFixed(2), z: +mw[14].toFixed(2) };
          // raycast THREE real desde los ojos al centro
          const dir = cw.clone().sub(ojos).normalize();
          const rc = new THREE.Raycaster();
          rc.set(ojos, dir);
          const hitsF = rc.intersectObjects(G._menuPanelas, false);
          const old = pa.material.side;
          pa.material.side = THREE.DoubleSide;
          const rc2 = new THREE.Raycaster();
          rc2.set(ojos, dir);
          const hitsD = rc2.intersectObjects(G._menuPanelas, false);
          pa.material.side = old;
          // intersección analítica en LOCAL: origen/dir → espacio local
          const inv = new THREE.Matrix4().copy(pa.matrixWorld).invert();
          const oL = ojos.clone().applyMatrix4(inv);
          const dL = dir.clone().transformDirection(inv);
          const tL = oL.z !== 0 ? -oL.z / dL.z : NaN;
          const pL = oL.clone().addScaledVector(dL, tL);
          const p = pa.userData.panela;
          return {
            boundingSphere: { r: +bs.radius.toFixed(3),
              c: [+bs.center.x.toFixed(3), +bs.center.y.toFixed(3), +bs.center.z.toFixed(3)] },
            verts: g.attributes.position.count,
            tris: g.index ? g.index.count / 3 : 0,
            matrixWorldPos: mwPos,
            meshPosition: [+pa.position.x.toFixed(2), +pa.position.y.toFixed(2), +pa.position.z.toFixed(2)],
            grupoPos: [+G.menuGroup.position.x.toFixed(2), +G.menuGroup.position.y.toFixed(2), +G.menuGroup.position.z.toFixed(2)],
            ojos: [+ojos.x.toFixed(2), +ojos.y.toFixed(2), +ojos.z.toFixed(2)],
            hitsFront: hitsF.length,
            hitsDouble: hitsD.length,
            hitFrontInfo: hitsF[0] ? { d: +hitsF[0].distance.toFixed(3),
              uv: [+hitsF[0].uv.x.toFixed(3), +hitsF[0].uv.y.toFixed(3)] } : null,
            analitica: { tLocal: +tL.toFixed(3),
              punto: [+pL.x.toFixed(3), +pL.y.toFixed(3)],
              dentro: Math.abs(pL.x) <= p.anchoM / 2 && Math.abs(pL.y) <= p.altoM / 2 },
            side: old,
          };
        }""")
        import json
        print(json.dumps(out, indent=1, ensure_ascii=False))
        b.close()
finally:
    server.terminate()

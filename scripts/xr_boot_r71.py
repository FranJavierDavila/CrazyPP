#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xr_boot_r71.py — SIMULACIÓN DEL ARRANQUE XR REAL (camino M4 verbatim).

El dueño entra en VR: onSessionStart → rules.startMatch + bloque M4:
  menuOpen=true; menuGroup.visible=true; anchorMenu();  ← SIN forzar
Con menuPin=true (default), anchorMenu() SIN forzar RETORNA sin anclar ni
firmar (_menuAnchorEst=''). El heal r114 del primer frame entonces dispara:
suelta la chincheta y re-ancla — el menú queda SIGUIENDO (no fijo).
Este arnés mide: pin, distancia al rostro, cambios de posición del grupo y
disparos del heal durante 300 frames tras el arranque M4.
"""
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3680', '--bind', '127.0.0.1',
     '--directory', '/home/z/my-project/upload/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader',
                                     '--enable-unsafe-swiftshader'])
        page = b.new_page(viewport={'width': 960, 'height': 600})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto('http://127.0.0.1:3680/game.html', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        page.wait_for_timeout(1000)
        # instrumentation: contar disparos del heal
        page.evaluate("""() => {
          const G = window.__PP_GAME;
          Object.defineProperty(G.renderer.xr, 'isPresenting',
            { value: true, configurable: true });
          G.connected = [true, true];
          G._healCount = 0;
          const orig = G._menuAnclaHeal.bind(G);
          G._menuAnclaHeal = function () {
            const antes = this.menuPin;
            orig();
            if (antes !== this.menuPin || true) G._healCount++;
          };
        }""")
        # — ARRANQUE XR REAL (onSessionStart: startMatch + bloque M4 con el
        # fix r71 — anchorMenu(true) — firmado de estancia incluido) —
        page.evaluate("""() => {
          const G = window.__PP_GAME;
          G.pendingMode = 'match';
          G.onSessionStart();
        }""")
        # muestrear 30 veces x 10 frames
        muestras = []
        for i in range(30):
            m = page.evaluate("""() => {
              const G = window.__PP_GAME;
              const V3 = G.menuGroup.position.constructor;
              const ojos = G.camera.getWorldPosition(new V3());
              const gp = G.menuGroup.position;
              const d = gp.distanceTo(ojos);
              return { pin: G.menuPin, dist: +d.toFixed(3),
                       pos: [ +gp.x.toFixed(2), +gp.y.toFixed(2), +gp.z.toFixed(2) ],
                       est: G._menuAnchorEst, heals: G._healCount };
            }""")
            muestras.append(m)
            page.wait_for_timeout(50)
        # resumen: ¿el pin muere? ¿la posición se mueve sola?
        pins = [m['pin'] for m in muestras]
        dists = [m['dist'] for m in muestras]
        print('pin (primeros 10):', pins[:10])
        print('pin (últimos 10):', pins[-10:])
        print('dist (primeros 10):', dists[:10])
        print('dist (últimos 10):', dists[-10:])
        print('posición inicial:', muestras[0]['pos'], '· final:', muestras[-1]['pos'])
        print('estancia firmada:', repr(muestras[-1]['est']), '· heals disparados:', muestras[-1]['heals'])
        movio = max(dists) - min(dists)
        print('rango de dist:', round(min(dists), 3), '→', round(max(dists), 3),
              '(viaja' if movio > 0.05 else '(QUIETO)', round(movio, 3), 'm)')
        if errs:
            print('pageerrors:', errs[:3])
        b.close()
finally:
    server.terminate()

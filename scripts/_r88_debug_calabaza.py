#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonda de depuración r88: ¿paso() de la calabaza corre? ¿qué state hay
en la sala 2D? ¿dónde queda la bola aparcada?"""
import os, functools, json, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8766
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('CON:' + m.text) if 'r88' in m.text else None)
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(13000)
    out = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const motor = ctrl.poderes;
      const r = { state: g.rules.state, active: !!(g.renderer && g.renderer.xr && g.renderer.xr.isPresenting),
                  updateHookVivo: typeof ctrl.update };
      // ¿CTRL.update lo llama el bucle? medimos el reloj del motor con un parche temporal
      let ticks = 0; const orig = motor.update.bind(motor);
      motor.update = (dt, c) => { ticks++; return orig(dt, c); };
      await new Promise(r2 => setTimeout(r2, 1000));
      motor.update = orig;
      r.ticksPorSegundo = ticks;
      // lanzamos la calabaza a mano y damos 1,2 s
      const p = motor.lista.find(p => p.kind === 'calabaza');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const C = motor.ctx.calabaza;
      r.lanzada = !!C;
      await new Promise(r2 => setTimeout(r2, 1200));
      if (C) {
        r.cal = { t: +C.t.toFixed(2), listo: C.listo, gltf: !!C.gltf,
                  pos: C.gltf ? [+C.gltf.position.x.toFixed(2), +C.gltf.position.y.toFixed(2), +C.gltf.position.z.toFixed(2)] : null,
                  bola: [+g.ball.pos.x.toFixed(2), +g.ball.pos.y.toFixed(2), +g.ball.pos.z.toFixed(2)],
                  activo: motor.activo ? motor.activo.kind : null,
                  powerT: +motor.powerT.toFixed(2), bolaOculta: !g.ballMesh.visible,
                  mats: C.mats.length };
      }
      try { motor._cerrar(); } catch (e) {}
      r.errs = window.__r88err || null;
      return r;
    }""")
    print(json.dumps(out, indent=1))
    print('pageerrors:', errs[:4])
    b.close()
srv.shutdown()

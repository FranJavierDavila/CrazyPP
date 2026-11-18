#!/usr/bin/env python3
"""Sonda rápida: estado del motor de poderes + champDecor en vivo."""
import os, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8749
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load', timeout=60000)
    pg.wait_for_timeout(12000)
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), g = ctrl.game, motor = ctrl.poderes;
      const cd = g.champDecor;
      return {
        vive: true,
        motor: { cd: motor.cd, pendT: motor.pendT, powerT: motor.powerT, pend: !!motor.pend,
                 activo: motor.activo && motor.activo.kind, bag: motor.bag.length,
                 lista: motor.lista.map(p=>p.kind), garantiaT: motor.garantiaT },
        decor: { activeId: cd && cd.activeId, hidden: g.champDecorHidden,
                 ninos: cd && cd.group ? cd.group.children.length : -1,
                 piezas: (H.man() && H.man().decor.pieces || []).length },
        champsActiveId: g.champs && g.champs.activeId,
        room: g.champRoom && g.champRoom.activeId,
        errs: %d,
      };
    }""" % len(errs))
    import json as J
    print(J.dumps(st, indent=1, ensure_ascii=False))
    # segundo paso: disparar limpio y ver qué pasa paso a paso
    p2 = pg.evaluate("""() => {
      const motor = window.__PP_HALLOWEEN.ctrl().poderes;
      const st1 = { antes: { cd: motor.cd, pendT: motor.pendT, powerT: motor.powerT, pend: !!motor.pend } };
      motor.cd = 0;
      motor.disparar();
      st1.trasDisparar = { pendT: motor.pendT, pend: motor.pend ? motor.pend.kind : null,
                           freeze: window.__PP_HALLOWEEN.ctrl().game.freezeT };
      try { motor.pendT = 0.01; motor._lanzar(); st1.trasLanzar = { activo: motor.activo && motor.activo.kind, powerT: motor.powerT }; }
      catch (e) { st1.trasLanzar = { error: '' + e }; }
      try { motor._cerrar(); st1.trasCerrar = { activo: motor.activo, powerT: motor.powerT }; } catch (e) { st1.trasCerrar = { error: '' + e }; }
      return st1;
    }""")
    print(J.dumps(p2, indent=1, ensure_ascii=False))
    b.close()
srv.shutdown()

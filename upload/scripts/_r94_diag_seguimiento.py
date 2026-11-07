#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico r94: ¿por qué la calabaza no siguió a la bola movida en la
sonda C? Muestreo temporal de dist / posiciones / estado / powerT."""
import os, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8815

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => { const g = window.__PP_HALLOWEEN && window.__PP_HALLOWEEN.ctrl().game;
                           if (g && g.champIntro) g.hideChampIntro(true); }""")
    pg.wait_for_timeout(3000)

    vivo = pg.evaluate("""() => {
      const P = window.__PP_HALLOWEEN.ctrl().poderes;
      const cal = (P.lista || []).find(p => p.kind === 'calabaza');
      P.pend = cal; P.pendT = 0.001; return true;
    }""")
    pg.wait_for_timeout(600)

    diag = pg.evaluate("""async () => {
      const ctrl = window.__PP_HALLOWEEN.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      const C = P.ctx && P.ctx.calabaza;
      if (!C || !C.gltf) return { err: 'sin calabaza' };
      const d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
      const out = { antes: { dist: +d(C.gltf.position, g.ballMesh.position).toFixed(6),
                             estado: g.rules.state,
                             activo: P.activo && P.activo.kind,
                             powerT: +P.powerT.toFixed(2) } };
      g.ball.pos.x += 0.35; g.ball.pos.y += 0.22; g.ball.pos.z -= 0.4;
      g.ballMesh.position.copy(g.ball.pos);
      out.muestras = [];
      for (let i = 0; i < 12; i++) {
        await new Promise(r => setTimeout(r, 50));
        out.muestras.push({
          t: (i + 1) * 50,
          dist: +d(C.gltf.position, g.ballMesh.position).toFixed(6),
          cala: [ +C.gltf.position.x.toFixed(3), +C.gltf.position.y.toFixed(3), +C.gltf.position.z.toFixed(3) ],
          mesh: [ +g.ballMesh.position.x.toFixed(3), +g.ballMesh.position.y.toFixed(3), +g.ballMesh.position.z.toFixed(3) ],
          bola: [ +g.ball.pos.x.toFixed(3), +g.ball.pos.y.toFixed(3), +g.ball.pos.z.toFixed(3) ],
          estado: g.rules.state,
          visibleBola: g.ballMesh.visible,
          explotada: !!C.explotada,
          powerT: +P.powerT.toFixed(2),
        });
        if (out.muestras[i].explotada) break;
      }
      return out;
    }""")
    import json
    print(json.dumps(diag, indent=1, ensure_ascii=False))
    print('pageerrors:', errs[:3])
    b.close()
srv.shutdown()

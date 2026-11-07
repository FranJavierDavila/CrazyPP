#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r89_probe_mano.py — caza el salto de spawn (0-2 vivos, se esperaban 3)."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8801
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

JS = r"""() => {
  const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
  const p = motor.lista.find(q => q.kind === 'mano');
  const impl = H.pods.mano;
  const log = [];
  const origSpawn = impl._spawn;
  impl._spawn = function(ga, M) {
    const D = window.__PP_CORE.DIMS;
    const HW = D.tableHalfWidth, HL = D.tableHalfLength, cz = D.tableCenterZ;
    const MON = 0.23 * 1.18, BORDE = 0.07;
    const b = ga.ball ? ga.ball.pos : null;
    const SLOTS = [[-0.30, -0.9], [0.30, 0.0], [-0.30, 0.9]];
    const detalle = [];
    for (let si = 0; si < 3; si++) {
      const cx2 = SLOTS[si][0], cz2 = SLOTS[si][1];
      const canto = (Math.abs(cx2) + MON + BORDE > HW) || (Math.abs(cz2) + MON + BORDE > HL);
      let libre = true;
      for (const v of M.vivos) {
        const dx = cx2 - v.mont.position.x, dz = (cz + cz2) - v.mont.position.z;
        if (dx*dx + dz*dz < 0.62*0.62) { libre = false; break; }
      }
      const bola = !!(b && Math.abs(b.x - cx2) < 0.24 && Math.abs(b.z - (cz + cz2)) < 0.24);
      detalle.push('s' + si + ':' + (canto ? 'CANTO' : (libre ? (bola ? 'BOLA' : 'ok') : 'ocupado')));
    }
    log.push('spawn→' + detalle.join(' ') + ' vivos=' + M.vivos.length);
    const r = origSpawn.call(this, ga, M);
    log.push('  → vivos ahora ' + M.vivos.length);
    return r;
  };
  motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
  const M = motor.ctx.mano;
  const pre = { tex: M ? M.tex.length : -1, mont: M ? !!M.texMonticulo : null,
                state: g.rules.state, activo: motor.activo ? motor.activo.kind : null,
                prox: M ? M.prox : null };
  for (let s = 0; s < 6; s++) { try { motor.update(0.5, motor.game.rules); } catch (e) { log.push('EXC update: ' + e); } }
  impl._spawn = origSpawn;
  return { pre, log, vivos: M ? M.vivos.length : -1, ball: g.ball ? [+g.ball.pos.x.toFixed(2), +g.ball.pos.z.toFixed(2)] : null };
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(15000)
    out = pg.evaluate(JS)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    b.close()
srv.shutdown()

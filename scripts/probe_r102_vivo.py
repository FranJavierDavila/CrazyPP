#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_r102_vivo.py — el arreglo del SEGUNDO TOQUE, probado EN EL BUNDLE VIVO.

Arranca el game.html V3.6.200-SDK6 headless, monta un rallye guiado contra la
CPU real (la IA de c06 + el árbitro Rules + updateAIPaddlePose, todo el juego
real en su bucle rAF): el «jugador» scripted devuelve cada bola hacia el rival
y la sonda mide
  · DEVOLUCIONES del rival (¿responde al 2º, 3º, N-ésimo toque?),
  · PARQUES: cadena en recover con la pala quieta ≥ 1,0 s mientras la bola
    entra a su campo (el defecto del dueño en V3.6.199),
  · pageerrors del bundle.
Verde = devoluciones en todos los intercambios y 0 parques ≥ 1 s.
"""
import functools, json, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8841
OK, FAIL = [], []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

DRIVE = r"""
(() => {
  const g = window.__PP_GAME;
  if (!g) return { err: 'sin __PP_GAME' };
  const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || g.DIMS;
  if (!D) return { err: 'sin DIMS' };
  const C = D.tableCenterZ, HL = D.tableHalfLength;
  const V = g.ball.pos.constructor;
  // el cuerpo EXACTO del case 'start' del menú (arranque rápido vs CPU)
  g.closeTrainingV3 && g.closeTrainingV3();
  if (g.calibPala) g.exitCalib();
  if (g.champs) g.champs.leaveAll();
  g.exitHall();
  g.doblesActivo = false;
  if (g.mode !== 'match') g.switchMode('match');
  else { g.rules.bestOf = 3; g.rules.startMatch('match'); g.resetToss(); }
  g.closeMenu();
  window.__r102 = { f: 0, ult: new V(), quieta: 0, parks: 0, parkMax: 0,
    devRival: 0, devJug: 0, saques: 0, sgnPrev: 0, causas: {}, fase: 'arranque' };
  window.__r102drive = setInterval(() => {
    const r = window.__r102, b = g.ball, ai = g.ai, ch = ai.chain;
    const rules = g.rules;
    r.f++;
    if (rules.state === 'serve' && rules.server === 'player') {
      // saque scripted del jugador (reglamento: bote propio → cruzar)
      rules.beginServeRally('player');
      b.pos.set((Math.random() - 0.5) * 0.2, 1.05, C + HL - 0.10);
      b.vel.set((Math.random() - 0.5) * 0.4, 1.1 + Math.random() * 0.3,
                -(3.3 + Math.random() * 0.5));
      b.spin.set(0, 0, 0);
      r.saques++;
      r.sgnPrev = 0;
      r.fase = 'rallye';
    }
    const entrante = b.vel.z * ai.sign > 0 && (b.pos.z - C) * ai.sign > 0;
    const pala = ch ? ch.cur : ai.pos;
    if (pala.distanceTo(r.ult) < 0.0015 && ch && ch.phase === 'recover' && entrante) {
      r.quieta += 1 / 60;
      if (r.quieta >= 1.0) { r.parks++; r.parkMax = Math.max(r.parkMax, r.quieta); r.quieta = 0.55; }
    } else r.quieta = 0;
    r.ult.copy(pala);
    // devoluciones por BORDES de signo (histéresis ±0,8 m/s)
    const vz = b.vel.z;
    const sgn = vz > 0.8 ? 1 : (vz < -0.8 ? -1 : (r.sgnPrev || 0));
    if (r.sgnPrev === -1 && sgn === 1) r.devRival++;
    if (r.sgnPrev === 1 && sgn === -1) r.devJug++;
    if (sgn) r.sgnPrev = sgn;
    // devolución del «jugador»: bola botada en mi campo y viniéndome
    if (rules.state === 'rally' && rules.validBounce && vz > 0.2 &&
        b.pos.z > C + HL - 0.30) {
      b.pos.set(Math.max(-0.45, Math.min(0.45, b.pos.x)), 1.02, C + HL + 0.28);
      b.vel.set((Math.random() - 0.5) * 1.0, 1.6 + Math.random() * 0.5,
                -(3.6 + Math.random() * 0.8));
      rules.registerPaddleHit('player');
      r.devJug++;
    }
    // causas de punto para el informe
    if (rules.state === 'point') {
      r.causas[rules.message] = (r.causas[rules.message] || 0) + 1;
      r.fase = 'punto→' + (rules.computeNextServer ? rules.computeNextServer() : '?');
    }
  }, 1000 / 60);
  return { ok: true };
})()
"""

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    # sin clic de menú: el drive arranca el partido por API (case 'start')

    ver = pg.evaluate("() => (window.__PP_CORE && window.__PP_CORE.VERSION) || (window.VERSION || '')")
    badge = pg.evaluate("() => { const e = document.querySelector('#verBadge'); return e ? e.textContent : ''; }")
    CHK('3.6.200' in str(ver) or '3.6.200' in str(badge),
        'bundle vivo sella V3.6.200-SDK6 (core=%s badge=%s)' % (ver, badge))

    d = pg.evaluate(DRIVE)
    CHK('ok' in (d or {}), 'rallye guiado montado (%s)' % (json.dumps(d) if 'err' in (d or {}) else 'drive activo'))
    pg.wait_for_timeout(45000)   # 45 s de rallye
    r = pg.evaluate("() => window.__r102 ? { f: window.__r102.f, parks: window.__r102.parks,"
                    " parkMax: +window.__r102.parkMax.toFixed(2), devR: window.__r102.devRival,"
                    " devJ: window.__r102.devJug, estado: window.__PP_GAME.rules.state,"
                    " marcador: [window.__PP_GAME.rules.scorePlayer, window.__PP_GAME.rules.scoreAi],"
                    " causas: window.__r102.causas } : null")
    print('  · telemetría:', json.dumps(r))
    if r:
        CHK(r['devR'] >= 8, 'el rival DEVUELVE en cadena (%d devoluciones al 2º…N toque)' % r['devR'])
        CHK(r['parks'] == 0, '0 parques ≥ 1 s en recover (antes: la pala se quedaba bloqueada)')
        CHK(r['devR'] >= r['devJ'] - 4, 'el rival responde a CADA devolución (%d vs %d)' % (r['devR'], r['devJ']))
    CHK(len(errs) == 0, '0 pageerrors en el bundle vivo %s' % (errs[:2] if errs else ''))

    pg.screenshot(path='/tmp/render/r102_vivo.png')
    b.close()

print('— RESUMEN: %d OK · %d FALLOS —' % (len(OK), len(FAIL)))
raise SystemExit(1 if FAIL else 0)

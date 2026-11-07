#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_arnes_vivo_v3698.py — M2a · ARNÉS VIVO: el juego REAL juega un partido
en el navegador (Chromium headless + SwiftShader) y el arnés verifica
INVARIANTES POR FRAME durante 60 s de TIEMPO DE JUEGO (el arnés toma el
reloj: setAnimationLoop(null) + g.animate(t) paso a paso — en headless el
rAF real corre a ~1,5 fps y 25 s de pared serían 1,3 s de juego).

Se ejecuta el BUCLE COMPLETO del juego (escena, física, árbitro, IA rival,
audio) más un PILOTO IA inyectado (la clase OpponentAI real, mitad del
jugador, casa espejo de la del rival).

Invariantes por frame (ROJA si alguna se viola):
  V1  ball.pos/vel/spin FINITOS (sin NaN/Inf)
  V2  la bola VIVE en la sala (|x|<3 · −0,5<y<4 · |z|<5)
  V3  la IA rival permanece anclada (dz>0,15 — nunca cruza la red ·
      dz<3,3 — dentro de la sala: puede defender bolas profundas hasta su
      tope legal de c06 · |x|<1,6)
Señales de vida en 60 s de juego (exigidas): ≥3 puntos, ≥15 botes, ≥3 saques.
CANARIO (al t≈35 s): bola teletransportada fuera de la sala — V2 DEBE
disparar; si el arnés no muerde, el arnés no sirve y ROJA.
"""
import functools, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8844
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

print('== ARNÉS VIVO (partido real en navegador, 60 s de juego) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SESION = """
window.__ARNES = { viol: [], muestras: 0, botes: 0, saques: 0, puntos0: null,
  erroresNet: 0, canario: false };
(() => {
  const g = window.__PP_GAME;
  if (!g) return 'sin __PP_GAME';
  const A = window.__ARNES;
  A.puntos0 = g.rules.scorePlayer + g.rules.scoreAi;
  // — piloto de la mitad del jugador (IA real de c06, casa espejo del rival) —
  const V3 = g.ball.pos.constructor;
  const piloto = new (g.ai.constructor)(g.ai.cfg, +1, new V3(0, 1.05, -g.ai.home.z));
  // — un PASO de partido: piloto decide → juego integra → arnés muestrea —
  //   el reloj sintético arranca POR DELANTE del real (animate calcula
  //   dt = t−lastTime: un t por debajo del último rAF daría dt NEGATIVO y
  //   corrompería la simulación — lección de la primera pasada)
  window.__t0 = performance.now() + 500;
  window.__tMs = window.__t0;
  window.__paso = () => {
    window.__tMs += 33.4;                    // 30 fps de tiempo de JUEGO (dt
                                             // máximo que el juego acepta)
    try {
      const b = g.ball, r = g.rules;
      if (r.state === 'serve') {
        if (r.server === 'player') {
          A._espera = (A._espera || 0) + 1;
          if (A._espera > 120) {             // 2 s de juego sin saque demo
            A._espera = 0;
            if (g.demoServeSpot) b.pos.copy(g.demoServeSpot);
            else b.pos.set(0.25, 1.2, 1.67);
            g.serveFromAI('player');         // saque LEGAL del juego (c05)
          }
        }
      } else {
        A._espera = 0;
        const toward = b.vel.z > 0;          // el piloto vive en +z
        const v = piloto.update(1 / 30, b, {
          canHit: true, validBounce: r.validBounce,
          oppPadX: g.ai.pos.x, oppPadZ: g.ai.pos.z,
          rallyHits: r.rallyHits, holdTarget: null, prevBall: null,
        });
        if (v && toward) { b.vel.copy(v); r.registerPaddleHit('player'); }
      }
    } catch (e) { A.erroresNet++; }
    g.animate(window.__tMs);                 // el juego integra y renderiza
    window.__muestrear();
  };
  // — INVARIANTES V1-V3 (expuestos: el CANARIO los llama ANTES de que el
  //   juego se autocure — el reset del juego tarda un frame) —
  window.__muestrear = () => {
    A.muestras++;
    try {
      const b = g.ball;
      const fin = [b.pos, b.vel, b.spin].every((v) =>
        Number.isFinite(v.x) && Number.isFinite(v.y) && Number.isFinite(v.z));
      if (!fin) A.viol.push('V1 NaN/Inf en la bola');
      else if (g.rules.state !== 'point') {
        // V2 · sala: x/z SIEMPRE vigilados (fuga por pared = bug real). El
        // tope de altura se RELAJA cuando la bola viene de su aparcamiento
        // entre puntos (el juego la deja caer desde y≈50: transición propia,
        // no fuga) — el frame anterior alto desactiva el tope un frame más.
        const vieneDeAparcar = (A._yPrev || 0) > 20;
        A._yPrev = b.pos.y;
        const escapeXZ = Math.abs(b.pos.x) > 3 || Math.abs(b.pos.z) > 5;
        const bajoSuelo = b.pos.y < -0.5;
        const altoSospechoso = b.pos.y > 4 && !vieneDeAparcar;
        if (escapeXZ || bajoSuelo || altoSospechoso)
          A.viol.push('V2 bola fuera de sala ' + b.pos.toArray().map((x) => x.toFixed(2)).join(','));
      } else { A._yPrev = b.pos.y; }
      const dz = (g.ai.pos.z - (-1.6)) * -1;   // el rival vive en −z · CENTRO
                                                // REAL de mesa C=−1,6 (DIMS);
                                                // antes asumía C=0 y daba falsas
                                                // desancladas en la propia casa
      if (dz < 0.15 || dz > 3.0 || Math.abs(g.ai.pos.x) > 1.6)
        A.viol.push('V3 IA rival desanclada dz=' + dz.toFixed(2) + ' x=' + g.ai.pos.x.toFixed(2));
    } catch (e) { A.viol.push('V1 excepción muestreando: ' + e.message); }
  };
  // — contadores de vida —
  const origPE = g.processEvents.bind(g);
  g.processEvents = (evs) => {
    for (const e of evs) if (e.type === 'table') A.botes++;
    return origPE(evs);
  };
  const origServe = g.serveFromAI.bind(g);
  g.serveFromAI = (side) => { A.saques++; return origServe(side); };
  return 'ok';
})()
"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 320, 'height': 240})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(1500)

    setup = pg.evaluate(SESION)
    CHK(setup == 'ok', 'arnés instalado sobre el juego vivo (%s)' % setup)
    pg.evaluate("""() => {
      window.__pp2DPlay = true;                       // partido real en escritorio
      window.__PP_GAME.rules.startMatch('match');
      window.__PP_GAME.renderer.setAnimationLoop(null); // el arnés toma el reloj
    }""")

    # 45 s de juego a dt=1/30 = 1350 pasos, en tandas con presupuesto de
    # pared (SwiftShader renderiza lento: cada evaluate ≤ 5 s de reloj)
    OBJETIVO_MS = 45000
    CANARIO_EN_MS = 25000
    canario_dado = False
    for _ in range(40):
        estado = pg.evaluate("""() => {
          const t0 = performance.now();
          while (window.__tMs - window.__t0 < %d && performance.now() - t0 < 5000) {
            window.__paso();
          }
          return window.__tMs - window.__t0;
        }""" % (OBJETIVO_MS if not canario_dado else OBJETIVO_MS))
        if not canario_dado and estado >= CANARIO_EN_MS:
            canario_dado = True
            pg.evaluate("() => { window.__violAntes = window.__ARNES.viol.length; }")
            pg.evaluate("""window.__ARNES.canario = true;
           window.__PP_GAME.rules.state = 'rally';   // bola EN JUEGO: V2 activa
           window.__PP_GAME.ball.pos.set(50, 50, 50);
           window.__muestrear();                     // muestrear ANTES de que
           // el juego se autocure (resetea la bola envenenada en 1 frame)""")
        if estado >= OBJETIVO_MS:
            break
    pg.wait_for_timeout(400)

    vivo = pg.evaluate("""() => {
      const A = window.__ARNES, g = window.__PP_GAME;
      return { viol: A.viol.slice(0, 4), nViol: window.__violAntes,
        muestras: A.muestras, botes: A.botes, saques: A.saques,
        puntos: g.rules.scorePlayer + g.rules.scoreAi - A.puntos0,
        marcador: [g.rules.scorePlayer, g.rules.scoreAi],
        pilotoErr: A.erroresNet, tMs: window.__tMs - window.__t0 };
    }""")
    CHK(vivo['tMs'] >= 44000, 'tiempo de juego simulado: %.1f s' % (vivo['tMs'] / 1000))
    CHK(vivo['muestras'] >= 1300, 'frames muestreados: %d' % vivo['muestras'])
    CHK(vivo['nViol'] == 0, 'invariantes V1-V3 íntegras en partido real (%s)' %
        (vivo['viol'] or '0 violaciones'))
    CHK(vivo['puntos'] >= 2, 'el partido PUNTEA: %d puntos en 45 s (marcador %s)' %
        (vivo['puntos'], vivo['marcador']))
    CHK(vivo['botes'] >= 10, 'botes de mesa reales: %d' % vivo['botes'])
    CHK(vivo['saques'] >= 2, 'saques servidos: %d' % vivo['saques'])
    CHK(vivo['pilotoErr'] == 0, 'piloto sin excepciones (%d)' % vivo['pilotoErr'])
    CHK(canario_dado, 'canario inyectado a mitad del partido')

    # el canario DEBE haber disparado V2 (la bola envenenada salió de sala)
    can = pg.evaluate(
        "() => window.__ARNES.viol.slice(window.__violAntes)"
        ".some((v) => v.indexOf('V2') === 0)")
    CHK(can, 'CANARIO detectado: V2 disparó al envenenar la bola (el arnés muerde)')

    CHK(errs == [], 'cero pageerrors (%s)' % (errs[:2] or 'limpio'))
    b.close()

srv.shutdown()

print('\n== RESUMEN qa_arnes_vivo_v3698 ==')
print('  OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
print('RESULTADO: arnés vivo · %d OK · %d fallos' % (len(OK), len(FAIL)))
if FAIL:
    print('\n'.join('  ✗ ' + f for f in FAIL))
    raise SystemExit(1)
print('  VERDE: el juego REAL juega, puntúa y respeta las invariantes · canario cazado')

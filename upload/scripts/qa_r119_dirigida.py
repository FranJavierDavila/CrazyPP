#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r119_dirigida.py — M7c · DOBLES 2v2 (PROTOTIPO), regla del dueño:
sólo lo tocado HOY. Servidor estático de public/ + reloj sintético
(patrón arnés vivo): el juego REAL juega y el QA verifica.

1 · Arranque limpio: dobles OFF por defecto, palas extra OCULTAS, 0 pageerrors.
2 · Botón real en AJUSTES › JUEGO (página optsJuego) y activación por
    menuClick: flag + partido arrancado + mensajes + meshes vivos.
3 · Configuración IA: rival 2 con la MISMA cfg efectiva que el rival 1 y
    compañero anclado a easy (sin estilo ni adaptación).
4 · RALLY REAL 2v2 (2D): el compañero devuelve bolas del lado del jugador
    (registerPaddleHit('player')) y el rival 2 las del lado CPU.
5 · ARBITRAJE DE ALCANCE (par completo): pala del jugador junto a la bola →
    el compañero NO roba; pala lejos → SÍ toma (y simétrico en el lado CPU).
6 · Regla de doble golpe: el segundo toque del mismo equipo = falta (Rules).
7 · Anti-fugas: ▶ JUGAR limpia doblesActivo y las palas extra desaparecen.

Uso: python3 scripts/qa_r119_dirigida.py
Salida: RESULTADO: N OK · N fallos · exit 0/1
"""
import functools
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading

from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8861
OK = []
FAIL = []


def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)


print('== QA r119 · DOBLES 2v2 (prototipo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

RELOJ = """() => {
  // toma del reloj (patrón arnés vivo): rAF headless ~1,5 fps no sirve
  window.__t0 = performance.now() + 500;
  window.__tMs = window.__t0;
  window.__PP_GAME.renderer.setAnimationLoop(null);
  window.__paso = () => {
    window.__tMs += 33.4;                 // dt 1/30 s de tiempo de juego
    try { window.__PP_GAME.animate(window.__tMs); } catch (e) {}
  };
  return 'ok';
}"""

# pasos hasta que la expresión sea verdad (sondeo por tandas de 2 pasos)
HASTA = """(cond) => {
  for (let i = 0; i < 40; i++) {
    for (let k = 0; k < 2; k++) window.__paso();
    if (%s) return i * 2 + 2;
  }
  return -1;
}"""


def pasos_hasta(pg, cond_js):
    return pg.evaluate(HASTA % cond_js)


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

    # ── 1 · arranque limpio ──────────────────────────────────────────────
    a = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      if (!g) return { vivo: false };
      return {
        vivo: true,
        activo: g.doblesActivo === false,
        hayComp: !!g.aiComp && g.aiComp.sign === 1,
        hayRiv2: !!g.aiRiv2 && g.aiRiv2.sign === -1,
        casaComp: g.aiComp.home.z > 0, casaRiv2: g.aiRiv2.home.z < 0,
        meshComp: !!g.partnerPaddleMesh && g.partnerPaddleMesh.visible === false,
        meshRiv2: !!g.riv2PaddleMesh && g.riv2PaddleMesh.visible === false,
        stats: g._dbStats && g._dbStats.comp === 0 && g._dbStats.r2 === 0,
      };
    }""")
    CHK(a.get('vivo'), '1 · __PP_GAME vivo')
    CHK(a.get('activo'), '1 · dobles OFF por defecto')
    CHK(a.get('hayComp') and a.get('hayRiv2'), '1 · aiComp(sign +1) y aiRiv2(sign -1) nacen')
    CHK(a.get('casaComp') and a.get('casaRiv2'), '1 · casas correctas (compañero lado jugador, riv2 lado CPU)')
    CHK(a.get('meshComp') and a.get('meshRiv2'), '1 · palas extra OCULTAS al arranque')
    CHK(a.get('stats'), '1 · contadores de golpes a cero')

    # ── 2 · botón real + activación por menuClick ────────────────────────
    pg.evaluate("() => { window.__pp2DPlay = true; }")   # partido real en escritorio
    clk = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.menuPage = 'optsJuego'; g.menuSec = '';
      g.drawMenu();
      const rects = g._menuRects || [];
      const idx = rects.findIndex((x) => x.id === 'dobles');
      if (idx < 0) return { error: 'sin rect', n: rects.length };
      const antes = g.doblesActivo;
      g.menuClick(idx, 0);
      return { hay: true, n: rects.length, antes,
               activo: g.doblesActivo, estado: g.rules.state,
               msgOk: typeof g.rules.message === 'string' &&
                      g.rules.message.length > 0 };
    }""")
    CHK(clk.get('hay'), '2 · el botón DOBLES existe en AJUSTES › JUEGO (%d rects)' % clk.get('n', 0))
    CHK(clk.get('activo') is True, '2 · menuClick(dobles) arma el modo')
    CHK(clk.get('estado') in ('serve', 'rally', 'point'),
        '2 · el partido de dobles ARRANCA (estado %s)' % clk.get('estado'))

    pg.evaluate(RELOJ)
    pasos_hasta(pg, "window.__PP_GAME.partnerPaddleMesh.visible && window.__PP_GAME.riv2PaddleMesh.visible")
    CHK(True, '2 · las dos palas extra VIVEN en la cancha (visibles con el modo on)')

    # ── 3 · configuración IA ─────────────────────────────────────────────
    cfg = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const r1 = g.ai.cfg, r2 = g.aiRiv2.cfg, comp = g.aiComp.cfg;
      return {
        misma: Math.abs(r1.maxSpeed - r2.maxSpeed) < 1e-9 &&
               Math.abs(r1.missBase - r2.missBase) < 1e-9 &&
               Math.abs(r1.errStd - r2.errStd) < 1e-9,
        compEasy: comp.maxSpeed < r1.maxSpeed && comp.missBase >= r1.missBase,
      };
    }""")
    CHK(cfg.get('misma'), '3 · rival 2 con la MISMA cfg efectiva que el rival 1')
    CHK(cfg.get('compEasy'), '3 · compañero anclado a easy (más lento, más falón)')

    # ── 4/5/6 · rally real, rival 2 y arbitraje: ATÓMICOS (inyectar + pasos +
    # asertar dentro de un solo evaluate — sin carreras con la dinámica viva) ──
    atomico = pg.evaluate("""() => {
      const g = window.__PP_GAME, r = g.rules, b = g.ball;
      const out = {};
      const inyecta = (lado) => {
        r.state = 'rally'; r.server = 'player';
        g.aiToss = null; g.aiServeTimer = 9; g.aiServeWait = 0; g.aiStrikeT = 0;
        r.serveOwnPending = false; r.mustBounceOpp = false;
        r.validBounce = true; r.isServeBall = false;
        if (lado === 'comp') {
          r.lastHitter = 'ai';
          b.pos.set(-0.40, 1.00, -0.70);      // mitad jugador (C=-1.6)
          b.vel.set(0.05, 0.25, 0.35);
          g.aiComp.pos.set(b.pos.x - 0.06, b.pos.y, b.pos.z - 0.05);  // a 8 cm
        } else {
          r.lastHitter = 'player';
          b.pos.set(0.42, 1.00, -2.60);       // mitad CPU
          b.vel.set(-0.05, 0.25, -0.35);
          g.aiRiv2.pos.set(b.pos.x + 0.06, b.pos.y, b.pos.z + 0.05);  // a 8 cm
          g.ai.pos.set(-0.60, 1.05, -0.55);   // rival 1 LEJOS (que no gane la carrera)
        }
        if (b.__exPrev) b.__exPrev.copy(b.pos);
        b.spin.set(0, 0, 0);
        g._prevBallForAI && g._prevBallForAI.copy(b.pos);
      };
      const pasos = (n) => { for (let i = 0; i < n; i++) window.__paso(); };

      // 4 · el COMPAÑERO devuelve (bola lejos de toda pala del jugador)
      inyecta('comp');
      const c0 = g._dbStats.comp;
      pasos(12);
      out.compHit = g._dbStats.comp > c0;
      out.compVz = +b.vel.z.toFixed(2);
      out.compLast = r.lastHitter;

      // 5 · el RIVAL 2 devuelve
      inyecta('riv2');
      const r20 = g._dbStats.r2;
      pasos(12);
      out.r2Hit = g._dbStats.r2 > r20;
      out.r2Vz = +b.vel.z.toFixed(2);
      out.r2Last = r.lastHitter;

      // 6a · pala del jugador JUNTO a la bola → el compañero NO roba
      inyecta('comp');
      const pad = g.controllerPaddles[g.paddleHand];
      pad.active = true;
      pad.pos.set(b.pos.x + 0.10, b.pos.y, b.pos.z - 0.10);   // 14 cm: DENTRO
      const cA = g._dbStats.comp;
      let dMin = 9, pasosRoba = -1;
      for (let i = 0; i < 24; i++) {
        window.__paso();
        dMin = Math.min(dMin, pad.pos.distanceTo(b.pos));
        if (g._dbStats.comp > cA) { pasosRoba = i + 1; break; }   // robó: cuándo
      }
      out.padCercaRoba = g._dbStats.comp > cA;
      out.padCercaPasos = pasosRoba;
      out.padDist = +dMin.toFixed(2);

      // 6b · pala del jugador LEJOS (compañero a 8 cm) → SÍ toma
      inyecta('comp');
      pad.active = true;
      pad.pos.set(0.6, 1.0, -3.4);          // >2,7 m: FUERA de alcance
      const cB = g._dbStats.comp;
      pasos(12);
      out.padLejosToma = g._dbStats.comp > cB;

      // 6c · rival 1 a 0,35 m de la bola (no llega a golpear en 2 pasos pero
      // SÍ activa el arbitraje del rival 2) → el rival 2 NO roba
      inyecta('riv2');
      g.ai.pos.set(b.pos.x - 0.35, 1.0, b.pos.z);
      const rA = g._dbStats.r2;
      pasos(2);
      out.r1CercaRoba = g._dbStats.r2 > rA;

      // limpieza: la pala del mando vuelve a inactiva y el rival a su casa
      pad.active = false;
      g.ai.pos.set(0, 1.05, -3.0);
      return out;
    }""")
    CHK(atomico.get('compHit'), '4 · el COMPAÑERO devolvió la bola (12 pasos)')
    CHK(atomico.get('compVz', 0) < 0, '4 · la bola sale HACIA el campo rival (vz=%.2f)' % atomico.get('compVz', 0))
    CHK(atomico.get('compLast') == 'player', '4 · árbitro: golpe del EQUIPO jugador (%s)' % atomico.get('compLast'))
    CHK(atomico.get('r2Hit'), '5 · el RIVAL 2 devolvió la bola (12 pasos)')
    CHK(atomico.get('r2Vz', 0) > 0, '5 · la bola sale HACIA el campo del jugador (vz=%.2f)' % atomico.get('r2Vz', 0))
    CHK(atomico.get('r2Last') == 'ai', '5 · árbitro: golpe del EQUIPO CPU (%s)' % atomico.get('r2Last'))
    CHK(not atomico.get('padCercaRoba'),
        '6 · pala del jugador CERCA (%s m): el compañero NO roba (%d pasos)' %
        (atomico.get('padDist'), atomico.get('padCercaPasos', -1)))
    CHK(atomico.get('padLejosToma'), '6 · pala del jugador LEJOS: el compañero SÍ toma')
    CHK(not atomico.get('r1CercaRoba'), '6 · rival 1 CERCA: el rival 2 NO roba')

    # ── 7 · doble golpe = falta (Rules intacta) ──────────────────────────
    dbl = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const r = g.rules;
      r.state = 'rally'; r.server = 'player';
      g.aiToss = null; g.aiServeTimer = 9; g.aiServeWait = 0;
      r.serveOwnPending = false; r.mustBounceOpp = false; r.validBounce = true;
      r.lastHitter = 'ai'; r.isServeBall = false;
      const i1 = r.registerPaddleHit('player');   // compañero: legal
      const i2 = r.registerPaddleHit('player');   // segundo toque del EQUIPO
      return { i1: i1.length, i2: i2.length ? i2[0].cause : 'nada' };
    }""")
    CHK(dbl.get('i1') == 0 and dbl.get('i2') == 'dblhit',
        '7 · segundo toque del mismo equipo = FALTA (cause %s)' % dbl.get('i2'))

    # ── 8 · anti-fugas: ▶ JUGAR limpia el dobles ─────────────────────────
    limpiar = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      // camino REAL: la tarjeta ▶ JUGAR (id 'start') de la página main
      g.menuPage = 'main'; g.menuSec = '';
      g.drawMenu();
      const idx = (g._menuRects || []).findIndex((x) => x.id === 'start');
      if (idx < 0) return { error: 'sin start' };
      g.menuClick(idx, 0);
      return { activo: g.doblesActivo, estado: g.rules.state };
    }""")
    CHK(limpiar.get('activo') is False, '8 · ▶ JUGAR limpia doblesActivo (vuelve al 1v1)')
    CHK(limpiar.get('estado') in ('serve', 'rally', 'point'), '8 · partido 1v1 normal arrancado')
    pasos_hasta(pg, "true")
    ocultas = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      return { comp: g.partnerPaddleMesh.visible, r2: g.riv2PaddleMesh.visible };
    }""")
    CHK(not ocultas.get('comp') and not ocultas.get('r2'), '8 · palas extra de nuevo OCULTAS')

    CHK(errs == [], '9 · cero pageerrors en toda la sesión (%s)' % (errs[:2] or 'limpio'))

    b.close()

srv.shutdown()
print('RESULTADO: %d OK · %d fallos' % (len(OK), len(FAIL)))
sys.exit(1 if FAIL else 0)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r120_dirigida.py — M7d · PRO TRAINING EXTENDIDO, regla del dueño:
sólo lo tocado HOY. Servidor estático de public/ + juego REAL: el juez
de la academia (judgeAiBounce) se dispara de verdad vía la costura
__test.qaJudge (patrón __test/__debug de la casa, r76/r80/r118) y el
estado S es el real del perfil (__debug.S).

1 · Arranque limpio: __test con las costuras nuevas, 11 modos,
    PLAN_POOL = 9 clásicos en orden, 0 pageerrors.
2 · DETERMINISMO de los retos (r76/r118): dailyPlan/weeklyPlan con pool
    congelado — el modo de hoy y de la septana coincide con una
    implementación INDEPENDIENTE del FNV-1a en python y los 400 días
    sondeados JAMÁS devuelven un ejercicio nuevo.
3 · MEDALLAS (derivadas, retroactivas): bronce/plata/oro por
    estrellas+precisión en modos de habilidad y por MARCA en los de
    rally; or5 (MEDALLERO DE ORO) con 5 oros; all9 anclado al circuito
    clásico.
4 · JUEZ REAL t1c ESQUINA EXACTA: esquina legal suma, centro-fondo
    falla, corto falla; 3 esquinas seguidas = meta con bonus, 3
    estrellas, precisión 100 y MEDALLA DE ORO viva.
5 · JUEZ REAL t5b METRÓNOMO LOCO: hito 20 (bonus 15), hito 40 (bonus
    25), rally 50 otorga m50 RE-ANCLADO (el camino vivo del juez), hito
    80 (bonus 50) con 3 estrellas y medalla de ORO por marca.
6 · MENÚ REAL: el área DIRECCIÓN pinta 3 tarjetas (t1a/t1b/t1c) y RITMO
    2 (t5a/t5b) por menuClick del camino de la casa; drawMenu con
    medallero no lanza excepciones.
7 · Anti-fugas: qaOff deja el entrenamiento dormido (activo null).

Uso: python3 scripts/qa_r120_dirigida.py
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
PORT = 8862
OK = []
FAIL = []


def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)


def fnv1a(s):
    """FNV-1a 32 bits — implementación INDEPENDIENTE que replica el
    comportamiento EXACTO del seedOf del juego en JS: XOR con ToInt32
    (con signo), multiplicación en float64 (redondeo IEEE del producto,
    pierde bits bajos > 2^53) y >>> 0 (trunca hacia 0, mod 2^32)."""
    def to_int32(x):
        x &= 0xFFFFFFFF
        return x - 0x100000000 if x >= 0x80000000 else x
    h = 0x811c9dc5
    for ch in s:
        h = to_int32(h ^ ord(ch))
        prod = float(h * 0x01000193)          # float64 como JS
        h = int(prod) & 0xFFFFFFFF            # >>> 0
    return h


POOL = ['t1a', 't1b', 't2a', 't2b', 't3a', 't3b', 't4a', 't4b', 't5a']

print('== QA r120 · M7d PRO TRAINING extendido ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 320, 'height': 240})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    # la portada se RECARGA sola (service worker/PWA): espera activa a las
    # costuras de la academia en el contexto FINAL (hasta 20 s)
    boot = pg.evaluate("""async () => {
      for (let i = 0; i < 200; i++) {
        const T = window.__PP_TRAIN;
        if (T && T.__test && T.__test.medallaDe && T.__test.qaJudge &&
            T.__debug && T.__debug.MODES && window.__PP_GAME) return i;
        await new Promise((r) => setTimeout(r, 100));
      }
      return -1;
    }""")
    CHK(boot >= 0, '0 · arranque: __test/__debug + __PP_GAME vivos en %.1f s' % (0.1 * max(boot, 0)))
    pg.mouse.click(160, 120)
    pg.wait_for_timeout(800)

    # ── 1 · registro de modos + pool congelado ───────────────────────────
    a = pg.evaluate("""() => {
      const D = window.__PP_TRAIN.__debug;
      const ids = Object.keys(D.MODES);
      return {
        n11: ids.length === 11,
        hay1c: !!D.MODES.t1c && D.MODES.t1c.area === 'dir',
        hay5b: !!D.MODES.t5b && D.MODES.t5b.area === 'rit',
        pool: JSON.stringify(D.PLAN_POOL),
        dims: !!window.__PP_TRAIN.__test.trainDims(),
      };
    }""")
    CHK(a.get('n11'), '1 · 11 ejercicios registrados (9 + t1c + t5b)')
    CHK(a.get('hay1c') and a.get('hay5b'), '1 · t1c en DIRECCIÓN y t5b en RITMO')
    CHK(a.get('pool') == '["t1a","t1b","t2a","t2b","t3a","t3b","t4a","t4b","t5a"]',
        '1 · PLAN_POOL = 9 clásicos CONGELADO en orden (byte-idéntico a 3.6.108)')
    CHK(a.get('dims'), '1 · trainDims() vivo (HW/HL/C/TOP para el juez)')

    # ── 2 · determinismo de los retos ────────────────────────────────────
    det = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, D = window.__PP_TRAIN.__debug;
      const p = (n) => (n < 10 ? '0' : '') + n;
      const hoy = (() => { const d = new Date();
        return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()); })();
      const lunes = (() => { const d = new Date(); d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
        return d.getFullYear() + '-W' + p(d.getMonth() + 1) + p(d.getDate()); })();
      let fuera = 0;
      for (let i = 0; i < 400; i++) {
        const d = new Date(2026, 0, 1 + i);
        const k = d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
        if (!D.PLAN_POOL.includes(T.dailyPlan(k).mode)) fuera++;
      }
      return { hoy, lunes, mHoy: T.dailyPlan(hoy).mode, nHoy: T.dailyPlan(hoy).n,
               mSem: T.weeklyPlan(lunes).mode, nSem: T.weeklyPlan(lunes).n, fuera };
    }""")
    esperado_dia = POOL[fnv1a('ppx-' + det['hoy']) % 9]
    esperado_sem = POOL[fnv1a('ppx-semana-' + det['lunes']) % 9]
    CHK(det.get('mHoy') == esperado_dia,
        '2 · reto del día = FNV independiente (%s = %s)' % (det.get('mHoy'), esperado_dia))
    CHK(det.get('mSem') == esperado_sem,
        '2 · reto de la semana = FNV independiente (%s = %s)' % (det.get('mSem'), esperado_sem))
    CHK(det.get('fuera') == 0, '2 · 400 días sondeados: JAMÁS un ejercicio nuevo en los retos')
    CHK(det.get('nHoy', 0) > 0 and det.get('nSem', 0) > 0, '2 · objetivos del reto vivos (%s/%s)' % (det.get('nHoy'), det.get('nSem')))

    # ── 3 · medallas derivadas (retroactivas) + or5 + all9 ──────────────
    med = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, S = window.__PP_TRAIN.__debug.S;
      const set = (id, stars, acc) => {
        if (stars == null) delete S.stars[id]; else S.stars[id] = stars;
        if (acc == null) delete S.acc[id]; else S.acc[id] = acc;
      };
      for (const id of Object.keys(window.__PP_TRAIN.__debug.MODES)) set(id, null, null);
      const out = {};
      out.cero = T.medallaDe('t1a');
      set('t1a', 1, null); out.bronce = T.medallaDe('t1a');
      set('t1a', 2, 70); out.plata = T.medallaDe('t1a');
      set('t1a', 3, 60); out.plataSin = T.medallaDe('t1a');
      set('t1a', 3, 85); out.oro = T.medallaDe('t1a');
      return out;
    }""")
    CHK(med.get('cero') == 0, '3 · sin datos = sin medalla')
    CHK(med.get('bronce') == 1, '3 · 1 estrella = 🥉 BRONCE (retroactivo)')
    CHK(med.get('plata') == 2, '3 · 2 estrellas + 70 % = 🥈 PLATA')
    CHK(med.get('plataSin') == 2, '3 · 3 estrellas sin precisión = PLATA (el oro se gana)')
    CHK(med.get('oro') == 3, '3 · 3 estrellas + 85 % = 🥇 ORO')

    marca = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, S = window.__PP_TRAIN.__debug.S;
      S.best = S.best || {};
      const antes = T.medallaDe('t5b');
      S.best.t5b = 20; const bronce = T.medallaDe('t5b');
      S.best.t5b = 40; const plata = T.medallaDe('t5b');
      S.best.t5b = 80; const oro = T.medallaDe('t5b');
      S.best.t5b = 79; const casi = T.medallaDe('t5b');
      delete S.best.t5b;
      return { antes, bronce, plata, oro, casi };
    }""")
    CHK(marca.get('antes') == 0 and marca.get('bronce') == 1,
        '3 · rally: marca 20 = 🥉 (los hitos SON la meta)')
    CHK(marca.get('plata') == 2 and marca.get('oro') == 3,
        '3 · rally: marca 40 = 🥈 · marca 80 = 🥇')
    CHK(marca.get('casi') == 2, '3 · rally: marca 79 se queda en 🥈 (frontera honesta)')

    ach = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, D = window.__PP_TRAIN.__debug, S = D.S;
      for (const id of Object.keys(D.MODES)) {
        delete S.stars[id]; delete S.acc[id];
      }
      S.ach = {}; S.best = S.best || {};
      // circuito clásico al 1: all9 SÍ, or5 NO
      for (const id of D.PLAN_POOL) S.stars[id] = 1;
      T.checkGlobalAch();
      const all9SinOros = !!S.ach.all9 && !S.ach.or5;
      // 5 oros: 4 por precisión + t5a por MARCA (100)
      S.stars.t1a = 3; S.acc.t1a = 90; S.stars.t1b = 3; S.acc.t1b = 90;
      S.stars.t2a = 3; S.acc.t2a = 90; S.stars.t3a = 3; S.acc.t3a = 90;
      delete S.stars.t5a; S.best.t5a = 100;
      T.checkGlobalAch();
      return { all9SinOros, or5: !!S.ach.or5, all9Vivo: !!S.ach.all9 };
    }""")
    CHK(ach.get('all9SinOros'), '3 · all9 anclado al CIRCUITO CLÁSICO (9 estrellas bastan)')
    CHK(ach.get('or5'), '3 · 5 medallas de ORO (4 + t5a por marca) = logro MEDALLERO DE ORO')
    CHK(ach.get('all9Vivo'), '3 · all9 sigue vivo con los oros puestos')

    # limpieza del estado de logros para las pruebas de juez
    pg.evaluate("""() => {
      const D = window.__PP_TRAIN.__debug;
      for (const id of Object.keys(D.MODES)) { delete D.S.stars[id]; delete D.S.acc[id]; }
      D.S.ach = {}; D.S.pts = 0; D.S.best = {};
    }""")

    # ── 4 · juez REAL t1c ESQUINA EXACTA ─────────────────────────────────
    j1c = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, D = T.trainDims();
      const esquina = { x: -(D.HW - 0.05), y: D.TOP, z: D.C - D.HL + 0.30 };
      const centroFondo = { x: 0, y: D.TOP, z: D.C - D.HL + 0.30 };
      const corto = { x: -(D.HW - 0.05), y: D.TOP, z: D.C - 0.30 };
      const r = {};
      // meta completa PRIMERO (ronda limpia): 3 esquinas seguidas
      const d1 = T.qaJudge('t1c', esquina);
      T.qaJudge('t1c', esquina);
      const d3 = T.qaJudge('t1c', esquina);
      r.pts1 = d1.delta; r.streak1 = d1.streak;
      r.metaDelta = d3.delta;                    // 3 pts + bonus 25 = 28
      const S = window.__PP_TRAIN.__debug.S;
      r.stars = S.stars.t1c; r.acc = S.acc.t1c; r.best = S.best.t1c;
      r.medalla = T.medallaDe('t1c');
      r.p1 = !!S.ach.p1;
      // fallos: centro-fondo (banda no) y corto (fondo no)
      const f1 = T.qaJudge('t1c', centroFondo);
      const f2 = T.qaJudge('t1c', corto);
      r.fallo1 = f1.streak === 0 && f1.delta === 0;
      r.fallo2 = f2.streak === 0 && f2.delta === 0;
      T.qaOff();
      return r;
    }""")
    CHK(j1c.get('pts1') == 3 and j1c.get('streak1') == 1, '4 · t1c esquina legal: +3 pts y racha 1')
    CHK(j1c.get('metaDelta') == 28, '4 · t1c META 3 esquinas: +3 y bonus 25 (= 28)')
    CHK(j1c.get('stars') == 3 and j1c.get('acc') == 100, '4 · t1c ronda limpia: 3 estrellas · 100 %')
    CHK(j1c.get('medalla') == 3, '4 · t1c MEDALLA DE ORO viva (derivada de lo grabado)')
    CHK(j1c.get('p1'), '4 · logro PERFECTO concedido por el camino real')
    CHK(j1c.get('fallo1') and j1c.get('fallo2'), '4 · t1c centro-fondo y corto FALLAN (racha 0, 0 pts)')

    # ── 5 · juez REAL t5b METRÓNOMO LOCO + m50 re-anclado ────────────────
    j5b = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test, D = T.trainDims();
      const bote = { x: 0.2, y: D.TOP, z: D.C - 0.9 };
      const r = {};
      const h20 = T.qaJudge('t5b', bote, null, null, 19);   // rally 19 → 20
      r.h20 = { delta: h20.delta, rally: h20.rally };
      const h40 = T.qaJudge('t5b', bote, null, null, 39);   // rally 39 → 40
      r.h40 = { delta: h40.delta, rally: h40.rally };
      const r50 = T.qaJudge('t5b', bote, null, null, 49);   // rally 49 → 50: SIN hito, CON m50
      r.r50 = { delta: r50.delta, rally: r50.rally };
      const h80 = T.qaJudge('t5b', bote, null, null, 79);   // rally 79 → 80: hito mayor
      r.h80 = { delta: h80.delta, rally: h80.rally };
      const S = window.__PP_TRAIN.__debug.S;
      r.stars = S.stars.t5b; r.best = S.best.t5b;
      r.medalla = T.medallaDe('t5b');
      r.m50 = !!S.ach.m50; r.m100 = !!S.ach.m100;
      T.qaOff();
      return r;
    }""")
    CHK(j5b.get('h20', {}).get('delta') == 16 and j5b.get('h20', {}).get('rally') == 20,
        '5 · t5b hito 20: +1 y bonus 15 (= 16), rally vivo')
    CHK(j5b.get('h40', {}).get('delta') == 26, '5 · t5b hito 40: +1 y bonus 25 (= 26)')
    CHK(j5b.get('r50', {}).get('delta') == 1 and j5b.get('m50'),
        '5 · rally 50 SIN hito t5b pero CON logro m50 RE-ANCLADO (camino vivo)')
    CHK(j5b.get('h80', {}).get('delta') == 51, '5 · t5b hito 80: +1 y bonus 50 (= 51)')
    CHK(j5b.get('stars') == 3, '5 · t5b estrellas 1/2/3 en los hitos (20/40/80)')
    CHK(j5b.get('best') == 80 and j5b.get('medalla') == 3, '5 · t5b marca 80 grabada y MEDALLA DE ORO por marca')
    CHK(not j5b.get('m100'), '5 · m100 exige 100 (aún no)')

    # ── 6 · menú REAL: tarjetas nuevas visibles por camino de la casa ────
    menu = pg.evaluate("""() => {
      const g = window.__PP_GAME, out = {};
      g.menuPage = 'train'; g.menuSec = '';
      g.drawMenu();
      const rects = g._menuRects || [];
      const iDir = rects.findIndex((x) => x.id === 'trv3:area:dir');
      if (iDir < 0) return { error: 'sin area dir' };
      g.menuClick(iDir, 0);
      const r2 = g._menuRects || [];
      out.dirIds = r2.map((x) => x.id).filter((x) => x && x.indexOf('trv3:start:') === 0);
      // pintar con estado con medallas no debe lanzar
      let pintura = 'ok';
      try { g.drawMenu(); } catch (e) { pintura = String(e); }
      out.pintura = pintura;
      // RITMO
      const iBack = r2.findIndex((x) => x.id === 'trv3:back');
      g.menuClick(iBack, 0);
      const r3 = g._menuRects || [];
      const iRit = r3.findIndex((x) => x.id === 'trv3:area:rit');
      g.menuClick(iRit, 0);
      const r4 = g._menuRects || [];
      out.ritIds = r4.map((x) => x.id).filter((x) => x && x.indexOf('trv3:start:') === 0);
      g.menuClick(r4.findIndex((x) => x.id === 'trv3:back'), 0);
      return out;
    }""")
    CHK('trv3:start:t1c' in (menu.get('dirIds') or []) and len(menu.get('dirIds') or []) == 3,
        '6 · DIRECCIÓN pinta 3 tarjetas: t1a, t1b y t1c NUEVA (%s)' % (menu.get('dirIds') or []))
    CHK('trv3:start:t5b' in (menu.get('ritIds') or []) and len(menu.get('ritIds') or []) == 2,
        '6 · RITMO pinta 2 tarjetas: t5a y t5b NUEVA (%s)' % (menu.get('ritIds') or []))
    CHK(menu.get('pintura') == 'ok', '6 · drawMenu de área con medallero pinta SIN excepciones')
    hub = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.menuPage = 'train'; g.menuSec = '';
      let pintura = 'ok';
      try { g.drawMenu(); } catch (e) { pintura = String(e); }
      return pintura;
    }""")
    CHK(hub == 'ok', '6 · HUB con medallero por área pinta SIN excepciones')

    # ── 7 · anti-fugas ───────────────────────────────────────────────────
    off = pg.evaluate("""() => {
      const T = window.__PP_TRAIN.__test;
      T.qaOff();
      return { activo: T.activo() };
    }""")
    CHK(off.get('activo') is None, '7 · qaOff: el entrenamiento queda DORMIDO (activo null)')

    CHK(errs == [], '8 · cero pageerrors en toda la sesión (%s)' % (errs[:2] or 'limpio'))

    b.close()

srv.shutdown()
print('RESULTADO: %d OK · %d fallos' % (len(OK), len(FAIL)))
sys.exit(1 if FAIL else 0)

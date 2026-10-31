#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r101_v3693.py — capa de QA de la ronda 101 (V3.6.93-SDK6).

El dueño devolvió la r100 con tres defectos:
 1) «en el Entrenamiento es mucho más difícil sacar, el gatillo no lanza la
    bola automáticamente, se traba» — el hook del gatillo de las flechas se
    COMÍA el gesto (la bola del tee no salía). r101: serveTrigger EXACTO de
    V3.6.91 (el gatillo siempre lanza).
 2) «has estropeado el saque» — el velInst del lanzamiento (núcleo y tee)
    REVERTIDO: V3.6.91 byte a byte.
 3) «no has sabido resolver lo del contacto de la bola parada» — el umbral
    dual 0,95/0,65 SECUESTRABA botes suaves. r101: umbral ÚNICO 0,25 m/s:
    bota lo que llega con vida, se posa sólo lo que llega muerto.
 4) «el control para subir y bajar la barra es inútil… se pisa el gatillo» —
    AJUSTE POR PROXIMIDAD sin NINGÚN botón: la mano libre entra en el
    pasillo de la cinta (≥0,30 s) y la barra sigue su altura en pasos de
    1 cm; apartar la mano fija y guarda.
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8836
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html servido) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

AGUJAS = [
    # 1 · gatillo LIBRE (revert V3.6.91)
    ("serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } },",
     'c13: serveTrigger EXACTO de V3.6.91 (el gatillo SIEMPRE lanza el tee)'),
    # 2 · saque revertido (sin velInst en núcleo ni tee)
    ('// v3.0.9-HALL1 · subida mínima del saque asistido según dificultad',
     'c12: tossFromHand intacto tras el revert (el filtro de siempre)'),
    # 4 · ajuste por proximidad
    ('function barraUpdate(px, py, pz, dt) {', 'c13: máquina de ajuste por proximidad'),
    ('const BARRA_DWELL = 0.30;', 'c13: dwell de agarre 0,30 s'),
    ('function barraSoltar() {', 'c13: soltar = fijar + guardar'),
    ('function pistaBarra() {', 'c13: pista del rótulo por estado'),
    ('barraFijar(py - DIMS.netTopY, false);     // sigue la mano en vivo',
     'c13: la barra sigue la mano en vivo mientras dura el agarre'),
    ("toast((LANG === 'en' ? 'Bar: ' : 'Barra: ') + BARRA_CM() + ' cm', true);",
     'c13: toast de confirmación al fijar'),
    # 3 · reposo con umbral único
    ('-vRelN <= DIMS.paddleRestSpeed) {', 'c05: reposo con umbral ÚNICO'),
    ('paddleRestSpeed: 0.25,', 'c02: umbral de reposo 0,25 m/s'),
    ("events.push({ type: 'restTouch', speed: -vRelN, pos: crossPoint.clone() });",
     'c05: «toc» suave del apoyo intacto'),
    ('if (ball.__ppRestIdx >= 0) {', 'c05: transporte del apoyo intacto (r100)'),
    ("case 'restTouch':", 'c12: sonido del apoyo intacto'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# lo ANTIGUO retirado del servido
RETIRADAS = [
    ('if (barraAjustarHover()) return;', 'c13: el gatillo CONSUMIDO por las flechas RETIRADO'),
    ('function barraAjustarHover() {', 'c13: ajuste por hover RETIRADO'),
    ('function barraHazEnsure() {', 'c13: haz de selección por rayo RETIRADO'),
    ('if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);',
     'c12: velInst del saque RETIRADO (V3.6.91)'),
    ('if (bh.velInst && bh.velInst.lengthSq() > v.lengthSq()) v.copy(bh.velInst);',
     'c13: velInst del tee RETIRADO (V3.6.91)'),
    ('paddleRestSpeedPad', 'c02: umbral dual 0,95 RETIRADO'),
    ('paddleRestBounce', 'c02: constante muerta RETIRADA'),
    ('Ajusta la altura de la barra (±1 cm) enfocando sus flechas',
     'i18n: texto del gesto por gatillo RETIRADO'),
]
for aguja, nombre in RETIRADAS:
    CHK(aguja not in GH, 'game.html: ' + nombre)

# el aro del globo sigue al centro (r100-B, sin queja del dueño)
CHK('g.position.set(0, APEX_Y, C());' in GH, 'game.html: aro del globo al CENTRO (r100-B intacto)')
CHK('C() + 0.5' not in GH, 'game.html: aro a +0,50 m sigue retirado')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.93-SDK6', 'c00: VERSION sella 3.6.93-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 95, 'VERSION.json: FASE 95')
CHK(V.get('hub') == 'v3693-sdk6', 'VERSION.json: hub v3693-sdk6')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
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
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2500)

    # ---- 1 · SAQUE REVERTIDO: el filtro de V3.6.91 manda (velInst NO secuestra)
    toss = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const h = g.controllerPaddles[0];
      const D = window.__PP_CORE ? window.__PP_CORE.DIMS : g.DIMS;
      const out = {};
      // flick: la mano va a 4 m/s INSTANTÁNEOS pero el filtro va a 2 —
      // en V3.6.91 (el estado que el dueño quiere) la bola sale con el FILTRO
      h.vel.set(0, 2, 0); h.velInst.set(0, 4, 0);
      g.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.3);
      g.tossFromHand(0, false);
      out.flick = Math.round(g.ball.vel.y * 1000) / 1000;
      // gesto suave: idéntico de siempre
      h.vel.set(0, 2, 0); h.velInst.set(0, 1, 0);
      g.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.3);
      g.tossFromHand(0, false);
      out.suave = Math.round(g.ball.vel.y * 1000) / 1000;
      return out;
    }""")
    if 'err' in (toss or {}):
        CHK(False, 'saque: %s' % toss.get('err'))
    else:
        CHK(toss['flick'] == 2, 'saque: flick ⇒ filtro de V3.6.91 (2 m/s; el velInst 4 NO secuestra)')
        CHK(toss['suave'] == 2, 'saque: gesto suave ⇒ 2 m/s (idéntico)')

    # ---- 2 · REPOSO REAL: bola que llega quieta SE POSA (sin golpe, sin trompicones)
    rest = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const C = window.__PP_CORE; if (!C || !C.stepPhysics) return { err: 'sin stepPhysics' };
      const D = C.DIMS;
      const V3 = g.ball.pos.constructor;
      const out = {};
      const pad = g.controllerPaddles[0];
      pad.who = 'player'; pad.index = 0; pad.active = true;
      pad.serveFlight = false; pad.cooldown = 0;
      pad.normal.set(0, 1, 0); pad.prevNormal.copy(pad.normal);
      pad.up.set(0, 0, -1); pad.prevUp.copy(pad.up);
      pad.right.set(1, 0, 0); pad.prevRight.copy(pad.right);
      const HZ = D.tableCenterZ + 1.04;
      pad.pos.set(0.15, 1.00, HZ);
      pad.prev.copy(pad.pos);
      pad.vel.set(0, 0, 0); pad.velInst.set(0, 0, 0);
      // bola POSADA: a 0,5 mm de la cara y casi sin velocidad (v0 −0,02)
      const ball = { pos: new V3(0.15, 1.00 + D.ballRadius + 0.0005, D.tableCenterZ + 0.90),
                     vel: new V3(0, -0.02, 0), spin: new V3(0, 0, 0), dragMul: 1 };
      const evs = [];
      const dt = 1 / 72;
      for (let f = 0; f < 12; f++) C.stepPhysics(dt, ball, [pad], evs, null);
      out.apoyada = Math.abs(ball.pos.y - (1.00 + D.ballRadius)) < 0.004;
      out.quiet = ball.vel.length() < 0.08;
      out.sinGolpe = !evs.some(e => e.type === 'paddle');
      out.conToque = evs.some(e => e.type === 'restTouch');
      out.registrada = ball.__ppRestIdx === 0;
      return out;
    }""")
    if 'err' in (rest or {}):
        CHK(False, 'reposo: %s' % rest.get('err'))
    else:
        CHK(rest['apoyada'], 'reposo: la bola se POSA sobre la hoja')
        CHK(rest['quiet'], 'reposo: velocidad estable < 0,08 m/s (SIN trompicones)')
        CHK(rest['sinGolpe'], 'reposo: CERO eventos de golpe al posarse')
        CHK(rest['conToque'], 'reposo: «toc» suave (restTouch)')
        CHK(rest['registrada'], 'reposo: apoyo registrado (__ppRestIdx)')

    # ---- 3 · BOTE NATURAL (lo que la r100 secuestraba): cae a 1,2 m/s ⇒ BOTA
    #          y decae hasta posarse solo al final
    bote = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const C = window.__PP_CORE; if (!C || !C.stepPhysics) return { err: 'sin stepPhysics' };
      const D = C.DIMS;
      const V3 = g.ball.pos.constructor;
      const pad = g.controllerPaddles[0];
      pad.who = 'player'; pad.index = 0; pad.active = true;
      pad.serveFlight = false; pad.cooldown = 0;
      pad.normal.set(0, 1, 0); pad.prevNormal.copy(pad.normal);
      pad.up.set(0, 0, -1); pad.prevUp.copy(pad.up);
      pad.right.set(1, 0, 0); pad.prevRight.copy(pad.right);
      const HZ = D.tableCenterZ + 1.04;
      pad.pos.set(0.15, 1.00, HZ);
      pad.prev.copy(pad.pos);
      pad.vel.set(0, 0, 0); pad.velInst.set(0, 0, 0);
      // bola BOTANDO: llega a 1,2 m/s (un bote suave de verdad)
      const ball = { pos: new V3(0.15, 1.00 + D.ballRadius + 0.02, D.tableCenterZ + 0.90),
                     vel: new V3(0, -1.2, 0), spin: new V3(0, 0, 0), dragMul: 1 };
      const evs = [];
      const dt = 1 / 72;
      let primerBote = 0, vyTrasPrimerPaso = 0;
      for (let f = 0; f < 140; f++) {
        C.stepPhysics(dt, ball, [pad], evs, null);
        if (f === 1) vyTrasPrimerPaso = ball.vel.y;
        if (!primerBote && ball.vel.y > 0.4) primerBote = f + 1;
      }
      return { primerBote, vyTrasPrimerPaso: Math.round(vyTrasPrimerPaso * 100) / 100,
               golpes: evs.filter(e => e.type === 'paddle').length,
               apoyada: ball.__ppRestIdx === 0, quiet: ball.vel.length() < 0.12 };
    }""")
    if 'err' in (bote or {}):
        CHK(False, 'bote: %s' % bote.get('err'))
    else:
        CHK(bote['primerBote'] > 0 and bote['primerBote'] < 8,
            'bote: la bola que llega a 1,2 m/s BOTA en el primer contacto (frame %s, vy %s)' %
            (bote['primerBote'], bote['vyTrasPrimerPaso']))
        CHK(bote['golpes'] >= 2, 'bote: la serie de botes suena (%d golpes)' % bote['golpes'])
        CHK(bote['apoyada'], 'bote: al decaer se POSA sola (Eleven)')
        CHK(bote['quiet'], 'bote: reposo final estable')

    # ---- 4 · TRANSPORTE + SWING (r100 intacto)
    carry = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const C = window.__PP_CORE; if (!C || !C.stepPhysics) return { err: 'sin stepPhysics' };
      const D = C.DIMS;
      const V3 = g.ball.pos.constructor;
      const pad = g.controllerPaddles[0];
      pad.who = 'player'; pad.index = 0; pad.active = true;
      pad.serveFlight = false; pad.cooldown = 0;
      pad.normal.set(0, 1, 0); pad.prevNormal.copy(pad.normal);
      pad.up.set(0, 0, -1); pad.prevUp.copy(pad.up);
      pad.right.set(1, 0, 0); pad.prevRight.copy(pad.right);
      const HZ = D.tableCenterZ + 1.04;
      pad.pos.set(0.15, 1.00, HZ);
      pad.prev.copy(pad.pos);
      pad.vel.set(0, 0, 0); pad.velInst.set(0, 0, 0);
      const ball = { pos: new V3(0.15, 1.00 + D.ballRadius + 0.0005, D.tableCenterZ + 0.90),
                     vel: new V3(0, -0.02, 0), spin: new V3(0, 0, 0), dragMul: 1 };
      const evs = [];
      const dt = 1 / 72;
      for (let f = 0; f < 12; f++) C.stepPhysics(dt, ball, [pad], evs, null);
      // TRANSPORTE: la pala sube DESPACIO 3 cm (24 frames) — la bola viaja con ella
      evs.length = 0;
      const sube = 0.03 / 24;
      for (let f = 0; f < 24; f++) {
        pad.prev.copy(pad.pos);
        pad.pos.y += sube;
        pad.vel.set(0, sube / dt, 0);   // ~0,078 m/s < paddleRestCarry
        C.stepPhysics(dt, ball, [pad], evs, null);
      }
      const carryOk = Math.abs(ball.pos.y - (1.03 + D.ballRadius)) < 0.004;
      // SWING: la pala ACELERA — el apoyo se rompe y GOLPEA
      evs.length = 0;
      ball.vel.set(0, 0, 0);
      let golpe = false, vuela = false, despegada = false;
      for (let f = 0; f < 6; f++) {
        pad.prev.copy(pad.pos);
        pad.pos.y += 0.045;
        pad.vel.set(0, 0.045 / dt, 0);
        C.stepPhysics(dt, ball, [pad], evs, null);
        if (evs.some(e => e.type === 'paddle')) golpe = true;
        if (ball.vel.y > 0.5) vuela = true;
        if (ball.__ppRestIdx === -1) despegada = true;
      }
      return { carryOk, golpe, vuela, despegada };
    }""")
    if 'err' in (carry or {}):
        CHK(False, 'transporte: %s' % carry.get('err'))
    else:
        CHK(carry['carryOk'], 'transporte: la bola sube CON la pala despacio (3 cm, 1:1)')
        CHK(carry['golpe'], 'swing: la pala que acelera GOLPEA (evento paddle)')
        CHK(carry['vuela'], 'swing: la bola sale volando (bote recuperado)')
        CHK(carry['despegada'], 'swing: el apoyo se rompe limpio (__ppRestIdx −1)')

    # ---- 5 · BARRA POR PROXIMIDAD: agarrar, seguir, fijar, clamps, persistencia
    barra = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const D = window.__PP_CORE.DIMS;
      const T = window.__PP_TRAIN.__test;
      const net = D.netTopY, top = D.tableTopY;
      const cm = (h) => Math.round((net + h - top) * 100);
      const out = { netMenosTop: Math.round((net - top) * 1000) / 1000 };
      out.h0 = T.barraH(); out.cm0 = T.barraCm(); out.cmEsperado = cm(out.h0);
      const X = T;
      X.barraVisSet(true);                 // estado visual de la prueba t2a
      const dt = 1 / 72;
      const zCinta = window.__PP_TRAIN.__test.barraSpr().grupo;
      // mano libre DENTRO del pasillo, quieta a 24 cm sobre la red: dwell 0,30 s
      let st = null;
      for (let k = 0; k < 22; k++) st = X.barraUpdate(0, net + 0.24, zCinta, dt);
      out.agarrada = st && st.agarrada;
      out.hAgarre = T.barraH();            // la barra saltó a la mano (0,24)
      // la mano SUBE a 33 cm: la barra la sigue en vivo
      for (let k = 0; k < 6; k++) st = X.barraUpdate(0, net + 0.33, zCinta, dt);
      out.hSiguiendo = T.barraH();
      out.cmSiguiendo = T.barraCm(); out.cmSigEsperado = cm(T.barraH());
      // la mano se APARTA: fijar + guardar
      st = X.barraUpdate(0, net + 0.33, zCinta + 0.6, dt);
      out.soltada = st && !st.agarrada && !st.zona;
      out.ls = localStorage.getItem('pp_train_barra_v1');
      // ajuste directo ±1 cm y clamps (QA)
      X.barraAjustar(1); out.hMas = T.barraH();
      for (let k = 0; k < 60; k++) X.barraAjustar(-1);
      out.min = T.barraH();
      for (let k = 0; k < 60; k++) X.barraAjustar(1);
      out.max = T.barraH();
      X.barraVisSet(false);
      return out;
    }""")
    if 'err' in (barra or {}):
        CHK(False, 'barra: %s' % barra.get('err'))
    else:
        CHK(barra['cm0'] == barra['cmEsperado'],
            'barra: lectura en cm sobre la SUPERFICIE (%d cm = red %s + barra %s)' %
            (barra['cm0'], barra['netMenosTop'], barra['h0']))
        CHK(barra['agarrada'] is True, 'barra: la mano libre en el pasillo (0,31 s) AGARRA la barra')
        CHK(abs(barra['hAgarre'] - 0.24) < 1e-9, 'barra: al agarrar salta a la altura de la mano (0,24)')
        CHK(abs(barra['hSiguiendo'] - 0.33) < 1e-9, 'barra: sigue la mano en vivo (0,24 → 0,33)')
        CHK(barra['cmSiguiendo'] == barra['cmSigEsperado'], 'barra: rótulo con los cm vivos')
        CHK(barra['soltada'] is True, 'barra: apartar la mano FIJA la altura')
        CHK('{"h":0.33}' in (barra['ls'] or ''), 'barra: persistencia escrita limpia (%s)' % barra['ls'])
        CHK(abs(barra['hMas'] - 0.34) < 1e-9, 'barra: ajuste directo +1 cm (0,33 → 0,34)')
        CHK(barra['min'] == 0.05, 'barra: clamp INFERIOR a 5 cm')
        CHK(barra['max'] == 0.40, 'barra: clamp SUPERIOR a 40 cm')

    # ---- 6 · el gatillo del módulo NO toca la barra (libre para el tee)
    trig = pg.evaluate("""() => {
      const T = window.__PP_TRAIN;
      return { src: String(T.serveTrigger), toca: String(T.serveTrigger).indexOf('barra') >= 0 };
    }""")
    CHK(not trig['toca'], 'gatillo: serveTrigger NO menciona la barra (lanza SIEMPRE)')

    # ---- 7 · escena: mandos pegados a la cinta (rótulo centro, flechas flanco)
    esc = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const T = window.__PP_TRAIN;
      try { T.tick(0.016); } catch (e) { return { err: 'tick: ' + (e && e.message) }; }
      const X = T.__test;
      const D = window.__PP_CORE.DIMS;
      return { spr: X.barraSpr(), zCentro: Math.round((D.tableCenterZ) * 1000) / 1000 };
    }""")
    if 'err' in (esc or {}):
        CHK(False, 'escena: %s' % esc.get('err'))
    else:
        s = esc['spr']
        if not s or not s.get('up'):
            CHK(False, 'escena: los mandos de la barra NO existen tras el buildScene')
        else:
            CHK(abs(s['lbl']['x']) < 1e-6, 'escena: rótulo al CENTRO de la cinta (x=0)')
            CHK(abs(s['up']['x'] + 0.24) < 1e-6 and abs(s['dn']['x'] - 0.24) < 1e-6,
                'escena: flechas flanqueando el rótulo (±0,24 m)')
            CHK(abs(s['up']['y'] - s['lbl']['y']) < 1e-6 and abs(s['dn']['y'] - s['lbl']['y']) < 1e-6,
                'escena: todo el conjunto a la MISMA altura (viaja con la cinta)')
            CHK(s['cinta'] is not None and abs(s['cinta']['band'] - (s['lbl']['y'] - 0.13)) < 1e-6,
                'escena: la cinta vive 13 cm por debajo del rótulo')
            CHK(abs(s['grupo'] - esc['zCentro']) < 1e-6,
                'escena: conjunto sobre el centro de la mesa (z=%s)' % s['grupo'])

    # ---- 8 · sin errores de página
    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))

    b.close()
srv.shutdown()

print()
print('QA r101 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)

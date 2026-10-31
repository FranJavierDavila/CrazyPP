#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r100_v3692.py — capa de QA de la ronda 100 (V3.6.92-SDK6).
Cuatro peticiones del dueño tras V3.6.91:
 1) BARRA INTERACTIVA DEL PASE BAJO (Pro Training · t2a): «que pudiésemos
    modificar la altura de dicha barra de manera interactiva durante el
    entrenamiento… pulsando unos iconos que se encuentran a la altura de la
    barra con forma de flecha hacia arriba y otra flecha hacia abajo con la
    medida de la altura de la barra sobre la superficie de la mesa… ajustar
    en rangos de 1 cm… enfocando con la mano que no tiene pala hacia esos
    iconos sale un haz de selección».
 2) ARO DEL GLOBO DEFENSIVO (t2b): la representación (toro + haz) es
    correcta pero vivía a +0,50 m hacia el rival — pasa al CENTRO de la mesa.
 3) PRIMER SAQUE RESTRINGIDO: «a veces el primer saque no me permite lanzar
    la pelota al aire con la mano libre hasta donde quiera» — el filtro de
    media móvil llegaba detrás del pico del flick; ahora la velocidad
    INSTANTÁNEA del mando manda cuando es mayor (velocidad real de la mano).
 4) FÍSICA BOLA-PALA (el estándar Eleven, SIN tocar la física de golpes):
    «si paramos la bola sobre la pala va a trompicones… y si levanto la pala
    la bola la atraviesa y desaparece» — contacto de reposo (proyección sin
    rebote + fricción + rodadura) y transporte por frame de la bola apoyada;
    el swing real sigue siendo GOLPE puro (golden de física intacto).
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
CORE = os.path.join(RAIZ, 'src/game/core')
PORT = 8833
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (fuente + servido) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
C02 = open(os.path.join(CORE, 'c02_cfg_escena.js'), encoding='utf-8').read()
C05 = open(os.path.join(CORE, 'c05_colisiones_ia_golpeo.js'), encoding='utf-8').read()
C12 = open(os.path.join(CORE, 'c12_pingponggame.js'), encoding='utf-8').read()
C13 = open(os.path.join(CORE, 'c13_ui_arranque.js'), encoding='utf-8').read()

AGUJAS = [
    # (1) barra interactiva del pase bajo
    ('r100 · BARRA INTERACTIVA DEL PASE BAJO', 'c13: cabecera del ajuste (r100)'),
    ("let barraH = 0.17;", 'c13: altura viva de la barra (17 cm de siempre)'),
    ("localStorage.getItem('pp_train_barra_v1'", 'c13: persistencia LEÍDA al arrancar'),
    ("localStorage.setItem('pp_train_barra_v1', JSON.stringify({ h: Math.round(barraH * 1000) / 1000 }))",
     'c13: persistencia ESCRITA (limpia, sin ruido float) en cada ajuste'),
    ('const RIBBON_Y = () => DIMS.netTopY + barraH;         // cinta AJUSTABLE (r100)',
     'c13: la cinta usa la altura viva (era +0.17 fijo)'),
    ('const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);',
     'c13: lectura en cm SOBRE LA SUPERFICIE de la mesa'),
    ('const BARRA_MIN = 0.05, BARRA_MAX = 0.40;',
     'c13: clamps 5..40 cm'),
    ('function barraChevronTex(dir) {', 'c13: flechas ↑/↓ dibujadas (canvas)'),
    ('function barraLabelTex() {', 'c13: rótulo de cm (canvas)'),
    ('function barraLay() {', 'c13: recolocación viva de cinta + mandos'),
    ('barraUp = mkBoton(1);', 'c13: flecha ARRIBA creada'),
    ('barraDn = mkBoton(-1);', 'c13: flecha ABAJO creada'),
    ('const BARRA_X = 1.05;', 'c13: mandos fuera del extremo de la cinta'),
    ('function barraHazEnsure() {', 'c13: haz de selección perezoso'),
    ('function barraTick(dt) {', 'c13: tick del rayo de la mano libre'),
    ('if (_bRay.ray.distanceToPoint(_bW) <= 0.075) { hit = k; break; }',
     'c13: hover MATEMÁTICO del rayo (radio 7,5 cm)'),
    ("try { G.haptic(h, 0.14, 20); } catch (eHH) { /* */ }",
     'c13: háptica de hover en el cambio'),
    ('function barraAjustarHover() {', 'c13: ajuste ±1 cm con el gatillo'),
    ('barraH + (barraHover === 0 ? 0.01 : -0.01), BARRA_MIN, BARRA_MAX);',
     'c13: paso de 1 cm con clamp'),
    ('if (barraAjustarHover()) return;', 'c13: el gatillo sobre una flecha SE CONSUME'),
    ('barraTick(dt);', 'c13: barraTick vivo en el tick del módulo'),
    ("x.fillText(String(BARRA_CM()) + ' cm', 160, 44);",
     'c13: el rótulo pinta los cm vivos'),
    ("x.fillText(LANG === 'en' ? 'BAR HEIGHT' : 'ALTURA BARRA', 160, 86);",
     'c13: rótulo i18n ES/EN'),
    ('m_t2a_d: \'Golpea drives profundos pasando ENTRE la red y la cinta naranja. Ajusta la altura de la barra',
     'c13 ES: descripción del modo con la barra ajustable'),
    ('m_t2a_d: \'Hit deep drives passing BETWEEN the net and the orange ribbon. Adjust the bar height',
     'c13 EN: descripción del modo con la barra ajustable'),
    ('barraH: () => barraH,', 'c13: internos de la barra expuestos para la QA'),
    # (2) aro del globo al centro
    ('r100 · ARO EN EL CENTRO DE LA MESA', 'c13: cabecera del aro (r100)'),
    ('g.position.set(0, APEX_Y, C());', 'c13: aro sobre el CENTRO de la mesa'),
    # (3) primer saque: lanzamiento fiel
    ('r100 · LANZAMIENTO FIEL AL GESTO', 'c12: cabecera del fix del flick'),
    ('if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);',
     'c12: la velocidad INSTANTÁNEA manda si es mayor'),
    ('r100 · lanzamiento FIEL al gesto (mismo fix que el núcleo)',
     'c13: el tee del Pro Training usa el mismo criterio'),
    ('if (bh.velInst && bh.velInst.lengthSq() > v.lengthSq()) v.copy(bh.velInst);',
     'c13: velInst manda en serveTossFromTee'),
    # (4) contacto de reposo + transporte
    ('r100 · CONTACTO DE REPOSO pala-bola (el estándar Eleven).',
     'c05: cabecera del contacto de reposo'),
    ('paddleRestSpeed: 0.65,', 'c02: umbral de apoyo (no golpe) con pala viva'),
    ('paddleRestSpeedPad: 0.95,', 'c02: umbral aplicado con pala lenta (posar la bola)'),
    ('paddleRestFric: 0.38,', 'c02: fricción tangencial del apoyo'),
    ('paddleRestMuS: 0.35,', 'c02: fricción estática (pala plana = bola quieta)'),
    ('paddleRestDrop: 0.09,', 'c02: edad del apoyo sin re-confirmar'),
    ('paddleRestCarry: 0.5,', 'c02: velocidad máx de arrastre'),
    ("pad.who === 'player' && !pad.serveFlight && !onHandle &&",
     'c05: reposo SOLO en la cara del jugador (nunca saque ni canto)'),
    ('Math.abs(lhz) >= hT &&',
     'c05: cara únicamente (el canto nunca posa)'),
    ('-vRelN <= (pad.vel.lengthSq() <= DIMS.paddleRestCarry * DIMS.paddleRestCarry',
     'c05: llegada MUY lenta = APOYO (umbral dual según la pala)'),
    ('ball.__ppRestIdx = pad.index;', 'c05: registro del apoyo en la bola'),
    ("events.push({ type: 'restTouch', speed: -vRelN, pos: crossPoint.clone() });",
     'c05: evento «toc» del apoyo (sólo contacto nuevo)'),
    ('r100 · TRANSPORTE DEL APOYO', 'c05: transporte por frame en stepPhysics'),
    ("for (const p of paddles) if (p && p.index === ball.__ppRestIdx) { rp = p; break; }",
     'c05: la pala del apoyo se busca por index'),
    ('rp.vel.lengthSq() > DIMS.paddleRestCarry * DIMS.paddleRestCarry) {',
     'c05: pala rápida ⇒ despegue (el swing golpea, no arrastra)'),
    ('const quieta = (sx * sx + sy * sy) < 1e-6 &&',
     'c05: fricción estática (pala plana: la bola NO rueda)'),
    ('ball.__ppRestIdx = -1;                     // rodó fuera del borde',
     'c05: la bola que rueda fuera del disco se suelta'),
    ('r100 · un GOLPE rompe cualquier apoyo previo',
     'c05: el golpe limpia el apoyo (el transporte jamás persigue la bola)'),
    ("case 'restTouch':", 'c12: «toc» suave del apoyo (audio + háptica)'),
    ('r100 · la bola SE POSA sobre la pala (contacto de reposo c05)',
     'c12: comentario del caso restTouch'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# lo ANTIGUO retirado del servido
CHK('const RIBBON_Y = () => DIMS.netTopY + 0.17;' not in GH,
    'game.html: cinta fija a 17 cm RETIRADA (ahora ajustable)')
CHK('C() + 0.5' not in GH, 'game.html: aro a +0,50 m RETIRADO (ahora centro)')
CHK('DIMS.paddleRestSpeed' in GH, 'game.html: la física ve el umbral del reposo')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.92-SDK6', 'c00: VERSION sella 3.6.92-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 94, 'VERSION.json: FASE 94')
CHK(V.get('hub') == 'v3692-sdk6', 'VERSION.json: hub v3692-sdk6')

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

    # ---- 1 · PRIMER SAQUE: la velocidad INSTANTÁNEA manda si es mayor
    toss = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const h = g.controllerPaddles[0];
      const D = window.__PP_CORE ? window.__PP_CORE.DIMS : g.DIMS;
      const out = {};
      // flick: el filtro va detrás (2 m/s) y la mano va a 4 m/s → manda velInst
      h.vel.set(0, 2, 0); h.velInst.set(0, 4, 0);
      g.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.3);
      g.tossFromHand(0, false);
      out.flick = Math.round(g.ball.vel.y * 1000) / 1000;
      // gesto suave: velInst menor → la filtrada (comportamiento de siempre)
      h.vel.set(0, 2, 0); h.velInst.set(0, 1, 0);
      g.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.3);
      g.tossFromHand(0, false);
      out.suave = Math.round(g.ball.vel.y * 1000) / 1000;
      return out;
    }""")
    if 'err' in (toss or {}):
        CHK(False, 'saque: %s' % toss.get('err'))
    else:
        CHK(toss['flick'] == 4, 'saque: flick ⇒ sale con la velocidad REAL de la mano (4 m/s, era 2)')
        CHK(toss['suave'] == 2, 'saque: gesto suave ⇒ filtro de siempre (2 m/s) intacto')

    # ---- 2 · CONTACTO DE REPOSO + TRANSPORTE + GOLPE (física real c05)
    rest = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const C = window.__PP_CORE; if (!C || !C.stepPhysics) return { err: 'sin stepPhysics' };
      const D = C.DIMS;
      const V3 = g.ball.pos.constructor;
      const out = {};
      // pala del jugador PLANA (normal +Y, up hacia −Z mundo), quieta,
      // hoja plana a 1,00 m — el centro de hoja C1 = pad.pos + up·0,14
      const pad = g.controllerPaddles[0];
      pad.who = 'player'; pad.index = 0; pad.active = true;
      pad.serveFlight = false; pad.cooldown = 0;
      pad.normal.set(0, 1, 0); pad.prevNormal.copy(pad.normal);
      pad.up.set(0, 0, -1); pad.prevUp.copy(pad.up);
      pad.right.set(1, 0, 0); pad.prevRight.copy(pad.right);
      const HZ = D.tableCenterZ + 1.04;        // agarre: la hoja cae en C+0,90
      pad.pos.set(0.15, 1.00, HZ);
      pad.prev.copy(pad.pos);
      pad.vel.set(0, 0, 0); pad.velInst.set(0, 0, 0);
      // bola cayendo MUY despacio SOBRE EL CENTRO de la hoja (y=1,00)
      const ball = { pos: new V3(0.15, 1.00 + D.ballRadius + 0.02, D.tableCenterZ + 0.90),
                     vel: new V3(0, -0.35, 0), spin: new V3(0, 0, 0), dragMul: 1 };
      const evs = [];
      const dt = 1 / 72;
      // 12 frames: la bola llega lenta y SE POSA (sin rebote, sin golpe)
      for (let f = 0; f < 12; f++) C.stepPhysics(dt, ball, [pad], evs, null);
      out.apoyada = Math.abs(ball.pos.y - (1.00 + D.ballRadius)) < 0.004;
      out.quiet = ball.vel.length() < 0.08;
      out.sinGolpe = !evs.some(e => e.type === 'paddle');
      out.conToque = evs.some(e => e.type === 'restTouch');
      out.registrada = ball.__ppRestIdx === 0;
      // TRANSPORTE: la pala sube DESPACIO 3 cm (24 frames) — la bola viaja con ella
      evs.length = 0;
      const sube = 0.03 / 24;
      for (let f = 0; f < 24; f++) {
        pad.prev.copy(pad.pos);
        pad.pos.y += sube;
        pad.vel.set(0, sube / dt, 0);   // ~0,078 m/s < paddleRestCarry
        C.stepPhysics(dt, ball, [pad], evs, null);
      }
      out.carryY = Math.round(ball.pos.y * 1000) / 1000;
      out.carryOk = Math.abs(ball.pos.y - (1.03 + D.ballRadius)) < 0.004;
      // GOLPE: la pala ACELERA hacia la bola (swing real) — el apoyo se rompe
      evs.length = 0;
      ball.vel.set(0, 0, 0);
      for (let f = 0; f < 6; f++) {
        pad.prev.copy(pad.pos);
        pad.pos.y += 0.045;                       // ~3,2 m/s
        pad.vel.set(0, 0.045 / dt, 0);
        C.stepPhysics(dt, ball, [pad], evs, null);
      }
      out.golpe = evs.some(e => e.type === 'paddle');
      out.vuela = ball.vel.y > 0.5;
      out.despegada = ball.__ppRestIdx === -1;
      return out;
    }""")
    if 'err' in (rest or {}):
        CHK(False, 'reposo: %s' % rest.get('err'))
    else:
        CHK(rest['apoyada'], 'reposo: la bola se POSA sobre la hoja (a rB de la cara)')
        CHK(rest['quiet'], 'reposo: velocidad estable < 0,08 m/s (SIN trompicones)')
        CHK(rest['sinGolpe'], 'reposo: CERO eventos de golpe al posarse (sin carga ni FX)')
        CHK(rest['conToque'], 'reposo: evento restTouch del «toc» suave')
        CHK(rest['registrada'], 'reposo: apoyo registrado (__ppRestIdx)')
        CHK(rest['carryOk'], 'transporte: la bola sube CON la pala despacio (3 cm, y=%s)' % rest['carryY'])
        CHK(rest['golpe'], 'swing: la pala que acelera GOLPEA (evento paddle)')
        CHK(rest['vuela'], 'swing: la bola sale volando (bote recuperado)')
        CHK(rest['despegada'], 'swing: el apoyo se rompe limpio (__ppRestIdx −1)')

    # ---- 3 · BARRA INTERACTIVA: altura viva, ±1 cm, clamp y persistencia
    barra2 = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const D = window.__PP_CORE.DIMS;
      const T = window.__PP_TRAIN.__test;
      const net = D.netTopY, top = D.tableTopY;
      const cm = (h) => Math.round((net + h - top) * 100);
      const out = { netMenosTop: Math.round((net - top) * 1000) / 1000 };
      out.h0 = T.barraH(); out.cm0 = T.barraCm(); out.cmEsperado = cm(out.h0);
      const X = T;
      X.barraVisSet(true);            // QA: estado visual de la prueba t2a
      X.barraHoverSet(0); out.consumo = X.barraAjustar(); out.h1 = X.barraH();
      out.cm1 = T.barraCm(); out.cm1Esperado = cm(out.h1);
      out.ls = localStorage.getItem('pp_train_barra_v1');
      X.barraHoverSet(1);
      for (let k = 0; k < 60; k++) X.barraAjustar();
      out.min = T.barraH();
      X.barraHoverSet(0);
      for (let k = 0; k < 60; k++) X.barraAjustar();
      out.max = T.barraH();
      X.barraHoverSet(-1);
      X.barraVisSet(false);
      return out;
    }""")
    if 'err' in (barra2 or {}):
        CHK(False, 'barra2: %s' % barra2.get('err'))
    else:
        CHK(barra2['cm0'] == barra2['cmEsperado'],
            'barra: lectura en cm sobre la SUPERFICIE (%d cm = red %s + barra %s)' %
            (barra2['cm0'], barra2['netMenosTop'], barra2['h0']))
        CHK(barra2['consumo'] is True, 'barra: el gatillo sobre la flecha SE CONSUME')
        CHK(abs(barra2['h1'] - 0.18) < 1e-9, 'barra: flecha ARRIBA sube 1 cm (0,17 → 0,18)')
        CHK(barra2['cm1'] == barra2['cm1Esperado'], 'barra: rótulo repintado a los cm vivos')
        CHK('{"h":0.18}' in (barra2['ls'] or ''), 'barra: persistencia escrita limpia (%s)' % barra2['ls'])
        CHK(barra2['min'] == 0.05, 'barra: clamp INFERIOR a 5 cm tras 60 pulsaciones')
        CHK(barra2['max'] == 0.40, 'barra: clamp SUPERIOR a 40 cm')

    # ---- 4 · la escena: mandos y cinta recolocados a la altura viva
    esc = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const T = window.__PP_TRAIN;
      try { T.tick(0.016); } catch (e) { return { err: 'tick: ' + (e && e.message) }; }
      const X = T.__test;
      const D = window.__PP_CORE.DIMS;
      const s = X.barraSpr();
      const out = { spr: s };
      out.zCentro = Math.round((D.tableCenterZ) * 1000) / 1000;
      return out;
    }""")
    if 'err' in (esc or {}):
        CHK(False, 'escena: %s' % esc.get('err'))
    else:
        s = esc['spr']
        if not s or not s.get('up'):
            CHK(False, 'escena: los mandos de la barra NO existen tras el buildScene')
        else:
            CHK(abs(s['up']['x'] - 1.05) < 1e-6 and abs(s['dn']['x'] - 1.05) < 1e-6 and abs(s['lbl']['x'] - 1.05) < 1e-6,
                'escena: flechas + rótulo a 1,05 m (fuera del extremo de la cinta)')
            CHK(abs(s['up']['y'] - (s['lbl']['y'] + 0.10)) < 1e-6 and abs(s['dn']['y'] - (s['lbl']['y'] - 0.10)) < 1e-6,
                'escena: ↑ arriba, cm en medio, ↓ abajo (columna de mandos)')
            CHK(s['cinta'] is not None and abs(s['cinta']['band'] - s['lbl']['y']) < 1e-6,
                'escena: la cinta vive a la MISMA altura que el rótulo')
            CHK(abs(s['grupo'] - esc['zCentro']) < 1e-6,
                'escena: todo el conjunto sobre el centro de la mesa (z=%s)' % s['grupo'])

    # ---- 5 · sin errores de página durante toda la sesión
    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))

    b.close()
srv.shutdown()

print()
print('QA r100 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)

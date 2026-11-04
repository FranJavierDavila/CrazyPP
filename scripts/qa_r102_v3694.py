#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r102_v3694.py — capa de QA de la ronda 102 (V3.6.94-SDK6).

Cuatro peticiones del dueño que quedaban vivas:
 1) «La partida multijugador es imposible… no ven la colocación de la
    raqueta de forma correcta… la orientación de la pala no se corresponde»:
    la pose v2 enviaba el grip CRUDO y el receptor multiplicaba la montura
    SIN conjugarla por el espejo de 180° → error de roll ≈166° y hoja
    desplazada ~26 cm. r102: la mano-con-pala viaja como CUATERNIÓN VISUAL
    (grip ⊗ montura viva, fórmula probada de v1) y el receptor lo conjuga
    entero sin multiplicar nada. PROTO 1→2 (parejas mixtas caen a v1, jamás
    interpretan mal el cable).
 2) «La etiqueta informativa… sobre la mesa pero pegada al jugador, no en
    el centro bajo la red»: rótulo cm + flechas sobre el cuadrante propio
    (z mundo = C()+HL−0,30); la cinta sigue en la red.
 3) «Su altura se controla mejor con cualquiera de los joysticks»: eje Y de
    CUALQUIER stick, pasos de 1 cm, 14 cm/s, muerta 0,30; el stick manda
    sobre la proximidad (suelta y anula el dwell).
 4) «Debemos informar de este control al jugador»: pista del rótulo con los
    dos caminos + toast 1 vez/sesión al entrar al PASE BAJO.
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8838
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html servido) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

AGUJAS = [
    # 1 · multijugador: la pose viaja como VISUAL y el receptor no toca monturas
    ('qv.copy(grip.quaternion).multiply(mq);',
     'c09: _samplePose compone el VISUAL grip⊗montura para la mano con pala'),
    ('if (i === g.paddleHand) {\n          const mq = (g.paddleMounts && g.paddleMounts[i] && g.paddleMounts[i].quaternion)',
     'c09: la rama visual SOLO en la mano con pala'),
    ('NetLink._poseQ || (NetLink._poseQ = new THREE.Quaternion())',
     'c09: scratch de pose sin asignaciones por frame'),
    ('// aquí NO se multiplica ninguna montura',
     'c12: el receptor usa el visual conjugado SIN multiplicar monturas'),
    ('netTmpV.set(0, (PALA_BLADE_Y - PALA_GRIP_Y) * PALA_SCALE, 0)\n            .applyQuaternion(netTmpQ).add(netTmpP);',
     'c12: hoja girada por la visual YA conjugada'),
    ('PROTO: 2,', 'c09b: PROTO=2 (parejas mixtas caen a v1, no interpretan mal el cable)'),
    # 2 · etiqueta (r103 la movió: pegada al jugador → DERECHA fuera de la vista,
    #     plano de la barra y mallas de orientación fija)
    ('const BARRA_LBL_X = () => HW() + 0.42;',
     'c13: rótulo a la DERECHA fuera de la visión de la mesa (r103)'),
    ('if (barraLbl) barraLbl.position.set(xl, by + 0.075, 0);',
     'c13: el rótulo viaja con la cinta (altura viva, plano de la barra)'),
    ('const cv = mkCanvas(400, 110), x = cv.getContext(\'2d\');',
     'c13: lienzo del rótulo 400 px (pista con joystick)'),
    ('new THREE.PlaneGeometry(0.34, 0.0935)',
     'c13: rótulo malla FIJA 0,34 m (misma densidad de píxeles)'),
    # 3 · joystick
    ('function barraStick(dt) {', 'c13: máquina del JOYSTICK presente'),
    ('const BARRA_STICK_V = 0.14;', 'c13: 14 cm/s a plena deflexión'),
    ('if (ax && Math.abs(ax.y) > 0.30) y += -ax.y;',
     'c13: eje Y de CUALQUIER stick, muerta 0,30, arriba=subir'),
    ('if (barraAgarrada) barraSoltar();\n      barraZona = false; barraZonaT = 0;',
     'c13: el stick MANDA — suelta el agarre y anula el dwell'),
    ('barraStick(dt);                        // r102: joystick, cualquier mando',
     'c13: barraTick alimenta la máquina del stick ANTES que la de la mano'),
    # 4 · informar al jugador
    ("return LANG === 'en' ? 'STICK ↑↓ OR HAND AT RIBBON' : 'JOYSTICK ↑↓ O MANO EN LA CINTA';",
     'c13: pista del rótulo con los DOS caminos'),
    ("'Barra: ' + BARRA_CM() + ' cm · ajústala con CUALQUIER JOYSTICK ↑↓ (o la mano en la cinta)'",
     'c13: toast informativo 1 vez/sesión'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

RETIRADAS = [
    # el defecto de fondo del multijugador
    ('const qVis = netTmpQ2.copy(netTmpQ)',
     'c12: montura multiplicada SIN conjugar RETIRADA (roll ~166°)'),
    ('const fisicaIzq = (smp.fl & 8) !== 0;',
     'c12: eleccion de montura por mano RETIRADA (la montura viaja en la pose)'),
    # la etiqueta en el centro de la red
    ('if (barraLbl) barraLbl.position.set(0, by + 0.13, 0);',
     'c13: rótulo en el CENTRO bajo la red RETIRADO'),
    ('barraLbl.scale.set(0.27, 0.093, 1);', 'c13: lienzo 320 px RETIRADO'),
]
for aguja, nombre in RETIRADAS:
    CHK(aguja not in GH, 'game.html: ' + nombre)

# la máquina de proximidad r101 queda INTACTA
CHK('function barraUpdate(px, py, pz, dt) {' in GH, 'game.html: máquina por proximidad intacta (r101)')
CHK('const BARRA_DWELL = 0.30;' in GH, 'game.html: dwell 0,30 intacto (r101)')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
# r103 · re-anclada a la build viva (la r103 movió el rótulo y selló 3.6.95)
CHK(bool(mver) and mver.group(1) == '3.6.104-SDK6', 'c00: VERSION sella 3.6.104-SDK6 (re-anclada r103)')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 100, 'VERSION.json: FASE 99 (re-anclada r105)')
CHK(V.get('hub') == 'v36104-sdk6', 'VERSION.json: hub v3695-sdk6 (re-anclada r103)')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

JS_QMATH = """
window.__qmul = function(a, b) {
  const [ax, ay, az, aw] = a, [bx, by, bz, bw] = b;
  return [
    aw*bx + ax*bw + ay*bz - az*by,
    aw*by - ax*bz + ay*bw + az*bx,
    aw*bz + ax*by - ay*bx + az*bw,
    aw*bw - ax*bx - ay*by - az*bz,
  ];
};
window.__qconj = (a) => [-a[0], -a[1], -a[2], a[3]];
window.__qmirror = (a) => window.__qmul(window.__qmul([0,1,0,0], a), [0,-1,0,0]);
window.__qaplicar = function(q, v) {
  // v' = q · v · q⁻¹ (fórmula clásica sin THREE)
  const [qx, qy, qz, qw] = q, [vx, vy, vz] = v;
  const ix = qw*vx + qy*vz - qz*vy, iy = qw*vy + qz*vx - qx*vz, iz = qw*vz + qx*vy - qy*vx, iw = -qx*vx - qy*vy - qz*vz;
  return [
    ix*qw + iw*(-qx) + iy*(-qz) - iz*(-qy),
    iy*qw + iw*(-qy) + iz*(-qx) - ix*(-qz),
    iz*qw + iw*(-qz) + ix*(-qy) - iy*(-qx),
  ];
};
window.__qangulo = function(a, b) {
  let d = Math.abs(a[0]*b[0] + a[1]*b[1] + a[2]*b[2] + a[3]*b[3]);
  d = Math.min(1, Math.max(-1, d));
  return 2 * Math.acos(d);   // radianes
};
// montura de c02: pitch −90° en X, roll ±(90°−0,12) en Z, mount = roll ⊗ pitch
window.__mountQ = function(roll) {
  const pitch = window.__qmul([Math.sin(-Math.PI/4),0,0,Math.cos(-Math.PI/4)], [0,0,0,1]);
  const p = [Math.sin(-Math.PI/4), 0, 0, Math.cos(-Math.PI/4)];
  const r = [0, 0, Math.sin(roll/2), Math.cos(roll/2)];
  return window.__qmul(r, p);
};
"""

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
    pg.evaluate(JS_QMATH)

    # ---- 1 · PROTO=2 y códec: la pose hace ida y vuelta BYTE-FIEL
    codec = pg.evaluate("""() => {
      const P = window.__PPNET;
      const out = { proto: P.VP.PROTO };
      const qVis = [0.12, 0.35, -0.08, Math.sqrt(1 - 0.12*0.12 - 0.35*0.35 - 0.08*0.08)];
      const pose = { hp:[0.1,1.7,-0.2], hq:[0,0,0,1], lp:[-0.3,1.0,-1.2], lq:[0,0,0,1],
                     rp:[0.3,1.0,-1.2], rq:qVis, fl: 1|2|4 };
      const buf = new ArrayBuffer(P.VP.MAX_PKT);
      const n = P.encodePacket(buf, { seq:7, ack:0, ackBits:0, sendTime:1234, echoTime:0,
                                      echoDelay:0, pose, yAnchor:0.76 });
      const pkt = P.decodePacket(buf.slice(0, n), { yAnchor:0.76, evs: [] });
      if (!pkt || !pkt.pose) { out.err = 'paquete nulo'; return out; }
      out.rq = pkt.pose.rq;
      out.yLp = pkt.pose.lp[1];
      return out;
    }""")
    CHK(codec.get('proto') == 2, 'códec: PROTO=2 vivo en el juego')
    if 'err' in codec:
        CHK(False, 'códec: %s' % codec['err'])
    else:
        dq = codec['rq']
        errq = max(abs(dq[i] - [0.12, 0.35, -0.08, dq[3]][i]) for i in (0, 1, 2))
        CHK(errq < 3e-3, 'códec: el cuaternión visual sobrevive al binario (±%s rad en componentes)' % ('5e-4'))
        CHK(abs(codec['yLp'] - 1.0) < 1e-6, 'códec: la Y re-anclada al tapete propio (yAnchor)')

    # ---- 2 · EL CORAZÓN DEL FIX: el quatFromNet EXACTO del fuente (el build
    # es byte-exacto) conjuga el visual entero; la fórmula vieja (grip crudo +
    # montura sin conjugar) volteaba la CARA ~166° y desplazaba la hoja ~26 cm
    def extraer_fun(nombre, siguiente):
        src = open(os.path.join(RAIZ, 'src/game/core/c09_red_netlink.js'), encoding='utf-8').read()
        i0 = src.index('static %s(' % nombre)
        i1 = src.index('static %s(' % siguiente)
        cuerpo = src[i0:i1].strip()
        cuerpo = cuerpo[cuerpo.index('{') + 1:cuerpo.rindex('}')]
        return cuerpo.strip()
    QA_QUATFROMNET = extraer_fun('quatFromNet', 'quatToNet')
    conj = pg.evaluate(
        """(codigoQ) => {
          const STUB = () => ({ x: 0, y: 0, z: 0, w: 1,
            set(x, y, z, w) { this.x = x; this.y = y; this.z = z; this.w = w; } });
          const quatFromNet = new Function('a', 'out', codigoQ);
          const out = {};
          const roll = Math.PI / 2 - 0.12;
          const M = window.__mountQ(roll);              // montura de la mano derecha
          const casos = {
            identidad: [0, 0, 0, 1],
            tilt: window.__qmul(
              [Math.sin(0.26), 0, 0, Math.cos(0.26)],
              [0, Math.sin(0.17), 0, Math.cos(0.17)]),
          };
          for (const k in casos) {
            const grip = casos[k];
            const qVis = window.__qmul(grip, M);                 // lo que r102 ENVÍA
            const rec = quatFromNet(qVis.slice(), STUB());
            const esperado = window.__qmirror(qVis);             // R⊗qVis⊗R⁻¹
            const arr = [rec.x, rec.y, rec.z, rec.w];
            out[k] = { errConj: window.__qangulo(arr, esperado) };
            // LO VIEJO: conjugar el grip crudo y multiplicar la montura sin conjugar
            const g2 = quatFromNet(grip.slice(), STUB());
            out[k].viejo = window.__qmul([g2.x, g2.y, g2.z, g2.w], M);
            // desplazamiento del centro de la hoja (offset del modelo: 0,026·(2,1115+2,9) m)
            const off = 0.026 * (2.1115 + 2.9);
            const dN = window.__qaplicar(arr, [0, 1, 0]);
            const dV = window.__qaplicar(out[k].viejo, [0, 1, 0]);
            const dC = window.__qaplicar(esperado, [0, 1, 0]);
            out[k].desvioNuevo = Math.hypot(dN[0]-dC[0], dN[1]-dC[1], dN[2]-dC[2]) * off;
            out[k].desvioViejo = Math.hypot(dV[0]-dC[0], dV[1]-dC[1], dV[2]-dC[2]) * off;
          }
          return out;
        }""", QA_QUATFROMNET)
    for k in ('identidad', 'tilt'):
        if k not in conj:
            CHK(False, 'conjugación: caso %s ausente' % k)
            continue
        c = conj[k]
        CHK(c['errConj'] < 1e-6, 'conjugación (%s): quatFromNet(visual) == R⊗visual⊗R⁻¹ (err %.2e rad)' % (k, c['errConj']))
        CHK(c['desvioNuevo'] < 5e-3, 'conjugación (%s): centro de la hoja FIEL (desvío %.1f mm)' % (k, c['desvioNuevo'] * 1000))
        CHK(c['desvioViejo'] > 0.15, 'conjugación (%s): la fórmula VIEJA desviaba la hoja %.1f cm (el defecto del dueño)' % (k, c['desvioViejo'] * 100))

    # ---- 3 · rótulo FUERA DE LA VISTA (r103): derecha + plano de la barra
    esc = pg.evaluate("""() => {
      const T = window.__PP_TRAIN;
      const X = T.__test;
      const D = window.__PP_CORE.DIMS;
      try { T.tick(0.016); } catch (e) { return { err: 'tick: ' + (e && e.message) }; }
      X.barraVisSet(true); X.barraLay();
      return { spr: X.barraSpr(), fijo: X.barraFijo(), zLbl: X.barraEtiquetaZ(),
               xEsperado: D.tableHalfWidth + 0.42, cz: D.tableCenterZ };
    }""")
    if 'err' in (esc or {}):
        CHK(False, 'etiqueta: %s' % esc.get('err'))
    else:
        s = esc['spr']
        CHK(s and s.get('up'), 'etiqueta: mandos construidos')
        if s and s.get('up'):
            CHK(abs(s['lbl']['x'] - esc['xEsperado']) < 1e-6,
                'etiqueta: rótulo a la DERECHA de la mesa (x=%s = canto+0,42) — r103' % round(s['lbl']['x'], 4))
            CHK(abs(s['up']['x'] - (esc['xEsperado'] - 0.24)) < 1e-6 and
                abs(s['dn']['x'] - (esc['xEsperado'] + 0.24)) < 1e-6,
                'etiqueta: flechas flanqueando el rótulo (±0,24 m)')
            CHK(abs(esc['zLbl'] - esc['cz']) < 1e-6,
                'etiqueta: en el MISMO PLANO que la barra (z mundo=%s = centro de mesa)' % round(esc['zLbl'], 3))
            CHK(esc['fijo']['lblMesh'] and esc['fijo']['upMesh'] and esc['fijo']['dnMesh'],
                'etiqueta: MALLAS de orientación FIJA (isMesh, jamás sprites)')

    # ---- 4 · JOYSTICK: pasos de 1 cm, arriba=subir, clamps, manda sobre la mano
    stick = pg.evaluate("""() => {
      const T = window.__PP_TRAIN, X = T.__test, g = window.__PP_GAME;
      const D = window.__PP_CORE.DIMS;
      const out = {};
      X.barraVisSet(true);
      X.barraLay();
      const h0 = X.barraH();
      out.h0 = h0;
      const orig = g.stickAxis.bind(g);
      try {
        g.stickAxis = (h) => (h === 0 ? { x: 0, y: -1 } : { x: 0, y: 0 });  // SÓLO un stick arriba
        let n = 0;
        for (let k = 0; k < 72; k++) if (X.barraStick(1 / 72)) n++;
        out.pasosSube = n;
        out.hSube = X.barraH();
        out.acc = X.barraStickEstado().acc;
        g.stickAxis = (h) => (h === 0 ? { x: 0, y: 1 } : { x: 0, y: 0 });   // un stick abajo
        for (let k = 0; k < 72 * 6; k++) X.barraStick(1 / 72);
        out.hSuelo = X.barraH();                          // clamp inferior 0,05
        g.stickAxis = (h) => (h === 0 ? { x: 0, y: -1 } : { x: 0, y: 0 });
        for (let k = 0; k < 72 * 6; k++) X.barraStick(1 / 72);
        out.hTecho = X.barraH();                          // clamp superior 0,40
        g.stickAxis = orig;
        X.barraStick(1 / 72);                             // sin eje → acc a 0
        out.accSuelto = X.barraStickEstado().acc;
        // el stick MANDA sobre la proximidad: agarro primero con la mano…
        const zCinta = D.tableCenterZ, net = D.netTopY;
        for (let k = 0; k < 22; k++) X.barraUpdate(0, net + 0.24, zCinta, 1 / 72);
        out.agarrada = X.barraEstado().agarrada;
        out.hAgarrada = X.barraH();
        g.stickAxis = (h) => (h === 0 ? { x: 0, y: -1 } : { x: 0, y: 0 });
        for (let k = 0; k < 72; k++) X.barraStick(1 / 72);
        out.soltadaPorStick = !X.barraEstado().agarrada && !X.barraEstado().zona;
        out.hTrasStick = X.barraH();
        // …y el dwell quedó ANULADO: la mano en el pasillo NO re-agarra al instante
        X.barraUpdate(0, net + 0.24, zCinta, 1 / 72);
        out.zonaTrasStick = X.barraEstado().zona;
        out.reAgarrada = X.barraEstado().agarrada;
        g.stickAxis = orig;
        X.barraVisSet(false);
      } catch (e) {
        out.err = e && e.message;
        try { g.stickAxis = orig; } catch (e2) { /* */ }
      }
      return out;
    }""")
    if 'err' in stick:
        CHK(False, 'joystick: %s' % stick['err'])
    else:
        CHK(13 <= stick['pasosSube'] <= 15,
            'joystick: 72 frames a 14 cm/s ≈ 14 pasos de 1 cm (%s)' % stick['pasosSube'])
        CHK(abs(stick['hSube'] - (stick['h0'] + stick['pasosSube'] * 0.01)) < 1e-9,
            'joystick: cada paso = 1 cm exacto (0,%02d → 0,%02d)' % (round(stick['h0'] * 100), round(stick['hSube'] * 100)))
        CHK(0 <= stick['acc'] <= 1.0 + 1e-9, 'joystick: el acumulador nunca guarda más de 1 paso (acc=%.4f — sin saltos)' % stick['acc'])
        CHK(abs(stick['hSuelo'] - 0.05) < 1e-9, 'joystick: clamp INFERIOR 5 cm')
        CHK(abs(stick['hTecho'] - 0.40) < 1e-9, 'joystick: clamp SUPERIOR 40 cm')
        CHK(stick['accSuelto'] == 0, 'joystick: sin eje → acumulador a 0')
        CHK(stick['agarrada'], 'joystick: (preparación) la mano AGARRÓ la barra por proximidad')
        CHK(stick['soltadaPorStick'], 'joystick: el stick SUELTA la barra y limpia la zona')
        CHK(abs(stick['hTrasStick'] - (stick['hAgarrada'] + 0.14)) < 0.011,
            'joystick: tras soltar, 72 frames suben 14 cm desde el agarre (0,%02d → 0,%02d)'
            % (round(stick['hAgarrada'] * 100), round(stick['hTrasStick'] * 100)))
        CHK(stick['zonaTrasStick'] and not stick['reAgarrada'],
            'joystick: dwell ANULADO — la mano vuelve a ZONA pero NO re-agarra al instante')

    # ---- 5 · sin errores de página
    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))

    b.close()
srv.shutdown()

print()
print('QA r102 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)

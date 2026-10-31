#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r98_v3690.py — capa de QA de la ronda 98 (V3.6.90-SDK6).
Tres peticiones del dueño sobre la interfaz de los menús:
 1) TOOLTIPS BONITOS: «quiero algo más vistoso y bonito como un bocadillo
    sobre fondo blanco con el texto en negro y que apunte con precisión a
    cada apartado al que hace referencia» — burbuja blanca, texto negro,
    sombra suave y COLA (triángulo) hasta el centro exacto del control,
    inclinada si la burbuja se recorta en los bordes.
 2) DESLIZADORES ARRASTRABLES: «pudiéndolos desplazar con el mando
    apuntando al deslizador y con el gatillo apretado moviendo el mando a
    derecha e izquierda» — las barras de volumen (música/efectos) fijan al
    pulsar Y siguen ajustando EN VIVO mientras el gatillo va apretado
    (_menuDrag + _menuDragUpdate por frame, cierre honesto en selectend).
 3) MESA AGARRABLE: «poder cogerla simplemente apuntando con los mandos
    hacia ella (aparece un rayo de selección) y moviendo hacia arriba o
    hacia abajo la subimos o bajamos y bien grande sobre nuestro lado de
    la mesa un texto con su altura. El tooltip que diga en este caso cómo
    se ajusta su altura» — adiós al raíl del deslizador: rayo de
    selección + anillo en el punto de contacto, agarre 1:1 con la altura
    del mando (clamp 0,70-0,84), RÓTULO GRANDE sobre el lado del dueño
    con los cm vivos, tick por cm, persistencia y limpieza total al salir
    de la página MESA (los campeonatos siguen intocables — regla r96).
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
CORE = os.path.join(RAIZ, 'src/game/core')
PORT = 8820
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (fuente + servido) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
C00 = open(os.path.join(CORE, 'c00_pre_three.js'), encoding='utf-8').read()
C12 = open(os.path.join(CORE, 'c12_pingponggame.js'), encoding='utf-8').read()

AGUJAS = [
    # (1) bocadillo blanco con texto negro y cola precisa
    ('r98 · BOCADILLO DEL DUEÑO', 'c12: bocadillo blanco (cabecera del pintor)'),
    ("c.fillStyle = '#ffffff';", 'c12: burbuja RELLENA DE BLANCO'),
    ("c.shadowColor = 'rgba(0,0,0,0.42)';", 'c12: sombra suave que despega la burbuja'),
    ('COLA del bocadillo', 'c12: cola del bocadillo (triángulo)'),
    ("c.fillStyle = '#0e1219';", 'c12: texto NEGRO del bocadillo'),
    ("const itemCx = Math.min(Math.max(r.x + r.w / 2, 20), 1004);",
     'c12: la cola aterriza en el centro EXACTO del control'),
    # (2) deslizadores arrastrables
    ('this._menuDrag = { hand, id: ns };', 'c12: el clic ARMA el arrastre por mano'),
    ('_menuDragUpdate() {', 'c12: actualización en vivo del arrastre'),
    ('onSelectEnd(i) {', 'c12: cierre honesto del gesto al soltar el gatillo'),
    ("targetRay.addEventListener('selectend', () => this.onSelectEnd(i));",
     'c12: listener selectend por mando (r98)'),
    ("const nuevo = Math.round(frac * 10) / 10;", 'c12: el arrastre respeta los deciles'),
    # (3) mesa agarrable
    ('_mesaGrabActivo()', 'c12: guard del agarre (página MESA + sala a la vista)'),
    ('_mesaRay(origin, dir) {', 'c12: rayo de selección contra la mesa real'),
    ('_mesaGrabUpdate() {', 'c12: la mesa sigue la altura del mando 1:1'),
    ('_mesaLabelShow() {', 'c12: rótulo GRANDE con los cm vivos'),
    ('_mesaGrabCleanup() {', 'c12: limpieza total al salir de la página MESA'),
    ('this._mesaGrab = { hand: i, y0: this.mesaAltoY, cy0: p0.y };',
     'c12: el gatillo sobre la mesa COMIENZA el agarre'),
    ('this._menuGripPos[h] = muGrip.y;', 'c12: altura viva del mando captada por frame'),
    ('line.scale.z = sobreMesa ? sobreMesa.dist : (hit ? hit.distance : 0.5);',
     'c12: el haz LLEGA a la mesa cuando es ella la que se apunta'),
    ('const thick = (idx >= 0 || sobreMesa) ? 1.7 : 1;',
     'c12: el haz engorda también sobre la mesa'),
    ('RingGeometry(0.026, 0.044, 28)', 'c12: anillo de selección en el punto de contacto'),
    ('PlaneGeometry(1.12, 0.28)', 'c12: rótulo GRANDE (1,12 m) sobre la mesa'),
    ('this._mesaLabel.position.set(0, DIMS.tableTopY + 0.52, 0.92);',
     'c12: rótulo sobre el LADO DEL DUEÑO (+z), flotando'),
    ('MESA_ALTO_MAX, Math.max(MESA_ALTO_MIN, g2.y0 + (gy - g2.cy0))',
     'c12: agarre con clamp honesto 0,70-0,84'),
    # (4) página MESA sin raíl, con lectura + pista del gesto
    ("label(T('mesa_alto_grab')", 'c12: la página MESA explica el gesto nuevo'),
    ('r98 · ADIÓS AL RAÍL', 'c12: la página MESA documenta la retirada del raíl'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# el raíl del deslizador NO queda en el juego (re-ancla honesto r98)
CHK("id: 'mesa_altoy'" not in GH, 'game.html: el raíl mesa_altoy está RETIRADO')

# i18n del gesto nuevo (ES + EN)
CHK("hint_mesa_altoy: 'Apunta a la mesa, mantén el gatillo y súbela o bájala moviendo el mando: verás su altura en grande'" in C00,
    'c00 ES: tooltip del gesto de altura')
CHK("hint_mesa_altoy: 'Point at the table, hold the trigger and move it up or down: its height shows BIG'" in C00,
    'c00 EN: tooltip del gesto de altura')
CHK("mesa_alto_grab: 'Agarra la mesa: apunta, mantén el gatillo y muévela arriba/abajo'" in C00,
    'c00 ES: pista del gesto en la página MESA')
CHK("mesa_alto_grab: 'Grab the table: aim, hold the trigger and move it up or down'" in C00,
    'c00 EN: pista del gesto en la página MESA')
CHK("hint_mvolset: 'Mantén el gatillo sobre la barra y desliza el mando a izquierda o derecha'" in C00,
    'c00 ES: tooltip del arrastre (música)')
CHK("hint_fvolset: 'Mantén el gatillo sobre la barra y desliza el mando a izquierda o derecha'" in C00,
    'c00 ES: tooltip del arrastre (efectos)')
CHK("hint_mvolset: 'Hold the trigger on the bar and slide your controller left or right'" in C00,
    'c00 EN: tooltip del arrastre (música)')
CHK("hint_fvolset: 'Hold the trigger on the bar and slide your controller left or right'" in C00,
    'c00 EN: tooltip del arrastre (efectos)')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.90-SDK6', 'c00: VERSION sella 3.6.90-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 92, 'VERSION.json: FASE 92')
CHK(V.get('hub') == 'v3690-sdk6', 'VERSION.json: hub v3690-sdk6')

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

    # ---- 1 · BOCADILLO: blanco, texto negro, cola precisa, nada sin hover
    tip = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const c = g.menuCanvas.getContext('2d');
      const STRIP = (x, y, w, h) => Array.from(c.getImageData(x, y, w, h).data);
      const blancos = (d) => d.filter((v, i) => i % 4 === 0 && v > 244).length;
      const oscuros = (d) => d.filter((v, i) => i % 4 === 0 && v < 90).length;
      g.menuOpen = true; g.menuPage = 'optsSalaMesa';
      g.menuHover = [-1, -1];
      g.drawMenu();
      const r = g.menuRects.find(x => x.id === 'mesa_skin:verde');
      const ir = g.menuRects.indexOf(r);
      const sin = { cuerpo: STRIP(430, r.y - 62, 160, 4), cola: STRIP(511, r.y - 12, 2, 8) };
      g.menuHover = [ir, -1];
      g.drawMenu();
      // burbuja de 1 línea: borde inferior en r.y-14, texto centrado en r.y-46
      const con = {
        cuerpo: STRIP(430, r.y - 62, 160, 4),     // interior blanco de la burbuja
        texto: STRIP(470, r.y - 54, 84, 16),      // trazo negro del texto
        cola: STRIP(511, r.y - 12, 2, 8),         // triángulo sobre el control
      };
      g.menuHover = [-1, -1];
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return { sin, con };
    }""")
    if 'err' in (tip or {}):
        CHK(False, 'bocadillo: %s' % tip.get('err'))
    else:
        CHK(tip['con']['cuerpo'].count(255) > 300 and tip['sin']['cuerpo'] != tip['con']['cuerpo'],
            'bocadillo: cuerpo BLANCO puro al apuntar (y distinto del panel sin hover)')
        CHK(len(tip['con']['texto']) > 0 and sum(1 for v in tip['con']['texto'] if v < 90) > 8,
            'bocadillo: texto NEGRO legible dentro de la burbuja')
        CHK(sum(1 for v in tip['con']['cola'] if v > 244) >= 2,
            'bocadillo: COLA blanca llegando al borde superior del control')
        CHK(sum(1 for v in tip['sin']['cola'] if v > 244) == 0,
            'bocadillo: sin hover NO pinta cola ni burbuja')

    # ---- 2 · ARRASTRE de deslizadores: arma, mueve en vivo, cierra
    # (en el casco connected[] es cierto por XR; en headless lo simula el QA)
    drag = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const out = {};
      g.connected = [true, true];   // r98: los gestos exigen mando vivo (QA)
      g.menuOpen = true; g.menuPage = 'optsSonido'; g.drawMenu();
      const busc = (id) => g.menuRects.find(x => x.id === id);   // SIEMPRE fresco
      // música: clic al 20% (arma el arrastre) y arrastre hasta el 70%
      let rv = busc('mvolset');
      g._menuHitPx = [{ x: rv.x + rv.w * 0.2, y: rv.y + 10 }, null];
      g.menuClick(g.menuRects.indexOf(rv), 0);
      out.v1 = g.audio.musicVol;
      out.arma = !!(g._menuDrag && g._menuDrag.id === 'mvolset' && g._menuDrag.hand === 0);
      g._menuHitPx[0] = { x: rv.x + rv.w * 0.74, y: rv.y + 10 };
      g._menuDragUpdate();
      out.v2 = g.audio.musicVol;          // 74% → 0,7 (decil)
      g._menuHitPx[0] = { x: rv.x + rv.w * 0.98, y: rv.y + 10 };
      g._menuDragUpdate();
      out.v3 = g.audio.musicVol;          // 98% → 1,0
      g.onSelectEnd(0);
      out.cierra = g._menuDrag === null;
      out.v4 = g.audio.musicVol;          // el valor PERSISTE tras soltar
      // efectos: clic al 50% y arrastre al 30% con la OTRA mano
      let rf = busc('fvolset');
      g._menuHitPx = [null, { x: rf.x + rf.w * 0.5, y: rf.y + 10 }];
      g.menuClick(g.menuRects.indexOf(rf), 1);
      out.f1 = g.audio.fxVol;
      g._menuHitPx[1] = { x: rf.x + rf.w * 0.31, y: rf.y + 10 };
      g._menuDragUpdate();
      out.f2 = g.audio.fxVol;
      g.onSelectEnd(1);
      g.audio.setMusicVol(1);
      g.audio.setFxVol(1);
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return out;
    }""")
    if 'err' in (drag or {}):
        CHK(False, 'arrastre: %s' % drag.get('err'))
    else:
        CHK(abs(drag['v1'] - 0.2) < 0.011, 'arrastre música: clic al 20%% fija 0,2 (%s)' % drag['v1'])
        CHK(drag['arma'] is True, 'arrastre música: el clic ARMA _menuDrag (mano 0, mvolset)')
        CHK(abs(drag['v2'] - 0.7) < 0.011, 'arrastre música: mando al 74%% → 0,7 EN VIVO (%s)' % drag['v2'])
        CHK(abs(drag['v3'] - 1.0) < 0.011, 'arrastre música: mando al 98%% → 1,0 (%s)' % drag['v3'])
        CHK(drag['cierra'] is True, 'arrastre música: onSelectEnd cierra el gesto')
        CHK(abs(drag['v4'] - 1.0) < 0.011, 'arrastre música: el valor se queda al soltar')
        CHK(abs(drag['f1'] - 0.5) < 0.011, 'arrastre efectos: clic al 50%% fija 0,5 (%s)' % drag['f1'])
        CHK(abs(drag['f2'] - 0.3) < 0.011, 'arrastre efectos: la OTRA mano arrastra al 30%% (%s)' % drag['f2'])

    # ---- 3 · MESA AGARRABLE: guard, agarre 1:1, rótulo, clamps, limpieza
    # (connected[0]=true ya lo dejó el bloque de arrastre — como en el casco)
    grab = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      g.connected = [true, true];   // los gestos exigen mando vivo (QA)
      const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || g.DIMS;
      const out = {};
      out.rings = (g._mesaRings || []).length;
      out.labelMesh = !!g._mesaLabel;
      // guard: sin menú no hay agarre
      g.menuOpen = false;
      out.guardSinMenu = g._mesaGrabActivo();
      // guard: menú abierto en la página MESA con el Hall delante
      g.menuOpen = true; g.inHall = true; g.menuPage = 'optsSalaMesa';
      g._salaPreviewUpdate();
      out.guardOn = g._mesaGrabActivo();
      out.guardOtraPag = (g.menuPage = 'optsSalaRoom', g._mesaGrabActivo());
      g.menuPage = 'optsSalaMesa';
      // rayo: con la mesa oculta el rayo de selección responde NULL
      const tg = g.tableGroup;
      const vis0 = tg.visible;
      tg.visible = false;
      out.rayoOculto = g._mesaRay(null, null) === null;
      tg.visible = vis0;
      // agarre: base 0,76 · el mando SUBE 5 cm → mesa a 0,81 · rótulo vivo
      g._mesaAplicarY(0.76);
      g._mesaGrab = { hand: 0, y0: 0.76, cy0: 1.10 };
      g._mesaCmLast = 76;
      g._menuGripPos = [1.15, null];
      g._mesaGrabUpdate();
      out.y1 = Math.round(g.mesaAltoY * 1000) / 1000;
      out.dims1 = Math.round(D.tableTopY * 1000) / 1000;
      out.labelVis = g._mesaLabel.visible;
      out.labelPos = [Math.round(g._mesaLabel.position.x * 100) / 100,
                      Math.round(g._mesaLabel.position.y * 100) / 100,
                      Math.round(g._mesaLabel.position.z * 100) / 100];
      out.ls1 = localStorage.getItem('pp_mesaaltoy');
      // clamp alto: el mando se dispara a 2,5 → la mesa se frena en 0,84
      g._menuGripPos[0] = 2.5;
      g._mesaGrabUpdate();
      out.yHi = Math.round(g.mesaAltoY * 1000) / 1000;
      // clamp bajo: el mando cae a 0,0 → la mesa se frena en 0,70
      g._mesaGrab = { hand: 0, y0: 0.84, cy0: 2.0 };
      g._menuGripPos[0] = 0.0;
      g._mesaGrabUpdate();
      out.yLo = Math.round(g.mesaAltoY * 1000) / 1000;
      // soltar: el agarre muere y el rótulo se despide (1 s de fundido)
      g.onSelectEnd(0);
      out.grabOff = g._mesaGrab === null;
      out.labelT = Math.round((g._mesaLabelT || 0) * 100) / 100;
      // limpieza: al salir de la página MESA no queda NADA vivo
      g.menuPage = 'optsSala';
      g._mesaGrabCleanup();
      out.limpieza = !g._mesaLabel.visible && g._mesaRings.every(r2 => !r2.visible)
                     && g._mesaHover.every(h2 => !h2) && g._mesaGrab === null;
      g._mesaAplicarY(0.76);
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return out;
    }""")
    if 'err' in (grab or {}):
        CHK(False, 'agarre: %s' % grab.get('err'))
    else:
        CHK(grab['rings'] == 2, 'agarre: DOS anillos de selección (uno por mando)')
        CHK(grab['labelMesh'] is True, 'agarre: el rótulo 3D existe')
        CHK(grab['guardSinMenu'] is False, 'agarre: sin menú abierto NO hay agarre')
        CHK(grab['guardOn'] is True, 'agarre: página MESA con el Hall delante SÍ hay agarre')
        CHK(grab['guardOtraPag'] is False, 'agarre: en la página SALA (temas) NO hay agarre')
        CHK(grab['rayoOculto'] is True, 'agarre: mesa oculta → el rayo de selección responde null')
        CHK(abs(grab['y1'] - 0.81) < 0.0011, 'agarre: mando +5 cm → mesa 0,76→0,81 (1:1, %s)' % grab['y1'])
        CHK(abs(grab['dims1'] - 0.81) < 0.0011, 'agarre: DIMS.tableTopY acompaña EN VIVO (%s)' % grab['dims1'])
        CHK(grab['labelVis'] is True, 'agarre: el rótulo grande se VE durante el agarre')
        CHK(grab['labelPos'][2] == 0.92 and grab['labelPos'][1] > 1.3,
            'agarre: rótulo sobre el LADO DEL DUEÑO (z +0,92, por encima del tablero)')
        CHK(grab['ls1'] == '0.81', 'agarre: la altura agarrada PERSISTE (pp_mesaaltoy=0.81)')
        CHK(abs(grab['yHi'] - 0.84) < 0.0011, 'agarre: clamp ALTO honesto (0,84, %s)' % grab['yHi'])
        CHK(abs(grab['yLo'] - 0.70) < 0.0011, 'agarre: clamp BAJO honesto (0,70, %s)' % grab['yLo'])
        CHK(grab['grabOff'] is True, 'agarre: soltar el gatillo termina el agarre')
        CHK(grab['labelT'] == 1.0, 'agarre: el rótulo se despide con fundido (1 s)')
        CHK(grab['limpieza'] is True, 'agarre: fuera de la página MESA no queda NADA vivo')

    # ---- 4 · MESA OCUPADA (campeonato): la mesa es INTOCABLE — regla r96
    intoc = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const out = {};
      const real = g.mesaOcupada;
      g.mesaOcupada = () => true;          // sombra: campeonato activo
      g.menuOpen = true; g.inHall = true; g.menuPage = 'optsSalaMesa';
      out.guardChamp = g._mesaGrabActivo();
      out.rayoChamp = g._mesaRay(null, null) === null;
      g.mesaOcupada = real;
      g.menuOpen = false;
      return out;
    }""")
    if 'err' in (intoc or {}):
        CHK(False, 'intocable: %s' % intoc.get('err'))
    else:
        CHK(intoc['guardChamp'] is False, 'intocable: en campeonato la mesa NO se agarra (regla r96)')
        CHK(intoc['rayoChamp'] is True, 'intocable: en campeonato el rayo de selección responde null')

    # ---- 5 · páginas del menú sin errores (con los gestos armados y limpios)
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      for (const p of ['opts', 'optsJuego', 'optsSala', 'optsSalaRoom', 'optsSalaMesa',
                       'optsSonido', 'optsVisual', 'optsPerfil', 'optsRendi', 'optsPala',
                       'main', 'champs', 'rank', 'multi']) {
        g.menuOpen = true; g.menuPage = p; g.drawMenu(); g.updateMenu(0.016);
      }
      g.menuOpen = false;
    }""")
    pg.wait_for_timeout(400)

    if errs:
        CHK(False, 'pageerrors: %d — %s' % (len(errs), errs[:2]))
    else:
        CHK(True, 'pageerrors: 0 en toda la sesión (boot + gestos + repintados)')

srv.shutdown()

print('\n== QA r98 · marcador ==')
print('  OK: %d · FALLO: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys_exit_code = 1
else:
    print('VERDE — r98 completa (bocadillo + arrastre + mesa agarrable)')
    sys_exit_code = 0
import sys as _s
_s.exit(sys_exit_code)

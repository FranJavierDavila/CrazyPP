#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r99_v3691.py — capa de QA de la ronda 99 (V3.6.91-SDK6).
Dos ajustes finos del dueño sobre la r98:
 1) % DE LOS DESLIZADORES ENCIMA DE LA BARRA: «los indicadores de % en los
    controles deslizantes del menú, ponerlos ligeramente encima de la barra
    de deslizamiento para que no se pisen por esta al moverlo» — la lectura
    sube SOBRE el raíl (ámbar 17 px) y la bola del deslizador ya no la tapa
    nunca (antes vivía EN la barra, a vy+27, y el knob pasaba por encima).
 2) RÓTULO DE ALTURA SOBRE LA PROPIA MESA: «la indicación de altura de la
    mesa ponerla mejor sobre la propia mesa con un texto algo más pequeño
    y paralela a la superficie de la mesa que se pueda leer bien» — el
    plano flotante (1,12×0,28 a +0,52 m) pasa a DECAL TUMBADO (rotation.x
    = −90°, texto mirando al techo) de 1,04×0,26 m con texto 96 px, a
    6 mm del tablero y 34 cm hacia la red desde el borde del dueño, con
    seguimiento POR FRAME de la superficie mientras se agarra.
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
CORE = os.path.join(RAIZ, 'src/game/core')
PORT = 8821
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
    # (1) % encima de la barra (r99)
    ('r99 · % LIGERAMENTE ENCIMA de la barra', 'c12: cabecera del ajuste del %'),
    ("c.fillText(Math.round(vol * 100) + '%', 512, vy + 2);",
     'c12: la lectura % vive SOBRE el raíl (vy+2, era vy+27 DENTRO)'),
    ("c.fillStyle = '#ffd257';\n          c.font = '800 17px system-ui, sans-serif';",
     'c12: % en ámbar 17 px, apartado de la barra'),
    # (2) rótulo decal sobre la superficie (r99)
    ('r99 · el rótulo pasa a DECAL PLANO SOBRE LA SUPERFICIE',
     'c12: cabecera del decal (creación)'),
    ('this._mesaLabel.rotation.x = -Math.PI / 2;   // decal plano sobre la mesa',
     'c12: plano TUMBADO paralelo a la superficie'),
    ('new THREE.PlaneGeometry(1.04, 0.26)',
     'c12: plano 1,04×0,26 (algo más pequeño que 1,12×0,28)'),
    ("c2.font = '800 96px system-ui, sans-serif';",
     'c12: texto 96 px (algo más pequeño que 118)'),
    ('DIMS.tableCenterZ + DIMS.tableHalfLength - 0.34',
     'c12: decal en el lado del dueño, 34 cm hacia la red'),
    ('DIMS.tableTopY + 0.006', 'c12: decal a 6 mm del tablero'),
    ('r99 · SOBRE la superficie, lado del dueño',
     'c12: _mesaLabelShow documenta la posición nueva'),
    ('r99 · el decal vive PEGADO a la superficie',
     'c12: seguimiento POR FRAME durante el agarre'),
    # r98 heredada e intacta (bocadillo + arrastre + agarre)
    ('r98 · BOCADILLO DEL DUEÑO', 'c12: bocadillo blanco (r98 heredada)'),
    ("c.fillStyle = '#0e1219';", 'c12: texto NEGRO del bocadillo (r98 heredada)'),
    ('this._menuDrag = { hand, id: ns };', 'c12: arrastre de deslizadores (r98 heredada)'),
    ('onSelectEnd(i) {', 'c12: cierre honesto selectend (r98 heredada)'),
    ('_mesaGrabActivo()', 'c12: guard del agarre (r98 heredada)'),
    ('_mesaRay(origin, dir) {', 'c12: rayo de selección (r98 heredada)'),
    ('_mesaGrabUpdate() {', 'c12: agarre 1:1 (r98 heredada)'),
    ('RingGeometry(0.026, 0.044, 28)', 'c12: anillos de selección (r98 heredada)'),
    ("label(T('mesa_alto_grab')", 'c12: pista del gesto en la página MESA (r98 heredada)'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

# las posiciones ANTIGUAS del rótulo y del % NO quedan en el juego
CHK('PlaneGeometry(1.12, 0.28)' not in GH, 'game.html: plano antiguo 1,12×0,28 RETIRADO')
CHK('DIMS.tableTopY + 0.52, 0.92' not in GH, 'game.html: posición flotante antigua RETIRADA')
CHK("c2.font = '800 118px" not in GH, 'game.html: texto 118 px RETIRADO (ahora 96)')
CHK("c.fillText(Math.round(vol * 100) + '%', 512, vy + 27);" not in GH,
    'game.html: % DENTRO de la barra RETIRADO (ahora vy+2)')
CHK(GH.count('DIMS.tableTopY + 0.006') >= 2,
    'game.html: los 6 mm viven en _mesaLabelShow Y en el seguimiento por frame')

# i18n del gesto intacta (r98)
CHK("mesa_alto_grab: 'Agarra la mesa: apunta, mantén el gatillo y muévela arriba/abajo'" in C00,
    'c00 ES: pista del gesto intacta (r98)')
CHK("mesa_alto_grab: 'Grab the table: aim, hold the trigger and move it up or down'" in C00,
    'c00 EN: pista del gesto intacta (r98)')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.91-SDK6', 'c00: VERSION sella 3.6.91-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 93, 'VERSION.json: FASE 93')
CHK(V.get('hub') == 'v3691-sdk6', 'VERSION.json: hub v3691-sdk6')

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

    # ---- 1 · % ENCIMA DE LA BARRA: ámbar sobre el raíl, NADA dentro de él
    pct = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const c = g.menuCanvas.getContext('2d');
      const STRIP = (x, y, w, h) => Array.from(c.getImageData(x, y, w, h).data);
      const ambar = (d) => d.filter((v, i) => i % 4 === 0
        && v > 240 && d[i + 1] > 175 && d[i + 1] < 235 && d[i + 2] < 140).length;
      const blanco = (d) => d.filter((v, i) => i % 4 === 0
        && v > 215 && d[i + 1] > 215 && d[i + 2] > 215).length;
      g.connected = [true, true];
      g.menuOpen = true; g.menuPage = 'optsSonido'; g.menuHover = [-1, -1];
      g.audio.setMusicVol(0.5);
      g.drawMenu();
      const r = g.menuRects.find(x => x.id === 'mvolset');
      const arriba = STRIP(470, r.y - 9, 84, 21);   // franja SOBRE la barra
      const dentro = STRIP(470, r.y + 20, 84, 14);  // interior de la barra
      g.audio.setMusicVol(1);
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return { arriba: ambar(arriba), dentro: blanco(dentro), y: r.y };
    }""")
    if 'err' in (pct or {}):
        CHK(False, '%% barra: %s' % pct.get('err'))
    else:
        CHK(pct['arriba'] > 40, '%% barra: lectura ÁMBAR ENCIMA del raíl (%d px en franja vy−9..vy+12)' % pct['arriba'])
        CHK(pct['dentro'] == 0, '%% barra: CERO tinta de texto DENTRO de la barra (el knob ya no la pisa)')

    # ---- 2 · DECAL: geometría, orientación, posición y pegado por frame
    decal = pg.evaluate("""() => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      g.connected = [true, true];
      const D = (window.__PP_CORE && window.__PP_CORE.DIMS) || g.DIMS;
      const out = {};
      const geo = g._mesaLabel.geometry.parameters;
      out.w = geo.width; out.h = geo.height;
      out.rx = g._mesaLabel.rotation.x;
      // show con la mesa a 0,76: el decal nace SOBRE la superficie
      g.menuOpen = true; g.inHall = true; g.menuPage = 'optsSalaMesa';
      g._salaPreviewUpdate();
      g._mesaAplicarY(0.76);
      g._mesaLabelT = 0;
      g._mesaLabelShow();
      out.px = Math.round(g._mesaLabel.position.x * 1000) / 1000;
      out.py = Math.round(g._mesaLabel.position.y * 1000) / 1000;
      out.pz = Math.round(g._mesaLabel.position.z * 1000) / 1000;
      out.dims = Math.round(D.tableTopY * 1000) / 1000;
      // pegado por FRAME: hundimos el decal a mano y el seguimiento lo
      // recoloca ANTES de tocar la altura (sin cambio de cm → sin repintado)
      g._mesaLabel.position.y = 0.5;
      g._mesaGrab = { hand: 0, y0: g.mesaAltoY, cy0: 1.15 };
      g._mesaCmLast = Math.round(g.mesaAltoY * 100);
      g._menuGripPos = [1.15, null];
      g._mesaGrabUpdate();
      out.glue = Math.round(g._mesaLabel.position.y * 1000) / 1000;
      out.yQuieta = Math.round(g.mesaAltoY * 1000) / 1000;
      // agarre vivo +5 cm: la mesa sube y el decal la acompaña
      g._mesaGrab = { hand: 0, y0: 0.76, cy0: 1.10 };
      g._menuGripPos[0] = 1.15;
      g._mesaGrabUpdate();
      g._mesaGrabUpdate();          // 2.º frame: el pegado roza el valor vivo
      out.y1 = Math.round(g.mesaAltoY * 1000) / 1000;
      out.py1 = Math.round(g._mesaLabel.position.y * 1000) / 1000;
      out.z1 = Math.round(g._mesaLabel.position.z * 1000) / 1000;
      out.persiste = localStorage.getItem('pp_mesaaltoy');
      // soltar + limpieza (r98 heredada)
      g.onSelectEnd(0);
      out.labelT = Math.round((g._mesaLabelT || 0) * 100) / 100;
      g.menuPage = 'optsSala';
      g._mesaGrabCleanup();
      out.limpieza = !g._mesaLabel.visible && g._mesaRings.every(r2 => !r2.visible);
      g._mesaAplicarY(0.76);
      g.menuPage = 'main'; g.drawMenu(); g.menuOpen = false;
      return out;
    }""")
    if 'err' in (decal or {}):
        CHK(False, 'decal: %s' % decal.get('err'))
    else:
        CHK(abs(decal['w'] - 1.04) < 1e-6 and abs(decal['h'] - 0.26) < 1e-6,
            'decal: geometría 1,04×0,26 m (algo más pequeño, era 1,12×0,28)')
        CHK(abs(decal['rx'] + 1.5707963) < 1e-5,
            'decal: plano TUMBADO paralelo a la superficie (rotation.x = −90°)')
        CHK(decal['px'] == 0 and decal['pz'] == -0.57,
            'decal: sobre el LADO DEL DUEÑO, 34 cm hacia la red (x 0 · z −0,57)')
        CHK(abs(decal['py'] - (decal['dims'] + 0.006)) < 1e-6,
            'decal: a 6 mm de la superficie (y %s con tablero %s)' % (decal['py'], decal['dims']))
        CHK(abs(decal['glue'] - 0.766) < 1e-6 and decal['yQuieta'] == 0.76,
            'decal: pegado POR FRAME a la superficie (0,5 hundido → 0,766 sin tocar la altura)')
        CHK(abs(decal['y1'] - 0.81) < 0.0011, 'decal: el agarre 1:1 sigue vivo (0,76→0,81, r98)')
        CHK(abs(decal['py1'] - 0.816) < 0.0011, 'decal: acompaña a la mesa subida (y 0,816)')
        CHK(decal['z1'] == -0.57, 'decal: la z NO cambia con la altura (siempre sobre el tablero)')
        CHK(decal['persiste'] == '0.81', 'decal: persistencia intacta (pp_mesaaltoy=0.81)')
        CHK(decal['labelT'] == 1.0, 'decal: fundido de despedida al soltar (r98)')
        CHK(decal['limpieza'] is True, 'decal: limpieza total fuera de la página MESA (r98)')

    # ---- 3 · páginas del menú sin errores (repintados con el decal nuevo)
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
        CHK(True, 'pageerrors: 0 en toda la sesión (boot + % + decal + repintados)')

srv.shutdown()

print('\n== QA r99 · marcador ==')
print('  OK: %d · FALLO: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys_exit_code = 1
else:
    print('VERDE — r99 completa (% encima de la barra + decal sobre la mesa)')
    sys_exit_code = 0
import sys as _s
_s.exit(sys_exit_code)

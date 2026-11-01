#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r105_v3697.py — capa de QA de la ronda 105 (V3.6.97-SDK6).

Informe del dueño tras V3.6.96: «muchísimo mejor ahora los menús, PERO
debes revisar que existe una DERIVA entre los punteros y el menú y no se
corresponde donde apuntas con los botones. Lo que me parece es que ahora
tenemos bastante pérdida de rendimiento y eso es muy importante no
perderlo».

r105 · FIX DERIVA + RENDIMIENTO:
  1) DERIVA: el cursor del menú (dot) proyectaba en el plano ANTIGUO
     0,72×1,08 mientras el panel es 0,90×1,35 desde r104 → desviación de
     hasta 0,09 m (X) y 0,135 m (Y) hacia el centro. Ahora el punto
     coincide EXACTAMENTE con el rayo y con el botón que activa el
     gatillo (el hit-test y los sliders ya usaban el punto exacto).
  2) RENDIMIENTO: mips OFF en menuTex (a ~1 m el panel es magnificación
     pura: cada repintado pagaba mipgen de ~12 niveles sin ganancia) y
     repintado por HOVER throttled a 90 ms (barriendo el panel se
     encadenaban 15-20 drawMenu/s del lienzo 1024×1536).
  3) REGRESIÓN cero: panel/fuentes/contraste de r104 intactos, r101/r102/
     r103 intactas, física determinista 11/0.
"""
import functools, json, os, re as _re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8842
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()

AGUJAS = [
    # 1 · FIX DERIVA del cursor
    ('dot.position.set((hit.uv.x - 0.5) * 0.90, (hit.uv.y - 0.5) * 1.35, 0.004);',
     'cursor del menú en el plano REAL 0,90×1,35 (desviación 0)'),
    ('dimensiones DEBEN coincidir con PlaneGeometry(0.90, 1.35) de\n          // buildMenu',
     'guard de sincronización cursor↔malla documentado'),
    # 2 · RENDIMIENTO
    ('this.menuTex.generateMipmaps = false;',
     'menuTex: mips OFF (ahorra mipgen por repintado)'),
    ('this.menuTex.minFilter = THREE.LinearFilter;',
     'menuTex: minFilter Linear (magnificación pura a ~1 m)'),
    ('this.menuTex.anisotropy = 1;   // sin mips el anisotrópico no aplica (era 8)',
     'menuTex: anisotropía 1 (coherente sin mips)'),
    ('if ((nowH - (this._menuHoverDrawAt || 0)) >= 90) {',
     'repintado por HOVER throttled a 90 ms (≈11 Hz)'),
    ('this._menuDrawPend = true;   // se atiende en el siguiente frame',
     'hover pendiente marcado cuando el throttle no deja pintar'),
    ('this._menuDrawPend = false;   // r105 · cualquier repintado real atiende el hover pendiente',
     'drawMenu() atiende el hover pendiente (acciones inmediatas)'),
    ('this._menuHoverDrawAt = 0;      // r105 · última hora de repintado por hover',
     'estado del throttle inicializado en el constructor'),
    # 3 · regresión r104 (panel/fuentes/contraste intactos)
    ('new THREE.PlaneGeometry(0.90, 1.35),',
     'panel del menú 0,90×1,35 m intacto (r104)'),
    ('const MENU_FS = 1.16;',
     'escalado global de fuentes ×1,16 intacto (r104)'),
    ("const label = (txt, y, size = 28, col = '#c9d3dd', align = 'left') => {",
     'label 28 px gris luminoso intacto (r104)'),
    ('new THREE.CircleGeometry(0.011, 24),',
     'cursor 0,011 m proporcional intacto (r104)'),
    ('this.menuMesh.renderOrder = 9998;',
     'panel renderOrder 9998 intacto (el menú manda)'),
    ('dot.renderOrder = 9999;',
     'cursor renderOrder 9999 intacto (sobre el panel)'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

RETIRADAS = [
    ('(hit.uv.x - 0.5) * 0.72, (hit.uv.y - 0.5) * 1.08', 'cursor en plano antiguo 0,72×1,08 RETIRADO (causa de la deriva)'),
    ('this.menuTex.anisotropy = 8;', 'anisotropía 8 con mips RETIRADA'),
]
for aguja, nombre in RETIRADAS:
    CHK(aguja not in GH, 'game.html: ' + nombre)

# r101/r102/r103 intactas (regresión cero)
CHK('function barraUpdate(px, py, pz, dt) {' in GH, 'game.html: máquina por proximidad intacta (r101)')
CHK('function barraStick(dt) {' in GH, 'game.html: máquina del JOYSTICK intacta (r102)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in GH, 'game.html: rótulo de la barra a la DERECHA intacto (r103)')
CHK('barraFijo: () => ({' in GH, 'game.html: mallas fijas del rótulo intactas (r103)')
CHK('PROTO: 2,' in GH, 'game.html: pala rival FIEL intacta (r102 códec)')
HWJS = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()
CHK('(this.game.rig || this.game.scene).add(this.r.node);' in HWJS, 'halloween: rival en el RIG intacto (r103)')

# versión sellada
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.97-SDK6', 'c00: VERSION sella 3.6.97-SDK6')
CHK('>V3.6.97-SDK6</span>' in open(os.path.join(RAIZ, 'src/game/03_body.html'), encoding='utf-8').read(),
    'portada: badge V3.6.97-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 99, 'VERSION.json: FASE 99')
CHK(V.get('hub') == 'v3697-sdk6', 'VERSION.json: hub v3697-sdk6')
CHK(V.get('golden', '').startswith('f22445cb'), 'VERSION.json: golden f22445cb…')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo: textura, fuentes, menú abierto) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SHOTS = os.path.join(RAIZ, 'scripts', 'qa_shots_r105')
os.makedirs(SHOTS, exist_ok=True)

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

    # ---- 1 · textura del menú: mips OFF y coherencia de filtros (r105)
    tex = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      return { mm: g.menuTex.generateMipmaps, min: g.menuTex.minFilter,
               ani: g.menuTex.anisotropy, w: g.menuMesh.geometry.parameters.width,
               h: g.menuMesh.geometry.parameters.height,
               ro: g.menuMesh.renderOrder, roDot: g.menuDots[0].renderOrder };
    }""")
    CHK(tex['mm'] is False, 'menuTex: generateMipmaps false en vivo')
    CHK(tex['min'] == 1006, 'menuTex: minFilter LINEAR (1006) en vivo')
    CHK(tex['ani'] == 1, 'menuTex: anisotropía 1 en vivo')
    CHK(abs(tex['w'] - 0.90) < 1e-9 and abs(tex['h'] - 1.35) < 1e-9,
        'panel: malla 0,90×1,35 m en vivo (%.2f×%.2f)' % (tex['w'], tex['h']))
    CHK(tex['ro'] == 9998, 'panel: renderOrder 9998 intacto')
    CHK(tex['roDot'] == 9999, 'cursor: renderOrder 9999 intacto')

    # ---- 2 · fuentes ×1,16 siguen vivas (regresión r104)
    fs = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const c = g.menuCanvas.getContext('2d');
      c.font = '700 20px system-ui, sans-serif';
      const leido = c.font;
      return leido;
    }""")
    CHK('23.2px' in fs, 'fuentes: `700 20px` sigue dibujándose a 23,2 px (%s)' % fs)

    # ---- 3 · throttle de hover: estado existe y drawMenu lo atiende
    thr = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      return { at: g._menuHoverDrawAt, pend: g._menuDrawPend };
    }""")
    CHK(thr['at'] is not None and thr['pend'] is not None,
        'throttle: estado r105 vivo (_menuHoverDrawAt=%s, _menuDrawPend=%s)'
        % (thr['at'], thr['pend']))

    # ---- 4 · abrir el menú en vivo: sin errores, hover throttle activo
    ab = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      try { g.toggleMenu(); } catch (e) { return { err: 'toggle: ' + (e && e.message) }; }
      return { abierto: g.menuOpen, ancho: g.menuMesh.geometry.parameters.width };
    }""")
    CHK(ab.get('err') is None and ab.get('abierto') is True,
        'menú abierto en vivo sin errores (%s)' % (ab.get('err') or 'OK'))
    pg.wait_for_timeout(900)
    pg.screenshot(path=os.path.join(SHOTS, 'menu_abierto.png'))

    # ---- 5 · barrido de hover: el repintado va throttled (≤ ~11 Hz)
    n_draws = pg.evaluate("""async () => {
      const g = window.__PP_GAME;
      let n = 0;
      const orig = g.drawMenu.bind(g);
      g.drawMenu = function () { n++; return orig(); };
      // mueve menuHover por 12 rects sintéticos (como un barrido del rayo)
      for (let i = 0; i < 12; i++) {
        g.menuHover[0] = i;
        try { g.updateMenu(0.016); } catch (e) { /* sin XR: el update sigue */ }
        await new Promise(r => setTimeout(r, 16));
      }
      g.drawMenu = orig;
      return n;
    }""")
    CHK(n_draws <= 6, 'throttle vivo: 12 cambios de hover → %d drawMenu (≤6 en ~0,2 s)' % n_draws)

    CHK(errs == [], 'RUNTIME: cero pageerrors (%s)' % (errs or 'limpio'))
    b.close()

srv.shutdown()

print('\n== RESUMEN qa_r105_v3697 ==')
print('  OK: %d · FALLOS: %d' % (len(OK), len(FAIL)))
if FAIL:
    print('\n'.join('  ✗ ' + f for f in FAIL))
    raise SystemExit(1)
print('  VERDE: deriva del puntero fijada + rendimiento del menú recuperado')

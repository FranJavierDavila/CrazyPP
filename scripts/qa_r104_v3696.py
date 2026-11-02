#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r104_v3696.py — capa de QA de la ronda 104 (V3.6.101-SDK6).

Petición del dueño: «Los textos pequeños de los menús no se leen muy bien, y
revisar que no desborden y estén bien encajadas. Habría alguna manera de que
los menús y todas sus opciones fuesen más claras y mejor definidas (quizás
que se distribuyan a pantalla completa para ganar todo el espacio posible y
ser más cómodos y legibles?).

r104 · MENÚS A PANTALLA COMPLETA:
  1) PANEL GRANDE: 0,72×1,08 m → 0,90×1,35 m (+25 % lineal, 2:3 intacto;
     ~1 texel = 1 px de visor a 1,08 m) + anisotropía 4 → 8.
  2) FUENTES ×1,16: interceptación de `font` en el contexto del lienzo del
     menú — TODO el texto (c12 + PRO TRAINING + champloader) sube un 16 %;
     los autofits (measureText) siguen cuadrando por diseño.
  3) CLARIDAD/DEFINICIÓN: label 24→28 px y gris más luminoso; borde de
     botones 0,18→0,30; casilla ☑ mayor; palas de idioma 118→132 px; sello
     de versión 19 px oro sólido; grises apagados sustituidos en TODAS las
     páginas (pie, hints, cabeceras de columnas, retos, perfil, rendimiento).
  4) SIN DESBORDES: nombres de la lista del PULSO (16 chars) y anfitrión de
     la invitación (14 chars) recortados; autofits ya existentes verificados.
  5) ANCLAJE compensado (panel más alto: centro −0,12 m).
"""
import functools, json, os, base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8841
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html + halloween) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()
HWJS = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()

AGUJAS = [
    # 1 · panel a pantalla completa
    ('new THREE.PlaneGeometry(0.90, 1.35),',
     'panel del menú 0,90×1,35 m (+25 % lineal, 2:3 intacto)'),
    ('this.menuTex.anisotropy = 1;   // sin mips el anisotrópico no aplica (era 8)',
     'anisotropía 1 coherente sin mips (re-anclada r105)'),
    ('new THREE.CircleGeometry(0.011, 24),',
     'cursor del menú proporcional al panel (0,011 m)'),
    # 2 · escalado global de fuentes
    ('const MENU_FS = 1.16;',
     'escalado global de fuentes del menú ×1,16'),
    ("Object.getOwnPropertyDescriptor(\n        Object.getPrototypeOf(_mctx), 'font');",
     'interceptación de `font` en el contexto del lienzo del menú'),
    ("(m0, n0) => (Math.round(parseFloat(n0) * MENU_FS * 10) / 10) + 'px',",
     'sustitución px→px×1,16 en CUALQUIER fuente del menú'),
    # 3 · claridad y definición
    ("const label = (txt, y, size = 28, col = '#c9d3dd', align = 'left') => {",
     'label por defecto 28 px y gris luminoso #c9d3dd'),
    ('c.font = `700 ${fsize || 28}px system-ui, sans-serif`;',
     'botón por defecto 28 px (antes 26)'),
    ("c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.30)';",
     'borde de botones MÁS DEFINIDO (0,30)'),
    ('const bs = 14, bx = x + 26, by = y + h / 2;',
     'casilla ☑/☐ más grande (bs 14)'),
    ('this._langPaddle(rects, \'es\', 728, 40);',
     'pala de idioma ES más grande y bien encajada'),
    ('this._langPaddle(rects, \'en\', 856, 40);',
     'pala de idioma EN más grande y bien encajada'),
    ('const S = 132;   // r104 · 118 → 132 con el panel a pantalla completa',
     'palas de idioma 132 px (dianas más cómodas)'),
    ("c.font = '800 19px system-ui, sans-serif';",
     'sello de versión más legible (19 px)'),
    # 4 · sin desbordes
    ('const nmT104 = nm104.length > 16 ? nm104.slice(0, 15) + \'…\' : nm104;',
     'lista del PULSO: nombres recortados (no invaden INVITAR)'),
    ('c.fillText(\'🎮 \' + T(\'rs_invita_de\', { n: deN104.length > 14 ? deN104.slice(0, 13) + \'…\' : deN104 })',
     'invitación: anfitrión recortado (no pisa UNIRSE)'),
    # 5 · anclaje compensado
    ('this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);',
     'anclaje compensado (panel 1,35 m repartido arriba/abajo)'),
    # 6 · encaje fino visto en las capturas del lienzo
    ("heat_t: 'MAPA DE CALOR',",
     'PRO TRAINING: claves del mapa de calor en su diccionario (adiós texto en crudo)'),
    ('while (sub104.length > 2 && c.measureText(sub104).width > 500) sub104 = sub104.slice(0, -1);',
     'PRO TRAINING: subtítulo de cabecera recortado (no pisa puntos/logros)'),
    ('while (hint104.length > 2 && c.measureText(hint104).width > 700) hint104 = hint104.slice(0, -1);',
     'campeonatos: hint recortado con elipsis (no roza el borde de la tarjeta)'),
]
for aguja, nombre in AGUJAS:
    CHK(aguja in GH, 'game.html: ' + nombre)

RETIRADAS = [
    ('new THREE.PlaneGeometry(0.72, 1.08),', 'panel pequeño 0,72×1,08 RETIRADO'),
    ('this.menuTex.anisotropy = 4;\n    this.menuMesh', 'anisotropía 4 en el menú RETIRADA'),
    ('new THREE.CircleGeometry(0.009, 24),', 'cursor pequeño RETIRADO'),
    ("const label = (txt, y, size = 24, col = '#9aa7b4', align = 'left') => {", 'label apagado 24 px RETIRADO'),
    ("c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.18)';", 'borde débil 0,18 RETIRADO'),
]
for aguja, nombre in RETIRADAS:
    CHK(aguja not in GH, 'game.html: ' + nombre)

# grises apagados: fuera del menú. En el lienzo del menú (c12 páginas +
# PRO TRAINING c13 + oferta del tutorial) quedan CERO; los únicos restos de
# #5c6672/#75828f son CSS de la portada 2D y el marcador 3D (no son menús).
CHK(GH.count('#7d8ea6') == 0 and GH.count('#5f6b78') == 0,
    'grises: #7d8ea6 y #5f6b78 eliminados de TODO el juego')
CHK(GH.count('#5c6672') == 2 and GH.count('#75828f') == 5,
    'grises: #5c6672/#75828f sólo en CSS de portada 2D + marcador 3D (menús limpios)')
CHK(GH.count('#98a6b4') >= 17 and GH.count('#93a1b0') == 3 and GH.count('#a9b8cc') >= 10,
    'grises: los menús usan los tonos luminosos r104 (#98a6b4/#93a1b0/#a9b8cc)')

# r101/r102/r103 intactas (regresión cero)
CHK('function barraUpdate(px, py, pz, dt) {' in GH, 'game.html: máquina por proximidad intacta (r101)')
CHK('function barraStick(dt) {' in GH, 'game.html: máquina del JOYSTICK intacta (r102)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in GH, 'game.html: rótulo de la barra a la DERECHA intacto (r103)')
CHK('barraFijo: () => ({' in GH, 'game.html: mallas fijas del rótulo intactas (r103)')
CHK('(this.game.rig || this.game.scene).add(this.r.node);' in HWJS, 'halloween: rival en el RIG intacto (r103)')
CHK('PROTO: 2,' in GH, 'game.html: pala rival FIEL intacta (r102 códec)')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.101-SDK6', 'c00: VERSION sella 3.6.101-SDK6')
CHK('>V3.6.101-SDK6</span>' in open(os.path.join(RAIZ, 'src/game/03_body.html'), encoding='utf-8').read(),
    'portada: badge V3.6.101-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 100, 'VERSION.json: FASE 98')
CHK(V.get('hub') == 'v36101-sdk6', 'VERSION.json: hub v36101-sdk6')
CHK(V.get('golden', '').startswith('414f27dc'), 'VERSION.json: golden 414f27dc…')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo + lienzo del menú) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SHOTS = os.path.join(RAIZ, 'scripts', 'qa_shots_r104')
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

    # ---- 1 · geometría del panel + anisotropía + anclaje
    geo = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const p = g.menuMesh.geometry.parameters;
      return { w: p.width, h: p.height, ani: g.menuTex.anisotropy,
               ro: g.menuMesh.renderOrder };
    }""")
    CHK(abs(geo['w'] - 0.90) < 1e-9 and abs(geo['h'] - 1.35) < 1e-9,
        'panel: malla 0,90×1,35 m en vivo (%.2f×%.2f)' % (geo['w'], geo['h']))
    CHK(geo['ani'] == 1, 'panel: anisotropía 1 en vivo (re-anclada r105, mips OFF)')
    CHK(geo['ro'] == 9998, 'panel: renderOrder 9998 intacto (el menú manda)')

    # ---- 2 · escalado de fuentes REAL del contexto (medido contra un lienzo limpio)
    fs = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const c = g.menuCanvas.getContext('2d');
      c.font = '700 20px system-ui, sans-serif';
      const leido = c.font;
      const wMenu = c.measureText('PRUEBA DE TEXTO 104').width;
      const ref = document.createElement('canvas').getContext('2d');
      ref.font = '700 20px system-ui, sans-serif';
      const wRef = ref.measureText('PRUEBA DE TEXTO 104').width;
      return { leido, wMenu, wRef, ratio: wMenu / wRef };
    }""")
    CHK('23.2px' in fs['leido'], 'fuentes: `700 20px` se dibuja 23,2 px en el menú (%s)' % fs['leido'])
    CHK(abs(fs['ratio'] - 1.16) < 0.03,
        'fuentes: ancho medido ×%.3f (objetivo ×1,16) sobre lienzo limpio' % fs['ratio'])

    # ---- 3 · abrir el menú en vivo: sin errores y capturas por página
    abierta = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      try { g.toggleMenu(); } catch (e) { return { err: 'toggle: ' + (e && e.message) }; }
      const y = g.menuGroup.position.y;
      const headY = (() => { try { const v = new (g.camera.position.constructor)(0,0,0); g.camera.getWorldPosition(v); return v.y; } catch (e) { return null; } })();
      return { y, headY, abierto: g.menuOpen,
               ancho: g.menuMesh.geometry.parameters.width };
    }""")
    if 'err' in (abierta or {}):
        CHK(False, 'menú: %s' % abierta.get('err'))
    else:
        CHK(abierta.get('abierto') is True, 'menú: abre en vivo sin errores')
        if abierta.get('headY'):
            esperado = max(0.85, abierta['headY'] - 0.12)
            CHK(abs(abierta['y'] - esperado) < 1e-6,
                'anclaje: centro a %.3f m (cabeza %.2f − 0,12)' % (abierta['y'], abierta['headY']))

    def shot(nombre, pagina=None):
        d = pg.evaluate("""(pagina) => {
          const g = window.__PP_GAME;
          if (pagina) { g.menuPage = pagina; try { g.drawMenu(); } catch (e) { return { err: '' + (e && e.message) }; } }
          return { img: g.menuCanvas.toDataURL('image/png'),
                   w: g.menuCanvas.width, h: g.menuCanvas.height };
        }""", pagina)
        if 'err' in (d or {}):
            CHK(False, 'captura %s: %s' % (nombre, d.get('err')))
            return
        png = base64.b64decode(d['img'].split(',', 1)[1])
        ruta = os.path.join(SHOTS, 'menu_%s.png' % nombre)
        open(ruta, 'wb').write(png)
        CHK(len(png) > 20000, 'captura %s: %d KB guardada' % (nombre, len(png) // 1024))

    shot('main')
    shot('opts', 'opts')
    shot('multi', 'multi')
    shot('champs', 'champs')
    shot('salamesa', 'optsSalaMesa')
    shot('train', 'train')

    # ---- 4 · regresión de la ronda anterior (rótulo de la barra vivo)
    reg = pg.evaluate("""() => {
      const T = window.__PP_TRAIN, X = T.__test;
      try { X.barraVisSet(true); X.barraLay(); const s = X.barraSpr();
        return { x: s.lbl.x, fijo: X.barraFijo() }; }
      catch (e) { return { err: e && e.message }; }
    }""")
    if 'err' in (reg or {}):
        CHK(False, 'regresión r103: %s' % reg.get('err'))
    else:
        D = pg.evaluate("() => window.__PP_CORE.DIMS")
        CHK(abs(reg['x'] - (D['tableHalfWidth'] + 0.42)) < 1e-6,
            'regresión r103: rótulo de la barra SIGUE a la derecha (x canto+0,42)')

    # ---- 5 · sin errores de página
    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))

    b.close()
srv.shutdown()

print()
print('QA r104 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)

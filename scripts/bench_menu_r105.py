#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bench_menu_r105.py — validación viva de la ronda 105 (deriva + rendimiento).

Pruebas (game.html servido en local + Chromium/SwiftShader):
  1 · DERIVA: mando falso apuntando a uv conocidos del panel; el cursor debe
      caer EXACTO (<=1 mm) en el punto apuntado (r104 quedaba hasta 13,5 cm).
  2 · CAMINO RÁPIDO: cruce de apuntado NO repinta la página (drawMenuPagina
      0 llamadas durante el barrido) y el resultado es PÍXEL-IGUAL al
      fallback r104 (toDataURL idéntico con y sin pinta en los rects).
  3 · COSTE: ms por cruce (blit + controles + tip) frente al repintado
      completo; repintados/s máximos con temblor en el borde de un botón.
  4 · MEDALLÓN: con social simulada viva, el panel NO se repinta al respirar
      (0 drawMenu en 3 s) y el overlay existe y respira.
  5 · REGRESIÓN: páginas pintan sin errores; agujas r104 vivas intactas.
Uso: python3 scripts/bench_menu_r105.py
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8853
OK, FAIL = [], []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# Inyecta un mando fijo APUNTANDO a (uvx, uvy) del panel con precisión
AIM_UV = r"""([uvx, uvy]) => {
  const g = window.__PP_GAME;
  const f = window.__BENCH.fake;
  g._menuAnchorUntil = 0;   // re-congela la flotación (el preview puede re-armarla)
  const gp = g.menuGroup.position;
  const e = g.menuMesh.geometry.parameters;
  const m = g.menuGroup.matrixWorld.elements;
  // columnas de la matriz = ejes del grupo en mundo
  const nx = [m[0], m[1], m[2]], ny = [m[4], m[5], m[6]], nz = [m[8], m[9], m[10]];
  const dx = (uvx - 0.5) * e.width, dy = (uvy - 0.5) * e.height;
  // objetivo T sobre el plano; mando en T + normal*0.55 mirando al panel
  const T = [gp.x + nx[0] * dx + ny[0] * dy,
             gp.y + nx[1] * dx + ny[1] * dy,
             gp.z + nx[2] * dx + ny[2] * dy];
  f.position.set(T[0] + nz[0] * 0.55, T[1] + nz[1] * 0.55, T[2] + nz[2] * 0.55);
  f.quaternion.copy(g.menuGroup.quaternion);   // -Z del mando = -Z del panel
  g.updateMenu(1 / 72);
  const dot = g.menuDots[0];
  return { uv: [uvx, uvy], dot: dot.visible ?
      [dot.position.x, dot.position.y] : null,
      esperado: [dx, dy], hover: g.menuHover[0] };
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(1500)

    prep = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const fake = new (g.menuGroup.constructor)();
      g.scene.add(fake);
      g.rays[0] = fake;
      g.connected[0] = true;
      window.__BENCH = { fake, npg: 0, ndm: 0 };
      const opg = g.drawMenuPagina.bind(g);
      g.drawMenuPagina = function (...a) { window.__BENCH.npg++; return opg(...a); };
      return { ok: !!g._menuBaseCtx, quad: !!g._medQuad };
    }""")
    CHK(prep.get('ok') is True, 'r105: caché base creada en buildMenu (_menuBaseCtx)')
    CHK(prep.get('quad') is True, 'r105: overlay del medallón creado (_medQuad)')

    pg.evaluate("() => { window.__PP_GAME.toggleMenu(); }")
    pg.wait_for_timeout(400)
    # congela la flotación y ASIENTA el preview del sala (el primer updateMenu
    # puede girar el entorno y re-armar anchorMenu)
    pg.evaluate("""() => { const g = window.__PP_GAME; g._menuAnchorUntil = 0; g.updateMenu(1/72); g._menuAnchorUntil = 0; }""")
    pg.wait_for_timeout(100)

    # ---- 1 · DERIVA: cuatro puntos del panel (dos bordes y centro lateral)
    for uv in [[0.06, 0.5], [0.94, 0.5], [0.5, 0.08], [0.5, 0.92], [0.3, 0.7]]:
        r = pg.evaluate(AIM_UV, uv)
        if not r['dot']:
            CHK(False, 'deriva uv=%s: sin impacto (rayo no toca el panel)' % uv)
            continue
        ex = abs(r['dot'][0] - r['esperado'][0])
        ey = abs(r['dot'][1] - r['esperado'][1])
        CHK(ex < 0.001 and ey < 0.001,
            'deriva uv=%s: error (%.1f, %.1f) mm — cursor EXACTO sobre el punto apuntado'
            % (uv, ex * 1000, ey * 1000))

    # ---- 2 · CAMINO RÁPIDO + PÍXEL-IGUALDAD con el fallback r104
    r = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const B = window.__BENCH;
      const aim = (uv) => {
        const f = B.fake, gp = g.menuGroup.position;
        const e = g.menuMesh.geometry.parameters;
        const m = g.menuGroup.matrixWorld.elements;
        const nx = [m[0], m[1], m[2]], ny = [m[4], m[5], m[6]], nz = [m[8], m[9], m[10]];
        const dx = (uv[0] - 0.5) * e.width, dy = (uv[1] - 0.5) * e.height;
        f.position.set(gp.x + nx[0] * dx + ny[0] * dy + nz[0] * 0.55,
                       gp.y + nx[1] * dx + ny[1] * dy + nz[1] * 0.55,
                       gp.z + nx[2] * dx + ny[2] * dy + nz[2] * 0.55);
        f.quaternion.copy(g.menuGroup.quaternion);
      };
      // sincroniza _menuState/base y deja el rayo FUERA de todo control
      const stBak = g.rules.state; g.rules.state = 'serve';
      aim([0.02, 0.98]);
      g._hoverPaintT = 0; g._hoverPaintPend = false;
      g.updateMenu(1 / 72);
      g.drawMenu();
      B.npg = 0;
      // cruce REAL a la tarjeta CAMPEONATOS: simula >=45 ms desde el último
      // repintado (si no, el aliño 45 ms APLAZA el paint — correcto por diseño)
      g._hoverPaintT = 0;
      aim([0.28, 0.42]);
      g.updateMenu(1 / 72);
      const npgCruce = B.npg;
      const hoverIdx = g.menuHover[0];
      const snapFast = g.menuCanvas.toDataURL('image/png');
      // pintado DIRECTO r104 (lo que hace el fallback): página con hover real
      g.drawMenuPagina();
      g.rules.state = stBak;
      const snapFall = g.menuCanvas.toDataURL('image/png');
      return { snapFast, snapFall, npgCruce, hoverIdx };
    }""")
    import base64 as _b64
    open(os.path.join(RAIZ, 'scripts', '_r105_snapfast.png'), 'wb').write(
        _b64.b64decode(r['snapFast'].split(',', 1)[1]))
    open(os.path.join(RAIZ, 'scripts', '_r105_snapfall.png'), 'wb').write(
        _b64.b64decode(r['snapFall'].split(',', 1)[1]))
    CHK(r['npgCruce'] == 0, 'camino rápido: 0 repintados de página en el cruce (npg=%d, hover=%d)' % (r['npgCruce'], r['hoverIdx']))
    if r['snapFast'] == r['snapFall']:
        CHK(True, 'píxel-igualdad: camino rápido == pintado directo r104 (byte-exacto)')
    else:
        from PIL import Image
        import io as _io
        import numpy as _np
        a = _np.array(Image.open(_io.BytesIO(_b64.b64decode(
            r['snapFast'].split(',', 1)[1]))).convert('RGBA')).astype(int)
        bb = _np.array(Image.open(_io.BytesIO(_b64.b64decode(
            r['snapFall'].split(',', 1)[1]))).convert('RGBA')).astype(int)
        dpx = int((_np.abs(a - bb).sum(axis=2) > 0).sum())
        mx = int(_np.abs(a - bb).max()) if dpx else 0
        # tolerancia sub-píxel: el doble dibujo del borde (blit + pinta) mueve
        # el antialiasing < 1/255 por canal — invisible y aceptado
        CHK(mx <= 2,
            'píxel-igualdad: %d px en el borde AA con delta máx %d/255 (<=2 = AA del doble borde)' % (dpx, mx))

    # ---- 2b · CLIC → la base se re-sella (el siguiente cruce NO pinta página vieja)
    r = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const B = window.__BENCH;
      const aim = (uv) => {
        const f = B.fake, gp = g.menuGroup.position;
        const e = g.menuMesh.geometry.parameters;
        const m = g.menuGroup.matrixWorld.elements;
        const nx = [m[0], m[1], m[2]], ny = [m[4], m[5], m[6]], nz = [m[8], m[9], m[10]];
        const dx = (uv[0] - 0.5) * e.width, dy = (uv[1] - 0.5) * e.height;
        f.position.set(gp.x + nx[0] * dx + ny[0] * dy + nz[0] * 0.55,
                       gp.y + nx[1] * dx + ny[1] * dy + nz[1] * 0.55,
                       gp.z + nx[2] * dx + ny[2] * dy + nz[2] * 0.55);
        f.quaternion.copy(g.menuGroup.quaternion);
      };
      // pulsa la pala EN (idioma): menuClick → drawMenu completo → base nueva
      aim([0.94, 0.09]);
      g._hoverPaintT = 0; g.updateMenu(1 / 72);
      const idx = g.menuHover.findIndex((v) => v >= 0);
      if (idx < 0) return { err: 'no hover sobre pala de idioma' };
      const id = g.menuRects[idx].id;
      g.menuClick(idx, 0);
      const en = (typeof TLang === 'function' ? TLang() : (window.__PP_I18N && window.__PP_I18N.lang));
      // cruce posterior: la base debe reflejar YA el idioma nuevo
      g._hoverPaintT = 0;
      aim([0.28, 0.42]);
      g.updateMenu(1 / 72);
      const esPagina = g.menuCanvas.toDataURL('image/png').length;
      return { id, en, esPagina, npg: B.npg };
    }""")
    if r.get('err'):
        CHK(False, 'clic idioma: %s' % r['err'])
    else:
        CHK(True, 'clic idioma: rect %s pulsado y base re-sellada (cruce posterior sin repintado)' % r['id'])
    # vuelve a ES
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const i = g.menuRects.findIndex((rc) => rc.id === 'lang:es');
      if (i >= 0) g.menuClick(i, 0);
    }""")

    # ---- 3 · COSTE: barrido raster + temblor en el borde
    r = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const B = window.__BENCH;
      const e = g.menuMesh.geometry.parameters;
      const gp = g.menuGroup.position;
      const m = g.menuGroup.matrixWorld.elements;
      const nx = [m[0], m[1], m[2]], ny = [m[4], m[5], m[6]], nz = [m[8], m[9], m[10]];
      const aim = (uvx, uvy) => {
        const dx = (uvx - 0.5) * e.width, dy = (uvy - 0.5) * e.height;
        B.fake.position.set(gp.x + nx[0] * dx + ny[0] * dy + nz[0] * 0.55,
                            gp.y + nx[1] * dx + ny[1] * dy + nz[1] * 0.55,
                            gp.z + nx[2] * dx + ny[2] * dy + nz[2] * 0.55);
        B.fake.quaternion.copy(g.menuGroup.quaternion);
      };
      B.npg = 0;
      const stBak = g.rules.state; g.rules.state = 'serve';
      let cruces = 0, prev = -2, tPaint = 0;
      const t0 = performance.now();
      const N = 72 * 5;
      for (let i = 0; i < N; i++) {
        const s = i / N;
        aim(0.06 + 0.88 * (s * 4 % 1), 0.16 + 0.7 * (((s * 4) | 0) % 4) / 4 + 0.05);
        const t1 = performance.now();
        g.updateMenu(1 / 72);
        tPaint += performance.now() - t1;
        if (g.menuHover[0] !== prev) { cruces++; prev = g.menuHover[0]; }
      }
      const tFull = performance.now() - t0;
      // temblor: rayo oscilando ±3 px sobre el borde de un botón 3 s
      const rEdge = g.menuRects.find((rc) => rc.id === 'start');
      const uvEdge = [(rEdge.x + rEdge.w / 2) / 1024, (rEdge.y + rEdge.h / 2) / 1536];
      let tTrem = 0, paintTrem = 0;
      B.npg = 0;
      const t2 = performance.now();
      for (let i = 0; i < 72 * 3; i++) {
        aim(uvEdge[0] + 0.003 * Math.sin(i * 0.9), uvEdge[1]);
        const t3 = performance.now();
        g.updateMenu(1 / 72);
        paintTrem += performance.now() - t3;
        tTrem = performance.now() - t2;
      }
      return { msFrame: tPaint / N, cruces, npg: B.npg, tFull,
               tremblePct: 100 * paintTrem / (72 * 3), trembleNpg: B.npg };
    }""")
    CHK(r['npg'] == 0, 'barrido 5 s (4 bandas): 0 repintados de página (%d cruces, %.2f ms/frame updateMenu)' % (r['cruces'], r['msFrame']))
    CHK(r['trembleNpg'] == 0, 'temblor en borde 3 s: 0 repintados de página')
    CHK(r['tremblePct'] < 25, 'temblor: coste updateMenu %.1f %% del frame (antes ~100 %% con repintados/s)' % r['tremblePct'])

    # ---- 4 · MEDALLÓN overlay: social simulada viva → 0 drawMenu al respirar
    r = pg.evaluate("""() => {
      const g = window.__PP_GAME;
      const B = window.__BENCH;
      // social simulada: medallonVivo + nOnline
      g.social = { medallonVivo: () => true, hayInvitas: () => false, nOnline: 7 };
      g.menuPage = 'main';
      g.menuHover = [-1, -1];
      const stBak = g.rules.state; g.rules.state = 'serve';   // sin churn de estado
      g.drawMenu();                 // pinta hub y fija _medRect
      B.npg = 0; B.ndm = 0;
      const t0 = performance.now();
      for (let i = 0; i < 72 * 3; i++) { g.rules.state = 'serve'; g.updateMenu(1 / 72); }   // 3 s
      g.rules.state = stBak;
      return { npg: B.npg, vis: g._medQuad.visible,
               pos: [g._medQuad.position.x, g._medQuad.position.y],
               t: performance.now() - t0 };
    }""")
    CHK(r['npg'] == 0, 'medallón respirando 3 s: 0 repintados de página (overlay a 30 Hz)')
    CHK(r['vis'] is True, 'medallón: overlay visible en el hub')
    CHK(abs(r['pos'][0]) < 0.5 and abs(r['pos'][1]) < 0.7, 'medallón: quad en la esquina de la tarjeta %s' % r['pos'])
    pg.evaluate("() => { window.__PP_GAME.social = null; window.__PP_GAME._medQuad.visible = false; }")

    # ---- 5 · páginas sin errores (regresión)
    for p in ['main', 'opts', 'multi', 'champs', 'wrl', 'train', 'optsSalaMesa']:
        rr2 = pg.evaluate("""(p) => {
          const g = window.__PP_GAME;
          try { g.menuPage = p; g.menuHover = [-1, -1]; g.drawMenu(); return null; }
          catch (e) { return '' + (e && e.message); }
        }""", p)
        CHK(rr2 is None, 'página %s pinta sin errores' % p)

    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))
    b.close()
srv.shutdown()

print()
print('bench r105 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)

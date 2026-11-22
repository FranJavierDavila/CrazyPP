#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r96_diag.py — sonda rápida de la r96 (V3.6.88): arranque vivo + las
palancas nuevas (deslizador MESA, tinte por campeonato, vista de sala,
FFR) antes de la capa de QA completa."""
import functools, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8831

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
    pg.wait_for_timeout(3000)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2500)

    out = pg.evaluate("""async () => {
      const g = window.__PP_GAME; if (!g) return { err: 'sin juego' };
      const r = {};
      // 1 · deslizador de altura
      const top0 = g.tableGroup.getObjectByName('ppTableTop').position.y;
      const y1 = g._mesaAplicarY(0.82);
      r.y1 = y1;
      r.top1 = g.tableGroup.getObjectByName('ppTableTop').position.y;
      r.dims = (window.__PP_DIMS_READ ? window.__PP_DIMS_READ() : null) || { topY: g.tableGroup.getObjectByName('ppTableTop').position.y };
      r.ls = localStorage.getItem('pp_mesaaltoy');
      r.mesaAlto = g.mesaAlto;
      g._mesaAplicarY(0.76);
      r.topBack = g.tableGroup.getObjectByName('ppTableTop').position.y;
      // 2 · tinte con campeonato simulado
      g._mesaTinte({ top: 0x1c6b47, edge: 0x125033, id: 'verde' });
      r.skinLibre = g.tableGroup.getObjectByName('ppTableTop').material.color.getHexString();
      g.champs = g.champs || {};
      const realActive = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(g.champs), 'active');
      // simular activo: parchear el getter es delicado; usar _mesaNativo directo
      g._mesaSkinReapply();
      r.skinReapply = g.tableGroup.getObjectByName('ppTableTop').material.color.getHexString();
      r.skinId = g.mesaSkin;
      // 3 · vista de sala
      r.inHall0 = g.inHall;
      g.menuOpen = true; g.menuPage = 'optsSala';
      g._salaPreviewUpdate();
      r.prevOn = !!g._salaPreview;
      r.rigZ = +g.rig.position.z.toFixed(2);
      r.roomVis = g.roomGroup ? g.roomGroup.visible : null;
      g.menuPage = 'main';
      g._salaPreviewUpdate();
      r.prevOff = !!g._salaPreview;
      r.rigZBack = +g.rig.position.z.toFixed(2);
      r.hallVis = g.hallGroup ? g.hallGroup.visible : null;
      g.menuOpen = false;
      // 4 · FFR
      if (g.perf) {
        g.perf.setFfr('max');
        r.foveaMax0 = g.perf.fovea;
        g.perf.setFfr('rinde');
        r.foveaCap = g.perf.foveaMax();
        g.perf.setFfr('def');
        r.foveaDef = g.perf.foveaMax();
        r.ffrLabel = g.perf.ffrLabel();
      }
      // 5 · tooltips: resolver claves
      r.tip1 = g._menuTipKey('theme:neon');
      r.tip2 = g._menuTipKey('mesa_altoy');
      r.tip3 = g._menuTipKey('start');
      r.tip4 = g._menuTipKey('nope');
      // 6 · menú pinta la página sala sin romper
      g.menuOpen = true; g.menuPage = 'optsSala'; g.drawMenu();
      r.rectsSala = g.menuRects.length;
      const idsSala = g.menuRects.map(x => x.id);
      r.salaIds = idsSala.slice(0, 6);
      g.menuPage = 'optsSalaMesa'; g.drawMenu();
      r.rectsMesa = g.menuRects.length;
      r.mesaIds = g.menuRects.map(x => x.id).filter(i => String(i).indexOf('mesa_alto') === 0);
      g.menuPage = 'optsSonido'; g.drawMenu();
      r.sonidoIds = g.menuRects.map(x => x.id).filter(i => String(i).indexOf('volset') >= 0);
      g.menuOpen = false; g.menuPage = 'main';
      return r;
    }""")
    print('RESULTADO:', out)
    print('PAGEERRORS:', errs if errs else '0')
    b.close()
srv.shutdown()

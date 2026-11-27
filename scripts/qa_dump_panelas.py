#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_dump_panelas · dump de números duros: lienzo, panelas de CONFIG vs
panelas MONTADAS en 'perfil'/'perfil_edit'/'main', y quién llama _menuArco
con qué ids. Para cazar el desalineado painter↔panela del dueño."""
import os, threading

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3011

JS = r'''() => {
  const g = window.__game;
  const CM = g._menuPanelas && g._menuPanelas.length ?
    g._menuPanelas[0].userData.panela : null;
  const dump = {
    lienzo: { w: g.menuCanvas.width, h: g.menuCanvas.height },
    page: g.menuPage,
    montadas: (g._menuPanelas || []).map((m) => {
      const pa = m.userData.panela;
      return { id: pa.id, x: pa.x, w: pa.w, dist: pa.dist,
        anchoM: Math.round(pa.anchoM * 100) / 100 };
    }),
    lados: g._menuLados || null,
    menuMap: g._menuMap,
    conchaPintada: !!g._menuConchaPintada,
    cvW: g.menuMesh ? g.menuMesh.userData.cv.width : null,
    rectsPerfil: (g.menuRects || []).filter(Boolean).map((r) =>
      ({ id: r.id, x: Math.round(r.x), y: Math.round(r.y),
         w: Math.round(r.w), h: Math.round(r.h) })),
  };
  return dump;
}'''


def serve():
    import http.server
    os.chdir(PUBLIC)
    handler = http.server.SimpleHTTPRequestHandler

    class H(handler):
        def log_message(self, *a):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    import json
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.goto('http://127.0.0.1:3011/game.html', wait_until='load',
                timeout=60_000)
        for _ in range(60):
            if pg.evaluate('() => !!window.__game'):
                break
            pg.wait_for_timeout(1_000)
        pg.wait_for_timeout(5_000)
        pg.evaluate('() => { const g = window.__game; g.menuOpen = true;'
                    '  g.menuPage = "main"; }')
        pg.wait_for_timeout(1_000)
        print('== MAIN ==')
        print(json.dumps(pg.evaluate(JS), indent=1, ensure_ascii=False))
        pg.evaluate('() => { const g = window.__game;'
                    '  g.menuPage = "perfil"; g.drawMenu(); }')
        pg.wait_for_timeout(1_000)
        print('== PERFIL ==')
        print(json.dumps(pg.evaluate(JS), indent=1, ensure_ascii=False))
        b.close()


if __name__ == '__main__':
    main()

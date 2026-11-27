#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_hittest_menu · REPLICA el hit-test EXACTO del mando VR
(c12:7008-7012: px = paHit.x + uv.x*paHit.w · py = (1-uv.y)*lienzo.alto ·
findIndex PRIMERA coincidencia) sobre TODOS los rects de cada página del
menú y lista los botones CUYO PRIMER-MATCH NO ES ELLOS (muertos para el
dueño: «botones cosméticos») + qué rect los tapa. Sirve public/ en :3009."""
import os, sys, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3009

JS = r'''(pages) => {
  const g = window.__game;
  const out = {};
  const alto = g.menuCanvas.height;
  const panelas = (g._menuPanelas || []).map((m) => m.userData.panela)
    .filter(Boolean);
  for (const pid of pages) {
    g.menuOpen = true;
    g.menuPage = pid;
    delete g._peTab;
    g.drawMenu();
    const rects = (g.menuRects || []).filter(Boolean);
    const hit = (px, py) => rects.findIndex((r) =>
      px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h);
    const filas = [];
    for (let i = 0; i < rects.length; i++) {
      const r = rects[i];
      const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
      // (a) coherencia interna: ¿el centro del rect i cae primero en otro?
      const j = hit(cx, cy);
      // (b) fórmula VR: ¿alguna panela puede producir este centro?
      let vrIdx = -1, paUsed = null;
      for (const pa of panelas) {
        if (cx < pa.x || cx > pa.x + pa.w) continue;
        const uvx = (cx - pa.x) / pa.w;
        const uvy = 1 - cy / alto;
        const px2 = pa.x + uvx * pa.w;       // == cx por construcción
        const py2 = (1 - uvy) * alto;        // == cy por construcción
        vrIdx = hit(px2, py2); paUsed = pa; break;
      }
      const muerto = (j !== i) || (vrIdx !== i && vrIdx !== -1);
      if (muerto) filas.push({
        id: r.id, idx: i, centro: [Math.round(cx), Math.round(cy)],
        tapadoPor: (j >= 0 && j !== i) ? { id: rects[j].id, idx: j } : null,
        vrHit: (vrIdx >= 0 && vrIdx !== i) ? { id: rects[vrIdx].id, idx: vrIdx } : null,
        panela: paUsed ? paUsed.id || paUsed.x : null,
      });
    }
    out[pid] = { total: rects.length, muertos: filas };
  }
  return out;
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
    from playwright.sync_api import sync_playwright
    pages = ['main', 'perfil', 'perfil_edit', 'opts', 'optsSala',
             'optsSalaMesa', 'wrl', 'champs']
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load',
                timeout=60_000)
        for _ in range(60):
            if pg.evaluate('() => !!window.__game'):
                break
            pg.wait_for_timeout(1_000)
        pg.wait_for_timeout(4_000)
        res = pg.evaluate(JS, pages)
        b.close()

    total_m = 0
    for pid, info in res.items():
        muertos = info['muertos']
        total_m += len(muertos)
        print(f"--- {pid}: {info['total']} rects, {len(muertos)} muertos")
        for m in muertos[:12]:
            print('   ✗', json.dumps(m, ensure_ascii=False))
    print(f"\nTOTAL botones muertos en hit-test: {total_m}")
    sys.exit(1 if total_m else 0)


if __name__ == '__main__':
    main()

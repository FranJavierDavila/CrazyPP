#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_hittest_vivo · mide menuRects TAL COMO LOS DEJA EL BUCLE REAL de rAF
(no drawMenu manual) tras navegar con menuClick REAL (por índice) y replica
el hit-test VR exacto sobre el array VIVO. Caza rects fantasma que empujan
capas de runtime (avisos, cortinas, conchas) y tapan botones por
primera-coincidencia — el síntoma «botones cosméticos» del dueño."""
import os, sys, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3010

JS_MEASURE = r'''() => {
  const g = window.__game;
  const alto = g.menuCanvas.height;
  const panelas = (g._menuPanelas || []).map((m) => m.userData.panela)
    .filter(Boolean);
  const rects = (g.menuRects || []).filter(Boolean);
  const hit = (px, py) => rects.findIndex((r) =>
    px >= r.x && px <= r.x + r.w && py >= r.y && py <= r.y + r.h);
  const muertos = [];
  for (let i = 0; i < rects.length; i++) {
    const r = rects[i];
    const cx = Math.round(r.x + r.w / 2), cy = Math.round(r.y + r.h / 2);
    const j = hit(cx, cy);
    // ¿el centro cae dentro de ALGUNA panela montada? (si no, inalcanzable VR)
    let enPanela = false;
    for (const pa of panelas) {
      if (cx >= pa.x && cx <= pa.x + pa.w) { enPanela = true; break; }
    }
    if (j !== i || !enPanela) muertos.push({
      id: r.id, idx: i, centro: [cx, cy],
      tapadoPor: (j >= 0 && j !== i) ? { id: rects[j].id, idx: j } : null,
      enPanela,
    });
  }
  return { page: g.menuPage, total: rects.length,
    ids: rects.map((r) => r.id), panelas: panelas.map((p) => p.id || p.x),
    muertos };
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
    fails = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load',
                timeout=60_000)
        for _ in range(60):
            if pg.evaluate('() => !!window.__game'):
                break
            pg.wait_for_timeout(1_000)
        pg.wait_for_timeout(5_000)
        # abrir el menú y DEJAR QUE EL BUCLE VIVO repinte varios frames
        pg.evaluate('() => { const g = window.__game; g.menuOpen = true;'
                    '  g.menuPage = "main"; }')
        pg.wait_for_timeout(1_200)

        def measure():
            return pg.evaluate(JS_MEASURE)

        def click_idx(i):
            pg.evaluate('(i) => window.__game.menuClick(i, null)', i)
            pg.wait_for_timeout(1_000)

        # 1 · MAIN vivo
        m = measure()
        print(f"MAIN vivo: {m['total']} rects, panelas {m['panelas']}, "
              f"muertos {len(m['muertos'])}")
        for d in m['muertos']:
            print('   ✗', json.dumps(d, ensure_ascii=False))
        if m['muertos']:
            fails.append('main vivo: rects muertos')

        # 2 · navegar MI PERFIL por el índice REAL del hit-test
        try:
            i_perfil = m['ids'].index('page:perfil')
        except ValueError:
            i_perfil = -1
        if i_perfil < 0:
            fails.append('main vivo: no existe page:perfil')
        else:
            click_idx(i_perfil)
            m = measure()
            print(f"PERFIL vivo: page={m['page']} {m['total']} rects, "
                  f"panelas {m['panelas']}, muertos {len(m['muertos'])}")
            for d in m['muertos']:
                print('   ✗', json.dumps(d, ensure_ascii=False))
            if m['muertos']:
                fails.append('perfil vivo: rects muertos')

            # 3 · EDITAR por índice real + medir el editor VIVO
            try:
                i_ed = m['ids'].index('page:perfil_edit')
            except ValueError:
                i_ed = -1
            if i_ed < 0:
                fails.append(f"perfil vivo (page={m['page']}): sin "
                             "page:perfil_edit — ids: " + ','.join(m['ids']))
            else:
                click_idx(i_ed)
                m = measure()
                print(f"EDITOR vivo: page={m['page']} {m['total']} rects, "
                      f"panelas {m['panelas']}, muertos {len(m['muertos'])}")
                for d in m['muertos']:
                    print('   ✗', json.dumps(d, ensure_ascii=False))
                if m['muertos']:
                    fails.append('editor vivo: rects muertos')
                # 4 · pestaña PAÍS viva
                try:
                    i_pa = m['ids'].index('petab:pais')
                except ValueError:
                    i_pa = -1
                if i_pa < 0:
                    fails.append('editor vivo: sin petab:pais')
                else:
                    click_idx(i_pa)
                    m = measure()
                    np = len([x for x in m['ids']
                              if x.startswith('ppais:')])
                    print(f"PAÍS vivo: {m['total']} rects, {np} banderas, "
                          f"muertos {len(m['muertos'])}")
                    for d in m['muertos'][:10]:
                        print('   ✗', json.dumps(d, ensure_ascii=False))
                    if m['muertos']:
                        fails.append('país vivo: rects muertos')
        # 5 · GUARDIA: JUGAR (supervivencia incluida) y RANKING (wrl) vivos
        pg.evaluate('() => { const g = window.__game;'
                    '  g.menuPage = "jugar"; g.drawMenu(); }')
        pg.wait_for_timeout(1_000)
        m = measure()
        print(f"JUGAR vivo: {m['total']} rects, panelas {m['panelas']}, "
              f"muertos {len(m['muertos'])}, "
              f"survigo={'survgo' in m['ids']}")
        for d in m['muertos'][:8]:
            print('   ✗', json.dumps(d, ensure_ascii=False))
        if m['muertos'] or 'survgo' not in m['ids']:
            fails.append('jugar vivo: muertos o sin survgo')
        pg.evaluate('() => { const g = window.__game;'
                    '  g.menuPage = "wrl"; g.drawMenu(); }')
        pg.wait_for_timeout(1_000)
        m = measure()
        print(f"WRL vivo: {m['total']} rects, panelas {m['panelas']}, "
              f"muertos {len(m['muertos'])}")
        for d in m['muertos'][:8]:
            print('   ✗', json.dumps(d, ensure_ascii=False))
        if m['muertos']:
            fails.append('wrl vivo: rects muertos')
        b.close()

    print('\n== RESULTADO ==')
    if fails:
        for f in fails:
            print(' ✗ ' + f)
        sys.exit(1)
    print(' hit-test vivo limpio en todas las páginas navegadas')


if __name__ == '__main__':
    main()

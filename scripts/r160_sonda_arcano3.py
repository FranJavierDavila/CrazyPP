#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r160 · sonda v3 del ARCANO: (A) flujo real con esperas largas — ¿el buffer
carga y la pista del arcano SONA?; (B) menú abierto/cerrado dentro de la sala
— ¿sobrevive la melodía?; (C) pp_hallmus=1 — ¿se reproduce el silencio del
dueño?; (D) URLs de los 404."""
import os, threading, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3014


def serve():
    import http.server
    os.chdir(PUBLIC)
    handler = http.server.SimpleHTTPRequestHandler

    class H(handler):
        def log_message(self, *a):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


SNAP = r'''() => {
  const a = window.__game.audio, g = window.__game;
  return { hallWanted: a.hallWanted, hallUrl: a._hallUrl,
           hallPlaying: !!a.hallPlaying, hallMute: !!a.hallMute,
           bufs: Object.keys(a._hallBufs || {}),
           loading: a._hallLoading || null,
           arconoOn: !!g._arconoOn, menuOpen: !!g.menuOpen,
           fadeDir: g._arconoFadeDir };
}'''

ESPERA_ARCOANO = r'''async (topeMs) => {
  const g = window.__game, a = window.__game.audio;
  const t0 = performance.now();
  while (performance.now() - t0 < topeMs) {
    if (g._arconoOn && (a.hallPlaying || !a._hallLoading)) break;
    await new Promise(r => requestAnimationFrame(r));
  }
  return performance.now() - t0;
}'''


def flujo(pg, etiqueta, con_menu_dentro):
    print(f'--- {etiqueta} ---')
    print('S0 salón :', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
    pg.evaluate('() => window.__game._arconoEntrar()')
    esperado = pg.evaluate(ESPERA_ARCOANO, 12000)
    print(f'  (espera sala montada: {esperado:.0f} ms)')
    print('S1 arcano:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
    if con_menu_dentro:
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(700)
        print('S2 menú  :', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(900)
        print('S3 cerrar:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
    # salir limpia
    pg.evaluate('() => window.__game._arconoSalir()')
    pg.wait_for_timeout(6000)


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    from playwright.sync_api import sync_playwright
    f404 = []
    cons = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()

        # (D) 404s identificados + consola de audio
        pg = b.new_page()
        pg.on('response', lambda r: f404.append(f'{r.status} {r.url[-60:]}')
              if r.status >= 400 else None)
        pg.on('console', lambda m: cons.append(m.text[:130])
              if 'música del salón' in m.text else None)
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg.wait_for_timeout(3000)
        pg.mouse.click(30, 30)
        pg.wait_for_timeout(1200)
        flujo(pg, '(A+B) NORMAL: entrada, melodía, menú dentro, cierre', True)
        pg.close()

        # (C) escenario del mute persistido
        pg2 = b.new_page()
        pg2.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='domcontentloaded')
        pg2.evaluate("() => localStorage.setItem('pp_hallmus', '1')")
        pg2.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg2.wait_for_timeout(3000)
        pg2.mouse.click(30, 30)
        pg2.wait_for_timeout(1200)
        flujo(pg2, '(C) pp_hallmus=1 (mute del salón persistido)', False)
        b.close()

    if f404:
        print('--- recursos >=400 ---')
        for u in f404[:8]:
            print(' ', u)
    if cons:
        print('--- consola audio ---')
        for c in cons[:5]:
            print(' ', c)


if __name__ == '__main__':
    main()

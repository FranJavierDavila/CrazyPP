#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r160 · sonda de la MELODÍA DEL ARCANO: reproduce el flujo del dueño en el
build actual (local, idéntico a producción) y registra TODA llamada de
música (espías) + el estado del canal salón en cada paso:
  S0 salón · S1 dentro del Arcano · S2 menú abierto · S3 menú cerrado.
La clave: ¿alguien vuelve a pedir arcano.mp3 tras cerrar el menú?"""
import os, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3012


def serve():
    import http.server
    os.chdir(PUBLIC)
    handler = http.server.SimpleHTTPRequestHandler

    class H(handler):
        def log_message(self, *a):
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


ESPION = r'''() => {
  const a = window.__game.audio;
  window.__AUDLOG = [];
  const snap = () => [a.hallWanted, a._hallUrl, a.hallPlaying, a.hallMute,
                      a.musicWanted, a.musicPlaying, !!a._menuReq,
                      a.ctx ? (a.ctx.state || 'sin-estado') : 'SIN-CTX'];
  const wrap = (k) => {
    const f = a[k].bind(a);
    a[k] = (...args) => {
      window.__AUDLOG.push({ t: Math.round(performance.now()),
        fn: k, args: JSON.stringify(args).slice(0, 60), pre: snap() });
      return f(...args);
    };
  };
  ['setHallWanted', 'stopHallMusic', 'startHallMusic', 'setMusicWanted',
   'startMusic', 'stopMusic', 'setHallMute', 'setArcDuck'].forEach(wrap);
  return snap();
}'''

SNAP = r'''() => {
  const a = window.__game.audio, g = window.__game;
  return { hallWanted: a.hallWanted, hallUrl: a._hallUrl,
           hallPlaying: !!a.hallPlaying, hallMute: !!a.hallMute,
           bufs: Object.keys(a._hallBufs || {}),
           loading: a._hallLoading || null,
           musicWanted: a.musicWanted, musicPlaying: !!a.musicPlaying,
           menuReq: !!a._menuReq,
           ctx: a.ctx ? a.ctx.state : 'SIN-CTX',
           arconoOn: !!g._arconoOn, inHall: !!g.inHall,
           menuOpen: !!g.menuOpen,
           variante: (g._hallVarDef() || {}).id || null,
           musicaVariante: (g._hallVarDef() || {}).musica || null };
}'''


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    from playwright.sync_api import sync_playwright
    cons = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on('console', lambda m: cons.append(m.text[:150])
              if 'música del salón' in m.text or m.type == 'error' else None)
        pg.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        pg.wait_for_timeout(3000)
        pg.mouse.click(30, 30)          # primer gesto 2D (como el dueño)
        pg.wait_for_timeout(1000)
        print('S0 salón:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        pg.evaluate('() => window.__game._arconoEntrar()')
        pg.wait_for_timeout(1800)
        print('S1 arcano:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(900)
        print('S2 menú  :', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(1800)
        print('S3 cerrar:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        print('--- BITÁCORA de llamadas de música (pre = estado ANTES) ---')
        for e in pg.evaluate('() => window.__AUDLOG'):
            print(f"  t+{e['t']:>6} {e['fn']}({e['args']})  pre={e['pre']}")
        b.close()
    if cons:
        print('--- consola ---')
        for c in cons[:8]:
            print(' ', c)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r160 · sonda v2 del ARCANO: captura los guards de _arconoEntrar, el estado
del fundido en el tiempo y la bitácora completa de espías de música."""
import os, threading, json

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, '..', 'public')
PORT = 3013


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
                      a.musicWanted, a.musicPlaying, !!a._menuReq];
  ['setHallWanted', 'stopHallMusic', 'startHallMusic', 'setMusicWanted',
   'startMusic', 'stopMusic', 'setHallMute'].forEach((k) => {
    const f = a[k].bind(a);
    a[k] = (...args) => {
      window.__AUDLOG.push({ t: Math.round(performance.now()), fn: k,
        args: JSON.stringify(args).slice(0, 55), pre: snap() });
      return f(...args);
    };
  });
  return 'espias instalados';
}'''

ENTRA = r'''() => {
  const g = window.__game;
  const guards = { arconoOn: g._arconoOn, inHall: g.inHall,
                   arcaneGroup: !!g.arcaneGroup,
                   arcaneVisible: !!(g.arcaneGroup && g.arcaneGroup.visible),
                   fadeDir: g._arconoFadeDir, fade: g._arconoFade };
  g._arconoEntrar();
  return { guards, fadeDirTras: g._arconoFadeDir,
           negro: g._arconoNegro ? g._arconoNegro.visible : null };
}'''

FADE = r'''() => {
  const g = window.__game;
  return { fadeDir: g._arconoFadeDir, fade: +g._arconoFade.toFixed(2),
           arconoOn: !!g._arconoOn,
           cbPend: !!g._arconoFadeCb };
}'''

SNAP = r'''() => {
  const a = window.__game.audio, g = window.__game;
  return { hallWanted: a.hallWanted, hallUrl: a._hallUrl,
           hallPlaying: !!a.hallPlaying, bufs: Object.keys(a._hallBufs || {}),
           loading: a._hallLoading || null,
           musicWanted: a.musicWanted, musicPlaying: !!a.musicPlaying,
           arconoOn: !!g._arconoOn, menuOpen: !!g.menuOpen };
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
        pg.mouse.click(30, 30)
        pg.wait_for_timeout(900)
        print('espías:', pg.evaluate(ESPION))
        print('S0 salón :', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        ent = pg.evaluate(ENTRA)
        print('ENTRAR   :', json.dumps(ent, ensure_ascii=False))
        for ms in (300, 900, 1600):
            pg.wait_for_timeout(ms if ms == 300 else ms - 300)
            print(f'  fundido t+{ms}:', json.dumps(pg.evaluate(FADE), ensure_ascii=False))
        print('S1 arcano:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        # ahora el flujo del dueño: abrir y cerrar el menú DENTRO del arcano
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(800)
        print('S2 menú  :', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        pg.evaluate('() => window.__game.toggleMenu()')
        pg.wait_for_timeout(1600)
        print('S3 cerrar:', json.dumps(pg.evaluate(SNAP), ensure_ascii=False))
        print('--- BITÁCORA ---')
        for e in pg.evaluate('() => window.__AUDLOG || []'):
            print(f"  t+{e['t']:>6} {e['fn']}({e['args']})  pre={e['pre']}")
        b.close()
    if cons:
        print('--- consola ---')
        for c in cons[:8]:
            print(' ', c)


if __name__ == '__main__':
    main()

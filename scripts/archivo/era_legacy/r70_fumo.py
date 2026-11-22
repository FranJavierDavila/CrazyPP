#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r70_fumo.py — humo rápido de la FASE 164: páginas nuevas sin errores
y estructura del arco (aspecto exacto + lados condicionales)."""
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:3671/game.html'

JS = """async () => {
  const G = window.__PP_GAME;
  const out = { errores: [] };
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }
  const CM = window.PP_CFG_ARCO || null;
  // 1 · aspecto exacto por panela
  const pas = G.menuGroup.children.filter((m) => m.userData && m.userData.panela)
    .map((m) => m.userData.panela);
  out.panelas = pas.map((pa) => ({
    id: pa.id, anchoM: +pa.anchoM.toFixed(4), yaw: pa.yaw || 0 }));
  out.aspectoOk = pas.every((pa) =>
    Math.abs((pa.anchoM / pa.altoM) - (pa.w / 1400)) < 0.01);
  // 2 · abrir menú (3 panelas en main)
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  out.ladosMain = G._menuLados;
  out.nMontadas = G._menuPanelas.length;
  // 3 · barrido de páginas: sin excepciones y lados según dato
  const paginas = ['multi', 'join', 'rankini', 'rank', 'rankme', 'champs',
    'train', 'trainext', 'trainarea', 'carrera', 'opts', 'optsJuego',
    'optsSala', 'name'];
  out.paginas = {};
  for (const p of paginas) {
    try {
      G.menuPage = p;
      G._mjMode = null;
      G.drawMenu();
      await dorme(60);
      out.paginas[p] = { lados: G._menuLados.join(''),
        n: G._menuPanelas.length, rects: G.menuRects.length };
    } catch (e) {
      out.paginas[p] = { error: String(e && e.stack || e).slice(0, 200) };
    }
  }
  // 4 · capturas clave
  const capt = async (p, key) => {
    G.menuPage = p; G._mjMode = null; G.drawMenu(); await dorme(160);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  await capt('main', 'capMain');
  await capt('multi', 'capMulti');
  await capt('champs', 'capChamps');
  await capt('carrera', 'capCarrera');
  await capt('train', 'capTrain');
  await capt('rankini', 'capRankini');
  return out;
}"""

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def main():
    global ok, fails
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3671', '--bind', '127.0.0.1'],
        cwd='/home/z/my-project/upload/public',
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        urllib.request.urlopen(URL, timeout=10).read(200)
    except Exception as e:
        print('servidor no responde:', e)
        server.terminate()
        sys.exit(1)
    errores = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errores.append(str(e)[:300]))
        page.on('console', lambda m: errores.append('console: ' + m.text[:200])
                if m.type == 'error' else None)
        page.goto(URL)
        try:
            page.wait_for_function('!!window.__PP_GAME', timeout=45000)
        except Exception:
            print('FALLO: __PP_GAME no llegó')
            browser.close(); server.terminate(); sys.exit(1)
        page.wait_for_timeout(1200)
        rt = page.evaluate(JS)
        # capturas
        import base64
        for key, name in [('capMain', 'r70_main.png'),
                          ('capMulti', 'r70_multi.png'),
                          ('capChamps', 'r70_champs.png'),
                          ('capCarrera', 'r70_carrera.png'),
                          ('capTrain', 'r70_train.png'),
                          ('capRankini', 'r70_rankini.png')]:
            if rt.get(key):
                raw = base64.b64decode(rt[key].split(',', 1)[1])
                open('/home/z/my-project/download/' + name, 'wb').write(raw)
        chk(not rt.get('sinJuego'), 'juego presente')
        chk(rt.get('aspectoOk'), 'aspecto exacto por panela')
        print('   panelas:', rt.get('panelas'))
        chk(rt.get('nMontadas') == 3 and rt.get('ladosMain') == ['L', 'C', 'R'],
            'main monta 3 panelas')
        for p, info in (rt.get('paginas') or {}).items():
            if 'error' in info:
                chk(False, f'página {p}: {info["error"][:120]}')
            else:
                chk(True, f'página {p}: lados {info["lados"]} · {info["n"]} panela(s) · {info["rects"]} rects')
        chk(not errores, 'sin pageerrors/console errors' +
            ('' if not errores else f' → {errores[:2]}'))
        if errores:
            print('   errores:', errores[:5])
        browser.close()
    server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()

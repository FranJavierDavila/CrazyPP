#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_gigante_r84.py — ¿quién pinta el texto GIGANTE sobre trainext?"""
import json
import subprocess
import sys
import time

RAIZ = '/home/z/my-project'
server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3674', '--bind', '127.0.0.1',
     '--directory', RAIZ + '/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)

JS = """
async () => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const out = {};
  // enganchar fillText y registrar llamadas con fuente >= 150 px
  const orig = CanvasRenderingContext2D.prototype.fillText;
  window.__gigantes = [];
  CanvasRenderingContext2D.prototype.fillText = function (txt, x, y) {
    try {
      const m = /([0-9]+)px/.exec(String(this.font) || '');
      if (m && parseInt(m[1], 10) >= 150) {
        window.__gigantes.push({ txt: String(txt).slice(0, 40),
          font: this.font, x: Math.round(x), y: Math.round(y) });
      }
    } catch (e) { /* */ }
    return orig.apply(this, arguments);
  };
  G.menuOpen = true;
  if (G.menuGroup) G.menuGroup.visible = true;
  G.menuPage = 'trainext';
  G.drawMenu();
  const a0 = G.menuCanvas.toDataURL().length;
  await dorme(600);
  const a1 = G.menuCanvas.toDataURL().length;
  out.lenSin = a0; out.lenCon = a1;
  out.estado = G.rules && G.rules.state;
  out.menuPage = G.menuPage;
  out.paused = !!G.paused;
  out.gigantes = window.__gigantes.slice(-12);
  CanvasRenderingContext2D.prototype.fillText = orig;
  return out;
}
"""

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={'width': 1280, 'height': 720})
        pg.goto('http://127.0.0.1:3674/game.html', wait_until='load',
                timeout=60000)
        pg.wait_for_function('() => !!window.__PP_GAME', timeout=30000)
        res = pg.evaluate(JS)
        pg.close()
        b.close()
finally:
    server.terminate()
print(json.dumps(res, indent=2, ensure_ascii=False))

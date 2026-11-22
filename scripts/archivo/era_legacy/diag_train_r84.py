#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_train_r84.py — diagnóstico visual de las subpáginas MIGRADAS.
Captura el lienzo (3696×1400) de trainarea y trainext + vuelca los rects.
Salida: JSON de veredicto + PNGs en download/r83_diag/.
"""
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

RAIZ = '/home/z/my-project'
OUT = Path(RAIZ) / 'download' / 'r83_diag'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:3673/game.html'

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3673', '--bind', '127.0.0.1',
     '--directory', RAIZ + '/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)

JS = """
async () => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const out = {};
  G.menuOpen = true;
  if (G.menuGroup) G.menuGroup.visible = true;
  for (const pg of ['train', 'trainarea', 'trainext']) {
    G.menuPage = pg;
    G.drawMenu();
    await dorme(180);
    const rs = (G.menuRects || []).filter((r) => r && r.id);
    out[pg + '_rects'] = rs.map((r) => ({ id: r.id, x: Math.round(r.x),
      y: Math.round(r.y), w: Math.round(r.w), h: Math.round(r.h) }));
    out['png_' + pg] = G.menuCanvas.toDataURL('image/png');
  }
  return out;
}
"""

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={'width': 1280, 'height': 720})
        pg.goto(URL, wait_until='networkidle', timeout=45000)
        pg.wait_for_function('() => !!window.__PP_GAME', timeout=30000)
        res = pg.evaluate(JS)
        pg.close()
        b.close()
finally:
    server.terminate()

if res.get('error'):
    print('ERROR:', res['error'])
    sys.exit(1)

try:
    from PIL import Image
    import io
    for pg in ('train', 'trainarea', 'trainext'):
        data = res.pop('png_' + pg)
        im = Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1])))
        im.save(OUT / (pg + '.png'))
        im.crop((1112, 0, 2584, 1400)).save(OUT / (pg + '_C.png'))
        print(pg, 'capturado ·', im.size)
except Exception as e:
    print('PIL:', e)

for pg in ('train', 'trainarea', 'trainext'):
    rects = res.get(pg + '_rects', [])
    xs = [r['x'] for r in rects] or [0]
    xf = [r['x'] + r['w'] for r in rects] or [0]
    ys = [r['y'] for r in rects] or [0]
    yf = [r['y'] + r['h'] for r in rects] or [0]
    print(f"{pg}: {len(rects)} rects · x {min(xs)}-{max(xf)} · y {min(ys)}-{max(yf)}"
          f" · fuera_de_C={len([r for r in rects if r['x'] < 1150 or r['x']+r['w'] > 2570])}")

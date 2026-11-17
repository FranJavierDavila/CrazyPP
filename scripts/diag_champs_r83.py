#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_champs_r83.py — diagnóstico r83 de la página CAMPEONATOS.
1) vuelca los rects de la página (banda chmus:set vs rejilla);
2) PRUEBA EN VIVO el bug de arrastre (_menuDragUpdate con id 'chmus':
   ¿mueve arcVol o fxVol?);
3) captura el lienzo completo + recortes de la banda para inspección.
Salida: JSON de veredicto + PNGs en download/r83_diag/.
"""
import base64
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = '/home/z/my-project'
OUT = Path(RAIZ) / 'download' / 'r83_diag'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:3671/game.html'

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3671', '--bind', '127.0.0.1',
     '--directory', os.path.join(RAIZ, 'public')],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)

JS = """
async () => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const out = {};
  // página champs viva
  G.menuPage = 'champs';
  G.menuOpen = true;
  if (G.menuGroup) G.menuGroup.visible = true;
  G.drawMenu();
  await dorme(200);
  const rs = (G.menuRects || []).filter((r) => r && r.id);
  out.rects = rs.map((r) => ({ id: r.id, x: r.x, y: r.y, w: r.w, h: r.h,
    slider: !!r.slider }));
  const banda = rs.find((r) => r.id === 'chmus:set');
  out.banda = banda || null;
  out.rectsBottom = rs.filter((r) => r.y + r.h > 1150)
    .map((r) => ({ id: r.id, x: Math.round(r.x), y: Math.round(r.y),
      w: Math.round(r.w), h: Math.round(r.h) }));
  const noBanda = rs.filter((r) => r.id !== 'chmus:set');
  out.rejillaMaxY = noBanda.length
    ? Math.max(...noBanda.map((r) => r.y + r.h)) : 0;
  out.rejillaMinY = noBanda.length ? Math.min(...noBanda.map((r) => r.y)) : 0;
  // — prueba del bug de arrastre en vivo —
  if (banda) {
    const fx0 = G.audio.fxVol, arc0 = G.audio.arcMute ? 0 : G.audio.arcVol;
    const mx = banda.x + banda.w * 0.8, my = banda.y + banda.h / 2;
    G._menuClickPx = [mx, my];
    G._menuHitPx = [mx, my];
    G._menuDrag = { hand: 0, id: 'chmus' };
    G._menuDragUpdate();
    G._menuDrag = null;
    const fx1 = G.audio.fxVol, arc1 = G.audio.arcMute ? 0 : G.audio.arcVol;
    out.bugArrastre = {
      fx_antes: fx0, fx_despues: fx1, arc_antes: arc0, arc_despues: arc1,
      mueve_fx: Math.abs(fx1 - fx0) > 1e-6,
      mueve_arc: Math.abs(arc1 - arc0) > 1e-6,
    };
  }
  // capturas del lienzo
  out.pngChamps = G.menuCanvas.toDataURL('image/png');
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(120);
  out.pngMain = G.menuCanvas.toDataURL('image/png');
  return out;
}
"""

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={'width': 1280, 'height': 720})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
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

png_champs = res.pop('pngChamps')
png_main = res.pop('pngMain')
for nombre, data in (('champs.png', png_champs), ('main.png', png_main)):
    (OUT / nombre).write_bytes(base64.b64decode(data.split(',', 1)[1]))

# recortes de la banda para inspección visual
try:
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(png_champs.split(',', 1)[1])))
    print('lienzo champs:', im.size)
    im.crop((0, 1150, 3696, 1400)).save(OUT / 'champs_banda.png')
    im.crop((1112, 1100, 2584, 1400)).resize((1472, 300)).save(
        OUT / 'champs_banda_C.png')
    im.crop((0, 0, 3696, 700)).save(OUT / 'champs_arriba.png')
except Exception as e:
    print('PIL:', e)

print(json.dumps(res, indent=2, ensure_ascii=False))
print('pageerrors:', len(res.get('_errs', [])) if '_errs' in res else errs)
print('PNGs en', OUT)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_r80.py — CAPTURAS VISUALES de las páginas que el dueño reclama
en la ronda 80 (sin checks): train + subapartados, rank, hallpick,
optsSala/Room, multi y main. Sirve public/ en el 3669 y guarda PNGs en
/tmp/render80/ para inspección del agente."""
import asyncio
import base64
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
OUT = Path('/tmp/render80')
OUT.mkdir(exist_ok=True)

JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  if (!G) { out.sinJuego = true; return out; }
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const capt = async (key, pre) => {
    if (pre) pre();
    G.menuOpen = true;
    G.menuGroup.visible = true;
    G.drawMenu();
    await dorme(140);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  const ids = () => (G.menuRects || []).map((r) => String(r.id));
  // 1 · ENTRENAR (landing)
  await capt('pngTrain', () => { G.menuPage = 'train'; });
  out.idsTrain = ids().slice(0, 14);
  // 2 · área DIRECCIÓN (trv3:area:dir)
  const iDir = ids().indexOf('trv3:area:dir');
  if (iDir >= 0) G.menuClick(iDir, 0);
  await dorme(160);
  await capt('pngTrainArea', () => {});
  out.areaPagina = G.menuPage;
  out.idsArea = ids().slice(0, 10);
  // 3 · RETO DE LA SEMANA
  G.menuPage = 'train'; G.drawMenu(); await dorme(60);
  const iSem = ids().indexOf('trv3:semana');
  if (iSem >= 0) G.menuClick(iSem, 0);
  await dorme(160);
  await capt('pngSemana', () => {});
  out.semanaPagina = G.menuPage;
  // 4 · PERFILES (TU PROGRESO)
  G.menuPage = 'train'; G.drawMenu(); await dorme(60);
  const iExt = ids().indexOf('page:trainext');
  if (iExt >= 0) G.menuClick(iExt, 0);
  await dorme(160);
  await capt('pngTrainExt', () => {});
  out.extPagina = G.menuPage;
  // 5 · RANKING MUNDIAL
  await capt('pngRank', () => { G.menuPage = 'rank'; });
  // 6 · ESCOGER HALL
  await capt('pngHallpick', () => { G.menuPage = 'hallpick'; });
  // 7 · AJUSTES › SALA Y ESCENA (landing y subpágina)
  await capt('pngOptsSala', () => { G.menuPage = 'optsSala'; });
  await capt('pngOptsSalaRoom', () => { G.menuPage = 'optsSalaRoom'; });
  // 8 · MULTIJUGADOR (zonas)
  await capt('pngMulti', () => { G._mjMode = null; G.net.status = 'off';
    G._salaEnEspera = false; G.menuPage = 'multi'; });
  // 9 · MI CASA (landing principal de la segunda panela)
  await capt('pngMain', () => { G.menuPage = 'main'; });
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    from playwright.async_api import async_playwright
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3669', '--bind', '127.0.0.1',
         '--directory', str(RAIZ / 'public')],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(
                viewport={'width': 1280, 'height': 720})
            page.on('pageerror',
                    lambda e: print('pageerror:', str(e)[:120]))
            await page.goto('http://127.0.0.1:3669/game.html')
            await page.wait_for_function(
                '() => !!window.__PP_GAME', timeout=45000)
            await page.evaluate('window.__PP_GAME.closeMenu()')
            await asyncio.sleep(2.0)
            out = await page.evaluate(JS)
            for k, v in out.items():
                if k.startswith('png'):
                    (OUT / (k[3:].lower() + '.png')).write_bytes(
                        base64.b64decode(v.split(',', 1)[1]))
                else:
                    print(' ', k, '=', v)
            await browser.close()
    finally:
        server.terminate()
    print('capturas en', OUT)


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_foto_r83 — fotografías de control de la r83 (AJUSTES 7 tarjetas,
subpágina PALA, teclado del nombre y panel frontal del ajuste)
→ tmp_frames/r83_*.png"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"

JS_FOTOS = """() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin juego' };
  const shots = {};
  // 1 · página AJUSTES con las 7 tarjetas
  G.menuPage = 'opts';
  G.menuOpen = true;
  G.drawMenu();
  shots.ajustes = G.menuCanvas.toDataURL('image/png');
  // 2 · subpágina PALA (con 2 agarres de muestra)
  const store = G.loadGripsStore();
  store['AGARRE 1'] = { px: 0.012, py: -0.031, pz: 0.044, rx: 0.09, ry: -0.15, rz: 0.02 };
  store['MANO ZURDA'] = { px: -0.02, py: 0.01, pz: 0.03, rx: -0.05, ry: 0.1, rz: 0 };
  G.saveGripsStore(store);
  G.menuPage = 'optsPala';
  G.drawMenu();
  shots.palaPage = G.menuCanvas.toDataURL('image/png');
  // 3 · teclado del NOMBRE DEL AGARRE
  G._gripBuf = 'QA MILIMETRO';
  G.menuPage = 'gripname';
  G.drawMenu();
  shots.gripname = G.menuCanvas.toDataURL('image/png');
  G._gripBuf = '';
  G.menuPage = 'opts';
  // limpiar los agarres de muestra (la foto no deja huella)
  delete G.loadGripsStore()['AGARRE 1'];
  delete G.loadGripsStore()['MANO ZURDA'];
  G.saveGripsStore(G.loadGripsStore());
  return shots;
}"""


async def main():
    import base64
    import pathlib
    out = pathlib.Path('/home/z/my-project/tmp_frames')
    out.mkdir(exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        for _ in range(90):
            if await page.evaluate("() => !!window.__PP_GAME"):
                break
            await page.wait_for_timeout(500)
        shots = await page.evaluate(JS_FOTOS)
        if shots.get('error'):
            print('✗ FALLO: ' + shots['error'])
            sys.exit(1)
        n = 0
        for nombre, data in shots.items():
            png = base64.b64decode(data.split(',', 1)[1])
            (out / ('r83_' + nombre + '.png')).write_bytes(png)
            print('  ✓ r83_' + nombre + '.png (' + str(len(png)) + ' B)')
            n += 1
        await browser.close()
        print('FOTOS: ' + str(n) + '/3')

asyncio.run(main())

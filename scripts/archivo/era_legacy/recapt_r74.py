#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recapt_r74.py — recaptura optsSalaBola/optsSalaRoom (nombres correctos)
+ zoom del candado en la página ESCOGER HALL (fila bloqueada)."""
import asyncio
import base64
import pathlib
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3669/game.html'
OUT = pathlib.Path('/home/z/my-project/download/r74_capturas')


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const capt = async (pg, key) => {
    G.menuPage = pg;
    G.drawMenu();
    await dorme(140);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  await capt('optsSalaBola', 'pngSalabola');
  await capt('optsSalaRoom', 'pngSalaroom');
  await capt('hallpick', 'pngHallpick');
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3669', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    get(URL)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3600)
        out = await page.evaluate(JS)
        await browser.close()
    for key, nombre in [('pngSalabola', 'optsSalaBola'),
                        ('pngSalaroom', 'optsSalaRoom'),
                        ('pngHallpick', 'hallpick')]:
        data = out.get(key)
        if data and data.startswith('data:image/png'):
            (OUT / (nombre + '.png')).write_bytes(
                base64.b64decode(data.split(',', 1)[1]))
            print('captura', nombre)
    # zoom: recorte de la ZONA DEL CANDADO (x0+w0-110 .. x0+w0, filas 2-4)
    from PIL import Image
    im = Image.open(OUT / 'hallpick.png')
    w, h = im.size
    # panela C: x≈1328..2352 en lienzo virtual 3698x1400 → escala al png
    esc = w / 3698.0
    x0 = int((2352 - 120 - 120) * esc)
    x1 = int((2352 + 40) * esc)
    y0 = int(560 * esc)
    y1 = int(1000 * esc)
    im.crop((x0, y0, x1, y1)).resize(
        ((x1 - x0) * 2, (y1 - y0) * 2), Image.LANCZOS).save(OUT / 'zoom_candado.png')
    print('zoom_candado.png', (x1 - x0) * 2, (y1 - y0) * 2)


if __name__ == '__main__':
    asyncio.run(main())

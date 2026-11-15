#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_r73_champuno.py — cuenta real de candy en champuno con el índice
de campeonatos YA cargado (la aguja viva del héroe falla y hay que ver
qué cuenta de más)."""
import asyncio
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3668/game.html'


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  await dorme(6500);   // dejar llegar el índice de campeonatos
  const chs = (G.champs && G.champs.list && G.champs.list()) || [];
  out.chs = chs.map((c) => ({ id: c.id, locked: !!c.locked }));
  const chLibre = chs.find((c0) => !c0.locked);
  out.chLibre = chLibre ? chLibre.id : null;
  const oc = G._vestCandy;
  let nC = 0, filas = [];
  G._vestCandy = function (c, x, y, w, h) {
    nC++; filas.push([x, y, w, h]);
    return oc.apply(this, arguments);
  };
  if (chLibre) {
    G._champSel = chLibre.id;
    G.menuPage = 'champuno';
    G.drawMenu();
    out.nC = nC;
    out.filas = filas;
    out.rects = (G.menuRects || []).map((r) => String(r.id));
  }
  G._vestCandy = oc;
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3668', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    get(URL)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(500)
        out = await page.evaluate(JS)
        await browser.close()
    for k, v in out.items():
        print(k, '=', v)


if __name__ == '__main__':
    asyncio.run(main())

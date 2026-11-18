#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_r73_optsala.py — por qué optsSala dibuja 2 candy/8 placas y qué
cuenta champuno (sonda de una sola página, consola + contadores)."""
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
  const oc = G._vestCandy, op = G._vestPlaca73;
  // optsSala
  let nC = 0, nP = 0;
  G._vestCandy = function () { nC++; return oc.apply(this, arguments); };
  G._vestPlaca73 = function () { nP++; return op.apply(this, arguments); };
  G.menuPage = 'optsSala'; G.drawMenu(); await dorme(30);
  out.optsSala = nC + '/' + nP;
  // ¿drawMenuOptsCat dibuja dos veces? cuentan llamadas al método entero
  let nCat = 0;
  const ocat = G.drawMenuOptsCat;
  G.drawMenuOptsCat = function () { nCat++; return ocat.apply(this, arguments); };
  G.menuPage = 'optsSala'; G.drawMenu(); await dorme(30);
  out.drawOptsCatVeces = nCat;
  G.drawMenuOptsCat = ocat;
  // champuno
  const chs = (G.champs && G.champs.list && G.champs.list()) || [];
  out.chsN = chs.length;
  out.chsIds = chs.slice(0, 3).map((c) => c.id);
  if (chs.length) {
    G._champSel = chs[0].id;
    nC = 0; nP = 0;
    G.menuPage = 'champuno'; G.drawMenu(); await dorme(30);
    out.champuno = nC + '/' + nP;
    out.champSel = G._champSel;
    const ids = (G.menuRects || []).map((r) => String(r.id));
    out.champIds = ids.slice(0, 8);
  }
  // strokeStyle tal cual lo devuelve Chrome
  const mc = document.createElement('canvas'); mc.width = 60; mc.height = 60;
  const mx = mc.getContext('2d');
  G._vestMedallion(mx, 30, 30, 12, 'partido', '#ffca1e');
  out.strokeBruto = String(mx.strokeStyle);
  out.strokeLimpio = String(mx.strokeStyle).replace(/\\s+/g, '');
  G._vestCandy = oc; G._vestPlaca73 = op;
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
        await page.wait_for_timeout(3600)
        out = await page.evaluate(JS)
        await browser.close()
    for k, v in out.items():
        print(k, '=', v)


if __name__ == '__main__':
    asyncio.run(main())

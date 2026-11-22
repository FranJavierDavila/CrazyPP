#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fotografía de los dos menús tocados por r80 (multi + hub) para revisión
a ojo del dueño: extrae el menuCanvas real del juego en vivo."""
import asyncio
import base64
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"

JS = """(page) => {
  const G = window.__PP_GAME;
  G.menuPage = page;
  if (page === 'multi') G._mjMode = null;
  G.drawMenu();
  return G.menuCanvas.toDataURL('image/png');
}"""

JS_SEL = """() => {
  const G = window.__PP_GAME;
  G.menuPage = 'multi'; G._mjMode = 'normal'; G.drawMenu();
  return G.menuCanvas.toDataURL('image/png');
}"""


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        for _ in range(90):
            if await page.evaluate("() => !!window.__PP_GAME"):
                break
            await page.wait_for_timeout(500)
        await page.wait_for_timeout(1500)
        for nombre, js in [("multi_seleccion", JS), ("multi_sala", JS_SEL), ("hub_reto", JS)]:
            arg = "multi" if nombre != "hub_reto" else "main"
            data = await page.evaluate(js, arg)
            open(f"/home/z/my-project/tmp_frames/r80_{nombre}.png", "wb").write(base64.b64decode(data.split(",", 1)[1]))
            print("foto:", nombre)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

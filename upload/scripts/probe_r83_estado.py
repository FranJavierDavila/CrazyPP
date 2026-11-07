#!/usr/bin/env python3
"""probe_r83_estado — sondeo del estado sala/hall antes y después del ajuste."""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

JS = """() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin juego' };
  const snap = (tag) => ({
    tag,
    inHall: G.inHall, mode: G.mode, inAR: G.inAR, pstOn: G.pstOn,
    roomVis: G.roomGroup ? G.roomGroup.visible : null,
    bg: G.scene.background ? 'obj' : null,
    pstAplicada: !!G._pstAplicada,
    hallGroupVis: G.hallGroup ? G.hallGroup.visible : null,
  });
  const xr = G.renderer.xr;
  Object.defineProperty(xr, 'isPresenting', { get() { return true; }, configurable: true });
  const s0 = snap('antes');
  G.inAR = true; G.pstOn = false;
  G.enterCalib(true);
  const s1 = snap('en ajuste');
  G.exitCalib();
  const s2 = snap('tras salir');
  try { delete xr.isPresenting; } catch (e) {}
  return { s0, s1, s2 };
}"""


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 480, "height": 320})
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        for _ in range(90):
            if await page.evaluate("() => !!window.__PP_GAME"):
                break
            await page.wait_for_timeout(500)
        r = await page.evaluate(JS)
        for k, v in r.items():
            print(k, v)
        await browser.close()

asyncio.run(main())
